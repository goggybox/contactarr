
# -----------------------------contactarr------------------------------
# This file is part of contactarr
# Copyright (C) 2025 goggybox https://github.com/goggybox

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# that this program is licensed under. See LICENSE file. If not
# available, see <https://www.gnu.org/licenses/>.

# Please keep this header comment in all copies of the program.
# --------------------------------------------------------------------

import sqlite3
import time
import os
import threading
from pathlib import Path
from datetime import datetime
from datetime import timezone
from backend.api import tautulli
from backend.api import overseerr
from backend.api import config
from backend.api import tmdb

DB_PATH = Path(__file__).parent / "contactarr.db"
POSTER_CACHE_DIR = ".image_cache/posters"
os.makedirs(POSTER_CACHE_DIR, exist_ok=True)

def _poster_cache_path(media_type: str, media_id: int) -> str:
    return os.path.join(POSTER_CACHE_DIR, f"{media_type}_{media_id}.jpg")

def load_cached_poster(media_type: str, media_id: int) -> bytes | None:
    path = _poster_cache_path(media_type, media_id)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f.read()
    return None

def save_cached_poster(media_type: str, media_id: int, data: bytes):
    path = _poster_cache_path(media_type, media_id)
    with open(path, "wb") as f:
        f.write(data)

def get_poster_image(*, movie_id=None, show_id=None):
    """
    return the poster image bytes for a movie OR show.
    tautlli is preferred for sourcing posters, tmdb if no tautulli url is known
    """
    if (movie_id is None) == (show_id is None):
        raise ValueError("Provide exactly one of movie_id or show_id")

    if movie_id is not None:
        media_type = "movie"
        media_id = movie_id
        table = "movies"
        id_col = "movie_id"
    else:
        media_type = "show"
        media_id = show_id
        table = "shows"
        id_col = "show_id"

    cached = load_cached_poster(media_type, media_id)
    if cached:
        return cached

    # no cached image. fetch from tautulli/tmdb
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            f"""
            SELECT tautulli_poster_url, tmdb_poster_url
            FROM {table}
            WHERE {id_col} = ?
            """,
            (media_id,),
        ).fetchone()

    if not row:
        return None

    image = None
    if row["tautulli_poster_url"]:
        image = tautulli.get_poster_image(row["tautulli_poster_url"])

    if image is None and row["tmdb_poster_url"]:
        image = tmdb.get_poster_image(row["tmdb_poster_url"])

    if image is None:
        return None

    save_cached_poster(media_type, media_id, image)
    return image


class SafeConnection:
    def __init__(self, conn):
        self._conn = conn
    
    def __enter__(self):
        return self._conn

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self._conn.rollback()
        else:
            self._conn.commit()
        self._conn.close()

    def __getattr__(self, name):
        return getattr(self._conn, name)

def _get_table(conn, name):
    """
    get the entire contents of a table, return a list of dicts (one per row)
    """
    contents = conn.execute(f"SELECT * FROM {name}").fetchall()
    return [dict(row) for row in contents]

def _get_table_indexed(conn, name, key_field):
    """
    get the entire contents of a table, but make it accessible by a particular
    field. (easy access, faster than O(n), which is what _get_table() would require).
    """
    rows = conn.execute(f"SELECT * FROM {name}").fetchall()
    return {row[key_field]: dict(row) for row in rows}

def get_field_from_table(conn, table, target_column, filters: dict):
    """
    fetch the value of a given column (target_column) with a WHERE
    clause made up of filters.
    e.g.: get_field_from_table(conn, "users", "user_id", {"username": username})
    """
    if not filters:
        raise ValueError("get_field_from_table called but filters not given.")
    
    where = " AND ".join(f"{col} = ?" for col in filters.keys())
    values = tuple(filters.values())
    
    query = f"""
        SELECT {target_column}
        FROM {table}
        WHERE {where}
        LIMIT 1
    """

    row = conn.execute(query, values).fetchone()
    return row[target_column] if row else None

def get_row_from_table(conn, table, filters: dict):
    """
    same as get_field_from_table but returns the entire row.
    """
    if not filters:
        raise ValueError("get_row_from_table called but filters not given.")

    where = " AND ".join(f"{con} = ?" for col in filters.keys())
    values = tuple(filters.values())

    query = f"""
        SELECT *
        FROM {table}
        WHERE {where}
        LIMIT 1
    """

    row = conn.execute(query, values).fetchone()
    return dict(row) if row else None

def set_show_tmdb_id(conn, show_name, tmdb_id):
    """

    """
    result = conn.execute(
        "UPDATE shows SET tmdb_id = ? WHERE show_name = ?",
        (tmdb_id, show_name)
    )
    conn.commit()
    return result.rowcount

def _attrs_vals_in_table(conn, spec):
    """
    determine whether a particular set of attributes&values exist in a table.
    if so, optionally return the value of one column of the record, or simply
    a boolean of whether or not such a record exists.
    spec = {
        "table": "table_name",
        "data": { column: value, ... }
        "return": "column_name" | None
    }
    """
    table = spec["table"]
    data = spec["data"]
    return_col = spec.get("return")

    where_clause = " AND ".join(f"{col} = ?" for col in data)
    values = list(data.values())

    select_expr = return_col if return_col else "1"

    sql = f"""
        SELECT {select_expr}
        FROM {table}
        WHERE {where_clause}
        LIMIT 1
    """

    cur = conn.execute(sql, values)
    row = cur.fetchone()

    if return_col:
        return row[0] if row else None

    return row is not None

def _add_to_table(conn, spec: dict):
    """
    spec should contain the following:
    {
        "table": "name",                    # table to insert into
        "data": { column: value, ... },     # column values to insert
        "return": "column_name" | None      # value to return after insertion
    }
    """
    table = spec["table"]
    data = spec["data"]
    return_col = spec.get("return")

    columns = ", ".join(data.keys())
    placeholders = ", ".join("?" for _ in data)
    values = list(data.values())

    sql = f"INSERT OR IGNORE INTO {table} ({columns}) VALUES ({placeholders})"

    if return_col:
        sql += f" RETURNING {return_col}"

    cur = conn.execute(sql, values)

    if return_col:
        row = cur.fetchone()
        return row[0] if row else None

    return

def _update_row_or_ignore(conn, attrs, vals, name):
    """
    update a row in the "name" table using the given attrs and vals.
        - the PRIMARY KEY attribute will be included (as the first attr) in attrs, which is
          used to find the exact row to modify.
        - if no row exists with the primary key value, fail silently.
    """
    attr_list = [attr.strip() for attr in attrs.split(",")]
    if not attr_list:
        return
    
    pk = attr_list[0]
    update_attrs = attr_list[1:]

    if not update_attrs:
        return

    set_clause = ", ".join(f"{attr}=?" for attr in update_attrs)
    pk_value = vals[0]
    update_values = vals[1:] + [pk_value] # SET ... WHERE pk = ?

    query = f"UPDATE {name} SET {set_clause} WHERE {pk} = ?"

    conn.execute(query, update_values)


def _add_or_ignore_to_table(conn, spec: dict):
    """
    same as _add_to_table(), but entries are not added if one already exists with the given values
    """
    table = spec["table"]
    data = spec["data"]
    return_col = spec.get("return")

    columns = ", ".join(data.keys())
    placeholders = ", ".join("?" for _ in vals)
    values = list(data.values())

    sql = f"INSERT OR IGNORE INTO {table} ({columns}) VALUES ({placeholders})"

    if return_col:
        sql += f" RETURNING {return_col}"

    cur = conn.execute(sql, values)

    if return_col:
        row = cur.fetchone()
        return row[0] if row else None

    return



def get_connection():
    if not DB_PATH.exists():
        DB_PATH.touch()
        init_db()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout = 30000;")
    return SafeConnection(conn)

def link_tautulli():
    if tautulli.validate_apikey():
        print("LINKING TAUTULLI...")
        begin_timer = time.time()
        populate_users_table()
        populate_movies()
        populate_shows()
        end_timer = time.time()
        print(f"\nFINISHED LINKING TAUTULLI. (Took {end_timer-begin_timer}s)")
        return True
    print("Tautulli API key not valid, cancelling link.")
    return False

def link_overseerr():
    if overseerr.validate_apikey():
        print("LINKING OVERSEERR...")
        process_overseerr_requests()
    else:
        print("Overseerr API key not valid, cancelling link.")

def get_overseerr_status():
    global _overseerr_running
    return _overseerr_running

"""
TODO:
prefer to get posters from Tautulli. metadata command returns data with "thumb" URI, can use that
in a "pms_image_proxy" command to get the poster.

need to link overseerr, and process all requests. add movies/shows from requests that were not
added from tautulli. WOULD BE BETTER to NOT add all tmdb poster urls to database right now,
very slow operation - and many movies on tautulli may no longer be on overseerr.

"""

def get_unix_from_iso(iso):
    # Handles variable decimal places automatically
    dt = datetime.fromisoformat(iso.replace('Z', '+00:00'))
    return int(dt.timestamp())

def process_overseerr_requests():
    cnf = config.get_overseerr_config()
    last_process = cnf.get('last_requests_process') # will ignore requests from before the last processing
    if not last_process:
        last_process = 0

    requests = overseerr.get_requests()
    
    with get_connection() as conn:
        with conn:
            # existing tables to compare against
            movies_table = _get_table_indexed(conn, "movies", "rating_key")
            shows_table = _get_table_indexed(conn, "shows", "rating_key")

            # consider each request
            for request in requests:
                if get_unix_from_iso(request["updatedAt"]) < last_process:
                    # this request will have been processed as part of a previous scan
                    continue
                
                # is it a movie or show?
                if request["type"] == "movie":
                    # movie
                    process_movie_request(request, movies_table)
                else:
                    # tv
                    process_tv_request(request, shows_table)

def extract_year_from_yyyy_dd_mm(datestr):
    # extract just year from 2026-02-08 format
    return datetime.fromisoformat(str(datestr)).year

def process_movie_request(request, movies_table):

    request_media = request["media"]
    tmdbId = request_media["tmdbId"]
    rating_key = request_media["ratingKey"]
    movie_id = None
    movie_name = None
    movie_year = None
    tmdb_movie_details = tmdb.get_movie(tmdbId) # get information about the movie from TMDB.
    
    # get movie from existing table
    if rating_key:
        # search for show using rating key
        movie_in_table = int(rating_key) in movies_table
    else:
        with get_connection() as conn:
            with conn:
                # search for show using tmdbID
                movies_by_tmdb = _get_table_indexed(conn, "movies", "tmdb_id")
                movie_in_table = int(tmdbId) in movies_by_tmdb

    if not movie_in_table:
        # the move is not in the movies table.

        # add it:
        with get_connection() as conn:
            with conn:
                movie_name = tmdb_movie_details["title"]
                movie_year = extract_year_from_yyyy_dd_mm(tmdb_movie_details["release_date"])
                tmdb_poster_url = tmdb_movie_details["poster_path"]

                movie_id = _add_to_table(conn, {
                    "table": "movies",
                    "data": {
                        "movie_name": movie_name,
                        "year": movie_year, # "release_date" is in format 2026-08-02, we just want year.
                        "rating_key": rating_key,
                        "tmdb_poster_url": tmdb_poster_url # not in tautulli, so can't use tautulli_poster_url
                    },
                    "return": "movie_id"
                })

                # if movie_id is None, that means it was not added to the table because there was a constraint
                # violation, namely that there already exists a movie with the same movie_name+year.
                #   - it can be the case that overseerr has the incorrect rating_key.
                if not movie_id:
                    # we now need to get the movie_id and rating_key of the entry in the movies table.
                    obtained_movie = get_row_from_table(conn, "movies", {"movie_name": movie_name, "year": movie_year})
                    movie_id = obtained_movie["movie_id"]
                    rating_key = obtained_movie["rating_key"]

                    # also, add tmdb_id to table entry
                    _update_row_or_ignore(conn,
                        "movie_id, tmdb_id",
                        [movie_id, tmdb_movie_details["id"]],
                        "movies"
                    )

    else:
        # there is a movie in the movies table with the rating key overseerr expected.
        # get the movie_name and movie_year
        with get_connection() as conn:
            with conn:
                if rating_key:
                    # it was obtained using rating_key
                    obtained_movie = get_row_from_table(conn, "movies", {"rating_key": rating_key})
                else:
                    # it was obtained using tmdbId
                    obtained_movie = get_row_from_table(conn, "movies", {"tmdb_id", tmdbId})

                movie_id = obtained_movie["movie_id"]
                movie_name = obtained_movie["movie_name"]
                movie_year = obtained_movie["year"]

                # also, add tmdb_id to table entry
                _update_row_or_ignore(conn,
                    "movie_id, tmdb_id",
                    [movie_id, tmdb_movie_details["id"]],
                    "movies"
                )

    # now, if the movie was already in the table, we got its id. if the movie wasn't in the table, we added it and got an id.
    # now add an entry to movie_requests for the obtained movie_id
    with get_connection() as conn:
        with conn:
            user_plex_id = request["requestedBy"].get("plexId")
            if not user_plex_id:
                # there may be a user in Overseerr who isn't connected to a Plex account (such as a local user).
                # they should still have a Plex ID, and it should be in Tautulli.
                #   - if their Overseerr username matches the username of a Plex user in our users table, the
                #     request will be assigned to them.
                username = request["requestedBy"]["username"]
                if (username):
                    user_plex_id = get_field_from_table(conn, "users", "user_id", {"username": username})

            request_id = _add_to_table(conn, {
                "table": "movie_requests",
                "data": {
                    "movie_id": movie_id,
                    "requested_at": get_unix_from_iso(request["createdAt"]),
                    "status": request["status"], # 1 = PENDING, 2 = APPROVED, 3 = DECLINED
                    "updated_at": get_unix_from_iso(request["updatedAt"]),
                    "user_id": user_plex_id,
                    "overseerr_request_id": request["id"]
                },
                "return": "request_id"
            })

            ## add overseerr request ID to entry

            print(f"Added request to movie_requests table for {movie_name} ({movie_year}): request ID {request_id}.")

def process_tv_request(request, shows_table):
    request_media = request["media"]
    tmdbId = request_media["tmdbId"]
    rating_key = request_media["ratingKey"]
    show_id = None
    show_name = None
    show_year = None
    tmdb_show_details = tmdb.get_show(tmdbId)

    
    if rating_key:
        # search for show using rating key
        show_in_table = int(rating_key) in shows_table
    else:
        with get_connection() as conn:
            with conn:
                # search for show using tmdbID
                shows_by_tmdb = _get_table_indexed(conn, "shows", "tmdb_id")
                show_in_table = int(tmdbId) in shows_by_tmdb

    if not show_in_table:
        # the show is not in the shows table.

        # add it:
        with get_connection() as conn:
            with conn:
                show_name = tmdb_show_details["name"]
                show_year = extract_year_from_yyyy_dd_mm(tmdb_show_details["first_air_date"])
                tmdb_poster_url = tmdb_show_details["poster_path"]

                show_id = _add_to_table(conn, {
                    "table": "shows",
                    "data": {
                        "show_name": show_name,
                        "year": show_year, # "first_air_date" is in format 2026-08-02, we just want year.
                        "rating_key": rating_key,
                        "tmdb_poster_url": tmdb_poster_url # not in tautulli, so can't use tautulli_poster_url
                    },
                    "return": "show_id"
                })

                # if show_id is None, that means it was not added to the table because there was a constraint
                # violation, namely that there already exists a show with the same movie_name+year.
                #   - it can be the case that overseerr has the incorrect rating_key.
                if not show_id:
                    # we now need to get the movie_id and rating_key of the entry in the movies table.
                    obtained_show = get_row_from_table(conn, "shows", {"show_name": show_name, "year": show_year})
                    show_id = obtained_show["show_id"]
                    rating_key = obtained_show["rating_key"]

                    # also, add tmdb_id to table entry
                    _update_row_or_ignore(conn,
                        "show_id, tmdb_id",
                        [show_id, tmdb_show_details["id"]],
                        "shows"
                    )

                # wasn't already in table, we added it above.
                print(f"Added show {tmdb_show_details["name"]} ({extract_year_from_yyyy_dd_mm(tmdb_show_details["first_air_date"])}) to shows table. (SHOW ID {show_id}) (RATING KEY {rating_key} {type(rating_key)})")
    else:
        # there is a show in the shows table with the rating key overseerr expected.
        # get the show_name and show_year
        with get_connection() as conn:
            with conn:
                if rating_key:
                    # it was obtained using rating_key
                    obtained_show = get_row_from_table(conn, "shows", {"rating_key": rating_key})
                else:
                    # it was obtained using tmdbId
                    obtained_show = get_row_from_table(conn, "shows", {"tmdb_id": tmdbId})
                show_id = obtained_show["show_id"]
                show_name = obtained_show["show_name"]
                show_year = obtained_show["year"]

                # also, add tmdb_id to table entry
                _update_row_or_ignore(conn,
                    "show_id, tmdb_id",
                    [show_id, tmdb_show_details["id"]],
                    "shows"
                )
    
    # now, if the movie was already in the table, we got its id. if the movie wasn't in the table, we added it and got an id.
    # now add an entry to movie_requests for the obtained movie_id
    with get_connection() as conn:
        with conn:
            # we now need to add entries to seasons table FOR EVERY SEASON IN SHOW.
            # we get season information from tmdb_show_details
            # if every season is already in seasons table, nothing will happen. 
            seasons = tmdb_show_details["seasons"]
            for season in seasons:
                data = {
                    "show_id": show_id,
                    "season_num": season["season_number"],
                    "episode_count": season["episode_count"],
                }

                if season["air_date"] is not None:
                    data["year"] = extract_year_from_yyyy_dd_mm(season["air_date"])

                season_id = _add_to_table(conn, {
                    "table": "seasons",
                    "data": data,
                    "return": "season_id"
                })

            user_plex_id = request["requestedBy"].get("plexId")
            if not user_plex_id:
                # there may be a user in Overseerr who isn't connected to a Plex account (such as a local user).
                # they should still have a Plex ID, and it should be in Tautulli.
                #   - if their Overseerr username matches the username of a Plex user in our users table, the
                #     request will be assigned to them.
                username = request["requestedBy"]["username"]
                if (username):
                    user_plex_id = get_field_from_table(conn, "users", "user_id", {"username": username})

            print(len(request["seasons"]))
            for season in request["seasons"]:
                # for each requested season, get the season id for the seasonNumber of the request, add an entry to season_requests.
                season_num = season["seasonNumber"]

                # get the season_id from the "seasons" table from the entry with the
                # given show_id and season_num combination
                season_id = get_field_from_table(conn, "seasons", "season_id" {"show_id": show_id, "season_num": season_num})
                
                request_id = _add_to_table(conn, {
                    "table": "season_requests",
                    "data": {
                        "season_id": season_id,
                        "show_id": show_id,
                        "requested_at": get_unix_from_iso(season["createdAt"]),
                        "status": season["status"],
                        "updated_at": get_unix_from_iso(season["updatedAt"]),
                        "user_id": user_plex_id,
                        "overseerr_request_id": request["id"]
                    },
                    "return": "request_id"
                })
                print(f"Added season request for {show_name} ({show_year}): season {season_num}, requested by {user_plex_id}, request ID: {request_id}")
                if not request_id:
                    print(f"    season_id: {season_id}, show_id: {show_id}, requested_at: {get_unix_from_iso(season["createdAt"])}, updated_at: {get_unix_from_iso(season["updatedAt"])}, user_id: {user_plex_id}")
                    print(f"    tried to get season id {season_id}. Did get_season_id_from_show_id_season_num(conn, {show_id}, {season_num})")

def get_user_requests(user_id):
    """
    get all requests for a given user (combines movie+tv requests).
    requests will be sorted from most to least recent
    """
    query = """
        SELECT
            'movie' AS type,
            mr.request_id,
            mr.movie_id AS movie_id,
            NULL AS show_id,
            NULL AS season_id,
            m.movie_name AS name,
            m.year AS year,
            NULL AS season_number,
            mr.requested_at,
            mr.status,
            mr.updated_at,
            mr.overseerr_request_id
        FROM movie_requests AS mr
        JOIN movies AS m ON mr.movie_id = m.movie_id
        WHERE mr.user_id = ?

        UNION ALL

        SELECT
            'show' AS type,
            sr.request_id,
            NULL AS movie_id,
            sr.show_id AS show_id,
            sr.season_id AS season_id,
            s.show_name AS name,
            s.year AS year,
            se.season_num AS season_number,
            sr.requested_at,
            sr.status,
            sr.updated_at,
            sr.overseerr_request_id
        FROM season_requests AS sr
        JOIN shows AS s ON sr.show_id = s.show_id
        JOIN seasons AS se ON sr.season_id = se.season_id
        WHERE sr.user_id = ?

        ORDER BY requested_at DESC

    """

    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, (user_id, user_id))
        return [dict(row) for row in cur.fetchall()]


def populate_users_table():
    """
    function to populate the "users" table in the database with an UPSERT operation.
        - gets users from the Tautulli API.
        - if a user is already in the db, info will be updated.
        - users who are in the db but not given by Tautulli will be left alone in the db.

    user table requires the following attributes:
        - user_id, username, friendly_name, is_active, total_duration, last_seen_unix, last_seen_date, last_seen_formatted, last_watched
    ^ ^ These can be obtained from the Tautulli backend
    """

    users = tautulli.get_users()
    
    if not users:
        return

    query = """
            INSERT INTO users (
                user_id, username, friendly_name, email, is_active, is_admin, total_duration, last_seen_unix,
                last_seen_date, last_seen_formatted, last_watched
            ) VALUES (
                :user_id, :username, :friendly_name, :email, :is_active, :is_admin, :total_duration, :last_seen_unix,
                :last_seen_date, :last_seen_formatted, :last_watched
            ) ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                friendly_name = excluded.friendly_name,
                email = excluded.email,
                is_active = excluded.is_active,
                is_admin = excluded.is_admin,
                total_duration = excluded.total_duration,
                last_seen_unix = excluded.last_seen_unix,
                last_seen_date = excluded.last_seen_date,
                last_seen_formatted = excluded.last_seen_formatted,
                last_watched = excluded.last_watched;
            """
    
    with get_connection() as conn:
        print("Adding users to table...")
        conn.executemany(query, users)
        print("Finished adding users.")
        return True
    
    return False

def print_hr():
    """
        will print a horizontal rule line.
    """
    length = 100
    print("="*length, flush=True)

def print_line(msg, indent_level=0):
    """
        will print a line, in between "| .. |" to contain it.
        will add an indent if indent_level=1, or 2 if =2, etc.
    """
    length = 100 # effective length = length-4 ("| " and " |")
    indent = "  "

    msg_space = length - 4 - (len(indent)*indent_level)

    # consider if the message is too long to fit in msg_space
    display_msg = msg
    if len(msg) > msg_space:
        display_msg = msg[0:msg_space]
    
    right_space_length = msg_space - len(display_msg)

    print("| " + (indent*indent_level) + display_msg + (" "*right_space_length) + " |", flush=True)

    # print the rest of the message on another line (if too long to fit in one)
    if display_msg != msg:
        print_line(msg[msg_space:], indent_level)

def print_header(msg):
    """
        will print a message in between two horizontal rule lines
    """
    print_hr()
    print_line(msg)
    print_hr()

def populate_shows():
    with get_connection() as conn:
        with conn:
            users = _get_table(conn, "users")

            print_header("GET SHOWS FROM TAUTULLI")

            # first add all shows from active libraries
            shows = tautulli.get_shows()
            num_shows = len(shows)
            print_line(f"Processing shows from Tautulli /get_library_media_info endpoint:")
            print_line(f"The endpoint returns a list of shows, each of which will be added to contactarr's database.", 1)
            #print(f"Shows: {len(shows)}")
            for i, show in enumerate(shows):
                print_line(f"Processing show ({i+1}/{num_shows})", 2)
                show_name = show["title"]
                year = show["year"]
                rating_key = show.get("rating_key", None)

                # consider shows
                existing_id = _attrs_vals_in_table(conn, {
                    "table": "shows",
                    "data": {
                        "show_name": show_name,
                        "year": year
                    },
                    "return": "show_id"
                })

                if not existing_id:
                    metadata = tautulli.get_metadata(rating_key)
                    if metadata:
                        # this is a version with metadata; add to table
                        existing_id = _add_to_table(conn, {
                            "table": "shows",
                            "data": {
                                "show_name": show_name,
                                "year": year,
                                "rating_key": rating_key,
                                "tautulli_poster_url": show["thumb"]
                            },
                            "return": "show_id"
                        })
                        if show["thumb"] == "/library/metadata/27/thumb/1766335013":
                            print("NOT ANOTHER ONE!!")

                # now consider seasons
                seasons = tautulli.get_seasons(rating_key)
                for j, season in enumerate(seasons):
                    year = season.get("year", "")
                    season_id = _add_to_table(conn, {
                        "table": "seasons",
                        "data": {
                            "show_id": existing_id,
                            "season_num": j,
                            "year": year if year != "" else 0,
                            "rating_key": season["rating_key"]
                        },
                        "return": "season_id"
                    })

                    # record when the season was added (at least, the most recent time it was added)
                    added_at = season.get("added_at")
                    if season_id and season_id != "" and added_at and added_at != "":
                        _add_to_table(conn, {
                            "table": "season_added",
                            "data": {
                                "season_id": season_id,
                                "added_at": added_at
                            }
                        })

            print_line("Finished processing shows from /get_libraries endpoint.")

            # Tautulli may still have data for shows that have been removed from the plex
            # server. we still want to include these.
            print_hr()
            print_line("Processing additional shows from each user from Tautulli /get_history endpoint:")
            print_line("Contactarr has a list of users from Tautulli. For each user, the /get_history endpoint will return"+ 
                        " each episode watched by the user. For each episode, add the show, season, and episode to the database"+
                        " if not already there. Then record the user's watch of the episode.", 1)
            num_users = len(users)
            for i, user in enumerate(users):
                # get the list of shows watched by the user
                user_id = user["user_id"]
                history = tautulli.get_episode_watch_history(user_id)

                if history and isinstance(history, list) and len(history) > 0:
                    num_episodes = len(history)
                    print_line(f"Processing user {user["username"]} ({i+1}/{num_users}) - {num_episodes} episode watches to consider...", 2)
                    for episode in history:
                        # consider each episode. if the show is not in the shows table,
                        # but does not Tautulli has no metadata for it, don't add it yet.
                        #   - (we want to get the TVDB ID)
                        #

                        # show
                        show_name = episode["grandparent_title"]
                        show_rating_key = episode["grandparent_rating_key"]
                        show_metadata = tautulli.get_metadata(show_rating_key)
                        # season
                        season_number = episode["parent_media_index"]
                        season_rating_key = episode["parent_rating_key"]
                        #episode
                        episode_name = episode["title"]
                        episode_number = episode["media_index"]
                        episode_year = episode["year"]
                        episode_rating_key = episode["rating_key"]
                        
                        #  consider show
                        #print(f"Considering show {show_name}")
                        show_year = None
                        show_id = None
                        if show_metadata and show_metadata.get("year"):
                            show_year = show_metadata["year"]
                        else:
                            # we need to know the year of the show. if this is the first ep
                            # of the first season, the episode's year is the same as the show's,
                            # so we can use that.
                            if int(season_number) == 1 and int(episode_number) == 1:
                                show_year = episode_year
                            # else:
                                # we don't know the show year therefore all we know is the name and rating key,
                                # and two instances of the same show may have different rating keys in
                                # tautulli. do not add to the table
                        
                        if show_year:
                            # we know the name+year of the show, we can add it IF it isn't already there.
                            existing_id = _attrs_vals_in_table(conn, {
                                "table": "shows",
                                "data": {
                                    "show_name": show_name,
                                    "year": show_year
                                },
                                "return": "show_id"
                            })

                            if not existing_id:
                                existing_id = _add_to_table(conn, {
                                    "table": "shows",
                                    "data": {
                                        "show_name": show_name,
                                        "year": show_year,
                                        "rating_key": show_rating_key,
                                        "tautulli_poster_url": show_metadata.get("thumb") if show_metadata else None
                                    },
                                    "return": "show_id"
                                })
                        else:
                            # we don't know the name+year of the show, we cannot add it yet.
                            # that being said, if there is a show in the table with the same name+rating_key
                            # we can accept that as being the same show.
                            existing_id = _attrs_vals_in_table(conn, {
                                "table": "shows",
                                "data": {
                                    "show_name": show_name,
                                    "rating_key": show_rating_key
                                },
                                "return": "show_id"
                            })

                        # if the existing_id is still None by this point, there is no way to figure out the show's name+year
                        # list this show as a failure and move on.
                        if not existing_id:
                            #print("NO EXISTING ID")
                            continue
                        
                        # show is now (or already was) in the shows table. now consider season.
                        season_id = _attrs_vals_in_table(conn, {
                            "table": "seasons",
                            "data": {
                                "show_id": existing_id,
                                "season_num": season_number
                            },
                            "return": "season_id"
                        })
                        if not season_id:
                            # season not in table - add it.
                            season_id = _add_to_table(conn, {
                                "table": "seasons",
                                "data": {
                                    "show_id": existing_id,
                                    "season_num": season_number,
                                    "rating_key": season_rating_key
                                }
                            })

                        # now consider episode.
                        episode_id = _attrs_vals_in_table(conn, {
                            "table": "episodes",
                            "data": {
                                "season_id": season_id,
                                "show_id": existing_id,
                                "number": episode_number,
                                "name": episode_name
                            }
                        })
                        if not episode_id:
                            episode_id = _add_to_table(conn, {
                                "table": "episodes",
                                "data": {
                                    "season_id": season_id,
                                    "show_id": existing_id,
                                    "rating_key": episode_rating_key,
                                    "number": episode_number,
                                    "name": episode_name
                                },
                                "return": "episode_id"
                            })

                        # now add the episode watch to the table
                        _add_to_table(conn, {
                            "table": "episode_watches",
                            "data": {
                                "user_id": user_id,
                                "episode_id": episode_id,
                                "started": episode["started"],
                                "stopped": episode["stopped"],
                                "pause_duration": episode["paused_counter"]
                            }
                        })

            print_line("Finished processing shows from /get_history endpoint.")
            print_hr()

def populate_movies():
    with get_connection() as conn:
        with conn:
            users = _get_table(conn, "users")

            print_header("GET MOVIES FROM TAUTULLI")

            # first add all movies from active libraries
            movies = tautulli.get_movies()
            num_movies = len(movies)
            print_line(f"Processing movies from Tautulli /get_library_media_info endpoint:")
            print_line(f"The endpoint returns a list of movies, each of which will be added to contactarr's database.", 1)
            for i, movie in enumerate(movies):
                print_line(f"Processing movie ({i+1}/{num_movies})", 2)
                in_table = _attrs_vals_in_table(conn, {
                    "table": "movies",
                    "data": {
                        "movie_name": movie["title"],
                        "year": movie["year"]
                    }
                })

                movie_id = None
                if not in_table:
                        # get tmdb_ID from TMDb
                        

                        movie_id = _add_to_table(conn, {
                            "table": "movies",
                            "data": {
                                "movie_name": movie["title"],
                                "year": movie["year"],
                                "rating_key": movie["rating_key"],
                                "tautulli_poster_url": movie["thumb"]
                            },
                            "return": "movie_id"
                        })

                # record when the movie was added (at least, the most recent time it was added)
                added_at = movie.get("added_at")
                if movie_id and added_at and added_at != "":
                    _add_to_table(conn, {
                        "table": "movie_added",
                        "data": {
                            "movie_id": movie_id,
                            "added_at": added_at
                        }
                    })

            # Tautulli may still have data for movies that have been removed from the plex
            # server. we still want to include those.
            print_hr()
            print_line("Processing additional movies from each user from Tautulli /get_history endpoint:")
            print_line("Contactarr has a list of users from Tautulli. For each user, the /get_history endpoint will return" +
                        " each movie watched by the user. Add each one to the database, if not already there. Then record the" +
                        " user's watch of the movie", 1)
            num_users = len(users)
            for i, user in enumerate(users):
                # get the list of movies watched by the user
                history = tautulli.get_movie_watch_history(user["user_id"])

                if history and isinstance(history, list) and len(history) > 0:
                    num_movies = len(history)
                    print_line(f"Processing user {user["username"]} ({i+1}/{num_users}) - {num_movies} movie watches to consider...", 2)
                    for movie in history:
                        # see if the movie is already in the the movies table.
                        # may not have the same rating_key, tmdb_id may be null.
                        # instead search for movie_name+year combination.
                        in_table = _attrs_vals_in_table(conn, {
                            "table": "movies",
                            "data": {
                                "movie_name": movie["title"],
                                "year": movie["year"]
                            }
                        })
                        
                        if not in_table:
                            metadata = tautulli.get_metadata(movie["rating_key"])
                            key = (movie["title"], movie["year"])

                            # add the movie to the table
                            _add_to_table(conn, {
                                "table": "movies",
                                "data": {
                                    "movie_name": movie["title"],
                                    "year": movie["year"],
                                    "rating_key": movie["rating_key"],
                                    "tautulli_poster_url": movie["thumb"]
                                }
                            })

                        # at the same time, we want to record the user's watch of the movie in movie_watches.
                        tmp = get_row_from_table(conn, "movies", {"movie_name": movie["title"], "year": movie["year"]})
                        movie_id = tmp["movie_id"]
                        user_id = user["user_id"]
                        started = movie["started"]
                        stopped = movie["stopped"]
                        pause_duration = movie["paused_counter"]
                        _add_to_table(conn, {
                            "table": "movie_watches",
                            "data": {
                                "user_id": user_id,
                                "movie_id": movie_id,
                                "started": started,
                                "stopped": stopped,
                                "pause_duration": pause_duration
                            }
                        })

            print_line("Finished processing movies from /get_history endpoint.")
            print_hr()

def get_users():
    with get_connection() as conn:
        users = _get_table(conn, "users")
    return users

def get_admins():
    admins = []
    with get_connection() as conn:
        users = _get_table(conn, "users")
        admins = [u for u in users if u['is_admin'] == 1]
    return admins

def set_admins(lst):
    """update list of admins"""
    # to do this, first set is_admin = 0 for all users
    with get_connection() as conn:
        conn.execute("UPDATE users SET is_admin=0")
        # now set is_admin = 1 for each user in lst
        for u in lst:
            conn.execute("UPDATE users SET is_admin=1 WHERE username = ?", (u["username"],))
    return True

def remove_admin(username):
    with get_connection() as conn:
        conn.execute("UPDATE users SET is_admin=0 WHERE username = ?", (username,))
        return True
    return False
    
def add_admin(username):
    with get_connection() as conn:
        conn.execute("UPDATE users SET is_admin=1 WHERE username = ?", (username,))
        return True
    return False

def get_unsubscribe_lists():
    """
    returns an array of each table in the database
    whose name ends with "_unsubscribe_list".
    * JOINS to the `users` table to get the username and
      friendly_name for each user.

    resulting array has structure:
    [
        {
            'table_name': '...',
            'rows': [
                {'user_id': ..., 'username': ..., 'friendly_name': ...},
                ...
            ]
        },
        {
            ...
        }
    ]
    """

    with get_connection() as conn:
        cur = conn.cursor()

        # get table names
        cur.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name LIKE '%_unsubscribe_list'
        """)
        table_names = [row[0] for row in cur.fetchall()]

        # fetch rows from each table
        result = []
        for table_name in table_names:
            cur.execute(f'''
                SELECT 
                    u.user_id,
                    usr.username,
                    usr.friendly_name
                FROM "{table_name}" u
                JOIN users usr ON u.user_id = usr.user_id
            ''')
            rows = cur.fetchall()
            result.append({
                'table_name': table_name,
                'rows': [
                    {
                        'user_id': row[0],
                        'username': row[1],
                        'friendly_name': row[2]
                    }
                    for row in rows
                ]
            })

        return result

def set_unsubscribe_list(table_name: str, user_ids: list):
    """
    replaces all rows in a given unsubscribe list table.
    expects a list in JSON format:
    {
        "table_name": "newly_released_Content_updates_unsubscribe_list",
        "user_ids": [..., ..., ...]
    }
    """
    
    if not table_name or not table_name.endswith('_unsubscribe_list'):
        return False

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = ?
        """, (table_name,))
        if not cur.fetchone():
            return False
        
        # clear existing table!
        cur.execute(f'DELETE FROM "{table_name}"')

        current_time = int(time.time())
        for user_id in user_ids:
            cur.execute(f'''
                INSERT INTO "{table_name}" (user_id, added_at)
                VALUES (?, ?)
            ''', (user_id, current_time))

        conn.commit()
    
    return True


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS shows (
                show_id INTEGER PRIMARY KEY,
                show_name TEXT,
                year INTEGER,
                rating_key INTEGER,
                tmdb_id INTEGER UNIQUE,
                tmdb_poster_url TEXT,
                tautulli_poster_url TEXT,
                UNIQUE(show_name, year)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS seasons (
                season_id INTEGER PRIMARY KEY,
                show_id INTEGER NOT NULL REFERENCES shows(show_id),
                season_num INTEGER NOT NULL,
                episode_count INTEGER,
                year INTEGER,
                rating_key INTEGER,
                UNIQUE(show_id,season_num)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS season_added (
                season_id INTEGER REFERENCES seasons(season_id),
                added_at INTEGER NOT NULL,
                UNIQUE(season_id, added_at)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                episode_id INTEGER PRIMARY KEY,
                season_id INTEGER NOT NULL REFERENCES seasons(season_id),
                show_id INTEGER NOT NULL,
                rating_key INTEGER,
                number INTEGER NOT NULL,
                name TEXT NOT NULL,
                UNIQUE(season_id, number, name)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS season_requests (
                request_id INTEGER PRIMARY KEY,
                season_id INTEGER NOT NULL REFERENCES seasons(season_id),
                show_id INTEGER NOT NULL,
                requested_at INTEGER NOT NULL,
                status INTEGER NOT NULL,
                updated_at INTEGER,
                user_id INTEGER NOT NULL REFERENCES users(user_id),
                UNIQUE(season_id, requested_at, user_id)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS episode_watches (
                watch_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(user_id),
                episode_id INTEGER NOT NULL REFERENCES episodes(episode_id),
                started INTEGER NOT NULL,
                stopped INTEGER NOT NULL,
                pause_duration INTEGER NOT NULL,
                CHECK (started < stopped),
                UNIQUE(user_id, episode_id, started, stopped, pause_duration)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                friendly_name TEXT,
                email TEXT,
                is_active INTEGER,
                is_admin INTEGER DEFAULT 0,
                total_duration TEXT,
                last_seen_unix INTEGER,
                last_seen_formatted TEXT,
                last_seen_date TEXT,
                last_watched TEXT
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                movie_id INTEGER PRIMARY KEY,
                movie_name INTEGER,
                year INTEGER,
                rating_key INTEGER,
                tmdb_id INTEGER UNIQUE,
                tmdb_poster_url TEXT,
                tautulli_poster_url TEXT,
                UNIQUE(movie_name, year)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS movie_added (
                movie_id INTEGER REFERENCES movies(movie_id),
                added_at INTEGER NOT NULL,
                UNIQUE(movie_id, added_at)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS movie_requests (
                request_id INTEGER PRIMARY KEY,
                movie_id INTEGER NOT NULL REFERENCES movies(movie_id),
                requested_at INTEGER NOT NULL,
                status INTEGER NOT NULL,
                updated_at INTEGER NOT NULL,
                user_id INTEGER,
                tmdb_poster_url TEXT,
                UNIQUE(movie_id, requested_at, user_id)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS movie_watches (
                watch_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(user_id),
                movie_id INTEGER NOT NULL REFERENCES movies(movie_id),
                started INTEGER NOT NULL,
                stopped INTEGER NOT NULL,
                pause_duration INTEGER NOT NULL,
                CHECK (started < stopped),
                UNIQUE(user_id, movie_id, started, stopped, pause_duration)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS newly_released_content_updates_unsubscribe_list (
                user_id INTEGER NOT NULL REFERENCES users(user_id),
                added_at INTEGER NOT NULL DEFAULT (unixepoch())
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS system_updates_unsubscribe_list (
                user_id INTEGER NOT NULL REFERENCES users(user_id),
                added_at INTEGER NOT NULL DEFAULT (unixepoch())
            );
        """)

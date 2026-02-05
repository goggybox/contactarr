
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
from pathlib import Path
from backend.api import tautulli
from backend.api import overseerr
from backend.api import config

DB_PATH = Path(__file__).parent / "contactarr.db"

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

def _get_movie_id_from_rating_key(conn, rating_key):
    """
    get a movie's id from its rating_key
    """
    row = conn.execute(
        "SELECT movie_id FROM movies WHERE rating_key = ? LIMIT 1",
        (rating_key,)
    ).fetchone()
    return row["movie_id"] if row else None

def _get_movie_id_from_name_year(conn, movie_name, year):
    row = conn.execute(
        "SELECT movie_id FROM movies WHERE movie_name = ? AND year = ?",
        (movie_name, year,)
    ).fetchone()
    return row["movie_id"] if row else None

def _get_movie_from_db_from_rating_key(conn, rating_key):
    row = conn.execute(
        "SELECT * FROM movies WHERE rating_key = ?",
        (int(rating_key),)
    ).fetchone()
    if row is None:
        return None
    return dict(row)
8
def _get_show_id_from_rating_key(conn, rating_key):
    """
    get a show's id from its rating_key
    """
    row = conn.execute(
        "SELECT show_id FROM shows WHERE rating_key = ? LIMIT 1",
        (rating_key,)
    ).fetchone()
    return row["show_id"] if row else None

def _get_season_id_from_rating_key(conn, rating_key):
    """
    get a season's id from its rating_key
    """
    row = conn.execute (
        "SELECT season_id FROM seasons WHERE rating_key = ? LIMIT 1",
        (rating_key,)
    ).fetchone()
    return row["season_id"] if row else None

def _get_episode_id_from_rating_key(conn, rating_key):
    """
    get an episode's id from its rating_key
    """
    row = conn.execute (
        "SELECT episode_id FROM episodes WHERE rating_key = ? LIMIT 1",
        (rating_key,)
    ).fetchone()
    return row["episode_id"] if row else None

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
        return True
    print("Overseerr API key not valid, cancelling link.")
    return False

"""
TODO:
prefer to get posters from Tautulli. metadata command returns data with "thumb" URI, can use that
in a "pms_image_proxy" command to get the poster.

need to link overseerr, and process all requests. add movies/shows from requests that were not
added from tautulli. WOULD BE BETTER to NOT add all tmdb poster urls to database right now,
very slow operation - and many movies on tautulli may no longer be on overseerr.

"""

def get_unix_from_iso(iso):
    dt = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S.%fZ")
    dt = dt.replace(tzinfo=timezone.utc)
    unix = int(dt.timestamp())
    return unix

def process_overseerr_requests():
    cnf = config.get_overseerr_config()
    last_process = cnf.get('last_requests_process', 0) # will ignore requests from before the last processing

    requests = overseerr.get_requests()
    
    with get_connection() as conn:
        with conn:
            # existing tables to compare against
            movies_table = _get_table_indexed(conn, "movies", "tmdb_id")
            # shows_table = _get_table(conn, "shows", "")

            # consider each request
            print(len(movies_table))
            # for request in requests:
            #     if get_unix_from_iso(request["updatedAt"] < last_process):
            #         # this request will have been processed as part of a previous scan
            #         continue
                
            #     # is it a movie or show?
            #     if request["type"] == "movie":
            #         # movie
            #         process_movie_request(request, movies_table)
            #     else:
            #         # tv
            #         process_tv_request(request, shows_table)

def process_movie_request(request, movies_table):
    # table fields for a request:
        # request_id
        # movie_id
        # requested_at
        # status
        # updated_at
        # user_id
    # relevant table fields for a movie:
        # tmdb_poster_url
        # tautulli_poster_url
        # movie_id
        # tmdb_id
        # rating_key

    media = request["media"]
    tmdbId = media["tmdbId"]
    
    # get movie from existing table
    print(media)
    movie_in_table = movies_table.get(tmdbId)
    print(movie_in_table)

    # if not movie_in_table:
        # the movie may still be in the table, just may not have its tmdbId so couldn't be found.
        # instead search for name+year.

    
    # if the movie doesn't have a tautulli_poster_url, and doesn't have
    # a tmdb_poster_url, add a tmdb_poster_url. (from /movie/{tmdbId}/ endpoint)
    



# def get_movie_poster_url_and_cache(rating_key: str):
#     with get_connection() as conn:
#         movie = _get_movie_from_db_from_rating_key(conn, rating_key)
#         if movie:
#             if not movie.get("tmdb_poster_url"):
#                 # we don't have it in the db yet.
#                 poster_url = overseerr.get_movie_poster_url(rating_key)
#                 conn.execute(
#                     "UPDATE movies SET tmdb_poster_url = ? WHERE rating_key = ?",
#                     (poster_url, rating_key)
#                 )
#                 conn.commit()
#                 return poster_url
#             else:
#                 return movie["tmdb_poster_url"]
#         return None
        

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
                                        "tautulli_poster_url": show["thumb"]
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
                                "rating_key": episode_rating_key,
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
                        movie_id = _get_movie_id_from_name_year(conn, movie["title"], movie["year"])
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
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name LIKE '%_unsubscribe_list'
        """)
        res = [row[0] for row in cur.fetchall()]
        return res

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS shows (
                show_id INTEGER PRIMARY KEY,
                show_name TEXT,
                year INTEGER,
                rating_key INTEGER NOT NULL,
                tvdb_id INTEGER UNIQUE,
                tvdb_poster_url TEXT,
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
                rating_key INTEGER UNIQUE NOT NULL,
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
                rating_key INTEGER NOT NULL,
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
                user_id INTEGER NOT NULL REFERENCES users(user_id)
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
                user_id INTEGER NOT NULL REFERENCES users(user_id)
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
                added_at INTEGER NOT NULL
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS request_for_unreleased_content_unsubscribe_list (
                user_id INTEGER NOT NULL REFERENCES users(user_id),
                added_at INTEGER NOT NULL
            );
        """)

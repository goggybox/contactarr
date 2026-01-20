
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

def _attr_val_in_table(conn, attr, val, name):
    """
    determine whether or not a given attribute value is in a table.
    """
    cursor = conn.execute(f"SELECT 1 FROM {name} WHERE {attr}={val} LIMIT 1")
    return cursor.fetchone() is not None

def _attrs_vals_in_table(conn, attrs, vals, name):
    """
    determine whether or not a given combination of attribute,value pairs are in a table.
    """
    query = f"""
        SELECT 1
        FROM {name}
        WHERE {attrs[0]} = ?
        AND {attrs[1]} = ?
        LIMIT 1
    """

    cursor = conn.execute(query, (vals[0], vals[1]))
    return cursor.fetchone() is not None

def _add_to_table(conn, attrs, vals, name):
    """
    attrs should be a string of attribute names separated by commas ("attr1, attr2, attr3")
    vals  should be a list of values for each corresponding attribute ([12, 15])
    name  should be the name of the table
    """
    placeholders = ", ".join("?" for _ in vals)
    conn.execute(
        f"INSERT INTO {name} ({attrs}) VALUES ({placeholders})",
        vals
    )
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


def _add_or_ignore_to_table(conn, attrs, vals, name):
    """
    same as _add_to_table(), but entries are not added if one already exists with the given values
    """
    placeholders = ", ".join("?" for _ in vals)
    conn.execute(
        f"INSERT OR IGNORE INTO {name} ({attrs}) VALUES ({placeholders})",
        vals
    )
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
        # populate_movies()
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
            process_movie_request(requests[3], movies_table)
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

def populate_shows():
    with get_connection() as conn:
        with conn:
            users = _get_table(conn, "users")

            # first add all shows from active libraries
            shows = tautulli.get_shows()
            print(f"Shows: {len(shows)}")
            shows_to_add = {}
            for show in shows:
                # CREATE TABLE IF NOT EXISTS shows (
                #     show_id INTEGER PRIMARY KEY,
                #     show_name TEXT,
                #     year INTEGER,
                #     rating_key INTEGER NOT NULL,
                #     tvdb_id INTEGER UNIQUE
                # );
                show_name = show["title"]
                year = show["year"]
                rating_key = show.get("rating_key", None)

                in_table = _attrs_vals_in_table(conn,
                    ["show_name", "year"],
                    [show_name, year],
                    "shows"
                )

                if not in_table:
                    metadata = tautulli.get_metadata(rating_key)
                    if not metadata:
                        # no metadata, don't add yet in case version with metadata is found
                        key = (show_name, year)
                        if not shows_to_add.get(key):
                            shows_to_add[key] = show
                    else:
                        # this is a version with metadata; add to table
                        _add_to_table(conn,
                            "show_name, year, rating_key, tautulli_poster_url",
                            [show_name, year, rating_key, show["thumb"]],
                            "shows"
                        )
            print(f"Shows to add: {len(shows_to_add)}")
            print(shows_to_add)

def populate_movies():
    with get_connection() as conn:
        with conn:
            users = _get_table(conn, "users")

            # first add all movies from active libraries
            movies = tautulli.get_movies()
            print(f"Movies: {len(movies)}")
            movies_to_add = {}
            for movie in movies:
                in_table = _attrs_vals_in_table(conn,
                    ["movie_name", "year"],
                    [movie["title"], movie["year"]],
                    "movies"
                )

                if not in_table:
                    metadata = tautulli.get_metadata(movie["rating_key"])
                    if not metadata:
                        # no metadata, don't add yet in case version with metadata is found
                        key = (movie["title"], movie["year"])
                        if not movies_to_add.get(key):
                            movies_to_add[key] = movie
                    else:
                        _add_to_table(conn,
                            "movie_name, year, rating_key, tautulli_poster_url",
                            [movie["title"], movie["year"], movie["rating_key"], movie["thumb"]],
                            "movies"
                        )
            print(f"Movies to add: {len(movies_to_add)}")
            
            # Tautulli may still have data for movies that have been removed from the plex
            # server. we still want to include those.
            for user in users:
                # get the list of movies watched by the user
                history = tautulli.get_movie_watch_history(user["user_id"])

                if history and isinstance(history, list) and len(history) > 0:
                    for movie in history:
                        # see if the movie is already in the the movies table.
                        # may not have the same rating_key, tmdb_id may be null.
                        # instead search for movie_name+year combination.
                        in_table = _attrs_vals_in_table(conn,
                            ["movie_name", "year"],
                            [movie["title"], movie["year"]],
                            "movies"
                        )
                        
                        if not in_table:
                            metadata = tautulli.get_metadata(movie["rating_key"])
                            key = (movie["title"], movie["year"])
                            if not metadata:
                                if not movies_to_add.get(key):
                                    movies_to_add[key] = movie

                            if movies_to_add.get(key):
                                movies_to_add.pop(key, None)

                            # add the movie to the table
                            _add_to_table(conn,
                                "movie_name, year, rating_key, tautulli_poster_url",
                                [movie["title"], movie["year"], movie["rating_key"], movie["thumb"]],
                                "movies"
                            )

                        # at the same time, we want to record the user's watch of the movie in movie_watches.
                        movie_id = _get_movie_id_from_name_year(conn, movie["title"], movie["year"])
                        user_id = user["user_id"]
                        started = movie["started"]
                        stopped = movie["stopped"]
                        pause_duration = movie["paused_counter"]
                        _add_to_table(conn,
                            "user_id, movie_id, started, stopped, pause_duration",
                            [movie_id, user_id, started, stopped, pause_duration],
                            "movie_watches"
                        )

            # if there are any movies still in movies_to_add, we will add them without metadata.
            print(f"Movies left to add: {len(movies_to_add)}")
            print(f"Adding without metadata...")
            if len(movies_to_add) > 0:
                for movie in movies_to_add.values():
                    _add_or_ignore_to_table(conn,
                        "movie_name, year, rating_key",
                        [movie["title"], movie["year"], movie["rating_key"]],
                        "movies"
                    )            

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
                rating_key INTEGER UNIQUE NOT NULL,
                UNIQUE(show_id,season_num,episode_count)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS season_added (
                season_id INTEGER REFERENCES seasons(season_id),
                added_at INTEGER NOT NULL
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
                added_at INTEGER NOT NULL
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

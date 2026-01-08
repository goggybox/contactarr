
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
from pathlib import Path
from backend.api import tautulli

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

def _get_show_id_from_rating_key(conn, rating_key):
    """
    get a show's id from its rating_key
    """
    row = conn.execute(
        "SELECT show_id FROM shows WHERE rating_key = ? LIMIT 1",
        (rating_key,)
    )
    return row["show_id"] if row else None

def _get_season_id_from_rating_key(conn, rating_key):
    """
    get a season's id from its rating_key
    """
    row = conn.execute (
        "SELECT season_id FROM seasons WHERE rating_key = ? LIMIT 1",
        (rating_key,)
    )
    return row["season_id"] if row else None

def _get_episode_id_from_rating_key(conn, rating_key):
    """
    get an episode's id from its rating_key
    """
    row = conn.execute (
        "SELECT episode_id FROM episodes WHERE rating_key = ? LIMIT 1",
        (rating_key,)
    )
    return row["episode_id"] if row else None

def _attr_val_in_table(conn, attr, val, name):
    """
    determine whether or not a given attribute value is in a table.
    """
    cursor = conn.execute(f"SELECT 1 FROM {name} WHERE {attr}={val} LIMIT 1")
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
    populate_users_table()
    return True

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
                user_id, username, friendly_name, is_active, total_duration, last_seen_unix,
                last_seen_date, last_seen_formatted, last_watched
            ) VALUES (
                :user_id, :username, :friendly_name, :is_active, :total_duration, :last_seen_unix,
                :last_seen_date, :last_seen_formatted, :last_watched
            ) ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                friendly_name = excluded.friendly_name,
                is_active = excluded.is_active,
                total_duration = excluded.total_duration,
                last_seen_unix = excluded.last_seen_unix,
                last_seen_date = excluded.last_seen_date,
                last_seen_formatted = excluded.last_seen_formatted,
                last_watched = excluded.last_watched;
            """
    
    with get_connection() as conn:
        conn.executemany(query, users)
        return True
    
    return False

def populate_shows():
    """
    function to populate the "shows", "seasons", "episodes", and "episode_watches" tables in the database.
        - loop over the users in the users table.
            - get the list of every episode watched by the user with "/get_history" endpoint.
            - for each episode:
                - if the grandparent_rating_key is already in the "shows" table, carry on. otherwise we must add the show:
                    - add new entry to show table: (grandparent_rating_key, )
    """

    # get every user from users table
    with get_connection() as conn:
        users = _get_table(conn, "users")
        
        # loop through every user
        for user in users:
            # get the list of episodes watched by the user
            history = tautulli.get_episode_watch_history(user["user_id"])

            # loop through each episode watch
            if history and isinstance(history, list) and len(history) > 0:
                for episode in history:
                    show_rating_key = episode["grandparent_rating_key"]

                    # if the show isn't already in the shows table, add it.
                    _add_or_ignore_to_table(conn,
                        "show_name, rating_key",
                        [episode["grandparent_title"], show_rating_key],
                        "shows"
                    )

                    show_id = _get_show_id_from_rating_key(conn, show_rating_key)
                    season_num = episode["parent_title"].split()[1] # episode["parent_title"] is of format "Season 1"

                    # if this season isn't already in the season table, add it.
                    #   - cannot add episode_count or added_at values from this data, will add later.
                    _add_or_ignore_to_table(conn,
                        "show_id, season_num, rating_key",
                        [show_id, season_num, episode["parent_rating_key"]],
                        "seasons"
                    )

                    season_id = _get_season_id_from_rating_key(conn, season_rating_key)

                    # if this season isn't already in the episode table, add it.
                    _add_or_ignore_to_table(conn,
                        "season_id, rating_key, number, name",
                        [season_id, episode["rating_key"], episode["media_index"], episode["title"]],
                        "episodes"
                    )

                    episode_id = _get_episode_id_from_rating_key(conn, episode_rating_key)



        # still need to populate seasons' episode_count and added_at values


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS shows (
                show_id INTEGER PRIMARY KEY,
                show_name TEXT,
                rating_key INTEGER NOT NULL UNIQUE,
                tvdb_id INTEGER UNIQUE
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS seasons (
                season_id INTEGER PRIMARY KEY,
                show_id INTEGER NOT NULL REFERENCES shows(show_id),
                season_num INTEGER NOT NULL,
                episode_count INTEGER NOT NULL,
                added_at INTEGER NOT NULL,
                rating_key INTEGER UNIQUE NOT NULL
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                episode_id INTEGER PRIMARY KEY,
                season_id INTEGER NOT NULL REFERENCES seasons(season_id),
                rating_key INTEGER NOT NULL,
                number INTEGER NOT NULL,
                name TEXT NOT NULL
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
                CHECK (started < stopped)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                friendly_name TEXT,
                email TEXT,
                is_active INTEGER,
                total_duration TEXT,
                last_seen_unix INTEGER,
                last_seen_formatted TEXT,
                last_seen_date TEXT,
                last_watched TEXT
            );
        """)

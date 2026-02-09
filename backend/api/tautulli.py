
# # -----------------------------contactarr------------------------------
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

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from backend.api.cache import apiGet, clearCache
from backend.api import config
from urllib.parse import urlencode

def get_poster_image(tautulli_poster_url: str) -> bytes | None:
    if not tautulli_poster_url:
        return None

    cnf = config.get_tautulli_config()
    api_key = cnf.get("api_key")
    api_url = cnf.get("api_url")

    if not api_key or not api_url:
        return None
    params = {
        "apikey": api_key,
        "cmd": "pms_image_proxy",
        "img": tautulli_poster_url,
    }

    try:
        r = requests.get(api_url, params=params, timeout=15)
        if r.status_code == 200:
            return r.content
    except Exception:
        pass

    return None

def getFromAPI(cmd, args=None, forceFresh=False):
    """
    use the TAUTULLI_API_KEY and TAUTULLI_API_URL fields from the .env file
    to contact the Tautulli api.
    """
    cnf = config.get_tautulli_config()
    api_key = cnf['api_key']
    api_url = cnf['api_url']

    if not api_key or not api_url:
        return None

    url = f"{api_url}"
    params = {
        'apikey': api_key,
        'cmd': cmd
    }

    # add args if given
    if args != None:
        for a in args:
            for k, v in a.items():
                params[k] = v

    try:
        data = apiGet(url=api_url, params=params, forceFresh=forceFresh)
        
        if data:
            if data["response"]["result"] != "error":
                return data["response"]
            else:
                return None
    except Exception as e:
        return None

def alive():
    """check if the tautulli instance is alive"""
    return True if getFromAPI("get_libraries") != None else False

def validate_apikey():
    response = getFromAPI("get_libraries", forceFresh=True)
    if response == None:
        return False
    elif response.get("result") and response["result"] == "success":
        return True

def apikey():
    """get the api key of the Tautulli instance from the .env file"""
    cnf = config.get_tautulli_config()
    api_key = cnf['api_key']
    return api_key

def set_apikey(val: str):
    """set the api key of the Tautulli instance to the .env file"""
    return config.set_config_value("TAUTULLI_API_KEY", val)

def url():
    """get the url of the Tautulli instance's API from the .env file"""
    cnf = config.get_tautulli_config()
    url = cnf['api_url']
    return url

def set_url(val: str):
    """set the url of the Tautulli instance's API to the .env file"""
    return config.set_config_value("TAUTULLI_API_URL", val)

def get_movies():
    # get library sections
    sections = getFromAPI("get_libraries")
    if not sections:
        return None
    
    section_ids = [section["section_id"] for section in sections["data"] if section["section_type"] == "movie"]

    # for each section, get the movies, and collect them all together
    total_movies = []
    for sec in section_ids:
        partial = getFromAPI("get_library_media_info", [{"section_id": sec}, {"length": 999999999}, {"order_column": "added_at"}, {"order_dir": "desc"}])
        if partial:
            total_movies.extend(partial["data"]["data"])

    return total_movies

def get_shows():
    sections = getFromAPI("get_libraries")
    if not sections:
        return None

    section_ids = [section["section_id"] for section in sections["data"] if section["section_type"] == "show"]

    # for each section, get the shows, and collect them all together
    total_shows = []
    for sec in section_ids:
        partial = getFromAPI("get_library_media_info", [{"section_id": sec}, {"length": 999999999}, {"order_column": "added_at"}, {"order_dir": "desc"}])
        if partial:
            total_shows.extend(partial["data"]["data"])

    return total_shows

def get_seasons(rating_key):
    seasons = getFromAPI("get_library_media_info", [{"rating_key": rating_key}])

    if seasons and seasons.get("data") and seasons["data"].get("data"):
        return seasons["data"]["data"]


def get_users():
    # get the first 5 attributes from the /get_users endpoint
    users = getFromAPI("get_users", forceFresh=True)
    if not users or not users['data']:
        return

    user_array = users['data']
    fields_to_keep = {"user_id", "username", "friendly_name", "email", "is_active", "is_admin"}
    filtered_users = [
        {k: v for k, v in u.items() if k in fields_to_keep}
        for u in user_array
    ]

    # filter array to remove Local user or user_id 0
    filtered_users = [u for u in filtered_users if u['user_id'] != 0 and u['username'] != "Local"]

    # get the remaining attributes from the /get_history endpoint
    for u in filtered_users:
        u['total_duration'] = ""
        u['last_seen_unix'] = ""
        u['last_seen_formatted'] = ""
        u['last_seen_date'] = ""
        u['last_watched'] = ""

        user = getFromAPI("get_history", [{"user_id": int(u['user_id'])}, {"order_column": "stopped"}, {"order_dir": "desc"}, {"length": 1}])
        if user:
            # total duration
            if user['data']['total_duration']:
                u['total_duration'] = user['data']['total_duration']
            
            # last_seen and last_watched
            if user['data']['data'] and len(user['data']['data']) > 0:
                most_recent = user['data']['data'][0]
                # if it is a tv show:
                #   - media_type: 'episode'
                #   - full_title: 'BoJack Horseman - Nice While It Lasted'
                #   - parent_title: 'Season 6'
                #   - media_index: 16 (episode number)
                # if it is a movie:
                #   - media_type: 'movie'
                #   - full_title: 'Sister Act'
                media_type = most_recent['media_type']
                title = most_recent['full_title']
                if media_type != 'movie':
                    # add e.g. S06E16 for tv show episode
                    season = most_recent['parent_title'].split()[1]
                    season = "0"+season if len(season) == 1 else season
                    episode = str(most_recent['media_index'])
                    episode = "0"+episode if len(episode) == 1 else episode
                    tmp = f"(S{season}E{episode}) -"
                    title = title.split("-")
                    title.insert(1, tmp)
                    title = "".join(title)

                # add data to user
                u['last_watched'] = title
                u['last_seen_unix'] = most_recent['stopped']

                # last_seen_formatted and last_seen_date
                dt = datetime.fromtimestamp(most_recent['stopped'])
                # format date
                now = datetime.now()
                diff = now - dt
                seconds = int(diff.total_seconds())
                intervals = [
                    ("year", 31536000),
                    ("month", 2592000),
                    ("week", 604800),
                    ("day", 86400),
                    ("hour", 3600),
                    ("minute", 60)
                ]
                if seconds < 60:
                    formatted_dt = "just now"
                for name, unit_seconds in intervals:
                    value = seconds // unit_seconds
                    if value >= 1:
                        formatted_dt = f"{value} {name}{'s' if value != 1 else ''} ago"
                        break

                u['last_seen_formatted'] = formatted_dt
                u['last_seen_date'] = dt.strftime("%H:%M, %a %d %b")
    
    filtered_users = sorted(
        filtered_users,
        key = lambda u: u.get("last_seen_unix") or 0,
        reverse=True
    )

    return filtered_users

def get_episode_watch_history(user_id):
    history = getFromAPI("get_history", [{"user_id": user_id}, {"media_type": "episode"}, {"length": 999999999}])
    if not history:
        return None
    
    if history.get("data") and history["data"].get("data"):
        return history["data"]["data"]

def get_movie_watch_history(user_id):
    history = getFromAPI("get_history", [{"user_id": user_id}, {"media_type": "movie"}, {"length": 999999999}])
    if not history:
        return None

    if history.get("data") and history["data"].get("data"):
        return history["data"]["data"]

def get_library_media_info(rating_key):
    seasons = getFromAPI("get_library_media_info", [{"rating_key": rating_key}])

    if seasons.get("data") and seasons["data"].get("data"):
        return seasons["data"]["data"]

def get_metadata(rating_key):
    metadata = getFromAPI("get_metadata", [{"rating_key": rating_key}])

    if metadata and metadata.get("data"):
        return metadata["data"]

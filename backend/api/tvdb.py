
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
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
from backend.api.cache import apiGet, clearCache
from backend.api import config

def getFromAPI(cmd, args=None, forceFresh=False):
    cnf = config.get_tvdb_config()
    api_key = cnf['api_key']
    api_url = cnf['api_url'].rstrip("/") # avoid double slashes
    api_token = cnf['api_token']

    if not api_key or not api_url:
        return None

    url = f"{api_url}/{cmd.lstrip('/')}" # avoid double slashes
    headers = {
        "Authorization": f"Bearer {api_token}"
    }
    params = args or {}

    try:
        data = apiGet(url=url, headers=headers, params=params, forceFresh=forceFresh)

        if data:
            if data.get("results"):
                return data["results"]
            else:
                return data
    except Exception as e:
        return None

def validate_token():
    cnf = config.get_tvdb_config()
    api_url = cnf['api_url'].rstrip("/")
    api_token = cnf['api_token']
    headers = {
        "Authorization": f"Bearer {api_token}"
    }
    print(headers)
    response = requests.get(f"{api_url}/languages", headers=headers)
    if response.status_code == 200:
        print("VALID")
        return True
    else:
        print("INVALID")
        return False

def get_new_token():
    cnf = config.get_tvdb_config()
    api_url = cnf['api_url'].rstrip("/")
    api_key = cnf['api_key']
    payload = {
        "apikey": api_key
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(f"{api_url}/login", json=payload, headers=headers)
    
    if response:
        token = response.json()["data"]["token"]
        if not token:
            return None

        config.set_config_value("TVDB_TOKEN", token)

        return token
    
    return None

def get_show_tvdb_id(searchQuery, year = None):
    result = getFromAPI(f"search?q={searchQuery}&year={year}")
    if (not (result and result.get("data") and len(result.get("data")) > 0 and result["data"][0].get("tvdb_id"))):
        return
    tvdbId = result["data"][0]["tvdb_id"]
    return tvdbId

def get_recent_episodes(tvdb_id):
    """
    will return a list of episodes that have been released in the last 7 days for the given
    show.

    episodes have format:
    {
        "id": 6770292,
        "seriesId": 350665,
        "name": "Pilot",
        "aired": "2018-10-16",
        "runtime": 45,
        "nameTranslations": [
            "deu",
            ...
        ],
        "overview": "Starting over isn’t easy, especially for small-town guy John Nolan who, after a life-altering incident, is pursuing his dream of being a police officer.",
        "overviewTranslations": [
            "deu",
            ...
        ],
        "image": "https://artworks.thetvdb.com/banners/episodes/350665/6770292.jpg",
        "imageType": 11,
        "isMovie": 0,
        "seasons": null,
        "numbers": 1,
        "absoluteNumber": 1,
        "seasonNumber": 1,
        "lastUpdated": "2025-08-30 07:35:20",
        "finaleType": null,
        "year": "2018"
    },
    """
    endpoint = f"series/{tvdb_id}/episodes/default"
    
    result = getFromAPI(endpoint) # just gets cached value (if it exists)
    if not result or not result.get("data"):
        return []

    series = result["data"].get("series") or {}
    episodes = result["data"].get("episodes") or []
    next_aired_str = series.get("nextAired") # is a string in format "2026-03-03"

    if next_aired_str:
        try:
            next_aired_date = datetime.strptime(next_aired_str, "%Y-%m-%d").date()

            if next_aired_date <= date.today():
                # the next episode has already aired, so we should now refresh
                # the cached entry to get the NEXT episode.
                result = getFromAPI(endpoint, forceFresh=True)

                if not result or not result.get("data"):
                    return []

                series = result["data"].get("series") or {}
                episodes = result["data"].get("episodes") or []

        except ValueError:
            pass
    
    # get and return every episode from the last 7 days
    seven_days_ago = date.today() - timedelta(days=7)
    recent = []

    for ep in episodes:
        aired_str = ep.get("aired")
        if not aired_str:
            continue

        try:
            aired_date = datetime.strptime(aired_str.strip(), "%Y-%m-%d").date()
            if seven_days_ago <= aired_date <= date.today():
                recent.append(ep)
        except ValueError:
            continue
    
    return recent

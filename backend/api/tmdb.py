
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

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w600_and_h900_face"

def getFromAPI(cmd, args=None, forceFresh=False):
    cnf = config.get_tmdb_config()
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

# def validate_token():
    # tmdb access tokens do not expire like tvdb tokens.

# def get_new_token():
    # tmdb access tokens do not expire like tvdb tokens.

def get_movie(tmdbId):
    # get details about a movie from tmdb
    return getFromAPI(f"movie/{tmdbId}")

def get_show(tmdbId):
    # get details about a show from tmdb
    return getFromAPI(f"tv/{tmdbId}")

def get_show_tmdb_id(searchQuery):
    # get tmdb ID for a show from its title
    searchQuery = searchQuery.replace(' ', '+')
    tmdbId = getFromAPI(f"search/tv?query={searchQuery}")
    print(f"Searched for '{searchQuery}', got ID {tmdbId}")
    return tmdbId

def get_poster_image(tmdb_poster_url: str) -> bytes | None:
    if not tmdb_poster_url:
        return None

    url = f"{TMDB_IMAGE_BASE}{tmdb_poster_url}"

    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.contents
    except Exception:
        pass

    return None
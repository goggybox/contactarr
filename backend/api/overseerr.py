
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

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from backend.api.cache import apiGet, clearCache
from backend.api import config

def getFromAPI(cmd, args=None, forceFresh=False):
    """
    use the OVERSEERR_API_KEY and OVERSEERR_API_URL fields from the .env
    file to contact Overseerr.
    """
    cnf = config.get_overseerr_config()
    api_key = cnf['api_key']
    api_url = cnf['api_url']

    if not api_key or not api_url:
        return None
    
    url = f"{api_url}/{cmd}"
    headers = {
        'x-api-key': api_key,
    }
    
    # add args if given
    params = {}
    if args != None:
        for a in args:
            for k, v in a.items():
                params[k] = v
    
    try:
        data = apiGet(url=url, headers=headers, params=params, forceFresh=forceFresh)

        if data:
            return data
        
        return None
    except Exception as e:
        return None

def alive():
    """check if the overseerr instance is alive"""
    response = getFromAPI("status")
    return True if response != None else False

def apikey():
    """get the api key of the Overseerr instance from the .env file"""
    cnf = config.get_overseerr_config()
    api_key = cnf['api_key']
    return api_key

def validate_apikey():
    response = getFromAPI("user", forceFresh=True)
    if response == None:
        return False

    return True

def set_apikey(val: str):
    """set the api key of the Overseerr instance to the .env file"""
    return config.set_config_value("OVERSEERR_API_KEY", val)

def url():
    """get the url of the Overseerr instance's API from the .env file"""
    cnf = config.get_overseerr_config()
    url = cnf['api_url']
    return url

def set_url(val: str):
    """set the url of the Overseerr instance's API to the .env file"""
    return config.set_config_value("OVERSEERR_API_URL", val)

def get_requests():
    response = getFromAPI("request", [{"take": 9999999}], forceFresh=True)
    if response and response.get("results"):
        return response["results"]

def get_movie_poster_url(tmdb_id: str):
    """get the TMDb URL for the poster of a given movie"""
    response = getFromAPI(f"movie/{tmdb_id}")
    if response and response.get("posterPath"):
        return response["posterPath"]

def get_show_poster_url(tmdb_id: str):
    """get the TMDb URL for the poster of a given show"""
    response = getFromAPI(f"tv/{tmdb_id}")
    if response and response.get("posterPath"):
        return response["posterPath"]

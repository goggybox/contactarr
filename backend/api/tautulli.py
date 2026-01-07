
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

def getFromAPI(cmd, args=None):
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
        data = apiGet(url=api_url, params=params)
        
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

def get_users():
    users = getFromAPI("get_users")
    user_array = users['data']
    fields_to_keep = {"user_id","username","friendly_name","email","is_active","is_home_user"}

    # filter each user to keep only the "fields_to_keep"
    intermed = [
        {k: v for k, v in u.items() if k in fields_to_keep}
        for u in user_array
    ]

    # filter array to remove Local user or user_id 0
    filtered_array = [u for u in intermed if u['user_id'] != 0 and u['username'] != "Local"]

    # get more data for each user
    for u in filtered_array:
        u['last_played'] = ""
        u['last_seen'] = ""
        u['last_seen_unix'] = None

        user = getFromAPI("get_history", [{"user_id": int(u['user_id'])}])
        if user and len(user['data']['data']) > 0:
            most_recent = user['data']['data'][0]

            # for TV shows:
            #   - media_type: 'episode'
            #   - full_title: 'BoJack Horseman - Nice While It Lasted'
            #   - parent_title: 'Season 6'
            #   - media_index: 16 (episode number)
            # for movies:
            #   - media_type: 'movie'
            #   - full_title: 'Sister Act'

            # determine whether the most_recent watched was a Movie or Show
            media_type = most_recent['media_type']
            title = most_recent['full_title']
            if media_type != 'movie':
                # add e.g. S06E13 for tv show episode
                season = most_recent['parent_title'].split()[1]
                season = "0"+season if len(season) == 1 else season
                episode = str(most_recent['media_index'])
                episode = "0"+episode if len(episode) == 1 else episode
                tmp = f"(S{season}E{episode}) -"
                title = title.split("-")
                title.insert(1, tmp)
                title = "".join(title)

            # get date and time watch ended
            ended_unix = most_recent['stopped']
            dt = datetime.fromtimestamp(ended_unix)
            
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
            
            u['last_played'] = title
            u['last_seen'] = formatted_dt
            u['last_seen_date'] = dt.strftime("%H:%M, %a %d %b")
            u['last_seen_unix'] = ended_unix

    # order the list by last_seen
    filtered_array = sorted(
        filtered_array,
        key = lambda u: u.get("last_seen_unix") or 0,
        reverse=True
    )

    print("="*142)
    id_space = 10
    space = 20
    is_active_space = 9
    is_home_user_space = 12
    print("ID"+(" "*8)+"| USERNAME"+(" "*12)+"| NAME"+(" "*16)+"| EMAIL"+(" "*15)+"| IS_ACTIVE"+" |"+" IS_HOME_USER" +" |"+" LAST SEEN          " + "|" + " LAST PLAYED         ")

    for u in filtered_array:
        print(type(u['last_seen']))
    #     id = str(u['user_id'])+(" "*(id_space - len(str(u['user_id']))))+"| "
    #     username = u['username'][:space]+(" "*(space - len(u['username'])))+"| "
    #     name = u['friendly_name'][:space]+(" "*(space - len(u['friendly_name'])))+"| "
    #     email = u['email'] or ""
    #     email = email[:space]+(" "*(space - len(email)))+"| "
    #     is_active = str(u['is_active'])+(" "*(is_active_space))+"| "
    #     is_home_user = str(u['is_home_user'])+(" "*(is_home_user_space))+"| "
    #     last_seen = str(u['last_seen'])+(" "*(space - len(str(u['last_seen']))))+"| "
    #     last_played = (u['last_played']+(" "*(space - len(u['last_played'])))) if u['last_played'] else ""
    #     print(id+username+name+email+is_active+is_home_user+last_seen+last_played)

    return filtered_array

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
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional

_env_path = None

def get_env_path():
    """get the path to the .env file"""
    global _env_path
    if _env_path is None:
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent
        _env_path = project_root / '.env'
    load_dotenv(dotenv_path=_env_path, override=True)
    return _env_path

def get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """get a fresh configuration value from the environment"""
    env_path = get_env_path()
    
    value = os.getenv(key, default)
    
    if key.endswith('_API_URL') and value and not value.startswith(('http://', 'https://')):
        value = f'http://{value}'
    
    return value

def set_config_value(key: str, value: str) -> bool:
    try:
        env_path = get_env_path()

        env_data = {}
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and '=' in line and not line.startswith('#'):
                        k, v = line.split('=', 1)
                        env_data[k.strip()] = v.strip()

        env_data[key] = value

        with open(env_path, 'w', encoding='utf-8') as f:
            for k, v in env_data.items():
                f.write(f'{k}={v}\n')

        return True
    except Exception as e:
        return False

def get_tautulli_config():
    """get fresh Tautulli configuration"""
    return {
        'api_key': get_config_value('TAUTULLI_API_KEY'),
        'api_url': get_config_value('TAUTULLI_API_URL'),
    }

def get_overseerr_config():
    """get fresh Overseerr configuration"""
    return {
        'api_key': get_config_value('OVERSEERR_API_KEY'),
        'api_url': get_config_value('OVERSEERR_API_URL'),
        'last_requests_process': get_config_value('OVERSEERR_LAST_REQUESTS_PROCESS')
    }

def get_smtp_config():
    """get SMTP configuration"""
    return {
        'host': get_config_value('SMTP_HOST'),
        'port': get_config_value('SMTP_PORT'),
        'user': get_config_value('SMTP_USER'),
        'pass': get_config_value('SMTP_PASS')
    }

def get_tvdb_config():
    """get fresh TVdb configuration"""
    return {
        'api_key': get_config_value('TVDB_API_KEY'),
        'api_url': get_config_value('TVDB_API_URL', 'https://api.thetvdb.com/v4'),
        'api_token': get_config_value('TVDB_TOKEN')
    }

def get_tmdb_config():
    """get fresh TMdb configuration"""
    return {
        'api_key': get_config_value('TMDB_API_KEY'),
        'api_url': get_config_value('TMDB_API_URL', 'https://api.themoviedb.org/3'),
        'api_token': get_config_value('TMDB_TOKEN')
    }

def get_server_config():
    return {
        'name': get_config_value('SERVER_NAME'),
        'unsubscribe_lists': [x for x in (get_config_value('UNSUBSCRIBE_LISTS') or '').split(",") if x],
    }

def get_or_init_config_vlaue(key):
    value = get_config_value(key)
    if value is None:
        set_config_value(key, 0)
        return 0
    return value

def get_automated_emails_config():
    return {
        'newly_released_content': get_or_init_config_vlaue('NEWLY_RELEASED_CONTENT_UPDATES'),
        'request_for_unreleased_content': get_or_init_config_vlaue('REQUEST_FOR_UNRELEASED_CONTENT')
    }
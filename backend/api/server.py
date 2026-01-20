
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

def get_server_name():
    cnf = config.get_server_config()
    return cnf['name']

def set_server_name(val: str):
    return config.set_config_value("SERVER_NAME", val)

def get_unsubscribe_lists():
    cnf = config.get_server_config()
    return cnf['unsubscribe_lists']

def set_unsubscribe_lists(lst: list):
    strVal = ','.join(lst)
    return config.set_config_value("UNSUBSCRIBE_LISTS", strVal)
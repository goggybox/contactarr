
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

def host():
    cnf = config.get_smtp_config()
    host = cnf['host']
    return host

def set_host(val: str):
    return config.set_config_value("SMTP_HOST", val)

def port():
    cnf = config.get_smtp_config()
    return cnf['port']

def set_port(val: str):
    return config.set_config_value("SMTP_PORT", val)

def user():
    cnf = config.get_smtp_config()
    return cnf['user']

def set_user(val: str):
    return config.set_config_value("SMTP_USER", val)

def password():
    cnf = config.get_smtp_config()
    return cnf['pass']

def set_pass(val: str):
    return config.set_config_value("SMTP_PASS", val)
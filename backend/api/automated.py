
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

from backend.api import config

def get_newly_released_content_setting():
    cnf = config.get_automated_emails_config()
    return cnf["newly_released_content"]

def set_newly_released_content_setting(val):
    return config.set_config_value("NEWLY_RELEASED_CONTENT_UPDATES", val)

def get_request_for_unreleased_content_setting():
    cnf = config.get_automated_emails_config()
    return cnf["request_for_unreleased_content"]

def set_request_for_unreleased_content_setting(val):
    return config.set_config_value("REQUEST_FOR_UNRELEASED_CONTENT", val)


# get all
def get_automated_email_settings():
    cnf = config.get_automated_emails_config()
    return cnf
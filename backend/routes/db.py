
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

from pydantic import BaseModel
from fastapi import APIRouter
from backend.api import tautulli
from backend.api import overseerr
from backend.db import db
from fastapi.responses import PlainTextResponse

router = APIRouter()

class APIModel(BaseModel):
    key: str

# ---------------------------------------- #
#                 TAUTULLI                 #
# ---------------------------------------- #

@router.get("/tautulli/apikey")
def tau_apikey():
    return PlainTextResponse(tautulli.apikey())

@router.post("/tautulli/set_apikey")
def tau_set_apikey(data: APIModel):
    return tautulli.set_apikey(data.key)

@router.get("/tautulli/url")
def tau_url():
    return PlainTextResponse(tautulli.url())

@router.post("/tautulli/set_url")
def tau_set_url(data: APIModel):
    return tautulli.set_url(data.key)

@router.get("/tautulli/alive")
def tau_alive():
    return tautulli.alive()

@router.get("/tautulli/get_users")
def tau_get_users():
    return tautulli.get_users()

# ---------------------------------------- #
#                OVERSEERR                 #
# ---------------------------------------- #

@router.get("/overseerr/apikey")
def ove_apikey():
    return PlainTextResponse(overseerr.apikey())

@router.post("/overseerr/set_apikey")
def ove_set_apikey(data: APIModel):
    return overseerr.set_apikey(data.key)

@router.get("/overseerr/url")
def ove_url():
    return PlainTextResponse(overseerr.url())

@router.post("/overseerr/set_url")
def ove_set_url(data: APIModel):
    return overseerr.set_url(data.key)

@router.get("/overseerr/alive")
def ove_alive():
    return overseerr.alive()

@router.get("/overseerr/get_requests")
def ove_get_requests():
    return overseerr.get_requests()

# ---------------------------------------- #
#                  OTHER                   #
# ---------------------------------------- #

@router.get("/populate_users_table")
def populate_users_table():
    return db.populate_users_table()

@router.get("/populate_shows")
def populate_shows():
    return db.populate_shows()

@router.get("/populate_movies")
def populate_movies():
    return db.populate_movies()

@router.get("/link_tautulli")
def link_tautulli():
    return db.link_tautulli()
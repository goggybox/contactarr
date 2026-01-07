
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

from pydantic import BaseModel
from fastapi import APIRouter
from backend.api import tautulli
from fastapi.responses import PlainTextResponse

router = APIRouter()

class APIModel(BaseModel):
    key: str

@router.get("/apikey")
def apikey():
    return PlainTextResponse(tautulli.apikey())

@router.post("/set_apikey")
def set_apikey(data: APIModel):
    return tautulli.set_apikey(data.key)

@router.get("/url")
def url():
    return PlainTextResponse(tautulli.url())

@router.post("/set_url")
def set_url(data: APIModel):
    return tautulli.set_url(data.key)

@router.get("/alive")
def alive():
    return tautulli.alive()

@router.get("/get_users")
def get_users():
    return tautulli.get_users()
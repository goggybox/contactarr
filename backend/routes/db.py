
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
from backend.api import smtp
from backend.db import db
from fastapi.responses import PlainTextResponse

router = APIRouter()

class APIModel(BaseModel):
    key: str

class SMTPAllModel(BaseModel):
    host: str
    port: str
    user: str
    password: str

class SMTPSenderRecipientModel(BaseModel):
    sender: str
    recipient: str

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
#                   SMTP                   #
# ---------------------------------------- #

@router.get("/smtp/host")
def smtp_host():
    return smtp.host()

@router.post("/smtp/set_host")
def smtp_set_host(data: APIModel):
    return smtp.set_host(data.key)

@router.get("/smtp/port")
def smtp_port():
    test = smtp.port()
    print(test)
    return test

@router.post("/smtp/set_port")
def smtp_set_port(data: APIModel):
    return smtp.set_port(data.key)

@router.get("/smtp/user")
def smtp_user():
    return smtp.user()

@router.post("/smtp/set_user")
def smtp_set_user(data: APIModel):
    return smtp.set_user(data.key)

@router.get("/smtp/pass")
def smtp_pass():
    return smtp.password()

@router.post("/smtp/set_pass")
def smtp_set_pass(data: APIModel):
    return smtp.set_pass(data.key)

@router.post("/smtp/set_all")
def smtp_set_all(data: SMTPAllModel):
    results = {
        "host": smtp.set_host(data.host),
        "port": smtp.set_port(data.port),
        "user": smtp.set_user(data.user),
        "password": smtp.set_pass(data.password),
    }
    return results

@router.post("/smtp/validate_sender")
def smtp_validate_sender(data: APIModel):
    return smtp.validate_sender(data.key)

@router.post("/smtp/validate_recipient")
def smtp_validate_recipient(data: APIModel):
    return smtp.validate_recipient_string(data.key)

@router.post("/smtp/send_test_email")
def smtp_send_email(data: SMTPSenderRecipientModel):
    return smtp.send_test_email(data.sender, data.recipient)

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

@router.get("/get_users")
def get_users():
    return db.get_users()

@router.get("/get_admins")
def get_admins():
    return db.get_admins()

@router.post("/remove_admin")
def remove_admin(data: APIModel):
    return db.remove_admin(data.key)
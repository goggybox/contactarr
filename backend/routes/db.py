
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
from fastapi.responses import StreamingResponse
from fastapi import BackgroundTasks
from typing import List
from backend.api import tautulli
from backend.api import overseerr
from backend.api import smtp
from backend.api import tvdb
from backend.api import tmdb
from backend.api import server
from backend.api import automated
from backend.db import db
from backend.api.jobRegister import start_job, get_jobs
from fastapi.responses import PlainTextResponse

router = APIRouter()

class APIModel(BaseModel):
    key: str

class ListModel(BaseModel):
    key: list

class SMTPAllModel(BaseModel):
    host: str
    port: str
    user: str
    password: str

class SMTPSenderRecipientModel(BaseModel):
    sender: str
    recipient: str

class UnsubscribeListModel(BaseModel):
    table_name: str
    user_ids: list[int]

class SendEmailRequest(BaseModel):
    subject: str
    html_body: str
    recipients: List[str]
    sender: str

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

@router.get("/tautulli/validate_apikey")
def tau_validate_apikey():
    return tautulli.validate_apikey()

@router.get("/tautulli/get_users")
def tau_get_users():
    return tautulli.get_users()

@router.get("/tautulli/get_movies")
def tau_get_movies():
    return tautulli.get_movies()

@router.get("/tautulli/get_shows")
def tau_get_shows():
    return tautulli.get_shows()

# ---------------------------------------- #
#                OVERSEERR                 #
# ---------------------------------------- #

@router.get("/overseerr/apikey")
def ove_apikey():
    return PlainTextResponse(overseerr.apikey())

@router.post("/overseerr/set_apikey")
def ove_set_apikey(data: APIModel):
    return overseerr.set_apikey(data.key)

@router.get("/overseerr/validate_apikey")
def ove_validate_apikey():
    return overseerr.validate_apikey()

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
    
@router.post("/overseerr/get_movie_poster_url")
def ove_get_movie_poster_url(data: APIModel):
    return db.get_movie_poster_url_and_cache(data.key)

@router.post("/overseerr/get_user_requests")
def ove_get_user_requests(data: APIModel):
    print(data)
    return db.get_user_requests(data.key)

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

@router.post("/smtp/send_email_stream")
def send_email_stream(data: SendEmailRequest):
    """
    send individual emails to a list of recipients.
    returns progress updates using SSEs.
    """
    return StreamingResponse(
        smtp.send_email_stream(data.subject, data.html_body, data.recipients, data.sender),
        media_type="text/event-stream"
    )

# ---------------------------------------- #
#                   TVDB                   #
# ---------------------------------------- #

@router.get("/tvdb/validate_token")
def tvdb_validate_token():
    return tvdb.validate_token()

@router.get("/tvdb/get_new_token")
def tvdb_get_new_token():
    return tvdb.get_new_token()

# ---------------------------------------- #
#                   TMDB                   #
# ---------------------------------------- #

@router.post("/tmdb/get_show_tmdb_id")
def tmdb_get_show_tmdb_id(data: APIModel):
    return tmdb.get_show_tmdb_id(data.key)

# ---------------------------------------- #
#             AUTOMATED EMAILS             #
# ---------------------------------------- #

@router.get("/automated/get_newly_released_content_setting")
def auto_get_newly_released_content_setting():
    return automated.get_newly_released_content_setting()

@router.post("/automated/set_newly_released_content_setting")
def auto_set_newly_released_content_setting(data: APIModel):
    return automated.set_newly_released_content_setting(data.key)

@router.get("/automated/get_request_for_unreleased_content_setting")
def auto_get_request_for_unreleased_content_setting():
    return automated.get_request_for_unreleased_content_setting()

@router.post("/automated/set_request_for_unreleased_content_setting")
def auto_set_request_for_unreleased_content_setting(data: APIModel):
    return automated.set_request_for_unreleased_content_setting(data.key)

# get all automated email settings
@router.get("/automated/get_automated_email_settings")
def auto_get_automated_email_settings():
    return automated.get_automated_email_settings()


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
    job_id = start_job(
        "Fetching data from Tautulli...",
        db.link_tautulli
    )
    return {"job_id": job_id}

@router.get("/link_overseerr")
def link_overseerr():
    if overseerr.validate_apikey():
        job_id = start_job(
            "Fetching data from Overseerr...",
            db.link_overseerr
        )
        return {"job_id": job_id}
    else:
        return False

@router.get("/jobs")
def job_status():
    return get_jobs()

@router.post("/get_movie_poster_image")
def get_movie_poster_image(data: APIModel):
    return db.get_poster_image(movie_id=data.key)

@router.post("/get_show_poster_image")
def get_show_poster_image(data: APIModel):
    return db.get_poster_image(show_id=data.key)

@router.get("/get_users")
def get_users():
    return db.get_users()

@router.get("/get_admins")
def get_admins():
    return db.get_admins()

@router.post("/set_admins")
def set_admins(data: ListModel):
    return db.set_admins(data.key)

@router.post("/remove_admin")
def remove_admin(data: APIModel):
    return db.remove_admin(data.key)

@router.post("/add_admin")
def add_admin(data: APIModel):
    return db.add_admin(data.key)

@router.get("/get_server_name")
def get_server_name():
    return server.get_server_name()

@router.post("/set_server_name")
def set_server_name(data: APIModel):
    return server.set_server_name(data.key)

@router.get("/get_unsubscribe_lists")
def get_unsubscribe_lists():
    return db.get_unsubscribe_lists()

@router.post("/set_unsubscribe_list")
def set_unsubscribe_list(data: UnsubscribeListModel):
    return db.set_unsubscribe_list(data.table_name, data.user_ids)
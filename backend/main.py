
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

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
# from backend.routes.tautulli import router as tautulli_router
from backend.routes.db import router as db_router
from dotenv import load_dotenv
import os

app = FastAPI()

load_dotenv('.env')

# API routes
# app.include_router(tautulli_router, prefix="/backend/tautulli")
app.include_router(db_router, prefix="/backend")

# front-end routes
@app.get("/")
def dashboard():
    return FileResponse("frontend/pages/dashboard/index.html")

@app.get("/connections")
def connections():
    return FileResponse("frontend/pages/connections/connections.html")

# Serve frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
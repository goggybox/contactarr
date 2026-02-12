
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

import threading
import uuid
import time

_jobs = {}
_jobs_lock = threading.Lock()

def start_job(name, target_func):
    job_id = str(uuid.uuid4())

    def wrapper():
        try:
            target_func()
        finally:
            with _jobs_lock:
                _jobs[job_id]["running"] = False

    with _jobs_lock:
        _jobs[job_id] = {
            "name": name,
            "running": True
        }

    threading.Thread(target=wrapper, daemon=True).start()
    return job_id

def get_jobs():
    with _jobs_lock:
        return dict(_jobs)
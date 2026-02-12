
// -----------------------------contactarr------------------------------
// This file is part of contactarr
// Copyright (C) 2025 goggybox https://github.com/goggybox

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// that this program is licensed under. See LICENSE file. If not
// available, see <https://www.gnu.org/licenses/>.

// Please keep this header comment in all copies of the program.
// --------------------------------------------------------------------

const jobContainer = document.getElementById("job-container");

const activeJobs = new Map();

async function fetchJobs() {
    try {
        const res = await fetch("/backend/jobs");
        const jobs = await res.json();

        Object.entries(jobs).forEach(([id, job]) => {
            if (job.running && !activeJobs.has(id)) {
                createJobIndicator(id, job.name);
                console.log(`CREATED JOB INDICATOR FOR ${id} ${job.name}`);
            }

            if (!job.running && activeJobs.has(id)) {
                removeJobIndicator(id);
            }

        });

    } catch (err) {
        console.error("Job polling failed:", err);
    }
}

function createJobIndicator(id, text) {

    const div = document.createElement("div");
    div.className = "job-indicator";

    div.innerHTML = `
        ${text}
        <span class="spinner"></span>
    `;

    jobContainer.appendChild(div);
    activeJobs.set(id, div);
}

function removeJobIndicator(id) {

    const el = activeJobs.get(id);
    if (!el) return;

    el.style.opacity = "0";
    setTimeout(() => {
        el.remove();
    }, 200);

    activeJobs.delete(id);
}


setInterval(fetchJobs, 500);

// run once on page load
document.addEventListener("DOMContentLoaded", fetchJobs);

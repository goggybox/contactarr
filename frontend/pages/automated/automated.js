
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

window.onload = async function() {
    const res = await fetch ("/backend/automated/get_automated_email_settings");
    const settings = await res.json();

    // each setting should have a corresponding checkbox with the same name+"_checkbox".
    // set the checkbox to be checked/unchecked corresponding to the setting value
    for (const [name, val] of Object.entries(settings)) {
        const elemId = name+"_checkbox";
        const elem = document.getElementById(elemId);

        elem.checked = val == 1;

        // add event listener to when elem is checked, update setting in storage
        elem.addEventListener('click', async () => {
            // the backend API call is the "set_"+name+"_setting"
            await this.fetch(`/backend/automated/set_${name}_setting`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    key: elem.checked ? "1" : "0"
                })
            });
        });
    }

}
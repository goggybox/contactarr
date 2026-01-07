
// # -----------------------------contactarr------------------------------
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

let tautulli_url;

async function initTautulliURLInputBox() {
    // tautulli api key
    const inp = document.getElementById("tautulli-connection2-input-box");
    let res = await fetch("/backend/tautulli/url");
    tautulli_url = await res.text();
    inp.value = tautulli_url;
    inp.addEventListener('input', tautulliAPIURLListener);
}

async function tautulliConnection2Save() {
    const inp = document.getElementById("tautulli-connection2-input-box");
    const val = inp.value;
    const res = await fetch("/backend/tautulli/set_url", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({key: val})
    });
    const success = await res.json();
    if (success) {
        tautulli_url = val;
        hideSaveAndCancelButtons2();
        showNotification("Tautulli API URL Saved");
    }
}

function tautulliConnection2Cancel() {
    const inp = document.getElementById("tautulli-connection2-input-box");
    inp.value = tautulli_url;
    hideSaveAndCancelButtons2();
}

function hideSaveAndCancelButtons2() {
    const btns = document.getElementById("tautulli-connection2-buttons");
    btns.classList.add("hide");
}

function showSaveAndCancelButtons2() {
    const btns = document.getElementById("tautulli-connection2-buttons");
    btns.classList.remove("hide");
}

function tautulliAPIURLListener() {
    // event listener for TautulliAPIKey input box.
    const inp = document.getElementById("tautulli-connection2-input-box");

    if (inp.value.trim() === tautulli_url) {
        // matches currently saved key value - hide Save/Cancel buttons
        hideSaveAndCancelButtons2();
    } else {
        // does not match currently saved key value - show Save/Cancel buttons
        showSaveAndCancelButtons2();
    }
}

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

let tautulli_key;

async function initTautulliAPIInputBox() {
    // tautulli api key
    const inp = document.getElementById("tautulli-connection-input-box");
    let res = await fetch("/backend/tautulli/apikey");
    tautulli_key = await res.text();
    inp.value = tautulli_key;
    inp.addEventListener('input', tautulliAPIKeyListener);
}

async function tautulliConnectionSave() {
    const inp = document.getElementById("tautulli-connection-input-box");
    const val = inp.value;
    const res = await fetch("/backend/tautulli/set_apikey", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({key: val})
    });
    const success = await res.json();
    if (success) {
        tautulli_key = val;
        hideSaveAndCancelButtons();
        showNotification("Tautulli API Key Saved");
    }
}

function tautulliConnectionCancel() {
    const inp = document.getElementById("tautulli-connection-input-box");
    inp.value = tautulli_key;
    hideSaveAndCancelButtons();
}

async function tautulliConnectionTest() {
    const res = await fetch("/backend/tautulli/alive");
    const alive = await res.json();
    console.log(alive);
    if (alive) {
        showSuccess("Successfully connected to Tautulli!");
    } else {
        showError("Cannot connect to Tautulli. Confirm that the API key and url are correct.");
    }
}

function hideSaveAndCancelButtons() {
    const btns = document.getElementById("tautulli-connection-buttons");
    const testBtn = document.getElementById("tautulli-connection-test");
    btns.classList.add("hide");
    testBtn.classList.remove("hide");
}

function showSaveAndCancelButtons() {
    const btns = document.getElementById("tautulli-connection-buttons");
    const testBtn = document.getElementById("tautulli-connection-test");
    btns.classList.remove("hide");
    testBtn.classList.add("hide");
}

function tautulliAPIKeyListener() {
    // event listener for TautulliAPIKey input box.
    const inp = document.getElementById("tautulli-connection-input-box");

    if (inp.value.trim() === tautulli_key) {
        // matches currently saved key value - hide Save/Cancel buttons
        hideSaveAndCancelButtons();
    } else {
        // does not match currently saved key value - show Save/Cancel buttons
        showSaveAndCancelButtons();
    }
}
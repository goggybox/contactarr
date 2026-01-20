
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

let overseerr_key;
let overseerr_url;

async function initOverseerr() {
    // api key
    const inp = document.getElementById("overseerr-connection-input-box");
    let res = await fetch("/backend/overseerr/apikey");
    overseerr_key = await res.text();
    inp.value = overseerr_key;
    inp.addEventListener('input', overseerrAPIKeyListener);
    
    // api url
    const inp2 = document.getElementById("overseerr-url-input-box");
    let r = await fetch("/backend/overseerr/url");
    overseerr_url = await r.text();
    inp2.value = overseerr_url;
    inp2.addEventListener('input', overseerrAPIURLListener);
}

// --------------- API KEY ---------------

async function overseerrConnectionSave() {
    // button to save the API key
    const inp = document.getElementById("overseerr-connection-input-box");
    const val = inp.value;
    const res = await fetch("/backend/overseerr/set_apikey", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({key: val})
    });
    const success = await res.json();
    if (success) {
        overseerr_key = val;
        hideOverseerSaveAndCancelButtons();
        showNotification("Overseerr API Key Saved");
        await fetch("/backend/link_overseerr");
    }
}

function overseerrConnectionCancel() {
    const inp = document.getElementById("overseerr-connection-input-box");
    inp.value = overseerr_key;
    hideOverseerrSaveAndCancelButtons();
}

async function overseerrConnectionTest() {
    const res = await fetch("/backend/overseerr/validate_apikey");
    const alive = await res.json();
    if (alive) {
        showSuccess("Successfully connected to Overseerr!");
    } else {
        showError("Cannot connect to Overseerr. Are you sure the API key and URL are correct?")
    }
}

function hideSaveAndChideOverseerSaveAndCancelButtonsancelButtons() {
    const btns = document.getElementById("overseerr-connection-buttons");
    const testBtn = document.getElementById("overseerr-connection-test");
    btns.classList.add("hide");
    testBtn.classList.remove("hide");
}

function showOverseerrSaveAndCancelButtons() {
    const btns = document.getElementById("overseerr-connection-buttons");
    const testBtn = document.getElementById("overseerr-connection-test");
    btns.classList.remove("hide");
    testBtn.classList.add("hide");
}

async function overseerrAPIKeyListener() {
    const inp = document.getElementById("overseerr-connection-input-box");

    if(inp.value.trim() === overseerr_key) {
        hideOverseerrSaveAndCancelButtons();
    } else {
        showOverseerrSaveAndCancelButtons();
    }
}

// --------------- API URL ---------------

async function overseerrURLSave() {
    const inp = document.getElementById("overseerr-url-input-box");
    const val = inp.value;
    const res = await fetch("/backend/overseerr/set_url", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({key: val})
    });
    const success = await res.json();
    if (success) {
        overseerr_url = val;
        hideURLSaveAndCancelButtons();
        showNotification("Overseerr API URL saved");
    }
}

function overseerrURLCancel() {
    const inp = document.getElementById("overseerr-url-input-box");
    inp.value = overseerr_url;
    hideURLSaveAndCancelButtons();
}

function hideURLSaveAndCancelButtons() {
    const btns = document.getElementById("overseerr-url-buttons");
    btns.classList.add("hide");
}

function showURLSaveAndCancelButtons() {
    const btns = document.getElementById("overseerr-url-buttons");
    btns.classList.remove("hide");
}

function overseerrAPIURLListener() {
    const inp = document.getElementById("overseerr-url-input-box");

    if (inp.value.trim() === overseerr_url) {
        hideURLSaveAndCancelButtons();
    } else {
        showURLSaveAndCancelButtons();
    }
}
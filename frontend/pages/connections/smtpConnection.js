
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

    let smtp_host;
    let smtp_port;
    let smtp_user;
    let smtp_pass;

    async function initSMTPInputBoxes() {
        // host
        const hostInp = document.getElementById("smtp-host-input-box");
        let res = await fetch("/backend/smtp/host");
        smtp_host = await res.json();
        hostInp.value = smtp_host;
        hostInp.addEventListener('input', smtpListener);
        // port
        const portInp = document.getElementById("smtp-port-input-box");
        res = await fetch("/backend/smtp/port");
        smtp_port = await res.json();
        portInp.value = smtp_port;
        portInp.addEventListener('input', smtpListener);
        // user
        const userInp = document.getElementById("smtp-user-input-box");
        res = await fetch("/backend/smtp/user");
        smtp_user = await res.json();
        userInp.value = smtp_user;
        userInp.addEventListener('input', smtpListener);
        // password
        const passInp = document.getElementById("smtp-pass-input-box");
        res = await fetch("/backend/smtp/pass");
        smtp_pass = await res.json();
        passInp.value = smtp_pass;
        passInp.addEventListener('input', smtpListener);
    }

    async function smtpConnectionSave() {
        const hostInp = document.getElementById("smtp-host-input-box");
        const portInp = document.getElementById("smtp-port-input-box");
        const userInp = document.getElementById("smtp-user-input-box");
        const passInp = document.getElementById("smtp-pass-input-box");
        const res = await fetch("/backend/smtp/set_all", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "host": hostInp.value,
                "port": portInp.value,
                "user": userInp.value,
                "password": passInp.value
            })
        });
        const response = await res.json();
        const failedKeys = Object.entries(response).filter(([key, value]) => value === false).map(([key]) => key);
        if (failedKeys.length === 0) {
            smtp_host = hostInp.value;
            smtp_port = portInp.value;
            smtp_user = userInp.value;
            smtp_pass = passInp.value;
            smtpHideSaveAndCancelButtons();
            showNotification("SMTP Credentials Saved");
        }
    }

    async function smtpConnectionCancel() {
        const hostInp = document.getElementById("smtp-host-input-box");
        const portInp = document.getElementById("smtp-port-input-box");
        const userInp = document.getElementById("smtp-user-input-box");
        const passInp = document.getElementById("smtp-pass-input-box");
        hostInp.value = smtp_host;
        portInp.value = smtp_port;
        userInp.value = smtp_user;
        passInp.value = smtp_pass;
        smtpHideSaveAndCancelButtons();
    }

    function smtpHideSaveAndCancelButtons() {
        const btns = document.getElementById("smtp-connection-buttons");
        btns.classList.add("hide");
    }

    function smtpShowSaveAndCancelButtons() {
        const btns = document.getElementById("smtp-connection-buttons");
        btns.classList.remove("hide");
    }

    function smtpListener() {
        const hostInp = document.getElementById("smtp-host-input-box");
        const portInp = document.getElementById("smtp-port-input-box");
        const userInp = document.getElementById("smtp-user-input-box");
        const passInp = document.getElementById("smtp-pass-input-box");

        if (hostInp.value.trim() === (smtp_host || "") && portInp.value.trim() === (smtp_port || "")
        && userInp.value.trim() === (smtp_user || "") && passInp.value.trim() === (smtp_pass || "")) {
            smtpHideSaveAndCancelButtons();
        } else {
            smtpShowSaveAndCancelButtons();
        }
    }

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
let users;
let admins;


function cr(type, clss, id) {
    const elem = document.createElement(type);
    if (clss) { elem.classList.add(clss); }
    if (id) { elem.id = id; }
    return elem;
}

function completeUserSelectors() {
    
    completeAdminUserSelect();
}

function completeAdminUserSelect() {
    // admin users selector "⌄" "⌃"
    console.log("RUNNING");
    const adminUsersSelector = document.getElementById("admin-users-selector");
    adminUsersSelector.innerHTML = ""; // clear it first
    const adminUsersDropdown = cr("div", "user-selector-dropdown", "admin-users-dropdown");
    const dropdownP = cr("p",null,null);
    dropdownP.textContent = "⌄";
    adminUsersDropdown.appendChild(dropdownP);
    // add each admin
    for (let admin of admins) {
        // add admin's name
        const userContainer = cr("div", "admin-user-container", null);
        const friendlyName = cr("p", "admin-friendly-name", null);
        friendlyName.textContent = admin["friendly_name"];
        const username = cr("p", "admin-username", null);
        username.textContent = `(${admin["username"]})`;
        userContainer.appendChild(friendlyName);
        userContainer.appendChild(username);
        adminUsersSelector.appendChild(userContainer);
        // add removal button
        const userRemoveButton = cr("div", "admin-user-remove", null);
        userRemoveButton.addEventListener("click", async () => {
            await fetch("/backend/remove_admin", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    key: admin["username"]
                })
            });
            admins.splice(admins.indexOf(admin), 1);
            completeAdminUserSelect();
        });
        const buttonP = cr("p",null,null);
        buttonP.textContent = "-";
        userRemoveButton.appendChild(buttonP);
        adminUsersSelector.appendChild(userRemoveButton);
    }
    
    // add "Add..." text
    const addContainer = cr("div", "admin-user-container", null);
    addContainer.classList.add("last");
    const addText = cr("p", "add-text", null);
    addText.textContent = "Add...";
    addContainer.appendChild(addText);
    adminUsersSelector.appendChild(addContainer);

    // add dropdown
    adminUsersSelector.appendChild(adminUsersDropdown);
}

window.onload = async function() {
    let res = await fetch("/backend/get_users");
    users = await res.json();
    res = await fetch("/backend/get_admins");
    admins = await res.json();

    initTautulliURLInputBox();
    initTautulliAPIInputBox();
    initSMTPInputBoxes();
    completeUserSelectors();
}
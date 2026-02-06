
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

// -------------------- utilities functions --------------------
function cr(type, clss, id) {
    const elem = document.createElement(type);
    if (clss) { elem.classList.add(clss); }
    if (id) { elem.id = id; }
    return elem;
}

const equal = (a, b) => JSON.stringify(a) === JSON.stringify(b);

// -------------------- SERVER SETTINGS --------------------
let serverName, serverNameInit;
let admins, adminsInit;
let adminSelector;

async function initServerSettings() {
    const input = document.getElementById("server-name-input-box");
    const res = await fetch("/backend/get_server_name");
    serverName = await res.json();
    serverNameInit = serverName;

    if (serverName) {
        input.value = serverName;
        const title = document.getElementById("server-section-name");
        title.textContent = `Your Server (${serverName})`;
    }

    input.addEventListener("input", checkForChanges);

    initUnsubscribeLists();
}

function checkForChanges() {
    const input = document.getElementById("server-name-input-box");
    const hasNameChange = input.value.trim() !== serverNameInit;
    const hasAdminChange = !equal(admins, adminsInit);
    
    if (hasNameChange || hasAdminChange) {
        showSaveCancelButtons();
    } else {
        hideSaveCancelButtons();
    }
}

function hideSaveCancelButtons() {
    document.getElementById("server-settings-buttons").classList.add("hide");
}

function showSaveCancelButtons() {
    document.getElementById("server-settings-buttons").classList.remove("hide");
}

function serverSettingsCancel() {
    const input = document.getElementById("server-name-input-box");
    input.value = serverNameInit;
    admins = [...adminsInit];
    adminSelector.reset(admins);
    hideSaveCancelButtons();
}

async function serverSettingsSave() {
    const input = document.getElementById("server-name-input-box");
    const newName = input.value.trim();
    
    if (newName !== serverNameInit) {
        await updateServerName(newName);
    }
    if (!equal(admins, adminsInit)) {
        await updateAdminsList(admins);
    }
    hideSaveCancelButtons();
}

async function updateAdminsList(list) {
    await fetch("/backend/set_admins", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({key: list})  
    });
    adminsInit = [...admins];
}

async function updateServerName(name) {
    await fetch("/backend/set_server_name", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({key: name})
    });
    serverNameInit = name;
    serverName = name;
    const title = document.getElementById("server-section-name");
    title.textContent = `Your Server (${serverName})`;
}


const list_name_map = {
    "newly_released_content_updates_unsubscribe_list": "Newly Released Content",
    "system_updates_unsubscribe_list": "System Updates"
}
async function initUnsubscribeLists() {
    const res = await fetch("/backend/get_unsubscribe_lists");
    const lists = await res.json();
    
    const parent = document.getElementById("unsubscribe-list-selector");

    // add existing unsubscribe lists if there are any
    for (const [index, list] of lists.entries()) {
        const selector = cr("div", "selector", list+"_selector");
        const translateAmount = 2 * (index);

        // translate to account for double borders of each selector
        selector.style.transform = `translateY(-${translateAmount}px)`;

        const listName = cr("p", null, null);
        listName.textContent = list_name_map[list] || list;
        selector.appendChild(listName);
        parent.appendChild(selector);
    }

    // // add box to enter new unsubscribe list in
    // const list_adder = cr("div", "list-adder", "unsubscribe-list-adder");
    // const listAdderInp = cr("input", "connection-input-box", "list-adder-text");
    // listAdderInp.placeholder="Enter new list name...";
    // listAdderInp.addEventListener("input", (e) => {
    //     const par = document.getElementById("unsubscribe-list-selector");
    //     if (e.target.value !== "") {
    //         par.classList.add("typing-new-list");
    //     } else {
    //         par.classList.remove("typing-new-list");
    //     }
    //     addListAdderButton();
    // });
    // listAdderInp.addEventListener("focus", () => {
    //     const la = document.getElementById("unsubscribe-list-adder");
    //     la.classList.add("active");
    // });
    // listAdderInp.addEventListener("blur", () => {
    //     const la = document.getElementById("unsubscribe-list-adder");
    //     la.classList.remove("active");
    // });
    // list_adder.appendChild(listAdderInp);
    // parent.appendChild(list_adder);
}

// -------------------- on load function --------------------
window.onload = async function() {
    const usersRes = await fetch("/backend/get_users");
    const users = await usersRes.json();
    const adminsRes = await fetch("/backend/get_admins");
    admins = await adminsRes.json();
    adminsInit = [...admins];

    initServerSettings();

    adminSelector = new UserListSelector(
        "admin-selector",
        admins,
        users,
        (newList) => {
            admins = newList;
            checkForChanges();
        },
        "admin-dropdown"
    );
}
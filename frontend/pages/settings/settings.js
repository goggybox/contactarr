
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
let users_init;
let admins;
let admins_init;
let serverName;

function cr(type, clss, id) {
    const elem = document.createElement(type);
    if (clss) { elem.classList.add(clss); }
    if (id) { elem.id = id; }
    return elem;
}

async function initServerSettings() {
    // server name
    const container = document.getElementById("server-name-input-box");
    const res = await fetch("/backend/get_server_name");
    serverName = await res.json();
    if (serverName) {
        container.value = serverName;

        // rename the section from "Your Server" to the name
        const title = document.getElementById("server-section-name");
        title.textContent = `Your Server (${serverName})`;
    }
    // add listener to input box
    container.addEventListener("input", () => {
        serverSettingsListener();
    });

    // admin users
    completeAdminUserSelect();
}

function initAddRow() {
    // delete if exists
    if (document.getElementById("add-row")) { document.getElementById("add-row").remove(); }

    // row with "Add..." text (and dropdown button)
    const adminSelector = document.getElementById("admin-selector");
    // var for if the dropdown is currently open
    const dropdownCurrentlyOpen = adminSelector.classList.contains("dropdown");
    const addRow = cr("div", "add-row");
    if (admins.length > 3) { addRow.classList.add("top-shadow"); } // show shadow to indicate scrolling
    if (dropdownCurrentlyOpen) { addRow.classList.add("bottom-shadow"); } // bottom shadow when dropdown open
    // add-text
    const p = cr("p", "add-text", null);
    p.textContent="Add...";
    addRow.appendChild(p);
    // dropdown-button
    const dropdownButton = cr("div", "dropdown-button", null);
    const dropdownChevron = cr("p", "dropdown-chevron", null);
    dropdownChevron.textContent = dropdownCurrentlyOpen ? "⌃" : "⌄";
    dropdownChevron.classList.toggle("dropdown", !!dropdownCurrentlyOpen);
    dropdownButton.appendChild(dropdownChevron);
    addRow.appendChild(dropdownButton);
    // dropdown-button EVENT LISTENER
    dropdownButton.addEventListener("click", () => {
        let adminSelector = document.getElementById("admin-selector");
        adminSelector.classList.toggle("dropdown");
        let adminDropdown = document.getElementById("admin-dropdown");
        adminDropdown.classList.toggle("dropdown");
        completeAdminUserSelect();
    });
    adminSelector.appendChild(addRow);
}

const equal = (a, b) =>
    JSON.stringify(a) === JSON.stringify(b);

function serverSettingsListener() {
    // listener to determine, after any change to the settings, whether to show
    // the Save/Cancel buttons.
    const nameBox = document.getElementById("server-name-input-box");
    
    const serverSettingsButtons = document.getElementById("server-settings-buttons");
    if (nameBox.value.trim() !== serverName.trim() || !equal(admins, admins_init)) {
        showSaveCancelButtons();
    } else {
        hideSaveCancelButtons();
    }
}

function hideSaveCancelButtons() {
    const serverSettingsButtons = document.getElementById("server-settings-buttons");
    serverSettingsButtons.classList.add("hide");
}
function showSaveCancelButtons() {
    const serverSettingsButtons = document.getElementById("server-settings-buttons");
    serverSettingsButtons.classList.remove("hide");
}
function serverSettingsCancel() {
    // if the user clicks cancel, reset the namebox and admins list to original values.
    const nameBox = document.getElementById("server-name-input-box");
    nameBox.value = serverName;
    admins = [...admins_init];
    completeAdminUserSelect();
    const serverSettingsButtons = document.getElementById("server-settings-buttons");
    hideSaveCancelButtons();
}
function serverSettingsSave() {
    // save server name and/or admins list if updated
    const nameBox = document.getElementById("server-name-input-box");
    if (nameBox.value.trim() !== serverName.trim()) {
        updateServerName(nameBox.value.trim());
    }
    if (!equal(admins, admins_init)) {
        updateAdminsList(admins);
    }
    hideSaveCancelButtons();
}

async function updateAdminsList(list) {
    await fetch("/backend/set_admins", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            key: list
        })  
    });
    admins_init = [...admins];
}

async function updateServerName(name) {
    await fetch("/backend/set_server_name", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            key: name
        })
    });
    serverName = name;
    const title = document.getElementById("server-section-name");
    title.textContent = `Your Server (${serverName})`;
}

function initAddAdminsList() {
    // delete if exists
    if (document.getElementById("admin-dropdown")) { document.getElementById("admin-dropdown").remove(); }

    const adminSelector = document.getElementById("admin-selector");

    // admin-dropdown
    const adminDropdown = cr("div", "user-dropdown", "admin-dropdown");
    if (adminSelector.classList.contains("dropdown")) { adminDropdown.classList.add("dropdown"); }
    adminSelector.appendChild(adminDropdown);

    // only consider users who aren't already admins
    const adminUsernames = admins.map(e => e["username"]);
    const possibleUsers = users.filter(e => !adminUsernames.includes(e["username"]));
    
    // create a container for each such user
    for (let i = 0; i < possibleUsers.length; i++) {
        const user = possibleUsers[i];
        // user-container
        const userContainer = cr("div", "user-container", null);
        if (i === possibleUsers.length-1) { userContainer.classList.add("last"); }
        const friendlyName = cr("p", null, null);
        friendlyName.textContent = user["friendly_name"];
        friendlyName.style.fontWeight = '600';
        userContainer.appendChild(friendlyName);
        const username = cr("p", null, null);
        username.textContent = `(${user["username"]})`;
        userContainer.appendChild(username);
        adminDropdown.appendChild(userContainer);

        // add-button
        const addButton = cr("div", "add-button", null);
        const plus = cr("p", null, null);
        plus.textContent = "+";
        addButton.appendChild(plus);
        adminDropdown.appendChild(addButton);

        // add-button EVENT LISTENER
        addButton.addEventListener("click", () => {
            admins.push(user);
            completeAdminUserSelect();
            serverSettingsListener();
            const e = document.getElementById("list-of-admins");
            e.scrollTo(0, e.scrollHeight);
        });
        
    }
}

function completeAdminUserSelect() {
    /*

    <users-selector> ID=admin-selector
        <selector-list GRID>
            <user-container>
                //friendly_name,username
            </user-container>
            <remove-button/>
        </selector-list>
        <add-row>
            <add-text/>
            <dropdown-button>
                <dropdown-chevron/>
            </dropdown-button>
        </add-row>
        <admin-dropdown GRID>
            <user-container>
                //friendly_name,username
            </user-container>
            <add-button/>
        </admin-dropdown>
    </users-selector>

    */

    const adminSelector = document.getElementById("admin-selector");
    adminSelector.innerHTML = ""; // clear it before repopulating
    // list of users
    if (admins.length > 0) {
        const selectorList = cr("div", "selector-list", "list-of-admins");
        for (let i = 0; i < admins.length; i++) {
            let admin = admins[i];
            // user-container
            const userContainer = cr("div", "user-container", null);
            if (i === admins.length-1) { userContainer.classList.add("last"); }
                // friendly name
            const friendlyname = cr("p", null, null);
            friendlyname.textContent = admin["friendly_name"];
            friendlyname.style.fontWeight = '600';
            userContainer.appendChild(friendlyname);
                // username
            const username = cr("p",null,null);
            username.textContent = `(${admin["username"]})`;
            userContainer.appendChild(username);
            selectorList.appendChild(userContainer);
            // remove-button
            const removeButton = cr("div", "remove-button", null);
            if (i === admins.length-1) { removeButton.classList.add("last"); }
            const p = cr("p", null, null);
            p.textContent = "-";
            removeButton.appendChild(p);
            selectorList.appendChild(removeButton);
            // remove-button EVENT LISTENER
            removeButton.addEventListener("click", () => {
                admins.splice(admins.indexOf(admin), 1);
                completeAdminUserSelect();
                serverSettingsListener();
            });
        }
        adminSelector.appendChild(selectorList);
    }

    // row with "Add..." text (and dropdown button)
    initAddRow();

    // add list of users to add as admins
    initAddAdminsList();
}

function addListAdderButton() {
    const parent = document.getElementById("unsubscribe-list-selector");
    const existingButton = document.getElementById("unsubscribe-list-adder-button");
    if (!parent.classList.contains("typing-new-list")){
        if (existingButton) { existingButton.remove(); }
        return; 
    }
    else if (existingButton) { return; }

    console.log("ADDING");
    const container = document.getElementById("unsubscribe-list-adder");
    const btn = cr("div", "list-adder-button", "unsubscribe-list-adder-button");
    const p = cr("p",null,null);
    p.textContent = "+";
    btn.appendChild(p);
    container.appendChild(btn);
}

async function initUnsubscribeLists() {
    const res = await fetch("/backend/get_unsubscribe_lists");
    const lists = await res.json();
    
    const parent = document.getElementById("unsubscribe-list-selector");

    // add existing unsubscribe lists if there are any
    if (lists.length > 0) {
        const selector = cr("div", "selector", null);
        parent.appendChild(selector);
    }

    // add box to enter new unsubscribe list in
    const list_adder = cr("div", "list-adder", "unsubscribe-list-adder");
    const listAdderInp = cr("input", "connection-input-box", "list-adder-text");
    listAdderInp.placeholder="Enter new unsubscribe list name...";
    listAdderInp.addEventListener("input", (e) => {
        const par = document.getElementById("unsubscribe-list-selector");
        if (e.target.value !== "") {
            par.classList.add("typing-new-list");
        } else {
            par.classList.remove("typing-new-list");
        }
        addListAdderButton();
    });
    listAdderInp.addEventListener("focus", () => {
        const la = document.getElementById("unsubscribe-list-adder");
        la.classList.add("active");
    });
    listAdderInp.addEventListener("blur", () => {
        const la = document.getElementById("unsubscribe-list-adder");
        la.classList.remove("active");
    });
    list_adder.appendChild(listAdderInp);
    parent.appendChild(list_adder);
}

window.onload = async function() {
    let res = await fetch("/backend/get_users");
    users = await res.json();
    users_init = [...users];
    res = await fetch("/backend/get_admins");
    admins = await res.json();
    admins_init = [...admins];

    initTautulliURLInputBox();
    initTautulliAPIInputBox();
    initOverseerr();
    initSMTPInputBoxes();
    initServerSettings();
    initUnsubscribeLists();

    const r = await this.fetch("/backend/link_tautulli");
    const t = await r.json();
    console.log(t); 
}

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
let displayed_unsubscribe_list = "";
let unsubscribeLists, unsubscribeListsInit;
let unsubscribeUserSelector;
const list_name_map = {
    "newly_released_content_updates_unsubscribe_list": "Newly Released Content",
    "system_updates_unsubscribe_list": "System Updates"
}

async function initServerSettings(users) {
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

    initUnsubscribeLists(users);
}

/**
 * function to check for changes to any element in
 * the "Your Server" section. any change to:
 *      - Server Name
 *      - Admin Users
 *      - any unsubscribe list
 */
function checkForChanges() {
    // ---------- check Server Name and Admin Users ----------
    const input = document.getElementById("server-name-input-box");
    const hasNameChange = input.value.trim() !== serverNameInit;
    const hasAdminChange = !equal(admins, adminsInit);
    
    if (hasNameChange || hasAdminChange) {
        showSaveCancelButtons();
    } else {
        hideSaveCancelButtons();
    }

    // ---------- check unsubscribe lists ----------
    const haveUnsubscribeListsChanged = unsubscribeListsHaveChanged(unsubscribeLists, unsubscribeListsInit);
    
    if (haveUnsubscribeListsChanged) {
        // unsubscribe lists have been changed
        // show save/cancel buttons to save the unsubscribe lists 
        showUnsubscribeListSaveCancel();
    } else {
        // unsubscribe lists have NOT been changed
        // do nothing
        hideUnsubscribeListSaveCancel();
        return;
    }

}

// -------------------- Server Name & Admin Users --------------------

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


// -------------------- Email Unsubscribe Lists --------------------

/**
 * Compare two full arrays of unsubscribe lists by matching table names
 * @param {Array} currentLists - Array from get_unsubscribe_lists() (current state)
 * @param {Array} initialLists - Array from get_unsubscribe_lists() (cached/initial state)
 * @returns {boolean} - True if ANY list has changed (added, removed, or modified rows)
 */
function unsubscribeListsHaveChanged(currentLists, initialLists) {
    // Quick check: different number of tables means something changed
    if (currentLists.length !== initialLists.length) {
        return true;
    }

    // Build lookup map for initial lists by table_name
    const initialMap = new Map(initialLists.map(l => [l.table_name, l]));

    // Check each current list against its matching initial list
    for (const current of currentLists) {
        const initial = initialMap.get(current.table_name);
        
        // If table doesn't exist in initial, it's new
        if (!initial) {
            return true;
        }

        // Compare the two lists
        if (!unsubscribeListsEqual(current, initial)) {
            return true;
        }
    }

    return false;
}

/**
 * Deep equality check for two individual unsubscribe list objects
 * (your existing function, slightly cleaned up)
 */
function unsubscribeListsEqual(listA, listB) {
    // Check table names match
    if (listA.table_name !== listB.table_name) {
        return false;
    }

    // Check row counts match
    if (listA.rows.length !== listB.rows.length) {
        return false;
    }

    // Compare rows (order-independent using Set)
    const rowSignature = (row) => `${row.user_id}|${row.username}|${row.friendly_name}`;

    const setA = new Set(listA.rows.map(rowSignature));
    const setB = new Set(listB.rows.map(rowSignature));

    if (setA.size !== setB.size) return false;

    for (const sig of setA) {
        if (!setB.has(sig)) return false;
    }

    return true;
}

function getUnsubscribeListByTableName(tableName) {
    return unsubscribeLists.find(l => l.table_name === tableName) || null;
}

async function initUnsubscribeLists(users) {
    const res = await fetch("/backend/get_unsubscribe_lists");
    unsubscribeLists = await res.json();
    unsubscribeListsInit = structuredClone(unsubscribeLists);
    
    const parent = document.getElementById("unsubscribe-list-selector");

    // add existing unsubscribe lists if there are any
    for (const [index, list] of unsubscribeLists.entries()) {
        const selector = cr("div", "selector", list+"_selector");
        const translateAmount = 2 * (index);

        // translate to account for double borders of each selector
        selector.style.transform = `translateY(-${translateAmount}px)`;

        const listName = cr("p", null, null);
        const displayName = list_name_map[list["table_name"]] || list["table_name"];
        listName.textContent = displayName;
        selector.appendChild(listName);
        parent.appendChild(selector);

        const tableName = list.table_name;
        // add click event listeners
        selector.addEventListener("click", () => {
            // make Save/Cancel buttons visible (but hidden) if the displayed_unsubscribe_list is currently null.
            // (these elements hide beneath a container, but the list container only appears after choosing a list)
            if (!displayed_unsubscribe_list) {
                const buttons = document.getElementById("unsubscribe-list-buttons");
                buttons.classList.remove("invisible");
            }

            if (displayed_unsubscribe_list !== displayName) {
                // dsplay this unsubscribe list
                const freshList = getUnsubscribeListByTableName(tableName);
                if (freshList) { displayUnsubscribeList(freshList, users); }
            }

            // add class to selector to change its style
            document.querySelectorAll('.selector').forEach(el => el.classList.remove('selected'));
            selector.classList.add('selected');
        });
    }
}

async function displayUnsubscribeList(list, users) {
    // clear users-unsubscribe-selector element ready for new display
    document.getElementById("users-unsubscribe-selector").innerHTML = "";

    // store the currently displayed list
    displayed_unsubscribe_list = list_name_map[list.table_name] || list.table_name;

    // do not pass in the users list containing every field of each user,
    // filter it to keep just user_id, username, and friendly_name
    const pickFields = (obj, fields) => Object.fromEntries(fields.map(f => [f, obj[f]]));
    const filteredUsers = users.map(u => pickFields(u, ['user_id', 'username', 'friendly_name']));
    unsubscribedUsers = list['rows'];
    unsubscribeUserSelector = new UserListSelector(
        "users-unsubscribe-selector",
        unsubscribedUsers,
        filteredUsers,
        (newList) => {
            unsubscribedUsers = newList;
            checkForChanges();
        },
        "users-unsubscribe-dropdown"
    );
}

/**
 * gets the currently displayed unsubscribe list object from the
 * unsubscribeLists aray, using the name stored as the "displayed_unsubscribe_list".
 */
function getCurrentUnsubscribeList() {
    return unsubscribeLists.find(l =>
        (list_name_map[l.table_name] || l.table_name) === displayed_unsubscribe_list
    ) || null;
}

function hideUnsubscribeListSaveCancel() {
    document.getElementById("unsubscribe-list-buttons").classList.add("hide");
}

function showUnsubscribeListSaveCancel() {
    document.getElementById("unsubscribe-list-buttons").classList.remove("hide");
}

function unsubscribeListsSave() {
    // `unsubscribeLists` variable needs to be saved back to storage.
    // backend function /set_unsubscribe_list replaces an entire table with
    // the new provided list
    
    // first identify which lists changed
    console.log("SAVING LISTS...");
    const changedLists = [];
    for (const currentList of unsubscribeLists) {
        const initialList = unsubscribeListsInit.find(l => l.table_name === currentList.table_name);
        if (!initialList) {
            // list doesn't exist in initial, shouldn't happen but add it?
            changedLists.push(currentList);
            continue;
        }
        // check if list has changed
        const currentIds = new Set(currentList.rows.map(r => r.user_id));
        const initialIds = new Set(initialList.rows.map(r => r.user_id));
        // quick size check allows us to potentially skip detailed check
        if (currentIds.size !== initialIds.size) {
            changedLists.push(currentList);
            continue;
        }
        // detailed IDs comparison
        let hasChanges = false;
        for (const id of currentIds) {
            if (!initialIds.has(id)) {
                hasChanges = true;
                break;
            }
        }
        if (hasChanges) { changedLists.push(currentList); }
    }

    // separate backend call for each changed list
    const savePromises = changedLists.map(list => {
        const userIds = list.rows.map(r => r.user_id);
        return fetch("/backend/set_unsubscribe_list", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                table_name: list.table_name,
                user_ids: userIds
            })
        });
    });

    Promise.all(savePromises).then(() => {
        // update initial lists to match new, saved, lists.
        unsubscribeListsInit = structuredClone(unsubscribeLists);
        hideUnsubscribeListSaveCancel();
        // don't need to refresh UserListSelector.
    }).catch(err => {
        console.error("Failed to save unsubscribe lists ! ", err);
    });

}

function unsubscribeListsCancel() {
    // `unsubscribeLists` variabel should be reset to be `unsubscribeListsInit`
    unsubscribeLists = structuredClone(unsubscribeListsInit);
    hideUnsubscribeListSaveCancel();
    
    const currentListObj = getCurrentUnsubscribeList();
    
    if (currentListObj) {
        unsubscribeUserSelector.reset(currentListObj.rows);
    }
}

// -------------------- on load function --------------------
window.onload = async function() {
    const usersRes = await fetch("/backend/get_users");
    const users = await usersRes.json();
    const adminsRes = await fetch("/backend/get_admins");
    admins = await adminsRes.json();
    adminsInit = [...admins];

    initServerSettings(users);
    initTautulliURLInputBox();
    initTautulliAPIInputBox();
    initOverseerr();
    initSMTPInputBoxes();

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
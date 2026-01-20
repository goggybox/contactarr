
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

export let selecting_users = false;
export let selected_users = [];
let users;
let selected_email = "server";

function saveServerTextArea(value) {
    localStorage.setItem("ServerHtmlTextArea", value);
}

function loadServerTextArea() {
    let value = localStorage.getItem("ServerHtmlTextArea");
    const htmlEmail = document.getElementById("server-content-container");
    console.log(value);
    if (value === "" || value === null) {
        // use default email structure
        value = "<h2>Example Email Template</h2>\n";
        value += "<p>Dear Plex users,</p>\n"
        value += "<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec ac lectus eget lacus efficitur scelerisque. Mauris a lectus nec lectus pharetra congue et a ligula. Suspendisse velit nulla, dignissim sit amet imperdiet faucibus, dictum eget magna. Aenean sagittis risus in massa porttitor fermentum.</p>\n";
        value += "<p>Phasellus et libero vel tellus facilisis ultricies. Vivamus pellentesque lacus et elit vulputate, ut elementum arcu varius. Quisque sed maximus odio. Quisque ac leo iaculis, dapibus tortor id, cursus nisl. Nullam sagittis arcu sed dui suscipit pellentesque in id elit. Fusce nec semper risus. Suspendisse orci odio, posuere tempus quam id, commodo dictum arcu. Maecenas ac lacus quis massa euismod tincidunt et tristique quam. Vestibulum commodo bibendum efficitur.</p>\n";
    }
    htmlEmail.innerHTML = value;
    return value;
}

function getLineStart(text, index) {
  return text.lastIndexOf("\n", index - 1) + 1;
}

function getLineEnd(text, index) {
  const nextNewline = text.indexOf("\n", index);
  return nextNewline === -1 ? text.length : nextNewline;
}

function textAreaListeners() {
    // add input listener to HTML input
    const htmlInput = document.getElementById("htmlInput");
    const serverContentContainer = document.getElementById("server-content-container");
    htmlInput.addEventListener('input', () => {
        // update the HTML email being displayed
        serverContentContainer.innerHTML = htmlInput.value;
        // save the changes to browser storage
        saveServerTextArea(htmlInput.value);
    });

    // modify behaviour of Tab
    const INDENT = "  ";
    htmlInput.addEventListener('keydown', (e) => {
        if (e.key !== "Tab") return;

        e.preventDefault();

        // get selected text area    
        const rawStart = htmlInput.selectionStart;
        const rawEnd = htmlInput.selectionEnd;
        const start = getLineStart(htmlInput.value, rawStart);
        const end = getLineEnd(htmlInput.value, rawEnd);
        const value = htmlInput.value;
        const selected = value.slice(start, end);

        if (selected.includes("\n")) {
            // multiple lines are selected
            const lines = selected.split("\n");

            if (e.shiftKey) {
                // unindent
                console.log(lines[0].startsWith(INDENT));
                const unindented = lines.map(line =>
                    line.startsWith(INDENT)
                        ? line.slice(INDENT.length)
                        : line.startsWith("\t")
                            ? line.slice(1)
                            : line
                );

                console.log(`Start: ${rawStart}, ${start}`);
                console.log(`End: ${rawEnd}, ${end}`);
                console.log(`Has first line changed: ${lines[0]===unindented[0]}`);
                console.log(`Has last line changed: ${lines[lines.length-1]===unindented[unindented.length-1]}`);

                // insert back into textarea
                htmlInput.value = 
                    value.slice(0, start) +
                    unindented.join("\n") +
                    value.slice(end);


                // make sure the text is still selected
                //  - if first line has not changed, it was not unindented, so don't move the selectionStart
                //  - same for the last line.
                const changeStart = lines[0] !== unindented[0];
                const changeEnd = lines[lines.length - 1] !== unindented[unindented.length - 1];
                htmlInput.selectionStart = changeStart ? rawStart - INDENT.length : rawStart;
                htmlInput.selectionEnd = changeEnd ? rawEnd - (INDENT.length * unindented.length) : rawEnd;
            } else {
                // indent
                const indented = lines.map(line => INDENT + line);

                // insert back into textarea
                htmlInput.value =
                    value.slice(0, start) +
                    indented.join("\n") +
                    value.slice(end);

                // make sure the text is still selected
                htmlInput.selectionStart = rawStart + INDENT.length;
                htmlInput.selectionEnd = rawEnd + (INDENT.length * indented.length);
            }
        } else {
            // single line / no selection (just the line the caret is on).
            if (e.shiftKey) {
                // unindent single line
                if (value.slice(start, start + INDENT.length) === INDENT) {
                    htmlInput.value =
                        value.slice(0, start) +
                        value.slice(start + INDENT.length);

                    // make sure the text is still selected
                    htmlInput.selectionStart = rawStart - INDENT.length;
                    htmlInput.selectionEnd = rawEnd - INDENT.length;
                }
            } else {
                // indent single line
                // htmlInput.selectionStart = start;
                // htmlInput.selectionEnd = start + INDENT.length;
                htmlInput.value = 
                    value.slice(0, rawStart) +
                    INDENT + value.slice(rawStart);

                htmlInput.selectionStart = rawStart + INDENT.length;
                htmlInput.selectionEnd = rawEnd + INDENT.length;
            }
        }
    });
}

function displayTautulliError() {
    const listContainer = document.getElementById("user-list");
    const msgContainer = document.createElement("div");
    msgContainer.classList.add("tautulli-error-message-container");
    listContainer.appendChild(msgContainer);

    const msg = document.createElement("p");
    msg.classList.add("tautulli-error-message");
    msg.textContent = "Could not connect to Tautulli...";
    msgContainer.appendChild(msg);
}

function clickSelectUsersButton(button) {
    button.classList.toggle("selecting");
    button.textContent = button.classList.contains("selecting") ? "Cancel Selection" : "Select Users";
    const checkboxes = document.getElementsByClassName("user-container-checkbox");
    for (const checkbox of checkboxes) {
        checkbox.classList.toggle("hidden");
    }
    const selectUsersButtons = document.getElementById("select-users-buttons");
    selectUsersButtons.classList.toggle("hidden");
}

function clickUserCheckbox(checkbox) {
    const username = checkbox.textContent;
    if (checkbox.checked) {
        // the checkbox was clicked and is now checked
        if (!selected_users.includes(username)) { selected_users.push(username); }
    } else {
        // the checkbox was clicked and is now unchecked
        if (selected_users.includes(username)) { selected_users.splice(selected_users.indexOf(username), 1); }
    }

    updateSelectUsersButtons();
}

function updateSelectUsersButtons() {
    const selectAllUsersButton = document.getElementById("select-all-users-button");
    const deselectAllUsersButton = document.getElementById("deselect-all-users-button");
    const checkboxes = document.getElementsByClassName("user-container-checkbox");
    let allSelected = true;
    let allUnselected = true;
    for (const checkbox of checkboxes) {
        if (!checkbox.checked) { allSelected = false; }
        else { allUnselected = false; }
    }

    selectAllUsersButton.classList.toggle("selected", allSelected);
    deselectAllUsersButton.classList.toggle("unselected", allUnselected);
}

function selectAllUsers() {
    const checkboxes = document.getElementsByClassName("user-container-checkbox");
    for (const checkbox of checkboxes) {
        checkbox.checked = true;
        clickUserCheckbox(checkbox);
    }

    console.log(selected_users);
}

function deselectAllUsers() {
    const checkboxes = document.getElementsByClassName("user-container-checkbox");
    for (const checkbox of checkboxes) {
        checkbox.checked = false;
        clickUserCheckbox(checkbox);
    }

    console.log(selected_users);
}

function displayUsers(users) {
    // HTML structure for each user container:checkboxes.classList.
    // <div class="user-container">
    //     <div class="user-left">
    //         <input type="checkbox" class="user-container-checkbox hidden">
    //         <div class="user-container-info">
    //             <div class="user-name">
    //                 <p class="name">Aidan</p>
    //                 <p class="username">(aidanc2030)</p>
    //             </div>
    //             <p class="email">me@aidan.digital</p>
    //         </div>
    //     </div>
    //     <div class="user-right">
    //         <p>Last seen:</p>
    //         <p>NEVER</p>
    //     </div>
    // </div>
    const listContainer = document.getElementById("user-list");
    for (const [index, user] of users.entries()) {
        // user-containeri
        const userContainer = document.createElement("div");
        userContainer.classList.add("user-container");
        listContainer.appendChild(userContainer);
        // add #last id if this is the last user
        if (index === users.length -1) {
            userContainer.id = "last";
        }
        // user-left
        const userLeft = document.createElement("div");
        userLeft.classList.add("user-left");
        userContainer.appendChild(userLeft);
        // user-container-checkbox
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.classList.add("user-container-checkbox", "hidden");
        checkbox.textContent = user["username"];
        checkbox.addEventListener("click", () => {clickUserCheckbox(checkbox)});
        userLeft.appendChild(checkbox);
        // user-container-info
        const containerInfo = document.createElement("div");
        containerInfo.classList.add("user-container-info");
        userLeft.appendChild(containerInfo);
        // user-name
        const userName = document.createElement("div");
        userName.classList.add("user-name");
        containerInfo.appendChild(userName);
        // name
        const name = document.createElement("p");
        name.textContent = user['friendly_name'] ?? "-";
        name.classList.add("name");
        userName.appendChild(name);
        // username
        const username = document.createElement("p");
        username.textContent = user['username'] ?? "-";
        username.classList.add("username");
        userName.appendChild(username);
        // email
        const email = document.createElement("p");
        email.textContent = user['email'] ?? "-";
        email.classList.add("email");
        containerInfo.appendChild(email);
        // user-right
        const userRight = document.createElement("div");
        userRight.classList.add("user-right");
        userContainer.appendChild(userRight);
        // p last seen
        const lastSeen = document.createElement("p");
        lastSeen.textContent = user['last_seen_formatted'] === "" ? "" : `Seen ${user['last_seen_formatted']}`;
        lastSeen.classList.add("last-seen");
        userRight.appendChild(lastSeen);
        // last-seen
        const lastSeenDate = document.createElement("p");
        lastSeenDate.textContent = user['last_seen_date'] ?? "Never Seen";
        lastSeenDate.classList.add("last-seen-date");
        userRight.appendChild(lastSeenDate);

    }

    // attach checkbox toggle event to Select Users button
    const button = document.getElementById("server-select-users-button");
    button.addEventListener("click", () => {clickSelectUsersButton(button)});

    // attach event to "Select All" users button.
    const selectAllUsersButton = document.getElementById("select-all-users-button");
    selectAllUsersButton.addEventListener("click", selectAllUsers);

    // attach event to "Deselect All" users button.
    const deselectAllUsersButton = document.getElementById("deselect-all-users-button");
    deselectAllUsersButton.addEventListener("click", deselectAllUsers);
}

function displayEmail(service) {
    // display the example email for titan.
    // STRUCTURE:
    //   <div class="titan-email-container">
    //     <img src="titan-banner.png" alt="Banner" class="titan-banner">
    //     <div class="titan-content-container">
    //       <h2>Don't Worry About "Failed" Movie Requests</h2>
    //       <p>
    //         Hi, it's Aidan & George!
    //       </p>
    //       ...
    //     </div>
    //     <div class="titan-footer">
    //         <p>You can unsubscribe from receiving new content notifications and/or service updates. To do so, reply to this email and specify which (or both) you would like to unsubscribe from.</p>
    //       </div>
    //   </div>

    const embedContainer = document.getElementById("embed-container");
    embedContainer.innerHTML = '';

    if (service === "server") {
        // server-email-container
        const serverEmailContainer = document.createElement("div");
        serverEmailContainer.classList.add("server-email-container");
        embedContainer.appendChild(serverEmailContainer);

        // img
        const img = document.createElement("img");
        img.classList.add("server-banner");
        img.src = '/emails/server/banner.png';
        serverEmailContainer.appendChild(img);

        // content-container
        const contentContainer = document.createElement("div");
        contentContainer.id = "server-content-container";
        serverEmailContainer.appendChild(contentContainer);

        // footer
        const footer = document.createElement("div");
        footer.classList.add("server-footer");
        const p = document.createElement("p");
        p.textContent = "You can unsubscribe from email notifications by replying to this email.";
        footer.appendChild(p);
        serverEmailContainer.appendChild(footer);
        
        // load textarea value
        const htmlInput = document.getElementById("htmlInput");
        htmlInput.value = loadServerTextArea();

        textAreaListeners();
    }

}

function serverSelected() {
    displayEmail(selected_email);
}

window.onload = async function() {
    // load array of Tautulli users when dashboard loads
    let res = await fetch ("/backend/tautulli/get_users");
    
    if (res.status === 200) {
        users = await res.json();
        displayUsers(users);
        displayEmail(selected_email);
    } else {
        // could not connect to tautulli
        displayTautulliError();
    }
}
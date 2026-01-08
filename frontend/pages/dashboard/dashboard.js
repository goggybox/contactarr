
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
let selected_email = "titan";

function saveTitanTextArea(value) {
    localStorage.setItem("TitanHtmlTextArea", value);
}

function loadTitanTextArea() {
    const value = localStorage.getItem("TitanHtmlTextArea");
    const htmlEmail = document.getElementById("titan-content-container");
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
    const titanContentContainer = document.getElementById("titan-content-container");
    htmlInput.addEventListener('input', () => {
        // update the HTML email being displayed
        titanContentContainer.innerHTML = htmlInput.value;
        // save the changes to browser storage
        saveTitanTextArea(htmlInput.value);
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

function displayUsers(users) {
    // HTML structure for each user container:
    // <div class="user-container">
    //     <div class="user-left">
    //         <div class="user-name">
    //             <p class="name">Aidan</p>
    //             <p class="username">(aidanc2030)</p>
    //         </div>
    //         <p class="email">me@aidan.digital</p>
    //     </div>
    //     <div class="user-right">
    //         <p>Last seen:</p>
    //         <p>NEVER</p>
    //     </div>
    // </div>
    const listContainer = document.getElementById("user-list");
    for (const [index, user] of users.entries()) {
        // user-containeri("titan-cont
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
        // user-name
        const userName = document.createElement("div");
        userName.classList.add("user-name");
        userLeft.appendChild(userName);
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
        userLeft.appendChild(email);
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

    if (service === "titan") {
        // titan-email-container
        const titanEmailContainer = document.createElement("div");
        titanEmailContainer.classList.add("titan-email-container");
        embedContainer.appendChild(titanEmailContainer);

        // img
        const img = document.createElement("img");
        img.classList.add("titan-banner");
        img.src = '/emails/titan/banner.png';
        titanEmailContainer.appendChild(img);

        // content-container
        const contentContainer = document.createElement("div");
        contentContainer.id = "titan-content-container";
        titanEmailContainer.appendChild(contentContainer);

        // footer
        const footer = document.createElement("div");
        footer.classList.add("titan-footer");
        const p = document.createElement("p");
        p.textContent = "You can unsubscribe from receiving new content notifications and/or service updates. To do so, reply to this email and specify which (or both) you would like to unsubscribe from.";
        footer.appendChild(p);
        titanEmailContainer.appendChild(footer);
        
        // load textarea value
        const htmlInput = document.getElementById("htmlInput");
        htmlInput.value = loadTitanTextArea();

        textAreaListeners();
    }

}

function titanSelected() {
    displayEmail(selected_email);
}

window.onload = async function() {
    // load aray of Tautulli users when dashboard loads
    res = await fetch ("/backend/tautulli/get_users");
    
    if (res.status === 200) {
        users = await res.json();
        displayUsers(users);
        displayEmail(selected_email);
    } else {
        // could not connect to tautulli
        displayTautulliError();
    }
}
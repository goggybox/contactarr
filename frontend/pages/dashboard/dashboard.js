
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


// -------------------- vars and consts --------------------
const INDENT = "  ";
const DEFAULT_EMAIL_CONTENT = `<h2>Example Email Template</h2>
<p>Dear Plex users,</p>
<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec ac lectus eget lacus efficitur scelerisque. Mauris a lectus nec lectus pharetra congue et a ligula. Suspendisse velit nulla, dignissim sit amet imperdiet faucibus, dictum eget magna. Aenean sagittis risus in massa porttitor fermentum.</p>
<p>Phasellus et libero vel tellus facilisis ultricies. Vivamus pellentesque lacus et elit vulputate, ut elementum arcu varius. Quisque sed maximus odio. Quisque ac leo iaculis, dapibus tortor id, cursus nisl. Nullam sagittis arcu sed dui suscipit pellentesque in id elit. Fusce nec semper risus. Suspendisse orci odio, posuere tempus quam id, commodo dictum arcu. Maecenas ac lacus quis massa euismod tincidunt et tristique quam. Vestibulum commodo bibendum efficitur.</p>`;

const DEFAULT_FOOTER_CONTENT = `You can unsubscribe from email notifications by replying to this email.`;

export let selecting_users = false;
export let selected_users = [];
let users;
let selected_email = "server";

// -------------------- text area functions --------------------

function getLineStart(text, index) {
  return text.lastIndexOf("\n", index - 1) + 1;
}

function getLineEnd(text, index) {
  const nextNewline = text.indexOf("\n", index);
  return nextNewline === -1 ? text.length : nextNewline;
}

function handleTabIndentation(textarea, e) {
    if (e.key !== "Tab") { return; }
    e.preventDefault();

    // get selected text area
    const rawStart = textarea.selectionStart;
    const rawEnd = textarea.selectionEnd;
    const start = getLineStart(textarea.value, rawStart);
    const end = getLineEnd(textarea.value, rawEnd);
    const value = textarea.value;
    const selected = value.slice(start, end);

    if (selected.includes("\n")) {
        // multiple lines are selected
        handleMultiLineIndent(textarea, rawStart, rawEnd, start, end, selected, e.shiftKey);
    } else {
        // single line / no selection (just the line the caret is on).
        handleSingleLineIndent(textarea, rawStart, rawEnd, start, value, e.shiftKey);
    }
    return;
}

function handleMultiLineIndent(textarea, rawStart, rawEnd, start, end, selected, isUnindent) {
    const lines = selected.split("\n");

    let processedLines;
    if (isUnindent) {
        processedLines = lines.map(line =>
            line.startsWith(INDENT) ? line.slice(INDENT.length) :
            line.startsWith("\t") ? line.slice(1) : line
        );
    } else {
        processedLines = lines.map(line => INDENT + line);
    }

    textarea.value = textarea.value.slice(0, start) + processedLines.join("\n") + textarea.value.slice(end);
    
    const firstLineChanged = lines[0] !== processedLines[0];
    const lastLineChanged = lines[lines.length - 1] !== processedLines[processedLines.length - 1];

    textarea.selectionStart = firstLineChanged ? rawStart - INDENT.length : rawStart;
    textarea.selectionEnd = lastLineChanged ?
        rawEnd - (INDENT.length * (isUnindent ? 1 : -1) * (firstLineChanged ? 1 : 0)) :
        rawEnd + (isUnindent ? 0 : INDENT.length * processedLines.length);

}

function handleSingleLineIndent(textarea, rawStart, rawEnd, start, value, isUnindent) {
    if (isUnindent) {
        if (value.slice(start, start + INDENT.length) === INDENT) {
            textarea.value = value.slice(0, start) + value.slice(start + INDENT.length);
            textarea.selectionStart = rawStart - INDENT.length;
            textarea.selectionEnd = rawEnd - INDENT.length;
        }
    } else {
        textarea.value = value.slice(0, rawStart) + INDENT + value.slice(rawStart);
        textarea.selectionStart = rawStart + INDENT.length;
        textarea.selectionEnd = rawEnd + INDENT.length;
    }
}

// -------------------- email content managers --------------------

function loadEmailContent() {
    const content = localStorage.getItem("ServerHTMLTextArea");
    const footer = localStorage.getItem("ServerFooterTextArea");

    return {
        content: (content === "" || content === null) ? DEFAULT_EMAIL_CONTENT : content,
        footer: (footer === "" || footer === null) ? DEFAULT_FOOTER_CONTENT : footer
    };
}

function saveEmailContent(value) {
    localStorage.setItem("ServerHTMLTextArea", value);
}

function saveEmailFooter(value) {
    localStorage.setItem("ServerFooterTextArea", value);
}

// -------------------- UI components --------------------

function createUserContainer(user, index, totalUsers) {
    const userContainer = document.createElement("div");
    userContainer.classList.add("user-container");
    if (index === totalUsers - 1) userContainer.id = "last";

    const userLeft = document.createElement("div");
    userLeft.classList.add("user-left");
    
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.classList.add("user-container-checkbox", "hidden");
    checkbox.textContent = user.username;
    checkbox.addEventListener("click", () => clickUserCheckbox(checkbox));
    
    const containerInfo = document.createElement("div");
    containerInfo.classList.add("user-container-info");

    const userName = document.createElement("div");
    userName.classList.add("user-name");
    
    const name = document.createElement("p");
    name.textContent = user.friendly_name ?? "-";
    name.classList.add("name");
    
    const username = document.createElement("p");
    username.textContent = user.username ?? "-";
    username.classList.add("username");
    
    userName.append(name, username);

    const email = document.createElement("p");
    email.textContent = user.email ?? "-";
    email.classList.add("email");

    containerInfo.append(userName, email);
    userLeft.append(checkbox, containerInfo);

    const userRight = document.createElement("div");
    userRight.classList.add("user-right");
    
    const lastSeen = document.createElement("p");
    lastSeen.textContent = user.last_seen_formatted ? `Seen ${user.last_seen_formatted}` : "";
    lastSeen.classList.add("last-seen");
    
    const lastSeenDate = document.createElement("p");
    lastSeenDate.textContent = user.last_seen_date ?? "Never Seen";
    lastSeenDate.classList.add("last-seen-date");
    
    userRight.append(lastSeen, lastSeenDate);
    userContainer.append(userLeft, userRight);
    
    return userContainer;
}

function displayUsers(users) {
    const listContainer = document.getElementById("user-list");
    listContainer.innerHTML = "";

    users.forEach((user, index) => {
        listContainer.appendChild(createUserContainer(user, index, users.length));
    });

    document.getElementById("server-select-users-button").addEventListener("click", function() {
        clickSelectUsersButton(this);
    });

    document.getElementById("select-all-users-button").addEventListener("click", selectAllUsers);

    document.getElementById("deselect-all-users-button").addEventListener("click", deselectAllUsers);
}

function displayEmail(service) {
    const embedContainer = document.getElementById("embed-container");
    embedContainer.innerHTML = "";

    if (service !== "server") { return; }

    const serverEmailContainer = document.createElement("div");
    serverEmailContainer.classList.add("server-email-container");

    const img = document.createElement("img");
    img.classList.add("server-banner");
    img.src = '/emails/server/banner.png';

    const contentContainer = document.createElement("div");
    contentContainer.id = "server-content-container";

    const footer = document.createElement("div");
    footer.classList.add("server-footer");
    const footerP = document.createElement("p");
    footerP.id = "server-footer-text";
    footer.appendChild(footerP);

    serverEmailContainer.append(img, contentContainer, footer);
    embedContainer.appendChild(serverEmailContainer);

    const { contentTextarea, footerTextarea } = setupEmailEditors(contentContainer, footerP);
    
    const saved = loadEmailContent();
    contentTextarea.value = saved.content;
    footerTextarea.value = saved.footer;
    
    contentContainer.innerHTML = saved.content;
    footerP.textContent = saved.footer;
}

function setupEmailEditors(contentContainer, footerElement) {
    const contentTextarea = document.getElementById("htmlInput");
    const footerTextarea = document.getElementById("footerInput");

    contentTextarea.addEventListener('input', () => {
        contentContainer.innerHTML = contentTextarea.value;
        saveEmailContent(contentTextarea.value);
    });

    footerTextarea.addEventListener('input', () => {
        footerElement.textContent = footerTextarea.value;
        saveEmailFooter(footerTextarea.value);
    });

    contentTextarea.addEventListener('keydown', (e) => handleTabIndentation(contentTextarea, e));
    footerTextarea.addEventListener('keydown', (e) => handleTabIndentation(footerTextarea, e));

    return { contentTextarea, footerTextarea };
}

function displayTautulliError() {
    const listContainer = document.getElementById("user-list");
    const msgContainer = document.createElement("div");
    msgContainer.classList.add("tautulli-error-message-container");
    
    const msg = document.createElement("p");
    msg.classList.add("tautulli-error-message");
    msg.textContent = "Could not connect to Tautulli...";
    
    msgContainer.appendChild(msg);
    listContainer.appendChild(msgContainer);
}

// -------------------- user selection --------------------

function clickSelectUsersButton(button) {
    selecting_users = !selecting_users;
    button.classList.toggle("selecting", selecting_users);
    button.textContent = selecting_users ? "Cancel Selection" : "Select Users";
    
    document.querySelectorAll(".user-container-checkbox").forEach(cb => {
        cb.classList.toggle("hidden", !selecting_users);
    });
    
    document.getElementById("select-users-buttons").classList.toggle("hidden", !selecting_users);
}

function clickUserCheckbox(checkbox) {
    const username = checkbox.textContent;
    
    if (checkbox.checked) {
        if (!selected_users.includes(username)) selected_users.push(username);
    } else {
        const index = selected_users.indexOf(username);
        if (index > -1) selected_users.splice(index, 1);
    }
    
    updateSelectUsersButtons();
}

function updateSelectUsersButtons() {
    const checkboxes = document.querySelectorAll(".user-container-checkbox");
    const allSelected = Array.from(checkboxes).every(cb => cb.checked);
    const allUnselected = Array.from(checkboxes).every(cb => !cb.checked);

    document.getElementById("select-all-users-button").classList.toggle("selected", allSelected);
    document.getElementById("deselect-all-users-button").classList.toggle("unselected", allUnselected);
}

function selectAllUsers() {
    document.querySelectorAll(".user-container-checkbox").forEach(cb => {
        cb.checked = true;
        clickUserCheckbox(cb);
    });
}

function deselectAllUsers() {
    document.querySelectorAll(".user-container-checkbox").forEach(cb => {
        cb.checked = false;
        clickUserCheckbox(cb);
    });
    selected_users = [];
}

// -------------------- init --------------------

window.onload = async function() {
    try {
        const res = await fetch("/backend/tautulli/get_users");

        if (res.status !== 200) { throw new Error("Tautulli connection failed"); }

        users = await res.json();
        displayUsers(users);
        displayEmail(selected_email);
    } catch (error) {
        console.error("Dashboard initialisation error: ", error);
        displayTautulliError();
    }
}
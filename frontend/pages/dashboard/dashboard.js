
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

import { buildEmailHtml, sendIndividualEmailsWithProgress } from "./emailSender.js";

// -------------------- vars and consts --------------------
const INDENT = "  ";
const EMAIL_TYPES = {
    SERVER: "server",
    OVERSEERR: "overseerr"
};

const DEFAULTS = {
    [EMAIL_TYPES.SERVER]: {
        content: `<h2>Example Email Template</h2>
<p>Dear Plex users,</p>
<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec ac lectus eget lacus efficitur scelerisque. Mauris a lectus nec lectus pharetra congue et a ligula. Suspendisse velit nulla, dignissim sit amet imperdiet faucibus, dictum eget magna. Aenean sagittis risus in massa porttitor fermentum.</p>
<p>Phasellus et libero vel tellus facilisis ultricies. Vivamus pellentesque lacus et elit vulputate, ut elementum arcu varius. Quisque sed maximus odio. Quisque ac leo iaculis, dapibus tortor id, cursus nisl. Nullam sagittis arcu sed dui suscipit pellentesque in id elit. Fusce nec semper risus. Suspendisse orci odio, posuere tempus quam id, commodo dictum arcu. Maecenas ac lacus quis massa euismod tincidunt et tristique quam. Vestibulum commodo bibendum efficitur.</p>`,
        footer: `You can unsubscribe from email notifications by replying to this email.`
    },
    [EMAIL_TYPES.OVERSEERR]: {
        content: `<p>Hi {{user}}</p>`,
        footer: ``
    }
}

export let selecting_users = false;
export let selected_users = [];
let selected_requests = [];
let users;
let selected_email = EMAIL_TYPES.SERVER;
let systemUpdatesUnsubscribeList = [];

function getUserByUsername(username) {
    return users.find(u => u.username === username) || null;
}

function cr(type, clss, id) {
    const elem = document.createElement(type);
    if (clss) { elem.classList.add(clss); }
    if (id) { elem.id = id; }
    return elem;
}

// -------------------- STORAGE MANAGEMENT --------------------

const getStorageKey = (emailType, field) => `${emailType.charAt(0).toUpperCase() + emailType.slice(1)}${field}TextArea`;

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

function loadEmailContent(emailType) {
    const content = localStorage.getItem(getStorageKey(emailType, "HTML"));
    const footer = localStorage.getItem(getStorageKey(emailType, "Footer"));
    const defaults = DEFAULTS[emailType];

    return {
        content: (content ?? "") === "" ? defaults.content : content,
        footer:  (footer  ?? "") === "" ? defaults.footer  : footer
    };
}

function saveEmailContent(emailType, value) {
    localStorage.setItem(getStorageKey(emailType, "HTML"), value);
}

function saveEmailFooter(emailType, value) {
    localStorage.setItem(getStorageKey(emailType, "Footer"), value);
}

// -------------------- UI components --------------------

function createUserContainer(user, index, totalUsers) {
    const userContainer = document.createElement("div");
    userContainer.classList.add("user-container");
    if (index === totalUsers - 1) userContainer.id = "last";

    // if user is in unsubscribed list, their name should be red when selecting users.
    const isUnsubscribed = systemUpdatesUnsubscribeList.includes(parseInt(user.user_id));
    if (isUnsubscribed) { userContainer.classList.add("unsubscribed"); }

    const userLeft = document.createElement("div");
    userLeft.classList.add("user-left");
    
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.classList.add("user-container-checkbox", "hidden");
    checkbox.textContent = user.username;
    checkbox.dataset.userId = user.user_id;
    checkbox.addEventListener("click", () => clickUserCheckbox(checkbox));
    
    const containerInfo = document.createElement("div");
    containerInfo.classList.add("user-container-info");

    const userName = document.createElement("div");
    userName.classList.add("user-name");
    
    const name = createUserInfoElement(user.friendly_name ?? "-", "name", isUnsubscribed);
    const username = createUserInfoElement(user.username ?? "-", "username", isUnsubscribed);

    userName.append(name, username);

    const email = createUserInfoElement(user.email ?? "-", "email", isUnsubscribed);

    containerInfo.append(userName, email);
    userLeft.append(checkbox, containerInfo);

    const userRight = document.createElement("div");
    userRight.classList.add("user-right");

    const lastSeen = createUserInfoElement(
        user.last_seen_formatted ? `Seen ${user.last_seen_formatted}` : "",
        "last-seen",
        isUnsubscribed
    );
    const lastSeenDate = createUserInfoElement(
        user.last_seen_date ?? "Never Seen",
        "last-seen-date",
        isUnsubscribed
    );

    userRight.append(lastSeen, lastSeenDate);
    userContainer.append(userLeft, userRight);

    return userContainer;
}

function createUserInfoElement(text, className, isUnsubscribed) {
    const el = document.createElement("p");
    el.textContent = text;
    el.classList.add(className);
    if (isUnsubscribed) { el.classList.add("unsubscribed"); }
    return el;
}

async function fetchUnsubscribeLists() {
    try {
        const res = await fetch("/backend/get_unsubscribe_lists");
        if (res.status === 200) {
            const lists = await res.json();
            const systemUpdatesList = lists.find(l => l.table_name === "system_updates_unsubscribe_list");
            if (systemUpdatesList) {
                systemUpdatesUnsubscribeList = systemUpdatesList.rows.map(r => r.user_id);
            }
        }
    } catch (error) {
        console.error("Failed to fetch unsubscribe list: ", error);
    }
}

function displayUsers(users) {
    const listContainer = document.getElementById("user-list");
    listContainer.innerHTML = "";

    users.forEach((user, index) => {
        listContainer.appendChild(createUserContainer(user, index, users.length));
    });

    document.getElementById("server-select-users-button").addEventListener("click", function() {
        clickSelectUsersButton(this, EMAIL_TYPES.SERVER);
    });

    // TODO: overseerr-select-users-button event clicker
    document.getElementById("overseerr-select-users-button").addEventListener("click", function () {
        clickSelectUsersButton(this, EMAIL_TYPES.OVERSEERR);
    });

    document.getElementById("select-subscribed-users-button").addEventListener("click", selectSubscribedUsers);

    document.getElementById("select-all-users-button").addEventListener("click", selectAllUsers);

    document.getElementById("deselect-all-users-button").addEventListener("click", deselectAllUsers);
}

// -------------------- email display components --------------------

function selectEmailType(emailType) {
    // first, for current email, deselect all selected_users, and close selection if open.
    clearSelectedUsers();
    let button;
    if (emailType == EMAIL_TYPES.SERVER) { button = document.getElementById("overseerr-select-users-button"); } // switching to server, so currently overseerr.
    else { button = document.getElementById("server-select-users-button"); } // vice versa

    if (selecting_users) { clickSelectUsersButton(button, emailType); }

    selected_email = emailType;
    updateEmailSelectorUI(emailType);
    displayEmail(emailType);
}

function updateEmailSelectorUI(emailType) {
    const isServer = emailType === EMAIL_TYPES.SERVER;
    document.getElementById("server-selector").classList.toggle("selected", isServer);
    document.getElementById("overseerr-selector").classList.toggle("selected", !isServer);
    document.getElementById("server-inner-email-container").classList.toggle("hidden", !isServer);
    document.getElementById("overseerr-inner-email-container").classList.toggle("hidden", isServer);
}

function displayEmail(emailType) {
    const embedContainer = document.getElementById(`${emailType}-embed-container`);
    embedContainer.innerHTML = "";

    const emailContainer = document.createElement("div");
    emailContainer.classList.add(`${emailType}-email-container`);

    const img = document.createElement("img");
    img.classList.add(`${emailType}-banner`);
    img.src = `emails/${emailType}/banner.png`;

    const contentContainer = document.createElement("div");
    contentContainer.id = `${emailType}-content-container`;

    const footer = document.createElement("div");
    footer.classList.add(`${emailType}-footer`);
    const footerP = document.createElement("p");
    footerP.id = `${emailType}-footer-text`;
    footer.appendChild(footerP);

    emailContainer.append(img, contentContainer, footer);

    embedContainer.appendChild(emailContainer);

    const { contentTextarea, footerTextarea } = setupEmailEditors(emailType, contentContainer, footerP);

    const saved = loadEmailContent(emailType);
    contentTextarea.value = saved.content;
    footerTextarea.value = saved.footer;
    contentContainer.innerHTML = saved.content;
    footerP.textContent = saved.footer;
}

function setupEmailEditors(email, contentContainer, footerElement) {
    const contentTextarea = document.getElementById(`${email}-htmlInput`);
    const footerTextarea = document.getElementById(`${email}-footerInput`);

    contentTextarea.addEventListener('input', () => {
        contentContainer.innerHTML = contentTextarea.value;
        saveEmailContent(email, contentTextarea.value);
    });

    footerTextarea.addEventListener('input', () => {
        footerElement.textContent = footerTextarea.value;
        saveEmailFooter(email, footerTextarea.value);
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

/**
 * called when "Select Users" button is clicked. calls separate handlers
 * depending on whether the Server or Overseerr email is selected.
 * @param {*} button 
 * @param {*} emailType 
 */
function clickSelectUsersButton(button, emailType) {
    // if clicking the select users button, either way, we need to clear selected_users
    clearSelectedUsers();

    if (emailType === EMAIL_TYPES.OVERSEERR) {
        // call custom handler for overseerr
        handleOverseerrSelection(button);
    }
    else if (emailType === EMAIL_TYPES.SERVER) {
        handleServerSelection(button);
    }
}

/**
 * custom handler for user selection when the Overseerr email is selected.
 * rather than being able to pick any user, you can only pick one.
 * @param {*} button 
 * @param {*} allUsers 
 * @param {*} currentlySelected 
 */
function handleOverseerrSelection(button) {
    
    selecting_users = ! selecting_users;
    button.classList.toggle("selecting", selecting_users);
    button.textContent = selecting_users ? "Cancel Selection" : "Select User";

    document.querySelectorAll(".user-container-checkbox").forEach(cb => {
        cb.classList.toggle("hidden", !selecting_users);
    });
}

/**
 * custom handler for user selection when the server email is selected.
 * you can pick multiple users, as opposed to just one with Overseerr.
 * @param {*} buton 
 */
function handleServerSelection(button) {

    selecting_users = !selecting_users;
    button.classList.toggle("selecting", selecting_users);
    button.textContent = selecting_users ? "Cancel Selection" : "Select Users";
    
    document.querySelectorAll(".user-container-checkbox").forEach(cb => {
        cb.classList.toggle("hidden", !selecting_users);
    });
    
    document.getElementById("select-users-buttons").classList.toggle("hidden", !selecting_users);

    
    
    // show warning about unsubscribed users, only if there are any.
    if (systemUpdatesUnsubscribeList.length > 0) {
        document.getElementById("user-list-desc").classList.toggle("hidden", !selecting_users);
        const unsubscribedUsers = document.querySelectorAll(".user-container.unsubscribed");
        unsubscribedUsers.forEach(container => {
            // all children with the "unsubscribed" class, add the "show" class.
            const innerUnsubscribedElements = container.querySelectorAll(".unsubscribed");
            innerUnsubscribedElements.forEach(el => {
                el.classList.toggle("show", selecting_users);
            })
        })
    }

    // show "SEND EMAIL" button
    document.getElementById("send-email-button").classList.toggle("hidden", !selecting_users);
}

/**
 * user checkbox clicked behaviour
 * @param {*} checkbox 
 */
async function clickUserCheckbox(checkbox) {

    if (selected_email === EMAIL_TYPES.SERVER) {
        // SERVER EMAIL
        const username = checkbox.textContent;
        
        if (checkbox.checked) {
            if (!selected_users.includes(getUserByUsername(username))) { selected_users.push(getUserByUsername(username)); }
        } else {
            const index = selected_users.indexOf(getUserByUsername(username));
            if (index > -1) selected_users.splice(index, 1);
        }

        updateSelectUsersButtons();
    } else {
        // OVERSEERR EMAIL
        const username = checkbox.textContent;
        if (checkbox.checked) {
            const user = getUserByUsername(username);
            if (!selected_users.includes(user)) {
                clearSelectedUsersExcept(checkbox);
                selected_users.push(user);

                // get user's requests
                const res = await fetch ('/backend/overseerr/get_user_requests', {
                    method: 'POST',
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({key: String(user["user_id"])}) 
                })
                selected_requests = await res.json();
                console.log(selected_requests);

                document.getElementById("overseerr-userInput").textContent = username;
                showRequestSelection();
            }
        } else {
            const user = getUserByUsername(username);
            const index = selected_users.indexOf(user);
            if (index > -1) selected_users.splice(index, 1);
            document.getElementById("overseerr-userInput").textContent = "";
            hideRequestSelection();
        }

    }
}

function showRequestSelection() {
    document.getElementById("overseerr-request-container").classList.remove("hidden");
}

function hideRequestSelection() {
    document.getElementById("overseerr-request-container").classList.add("hidden");
}

function clickRequestDropdown() {
    if (document.getElementById("overseerr-request-dropdown").classList.contains("hidden")) {
        showRequestDropdown();
    } else {
        hideRequestDropdown();
    }
}

function showRequestDropdown() { 
    // clear current dropdown
    document.getElementById("overseerr-request-dropdown").innerHTML = "";

    addRequests();
    document.getElementById("overseerr-request-dropdown").classList.remove("hidden");
    document.getElementById("overseerr-requestInput").classList.add("bottom-shadow");
    const el = document.getElementById("content-wrapper");
    el.scrollTop = el.scrollHeight - el.clientHeight;
}

function formatUnix(timestamp) {
    timestamp = parseInt(timestamp);
    if (timestamp.toString().length === 10) {
        timestamp *= 1000;
    }

    const date = new Date(timestamp);
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");

    return `${day}/${month} at ${hours}:${minutes}`;
}

function addRequests() {

    for (const request of selected_requests) {
        const status = request["status"];
        const status_colours = ["var(--overseerr-pending-colour)", "var(--overseerr-approved-colour)", "var(--overseerr-declined-colour)"];
        const status_summaries = ["PENDING", "APPROVED", "DECLINED"];

        // request list
        const list = document.getElementById("overseerr-request-dropdown");

        // request object
        const container = cr("div", null, "overseerr-request");
        list.appendChild(container);

        // request badge
        const badge = cr("div", null, "overseerr-request-badge");
        badge.style.background = status_colours[status-1];
        container.appendChild(badge);

        // request text container
        const text_container = cr("div", null, "overseerr-request-text");
        container.appendChild(text_container);

        // media title container
        const title_container = cr("div", null, "media-title-container");
        text_container.appendChild(title_container);
        // name
        const name = cr("p", null, "media-title-name");
        name.textContent = request["name"];
        title_container.appendChild(name);
        // year
        const year = cr("p", null, "media-title-year");
        year.textContent = `(${request["year"]})`;
        title_container.appendChild(year);

        // overseerr-request objects for each request, added to overseerr-request-dropdown
        // <div id="overseerr-request">
        //     <div id="overseerr-request-badge">
        //     </div>
        //     <div id="overseerr-request-text">
                // <div id="media-title-container">
                //     <p id="media-title-name">Movie TitleTitle</p>
                //     <p id="media-title-year">(2023)</p>
                // </div>
                // <div id="request-info-container">
                //     <p id="requested-at">MOVIE | Requested 12/02 at 09:30</p>
                // </div>
        //     </div>
        //     <div id="request-status">
        //     <p id="status-summary">DECLINED</p>
        //     <p id="status-detail">12/02 at 11:00</p>
        //     </div>
        // </div>

        // info container
        const info_container = cr("div", null, "request-info-container");
        text_container.appendChild(info_container);

        // requested-at
        const requested_at = cr("p", null, "requested-at");
        requested_at.textContent = `${request["type"]==="movie" ? "MOVIE" : `S${request["season_number"]}`} | Req: ${formatUnix(request["requested_at"])}`;
        text_container.appendChild(requested_at);

        // request-status
        const request_status = cr("div", null, "request-status");
        // summary
        const summary = cr("p", null, "status-summary");
        summary.textContent = status_summaries[status-1];
        summary.style.color = status_colours[status-1];
        request_status.appendChild(summary);
        // detail
        const detail = cr("p", null, "status-detail");
        detail.textContent = formatUnix(request["updated_at"]);
        request_status.appendChild(detail);
        container.appendChild(request_status);
    }


}

function hideRequestDropdown() {
    document.getElementById("overseerr-request-dropdown").classList.add("hidden");
    document.getElementById("overseerr-requestInput").classList.remove("bottom-shadow");
}

function updateSelectUsersButtons() {
    const checkboxes = Array.from(document.querySelectorAll(".user-container-checkbox"));
    const allSelected = Array.from(checkboxes).every(cb => cb.checked);
    const allUnselected = Array.from(checkboxes).every(cb => !cb.checked);

    document.getElementById("select-all-users-button").classList.toggle("selected", allSelected);
    document.getElementById("deselect-all-users-button").classList.toggle("unselected", allUnselected);

    const subscribedCheckboxes = checkboxes.filter(cb => {
        const userId = parseInt(cb.dataset.userId);
        return !systemUpdatesUnsubscribeList.includes(userId);
    });

    const allSubscribedSelected = subscribedCheckboxes.length > 0 && subscribedCheckboxes.every(cb => cb.checked);
    document.getElementById("select-subscribed-users-button").classList.toggle("selected", allSubscribedSelected);

    // update SEND EMAIL button (must have at least 1 user selected to send)
    const anySelected = checkboxes.some(cb => cb.checked);
    document.getElementById("send-email-button").classList.toggle("disabled", !anySelected);
}

function clearSelectedUsers() {
    // function used to deselect all users
    selected_users = [];
    document.querySelectorAll(".user-container-checkbox").forEach(cb => {
        if (cb.checked) { cb.checked = false; }
    });
    updateSelectUsersButtons();

    if (selected_email === EMAIL_TYPES.OVERSEERR) {
        document.getElementById("overseerr-userInput").textContent = "";
        hideRequestSelection();
    }
}

function clearSelectedUsersExcept(checkbox) {
    document.querySelectorAll(".user-container-checkbox").forEach(cb => {
        if (cb !== checkbox) {
            selected_users.splice(selected_users.indexOf(getUserByUsername((cb.textContent))));
            cb.checked = false;
        }
    })
}

function selectSubscribedUsers() {
    // if all subscribed users are already selected, don't register a click
    if (document.getElementById("select-subscribed-users-button").classList.contains("selected")) { return; }

    document.querySelectorAll(".user-container-checkbox").forEach(cb => {
        const userId = parseInt(cb.dataset.userId);
        const isUnsubscribed = systemUpdatesUnsubscribeList.includes(userId);

        if (!isUnsubscribed) {
            cb.checked = true;
            clickUserCheckbox(cb);
        } else {
            cb.checked = false;
            const username = cb.textContent;
            const idx = selected_users.indexOf(getUserByUsername(username));
            if (idx > -1) { selected_users.splice(idx, 1); }
        }
    });
    updateSelectUsersButtons();
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

// -------------------- send email --------------------

async function sendEmail(emailType) {

    if (emailType === EMAIL_TYPES.OVERSEERR) {
        await sendOverseerrEmail();
    }
    else if (emailType === EMAIL_TYPES.SERVER) {
        await sendServerEmail();
    }

}

async function sendOverseerrEmail() {
    // TODO: implement
}

async function sendServerEmail() {

    // get selected users' email address
    const selectedUserData = users.filter(u => selected_users.includes(getUserByUsername(u.username)));
    const recipientEmails = selectedUserData.map(u => u.email).filter(e => e && e !== "-");

    if (recipientEmails.length === 0) {
        console.log("No valid email addresses selected");
        return;
    }

    const subject = document.getElementById("server-subjectInput").value;
    if (!subject.trim()) {
        showError("You must enter a valid sender address.");
        console.log("No valid subject");
        return;
    }

    const contentHtml = document.getElementById("server-htmlInput").value;
    const footerHtml = document.getElementById("server-footerInput").value;
    const fullHtml = buildEmailHtml(contentHtml, footerHtml);

    const sender = document.getElementById("server-senderInput").value;

    if (!sender) {
        console.log("No sender");
        return;
    }

    const confirmed = await showConfirm(
        `Are you sure you want to send this email to ${recipientEmails.length} recipients?\n\n` +
        `Subject: ${subject}\n` +
        `Sender: ${sender}`
    );

    if (!confirmed) { return; }

    const progressContainer = createProgressContainer(recipientEmails.length);
    document.body.appendChild(progressContainer);

    const progressFill = progressContainer.querySelector(".email-progress-fill");
    const progressText = progressContainer.querySelector(".email-progress-text");
    const progressStatus = progressContainer.querySelector(".email-progress-status");

    const sendBtn = document.getElementById("send-email-button");
    sendBtn.classList.add("disabled");

    try {
        const result = await sendIndividualEmailsWithProgress(
            subject,
            fullHtml,
            recipientEmails,
            sender,
            createProgressHandlers(progressContainer, sendBtn)
        );
    } catch (error) {
        progressContainer.remove();
        console.log(`Failed to send emails: ${error.message}`);
    } finally {
        sendBtn.classList.remove("disabled");
    }
}

function createProgressContainer(total) {
    const progressContainer = document.createElement("div");
    progressContainer.className = "email-progress-container";
    progressContainer.innerHTML = `
        <div class="email-progress-bar">
            <div class="email-progress-fill" style="width: 0%"></div>
        </div>
        <p class="email-progress-text">Sending 0 of ${total}...</p>
        <p class="email-progress-status"></p>
    `;
    return progressContainer;
}

function createProgressHandlers(container, sendBtn) {
    const progressFill = container.querySelector(".email-progress-fill");
    const progressText = container.querySelector(".email-progress-text");
    const progressStatus = container.querySelector(".email-progress-status");

    return {
        onStart: (data) => {
            console.log(`Starting to send ${data.total} emails.`);
        },
        onProgress: (data) => {
            const percent = (data.current / data.total) * 100;
            progressFill.style.width = `${percent}%`;
            progressText.textContent = `Sending ${data.current} of ${data.total}...`;
            progressStatus.textContent = data.status === "success" ? `✓ ${data.recipient}` : `X ${data.recipient} (failed)`;
            progressStatus.className = data.status === "success" ? "email-progress-status success" : "email-progress-status error";
        },
        onComplete: (data) => {
            progressFill.style.width = "100%";
            progressText.textContent = `Complete! ${data.successful} sent, ${data.failed} failed`;
            setTimeout(() => {
                container.remove();
                if (data.failed === 0) {
                    console.log(`Email sent successfully to ${data.successful} recipient(s)`);
                    deselectAllUsers();
                } else if (data.successful > 0) {
                    console.log(`Partial success: ${data.successful} sent, ${data.failed} failed.`);
                } else {
                    console.log(`All emails failed to send.`);
                }
            }, 1000);
        },
        onError: (message) => {
            container.remove();
            console.log(`Failed: ${message}`);
            sendBtn.classList.remove("disabled");
        }
    }
}


// -------------------- init --------------------

window.onload = async function() {
    try {
        await fetchUnsubscribeLists();

        const res = await fetch("/backend/tautulli/get_users");

        if (res.status !== 200) { throw new Error("Tautulli connection failed"); }

        users = await res.json();
        displayUsers(users);
        displayEmail(selected_email);
    } catch (error) {
        console.error("Dashboard initialisation error: ", error);
        displayTautulliError();
    }

    await this.fetch("/backend/tmdb/get_show_tmdb_id", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            key: "Designated Survivor"
        })
    });

    // add event listener to send email button
    document.getElementById("send-email-button").addEventListener("click", () => sendEmail(selected_email));

    // add event listener to server and overseerr email buttons
    document.getElementById("server-selector").addEventListener("click", () => selectEmailType(EMAIL_TYPES.SERVER));
    document.getElementById("overseerr-selector").addEventListener("click", () => selectEmailType(EMAIL_TYPES.OVERSEERR));

    // add event listener to overseerr Select Request button
    document.getElementById("overseerr-select-requests-button").addEventListener("click", () => clickRequestDropdown());
};
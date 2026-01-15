
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

const modal_window = document.getElementById("modal-window");
const senderDescText = "Address from which the email will be sent";
const recipientDescText = "Recipient addresses (separated by commas)";

function cr(type, clss, id) {
    const elem = document.createElement(type);
    if (clss) { elem.classList.add(clss); }
    if (id) { elem.id = id; }
    return elem;
}

function buildTestEmailModal() {
    // <div class="modal-container" id="test-email-modal">
    //   <div class="modal-title" id="test-email-modal-title">
    //     <h2>Send Test Email</h2>
    //   </div>
    //   <div class="modal-content" id="test-email-modal-content">
    //     <p>You are about to send a test email. Please enter the sender and recipient email addresses:</p>
    //     <div class="modal-inputs-container" id="test-email-modal-inputs-container">
    //       <div class="modal-input-grid" id="test-email-modal-input-grid">
    //         <p class="modal-input-text">Sender email address:</p>
    //         <input class="modal-input" id="test-email-sender-modal-input"/>
    //         <p class="modal-description">Address from which the email will be sent</p>
    //         <p class="modal-input-text">Recipient email address:</p>
    //         <input class="modal-input" id="test-email-recipient-modal-input"/>
    //         <p class="modal-description">Recipient addresses (separated by commas)</p>
    //       </div>
    //     </div>
    //     <div class="modal-buttons" id="test-email-modal-buttons">
    //       <div class="modal-confirm-button" id="test-email-modal-send-button">Send</div>
    //       <div class="modal-cancel-button" id="test-email-modal-cancel-button">Cancel</div>
    //     </div>
    //   </div>
    // </div>
    // div modal-container
    const container = cr("div", "modal-container", "test-email-modal");
    // div modal-title
    const title = cr("div", "modal-title", "test-email-modal-title");
    container.appendChild(title);
    // h2
    const h2 = cr("h2", null, null);
    h2.innerHTML = "Send Test Email";
    title.appendChild(h2);
    // modal-content
    const content = cr("div", "modal-content", "test-email-modal-content");
    container.appendChild(content);
    // p
    const p = cr("p", null, null);
    p.textContent = "You are away to send a test email. Please enter the sender and recipient email addresses:"
    content.appendChild(p);
    // modal-inputs-container
    const inputsContainer = cr("div", "modal-inputs-container", "test-email-modal-inputs-container");
    content.appendChild(inputsContainer);
    // modal-input-grid
    const inputGrid = cr("div", "modal-input-grid", "test-email-modal-input-grid");
    inputsContainer.appendChild(inputGrid);
    // modal-input-text
    const p2 = cr("p", "modal-input-text", null);
    p2.textContent = "Sender email address:"
    inputGrid.appendChild(p2);
    //modal-input
    const input1 = cr("input", "modal-input", "test-email-sender-modal-input");
    input1.addEventListener('input', hideSenderDescriptionError);
    inputGrid.appendChild(input1)
    // modal-description
    const desc1 = cr("p", "modal-description", "test-email-sender-desc");
    desc1.textContent = senderDescText;
    inputGrid.appendChild(desc1);
    //         <p class="modal-input-text">Recipient email address:</p>
    const p3 = cr("p", "modal-input-text", null);
    p3.textContent = "Recipient email address:";
    inputGrid.appendChild(p3);
    //         <input class="modal-input" id="test-email-recipient-modal-input"/>
    const input2 = cr("input", "modal-input", "test-email-recipient-modal-input");
    input2.addEventListener('input', hideRecipientDescriptionError);
    inputGrid.appendChild(input2);
    //         <p class="modal-description">Recipient addresses (separated by commas)</p>
    const p4 = cr("p", "modal-description", "test-email-recipient-desc");
    p4.textContent = recipientDescText;
    inputGrid.appendChild(p4);

    //     <div class="modal-buttons" id="test-email-modal-buttons">
    const buttons = cr("div", "modal-buttons", "test-email-modal-buttons");
    content.appendChild(buttons);
    //       <div class="modal-confirm-button" id="test-email-modal-send-button">Send</div>
    const confirm = cr("div", "modal-confirm-button", "test-email-modal-send-button");
    confirm.innerHTML = "Send";
    confirm.addEventListener("click", sendTestEmail);
    buttons.appendChild(confirm);
    //       <div class="modal-cancel-button" id="test-email-modal-cancel-button">Cancel</div>
    const cancel = cr("div", "modal-cancel-button", "test-email-modal-cancel-button");
    cancel.innerHTML = "Cancel";
    cancel.addEventListener("click", closeTestEmail);
    buttons.appendChild(cancel);

    return container;
}

function showSenderDescriptionError() {
    const descEl = document.getElementById("test-email-sender-desc");
    descEl.classList.add("error");
    descEl.textContent = "Please enter a valid sender address.";
}
function hideSenderDescriptionError() {
    const descEl = document.getElementById("test-email-sender-desc");
    if (descEl.classList.contains("error")) { descEl.classList.remove("error"); }
    descEl.textContent = senderDescText;
}
function showRecipientDescriptionError() {
    const descEl = document.getElementById("test-email-recipient-desc");
    descEl.classList.add("error");
    descEl.textContent = "Please enter valid recipient address(es).";
}
function hideRecipientDescriptionError() {
    const descEl = document.getElementById("test-email-recipient-desc");
    if (descEl.classList.contains("error")) { descEl.classList.remove("error"); }
    descEl.textContent = recipientDescText;
}

async function sendTestEmail() {
    const send = document.getElementById("test-email-modal-send-button");
    if (!send.classList.contains("loading")) {
        const senderEl = document.getElementById("test-email-sender-modal-input");
        const sender = senderEl.value;
        const recipientEl = document.getElementById("test-email-recipient-modal-input");
        const recipient = recipientEl.value;
    
        const width = send.getBoundingClientRect().width;
        send.style.width = `${width}px`;
        const saveContent = send.innerHTML;
        send.innerHTML = "";
        send.classList.add("loading");
        res = await fetch("/backend/smtp/send_test_email", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "sender": sender,
                "recipient": recipient
            })
        });
        data = await res.json();
        send.classList.remove("loading");
        send.innerHTML = saveContent;
        if (data.status === 200) {
            // successful
            console.log("STATUS 200");
            closeTestEmail();
            showSuccess("Test email(s) successfully sent!");
        } else if (data.status === 400) {
            // sender and/or recipient emails were invalid
            console.log("STATUS 400");
            if (data.issue == "sender") {
                showSenderDescriptionError();
            } else if (data.issue == "recipient") {
                showRecipientDescriptionError();
            }
        } else if (data.status === 500) {
            // one or more email couldn't be sent
            console.log("STATUS 500"); 
            showError("Error occurred while sending test email. Are your SMTP credentials correct?");
        }
    }
}

function closeTestEmail() {
    modal_window.innerHTML = "";
    modal_window.classList.add("hidden");
}

function showTestEmailModal() {
    const html = buildTestEmailModal();
    modal_window.classList.remove("hidden");
    modal_window.appendChild(html);
}   
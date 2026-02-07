
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

let confirmResolve = null;

function showConfirm(message, { confirmText = "Confirm", cancelText = "Cancel" } = {}) {
    return new Promise((resolve) => {

        confirmResolve = resolve;

        const container = document.getElementById("notification-container");

        const modalWindow = document.getElementById("modal-window");
        modalWindow.classList.remove("hidden");

        const modal = document.createElement("div");
        modal.className = "confirm-modal";
        modal.id = "active-confirm-modal";

        const text = document.createElement("p");
        text.textContent = message;
        text.className = "confirm-modal-text";

        const buttons = document.createElement("div");
        buttons.className = "confirm-modal-buttons";

        const confirmBtn = document.createElement("button");
        confirmBtn.textContent = confirmText;
        confirmBtn.className = "confirm-modal-btn confirm";
        confirmBtn.onclick = () => closeConfirm(true);

        const cancelBtn = document.createElement("button");
        cancelBtn.textContent = cancelText;
        cancelBtn.className = "confirm-modal-btn cancel";
        cancelBtn.onclick = () => closeConfirm(false);

        buttons.append(cancelBtn, confirmBtn);
        modal.append(text, buttons);
        container.appendChild(modal);

        // Animate in
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                modal.classList.add("show");
            });
        });

    });
}

function closeConfirm(result) {
  const modal = document.getElementById("active-confirm-modal");
  if (!modal) return;

  const modalWindow = document.getElementById("modal-window");
    modalWindow.classList.add("hidden");
  
  modal.classList.remove("show");
  modal.classList.add("hide");
  
  setTimeout(() => {
    modal.remove();
    if (confirmResolve) {
      confirmResolve(result);
      confirmResolve = null;
    }
  }, 300);
}

// close if Escape key pressed
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeConfirm(false);
  }
});
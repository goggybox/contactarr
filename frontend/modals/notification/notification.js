
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

function showNotification(message, {type = "", timeout = 2500} = {}) {
  const container = document.getElementById("notification-container");

  const notification = document.createElement("div");
  notification.className = `notification-modal ${type} hide`.trim();

  const text = document.createElement("span");
  text.textContent = message;
  text.className = "notification-modal-text";

  const close = document.createElement("span");
  close.className = "notification-modal-close";
  close.textContent = "×";
  close.onclick = () => hideNotification(notification);

  notification.append(text, close);
  container.appendChild(notification);

  // ensure transition runs
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      notification.classList.remove("hide");
    });
  });

  setTimeout(() => {
    hideNotification(notification);
  }, timeout);
}

function showError(message, timeout = 5000) {
  showNotification(message, { type: "error", timeout });
}

function showSuccess(message, timeout = 5000) {
  showNotification(message, { type: "success", timeout });
}

function hideNotification(notification) {
    notification.classList.add("hide");
}
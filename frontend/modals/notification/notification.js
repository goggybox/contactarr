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
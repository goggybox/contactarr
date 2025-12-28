let tautulli_url;

async function initTautulliURLInputBox() {
    // tautulli api key
    const inp = document.getElementById("tautulli-connection2-input-box");
    let res = await fetch("/backend/tautulli/url");
    tautulli_url = await res.text();
    inp.value = tautulli_url;
    inp.addEventListener('input', tautulliAPIURLListener);
}

async function tautulliConnection2Save() {
    const inp = document.getElementById("tautulli-connection2-input-box");
    const val = inp.value;
    const res = await fetch("/backend/tautulli/set_url", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({key: val})
    });
    const success = await res.json();
    if (success) {
        tautulli_url = val;
        hideSaveAndCancelButtons2();
        showNotification("Tautulli API URL Saved");
    }
}

function tautulliConnection2Cancel() {
    const inp = document.getElementById("tautulli-connection2-input-box");
    inp.value = tautulli_url;
    hideSaveAndCancelButtons2();
}

function hideSaveAndCancelButtons2() {
    const btns = document.getElementById("tautulli-connection2-buttons");
    btns.classList.add("hide");
}

function showSaveAndCancelButtons2() {
    const btns = document.getElementById("tautulli-connection2-buttons");
    btns.classList.remove("hide");
}

function tautulliAPIURLListener() {
    // event listener for TautulliAPIKey input box.
    const inp = document.getElementById("tautulli-connection2-input-box");

    if (inp.value.trim() === tautulli_url) {
        // matches currently saved key value - hide Save/Cancel buttons
        hideSaveAndCancelButtons2();
    } else {
        // does not match currently saved key value - show Save/Cancel buttons
        showSaveAndCancelButtons2();
    }
}
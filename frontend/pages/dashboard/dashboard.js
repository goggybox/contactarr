let users;

function displayUsers() {
    
}

window.onload = async function() {
    // load aray of Tautulli users when dashboard loads
    res = await fetch ("/backend/tautulli/get_users");
    users = await res.json();
    displayUsers();
}
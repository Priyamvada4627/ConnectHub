const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "index.html";
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "index.html";
}

const logoutBtn = document.getElementById("logoutBtn");

if (logoutBtn) {
    logoutBtn.addEventListener("click", logout);
}
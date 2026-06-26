const searchInput = document.getElementById("searchInput");
const searchResults = document.getElementById("searchResults");

let debounceTimer;

searchInput.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(doSearch, 300);
});

async function doSearch() {
    const q = searchInput.value.trim();

    if (!q) {
        searchResults.innerHTML = "";
        return;
    }

    try {
        const users = await apiRequest(`/users/search/?q=${encodeURIComponent(q)}`);

        searchResults.innerHTML = "";

        if (users.length === 0) {
            searchResults.innerHTML = "<p>No users found.</p>";
            return;
        }

        users.forEach(user => {
            const div = document.createElement("div");
            div.className = "notification"; // reuse existing card style
            div.style.cursor = "pointer";
            div.innerHTML = `
                <img
                    src="${sanitize(user.avatar_url || 'https://placehold.co/50')}"
                    style="width:50px;height:50px;border-radius:50%;object-fit:cover;">
                <div>
                    <strong>${sanitize(user.full_name ?? user.username)}</strong>
                    <br>
                    <small>@${sanitize(user.username)}</small>
                </div>
            `;
            div.addEventListener("click", () => {
                window.location.href = `profile.html?user=${user.username}`;
            });
            searchResults.appendChild(div);
        });

    } catch (err) {
        console.error(err);
    }
}
const form = document.getElementById("loginForm");

form.addEventListener("submit", async (e) => {

    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    try {

        const response = await apiRequest(
            "/login",
            "POST",
            formData
        );

        localStorage.setItem(
            "token",
            response.access_token
        );

        window.location.href = "feed.html";

    } catch (err) {

        alert(err.message);

    }

});
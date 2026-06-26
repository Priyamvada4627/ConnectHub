const form = document.getElementById("registerForm");

form.addEventListener("submit", async (e) => {

    e.preventDefault();

    try {

        await apiRequest(
            "/users/",
            "POST",
            {
                username: document.getElementById("username").value,
                full_name: document.getElementById("full_name").value,
                email: document.getElementById("email").value,
                password: document.getElementById("password").value,
            }
        );

        alert("Registration successful!");

        window.location.href = "index.html";

    } catch (err) {

        alert(err.message);

    }

});
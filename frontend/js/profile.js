const avatar = document.getElementById("avatar");
const fullName = document.getElementById("fullName");
const username = document.getElementById("username");
const bio = document.getElementById("bio");

const followers = document.getElementById("followers");
const following = document.getElementById("following");
const postsCount = document.getElementById("postsCount");

const postsDiv = document.getElementById("posts");

const editBtn = document.getElementById("editBtn");
const saveBtn = document.getElementById("saveBtn");

const editSection = document.getElementById("editSection");

const editName = document.getElementById("editName");
const editBio = document.getElementById("editBio");
const editAvatar = document.getElementById("editAvatar");

let profile = null;

// =======================================
// PAGE LOAD
// =======================================

window.onload = async () => {

    await loadProfile();

};

function getProfileUsername() {

    const params = new URLSearchParams(window.location.search);

    return params.get("user");

}

// =======================================
// LOAD PROFILE
// =======================================

async function loadProfile() {

    try {

        const usernameParam = getProfileUsername();

        if (usernameParam) {

            profile = await apiRequest(
                `/profile/${usernameParam}`
            );

        } else {

            profile = await apiRequest(
                "/profile/me"
            );

        }

        avatar.src =
            profile.avatar_url ||
            "https://placehold.co/150";

        fullName.textContent =
            profile.full_name ?? profile.username;

        username.textContent =
            "@" + profile.username;

        bio.textContent =
            profile.bio || "No bio yet.";

        followers.textContent = profile.followers;

        following.textContent = profile.following;

        postsCount.textContent = profile.posts_count;

        editName.value =
            profile.full_name || "";

        editBio.value =
            profile.bio || "";

        const followBtn = document.getElementById("followBtn");

        if (usernameParam) {

            editBtn.style.display = "none";

            followBtn.style.display = "inline-block";
            followBtn.textContent = profile.is_following ? "Unfollow" : "Follow";
            followBtn.onclick = () => toggleFollow(profile.id, profile.is_following);

        } else {

            editBtn.style.display = "inline-block";
            followBtn.style.display = "none";

        }

        await loadPosts();

    }

    catch(err){

        console.error(err);

    }

}

// =======================================
// FOLLOW / UNFOLLOW
// =======================================

async function toggleFollow(userId, isFollowing) {

    try {

        if (isFollowing) {

            await apiRequest(`/follow/${userId}`, "DELETE");

        } else {

            await apiRequest("/follow/", "POST", { following_id: userId });

        }

        await loadProfile();

    } catch (err) {

        alert(err.message);

    }

}

// =======================================
// FOLLOWERS / FOLLOWING MODAL
// =======================================

async function loadUsers(type) {

    try {

        const users = await apiRequest(
            `/profile/${profile.username}/${type}`
        );

        document.getElementById("modalTitle").textContent =
            type.charAt(0).toUpperCase() + type.slice(1);

        const list = document.getElementById("userList");
        list.innerHTML = "";

        users.forEach(user => {
            list.innerHTML += `
                <div class="user-card"
                     onclick="openProfile('${sanitize(user.username)}')">

                    <img
                        src="${user.avatar_url || "https://placehold.co/60"}"
                        class="user-avatar">

                    <div class="user-info">
                        <strong>${sanitize(user.full_name ?? user.username)}</strong>
                        <br>
                        <small>@${sanitize(user.username)}</small>
                    </div>

                    <button
                        class="message-btn"
                        onclick="event.stopPropagation(); messageUser(${user.id})">
                        Message
                    </button>

                </div>
            `;
        });

        document
            .getElementById("userModal")
            .classList.remove("hidden");

    } catch (err) {

        console.error(err);

    }

}

document
    .getElementById("followersCard")
    .onclick = () => loadUsers("followers");

document
    .getElementById("followingCard")
    .onclick = () => loadUsers("following");

// =======================================
// LOAD POSTS
// =======================================

async function loadPosts() {

    try {

        const posts = await apiRequest(
            `/profile/${profile.username}/posts`
        );

        postsDiv.innerHTML = "";

        if (posts.length === 0) {

            postsDiv.innerHTML = `
                <h3>No Posts Yet</h3>
            `;

            return;

        }

        posts.forEach(item => {

            const post = item.post;

            const card = document.createElement("div");

            card.className = "post";

            card.innerHTML = `

                <h3>${sanitize(post.title)}</h3>

                <p>${sanitize(post.content)}</p>

                ${
                    post.image_url
                        ? `<img src="${sanitize(post.image_url)}">`
                        : ""
                }

                <div class="post-footer">

                    <span>
                        💬 ${item.comments ?? 0}
                    </span>

                    <span>
                        ${new Date(post.created_at).toLocaleDateString()}
                    </span>

                </div>

                ${
                    !getProfileUsername()
                    ? `
                        <div class="post-actions">

                            <button onclick="editPost(${post.id})">
                                Edit
                            </button>

                            <button onclick="deletePost(${post.id})">
                                Delete
                            </button>

                        </div>
                    `
                    : ""
                }

            `;

            postsDiv.appendChild(card);

        });

    }

    catch (err) {

        console.error(err);

        alert(err.message);

    }

}

// =======================================
// EDIT PROFILE
// =======================================

editBtn.addEventListener("click", () => {

    editSection.classList.toggle("hidden");

});

// =======================================
// SAVE PROFILE
// =======================================

saveBtn.addEventListener("click", saveProfile);

async function saveProfile() {

    const formData = new FormData();

    formData.append("full_name", editName.value);

    formData.append("bio", editBio.value);

    if (editAvatar.files.length > 0) {

        formData.append("avatar", editAvatar.files[0]);

    }

    try {

        await apiRequest("/profile/me", "PUT", formData);

        editSection.classList.add("hidden");

        await loadProfile();

        alert("Profile updated successfully.");

    }

    catch (err) {

        alert(err.message);

    }

}

// =======================================
// EDIT POST
// =======================================

async function editPost(postId) {

    try {

        const posts = await apiRequest(
            `/profile/${profile.username}/posts`
        );

        const item = posts.find(p => p.post.id === postId);

        if (!item) return;

        const title = prompt("Title", item.post.title);

        if (title === null) return;

        const content = prompt("Content", item.post.content);

        if (content === null) return;

        await apiRequest(
            `/posts/${postId}`,
            "PUT",
            { title, content, published: true }
        );

        await loadProfile();

    } catch (err) {

        alert(err.message);

    }

}

// =======================================
// DELETE POST
// =======================================

async function deletePost(postId) {

    if (!confirm("Delete this post?")) return;

    try {

        await apiRequest(`/posts/${postId}`, "DELETE");

        await loadProfile();

    } catch (err) {

        alert(err.message);

    }

}

// =======================================
// HELPERS
// =======================================

function messageUser(userId) {

    localStorage.setItem("chatUser", userId);

    window.location.href = "chat.html";

}

function openProfile(username) {

    window.location.href = `profile.html?user=${username}`;

}

document
    .getElementById("closeModal")
    .addEventListener("click", () => {

        document
            .getElementById("userModal")
            .classList.add("hidden");

    });

window.addEventListener("click", (event) => {

    const modal = document.getElementById("userModal");

    if (event.target === modal) {

        modal.classList.add("hidden");

    }

});
const currentUserDiv = document.getElementById("currentUser");
const postsDiv = document.getElementById("posts");
const postBtn = document.getElementById("postBtn");

window.onload = () => {
    loadCurrentUser();
    loadFeed();
};

// =======================================
// CURRENT USER
// =======================================

async function loadCurrentUser() {

    try {

        const user = await apiRequest("/profile/me");

        currentUserDiv.innerHTML = `
            <img
                src="${user.avatar_url || 'https://placehold.co/100x100'}"
                class="avatar">

            <h2>${sanitize(user.full_name ?? user.username)}</h2>

            <p>@${sanitize(user.username)}</p>

            <p>${sanitize(user.bio ?? "")}</p>

            <hr>

            <p><strong>Followers:</strong> ${user.followers}</p>

            <p><strong>Following:</strong> ${user.following}</p>

            <p><strong>Posts:</strong> ${user.posts_count}</p>
        `;

    }

    catch (err) {

        alert(err.message);

    }

}

async function loadFeed() {

    try {

        const feed = await apiRequest("/feed");

        postsDiv.innerHTML = "";

        feed.forEach(item => {

            const post = item.post;

            const card = document.createElement("div");

            card.className = "post";

            card.innerHTML = `
                <div class="post-header">
                    <h3>${sanitize(post.owner.full_name ?? post.owner.username)}</h3>
                    <small>@${sanitize(post.owner.username)}</small>
                </div>

                <h2 class="post-title">${sanitize(post.title)}</h2>

                <p>${sanitize(post.content)}</p>

                ${
                    post.image_url
                        ? `<img src="${sanitize(post.image_url)}" class="post-image">`
                        : ""
                }

                <hr>

                <div class="post-actions">

                    <button onclick="toggleLike(${post.id}, ${item.is_liked})">
                        ${item.is_liked ? "❤️" : "🤍"} ${item.likes}
                    </button>

                    <button onclick="toggleComments(${post.id})">
                        💬 ${item.comments}
                    </button>

                    ${
                        item.is_owner
                            ? `
                                <button onclick="editPost(${post.id})">
                                    Edit
                                </button>

                                <button onclick="deletePost(${post.id})">
                                    Delete
                                </button>
                            `
                            : ""
                    }

                </div>

                <div
                    id="comments-${post.id}"
                    class="comments-container"
                    style="display:none;">

                    <div id="comments-list-${post.id}"></div>

                    <div class="comment-input">

                        <input
                            type="text"
                            id="comment-input-${post.id}"
                            placeholder="Write a comment...">

                        <button
                            onclick="addComment(${post.id})">
                            Send
                        </button>

                    </div>

                </div>
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
// LIKE
// =======================================

async function toggleLike(postId, liked) {

    try {

        await apiRequest(
            "/votes",
            "POST",
            {
                post_id: postId,
                dir: liked ? 0 : 1
            }
        );

        loadFeed();

    }

    catch (err) {

        alert(err.message);

    }

}

// =======================================
// COMMENTS
// =======================================

async function toggleComments(postId) {

    const container = document.getElementById(
        `comments-${postId}`
    );

    if (container.style.display === "none") {

        container.style.display = "block";

        await loadComments(postId);

    }

    else {

        container.style.display = "none";

    }

}
async function loadComments(postId) {

    try {

        const comments = await apiRequest(
            `/posts/${postId}/comments`
        );

        const list = document.getElementById(
            `comments-list-${postId}`
        );

        list.innerHTML = "";

        if (comments.length === 0) {

            list.innerHTML = `
                <p>No comments yet.</p>
            `;

            return;
        }

        comments.forEach(comment => {

            list.innerHTML += `

                <div class="comment">

                    <div class="comment-header">

                        <strong>

                            ${sanitize(comment.user.full_name ?? comment.user.username)}

                        </strong>

                        <small>

                            ${new Date(comment.created_at).toLocaleString()}

                        </small>

                    </div>

                    <p>

                        ${sanitize(comment.content)}

                    </p>

                </div>

            `;

        });

    }

    catch(err){

        alert(err.message);

    }

}

async function addComment(postId){

    const input = document.getElementById(
        `comment-input-${postId}`
    );

    const content = input.value.trim();

    if(!content){
        return;
    }

    try{

        await apiRequest(
            `/posts/${postId}/comments`,
            "POST",
            {
                content: content
            }
        );

        input.value = "";

        await loadComments(postId);

        loadFeed();

    }

    catch(err){

        alert(err.message);

    }

}

// =======================================
// CREATE POST
// =======================================

postBtn.addEventListener("click", createPost);

async function createPost() {

    const title = document.getElementById("title").value.trim();

    const content = document.getElementById("content").value.trim();

    const image = document.getElementById("image").files[0];

    if (!title || !content) {

        alert("Title and content are required.");

        return;

    }

    const formData = new FormData();

    formData.append("title", title);

    formData.append("content", content);

    formData.append("published", true);

    if (image) {

        formData.append("image", image);

    }

    try {

        await apiRequest(
            "/posts/",
            "POST",
            formData
        );

        document.getElementById("title").value = "";

        document.getElementById("content").value = "";

        document.getElementById("image").value = "";

        loadFeed();

    }

    catch (err) {

        alert(err.message);

    }

}


// =======================================
// EDIT
// =======================================

async function editPost(postId) {

    try {

        const feed = await apiRequest("/feed");

        const item = feed.find(p => p.post.id === postId);

        if (!item)
            return;

        const title = prompt("Title", item.post.title);

        if (title === null)
            return;

        const content = prompt("Content", item.post.content);

        if (content === null)
            return;

        await apiRequest(
            `/posts/${postId}`,
            "PUT",
            {
                title,
                content,
                published: true
            }
        );

        loadFeed();

    } catch (err) {

        alert(err.message);

    }

}

// =======================================
// DELETE
// =======================================

async function deletePost(postId) {

    if (!confirm("Delete this post?"))
        return;

    try {

        await apiRequest(
            `/posts/${postId}`,
            "DELETE"
        );

        loadFeed();

    } catch (err) {

        alert(err.message);

    }

}
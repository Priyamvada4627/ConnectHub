const notificationList =
    document.getElementById("notificationList");

// =====================================
// PAGE LOAD
// =====================================

window.addEventListener("DOMContentLoaded", async () => {

    await loadNotifications();

    await loadCount();

    const readAllBtn =
        document.getElementById("readAllBtn");

    readAllBtn.addEventListener(
        "click",
        markAllRead
    );

});

// =====================================
// LOAD NOTIFICATIONS
// =====================================

async function loadNotifications() {

    try {

        const notifications =
            await apiRequest("/notifications");

        notificationList.innerHTML = "";

        if (notifications.length === 0) {

            notificationList.innerHTML = `
                <h3>No Notifications</h3>
            `;

            return;

        }

        notifications.forEach(renderNotification);

    }

    catch (err) {

        console.error(err);

        alert(err.message);

    }

}

// =====================================
// RENDER
// =====================================

function renderNotification(notification) {

    const div = document.createElement("div");

    div.className =
        notification.is_read
            ? "notification"
            : "notification unread";

    div.innerHTML = `

        <div>

            <div class="actor">

                ${notification.actor.full_name ??
                notification.actor.username}

            </div>

            <div>

                ${getText(notification)}

            </div>

            <div class="time">

                ${new Date(
                    notification.created_at
                ).toLocaleString()}

            </div>

        </div>

        <button
            class="delete-btn">

            Delete

        </button>

    `;

    // Delete button
    div.querySelector(".delete-btn")
        .addEventListener("click", async (e) => {

            e.stopPropagation();

            await deleteNotification(notification.id);

        });

    // Open notification
    div.addEventListener("click", () => {

        openNotification(notification);

    });

    notificationList.appendChild(div);

}

// =====================================
// TEXT
// =====================================
function getText(notification) {
    switch (notification.type) {
        case "FOLLOW":
            return "started following you.";

        case "MESSAGE":
            return "sent you a message.";

        case "LIKE":
            return "liked your post.";

        case "COMMENT":
            return "commented on your post.";

        default:
            return "interacted with you.";
    }
}

// =====================================
// OPEN NOTIFICATION
// =====================================

async function openNotification(notification) {

    try {

        if (!notification.is_read) {

            await apiRequest(
                `/notifications/${notification.id}/read`,
                "PATCH"
            );

        }

        await loadCount();

        switch (notification.type) {

            case "FOLLOW":

                window.location.href =
                    `profile.html?user=${notification.actor.username}`;

                break;

            case "MESSAGE":

                localStorage.setItem(
                    "chatUser",
                    notification.actor.id
                );

                window.location.href = "chat.html";

                break;

            default:

                window.location.href = "feed.html";

        }

    }

    catch (err) {

        console.error(err);
        return

    }

}

// =====================================
// MARK ALL READ
// =====================================
async function markAllRead() {

    console.log("Mark all clicked");

    try {

        const res = await apiRequest(
            "/notifications/read-all",
            "PATCH"
        );

        console.log(res);

        await loadNotifications();

        await loadCount();

    } catch (err) {

        console.error(err);
        return

    }

}

// =====================================
// DELETE
// =====================================

async function deleteNotification(id) {

    try {

        await apiRequest(
            `/notifications/${id}`,
            "DELETE"
        );

        await loadNotifications();

        await loadCount();

    }

    catch (err) {

        console.error(err);

        alert(err.message);

    }

}

// =====================================
// BADGE
// =====================================

async function loadCount() {

    try {

        const badge =
            document.getElementById("notificationCount");

        if (!badge) return;

        const data = await apiRequest(
            "/notifications/unread-count"
        );

        if (data.count > 0) {

            badge.textContent = data.count;

            badge.style.display = "inline-block";

        } else {

            badge.textContent = "";

            badge.style.display = "none";

        }

    }

    catch (err) {

        console.error(err);
        return

    }

}
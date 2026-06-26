const conversationList = document.getElementById("conversationList");
const chatHeader = document.getElementById("chatHeader");
const messages = document.getElementById("messages");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const typingIndicator = document.getElementById("typingIndicator");

let currentUser = null;
let selectedUser = null;
let socket = null;

// =====================================
// START
// =====================================

window.addEventListener("DOMContentLoaded", async () => {

    try {

        currentUser = await apiRequest("/profile/me");

        connectSocket();

        await loadInbox();
        const chatUser = localStorage.getItem("chatUser");

        if (chatUser) {
            const inbox = await apiRequest("/messages/");

            const user = inbox.find(c => c.user.id == chatUser);
            if (user) {
                openConversation(user.user);
            } else {
    // First time messaging — fetch user directly and open
            const freshUser = await apiRequest(`/users/${chatUser}`);
            if (freshUser) openConversation(freshUser);}

        }

    } catch (err) {

        console.error(err);
        alert(err.message);

    }

});

// =====================================
// WEBSOCKET
// =====================================

function connectSocket() {

    const token = localStorage.getItem("token");

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
        ? '127.0.0.1:8000'
        : 'your-api.onrender.com'; // TODO: replace with your deployed API host

    socket = new WebSocket(
        `${wsProtocol}//${wsHost}/ws/${currentUser.id}?token=${token}`
    );

    socket.onopen = () => {

        console.log("✅ WebSocket Connected");

    };

    socket.onclose = (event) => {

        console.log("❌ WebSocket Closed");
        console.log(event);

    };

    socket.onerror = (event) => {

        console.log("WebSocket Error", event);

    };

    socket.onmessage = (event) => {

        const data = JSON.parse(event.data);

        console.log("Socket:", data);

        handleSocketMessage(data);

    };

}

// =====================================
// LOAD INBOX
// =====================================

async function loadInbox() {

    const inbox = await apiRequest("/messages/");

    conversationList.innerHTML = "";

    if (inbox.length === 0) {

        conversationList.innerHTML =
            "<p>No conversations</p>";

        return;

    }

    inbox.forEach(chat => {

        const div = document.createElement("div");

        div.className = "conversation";

        div.innerHTML = `

            <strong>

                ${sanitize(chat.user.full_name ?? chat.user.username)}

            </strong>

            <br>

            <small>

                ${sanitize(chat.last_message)}

            </small>

        `;

        div.onclick = () => {

            openConversation(chat.user);

        };

        conversationList.appendChild(div);

    });

}

// =====================================
// OPEN CHAT
// =====================================
async function openConversation(user) {

    selectedUser = user;

    chatHeader.innerHTML = `
        <h3>${sanitize(user.full_name ?? user.username)}</h3>
        <small id="presenceText">Checking...</small>
    `;

    messages.innerHTML = "";
    typingIndicator.innerHTML = "";

    try {

        // Load conversation
        const conversation = await apiRequest(
            `/messages/${user.id}`
        );

        messages.innerHTML = "";

        conversation.forEach(message => {
            renderMessage(message);
        });

        scrollBottom();

        // Check online status
        const onlineResponse = await apiRequest("/online-users");

        const presenceText = document.getElementById("presenceText");

        if (onlineResponse.online_users.includes(user.id)) {
            presenceText.textContent = "🟢 Online";
        } else {
            presenceText.textContent = "⚪ Offline";
        }

    } catch (err) {

        console.error(err);
        alert(err.message);

    }

}

// =====================================
// RENDER MESSAGE
// =====================================
function renderMessage(message) {

    const bubble = document.createElement("div");
    

    bubble.id = `message-${message.id}`;

    const isMine = message.sender_id === currentUser.id;
    
    bubble.className = isMine
        ? "message sent"
        : "message received";

    let html = "";

    // ============================
    // Text
    // ============================

    if (message.content) {

        html += `
            <p class="message-text">
                ${sanitize(message.content)}
            </p>
        `;

    }

    // ============================
    // Image
    // ============================

    if (message.image_url) {

        html += `
            <img
                src="${sanitize(message.image_url)}"
                class="chat-image"
                onclick="window.open('${sanitize(message.image_url)}')"
            >
        `;

    }

    // ============================
    // Audio
    // ============================

    if (message.audio_url) {

        html += `
            <audio controls class="chat-audio">
                <source
                    src="${sanitize(message.audio_url)}">
            </audio>
        `;

    }

    // ============================
    // Footer
    // ============================

    const time = new Date(
        message.created_at
    ).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });

    html += `
        <div class="message-footer">

            <small>

                ${time}

            </small>

            ${
                isMine
                ?
                `<span class="seen-status" id="seen-${message.id}">

                    ${message.is_seen ? "✓✓" : "✓"}

                </span>`
                :
                ""
            }

        </div>
    `;

    bubble.innerHTML = html;

    messages.appendChild(bubble);

}

// =====================================
// SCROLL
// =====================================

function scrollBottom() {

    messages.scrollTop =
        messages.scrollHeight;

}

// =====================================
// SOCKET EVENTS
// =====================================

// =====================================
// SOCKET EVENTS
// =====================================
function handleSocketMessage(data) {
    console.log("Socket Event:", data);

    switch (data.type) {

        case "message":

            // Refresh inbox
            loadInbox();

            if (
                selectedUser &&
                (
                    data.sender_id === selectedUser.id ||
                    data.receiver_id === selectedUser.id
                )
            ) {

                renderMessage(data);

                scrollBottom();

            }

            break;

        case "typing":

            if (
                selectedUser &&
                data.user_id === selectedUser.id
            ) {

                typingIndicator.textContent = `${sanitize(selectedUser.username)} is typing...`;

            }

            break;

        case "stop_typing":

            typingIndicator.innerHTML = "";

            break;

        case "seen":
            const tick = document.getElementById(`seen-${data.message_id}`);

            if (tick) {
            tick.textContent = "✓✓";
            }

            break;

        case "presence":

            updatePresence(data);

            break;

        case "error":

            alert(data.message);

            break;
    }

}
// =====================================
// SEND MESSAGE
// =====================================

sendBtn.addEventListener("click", sendMessage);
function sendMessage() {

    if (!selectedUser) {

        alert("Select a conversation first.");

        return;

    }

    if (socket.readyState !== WebSocket.OPEN) {

        alert("Connection lost.");

        return;

    }

    const content = messageInput.value.trim();

    if (!content) {

        return;

    }

    socket.send(
        JSON.stringify({
            type: "message",
            receiver_id: selectedUser.id,
            content: content,
            image_url: null,
            audio_url: null
        })
    );

    messageInput.value = "";

}

function updatePresence(data) {

    if (!selectedUser) {

        return;

    }

    if (data.user_id !== selectedUser.id) {

        return;

    }

    const presence = document.getElementById("presenceText");

    if (!presence) {

        return;

    }

    presence.textContent = data.online
        ? "🟢 Online"
        : "⚪ Offline";

}

messageInput.addEventListener("keydown", (e) => {

    if (e.key === "Enter") {

        e.preventDefault();

        sendMessage();

    }

});

let typingTimeout;

messageInput.addEventListener("input", () => {

    if (!selectedUser) return;

    socket.send(
        JSON.stringify({
            type: "typing",
            receiver_id: selectedUser.id
        })
    );

    clearTimeout(typingTimeout);

    typingTimeout = setTimeout(() => {

        socket.send(
            JSON.stringify({
                type: "stop_typing",
                receiver_id: selectedUser.id
            })
        );

    }, 1000);

});
// Escapes user-generated text before inserting into HTML
function sanitize(str) {
    if (str == null) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#x27;");
}

const IS_LOCAL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const BASE_URL = IS_LOCAL
    ? "http://127.0.0.1:8000"
    : "https://connecthub-lyyq.onrender.com"; 

async function apiRequest(
    endpoint,
    method = "GET",
    body = null
) {

    const token = localStorage.getItem("token");

    const headers = {};

    if (!(body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(
        BASE_URL + endpoint,
        {
            method,
            headers,
            body:
                body instanceof FormData
                    ? body
                    : body
                    ? JSON.stringify(body)
                    : null,
        }
    );

    // 204 No Content (DELETE)
    if (response.status === 204) {
        return null;
    }

    const text = await response.text();

    const data = text ? JSON.parse(text) : null;

    if (!response.ok) {
        throw new Error(
            data?.detail || "Something went wrong"
        );
    }

    return data;
}
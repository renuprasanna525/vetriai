const API_BASE_URL =
    "https://vetri-ai-backend-i3pw.onrender.com/api";


export async function refreshAccessToken() {
    const refreshToken = localStorage.getItem("refresh_token");

    if (!refreshToken) {
        throw new Error("No refresh token available.");
    }

    const response = await fetch(
        `${API_BASE_URL}/auth/refresh/`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                refresh: refreshToken,
            }),
        }
    );

    const data = await response.json();

    if (!response.ok || !data.access) {
        throw new Error(
            data.detail || "Session expired. Please log in again."
        );
    }

    localStorage.setItem("access_token", data.access);

    return data.access;
}


export async function authFetch(url, options = {}) {
    let accessToken = localStorage.getItem("access_token");

    if (!accessToken) {
        throw new Error("You are not logged in.");
    }

    async function makeRequest(token) {
        const headers = {
            ...(options.headers || {}),
            Authorization: `Bearer ${token}`,
        };

        return fetch(url, {
            ...options,
            headers,
        });
    }

    let response = await makeRequest(accessToken);

    // Access token expired/invalid.
    if (response.status === 401) {
        try {
            accessToken = await refreshAccessToken();

            // Retry the original request once.
            response = await makeRequest(accessToken);
        } catch (error) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");

            window.location.href = "/login";

            throw new Error(
                "Your session has expired. Please log in again."
            );
        }
    }

    return response;
}
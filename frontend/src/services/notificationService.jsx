import { authFetch } from "./authFetch";

const API_BASE_URL =
    "https://vetri-ai-backend-i3pw.onrender.com/api/notifications";


export async function getNotifications() {
    const response = await authFetch(
        `${API_BASE_URL}/`,
        {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || "Failed to fetch notifications"
        );
    }

    return data;
}


export async function getNotification(notificationId) {
    const response = await authFetch(
        `${API_BASE_URL}/${notificationId}/`,
        {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || "Failed to fetch notification"
        );
    }

    return data;
}


export async function markNotificationRead(notificationId) {
    const response = await authFetch(
        `${API_BASE_URL}/${notificationId}/read/`,
        {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || "Failed to mark notification as read"
        );
    }

    return data;
}

import { authFetch } from "./authFetch";
import { API_BASE_URL } from "./apiConfig";

const NOTIFICATIONS_URL = `${API_BASE_URL}/notifications`;

export async function getNotifications() {
    const response = await authFetch(
        `${NOTIFICATIONS_URL}/`,
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
        `${NOTIFICATIONS_URL}/${notificationId}/`,
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
        `${NOTIFICATIONS_URL}/${notificationId}/read/`,
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

export async function deleteNotification(notificationId) {
    const response = await authFetch(
        `${NOTIFICATIONS_URL}/${notificationId}/`,
        {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
            },
        }
    );

    if (!response.ok) {
        let data = {};

        try {
            data = await response.json();
        } catch {
            // DELETE may return an empty response body.
        }

        throw new Error(
            data.detail || "Failed to delete notification"
        );
    }

    return true;
}
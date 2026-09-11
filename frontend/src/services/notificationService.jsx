const API_BASE_URL =
    "https://vetri-ai-backend-i3pw.onrender.com/api/notifications";


export async function getNotifications(accessToken) {
    const response = await fetch(`${API_BASE_URL}/`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
        },
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || "Failed to fetch notifications"
        );
    }

    return data;
}


export async function getNotification(
    notificationId,
    accessToken
) {
    const response = await fetch(
        `${API_BASE_URL}/${notificationId}/`,
        {
            method: "GET",
            headers: {
                Authorization: `Bearer ${accessToken}`,
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


export async function markNotificationRead(
    notificationId,
    accessToken
) {
    const response = await fetch(
        `${API_BASE_URL}/${notificationId}/read/`,
        {
            method: "PUT",
            headers: {
                Authorization: `Bearer ${accessToken}`,
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
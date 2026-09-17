import { authFetch } from "./authFetch";

const API_BASE_URL =
    "https://vetri-ai-backend-i3pw.onrender.com/api";


export async function getUserRoles() {
    const response = await authFetch(
        `${API_BASE_URL}/user-roles/`,
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
            data.detail || "Failed to load user roles"
        );
    }

    return data;
}
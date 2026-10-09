
import { authFetch } from "./authFetch";
import { API_BASE_URL } from "./apiConfig";

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
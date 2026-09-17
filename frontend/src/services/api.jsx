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
            data.detail || "Failed to fetch user roles."
        );
    }

    return data;
}


export async function getPermissions() {
    const response = await authFetch(
        `${API_BASE_URL}/permissions/`,
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
            data.detail || "Failed to fetch permissions."
        );
    }

    return data;
}


export async function getAgents() {
    const response = await authFetch(
        `${API_BASE_URL}/agents/`,
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
            data.detail || "Failed to fetch available agents."
        );
    }

    return data;
}


export async function getDashboard() {
    const response = await authFetch(
        `${API_BASE_URL}/dashboard/`,
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
            data.detail || "Failed to fetch dashboard data."
        );
    }

    return data;
}
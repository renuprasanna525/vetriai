
import { authFetch } from "./authFetch";
import { API_BASE_URL } from "./apiConfig";

const APPROVALS_URL = `${API_BASE_URL}/approvals`;

export async function createApprovalPreview({
    agent_name,
    tool_name,
    action,
    parameters = {},
}) {
    const response = await authFetch(
        `${APPROVALS_URL}/preview/`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                agent_name,
                tool_name,
                action,
                parameters,
            }),
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.message ||
            data.detail ||
            "Failed to create approval preview"
        );
    }

    return data;
}

export async function getApprovals(status = "") {
    const query = status
        ? `?status=${encodeURIComponent(status)}`
        : "";

    const response = await authFetch(
        `${APPROVALS_URL}/${query}`,
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
            data.message ||
            data.detail ||
            "Failed to get approvals"
        );
    }

    return data;
}

export async function getApproval(actionId) {
    const response = await authFetch(
        `${APPROVALS_URL}/${actionId}/`,
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
            data.message ||
            data.detail ||
            "Failed to get approval"
        );
    }

    return data;
}

export async function approveAction(actionId) {
    const response = await authFetch(
        `${APPROVALS_URL}/${actionId}/approve/`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.message ||
            data.detail ||
            "Failed to approve action"
        );
    }

    return data;
}

export async function editApproval(
    actionId,
    parameters
) {
    const response = await authFetch(
        `${APPROVALS_URL}/${actionId}/edit/`,
        {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                parameters,
            }),
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.message ||
            data.detail ||
            "Failed to edit action"
        );
    }

    return data;
}

export async function cancelAction(actionId) {
    const response = await authFetch(
        `${APPROVALS_URL}/${actionId}/cancel/`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.message ||
            data.detail ||
            "Failed to cancel action"
        );
    }

    return data;
}
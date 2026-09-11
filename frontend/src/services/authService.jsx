const API_BASE_URL = 'https://vetri-ai-backend-i3pw.onrender.com/api';

export async function loginUser(username, password) {
    const response = await fetch(
        `${API_BASE_URL}/auth/login/`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                password,
            }),
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || 'Invalid username or password'
        );
    }

    return data;
}


export async function getCurrentUser() {
    const accessToken = localStorage.getItem('access_token');

    if (!accessToken) {
        throw new Error('You are not logged in.');
    }

    const response = await fetch(
        `${API_BASE_URL}/auth/me/`,
        {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || 'Failed to get current user'
        );
    }

    return data;
}
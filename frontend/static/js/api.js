const API_BASE = '/api';

async function apiRequest(method, path, body = null) {
    const opts = {
        method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
    };
    if (body) opts.body = JSON.stringify(body);

    const res = await fetch(`${API_BASE}${path}`, opts);
    const data = await res.json();

    if (res.status === 401 && !path.includes('/auth/login')) {
        window.location.href = '/login';
        return data;
    }

    return data;
}

const api = {
    login: (username, password) => apiRequest('POST', '/auth/login', { username, password }),
    logout: () => apiRequest('POST', '/auth/logout'),
    getProfile: () => apiRequest('GET', '/profile/me'),
    getTodayPrediction: () => apiRequest('GET', '/predictions/today'),
    createPrediction: (target_gpa) => apiRequest('POST', '/predictions', { target_gpa }),
    getHistory: () => apiRequest('GET', '/predictions/history'),
    adminListUsers: () => apiRequest('GET', '/admin/users'),
    adminCreateUser: (data) => apiRequest('POST', '/admin/users', data),
    adminLockUser: (id) => apiRequest('PUT', `/admin/users/${id}/lock`),
    adminUnlockUser: (id) => apiRequest('PUT', `/admin/users/${id}/unlock`),
    adminListProfiles: () => apiRequest('GET', '/admin/profiles'),
    adminUpdateProfile: (id, data) => apiRequest('PUT', `/admin/profiles/${id}`, data),
};

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('loginError');
        const btn = form.querySelector('button');

        errorDiv.style.display = 'none';
        btn.disabled = true;
        btn.textContent = 'Logging in...';

        const result = await api.login(username, password);

        if (result.success) {
            if (result.data.role === 'ADMIN') {
                window.location.href = '/admin';
            } else {
                window.location.href = '/dashboard';
            }
        } else {
            errorDiv.textContent = result.message || 'Login failed';
            errorDiv.style.display = 'block';
            btn.disabled = false;
            btn.textContent = 'Login';
        }
    });
});

async function logout() {
    await api.logout();
    window.location.href = '/login';
}

document.addEventListener('DOMContentLoaded', async () => {
    const section = document.getElementById('adminSection');
    const action = section?.dataset.action;

    if (action === 'dashboard') await loadAdminDashboard();
    else if (action === 'users') await loadUsers();
    else if (action === 'profiles') await loadProfiles();
    else if (action === 'createUser') initCreateUser();
    else if (action === 'editProfile') initEditProfile();
});

async function loadAdminDashboard() {
    const usersRes = await api.adminListUsers();
    const profilesRes = await api.adminListProfiles();
    const statsDiv = document.getElementById('adminStats');

    if (usersRes.success && profilesRes.success) {
        const users = usersRes.data.users;
        const profiles = profilesRes.data.profiles;
        const activeUsers = users.filter(u => u.status === 'ACTIVE').length;
        const lockedUsers = users.filter(u => u.status === 'LOCKED').length;
        const completedProfiles = profiles.filter(p => p.student_code !== 'PENDING').length;

        statsDiv.innerHTML = `
            <div class="profile-grid" style="grid-template-columns:repeat(auto-fill,minmax(180px,1fr))">
                <div class="profile-item"><div class="label">Total Users</div><div class="value">${users.length}</div></div>
                <div class="profile-item"><div class="label">Active Users</div><div class="value">${activeUsers}</div></div>
                <div class="profile-item"><div class="label">Locked Users</div><div class="value">${lockedUsers}</div></div>
                <div class="profile-item"><div class="label">Total Profiles</div><div class="value">${profiles.length}</div></div>
                <div class="profile-item"><div class="label">Completed Profiles</div><div class="value">${completedProfiles}</div></div>
            </div>
        `;
    }
}

async function loadUsers() {
    const tbody = document.getElementById('usersBody');
    const res = await api.adminListUsers();
    if (!res.success) return;

    res.data.users.forEach(u => {
        const tr = document.createElement('tr');
        const badgeClass = u.status === 'ACTIVE' ? 'badge-active' : 'badge-locked';
        const lockBtn = u.username === 'admin' ? '' :
            u.status === 'ACTIVE'
                ? `<button class="btn btn-sm btn-danger" onclick="toggleLock(${u.user_id}, 'lock')">Lock</button>`
                : `<button class="btn btn-sm btn-success" onclick="toggleLock(${u.user_id}, 'unlock')">Unlock</button>`;
        tr.innerHTML = `
            <td>${u.user_id}</td>
            <td>${u.username}</td>
            <td>${u.role}</td>
            <td><span class="badge ${badgeClass}">${u.status}</span></td>
            <td>${new Date(u.created_at).toLocaleDateString()}</td>
            <td class="btn-group">${lockBtn}</td>
        `;
        tbody.appendChild(tr);
    });
}

async function toggleLock(userId, action) {
    const res = action === 'lock'
        ? await api.adminLockUser(userId)
        : await api.adminUnlockUser(userId);
    if (res.success) {
        window.location.reload();
    } else {
        alert(res.message || res.detail?.message || 'Action failed');
    }
}

async function loadProfiles() {
    const tbody = document.getElementById('profilesBody');
    const res = await api.adminListProfiles();
    if (!res.success) return;

    res.data.profiles.forEach(p => {
        const tr = document.createElement('tr');
        const isPending = p.student_code === 'PENDING';
        tr.innerHTML = `
            <td>${p.profile_id}</td>
            <td>${p.user_id}</td>
            <td>${p.student_code}</td>
            <td>${p.full_name}</td>
            <td>${p.major || '-'}</td>
            <td>${p.previous_cgpa || '-'}</td>
            <td><a href="/admin/profiles/${p.profile_id}/edit" class="btn btn-sm btn-primary">${isPending ? 'Setup' : 'Edit'}</a></td>
        `;
        tbody.appendChild(tr);
    });
}

function initCreateUser() {
    const form = document.getElementById('createUserForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const errorDiv = document.getElementById('createError');
        errorDiv.style.display = 'none';

        const data = {
            username: document.getElementById('username').value.trim(),
            password: document.getElementById('password').value,
            role: document.getElementById('role').value,
        };

        const res = await api.adminCreateUser(data);
        if (res.success) {
            window.location.href = '/admin/users';
        } else {
            errorDiv.textContent = res.message || res.detail?.message || 'Failed to create user';
            errorDiv.style.display = 'block';
        }
    });
}

function initEditProfile() {
    const section = document.getElementById('adminSection');
    const profileId = section.dataset.profileId;
    const form = document.getElementById('editProfileForm');

    api.adminListProfiles().then(res => {
        if (res.success) {
            const profile = res.data.profiles.find(p => p.profile_id == profileId);
            if (profile) {
                document.getElementById('studentCode').value = profile.student_code === 'PENDING' ? '' : profile.student_code;
                document.getElementById('fullName').value = profile.full_name === 'Not Set' ? '' : profile.full_name;
            }
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const errorDiv = document.getElementById('profileError');
        errorDiv.style.display = 'none';

        const data = {
            student_code: document.getElementById('studentCode').value.trim(),
            full_name: document.getElementById('fullName').value.trim(),
            gender: document.getElementById('gender').value,
            age: parseInt(document.getElementById('age').value),
            major: document.getElementById('major').value.trim(),
            attendance_percentage: parseFloat(document.getElementById('attendance').value),
            study_hours_per_day: parseFloat(document.getElementById('studyHours').value),
            sleep_hours_per_day: parseFloat(document.getElementById('sleepHours').value),
            social_hours_per_week: parseFloat(document.getElementById('socialHours').value),
            previous_cgpa: parseFloat(document.getElementById('previousCgpa').value),
        };

        const res = await api.adminUpdateProfile(profileId, data);
        if (res.success) {
            window.location.href = '/admin/profiles';
        } else {
            errorDiv.textContent = res.message || res.detail?.message || 'Failed to update profile';
            errorDiv.style.display = 'block';
        }
    });
}

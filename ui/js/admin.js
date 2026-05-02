document.addEventListener('DOMContentLoaded', async () => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/admin/login';
        return;
    }

    // Load Admin Info
    try {
        const response = await fetch('/api/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const user = await response.json();
            document.getElementById('header-user-name').textContent = user.full_name || user.email;
            document.getElementById('header-avatar').textContent = (user.full_name ? user.full_name[0] : user.email[0]).toUpperCase();

            if (user.role !== 'admin') {
                alert('Access Denied: Admin privileges required.');
                window.location.href = '/';
                return;
            }
        } else {
            window.location.href = '/admin/login';
            return;
        }
    } catch (e) {
        window.location.href = '/admin/login';
        return;
    }

    // Initial Load
    initNavigation();
    loadDashboardStats();

    // Auto Refresh for live data (every 10 seconds) - Silently update
    setInterval(() => {
        const activeSection = document.querySelector('.admin-content-section:not(.hidden)').id;
        if (activeSection === 'overview-section') loadDashboardStats(true);
        if (activeSection === 'audit-section') fetchAuditLogs(true);
        if (activeSection === 'users-section') fetchUsers(true);
    }, 10000);

    // Fade out loader
    const loader = document.getElementById('loading-overlay');
    loader.style.opacity = '0';
    setTimeout(() => loader.classList.add('hidden'), 500);
});

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item[data-section]');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const sectionId = item.getAttribute('data-section');

            // Update UI State
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            document.querySelectorAll('.admin-content-section').forEach(section => {
                section.classList.add('hidden');
                section.classList.remove('active');
            });

            const activeSection = document.getElementById(`${sectionId}-section`);
            activeSection.classList.remove('hidden');
            activeSection.classList.add('active');

            // Load Data
            if (sectionId === 'users') fetchUsers();
            if (sectionId === 'audit') fetchAuditLogs();
            if (sectionId === 'overview') loadDashboardStats();
        });
    });
}

async function loadDashboardStats(isSilent = false) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/admin/stats', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const data = await response.json();
            document.getElementById('stat-total-users').textContent = data.total_users;
            document.getElementById('stat-active-users').textContent = data.active_users;
            document.getElementById('stat-total-threads').textContent = data.total_threads;
            document.getElementById('stat-total-emails').textContent = data.total_emails;
            document.getElementById('stat-total-meetings').textContent = data.total_meetings;
            document.getElementById('stat-total-errors').textContent = data.total_errors;
        }
    } catch (e) { console.error("Stats fail", e); }
}

async function fetchUsers(isSilent = false) {
    const tableBody = document.getElementById('users-table-body');
    // Only show loading if table is empty
    if (!isSilent && tableBody.children.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 48px; color: #64748b;">Syncing users...</td></tr>';
    }

    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/admin/users', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const users = await response.json();
            let html = '';
            users.forEach(user => {
                html += `
                    <tr>
                        <td><div style="font-weight: 600;">${user.full_name || 'System User'}</div></td>
                        <td style="color: #64748b;">${user.email}</td>
                        <td><span class="badge badge-${user.role}">${user.role}</span></td>
                        <td><span class="badge-status badge-${user.is_active ? 'active' : 'inactive'}">● ${user.is_active ? 'Active' : 'Disabled'}</span></td>
                        <td style="color: #94a3b8; font-size: 13px;">${new Date(user.created_at).toLocaleDateString()}</td>
                        <td style="color: #94a3b8; font-size: 13px;">${user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</td>
                        <td>
                            <button class="btn-view" onclick="viewUserDetail(${user.id})">View</button>
                            <button class="btn-view" style="color: #ef4444; margin-left: 8px;" onclick="toggleUserStatus(${user.id}, ${user.is_active})">
                                ${user.is_active ? 'Disable' : 'Enable'}
                            </button>
                        </td>
                    </tr>
                `;
            });
            tableBody.innerHTML = html;
        }
    } catch (e) { console.error("Users fail", e); }
}

async function fetchAuditLogs(isSilent = false) {
    const container = document.getElementById('audit-list');
    // Only show loading if list is empty
    if (!isSilent && container.children.length === 0) {
        container.innerHTML = '<div style="padding: 48px; text-align: center; color: #64748b;">Loading activity trail...</div>';
    }

    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/admin/audit', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const logs = await response.json();
            let html = '';
            logs.forEach(log => {
                const actionType = log.action.split('_')[0].toLowerCase();
                html += `
                    <div class="audit-row">
                        <div class="audit-badge ${actionType}">${log.action}</div>
                        <div style="flex: 1;">
                            <div style="font-weight: 600; font-size: 14px;">${log.user_name} <span style="font-weight: 400; color: #94a3b8; margin-left: 4px;">&lt;${log.user_email}&gt;</span></div>
                            <div style="font-size: 12px; color: #64748b; margin-top: 2px;">IP: ${log.ip_address || '0.0.0.0'}</div>
                        </div>
                        <div style="color: #94a3b8; font-size: 13px;">${new Date(log.timestamp).toLocaleString()}</div>
                    </div>
                `;
            });
            container.innerHTML = html || '<div style="padding: 40px; text-align: center; color: #94a3b8;">No activity logged yet.</div>';
        }
    } catch (e) { console.error("Audit fail", e); }
}

async function viewUserDetail(userId) {
    const drawer = document.getElementById('details-drawer');
    const overlay = document.getElementById('sidebar-overlay');
    const content = document.getElementById('drawer-content');
    const disableBtn = document.getElementById('sidebar-disable-btn');

    content.innerHTML = '<div style="padding: 40px; text-align: center; color: #64748b;">Fetching account details...</div>';
    drawer.style.right = '0';
    overlay.style.display = 'block';

    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/admin/users/${userId}/detail`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const data = await response.json();
            const u = data.user;
            const s = data.stats;

            disableBtn.onclick = () => toggleUserStatus(u.id, u.is_active);
            disableBtn.textContent = u.is_active ? 'Disable User' : 'Enable User';

            content.innerHTML = `
                <div class="detail-box" style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);">
                    <div style="font-size: 24px; font-weight: 700; margin-bottom: 4px;">${u.full_name || 'System User'}</div>
                    <div style="color: #0369a1; font-size: 14px; margin-bottom: 16px;">${u.email}</div>
                    <div style="display: flex; gap: 8px;">
                        <span class="badge badge-${u.role}">${u.role}</span>
                        <span class="badge-status badge-${u.is_active ? 'active' : 'inactive'}" style="background: white; padding: 4px 10px; border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">● ${u.is_active ? 'Active' : 'Disabled'}</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 32px;">
                        <div>
                            <div class="detail-label">Joined</div>
                            <div class="detail-value">${new Date(u.created_at).toLocaleDateString()}</div>
                        </div>
                        <div>
                            <div class="detail-label">Last Login</div>
                            <div class="detail-value">${u.last_login ? new Date(u.last_login).toLocaleDateString() : 'Never'}</div>
                        </div>
                    </div>
                </div>

                <div style="margin-bottom: 32px;">
                    <div class="detail-label">Metric Summary</div>
                    <div style="display: flex; gap: 24px; margin-top: 12px;">
                        <div>
                            <div style="font-size: 20px; font-weight: 700;">${s.emails_processed}</div>
                            <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">Emails</div>
                        </div>
                        <div>
                            <div style="font-size: 20px; font-weight: 700;">${s.drafts_created}</div>
                            <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">Drafts</div>
                        </div>
                    </div>
                </div>

                <div class="detail-label" style="margin-bottom: 16px;">Record History (${data.recent_activity.length})</div>
                <div style="display: flex; flex-direction: column; gap: 12px;">
                    ${data.recent_activity.map(log => `
                        <div style="padding: 16px; background: #fafafa; border-radius: 12px; border: 1px solid #f1f5f9;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                <span style="font-size: 11px; color: var(--text-muted);">${new Date(log.timestamp).toLocaleDateString()}</span>
                                <span style="font-weight: 700; font-size: 10px; color: var(--primary-blue); text-transform: uppercase;">${log.action}</span>
                            </div>
                            <div style="font-size: 13px; font-weight: 600;">System Interaction</div>
                            <div style="font-size: 12px; color: #64748b; margin-top: 4px;">${log.details || 'General action recorded.'}</div>
                        </div>
                    `).join('')}
                    ${data.recent_activity.length === 0 ? '<div style="color: #94a3b8; font-size: 13px; font-style: italic; text-align: center; padding: 20px;">No record found.</div>' : ''}
                </div>
            `;
        }
    } catch (e) {
        content.innerHTML = '<div style="padding: 40px; color: #ef4444; text-align: center;">Connection lost.</div>';
    }
}

function closeDetails() {
    document.getElementById('details-drawer').style.right = '-450px';
    document.getElementById('sidebar-overlay').style.display = 'none';
}

async function toggleUserStatus(userId, currentStatus) {
    if (!confirm('Confirm status modification?')) return;
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/admin/users/${userId}`, {
            method: 'PATCH',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_active: !currentStatus })
        });
        if (response.ok) { fetchUsers(true); viewUserDetail(userId); }
    } catch (e) { console.error("Toggle fail", e); }
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/admin/login';
}

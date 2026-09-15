// FindIT Client Interactivity Script
document.addEventListener('DOMContentLoaded', function () {
    loadNotifications();
    setInterval(loadNotifications, 30000); // Poll notifications every 30s
});

function loadNotifications() {
    const dropdown = document.getElementById('notif-dropdown-list');
    const badge = document.getElementById('notif-unread-count');
    if (!dropdown || !badge) return;

    fetch('/api/notifications?unread=true')
        .then(res => res.json())
        .then(data => {
            badge.textContent = data.unread_count > 0 ? data.unread_count : '';
            badge.style.display = data.unread_count > 0 ? 'inline-block' : 'none';

            if (data.notifications.length === 0) {
                dropdown.innerHTML = '<li><span class="dropdown-item text-muted">No unread notifications</span></li>';
                return;
            }

            let html = '';
            data.notifications.forEach(n => {
                html += `
                <li>
                    <a class="dropdown-item text-wrap py-2" href="#" onclick="markNotificationRead(${n.id}); return false;">
                        <strong class="d-block text-info">${escapeHtml(n.title)}</strong>
                        <small class="text-light">${escapeHtml(n.message)}</small>
                    </a>
                </li>`;
            });
            dropdown.innerHTML = html;
        })
        .catch(err => console.error('Failed to load notifications:', err));
}

function markNotificationRead(id) {
    fetch(`/api/notifications/${id}/read`, { method: 'POST' })
        .then(() => loadNotifications())
        .catch(err => console.error('Error marking notification read:', err));
}

function triggerMatchEngine(reportId) {
    const btn = document.getElementById('btn-run-match');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Evaluating...';
    }

    fetch('/api/matches/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lost_report_id: reportId })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        window.location.reload();
    })
    .catch(err => {
        alert('Matching engine execution failed.');
        console.error(err);
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = 'Run Matching Engine';
        }
    });
}

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

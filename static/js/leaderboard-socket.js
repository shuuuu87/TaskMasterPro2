// Connect to Socket.IO
const socket = io();

let leaderboardData = [];
let sortAsc = false;
let currentUserId = null;

// Try to get current user id from a meta tag or global JS variable if available
if (window.currentUserId === undefined) {
    const meta = document.querySelector('meta[name="current-user-id"]');
    if (meta) currentUserId = parseInt(meta.getAttribute('content'));
} else {
    currentUserId = window.currentUserId;
}

socket.on('leaderboard_update', function(leaderboard) {
    leaderboardData = leaderboard;
    // Find current user streak and update streak bar
    if (currentUserId) {
        const me = leaderboard.find(u => u.id === currentUserId);
        if (me) updateStreakBar(me.streak || 0);
    }
    renderLeaderboard();
});

function renderLeaderboard() {
    const tbody = document.querySelector('#leaderboard-table-body');
    if (!tbody) return;
    tbody.innerHTML = '';
    let filtered = leaderboardData;
    const search = document.getElementById('search-user');
    if (search && search.value.trim()) {
        const val = search.value.trim().toLowerCase();
        filtered = leaderboardData.filter(u => u.username.toLowerCase().includes(val));
    }
    filtered = filtered.slice();
    if (window.sortByScore) {
        filtered.sort((a, b) => sortAsc ? a.score - b.score : b.score - a.score);
    }
    filtered.forEach((user, idx) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${idx + 1}</td>
            <td><i class="fas fa-user-circle me-2 text-muted"></i> ${user.username}</td>
            <td><span class="badge" style="background-color: ${user.badge_color};"><i class="fas ${user.badge_icon} me-1"></i>${user.badge_name}</span></td>
            <td>${user.is_online ? '<span class="badge bg-success" aria-label="Online" title="Online"><i class="fas fa-circle me-1"></i>Online</span>' : '<span class="badge bg-secondary" aria-label="Offline" title="Offline"><i class="fas fa-circle me-1"></i>Offline</span>'}</td>
            <td>${user.score}</td>
            <td class="last-online" data-last-active="${user.last_active || ''}">${formatTimeAgo(user.last_active)}</td>
        `;
        tbody.appendChild(tr);
    });
}

function formatTimeAgo(isoString) {
    if (!isoString) return '';
    const lastActive = new Date(isoString);
    const now = new Date();
    const diff = Math.floor((now - lastActive) / 1000); // seconds
    if (diff < 1) return 'just now';
    if (diff < 60) return `${diff} second(s) ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)} minute(s) ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} hour(s) ago`;
    return `${Math.floor(diff / 86400)} day(s) ago`;
}

// Periodically update 'Last Online' text
setInterval(() => {
    document.querySelectorAll('.last-online').forEach(td => {
        const iso = td.getAttribute('data-last-active');
        td.textContent = formatTimeAgo(iso);
    });
}, 1000); // every 1 second

// Search functionality
const searchInput = document.getElementById('search-user');
if (searchInput) {
    searchInput.addEventListener('input', renderLeaderboard);
}

// Sorting functionality
const scoreSort = document.getElementById('score-sort');
if (scoreSort) {
    scoreSort.addEventListener('click', () => {
        window.sortByScore = !window.sortByScore;
        sortAsc = !sortAsc;
        renderLeaderboard();
    });
}

// Notification UI logic
let notifications = [];
function addNotification(msg) {
    notifications.unshift({ msg, time: new Date() });
    updateNotifUI();
}
function updateNotifUI() {
    const notifCount = document.getElementById('notif-count');
    const notifDropdown = document.getElementById('notif-dropdown');
    if (!notifCount || !notifDropdown) return;
    if (notifications.length > 0) {
        notifCount.textContent = notifications.length;
        notifCount.style.display = '';
        notifDropdown.innerHTML = notifications.slice(0, 5).map(n => `<li><span class="dropdown-item-text">${n.msg}<br><small class='text-muted'>${formatTimeAgo(n.time.toISOString())}</small></span></li>`).join('');
    } else {
        notifCount.style.display = 'none';
        notifDropdown.innerHTML = '<li><span class="dropdown-item-text text-muted">No new notifications</span></li>';
    }
}
// Example: addNotification('Welcome to the leaderboard!');

// Streak/progress bar logic (dummy example, replace with real data)
function updateStreakBar(days) {
    const bar = document.getElementById('streak-bar');
    if (!bar) return;
    const maxStreak = 120;
    const percent = Math.min(100, (days / maxStreak) * 100);
    bar.style.width = percent + '%';
    bar.setAttribute('aria-valuenow', percent);
    bar.textContent = `${days} / ${maxStreak} days`;
    // Change color if max streak reached
    if (days >= maxStreak) {
        bar.classList.remove('bg-success');
        bar.classList.add('bg-warning');
    } else {
        bar.classList.remove('bg-warning');
        bar.classList.add('bg-success');
    }
}
// Example: updateStreakBar(3);

document.addEventListener('DOMContentLoaded', function() {
    updateNotifUI();
    updateStreakBar(3); // Replace 3 with real streak value from backend
});

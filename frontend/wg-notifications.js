// wg-notifications.js — shared across all pages.
// Notifications are now stored server-side (shared across everyone), with
// read/unread state tracked per logged-in user's email. If nobody is logged
// in, the badge just stays hidden — notifications are tied to an account.

const WG_BACKEND_URL = "https://wildguard-hwc-prediction-system.onrender.com";

function wgCurrentUserEmail() {
  try {
    const user = JSON.parse(localStorage.getItem('wg_user') || 'null');
    return (user && user.loggedIn && user.email) ? user.email : null;
  } catch (e) { return null; }
}

async function wgGetNotifications() {
  const email = wgCurrentUserEmail();
  if (!email) return [];
  try {
    const res = await fetch(`${WG_BACKEND_URL}/api/notifications?user_email=${encodeURIComponent(email)}`);
    if (!res.ok) return [];
    return await res.json(); // [{id, title, body, created_at, read}]
  } catch (e) { return []; }
}

// For ad-hoc client-triggered notifications (e.g. escalating a risk level).
// Detections don't need this — the backend creates one automatically per detection.
async function wgAddNotification(title, body) {
  try {
    await fetch(`${WG_BACKEND_URL}/api/notifications?title=${encodeURIComponent(title)}&body=${encodeURIComponent(body)}`, { method: 'POST' });
  } catch (e) { /* best-effort */ }
  wgUpdateBadge();
}

async function wgMarkNotificationRead(id) {
  const email = wgCurrentUserEmail();
  if (!email) return;
  try {
    await fetch(`${WG_BACKEND_URL}/api/notifications/${id}/read?user_email=${encodeURIComponent(email)}`, { method: 'POST' });
  } catch (e) { /* best-effort */ }
  wgUpdateBadge();
}

async function wgMarkAllNotificationsRead() {
  const email = wgCurrentUserEmail();
  if (!email) return;
  try {
    await fetch(`${WG_BACKEND_URL}/api/notifications/read-all?user_email=${encodeURIComponent(email)}`, { method: 'POST' });
  } catch (e) { /* best-effort */ }
  wgUpdateBadge();
}

async function wgUpdateBadge() {
  const list = await wgGetNotifications();
  const unread = list.filter(n => !n.read).length;
  document.querySelectorAll('.wg-nav-badge').forEach(function (el) {
    if (unread > 0) {
      el.textContent = unread > 9 ? '9+' : String(unread);
      el.style.display = '';
    } else {
      el.style.display = 'none';
    }
  });
}

/* ── Config ─────────────────────────────────────────── */
const API = 'http://localhost:8001/api';

/* ── Auth ───────────────────────────────────────────── */
const Auth = {
  getToken: () => localStorage.getItem('ims_token'),
  getUser:  () => JSON.parse(localStorage.getItem('ims_user') || 'null'),
  set(token, user) {
    localStorage.setItem('ims_token', token);
    localStorage.setItem('ims_user', JSON.stringify(user));
  },
  clear() {
    localStorage.removeItem('ims_token');
    localStorage.removeItem('ims_user');
  },
  isLoggedIn: () => !!localStorage.getItem('ims_token'),
  requireAuth() {
    if (!this.isLoggedIn()) {
      window.location.href = '/pages/login.html';
      return false;
    }
    return true;
  }
};

/* ── API Client ─────────────────────────────────────── */
async function apiFetch(path, options = {}) {
  const token = Auth.getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  try {
    const res = await fetch(`${API}${path}`, { ...options, headers });
    if (res.status === 401) { Auth.clear(); window.location.href = '/pages/login.html'; return null; }
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || `Error ${res.status}`);
    return data;
  } catch (e) {
    throw e;
  }
}

const get    = (path)         => apiFetch(path);
const post   = (path, body)   => apiFetch(path, { method: 'POST',   body: JSON.stringify(body) });
const put    = (path, body)   => apiFetch(path, { method: 'PUT',    body: body ? JSON.stringify(body) : undefined });
const del    = (path)         => apiFetch(path, { method: 'DELETE' });
const patch  = (path, body)   => apiFetch(path, { method: 'PATCH',  body: JSON.stringify(body) });

/* ── Toast ──────────────────────────────────────────── */
function toast(msg, type = 'success', duration = 3500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const icons = { success: '✓', error: '✕', warning: '⚠' };
  const el = document.createElement('div');
  el.className = `toast-msg ${type}`;
  el.innerHTML = `<span>${icons[type] || '•'}</span><span>${msg}</span>`;
  container.appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; el.style.transition = 'opacity .3s'; setTimeout(() => el.remove(), 300); }, duration);
}

/* ── Modal helpers ──────────────────────────────────── */
function openModal(id) { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }
function closeAllModals() { document.querySelectorAll('.modal-backdrop-custom').forEach(m => m.classList.remove('open')); }
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeAllModals(); });

/* ── Format helpers ─────────────────────────────────── */
function fmtCurrency(v) {
  return '₹' + Number(v || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function fmtDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}
function fmtDateTime(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
}
function timeAgo(iso) {
  if (!iso) return '';
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

/* ── Status badge ───────────────────────────────────── */
function statusBadge(status) {
  const map = {
    draft:'gray', submitted:'info', approved:'purple', received:'success', cancelled:'danger',
    pending:'warning', confirmed:'info', picked:'purple', shipped:'info', delivered:'success',
    low_stock:'warning', out_of_stock:'danger', overstock:'info',
    ok:'success', low:'warning', out:'danger',
    healthy:'success', reorder:'warning', critical:'danger'
  };
  const cls = map[status] || 'gray';
  return `<span class="badge-status ${cls}">${status.replace(/_/g,' ')}</span>`;
}

/* ── Sidebar active link ────────────────────────────── */
function setSidebarActive() {
  const path = window.location.pathname.split('/').pop();
  document.querySelectorAll('.sidebar-nav a').forEach(a => {
    const href = a.getAttribute('href').split('/').pop();
    a.classList.toggle('active', href === path);
  });
}

/* ── Render sidebar user ────────────────────────────── */
function renderSidebarUser() {
  const user = Auth.getUser();
  if (!user) return;
  const el = document.getElementById('sidebar-user-info');
  if (!el) return;
  const initials = user.name.split(' ').map(n => n[0]).join('').slice(0,2).toUpperCase();
  el.innerHTML = `
    <div class="avatar">${initials}</div>
    <div>
      <div class="user-name">${user.name}</div>
      <div class="user-role">${user.role}</div>
    </div>
    <a href="#" class="logout-btn" onclick="logout()" title="Logout">⏻</a>
  `;
}

function logout() {
  Auth.clear();
  window.location.href = '/pages/login.html';
}

/* ── Alert badge refresh ─────────────────────────────── */
async function refreshAlertBadge() {
  try {
    const alerts = await get('/alerts/');
    const unread = alerts ? alerts.filter(a => !a.is_read).length : 0;
    const badge = document.getElementById('alert-badge');
    if (badge) {
      badge.textContent = unread;
      badge.style.display = unread > 0 ? 'inline' : 'none';
    }
  } catch (e) {}
}

/* ── Stock bar HTML ─────────────────────────────────── */
function stockBar(qty, reorder, max) {
  const pct = Math.min(100, Math.round((qty / (max || 100)) * 100));
  const color = qty === 0 ? 'var(--danger)' : qty <= reorder ? 'var(--warning)' : 'var(--success)';
  return `
    <div class="stock-bar-wrap">
      <span class="mono fw-600" style="min-width:40px">${qty}</span>
      <div class="stock-bar-bg">
        <div class="stock-bar-fill" style="width:${pct}%;background:${color}"></div>
      </div>
    </div>`;
}

/* ── PO / SO status color ────────────────────────────── */
function poStatusBadge(s) { return statusBadge(s); }

/* ── On every page load ──────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  setSidebarActive();
  renderSidebarUser();

  // Only run alert polling on authenticated pages
  if (Auth.isLoggedIn()) {
    refreshAlertBadge();
    setInterval(refreshAlertBadge, 30000);
  }
});
// Clock
function updateClock() {
  const el = document.getElementById('clock');
  if (!el) return;
  const now = new Date();
  const h = String(now.getHours()).padStart(2,'0');
  const m = String(now.getMinutes()).padStart(2,'0');
  const s = String(now.getSeconds()).padStart(2,'0');
  el.textContent = `${h}:${m}:${s} WIB`;
}
setInterval(updateClock, 1000);
updateClock();

// Dark Mode
function applyDark(on) {
  document.body.classList.toggle('dark', on);
  const btn = document.getElementById('darkToggle');
  if (btn) btn.classList.toggle('on', on);
}
document.addEventListener('DOMContentLoaded', () => {
  applyDark(localStorage.getItem('dark') === '1');
});
function toggleDark() {
  const on = !document.body.classList.contains('dark');
  applyDark(on);
  localStorage.setItem('dark', on ? '1' : '0');
}

// Sidebar toggle handled in base.html with localStorage persistence

// Toast
function showToast(msg, type = 'success') {
  const toast = document.getElementById('toast');
  const msgEl = document.getElementById('toastMsg');
  if (!toast) return;
  if (msgEl) msgEl.textContent = msg;
  toast.className = 'toast' + (type === 'error' ? ' error' : '');
  toast.classList.add('show');
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove('show'), 3000);
}

// Format Rupiah
function fRp(n) {
  return 'Rp ' + Number(n).toLocaleString('id-ID');
}

// Confirm helper
function confirmDel(msg) {
  return confirm(msg || 'Yakin ingin menghapus data ini?');
}

// CSRF from cookie
function getCsrf() {
  const c = document.cookie.split(';').find(x => x.trim().startsWith('csrftoken='));
  return c ? c.trim().split('=')[1] : '';
}

/* StakeFolclor v2 - main.js */

// ── Auto-dismiss alerts ──────────────────────────────
document.addEventListener('DOMContentLoaded', () => {

  document.querySelectorAll('.sf-alert-auto').forEach(el => {
    setTimeout(() => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(-8px)';
      el.style.transition = 'all .3s';
      setTimeout(() => el.remove(), 320);
    }, 4500);
  });

  // ── Active nav ──────────────────────────────────────
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link-sf').forEach(a => {
    if (a.getAttribute('href') === path) a.classList.add('active');
  });

  // ── Ticket drawer ───────────────────────────────────
  const drawer = document.getElementById('ticket-drawer');
  const fab    = document.getElementById('ticket-fab');
  const drawerClose = document.getElementById('drawer-close');
  const overlay = document.getElementById('drawer-overlay');

  function openDrawer() {
    drawer?.classList.add('open');
    overlay?.classList.add('show');
    document.body.style.overflow = 'hidden';
  }
  function closeDrawer() {
    drawer?.classList.remove('open');
    overlay?.classList.remove('show');
    document.body.style.overflow = '';
  }
  fab?.addEventListener('click', openDrawer);
  drawerClose?.addEventListener('click', closeDrawer);
  overlay?.addEventListener('click', closeDrawer);

  // Drawer tabs
  document.querySelectorAll('.drawer-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;
      document.querySelectorAll('.drawer-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.drawer-panel').forEach(p => p.style.display = 'none');
      tab.classList.add('active');
      document.getElementById(target)?.style.setProperty('display', 'block');
    });
  });

  // ── Bet preview ─────────────────────────────────────
  document.addEventListener('input', e => {
    if (!e.target.matches('.bet-input')) return;
    const id   = e.target.dataset.optid;
    const odds = parseFloat(document.getElementById('odds-' + id)?.textContent || 1);
    const amt  = parseFloat(e.target.value) || 0;
    const prev = document.getElementById('prev-' + id);
    if (prev) prev.innerHTML = `Ganar: <strong>S/${(amt * odds).toFixed(2)}</strong> &bull; @<strong style="color:var(--gold)">${odds.toFixed(2)}</strong>`;
  });

  // ── Quick amount buttons ─────────────────────────────
  document.querySelectorAll('.btn-quick').forEach(btn => {
    btn.addEventListener('click', () => {
      const optid = btn.dataset.optid;
      const add   = parseInt(btn.dataset.add);
      const input = document.querySelector(`.bet-input[data-optid="${optid}"]`);
      if (input) {
        input.value = Math.max(1, parseInt(input.value || 0) + add);
        input.dispatchEvent(new Event('input'));
      }
    });
  });

  // ── Lobby tabs ──────────────────────────────────────
  document.querySelectorAll('.bet-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      const tgt = btn.dataset.tab;
      document.querySelectorAll('.bet-tab').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.bet-tab-panel').forEach(p => p.hidden = true);
      btn.classList.add('active');
      document.getElementById(tgt)?.removeAttribute('hidden');
    });
  });

  // ── Animate accuracy bars ────────────────────────────
  document.querySelectorAll('.acc-bar-fill').forEach(el => {
    const w = el.dataset.width || '0';
    setTimeout(() => { el.style.width = w + '%'; }, 200);
  });

  // ── Animate poll bars ────────────────────────────────
  document.querySelectorAll('.poll-item').forEach(el => {
    const bar = el.dataset.bar || '0';
    setTimeout(() => { el.style.setProperty('--bar', bar + '%'); }, 300);
  });

});

/* ============================================================
   StakeFolclor — Hero JS v3
   Dark/Light + Drawer Tickets correcto + Parallax + Nav
   ============================================================ */

(function () {
  'use strict';

  const THEME_KEY = 'sf-theme';

  /* ── 1. Tema ──────────────────────────────────────────── */
  function applyTheme(t) {
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem(THEME_KEY, t);
    _updateToggleIcons(t);
  }

  function _updateToggleIcons(t) {
    document.querySelectorAll('.theme-toggle-btn').forEach(function (btn) {
      const icon = btn.querySelector('i');
      if (icon) {
        icon.className = t === 'dark' ? 'bi bi-moon-stars-fill' : 'bi bi-sun-fill';
      }
      btn.title = t === 'dark' ? 'Activar modo claro' : 'Activar modo oscuro';
    });
  }

  // Aplicar tema guardado ANTES del DOMContentLoaded
  (function () {
    var saved = localStorage.getItem(THEME_KEY);
    var preferred = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    var initial = saved || preferred;
    document.documentElement.setAttribute('data-theme', initial);
  })();

  // Exponer globalmente
  window.toggleTheme = function () {
    var cur = document.documentElement.getAttribute('data-theme') || 'dark';
    applyTheme(cur === 'dark' ? 'light' : 'dark');
  };

  /* ── 2. DOM listo ─────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {

    // Sincronizar iconos con tema actual
    _updateToggleIcons(document.documentElement.getAttribute('data-theme') || 'dark');

    /* ── 2a. Navbar scroll ────────────────────────────── */
    var nav = document.querySelector('.sf-nav');
    function onScroll() {
      if (!nav) return;
      nav.classList.toggle('hero-scrolled', window.scrollY > 55);
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    /* ── 2b. Parallax hero ───────────────────────────── */
    var heroBg = document.querySelector('.cf-hero-bg-img');
    if (heroBg) {
      window.addEventListener('scroll', function () {
        var y = window.scrollY;
        if (y < window.innerHeight * 1.2) {
          heroBg.style.transform = 'scale(1.04) translateY(' + (y * 0.16) + 'px)';
        }
      }, { passive: true });
    }

    /* ── 2c. TICKET DRAWER ───────────────────────────── */
    var drawer     = document.getElementById('ticket-drawer');
    var overlay    = document.getElementById('drawer-overlay');
    var fab        = document.getElementById('ticket-fab');
    var dClose     = document.getElementById('drawer-close');
    // Botón en navbar
    var navTickBtn = document.getElementById('nav-tickets-btn');

    function openDrawer() {
      if (!drawer) return;
      drawer.classList.add('open');
      if (overlay) {
        overlay.style.display = 'block';
        // forzar reflow antes de transición
        void overlay.offsetWidth;
        overlay.classList.add('show');
      }
      document.body.style.overflow = 'hidden';
    }

    function closeDrawer() {
      if (!drawer) return;
      drawer.classList.remove('open');
      if (overlay) {
        overlay.classList.remove('show');
        setTimeout(function () { overlay.style.display = 'none'; }, 320);
      }
      document.body.style.overflow = '';
    }

    if (fab)        fab.addEventListener('click', openDrawer);
    if (dClose)     dClose.addEventListener('click', closeDrawer);
    if (overlay)    overlay.addEventListener('click', closeDrawer);
    if (navTickBtn) navTickBtn.addEventListener('click', openDrawer);

    /* Drawer tabs */
    document.querySelectorAll('.drawer-tab').forEach(function (tab) {
      tab.addEventListener('click', function () {
        var target = tab.dataset.tab;
        document.querySelectorAll('.drawer-tab').forEach(function (t) {
          t.classList.remove('active');
        });
        document.querySelectorAll('.drawer-panel').forEach(function (p) {
          p.style.display = 'none';
        });
        tab.classList.add('active');
        var panel = document.getElementById(target);
        if (panel) panel.style.display = 'block';
      });
    });

    /* ── 2d. Auto-dismiss alerts ─────────────────────── */
    document.querySelectorAll('.sf-alert-auto').forEach(function (el) {
      setTimeout(function () {
        el.style.transition = 'opacity .3s, transform .3s';
        el.style.opacity = '0';
        el.style.transform = 'translateY(-6px)';
        setTimeout(function () { el.remove(); }, 330);
      }, 4500);
    });

    /* ── 2e. Nav active link ─────────────────────────── */
    var path = window.location.pathname;
    document.querySelectorAll('.nav-link-sf').forEach(function (a) {
      var href = a.getAttribute('href');
      if (!href) return;
      if (href === '/' && path === '/') a.classList.add('active');
      else if (href !== '/' && path.startsWith(href)) a.classList.add('active');
    });

    /* ── 2f. Bet quick amounts ───────────────────────── */
    document.querySelectorAll('.btn-quick').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id  = btn.dataset.optid;
        var add = parseInt(btn.dataset.add);
        var inp = document.querySelector('.bet-input[data-optid="' + id + '"]');
        if (inp) {
          inp.value = Math.max(1, parseInt(inp.value || 0) + add);
          inp.dispatchEvent(new Event('input'));
        }
      });
    });

    document.addEventListener('input', function (e) {
      if (!e.target.matches('.bet-input')) return;
      var id   = e.target.dataset.optid;
      var oddsEl = document.getElementById('odds-' + id);
      var odds = oddsEl ? parseFloat(oddsEl.textContent) : 1;
      var amt  = parseFloat(e.target.value) || 0;
      var prev = document.getElementById('prev-' + id);
      if (prev) {
        prev.innerHTML = 'Ganar: <strong>S/' + (amt * odds).toFixed(2) + '</strong> &bull; @<strong style="color:var(--gold)">' + odds.toFixed(2) + '</strong>';
      }
    });

    /* ── 2g. Lobby tabs ──────────────────────────────── */
    document.querySelectorAll('.bet-tab').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var tgt = btn.dataset.tab;
        document.querySelectorAll('.bet-tab').forEach(function (b) { b.classList.remove('active'); });
        document.querySelectorAll('.bet-tab-panel').forEach(function (p) { p.hidden = true; });
        btn.classList.add('active');
        var panel = document.getElementById(tgt);
        if (panel) panel.removeAttribute('hidden');
      });
    });

    /* ── 2h. Accuracy bars animadas ─────────────────── */
    setTimeout(function () {
      document.querySelectorAll('.pred-acc-bar-fill').forEach(function (el) {
        el.style.width = (el.dataset.width || '0') + '%';
      });
      document.querySelectorAll('.poll-item').forEach(function (el) {
        el.style.setProperty('--bar', (el.dataset.bar || '0') + '%');
      });
    }, 350);

    /* ── 2i. Stat counters ───────────────────────────── */
    function animateCount(el) {
      var target = parseInt(el.dataset.target || '0');
      if (!target) return;
      var dur  = 1800;
      var step = target / (dur / 16);
      var cur  = 0;
      var pfx  = el.dataset.prefix || '';
      var sfx  = el.dataset.suffix || '';
      var timer = setInterval(function () {
        cur = Math.min(cur + step, target);
        el.textContent = pfx + Math.floor(cur).toLocaleString() + sfx;
        if (cur >= target) clearInterval(timer);
      }, 16);
    }
    var cObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { animateCount(e.target); cObs.unobserve(e.target); }
      });
    }, { threshold: 0.5 });
    document.querySelectorAll('.stat-counter').forEach(function (el) { cObs.observe(el); });

  });
})();

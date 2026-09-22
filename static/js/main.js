/* UNISA AI Financial Aid Assistant — main.js */

/* ── Smooth-scroll for all sidebar anchor links ─────────── */
document.querySelectorAll('.sidebar-link[href^="#"]').forEach(link => {
  link.addEventListener('click', e => {
    const target = document.querySelector(link.getAttribute('href'));
    if (!target) return;
    e.preventDefault();
    const navH = parseInt(
      getComputedStyle(document.documentElement).getPropertyValue('--nav-h')
    ) || 62;
    window.scrollTo({ top: target.getBoundingClientRect().top + window.scrollY - navH - 12, behavior: 'smooth' });
  });
});

/* ── Active sidebar link tracking on scroll ─────────────── */
(function () {
  const links  = document.querySelectorAll('.sidebar-link[href^="#"]');
  if (!links.length) return;

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        links.forEach(l => l.classList.remove('active'));
        const active = document.querySelector(`.sidebar-link[href="#${entry.target.id}"]`);
        if (active) active.classList.add('active');
      }
    });
  }, { rootMargin: '-62px 0px -55% 0px', threshold: 0 });

  document.querySelectorAll('section[id], div[id]').forEach(el => observer.observe(el));
})();

/* ── Collapse long payment tables (> 5 rows on mobile) ──── */
(function () {
  const tbody = document.querySelector('#payments tbody');
  if (!tbody) return;
  const rows = Array.from(tbody.querySelectorAll('tr'));
  if (rows.length <= 5) return;

  rows.forEach((row, i) => { if (i >= 5) row.style.display = 'none'; });

  const btn = document.createElement('button');
  btn.textContent = `Show all ${rows.length} payments`;
  btn.setAttribute('type', 'button');
  btn.style.cssText = (
    'display:block; margin:.75rem auto 0; padding:.4rem 1rem;'
    + 'background:var(--unisa-red-light); color:var(--unisa-red);'
    + 'border:1px solid var(--unisa-red); border-radius:4px;'
    + 'font-size:.8rem; font-weight:700; cursor:pointer;'
  );
  btn.addEventListener('click', () => {
    rows.forEach(r => { r.style.display = ''; });
    btn.remove();
  });
  tbody.closest('.card').querySelector('.card-body-flush').appendChild(btn);
})();

/* ── Navbar transparency on scroll ──────────────────────── */
(function () {
  const nav = document.querySelector('.navbar');
  if (!nav) return;
  const update = () => {
    if (window.scrollY > 10) {
      nav.classList.add('navbar--scrolled');
    } else {
      nav.classList.remove('navbar--scrolled');
    }
  };
  window.addEventListener('scroll', update, { passive: true });
  update(); // run on load
})();

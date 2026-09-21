/* UNISA AI Financial Aid Assistant — Main JS */

/* ── Smooth-scroll for sidebar links ──────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (!target) return;
    e.preventDefault();
    const navH = parseInt(getComputedStyle(document.documentElement)
      .getPropertyValue('--nav-h')) || 64;
    const y = target.getBoundingClientRect().top + window.scrollY - navH - 16;
    window.scrollTo({ top: y, behavior: 'smooth' });
  });
});

/* ── Active sidebar link on scroll ───────────────────────── */
(function () {
  const links  = document.querySelectorAll('.sidebar-link[href^="#"]');
  const navH   = 80;

  if (!links.length) return;

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        links.forEach(l => l.classList.remove('active'));
        const active = document.querySelector(`.sidebar-link[href="#${id}"]`);
        if (active) active.classList.add('active');
      }
    });
  }, { rootMargin: `-${navH}px 0px -60% 0px`, threshold: 0 });

  document.querySelectorAll('[id]').forEach(el => observer.observe(el));
})();

/* ── Collapsible payment history rows (mobile) ────────────── */
(function () {
  const tableWrap = document.querySelector('#payments .table-wrap');
  if (!tableWrap) return;
  const rows = tableWrap.querySelectorAll('tbody tr');
  if (rows.length <= 5) return;

  // Hide rows beyond first 5
  rows.forEach((row, i) => { if (i >= 5) row.style.display = 'none'; });

  const btn = document.createElement('button');
  btn.textContent = `Show all ${rows.length} payments`;
  btn.style.cssText = 'display:block;margin:.75rem auto 0;padding:.4rem 1rem;'
    + 'background:var(--unisa-blue-light);color:var(--unisa-blue);border:1px solid var(--unisa-blue);'
    + 'border-radius:6px;font-size:.82rem;font-weight:600;cursor:pointer;';
  btn.addEventListener('click', () => {
    rows.forEach(row => { row.style.display = ''; });
    btn.remove();
  });
  tableWrap.after(btn);
})();

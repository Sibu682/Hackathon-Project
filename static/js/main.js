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


/* ═══════════════════════════════════════════════════════════
   AI AGENT STREAMING — Server-Sent Events client
   Connects to /api/agent/stream on dashboard load and renders
   the AI assessment progressively, word by word.
   ═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  // ── DOM references ────────────────────────────────────────
  const banner      = document.getElementById('ai-banner');
  const statusBar   = document.getElementById('ai-status-bar');
  const statusDot   = document.getElementById('ai-status-dot');
  const statusLabel = document.getElementById('ai-status-label');
  const heading     = document.getElementById('ai-banner-heading');
  const streamText  = document.getElementById('ai-stream-text');
  const sourceBar   = document.getElementById('ai-banner-source');
  const engineLabel = document.getElementById('ai-engine-label');

  // Only run on pages that have the streaming banner
  if (!banner || !streamText) return;

  // Read SSE URL from the <meta> tag injected by the template
  const streamUrl = (
    document.querySelector('meta[name="agent-stream-url"]') || {}
  ).content;
  const appVersion = (
    document.querySelector('meta[name="app-version"]') || {}
  ).content || '';

  if (!streamUrl) return;

  // ── State ─────────────────────────────────────────────────
  let tokenBuffer   = [];   // queued tokens waiting to be painted
  let paintPending  = false;
  let isComplete    = false;
  let hasCursor     = false;

  // ── Typing cursor helpers ─────────────────────────────────
  function addCursor() {
    if (hasCursor) return;
    hasCursor = true;
    const cursor = document.createElement('span');
    cursor.id        = 'ai-cursor';
    cursor.className = 'ai-cursor';
    cursor.setAttribute('aria-hidden', 'true');
    streamText.appendChild(cursor);
  }

  function removeCursor() {
    const cursor = document.getElementById('ai-cursor');
    if (cursor) cursor.remove();
    hasCursor = false;
  }

  // ── Progressive token painter ─────────────────────────────
  // Uses requestAnimationFrame to batch DOM writes so the browser
  // never blocks on individual insertions.
  function schedulePaint() {
    if (paintPending) return;
    paintPending = true;
    requestAnimationFrame(paintNextToken);
  }

  function paintNextToken() {
    paintPending = false;
    if (!tokenBuffer.length) return;

    const token = tokenBuffer.shift();

    // Remove cursor, append text node, re-add cursor
    removeCursor();
    streamText.appendChild(document.createTextNode(token));
    if (!isComplete) addCursor();

    // If more tokens are waiting, schedule the next frame
    if (tokenBuffer.length) {
      // Small artificial delay between tokens for the typing feel
      setTimeout(schedulePaint, 28);
    }
  }

  function enqueueToken(token) {
    tokenBuffer.push(token);
    schedulePaint();
  }

  // ── Status transitions ────────────────────────────────────
  function setStatus(state) {
    switch (state) {

      case 'analysing':
        statusDot.classList.add('ai-status-dot--pulse');
        statusLabel.textContent = 'AI Agent is analysing your data…';

        // Reveal the heading as soon as the agent starts writing
        heading.classList.remove('ai-banner-heading-hidden');
        heading.classList.add('ai-banner-heading-visible');
        addCursor();
        break;

      case 'complete':
        isComplete = true;
        statusDot.classList.remove('ai-status-dot--pulse');
        statusDot.classList.add('ai-status-dot--done');
        statusLabel.textContent = 'Analysis complete';

        // Wait for the token queue to drain before removing the cursor
        // and revealing the source line.
        const waitForDrain = setInterval(() => {
          if (tokenBuffer.length === 0) {
            clearInterval(waitForDrain);
            removeCursor();

            // Fade the status bar out, reveal source line
            statusBar.classList.add('ai-status-bar--done');
            if (sourceBar) {
              sourceBar.style.display = '';
              sourceBar.classList.add('ai-source-reveal');
            }
          }
        }, 60);
        break;

      case 'error':
        isComplete = true;
        removeCursor();
        statusDot.classList.remove('ai-status-dot--pulse');
        statusDot.classList.add('ai-status-dot--error');
        statusLabel.textContent = 'Analysis unavailable — please refresh';
        if (!streamText.textContent.trim()) {
          streamText.textContent =
            'We were unable to complete the AI assessment at this time. '
            + 'Your dashboard data is still accurate.';
        }
        break;
    }
  }

  // ── Handle the final structured result ───────────────────
  // Updates the engine label and applies any deferred UI changes
  // that depend on the full assessment (e.g. outstanding-balance
  // alerts that may not have rendered from the placeholder).
  function applyResult(result) {
    if (!result) return;

    // Update engine/source label
    if (engineLabel) {
      engineLabel.textContent =
        result.source === 'ai'
          ? 'Groq — ' + (appVersion || '')
          : 'Rule-based engine (no API key configured)';
    }

    // If there are potential_reasons and the reasons list is empty on
    // the page, populate it dynamically so it matches the streamed result.
    const reasonsList = document.querySelector('.reason-list');
    if (reasonsList && result.potential_reasons && result.potential_reasons.length) {
      // Only update if the list is currently empty (placeholder had none)
      if (!reasonsList.querySelector('li')) {
        result.potential_reasons.forEach(reason => {
          const li = document.createElement('li');
          li.textContent = reason;
          reasonsList.appendChild(li);
        });
      }
    }
  }

  // ── EventSource connection ────────────────────────────────
  const sse = new EventSource(streamUrl);

  sse.addEventListener('status', function (e) {
    setStatus(e.data.trim());
    if (e.data.trim() === 'complete' || e.data.trim() === 'error') {
      sse.close();
    }
  });

  sse.addEventListener('token', function (e) {
    try {
      const payload = JSON.parse(e.data);
      if (payload.token) enqueueToken(payload.token);
    } catch (_) {
      // malformed chunk — skip
    }
  });

  sse.addEventListener('result', function (e) {
    try {
      const result = JSON.parse(e.data);
      applyResult(result);
    } catch (_) {
      // non-critical — engine label stays as default
    }
  });

  sse.onerror = function () {
    sse.close();
    setStatus('error');
  };

})();


/* ═══════════════════════════════════════════════════════════
   FUNDING STREAM — Server-Sent Events client
   Connects to /api/funding/stream on dashboard load and builds
   bursary + alternative funding cards progressively.
   ═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  // ── Read SSE URL ──────────────────────────────────────────
  const fundingUrl = (
    document.querySelector('meta[name="funding-stream-url"]') || {}
  ).content;

  if (!fundingUrl) return;   // not on a dashboard page

  // ── DOM refs — bursaries section ─────────────────────────
  const bursaryStatusBar   = document.getElementById('bursary-status-bar');
  const bursaryStatusDot   = document.getElementById('bursary-status-dot');
  const bursaryStatusLabel = document.getElementById('bursary-status-label');
  const bursarySkeletons   = document.getElementById('bursary-skeletons');
  const bursaryList        = document.getElementById('bursary-list');
  const bursaryEmpty       = document.getElementById('bursary-empty');
  const bursaryCountBadge  = document.getElementById('bursary-count-badge');

  // ── DOM refs — alt-funding section ───────────────────────
  const altStatusBar       = document.getElementById('altfunding-status-bar');
  const altStatusDot       = document.getElementById('altfunding-status-dot');
  const altStatusLabel     = document.getElementById('altfunding-status-label');
  const altSkeletons       = document.getElementById('altfunding-skeletons');
  const altList            = document.getElementById('altfunding-list');
  const altEmpty           = document.getElementById('altfunding-empty');
  const altCountBadge      = document.getElementById('altfunding-count-badge');
  const altSummaryAlert    = document.getElementById('altfunding-summary-alert');
  const altSummaryTitle    = document.getElementById('altfunding-summary-title');

  // ── Helpers ───────────────────────────────────────────────

  function fmt(n) {
    // Format a number as a ZAR amount string e.g. 60000 → "60,000"
    return Number(n).toLocaleString('en-ZA');
  }

  function escHtml(str) {
    const d = document.createElement('div');
    d.appendChild(document.createTextNode(String(str || '')));
    return d.innerHTML;
  }

  /** Mark a status bar as done: stop pulse, show tick, fade out. */
  function markSectionDone(dot, label, text) {
    if (!dot) return;
    dot.classList.remove('funding-status-dot--pulse');
    dot.classList.add('funding-status-dot--done');
    if (label) label.textContent = text || 'Done';
    const bar = dot.closest('.funding-status-bar');
    if (bar) {
      setTimeout(() => bar.classList.add('funding-status-bar--done'), 600);
    }
  }

  /** Mark a status bar as errored. */
  function markSectionError(dot, label) {
    if (!dot) return;
    dot.classList.remove('funding-status-dot--pulse');
    dot.classList.add('funding-status-dot--error');
    if (label) label.textContent = 'Could not load — please refresh';
  }

  // ── Card builders ─────────────────────────────────────────

  /**
   * Build a full bursary card DOM element from SSE data.
   * Mirrors the markup in the old static bursaries.html Jinja loop.
   */
  function buildBursaryCard(b, rank) {
    const card = document.createElement('div');
    card.className = 'bursary-card funding-card-reveal';
    card.setAttribute('role', 'listitem');

    // Matched criteria chips
    const criteria = (b._matched_criteria || []);
    const chipsHtml = criteria.length
      ? `<div class="criteria-list" style="margin-top:.5rem;">
           ${criteria.map(c => `<span class="criteria-chip">✓ ${escHtml(c)}</span>`).join('')}
         </div>`
      : '';

    // Financial need badge
    const needBadge = b.financial_need_required
      ? `<span>💰 Financial need required</span>` : '';

    card.innerHTML = `
      <div class="bursary-card-header">
        <div class="bursary-rank" aria-label="Rank ${rank}">${rank}</div>
        <h3>${escHtml(b.name)}</h3>
        <span class="badge badge-success" style="font-size:.78rem;">
          R${fmt(b.amount)} / year
        </span>
      </div>
      <div class="bursary-card-body">
        <div class="bursary-meta">
          <span>🏢 ${escHtml(b.funder)}</span>
          <span>📅 Deadline: <strong>${escHtml(b.deadline)}</strong></span>
          <span>📖 ${escHtml((b.fields_of_study || []).join(' · '))}</span>
          <span>🎓 Min GPA: ${escHtml(b.min_gpa)}%</span>
          ${needBadge}
        </div>
        <p class="bursary-desc">${escHtml(b.description)}</p>
        ${criteria.length
          ? `<div style="margin-top:.5rem;">
               <p style="font-size:.7rem;font-weight:700;text-transform:uppercase;
                         letter-spacing:.07em;color:var(--text-muted);margin-bottom:.4rem;">
                 Why you qualify
               </p>
               ${chipsHtml}
             </div>`
          : ''}
        <a href="${escHtml(b.application_url)}" target="_blank" rel="noopener"
           class="btn-apply">Apply Now →</a>
      </div>`;

    return card;
  }

  /**
   * Build a full alternative-funding partner card DOM element.
   * Mirrors the markup in the old static alt_funding.html Jinja loop.
   */
  function buildPartnerCard(p) {
    const card = document.createElement('div');
    card.className = 'alt-card funding-card-reveal';
    card.setAttribute('role', 'listitem');

    const incomeHtml = p.income_threshold
      ? `<div class="alert alert-info"
              style="padding:.55rem .9rem;margin-bottom:.85rem;">
           <span class="alert-icon" style="font-size:.9rem;">💰</span>
           <div class="alert-body">
             <p>Income threshold: household income up to
                R${fmt(p.income_threshold)} per annum</p>
           </div>
         </div>` : '';

    const eligHtml = (p.eligibility || [])
      .map(req => `<li>${escHtml(req)}</li>`)
      .join('');

    card.innerHTML = `
      <div class="alt-card-header">
        <h3>${escHtml(p.name)}</h3>
        <span class="badge badge-info">${escHtml(p.type)}</span>
      </div>
      <div class="alt-card-body">
        <p class="alt-desc">${escHtml(p.description)}</p>
        ${incomeHtml}
        <p style="font-size:.72rem;font-weight:700;text-transform:uppercase;
                  letter-spacing:.07em;color:var(--text-muted);margin-bottom:.45rem;">
          Eligibility Requirements
        </p>
        <ul class="elig-list">${eligHtml}</ul>
        <div class="alt-meta">
          <span>📅 Deadline: <strong>${escHtml(p.deadline)}</strong></span>
          <span>✉ <a href="mailto:${escHtml(p.contact_email)}">${escHtml(p.contact_email)}</a></span>
        </div>
        <a href="${escHtml(p.application_url)}" target="_blank" rel="noopener"
           class="btn-alt-apply">Apply Now →</a>
      </div>`;

    return card;
  }

  // ── Section state ─────────────────────────────────────────
  let bursaryTotal = null;
  let altTotal     = null;

  // ── SSE event handlers ────────────────────────────────────

  function handleStatus(status) {
    switch (status) {

      case 'bursaries_start':
        // Skeletons already visible — nothing extra needed
        break;

      case 'altfunding_start':
        // Bursary section is fully loaded — finalise it
        finaliseBursarySection();
        break;

      case 'complete':
        finaliseAltSection();
        break;

      case 'error':
        markSectionError(bursaryStatusDot, bursaryStatusLabel);
        markSectionError(altStatusDot, altStatusLabel);
        if (bursarySkeletons) bursarySkeletons.style.display = 'none';
        if (altSkeletons)     altSkeletons.style.display = 'none';
        break;
    }
  }

  function handleCount(payload) {
    if (payload.section === 'bursaries') {
      bursaryTotal = payload.total;
      // Update count badge immediately
      if (bursaryCountBadge) {
        const n = payload.total;
        bursaryCountBadge.innerHTML =
          `<span class="badge badge-success">${n} match${n !== 1 ? 'es' : ''}</span>`;
      }
      if (bursaryStatusLabel) {
        bursaryStatusLabel.textContent =
          payload.total > 0
            ? `Found ${payload.total} eligible bursary match${payload.total !== 1 ? 'es' : ''}…`
            : 'Checking bursary catalogue…';
      }
    }

    if (payload.section === 'altfunding') {
      altTotal = payload.total;
      if (altCountBadge) {
        const n = payload.total;
        altCountBadge.innerHTML =
          `<span class="badge badge-neutral">${n} scheme${n !== 1 ? 's' : ''}</span>`;
      }
      // Reveal the summary alert now that we know the count
      if (altSummaryAlert && altSummaryTitle && payload.total > 0) {
        const n = payload.total;
        altSummaryTitle.textContent =
          `${n} scheme${n !== 1 ? 's' : ''} matched to your profile`;
        altSummaryAlert.style.display = '';
        altSummaryAlert.classList.add('funding-card-reveal');
      }
      if (altStatusLabel) {
        altStatusLabel.textContent =
          payload.total > 0
            ? `Found ${payload.total} alternative funding scheme${payload.total !== 1 ? 's' : ''}…`
            : 'Checking alternative funding options…';
      }
    }
  }

  function handleBursary(payload) {
    if (!bursaryList) return;

    // Remove skeletons on the first real card
    if (payload.index === 0 && bursarySkeletons) {
      bursarySkeletons.classList.add('skeleton-fade-out');
      setTimeout(() => {
        bursarySkeletons.style.display = 'none';
        bursarySkeletons.classList.remove('skeleton-fade-out');
      }, 300);
    }

    const card = buildBursaryCard(payload.data, payload.index + 1);
    // Stagger the animation delay so cards cascade in
    card.style.animationDelay = `${payload.index * 80}ms`;
    bursaryList.appendChild(card);
  }

  function handlePartner(payload) {
    if (!altList) return;

    // Remove alt skeletons on first real card
    if (payload.index === 0 && altSkeletons) {
      altSkeletons.classList.add('skeleton-fade-out');
      setTimeout(() => {
        altSkeletons.style.display = 'none';
        altSkeletons.classList.remove('skeleton-fade-out');
      }, 300);
    }

    const card = buildPartnerCard(payload.data);
    card.style.animationDelay = `${payload.index * 80}ms`;
    altList.appendChild(card);
  }

  // ── Section finalisation ──────────────────────────────────

  function finaliseBursarySection() {
    if (bursarySkeletons) bursarySkeletons.style.display = 'none';

    if (bursaryTotal === 0) {
      if (bursaryEmpty) bursaryEmpty.style.display = '';
    }

    const label = bursaryTotal === 0
      ? 'No bursary matches found'
      : `${bursaryTotal} bursary match${bursaryTotal !== 1 ? 'es' : ''} loaded`;

    markSectionDone(bursaryStatusDot, bursaryStatusLabel, label);
  }

  function finaliseAltSection() {
    if (altSkeletons) altSkeletons.style.display = 'none';

    if (altTotal === 0) {
      if (altSummaryAlert) altSummaryAlert.style.display = 'none';
      if (altEmpty)        altEmpty.style.display = '';
    }

    const label = altTotal === 0
      ? 'No alternative schemes matched'
      : `${altTotal} scheme${altTotal !== 1 ? 's' : ''} loaded`;

    markSectionDone(altStatusDot, altStatusLabel, label);
  }

  // ── Open SSE connection ───────────────────────────────────
  const fundingSSE = new EventSource(fundingUrl);

  fundingSSE.addEventListener('status', function (e) {
    handleStatus(e.data.trim());
    if (e.data.trim() === 'complete' || e.data.trim() === 'error') {
      fundingSSE.close();
    }
  });

  fundingSSE.addEventListener('count', function (e) {
    try { handleCount(JSON.parse(e.data)); } catch (_) {}
  });

  fundingSSE.addEventListener('bursary', function (e) {
    try { handleBursary(JSON.parse(e.data)); } catch (_) {}
  });

  fundingSSE.addEventListener('partner', function (e) {
    try { handlePartner(JSON.parse(e.data)); } catch (_) {}
  });

  fundingSSE.onerror = function () {
    fundingSSE.close();
    handleStatus('error');
  };

})();

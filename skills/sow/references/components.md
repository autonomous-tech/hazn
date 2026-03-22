# Component Library — Copy-Paste HTML

All components assume the base CSS from `templates/doc-base.html` is present.

---

## #cover

```html
<div class="page">
  <div class="page-header">
    <span class="logo-mark">Autonomous</span>
    <span class="doc-label">Statement of Work</span>
  </div>
  <div class="cover-inner">
    <div class="cover-logos">
      <!-- OPTION A: SVG inline -->
      <div class="client-logo-wrap">
        {CLIENT_SVG}
      </div>
      <!-- OPTION B: PNG/JPG base64 -->
      <div class="client-logo-wrap">
        <img src="data:image/png;base64,{B64}" height="28" style="display:block;">
      </div>
      <!-- OPTION C: placeholder -->
      <div class="client-logo-wrap">
        <div class="logo-placeholder">
          <span class="logo-placeholder-icon">⬡</span>
          <span class="logo-placeholder-text">{CLIENT_NAME}</span>
        </div>
      </div>
      <span class="cover-logo-x">×</span>
      <div class="autonomous-logo-wrap">
        <span class="autonomous-wordmark">Autonomous</span>
      </div>
    </div>
    <h1 class="cover-headline">{HEADLINE}</h1>
    <p class="cover-sub">{SUBTITLE}</p>
    <div class="cover-price">
      <span class="cover-price-label">Your Investment</span>
      <span class="cover-price-amount">${AMOUNT} USD</span>
    </div>
    <div class="cover-meta">
      <div class="meta-item">
        <span class="meta-label">Prepared for</span>
        <span class="meta-value">{CLIENT_NAME}</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Prepared by</span>
        <span class="meta-value">Autonomous Technology Inc.</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Date</span>
        <span class="meta-value">{DATE}</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Valid for</span>
        <span class="meta-value">30 Days</span>
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span class="footer-text">hello@autonomoustech.ca</span>
    <span class="footer-text">autonomoustech.ca</span>
  </div>
</div>
```

---

## #scope

```html
<div class="page page-white">
  <div class="page-header">
    <span class="logo-mark">Autonomous</span>
    <span class="doc-label">Your Scope</span>
  </div>
  <div class="page-body">
    <span class="eyebrow">Your Engagement</span>
    <h2 class="section-title">What's included in your {PROJECT_TYPE}</h2>
    <p class="body-text" style="margin-bottom:0.26in; max-width:6.2in;">{OVERVIEW_PARAGRAPH}</p>
    <span class="eyebrow" style="margin-bottom:0.13in;">Your Scope of Work</span>
    <ul class="scope-list">
      <li class="scope-item">
        <span class="scope-num">01</span>
        <div>
          <div class="scope-title">{SCOPE_TITLE}</div>
          <div class="scope-desc">{SCOPE_DESC}</div>
        </div>
      </li>
      <!-- repeat for each scope item -->
    </ul>
  </div>
  <div class="page-footer">
    <span class="footer-text">{CLIENT_NAME} — {DOC_TITLE}</span>
    <span class="footer-text">{PAGE} of {TOTAL}</span>
  </div>
</div>
```

---

## #cards (deliverables)

```html
<div class="cards-grid" style="margin-bottom:0.28in;">
  <div class="card">
    <div class="card-title">{DELIVERABLE_NAME}</div>
    <div class="card-desc">{DELIVERABLE_DESC}</div>
  </div>
  <!-- repeat — max 6 cards per page -->
</div>
```

---

## #timeline (phase strip)

```html
<span class="eyebrow" style="margin-bottom:0.13in;">Your Timeline</span>
<div class="timeline-strip">
  <div class="tl-phase">
    <div class="tl-label">Phase 1</div>
    <div class="tl-title">{PHASE_NAME}</div>
    <div class="tl-desc">{WEEK_RANGE} — {WHAT_HAPPENS}</div>
  </div>
  <!-- repeat for each phase — max 4 phases -->
</div>
```

---

## #milestones (dated list — optional)

```html
<div class="milestones">
  <div class="milestone">
    <div class="milestone-left">
      <div class="milestone-dot"></div>
      <div class="milestone-line"></div>
    </div>
    <div class="milestone-content">
      <div class="milestone-date">{WEEK} · {DATE}</div>
      <div class="milestone-title">{MILESTONE_TITLE}</div>
      <div class="milestone-desc">{MILESTONE_DESC}</div>
    </div>
  </div>
  <!-- last milestone: no .milestone-line inside .milestone-left -->
</div>
```

---

## #investment (table)

For monthly/retainer engagements:
- Change `${AMOUNT} USD — flat fee` → `${AMOUNT}/mo USD` or `${SETUP} + ${MONTHLY}/mo`
- Change `Your Total` row → `Monthly Total` or `Your Commitment`
- Add a sub-row above total if needed: `× {N} months = ${TOTAL}` in muted style



```html
<span class="eyebrow">Your Investment</span>
<h2 class="section-title" style="margin-bottom:0.18in;">${AMOUNT} USD — flat fee</h2>
<table class="inv-table" style="margin-bottom:0.26in;">
  <thead>
    <tr>
      <th>What you're getting</th>
      <th>Description</th>
      <th style="text-align:right;">Amount</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>{ITEM_NAME}</td>
      <td class="muted">{ITEM_DESC}</td>
      <td class="right">Included</td>
    </tr>
    <!-- repeat for each line item -->
    <tr class="total">
      <td>Your Total</td>
      <td></td>
      <td class="right">${AMOUNT} USD</td>
    </tr>
  </tbody>
</table>
```

---

## #payment (payment schedule bar)

Three variants — pick the right one based on engagement type.

### Variant A — Flat fee (one-time, 50/50 split)
```html
<span class="eyebrow" style="margin-bottom:0.14in; display:block;">Your Payment Schedule</span>
<div class="payment-bar">
  <div class="pay-seg active">
    <div class="pay-seg-label">Deposit · Due on signing</div>
    <div class="pay-seg-amount">${DEPOSIT}</div>
    <div class="pay-seg-when">Paid before work begins</div>
  </div>
  <div class="pay-seg">
    <div class="pay-seg-label">Final Payment · Due on delivery</div>
    <div class="pay-seg-amount">${FINAL}</div>
    <div class="pay-seg-when">Due on completion &amp; handoff</div>
  </div>
</div>
```

### Variant B — Monthly retainer (ongoing, no end date)
```html
<span class="eyebrow" style="margin-bottom:0.14in; display:block;">Your Payment Schedule</span>
<div class="payment-bar">
  <div class="pay-seg active">
    <div class="pay-seg-label">Monthly Retainer · Billed {BILLING_DAY}</div>
    <div class="pay-seg-amount">${AMOUNT}<span style="font-family:'DM Sans',sans-serif; font-size:11pt; font-weight:400; color:rgba(255,255,255,0.5); margin-left:4px;">/mo</span></div>
    <div class="pay-seg-when">First payment due on signing · Ongoing until cancelled</div>
  </div>
  <div class="pay-seg">
    <div class="pay-seg-label">Cancellation</div>
    <div class="pay-seg-amount" style="font-size:14pt;">{NOTICE} days</div>
    <div class="pay-seg-when">Written notice required to cancel</div>
  </div>
</div>
```

### Variant C — Hybrid (setup fee + monthly retainer)
```html
<span class="eyebrow" style="margin-bottom:0.14in; display:block;">Your Payment Schedule</span>
<div class="payment-bar">
  <div class="pay-seg active">
    <div class="pay-seg-label">Setup Fee · Due on signing</div>
    <div class="pay-seg-amount">${SETUP}</div>
    <div class="pay-seg-when">One-time · Paid before work begins</div>
  </div>
  <div class="pay-seg">
    <div class="pay-seg-label">Monthly Retainer · From {START_DATE}</div>
    <div class="pay-seg-amount">${MONTHLY}<span style="font-family:'DM Sans',sans-serif; font-size:11pt; font-weight:400; color:var(--caption); margin-left:4px;">/mo</span></div>
    <div class="pay-seg-when">Billed {BILLING_DAY} each month · {NOTICE}-day cancellation notice</div>
  </div>
</div>
```

### Variant D — Fixed term (monthly × N months)
```html
<span class="eyebrow" style="margin-bottom:0.14in; display:block;">Your Payment Schedule</span>
<div class="payment-bar">
  <div class="pay-seg active">
    <div class="pay-seg-label">Monthly · {N} month commitment</div>
    <div class="pay-seg-amount">${MONTHLY}<span style="font-family:'DM Sans',sans-serif; font-size:11pt; font-weight:400; color:rgba(255,255,255,0.5); margin-left:4px;">/mo</span></div>
    <div class="pay-seg-when">First payment due on signing · Then monthly on the same date</div>
  </div>
  <div class="pay-seg">
    <div class="pay-seg-label">Total Commitment</div>
    <div class="pay-seg-amount" style="font-size:18pt;">${TOTAL}</div>
    <div class="pay-seg-when">{N} payments of ${MONTHLY} over {N} months</div>
  </div>
</div>
```

Note: active `.pay-seg` (dark/midnight) = what they pay now or the primary amount. Light segment = secondary info.

---

## #terms (terms grid)

```html
<span class="eyebrow" style="margin-bottom:0.13in; display:block;">Terms &amp; Conditions</span>
<div class="terms-grid">
  <div class="term">
    <span class="term-label">Intellectual Property</span>
    <p class="term-text">Everything built becomes yours upon receipt of final payment. Full access handed off — no strings attached.</p>
  </div>
  <div class="term">
    <span class="term-label">Out of Scope</span>
    <p class="term-text">Any work beyond the defined scope requires a separate written agreement before commencement.</p>
  </div>
  <div class="term">
    <span class="term-label">Changes &amp; Revisions</span>
    <p class="term-text">Changes to agreed deliverables after commencement may be subject to additional fees at $150/hr USD.</p>
  </div>
  <div class="term">
    <span class="term-label">Validity</span>
    <p class="term-text">This agreement is valid for 30 days from the date on the cover. Pricing subject to change after expiry.</p>
  </div>
</div>
```

---

## #stats (stats bar — optional)

```html
<div class="stats-bar">
  <div class="stat">
    <div class="stat-value">{VALUE}</div>
    <div class="stat-label">{LABEL}</div>
  </div>
  <!-- repeat — max 4 stats -->
</div>
```

---

## #quote (quote block — optional)

```html
<div class="quote-block">
  <span class="quote-mark">"</span>
  <p class="quote-text">{QUOTE_TEXT}</p>
  <p class="quote-attribution">— {NAME}, {TITLE} · {COMPANY}</p>
</div>
```

---

## #twocol (two-column text — optional)

```html
<div class="two-col">
  <div>
    <div class="col-heading">{HEADING_LEFT}</div>
    <p class="col-text">{TEXT_LEFT}</p>
  </div>
  <div>
    <div class="col-heading">{HEADING_RIGHT}</div>
    <p class="col-text">{TEXT_RIGHT}</p>
  </div>
</div>
```

---

## #cta (CTA block)

```html
<div style="background:var(--midnight); border-radius:14px; padding:0.3in 0.38in; margin-bottom:0.3in;">
  <span class="eyebrow" style="color:var(--vermillion);">Ready to get started?</span>
  <h2 style="font-family:'Fraunces',serif; font-size:22pt; font-weight:400; letter-spacing:-0.03em; color:var(--parchment-light); margin-top:0.08in; margin-bottom:0.1in; line-height:1.15;">Sign below and your project kicks off</h2>
  <p style="font-size:9pt; color:rgba(255,255,255,0.4); line-height:1.65;">Return this signed agreement with your deposit and we'll kick off within 1–2 business days. Questions? hello@autonomoustech.ca</p>
</div>
```

---

## #signatures

```html
<hr class="rule">
<span class="eyebrow" style="margin-bottom:0.2in; display:block;">Signatures</span>
<div class="sig-row">
  <div class="sig-block">
    <span class="sig-party">{CLIENT_NAME} — Client</span>
    <div class="sig-line"></div>
    <span class="sig-name">Authorised Signatory</span>
    <span class="sig-date">Date: ___________________________</span>
  </div>
  <div class="sig-block">
    <span class="sig-party">Autonomous Technology Inc.</span>
    <div class="sig-line"></div>
    <span class="sig-name">Rizwan Qaiser</span>
    <span class="sig-date">Date: ___________________________</span>
  </div>
</div>
```
**Rule:** Client always on LEFT. Autonomous always on RIGHT.

---

## #badges (status badges)

```html
<span class="badge vermillion">In Progress</span>
<span class="badge sage">Delivered</span>
<span class="badge gold">Pending Review</span>
<span class="badge indigo">Scheduled</span>
<span class="badge">Draft</span>
```

---

## #gantt (horizontal Gantt timeline)

Use for multi-phase projects where phases overlap. Shows parallel work as a selling point.
Place on the scope page or investment page. Fits in `.page-body` (7.3in usable width).

**CSS to add to `<style>` block:**

```css
/* ── Gantt timeline ── */
.gantt-wrap { background: var(--parchment-light); border: 1px solid var(--parchment-dark); border-radius: 14px; padding: 0.28in 0.32in; }
.gantt-ruler { display: grid; grid-template-columns: 130px 1fr; margin-bottom: 5px; }
.gantt-weeks { display: flex; }
.gantt-week-tick { flex: 1; font-family: 'JetBrains Mono', monospace; font-size: 5.5pt; color: var(--caption); text-align: center; border-left: 1px solid var(--parchment-dark); padding-bottom: 5px; }
.gantt-week-tick:last-child { border-right: 1px solid var(--parchment-dark); }
.gantt-body { display: flex; flex-direction: column; gap: 6px; }
.gantt-row { display: grid; grid-template-columns: 130px 1fr; align-items: center; min-height: 36px; }
.gantt-phase-label { display: flex; flex-direction: column; gap: 2px; padding-right: 12px; }
.gantt-phase-num { font-family: 'JetBrains Mono', monospace; font-size: 5.5pt; text-transform: uppercase; letter-spacing: 0.1em; color: var(--vermillion); }
.gantt-phase-name { font-size: 7.5pt; font-weight: 600; color: var(--ink); line-height: 1.3; }
.gantt-track { position: relative; height: 36px; }
.gantt-track::before { content: ''; position: absolute; inset: 0; background-image: repeating-linear-gradient(to right, var(--parchment-dark) 0px, var(--parchment-dark) 1px, transparent 1px, transparent calc(100% / {TOTAL_WEEKS})); background-size: calc(100% / {TOTAL_WEEKS}) 100%; pointer-events: none; }
.gantt-bar { position: absolute; top: 5px; height: 26px; border-radius: 6px; display: flex; align-items: center; padding: 0 9px; }
.gantt-bar-label { font-family: 'JetBrains Mono', monospace; font-size: 6pt; font-weight: 500; white-space: nowrap; color: rgba(255,255,255,0.85); }
.gantt-overlap { position: absolute; top: 5px; height: 26px; background: rgba(232,81,61,0.18); border-left: 2px solid var(--vermillion); border-right: 2px solid var(--vermillion); pointer-events: none; }
.gantt-footer { margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--parchment-dark); display: flex; align-items: center; gap: 18px; }
.gantt-legend-item { display: flex; align-items: center; gap: 5px; font-size: 7pt; color: var(--caption); }
.gantt-legend-swatch { width: 14px; height: 9px; border-radius: 3px; }
.gantt-legend-overlap { width: 14px; height: 9px; background: rgba(232,81,61,0.18); border-left: 2px solid var(--vermillion); border-right: 2px solid var(--vermillion); }
```

**HTML template (14-week, 5-phase example):**

Position math: each week = `100% / TOTAL_WEEKS`. For 14 weeks, 1 week = 7.14%.
- `left` = `(start_week - 1) / total_weeks * 100%`
- `width` = `(end_week - start_week + 1) / total_weeks * 100%`
- Overlap zone: shared weeks between consecutive phases — same left/width as the overlapping segment.

Bar colours (use in order, last phase always vermillion):
- Phase 1: `#0D0D1F` (midnight)
- Phase 2: `#1a1a3a`
- Phase 3: `#272750`
- Phase 4: `#1f1f42`
- Phase 5+: `var(--vermillion)`

```html
<div class="gantt-wrap">
  <span class="eyebrow" style="margin-bottom:5px;">Your Timeline</span>
  <h3 style="font-family:'Fraunces',serif; font-size:14pt; font-weight:400; letter-spacing:-0.03em; color:var(--ink); margin-bottom:20px;">{TOTAL_WEEKS} weeks, phases overlap by design</h3>

  <!-- Week ruler -->
  <div class="gantt-ruler">
    <div></div>
    <div class="gantt-weeks">
      <div class="gantt-week-tick">1</div>
      <div class="gantt-week-tick">2</div>
      <!-- repeat for each week -->
      <div class="gantt-week-tick">{N}</div>
    </div>
  </div>

  <div class="gantt-body">
    <!-- Repeat .gantt-row for each phase -->
    <div class="gantt-row">
      <div class="gantt-phase-label">
        <span class="gantt-phase-num">Phase 1</span>
        <span class="gantt-phase-name">{PHASE_NAME}</span>
      </div>
      <div class="gantt-track">
        <!-- Optional overlap zone (omit for first phase) -->
        <div class="gantt-overlap" style="left:{OVERLAP_LEFT}%; width:{OVERLAP_WIDTH}%;"></div>
        <!-- Phase bar -->
        <div class="gantt-bar" style="background:{BAR_COLOR}; left:{LEFT}%; width:{WIDTH}%;">
          <span class="gantt-bar-label">Wks {START}–{END}</span>
        </div>
      </div>
    </div>
  </div>

  <div class="gantt-footer">
    <div class="gantt-legend-item">
      <div class="gantt-legend-swatch" style="background:#0D0D1F;"></div>
      <span>Active phase</span>
    </div>
    <div class="gantt-legend-item">
      <div class="gantt-legend-overlap"></div>
      <span>Phases overlap — parallel work in progress</span>
    </div>
    <div style="margin-left:auto; font-family:'JetBrains Mono',monospace; font-size:6pt; color:var(--caption);">{FOOTER_NOTE}</div>
  </div>
</div>
```

**Container One example values (14 weeks, 5 phases):**

| Phase | Start | End | left% | width% | Overlap left% | Overlap width% |
|---|---|---|---|---|---|---|
| 1 — Foundation | 1 | 3 | 0% | 21.4% | — | — |
| 2 — Pricing Sync | 3 | 7 | 14.3% | 35.7% | 14.3% | 7.1% |
| 3 — Checkout API | 6 | 9 | 35.7% | 28.6% | 35.7% | 14.3% |
| 4 — Orders + CRM | 8 | 11 | 50% | 28.6% | 50% | 14.3% |
| 5 — Cutover | 11 | 14 | 71.4% | 28.6% | 71.4% | 7.1% |

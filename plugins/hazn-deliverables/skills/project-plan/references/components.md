# Project Plan — Component Library

All components assume the full CSS from the project plan base is present (see the Jurist AI project plan HTML as the canonical reference at `~/autonomous-proposals/proposals/jurist-ai-project-plan.html`).

---

## #cover

```html
<div class="page">
  <div class="page-header">
    <span class="logo-mark">Autonomous</span>
    <span class="doc-label">Project Plan</span>
  </div>
  <div class="cover-body">
    <div class="cover-logos">
      <!-- OPTION A: SVG inline -->
      <div class="client-logo-wrap">{CLIENT_SVG}</div>
      <!-- OPTION B: PNG base64 -->
      <div class="client-logo-wrap"><img src="data:image/png;base64,{B64}" height="28" style="display:block;"></div>
      <!-- OPTION C: placeholder -->
      <div class="client-logo-wrap">
        <div class="logo-placeholder">
          <span class="logo-placeholder-icon">⬡</span>
          <span class="logo-placeholder-text">{CLIENT_NAME}</span>
        </div>
      </div>
      <span class="cover-logo-x">×</span>
      <div class="autonomous-logo-wrap"><span class="autonomous-wordmark">Autonomous</span></div>
    </div>

    <h1 class="cover-headline">{HEADLINE_LINE1}<br>{HEADLINE_LINE2}<br>{HEADLINE_LINE3}</h1>
    <p class="cover-subtitle">{TECH_STACK_OR_SCOPE_SUMMARY}</p>

    <!-- PHASE PILLS — one per phase -->
    <div class="cover-phase-strip">
      {PHASE_PILLS}
    </div>

    <div class="cover-meta">
      <div class="cover-meta-item">
        <span class="cover-meta-label">Prepared for</span>
        <span class="cover-meta-value">{CLIENT_NAME} — {CONTACT_NAME}, {CONTACT_TITLE}</span>
      </div>
      <div class="cover-meta-item">
        <span class="cover-meta-label">Prepared by</span>
        <span class="cover-meta-value">Rizwan Qaiser — Autonomous</span>
      </div>
      <div class="cover-meta-item">
        <span class="cover-meta-label">Kickoff</span>
        <span class="cover-meta-value">{KICKOFF_DATE}</span>
      </div>
      <div class="cover-meta-item">
        <span class="cover-meta-label">Target Completion</span>
        <span class="cover-meta-value">{COMPLETION_DATE}</span>
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

## #phase-pills

```html
<div class="cover-phase-pill">
  <span class="cover-phase-pill-label">Phase {N}</span>
  <span class="cover-phase-pill-title">{PHASE_NAME}</span>
  <span class="cover-phase-pill-sub">{WEEK_RANGE} — {SHORT_DESCRIPTION}</span>
</div>
```

Max ~4 pills per cover. If 5+ phases, use shorter sub-labels.

---

## #phase-page

```html
<div class="page page-white">
  <div class="page-header">
    <span class="logo-mark">Autonomous</span>
    <span class="doc-label">Phase {N} — {PHASE_NAME}</span>
  </div>
  <div class="page-body">
    <span class="eyebrow">{WEEK_RANGE}</span>
    <h2 class="section-title">{PHASE_FULL_TITLE}</h2>

    <!-- PHASE HEADER BAR -->
    <div class="phase-header">
      <div class="phase-header-left">
        <span class="phase-tag">Phase {N}</span>
        <span class="phase-name">{PHASE_NAME}</span>
      </div>
      <span class="phase-timeline">{WEEK_RANGE} · {DATE_RANGE}</span>
    </div>

    <!-- TASK LIST -->
    <div class="task-list">
      {TASK_ITEMS}
    </div>

  </div>
  <div class="page-footer">
    <span class="footer-text">{CLIENT_NAME} — {DOC_TITLE}</span>
    <span class="footer-text">{PAGE} of {TOTAL}</span>
  </div>
</div>
```

Alternate pages between `.page` (parchment) and `.page page-white` (lighter parchment) for visual rhythm.

---

## #task-item

Standard task — no badge:

```html
<div class="task-item">
  <div class="task-checkbox"></div>
  <div class="task-content">
    <div class="task-title">{TASK_TITLE}</div>
    <div class="task-desc">{TASK_DESCRIPTION}</div>
  </div>
</div>
```

---

## #task-fix

Task with audit fix badge (vermillion left border + badge):

```html
<div class="task-item fix">
  <div class="task-checkbox"></div>
  <div class="task-content">
    <div class="task-title">Fix: {TASK_TITLE}</div>
    <div class="task-desc">{TASK_DESCRIPTION}</div>
  </div>
  <span class="fix-badge">{BADGE_LABEL}</span>
</div>
```

Badge label options: `Fix`, `Critical`, `Bug`, `SEO`, `Attribution`, `Performance`

---

## #task-green-badge

Task with sage green badge (source of truth, impact tracking, day 1 priority):

```html
<div class="task-item">
  <div class="task-checkbox"></div>
  <div class="task-content">
    <div class="task-title">{TASK_TITLE}</div>
    <div class="task-desc">{TASK_DESCRIPTION}</div>
  </div>
  <span class="posthog-badge">{BADGE_LABEL}</span>
</div>
```

Badge label options: `Source of Truth`, `Impact Tracking`, `Day 1`, `Baseline`

---

## #notes-block

Midnight callout — goes at the bottom of the last task list on a phase page:

```html
<div class="notes-block">
  <span class="notes-eyebrow">{EYEBROW_LABEL}</span>
  <p class="notes-headline" style="font-size:13pt;">{HEADLINE}</p>
  <p class="notes-text">{BODY_TEXT}</p>
</div>
```

Use to:
- Reinforce the consulting narrative ("The baseline is already locked. Now we move.")
- Set expectations for the next phase
- Remind the client why the phase matters

---

## Logo Placeholder (when no logo available)

```html
<div class="logo-placeholder">
  <span class="logo-placeholder-icon">⬡</span>
  <span class="logo-placeholder-text">{CLIENT_NAME}</span>
</div>
```

CSS needed (add to `<style>`):
```css
.logo-placeholder {
  display: flex;
  align-items: center;
  gap: 8px;
}
.logo-placeholder-icon {
  font-size: 18px;
  color: var(--caption);
}
.logo-placeholder-text {
  font-family: 'Fraunces', serif;
  font-size: 12pt;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.02em;
}
```

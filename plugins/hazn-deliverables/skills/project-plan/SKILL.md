---
name: project-plan
description: Generate a branded Project Plan PDF for Autonomous Technology Inc. engagements. Use when a client project is kicking off and needs a structured phase-by-phase plan delivered as a polished PDF. Trigger on any mention of "project plan", "engagement plan", "kickoff doc", "phase plan", or when building a structured deliverable that outlines phases, tasks, timelines, and consulting approach. Uses the same Editorial Warmth v2 brand as the SoW — Fraunces + DM Sans + JetBrains Mono, parchment/midnight palette.
---

# Project Plan Generator

Generates a polished, print-ready Project Plan PDF using the Autonomous Editorial Warmth v2 design system. Companion to the SoW skill — the SoW defines the *what*, the Project Plan defines the *how we execute*.

## Core Principles

- **Phases are the structure.** Every project plan is organized into phases. Each phase gets its own page.
- **Tasks are checkboxes.** Every deliverable or action item is a task card with a checkbox, title, and description.
- **Baseline first.** If the engagement involves measuring impact (e.g. consulting, CRO), the baseline lock task goes at the top of Phase 1 — before any changes are made.
- **Notes blocks close phases.** Use midnight dark blocks at the bottom of phase pages to reinforce the consulting narrative.
- **Badges signal context.** Use `fix-badge` (vermillion) for audit/bug fixes, `posthog-badge` (sage green) for impact/source-of-truth markers, `day1-badge` for time-critical first tasks.

---

## Interview — Ask Everything in One Message

If not already provided, ask in a single message:

```
1. Client name + their point of contact (name, title)?
2. Engagement type? (e.g. Analytics Implementation, Website Build, SEO, etc.)
3. Project headline for the cover? (e.g. "Analytics Implementation Project Plan")
4. Cover subtitle — the tech stack or scope summary? (e.g. "GTM · GA4 · PostHog · CRO")
5. How many phases? List them with:
   - Phase name
   - Timeline (e.g. "Week 1", "Weeks 1–2", "Weeks 3–4")
   - Tasks for each phase (bullet points fine — I'll expand them)
6. Any tasks that are audit fixes (will get vermillion Fix badge)?
7. Any tasks that are impact/baseline tracking (will get green badge)?
8. Kickoff date?
9. Target completion date?
10. Client logo — choose one:
    a) Their website URL (I'll fetch it automatically)
    b) Upload/paste a logo file
    c) Skip — use text placeholder
```

---

## Workflow

### Step 1 — Interview

### Step 2 — Fetch Logo

Same as SoW skill. Use `~/autonomous-proposals/scripts/fetch-logo.js <url>`. See `sow/references/logo-fetch.md` for details.

Save to `~/hazn/logos/{client-slug}.svg` or `.png`.

### Step 3 — Generate HTML

Output file:
```
~/autonomous-proposals/proposals/{client-slug}-project-plan.html
```

Page structure — one page per phase:

| Page | Content |
|------|---------|
| 1 | Cover — logos, headline, subtitle, phase pills, meta bar |
| 2 | Phase 1 — phase header + task list |
| 3+ | Each additional phase — same structure |
| Last | Final phase — task list + notes block |

**Phase page rules:**
- Max ~7–8 tasks per page. If more, split into two pages.
- Every phase page has: eyebrow (week), section-title, phase-header (midnight bar), task-list
- Last phase always ends with a `notes-block` (midnight callout reinforcing consulting narrative)

**Footer page numbers:** "X of Y" — update after counting all pages.

### Step 4 — Export PDF

```bash
cd ~/autonomous-proposals && node scripts/to-pdf.js proposals/{slug}-project-plan.html proposals/{slug}-project-plan.pdf
```

### Step 5 — Deliver

Share PDF path. State page count. Mention HTML path for future edits.

---

## HTML Components Reference

See `references/components.md` for copy-paste HTML for every component.

| Component | Reference |
|-----------|-----------|
| Cover page | `#cover` |
| Phase header bar | `#phase-header` |
| Task item (standard) | `#task-item` |
| Task item with fix badge | `#task-fix` |
| Task item with green badge | `#task-green-badge` |
| Notes block (midnight) | `#notes-block` |
| Phase pills (cover) | `#phase-pills` |

---

## CSS Design Tokens

```css
:root {
  --parchment:       #F5EFE0;  /* page bg */
  --parchment-light: #FAF7F0;  /* alternate page bg */
  --parchment-dark:  #EDE5D3;  /* borders */
  --midnight:        #0D0D1F;  /* phase headers, notes blocks */
  --vermillion:      #E8513D;  /* eyebrows, fix badges */
  --ink:             #1A1A2E;  /* headlines */
  --prose:           #4A4A60;  /* body text */
  --caption:         #7A7A90;  /* labels, footer */
  --sage:            #284838;  /* green badges */
}
```

**Fonts:**
- Headlines: `'Fraunces'` serif, `font-variation-settings: 'opsz' 72–144`
- Body: `'DM Sans'` sans-serif
- Labels/mono: `'JetBrains Mono'` monospace, uppercase, `letter-spacing: 0.1em`

---

## Badge Types

| Badge | Use case | Style |
|-------|----------|-------|
| `fix-badge` | Audit fix, bug, known breakage | Vermillion border + bg |
| `posthog-badge` | Source of truth, impact tracking, Day 1 priority | Sage green bg, white text |

Custom badge label text is flexible — use whatever makes sense in context (e.g. "Fix", "Critical", "SEO", "Bug", "Day 1", "Source of Truth", "Impact Tracking").

---

## Cover Page Rules

- Client logo on LEFT, Autonomous wordmark on RIGHT (× separator between)
- If no logo: use text placeholder `<div class="logo-placeholder">` — never block generation
- Headline: 3-line max, Fraunces 52pt, letter-spacing -0.04em
- Phase pills: one pill per phase — label + title + sub (week/timeline)
- Meta bar at bottom: Prepared for / Prepared by / Kickoff / Target Completion

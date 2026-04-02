---
name: Client Report HTML Generator
description: >
  Use when asked to "create the client report", "generate HTML report",
  "build the presentation", "create client-facing deliverable", or when
  Phase 4 delivery of the audit is needed. Transforms the markdown audit
  report and JSON data into a polished, single-file HTML report.
version: 1.0.0
---

## Brand Config Injection

Before generating the HTML report, load brand config from Step 0:
- Use brand_config.company_name in header/footer (replace "Autonomous")
- Use brand_config.cta_url for all Calendly links (default: https://calendly.com/rizwan-20/30min)
- Use brand_config.cta_label for CTA button text
- Use brand_config.primary_color for accent elements
- If brand_config.hide_autonomous = true: remove all "Autonomous Technology Inc." mentions

Report product name: always use "Revenue Leak Audit" not "Analytics Audit" or "GA4 Audit"

---

# Client Report HTML Generator

Transform the markdown audit report and JSON data into a polished, single-file HTML client report. This is the final deliverable — a curated executive presentation, not a 1:1 dump of the markdown.

## Step 1: Gather Inputs

Read these files before generating the report:

| File | Contents |
|------|----------|
| `.hazn/outputs/analytics-audit/<domain>-audit.md` | Completed markdown audit report (sections A-Q) |
| `.hazn/outputs/analytics-audit/ga4_audit_data.json` | Primary GA4 data (events, conversions, traffic, campaigns, ecommerce) |
| `.hazn/outputs/analytics-audit/ga4_audit_extra.json` | Extended GA4 data (engagement, browsers, UTMs, keywords, trends) |
| `.hazn/outputs/analytics-audit/gsc_audit_data.json` | Organic search data (queries, landing pages, brand analysis, cannibalization) — optional |
| `.hazn/outputs/analytics-audit/site_inspection.json` | Tracking code inventory — optional |

Collect client metadata from the data:
- Domain name
- Audit date
- GA4 Property ID
- Total sessions analyzed
- Date ranges covered

## Step 2: Plan Report Sections

The HTML report is a **curated executive presentation** — not all 17+ markdown sections appear. Map the most impactful findings into these HTML sections:

| HTML Section | Source Sections | Component Type |
|-------------|----------------|----------------|
| Hero | Exec summary + metadata | Full-bleed image + title overlay |
| Score Cards | Sections A, D, F | `.score-card` grid (3-4 cards) |
| Key Findings | Section G priorities | `.finding` cards (red/amber/green severity) |
| MarTech Stack | Section K | `.tool-grid` with health indicator dots |
| Attribution Architecture | Section L | Styled flow diagram (current vs ideal) |
| Why It Matters | Section L signal loss | `.section--dark` with stat strip |
| Meta CAPI | Section L CAPI subsection | Data + recommendations |
| Google Ads | Section N | Signal-to-noise stats + restructuring |
| Channel Performance | Section F traffic + Section O | Comparison table |
| Organic Search | Section Q (GSC data) | Brand/non-brand stats, top query table, opportunities |
| Before & After | Section G + Section P combined | `.comparison` table |
| Roadmap | Section P | `.timeline` phases (weeks 1-12) |
| Expected ROI | Section P ROI estimates | `.section--dark` metric cards |
| Investment | Section P cost summary | Pricing breakdown |
| CTA | — | Full-width `section--dark` with Calendly booking button (`https://calendly.com/rizwan-20/30min`) + 3 trust signals |

**If GSC data is not available**, skip the Organic Search section.

## Step 3: Generate HTML

Write a single `.hazn/outputs/analytics-audit/client-report/index.html` file with:

- **All CSS inline** in a `<style>` block (no external stylesheets)
- **No JavaScript dependencies** — only vanilla JS for ToC scroll-tracking
- **Responsive design** at 375px, 768px, 1024px, 1440px breakpoints
- **Sticky sidebar ToC** with scroll-tracking active state (Intersection Observer pattern)
- **All data hardcoded** from the JSON files (no runtime templating)
- **Image references** to `images/` subdirectory (hero, section backgrounds)
- **Print-friendly** — hide ToC and reduce margins for print media

### Design System

Use the **Stone/Amber palette** and typography below. These tokens are canonical — do not substitute or abbreviate.

```css
:root {
  /* Base palette — Stone */
  --stone-50: #fafaf9;    --stone-100: #f5f5f4;   --stone-200: #e7e5e3;
  --stone-300: #d6d3d1;   --stone-400: #a8a29e;   --stone-500: #78716c;
  --stone-600: #57534e;   --stone-700: #44403c;   --stone-800: #292524;
  --stone-900: #1c1917;

  /* Accent — Amber */
  --amber-400: #fbbf24;   --amber-500: #f59e0b;   --amber-600: #d97706;

  /* Severity */
  --red-500: #ef4444;     --red-100: #fee2e2;
  --amber-100: #fef3c7;
  --green-500: #22c55e;   --green-100: #dcfce7;
  --blue-500: #3b82f6;    --blue-100: #dbeafe;
}
```

### Typography

```css
/* Headings */
font-family: 'Source Serif 4', Georgia, serif;

/* Body */
font-family: 'Inter', system-ui, -apple-system, sans-serif;

/* Google Fonts import — always include at top of <style> block */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap');
```

> ⚠️ **Finding override — required:** Always add `color: var(--stone-800)` explicitly to `.finding`, `.before`, `.after`. These use light backgrounds (amber-100, red-100, green-100) that will render white text if placed inside a `.section--dark` parent. Never omit this.

> ⚠️ **Section padding:** Use `6rem` top/bottom on regular sections, `8rem` on the final CTA section. Score card grid: `2rem 1.25rem` padding per card, `1.25rem` gap.

### CTA Strategy

**All CTAs must use:** `https://calendly.com/rizwan-20/30min`

Do NOT use generic email links or `autonomoustech.ca/contact`.

**CTA button CSS — required on every CTA button:**

```css
.cta-btn {
  display: block;
  margin: 0 auto;
  max-width: 280px;
  white-space: normal;
  text-align: center;
  padding: 1rem 2.5rem;
  background: var(--amber-500);
  color: var(--stone-900);
  font-weight: 700;
  font-size: 1.1rem;
  border-radius: 8px;
  text-decoration: none;
  transition: background 0.2s, transform 0.2s;
  box-shadow: 0 6px 24px rgba(245,158,11,0.35);
}
.cta-btn:hover { background: var(--amber-600); transform: translateY(-2px); }
```

**CTA copy — implementation-hire framing. Use one of these or equivalent:**
- "Book a 20-min call — we'll walk through your GA4 live →"
- "Let's review this together — book a 20-min call →"
- "Your implementation roadmap starts here →"
- "Book a call — we'll build the fix plan together →"

**Final CTA section** must use `section--dark` (full-width dark background) containing:
1. The Calendly CTA button (using `.cta-btn` above)
2. Three trust signals below the button — e.g. "No commitment required", "Walk away with an action plan", "We've done this for [X] brands"

## Step 4: Component Library Reference

Use these CSS classes for consistent component styling:

| Component | Class | Usage |
|-----------|-------|-------|
| Section | `.section`, `.section--dark`, `.section--wide` | Content containers; dark uses stone-900 bg |
| Section label | `.section__label` | Small caps category label above title |
| Section title | `.section__title` | Main section heading (Source Serif 4) |
| Section lead | `.section__lead` | Intro paragraph below title |
| Score card | `.score-card` | KPI display with large value |
| Score card value | `.score-card__value--red`, `--amber`, `--green` | Color-coded scores |
| Finding card | `.finding`, `.finding--warn`, `.finding--good` | Severity-coded finding items |
| Stat strip | `.stat-strip`, `.stat-strip__item` | Horizontal metric row (dark sections) |
| Tool card | `.tool-card` | MarTech inventory item |
| Tool health dot | `.tool-card__dot--red`, `--amber`, `--green` | Status indicators |
| Comparison table | `.comparison` | Before/after layout |
| Before cell | `.before` | Red-tinted before state |
| After cell | `.after` | Green-tinted after state |
| Timeline | `.timeline` | Roadmap container |
| Timeline phase | `.timeline__phase` | Individual phase block |
| Timeline dot | `.timeline__dot` | Phase indicator |
| Metric card | `.metric-card` | ROI projection display |
| Callout | `.callout`, `.callout--danger`, `.callout--stat` | Highlighted content blocks |
| Pull quote | `.pullquote` | Emphasis quotes |
| ToC nav | `.toc` | Sticky sidebar navigation |
| ToC link | `.toc__link`, `.toc__link--active` | Navigation items with active state |
| ToC toggle | `.toc__toggle` | Mobile hamburger toggle |
| Data table | `.data-table` | Styled tables with alternating rows |

### Layout Patterns

- **Light/dark section alternation** for visual rhythm
- **Max content width:** 720px centered within sections (left column in desktop TOC layout)
- **Section padding:** `6rem` top/bottom on regular sections; `8rem` on the final CTA section; `3rem` on mobile
- **Grid layouts:** CSS Grid for score cards (auto-fit, minmax(240px, 1fr))
- **Responsive breakpoints:** 375px, 768px, 1024px, 1440px
- **Two-column desktop layout:** sticky sidebar TOC (240px) + main content (flex: 1), `gap: 3rem`, inside a `max-width: 1200px` outer wrapper

### Sticky Sidebar TOC

On desktop (≥1024px), the ToC renders as a fixed left sidebar (240px wide, frosted glass). On mobile/tablet it collapses to a hidden off-canvas drawer toggled by a button.

```css
.page-layout {
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  gap: 3rem;
  align-items: flex-start;
}
.toc {
  width: 240px;
  flex-shrink: 0;
  position: sticky;
  top: 2rem;
  max-height: calc(100vh - 4rem);
  overflow-y: auto;
  background: rgba(255,255,255,0.7);
  backdrop-filter: blur(8px);
  border: 1px solid var(--stone-200);
  border-radius: 10px;
  padding: 1.25rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.toc__link--active {
  background: var(--amber-500);
  color: var(--stone-900);
  font-weight: 600;
}
@media (max-width: 1023px) {
  .page-layout { display: block; padding: 0 1rem; }
  .toc {
    display: none;
    position: fixed; top: 0; left: 0; bottom: 0;
    width: 280px; z-index: 1000;
    border-radius: 0; max-height: 100vh;
  }
  .toc.toc--open { display: block; }
  .toc__toggle {
    display: flex;
    position: fixed; bottom: 5rem; right: 1rem;
    background: var(--stone-900); color: white;
    border: none; border-radius: 50%;
    width: 44px; height: 44px;
    align-items: center; justify-content: center;
    cursor: pointer; z-index: 999;
  }
}
```

### Mobile Bottom CTA Banner

Must be hidden on desktop and shown on mobile only:

```css
.mobile-cta-banner {
  display: none;
  position: fixed;
  bottom: 0; left: 0; right: 0;
  background: var(--stone-900);
  color: #fff;
  padding: 0.75rem 1rem;
  z-index: 1000;
  box-shadow: 0 -4px 12px rgba(0,0,0,0.15);
}
@media (max-width: 768px) {
  .mobile-cta-banner { display: flex; align-items: center; justify-content: space-between; }
}
.mobile-cta-banner__btn {
  padding: 0.5rem 1.25rem;
  background: var(--amber-500);
  color: var(--stone-900);
  font-weight: 600;
  font-size: 0.85rem;
  border-radius: 6px;
  text-decoration: none;
  white-space: nowrap;
}
```

The banner button must link to `https://calendly.com/rizwan-20/30min`.

### Scroll Reveal

Add `IntersectionObserver` fade-in-up on scorecard grids, stat strips, and tool grids. The `.reveal` class starts hidden and animates in:

```css
.reveal {
  opacity: 0;
  transform: translateY(28px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}
.reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}
```

```javascript
const revealObserver = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('is-visible'); } });
}, { threshold: 0.1 });
document.querySelectorAll('.score-card, .stat-strip, .tool-card, .metric-card').forEach(el => {
  el.classList.add('reveal');
  revealObserver.observe(el);
});
```

### Hover States

All interactive cards must have smooth lift transitions:

```css
.score-card, .tool-card, .finding, .metric-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.score-card:hover, .tool-card:hover, .finding:hover, .metric-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
}
```

### ToC Implementation

```javascript
// Intersection Observer for scroll-tracking
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      document.querySelectorAll('.toc__link').forEach(l => l.classList.remove('toc__link--active'));
      document.querySelector(`.toc__link[href="#${entry.target.id}"]`)?.classList.add('toc__link--active');
    }
  });
}, { rootMargin: '-20% 0px -70% 0px' });
document.querySelectorAll('section[id]').forEach(s => observer.observe(s));
```

## Step 5: Quality Checklist

Before finalizing, verify:

### Data & Content
- [ ] All numbers sourced from JSON data — no placeholder text ("XX%", "N/A", "[TBD]")
- [ ] Hero section has image and client name
- [ ] Score card colors match severity (red < 50, amber 50-75, green > 75)
- [ ] Finding cards use correct severity classes
- [ ] Timeline phases match the roadmap from Section P
- [ ] ROI numbers match Section P estimates
- [ ] If GSC data exists, Organic Search section is present with real query data

### Design & UX
- [ ] **Dark/light section alternation** maintained for visual rhythm
- [ ] **Responsive** at 375px, 768px, 1024px, 1440px — test all four
- [ ] **Single file** — no external dependencies except Google Fonts
- [ ] **No inline styles** — use CSS classes throughout; extract repeated inline styles to utility classes
- [ ] **Section padding** — `6rem` top/bottom on regular sections, `8rem` on final CTA section; scorecard cards: `2rem 1.25rem` padding, `1.25rem` gap
- [ ] **Print-friendly** — `@media print` hides ToC and mobile banner; reduces margins
- [ ] **Scroll reveal** — `IntersectionObserver` fade-in-up (`.reveal` class: `opacity 0→1` + `translateY(28px)→0` at `0.6s ease`) on scorecard grids, stat strips, tool grids, metric cards
- [ ] **Hover states** — all interactive cards (`.score-card`, `.tool-card`, `.finding`, `.metric-card`) have `0.2s` transitions with `translateY(-1px)` lift + shadow
- [ ] **Sticky sidebar TOC** — frosted glass (`background: rgba(255,255,255,0.7); backdrop-filter: blur(8px)`) with amber active links (`.toc__link--active`); collapses to off-canvas drawer on mobile (≤1023px)
- [ ] **Mobile bottom CTA banner** — `display: none` by default; `@media (max-width: 768px) { display: flex }` — amber button links to Calendly

### CTAs & Links
- [ ] **Calendly links** — ALL CTAs use `https://calendly.com/rizwan-20/30min` — no exceptions, no generic email links, no `autonomoustech.ca/contact`
- [ ] **CTA button CSS** — `display: block; margin: 0 auto; max-width: 280px; white-space: normal; text-align: center; box-shadow: 0 6px 24px rgba(245,158,11,0.35)`
- [ ] **Final CTA section** — uses `section--dark` (dark background) with Calendly button + 3 trust signals

### Typography & Color
- [ ] **Google Fonts import** — `Inter` + `Source Serif 4` imported at top of `<style>` block
- [ ] **Full Stone/Amber palette** — all `--stone-*` and `--amber-*` CSS variables defined in `:root`; severity colors (`--red-100/500`, `--amber-100`, `--green-100/500`, `--blue-100/500`) also defined
- [ ] **Finding text** — `.finding`, `.before`, `.after` always have `color: var(--stone-800)` explicitly set — prevents white text on light backgrounds inside dark sections

### Other
- [ ] No broken image references (check `images/` directory)
- [ ] ToC links scroll to correct sections; active state tracks on scroll via Intersection Observer

## Step 6: Reference Existing Report

If `.hazn/outputs/analytics-audit/client-report/index.html` already exists, use it as a **design benchmark**:
- Match or exceed the typography, spacing, and color quality
- Maintain the same component patterns and visual rhythm
- Preserve any client-specific customizations (images, branding)
- The existing report is the gold standard — new output should be at least as polished

## Deployment

After generating the report HTML:

1. Save to `~/autonomous-proposals/docs/{client-slug}-analytics-audit-{date}/index.html`
2. Commit and push to `https://github.com/autonomous-tech/autonomous-proposals` (main branch)
3. Cloudflare Pages auto-deploys to `https://docs.autonomoustech.ca/docs/{client-slug}-analytics-audit-{date}/`
4. Use the SHARE button (auto-injected by GitHub Actions) to generate a 30-day shareable link via `share.autonomoustech.ca`
5. Share the link with the client — no login required for the recipient

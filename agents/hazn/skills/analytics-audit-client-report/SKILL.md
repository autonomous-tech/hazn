---
name: Client Report HTML Generator
description: >
  Use when asked to "create the client report", "generate HTML report",
  "build the presentation", "create client-facing deliverable", or when
  Phase 4 delivery of the audit is needed. Transforms the markdown audit
  report and JSON data into a polished, single-file HTML report.
version: 1.0.0
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
| CTA | — | Call-to-action footer |

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

Use the Stone/Amber palette with Inter + Source Serif 4 typography:

```css
/* Colors */
--stone-50: #fafaf9;   --stone-100: #f5f5f4;  --stone-200: #e7e5e3;
--stone-600: #57534e;   --stone-800: #292524;   --stone-900: #1c1917;
--amber-400: #fbbf24;   --amber-500: #f59e0b;   --amber-600: #d97706;
--red-500: #ef4444;     --green-500: #22c55e;

/* Typography */
font-family: 'Inter', system-ui, sans-serif;          /* body */
font-family: 'Source Serif 4', Georgia, serif;         /* headings */
```

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
- **Max content width:** 720px centered within sections
- **Section padding:** 5rem top/bottom on desktop, 3rem on mobile
- **Grid layouts:** CSS Grid for score cards (auto-fit, minmax(240px, 1fr))

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

- [ ] All numbers sourced from JSON data — no placeholder text ("XX%", "N/A", "[TBD]")
- [ ] Responsive at 375px (mobile), 768px (tablet), 1024px (laptop), 1440px (desktop)
- [ ] ToC links scroll to correct sections; active state tracks on scroll
- [ ] Dark/light section alternation maintained for visual rhythm
- [ ] Hero section has image and client name
- [ ] Score card colors match severity (red < 50, amber 50-75, green > 75)
- [ ] Finding cards use correct severity classes
- [ ] Timeline phases match the roadmap from Section P
- [ ] ROI numbers match Section P estimates
- [ ] If GSC data exists, Organic Search section is present with real query data
- [ ] CTA section has correct contact email/link
- [ ] No broken image references (check `images/` directory)
- [ ] Print media query hides ToC and adjusts layout

## Step 6: Reference Existing Report

If `.hazn/outputs/analytics-audit/client-report/index.html` already exists, use it as a **design benchmark**:
- Match or exceed the typography, spacing, and color quality
- Maintain the same component patterns and visual rhythm
- Preserve any client-specific customizations (images, branding)
- The existing report is the gold standard — new output should be at least as polished

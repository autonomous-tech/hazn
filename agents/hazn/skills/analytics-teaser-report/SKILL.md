---
name: Teaser Report HTML Generator
description: >
  Use when generating the /hazn-analytics-teaser prospect report. Defines the design system,
  section mapping, scoring formulas, and Copy/UX/CRO evaluation criteria for
  the zero-access prospect teaser report.
version: 1.0.0
---

# Teaser Report — Prospect Teaser HTML Generator

Generate a single-file HTML teaser report from publicly collected website data. This is a sales asset — a zero-access prospect report that delivers genuine value across analytics, UX, copy, and CRO, while funneling prospects toward deeper paid engagements.

---

## Step 1: Gather Inputs

Read these files before generating the report:

| File | Contents |
|------|----------|
| `.hazn/outputs/analytics-teaser/<domain>/site_inspection.json` | MarTech stack, tracking codes, consent, structured data |
| `.hazn/outputs/analytics-teaser/<domain>/pagespeed.json` | Lighthouse scores, Core Web Vitals, third-party scripts |
| `.hazn/outputs/analytics-teaser/<domain>/teaser_data.json` | robots.txt, sitemap, security headers, SSL, technology |
| `.hazn/outputs/analytics-teaser/<domain>/playwright_data.json` | Accessibility snapshots, console errors, page list |
| `.hazn/outputs/analytics-teaser/<domain>/screenshots/*.png` | Desktop + mobile screenshots for each page |

Collect metadata:
- Domain name
- Company name (from argument or extracted from site)
- Audit date
- Calendly URL for CTAs: **always use `https://calendly.com/rizwan-20/30min`**

---

## Step 2: Report Structure — 11 Sections + 3 Gates + CTA

| # | Section ID | Section | Source | Component Type |
|---|-----------|---------|--------|----------------|
| 1 | `hero` | **Hero** | Screenshot + domain | Full-bleed hero with desktop screenshot, site grade, personalized headline |
| 2 | `scorecard` | **Site Health Scorecard** | All data sources | `.grade-badge` grid (5 grades: Performance, SEO, MarTech, Copy/UX, Security) |
| 3 | `cwv` | **Core Web Vitals** | PageSpeed API | `.cwv-display` three-column gauge (LCP, INP/FID, CLS) with pass/fail |
| 4 | `martech` | **MarTech Stack Inventory** | site_inspection.json | `.tool-grid` with health dots, missing tools flagged |
| 5 | `privacy` | **Tracking & Privacy** | site_inspection.json | Consent mode status, cookie analysis, compliance flags |
| 6 | `seo` | **SEO & Structured Data** | site_inspection + teaser_data | Meta tags, schemas, sitemap health, AI crawler status |
| 7 | `performance` | **Performance & Script Bloat** | PageSpeed third-party | Third-party inventory with blocking time, page weight breakdown |
| 8 | `security` | **Security & Infrastructure** | teaser_data.json | SSL status, security headers grade, tech stack display |
| — | `gate-1` | **Gate 1: Organic Search** | — | `.teaser-gate` locked section with GSC upsell |
| 9 | `copy-audit` | **Copy Audit** | Playwright snapshots + screenshots | Headline, CTA, value prop, social proof analysis |
| 10 | `ux-audit` | **UX Audit** | Playwright snapshots + screenshots | Visual hierarchy, navigation, mobile, accessibility |
| 11 | `cro-audit` | **CRO Audit** | Playwright snapshots + screenshots | Conversion path, forms, trust signals, CTA placement |
| — | `gate-2` | **Gate 2: Analytics Deep-Dive** | — | `.teaser-gate` locked section with GA4 upsell |
| — | `gate-3` | **Gate 3: Paid SEO** | — | `.teaser-gate` locked section with SEO engagement upsell |
| — | `cta` | **Final CTA** | — | Full-width CTA section with Calendly booking |

---

## Step 3: Scoring System

### Overall Site Grade (A–F)

Weighted composite displayed in hero and scorecard:

| Dimension | Weight | Source | Score Range |
|-----------|--------|--------|-------------|
| Performance | 15% | Lighthouse performance score (0–100) | Map to 0–100 |
| SEO Basics | 10% | Lighthouse SEO score + meta tag completeness + structured data count | Map to 0–100 |
| Core Web Vitals | 10% | CWV pass rate (3 metrics: LCP, INP/FID, CLS) | 0, 33, 67, or 100 |
| MarTech Maturity | 15% | Composite formula (see below) | 0–100 |
| Privacy Compliance | 10% | Consent mode + CMP presence | 0–100 |
| Security | 5% | Security headers score (0–9) mapped to 0–100 | 0–100 |
| Copy Quality | 15% | Copy audit grade (see rubric below) | Map A=95, B=80, C=65, D=45, F=25 |
| UX Quality | 10% | UX audit grade (see rubric below) | Map A=95, B=80, C=65, D=45, F=25 |
| CRO Effectiveness | 10% | CRO audit grade (see rubric below) | Map A=95, B=80, C=65, D=45, F=25 |

**Grade thresholds:** A ≥ 85, B ≥ 70, C ≥ 55, D ≥ 40, F < 40

### MarTech Maturity Score (0–100)

| Component | Points |
|-----------|--------|
| GTM or TMS present | +15 |
| Analytics (GA4/similar) present | +15 |
| Ad pixel (any) present | +10 |
| Consent/CMP present | +15 |
| Session recording (Hotjar/Clarity/etc) | +5 |
| Structured data (3+ types) | +10 |
| Server-side tracking signals | +15 |
| CRM/email platform present | +10 |
| Call tracking present | +5 |
| **Penalty:** per critical issue | -10 |

### Copy Audit Grade Rubric

| Criterion | Weight | What to Evaluate |
|-----------|--------|-----------------|
| Hero headline quality | 25% | Length (6–12 words ideal), clarity, specificity, power words, framework compliance (PAS/AIDA/StoryBrand) |
| Value proposition clarity | 20% | Clear within 5 seconds? States what, for whom, why different? |
| CTA quality | 20% | Action-oriented text (not "Submit"), prominent placement, strong contrast |
| Social proof presence | 15% | Testimonials present, attributed, specific, quantified? Client logos? |
| Readability & scannability | 10% | Short paragraphs, bullet points, clear headers, minimal jargon |
| Messaging consistency | 10% | Heading messages align across pages |

**Grade:** A = excellent across all criteria, B = strong with minor gaps, C = adequate but generic, D = significant issues, F = major problems

### UX Audit Grade Rubric

| Criterion | Weight | What to Evaluate |
|-----------|--------|-----------------|
| Visual hierarchy | 20% | Eye flow logic, primary action prominence, whitespace |
| Navigation clarity | 20% | Depth, labels, mobile menu, search |
| Above-the-fold effectiveness | 15% | Value prop + CTA visible without scroll |
| Mobile experience | 20% | Tap targets, text readability, responsive layout |
| Accessibility basics | 15% | Heading hierarchy, alt text, ARIA, color contrast |
| Design consistency | 10% | Typography, spacing, color, component consistency |

### CRO Audit Grade Rubric

| Criterion | Weight | What to Evaluate |
|-----------|--------|-----------------|
| Conversion path efficiency | 20% | Steps from landing to conversion, friction points |
| CTA placement & quality | 20% | Above-fold CTA, frequency, sticky CTA, text quality |
| Trust signal density | 20% | Client logos, testimonials near CTAs, certifications, guarantees |
| Form optimization | 15% | Field count, labels, error handling, friction |
| Social proof placement | 15% | Proximity to decision points (CTAs, pricing, forms) |
| Risk reversal | 10% | Guarantees, free trials, "no CC required" |

---

## Step 4: Design System

Inherit the **Stone/Amber palette** and typography from the client-report skill.

### Colors

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

  /* Grade colors */
  --grade-a: #22c55e;
  --grade-b: #84cc16;
  --grade-c: #f59e0b;
  --grade-d: #f97316;
  --grade-f: #ef4444;
}
```

### Typography

```css
/* Headings */
font-family: 'Source Serif 4', Georgia, serif;

/* Body */
font-family: 'Inter', system-ui, -apple-system, sans-serif;

/* Import */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap');
```

### Inherited Components

All components from the client-report skill apply:

`.section`, `.section--dark`, `.section--wide`, `.section__label`, `.section__title`, `.section__lead`,
`.score-card`, `.score-card__value--red/amber/green`, `.finding`, `.finding--warn`, `.finding--good`,
`.stat-strip`, `.stat-strip__item`, `.tool-card`, `.tool-card__dot--red/amber/green`,
`.callout`, `.callout--danger`, `.callout--stat`, `.pullquote`,
`.toc`, `.toc__link`, `.toc__link--active`, `.toc__toggle`,
`.data-table`, `.metric-card`, `.comparison`, `.before`, `.after`

> ⚠️ **Override required:** Always add `color: var(--stone-800)` explicitly to `.finding`, `.before`, `.after` — these use light backgrounds (amber-100, red-100, green-100) that will render white text if placed inside a `.section--dark` parent. Same applies to any light-background component inside a dark section.

The final CTA button must always include `white-space: nowrap` to prevent text like "Call" or "→" orphaning on a second line:

```css
.cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2.5rem;
  background: var(--amber-500);
  color: var(--stone-900);
  font-weight: 700;
  font-size: 1.1rem;
  border-radius: 8px;
  text-decoration: none;
  transition: background 0.2s, transform 0.2s;
  white-space: nowrap; /* prevents line-break inside button label */
}
.cta-btn:hover { background: var(--amber-600); transform: translateY(-2px); }
```

### New Components — Teaser-Specific

#### `.grade-badge` — Circular Letter Grade

```css
.grade-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  font-family: 'Source Serif 4', Georgia, serif;
  font-size: 2rem;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}
.grade-badge--a { background: var(--grade-a); }
.grade-badge--b { background: var(--grade-b); }
.grade-badge--c { background: var(--grade-c); }
.grade-badge--d { background: var(--grade-d); }
.grade-badge--f { background: var(--grade-f); }

/* Large version for hero */
.grade-badge--lg {
  width: 120px;
  height: 120px;
  font-size: 3.5rem;
  box-shadow: 0 4px 24px rgba(0,0,0,0.15);
}
```

#### `.cwv-display` — Core Web Vitals Gauge

```css
.cwv-display {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  max-width: 720px;
  margin: 0 auto;
}
.cwv-metric {
  text-align: center;
  padding: 1.5rem;
  border-radius: 12px;
  background: var(--stone-50);
  border: 2px solid var(--stone-200);
}
.cwv-metric--pass { border-color: var(--green-500); }
.cwv-metric--needs-improvement { border-color: var(--amber-500); }
.cwv-metric--fail { border-color: var(--red-500); }
.cwv-metric__value {
  font-size: 2rem;
  font-weight: 700;
  font-family: 'Inter', sans-serif;
}
.cwv-metric__label {
  font-size: 0.85rem;
  color: var(--stone-500);
  margin-top: 0.25rem;
}
.cwv-metric__status {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 0.5rem;
}
```

#### `.teaser-gate` — Locked Service Gate

```css
.teaser-gate {
  position: relative;
  border: 2px dashed var(--stone-300);
  border-radius: 16px;
  padding: 3rem 2rem;
  margin: 3rem 0;
  overflow: hidden;
  background: linear-gradient(135deg, var(--stone-50) 0%, var(--stone-100) 100%);
}
.teaser-gate__blur {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 0%, var(--stone-100) 60%);
  backdrop-filter: blur(4px);
  z-index: 1;
}
.teaser-gate__content {
  position: relative;
  z-index: 2;
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
}
.teaser-gate__lock {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--stone-800);
  color: var(--amber-400);
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
}
.teaser-gate__title {
  font-family: 'Source Serif 4', Georgia, serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--stone-900);
  margin-bottom: 0.75rem;
}
.teaser-gate__preview {
  font-size: 0.95rem;
  color: var(--stone-600);
  line-height: 1.6;
  margin-bottom: 1rem;
}
.teaser-gate__preview-items {
  background: var(--stone-50);
  border: 1px solid var(--stone-200);
  border-radius: 8px;
  padding: 1rem 1.5rem;
  margin: 1rem 0;
  text-align: left;
  font-size: 0.9rem;
}
.teaser-gate__cta {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 2rem;
  background: var(--amber-500);
  color: var(--stone-900);
  font-weight: 600;
  font-size: 1rem;
  border-radius: 8px;
  text-decoration: none;
  transition: background 0.2s, transform 0.2s;
  margin-top: 1rem;
}
.teaser-gate__cta:hover {
  background: var(--amber-600);
  transform: translateY(-1px);
}
```

#### `.audit-card` — Copy/UX/CRO Finding Items

```css
.audit-card {
  display: flex;
  gap: 1rem;
  padding: 1.25rem;
  border-radius: 10px;
  background: #fff;
  border: 1px solid var(--stone-200);
  margin-bottom: 0.75rem;
}
.audit-card__icon {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}
.audit-card__icon--critical { background: var(--red-100); color: var(--red-500); }
.audit-card__icon--warning { background: var(--amber-100); color: var(--amber-600); }
.audit-card__icon--good { background: var(--green-100); color: var(--green-500); }
.audit-card__icon--info { background: var(--blue-100); color: var(--blue-500); }
.audit-card__body { flex: 1; }
.audit-card__title {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--stone-800);
  margin-bottom: 0.25rem;
}
.audit-card__desc {
  font-size: 0.875rem;
  color: var(--stone-600);
  line-height: 1.5;
}
```

#### `.teaser-banner` — Fixed Mobile Bottom CTA

```css
.teaser-banner {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--stone-900);
  color: #fff;
  padding: 0.75rem 1rem;
  z-index: 1000;
  box-shadow: 0 -4px 12px rgba(0,0,0,0.15);
}
@media (max-width: 768px) {
  .teaser-banner { display: flex; align-items: center; justify-content: space-between; }
}
.teaser-banner__text {
  font-size: 0.85rem;
  font-weight: 500;
}
.teaser-banner__btn {
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

#### `.hero-screenshot` — Embedded Site Screenshot

```css
.hero-screenshot {
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
  border: 1px solid var(--stone-200);
  max-width: 100%;
  height: auto;
}
```

### Layout Patterns

- **Light/dark section alternation** for visual rhythm
- **Max content width:** 720px centered within sections
- **Section padding:** 5rem top/bottom on desktop, 3rem on mobile
- **Grid layouts:** CSS Grid for score cards and CWV metrics
- **Responsive breakpoints:** 375px, 768px, 1024px, 1440px
- **Base64-embed screenshots** into the HTML for single-file delivery

### ToC Implementation

Same Intersection Observer pattern as client-report:

```javascript
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

---

## Step 5: Screenshot Embedding

All screenshots must be Base64-encoded and embedded directly in the HTML:

```javascript
// Read screenshot file, convert to base64 data URI
// <img src="data:image/png;base64,..." class="hero-screenshot" alt="...">
```

Use Bash to convert: `base64 -i screenshots/home-desktop.png`

This ensures the report is a single self-contained HTML file with no external dependencies.

---

## Step 6: Gate Copy Templates

### Gate 1: Organic Search Intelligence (GSC Access)

- **Lock icon:** 🔒
- **Title:** "Unlock Your Organic Search Intelligence"
- **Hook:** Use sitemap URL count from teaser_data.json: "Your site has {N} pages in its sitemap. But which ones actually drive organic traffic?"
- **Preview items** (2–3 visible): Use real data from robots/sitemap analysis
- **What the full analysis delivers:** Brand vs non-brand split, keyword cannibalization, content refresh opportunities
- **CTA:** "Book a 15-min walkthrough →" → Calendly link

### Gate 2: Analytics Deep-Dive (GA4 Access)

- **Lock icon:** 🔒
- **Title:** "See What Your Analytics Is Really Telling You"
- **Hook:** Use tag count from site_inspection.json: "We found {N} tracking tags on your site. But tags installed ≠ tags working."
- **Preview items:** Blurred score cards with "??/100" scores
- **What the full analysis delivers:** GA4 implementation score, attribution architecture, ad platform signal loss
- **CTA:** "Book your audit walkthrough →" → Calendly link

### Gate 3: Paid SEO Strategy

- **Lock icon:** 🔒
- **Title:** "Validated Content Strategy & Execution"
- **Hook:** Reference sitemap + SEO findings: "Are you ranking for the RIGHT keywords?"
- **Preview items:** Reference real SEO findings from the free section
- **Social proof:** "For one client, we identified 4,800–8,500 clicks/month in unrealized organic traffic"
- **CTA:** "Book your strategy call →" → Calendly link

---

## Step 7: Quality Checklist

Before finalizing, verify:

- [ ] **All scores calculated from real data** — no placeholder text ("XX%", "N/A", "[TBD]")
- [ ] **Overall grade displayed** in hero section with large `.grade-badge--lg`
- [ ] **5 scorecard grades** all present and color-coded
- [ ] **Core Web Vitals** show actual values with pass/fail indicators
- [ ] **MarTech grid** lists real tools detected (or explicitly flags "Not detected")
- [ ] **Copy/UX/CRO audit cards** contain specific, actionable findings — NOT generic advice
- [ ] **3 teaser gates** render with contextual hooks using real numbers from the data
- [ ] **All screenshots** Base64-embedded and rendering
- [ ] **Responsive** at 375px, 768px, 1440px — test all three
- [ ] **Mobile bottom CTA banner** visible on mobile only
- [ ] **ToC** with working scroll-tracking
- [ ] **Single file** — no external dependencies except Google Fonts
- [ ] **File size** under 300KB (screenshots may push this; aim for <500KB max with screenshots)
- [ ] **Print-friendly** — hide ToC and banner for print
- [ ] **Calendly links** — all CTAs use `https://calendly.com/rizwan-20/30min` (not autonomoustech/30min or any other URL)
- [ ] **Dark/light section alternation** maintained
- [ ] **Company name** personalized throughout (not just "this site")
- [ ] **Finding box text** — `.finding` always has `color: var(--stone-800)` explicitly set to prevent white text bleeding from dark parent sections (amber-100, red-100, green-100 backgrounds must never render white text)
- [ ] **CTA button** — use `display: block; margin: 0 auto; max-width: 280px; white-space: normal; text-align: center` — do NOT use `<br>` hacks or `white-space: nowrap`. Let it wrap naturally. Add `box-shadow: 0 6px 24px rgba(245,158,11,0.35)` for visual weight.
- [ ] **Deployment** — ALWAYS deploy to `autonomous-proposals` repo → `docs.autonomoustech.ca` (auth-gated, shareable via expiring link). NEVER deploy prospect reports to `landing-pages` → `pages.autonomoustech.ca` (public). See TOOLS.md decision rule.
- [ ] **Hover states** — all interactive cards (`.audit-card`, `.tool-card`, `.score-card`, `.status-row`) must have smooth `0.2s` transitions with subtle `translateY(-1px)` or `translateY(-2px)` lift + shadow
- [ ] **Scroll reveal** — add `IntersectionObserver` fade-in-up (`.reveal` class, `opacity 0→1` + `translateY(28px)→0` at `0.6s ease`) on scorecard grid, CWV display, tool grid, stat strip, gates
- [ ] **Gate lock animation** — `.teaser-gate__lock` must have a `@keyframes lockPulse` amber glow ring animation (every 2.4s) to draw attention
- [ ] **Gate border/background** — use amber-400 dashed border + amber-100 gradient background on gates, not stone-300 — more attention-grabbing
- [ ] **Section padding** — use `6rem` top/bottom on regular sections, `8rem` on final CTA section. Scorecard cards: `2rem 1.25rem` padding, `1.25rem` gap.
- [ ] **ToC** — frosted glass panel: `background: rgba(255,255,255,0.7); backdrop-filter: blur(8px)` with border + box-shadow
- [ ] **No inline styles** — extract all repeated inline styles to CSS classes. Use utility classes (`mt-sm`, `mt-md`, `mt-lg`) for margin-top variations
- [ ] **Mobile scorecard grid** — collapses to 2-col at 600px, 1-col at 400px
- [ ] **Share button** — must be injected from `briar-creek-construction/index.html` before `</body>` in every report

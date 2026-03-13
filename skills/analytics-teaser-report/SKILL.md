---
name: Teaser Report HTML Generator
description: >
  Use when generating the /hazn-analytics-teaser prospect report. Defines the design system,
  section mapping, scoring formulas, and Copy/UX/CRO evaluation criteria for
  the zero-access prospect teaser report.
version: 2.0.0
---

# Teaser Report — Prospect Teaser HTML Generator

> **Strategic intent: This is a lead gen tool, not just a report.**

The teaser audit exists to open conversations with prospects who haven't hired us yet. Every design and copy decision should serve one goal: **get them to book a call.**

The playbook:
1. **Deliver real value** — findings based on public signals that are genuinely useful. Not fluff. The prospect should feel "these people already understand my site better than my last agency did."
2. **Reveal a gap they didn't know existed** — each track should surface at least one finding that makes them uncomfortable in a productive way.
3. **Make the upgrade irresistible** — every section closes with a concrete "here's what we'd show you with GA4/GSC access." The report is a preview, not the full product.
4. **Remove friction from the next step** — every upsell CTA goes to the same Calendly link. One action, everywhere.
5. **No time estimates on fixes.** Never say "this takes 30 mins" or "a quick 2-hour fix." Time is subjective and presumptuous. Use effort levels (Low / Medium / High) only — no durations.

Generate a single-file HTML teaser report from publicly collected website data. Delivers genuine value across analytics, UX, copy, and CRO — while building the case for a deeper paid engagement.

---

## Step 0: Intake — ALWAYS Ask First

Before collecting any data or generating the report, ask:

> **"Which sections do you want included in this teaser report?"**
>
> Select all that apply:
> 1. ✅ **Core** — Site Health Scorecard, Core Web Vitals, Performance & Script Bloat, Security (always included)
> 2. 📊 **MarTech & Privacy** — MarTech stack inventory, tracking setup, consent compliance
> 3. 🔍 **SEO Audit** — Technical SEO, On-Page SEO, Structured Data, AI Search Readiness *(4 sub-sections)*
> 4. ✍️ **Copy Audit** — Headlines, CTAs, value proposition, social proof, messaging
> 5. 🎨 **UX Audit** — Visual hierarchy, navigation, mobile experience, accessibility
> 6. 📈 **CRO Audit** — Conversion path, trust signals, form friction, CTA placement
>
> Default if no answer: **all sections**.

Only collect data and build sections the user has confirmed. Skip unlisted sections entirely — do not include them as placeholders.

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

Also read `seo_data.json` if SEO sections are selected:

| File | Contents |
|------|----------|
| `.hazn/outputs/analytics-teaser/<domain>/seo_data.json` | Technical SEO signals, on-page data, structured data, AI crawler rules |

---

## Step 1b: SEO Data Collection Script

Run this bash module when SEO sections are selected. Save output to `seo_data.json`.

```bash
collect_seo_signals() {
  local URL=$1
  local BASE="${URL%/}"
  local DOMAIN=$(echo "$URL" | sed -E 's|https?://(www\.)?||' | cut -d'/' -f1)

  echo "=== REDIRECT CHAIN ==="
  curl -sI -L --max-redirs 10 -o /dev/null \
    -w "hops=%{num_redirects}\nfinal=%{url_effective}\nstatus=%{http_code}" "$URL"

  echo "=== CANONICAL ==="
  curl -s "$URL" | grep -i 'rel="canonical"' | head -1

  echo "=== ROBOTS META ==="
  curl -s "$URL" | grep -iE 'name="robots"|name="googlebot"' | head -3

  echo "=== X-ROBOTS HEADER ==="
  curl -sI "$URL" | grep -i "x-robots-tag"

  echo "=== TITLE ==="
  curl -s "$URL" | grep -oP '(?<=<title>)[^<]*'

  echo "=== META DESCRIPTION ==="
  curl -s "$URL" | grep -i 'name="description"' | grep -oP 'content="[^"]*"' | head -1

  echo "=== H1 ==="
  curl -s "$URL" | grep -oP '(?<=<h1[^>]*>)[^<]*' | head -3

  echo "=== H2 COUNT ===" && curl -s "$URL" | grep -c '<h2'
  echo "=== H3 COUNT ===" && curl -s "$URL" | grep -c '<h3'
  echo "=== WORD COUNT ===" && curl -s "$URL" | sed 's/<[^>]*>//g' | wc -w

  echo "=== IMAGES WITHOUT ALT ==="
  TOTAL_IMGS=$(curl -s "$URL" | grep -c '<img')
  NO_ALT=$(curl -s "$URL" | grep -oP '<img[^>]*>' | grep -cv 'alt="[^"]*"')
  echo "total=$TOTAL_IMGS missing_alt=$NO_ALT"

  echo "=== OG TAGS ===" && curl -s "$URL" | grep -i 'property="og:' | wc -l
  echo "=== TWITTER CARD ===" && curl -s "$URL" | grep -i 'name="twitter:card"' | head -1

  echo "=== SCHEMA TYPES ==="
  curl -s "$URL" | grep -oP '"@type"\s*:\s*"[^"]*"' | sort | uniq
  echo "=== SCHEMA COUNT ===" && curl -s "$URL" | grep -c 'application/ld+json'

  echo "=== ROBOTS TXT ===" && curl -s "$BASE/robots.txt" | head -80

  echo "=== SITEMAP LOCATIONS ==="
  for path in /sitemap.xml /sitemap_index.xml /sitemap/sitemap.xml /wp-sitemap.xml /news-sitemap.xml; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$path")
    COUNT=0; LASTMOD=""
    if [ "$STATUS" = "200" ]; then
      COUNT=$(curl -s "$BASE$path" | grep -c '<loc>')
      LASTMOD=$(curl -s "$BASE$path" | grep '<lastmod>' | head -1 | grep -oP '\d{4}-\d{2}-\d{2}')
    fi
    echo "path=$path status=$STATUS count=$COUNT lastmod=$LASTMOD"
  done

  echo "=== LLMS TXT ==="
  curl -s -o /dev/null -w "%{http_code}" "$BASE/llms.txt"
  curl -s "$BASE/llms.txt" | head -20

  echo "=== AI CRAWLERS IN ROBOTS ==="
  ROBOTS=$(curl -s "$BASE/robots.txt")
  for BOT in GPTBot ClaudeBot PerplexityBot anthropic-ai cohere-ai CCBot Bytespider YouBot; do
    RULE=$(echo "$ROBOTS" | grep -A2 -i "User-agent: $BOT" | head -3)
    echo "bot=$BOT rule=$RULE"
  done

  echo "=== MOBILE PARITY ==="
  DESKTOP_WORDS=$(curl -s "$URL" | sed 's/<[^>]*>//g' | wc -w)
  MOBILE_WORDS=$(curl -s -A "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15" \
    "$URL" | sed 's/<[^>]*>//g' | wc -w)
  echo "desktop=$DESKTOP_WORDS mobile=$MOBILE_WORDS"

  echo "=== HTTPS CHECK ==="
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://${DOMAIN}")
  HTTP_FINAL=$(curl -sI -L "http://${DOMAIN}" | grep "Location:" | tail -1)
  echo "http_status=$HTTP_STATUS redirect_to=$HTTP_FINAL"

  echo "=== WWW CHECK ==="
  WWW_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://www.${DOMAIN}")
  WWW_FINAL=$(curl -sI -L "https://www.${DOMAIN}" 2>/dev/null | grep "Location:" | tail -1)
  echo "www_status=$WWW_STATUS redirect_to=$WWW_FINAL"
}
```

Also extract from the existing PageSpeed API response: `is-crawlable`, `robots-txt`, `canonical`, `hreflang`, `structured-data`, `link-text`, `document-title`, `meta-description`, `image-alt`, `heading-order`, `font-size`, `tap-targets`

---

## Step 2: Report Structure — 15 Sections + 3 Gates + CTA

Sections marked *(optional)* are only included if selected in Step 0. Core sections are always included.

| # | Section ID | Section | Source | Component Type | Required? |
|---|-----------|---------|--------|----------------|-----------|
| 1 | `hero` | **Hero** | Screenshot + domain | Full-bleed hero with desktop screenshot, site grade, personalized headline | ✅ Core |
| 2 | `scorecard` | **Site Health Scorecard** | All data sources | `.grade-badge` grid (6 grades: Performance, SEO Health, MarTech, Copy/UX, Security + CRO) | ✅ Core |
| 3 | `cwv` | **Core Web Vitals** | PageSpeed API | `.cwv-display` three-column gauge (LCP, INP/FID, CLS) with pass/fail | ✅ Core |
| 4 | `martech` | **MarTech Stack Inventory** | site_inspection.json | `.tool-grid` with health dots, missing tools flagged | Optional |
| 5 | `privacy` | **Tracking & Privacy** | site_inspection.json | Consent mode status, cookie analysis, compliance flags | Optional |
| 6a | `seo-technical` | **Technical SEO** | curl/headers/robots/sitemap | Crawlability, redirects, canonical, noindex, sitemap health | Optional |
| 6b | `seo-onpage` | **On-Page SEO** | HTML parse + PSI audits | Title tag, meta desc, H1–H3, alt text, word count, OG tags | Optional |
| 6c | `seo-structured-data` | **Structured Data & Rich Results** | JSON-LD extraction | Schema inventory, rich result eligibility map, missing types | Optional |
| 6d | `seo-ai-search` | **AI Search Readiness** | robots.txt + llms.txt | AI crawler access grid, llms.txt, entity signals | Optional |
| 7 | `performance` | **Performance & Script Bloat** | PageSpeed third-party | Third-party inventory with blocking time, page weight breakdown | ✅ Core |
| 8 | `security` | **Security & Infrastructure** | teaser_data.json | SSL status, security headers grade, tech stack display | ✅ Core |
| — | `gate-1` | **Gate 1: Organic Search** | — | `.teaser-gate` locked section with GSC upsell | ✅ Core |
| 9 | `copy-audit` | **Copy Audit** | Playwright snapshots + screenshots | Headline, CTA, value prop, social proof analysis | Optional |
| 10 | `ux-audit` | **UX Audit** | Playwright snapshots + screenshots | Visual hierarchy, navigation, mobile, accessibility | Optional |
| 11 | `cro-audit` | **CRO Audit** | Playwright snapshots + screenshots | Conversion path, forms, trust signals, CTA placement | Optional |
| — | `gate-2` | **Gate 2: Analytics Deep-Dive** | — | `.teaser-gate` locked section with GA4 upsell | ✅ Core |
| — | `gate-3` | **Gate 3: Paid SEO** | — | `.teaser-gate` — shown when SEO section included, otherwise skip | Optional (show if SEO included) |
| — | `cta` | **Final CTA** | — | Full-width CTA section with Calendly booking | ✅ Core |

> **Scorecard note:** The scorecard always shows 6 grade badges. For any section not selected, show the badge as "—" (not scored) rather than hiding it — this signals there's more analysis available.

---

## Step 3: Scoring System

### Overall Site Grade (A–F)

Weighted composite displayed in hero and scorecard. When a section is skipped (not selected in Step 0), redistribute its weight proportionally across the included dimensions.

| Dimension | Weight | Source | Score Range |
|-----------|--------|--------|-------------|
| Performance | 20% | Lighthouse performance score (0–100) | Map to 0–100 |
| SEO Health | 20% | Composite SEO score (see SEO scoring below) | 0–100 |
| Core Web Vitals | 10% | CWV pass rate (3 metrics: LCP, INP/FID, CLS) | 0, 33, 67, or 100 |
| MarTech Maturity | 15% | Composite formula (see below) | 0–100 |
| Security | 15% | Security headers score (0–9) mapped to 0–100 | 0–100 |
| Copy Quality | 15% | Copy audit grade (see rubric below) | Map A=95, B=80, C=65, D=45, F=25 |
| UX Quality | 5% | UX audit grade (see rubric below) | Map A=95, B=80, C=65, D=45, F=25 |

**Grade thresholds:** A ≥ 85, B ≥ 70, C ≥ 55, D ≥ 40, F < 40

---

### SEO Health Score (Composite, 0–100)

Used as the "SEO Health" dimension in the overall grade. Made up of 4 sub-scores:

```
SEO Score = (
  Technical SEO Sub-Score  × 0.35 +
  On-Page Sub-Score        × 0.30 +
  Structured Data Score    × 0.20 +
  AI Search Score          × 0.15
)
```

If only some SEO sub-sections are collected, redistribute weights proportionally.

#### Technical SEO Sub-Score (0–100)

| Signal | Points |
|--------|--------|
| HTTPS enforced | +10 |
| Redirect chain ≤ 1 hop | +10 (2 hops: +5, 3+: 0) |
| robots.txt found, Googlebot not blocked | +10 |
| Canonical tag present + self-referencing | +15 |
| No noindex on production pages | +20 (**CRITICAL** — 0 if failing) |
| Sitemap found + >5 URLs | +10 |
| www/non-www consistency | +5 |
| Mobile content parity (<20% word count delta) | +10 |
| No crawl-delay directive | +5 |
| No X-Robots noindex header | +5 |

#### On-Page Sub-Score (0–100)

| Signal | Points |
|--------|--------|
| Title tag exists | +10 |
| Title tag 50–60 chars | +10 (40–49 or 61–70: +5) |
| Meta description exists | +10 |
| Meta description 140–160 chars | +10 (outside range: +5) |
| Single H1 present | +15 |
| H2s present (>2) | +10 |
| Heading order logical (PSI) | +10 |
| Image alt coverage ≥80% | +15 (50–79%: +8, <50%: 0) |
| Word count ≥300 | +10 |
| OG tags present | +5 |
| Link text quality pass (PSI) | +5 |

#### Structured Data Sub-Score (0–100)

| Signal | Points |
|--------|--------|
| Any schema present | +15 |
| Organization schema | +10 |
| WebSite schema | +5 |
| FAQPage or HowTo | +15 |
| BreadcrumbList | +10 |
| Article/Product (if relevant) | +10 |
| No malformed JSON-LD | +15 |
| Multiple schema types (≥3) | +10 |
| Schema nesting depth (≥2 levels) | +10 |

#### AI Search Sub-Score (0–100)

| Signal | Points |
|--------|--------|
| Googlebot allowed (prerequisite — 0 halves all other scores) | +20 |
| GPTBot allowed | +15 |
| PerplexityBot allowed | +15 |
| ClaudeBot allowed | +10 |
| CCBot allowed | +10 |
| llms.txt present | +15 |
| FAQPage schema present | +10 |
| Organization entity schema | +5 |

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
- **Max content width:** 720px centered within sections (left column in desktop layout)
- **Section padding:** 5rem top/bottom on desktop, 3rem on mobile
- **Grid layouts:** CSS Grid for score cards and CWV metrics
- **Responsive breakpoints:** 375px, 768px, 1024px, 1440px
- **Base64-embed screenshots** into the HTML for single-file delivery
- **Two-column desktop layout:** sticky sidebar TOC (240px) + main content (flex: 1), with `gap: 3rem`, inside a `max-width: 1200px` outer wrapper

### Teaser Header Banner (MANDATORY)

Every teaser report **must** open with a slim informational banner immediately below the `<body>` tag — before the main nav/cover — clearly marking this as a teaser. **The banner is context-setting only — no CTA button here.** The CTA lives at the end of the report where it earns it.

```html
<div class="teaser-header-banner">
  <div class="teaser-header-banner__inner">
    <div class="teaser-header-banner__eyebrow">📊 Teaser Report — Public Signals Only</div>
    <p class="teaser-header-banner__body">
      This report was built from publicly available data only. With access to <strong>GA4, Google Search Console, 
      PostHog</strong> (or whatever you use), this analysis can be dramatically more powerful.
    </p>
  </div>
</div>
```

```css
.teaser-header-banner {
  background: linear-gradient(135deg, #1c1917 0%, #292524 100%);
  border-bottom: 3px solid var(--amber-500);
  padding: 1.5rem 2rem;
}
.teaser-header-banner__inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.teaser-header-banner__eyebrow {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--amber-400);
}
.teaser-header-banner__body {
  font-size: 0.95rem;
  color: #d6d3d1;
  line-height: 1.6;
  max-width: 700px;
}
.teaser-header-banner__body strong { color: #fff; }
@media (max-width: 768px) {
  .teaser-header-banner { padding: 1rem; }
}
```

### Sticky Sidebar TOC

On desktop (≥1024px), the ToC renders as a **fixed left sidebar**. On mobile/tablet it collapses to a hidden off-canvas drawer toggled by a hamburger button.

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
  background: rgba(255,255,255,0.75);
  backdrop-filter: blur(8px);
  border: 1px solid var(--stone-200);
  border-radius: 10px;
  padding: 1.25rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.toc__title {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--stone-600);
  margin-bottom: 0.75rem;
}
.toc__link {
  display: block;
  font-size: 0.82rem;
  color: var(--stone-600);
  text-decoration: none;
  padding: 0.3rem 0.5rem;
  border-radius: 4px;
  margin-bottom: 0.15rem;
  transition: background 0.15s, color 0.15s;
  line-height: 1.4;
}
.toc__link:hover { background: var(--stone-100); color: var(--stone-900); }
.toc__link--active { 
  background: var(--amber-500); 
  color: var(--stone-900); 
  font-weight: 600;
}
.toc__main { flex: 1; min-width: 0; }
@media (max-width: 1023px) {
  .page-layout { display: block; padding: 0 1rem; }
  .toc { 
    display: none; 
    position: fixed; top: 0; left: 0; bottom: 0;
    width: 280px; z-index: 1000;
    border-radius: 0;
    max-height: 100vh;
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
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  }
}
```

HTML structure:
```html
<button class="toc__toggle" aria-label="Toggle navigation" onclick="this.closest('body').querySelector('.toc').classList.toggle('toc--open')">☰</button>
<div class="page-layout">
  <nav class="toc">
    <div class="toc__title">Contents</div>
    <a href="#executive-summary" class="toc__link">01 — Executive Summary</a>
    <!-- ... one link per section ... -->
  </nav>
  <main class="toc__main">
    <!-- all sections go here -->
  </main>
</div>
```

### ToC Implementation

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

**Lead gen framing:** The prospect is reading this because they care about growth. The GSC gate should make them feel like they're standing in front of a locked room full of their own data. The CTA isn't "hire us" — it's "let's look at this together."

- **Lock icon:** 🔒
- **Title:** "Your organic search data tells a story. We can't read it without GSC access."
- **Hook:** Use sitemap URL count from teaser_data.json: "Your site has {N} pages. We can see which ones are indexed — but not which ones are actually winning traffic, which are cannibalizing each other, or where you're ranking on page 2 and just need a nudge."
- **Preview items** (2–3 visible): Use real data from robots/sitemap analysis
- **What the full analysis delivers:** Brand vs non-brand split, keyword cannibalization, content refresh opportunities, exact queries driving impressions with no clicks
- **CTA:** "Book a 20-min call — we'll pull this up live →" → `https://calendly.com/rizwan-20/30min`

### Gate 2: Analytics Deep-Dive (GA4 Access)

**Lead gen framing:** Don't just say "we need GA4 access." Show them what they're flying blind on. Make the gap feel concrete.

- **Lock icon:** 🔒
- **Title:** "You have analytics. But is it telling you the truth?"
- **Hook:** Use tag count from site_inspection.json: "We found {N} tracking tags on your site. Tags installed ≠ tags working. Without a live GA4 review, you may be making decisions on data that's been silently broken for months."
- **Preview items:** Blurred score cards with "??/100" scores, greyed-out funnel visualization
- **What the full analysis delivers:** GA4 implementation score, attribution architecture review, ad platform signal loss, actual conversion funnel by step, real bounce rates vs. GA4 session inflation
- **CTA:** "Book a 20-min call — we'll walk through your GA4 live →" → `https://calendly.com/rizwan-20/30min`

### Gate 3: Paid SEO — Full Site Crawl + GSC Integration

Only show this gate when the SEO section is included. It appears after the AI Search Readiness sub-section.

- **Lock icon:** 🔒
- **Title:** "We crawled your homepage. Googlebot doesn't stop at one page."
- **Hook:** Use real sitemap count: "Your sitemap lists {N} pages. We can see the surface — technical issues, missing schema, on-page gaps. With a full crawl and GSC access, we'd tell you which {N÷4} of those pages are cannibalizing each other for your money keywords — and the exact fix order."
- **Preview items (show as blurred cards):**
  - Orphaned pages (no internal links pointing to them)
  - Redirect chains longer than 2 hops (kills PageRank)
  - Pages blocked by robots.txt that Google has already indexed
  - Crawl budget allocation across all {N} URLs
  - Keyword cannibalization report
- **What unlocks it:** SEO Audit — full Screaming Frog crawl + GSC integration + keyword cannibalization + schema validation + redirect chain audit + AI citation competitor gap + 90-day priority fix roadmap
- **Social proof:** "For one client, we identified 4,800–8,500 clicks/month in unrealized organic traffic — all from existing pages, no new content needed."
- **CTA:** "Unlock the full SEO Audit →" → Calendly link

#### Inline Micro-Upsell Cards (inside SEO sub-sections, not gated)

Each SEO sub-section ends with a small `.callout` card naming exactly what deeper access would reveal:

**Technical SEO micro-upsell:**
> 🔍 *Full Crawl + GSC Integration* — maps every orphaned page, redirect chain >2 hops, and pages already indexed that your robots.txt is trying to block. Part of the **SEO Audit**.

**On-Page micro-upsell:**
> 📝 *Content Depth & Keyword Alignment Audit* — checks every indexable page for thin content, duplicate titles, missing H1s, and keyword-to-page alignment. Part of the **SEO Content Audit**.

**Structured Data micro-upsell:**
> 🏷️ *Schema Validation & Implementation* — validates every schema block against Google's testing tool, fixes errors, and implements the missing types (FAQPage, BreadcrumbList, HowTo). Part of the **SEO Audit**.

**AI Search micro-upsell:**
> 🤖 *AI Citation Gap Analysis* — identifies which queries in your niche AI engines are answering, whether competitors are being cited instead of you, and how to reformat existing content for LLM extraction. Part of the **AI SEO Add-on** or **Full SEO Audit**.

---

## Step 7: Quality Checklist

Before finalizing, verify:

- [ ] **Step 0 intake completed** — sections to include were confirmed before any data collection
- [ ] **Only selected sections are included** — no placeholder or empty sections for skipped modules
- [ ] **All scores calculated from real data** — no placeholder text ("XX%", "N/A", "[TBD]")
- [ ] **Overall grade displayed** in hero section with large `.grade-badge--lg`
- [ ] **6 scorecard grades** all present — unscored sections show "—" not a fake grade
- [ ] **Core Web Vitals** show actual values with pass/fail indicators
- [ ] **MarTech grid** lists real tools detected (or explicitly flags "Not detected")
- [ ] **Copy/UX/CRO audit cards** contain specific, actionable findings — NOT generic advice
- [ ] **3 teaser gates** render with contextual hooks using real numbers from the data
- [ ] **All screenshots** Base64-embedded and rendering
- [ ] **Responsive** at 375px, 768px, 1440px — test all three
- [ ] **Mobile bottom CTA banner** visible on mobile only
- [ ] **Teaser header banner** — slim amber-bordered dark banner at top of `<body>`, eyebrow "📊 Teaser Report — Public Signals Only" + one-line body naming GA4/GSC/PostHog. **No CTA button in the banner** — CTA lives at the end of the report only
- [ ] **Sticky sidebar TOC** — renders as left sidebar on desktop (≥1024px), hidden off-canvas drawer on mobile; frosted glass panel (`rgba(255,255,255,0.75)` + `backdrop-filter: blur(8px)`); active link highlighted amber
- [ ] **ToC** with working scroll-tracking (Intersection Observer)
- [ ] **Single file** — no external dependencies except Google Fonts
- [ ] **File size** under 300KB (screenshots may push this; aim for <500KB max with screenshots)
- [ ] **Print-friendly** — hide ToC and banner for print
- [ ] **Calendly links** — all CTAs use `https://calendly.com/rizwan-20/30min` (not autonomoustech/30min or any other URL)
- [ ] **Dark/light section alternation** maintained
- [ ] **Company name** personalized throughout (not just "this site")
- [ ] **Finding box text** — `.finding` always has `color: var(--stone-800)` explicitly set to prevent white text bleeding from dark parent sections (amber-100, red-100, green-100 backgrounds must never render white text)
- [ ] **CTA button** — use `display: block; margin: 0 auto; max-width: 280px; white-space: normal; text-align: center` — do NOT use `<br>` hacks or `white-space: nowrap`. Let it wrap naturally. Add `box-shadow: 0 6px 24px rgba(245,158,11,0.35)` for visual weight.
- [ ] **Deployment** — ALWAYS deploy to `autonomous-proposals` repo → `docs.autonomoustech.ca`. Share externally via the share button (30-day expiry link via `share.autonomoustech.ca`). See TOOLS.md.
- [ ] **Hover states** — all interactive cards (`.audit-card`, `.tool-card`, `.score-card`, `.status-row`) must have smooth `0.2s` transitions with subtle `translateY(-1px)` or `translateY(-2px)` lift + shadow
- [ ] **Scroll reveal** — add `IntersectionObserver` fade-in-up (`.reveal` class, `opacity 0→1` + `translateY(28px)→0` at `0.6s ease`) on scorecard grid, CWV display, tool grid, stat strip, gates
- [ ] **Gate lock animation** — `.teaser-gate__lock` must have a `@keyframes lockPulse` amber glow ring animation (every 2.4s) to draw attention
- [ ] **Gate border/background** — use amber-400 dashed border + amber-100 gradient background on gates, not stone-300 — more attention-grabbing
- [ ] **Section padding** — use `6rem` top/bottom on regular sections, `8rem` on final CTA section. Scorecard cards: `2rem 1.25rem` padding, `1.25rem` gap.
- [ ] **ToC** — frosted glass panel: `background: rgba(255,255,255,0.7); backdrop-filter: blur(8px)` with border + box-shadow
- [ ] **No inline styles** — extract all repeated inline styles to CSS classes. Use utility classes (`mt-sm`, `mt-md`, `mt-lg`) for margin-top variations
- [ ] **Tool card HTML** — every `.tool-card__name` div must have a proper closing `>` before the text content: `<div class="tool-card__name">Tool Name</div>`. Missing `>` causes the entire MarTech grid to collapse. Always validate HTML structure after any automated edits.
- [ ] **Mobile scorecard grid** — collapses to 2-col at 600px, 1-col at 400px
- [ ] **Share button** — must be injected from `{client-name}/index.html` before `</body>` in every report

### SEO Section Checks (when SEO is included)

- [ ] **seo_data.json collected** — bash collection script was run before generating the report
- [ ] **4 SEO sub-sections present** — Technical SEO, On-Page, Structured Data, AI Search Readiness
- [ ] **Technical SEO signal grid** — shows real values: redirect hops, canonical status, noindex check, sitemap URL count, HTTPS/www consistency
- [ ] **noindex on production = red critical alert** — never downgrade this to a warning
- [ ] **On-Page section** — shows actual title tag text + char count, actual meta description text + char count, actual H1 text
- [ ] **Structured Data section** — shows real schema types found (or "None detected"), maps to rich result eligibility table
- [ ] **AI crawler grid** — shows GPTBot/ClaudeBot/PerplexityBot/CCBot as ✅ allowed or ❌ blocked based on actual robots.txt
- [ ] **llms.txt badge** — shows Found or Not Found based on actual check
- [ ] **Gate 3 hook uses real number** — sitemap page count or indexed page count from actual data
- [ ] **4 inline micro-upsell callouts** — one at the end of each SEO sub-section, naming the exact package
- [ ] **SEO Health grade badge** — appears in scorecard with composite SEO score
- [ ] **SEO scoring weights applied correctly** — Technical 35%, On-Page 30%, Structured Data 20%, AI Search 15%

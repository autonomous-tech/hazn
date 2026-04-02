---
name: ConversionIQ — CRO Audit
description: Run a comprehensive landing page conversion audit covering copywriting, design, and UX/experience. Three tiers (Free / Standard / Deep Dive) with brand config support. Generates a branded HTML audit report with scores, before/after recommendations, implementation roadmap, CVR projections, and A/B testing opportunities. Styled with Stone/Amber design system (Source Serif 4 + Inter, stone/amber palette). Brand tokens in references/brand.md.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
---

## Step 0: Tier & Brand Intake

Before collecting any data, ask everything in ONE message:

> A few quick questions before I start:
>
> 1. **Tier:** Free / Standard / Deep Dive?
> 2. **Brand:** Who is this report for?
>    - (a) Autonomous delivery (default)
>    - (b) Partner white-label — which partner slug?
>    - (c) End-customer branded — provide: company name, primary colour, CTA URL
> 3. **Primary conversion goal:** demo / signup / purchase / other?
> 4. **Client email** (optional)
>
> [Deep Dive only — also ask:]
> 5. GA4 Property ID (for real funnel data)
> 6. PostHog access (for session data, if available)
> 7. 2–3 competitor landing pages to benchmark against

After intake:
- Load brand config from ~/hazn/brands/{slug}.json. Default: ~/hazn/brands/autonomous.json
- Standard does NOT require platform access — runs from public page analysis only
- Deep Dive AND access NOT provided: offer Standard fallback — "Without GA4 access I cannot pull real funnel data. Want me to run Standard instead?"
- Set TIER variable. Proceed to Step 0b.

---

## Step 0b: Tier Execution Gate

**TIER = Free:**
- Analyse homepage only: headline + value prop review, CTA audit (count, placement, strength), top 3 conversion blockers flagged, overall conversion score
- Output: score + 1 finding in full, locked rows for rest
- Deliver immediately (3–24 hours)

**TIER = Standard:**
- Run full audit (all existing process steps) from public signals only
- Three pillars: Copy + Design + UX (remove SEO pillar — SEO is SiteScore)
- Set human_review_required = true
- Delivery: 24–48 hours

**TIER = Deep Dive:**
- Verify GA4 access provided. If missing → offer Standard fallback.
- Run full Standard audit PLUS Deep Dive additions:
  - Full funnel drop-off analysis using real GA4 data
  - Session data review if PostHog available
  - Competitor landing page benchmarks (web_fetch + screenshot 2-3 competitors)
  - Full A/B test plan with sequencing by traffic and impact
  - ROI projection using real traffic data from GA4
- Load ab-test-setup skill for the A/B plan section
- Set human_review_required = true, call_required = true
- Delivery: 3–5 business days

---

# ConversionIQ — CRO Audit

> **When conducted without analytics access: this is a lead gen tool.**

A free tier conversion audit (public signals only) serves a dual purpose: it delivers real, actionable findings AND builds the case for a deeper paid engagement. Every section should make the prospect think "these people already understand my site — imagine what they'd find with full access."

Generate a comprehensive, branded landing page conversion audit covering three pillars: Copywriting, Design, and UX/Experience — plus a measurement framework for validating improvements.

## Step 0c: Audience — Ask First

**Before anything else, ask the audience question.** Read `~/hazn/skills/references/audience-routing.md` for the full routing spec. Then ask:

> **Who is this report for?**
>
> 1. 👔 **Business Executive** — ROI framing, plain English, impact/effort badges, no jargon
> 2. 🔧 **Technical Team** — Full metrics, code examples, implementation detail
> 3. 📋 **Both** — Executive summary first, then technical appendix

Apply the appropriate output mode throughout the report and all findings.

---

## Process

### 1. Gather Target Info

Ask the user:
- **URL** to audit
- **Primary conversion goal** (leads, signups, purchases, bookings)
- **Target audience** (who are they selling to?)
- **Price point** (affects design expectations — $50 product vs $50K B2B service)
- **Current traffic volume** (affects A/B testing feasibility)
- **Is this for a client or internal?** (affects tone and framing)

### 2. Research the Page

```bash
# Fetch the page content
web_fetch <url> --extractMode markdown

# Check competitors if relevant
web_search "<industry> landing page best practices"
```

Analyze:
- Full page copy (headline, subhead, body, CTAs, social proof, guarantees)
- Page structure (sections, flow, length)
- SEO elements (meta, headings, schema, technical)
- Design signals (can infer from HTML structure, classes, frameworks)

If user provides screenshots or a separate audit doc, incorporate those findings.

### 3. Score Each Pillar

Score on a 1-10 scale with justification:

| Pillar | What to Evaluate |
|--------|-----------------|
| **Copywriting** | Headline clarity, value prop, CTA strength, social proof, urgency, guarantee placement, copy length, specificity of claims |
| **Design** | Visual hierarchy, CTA visibility, color contrast, typography, whitespace, brand consistency, premium feel, layout and composition |
| **UX/Experience** | Mobile responsiveness, page load time, navigation clarity, form UX, scroll depth engagement, interaction feedback, accessibility basics, user flow friction |

### 4. Identify Issues & Recommendations

For each pillar, document:
- **Strengths** (what's working — always lead with positives)
- **Critical Issues** (numbered, with before/after examples)
- **Quick Wins** (can be done this week)
- **Short-term Improvements** (2-4 weeks)
- **Long-term Recommendations** (1-3 months)

### 5. Build Implementation Roadmap

Organize all recommendations into a prioritized table:

| Timeframe | Action | Category | Impact | Testable? |
|-----------|--------|----------|--------|-----------|
| Immediate | ... | Copy/Design/UX | Very High/High/Medium | Yes/No |

---

## A/B Testing Recommendations

For each significant recommendation, evaluate whether it's testable:

### Test Prioritization Matrix

| Recommendation | Hypothesis | Test Type | Traffic Needed | Priority |
|----------------|------------|-----------|----------------|----------|
| New headline | Specificity increases clarity → +15% CTR | A/B | ~3k visitors | High |
| CTA button redesign | Higher contrast → +10% clicks | A/B | ~5k visitors | High |
| Social proof placement | Above fold → +8% trust signals | A/B | ~4k visitors | Medium |

### Hypothesis Framework for Each Test

Structure recommendations as testable hypotheses:

```
Because [observation from audit],
we believe [specific change]
will cause [expected outcome]
for [target audience].
We'll know this is true when [metric] improves by [target %].
```

### B2B Testing Considerations

For B2B clients (lower traffic, higher deal value):
- **Longer test durations** — Account for weekly business cycles
- **Micro-conversions** — Track scroll depth, time on page, PDF downloads
- **Qualitative signals** — Demo request quality, sales feedback
- **Sequential testing** — When traffic is too low for simultaneous tests

### Quick Reference: Sample Sizes

| Baseline CVR | 10% Lift | 20% Lift | 50% Lift |
|--------------|----------|----------|----------|
| 1% | 150k/variant | 39k/variant | 6k/variant |
| 3% | 47k/variant | 12k/variant | 2k/variant |
| 5% | 27k/variant | 7k/variant | 1.2k/variant |
| 10% | 12k/variant | 3k/variant | 550/variant |

**Low-traffic B2B recommendation:** Focus on bolder changes (50%+ lift potential) or use sequential testing.

---

## Measurement Framework

### Tracking Requirements Checklist

Before implementing changes, ensure tracking is in place:

| Event | Required For | Implementation |
|-------|--------------|----------------|
| `page_view` with UTM params | Attribution | GA4 auto / PostHog |
| `cta_clicked` | Button performance | Custom event |
| `form_started` | Funnel analysis | Custom event |
| `form_submitted` | Conversion tracking | Custom event |
| `scroll_depth` | Engagement | GA4 enhanced / Custom |
| `time_on_page` | Content quality | GA4 auto |

### Conversion Funnel Setup

Define the funnel for each conversion goal:

```
Page View → CTA Click → Form Start → Form Submit → Thank You Page
   │           │            │             │              │
  100%        40%          25%           15%            12%
```

Track drop-off at each stage to identify optimization priorities.

### Key Metrics to Monitor

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Primary CVR | X% | +Y% | GA4 Conversion |
| Bounce Rate | X% | -Y% | GA4 |
| Avg. Session Duration | Xs | +Ys | GA4 |
| Scroll Depth (75%+) | X% | +Y% | Custom Event |
| CTA Click Rate | X% | +Y% | Custom Event |

### Reporting Cadence

- **Week 1:** Baseline established, tracking verified
- **Week 2-4:** Quick wins implemented, monitoring
- **Month 2:** Short-term improvements, first A/B test results
- **Month 3:** Full optimization cycle, ROI calculation

---

## Project CVR Impact

Estimate conversion rate improvements:
- Current state (based on industry benchmarks)
- After quick wins (+X%)
- After short-term improvements (+Y%)
- After full optimization with validated tests (+Z%)

Use industry benchmarks as reference. See `references/benchmarks.md`.

### ROI Projection Template

```
Current State:
- Monthly visitors: [X]
- Conversion rate: [Y%]
- Conversions/month: [Z]
- Avg. deal value: [$A]
- Monthly revenue: [$B]

After Optimization:
- Projected CVR: [Y + improvement%]
- Projected conversions: [Z × multiplier]
- Projected revenue lift: [$C]
- Annual impact: [$C × 12]
```

---

## Generate HTML Report

**Brand config:** Load from Step 0 brand config.
- Use brand_config.cta_url for all Calendly links (default: https://calendly.com/rizwan-20/30min)
- Use brand_config.company_name in header/footer
- Use brand_config.primary_color for accent elements
- If brand_config.hide_autonomous = true: remove all "Autonomous Technology Inc." mentions
Report product name: always use "ConversionIQ" not "Conversion Audit"

Generate a single-file HTML report from scratch using the **Stone/Amber design system**. Follow `references/brand.md` for all design tokens. Do NOT use any legacy template — build fresh each time.

### Design System — Stone/Amber Palette

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
/* Google Fonts — REQUIRED */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap');

/* Headings: 'Source Serif 4', Georgia, serif */
/* Body:     'Inter', system-ui, -apple-system, sans-serif */
```

### CTA Button (MANDATORY)

```css
.cta-btn {
  display: block;
  margin: 0 auto;
  max-width: 280px;
  white-space: normal;
  text-align: center;
  padding: 1rem 2rem;
  background: var(--amber-500);
  color: var(--stone-900);
  font-weight: 700;
  font-size: 1.05rem;
  border-radius: 8px;
  text-decoration: none;
  box-shadow: 0 6px 24px rgba(245,158,11,0.35);
  transition: background 0.2s, transform 0.2s;
}
.cta-btn:hover { background: var(--amber-600); transform: translateY(-2px); }
```

All CTAs link to: **`https://calendly.com/rizwan-20/30min`** — no exceptions. No email links. No `autonomoustech.ca/contact`.

### Report Sections

Key sections in the HTML:
1. **Hero** — Client name, URL, date, conversion goal
2. **Overall Scores** — 4 score blocks (Copy, Design, UX, Overall)
3. **CVR Projections** — 3-column: Current → Quick Wins → Full Redesign
4. **Top 5 Quick Wins** — Numbered cards with before/after comparisons
5. **Part 1: Copywriting Audit** — Strengths (green cards) + Issues (red cards with before/after)
6. **Part 2: Design Audit** — Visual hierarchy, layout, CTA visibility + specific issues
7. **Part 3: UX/Experience Audit** — Mobile responsiveness, user flow, interaction friction + specific issues
8. **Part 4: A/B Testing Roadmap** — Prioritized experiments with hypotheses
9. **Part 5: Measurement Framework** — Tracking checklist + funnel visualization
10. **Implementation Roadmap** — Prioritized tables by timeframe
11. **Conclusion** — Hero-style closing with single biggest win + risk + CVR potential
12. **Final CTA Section** — Full-width, dark background (`var(--stone-900)`). Calendly CTA button + 3 trust signals below it. No other links in this section.

### Micro-Upsell Callout Pattern (end of each section)

```html
<div class="callout callout--info" style="color: var(--stone-800);">
  🔍 <strong>Want the full picture?</strong> With analytics access, we'd show you
  [specific deeper insight]. Part of the <strong>ConversionIQ</strong> engagement.
  <a href="https://calendly.com/rizwan-20/30min" style="color: var(--amber-600); font-weight: 600;">
    Book a 20-min call →
  </a>
</div>
```

### Final CTA Section Spec

The last section of every report must be a full-width dark-background CTA block:

```html
<section style="padding: 8rem 0; background: var(--stone-900); text-align: center;">
  <p style="color: var(--amber-400); font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;">
    Ready to Fix This?
  </p>
  <h2 style="color: #fff; font-family: 'Source Serif 4', Georgia, serif; font-size: 2rem; margin: 0.75rem 0 1rem;">
    Your CRO roadmap starts with a 20-min call
  </h2>
  <p style="color: var(--stone-300); max-width: 560px; margin: 0 auto 2.5rem; line-height: 1.6;">
    Walk through these findings live. We'll prioritize the fixes that move the needle fastest for your site.
  </p>
  <a href="https://calendly.com/rizwan-20/30min" class="cta-btn">
    Book a 20-min call — we'll walk through the fixes live →
  </a>
  <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 3rem; flex-wrap: wrap;">
    <span style="color: var(--stone-400); font-size: 0.875rem;">✓ No commitment required</span>
    <span style="color: var(--stone-400); font-size: 0.875rem;">✓ Walk away with a prioritized fix list</span>
    <span style="color: var(--stone-400); font-size: 0.875rem;">✓ We've improved CVR for 30+ brands</span>
  </div>
</section>
```

**CTA copy options** (use one per report, vary across clients):
- "Book a 20-min call — we'll walk through the fixes live →"
- "Your CRO roadmap starts with a 20-min call →"
- "Let's turn these findings into a conversion plan →"
- "See which fix to tackle first — book a 20-min call →"

**All CTAs in the report must link to:** `https://calendly.com/rizwan-20/30min`
No `autonomoustech.ca/contact`, no email links, no generic contact forms.

---

## Deep Dive Additions (run after standard audit when TIER = Deep Dive)

### Real Funnel Analysis
Using GA4 data provided:
- Map the actual funnel: landing page → key interaction → conversion event
- Show real drop-off % at each step (not benchmark estimates)
- Identify biggest drop-off point — this becomes Priority #1 fix

### Session Data Review (if PostHog available)
- Review session recordings for the top 3 pages by traffic
- Document: where do users scroll to? where do they drop off? what do they click that leads nowhere?
- Surface 3–5 behavioural findings not visible from page analysis alone

### Competitor Benchmarks
For each competitor URL provided:
- Fetch page via web_fetch
- Capture screenshot via browser tool
- Compare: headline strength, CTA visibility, social proof placement, page length, trust signals
- Output: side-by-side comparison table with ConversionIQ findings in context

### A/B Test Plan
Load ab-test-setup skill.
Build full A/B test plan:
- Tests sequenced by: (1) traffic available, (2) estimated impact, (3) implementation effort
- Each test: hypothesis, variant description, success metric, traffic requirement, priority

### ROI Projection
Using real GA4 traffic data:
- Current monthly visitors + current CVR = current conversions
- Apply projected CVR improvements from audit findings
- Show: if we fix the top 3 issues → estimated uplift in conversions → revenue impact at average deal value

---

## Checkpoints (Human-in-Loop)

**CHECKPOINT 1:** After scoring all three pillars (Copywriting, Design, UX/Experience)
- Present scores and top 3 issues per pillar
- Ask: "Do these priorities align with your goals? Any areas to emphasize?"

**CHECKPOINT 2:** Before finalizing A/B test recommendations
- Present proposed tests with traffic requirements
- Ask: "Given your traffic volume, which tests are feasible? Want to adjust priorities?"

**CHECKPOINT 3:** Before generating final report
- Present outline and key recommendations
- Ask: "Ready to generate the full HTML report?"

---

## Free Tier (Public Signals Only)

When the audit is conducted **without analytics access** (GA4, GSC, PostHog, Hotjar, or platform data not provided), the report is a **free tier** report and MUST include:

### 1. Free Tier Header Banner (mandatory, top of `<body>`)

A slim informational banner immediately before the cover section. **Context-setting only — no CTA button.** The CTA lives at the end of the report where it has been earned by the content.

```html
<div class="free-tier-header-banner">
  <div class="free-tier-header-banner__inner">
    <div class="free-tier-header-banner__eyebrow">📊 Free Tier Report — Public Signals Only</div>
    <p class="free-tier-header-banner__body">
      This report was built from publicly available data only. With access to <strong>GA4, Google Search Console, 
      PostHog</strong> (or whatever you use), this analysis can be dramatically more powerful.
    </p>
  </div>
</div>
```

Style: dark (`#1c1917`) background, `3px solid` amber bottom border. No CTA button in the banner. CSS classes use `free-tier-header-banner` prefix.

### 2. Methodology Disclaimer Section

Include a "How This Report Was Built" section early in the report (after the executive summary scores):

> **Methodology Note:** This audit was conducted using publicly available signals only — page source inspection, browser-observable tracking calls, public sitemap and robots.txt, and manual UX review. Where analytics or platform data (GA4, GSC, Hotjar, CRM) was unavailable, findings are directional and based on industry benchmarks. Revenue and conversion estimates are illustrative ranges, not projections.
>
> **What changes with full access:** Form completion rates, actual funnel drop-off by step, real bounce rates, keyword rankings, and attribution accuracy. [Book a call](https://calendly.com/rizwan-20/30min) to unlock the full picture.

### 3. Upsell Callouts in Each Track

At the end of each audit track section, include a brief upsell callout:

```html
<div class="upsell-callout">
  <span class="upsell-callout__icon">🔒</span>
  <div>
    <strong>Want to go deeper on [Design / UX / CRO / Copy]?</strong>
    With GA4 + GSC access, we can show you exactly where users drop off, which pages are cannibalizing each other, 
    and what your top converting traffic sources actually are.
    <a href="https://calendly.com/rizwan-20/30min">Book a 20-min call →</a>
  </div>
</div>
```

### 4. Sticky TOC Sidebar

All audit reports (free tier or full) must include a sticky sidebar Table of Contents:
- Desktop (≥1024px): left sidebar, `240px` wide, `position: sticky; top: 2rem`
- Mobile: hidden off-canvas, toggled by hamburger button
- Frosted glass: `background: rgba(255,255,255,0.75); backdrop-filter: blur(8px)`
- Active link: amber background highlight
- Intersection Observer tracks current section

### 5. Caveat Language for Estimates

In free tier mode, all revenue/conversion estimates **must** use directional language:
- ❌ "This will increase revenue by $50K–$200K"
- ✅ "Based on industry benchmarks for comparable B2B agencies, this could represent significant revenue impact — exact numbers require your actual traffic and close rate data"
- ❌ "+15–25% contact page visits"
- ✅ "Directional uplift expected — establish your baseline first"

---

## Deployment

After generating the report HTML:

1. **Save** to `~/autonomous-proposals/audits/{client-slug}-conversioniq-{date}.html`
2. **Commit and push** to `https://github.com/autonomous-tech/autonomous-proposals` (main branch)
3. **Cloudflare Pages auto-deploys** to `https://docs.autonomoustech.ca/audits/{client-slug}-conversioniq-{date}.html`
4. **Use the SHARE button** (auto-injected by GitHub Actions) to generate a 30-day shareable link via `share.autonomoustech.ca`
5. **Share the link with the client** — no login required

```bash
# Full deployment flow
CLIENT_SLUG="acme-corp"
DATE=$(date +%Y-%m-%d)
FILENAME="${CLIENT_SLUG}-conversioniq-${DATE}.html"

# 1. Write the file
# (agent writes HTML to this path)

# 2. Commit and push
cd ~/autonomous-proposals
git add "audits/${FILENAME}"
git commit -m "Agent Hazn: ConversionIQ for ${CLIENT_SLUG} (${DATE})"
git push origin main

# 3. Cloudflare Pages deploys automatically
# Live at: https://docs.autonomoustech.ca/audits/${FILENAME}
```

**⚠️ Audits ALWAYS go to `autonomous-proposals` → `docs.autonomoustech.ca`. Never to `landing-pages`.**
Audit reports contain confidential client analysis. Share externally via the 📤 SHARE button only (generates 30-day expiry link via `share.autonomoustech.ca`).

**Share button:** Copy from `{client-name}/index.html` in `autonomous-proposals`. Must be present before `</body>`.

**Preview locally:** Use `canvas action=present` to display the report inline before deploying.

---

---

## Quality Checklist

Before delivering the final HTML report, verify every item below:

### CTA & Links
- [ ] **Calendly links** — ALL CTAs use `https://calendly.com/rizwan-20/30min` — no exceptions. No `autonomoustech.ca/contact`, no email links.
- [ ] **Final CTA section** — full-width dark background, Calendly CTA button, 3 trust signals present
- [ ] **CTA copy** — implementation-hire framing (e.g. "Book a 20-min call — we'll walk through the fixes live →"), not generic "Contact Us"

### UX & Interactivity
- [ ] **Scroll reveal** — `IntersectionObserver` fade-in-up on score cards, findings grids, before/after sections (`.reveal` class: `opacity 0→1` + `translateY(28px)→0` at `0.6s ease`)
- [ ] **Hover states** — all finding cards and score cards have `0.2s` transitions with subtle lift (`translateY(-2px)` + shadow increase)
- [ ] **Mobile bottom CTA banner** — fixed bottom strip visible on mobile only (`display: none` → `display: flex` at `max-width: 768px`), amber CTA button linking to Calendly
- [ ] **Sticky sidebar TOC** — desktop: left sidebar `240px wide`, `position: sticky; top: 2rem`; mobile: hidden off-canvas, toggled by hamburger; frosted glass (`rgba(255,255,255,0.75)` + `backdrop-filter: blur(8px)`)
- [ ] **TOC active link** — Intersection Observer tracks current section, active link highlighted with amber (`background: var(--amber-500); color: var(--stone-900)`)

### File & Output
- [ ] **Single file** — no external dependencies except Google Fonts. All images/screenshots Base64-embedded.
- [ ] **Responsive** at 375px, 768px, 1440px — manually verify all three breakpoints
- [ ] **Print-friendly** — `@media print` hides TOC, banners, and sticky elements; `break-inside: avoid` on cards/tables

### Content Rules
- [ ] **No time estimates on fixes** — use effort levels only: **Low / Medium / High**. Never say "this takes 30 mins", "easy fix", "a quick 2-hour change", or any duration phrasing.
- [ ] **Before/After for every issue** — don't just flag problems; show the improved version
- [ ] **Scores justified** — every pillar score has a written rationale, not just a number
- [ ] **Quantities, not vague claims** — "3 CTAs compete for attention" not "CTAs are unclear"

### Design Integrity
- [ ] **Stone/Amber tokens intact** — Source Serif 4 + Inter, stone/amber palette. CSS variables only, no old parchment/vermillion/fraunces tokens.
- [ ] **Dark section text** — any light-background component inside a dark section must have `color: var(--stone-800)` explicitly set to prevent white-on-white
- [ ] **Share button** — injected from `{client-name}/index.html` in `autonomous-proposals`, present before `</body>`

---

## Key Principles

- **Always lead with strengths.** Clients need to feel validated before hearing criticism.
- **Before/After for everything.** Don't just say "this is bad" — show what "good" looks like.
- **Quantify impact.** Use CVR projections and revenue lift estimates. Never time-to-implement estimates.
- **No time estimates on fixes.** Never say "this takes 30 mins" or "easy 2-hour fix." Time is subjective and condescending — the client's team or context may be completely different. State effort level (Low/Medium/High) without attaching a duration.
- **Make it actionable.** Every recommendation should be implementable, not theoretical.
- **Make it testable.** Frame recommendations as hypotheses when traffic allows.
- **Design for the price point.** A $50K service needs a premium-feeling audit. A $20 product can be simpler.
- **Print-friendly.** Include A4 print styles with `break-inside: avoid` on cards/tables.

---

## Related Skills

- `ab-test-setup` — For designing and implementing experiments
- `analytics-tracking` — For setting up measurement infrastructure
- `b2b-marketing-ux` — For B2B-specific conversion principles

---

## References

- `references/brand.md` — Colors, fonts, CSS variables, component styles
- `references/audit-framework.md` — Detailed scoring criteria for each pillar
- `references/benchmarks.md` — Industry CVR benchmarks by vertical

## Assets

- Reports are generated from scratch using the Stone/Amber design system — no base template file needed.

---
name: website-audit
description: Comprehensive website audit combining Copy, SEO, Visual/UI, and CRO analysis. Always asks which audit types to run, what analytics access exists, and market context before starting. Outputs branded HTML reports using Autonomous brand guide.
---

# Website Audit Skill

Comprehensive audit framework for websites (Shopify, custom, any platform). Combines multiple audit types into a single workflow with branded deliverables.

## When to Use

- Auditing prospect/client websites
- Pre-sales value-add deliverables
- Client optimization roadmaps
- Competitive analysis

---

## MANDATORY: Discovery Workflow

**NEVER skip this section. ALWAYS ask these questions before starting any audit work.**

### Step 0: Audience — Ask First

**This is the very first question. Ask before anything else.** Read `~/hazn/skills/references/audience-routing.md` for the full routing spec. Then ask:

> **Who is this report for?**
>
> 1. 👔 **Business Executive** — ROI framing, plain English, impact/effort badges, no jargon
> 2. 🔧 **Technical Team** — Full metrics, code examples, implementation detail
> 3. 📋 **Both** — Executive summary first, then technical appendix

Apply the appropriate output mode throughout **all** audit types selected.

---

### Step 1: Audit Type Selection

Ask the user:

> **Which audit types do you want to run?** (Select all that apply)
>
> 1. **📝 Copy Audit** — Headlines, CTAs, value propositions, persuasion techniques
> 2. **🔍 SEO Audit** — Meta tags, structured data, technical SEO, content optimization
> 3. **🎨 Visual/UI Audit** — Design, hierarchy, accessibility, cognitive load, UX patterns
> 4. **📈 CRO Audit** — Conversion flow, trust signals, checkout optimization, funnel analysis
>
> Reply with numbers (e.g., "1, 3, 4") or "all"

Wait for response before proceeding.

### Step 2: Target Information

Ask the user:

> **Target details:**
>
> - **Website URL:** (e.g., example.com)
> - **Platform:** Shopify / WooCommerce / Custom / Other?
> - **Industry/Vertical:** (fashion, beauty, electronics, home, food, health, luxury, B2B, SaaS, etc.)
> - **Price point:** Budget (<$50 avg) / Mid-market ($50-200) / Premium ($200-500) / Luxury ($500+)?
> - **Primary markets:** (Pakistan, UAE, US, UK, etc.)

Wait for response before proceeding.

### Step 3: Analytics Access

Ask the user:

> **What analytics/data access do you have?** (helps depth of analysis)
>
> - [ ] CDP access (RudderStack/Segment) — source ID?
> - [ ] PostHog access — project ID?
> - [ ] Shopify Admin API — store domain + token?
> - [ ] Google Analytics — view access?
> - [ ] Hotjar/Clarity — heatmaps available?
> - [ ] None — visual audit only
>
> If none, I'll do a visual-only audit from screenshots.

Wait for response before proceeding.

### Step 4: Known Context (Optional)

Ask if relevant:

> **Any known issues or focus areas?**
>
> - Current CVR if known?
> - Specific pages to prioritize?
> - Known pain points?
> - Competitor URLs to compare against?

---

## Audit Execution

Once discovery is complete, execute the selected audit types.

### Load Required Skills

For each selected audit type, load the corresponding skill:

| Audit Type | Skill to Load | Location |
|------------|---------------|----------|
| Copy Audit | landing-page-copywriter | `~/hazn/skills/landing-page-copywriter/SKILL.md` |
| SEO Audit | seo-audit | `~/hazn/skills/seo-audit/SKILL.md` |
| Visual/UI Audit | ui-audit | `~/hazn/skills/ui-audit/SKILL.md` |
| CRO Audit | shopify-revenue-audit (or this skill's CRO section) | `~/hazn/skills/shopify-revenue-audit/SKILL.md` |

Also apply:
- **Brand styling:** Use client's brand guidelines if provided, or professional default styling

### Screenshot Capture (All Audit Types)

Capture screenshots for analysis:

```
browser action=start profile=hazn
browser action=navigate targetUrl="{URL}"

# Desktop (1440px)
browser action=screenshot fullPage=true  # → homepage-desktop.jpg

# Mobile (390px) - resize viewport
browser action=act request='{"kind":"resize","width":390,"height":844}'
browser action=screenshot fullPage=true  # → homepage-mobile.jpg
```

Required pages (adjust based on site type):
- Homepage
- Key landing page / Product page
- Pricing / Cart page (if applicable)
- Checkout / Signup flow (if accessible)

Save to: `projects/{client}/audits/{site-name}-assets/`

---

## Audit Type Details

### 📝 Copy Audit

Evaluate:
- **Headlines:** Clear, benefit-driven, attention-grabbing?
- **Value proposition:** Unique, specific, compelling?
- **CTAs:** Action-oriented, high-contrast, urgency?
- **Body copy:** Scannable, benefits > features, social proof?
- **Objection handling:** FAQs, guarantees, risk reversal?

Frameworks to apply:
- PAS (Problem-Agitate-Solution)
- AIDA (Attention-Interest-Desire-Action)
- StoryBrand clarity

Output: Before/after copy recommendations with specific rewrites.

### 🔍 SEO Audit

Evaluate:
- **Meta tags:** Title, description, OG tags
- **Headings:** H1-H6 hierarchy, keyword usage
- **Technical:** Page speed, mobile-friendliness, Core Web Vitals
- **Content:** Keyword density, internal linking, content depth
- **Structured data:** Schema markup, rich snippets
- **Indexability:** Robots.txt, sitemap, canonical tags

Tools: Use `web_fetch` for HTML analysis, Lighthouse for performance.

Output: Technical checklist with priority fixes.

### 🎨 Visual/UI Audit

Load `ui-audit` skill and evaluate:
- **Visual hierarchy:** F-pattern/Z-pattern, focal points
- **Accessibility:** Contrast, touch targets, screen reader
- **Cognitive load:** Information density, decision fatigue
- **Consistency:** Design system adherence, spacing, typography
- **Mobile UX:** Thumb zones, tap targets, scroll depth

Output: Annotated screenshots with UX recommendations.

### 📈 CRO Audit

Evaluate:
- **Trust signals:** Reviews, badges, guarantees, social proof
- **Friction points:** Form fields, checkout steps, loading time
- **Urgency/scarcity:** Stock levels, countdown timers, limited offers
- **Payment options:** Local methods, BNPL, express checkout
- **Cart optimization:** Cross-sells, upsells, abandonment recovery

Market-specific (Pakistan/MENA):
- WhatsApp button (critical)
- COD visibility
- Local payment methods
- Free shipping threshold

Output: Prioritized issue list with CVR impact estimates.

---

## Report Generation

### Apply Professional Styling — Stone/Amber Design System

Use the **Stone/Amber design system** for ALL audit HTML reports. Do not use Fraunces/DM Sans/parchment. The only exception is if a client provides brand guidelines that override this — even then, maintain the CTA and UX interaction patterns.

#### Color Tokens

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

#### Typography

```css
/* Google Fonts import — REQUIRED */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap');

/* Headings */
font-family: 'Source Serif 4', Georgia, serif;

/* Body */
font-family: 'Inter', system-ui, -apple-system, sans-serif;
```

#### Section Padding

- Regular sections: `padding: 6rem 0` (top/bottom)
- Final CTA section: `padding: 8rem 0` (top/bottom)
- Score cards: `padding: 2rem 1.25rem`, gap: `1.25rem`

#### CTA Button Style (MANDATORY)

All CTA buttons must use this exact styling — no exceptions:

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

#### Final CTA Section (MANDATORY)

Every audit report must close with a full-width dark section:

```html
<section class="section section--dark" style="padding: 8rem 0; background: var(--stone-900); text-align: center;">
  <p class="section__label" style="color: var(--amber-400);">Ready to Fix This?</p>
  <h2 class="section__title" style="color: #fff; font-family: 'Source Serif 4', Georgia, serif;">
    Let's turn these findings into fixes
  </h2>
  <p style="color: var(--stone-300); max-width: 560px; margin: 1rem auto 2.5rem;">
    Book a 20-min call and we'll walk through your findings live — and map out exactly what to tackle first.
  </p>
  <a href="https://calendly.com/rizwan-20/30min" class="cta-btn">
    Book a 20-min call — we'll walk through your findings live →
  </a>
  <!-- 3 trust signals -->
  <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 3rem; flex-wrap: wrap;">
    <span style="color: var(--stone-400); font-size: 0.875rem;">✓ No commitment required</span>
    <span style="color: var(--stone-400); font-size: 0.875rem;">✓ We come with your audit findings loaded</span>
    <span style="color: var(--stone-400); font-size: 0.875rem;">✓ Implementation roadmap included</span>
  </div>
</section>
```

> **CTA copy variants** (pick whichever fits the context):
> - "Book a 20-min call — we'll walk through your findings live →"
> - "Your implementation roadmap starts here →"
> - "Let's turn these findings into fixes — book a 20-min call →"
>
> ALL CTAs link to: `https://calendly.com/rizwan-20/30min` — no exceptions. Do NOT use generic email links or `autonomoustech.ca/contact`.

> ⚠️ **Color override required:** Always set `color: var(--stone-800)` explicitly on `.finding`, `.before`, `.after` boxes — these use light backgrounds (amber-100, red-100, green-100) that will render white text if nested inside a `.section--dark` parent.

### Report Structure

```html
1. Cover
   - Autonomous branding
   - Site name + URL
   - Audit types performed
   - Overall score
   - Date

2. Executive Summary
   - Key findings (top 3 issues)
   - Projected impact
   - Quick wins summary

3. [Copy Audit Section] (if selected)
   - Headlines analysis
   - CTA recommendations
   - Before/after rewrites

4. [SEO Audit Section] (if selected)
   - Technical checklist
   - Content recommendations
   - Priority fixes

5. [Visual/UI Audit Section] (if selected)
   - Annotated screenshots
   - UX recommendations
   - Accessibility notes

6. [CRO Audit Section] (if selected)
   - Funnel analysis
   - Trust signal gaps
   - Checkout optimization

7. Quick Wins Checklist
   - Top 5-10 implementable this week
   - Effort estimates
   - Expected impact

8. Implementation Roadmap
   - Week 1-2: Critical
   - Week 3-4: High impact
   - Month 2: Optimization

9. Appendix
   - Full screenshots
   - Tool recommendations
   - Benchmark data
```

### Teaser Mode (No Analytics Access)

When audit is conducted without GA4, GSC, PostHog, or platform data, the report is a **teaser**. Mandatory additions:

**1. Teaser Header Banner** — slim informational strip at the very top of `<body>`, before any content. **Context-setting only — no CTA button here:**
- Dark (`#1c1917`) background, `3px solid` amber bottom border
- Eyebrow: "📊 Teaser Report — Public Signals Only"  
- Body (one line): "This report was built from publicly available data. With access to GA4, GSC, PostHog (or your stack), it can be dramatically more powerful."
- The Calendly CTA lives at the end of the report — after the content has earned it

**2. Methodology Disclaimer** — after the executive summary scores:
State clearly that findings are based on public signals, revenue estimates are illustrative benchmarks (not projections), and full access changes the analysis significantly.

**3. Per-Track Upsell Callouts** — at the end of each section:
"Want deeper [CRO / SEO / Copy] analysis? With GA4 + GSC access, we can show exact drop-off points, keyword rankings, and attribution gaps. [Book a call →](https://calendly.com/rizwan-20/30min)"

**4. Caveat revenue estimates** — always use directional language in teaser mode, never specific dollar figures without real data.

### Sticky Sidebar TOC (ALL audit reports)

Every audit report must include a sticky TOC sidebar:
- **Desktop (≥1024px):** Left sidebar, `240px` wide, `position: sticky; top: 2rem`, frosted glass (`rgba(255,255,255,0.75)` + `backdrop-filter: blur(8px)`)
- **Mobile:** Hidden off-canvas, toggled by hamburger button
- **Active state:** Amber highlight on current section (Intersection Observer)
- **Layout:** `display: flex; gap: 3rem` wrapper with sidebar + `<main>` content column

### Save & Deploy

```bash
# Save report to project folder
projects/{client}/audits/{site-name}-audit-{date}.html

# Save assets
projects/{client}/audits/{site-name}-assets/
```

**⚠️ Audits ALWAYS deploy to `autonomous-proposals` → `docs.autonomoustech.ca`** (never to `landing-pages`).
Add the share button before `</body>`. Share externally via 30-day expiry link.

**Preview:** Use `canvas action=present` for immediate preview before deploying.

## Deployment

After generating the report HTML:
1. Save to `~/autonomous-proposals/audits/{client-slug}-{audit-type}-{date}/index.html` (or single HTML file for simpler reports)
2. Commit and push to `https://github.com/autonomous-tech/autonomous-proposals` (main branch)
3. Cloudflare Pages auto-deploys to `https://docs.autonomoustech.ca/audits/{client-slug}-{audit-type}-{date}/`
4. Use the SHARE button (auto-injected by GitHub Actions) to generate a 30-day shareable link via `share.autonomoustech.ca`
5. Share the link with the client — no login required for the recipient

---

## Example Workflow

**User:** Run an audit on example.com

**Agent:**
> Which audit types do you want to run?
> 1. 📝 Copy Audit
> 2. 🔍 SEO Audit  
> 3. 🎨 Visual/UI Audit
> 4. 📈 CRO Audit
>
> Reply with numbers or "all"

**User:** 1, 3, 4

**Agent:**
> Got it — Copy, Visual/UI, and CRO audits.
>
> Target details:
> - Website URL: example.com ✓
> - Platform: Shopify / WooCommerce / Custom?
> - Industry: ?
> - Price point: ?
> - Primary markets: ?

**User:** Shopify, jewelry, mid-market, Pakistan

**Agent:**
> What analytics access do you have?
> - CDP / PostHog / Shopify API / GA / Hotjar?
> - Or visual-only audit?

**User:** None, visual only

**Agent:**
> Perfect. Running Copy + Visual/UI + CRO audit on example.com (Shopify jewelry store, Pakistan market, visual-only).
>
> Capturing screenshots now...

[Then proceeds with audit execution]

---

---

## HTML Report Quality Checklist

Before finalizing any HTML audit report, verify every item below:

### Design System
- [ ] **Stone/Amber palette** — CSS variables from the tokens above (`--stone-*`, `--amber-*`, severity tokens) — no old parchment/vermillion colors
- [ ] **Google Fonts import** — `Inter` (body) + `Source Serif 4` (headings) at top of `<style>`
- [ ] **Section padding** — `6rem` top/bottom on regular sections, `8rem` on final CTA section
- [ ] **Score card padding** — `2rem 1.25rem` with `1.25rem` gap

### CTA
- [ ] **Calendly links** — ALL CTAs use `https://calendly.com/rizwan-20/30min` — no exceptions (no email links, no `autonomoustech.ca/contact`)
- [ ] **CTA button CSS** — `display: block; margin: 0 auto; max-width: 280px; white-space: normal; text-align: center; box-shadow: 0 6px 24px rgba(245,158,11,0.35)`
- [ ] **Final CTA section** — full-width dark background (`var(--stone-900)`) with amber CTA + 3 trust signals

### UX Interactions
- [ ] **Scroll reveal** — `IntersectionObserver` fade-in-up on score cards, findings grids, stat strips (`.reveal` class: `opacity 0→1` + `translateY(28px)→0` at `0.6s ease`)
- [ ] **Hover states** — all interactive cards have `0.2s` transitions with `translateY(-1px)` lift + shadow increase
- [ ] **Mobile bottom CTA banner** — fixed bottom amber strip visible on mobile only (`max-width: 768px`): dark bg, amber CTA button
- [ ] **Sticky sidebar TOC** — frosted glass panel (`rgba(255,255,255,0.75)` + `backdrop-filter: blur(8px)`) on desktop (≥1024px) with amber active link; collapses to off-canvas drawer on mobile

### Technical
- [ ] **Single file** — no external dependencies except Google Fonts
- [ ] **Responsive** — tested at 375px, 768px, 1024px, 1440px
- [ ] **No inline styles** — use CSS classes (utility classes `mt-sm`, `mt-md`, `mt-lg` for margin variations)
- [ ] **Finding box text** — `.finding`, `.before`, `.after` always have `color: var(--stone-800)` to prevent white-on-light rendering inside dark sections
- [ ] **Dark/light section alternation** maintained throughout

---

## Core Rules

- **No time estimates on fixes.** Never say "this takes 30 mins" or "a quick 2-hour fix." Time is subjective and different for every team. Use effort levels (Low / Medium / High) only — no durations.
- **No CTA in the teaser header banner.** The banner is context-setting ("this is public-signals only"). The Calendly CTA belongs at the end of the report, after the content has earned it.

## Related Skills

- `landing-page-copywriter` — Deep copy analysis
- `seo-audit` — Technical SEO
- `ui-audit` — UX/UI patterns
- `shopify-revenue-audit` — Shopify-specific CRO
- `conversion-audit` — Landing page focus

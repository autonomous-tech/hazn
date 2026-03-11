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
| Copy Audit | landing-page-copywriter | `~/clawd/skills/landing-page-copywriter/SKILL.md` |
| SEO Audit | seo-audit | `~/clawd/skills/seo-audit/SKILL.md` |
| Visual/UI Audit | ui-audit | `~/clawd/skills/ui-audit/SKILL.md` |
| CRO Audit | shopify-cro-audit (or this skill's CRO section) | `~/clawd/skills/shopify-cro-audit/SKILL.md` |

Also apply:
- **Brand styling:** Use client's brand guidelines if provided, or professional default styling

### Screenshot Capture (All Audit Types)

Capture screenshots for analysis:

```
browser action=start profile=clawd
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

### Apply Professional Styling

Use client's brand guidelines if provided, or apply the **Autonomous Editorial Warmth v2** design system as the default:
- Source: `/home/rizki/clawd/agents/hazn/skills/conversion-audit/references/brand.md`
- Fonts: Fraunces (display) + DM Sans (body) + JetBrains Mono (labels)
- Colors: parchment `#F5EFE0` background, midnight `#0D0D1F` dark sections, vermillion `#E8513D` accent
- Score circles: sage `#7CA982` (≥70), gold `#D4A853` (50–69), vermillion `#E8513D` (<50)
- Reference wireframes: `/home/rizki/autonomous-proposals/wireframes-v2/`
- Clean header with client/agency logo
- Clear score visualization
- Section numbers (01, 02, etc.)
- Card-based layout for findings
- Consistent color scheme throughout

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

## Core Rules

- **No time estimates on fixes.** Never say "this takes 30 mins" or "a quick 2-hour fix." Time is subjective and different for every team. Use effort levels (Low / Medium / High) only — no durations.
- **No CTA in the teaser header banner.** The banner is context-setting ("this is public-signals only"). The Calendly CTA belongs at the end of the report, after the content has earned it.

## Related Skills

- `landing-page-copywriter` — Deep copy analysis
- `seo-audit` — Technical SEO
- `ui-audit` — UX/UI patterns
- `shopify-cro-audit` — Shopify-specific CRO
- `conversion-audit` — Landing page focus

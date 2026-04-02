---
name: ui-audit
description: "UX/UI Audit — visual hierarchy, accessibility (WCAG 2.1 AA), cognitive load, navigation, annotated screenshots. Three tiers: Free / Standard / Deep Dive."
author: Tommy Geoco
homepage: https://audit.uxtools.co
logo: logo-light.png
logoDark: logo-dark.png
---

# UI Audit Skill

Evaluate interfaces against proven UX principles. Based on [Making UX Decisions](https://uxdecisions.com) by Tommy Geoco.

## When to Use This Skill

- Making UI/UX design decisions under time pressure
- Evaluating design trade-offs with business context
- Choosing appropriate UI patterns for specific problems
- Reviewing designs for completeness and quality
- Structuring design thinking for new interfaces

## Core Philosophy

**Speed ≠ Recklessness.** Designing quickly is not automatically reckless. Recklessly designing quickly is reckless. The difference is intentionality.

## The 3 Pillars of Warp-Speed Decisioning

1. **Scaffolding** — Rules you use to automate recurring decisions
2. **Decisioning** — Process you use for making new decisions  
3. **Crafting** — Checklists you use for executing decisions

## Quick Reference Structure

### Foundational Frameworks
- `references/00-core-framework.md` — 3 pillars, decisioning workflow, macro bets
- `references/01-anchors.md` — 7 foundational mindsets for design resilience
- `references/02-information-scaffold.md` — Psychology, economics, accessibility, defaults

### Checklists (Execution)
- `references/10-checklist-new-interfaces.md` — 6-step process for designing new interfaces
- `references/11-checklist-fidelity.md` — Component states, interactions, scalability, feedback
- `references/12-checklist-visual-style.md` — Spacing, color, elevation, typography, motion
- `references/13-checklist-innovation.md` — 5 levels of originality spectrum

### Patterns (Reusable Solutions)
- `references/20-patterns-chunking.md` — Cards, tabs, accordions, pagination, carousels
- `references/21-patterns-progressive-disclosure.md` — Tooltips, popovers, drawers, modals
- `references/22-patterns-cognitive-load.md` — Steppers, wizards, minimalist nav, simplified forms
- `references/23-patterns-visual-hierarchy.md` — Typography, color, whitespace, size, proximity
- `references/24-patterns-social-proof.md` — Testimonials, UGC, badges, social integration
- `references/25-patterns-feedback.md` — Progress bars, notifications, validation, contextual help
- `references/26-patterns-error-handling.md` — Form validation, undo/redo, dialogs, autosave
- `references/27-patterns-accessibility.md` — Keyboard nav, ARIA, alt text, contrast, zoom
- `references/28-patterns-personalization.md` — Dashboards, adaptive content, preferences, l10n
- `references/29-patterns-onboarding.md` — Tours, contextual tips, tutorials, checklists
- `references/30-patterns-information.md` — Breadcrumbs, sitemaps, tagging, faceted search
- `references/31-patterns-navigation.md` — Priority nav, off-canvas, sticky, bottom nav

## Step 0: Tier & Brand Intake

Ask everything in ONE message:

> A few quick questions before I start:
>
> 1. **Tier:** Free / Standard / Deep Dive?
> 2. **Brand:** Who is this report for?
>    - (a) Autonomous delivery (default)
>    - (b) Partner white-label — which partner slug?
>    - (c) End-customer branded — provide: company name, primary colour, CTA URL
> 3. **URL to audit:** (if not already provided)
> 4. **Client email** (optional)
>
> [Deep Dive only — also ask:]
> 5. Key user journeys to map (e.g. homepage → pricing → signup)
> 6. Figma link or design system URL (optional — for design system consistency review)
> 7. 2–3 competitor sites for UX benchmarks

After intake:
- Load brand config from ~/hazn/brands/{slug}.json. Default: ~/hazn/brands/autonomous.json
- Set TIER variable. Proceed to Step 0b.

---

## Step 0b: Audience Routing

**Before starting any audit or review, ask the audience question.** Read `~/hazn/skills/references/audience-routing.md` for the full routing spec. Then ask:

> **Who is this report for?**
>
> 1. 👔 **Business Executive** — ROI framing, plain English, impact/effort badges. Translate UX jargon into business language (e.g., "users leave before seeing the offer" not "above-fold conversion drop").
> 2. 🔧 **Technical / Design Team** — Full UX detail, design system notes, implementation specs, pattern references.
> 3. 📋 **Both** — Executive summary first, then technical appendix.

Apply the appropriate output mode throughout the audit.

---

## Step 0c: Tier Execution Gate

**TIER = Free:**
- Capture homepage screenshot (desktop + mobile) via browser tool
- Run visual hierarchy scan and top friction points only
- Output: overall UX score, 1 finding in full, locked rows for rest
- Deliver immediately (3–24 hours)

**TIER = Standard:**
- Run Steps 1–6 (screenshot capture + full analysis across all dimensions)
- Generate HTML report with annotated findings
- Set human_review_required = true
- Delivery: 24–48 hours

**TIER = Deep Dive:**
- Run full Standard analysis PLUS:
  - Full WCAG 2.1 AA compliance report
  - Design system consistency review (if Figma provided)
  - User flow mapping across provided journeys
  - Competitor UX benchmarks (capture + compare)
  - Form UX deep-dive
- Set human_review_required = true, call_required = true
- Delivery: 3–5 business days

---

## Step 1: Screenshot Capture

Before any analysis, capture screenshots using the browser tool.

**Desktop (1440px viewport):**
- Homepage
- Any additional key pages mentioned in brief

**Mobile (390px viewport):**
- Same pages as desktop
- Use browser tool to resize: action=act, kind=resize, width=390, height=844

Save paths:
- ~/hazn/projects/{client-slug}/ux-audit-{date}/screenshots/desktop-homepage.jpg
- ~/hazn/projects/{client-slug}/ux-audit-{date}/screenshots/mobile-homepage.jpg

These screenshots are used for:
1. Analysis reference during audit
2. Annotated findings in HTML report (base64 embedded)
3. Competitor comparison in Deep Dive

---

## Usage Instructions

### For Design Decisions
1. Read `00-core-framework.md` for the decisioning workflow
2. Identify if this is a recurring decision (use scaffold) or new decision (use process)
3. Apply the 3-step weighing: institutional knowledge → user familiarity → research

### For New Interfaces
1. Follow the 6-step checklist in `10-checklist-new-interfaces.md`
2. Reference relevant pattern files for specific UI components
3. Use fidelity and visual style checklists to enhance quality

### For Pattern Selection
1. Identify the core problem (chunking, disclosure, cognitive load, etc.)
2. Load the relevant pattern reference
3. Evaluate benefits, use cases, psychological principles, and implementation guidelines

## Decision Workflow Summary

When facing a UI decision:

```
1. WEIGH INFORMATION
   ├─ What does institutional knowledge say? (existing patterns, brand, tech constraints)
   ├─ What are users familiar with? (conventions, competitor patterns)
   └─ What does research say? (user testing, analytics, studies)

2. NARROW OPTIONS
   ├─ Eliminate what conflicts with constraints
   ├─ Prioritize what aligns with macro bets
   └─ Choose based on JTBD support

3. EXECUTE
   └─ Apply relevant checklist + patterns
```

## Macro Bet Categories

Companies win through one or more of:

| Bet | Description | Design Implication |
|-----|-------------|-------------------|
| **Velocity** | Features to market faster | Reuse patterns, find metaphors in other markets |
| **Efficiency** | Manage waste better | Design systems, reduce WIP |
| **Accuracy** | Be right more often | Stronger research, instrumentation |
| **Innovation** | Discover untapped potential | Novel patterns, cross-domain inspiration |

Always align micro design bets with company macro bets.

## Key Principle: Good Design Decisions Are Relative

A design decision is "good" when it:
- Supports the product's jobs-to-be-done
- Aligns with company macro bets
- Respects constraints (time, tech, team)
- Balances user familiarity with differentiation needs

There is no universally correct UI solution—only contextually appropriate ones.

---

## Generating Audit Reports

When asked to audit a design, generate a comprehensive report. Always include these sections:

### Required Sections (always include)
1. **Visual Hierarchy** — Headings, CTAs, grouping, reading flow, type scale, color hierarchy, whitespace
2. **Visual Style** — Spacing consistency, color usage, elevation/depth, typography, motion/animation
3. **Accessibility** — Keyboard navigation, focus states, contrast ratios, screen reader support, touch targets

### Contextual Sections (include when relevant)
4. **Navigation** — For multi-page apps: wayfinding, breadcrumbs, menu structure, information architecture
5. **Usability** — For interactive flows: discoverability, feedback, error handling, cognitive load
6. **Onboarding** — For new user experiences: first-run, tutorials, progressive disclosure
7. **Social Proof** — For landing/marketing pages: testimonials, trust signals, social integration
8. **Forms** — For data entry: labels, validation, error messages, field types

### Audit Output Format

```json
{
  "title": "Design Name — Screen/Flow",
  "project": "Project Name",
  "date": "YYYY-MM-DD",
  "figma_url": "optional",
  "screenshot_url": "optional - URL to screenshot",
  
  "macro_bets": [
    { "category": "velocity|efficiency|accuracy|innovation", "description": "...", "alignment": "strong|moderate|weak" }
  ],
  
  "jtbd": [
    { "user": "User Type", "situation": "context without 'When'", "motivation": "goal without 'I want to'", "outcome": "benefit without 'so I can'" }
  ],
  
  "visual_hierarchy": {
    "title": "Visual Hierarchy",
    "checks": [
      { "label": "Check name", "status": "pass|warn|fail|na", "notes": "Details" }
    ]
  },
  "visual_style": { ... },
  "accessibility": { ... },
  
  "priority_fixes": [
    { "rank": 1, "title": "Fix title", "description": "What and why", "framework_reference": "XX-filename.md → Section Name" }
  ],
  
  "notes": "Optional overall observations"
}
```

### Checks Per Section (aim for 6-10 each)

**Visual Hierarchy**: heading distinction, primary action clarity, grouping/proximity, reading flow, type scale, color hierarchy, whitespace usage, visual weight balance

**Visual Style**: spacing consistency, color palette adherence, elevation/shadows, typography system, border/radius consistency, icon style, motion principles

**Accessibility**: keyboard operability, visible focus, color contrast (4.5:1), touch targets (44px), alt text, semantic markup, reduced motion support

**Navigation**: clear current location, predictable menu behavior, breadcrumb presence, search accessibility, mobile navigation pattern

**Usability**: feature discoverability, feedback on actions, error prevention, recovery options, cognitive load management, loading states

---

## Step 7: Generate HTML Report

Generate a single-file HTML report using the Stone/Amber design system.

### Design Tokens

**Brand config injection:** Load brand config from Step 0. Replace hardcoded design tokens:
- Use brand_config.primary_color for CTA buttons and accent elements
- Use brand_config.cta_url for all Calendly links (default: https://calendly.com/rizwan-20/30min)
- Use brand_config.cta_label for CTA button text
- Use brand_config.company_name in header/footer (replace "Autonomous")
- If brand_config.hide_autonomous = true, remove all "Autonomous Technology Inc." mentions

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

### Section Padding

- Regular sections: `padding: 6rem 0`
- Final CTA section: `padding: 8rem 0`
- Score cards: `padding: 2rem 1.25rem`, gap: `1.25rem`

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

> CTA copy examples:
> - "Book a 20-min call — we'll walk through your findings live →"
> - "Your implementation roadmap starts here →"
> - "Let's turn these findings into fixes — book a 20-min call →"

### Report Sections

Include all of the following in the HTML output:

**Cover section:**
- Domain, audit date, overall UX score (0–100)
- Score badge (sage ≥70, gold 50–69, vermillion <50)
- Tier label (Free / Standard / Deep Dive)
- Brand config: company name + logo

**Executive Summary:**
- Top 3 critical findings
- Score breakdown: Visual Hierarchy / Accessibility / Cognitive Load / Navigation
- Annotated homepage screenshot (desktop) with top 3 issues marked

**Visual Hierarchy section:**
- Score + findings
- Annotated screenshot showing hierarchy issues
- Each finding: issue name, severity (High/Medium/Low), what it means, recommended fix
- Micro-upsell callout at end of section (Standard+)

**Accessibility section (WCAG 2.1 AA):**
- Score + findings
- Contrast ratio failures listed with actual vs required values
- Touch target violations
- Keyboard navigation issues
- Each finding with severity + recommended fix
- Micro-upsell callout

**Cognitive Load section:**
- Score + findings
- Decision fatigue, form friction, navigation complexity
- Mobile-specific findings with mobile screenshot
- Micro-upsell callout

**Navigation & Information Architecture section:**
- Score + findings
- Menu structure, wayfinding, breadcrumbs
- Micro-upsell callout

**[Deep Dive only] WCAG Full Compliance Report:**
- Complete WCAG 2.1 AA checklist
- Pass/Fail/Not Tested for each criterion

**[Deep Dive only] User Flow Mapping:**
- For each journey provided: step-by-step screenshots + friction points

**[Deep Dive only] Competitor UX Benchmarks:**
- Side-by-side comparison table
- Screenshots of competitors on same viewport

**Priority Fix Roadmap:**
- All findings sorted by: High effort issues / Medium / Low (quick wins)
- NO time estimates — effort levels only (Low / Medium / High)
- Each item: finding, effort level, expected impact

**Final CTA section:**
- Dark background (--stone-900)
- brand_config.cta_url button
- 3 trust signals

### Micro-Upsell Callout Pattern (end of each section)

```html
<div class="callout callout--info" style="color: var(--stone-800);">
  🔍 <strong>Want the full picture?</strong> With a full UX deep-dive, we'd show you
  [specific deeper insight]. Part of the <strong>UX/UI Audit</strong> engagement.
  <a href="https://calendly.com/rizwan-20/30min" style="color: var(--amber-600); font-weight: 600;">
    Book a 20-min call →
  </a>
</div>
```

### Final CTA Section Template

```html
<section style="padding: 8rem 0; background: var(--stone-900); text-align: center;">
  <p style="color: var(--amber-400); font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;">
    Ready to Fix This?
  </p>
  <h2 style="color: #fff; font-family: 'Source Serif 4', Georgia, serif; font-size: 2rem; margin: 0.75rem 0 1rem;">
    Let's turn these findings into fixes
  </h2>
  <p style="color: var(--stone-300); max-width: 560px; margin: 0 auto 2.5rem; line-height: 1.6;">
    Book a 20-min call and we'll walk through your UX audit findings live — and map out exactly what to tackle first.
  </p>
  <a href="https://calendly.com/rizwan-20/30min" class="cta-btn">
    Book a 20-min call — we'll walk through your findings live →
  </a>
  <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 3rem; flex-wrap: wrap;">
    <span style="color: var(--stone-400); font-size: 0.875rem;">✓ No commitment required</span>
    <span style="color: var(--stone-400); font-size: 0.875rem;">✓ We come with your audit findings loaded</span>
    <span style="color: var(--stone-400); font-size: 0.875rem;">✓ Implementation roadmap included</span>
  </div>
</section>
```

### Annotating Screenshots

For each key finding, reference the screenshot and describe the annotation:
Format: "See homepage screenshot — the primary CTA (Book a Demo) has insufficient contrast at 2.8:1 against the background. WCAG requires 4.5:1 for normal text."

We cannot draw on screenshots programmatically, so instead:
- Include the screenshot inline (base64 embedded)
- Immediately below it, list the annotated findings as numbered callouts
- Each callout references a visible element: "① Primary CTA button — contrast ratio 2.8:1 (fail)"

### Free Tier Report Variant

When TIER = Free:
- Show cover with overall score
- Show: "We found [N] UX issues across [M] categories"
- Show 1 finding in full
- Show remaining as locked rows (grey CSS bars)
- CTA: "Unlock the full UX audit — from $497"

### Sticky Sidebar TOC

Every HTML report must include a sticky sidebar TOC on desktop (≥1024px):
- Frosted glass panel: `background: rgba(255,255,255,0.75); backdrop-filter: blur(8px)`
- Active link: amber highlight (`background: var(--amber-500); color: var(--stone-900)`)
- Mobile: hidden off-canvas, toggled by hamburger button
- Intersection Observer tracks active section

### HTML Report Quality Checklist

Before delivering the HTML report, verify:

- [ ] **Stone/Amber palette** — CSS variables only, no old parchment/vermillion/fraunces tokens
- [ ] **Google Fonts** — `Inter` + `Source Serif 4` imported at top of `<style>`
- [ ] **Section padding** — `6rem` on regular sections, `8rem` on final CTA section
- [ ] **Calendly links** — ALL CTAs use `https://calendly.com/rizwan-20/30min` — no exceptions
- [ ] **CTA button CSS** — `display: block; margin: 0 auto; max-width: 280px; white-space: normal; text-align: center; box-shadow: 0 6px 24px rgba(245,158,11,0.35)`
- [ ] **Final CTA section** — full-width dark background + Calendly CTA + 3 trust signals
- [ ] **Scroll reveal** — `IntersectionObserver` fade-in-up on score cards, findings grids (`.reveal` class: `opacity 0→1` + `translateY(28px)→0` at `0.6s ease`)
- [ ] **Hover states** — all interactive cards have `0.2s` transitions with `translateY(-1px)` lift + shadow
- [ ] **Mobile bottom CTA banner** — fixed bottom amber strip on mobile only (`max-width: 768px`)
- [ ] **Sticky sidebar TOC** — frosted glass panel with amber active links on desktop
- [ ] **Single file** — no external dependencies except Google Fonts
- [ ] **Responsive** at 375px, 768px, 1024px, 1440px
- [ ] **Finding box text** — `.finding` boxes always have `color: var(--stone-800)` set explicitly
- [ ] **Dark/light section alternation** maintained
- [ ] **Annotated screenshots** — base64 embedded with numbered callouts below each image
- [ ] **4 content sections** — Visual Hierarchy, Accessibility, Cognitive Load, Navigation all present
- [ ] **4 micro-upsell callouts** — one at end of each section, each with Calendly link
- [ ] **Priority roadmap** — all findings with effort levels (Low/Medium/High), no time estimates
- [ ] **Score 0–100** — overall UX score calculated and displayed in cover/hero

---

## Deployment

Save to: ~/hazn/projects/{client-slug}/ux-audit-{date}/report.html
Commit and push to autonomous-proposals repo if applicable.
Use canvas action=present for preview before delivering.

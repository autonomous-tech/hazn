---
name: b2b-wireframe
description: "Mid-fidelity wireframing for B2B marketing websites. Use this skill after UX strategy is defined (page blueprints, content hierarchy, conversion goals) and before production code is written. Trigger on any mention of 'wireframe', 'mockup', 'layout preview', 'page layout', 'visual layout', or when the user wants to see/review a page design before building it. Also trigger when reviewing or iterating on an existing wireframe. Outputs responsive HTML files for review. Consumes page blueprints from `b2b-marketing-ux` and produces a section manifest for `payload-nextjs-stack`."
---

# B2B Marketing Website Wireframe Skill

## Purpose

You produce mid-fidelity wireframes as standalone HTML files for B2B marketing websites — agencies, consultancies, and service providers. These wireframes sit between UX strategy and production code. They are the design review checkpoint.

**You are not generating production code.** You are generating a visual artifact that the team and client can review, iterate on, and approve before a single line of production code is written. This prevents expensive rework.

**You are not generating low-fidelity sketches.** These wireframes use real typography scales, realistic spacing, proper responsive behavior, and placeholder content that reads like the real thing. A client should look at this and understand exactly what their site will feel like.

---

## Where This Skill Fits

```
b2b-marketing-ux           →  THIS SKILL              →  payload-nextjs-stack
(page blueprint + content)    (wireframe + review)        (production code)
```

### What You Receive (Input)

From the `b2b-marketing-ux` skill or from the user directly:

- **Page blueprint**: Which sections, in what order (e.g., Hero → Pain Agitation → Services Grid → Process → Case Study → CTA)
- **Content hierarchy**: Headlines, subheadlines, CTA copy, trust signal placement per section
- **Target audience**: Who visits this page, what stage of the buying journey
- **Conversion goal**: What the visitor should do (book a call, request a proposal, explore case studies)
- **Brand direction** (optional): Colors, fonts, tone — if known. If not known, use tasteful defaults.

If the user provides a page blueprint from `b2b-marketing-ux`, follow it. If they provide a rough description ("wireframe a homepage for an agency that does martech"), use the page architecture patterns from `b2b-marketing-ux` to generate the blueprint yourself, then wireframe it.

### What You Produce (Output)

1. **A standalone HTML wireframe file** — single `.html` file with embedded CSS. No external dependencies except Google Fonts. Opens in any browser. Fully responsive (mobile, tablet, desktop).

2. **A section manifest** — a structured comment block at the end of the HTML file (or a separate markdown block in the response) that maps each wireframed section to its intended component name, key props, and responsive behavior notes. This is what `payload-nextjs-stack` consumes.

---

## ⚠️ MANDATORY: Mobile Requirements

**Every wireframe must pass this checklist before delivery. No exceptions.**

The check: *"Would this render usably on a 390px wide phone?"* — must be answered **YES** before you declare the wireframe complete.

---

### 1. Always link shared.css

Every IDU page (and any multi-page wireframe project with a shared asset) **must** include the shared CSS file in `<head>`, after the local `<style>` block:

```html
<link rel="stylesheet" href="shared.css">
```

---

### 2. No inline styles for grid layout

**Never** use inline `style` attributes for grid layout column definitions. Always use the class names from `shared.css` (or equivalent) instead.

| ❌ Wrong | ✅ Correct |
|---|---|
| `<div style="display:grid;grid-template-columns:repeat(3,1fr);">` | `<div class="grid-3col">` |
| `<div style="display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr;">` | `<div class="grid-4col-footer">` |
| `<div style="display:grid;grid-template-columns:1fr 100px 1fr;">` | `<div class="grid-timeline">` |

When keeping other inline styles (gap, margin, background), remove only `display:grid` and `grid-template-columns` and replace with the class:
```html
<!-- BEFORE -->
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:32px;margin-bottom:48px;">
<!-- AFTER -->
<div class="grid-3col" style="gap:32px;margin-bottom:48px;">
```

If a grid pattern has no class equivalent (e.g. `repeat(5,1fr)`), add a local `@media(max-width:768px)` override in the page's `<style>` block.

---

### 3. Hamburger nav required on every page

Every wireframe must include the mobile nav drawer pattern. The standard implementation:

```html
<nav id="navbar">
  <a href="index.html" class="nav-logo">BRAND<span>·</span></a>
  <div class="nav-links">
    <!-- desktop nav links -->
  </div>
  <button class="nav-hamburger" id="nav-hamburger" aria-label="Open navigation menu" aria-expanded="false">
    <span></span><span></span><span></span>
  </button>
</nav>

<div class="nav-drawer" id="nav-drawer">
  <!-- same links as desktop -->
  <a href="#" class="nav-drawer-login">Member Login</a>
</div>
<div class="nav-drawer-overlay" id="nav-overlay"></div>
```

Plus the toggle JS before `</body>` (before any share button script):
```html
<script>
(function() {
  var btn = document.getElementById('nav-hamburger');
  var drawer = document.getElementById('nav-drawer');
  var overlay = document.getElementById('nav-overlay');
  if (!btn || !drawer) return;
  function openNav() { btn.classList.add('is-open'); drawer.classList.add('is-open'); overlay.classList.add('is-open'); btn.setAttribute('aria-expanded','true'); document.body.style.overflow='hidden'; }
  function closeNav() { btn.classList.remove('is-open'); drawer.classList.remove('is-open'); overlay.classList.remove('is-open'); btn.setAttribute('aria-expanded','false'); document.body.style.overflow=''; }
  btn.addEventListener('click', function() { if (drawer.classList.contains('is-open')) closeNav(); else openNav(); });
  overlay.addEventListener('click', closeNav);
  drawer.querySelectorAll('a').forEach(function(a) { a.addEventListener('click', closeNav); });
})();
</script>
```

- Use `class="light"` on the hamburger button for transparent/dark-background navs (e.g. homepage hero)
- On pages with an active nav link, apply `style="color:#C9A84C;font-weight:700;"` to the matching drawer link

---

### 4. Section padding — never hardcode `80px` horizontal padding

**Never** use fixed pixel horizontal padding like `padding:80px 80px` or `padding:96px 48px` in inline styles.

The `shared.css` attribute selectors will override these on mobile, but they rely on exact string matches which are fragile. Prefer:

- Use `clamp()` for responsive padding: `padding: clamp(40px, 8vw, 96px) clamp(20px, 5vw, 80px);`
- Or use the class helpers: `class="section-pad"` (96px 48px desktop → 48px 20px mobile)
- Or use `class="section-pad-sm"` (80px 48px desktop → 48px 20px mobile)

---

### 5. Mobile media query checklist

Every page's `<style>` block `@media(max-width:768px)` must explicitly address:

- [ ] **Nav**: `padding: 0 20px`, `.nav-links { display: none }`
- [ ] **Section padding**: override inline paddings or use clamp/classes
- [ ] **All 2+ column grids**: verified covered by class names or attribute selectors
- [ ] **Any grid with non-standard column counts** (5-col, 7-col, etc.): manual `grid-template-columns: 1fr` override
- [ ] **Fixed pixel heights on image containers**: ensure height collapses gracefully (`height: auto` or reduced fixed value)

---

### 6. Playwright validation required

Before declaring any wireframe complete, run a mobile screenshot test at 390×844 (iPhone 14) and verify `scrollWidth ≤ viewport width`:

```javascript
// Run from /home/rizki/hazn (where playwright is installed)
const { chromium } = require('./node_modules/playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('file:///path/to/wireframe.html');
  const sw = await page.evaluate(() => document.documentElement.scrollWidth);
  console.log('Scroll width:', sw, sw <= 395 ? '✅ PASS' : '❌ FAIL - horizontal overflow!');
  await page.screenshot({ path: '/tmp/mobile-check.png', fullPage: true });
  await browser.close();
})();
```

A `scrollWidth > 395` means something is overflowing the viewport — find and fix it before delivery.

---

## Wireframe Fidelity Level

These are **mid-fidelity** wireframes. That means:

### What IS included
- Real typography hierarchy (proper heading sizes, weights, line heights, font pairing)
- Realistic spacing and vertical rhythm (sections feel proportionally correct)
- Actual responsive behavior (not just "it stacks on mobile" — real breakpoints, real reflow)
- Placeholder content that reads like real copy (not "Lorem ipsum" — write realistic B2B services copy)
- Proper CTA styling (primary vs secondary buttons are visually distinct)
- Visual hierarchy cues (size, weight, color contrast between elements)
- Image placeholders with correct aspect ratios and descriptive labels
- Navigation with realistic link labels
- Icon placeholders where icons are intended (use simple SVG shapes or emoji)

### What is NOT included
- Final brand colors (use a neutral palette with one accent color — see defaults below)
- Final imagery (use labeled placeholder boxes with aspect ratios)
- Micro-interactions and animations (note them in comments where intended)
- Production-quality code patterns (no component extraction, no TypeScript, no CMS integration)
- Pixel-perfect polish (spacing can be approximate — the goal is layout validation, not design perfection)

### The "Squint Test"
A good mid-fidelity wireframe passes the squint test: squint at it, and you should immediately understand the visual hierarchy, section flow, and where the CTAs are. If everything looks the same importance when squinted, the hierarchy has failed.

---

## Default Wireframe Palette

When no brand direction is provided, use this palette. It's intentionally restrained so reviewers focus on layout, not color opinions.

```css
:root {
  /* Neutrals */
  --wf-white: #FFFFFF;
  --wf-bg: #F8F9FA;          /* Page background — light warm gray */
  --wf-surface: #FFFFFF;      /* Card/section surfaces */
  --wf-border: #E2E5E9;      /* Borders, dividers */
  --wf-text: #1A1D23;         /* Primary text */
  --wf-text-muted: #5F6B7A;   /* Secondary text, subheadlines */
  --wf-text-light: #8E99A8;   /* Captions, eyebrows, metadata */

  /* Accent — a single muted accent for CTAs and highlights */
  --wf-accent: #2563EB;       /* Blue — universally neutral for wireframes */
  --wf-accent-hover: #1D4ED8;
  --wf-accent-light: #EFF6FF; /* Light accent for backgrounds */

  /* Dark section variant */
  --wf-dark-bg: #111318;
  --wf-dark-text: #F1F3F5;
  --wf-dark-muted: #9CA3AF;

  /* Placeholder image background */
  --wf-placeholder: #D1D5DB;
  --wf-placeholder-text: #6B7280;
}
```

### Default Typography

Use Google Fonts. Pair a slightly distinctive heading font with a clean body font. Vary per project when brand direction is given.

**Default pairing (when no direction given):**
- Heading: `DM Sans` at weights 500, 600, 700
- Body: `Inter` at weights 400, 500

**Alternate pairings to suggest during review:**
- Plus Jakarta Sans + Inter (modern/tech-forward)
- Manrope + Source Serif 4 (warm/professional)
- Space Grotesk + Work Sans (bold/creative)
- Outfit + Lora (approachable/established)

### Typography Scale

```css
/* Mobile-first, then scale up */
.wf-hero-heading    { font-size: 2.25rem; line-height: 1.15; font-weight: 700; }
.wf-section-heading { font-size: 1.875rem; line-height: 1.2; font-weight: 700; }
.wf-subheading      { font-size: 1.125rem; line-height: 1.5; font-weight: 400; color: var(--wf-text-muted); }
.wf-body            { font-size: 1rem; line-height: 1.6; font-weight: 400; }
.wf-small           { font-size: 0.875rem; line-height: 1.5; color: var(--wf-text-light); }
.wf-eyebrow         { font-size: 0.75rem; line-height: 1.5; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; color: var(--wf-accent); }

/* Desktop scale-up (1024px+) */
@media (min-width: 1024px) {
  .wf-hero-heading    { font-size: 3.75rem; }
  .wf-section-heading { font-size: 2.5rem; }
  .wf-subheading      { font-size: 1.25rem; }
}
```

---

## Wireframe Structure

Every wireframe HTML file follows this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Page Name] — Wireframe</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
  <style>
    /* Reset + wireframe palette + typography + components + sections */
    /* ALL CSS embedded — no external stylesheets */
  </style>
</head>
<body>
  <!-- WIREFRAME ANNOTATION BAR (top of page, identifies this as a wireframe) -->
  <div class="wf-annotation-bar">
    <span>📐 WIREFRAME — [Page Name] — [Date] — Not final design</span>
    <span class="wf-annotation-controls">
      <button onclick="document.body.classList.toggle('wf-mobile-preview')">Toggle Mobile View</button>
    </span>
  </div>

  <!-- PAGE CONTENT -->
  <header><!-- Navigation --></header>
  <main>
    <!-- Sections in blueprint order -->
    <!-- Each section wrapped in a comment identifying it:
         <!-- SECTION: Hero | Component: HeroSection | Notes: ... -->
    -->
  </main>
  <footer><!-- Footer --></footer>

  <!-- SECTION MANIFEST (structured data for handoff to production) -->
  <!--
  SECTION_MANIFEST:
  [
    {
      "order": 1,
      "section": "Hero",
      "component": "HeroSection",
      "props": { "eyebrow": "...", "headline": "...", "subheadline": "...", "primaryCTA": {...}, "secondaryCTA": {...}, "image": true },
      "responsive": "Stack vertically on mobile. Image below text. CTA full-width on mobile.",
      "notes": "Hero image should be a real screenshot of client work, not stock."
    },
    ...
  ]
  -->
</body>
</html>
```

### The Annotation Bar

Every wireframe includes a fixed top bar that:
- Clearly labels the page as a wireframe (prevents confusion with a finished design)
- Shows the page name and date
- Includes a toggle to simulate mobile viewport width (sets max-width: 375px on body, centered)

This bar is styled distinctly (yellow/amber background, monospace font) so it's unmistakably "tooling, not design."

---

## Section Patterns

When wireframing sections, use these patterns. They encode the UX principles from `b2b-marketing-ux` into visual layout.

### Navigation
- Sticky header, transparent on hero → solid white with shadow on scroll (use a simple JS scroll listener)
- Logo placeholder (left) — labeled rectangle
- Nav links (center or right): 4-6 items with realistic labels (Services, Work, About, Blog)
- Primary CTA button (right): "Book a Call" or equivalent — always visible, accent color
- Mobile: hamburger icon + visible CTA button (CTA does NOT hide behind hamburger)

### Hero Section
- **Desktop**: Two-column grid. Left: eyebrow + headline + subheadline + CTA buttons. Right: image placeholder.
- **Mobile**: Single column, stacked: eyebrow → headline → subheadline → CTAs → image below.
- Headline is the largest text on the page. Subheadline is muted.
- Primary CTA: solid accent button. Secondary CTA: outline/ghost button.
- Optional: logo strip or key metric below the hero content area.

### Logo Strip
- Horizontal row of 4-6 grayscale logo placeholders
- Optional eyebrow above: "Trusted by" or "Our clients include"
- Mobile: horizontally scrollable or 2-row grid

### Problem / Pain Agitation
- Centered text block with a strong headline addressing the visitor's pain
- 2-3 short paragraphs or a grid of pain points (icon + text)
- No CTA here — this section builds tension that the next section resolves

### Services Grid
- Eyebrow + section headline + optional subheadline
- Grid of 3-4 service cards (icon placeholder + service name + 1-2 line description + link arrow)
- **Desktop**: 3 or 4 columns. **Tablet**: 2 columns. **Mobile**: stacked cards.

### Process / How We Work
- Eyebrow + section headline
- 3-4 numbered steps in a horizontal flow (desktop) or vertical stack (mobile)
- Each step: number/icon + title + short description
- Connecting lines or arrows between steps on desktop

### Case Study Highlight
- Featured case study with: client name, industry tag, hero image placeholder, 2-3 key metrics, 1-line description, "Read case study" link
- Optional: smaller grid of 2-3 additional case study cards below
- **Desktop**: large featured card, possibly with side-by-side layout
- **Mobile**: stacked card

### Testimonials
- 2-3 testimonial cards with: quote text, person name, role, company, photo placeholder (circle)
- **Desktop**: side-by-side cards or a featured single quote
- **Mobile**: stacked or swipeable (note in manifest, but wireframe shows stacked)

### Stats / Metrics
- 3-4 key numbers in a horizontal row
- Each stat: large number + label below (e.g., "50+" / "agencies served")
- **Mobile**: 2x2 grid

### Team Section
- Eyebrow + headline
- Grid of team member cards: photo placeholder (square) + name + role + optional 1-line bio
- **Desktop**: 3-4 columns. **Mobile**: 2 columns or stacked.

### FAQ
- Eyebrow + headline
- Accordion-style Q&A list (show first item expanded, rest collapsed)
- Wireframe shows the expand/collapse UI but functionality is optional (nice-to-have with simple JS)

### Packages / Pricing
- Eyebrow + headline framing packages around the client's goal
- 2-3 package cards side-by-side (desktop) or stacked (mobile)
- Highlighted/recommended package visually distinct (accent border or "Most Popular" badge)
- Each card: package name, who it's for, price, feature list, CTA button
- Trust signal below packages (testimonial snippet or "100+ clients served")

### Final CTA Section
- Full-width section with contrasting background (dark variant or accent-light)
- Centered headline + subheadline + primary CTA button
- Optional: testimonial snippet or trust badge beside CTA
- This is the last push before the footer — make it count

### Footer
- Multi-column layout: company info + nav links + services links + contact info
- **Mobile**: accordion-style or stacked single-column
- Bottom bar: copyright + privacy/terms links
- Optional: brief positioning tagline

---

## Responsive Behavior Rules

The wireframe MUST be responsive. This is not optional and not approximate — the wireframe should behave correctly at all viewport widths because responsive behavior is one of the key things being reviewed.

```css
/* Breakpoints */
@media (max-width: 639px)  { /* Mobile: single column, stacked */ }
@media (min-width: 640px)  { /* Tablet: 2 columns where helpful */ }
@media (min-width: 1024px) { /* Desktop: full multi-column layouts */ }
@media (min-width: 1280px) { /* Large: max-width container, generous spacing */ }
```

### Rules
- **Container**: max-width 1200px, centered, with 16px padding (mobile) / 24px (tablet) / 32px (desktop)
- **Section vertical padding**: 64px mobile / 96px tablet / 128px desktop
- **Grid gaps**: 16px mobile / 24px tablet / 32px desktop
- **Images**: 100% width on mobile, constrained on desktop. Aspect ratios preserved.
- **Navigation**: hamburger on mobile, horizontal on desktop. CTA always visible.
- **Cards**: full-width stacked on mobile, grid on tablet+

---

## Placeholder Content Rules

**Never use Lorem Ipsum.** Every piece of placeholder text should read like realistic B2B services copy. The person reviewing this wireframe should be able to evaluate the messaging, not just the layout.

### How to Write Placeholder Content

- **Headlines**: Use the outcome-first patterns from `b2b-marketing-ux`. If the specific business is known, tailor to them. If not, write for a generic but realistic agency/consultancy.
- **Subheadlines**: Add specificity — who is this for, what makes the approach different.
- **Body copy**: 2-3 sentences that sound like real marketing copy. Front-load value.
- **CTAs**: Use strong CTA copy (e.g., "Book a Free Strategy Call", not "Submit").
- **Testimonials**: Write realistic-sounding quotes attributed to realistic names and roles. Mark clearly as placeholder: `[Placeholder — replace with real testimonial]`.
- **Stats**: Use realistic but clearly placeholder numbers. Mark as `[Placeholder]`.
- **Client names**: Use "[Client Name]" or generic industry descriptors.

### Image Placeholders

Use styled `<div>` elements with:
- Correct aspect ratio for the intended image type
- A light gray background (`var(--wf-placeholder)`)
- A centered label describing what goes there: "Hero Image — Screenshot of Client Work", "Team Photo — [Name]", "Client Logo"
- Optional: a simple SVG icon (image icon, user icon) centered in the box

---

## Section Manifest Format

At the bottom of every wireframe HTML file, include a structured manifest as an HTML comment. This manifest is the handoff artifact that `payload-nextjs-stack` consumes.

```json
[
  {
    "order": 1,
    "section": "Navigation",
    "component": "Header",
    "props": {
      "logo": true,
      "navItems": ["Services", "Work", "About", "Blog"],
      "ctaLabel": "Book a Call",
      "ctaUrl": "/contact",
      "sticky": true,
      "transparentOnHero": true
    },
    "responsive": "Hamburger menu on mobile. CTA button always visible in header.",
    "notes": ""
  },
  {
    "order": 2,
    "section": "Hero",
    "component": "HeroSection",
    "block": "hero",
    "props": {
      "eyebrow": "For B2B Agencies",
      "headline": "Marketing websites that actually convert",
      "subheadline": "We build high-performing sites on modern stacks...",
      "primaryCTA": { "label": "Book a Free Strategy Call", "url": "/contact" },
      "secondaryCTA": { "label": "See Our Work", "url": "/work" },
      "image": { "type": "screenshot", "aspect": "16:10" }
    },
    "responsive": "Two columns on desktop, stacked on mobile. Image below text on mobile. CTAs full-width on mobile.",
    "notes": "Image should be a real screenshot of best client work. Priority load."
  }
]
```

Each entry maps to:
- `component` — the React component name in `payload-nextjs-stack`
- `block` — the Payload CMS block slug (if applicable)
- `props` — the content/config the component receives
- `responsive` — key responsive behavior to preserve in production
- `notes` — anything the developer should know

---

## Iteration Workflow

Wireframes are meant to be iterated on. When the user requests changes:

1. **Understand the feedback**: Is it about layout, content, hierarchy, or responsiveness?
2. **Apply the change**: Modify the wireframe HTML.
3. **Update the manifest**: If sections were added, removed, reordered, or structurally changed, update the manifest.
4. **Call out what changed**: Briefly note the changes in your response so the reviewer can focus their re-review.

Common iteration requests:
- "Move the testimonials above the CTA" → reorder sections + update manifest
- "The services grid needs a 4th card" → add card + update props in manifest
- "Make the hero more prominent" → increase heading size, add more whitespace, simplify
- "Add a pricing section" → insert packages section using the pattern above
- "How does this look on mobile?" → remind them to resize browser, or describe the mobile behavior

---

## Workflow Summary

1. **Receive input**: Page blueprint + content hierarchy (from `b2b-marketing-ux` or user description)
2. **If no blueprint**: Generate one using `b2b-marketing-ux` page architecture patterns, confirm with user
3. **Write placeholder content**: Realistic B2B copy for every headline, subheadline, CTA, and body section
4. **Build the wireframe**: Single HTML file, fully responsive, mid-fidelity, with annotation bar
5. **Include section manifest**: Structured comment at bottom of HTML for production handoff
6. **Present for review**: Share the file. Note any open questions or alternative approaches.
7. **Iterate**: Apply feedback, update manifest, re-share.
8. **Approve and hand off**: Once approved, the wireframe HTML + manifest feed into `payload-nextjs-stack`.

---

## Companion Skills

- **`b2b-marketing-ux`** — Upstream. Provides page blueprints, content hierarchy, conversion strategy, and trust signal placement. If no blueprint is provided, use the patterns from this skill to generate one. **Always reference this skill's UX principles when making layout decisions.**
- **`payload-nextjs-stack`** — Downstream. Consumes the section manifest to generate production React components, Payload CMS blocks, and page templates. The wireframe is the visual source of truth for what production code should match.
- **`frontend-design`** — Visual aesthetics reference. When the wireframe moves to production, this skill handles the creative direction upgrade from wireframe palette to final brand design.

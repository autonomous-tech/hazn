---
name: wireframe-fidelity
description: "Deep wireframe-to-implementation fidelity verification. Uses Playwright tests and manual audit to ensure built pages match wireframe specs exactly: copy, CSS, layout, typography, visual details. Extract wireframe specs before building, audit implementation after. Prevents the drift that degrades UX."
---

# wireframe-fidelity

Deep wireframe-to-implementation review skill. Ensures every page built matches its wireframe HTML source of truth — copy, CSS, layout, typography, and visual details.

**Use before and after building any page.** This skill prevents the drift that caused 24 gaps on the homepage.

---

## When to Use

- **Before building a page:** Extract the wireframe's exact content, CSS properties, and structure into a build spec
- **After building a page:** Audit the implementation against the wireframe and flag every deviation
- **Before declaring a phase complete:** Run across all pages touched in that phase

---

## Inputs

- **Wireframe HTML file** from `references/wireframes/{page}.html`
- **Implementation files:** the React component(s), seed command, and relevant CSS

---

## Process

### Step 1: Extract Wireframe Spec

Read the full wireframe HTML file. For EVERY section (identified by `<!-- COMMENT -->` markers or `<section>` tags), extract:

#### A. Content Inventory
- [ ] Every heading (h1-h6): exact text, including line breaks (`<br>`) and decoration (`<span class="squiggle">`)
- [ ] Every body paragraph: exact text, word for word
- [ ] Every CTA: exact text, exact href (convert `.html` to Next.js route with trailing slash)
- [ ] Every eyebrow/label: exact text
- [ ] Every stat: exact value + exact label
- [ ] Every list item, card title, testimonial quote — everything
- [ ] Image references and alt text

#### B. Visual Properties Per Section
For each `<section>`, record:
- [ ] Background: Tailwind class or inline style (e.g., `bg-parchment`, `bg-vermillion`, `bg-ink`)
- [ ] Padding: exact `py-*` and `px-*` values, including responsive variants (`md:py-20 lg:py-24`)
- [ ] Container: `max-w-*` value
- [ ] Grid/flex layout: column count, gap, responsive breakpoints
- [ ] Animation classes: `reveal`, `stagger`, `hero-stagger`, `marquee-track`

#### C. Typography Per Element
For each text element, record:
- [ ] Font family: Fraunces (display), DM Sans (body), or JetBrains Mono (mono)
- [ ] Font size: exact `clamp()` values or Tailwind size classes
- [ ] Font weight: 400, 500, 600, 700 — exact value
- [ ] Letter spacing: `-0.04em`, `-0.03em`, or `tracking-wider`
- [ ] Line height: exact decimal (0.92, 1.05, 1.1, 1.7)
- [ ] Color: exact Tailwind class (`text-ink`, `text-prose`, `text-white/60`, etc.)
- [ ] `font-variation-settings` if present (e.g., `'opsz' 144`)

#### D. Component Details
- [ ] Card styles: border-radius, padding, shadow, border, hover states
- [ ] Button styles: bg color, text color, padding, border-radius, hover effects
- [ ] Icon sizes and colors
- [ ] Divider styles: color, opacity, spacing
- [ ] Special treatments: noise overlay opacity, radial glow gradients, diagonal stripe textures

### Step 2: Compare Against Implementation

For each section from Step 1, read the corresponding React component and seed data. Compare EVERY property:

#### A. Content Check
- [ ] Does the seed data match the wireframe text **word for word**?
- [ ] Are CTA hrefs correct? (wireframe `.html` → Next.js route with `/`)
- [ ] Are all items present? (e.g., all 15 marquee clients, not 5)
- [ ] Is text structure preserved? (line breaks via `<span class="block">`, `<br>` tags)

#### B. CSS/Visual Check
- [ ] Do Tailwind classes match exactly? (compare class strings side by side)
- [ ] Do inline styles match? (font-size, letter-spacing, line-height, color, opacity)
- [ ] Are background treatments identical? (gradients, patterns, overlays)
- [ ] Are shadows the same format? (`shadow-[0_2px_16px_rgba(0,0,0,0.06)]`)
- [ ] Are hover states correct? (hover colors, transforms, transitions)
- [ ] Are responsive breakpoints the same? (`sm:`, `md:`, `lg:` prefixes)

#### C. Global CSS Check
Compare `globals.css` classes against wireframe `<style>` block:
- [ ] `.hero-headline` — font-size clamp values, line-height, letter-spacing
- [ ] `.section-headline` — font-size clamp values, line-height, font-family
- [ ] `body::after` noise overlay — opacity value (wireframe: 0.35)
- [ ] Animation durations, easings, delays
- [ ] Squiggle underline SVG strokes

#### D. Navigation Check (if homepage or layout)
- [ ] Nav positioning (fixed, z-index, centering method)
- [ ] Glass morphism properties (bg-white/75, backdrop-blur-2xl, rounded-full)
- [ ] Dropdown interaction model (hover vs click)
- [ ] Mobile drawer structure and z-index stack
- [ ] Announcement bar properties

#### E. Footer Check
- [ ] Column count and content
- [ ] Nested links flattened correctly
- [ ] Padding, spacing between links
- [ ] Border-top on footer element
- [ ] Copyright text
- [ ] Tagline text

### Step 3: Generate Gap Report

Produce a structured report in this format:

```markdown
# Wireframe Fidelity Report: {page-name}

**Wireframe:** `references/wireframes/{page}.html`
**Date:** {date}
**Status:** {X gaps found / Clean}

## Content Gaps
| # | Section | Field | Wireframe Value | Implementation Value | File |
|---|---------|-------|-----------------|---------------------|------|

## Visual Gaps
| # | Section | Property | Wireframe | Implementation | File |
|---|---------|----------|-----------|----------------|------|

## Navigation Gaps (if applicable)
| # | Element | Property | Wireframe | Implementation | File |
|---|---------|----------|-----------|----------------|------|
```

### Step 4: Build Spec (Pre-Build Mode)

When used BEFORE building, produce a **build spec** instead of a gap report:

```markdown
# Build Spec: {page-name}

**Wireframe:** `references/wireframes/{page}.html`

## Section-by-Section Spec

### Section 1: {name}
- **Background:** {exact classes}
- **Padding:** {exact classes}
- **Content:**
  - Eyebrow: "{exact text}"
  - Headline: "{exact text with markup notes}"
  - Body: "{exact text}"
  - CTA: "{text}" → {url}
  - Stats: {value}: {label} (for each)
- **Typography:** {font, size, weight, color for each element}
- **Layout:** {grid/flex config with responsive breakpoints}
- **Cards/Items:** {count, styles, hover states}
- **Animations:** {classes to apply}

### Section 2: {name}
...
```

This spec becomes the reference for the developer building the page — eliminating guesswork.

---

## Principles

1. **The wireframe HTML is the source of truth** — not CLAUDE.md, not memory, not assumptions. When in doubt, read the wireframe.
2. **Word-for-word copy** — Don't paraphrase, don't "improve", don't abbreviate. If the wireframe says "we engineer", the seed must say "we engineer", not "we build".
3. **Exact CSS values** — `0.35` is not `0.035`. `3.8rem` is not `3.2rem`. `space-y-3` is not `space-y-2.5`. Every value matters.
4. **Count everything** — If the wireframe shows 15 marquee clients, seed 15. If it shows 4 stats, seed 4. Don't skip items.
5. **Preserve structure** — If the wireframe uses `<span class="block">` for line breaks, the component must do the same. If it uses `<br class="hidden md:block">`, note it.
6. **Convert hrefs** — Wireframe uses `page.html`, implementation uses `/page/` with trailing slash. This is the ONLY acceptable transformation.
7. **Flag decisions, don't assume** — If the wireframe contradicts CLAUDE.md (e.g., font-family on section headlines), flag it as a decision point. Don't silently pick one.

---

## Completion Checklist

Before signing off on any page:

- [ ] Every text string in seed data matches wireframe word-for-word
- [ ] All items/lists are complete (no missing cards, clients, stats, testimonials)
- [ ] CTA text and URLs match (with .html → /slug/ conversion)
- [ ] Background colors/styles per section match
- [ ] Typography (font, size, weight, spacing, line-height, color) matches per element
- [ ] Card/component styles (radius, padding, shadow, border, hover) match
- [ ] Responsive breakpoints match (sm/md/lg prefixes)
- [ ] Animation classes applied correctly
- [ ] Global CSS values (noise opacity, headline sizes) are correct
- [ ] Footer links include nested children
- [ ] No property is more than 1 Tailwind unit off from wireframe

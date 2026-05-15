# Element Roles & Rules Reference

> For each design role, the exact properties to check and their expected values.
> Used by the role-based element audit (SKILL.md Step 1.3).
> Every rule is binary: PASS or FAIL. No judgment calls.

---

## How to Use

1. Read a component file
2. For each visible JSX element, assign a role from this document
3. For each role, check every property listed
4. Record PASS/FAIL per property

---

## Role: `page-section`

**Applies to:** `<section>` elements

| Property | Rule | Fail = |
|----------|------|--------|
| `padding` | Standard: `py-16 md:py-20 lg:py-24`. Hero: `pt-36 pb-16 md:pb-20 lg:pb-24` or `pt-32 pb-20 md:pt-36 md:pb-28`. Compact bands (urgency, CTA): `py-12`. Other values need justification. | 🟡 |
| `overflow` | If section contains ANY child with `absolute` or `fixed` positioning → MUST have `overflow-hidden` on the `<section>`. | 🔴 |
| `background` | Should match the design intent (check wireframe): `bg-parchment`, `bg-white`, `bg-ink`, `bg-vermillion`, `bg-parchment-light`, or gradient via `style={}`. | 🟡 |

---

## Role: `section-inner`

**Applies to:** First `<div>` inside `<section>` — the content container

| Property | Rule | Fail = |
|----------|------|--------|
| `container` | MUST have: `max-w-{size} mx-auto px-6 lg:px-8` where size is `7xl` (standard), `6xl`, `5xl`, `4xl`, or `3xl` (narrow). Missing `mx-auto` = not centered. Missing `px-6` = no horizontal padding on mobile. | 🔴 |

---

## Role: `header-group`

**Applies to:** Wrapper around eyebrow + heading + optional description, before the main content grid/cards

| Property | Rule | Fail = |
|----------|------|--------|
| `bottom-margin` | Gap to content below: `mb-10 md:mb-12` or `mb-12 md:mb-16`. Using `mb-4`, `mb-6`, or `mb-8` between header group and content grid = too tight. | 🟡 |
| `alignment` | Centered sections (cards below): `text-center`. Asymmetric layouts (2-col): `text-center lg:text-left` or just left on large screens. | 🟡 |

---

## Role: `hero-heading`

**Applies to:** `<h1>` in a hero section (first section on the page)

| Property | Rule | Fail = |
|----------|------|--------|
| `css-class` | MUST use the correct CSS class for the page type (see table below). Using inline `style={{fontFamily, fontSize, ...}}` = 🔴. Using raw `text-5xl`/`text-6xl`/etc. = 🔴. | 🔴 |
| `color` | On light hero (parchment bg): add `text-ink`. On dark hero: the hero-headline-* class already sets `color: var(--color-parchment-light)` — do NOT add a text color that conflicts. | 🟡 |
| `responsive-align` | Asymmetric heroes (hero + bg image, or hero with stats on side): `text-center lg:text-left`. Centered heroes: `text-center`. **Light heroes with 2-col grid** (e.g., engineering): the stagger container needs `mx-auto lg:mx-0 text-center lg:text-left`, subhead needs `mx-auto lg:mx-0`, CTA group needs `justify-center lg:justify-start` — same trio as dark heroes. | 🟡 |
| `no-font-bold` | Hero classes are weight 400 or 500. Adding `font-bold` or `font-semibold` = wrong. | 🟡 |

### Page-Type → Hero Class Mapping

| Pages | Hero Class |
|-------|-----------|
| `/` (homepage) | `hero-headline` |
| `/contact/`, `/pricing/`, `/work/`, `/ecommerce/operations/` | `hero-headline-compact` |
| `/work/[slug]/` (case studies) | `hero-headline-case` |
| `/marketing/`, `/ecommerce/` | `hero-headline-flex` |
| `/engineering/` | `hero-headline-md` (light hero, 2-col with cluster panel) |
| `/intelligence/sitescore/`, `/intelligence/attributioncheck/`, `/intelligence/searchintel/`, `/intelligence/conversioniq/`, `/intelligence/analyticsaudit/` | `hero-headline-md` |
| `/intelligence/` (suite hub) | `hero-headline-lg` |
| All other service pages (engineering, agency, enterprise, fintech, etc.) | `hero-headline-flex` (default in DarkHero component) |

---

## Role: `section-heading`

**Applies to:** `<h2>` — section titles within the page body (not in the hero)

| Property | Rule | Fail = |
|----------|------|--------|
| `css-class` | MUST have `section-headline` class. Raw `font-display` + manual size classes (`text-3xl md:text-5xl`) = 🔴. | 🔴 |
| `color-light` | On light background: `text-ink`. | 🟡 |
| `color-dark` | On dark background: `text-white`. | 🔴 (invisible) |
| `no-font-bold` | `section-headline` is weight 400. Adding `font-bold`/`font-semibold` = 🟡. | 🟡 |
| `no-inline-style` | No `style={{fontFamily: ...}}`. The class handles it. | 🔴 |

---

## Role: `card-title`

**Applies to:** `<h3>`, `<h4>` inside a card component

| Property | Rule | Fail = |
|----------|------|--------|
| `font` | DM Sans (the default body font). MUST NOT have `font-display` class — card titles are NOT display type. Fraunces on a card title = 🟡. | 🟡 |
| `weight` | `font-medium` (preferred) or `font-semibold`. Not `font-bold`. | — |
| `color-light` | `text-ink`. | — |
| `color-dark` | `text-white`. Default heading color from `@layer base` is `text-ink` — on a dark card this is invisible without override. | 🔴 |

---

## Role: `eyebrow`

**Applies to:** Small label text above a section heading (e.g., "Our Approach", "Why Autonomous")

| Property | Rule | Fail = |
|----------|------|--------|
| `component` | MUST use `<EyebrowLabel>` component. Manual `<span className="font-mono uppercase tracking-wider...">` = 🔴. Manual `<p className="text-xs font-mono...">` = 🔴. | 🔴 |
| `color-light` | Color prop: `vermillion` (default) or `caption`. | — |
| `color-dark` | Color prop: `white`, `gold`, or `ocean`. Using `vermillion` on dark bg = 🟡 (low contrast). | 🟡 |
| `spacing-below` | Gap to heading below: `mt-4` on the heading (not `mb-X` on eyebrow). Or eyebrow div has no bottom margin and heading has `mt-4`/`mt-6`. | — |

**Special case: DarkHero eyebrow.** DarkHero uses its own eyebrow pattern (`<span className="text-sm font-mono...">` with a colored line before it). This is by design — the DarkHero eyebrow includes a horizontal line + badge which EyebrowLabel doesn't support. This is an **intentional deviation**, not a finding.

---

## Role: `body-text`

**Applies to:** `<p>` elements with paragraph content

| Property | Rule | Fail = |
|----------|------|--------|
| `font` | DM Sans (default, no class needed). | — |
| `color-light` | `text-prose`. | — |
| `color-dark` | `text-white/60`, `text-white/70`, or `text-parchment/70`. Not bare `text-white` (that's for headings). | 🟡 |
| `leading` | `leading-relaxed` for body paragraphs. | — |
| `line-length` | Inside a constrained container: `max-w-2xl`, `max-w-3xl`, or within a grid column that limits width. Full-width body text in `max-w-7xl` with no constraint = 🟡. | 🟡 |
| `color-dark-visible` | On dark background: MUST have explicit light color. Inheriting default `text-prose` on `bg-ink` = invisible. | 🔴 |

---

## Role: `muted-text`

**Applies to:** Captions, footnotes, sub-labels, secondary descriptions

| Property | Rule | Fail = |
|----------|------|--------|
| `color-light` | `text-caption` or `text-prose`. | — |
| `color-dark` | `text-white/40` or `text-white/50` or `text-white/60`. | 🔴 if missing on dark bg |
| `size` | `text-sm` or `text-xs`. | — |

---

## Role: `stat-value`

**Applies to:** Display numbers in stats strips (67%, 3×, $1.2M, 15+)

| Property | Rule | Fail = |
|----------|------|--------|
| `font` | MUST be Fraunces. Check for `font-display` class OR `style={{fontFamily: "var(--font-display)"}}`. Using default DM Sans for stat numbers = 🟡. | 🟡 |
| `color-light` | `text-ink`. | — |
| `color-dark` | `text-white`. | 🔴 |
| `weight` | `font-medium` or default 400. NOT `font-bold`. | 🟡 |
| `size` | Display-level: `text-3xl` or `text-4xl` or larger. Smaller = 🟡. | 🟡 |
| `centering` | Inside a hero-stagger container with `text-center lg:text-left`: the stat flex row must have `justify-center lg:justify-start` and individual stat items need `text-center lg:text-left`. Without this, stats pile left on mobile while all other hero content centers. | 🟡 |

---

## Role: `stat-label`

**Applies to:** Label text below a stat value

| Property | Rule | Fail = |
|----------|------|--------|
| `font` | DM Sans (default) or JetBrains Mono (`font-mono`). | — |
| `color-light` | `text-caption` or `text-prose`. | — |
| `color-dark` | `text-white/40` or `text-white/50` or `text-white/60`. | 🔴 if missing |
| `size` | `text-sm` or `text-xs`. | — |

---

## Role: `cta-primary`

**Applies to:** Primary action buttons (the main CTA — "Get Your Free Report", "Let's Talk About Your Stack")

| Property | Rule | Fail = |
|----------|------|--------|
| `component` | Prefer `<Button>` component. Raw `<Link>` with `bg-vermillion rounded-full px-8 py-4` works but is inconsistent = 🟡. Raw `<a>` = 🟡. | 🟡 |
| `display` | `inline-flex items-center justify-center` (Button provides this). `inline-block` = 🟡. | 🟡 |
| `arrow` | If children include text `→` appended (e.g., `{text} →`) = 🔴. Use SVG arrow or no arrow. | 🔴 |
| `radius` | `rounded-full`. | — |
| `size` | Standard: `px-8 py-4 text-base` (Button `size="lg"`). | — |
| `hover` | `hover:bg-vermillion-light` or similar. Present. | — |

---

## Role: `cta-secondary`

**Applies to:** Secondary/ghost buttons (border style, "See Our Work →")

| Property | Rule | Fail = |
|----------|------|--------|
| `display` | `inline-flex items-center justify-center gap-2`. | 🟡 |
| `border` | Dark bg: `border border-white/20`. Light bg: `border border-current` or `border border-ink/20`. | — |
| `radius` | `rounded-full`. | — |
| `arrow` | SVG arrow inside. Text `→` = 🔴 (except inside `<Button variant="text">`). | 🔴 |
| `no-group-hover-span` | Should NOT use `<span className="group-hover:translate-x-1">→</span>` pattern. Use SVG directly. | 🟡 |

---

## Role: `cta-text`

**Applies to:** Text-style links ("View all services →", "Learn more →")

| Property | Rule | Fail = |
|----------|------|--------|
| `pattern` | Either `<Button variant="text">` (which auto-appends `→`) OR `inline-flex items-center gap-2` with SVG arrow. | 🟡 |
| `color` | `text-vermillion`. | — |
| `hover` | Some visible hover effect (underline, color change, arrow move). | — |

---

## Role: `cta-group`

**Applies to:** Flex wrapper that contains 1+ CTA buttons

| Property | Rule | Fail = |
|----------|------|--------|
| `layout` | `flex flex-col sm:flex-row gap-4` or `flex flex-wrap gap-4`. | — |
| `align-items` | `items-center`. | 🟡 |
| `responsive-justify` | **Asymmetric layout** (hero with side image, 2-col section): `justify-center lg:justify-start`. **Centered layout** (full-width centered section): `justify-center`. | 🟡 |
| `margin-top` | `mt-10` or similar (space above CTAs from content). | — |

---

## Role: `card`

**Applies to:** Card container div/article

| Property | Rule | Fail = |
|----------|------|--------|
| `radius` | `rounded-2xl`. NOT `rounded-3xl` = 🟡. NOT `rounded-xl` = 🟡. | 🟡 |
| `shadow-light` | Standard: `shadow-[0_2px_16px_rgba(0,0,0,0.06)]` or subtle variant. `shadow-lg`/`shadow-xl` without hover qualifier = 🟡. | 🟡 |
| `shadow-dark` | Dark cards: No shadow. Use `bg-white/5 border border-white/10` or `bg-midnight`. | — |
| `hover` | Interactive cards: `hover:-translate-y-1 transition-all duration-300`. | — |
| `padding` | `p-6` (standard), `p-7`, `p-8` (spacious). On mobile, if card has wide content (CTA buttons, inline rows), use `p-5 sm:p-8` to give content room at 375px. Calculate: 375 − 48 (container) − padding*2 = available width. If card CTA is ≥200px and available < 260px → reduce mobile padding. | 🟡 |
| `overflow` | Cards with inline CTA buttons or wide content: `overflow-hidden` to prevent horizontal page scroll if content slightly exceeds bounds. | 🟡 |

---

## Role: `process-steps`

**Applies to:** Numbered step sequences (How We Work, process flows). Reference implementation: `homepage/HowWeWorkSection.tsx`.

| Property | Rule | Fail = |
|----------|------|--------|
| `number-to-title-gap` | Circle/number element margin-bottom to h3: `mb-3`. Larger values (`mb-6`) create ambiguity about which title belongs to which number, especially on stacked mobile layouts. | 🟡 |
| `title-to-body-gap` | h3 margin-bottom to description p: `mb-2`. Larger values (`mb-3`+) weaken the visual grouping of title+body within a step. | 🟡 |
| `grid-gap` | Container gap: `gap-6`. Larger values (`gap-8`+) make step-to-step separation similar to number-to-title separation, breaking the proximity hierarchy. | 🟡 |
| `mobile-scroll` | On mobile (< sm), steps SHOULD use horizontal snap scroll: `flex overflow-x-auto snap-x snap-mandatory scrollbar-hide` with `sm:grid sm:overflow-visible sm:snap-none`. Each step card: `flex-shrink-0 w-[85%] snap-center sm:w-auto`. Without this, stacked steps blur together on small screens. | 🟡 |
| `font-consistency` | Step title h3: `text-lg font-medium` (body font). Do NOT use `font-display` or `font-semibold` on step titles — they should be lighter than section headings to maintain hierarchy. | 🟡 |
| `cross-page-parity` | Process steps sections across pages MUST use identical spacing and structure. Compare against homepage `HowWeWorkSection.tsx` as the canonical reference. | 🟡 |

---

## Role: `grid-layout`

**Applies to:** Grid containers for cards, features, etc.

| Property | Rule | Fail = |
|----------|------|--------|
| `responsive` | Must start as 1-col on mobile, add columns at breakpoints: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`, etc. Or for 2-col: `grid lg:grid-cols-2`. | 🟡 |
| `cta-column-width` | If cards in the grid contain CTA buttons with multi-word text, the breakpoint to N-col must be high enough that button text doesn't wrap to 3+ lines. For 3-col grids with CTA buttons, prefer `min-[900px]:grid-cols-3` over `md:grid-cols-3` (768px is too narrow). | 🟡 |
| `content-squeeze` | At the **minimum** width of each breakpoint, does card content fit? Calculate: `(viewport - container padding - gaps) / cols`. At `md:grid-cols-3` (768px): each col ≈ 230px. If card has badges + CTA buttons + long text → too tight. Use `lg:grid-cols-3` or custom breakpoint. | 🟡 |
| `two-col-align` | `lg:grid-cols-2` grids with mixed content (text + image, text + cards): `items-center`. | 🟡 |
| `gap` | `gap-6` to `gap-12` standard. `gap-20` only for narrative 2-col. | — |

---

## Role: `inline-row`

**Applies to:** Horizontal flex/inline-flex rows of small items (badge rows, trust signals, tag groups, tier badge rows, icon+text pairs)

| Property | Rule | Fail = |
|----------|------|--------|
| `wrap` | Rows of badges, tags, or trust signals MUST have `flex-wrap` if there are 3+ items or total content width > ~300px. Without `flex-wrap`, items overflow or squeeze on mobile. | 🟡 |
| `gap` | `gap-2` to `gap-4` between inline items. `gap-8`+ between inline items is too wide for mobile. | — |
| `centering` | In a `text-center` parent context, the flex row needs `justify-center` to actually center. | 🟡 |
| `mobile-stack` | If items are too wide to sit side-by-side on 375px, use `flex-col sm:flex-row` to stack on mobile. | 🟡 |

---

## Role: `image-hero`

**Applies to:** Hero background/decorative images

| Property | Rule | Fail = |
|----------|------|--------|
| `component` | `next/image` (not `<img>`). | 🔴 |
| `priority` | MUST have `priority` prop (LCP). | 🟡 |
| `responsive` | Large decorative hero images SHOULD be `hidden lg:block` to avoid mobile overlap/overflow. | 🟡 |
| `pointer` | `pointer-events-none`. | 🟡 |
| `a11y` | `aria-hidden="true"`. | 🟡 |

---

## Role: `image-content`

**Applies to:** In-content images (case study photos, team photos, etc.)

| Property | Rule | Fail = |
|----------|------|--------|
| `component` | `next/image` (not `<img>`). | 🔴 |
| `props` | MUST have `width`, `height`, `sizes`. | 🟡 |
| `radius` | Standalone content images: `rounded-2xl`. | 🟡 |
| `alt` | Has meaningful `alt` text (not empty for content images). Decorative images: `alt=""` or `aria-hidden`. | 🟡 |

---

## Role: `decorative`

**Applies to:** Absolute/fixed positioned overlays (blobs, gradients, patterns)

| Property | Rule | Fail = |
|----------|------|--------|
| `pointer` | `pointer-events-none`. | 🟡 |
| `parent-overflow` | Parent `<section>` or wrapper MUST have `overflow-hidden`. | 🔴 |

---

## Role: `arrow-icon`

**Applies to:** Directional arrow icons in CTAs and links

| Property | Rule | Fail = |
|----------|------|--------|
| `type` | MUST be SVG. The standard arrow: `<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" /></svg>`. Text `→` only inside `<Button variant="text">` (component handles it). | 🔴 |
| `a11y` | `aria-hidden="true"`. | 🟡 |

---

## Role: `nav-item`

**Applies to:** Navigation elements (checked only when auditing global nav)

| Property | Rule | Fail = |
|----------|------|--------|
| `breakpoint` | Desktop nav uses `min-[930px]` (not `md:`/768px). Mobile hamburger shows below 930px. | 🔴 |

---

## Role: `footer-link`

**Applies to:** Links in the footer (checked only when auditing footer)

| Property | Rule | Fail = |
|----------|------|--------|
| `color` | `text-white/40 hover:text-white`. NOT `text-parchment-dark`. | 🟡 |

---

## Quick Decision Tree

```
Is it a <section>?                    → page-section
Is it the container div in section?   → section-inner
Is it a <h1>?                         → hero-heading
Is it a <h2>?                         → section-heading
Is it a <h3>/<h4> inside a card?      → card-title
Is it eyebrow text above heading?     → eyebrow
Is it a <p> paragraph?                → body-text
Is it a small label/caption?          → muted-text
Is it a display number (stat)?        → stat-value
Is it a label under a stat?           → stat-label
Is it a primary CTA button?           → cta-primary
Is it a ghost/outline button?         → cta-secondary
Is it a text link with arrow?         → cta-text
Is it a wrapper around CTAs?          → cta-group
Is it a card wrapper div?             → card
Is it a grid container div?           → grid-layout
Is it a numbered steps sequence?      → process-steps
Is it a row of badges/tags/signals?   → inline-row
Is it a hero background image?        → image-hero
Is it a content image?                → image-content
Is it an absolute/fixed overlay?      → decorative
Is it an arrow SVG or →?              → arrow-icon
Is it eyebrow+heading+desc wrapper?   → header-group
```

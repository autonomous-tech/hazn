# Editorial Warmth v2 — Design Tokens

Verbatim tokens from `repos/products/website/references/docs/editorial-warmth-v2.html`. Copy-paste into the audit HTML's `:root` block. Non-negotiable.

## Color palette

```css
:root {
  /* Base parchment (primary background spectrum) */
  --parchment:        #F5EFE0;   /* primary bg */
  --parchment-light:  #FAF7F0;   /* card bg, alternating sections */
  --parchment-dark:   #EDE5D3;   /* borders, dividers */

  /* Midnight (dark hero / accent sections) */
  --midnight:         #0D0D1F;   /* hero backdrop */
  --midnight-light:   #1A1A35;   /* hover, dark card variant */

  /* Vermillion (primary accent / CTA) */
  --vermillion:       #E8513D;   /* CTA, primary accent, headlines */
  --vermillion-light: #F06B59;   /* hover */
  --vermillion-dark:  #C43E2C;   /* pressed, border accents */

  /* Indigo (secondary) */
  --indigo:           #1E3A8A;
  --indigo-light:     #2D4EA3;

  /* Status semantics */
  --sage:             #7CA982;   /* pass / positive / strength */
  --gold:             #D4A853;   /* warning / medium severity */
  --ocean:            #0EA5E9;   /* info / opportunity / link */

  /* Typography colors */
  --ink:              #1A1A2E;   /* headings, heavy text */
  --prose:            #4A4A60;   /* body text */
  --caption:          #7A7A90;   /* muted labels, footnotes */

  /* Structural */
  --rule:             rgba(0,0,0,0.08);
  --shadow-card:      0 2px 16px rgba(0,0,0,0.06);
  --shadow-card-hover: 0 6px 28px rgba(0,0,0,0.09);
  --radius-lg:        1rem;
  --radius-xl:        1.25rem;

  /* Fonts */
  --font-display:     'Fraunces', Georgia, serif;
  --font-body:        'DM Sans', system-ui, -apple-system, sans-serif;
  --font-mono:        'JetBrains Mono', ui-monospace, monospace;
}
```

## Typography

### Google Fonts import (in `<head>`)
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,600;0,9..144,700&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

### Hierarchy
```css
/* H1 — hero only */
.hero-headline {
  font-family: var(--font-display);
  font-size: clamp(2.6rem, 6vw, 5rem);
  font-weight: 400;
  letter-spacing: -0.04em;
  line-height: 1.0;
  font-variation-settings: 'opsz' 144;
  color: var(--parchment-light);
}

/* H2 — section headlines */
.section-headline {
  font-family: var(--font-display);
  font-size: clamp(1.8rem, 3.8vw, 2.8rem);
  font-weight: 400;
  letter-spacing: -0.03em;
  line-height: 1.1;
  font-variation-settings: 'opsz' 72;
  color: var(--ink);
}

/* H3 — sub-section headings */
.h3-serif {
  font-family: var(--font-display);
  font-size: 1.4rem;
  font-weight: 500;
  color: var(--ink);
  margin-bottom: 0.6rem;
}

/* H4 — card titles */
.card-title {
  font-family: var(--font-body);
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--ink);
}

/* Body */
body {
  font-family: var(--font-body);
  font-size: 17px;        /* 17 not 18 — feels lighter on parchment */
  line-height: 1.7;
  color: var(--prose);
  background: var(--parchment);
}

/* Eyebrow / label / caption */
.eyebrow {
  font-family: var(--font-mono);
  font-size: 11.5px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--vermillion);
}

/* Code / kbd */
.kbd {
  font-family: var(--font-mono);
  font-size: 0.92em;
  background: var(--parchment-dark);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--ink);
}
```

## Status semantics

| Status | Color | Use case |
|---|---|---|
| Pass | `var(--sage)` | Score ≥ 70, healthy finding, "doing right" |
| Warning | `var(--gold)` | Score 50-69, MEDIUM severity finding |
| Critical / Fail | `var(--vermillion)` | Score < 50, HIGH severity finding |
| Opportunity | `var(--ocean)` | Info, future workstream, blue-ocean SERP |
| N/A | `var(--indigo)` | Background context, secondary info |

## Score circle thresholds

```javascript
function scoreColor(score) {
  if (score >= 70) return 'var(--sage)';
  if (score >= 50) return 'var(--gold)';
  return 'var(--vermillion)';
}
```

## Component classes (defined in template-snippets)

- `.hero` — midnight-backed top section
- `.section-wrap` (with `.light` modifier) — parchment-light alternating bg
- `.container` — max-width 1200px, padding 2rem
- `.card` — white bg, rounded-2xl, shadow-card
- `.callout` (with `.critical | .warning | .strength | .opportunity` modifiers) — colored left border
- `.score-card` — score circle + module name + summary
- `.finding` (with `.critical | .warning | .strength`) — left-border severity card
- `.qw-card` — numbered quick-win card
- `.impact-card` — Alarm section impact summary card
- `.pill-score` (with `.sage | .gold | .vermillion`) — module score pill
- `.badge` (with `.pass | .warning | .critical | .info`) — status badge
- `.grid-2` / `.grid-3` — responsive grid utilities
- `.toc` (sticky sidebar) — left-side nav
- `.kbd` — inline code style
- `.squiggle-vermillion` / `.squiggle-gold` — text underline accent

## FORBIDDEN (deprecated Proposals Dark — refuse to output)

| Forbidden | Replacement |
|---|---|
| `#0a0a12` | `#F5EFE0` (parchment) |
| Cyan-to-purple gradient `linear-gradient(135deg, #00d5ff, #b42aff)` | Solid `var(--vermillion)` or `var(--ink)` |
| `Outfit` font | `Fraunces` (display) or `DM Sans` (body) |
| `Pathway Extreme` font | `DM Sans` |
| Tagline "Canadian Expertise. Pakistani Efficiency. World-class Quality." | Use the Editorial Warmth tagline / no tagline |

If any forbidden token appears in the rendered output, regenerate the section.

## Voice

"Warm, editorial, precise."

- Confident but not promotional
- Specific over generic ("BreezeTech bamboo shirt" not "the product")
- Numbers cited with ranges, not single values
- Findings cite file:line evidence
- No hype words: avoid "amazing," "huge," "massive" — use specific numbers instead

## Visual signature elements

- **Squiggle underline:** vermillion or gold SVG background-image on selected H2 emphasis words
- **Noise texture overlay:** subtle SVG fractalNoise filter at 0.035 opacity, pointer-events none, fixed inset 0
- **Score circles:** SVG with stroke-dasharray, color by threshold
- **Sticky TOC:** 220-240px fixed left, parchment-dark border, scroll-spy active in vermillion
- **Print stylesheet:** hides sidebar, single-column, no shadows

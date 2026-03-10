# Brand Guide — Autonomous Tech
## "Editorial Warmth" Design System v2
### Source: `/home/rizki/autonomous-proposals/wireframes-v2/`

This is the canonical brand guide for all Hazn-generated reports, audits, proposals, and HTML deliverables. Extracted directly from the wireframes-v2 source files (Feb 2026).

---

## Font Loading

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,400;1,9..144,500&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
```

| Role | Font | Notes |
|------|------|-------|
| Display / Headings | **Fraunces** | Variable optical size (`opsz`). Use `font-variation-settings: 'opsz' 144` for hero, `opsz 72` for section titles. |
| Body | **DM Sans** | All body copy, UI labels, cards. |
| Mono / Eyebrows | **JetBrains Mono** | Section labels, tags, code snippets. |

---

## Tailwind Config (extend)

```js
tailwind.config = {
  theme: {
    extend: {
      fontFamily: {
        display: ['Fraunces', 'Georgia', 'serif'],
        body: ['DM Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        parchment:          '#F5EFE0',
        'parchment-light':  '#FAF7F0',
        'parchment-dark':   '#EDE5D3',
        midnight:           '#0D0D1F',
        'midnight-light':   '#1A1A35',
        vermillion:         '#E8513D',
        'vermillion-light': '#F06B59',
        'vermillion-dark':  '#C43E2C',
        indigo:             '#1E3A8A',
        'indigo-light':     '#2D4EA3',
        sage:               '#7CA982',
        'sage-light':       '#A7C4A0',
        gold:               '#D4A853',
        ocean:              '#0EA5E9',
        ink:                '#1A1A2E',
        prose:              '#4A4A60',
        caption:            '#7A7A90',
        rule:               'rgba(0,0,0,0.08)',
      }
    }
  }
}
```

---

## Color Reference

| Token | Hex | Usage |
|-------|-----|-------|
| `parchment` | `#F5EFE0` | Primary page background |
| `parchment-light` | `#FAF7F0` | Cards, alternate light sections |
| `parchment-dark` | `#EDE5D3` | Borders, dividers, table headers |
| `midnight` | `#0D0D1F` | Dark sections: hero (when dark), CTA, footer |
| `midnight-light` | `#1A1A35` | Dark card backgrounds, nav dark variant |
| `ink` | `#1A1A2E` | Primary headings, strong text |
| `prose` | `#4A4A60` | Body text |
| `caption` | `#7A7A90` | Labels, metadata, muted text |
| `rule` | `rgba(0,0,0,0.08)` | Dividers, borders |
| `vermillion` | `#E8513D` | **Primary accent** — CTAs, eyebrows, active states, squiggle |
| `vermillion-light` | `#F06B59` | Hover on vermillion |
| `vermillion-dark` | `#C43E2C` | Pressed state |
| `indigo` | `#1E3A8A` | Secondary accent — trust, technical, data |
| `sage` | `#7CA982` | Positive / pass / success |
| `gold` | `#D4A853` | Warning / attention / premium |
| `ocean` | `#0EA5E9` | Info / links / interactive |

---

## Base CSS

```css
*, *::before, *::after { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { font-family: 'DM Sans', system-ui, sans-serif; background: #F5EFE0; color: #4A4A60; overflow-x: hidden; }
h1, h2, h3, h4, h5, h6 { font-family: 'Fraunces', Georgia, serif; color: #1A1A2E; }

/* Grain texture overlay */
body::after {
  content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 9999; opacity: 0.35;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
}
```

---

## Typography Classes

```css
/* Hero display — use for main page H1s */
.hero-headline {
  font-family: 'Fraunces', Georgia, serif;
  font-size: clamp(3.2rem, 9vw, 8.5rem);
  font-weight: 400;
  letter-spacing: -0.04em;
  line-height: 0.92;
  font-variation-settings: 'opsz' 144;
  color: #FAF7F0; /* on dark bg */
}

/* Section headline — H2s */
.section-headline {
  font-family: 'Fraunces', Georgia, serif;
  font-size: clamp(2rem, 4.5vw, 3.8rem);
  font-weight: 400;
  letter-spacing: -0.03em;
  line-height: 1.05;
  font-variation-settings: 'opsz' 72;
}
```

**Tailwind equivalents:**
- Hero H1: `text-[clamp(3rem,8vw,9rem)] font-medium tracking-[-0.06em] leading-[0.95] text-ink font-display`
- Section H2: `text-[clamp(2rem,4vw,3.5rem)] font-medium tracking-[-0.03em] text-ink font-display`
- Eyebrow/label: `text-sm font-semibold uppercase tracking-wider text-vermillion font-mono`
- Body: `text-lg leading-relaxed text-prose`
- Caption: `text-sm text-caption`

---

## Squiggle Underline Accents

```css
/* Vermillion squiggle — use on hero highlight words */
.squiggle {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='10' viewBox='0 0 80 10'%3E%3Cpath d='M0 5 Q20 0 40 5 Q60 10 80 5' fill='none' stroke='%23E8513D' stroke-width='2.5' opacity='0.6'/%3E%3C/svg%3E");
  background-repeat: repeat-x; background-position: bottom; padding-bottom: 8px; background-size: 40px 7px;
}

/* Gold squiggle — secondary emphasis */
.squiggle-gold {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='10' viewBox='0 0 80 10'%3E%3Cpath d='M0 5 Q20 0 40 5 Q60 10 80 5' fill='none' stroke='%23D4A853' stroke-width='2.5' opacity='0.6'/%3E%3C/svg%3E");
  background-repeat: repeat-x; background-position: bottom; padding-bottom: 8px; background-size: 40px 7px;
}
```

---

## Section Backgrounds (pattern)

Sections alternate between:

```html
<!-- Light parchment (default) -->
<section class="bg-parchment py-16 md:py-20 lg:py-24">

<!-- Pure white (mid sections) -->
<section class="bg-white py-16 md:py-20 lg:py-24">

<!-- Dark midnight (hero, CTA, footer) -->
<section class="bg-midnight py-16 md:py-20 lg:py-24">
```

---

## Navigation (floating pill)

```html
<nav class="fixed top-12 left-1/2 -translate-x-1/2 z-[100] bg-white/75 backdrop-blur-2xl rounded-full shadow-[0_2px_20px_rgba(0,0,0,0.06)] border border-black/[0.04] px-3 py-2 flex items-center gap-1 max-w-4xl">
  <!-- Logo -->
  <a href="#" class="px-5 py-2.5 font-display text-sm font-semibold text-ink tracking-tight">Autonomous</a>
  <!-- Nav links -->
  <a href="#" class="px-3.5 py-2 text-[13px] font-medium text-prose hover:text-ink hover:bg-black/[0.04] rounded-full transition-all duration-200">Work</a>
  <!-- CTA -->
  <a href="#" class="bg-ink text-white px-5 py-2.5 rounded-full text-[13px] font-medium hover:bg-midnight-light transition-all duration-200 shadow-sm">Get Started</a>
</nav>
```

---

## Buttons

```html
<!-- Primary CTA -->
<a href="#" class="bg-vermillion text-white rounded-full px-8 py-4 text-base font-medium hover:bg-vermillion-light hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300">
  Let's Talk
</a>

<!-- Secondary / ghost -->
<a href="#" class="border border-ink/10 text-ink rounded-full px-6 py-3 text-sm font-medium hover:bg-ink/5 transition-all">
  See Pricing →
</a>

<!-- Text link with arrow -->
<a href="#" class="text-vermillion font-medium group">
  Read more <span class="inline-block transition-transform group-hover:translate-x-1">→</span>
</a>
```

---

## Cards

```html
<!-- Standard card on parchment bg -->
<div class="bg-white rounded-2xl p-6 shadow-[0_2px_16px_rgba(0,0,0,0.06)]">
  ...
</div>

<!-- Feature card with icon -->
<div class="flex gap-4">
  <div class="w-10 h-10 rounded-xl bg-vermillion/10 flex items-center justify-center flex-shrink-0">
    <!-- icon SVG, text-vermillion -->
  </div>
  <div>
    <h4 class="font-medium text-ink">Card Title</h4>
    <p class="text-sm text-prose mt-1">Description text.</p>
  </div>
</div>
```

Icon background colors by accent:
- Vermillion feature: `bg-vermillion/10` + `text-vermillion`
- Indigo feature: `bg-indigo/10` + `text-indigo`
- Ocean feature: `bg-ocean/10` + `text-ocean`
- Gold feature: `bg-gold/20` + `text-gold`
- Sage feature: `bg-sage/10` + `text-sage`

---

## Status Badges (for audit reports)

```html
<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-sage/15 text-green-800 border border-sage/30">✓ Pass</span>
<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-gold/15 text-amber-800 border border-gold/30">⚠ Warning</span>
<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-vermillion/10 text-red-800 border border-vermillion/25">✗ Fail</span>
<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-ocean/10 text-sky-800 border border-ocean/20">? Unknown</span>
```

---

## Score Circles (SVG — for audit scorecards)

```html
<!-- Radius 28, circumference 175.9 -->
<!-- stroke-dashoffset = (1 - score/100) × 175.9 -->
<!-- Color: sage (#7CA982) for ≥70, gold (#D4A853) for 50–69, vermillion (#E8513D) for <50 -->
<svg width="64" height="64" viewBox="0 0 64 64">
  <circle cx="32" cy="32" r="28" fill="none" stroke="#EDE5D3" stroke-width="7"/>
  <circle cx="32" cy="32" r="28" fill="none" stroke="#7CA982" stroke-width="7"
    stroke-linecap="round" stroke-dasharray="175.9"
    stroke-dashoffset="52.8"
    transform="rotate(-90 32 32)"/>
  <text x="32" y="37" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="13" font-weight="700" fill="#1A1A2E">70</text>
</svg>
```

---

## Animations

```css
/* Scroll reveal */
.reveal { opacity: 0; transform: translateY(40px); transition: opacity 0.9s cubic-bezier(0.16, 1, 0.3, 1), transform 0.9s cubic-bezier(0.16, 1, 0.3, 1); }
.reveal.visible { opacity: 1; transform: translateY(0); }
.reveal-left { opacity: 0; transform: translateX(-40px); transition: opacity 0.9s cubic-bezier(0.16, 1, 0.3, 1), transform 0.9s cubic-bezier(0.16, 1, 0.3, 1); }
.reveal-left.visible { opacity: 1; transform: translateX(0); }

/* Hero stagger */
.hero-stagger > *:nth-child(1) { animation: fadeUp 0.7s cubic-bezier(0.16,1,0.3,1) 0.1s both; }
.hero-stagger > *:nth-child(2) { animation: fadeUp 0.7s cubic-bezier(0.16,1,0.3,1) 0.25s both; }
.hero-stagger > *:nth-child(3) { animation: fadeUp 0.7s cubic-bezier(0.16,1,0.3,1) 0.4s both; }
.hero-stagger > *:nth-child(4) { animation: fadeUp 0.7s cubic-bezier(0.16,1,0.3,1) 0.55s both; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }

/* Marquee (logo strip) */
@keyframes marquee { from { transform: translateX(0); } to { transform: translateX(-50%); } }
.marquee-track { animation: marquee 35s linear infinite; }
.marquee-track:hover { animation-play-state: paused; }

/* Float (decorative elements) */
@keyframes float { 0%, 100% { transform: translateY(0px) rotate(0deg); } 50% { transform: translateY(-20px) rotate(2deg); } }
.float-slow { animation: float 8s ease-in-out infinite; }

/* Tab reveal */
@keyframes tabReveal { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .reveal, .reveal-left { opacity: 1; transform: none; transition: none; }
  .hero-stagger > * { animation: none !important; opacity: 1; }
  .marquee-track, .float-slow { animation: none; }
}
```

---

## CTA Section (dark)

```html
<section class="bg-midnight py-20 px-8 rounded-3xl mx-4 md:mx-8 my-16 text-center">
  <span class="text-sm font-semibold uppercase tracking-wider text-vermillion font-mono">Ready?</span>
  <h2 class="font-display text-[clamp(2rem,4vw,3.5rem)] font-medium tracking-tight text-parchment-light mt-4">
    Let's build something <span class="squiggle">together</span>
  </h2>
  <p class="text-prose max-w-xl mx-auto mt-4 mb-8">Description text here.</p>
  <a href="#" class="bg-vermillion text-white rounded-full px-8 py-4 text-base font-medium hover:bg-vermillion-light transition-all">
    Get Started
  </a>
</section>
```

---

## Organic Background SVG (decorative blobs)

```html
<!-- Place in section with position: relative, overflow: hidden -->
<svg class="absolute top-10 right-0 w-[600px] h-[600px] opacity-[0.06] pointer-events-none" viewBox="0 0 600 600">
  <circle cx="400" cy="200" r="250" fill="#E8513D"/>
  <circle cx="250" cy="350" r="200" fill="#1E3A8A"/>
</svg>
```

---

## Stats / Metrics Pattern

```html
<div class="flex flex-col sm:flex-row gap-8 sm:gap-12 mt-14 pt-10 border-t border-ink/10">
  <div>
    <div class="text-3xl md:text-4xl font-medium text-ink tracking-tight">15+</div>
    <div class="text-sm text-caption mt-1">Years Experience</div>
  </div>
  <div>
    <div class="text-3xl md:text-4xl font-medium text-ink tracking-tight">$10M+</div>
    <div class="text-sm text-caption mt-1">Revenue Powered</div>
  </div>
</div>
```

---

## Logo

```
Autonomous (wordmark only)
Font: Fraunces, font-semibold, tracking-tight
Color: text-ink (light bg) / text-parchment-light (dark bg)
```

Logo files: `/home/rizki/autonomous-proposals/logo-01.jpg` (standard)
Path from subfolder: `../logo-01.jpg`
Path from sub-subfolder: `../../logo-01.jpg`

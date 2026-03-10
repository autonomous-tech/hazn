# Brand Guide — Autonomous Tech
## "Editorial Warmth" v2

This is the active brand guide for all Hazn-generated reports, audits, proposals, and HTML deliverables.
Matches the Autonomous Tech website redesign wireframes (v2).

---

## Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| Parchment | `#F5EFE0` | Primary page background |
| Parchment Light | `#FAF7F0` | Alternate light sections, cards |
| Parchment Dark | `#EDE5D3` | Borders, dividers, subtle fills |
| Midnight | `#0D0D1F` | Dark sections (hero, CTA, footer) |
| Midnight Light | `#1A1A35` | Dark card backgrounds |
| Ink | `#1A1A2E` | Primary headings and display text |
| Prose | `#4A4A60` | Body text |
| Caption | `#7A7A90` | Muted text, labels, metadata |
| Vermillion | `#E8513D` | Primary accent — CTAs, highlights, active states |
| Vermillion Light | `#F06B59` | Hover states on vermillion |
| Vermillion Dark | `#C43E2C` | Pressed/active states |
| Indigo | `#1E3A8A` | Secondary accent — trust, technical, data |
| Sage | `#7CA982` | Positive, pass, success states |
| Gold | `#D4A853` | Warning, attention, premium highlight |
| Ocean | `#0EA5E9` | Info, links, interactive elements |

### Status Colors (for audit badges, findings)
| State | Hex | Usage |
|-------|-----|-------|
| Pass / Good | `#7CA982` (Sage) | Confirmed, passing checks |
| Warning | `#D4A853` (Gold) | Medium severity, needs attention |
| Fail / Critical | `#E8513D` (Vermillion) | Missing, critical, broken |
| Info / Unknown | `#0EA5E9` (Ocean) | Unverified, informational |

---

## CSS Variables

```css
:root {
  /* Backgrounds */
  --parchment: #F5EFE0;
  --parchment-light: #FAF7F0;
  --parchment-dark: #EDE5D3;
  --midnight: #0D0D1F;
  --midnight-light: #1A1A35;

  /* Text */
  --ink: #1A1A2E;
  --prose: #4A4A60;
  --caption: #7A7A90;

  /* Brand Accents */
  --vermillion: #E8513D;
  --vermillion-light: #F06B59;
  --vermillion-dark: #C43E2C;
  --indigo: #1E3A8A;
  --sage: #7CA982;
  --gold: #D4A853;
  --ocean: #0EA5E9;

  /* Status */
  --pass: #7CA982;
  --warn: #D4A853;
  --fail: #E8513D;
  --info: #0EA5E9;
}
```

---

## Typography

```html
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,400;1,9..144,500&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
```

| Element | Font | Weight | Notes |
|---------|------|--------|-------|
| Display / H1 | Fraunces | 300–500 | Variable optical size (`opsz`). Large, editorial. Use `font-variation-settings: 'opsz' 144` for hero. |
| H2–H3 | Fraunces | 400–600 | `opsz` 72 for section titles |
| H4–H5 | DM Sans | 600–700 | Subheadings, card titles |
| Body | DM Sans | 400 | 16–17px, line-height 1.7 |
| Labels / Eyebrows | JetBrains Mono | 400 | 11–12px, uppercase, letter-spacing 0.12em |
| Caption / Meta | DM Sans | 400–500 | 12–13px, --caption color |

```css
body { font-family: 'DM Sans', system-ui, sans-serif; background: var(--parchment); color: var(--prose); line-height: 1.7; }
h1, h2, h3, h4, h5, h6 { font-family: 'Fraunces', Georgia, serif; color: var(--ink); }
.label, .eyebrow { font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.12em; color: var(--caption); }
```

---

## Core Components

### Page Layout
```css
.container { max-width: 1080px; margin: 0 auto; padding: 0 28px; }
.section { padding: 72px 0; }
.section--dark { background: var(--midnight); color: var(--parchment-light); }
.section--mid { background: var(--parchment-dark); }
```

### Cards
```css
.card {
  background: var(--parchment-light);
  border: 1px solid var(--parchment-dark);
  border-radius: 14px;
  padding: 24px 28px;
  box-shadow: 0 1px 3px rgba(26,26,46,0.06), 0 4px 16px rgba(26,26,46,0.04);
}
/* Dark variant (inside dark sections) */
.card--dark {
  background: var(--midnight-light);
  border-color: rgba(245,239,224,0.08);
}
```

### Section Labels / Eyebrows
```css
.section-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--vermillion);
  margin-bottom: 8px;
}
```

### Buttons / CTAs
```css
/* Primary */
.btn-primary {
  background: var(--vermillion);
  color: white;
  padding: 13px 28px;
  border-radius: 100px;
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-primary:hover { background: var(--vermillion-dark); }

/* Secondary / Outline */
.btn-secondary {
  background: transparent;
  color: var(--ink);
  border: 1.5px solid var(--parchment-dark);
  padding: 13px 28px;
  border-radius: 100px;
  font-size: 14px;
  font-weight: 600;
  transition: border-color 0.2s, background 0.2s;
}
.btn-secondary:hover { border-color: var(--ink); background: rgba(26,26,46,0.04); }
```

### Status Badges (for audit reports)
```css
.badge { display: inline-flex; align-items: center; gap: 5px; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; font-family: 'DM Sans', sans-serif; }
.badge-pass  { background: rgba(124,169,130,0.15); color: #2E7D32; border: 1px solid rgba(124,169,130,0.3); }
.badge-warn  { background: rgba(212,168,83,0.15);  color: #92620A; border: 1px solid rgba(212,168,83,0.3); }
.badge-fail  { background: rgba(232,81,61,0.12);   color: #B83225; border: 1px solid rgba(232,81,61,0.25); }
.badge-info  { background: rgba(14,165,233,0.1);   color: #0369A1; border: 1px solid rgba(14,165,233,0.2); }
```

### Score Circles (SVG)
```html
<!-- Radius 28, circumference 175.9. stroke-dashoffset = (1 - score/100) × 175.9 -->
<!-- Color by score: ≥70 sage (#7CA982), 50–69 gold (#D4A853), <50 vermillion (#E8513D) -->
<svg width="64" height="64" viewBox="0 0 64 64">
  <circle cx="32" cy="32" r="28" fill="none" stroke="#EDE5D3" stroke-width="7"/>
  <circle cx="32" cy="32" r="28" fill="none" stroke="#7CA982" stroke-width="7"
    stroke-linecap="round" stroke-dasharray="175.9"
    stroke-dashoffset="52.8"<!-- example: 70/100 -->
    transform="rotate(-90 32 32)"/>
  <text x="32" y="37" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="13" font-weight="700" fill="#1A1A2E">70</text>
</svg>
```

### Callout / Alert Boxes
```css
/* Informational */
.callout { background: rgba(14,165,233,0.07); border: 1px solid rgba(14,165,233,0.2); border-radius: 12px; padding: 18px 22px; }
/* Warning */
.callout-warn { background: rgba(212,168,83,0.1); border: 1px solid rgba(212,168,83,0.3); border-radius: 12px; padding: 18px 22px; }
/* Critical */
.callout-critical { background: rgba(232,81,61,0.08); border: 1px solid rgba(232,81,61,0.25); border-radius: 12px; padding: 18px 22px; }
/* Success */
.callout-success { background: rgba(124,169,130,0.1); border: 1px solid rgba(124,169,130,0.3); border-radius: 12px; padding: 18px 22px; }
```

### Tables
```css
.table-wrap { background: var(--parchment-light); border: 1px solid var(--parchment-dark); border-radius: 12px; overflow: hidden; }
.audit-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.audit-table th { background: var(--parchment-dark); color: var(--caption); font-family: 'JetBrains Mono', monospace; font-size: 10px; text-transform: uppercase; letter-spacing: 0.1em; padding: 10px 16px; text-align: left; }
.audit-table td { padding: 11px 16px; border-bottom: 1px solid var(--parchment-dark); color: var(--prose); vertical-align: top; }
.audit-table tr:last-child td { border-bottom: none; }
.audit-table tr:hover td { background: rgba(26,26,46,0.02); }
```

### Wavy Underline Accent (brand detail)
```css
/* Vermillion wavy underline for highlighted words */
.accent-underline {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='10' viewBox='0 0 80 10'%3E%3Cpath d='M0 5 Q20 0 40 5 Q60 10 80 5' fill='none' stroke='%23E8513D' stroke-width='2.5' opacity='0.6'/%3E%3C/svg%3E");
  background-repeat: repeat-x;
  background-position: bottom;
  padding-bottom: 8px;
  background-size: 40px 7px;
}
/* Gold variant */
.accent-underline-gold {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='10' viewBox='0 0 80 10'%3E%3Cpath d='M0 5 Q20 0 40 5 Q60 10 80 5' fill='none' stroke='%23D4A853' stroke-width='2.5' opacity='0.6'/%3E%3C/svg%3E");
  background-repeat: repeat-x;
  background-position: bottom;
  padding-bottom: 8px;
  background-size: 40px 7px;
}
```

### Hero Section (dark)
```css
.hero {
  background: var(--midnight);
  color: var(--parchment-light);
  padding: 72px 0 0;
}
/* Hero display headline — use Fraunces with large opsz */
.hero-title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: clamp(2.8rem, 7vw, 6rem);
  font-weight: 400;
  font-variation-settings: 'opsz' 144;
  color: var(--parchment-light);
  line-height: 1.05;
}
```

### CTA Section
```css
.cta-section {
  background: var(--midnight);
  padding: 72px 40px;
  border-radius: 24px;
  text-align: center;
  margin: 64px 0;
}
.cta-section h2 { font-family: 'Fraunces', serif; color: var(--parchment-light); }
.cta-section p { color: var(--caption); max-width: 520px; margin: 0 auto 28px; }
```

### TOC Sidebar (for multi-section reports)
```css
.toc { position: fixed; left: 1.5rem; top: 50%; transform: translateY(-50%); display: flex; flex-direction: column; gap: 0.5rem; z-index: 100; }
.toc-dot { display: flex; align-items: center; gap: 0.5rem; font-size: 0.75rem; font-weight: 500; color: var(--caption); text-decoration: none; white-space: nowrap; transition: color 0.2s; }
.toc-dot .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--parchment-dark); flex-shrink: 0; transition: background 0.2s, transform 0.2s; }
.toc-dot.active { color: var(--vermillion); }
.toc-dot.active .dot { background: var(--vermillion); transform: scale(1.5); }
.toc-label { opacity: 0; transition: opacity 0.2s; }
.toc:hover .toc-label { opacity: 1; }
@media (max-width: 1100px) { .toc { display: none; } }
```

---

## Noise Texture (subtle background depth)
```css
body::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.025'/%3E%3C/svg%3E");
}
```

---

## Responsive Breakpoints
```css
@media (max-width: 768px) {
  .section { padding: 48px 0; }
  .hero-title { font-size: clamp(2rem, 9vw, 3.5rem); }
  .cta-section { padding: 48px 24px; border-radius: 16px; }
  .toc { display: none; }
}
```

---

## What Changed from v1 (dark theme)

| v1 (deprecated) | v2 (current) |
|---|---|
| Dark bg `#0a0a12` | Parchment `#F5EFE0` |
| Outfit font | Fraunces (display) + DM Sans (body) |
| Cyan `#00d5ff` accent | Vermillion `#E8513D` accent |
| Bright Purple `#b42aff` | Indigo `#1E3A8A` secondary |
| Glassmorphism cards | Clean parchment cards with shadow |
| Gradient text (cyan→purple) | Wavy underline accent |
| Dark hero gradient | Midnight `#0D0D1F` solid sections |

> **All new reports, audits, proposals, and wireframes use v2. Do not use v1 colors or fonts.**

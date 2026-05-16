# Brand Guide — Stone/Amber Design System
## Canonical source: `~/hazn/skills/seo-audit/SKILL.md` Step 9

All Hazn-generated audit reports use the Stone/Amber design system. This file mirrors the tokens defined in the SEO audit skill — keep them in sync.

---

## Color Palette — CSS Variables

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

---

## Typography

```css
/* Google Fonts — REQUIRED */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap');

/* Headings: 'Source Serif 4', Georgia, serif */
/* Body:     'Inter', system-ui, -apple-system, sans-serif */
```

| Role | Font | Notes |
|------|------|-------|
| Display / Headings | **Source Serif 4** | Variable optical size. Use for all H1–H6. |
| Body | **Inter** | All body copy, UI labels, cards. |

---

## Section Padding

- Regular sections: `padding: 6rem 0`
- Final CTA section: `padding: 8rem 0`

---

## CTA Button (MANDATORY)

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

All CTAs link to: **`https://calendly.com/rizwan-20/30min`** — no exceptions.

> CTA copy examples:
> - "Book a 20-min call — we'll walk through your findings live →"
> - "Your CRO roadmap starts with a 20-min call →"
> - "Let's turn these findings into fixes — book a 20-min call →"

---

## Final CTA Section Template

```html
<section style="padding: 8rem 0; background: var(--stone-900); text-align: center;">
  <p style="color: var(--amber-400); font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;">
    Ready to Fix This?
  </p>
  <h2 style="color: #fff; font-family: 'Source Serif 4', Georgia, serif; font-size: 2rem; margin: 0.75rem 0 1rem;">
    Let's turn these findings into fixes
  </h2>
  <p style="color: var(--stone-300); max-width: 560px; margin: 0 auto 2.5rem; line-height: 1.6;">
    Book a 20-min call and we'll walk through your audit findings live — and map out exactly what to tackle first.
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

---

## Sticky Sidebar TOC

- Desktop (≥1024px): left sidebar, `240px` wide, `position: sticky; top: 2rem`
- Mobile: hidden off-canvas, toggled by hamburger button
- Frosted glass: `background: rgba(255,255,255,0.75); backdrop-filter: blur(8px)`
- Active link: amber highlight (`background: var(--amber-500); color: var(--stone-900)`)
- Intersection Observer tracks current section

---

## Micro-Upsell Callout Pattern

```html
<div class="callout callout--info" style="color: var(--stone-800);">
  🔍 <strong>Want the full picture?</strong> With analytics access, we'd show you
  [specific deeper insight]. Part of the <strong>ConversionIQ</strong> engagement.
  <a href="https://calendly.com/rizwan-20/30min" style="color: var(--amber-600); font-weight: 600;">
    Book a 20-min call →
  </a>
</div>
```

---

## Brand Config

For white-label or partner reports, load brand config from `~/hazn/brands/{slug}.json`. Default: `~/hazn/brands/autonomous.json`. See `~/hazn/brands/README.md` for schema details.

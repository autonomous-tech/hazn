# Editorial Warmth v2 — Design System Rules

> Quick reference for auditing components against the design system.
> Source of truth: `references/docs/editorial-warmth-v2.html` and `frontend/src/app/globals.css`
> Role-specific audit rules: `element-roles.md`

---

## Fonts

| Role | Font Family | Token / Class |
|------|------------|---------------|
| Display / Headings | Fraunces | `--font-display` / `font-display` |
| Body / UI | DM Sans | `--font-body` / `font-body` |
| Mono / Labels | JetBrains Mono | `--font-mono` / `font-mono` |

## Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `parchment` | `#F5EFE0` | Page background |
| `parchment-light` | `#FAF7F0` | Cards, elevated surfaces |
| `parchment-dark` | `#EDE5D3` | Borders, progress tracks |
| `midnight` | `#0D0D1F` | Dark sections |
| `midnight-light` | `#1A1A35` | Dark hover states |
| `vermillion` | `#E8513D` | Primary accent / CTA |
| `vermillion-light` | `#F06B59` | Hover state |
| `vermillion-dark` | `#C43E2C` | Pressed state |
| `indigo` | `#1E3A8A` | Secondary accent |
| `indigo-light` | `#2D4EA3` | Secondary hover |
| `sage` | `#7CA982` | Positive / pass |
| `gold` | `#D4A853` | Warning / highlight |
| `ocean` | `#0EA5E9` | Info / links |
| `ink` | `#1A1A2E` | Headings, primary text |
| `prose` | `#4A4A60` | Body text |
| `caption` | `#7A7A90` | Muted text, labels |

## Typography Scale (CSS Classes)

| Class | Font | Size | Weight | Line-height | Used On |
|-------|------|------|--------|-------------|---------|
| `hero-headline` | Fraunces | clamp(3.2rem, 9vw, 8.5rem) | 400 | 1.15 mobile / 0.95 lg | Homepage hero only |
| `hero-headline-compact` | Fraunces | clamp(2.8rem, 7vw, 6rem) | 400 | 0.95 | Contact, pricing, work, ecom-ops |
| `hero-headline-case` | Fraunces | clamp(2.8rem, 7vw, 5.5rem) | 400 | 0.95 | Case study pages |
| `hero-headline-flex` | Fraunces | clamp(2.2rem, 9vw, 8.5rem) | 400 | 0.92 | Marketing, ecommerce |
| `hero-headline-md` | Fraunces | clamp(2.4rem, 5.5vw, 5.2rem) | 500 | 0.95 | Intelligence product pages |
| `hero-headline-lg` | Fraunces | clamp(2.4rem, 6vw, 6rem) | 500 | 0.95 | Intelligence suite hub |
| `section-headline` | Fraunces | clamp(2rem, 4.5vw, 3.8rem) | 400 | 1.05 | All section h2s |
| `eyebrow` | JetBrains Mono | 14px | 600 | — | All eyebrow labels |

## Shared UI Components

### EyebrowLabel (`@/components/ui/EyebrowLabel`)
- Uses `.eyebrow` CSS class (JetBrains Mono, 14px, 600, uppercase, tracking 0.1em)
- Color variants: `vermillion` (default), `caption`, `white`, `gold`, `ocean`
- **Rule:** All eyebrow text MUST use this component, not manual styling

### Button (`@/components/ui/Button`)
- Variants: `primary` (vermillion), `primary-indigo`, `secondary` (border), `text` (vermillion + arrow), `dark` (ink)
- Sizes: `sm` (px-4 py-2), `md` (px-6 py-3), `lg` (px-8 py-4)
- `text` variant auto-appends `→` with hover animation — don't duplicate
- Renders as `<Link>` when `href` provided, `<button>` otherwise
- **Rule:** Any element styled as a button (bg-vermillion, rounded-full, px-8 py-4) MUST use `<Button>`, never a raw `<Link>` or `<a>` with manual button classes

### getBgClasses (`@/lib/bg-styles`)
- Maps Wagtail `bg_style` values to Tailwind: `dark` → ink, `parchment` → parchment, etc.
- Returns `{ bg, text, prose }` — use all three for consistent text colors
- **Rule:** Never hardcode bg + text color combos when `bg_style` is available from CMS

## Standard SVG Arrow

The project-wide arrow icon for CTAs (NOT text `→`):

```tsx
<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
</svg>
```

**Only exception:** `Button` component's `text` variant uses `→` with hover translate animation.

## Nav Breakpoint

- Desktop nav: `min-[930px]` (NOT `md` / 768px)
- Mobile hamburger: below 930px

## Animation Classes

| Class | Effect |
|-------|--------|
| `hero-stagger` | Staggered fadeUp on direct children |
| `reveal` | Fade + translateY(40px), toggled by `.visible` |
| `reveal-left` / `reveal-right` | Horizontal reveal variants |
| `stagger` | Staggered transition-delay on children |

## Squiggle Underlines

- Class: `squiggle-vermillion` or `squiggle-gold`
- `padding-bottom: 0.08em` (not px)
- `white-space: nowrap`

## Footer Rules

- Links: `text-white/40 hover:text-white` (NOT `text-parchment-dark`)
- Headers: `text-white`
- CTA button: responsive sizing with `whitespace-nowrap`

---

## Common Mistakes (from manual fixes)

These patterns were manually found and fixed in commits 3072d2b through 9122e5e. The audit workflow should catch all of them:

1. **h1 using inline styles** instead of `hero-headline` CSS class — wrong font size, line-height, letter-spacing
2. **Eyebrows using manual `<span>`** instead of `<EyebrowLabel>` component
3. **Hero images showing on mobile** — needed `hidden lg:block` wrapper
4. **Hero section `pt-32`** instead of `pt-36` — not enough nav clearance
5. **CTA groups left-aligned on mobile** — needed `justify-center lg:justify-start`
6. **Text `→` arrows** instead of SVG arrows in CTAs
7. **`rounded-3xl`** on cards instead of `rounded-2xl`
8. **`inline-block`** on buttons instead of `inline-flex items-center justify-center`
9. **Missing `text-center lg:text-left`** on hero content in asymmetric layouts
10. **Missing `mx-auto lg:mx-0`** on hero stagger containers
11. **Squiggle padding `8px`** instead of `0.08em`
12. **Section headings using raw `text-3xl md:text-5xl font-bold`** instead of `section-headline` class
13. **DarkHero content not centered on mobile** — needed responsive alignment trio
14. **Card badges overlapping content** on small screens (absolute positioning collision)
15. **Nav using `md:` breakpoint** instead of `min-[930px]`

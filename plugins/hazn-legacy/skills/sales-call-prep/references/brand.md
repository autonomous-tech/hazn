# Brand Guide

## Colors

| Name | Hex | Usage |
|------|-----|-------|
| Deep Blue | `#151795` | Primary backgrounds, gradients |
| Blue | `#006aff` | Accents, highlights, links |
| Cyan | `#00d5ff` | Primary highlight, emphasis |
| Purple | `#8c18c5` | Secondary accent |
| Bright Purple | `#b42aff` | Calls to action, energy |
| Dark | `#0a0a12` | Base background |
| White | `#ffffff` | Primary text |
| Gray | `#a0a0b0` | Secondary text, labels |
| Light Gray | `#d0d0dd` | Body text |
| Green | `#66bb6a` | Success, positive |
| Amber | `#ffb74d` | Warning, caution |
| Red | `#ef5350` | Urgent, high priority |

## CSS Variables

```css
:root {
    --deep-blue: #151795;
    --blue: #006aff;
    --cyan: #00d5ff;
    --purple: #8c18c5;
    --bright-purple: #b42aff;
    --dark: #0a0a12;
    --white: #ffffff;
    --gray: #a0a0b0;
    --light-gray: #d0d0dd;
    --green: #66bb6a;
    --amber: #ffb74d;
    --red: #ef5350;
}
```

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Pathway+Extreme:wght@400;500&display=swap');
```

| Element | Font | Weight | Size |
|---------|------|--------|------|
| H1 | Outfit | 700 | 40-52px |
| H2 | Outfit | 600 | 28-32px |
| H3 | Outfit | 600 | 20-22px |
| Labels | Outfit | 500 | 11-13px, uppercase, letter-spacing: 2-3px |
| Body | Pathway Extreme | 400 | 17px |
| Cards | Pathway Extreme | 400 | 15-16px |

## Core Components

### Cards
```css
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14-16px;
    padding: 24-28px;
    backdrop-filter: blur(10px);
}
/* Border colors: card-cyan, card-purple, card-blue, card-green, card-amber, card-red */
```

### Hero Section
```css
.hero {
    background: linear-gradient(135deg, var(--deep-blue) 0%, var(--purple) 100%);
    padding: 48-80px;
    border-radius: 20-24px;
}
```

### Gradient Text
```css
.highlight {
    background: linear-gradient(90deg, var(--cyan), var(--bright-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
```

### Quote Blocks
```css
.quote {
    border-left: 3px solid var(--cyan);
    padding: 14-16px 20-24px;
    background: rgba(0,213,255,0.05);
    border-radius: 0 10-12px 10-12px 0;
    font-style: italic;
    color: var(--white);
}
```

### Status Pills
```css
.status { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.status-high { background: rgba(239,83,80,0.2); color: var(--red); }
.status-medium { background: rgba(255,183,77,0.2); color: var(--amber); }
.status-low { background: rgba(102,187,106,0.2); color: var(--green); }
```

### Callout Boxes
```css
.callout {
    background: linear-gradient(135deg, rgba(0,106,255,0.08), rgba(180,42,255,0.08));
    border: 1px solid rgba(0,213,255,0.2);
    border-radius: 14-16px;
    padding: 24-28px;
}
```

### Tables
Dark themed, 1px borders rgba(255,255,255,0.06-0.08), cyan headers with uppercase letter-spacing.

### Lists
Arrow style: `→` prefix in cyan, no bullet points.

### Page Layout
Max-width: 900-1100px centered. Dark body background. 40-60px page padding.

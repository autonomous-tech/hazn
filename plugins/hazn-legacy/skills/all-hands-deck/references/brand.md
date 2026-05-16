# FAST Brand Guide

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
}
```

## Typography

| Element | Font | Weight | Size |
|---------|------|--------|------|
| H1 | Outfit | 700 (Bold) | 64px |
| H2 | Outfit | 600 (SemiBold) | 42px |
| H3/Labels | Outfit | 500 (Medium) | 15px, uppercase, letter-spacing: 3px |
| Body | Pathway Extreme | 400 (Regular) | 22px |
| Cards | Pathway Extreme | 400 | 16px |

## Google Fonts Import

```css
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Pathway+Extreme:wght@400;500&display=swap');
```

## Gradients

```css
/* Primary gradient backgrounds */
.bg-gradient { background: linear-gradient(135deg, var(--deep-blue) 0%, var(--purple) 100%); }
.bg-blue { background: linear-gradient(135deg, var(--deep-blue) 0%, #0a0a20 100%); }
.bg-dark { background: linear-gradient(135deg, #0a0a12 0%, #12122a 100%); }

/* Text gradient */
.highlight-gradient {
    background: linear-gradient(90deg, var(--cyan), var(--bright-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Divider */
.divider { 
    width: 60px; 
    height: 4px; 
    background: linear-gradient(90deg, var(--blue), var(--cyan)); 
    border-radius: 2px;
}
```

## Card Styling

```css
.card { 
    background: rgba(255,255,255,0.05); 
    border: 1px solid rgba(255,255,255,0.1); 
    border-radius: 16px; 
    padding: 28px; 
    backdrop-filter: blur(10px); 
}

/* Accent borders by color */
.card-cyan { border-color: rgba(0,213,255,0.3); }
.card-purple { border-color: rgba(180,42,255,0.3); }
.card-blue { border-color: rgba(0,106,255,0.3); }
.card-green { border-color: rgba(102,187,106,0.3); }
```

## Status Pills

```css
.status { 
    display: inline-block; 
    padding: 4px 12px; 
    border-radius: 20px; 
    font-size: 12px; 
    font-weight: 600; 
}
.status-live { background: rgba(102,187,106,0.2); color: #66bb6a; }
.status-building { background: rgba(0,213,255,0.2); color: var(--cyan); }
.status-active { background: rgba(0,106,255,0.2); color: var(--blue); }
```

## Logo Usage

- Use transparent PNG logos (`logo-transparent.png`)
- Position: top-left, 40px height
- Class: `.logo { position: absolute; top: 30px; left: 50px; height: 40px; opacity: 0.9; }`

## Slide Dimensions

- Width: 1280px
- Height: 720px
- Padding: 50px 70px
- Widescreen 16:9 aspect ratio

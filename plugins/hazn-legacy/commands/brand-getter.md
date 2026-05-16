---
description: Extract brand identity from a website URL for white-labeling audit reports
argument-hint: <url>
---

Extract brand identity (colors, fonts, logo, key design elements) from a website using Firecrawl. If no URL argument is provided, ask the user for the target website URL.

## Steps

1. **Fetch Website Content**
   - Use Firecrawl to scrape the provided URL
   - Extract full HTML/CSS for design analysis

2. **Extract Brand Elements**
   - Identify primary and accent colors from CSS/inline styles
   - Extract font families used (headings, body, monospace)
   - Locate and document logo usage
   - Capture button styles and component design
   - Note spacing/padding patterns
   - Document any brand asset URLs (logo, icons, images)

3. **Generate Brand Profile**
   - Create `brand-profile.md` in the current working directory
   - Format: Markdown with color palettes (hex/RGB), typography details, component styles
   - Include screenshots or asset descriptions where relevant
   - Provide CSS variable recommendations based on extracted colors

## Output Format

```markdown
# Brand Profile: [Company/Domain]

## Colors
### Primary Colors
| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| ... | ... | ... | ... |

## Typography
| Type | Font | Weights | Usage |
|------|------|---------|-------|
| ... | ... | ... | ... |

## Assets
- Logo: [URL or description]
- Primary CTA Color: #XXXXXX
- Secondary Colors: [list]

## Component Styles
- Button styles
- Border radius
- Spacing patterns
- Shadow/depth treatment
```

## Notes
- Firecrawl extracts both rendered and source-level design information
- Prioritize colors and fonts from CSS over computed styles when available
- Document fallback fonts and web font sources (Google Fonts, etc.)

# Audit Scoring Framework

## Copywriting (1-10)

### Scoring Criteria

| Score | Description |
|-------|-------------|
| 9-10 | Clear single value prop, specific proof, strong CTAs, guarantee prominent, optimal length |
| 7-8 | Good fundamentals, minor issues (weak CTA, buried guarantee, slightly long) |
| 5-6 | Multiple value props competing, generic CTAs, social proof present but unoptimized |
| 3-4 | Unclear messaging, no social proof, feature-focused not benefit-focused |
| 1-2 | No clear value prop, no CTAs, wall of text, no proof |

### What to Evaluate

**Headline & Subhead**
- Is there ONE clear message in the first viewport?
- Does it communicate a specific outcome, not just a feature?
- Fear-based vs aspiration-based — appropriate for audience?

**Value Proposition**
- Can a visitor understand what you do + why you're different in 5 seconds?
- Is the unique differentiator (guarantee, method, results) front and center?
- Are competing messages diluting the primary value prop?

**Calls to Action**
- Is the CTA outcome-focused? ("Get Your Free Assessment" > "Book A Consultation")
- Is CTA copy consistent across the page?
- Are CTAs placed at decision points (after proof, after guarantee, after testimonials)?
- Does CTA color contrast with the surrounding design?

**Social Proof**
- Video testimonials > text testimonials > logos
- Do testimonials lead with OUTCOMES, not process?
- Named, specific people with photos > anonymous quotes
- Numbers: "12,000 families" > "thousands of families"

**Guarantee**
- Is there one? (If not, that's a major gap)
- How prominent is it? (Hero = best, buried mid-page = problem)
- Is the language clear and bold? ("100% refund. Period." > "satisfaction guaranteed")

**Copy Length**
- Match length to price point: $50 product = short, $50K service = long but structured
- Can the page be skimmed in 30 seconds? (scannable headers, bold key points)
- Is there scroll fatigue? (3000+ words without clear sections)

---

## SEO (1-10)

### Scoring Criteria

| Score | Description |
|-------|-------------|
| 9-10 | All schema types, optimized meta, clean hierarchy, fast vitals, structured data rich snippets |
| 7-8 | Meta present and optimized, most schema, minor hierarchy issues |
| 5-6 | Meta present but generic, some schema missing, disorganized headings |
| 3-4 | Generic meta, no schema, heading chaos, slow site |
| 1-2 | Missing meta, no schema, no heading structure, critical speed issues |

### Technical Checklist

| Element | Check For |
|---------|-----------|
| Meta Title | Unique, <60 chars, includes primary keyword + differentiator |
| Meta Description | Unique, <155 chars, includes CTA + key benefit |
| H1 Tag | Single H1, matches page intent |
| Heading Hierarchy | H1 → H2 → H3 logical flow, no skipped levels |
| Schema: Organization | Name, logo, social profiles |
| Schema: LocalBusiness | If applicable — address, hours, phone |
| Schema: FAQPage | If FAQ content exists on page |
| Schema: Review/Rating | If testimonials/reviews exist |
| Schema: Service | Service descriptions, price ranges |
| Schema: BreadcrumbList | Navigation path |
| Core Web Vitals | LCP <2.5s, FID <100ms, CLS <0.1 |
| Mobile Optimization | Responsive, touch targets, readable without zoom |
| Internal Linking | Logical site structure, breadcrumbs |
| Page Speed | GTmetrix/Lighthouse score |
| Image Optimization | WebP, lazy loading, proper alt text |
| Canonical URL | Properly set, no duplicates |

---

## Frontend Design (1-10)

### Scoring Criteria

| Score | Description |
|-------|-------------|
| 9-10 | Premium feel matching price point, strong visual hierarchy, memorable brand, fast |
| 7-8 | Professional, good hierarchy, minor contrast/spacing issues |
| 5-6 | Generic/template feel, weak CTA visibility, inconsistent spacing |
| 3-4 | Obviously templated, poor contrast, no visual hierarchy |
| 1-2 | Broken layout, unreadable on mobile, stock everything |

### What to Evaluate

**Visual Hierarchy**
- Can you identify the most important element in each section within 2 seconds?
- Is there a clear reading flow? (Z-pattern for hero, F-pattern for content)
- Are sections visually distinct from each other?

**CTA Visibility**
- Does the primary CTA button have the highest contrast on the page?
- Can you spot the CTA without scrolling? (above the fold)
- Does the button color NOT appear elsewhere on the page? (uniqueness)

**Brand & Differentiation**
- Does the design match the price point? ($50K service should feel premium)
- Is it distinguishable from competitors? (avoid "industry standard" palettes)
- Three directions to recommend: Editorial, Modern Minimalist, Warm/Human

**Typography**
- Readable body text (16px+ for web)
- Clear heading hierarchy with size/weight contrast
- Max 2 font families

**Whitespace & Density**
- Adequate breathing room between sections?
- Content density appropriate for audience?
- Mobile spacing sufficient for thumb taps?

**Load Performance**
- Hero image optimized?
- Fonts loaded efficiently? (font-display: swap)
- No layout shift on load?

---

## Quick Win Identification

A "quick win" must meet ALL criteria:
1. **Implementable in <1 day**
2. **High expected impact** on conversions
3. **Low risk** (won't break existing functionality)
4. **Measurable** (can A/B test the change)

Common quick wins:
- Move guarantee to hero
- Change CTA button color for contrast
- Rewrite headline for specificity
- Add missing schema markup
- Optimize meta title/description
- Lead testimonials with outcomes
- Reduce page length (cut 30-40%)
- Add urgency/scarcity element
- Fix heading hierarchy
- Add structured data for rich snippets

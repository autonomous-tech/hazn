---
name: conversion-audit
description: Run a comprehensive landing page conversion audit covering copywriting, SEO, and frontend design. Use when auditing client websites, preparing for sales calls, or delivering value-add reports. Generates a branded HTML audit report with scores, before/after recommendations, implementation roadmap, and CVR projections. Styled with Autonomous brand guide.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
---

# Conversion Audit

Generate a comprehensive, branded landing page conversion audit covering three pillars: Copywriting, SEO, and Frontend Design.

## Process

### 1. Gather Target Info

Ask the user:
- **URL** to audit
- **Primary conversion goal** (leads, signups, purchases, bookings)
- **Target audience** (who are they selling to?)
- **Price point** (affects design expectations — $50 product vs $50K service)
- **Is this for a client or internal?** (affects tone and framing)

### 2. Research the Page

```bash
# Fetch the page content
web_fetch <url> --extractMode markdown

# Check competitors if relevant
web_search "<industry> landing page best practices"
```

Analyze:
- Full page copy (headline, subhead, body, CTAs, social proof, guarantees)
- Page structure (sections, flow, length)
- SEO elements (meta, headings, schema, technical)
- Design signals (can infer from HTML structure, classes, frameworks)

If user provides screenshots or a separate audit doc, incorporate those findings.

### 3. Score Each Pillar

Score on a 1-10 scale with justification:

| Pillar | What to Evaluate |
|--------|-----------------|
| **Copywriting** | Headline clarity, value prop, CTA strength, social proof, urgency, guarantee placement, copy length, specificity of claims |
| **SEO** | Meta title/desc, heading hierarchy, schema markup, Core Web Vitals, mobile optimization, internal linking, keyword targeting |
| **Frontend Design** | Visual hierarchy, CTA visibility, color contrast, typography, whitespace, mobile responsiveness, load time, brand consistency, premium feel |

### 4. Identify Issues & Recommendations

For each pillar, document:
- **Strengths** (what's working — always lead with positives)
- **Critical Issues** (numbered, with before/after examples)
- **Quick Wins** (can be done this week)
- **Short-term Improvements** (2-4 weeks)
- **Long-term Recommendations** (1-3 months)

### 5. Build Implementation Roadmap

Organize all recommendations into a prioritized table:

| Timeframe | Action | Category | Impact |
|-----------|--------|----------|--------|
| Immediate | ... | Copy/SEO/Design | Very High/High/Medium |

### 6. Project CVR Impact

Estimate conversion rate improvements:
- Current state (based on industry benchmarks)
- After quick wins
- After short-term improvements
- After full redesign

Use industry benchmarks as reference. See `references/benchmarks.md`.

### 7. Generate HTML Report

Load `assets/template-audit.html` as the base template. Follow `references/brand.md` for styling.

Key sections in the HTML:
1. **Hero** — Client name, URL, date, conversion goal
2. **Overall Scores** — 4 score blocks (Copy, SEO, Design, Overall)
3. **CVR Projections** — 3-column: Current → Quick Wins → Full Redesign
4. **Top 5 Quick Wins** — Numbered cards with before/after comparisons
5. **Part 1: Copywriting Audit** — Strengths (green cards) + Issues (red cards with before/after)
6. **Part 2: SEO Audit** — Technical status table + critical issues
7. **Part 3: Frontend Design Audit** — Design direction options + specific issues
8. **Implementation Roadmap** — Prioritized tables by timeframe
9. **Conclusion** — Hero-style closing with single biggest win + risk + CVR potential

### 8. Save & Deliver

Save the audit report to the autonomous-proposals repo:

```bash
# Save report
mkdir -p ~/clawd/autonomous-proposals/audits
# Write to: ~/clawd/autonomous-proposals/audits/{client}-conversion-audit-{date}.html

# Deploy to docs site
cd ~/clawd/autonomous-proposals
git add audits/
git commit -m "Add {client} conversion audit"
git pull --rebase origin main && git push origin main
```

**Report URL:** `https://docs.autonomoustech.ca/audits/{client}-conversion-audit-{date}.html`

**Alternative:** Use `canvas action=present` to display the report inline if immediate preview is needed.

## Key Principles

- **Always lead with strengths.** Clients need to feel validated before hearing criticism.
- **Before/After for everything.** Don't just say "this is bad" — show what "good" looks like.
- **Quantify impact.** Use CVR projections, revenue lift estimates, time-to-implement.
- **Make it actionable.** Every recommendation should be implementable, not theoretical.
- **Design for the price point.** A $50K service needs a premium-feeling audit. A $20 product can be simpler.
- **Print-friendly.** Include A4 print styles with `break-inside: avoid` on cards/tables.

## References

- `references/brand.md` — Colors, fonts, CSS variables, component styles
- `references/audit-framework.md` — Detailed scoring criteria for each pillar
- `references/benchmarks.md` — Industry CVR benchmarks by vertical

## Assets

- `assets/template-audit.html` — Base HTML template (from Zenith audit)

---
name: conversion-audit
description: Run a comprehensive landing page conversion audit covering copywriting, SEO, and frontend design. Use when auditing client websites, preparing for sales calls, or delivering value-add reports. Generates a branded HTML audit report with scores, before/after recommendations, implementation roadmap, CVR projections, and A/B testing opportunities. Styled with Autonomous brand guide.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
---

# Conversion Audit

Generate a comprehensive, branded landing page conversion audit covering three pillars: Copywriting, SEO, and Frontend Design — plus a measurement framework for validating improvements.

## Process

### 1. Gather Target Info

Ask the user:
- **URL** to audit
- **Primary conversion goal** (leads, signups, purchases, bookings)
- **Target audience** (who are they selling to?)
- **Price point** (affects design expectations — $50 product vs $50K B2B service)
- **Current traffic volume** (affects A/B testing feasibility)
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

| Timeframe | Action | Category | Impact | Testable? |
|-----------|--------|----------|--------|-----------|
| Immediate | ... | Copy/SEO/Design | Very High/High/Medium | Yes/No |

---

## A/B Testing Recommendations

For each significant recommendation, evaluate whether it's testable:

### Test Prioritization Matrix

| Recommendation | Hypothesis | Test Type | Traffic Needed | Priority |
|----------------|------------|-----------|----------------|----------|
| New headline | Specificity increases clarity → +15% CTR | A/B | ~3k visitors | High |
| CTA button redesign | Higher contrast → +10% clicks | A/B | ~5k visitors | High |
| Social proof placement | Above fold → +8% trust signals | A/B | ~4k visitors | Medium |

### Hypothesis Framework for Each Test

Structure recommendations as testable hypotheses:

```
Because [observation from audit],
we believe [specific change]
will cause [expected outcome]
for [target audience].
We'll know this is true when [metric] improves by [target %].
```

### B2B Testing Considerations

For B2B clients (lower traffic, higher deal value):
- **Longer test durations** — Account for weekly business cycles
- **Micro-conversions** — Track scroll depth, time on page, PDF downloads
- **Qualitative signals** — Demo request quality, sales feedback
- **Sequential testing** — When traffic is too low for simultaneous tests

### Quick Reference: Sample Sizes

| Baseline CVR | 10% Lift | 20% Lift | 50% Lift |
|--------------|----------|----------|----------|
| 1% | 150k/variant | 39k/variant | 6k/variant |
| 3% | 47k/variant | 12k/variant | 2k/variant |
| 5% | 27k/variant | 7k/variant | 1.2k/variant |
| 10% | 12k/variant | 3k/variant | 550/variant |

**Low-traffic B2B recommendation:** Focus on bolder changes (50%+ lift potential) or use sequential testing.

---

## Measurement Framework

### Tracking Requirements Checklist

Before implementing changes, ensure tracking is in place:

| Event | Required For | Implementation |
|-------|--------------|----------------|
| `page_view` with UTM params | Attribution | GA4 auto / PostHog |
| `cta_clicked` | Button performance | Custom event |
| `form_started` | Funnel analysis | Custom event |
| `form_submitted` | Conversion tracking | Custom event |
| `scroll_depth` | Engagement | GA4 enhanced / Custom |
| `time_on_page` | Content quality | GA4 auto |

### Conversion Funnel Setup

Define the funnel for each conversion goal:

```
Page View → CTA Click → Form Start → Form Submit → Thank You Page
   │           │            │             │              │
  100%        40%          25%           15%            12%
```

Track drop-off at each stage to identify optimization priorities.

### Key Metrics to Monitor

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Primary CVR | X% | +Y% | GA4 Conversion |
| Bounce Rate | X% | -Y% | GA4 |
| Avg. Session Duration | Xs | +Ys | GA4 |
| Scroll Depth (75%+) | X% | +Y% | Custom Event |
| CTA Click Rate | X% | +Y% | Custom Event |

### Reporting Cadence

- **Week 1:** Baseline established, tracking verified
- **Week 2-4:** Quick wins implemented, monitoring
- **Month 2:** Short-term improvements, first A/B test results
- **Month 3:** Full optimization cycle, ROI calculation

---

## Project CVR Impact

Estimate conversion rate improvements:
- Current state (based on industry benchmarks)
- After quick wins (+X%)
- After short-term improvements (+Y%)
- After full optimization with validated tests (+Z%)

Use industry benchmarks as reference. See `references/benchmarks.md`.

### ROI Projection Template

```
Current State:
- Monthly visitors: [X]
- Conversion rate: [Y%]
- Conversions/month: [Z]
- Avg. deal value: [$A]
- Monthly revenue: [$B]

After Optimization:
- Projected CVR: [Y + improvement%]
- Projected conversions: [Z × multiplier]
- Projected revenue lift: [$C]
- Annual impact: [$C × 12]
```

---

## Generate HTML Report

Load `assets/template-audit.html` as the base template. Follow `references/brand.md` for styling.

Key sections in the HTML:
1. **Hero** — Client name, URL, date, conversion goal
2. **Overall Scores** — 4 score blocks (Copy, SEO, Design, Overall)
3. **CVR Projections** — 3-column: Current → Quick Wins → Full Redesign
4. **Top 5 Quick Wins** — Numbered cards with before/after comparisons
5. **Part 1: Copywriting Audit** — Strengths (green cards) + Issues (red cards with before/after)
6. **Part 2: SEO Audit** — Technical status table + critical issues
7. **Part 3: Frontend Design Audit** — Design direction options + specific issues
8. **Part 4: A/B Testing Roadmap** — Prioritized experiments with hypotheses
9. **Part 5: Measurement Framework** — Tracking checklist + funnel visualization
10. **Implementation Roadmap** — Prioritized tables by timeframe
11. **Conclusion** — Hero-style closing with single biggest win + risk + CVR potential

---

## Checkpoints (Human-in-Loop)

**CHECKPOINT 1:** After scoring all three pillars
- Present scores and top 3 issues per pillar
- Ask: "Do these priorities align with your goals? Any areas to emphasize?"

**CHECKPOINT 2:** Before finalizing A/B test recommendations
- Present proposed tests with traffic requirements
- Ask: "Given your traffic volume, which tests are feasible? Want to adjust priorities?"

**CHECKPOINT 3:** Before generating final report
- Present outline and key recommendations
- Ask: "Ready to generate the full HTML report?"

---

## Save & Deliver

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

---

## Key Principles

- **Always lead with strengths.** Clients need to feel validated before hearing criticism.
- **Before/After for everything.** Don't just say "this is bad" — show what "good" looks like.
- **Quantify impact.** Use CVR projections, revenue lift estimates, time-to-implement.
- **Make it actionable.** Every recommendation should be implementable, not theoretical.
- **Make it testable.** Frame recommendations as hypotheses when traffic allows.
- **Design for the price point.** A $50K service needs a premium-feeling audit. A $20 product can be simpler.
- **Print-friendly.** Include A4 print styles with `break-inside: avoid` on cards/tables.

---

## Related Skills

- `ab-test-setup` — For designing and implementing experiments
- `analytics-tracking` — For setting up measurement infrastructure
- `b2b-marketing-ux` — For B2B-specific conversion principles

---

## References

- `references/brand.md` — Colors, fonts, CSS variables, component styles
- `references/audit-framework.md` — Detailed scoring criteria for each pillar
- `references/benchmarks.md` — Industry CVR benchmarks by vertical

## Assets

- `assets/template-audit.html` — Base HTML template (from Zenith audit)

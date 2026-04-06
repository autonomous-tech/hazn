# Comprehensive Site Audit

> Multi-track website audit across conversion, copy, visual/UX, and SEO — scored findings, prioritized by impact, delivered as a branded HTML report.

## When to Use

- Evaluating an existing site before a redesign or replatform decision
- Delivering value to a prospect before they become a client (sales tool)
- Post-launch QC on a site you just built
- Client asks "why aren't we converting?" with no clear hypothesis

**NOT for:**
- Sites under active development with no live URL
- Deep GA4/MarTech attribution analysis → use `/hazn-analytics-audit`
- Single-issue investigations (e.g., just check the meta tags) — run the relevant sub-check directly

## Requirements

- Live website URL
- Primary conversion goal (what counts as a conversion on this site?)
- Scope decision: full audit (all 4 tracks) or specific tracks (conversion, copy, visual, SEO)
- Analytics access (GA4) — optional but improves depth of conversion analysis

## How It Works

### Phase 1 — Scope (~15 minutes)
Confirm URL, select audit tracks, gather analytics access if available, define the primary conversion goal.

### Phase 2 — Analysis (~1–3 hours)
**Agent:** Auditor  
Runs all selected tracks in parallel:

**Conversion/CRO track:** Above-fold clarity (5-second test), CTA visibility/copy, trust signals, form friction, mobile conversion path, page load speed, objection handling.

**Copy track:** Headline clarity and specificity, value proposition strength, benefit vs feature ratio, CTA effectiveness, voice consistency, social proof usage.

**Visual/UX track:** Visual hierarchy, whitespace, typography scale, color contrast, mobile responsiveness, navigation clarity, consistency across pages.

**SEO track:** Meta tags, header structure, Core Web Vitals, mobile-friendliness, structured data, internal linking, content depth.

Each finding scored: ✅ Good | ⚠️ Needs work | ❌ Critical issue

### Phase 3 — Synthesis (~30 minutes)
Aggregate scores, prioritize by Impact × Effort matrix:
- High Impact + Low Effort → Do first
- High Impact + High Effort → Plan for
- Low Impact + Low Effort → Quick wins
- Low Impact + High Effort → Skip

### Phase 4 — Report Generation (~30 minutes)
**Output:** Branded HTML report + summary markdown

## HITL Checkpoints

| Checkpoint | Why it matters / risk of skipping |
|---|---|
| Scope confirmation before analysis | Auditing conversion without knowing the conversion goal produces useless scores. If the goal is demo requests but the auditor evaluates for e-commerce checkout flow, findings are irrelevant. |

## Caveats & Gotchas

- Without GA4 access, conversion findings are visual/heuristic only — no behavioral data to validate claims.
- The auditor uses the browser tool for visual inspection. If the site uses heavy JS rendering that doesn't work without credentials, screenshots will be incomplete.
- Audit scores are heuristic, not statistically validated. Frame scores as directional indicators, not benchmarks.
- Each finding is framed as: what's wrong, why it costs them money, how to fix it. If context is too thin, findings become generic — push for the conversion goal upfront.
- Report is delivered as a single HTML file — can be dropped into `landing-pages` repo for client delivery.

## Outputs

```
.hazn/outputs/
├── audit-report.html      ← branded, shareable client report
└── audit-summary.md       ← markdown quick-reference
```

## Example Trigger

```
/hazn-audit
URL: https://acmeconsulting.com
Tracks: Full (conversion, copy, visual, SEO)
Goal: Inbound demo requests
Analytics: GA4 access available
```

---
name: shopify-revenue-audit
description: Use when auditing a Shopify store for revenue opportunities. Orchestrator that dispatches 4 module skills (AI Discovery 30%, Search & Catalog 20%, Conversion Experience 30%, Technical Foundation 20%) in a 4-wave pipeline. Owns composite scoring 0-100, honest P25-P75 quantification, MANDATORY red-team pass on every projection, Editorial Warmth v2 branded HTML deliverable. Triggers on "audit shopify store", "shopify revenue audit", "deep shopify audit".
---

# Shopify Revenue Audit (orchestrator)

## When to use
- User has a Shopify store URL and wants revenue opportunities surfaced
- Existing client wants an optimization review (partner framing, not sales)
- Phrases: "audit this shopify store", "shopify revenue audit", "deep shopify audit", "AEO/GEO audit for shopify"

This skill is the **orchestrator**. It does not perform any module audit work itself — it dispatches to 4 module skills and owns the wave pipeline, composite score, red-team gating, and deliverable rendering.

## What this skill produces
- 10-section HTML audit report (parchment + vermillion, ~140 KB, single self-contained file)
- 4-module SiteHealth composite score 0-100 (e.g., Sene = 42/100)
- Per-module deep-dive sections with cited evidence (produced by the 4 module skills)
- $-quantified Quick Wins (P25-P75 bands, NOT a single midpoint)
- Roadmap + Recommended Workstreams (partner close, no sales CTA)

## Module dispatch

| # | Module skill | Weight | Trigger |
|---|---|---|---|
| 1 | `module-1-ai-discovery`   | 30% | Wave 2 β lead |
| 2 | `module-2-search-catalog` | 20% | Wave 2 γ lead |
| 3 | `module-3-conversion`     | 30% | Wave 2 δ lead |
| 4 | `module-4-technical`      | 20% | Wave 2 ε lead |

**Wave 2 invokes `module-1-ai-discovery`, `module-2-search-catalog`, `module-3-conversion`, `module-4-technical` skills in parallel.** Each module skill owns its own audit criteria, scoring rubric, evidence requirements, and red-team gates. The orchestrator only collects their scores into the composite and gates progression.

For single-module reruns, the orchestrator dispatches to one module skill via `/shopify-revenue-audit:rerun-module <audit-dir> <N>`.

## The 4-wave pipeline

| Wave | Team | Output |
|---|---|---|
| 1 | α (3 agents): Crawler + Infra Probe + PageSpeed | `crawl/`, `infra-probe.json`, `pagespeed/` |
| 2 | β/γ/δ/ε — invokes the 4 module skills in parallel | `module{1-4}-*.md` + sub-JSON evidence |
| 3 | η (4 agents): Synthesis lead + Calculator + Quick-Wins ranker + Fact-check | `SYNTHESIS.md`, `REVENUE-PROJECTION.json`, `QUICK-WINS.json`, `FACT-CHECK.md` |
| Red-team | A/B/C/D (parallel, mandatory) | `RED-TEAM-{A,B,C,D}-*.md` → `REVENUE-PROJECTION-v2.json` |
| 4 | θ (HTML builder + QA) | `audits/<client>-*.html` |

Each wave gates on the next. See `references/agent-teams-playbook.md` for the full team briefs, copy-pasteable agent prompts, and Wave 1 / Wave 3 / Wave 4 agent specs. The Wave 2 module prompts live in each module skill's `SKILL.md`.

## Composite scoring formula

```
composite = 0.30 × M1 + 0.20 × M2 + 0.30 × M3 + 0.20 × M4
```

Each module score is 0-100. Composite is rounded to nearest integer.

## Mandatory practices

### HONEST quantification methodology
Every $ figure traces to `docs/strategy/revenue-leak-calculator.md` 8 categories with confidence tiers. Rules:
- **P25-P75 interquartile bands** (not min×min×min — that's a P1-P99 Cartesian extreme, not a range)
- **40% overlap haircut** on the SUM of correlated findings (trust cluster, AI-surface cluster, etc.)
- **30% execution haircut** for deployment friction
- **Ramp model:** month 1-3 = 20% of steady state; full ramp by month 6
- **Triangulated baseline:** never accept analyst-guessed `sessions × CVR × AOV`. Pull from ZoomInfo, SimilarWeb, Glossy, founder podcasts, review-volume back-solve.

### Mandatory red-team pass
Every audit MUST run all 4 red-team skills before publishing any $ projection:
- `audit-red-team-baseline` — kills fabricated baselines + benchmarks
- `audit-red-team-uplifts` — kills category errors + double-counting
- `audit-red-team-cfo` — kills statistical sloppiness + uncomfortable-question survival
- `audit-red-team-domain-check` — kills semantic errors a practitioner would catch

If ANY returns RED, rebuild the projection (v2) and re-run that red team to confirm.

Individual module skills also declare their own red-team gates (subset of the 4) that must clear before the module's score is final.

### Branding
Use **only** the Editorial Warmth v2 design system from `repos/products/website/references/docs/editorial-warmth-v2.html`. Render via `editorial-warmth-audit-renderer` skill.

**FORBIDDEN** (deprecated Proposals Dark): `#0a0a12`, cyan-to-purple gradient, Outfit, Pathway Extreme. Wave 4 QA must grep these and confirm 0 matches.

### Partner framing
This skill produces partner audits, not sales pitches. Close with **Recommended Workstreams** + **Data We Requested From You** appendix. NEVER include the "$7,500 Revenue Rescue" CTA — that's the prospect-facing variant (different skill).

## Required inputs from caller
- Shopify domain (just the URL)
- Optional: client name override, audit date override, `--skip-red-team` flag (DISCOURAGED — only for internal sandbox runs)

## Required outputs
Key deliverable: `audits/<client>-revenue-audit-YYYY-MM-DD/index.html`. See `references/agent-teams-playbook.md` for the full file tree.

Deliverable variants:
- **10-section deep-dive HTML** (default) — via `/shopify-revenue-audit:run`
- **Executive one-pager** — via `/shopify-revenue-audit:one-pager <audit-dir>` (skim artifact for board / CFO / Slack)
- **Build-brief** (post-engagement) — produced manually from `QUICK-WINS.json` + `SYNTHESIS.md`

## Related skills
- `module-1-ai-discovery`, `module-2-search-catalog`, `module-3-conversion`, `module-4-technical` — the 4 audit modules dispatched in Wave 2
- `audit-red-team-baseline`, `audit-red-team-uplifts`, `audit-red-team-cfo`, `audit-red-team-domain-check` — 4 mandatory red-team passes
- `editorial-warmth-audit-renderer` — Wave 4 HTML build
- `analytics-audit` — referenced by `module-4-technical`
- `b2b-ux-reference` — referenced by `module-3-conversion` for premium-AOV trust patterns

## Canonical example
**Sene Studio (April 2026)** — `audits/senestudio-revenue-audit-2026-04-20/index.html`
- SiteHealth: 42/100 (M1: 28, M2: 38, M3: 53, M4: 51)
- Quick-Wins recovery: $1.0M-$2.5M/yr at P50 (after rebuild from v1 $11M projection)
- Red-team caught: fabricated "Baymard premium apparel CVR" benchmark, 12x baseline range from min×min×min, F5 false-contradiction (custom-fit vs standard-size domain error)
- 7-file cascade fix when client clarified F5

Use Sene as your reference for tone, length per section, and evidence-citation density.

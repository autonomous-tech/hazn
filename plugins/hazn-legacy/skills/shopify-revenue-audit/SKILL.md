---
name: shopify-revenue-audit
description: Use when auditing a Shopify store for revenue opportunities. Covers AI Discovery & Agentic Commerce (30%), Search & Catalog (20%), Conversion Experience (30%), Technical Foundation (20%). Uses 4-module composite scoring 0-100, honest quantification (P25-P75 bands not min×min×min), MANDATORY red-team pass on projections (4 separate red-team skills), Editorial Warmth v2 branded HTML deliverable. Triggers on "audit shopify store", "shopify revenue audit", "deep shopify audit".
---

# Shopify Revenue Audit

## When to use
- User has a Shopify store URL and wants revenue opportunities surfaced
- Existing client wants an optimization review (partner framing, not sales)
- Phrases: "audit this shopify store", "shopify revenue audit", "deep shopify audit", "AEO/GEO audit for shopify"

## What this skill produces
- 10-section HTML audit report (parchment + vermillion, ~140 KB, single self-contained file)
- 4-module SiteHealth composite score 0-100 (e.g., Sene = 42/100)
- Per-module deep-dive sections with cited evidence
- $-quantified Quick Wins (P25-P75 bands, NOT a single midpoint)
- Roadmap + Recommended Workstreams (partner close, no sales CTA)

## Scoring framework

| # | Module | Weight | Covers |
|---|---|---|---|
| 1 | **AI Discovery & Agentic Commerce** | 30% | ChatGPT Shopping / Perplexity Shop / Google AI Shopping / Sidekick enrollment + llms.txt / agents.txt / ai-plugin.json + AI-crawler robots policy + schema.org coverage matrix + LLM answer-fit testing + product-feed JSON-LD (GTIN/MPN/brand) + checkout-via-agent support |
| 2 | **Search & Catalog Performance** (GEO + SEO) | 20% | Google classical + AI Overviews + collection sprawl triage + jean-fragmentation-style mapping + canonical audit + internal linking + sitemap + Core Web Vitals + image SEO |
| 3 | **Conversion Experience** | 30% | Homepage + 2 collection UX + 3 hero PDP teardowns (mid-price + highest-AOV + SEO canary) + cart + copy/offer + B2B trust patterns for premium tier |
| 4 | **Technical Foundation** | 20% | Platform fingerprint + Functions migration + Shopify Markets + B2B + variant limits + app conflicts + MarTech presence (GA4/Meta Pixel/Web Pixels Manager) |

## The 4-wave pipeline

| Wave | Team | Output |
|---|---|---|
| 1 | α (3 agents): Crawler + Infra Probe + PageSpeed | crawl/, infra-probe.json, pagespeed/ |
| 2 | β/γ/δ/ε (4 module leads, parallel) | module{1-4}-*.md + sub-JSON evidence |
| 3 | η (4 agents): Synthesis lead + Calculator + Quick-Wins ranker + Fact-check | SYNTHESIS.md, REVENUE-PROJECTION.json, QUICK-WINS.json, FACT-CHECK.md |
| Red-team | A/B/C/D (parallel, mandatory) | RED-TEAM-{A,B,C,D}-*.md → REVENUE-PROJECTION-v2.json |
| 4 | θ (HTML builder + QA) | audits/<client>-*.html |

Each wave gates on the next. See `references/agent-teams-playbook.md` for the full team briefs and copy-pasteable agent prompts.

## Mandatory practices

### HONEST quantification methodology
Every $ figure traces to `docs/strategy/revenue-leak-calculator.md` 8 categories with confidence tiers. Rules:
- **P25-P75 interquartile bands** (not min×min×min — that's a P1-P99 Cartesian extreme, not a range)
- **40% overlap haircut** on the SUM of correlated findings (trust cluster, AI-surface cluster, etc.)
- **30% execution haircut** for deployment friction
- **Ramp model**: month 1-3 = 20% of steady state; full ramp by month 6
- **Triangulated baseline**: never accept analyst-guessed `sessions × CVR × AOV`. Pull from ZoomInfo, SimilarWeb, Glossy, founder podcasts, review-volume back-solve.

### Mandatory red-team pass
Every audit MUST run all 4 red-team skills before publishing any $ projection:
- `audit-red-team-baseline` — kills fabricated baselines + benchmarks
- `audit-red-team-uplifts` — kills category errors + double-counting
- `audit-red-team-cfo` — kills statistical sloppiness + uncomfortable-question survival
- `audit-red-team-domain-check` — kills semantic errors a practitioner would catch

If ANY returns RED, rebuild the projection (v2) and re-run that red team to confirm.

### Branding
Use **only** the Editorial Warmth v2 design system from `repos/products/website/references/docs/editorial-warmth-v2.html`. Render via `editorial-warmth-audit-renderer` skill.

**FORBIDDEN** (deprecated Proposals Dark): `#0a0a12`, cyan-to-purple gradient, Outfit, Pathway Extreme. Wave 4 QA must grep these and confirm 0 matches.

### Partner framing
This skill produces partner audits, not sales pitches. Close with **Recommended Workstreams** + **Data We Requested From You** appendix. NEVER include the "$7,500 Revenue Rescue" CTA — that's the prospect-facing variant (different skill).

## Required inputs from caller
- Shopify domain (just the URL)
- Optional: client name override, audit date override, --skip-red-team flag (DISCOURAGED — only for internal sandbox runs)

## Required outputs
See `.claude/commands/shopify-revenue-audit.md` for full file tree. Key deliverable: `audits/<client>-revenue-audit-YYYY-MM-DD/index.html`.

## Related skills
- `audit-red-team-baseline`, `audit-red-team-uplifts`, `audit-red-team-cfo`, `audit-red-team-domain-check` — 4 mandatory red-team passes
- `editorial-warmth-audit-renderer` — Wave 4 HTML build
- `analytics-audit` (existing) — referenced by Module 4 ε team
- `b2b-ux-reference` (existing) — referenced by Module 3 δ team for premium-AOV trust patterns

## Canonical example
**Sene Studio (April 2026)** — `audits/senestudio-revenue-audit-2026-04-20/index.html`
- SiteHealth: 42/100 (M1: 28, M2: 38, M3: 53, M4: 51)
- Quick-Wins recovery: $1.0M-$2.5M/yr at P50 (after rebuild from v1 $11M projection)
- Red-team caught: fabricated "Baymard premium apparel CVR" benchmark, 12x baseline range from min×min×min, F5 false-contradiction (custom-fit vs standard-size domain error)
- 7-file cascade fix when client clarified F5

Use Sene as your reference for tone, length per section, and evidence-citation density.

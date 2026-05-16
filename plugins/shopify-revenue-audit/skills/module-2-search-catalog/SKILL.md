---
name: module-2-search-catalog
description: Module 2 of the Shopify Revenue Audit — Search & Catalog Performance / GEO + SEO (20% of composite). Audits Google classical SERPs + AI Overviews, collection sprawl triage, category fragmentation maps (jean/suit/etc. duplicated URL clusters), canonical hygiene, internal linking, sitemap, Core Web Vitals, and image SEO. Invoked by the `shopify-revenue-audit` orchestrator during Wave 2 or directly via `/shopify-revenue-audit:rerun-module 2`.
---

# Module 2 — Search & Catalog Performance (GEO + SEO)

## When to use
- Invoked by the `shopify-revenue-audit` orchestrator during Wave 2 (γ team lead).
- Invoked directly via `/shopify-revenue-audit:rerun-module <audit-dir> 2` after a fix.
- NOT for standalone use — operates against Wave 1 recon.

## Scope

**Weight in composite:** 20%.

**Covers:**
- Collection sprawl triage (active core vs duplicates vs dead campaigns vs celebrity drops)
- Category fragmentation mapping (e.g., jeans cluster across multiple competing URLs)
- Canonical audit + 301 redirect proposals + filter-vs-collection decisions
- Internal link graph (homepage → collection → PDP ratios, orphan estimates)
- Sitemap hygiene
- Core Web Vitals penalties applied here
- Image SEO (alt-text completeness from PDP HTML samples)
- AI Overview / SERP rank probe for brand + 1-2 head terms

**Does NOT cover:** AI-discovery layer files / robots / agentic commerce (→ Module 1), conversion UX (→ Module 3), platform fingerprint / MarTech (→ Module 4).

## Inputs (from Wave 1)
- `projects/<SLUG>/diagnostics/scope.md` — catalog scale, business context
- `projects/<SLUG>/diagnostics/infra-probe.json` — sitemap counts, sub-sitemap structure
- `projects/<SLUG>/diagnostics/crawl/collection-*.md` — collection page markdown
- `projects/<SLUG>/diagnostics/pagespeed/SUMMARY.md` — CWV implications for SEO penalty

## Audit criteria

### 1. Collection Sprawl Triage → `module2/collection-sprawl-map.json`

Categorize each collection from the sitemap into one of:
- `active_core` — primary product line, keep
- `active_campaign` — current promotion, keep with end-date
- `duplicate` — overlaps with active_core, redirect
- `dead_test` — abandoned A/B, 301 or 410
- `dead_old_campaign` — expired promo, 301 to parent
- `celebrity_drop` — one-off, archive
- `unknown` — needs client clarification

Recommend per row: `immediate_delete_or_301` / `consolidate_into_parent` / `archive_no_index`.

### 2. Category Fragmentation Map → `module2/<category>-fragmentation.json`

For each high-volume category (jeans, suits, dresses, etc.):
- Identify overlapping URLs competing for the same query cluster
- Propose canonical parents
- 301 redirect map
- Filter-vs-collection decisions (when does a filter need to be its own URL?)

### 3. Link Graph & Sitemap Hygiene → `module2/link-graph.json`

- Homepage links → collection / PDP ratio
- Orphan estimate (sitemap URLs not linked from home or other collections)
- Image SEO: alt-text completeness sampled across PDP HTML

### 4. AI Overview / SERP Probe (firecrawl search if credits permit)

- Brand query rank (does the brand own its own name?)
- 1-2 commodity head terms with rank + competitor leaders
- Note AI Overview presence and which sources Google cites

## Scoring rubric (0-100)

Weighted across the four sub-areas:
- Collection hygiene: 30%
- Fragmentation severity: 30%
- Link graph + sitemap: 25%
- CWV penalty: 15%

Apply CWV penalty multiplicatively if PSI Performance < 50 on hero PDP mobile.

Typical floors:
- Score < 40: sprawl unmanaged, dozens of fragmented URLs per category, orphan rate > 40%, CWV failing
- Score 40-60: some sprawl visible, fragmentation in 1-2 categories, link graph OK
- Score 60+: clean catalog, canonical hygiene tight, CWV passing

## Outputs

Write to `projects/<SLUG>/diagnostics/module2/`:
- `module2-search-catalog.md` — section draft + score + top 3 findings (`FINDING-XXX` format)
- `module2/collection-sprawl-map.json`
- `module2/<category>-fragmentation.json` (one per high-volume category)
- `module2/link-graph.json`

**Evidence requirements:**
- Every URL flagged for redirect/archive cites the sitemap entry + the overlap evidence
- Fragmentation claims cite specific competing URL pairs

## Red-team gates

Module 2 findings must pass:
- `audit-red-team-uplifts` — SEO uplift claims often violate category math (don't double-count traffic recovery across overlapping fragmentations)
- `audit-red-team-baseline` — never accept analyst-guessed organic traffic baselines; pull from SimilarWeb / Glossy / GSC if available

If RED, rebuild and re-run before composite score is final.

## Related skills
- `shopify-revenue-audit` — orchestrator
- `audit-red-team-uplifts`, `audit-red-team-baseline` — mandatory gates
- See `../shopify-revenue-audit/references/agent-teams-playbook.md` § Wave 2 γ for the full agent prompt

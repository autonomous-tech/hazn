# Section Structure — 10 Sections

Per-section spec. Use after reading SKILL.md.

---

## Section 1 · Hero

**Anchor:** `#hero`
**Background:** Midnight `#0D0D1F` with subtle vermillion glow
**Source:** `SYNTHESIS.md` §1 Executive Verdict

**Required elements:**
- Eyebrow (JetBrains Mono uppercase): `AUTONOMOUS × <CLIENT> · SHOPIFY REVENUE AUDIT`
- H1 (Fraunces, oversized clamp(2.6rem, 6vw, 5rem) parchment-light): the dominant blocker as a single sentence (e.g., "Sene Studio is conversion-healthy — and invisible to the next wave of commerce.")
- Date subline
- Score pill (vermillion-tinted): `<NN> · OVERALL SITEHEALTH · /100`
- Executive verdict box: 3-4 sentences from SYNTHESIS verdict

**Length target:** ~100 lines HTML

---

## Section 2 · The Alarm

**Anchor:** `#alarm`
**Background:** Parchment `#F5EFE0`
**Source:** SYNTHESIS dominant blocker + REVENUE-PROJECTION-v2 top_3_defensible_headlines

**Required elements:**
- Section eyebrow: `02 · DOMINANT REVENUE BLOCKER`
- Section H2 (Fraunces): the headline finding (e.g., "Sene has 916 verified reviews live today. Google sees zero.")
- Narrative paragraph (2-3 paragraphs) explaining the dominant blocker
- **CRITICAL CALLOUT BOX** (vermillion border): "We will not publish a total recovery number until admin baseline lands" + baseline triangulation summary
- 3 impact cards (grid-3) — the three highest-confidence individual findings with P25-P75 bands. NOT a single midpoint.
- 3 secondary cards (grid-3): Payback (in months at P25 + P50), Guarantee safety (Nx multiplier), Effort to unlock (hours)
- Closing callout: dominant-blocker rationale + score interpretation (X/100 is readiness, NOT % leak)

**Length target:** ~150 lines HTML

---

## Section 3 · Score Grid

**Anchor:** `#scores`
**Background:** Parchment-light `#FAF7F0`
**Source:** Each module's score (28, 38, 53, 51 for Sene example)

**Required elements:**
- Section H2: "Four module scores. One compounding problem."
- 4 score cards in grid-2 layout:
  - SVG score circle (stroke-dasharray) with color by range (sage ≥70, gold 50-69, vermillion <50)
  - Module number + name + weight
  - 2-3 sentence summary from each module's exec summary
  - "View deep dive →" link to module section
- Card order: Module 1 → 2 → 3 → 4

**Length target:** ~120 lines HTML

---

## Section 4 · Root Cause

**Anchor:** `#root-cause`
**Background:** Parchment
**Source:** SYNTHESIS §2 (Root Cause) + §3 (Cross-Module Correlations)

**Required elements:**
- Section H2 (with squiggle underline accent): "Four module scores. One compounding problem."
- 4-6 paragraph root-cause narrative
- Hypothesis callout (e.g., "Sene is conversion-healthy and invisible to the next 12-24 months of commerce.")
- 5-8 cross-module correlation bullets

**Length target:** ~150 lines HTML

---

## Section 5 · Module 1 Deep Dive — AI Discovery & Agentic Commerce

**Anchor:** `#module1`
**Background:** Parchment
**Source:** `module1-ai-discovery.md` + `module1/agentic-commerce.json` + `module1/schema-matrix.json` + `module1/llm-answer-fit.md`

**Required elements:**
- Section eyebrow + H2 + score badge (e.g., "28/100 · CRITICAL")
- Executive summary paragraph
- **Sub-section A: Agentic Commerce Readiness** — rubric walkthrough table
- **Sub-section B: Schema.org Coverage Matrix** — visible HTML table:
  - Rows: Home / Collection / PDP-1 / PDP-2 / PDP-3 / FAQ / Blog
  - Columns: Product / Offer / AggregateRating / Review / FAQPage / BreadcrumbList / Organization / WebSite / SearchAction
  - Cells: ✓ (sage), ✗ (vermillion), — (caption gray)
- **Sub-section C: LLM Answer-Fit Testing** — table of 8-10 target queries with rank/competitor results
- Top 3 findings as finding cards (left-border severity color)

**Length target:** ~250 lines HTML

---

## Section 6 · Module 2 Deep Dive — Search & Catalog Performance

**Anchor:** `#module2`
**Background:** Parchment-light
**Source:** `module2-search-catalog.md` + `module2/collection-sprawl-map.json` + `module2/jean-fragmentation.json` + `module2/link-graph.json`

**Required elements:**
- Section H2 + score badge
- **Collection Sprawl Map** visual: stacked horizontal bar showing N total → categorization (active_core / duplicate / dead_test / dead_old_campaign / celebrity_drop / unknown / etc.)
- Category fragmentation analysis (jean fragmentation table or analogous)
- Link graph + sitemap hygiene findings
- CWV ceiling callout (per pagespeed/SUMMARY.md)
- Top 3 findings as finding cards

**Length target:** ~200 lines HTML

---

## Section 7 · Module 3 Deep Dive — Conversion Experience

**Anchor:** `#module3`
**Background:** Parchment
**Source:** `module3-conversion.md` + `module3/pdp/*.md` + `module3/cart-copy-offer.md` + `module3/homepage-collection.md`

**Required elements:**
- Section H2 + score badge
- Homepage teardown findings
- Collection UX teardown
- **3 PDP teardown cards** (parchment-light, rounded-2xl):
  - Score pill per PDP
  - Top 3 finds per PDP
  - For highest-AOV PDP: B2B trust patterns sub-score + what's missing
- Cart UX + offer stack scatter analysis
- Top 5 findings as finding cards

**Length target:** ~350 lines HTML (widest module)

---

## Section 8 · Module 4 Deep Dive — Technical Foundation

**Anchor:** `#module4`
**Background:** Parchment-light
**Source:** `module4-technical.md` + `module4/platform-scan.json` + `module4/logic-scan.json` + `module4/app-analytics.json`

**Required elements:**
- Section H2 + score badge
- Platform fingerprint (theme, Functions, Markets, B2B)
- App stack inventory (10-app table with monthly cost estimates)
- Conflicts callout (Klaviyo + Postscript dual SMS, Rebuy + native cart, etc.)
- MarTech presence — pixel detection table (GA4 / GTM / Meta / TikTok / Web Pixels Manager / Trekkie)
- Healthy signals callout (no legacy ScriptTag, modern checkout extensibility)
- Top 3 findings

**Length target:** ~200 lines HTML

---

## Section 9 · Revenue Projection & Quick Wins

**Anchor:** `#revenue`
**Background:** Parchment
**Source:** `REVENUE-PROJECTION-v2.json` + `QUICK-WINS.json` + `RED-TEAM-{A,B,C,D}-*.md`

**Required elements:**
- **Methodology Update Callout** (vermillion border, prominent) — only if v2 exists alongside v1:
  > "Methodology update (YYYY-MM-DD) — Projection v2.0
  > This projection was rebuilt after internal red-team review identified [list of v1 errors]. V2 uses P25-P75 interquartile bands around a central baseline, cites only verifiable benchmarks, applies a 40% overlap discount + 30% execution haircut, and refuses to project totals until admin baseline data is plugged in. See diagnostics/REVENUE-PROJECTION-v2.json."
- **Scoring Summary Table**: 4 modules + weights + contributions + total
- **Revenue Projection Table** (3 scenarios): Current / Quick Wins / Full Optimization with P25/P50/P75
- **Top 5 by $ table**: ranked findings with confidence + monthly + annual ranges
- **Quick Wins grid** (12 numbered cards):
  - Rank, module, finding ID
  - Action title (Fraunces serif H4)
  - Effort badge (Low/Med/High) + Impact badge (Low/Med/High)
  - Monthly + annual $ range
- Methodology footer: cite Calculator + Baymard + Spiegel + Google PSI + Klaviyo + Invesp benchmarks; list dropped v1 benchmarks; data gaps

**Length target:** ~300 lines HTML

---

## Section 10 · Roadmap + Workstreams + Data Requested

**Anchor:** `#roadmap`
**Background:** Parchment-light
**Source:** `QUICK-WINS.json` + `data-to-request.md`

**Required elements:**
- 3-column roadmap grid: This Week / This Sprint / Next Quarter, 3-5 items each
- **Recommended Workstreams** section:
  - Agentic Commerce Sprint (3 weeks)
  - Collection Consolidation (2 weeks)
  - PDP Conversion Patches (ongoing)
  - Schema + AEO Build-Out (ongoing)
  - MarTech Audit w/ admin access (1 week)
- **Data We Requested From You** appendix: GA4 / GSC / Markets config / feed destinations / Klaviyo flow performance
- **NO sales CTA, NO "$7,500" reference, NO "Revenue Rescue engagement"** — partner framing throughout

**Length target:** ~150 lines HTML

---

## Footer

**Source:** FACT-CHECK.md + brand boilerplate

**Required elements:**
- Autonomous + Client mark
- "Prepared by Autonomous Technologies, YYYY-MM-DD"
- "Methodology: Revenue Leak Calculator v3 · HONEST framework · Fact-check PASS (η4) · Red-Team A/B/C/D PASS"
- "Projection v2.0 (YYYY-MM-DD). Supersedes v1.0 which contained [error class]; red-team corrections applied per RED-TEAM-{A,B,C,D}-*.md"
- Disclaimer: revenue ranges contingent on admin baseline; tightens within 48h of GA4 access

**Length target:** ~80 lines HTML

---

## Total HTML budget

~2000 lines, ~140 KB.

If significantly larger, sections are too verbose. If significantly smaller, content is too thin for a $25-50K engagement deliverable.

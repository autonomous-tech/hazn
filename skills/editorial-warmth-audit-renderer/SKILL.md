---
name: editorial-warmth-audit-renderer
description: Use to render a Shopify revenue audit (or comparable diagnostic deliverable) as a single self-contained HTML file in Autonomous's current Editorial Warmth v2 brand (parchment + vermillion + Fraunces + DM Sans + JetBrains Mono). Consumes diagnostic outputs from the 4-module audit pipeline (SYNTHESIS.md, REVENUE-PROJECTION-v2.json, per-module drafts, QUICK-WINS.json, FACT-CHECK.md, red-team reports) and produces a 10-section index.html with sticky TOC, responsive layout, and print stylesheet. SUPERSEDES the deprecated Proposals Dark template — actively forbids legacy `#0a0a12` / cyan-purple / Outfit / Pathway Extreme tokens. Triggers on "build the audit report", "render the audit HTML", or as Wave 4 of /shopify-revenue-audit pipeline.
---

# Editorial Warmth Audit Renderer

## When to use

- Wave 4 of the Shopify revenue audit pipeline (after Wave 3 synthesis + red-team rebuild)
- Anytime a diagnostic deliverable needs to render in Autonomous's current brand
- Phrases: "build the report", "render the audit HTML", "produce the deliverable"

## What you produce

A single self-contained `index.html` at:
```
audits/<client>-revenue-audit-YYYY-MM-DD/index.html
```

- **No build step** (no Tailwind compile, no JS framework)
- **External deps only:** Google Fonts (Fraunces, DM Sans, JetBrains Mono)
- **Inline CSS** (~140 KB total file, ~2000 lines)
- **Sticky left-sidebar TOC** with scroll-spy highlighting active section
- **Responsive:** sidebar collapses ≤900px, single-column ≤600px
- **Print stylesheet:** `@media print` hides sidebar, prevents page-break clipping

## Required inputs

Read all of these before writing the HTML:

```
projects/<client>/diagnostics/
├── scope.md                        # Business snapshot, pre-audit hypotheses
├── SYNTHESIS.md                    # Section 4 (Root Cause), Section 7 (hypothesis validation)
├── REVENUE-PROJECTION-v2.json      # Section 9 (Projection table, top 5)
├── QUICK-WINS.json                 # Section 9 (Quick Wins grid)
├── FACT-CHECK.md                   # Footer (PASS verdict)
├── module1-ai-discovery.md         # Section 5 + Module 1 score card
├── module1/schema-matrix.json      # Section 5 schema matrix visual
├── module2-search-catalog.md       # Section 6 + Module 2 score card
├── module2/collection-sprawl-map.json   # Section 6 sprawl visual
├── module3-conversion.md           # Section 7 + Module 3 score card
├── module3/pdp/*.md                # Section 7 PDP teardowns (× 3)
├── module4-technical.md            # Section 8 + Module 4 score card
├── data-to-request.md              # Section 10 appendix
├── RED-TEAM-A-baseline.md          # Methodology footer (cite)
├── RED-TEAM-B-uplifts.md           # Methodology footer (cite)
├── RED-TEAM-C-cfo.md               # Methodology footer (cite)
└── RED-TEAM-D-domain-check.md      # Methodology footer (cite)
```

Plus these brand sources:
- `repos/products/website/references/docs/editorial-warmth-v2.html` — DESIGN SYSTEM (copy tokens verbatim)
- `audits/senestudio-revenue-audit-2026-04-20/index.html` — CANONICAL EXAMPLE (140KB, 10 sections, all components)

## The 10 sections

See `references/section-structure.md` for full per-section spec. Quick map:

| # | Section | Source | Notes |
|---|---|---|---|
| 1 | Hero | SYNTHESIS executive verdict | Midnight-backed; oversized Fraunces H1 |
| 2 | The Alarm | SYNTHESIS dominant blocker | 3 highest-confidence findings as P25-P75 cards |
| 3 | Score Grid | Module scores | 4 score cards, parchment-light bg |
| 4 | Root Cause | SYNTHESIS §2-3 | 4-6 paragraphs + 5-8 cross-module bullets |
| 5 | Module 1 Deep Dive | module1-* | Includes schema matrix table + LLM answer-fit table |
| 6 | Module 2 Deep Dive | module2-* | Includes collection sprawl visual |
| 7 | Module 3 Deep Dive | module3-* | Includes 3 PDP teardown cards |
| 8 | Module 4 Deep Dive | module4-* | Apps + MarTech presence |
| 9 | Revenue Projection & Quick Wins | REVENUE-PROJECTION-v2.json + QUICK-WINS.json | Methodology Update callout if v2 rebuilt from v1 |
| 10 | Roadmap + Workstreams + Data Requested | QUICK-WINS.json + data-to-request.md | Partner close, NO sales CTA |

## Brand rules (non-negotiable)

See `references/design-tokens.md` for full palette + typography.

**Required tokens** (must appear in CSS):
- Parchment `#F5EFE0` (primary bg)
- Vermillion `#E8513D` (CTA / accent)
- Midnight `#0D0D1F` (hero band)
- Sage `#7CA982` (pass / positive)
- Gold `#D4A853` (warning / medium)
- Ocean `#0EA5E9` (info / opportunity)
- Ink `#1A1A2E` (headings)
- Prose `#4A4A60` (body)

**Forbidden tokens** (Wave 4 QA must grep these and confirm 0):
- `#0a0a12` (Proposals Dark bg)
- Cyan-to-purple gradient (`#00d5ff → #b42aff`)
- `Outfit` font
- `Pathway Extreme` font

If any forbidden token leaks into output, regenerate.

## Component patterns

See `references/template-snippets.html` for copy-paste markup. Components included:
- Hero section (midnight-backed)
- Sticky TOC (scroll-spy)
- Alarm section (refusal-to-project + 3 finding cards)
- Score card (1 of 4 in grid)
- Finding card (left-border severity color)
- Schema coverage matrix table
- Revenue projection table
- Quick win numbered card
- Roadmap 3-column grid
- Methodology update callout (for v2 rebuild)
- Footer

## Required behaviors

- **Self-contained**: inline ALL CSS. No external `.css` files. JS only for sticky-TOC scroll-spy (~30 lines).
- **Methodology Update callout in Section 9** if `REVENUE-PROJECTION-v2.json` exists alongside `REVENUE-PROJECTION.json` (signals red-team rebuild). Quote the corrections explicitly.
- **Partner framing**: close with "Recommended Workstreams". NEVER include "$7,500 Revenue Rescue" CTA, NEVER include sales pitch language. This is the partner-audit variant.
- **Cite evidence**: every $ figure, score, and finding must reference a diagnostic file path either inline or in a footer methodology block.

## Output verification (run before declaring done)

- `grep -E "#0a0a12|Outfit|Pathway Extreme|cyan|purple"` returns 0 in the HTML
- `grep -E "#F5EFE0|#E8513D|Fraunces|DM Sans"` returns >5 each
- All 10 sections present (search for section IDs: hero, alarm, scores, root-cause, module1, module2, module3, module4, revenue, roadmap)
- Module scores match SYNTHESIS.md scoring table
- Top-5 projection findings match REVENUE-PROJECTION-v2.json
- HTML validates (`python3 -c "import html.parser; html.parser.HTMLParser().feed(open(...).read())"`)

## Canonical example

**Sene Studio audit** at `audits/senestudio-revenue-audit-2026-04-20/index.html`:
- 140KB, ~2000 lines
- All Editorial Warmth tokens correct
- Methodology Update callout present (v2 rebuilt from v1)
- 10 sections, sticky TOC, print stylesheet
- 0 forbidden tokens

Use as the reference skeleton — DOM structure + class names are stable across audits.

## Related skills

- `shopify-revenue-audit` — orchestrator that invokes this in Wave 4
- All four `audit-red-team-*` skills — provide the corrections this renderer must surface in the Methodology Update callout

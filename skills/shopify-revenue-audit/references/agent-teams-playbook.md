# Agent Teams Playbook — Shopify Revenue Audit

Full team briefs and copy-pasteable agent prompts for the 4-wave pipeline. Read after `SKILL.md` when actually running the audit.

---

## Wave 0 — Orchestration (you, Opus)

You're the orchestrator. Read `SKILL.md` + this playbook + `.claude/commands/shopify-revenue-audit.md`. Then:

1. **Pick the client slug** (e.g., `senestudio`) and audit date (`YYYY-MM-DD`).
2. **Create dirs**:
   ```
   projects/<slug>/diagnostics/{crawl,pagespeed,module1,module2,module3/pdp,module4}
   audits/<slug>-revenue-audit-YYYY-MM-DD/assets
   ```
3. **Write `scope.md`** — fetch the homepage with firecrawl, summarize:
   - Business: what they sell, price range, geography
   - Stack: visible apps (Judge.me, Klaviyo, Shop Pay, Route, etc.) — grep `/cdn/shop/`, `klaviyo.com`, `shop.app`
   - Catalog scale: count `/collections/*` URLs from sitemap
   - Pre-audit hypotheses (per-module, will be tested)
   - Target LLM queries for answer-fit testing (8-10 high-intent queries)
4. **Identify hero PDPs** for Wave 2 δ team:
   - Mid-price representative (e.g., $100-200, high review count)
   - Highest-AOV (premium suit / tier-1 SKU — applies B2B trust patterns)
   - SEO-fragmentation canary (one with sibling-URL problems)
5. **Dispatch Wave 1.**

---

## Wave 1 — Discovery & Crawl Team (α)

3 parallel agents.

### α1 — Crawler (Sonnet)

```
You are α1 Crawler in a Shopify revenue audit. Save outputs to projects/<SLUG>/diagnostics/crawl/.

Use firecrawl. Concurrency limit is 2 parallel jobs. Total credit budget for this agent: ~15.

Fetch:
1. Homepage (firecrawl scrape, markdown + raw HTML via `--format markdown,html`)
2. 5 representative collections (markdown only): top mens/womens, jeans, suits, new-arrivals
3. 3 hero PDPs (markdown + raw HTML — needed for schema parsing):
   - <PDP-1 url> (mid-price)
   - <PDP-2 url> (highest-AOV)
   - <PDP-3 url> (SEO canary)
4. Cart, FAQ, returns, privacy, blog index (markdown only)

Run firecrawl in batches of 2 with `&` and `wait`. Save with descriptive filenames.

Report back:
- File list with sizes
- Any 404s
- Remaining firecrawl credits

Do NOT analyze the content — just fetch and save.
```

### α2 — Infrastructure Probe (Sonnet)

```
You are α2 Infrastructure Probe. Save to projects/<SLUG>/diagnostics/infra-probe.json.

Probe via curl (-A "Mozilla/5.0 (compatible; AutonomousAudit/1.0)"):

AI-layer files (presence + content preview):
- /llms.txt, /llms-full.txt, /agents.txt
- /.well-known/ai-plugin.json, openai.json, mcp.json

Classical infra:
- /robots.txt (full content)
- /sitemap.xml + sub-sitemaps (sitemap_products_1.xml, sitemap_collections_1.xml, sitemap_pages_1.xml)
- /products.json?limit=250 (sample 3 products for field coverage)
- /collections.json?limit=250

robots.txt AI-crawler policy — for each of these 13 bots, mark allowed/disallowed/not_mentioned:
GPTBot, ChatGPT-User, OAI-SearchBot, Claude-Web, ClaudeBot, PerplexityBot, Perplexity-User, Google-Extended, Applebot-Extended, Amazonbot, cohere-ai, Bytespider, CCBot

products.json field coverage (sample 3 products):
- Required fields: id, title, handle, body_html, vendor, product_type, tags
- Variants: sku, price, barcode (← GTIN), weight, grams
- Images, options

Output JSON shape (see SKILL.md for schema). Note any Shopify-injected policy comments in robots.txt (e.g., "no buy-for-me agents").

Report back:
- Top 3 concerning signals for discovery-layer readiness
- Whether llms.txt / agents.txt / ai-plugin.json present (Y/N each)
- AI-crawler policy summary (mostly allowed / mostly silent / mostly blocked)
```

### α3 — PageSpeed Runner (Haiku)

```
You are α3 PageSpeed runner. Save to projects/<SLUG>/diagnostics/pagespeed/.

Use Google PSI free endpoint:
https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=<URL>&strategy=<mobile|desktop>&category=performance&category=accessibility&category=seo&category=best-practices

5 URLs × 2 strategies = 10 calls. URLs:
1. Homepage
2. Top collection
3. PDP 1, 2, 3 (the hero PDPs from α1)

Run in parallel batches of 5. Retry 429 with 10s sleep.

Save filenames: home-{mobile,desktop}.json, collection-{slug}-{mobile,desktop}.json, pdp-{slug}-{mobile,desktop}.json

Then write SUMMARY.md:
- Per-page table: Page | Strategy | Performance | LCP | CLS | TBT | INP | Speed Index
- Top 3 opportunities per page (by estimated savings)
- Flag any page < 50 Performance

Report back:
- Per-page scores
- Biggest performance red flag
```

**Wave-1 gate:** all 3 agents complete. Verify file presence before Wave 2.

---

## Wave 2 — Module Teams (β/γ/δ/ε, parallel)

Each team owns one module: produces evidence + 0–100 score + draft section.

### β — Module 1: AI Discovery & Agentic Commerce (Sonnet)

```
You are β Lead. Module 1 (30% weight). Read first:
- projects/<SLUG>/diagnostics/scope.md
- projects/<SLUG>/diagnostics/infra-probe.json (α2)
- projects/<SLUG>/diagnostics/crawl/pdp-{1,2,3}.html (raw HTML for schema parsing)

Sub-rubric (3 parts, weighted):

A. Agentic Commerce Readiness (40%):
   - llms.txt / agents.txt / ai-plugin.json presence
   - AI-crawler robots policy (13 bots)
   - Product feed quality: GTIN/MPN/brand/condition presence in products.json
   - Checkout-via-agent signals (Shop Pay Catalyst, Apple Pay, Shopify Agent Checkout)
   - Shopify Sidekick / chatbot detection
   - Note any Shopify-platform-level robots policy ("no buy-for-me agents")

B. Schema.org Coverage Matrix (35%):
   Parse <script type="application/ld+json"> in PDP/collection/home HTML.
   Build matrix: Templates × Schema types
   Templates: Home, Collection, PDP-1, PDP-2, PDP-3, FAQ, Blog
   Schemas: Product, Offer, AggregateRating, Review, FAQPage, BreadcrumbList, Organization, WebSite, SearchAction
   For Product schema, flag presence of: gtin13/gtin/mpn/brand/aggregateRating
   For Offer: priceValidUntil, availability, shippingDetails

C. LLM Answer-Fit Testing (25%):
   Use `firecrawl search` for each of 8-10 target queries from scope.md
   For each: does <DOMAIN> appear? rank? competitor winners?
   Flag uncontested blue-ocean opportunities (queries with no apparel competitors in top 10)

Output:
- module1-ai-discovery.md (section draft + score)
- module1/agentic-commerce.json (rubric scores)
- module1/schema-matrix.json (the matrix)
- module1/llm-answer-fit.md (probe results)

Cite every claim to file:line. Report module score + top 3 findings.
```

### γ — Module 2: Search & Catalog Performance (Sonnet)

```
You are γ Lead. Module 2 (20% weight). Read first:
- scope.md
- infra-probe.json (sitemap counts)
- crawl/collection-*.md
- pagespeed/SUMMARY.md (CWV implications)

Tasks:
1. Collection Sprawl Triage → module2/collection-sprawl-map.json
   Categorize each collection from sitemap into:
   active_core | active_campaign | duplicate | dead_test | dead_old_campaign | celebrity_drop | unknown
   Recommend: immediate_delete_or_301, consolidate_into_parent, archive_no_index

2. Category Fragmentation Map (jeans, suits, etc.) → module2/jean-fragmentation.json (or analogous)
   Identify overlapping URLs competing for same query cluster.
   Propose canonical parents + 301 redirect map + filter-vs-collection decisions.

3. Link Graph & Sitemap Hygiene → module2/link-graph.json
   - Homepage links → collection / PDP ratio
   - Orphan estimate (sitemap URLs not linked from home)
   - Image SEO (alt-text completeness from PDP HTML samples)

4. AI Overview / SERP Probe (firecrawl search if credits permit):
   - Brand query rank
   - 1-2 commodity head terms
   - Note rank + competitor leaders

Score 0-100 weighted across: collection hygiene, fragmentation severity, link graph, CWV penalty.

Output: module2-search-catalog.md + module2/*.json. Cite evidence. Report score + top 3 findings.
```

### δ — Module 3: Conversion Experience (Sonnet)

```
You are δ Lead. Module 3 (30% weight, widest module). Read first:
- scope.md, pagespeed/SUMMARY.md
- crawl/home.json, crawl/collection-*.md, crawl/cart.md
- crawl/pdp-{1,2,3}.{md,html}
- repos/tools/autonomous-claude-plugins/plugins/shopify-cro-audit/skills/shopify-cro-audit/references/{checklist-homepage,checklist-product,checklist-cart,benchmarks}.md
- .hazn/skills/conversioniq/SKILL.md, .hazn/skills/ux-ui/SKILL.md, .hazn/skills/b2b-ux-reference/SKILL.md (premium tier)

For each of the 3 hero PDPs, check:
- Above-fold structure (hero image, title, price, ★ rating/review count, CTA)
- ★ rating visibility near price (commonly missing — verify)
- Fit quiz / configurator prominence
- Urgency/scarcity signals
- Mobile layout
- Trust signals (guarantee, shipping, returns near CTA)
- Upsell / cross-sell
- Review section quality
- Production/lead-time framing

For homepage: hero clarity, social proof above fold, navigation UX (catalog scale matters), mobile.
For collections: filter quality, per-tile review counts, made-to-order badges.
For cart: shipping threshold messaging, trust badges, upsell slot, save-for-later.
For copy/offer: value prop, guarantee framing, intl messaging, offer stack consolidation.
For premium tier (highest-AOV PDP): apply b2b-ux-reference rubric — case studies, founder story, process transparency, risk-reversal, comparison frame.

Score 0-100 weighted: homepage 15% / collections 15% / PDP-1 15% / PDP-2 15% / PDP-3 10% / cart 10% / copy 15% / B2B trust 5%. CWV penalty applied.

Output: module3-conversion.md + module3/{homepage-collection,cart-copy-offer}.md + module3/pdp/{1,2,3}.md. Cite evidence. Report score + top 5 findings.
```

### ε — Module 4: Technical Foundation (Sonnet)

```
You are ε Lead. Module 4 (20% weight). Read first:
- scope.md, infra-probe.json, pagespeed/SUMMARY.md
- crawl/pdp-{1,2,3}.html (signature detection)
- .hazn/skills/analytics-audit/SKILL.md (mandatory — use this rubric)

Detection tasks (grep PDP HTML):

1. Platform → module4/platform-scan.json
   - Theme name + version (Shopify.theme.name)
   - Shopify Plus signals (Shopify.plus, B2B endpoints)
   - Shopify Markets config (locale, multi-currency, country selector)
   - Shopify Functions (modern checkout extensions vs legacy ScriptTag)
   - Variant cap risk (count variants on the configurator-heaviest PDP)

2. Logic → module4/logic-scan.json
   - Pricing consistency (any JS-mutated prices?)
   - App conflicts (signatures of: Klaviyo + Postscript both? Rebuy + native cart? Searchanise vs Shopify Search?)
   - Render-blocking script count
   - Legacy ScriptTag traces

3. Apps + MarTech → module4/app-analytics.json
   Apps to detect: Judge.me, Klaviyo, Postscript, Attentive, Shop Pay, Loox, Yotpo, ReCharge, Bold, Shogun, GemPages, PageFly, Octane AI, Stamped, Gorgias, Tidio, ReConvert, Honeycomb, UpCart, Route, Seel, Rebuy, Searchanise, Accessibly, Richpanel
   
   MarTech presence (CRITICAL):
   - GA4 (G-XXXXXXX or gtag()
   - GTM (GTM-XXXXXXX)
   - Meta Pixel (fbq() or facebook.net/en_US/fbevents.js)
   - TikTok Pixel (ttq.track)
   - Pinterest, Microsoft Clarity, Hotjar
   - Web Pixels Manager (Shopify.analytics.publish)
   - Trekkie (Shopify internal)
   
   If GA4/Meta absent from public HTML but Web Pixels Manager active → mark "MarTech black box, requires admin access"

4. Data to Request → data-to-request.md (admin-side)
   - GA4 access (or 90d export)
   - Google Search Console
   - Shopify Markets / B2B / Functions config
   - Product feed destinations (GMC, Meta, TikTok, ChatGPT Shopping)
   - Klaviyo flow performance
   - Any AI/chat integrations

Score 0-100 weighted: platform 30% / logic 25% / apps 20% / MarTech 25%. CWV note.

Output: module4-technical.md + module4/*.json + data-to-request.md. Cite evidence. Report score + top 3 findings.
```

**Wave-2 gate:** all 4 module leads have score + draft. If any module returns without cited evidence, re-run.

---

## Wave 3 — Synthesis Team (η)

### η1 — Synthesis Lead (Opus)

```
You are η1. Read all 4 module drafts + scope.md + pagespeed/SUMMARY.md + the 8-10 LLM answer-fit probes.

Produce SYNTHESIS.md (1500-2500 words):

1. Executive Verdict (3-4 sentences) — TL;DR for client
2. Root Cause (4-6 paragraphs) — narrative showing 4 modules = 1 compounding loss
3. Cross-Module Correlations (5-8 bullets) — findings in DIFFERENT modules that amplify each other
4. Dominant Revenue Blocker (one to lead with) — sets up Section 2 "The Alarm"
5. What Sene Is Doing Right (3-5 positive bullets — do not be all doom)
6. Scoring Summary Table (verify arithmetic)
7. Pre-Audit Hypothesis Validation — table of all hypotheses from scope.md, marked Confirmed/Rejected/Partial with evidence

Cite every claim file:line. Verify the composite score arithmetic.
```

### η2 — Calculator Operator (Sonnet)

```
You are η2. Read SYNTHESIS.md + QUICK-WINS.json (if η3 ran first; otherwise produce concurrently) + docs/strategy/revenue-leak-calculator.md.

Build REVENUE-PROJECTION.json. For each finding:
- Calculator category (one of 8: pricing errors, API waste, broken UX, dead attribution, agency waste, manual labor, security risk, opportunity cost)
- Confidence tier: HIGH/MEDIUM/LOW
- Mechanism (1-2 sentences)
- Affected traffic share (% — flag if guessed)
- Uplift % range (cite benchmark explicitly: source + year + sample)
- Monthly $ leak range
- Annual $ leak range
- Fix effort hours
- Fix source (which quick-win?)

Three scenarios:
- current_state: baseline (P25/P50/P75)
- quick_wins_only: top 12 wins, ~76 hours, $35-50K engagement, post-haircut monthly + annual + payback
- full_optimization: F1-F20, post-ramp, 6-12mo

CRITICAL: do NOT produce min×min×min ranges. Use P25-P75 around a central baseline. Apply 40% overlap haircut + 30% execution haircut to additive sums (those happen post-Red-Team in v2 — for v1, document the gross sums and flag for haircut).

Output the gross v1 — Red Team will rebuild as v2.
```

### η3 — Quick-Wins Ranker (Sonnet)

```
You are η3. Read SYNTHESIS.md + module drafts.

Extract top 10-12 quick wins. For each:
{
  "rank": N,
  "title": "...",
  "module": 1|2|3|4,
  "effort": "low|medium|high",
  "effort_estimate_hours": N,
  "impact": "low|medium|high",
  "impact_rationale": "...",
  "source_findings": ["module1-ai-discovery.md §X", ...],
  "dependencies": [],
  "is_quick_win": true,
  "is_foundational": false
}

Also include foundational items (high-impact, longer ramp) separately as is_foundational:true.

Ranking criteria (in order): Module 1 weight first, ≤1 sprint, no client dependency, reversible, measurable.
At least 4 from M1, 2-3 each from M2/M3, 1-2 from M4.

Output: QUICK-WINS.json
```

### η4 — Fact-Check (Haiku)

```
You are η4. Read SYNTHESIS.md + QUICK-WINS.json + REVENUE-PROJECTION.json.

For every load-bearing claim (verdict, $ figure, score, benchmark citation), verify it appears in source diagnostics. Flag:
- Unsupported claims (no source)
- Questionable phrasing (claim stronger than evidence supports)
- Pre-flagged concerns from synthesis (verify each)

Output: FACT-CHECK.md with PASS / PASS-WITH-NOTES / FAIL verdict. Detail each unsupported/questionable claim.
```

**Wave-3 gate:** η4 PASS or PASS-WITH-NOTES.

---

## Red-Team Pass (mandatory)

Run all 4 in parallel. Each invokes its own skill:
- `audit-red-team-baseline` → RED-TEAM-A-baseline.md
- `audit-red-team-uplifts` → RED-TEAM-B-uplifts.md
- `audit-red-team-cfo` → RED-TEAM-C-cfo.md
- `audit-red-team-domain-check` → RED-TEAM-D-domain-check.md

If any return RED, dispatch a rebuild agent to produce REVENUE-PROJECTION-v2.json with corrections. Re-run that red team to confirm the rebuild. Do not proceed to Wave 4 until all reds resolve.

---

## Wave 4 — Deliverable Build (θ)

### θ1 — HTML Builder (Opus or Sonnet)

```
You are θ1. Use the `editorial-warmth-audit-renderer` skill.

Read first:
- repos/products/website/references/docs/editorial-warmth-v2.html (DESIGN SYSTEM SOURCE)
- audits/senestudio-revenue-audit-2026-04-20/index.html (SKELETON to copy)
- All wave-3 + red-team outputs in projects/<SLUG>/diagnostics/

Produce single self-contained audits/<SLUG>-revenue-audit-YYYY-MM-DD/index.html with:
- 10 sections per editorial-warmth-audit-renderer/references/section-structure.md
- Editorial Warmth v2 tokens only (parchment + vermillion + Fraunces + DM Sans + JetBrains Mono)
- Sticky TOC, responsive, print stylesheet
- Methodology Update callout in Section 9 if v2 projection rebuilt from v1
- Recommended Workstreams close (NO sales CTA)
```

### θ3 — QA (Haiku)

```
You are θ3. Open the new index.html. Verify:

Branding compliance:
- Required hex colors present: #F5EFE0, #E8513D, #0D0D1F, #7CA982, #D4A853, #0EA5E9, #1A1A2E, #4A4A60
- FORBIDDEN tokens absent: #0a0a12, "Outfit", "Pathway Extreme", cyan-to-purple gradient. Each must grep to 0.
- Google Fonts: Fraunces + DM Sans + JetBrains Mono

Content markers:
- Overall score in hero
- 4 module scores match SYNTHESIS.md table
- Revenue ranges match REVENUE-PROJECTION-v2.json (or v1 if no rebuild)
- All 3 PDP teardowns present
- Recommended Workstreams section
- NO "$7,500" / "Revenue Rescue engagement"

Structural:
- DOCTYPE, html lang, viewport meta
- Sticky TOC, @media print, responsive breakpoints
- HTML validates

Verdict: READY TO SHIP / NEEDS FIXES.
```

---

## Commit & deploy

```bash
cd repos/sales/autonomous-proposals
node scripts/generate-index.js   # Regenerates the master index.html
git add audits/<SLUG>-revenue-audit-YYYY-MM-DD/ projects/<SLUG>/ index.html
git commit -m "feat: add <SLUG> Shopify revenue audit (YYYY-MM-DD)"
git push origin main
```

GitHub Actions auto-publishes to `docs.autonomoustech.ca/audits/<slug>-revenue-audit-YYYY-MM-DD/`.

If repo bloat is a concern, drop raw Lighthouse JSONs (keep SUMMARY.md) and raw firecrawl HTML (keep markdown). Sene drop saved 19MB → 752KB.

## Firecrawl credit budget

- α1 Crawler: ~12-15 credits (1 map + 11-14 scrapes)
- α2 Probe: 0 (curl only)
- α3 PageSpeed: 0 (Google PSI free tier)
- β LLM Answer-Fit: ~10 credits (8-10 search probes)
- γ SERP Probe: ~3-5 credits

Total: ~25-30 credits per audit. Sene used ~30 against a 500-credit cycle.

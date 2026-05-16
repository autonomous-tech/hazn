---
name: module-1-ai-discovery
description: Module 1 of the Shopify Revenue Audit — AI Discovery & Agentic Commerce (30% of composite). Audits ChatGPT Shopping / Perplexity Shop / Google AI Shopping / Sidekick enrollment, llms.txt / agents.txt / ai-plugin.json presence, AI-crawler robots policy across 13 bots, schema.org coverage matrix, product-feed JSON-LD (GTIN/MPN/brand), checkout-via-agent signals, and LLM answer-fit testing. Invoked by the `shopify-revenue-audit` orchestrator during Wave 2 or directly via `/shopify-revenue-audit:rerun-module 1`.
---

# Module 1 — AI Discovery & Agentic Commerce

## When to use
- Invoked by the `shopify-revenue-audit` orchestrator during Wave 2 (β team lead).
- Invoked directly via `/shopify-revenue-audit:rerun-module <audit-dir> 1` after a client fix.
- NOT for standalone use — always operates against a Wave 1 recon snapshot.

## Scope

**Weight in composite:** 30% (heaviest module — this is the novel content most prospects miss).

**Covers:**
- Agentic commerce enrollment signals (Shopify Sidekick, Shop Pay Catalyst, Apple Pay, Shopify Agent Checkout, ChatGPT Shopping, Perplexity Shop, Google AI Shopping)
- AI-discovery layer files: `llms.txt`, `llms-full.txt`, `agents.txt`, `.well-known/ai-plugin.json`, `openai.json`, `mcp.json`
- AI-crawler robots policy across 13 named bots
- Schema.org coverage matrix (templates × schema types)
- Product feed quality fields in `products.json` (GTIN/MPN/brand/condition)
- LLM answer-fit testing against 8-10 target queries from `scope.md`

**Does NOT cover:** Classical SEO sitemap hygiene (→ Module 2), conversion UX on PDPs (→ Module 3), platform/theme/MarTech detection (→ Module 4).

## Inputs (from Wave 1)
Read these before scoring:
- `projects/<SLUG>/diagnostics/scope.md` — business context + 8-10 target LLM queries
- `projects/<SLUG>/diagnostics/infra-probe.json` — α2 output (AI-layer file presence, robots.txt policy, products.json field coverage)
- `projects/<SLUG>/diagnostics/crawl/pdp-{1,2,3}.html` — raw HTML for JSON-LD parsing

## Audit criteria (3-part sub-rubric)

### A. Agentic Commerce Readiness (40% of module score)

- `/llms.txt` present? `/llms-full.txt`? `/agents.txt`? `/.well-known/ai-plugin.json`? `/.well-known/openai.json`? `/.well-known/mcp.json`?
- AI-crawler robots policy — for each of these 13 bots, classify as allowed / disallowed / not_mentioned:
  GPTBot, ChatGPT-User, OAI-SearchBot, Claude-Web, ClaudeBot, PerplexityBot, Perplexity-User, Google-Extended, Applebot-Extended, Amazonbot, cohere-ai, Bytespider, CCBot
- Product feed quality in `products.json`: GTIN, MPN, brand, condition presence rate across 3 sampled products
- Checkout-via-agent signals — Shop Pay Catalyst, Apple Pay, Shopify Agent Checkout
- Shopify Sidekick / chatbot detection in PDP HTML
- Shopify-platform-level robots policy comments (e.g., "no buy-for-me agents")

### B. Schema.org Coverage Matrix (35% of module score)

Parse `<script type="application/ld+json">` in PDP / collection / home HTML.

Build matrix: **Templates × Schema types**
- Templates: Home, Collection, PDP-1, PDP-2, PDP-3, FAQ, Blog
- Schemas: Product, Offer, AggregateRating, Review, FAQPage, BreadcrumbList, Organization, WebSite, SearchAction

For Product schema, flag presence of: `gtin13`/`gtin`/`mpn`/`brand`/`aggregateRating`.
For Offer: `priceValidUntil`, `availability`, `shippingDetails`.

### C. LLM Answer-Fit Testing (25% of module score)

Use `firecrawl search` for each of 8-10 target queries from `scope.md`. For each:
- Does `<DOMAIN>` appear?
- Rank position
- Competitor winners

Flag uncontested blue-ocean opportunities (queries where no apparel / category competitors appear in top 10).

## Scoring rubric (0-100)

Weight the three sub-scores as above (40% / 35% / 25%) and compute a single module score 0-100.

Typical floor signals:
- Score < 30: no AI-layer files, mostly-silent robots policy, missing GTIN/MPN, no AggregateRating on PDPs, 0 wins on LLM answer-fit
- Score 30-50: partial schema coverage, some bots allowed, sparse feed fields
- Score 50-70: schema mostly complete, llms.txt present, feed fields good, some LLM wins
- Score 70+: full agentic-commerce stack enrolled, every bot named in robots, schema matrix dense, LLM wins on multiple high-intent queries

## Outputs

Write to `projects/<SLUG>/diagnostics/module1/`:
- `module1-ai-discovery.md` — section draft + score + top 3 findings, each tagged `FINDING-XXX` with file:line evidence
- `module1/agentic-commerce.json` — rubric A scores
- `module1/schema-matrix.json` — rubric B matrix
- `module1/llm-answer-fit.md` — rubric C probe results

**Evidence requirements:**
- Every claim cites `file:line` from Wave 1 outputs
- Every $ figure traces to `docs/strategy/revenue-leak-calculator.md` category
- No analyst-guessed baselines — pull from infra-probe.json / crawl/ exclusively

## Red-team gates

Module 1 findings must pass:
- `audit-red-team-uplifts` — kills category errors + double-counting (especially overlap with Module 4 MarTech findings)
- `audit-red-team-domain-check` — semantic check on AI-commerce claims (e.g., don't confuse Shopify Sidekick with ChatGPT Shopping enrollment)

If RED, rebuild this module's section and re-run the failing red team before the composite score is final.

## Related skills
- `shopify-revenue-audit` — orchestrator
- `audit-red-team-uplifts`, `audit-red-team-domain-check` — mandatory gates
- See `../shopify-revenue-audit/references/agent-teams-playbook.md` § Wave 2 β for the full agent prompt

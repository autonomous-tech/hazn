# Shopify CRO Benchmarks — Reference

Working file for the `revenue-calculator` agent. Every uplift % cited in `REVENUE-PROJECTION.json` should trace to a row here or to a primary source cited inline.

**NOTE:** This file is a living reference. Where a benchmark is asserted in industry chatter but lacks a primary source we can verify, it is marked **TODO: verify**. The red-team agents flag any uplift cited from a TODO row.

## Payment-rail uplifts

| Surface | Uplift range | Source | Year | Sample | Status |
|---|---|---|---|---|---|
| Shop Pay vs. Shopify Checkout | +1.5% to +4% checkout-completion | TODO: verify — Shopify case study citations vary widely | 2023-2024 | TODO | TODO: verify |
| Shop Pay Installments (BNPL) presence | +5% to +15% conversion lift on AOV > $100 | TODO: verify — Affirm + Klarna both publish in this band but methodologies differ | 2024 | TODO | TODO: verify |
| Apple Pay on mobile PDP | +1% to +3% mobile CVR | TODO: verify | TODO | TODO | TODO: verify |
| Shop Pay Catalyst (agent checkout) | Too new to benchmark | — | 2026 | — | EMERGING — flag as opportunity_cost not measured uplift |

## PDP trust signals

| Surface | Uplift range | Source | Year | Sample | Status |
|---|---|---|---|---|---|
| Star rating visible near price | +5% to +12% PDP CVR | TODO: verify — Bazaarvoice and PowerReviews both publish in this range with different methodologies | 2023 | TODO | TODO: verify |
| AggregateRating in JSON-LD (rich snippet in Google) | +10% to +30% organic CTR on PDP pages | TODO: verify — Search Engine Journal cites Google internal study, primary not public | 2022 | TODO | TODO: verify |
| Size guide present on apparel PDP | -10% to -25% returns | TODO: verify — Loop Returns publishes anecdotal data | 2024 | TODO | TODO: verify |
| Mobile sticky add-to-cart | +5% to +15% mobile CVR | TODO: verify — common Shopify CRO claim, primary source needed | 2023 | TODO | TODO: verify |
| Free-shipping threshold messaging | +5% to +10% AOV | TODO: verify | TODO | TODO | TODO: verify |

## Site-search & discovery

| Surface | Uplift range | Source | Year | Sample | Status |
|---|---|---|---|---|---|
| Algolia / Searchanise vs. native Shopify search (catalog > 500 SKUs) | +3% to +8% CVR for sessions that use search | TODO: verify — Algolia case studies cite this band | 2023 | TODO | TODO: verify |
| Predictive search w/ thumbnails | +10% to +20% search-using-session CVR | TODO: verify | TODO | TODO | TODO: verify |

## AI discovery / agentic commerce

| Surface | Uplift range | Source | Year | Sample | Status |
|---|---|---|---|---|---|
| llms.txt + agents.txt present | Unmeasured — opportunity_cost category | Emerging standard, no controlled studies yet | 2025-2026 | — | EMERGING |
| AI Overview citation (Google SGE) for a brand-relevant query | +5% to +25% incremental organic clicks for that query | TODO: verify — Google has not published controlled data; SEO vendors estimate | 2024-2025 | TODO | TODO: verify |
| ChatGPT Shopping inclusion via feed | Unmeasured at industry scale | — | 2025 | — | EMERGING |

## CWV (Core Web Vitals)

| Metric improvement | Uplift range | Source | Year | Sample | Status |
|---|---|---|---|---|---|
| LCP from 4s+ to <2.5s | +5% to +10% CVR | Google web.dev case studies (Vodafone, Renault) | 2020-2021 | Multiple brands | VERIFIED — primary source on web.dev |
| INP < 200ms | TODO: verify | TODO | TODO | TODO | TODO: verify |
| CLS < 0.1 from > 0.25 | +1% to +5% CVR | Google internal study | 2021 | TODO | TODO: verify |

## Email & SMS

| Surface | Uplift range | Source | Year | Sample | Status |
|---|---|---|---|---|---|
| Klaviyo abandoned-cart flow (3-email) | 5% to 15% recovered carts of those who reach the flow | Klaviyo benchmarks 2024 | 2024 | 100K+ stores | VERIFIED |
| Welcome flow w/ first-purchase discount | 15% to 30% first-time CVR for subscribers | Klaviyo benchmarks 2024 | 2024 | 100K+ stores | VERIFIED |
| SMS (Postscript/Attentive) on top of email | +5% to +10% incremental retention revenue | TODO: verify | TODO | TODO | TODO: verify |

## Catalog hygiene

| Surface | Uplift range | Source | Year | Sample | Status |
|---|---|---|---|---|---|
| Collection sprawl consolidation (50% reduction in active collections) | +10% to +20% organic clicks to surviving collections | Internal Autonomous estimate from Sene + Brixton audits | 2026 | n=2 | LOW CONFIDENCE — internal only, do not cite as external benchmark |
| Sibling-URL canonical fix (jeans-mens, jeans-men, mens-jeans all → one canonical) | +5% to +15% organic clicks on the surviving URL | TODO: verify — common SEO claim | TODO | TODO | TODO: verify |

## How to use this file

1. When `revenue-calculator` cites an uplift, it MUST cite the row here (or attach a primary source inline).
2. Rows marked **TODO: verify** are fair to use **only with confidence LOW** and the audit must call out the LOW-confidence caveat in `REVENUE-PROJECTION.json`.
3. Rows marked **EMERGING** are `opportunity_cost` category — never claim a quantified uplift, only frame as "captured value when the surface ships."
4. Rows marked **VERIFIED** are safe to cite with HIGH/MEDIUM confidence.
5. The red-team B (uplifts) agent grep-checks every projection against this file.

## TODO list for future versions

- Verify Shop Pay uplift band against a primary Shopify case study URL
- Verify Bazaarvoice / PowerReviews star-rating uplift band — pull from a published study, not chatter
- Verify size-guide returns reduction — Loop Returns has data but methodology is unclear
- Build out the AI-Overview citation band when Google publishes controlled data (probably never — keep marked as estimate)
- Replace internal-only catalog hygiene estimates with cross-audit n>5 sample

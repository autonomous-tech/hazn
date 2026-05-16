---
name: module-3-conversion
description: Module 3 of the Shopify Revenue Audit — Conversion Experience (30% of composite). Audits homepage + 2 collection pages + 3 hero PDP teardowns (mid-price, highest-AOV, SEO canary) + cart + copy/offer + B2B trust patterns for premium tier. Widest module by surface area. Invoked by the `shopify-revenue-audit` orchestrator during Wave 2 or directly via `/shopify-revenue-audit:rerun-module 3`.
---

# Module 3 — Conversion Experience

## When to use
- Invoked by the `shopify-revenue-audit` orchestrator during Wave 2 (δ team lead).
- Invoked directly via `/shopify-revenue-audit:rerun-module <audit-dir> 3` after a fix.
- NOT for standalone use — operates against Wave 1 recon.

## Scope

**Weight in composite:** 30% (tied with Module 1 for heaviest, and the widest by page count — 6+ pages teardown).

**Covers:**
- Homepage hero + social proof + nav UX + mobile layout
- 2 collection pages (filter quality, per-tile review counts, made-to-order badges)
- 3 hero PDP teardowns: mid-price representative, highest-AOV, SEO-fragmentation canary
- Cart (shipping threshold, trust badges, upsell, save-for-later)
- Copy / offer (value prop, guarantee, intl messaging, offer stack)
- B2B trust patterns for the premium-AOV tier (case studies, founder story, process transparency, risk-reversal, comparison frame)

**Does NOT cover:** AI-discovery / schema (→ Module 1), SEO catalog hygiene (→ Module 2), platform / MarTech detection (→ Module 4). Checkout is light-touch here (most behavior is locked by Shopify) — deep checkout extensions live in Module 4.

## Inputs (from Wave 1)
- `projects/<SLUG>/diagnostics/scope.md` — business context, pre-audit hypotheses
- `projects/<SLUG>/diagnostics/pagespeed/SUMMARY.md` — CWV implications
- `projects/<SLUG>/diagnostics/crawl/home.{md,html}`
- `projects/<SLUG>/diagnostics/crawl/collection-*.md` (2 representative collections)
- `projects/<SLUG>/diagnostics/crawl/cart.md`
- `projects/<SLUG>/diagnostics/crawl/pdp-{1,2,3}.{md,html}` — the 3 hero PDPs

Cross-reference (when present):
- `conversioniq` skill — general CRO rubric
- `ux-ui` skill — visual hierarchy rubric
- `b2b-ux-reference` skill — premium-tier trust patterns (mandatory for highest-AOV PDP)

> **Reference files restored (2026-05-16):** The granular checklist files from the deleted `shopify-cro-audit` skill have been restored to `references/` in this module. See the References section at the bottom of this file.

## Audit criteria

### Per hero PDP (run for all 3)

For each of PDP-1 (mid-price), PDP-2 (highest-AOV), PDP-3 (SEO canary), check:

- **Above-fold structure:** hero image, title, price, ★ rating / review count, primary CTA
- **★ rating visibility near price** — commonly missing; verify presence and prominence
- **Fit quiz / configurator prominence** — is it gated behind a modal, or surfaced?
- **Urgency / scarcity signals** — present, honest, calibrated? (Honest = real inventory, not fake countdown)
- **Mobile layout** — does the CTA stay above fold? Image gallery swipe-friendly?
- **Trust signals near CTA** — guarantee, shipping ETA, returns policy
- **Upsell / cross-sell** — relevant, not pushy
- **Review section quality** — count, recency, photo reviews, response from brand
- **Production / lead-time framing** — especially for premium/custom

### Homepage
- Hero clarity (1-sentence value prop visible above fold?)
- Social proof above fold (logos, press, review aggregate)
- Navigation UX — does catalog scale matter? Mega-menu? Faceted?
- Mobile layout — what's the second visible element?

### Collections (2 pages)
- Filter quality — do filters use real product attributes or sloppy tags?
- Per-tile review counts visible?
- Made-to-order / lead-time / B2B badges where relevant
- Empty-state handling

### Cart
- Shipping threshold messaging (progress bar to free shipping?)
- Trust badges (security, returns)
- Upsell slot — non-spammy, relevant
- Save-for-later or wishlist persistence

### Copy / offer
- Value prop clarity (the one-sentence test)
- Guarantee framing — what's the explicit promise?
- International messaging — currency, shipping ETA, duties handling
- Offer stack consolidation — are there 5 competing promo banners?

### Premium tier (highest-AOV PDP only)
Apply `b2b-ux-reference` rubric:
- Case studies / named-customer proof
- Founder story / brand origin
- Process transparency (how it's made, where, lead time)
- Risk reversal (return policy, fit guarantee, satisfaction promise)
- Comparison frame (us vs the alternative — competitor or DIY)

## Scoring rubric (0-100)

Weighted:
- Homepage: 15%
- Collections (avg of 2): 15%
- PDP-1 (mid-price): 15%
- PDP-2 (highest-AOV): 15%
- PDP-3 (SEO canary): 10%
- Cart: 10%
- Copy / offer: 15%
- B2B trust (premium tier overlay): 5%

CWV penalty applied multiplicatively if hero PDP mobile Performance < 50.

Typical floors:
- Score < 40: ratings missing near price, hero unclear, cart no shipping bar, no guarantee, B2B trust absent on premium PDP
- Score 40-60: half the patterns present but inconsistent, mobile experience uneven
- Score 60+: tight conversion stack, premium PDP has full trust frame, CWV passing

## Outputs

Write to `projects/<SLUG>/diagnostics/module3/`:
- `module3-conversion.md` — section draft + score + top 5 findings (`FINDING-XXX` format)
- `module3/homepage-collection.md`
- `module3/cart-copy-offer.md`
- `module3/pdp/1.md` (mid-price teardown)
- `module3/pdp/2.md` (highest-AOV teardown)
- `module3/pdp/3.md` (SEO canary teardown)

**Evidence requirements:**
- Every finding cites `file:line` from crawl HTML / markdown
- Above-fold claims should reference what's visible in a viewport screenshot or top-of-markdown section
- B2B trust claims on the premium PDP must cite specific missing elements from `b2b-ux-reference`

## Red-team gates

Module 3 findings must pass:
- `audit-red-team-uplifts` — CRO uplifts are the most-double-counted category; check for overlap with Module 1 (schema → trust signal) and Module 2 (CWV → conversion friction)
- `audit-red-team-domain-check` — does the proposed fix actually fit the business model? (e.g., don't propose "add free shipping" to a brand whose AOV is $4000 and shipping is already free)

If RED, rebuild this module and re-run the failing red team before composite is final.

## Related skills
- `shopify-revenue-audit` — orchestrator
- `audit-red-team-uplifts`, `audit-red-team-domain-check` — mandatory gates
- `conversioniq`, `ux-ui`, `b2b-ux-reference` — rubric source skills
- See `../shopify-revenue-audit/references/agent-teams-playbook.md` § Wave 2 δ for the full agent prompt

## References

The following files are available at `plugins/shopify-revenue-audit/skills/module-3-conversion/references/`:

| File | Description |
|------|-------------|
| `checklist-homepage.md` | Granular homepage CRO checklist — hero, social proof, nav, mobile layout |
| `checklist-product.md` | PDP-level checklist — above-fold structure, trust signals, reviews, upsell |
| `checklist-cart.md` | Cart experience checklist — shipping threshold, badges, upsell, persistence |
| `market-practices.md` | Regional CRO tactics for Pakistan, MENA, US, and EU — currency, trust norms, duty messaging |
| `app-recommendations.md` | Shopify app-to-issue mapping — recommended apps keyed to specific CRO problem types |

> `cdp-schema.md` (RudderStack CDP event schema) was placed in `module-4-technical/references/` — it is general MarTech/data-collection infrastructure, not CRO-specific.

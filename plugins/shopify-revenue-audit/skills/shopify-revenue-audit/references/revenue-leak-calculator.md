# Revenue Leak Calculator — Methodology

Formal methodology for `revenue-calculator.md` agent. Every $-figure in a Shopify Revenue Audit traces back to this document. If the math here is wrong, the audit is wrong.

## The 8 categories

Every finding lands in exactly one category:

| # | Category | Definition |
|---|---|---|
| 1 | pricing_errors | Mispriced SKUs, mis-applied discounts, currency-conversion errors, B2B price escapes |
| 2 | api_waste | API/app cost without proportional revenue (Algolia on a 200-SKU catalog, Klaviyo on 0 flows) |
| 3 | broken_ux | Surface-level UX defects with measurable conversion impact (inventory bug, missing reviews) |
| 4 | dead_attribution | MarTech installed but not measuring (GTM with no events, Web Pixels black-box) |
| 5 | agency_waste | Paid agency retainer producing low-ROI deliverables |
| 6 | manual_labor | Ops time on tasks that should be automated (manual order routing, manual reviews) |
| 7 | security_risk | Risk-weighted dollar value of unaddressed security/compliance gaps |
| 8 | opportunity_cost | Revenue we **can prove** would have been captured if a missing surface existed (AI Overview citations, blue-ocean LLM queries) |

## Confidence tiers

| Tier | Meaning | Use when |
|---|---|---|
| HIGH | Independent triangulation from 2+ sources, mechanism is observable | API call returns `available:true` while page renders "Unavailable" — visible, dated, reproducible |
| MEDIUM | One source + reasonable mechanism | Missing AggregateRating in schema → benchmark estimate of CTR loss |
| LOW | Best-effort estimate with named caveats | Variant-cap risk on a 500-variant configurator with no observed failure yet |

## The P25-P75 rule

**Never compute min × min × min × min.** That's a P1-P99 Cartesian extreme, not a range. It always reads as preposterous to a CFO.

Instead, for any product `A × B × C × D`:

1. Find each factor's P25 and P75 independently (one factor at a time, holding others at P50).
2. Sum the **squared deviations** from P50 in log-space.
3. Recover P25 and P75 of the product from that log-space band.

In practice: compute the P50 directly, then bound it with the largest single-factor uncertainty rounded to a 1.5x-2.5x band.

**Rule of thumb:** P75 should not exceed 4× P25. Wider means the inputs are guessed.

## Haircuts

Applied in order, multiplicatively, to the **sum** of correlated findings (NOT each finding individually):

### 40% cluster overlap haircut

Findings that share a root cause double-count revenue if summed naively. The "trust cluster" (missing reviews + missing trust badges + weak guarantee) overlaps. The "AI surface cluster" (no llms.txt + no AggregateRating + no AI Overview citation) overlaps.

After clustering, multiply the cluster sum by **0.60**.

### 30% execution haircut

Even with the right diagnosis, deployment friction (theme migration, app-conflict resolution, QA cycle) eats some of the projected gain.

After cluster haircut, multiply by **0.70**.

### Combined effect

`net = gross × 0.60 × 0.70 = gross × 0.42`

A finding cluster that projects $1.0M gross becomes $420K net. This is the number that goes on the deliverable.

## Ramp model

Even with a clean v2 deployment, conversions don't snap to steady state on day 1.

| Months | Multiplier on steady-state |
|---|---|
| 1-3 | 0.20 |
| 4-6 | 0.60 |
| 7-12 | 1.00 |

**Year 1 effective:** approximately 0.60 × steady-state annual. This is the number that goes on the 1-pager hero.

**Steady state:** the year-2 number, what the store should be doing in perpetuity once Quick Wins are deployed and ramped.

## Triangulated baseline

**Never accept** an analyst-guessed `sessions × CVR × AOV` as the DTC revenue baseline. The numbers most have access to:

- **ZoomInfo** — public company estimates, often stale
- **SimilarWeb** — traffic estimates, reasonable for monthly visitor counts
- **Glossy / Modern Retail / Retail Brew** — quoted founder numbers in press
- **Founder podcasts** — Shopify Masters, How I Built This, etc. — for AOV and CVR ranges
- **Review-volume back-solve** — `(review_count / typical_review_rate) × AOV × time_window`

A baseline is **triangulated** when 3 of these 5 agree within ±20%. Anything less is a single-source guess and must be flagged with confidence LOW.

## Benchmark integrity

Every uplift % cited in a $-figure must trace to:

- **Source** — named publisher, study URL, or proprietary internal dataset
- **Year** — when the data was published
- **Sample** — sample size or scope (e.g., "73 DTC apparel stores, 2024")

**Anti-pattern:** "Baymard premium apparel CVR is X%." Baymard publishes UX scores, NOT CVR. This is a hallucinated benchmark and fails red-team B.

## v1 vs v2 versioning

- **v1** — gross figures, haircuts documented but NOT applied. Goes to red-team.
- **v2** — haircuts applied, fabricated benchmarks removed, ranges tightened. Goes to deliverable.

Any audit that ships v1 to a client is broken. The HTML deliverable MUST cite v2 or note the rebuild explicitly in a Methodology Update callout.

## Quick reference: Sene case

- v1 projection: $11M/year (failed red-team — fabricated Baymard CVR benchmark, 12x range from min×min×min)
- v2 rebuild: $1.0M-$2.5M/yr at P50
- 7-file cascade fix when client clarified F5 (custom-fit vs standard-size domain error)
- Result: shipped composite 42/100, recovered the audit's credibility

This is the canonical example of why every projection runs through all 4 red-teams.

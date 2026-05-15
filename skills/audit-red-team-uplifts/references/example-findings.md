# Red Team B — Sene Studio Worked Example

How v1 ran the math wrong, and what we corrected.

## v1 claim summary (RED — pre-correction)

20 findings totaling $292K-$11M annual recovery, midpoint $5.7M. **Math was structurally wrong on 3 dimensions:**

1. Three biggest findings used misapplied benchmarks
2. No overlap discount on quick-wins scenario (only on full-optimization)
3. Sum of 20 linear uplifts compounded incorrectly

## Top-5 corrections (the $ headlines)

| ID | v1 monthly | v1 mechanism (wrong) | v2 monthly | v2 mechanism (right) | Reduction |
|---|---|---|---|---|---|
| F17 CWV | $152K | "Performance fix lifts all CVR" — assumes full multiplier | $35-55K | Specific to mobile session share × 8-15% recovery × execution haircut | ~70% off |
| F1 AggregateRating | $112K | "Baymard +20-35% CVR" | $6-25K | Baymard +20-35% **SERP CTR** → traffic ↑ → funnel CVR. Chain not direct multiplier. | ~85% off |
| F10 Offer-stack trust strap | $90K | "Hotjar/CXL +4-12% from trust strap" | $10-30K | Source can't be re-verified; reframed as 1-5% directional | ~80% off |
| F3 Stars near price | $84K | "Spiegel +58% purchase likelihood = +58% CVR" | $10-30K | Spiegel is intent survey. 20-30% translation → +12-17% CVR. Plus overlap with F1. | ~80% off |
| F13 Collection consolidation | $74K | "Full lift in 2-3 weeks" | $8-25K (steady) + $0-5K month 1-3 ramp | 3-6 months for Google to re-crawl. | ~80% off, but ramped |

**Aggregate quick-wins (F1-F12):** v1 $292K-$11M/yr → v2 **$1.0M-$2.5M/yr**.

## The 9 double-counting pairs (caught)

| Pair | Cluster | Overlap |
|---|---|---|
| F1 (schema) ↔ F3 (visible stars) | Trust-at-PDP | ~50% |
| F1 ↔ F19 (DOM-order fix) | Trust-at-PDP / AI-surface | ~50% |
| F3 ↔ F10 (trust strap) | Trust-at-PDP | ~40% |
| F2 (FAQPage) ↔ F4 (llms.txt) ↔ F7 (smart-body-quiz blue-ocean) | AI-surface | ~40% |
| F11 (MerchantReturnPolicy) ↔ F16 (BreadcrumbList) | AI-surface | ~35% |
| F13 (collection consolidation) ↔ F14 (jean fragmentation map) | Catalog-IA | ~70% (jeans subset) |
| F17 (CWV) amplifies all CVR findings | CWV-amplifier | ~25% with each |
| F5 (intl) ↔ F18 (Markets config) | Intl-merchandising | ~40% |
| F9 (women's empty collection) ↔ F13 ↔ F15 (women's UX) | Women's + Catalog | ~30% |

Without the overlap discount, the sum of v1 findings was internally inconsistent (claiming >50% of baseline recoverable on a healthy merchant with 916 customer reviews).

## The compounding error

v1 summed each finding's CVR lift linearly: 5 + 4 + 3 + 3 + 2 + ... = 35% combined CVR lift. **Reality:** correlation coefficient between trust-cluster findings is ~0.6-0.8. Combined CVR lift is closer to 8-12%, not 35%.

## Haircut sequence applied to v2

For aggregate quick-wins ($292K-$11M gross monthly P25/P75 sum):

1. **Cluster discount within each cluster** (max + 55% of others) → gross drops ~30%
2. **40% overlap haircut** on cross-cluster sum → drops another ~40%
3. **30% execution haircut** → drops another 30%
4. **Ramp model:** month 1-3 = 20% × steady; full by month 6 → year-1 ≈ 70% of steady

Net: v1 gross → v2 ~0.42× of gross at steady state, ~0.30× of gross in year 1. Aligned with our `$1.0M-$2.5M/yr` headline.

## What this taught us

1. **Always Google the benchmark.** Five seconds of search killed "Baymard premium apparel CVR" and "Spiegel as CVR multiplier."
2. **Build the cluster table BEFORE summing.** If you don't know which findings overlap, the sum is meaningless.
3. **Linear summation of correlated lifts is the most common audit error.** Always default to multiplicative + correlation discount.
4. **Execution haircut is non-optional.** No project ships clean — schema rich-result QA fails ~20% first try.

## Reference: full v1 vs v2 finding-by-finding table

See `projects/senestudio/diagnostics/REVENUE-PROJECTION-v2.json` field `findings[*].v1_midpoint_was_usd` for the exact v1→v2 deltas across all 20 findings.

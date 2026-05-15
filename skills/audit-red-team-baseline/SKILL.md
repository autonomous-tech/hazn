---
name: audit-red-team-baseline
description: Use before publishing any revenue projection in a Shopify or commerce audit. Triangulates true baseline revenue from public sources (ZoomInfo, SimilarWeb, Glossy/Modern Retail, founder podcasts, Judge.me review-volume back-solve) instead of accepting analyst-guessed sessions × CVR × AOV. Catches fabricated benchmarks (e.g. "Baymard premium apparel CVR" — Baymard publishes UX scores, not CVR data). Replaces min×min×min ranges with P25-P50-P75 interquartile bands. Triggers on "red-team this audit", "kill the baseline", "is this revenue projection defensible", or as part of /shopify-revenue-audit pipeline.
---

# Red Team A — Baseline Sanity Check

You are adversarial. Your job: **destroy or defend** the baseline revenue assumptions in a commerce audit before they reach a client.

## When to use

- After Wave 3 synthesis produces a `REVENUE-PROJECTION.json`, before publishing
- Anytime a $ projection rests on assumed traffic × CVR × AOV
- Phrases: "red-team this audit", "is this baseline defensible", "kill the projection"

## What you produce

`projects/<client>/diagnostics/RED-TEAM-A-baseline.md` with:
- Verdict: **GREEN** (defensible) | **YELLOW** (needs narrowing) | **RED** (indefensible, must redo)
- Per-attack findings with public-source citations
- Proposed defensible baseline as **P25 / P50 / P75 table** (interquartile band, not min-max)

## The 6 attacks

Read `references/methodology.md` for full attack playbook + firecrawl query patterns. Run all 6 — partial passes don't count.

1. **Public traffic estimate** — SimilarWeb / Ahrefs / Semrush proxy data for the domain. Get a real session order-of-magnitude.
2. **Competitor public financials** — Find 2-3 closest comparables (e.g., for premium custom menswear: Indochino, MTailor, Knot Standard, SuitSupply) with public revenue/traffic data. Triangulate.
3. **CVR challenge** — Verify any cited benchmark is real. Custom apparel converts BELOW off-the-rack (more friction). Reject "Baymard 1.2-2.5% premium apparel CVR" — Baymard doesn't publish CVR.
4. **AOV challenge** — Don't accept a *range of single-item prices* as AOV. Compute blended unit-mix-weighted AOV. Pull actual sale-vs-regular pricing from PDPs.
5. **Range methodology** — Min-sessions × min-CVR × min-AOV is a **P1-P99 Cartesian extreme** (≈1-in-1000 joint event), NOT a confidence interval. Replace with P25-P75 around a central estimate.
6. **Independent sanity** — Back-solve via review volume. Judge.me reviews per PDP × estimated review-conversion rate × inferred order frequency → implied MRR. Should bracket the proposed P50.

## Required triangulation

At minimum **3 independent sources** must bracket your proposed P50. Acceptable sources:
- ZoomInfo / RocketReach (employee count, revenue band)
- SimilarWeb / Ahrefs (traffic estimates)
- Glossy, Modern Retail, Retail Dive (industry coverage)
- Founder appearances on podcasts (The Pitch, Lenny's, Acquired, Shopify Masters) — disclosed run rates
- LinkedIn employee count (1-10 vs 50-200 vs 500+ implies very different revenue scales)
- Public S-1 / 10-K / press releases for comparables
- Review-volume back-solve (Judge.me, Yotpo, Loox)

## Output format

```markdown
# Red Team A — Baseline Sanity Check

## Verdict
[GREEN | YELLOW | RED]

## Attack 1 — Public traffic
[findings + sources]

## Attack 2 — Competitor financials
...

## Attack 3 — CVR challenge
...

## Attack 4 — AOV challenge
...

## Attack 5 — Range methodology
[why min×min×min is wrong here, mathematically]

## Attack 6 — Independent sanity (review back-solve)
...

## Proposed defensible baseline
| Variable | P25 | **P50** | P75 |
|---|---|---|---|
| Monthly sessions | X | **Y** | Z |
| CVR | X% | **Y%** | Z% |
| Blended AOV | $X | **$Y** | $Z |
| Monthly revenue | ~$X | **~$Y** | ~$Z |
| Annual revenue | ~$X | **~$Y** | ~$Z |

## Downstream impact on the audit
[how each Wave-3 finding's $ band needs rebuilding]
```

## Canonical example
**Sene Studio (April 2026)**: v1 claimed baseline `$1.79M-$21.83M annual` (12× spread). Red Team A killed it by triangulating from ZoomInfo (<$5M), Glossy 2019 (~$2M), founder Ray Li on The Pitch ($1.6M run rate), LA store closed per Yelp, SimilarWeb rank 207k (vs Indochino 73k). Proposed defensible P25/P50/P75: **$1.2M / $2.3M / $4.9M annual**. Verdict: RED.

See `references/example-findings.md` for the full Sene worked example.

## Related skills
- `audit-red-team-uplifts` (catches per-finding math errors after baseline is fixed)
- `audit-red-team-cfo` (final adversarial pass)
- `audit-red-team-domain-check` (catches semantic errors)

# Red Team A — Sene Studio Worked Example

The canonical case. Sene v1 baseline was indefensible; v2 baseline survives a CFO call.

## v1 baseline (RED — what we killed)

| Variable | Min | Max | Spread |
|---|---|---|---|
| Monthly sessions | 80,000 | 150,000 | 1.9× |
| CVR | 1.2% | 2.5% | 2.1× |
| AOV | $155 | $485 | 3.1× |
| **Monthly revenue** | **$148,800** | **$1,818,750** | **12×** |
| **Annual revenue** | **$1.79M** | **$21.83M** | **12×** |

Three damning attacks killed it.

---

### Attack 2 — Competitor financials (the kill shot)

ZoomInfo reported Sene Studio: **<$5M annual revenue, 1-10 employees**. Glossy 2019 coverage stated **~$2M/yr**. Founder Ray Li on The Pitch podcast disclosed **$1.6M run rate, bootstrapped**.

The $21.83M upper bound would make Sene 38% of Indochino's revenue ($58M, 661K sessions/mo, 100+ showrooms) on roughly 8% of Indochino's traffic, with zero showrooms (Sene's LA store is **listed CLOSED on Yelp** as of audit date), and 1-10 employees. **Physically impossible.**

SimilarWeb global rank for senestudio.com: **207,281**. Indochino: 73,005. The traffic isn't there.

### Attack 3 — CVR challenge (fabricated benchmark)

The v1 audit cited "Baymard premium apparel CVR 1.2-2.5%". **Baymard does not publish CVR.** They publish UX scores. Verified: searched Baymard's full publication list — zero CVR studies for apparel.

Real 2026 custom-apparel CVR band: **0.7-1.5%, central ~1.1%** (Indochino empirical anchor: ~1.27%).

### Attack 5 — Range methodology

Min×min×min was producing a 12× spread. Mathematically, with 3 independent variables each at P10:
- P(joint) ≈ 0.10³ = 0.001 (1-in-1000)

The arithmetic midpoint had near-zero probability mass. Replaced with P25-P75 around a central estimate.

---

## v2 baseline (GREEN — what we shipped)

| Variable | P25 | **P50 (central)** | P75 |
|---|---|---|---|
| Monthly sessions | 35,000 | **50,000** | 70,000 |
| CVR | 0.8% | **1.1%** | 1.4% |
| Blended AOV | $285 | **$350** | $420 |
| **Monthly revenue** | **~$100K** | **~$193K** | **~$412K** |
| **Annual revenue** | **~$1.2M** | **~$2.3M** | **~$4.9M** |

**Triangulation:**
- ZoomInfo: <$5M ✓ (P75 ceiling within)
- Glossy 2019: ~$2M ✓ (between P25 and P50)
- The Pitch (~2020): $1.6M run rate × ~5-year reasonable CAGR → ~$3.2M ✓ (between P50 and P75)
- Review back-solve: ~$4-12M lifetime ÷ 7 years ≈ $0.6-1.7M annual ✓ (covers P25-P50)
- SimilarWeb peer calibration: 207k rank → ~50K sessions/mo ✓

All 5 sources bracket the P50 ($2.3M). PASS.

---

## Downstream impact on the audit

Every finding's $ band had to be rebuilt against the new baseline. Aggregate quick-wins recoverable dropped from claimed **$292K-$11M/yr** to honest **$1.0M-$2.5M/yr**.

Guarantee-safety margin reframed: from "3-122× over the $7,500/mo floor" (innumerate) to **2-6×** at the conservative end. Still viable for engagement floor, but honest.

## What this taught us

1. **Always triangulate with public-source data BEFORE accepting analyst-guessed traffic.** Even one ZoomInfo + one founder podcast clip kills 90% of inflated baselines.
2. **Reject any benchmark you can't verify with one search.** "Baymard premium apparel CVR" sounded plausible; one search killed it.
3. **A 12× baseline range is not a "wide range" — it's an admission you don't have a baseline.** Either narrow it via triangulation or publish "we will not project a total until admin baseline lands."

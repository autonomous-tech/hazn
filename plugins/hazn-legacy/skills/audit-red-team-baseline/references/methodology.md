# Red Team A — Methodology

Full attack playbook. Use after reading SKILL.md.

## The 6 attacks — full execution

### Attack 1: Public traffic estimate

Get an order-of-magnitude monthly session count from public proxies.

**Sources (run in parallel where possible):**
- `firecrawl search "<domain> similarweb"` → SimilarWeb estimate
- `firecrawl search "<domain> traffic ahrefs"` → Ahrefs domain rating + organic traffic
- `firecrawl search "<domain> alexa rank"` (legacy but sometimes still cached)
- Wappalyzer / BuiltWith (tech stack + traffic tier)

**Acceptable error:** ±50% on monthly sessions. You're calibrating order of magnitude (10K vs 100K vs 1M), not pinpoint.

**Red flag:** If the analyst's assumed sessions are >2× what public proxies show, mark RED and propose narrower band.

### Attack 2: Competitor public financials

Find 2-3 closest comparables. For premium custom apparel: Indochino, MTailor, Knot Standard, SuitSupply, Hockerty, Tailor Store, Blacklapel.

Triangulate via:
- **Public S-1 / 10-K** if listed (Indochino was Kingsmen HK / Dadi Concepts)
- **Glossy / Modern Retail / Retail Dive coverage** with disclosed revenue ranges
- **Founder appearances on podcasts** — The Pitch, Lenny's, Acquired, Shopify Masters often disclose run rates
- **PE / VC announcement language** — "Series A $X to scale a $Y ARR business"
- **LinkedIn employee count** as proxy: 1-10 = <$5M; 50-100 = $20-50M; 200+ = $100M+

**Real-world calibration (premium custom menswear, 2026):**
| Brand | Approx revenue | Approx sessions/mo | Implied CVR |
|---|---|---|---|
| Indochino | ~$58M | ~661K | ~1.27% |
| MTailor | ~$15-30M | ~150-250K | ~0.6-1.0% |
| Knot Standard | ~$30-50M | ~80-120K (showroom-heavy) | n/a online-only |

If your audited brand sits much smaller in any of these dimensions than analyst-assumed, narrow.

### Attack 3: CVR challenge

**Most-cited fabricated benchmarks to reject:**
- "Baymard premium apparel CVR 1.2-2.5%" — **Baymard does not publish CVR data.** They publish UX scores and qualitative findings. Reject.
- "Shopify average CVR 3%" — outdated. Real 2024 data: Invesp 2024 apparel CVR median **1.4-1.8%**, premium apparel narrower **1.01-2.20%**.
- "Custom apparel CVR same as off-rack" — wrong. Custom converts BELOW because of fit-quiz friction, measurement step, lead-time anxiety. Real range: **0.6-1.5%**, central ~1.1%.

**Defensible custom-apparel CVR band (2026):**
| Tier | P25 | **P50** | P75 |
|---|---|---|---|
| Custom-fit US apparel | 0.7% | **1.1%** | 1.5% |
| Premium DTC general | 1.0% | **1.5%** | 2.2% |
| Mass DTC fashion | 1.4% | **1.8%** | 2.5% |

**Empirical anchor:** Indochino at $58M ÷ 661K sessions ÷ ~$575 AOV → ~1.27% CVR. Use as central anchor for custom-fit comparables.

### Attack 4: AOV challenge

**The error to catch:** range of single-item prices treated as AOV range. Example: "AOV $155-$485" derived from cheapest-shirt to highest-priced-suit. That's not AOV; that's price spread.

**Correct method:** blended unit-mix-weighted AOV.

```
blended_AOV = Σ (unit_price_i × order_share_i)
            ≈ Σ (sale_price_i × visible_demand_proxy_i)
```

**Visible demand proxies (in order of strength):**
1. Best-Sellers collection if exposed
2. PDP review counts (Judge.me/Yotpo aggregate counts)
3. Homepage feature placement
4. SimilarWeb page-view distribution
5. Social proof claims (e.g., "500K customers" disclosed)

**Red flag:** if analyst used max single-item price as AOV ceiling, recompute. Sene v1 had `$485` as ceiling — actual blended AOV was ~$350 because shirts/jeans/hats outweigh suits in unit mix.

### Attack 5: Range methodology

The mathematical case to make in the report:

> Min × min × min through max × max × max is a **Cartesian extreme** product, not a confidence interval. Three stacked 10th-percentile assumptions = ~0.001 joint probability under independence. The arithmetic mean of a 12-37× span has near-zero probability mass. A defensible range is **P25 to P75 (interquartile band, ~50% probability)** around a stated central estimate.

Replace min-max with:
```
P25 = central × 0.50
P50 = central
P75 = central × 1.75-2.0
```

(Or compute via Monte Carlo joint sample if you have time. Single-paragraph triangulation is usually enough.)

### Attack 6: Independent sanity (review back-solve)

Most direct sanity check: derive implied MRR from review volume.

```
Reviews per PDP × N_PDPs × inverse_review_rate × order_frequency × AOV = implied annual revenue
```

**Defaults for back-solve:**
- Inverse review rate: 1 review per 30-50 orders (varies by post-purchase email setup)
- Order frequency: ~1.0 for first-time, ~1.3 with customer base maturity

**Sene example:**
- 537 reviews on flagship suit, 322 on jeans, 57 on shirt, plus ~50-100 PDPs with smaller volumes
- Total reviews across catalog: ~3,000-5,000
- Implied lifetime orders: 90,000-250,000
- At ~$350 blended AOV: $31M-87M lifetime
- Over ~7 years operation: ~$4-12M annual revenue

That bracket includes the proposed P50 ($2.3M) and P75 ($4.9M). PASS.

## Triangulation rule

**Minimum 3 independent sources must bracket your proposed P50.** Acceptable:
- ZoomInfo / RocketReach revenue tier
- SimilarWeb traffic estimate
- Glossy / Modern Retail coverage
- Founder podcast disclosure
- LinkedIn employee count
- Public competitor financials
- Review-volume back-solve

If only 1-2 sources, mark **YELLOW: needs more triangulation before publish.**

## Common Pitfalls

- **Confusing "monthly visitors" with "monthly sessions"** — visitors are unique users, sessions are visit events; ratio is typically 1.3-1.7×
- **Using top-funnel metrics as bottom-funnel** — homepage sessions ≠ PDP sessions; PDP sessions ≠ checkout-eligible sessions
- **Forgetting paid-vs-organic mix** — organic-only assumptions inflate when 40%+ of traffic is paid
- **Forgetting refund/return rate** — net revenue ≠ gross orders × AOV; apply 8-15% return haircut for apparel

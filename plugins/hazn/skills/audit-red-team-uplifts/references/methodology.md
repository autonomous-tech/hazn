# Red Team B — Methodology

Full audit playbook. Use after reading SKILL.md.

## Common fabricated benchmarks to reject (running list)

| Fabricated claim | Why it fails | Correct framing |
|---|---|---|
| "Baymard premium apparel CVR 1.2-2.5%" | Baymard publishes UX scores, not CVR | Use Invesp 2024 (1.01-2.20% premium DTC band) |
| "Spiegel +58% as CVR multiplier" | Stated-intent survey, not measured behavior | Apply 20-30% intent→behavior translation; real CVR delta ~12-17% |
| "Hotjar trust strap +4-12%" | Source can't be re-verified | Reframe as "directional, typical 1-5% A/B" |
| "Schema rich results +30% conversion" | Confuses SERP CTR (the lift) with on-site CVR | Chain: schema → SERP CTR ↑ → traffic ↑ → funnel CVR; not direct |
| "Klaviyo abandon-cart 30% recovery" | Top-decile case studies cited as median | Real median: 5-15% of cart value |
| "Shopify Markets +40% intl" | Cherry-picked winners; no inventory/currency | Realistic 5-15% with full localization investment |
| "CRO experts agree X" | Appeal to authority without source | Demand published source + sample size |

## Verifiable benchmarks (use these instead)

| Benchmark | Source | Year | Notes |
|---|---|---|---|
| SERP CTR for star-rich snippets +20-35% | Baymard 2024 | 2024 | CTR, NOT CVR. Apply chain. |
| Stated purchase likelihood +58% with stars | Spiegel/Northwestern | (Pre-2018) | Apply 20-30% intent→behavior translation |
| Apparel CVR 1.01-2.20% | Invesp / Yaguara | 2024 | Premium subset narrower |
| 1s→5s LCP = +90% mobile bounce | Google PSI / web.dev | 2024 | Solid for CWV findings |
| Klaviyo abandoned-cart median 5-15% recovery | Klaviyo benchmarks | 2024 | Of cart value, not site revenue |
| BOPIS conversion lift 5-10% | Various retail | 2023+ | Specific to physical-store overlap |
| Subscription CVR uplift 15-25% | Recharge / Bold | 2024 | Subscription-only products |
| Mobile traffic share 60-75% (apparel) | SimilarWeb global | 2024 | Use as planning denominator |

## Category errors — the common confusions

### CTR vs CVR
- **CTR (Click-Through Rate)**: SERP impressions → SERP clicks. Schema markup, rich snippets, ad copy affect CTR.
- **CVR (Conversion Rate)**: site sessions → orders. Trust signals, page speed, copy affect CVR.

A schema fix increases CTR. Increased CTR brings more traffic. More traffic × the *site's existing* CVR = more revenue. Treating "+25% CTR" as "+25% CVR" overstates the lift by the dilution factor (i.e., not all increased CTR converts).

### Intent vs behavior
Stated-intent surveys ("would you be more likely to buy if X?") translate to actual behavior at ~20-30%. So "+58% stated intent" ≈ "+12-17% behavior change."

### B2B vs DTC benchmarks
B2B lifts ~3-5× DTC lifts on the same intervention type because order values are higher and consideration is longer. Don't apply B2B SaaS benchmarks (Saastr, Drift) to DTC apparel.

### Old data
Conversion benchmarks degrade. 2018 data is 7+ years stale; 2020 was COVID-distorted. Anchor to **2023+** sources where possible.

## Double-counting cluster inventory

For each audit, build this table:

| Cluster | Typical findings | Overlap % | Notes |
|---|---|---|---|
| Trust-at-PDP | AggregateRating schema · Stars near price · Trust strap · Cart trust badges · DOM-order fix | 40-50% | All target the same hesitant-buyer micro-decision |
| AI-surface | llms.txt · Schema coverage · FAQPage · MerchantReturnPolicy · Smart Body Quiz blue-ocean | 35-45% | Same incremental AI-search traffic |
| Catalog-IA | Collection consolidation · Canonical fix · Sitemap hygiene · Internal linking | 30-40% | Same organic ranking surface |
| CWV-amplifier | Performance fix · Lazy-load apps · Image optimization · LCP fix | 20-30% with everything | Multiplies every CVR fix; can't double-count |
| Women's | Empty women's collection · Women's-specific UX · Gendered homepage curation | 30% | Only matters if women's traffic is meaningful share |
| Intl-merchandising | Standard-size ship-to surfacing · Markets config · hreflang · Currency display | 30-40% | Only matters at non-US session share threshold |

## Compounding math

Linear: F1 +5% + F3 +5% = +10% (wrong)
Compound: (1.05 × 1.05) - 1 = +10.25% (right but tiny)
**Real (correlated):** ~6-8% combined if both target the same buyer (correlation coefficient 0.5-0.7)

If you're summing 12 wins each at +1-3%, the real combined CVR lift is probably 8-15%, not 24-36%.

## Recommended haircut sequence

For the additive sum of all quick-win $:

1. **Cluster within each cluster:** find max within a cluster, scale others by `(1 - cluster_overlap)`. So if Trust cluster has F1 $X, F3 $Y, F10 $Z, post-cluster sum = max($X, $Y, $Z) + 0.55 × (sum of others).
2. **Apply cross-cluster overlap discount: 40%** on the cluster-summed total. (Some inter-cluster overlap exists too.)
3. **Apply execution haircut: 30%.** This accounts for QA failures, deploy regressions, gated platform features (LLM enrollment), and client-review watering-down.
4. **Apply ramp model:** month 1-3 = 20% of post-haircut steady state; full ramp by month 6.

Combined: gross × ~0.42 → steady-state monthly recovery. Year-1 recovery ≈ 60-80% of steady-state annualized.

## Output structure

```markdown
| ID | v1 claim | Benchmark verifiable? | Category correct? | Cluster | Haircut needed | Recommended $ |
| F1 | $112K/mo | ❌ Baymard CTR not CVR | ❌ overstated 2-3× | Trust | overlap 45% + execution 30% | $6-25K/mo |
| ... |
```

---
name: audit-red-team-uplifts
description: Use to audit every uplift percentage claim in a revenue projection before publishing. Catches fabricated benchmarks (Baymard doesn't publish CVR; Spiegel +58% is intent not behavior), category errors (SERP CTR ≠ CVR; B2B benchmarks applied to DTC; 2018 data applied to 2026), double-counting across correlated findings (trust-cluster overlap, AI-surface-cluster overlap), missing overlap (40%) and execution (30%) haircuts. Triggers on "red-team this projection", "are the uplifts defensible", "audit the math", or as part of /shopify-revenue-audit pipeline.
---

# Red Team B — Uplift Math Audit

You are adversarial. Your job: **find the math errors** in every uplift claim before they reach a client.

## When to use

- After Wave 3 produces `REVENUE-PROJECTION.json` (and after Red Team A fixes the baseline)
- Anytime a finding cites a "X% lift from <benchmark>"
- Phrases: "red-team the math", "verify the uplifts", "audit the benchmarks"

## What you produce

`projects/<client>/diagnostics/RED-TEAM-B-uplifts.md` with:
- Verdict: **GREEN** | **YELLOW** | **RED**
- Per-finding audit table (uplift / benchmark verifiable / applied correctly / double-count cluster / haircut needed / recommended $)
- Double-counting cluster inventory + suggested overlap %
- Compounding math correction
- Per-headline $ correction recommendations

## The 5-part audit

### 1. Benchmark citation reality
For every "+X% from <benchmark>" claim, verify:
- Is the benchmark real and findable? (If you can't web-search it, treat as fabricated.)
- Is it from a comparable context? (B2B SaaS data ≠ DTC apparel; 2018 data ≠ 2026; small-merchant data ≠ enterprise.)
- Is it applied as the right *type* of metric?

### 2. Traffic-share application
If a finding says "affects 60% of traffic with 8-25% lift":
- Does 60% come from real GA4 data, or a guess?
- Is the 8-25% a CTR delta or a CVR delta? (These multiply ×traffic_share differently — CTR lifts SERP impressions; CVR lifts on-site conversions of existing sessions.)
- Show the math: `baseline × traffic_share × uplift_pct = $`. If the baseline range is 12x wide, every $ inherits that width.

### 3. Category errors (the worst class of error)
Common mis-applications to catch:
- **"Baymard +20-35% from rich snippets"** is **SERP CTR**, not on-site CVR. Chain is: schema → SERP CTR lift → traffic lift → THEN funnel CVR. Skipping the chain overstates ~3×.
- **"Spiegel +58% purchase likelihood"** is a **stated-intent survey**, not measured behavior. Apply 20-30% intent→behavior translation — so the real CVR delta is ~12-17%, not 58%.
- **"Hotjar/CXL trust strap +4-12%"** — verify it's a published study with sample size + controls. If you can't find the source, mark "directional only, do not apply as benchmark."
- **B2B SaaS benchmarks applied to DTC** — flag any.
- **Small-sample case studies as benchmarks** — flag and discount.

### 4. Double-counting across correlated findings
Multiple findings that target the same buyer hesitation or traffic source overlap. Map clusters:
- **Trust-at-PDP cluster**: AggregateRating schema (M1) + visible stars near price (M3) + offer-stack trust strap (M3) + cart-drawer trust badges (M3). Each claims a CVR lift on the same hesitant buyer. Combined effect ≠ sum.
- **AI-surface cluster**: llms.txt + schema.org + FAQPage + AI-crawler policy + product-feed JSON-LD. All claim incremental AI-search traffic. Can't triple-count the same $ opportunity.
- **CWV-amplifier cluster**: Performance fixes amplify every CVR finding. Summing CVR lifts AND a separate CWV lift double-counts.
- **Catalog-IA cluster**: Collection consolidation + canonical fixes + sitemap hygiene. All target the same organic traffic.

For each cluster: estimate overlap % (typically 30-50%) and apply as discount on the cluster sum.

### 5. Missing haircuts
Real-world realization is lower than gross modeled lift because:
- **Schema implementations have bugs** — ~20% don't rich-result-qualify on first deploy
- **Copy changes get watered down** in client review
- **CWV fixes can regress**
- **LLM-enrollment is platform-gated** — ChatGPT Shopping is invite-only for many merchants
- **Apps resist lazy-load** — JS deferral often regresses other features

Apply a **30% execution haircut** on top of the overlap discount. (Combined: gross × 0.60 overlap × 0.70 execution = 0.42 of gross.)

## Output format

```markdown
# Red Team B — Uplift Math Audit

## Verdict
[GREEN | YELLOW | RED]

## Per-finding audit
| ID | Uplift claim | Benchmark real? | Category correct? | Double-count cluster | Haircut needed | Recommended $ |

## Double-counting clusters
- Trust-at-PDP: F1+F3+F10+F19, ~45% overlap → apply 45% discount on cluster sum
- AI-surface: F1+F2+F4+F7+F11, ~40% overlap
- ...

## Compounding math fix
Linear sum is wrong. Correct: 1.05 × 1.05 ≠ 1.10. Combined CVR lifts apply multiplicatively, not additively.

## Top 5 attack
[for each headline finding: is the $ defensible? Honest replacement?]

## Recommended corrections
- Apply X% overlap discount to total quick-wins sum
- Apply 30% execution haircut
- Replace "midpoint = $X annual recovery" with honest $Y range
```

## Canonical example
**Sene Studio v1**: F1 (AggregateRating schema) claimed $112K/mo ($1.34M/yr). Red Team B caught:
- "Baymard +20-35%" is SERP CTR, not CVR (overstated 2-3×)
- F1 + F3 (stars near price) + F10 (offer-stack) overlap ~45% (all trust-at-PDP)
- No execution haircut applied
- Honest range after corrections: **$6-25K/mo ($72-300K/yr)** — 80% off the v1 claim.

Sene v1 had 9 unflagged double-counting pairs; Red Team B forced 30-40% overlap discount.

See `references/example-findings.md` for the full v1→v2 correction table.

## Related skills
- `audit-red-team-baseline` (run BEFORE this — baseline must be fixed first)
- `audit-red-team-cfo` (run AFTER this)
- `audit-red-team-domain-check`

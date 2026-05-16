# Red Team C — Sene Studio Worked Example

How v1's executive verdict would have died on a CFO call, and what we replaced it with.

## v1 Section 2 (RED — what we killed)

> **Revenue-at-risk: $291K–$11M annual**
> **Payback: 1–9 weeks**
> **Effort to unlock: 76 hours**
> Clears the $7,500/mo Calculator guarantee floor by 3-122×.
> Engagement scenarios:
> - Quick Wins: $292K-$11M/yr (midpoint $5.7M)
> - Full Optimization: $569K-$22M/yr (midpoint $11.3M)

## What a CFO would have asked (and we couldn't defend)

**Q1:** "Your baseline says my revenue is $1.79M-$21.83M. My CFO team knows the actual number. If I told you it's $4M, does your projection still hold?"
- The whole projection scales linearly from a 12× baseline range. We had no answer.

**Q2:** "Midpoint $5.7M on a $292K-$11M range. What probability makes the midpoint correct? 2%?"
- We had no joint distribution. The arithmetic mean was convenience.

**Q5:** "12 quick-win uplifts, summed linearly, claim 35% CVR lift. Real-world correlated combination is ~8-12%. What's your correlation discount?"
- We hadn't applied one. The 35% was structural overcounting.

**Q6:** "42/100 SiteHealth — that means 58% of my revenue is leaking?"
- It doesn't, but the report was ambiguous on this.

**Q8:** "Payback 1-9 weeks at what realization rate?"
- The 1-9 was an artifact of the 37× recovery range. At the floor, payback was 5 months. At ceiling, 1 day. Useless.

**Q10:** "'Guarantee cleared by 3-122×' — which is it?"
- Meaningless multiplier theater.

## Our v2 replacement (GREEN — what we shipped)

```markdown
## Section 2 · Dominant Revenue Blocker

# Sene has 916 verified reviews live today. Google sees zero.

Across three flagship PDPs, Sene Studio emits 57, 322, and 537 Judge.me 
reviews — 916 verified customer voices sitting in the DOM. Yet zero of 
those PDPs emit AggregateRating structured data. There is no /llms.txt, 
no /ai-plugin.json, no MCP manifest. The AI-crawler policy is silent on 
all thirteen bots. GTIN coverage across sampled products is 0%.

Translation: Sene is structurally invisible to ChatGPT Shopping, 
Perplexity Shop, Apple Intelligence Shopping, and Google AI Overviews 
during the exact 12-24 month window where AI-discovery is inflating.

---

**WE WILL NOT PUBLISH A TOTAL RECOVERY NUMBER UNTIL ADMIN BASELINE LANDS**

The dominant uncertainty in every recovery dollar is the baseline itself
— your actual GA4 sessions, blended CVR, and AOV. Until that lands, a 
single "total recoverable" figure is a forecast we cannot defend. Instead,
below are the three highest-confidence individual findings, each with 
a P25-P75 interquartile band against a defensible central baseline of 
~$2.3M annual revenue (P25 $1.2M / P75 $4.9M, triangulated from ZoomInfo, 
Glossy 2019, founder-disclosed Pitch-podcast run rate, SimilarWeb peer 
calibration, and Judge.me review-volume back-solve). Ranges tighten to 
point estimates within 48 hours of GA4 read access.

[F17 CWV remediation — $420K-$660K/yr — HIGH]
[F1 AggregateRating schema — $72K-$300K/yr — HIGH]
[F3 Star aggregate near price — $120K-$360K/yr — HIGH]

| Payback (conservative baseline) | 4-6 months at P25, 2-3 months at P50 |
| Guarantee safety | $7,500/mo floor cleared by 2-6× across P25-P75 |
| Effort to unlock (3 leads) | 62 hours: F1 (8h) + F3 (4h) + F17 (50h) |

42/100 SiteHealth is a readiness score for the next 12-24 months of 
AI/agent commerce + conversion fundamentals. NOT a "share of revenue 
leaking." Recoverable unrealized revenue is sized per-finding above.
```

## What changed and why

| v1 claim | Why it failed | v2 replacement |
|---|---|---|
| "$291K-$11M annual" | 37× span, midpoint 2% probability | Refusal to publish total + 3 named findings with P25-P75 bands |
| "Payback 1-9 weeks" | Denominator artifact | "4-6 months at P25, 2-3 months at P50" |
| "Cleared by 3-122×" | Meaningless multiplier theater | "Cleared by 2-6×" (single defensible range) |
| "Midpoint $5.7M" | Arithmetic mean of broken range | Dropped — three individual findings instead |
| Implicit "42/100 = 58% leaking" | Score interpretation conflation | Explicit "readiness score, NOT leak share" |

## What this taught us

1. **The CFO attack catches different errors than baseline/uplift checks.** Math could be perfect and CFO would still call out "midpoint of a wide range is meaningless."
2. **Replace ranges-of-ranges with single-figure findings + ranges-per-finding.** Three findings each with their own band is more credible than one aggregated range.
3. **Always state the readiness-score interpretation explicitly.** X/100 is intuitively read as a percentage — kill the ambiguity.
4. **Pre-empt the question "what does 42/100 mean for my P&L".** Answer up front: it's not P&L; it's readiness.

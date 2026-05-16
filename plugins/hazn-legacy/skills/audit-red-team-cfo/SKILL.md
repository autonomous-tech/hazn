---
name: audit-red-team-cfo
description: Use before sending an audit to a client. Adversarially attacks the revenue projection as if the client's CFO is reading it — surfaces the uncomfortable financial-leadership questions an analyst would ask. Validates statistical sanity (min×min×min Cartesian extremes, midpoint probability mass, payback-period coherence, X/100 score interpretation). Rewrites executive verdict to what survives a real CFO call. Triggers on "red-team this audit for credibility", "cfo attack", "would this survive a finance review", or as part of /shopify-revenue-audit pipeline.
---

# Red Team C — CFO Attack + Statistical Validity

You are the client's CFO. You have ten minutes before a board meeting. You opened this audit. **What's the first uncomfortable question you ask?**

## When to use

- Final pass before the audit ships to client
- After Red Teams A (baseline) and B (uplifts) have run
- Phrases: "would this survive a CFO review", "credibility check", "cfo attack the projection"

## What you produce

`projects/<client>/diagnostics/RED-TEAM-C-cfo.md` with:
- Verdict: **GREEN** | **YELLOW** | **RED**
- Top 3 statistical flaws with mathematical justification
- 10 uncomfortable CFO questions with best defense for each
- Proposed replacement language for the audit's executive verdict

## Two-part attack

### Part 1 — Statistical validity

#### Range construction
Min-sessions × min-CVR × min-AOV → max-of-each is a **P1-P99 Cartesian extreme**, not a confidence interval. Three stacked 10th-percentile assumptions = ~0.1% joint probability. The arithmetic midpoint of a 37× span has near-zero probability mass — citing it as a forecast is innumerate.

**Correct method:** simulate the joint distribution (Monte Carlo, log-space sum) or pick a central estimate and bracket P25-P75 around it.

#### Additive aggregation
Multiple findings target the same buyer / traffic surface. Two issues:
- **Correlation:** trust-at-PDP findings, AI-surface findings, CWV-amplified findings overlap. Sum overstates real combined effect.
- **Compounding math:** 1.05 × 1.05 = 1.1025, not 1.10. Small in isolation; meaningful when summing 12-20 wins.
- **Reality check:** if total additive sum > 30% of baseline, you're claiming the site is >30% broken. Established merchants with hundreds of reviews are extraordinary claims requiring extraordinary evidence.

#### Payback claims
"Payback 1-9 weeks" is meaningless when it's a denominator artifact of an over-wide range. At the floor recovery rate, payback is 5-8 *months*; at the ceiling, it's 1 day. The range is not informative. **Drop weekly payback figures unless baseline is point-estimated.**

#### Score interpretation
**X/100 readiness score ≠ X% of revenue leaking.** Don't conflate them. A 42/100 SiteHealth means "42% ready for the next 12-24 months of AI/agent commerce" — NOT "58% of revenue is leaking."

### Part 2 — CFO persona attack

Be the CFO. Not soft. Write the **10 most uncomfortable questions** they'd ask, each with:
- The question (verbatim, as a CFO phrases it)
- What it exposes
- Best defense Autonomous should have ready (or admit no defense)

Examples of the right register:

> *"Your baseline says my revenue is $1.79M-$21.83M. My CFO team knows the actual number. If I told you it's $4M, does your projection still hold?"*
> Exposes: the entire projection scales from a guessed baseline.
> Defense: "We refuse to project a total until admin baseline lands. The three highest-confidence individual findings have P25-P75 bands that hold at any baseline within $1M-$5M."

> *"You say I can recover $5.7M from 76 hours of work. My 2025 revenue was $X. How do you recover $5.7M from a $X business?"*
> Exposes: dollar figures don't pass back-of-envelope sanity check.
> Defense (if numbers are honest): "$5.7M is a P50 midpoint of a wide range; the floor is $300K. The ceiling assumes both quick wins and CWV ramping in-year." (If there's no defense: rewrite the projection.)

> *"Your 'star rating +58% purchase likelihood' citation — that's a stated-intent survey, not measured CVR. Did you apply intent→behavior translation?"*
> Exposes: category error. (No defense; correct it before publishing.)

## Output format

```markdown
# Red Team C — Statistical Validity + CFO Attack

## Verdict
[GREEN | YELLOW | RED]

## Part 1 — Statistical flaws
1. Range construction (min×min×min)
2. Additive aggregation (correlation + compounding)
3. Payback claim coherence
4. Score interpretation (X/100 ≠ leak share)

## Proposed corrections
- Replace min-max with P25-P75 around stated central estimate
- Discount additive sums by X% for correlation
- Drop "payback weeks" until baseline is point-estimated
- Reframe X/100 as "readiness score, not leak share"

## Part 2 — CFO's 10 questions
[10 questions, each: question / what it exposes / best defense]

## The "honest" executive verdict replacement
If the audit's hero / Section 2 "Alarm" would make a CFO laugh, replace with:
- A stated refusal to publish a TOTAL recovery number until admin baseline lands
- The 3 highest-confidence INDIVIDUAL findings with P25-P75 bands
- Guarantee-safety reframed as "even at P25 floor, recovery clears the engagement floor by Nx"
- No "engagement payback in 1-9 weeks" theater

[Full proposed language here.]
```

## Canonical example
**Sene Studio v1** Section 2 originally claimed: "Revenue-at-risk: $291K-$11M annual; payback 1-9 weeks; clears the $7,500/mo guarantee floor by 3-122x."

Red Team C verdict: **RED**. Replacement language:
- Drop the total recovery range entirely
- "We will not publish a total recovery number until admin baseline lands"
- Three highest-confidence individual findings with P25-P75 bands (F1 schema, F17 CWV, F5 intl — later F3 after F5 demotion)
- Payback: "4-6 months at P25, 2-3 months at P50"
- Guarantee safety: "cleared by 2-6×, not 3-122×"

See `references/example-findings.md` for the full Sene CFO attack and the replacement Section 2 language.

## Related skills
- `audit-red-team-baseline` (run FIRST)
- `audit-red-team-uplifts` (run BEFORE this)
- `audit-red-team-domain-check`

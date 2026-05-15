# Red Team C — Methodology

Full attack playbook. Use after reading SKILL.md.

## Statistical validity checklist

For every $ figure in the audit, ask:

- [ ] **Is this a P25-P75 interquartile band, or a min×max Cartesian extreme?** If the latter, mark RED.
- [ ] **Does the midpoint have meaningful probability mass?** A 12× span midpoint has ~2% probability if uniform. If you can't defend the central tendency, drop the midpoint.
- [ ] **Are correlated lifts summed linearly?** If yes, apply correlation discount (~0.5-0.7 coefficient typical).
- [ ] **Is the payback period coherent across the range?** "1-9 weeks" with $292K-$11M annual = 5 months at floor, 1 day at ceiling. Useless. Drop.
- [ ] **Is X/100 score interpreted as "% leaking"?** Wrong. X/100 is a readiness score. State this explicitly.

## The 10 hardest CFO questions (canonical bank)

Adapt to specific audit. Phrase in CFO register: terse, direct, financial-quantitative.

1. **"Your baseline says revenue is $A-$Z (with span >5×). My CFO knows the actual number. If I told you it's $X, does your projection still hold?"**
   - Exposes: projection scales from a guessed baseline.
   - Defense: refusal to project total + per-finding P25-P75 bands that hold across baseline range.

2. **"Your midpoint is $X on a $Y-$Z range. What probability distribution makes that midpoint? Because uniform gives it ~2% probability."**
   - Exposes: no joint distribution; midpoint is arithmetic-mean convenience.
   - Defense: state P50 explicitly with method (Monte Carlo or weighted central tendency).

3. **"Your 'star rating +58% purchase likelihood' citation — is that Baymard, Spiegel, or your guess?"**
   - Exposes: category error (intent vs behavior).
   - Defense: cite source + apply translation correctly. (No defense if numbers are unsourced.)

4. **"You claim $X recoverable from 76 hours of work. My business does $Y revenue. How do you recover X% of revenue from a 0.X% effort investment?"**
   - Exposes: projection ratios fail back-of-envelope sanity check.
   - Defense: scenarios should pass `recovery / effort` benchmarks (typical: $5-10K/hr engagement value, not $50K+/hr).

5. **"You sum 12 quick-win uplifts to 35% combined CVR. Real-world correlated combination is ~8-12%. What's your correlation discount?"**
   - Exposes: linear summation error.
   - Defense: explicit cluster table + correlation discount applied.

6. **"42/100 SiteHealth — does that mean 58% of my revenue is leaking?"**
   - Exposes: score interpretation conflation.
   - Defense: explicit "X/100 is a readiness score; recoverable revenue is sized per-finding above."

7. **"Your line item F[X] claims $Y. But that lift requires me to deploy 6 systems flawlessly. What's your execution-risk haircut?"**
   - Exposes: gross-modeled lift assumed perfect execution.
   - Defense: 30% execution haircut applied; document each gating dependency.

8. **"Your 'payback in 1-9 weeks' — at what realization rate? I want a single number for board."**
   - Exposes: payback claim is denominator artifact.
   - Defense: drop weekly payback; state in months at P25 and P50.

9. **"You list this competitor as 'invisible to ChatGPT Shopping.' Have you tried to enroll us? It's invite-gated for many merchants."**
   - Exposes: implementation gating not flagged.
   - Defense: enrollment-status disclosure per major channel; prerequisite work flagged.

10. **"Your 'guarantee safety: cleared by 3-122×' — that range tells me you don't know which it is. Cleared by what?"**
    - Exposes: meaningless multiplier theater.
    - Defense: "P25 floor clears engagement floor by X×, P50 by Y×" with both stated.

## How to write the executive verdict replacement

If the v1 hero/Section 2 contains:
- Single-number midpoints from wide ranges
- "Payback in N weeks" without baseline
- "$X-$Y total recovery" where Y/X >5

…replace with:

```markdown
**We will not publish a total recovery number until admin baseline lands.**

The dominant uncertainty in every recovery dollar is the baseline itself
— actual GA4 sessions, blended CVR, and AOV. Until that lands, a single
"total recoverable" figure is a forecast we cannot defend.

Below are the **three highest-confidence individual findings**, each with
a P25-P75 interquartile band against a defensible central baseline of
~$X annual revenue (P25 $Y / P75 $Z, triangulated from [3 sources]).
Ranges tighten to point estimates within 48 hours of GA4 read access.

[3 individual finding cards with P25-P75 bands]

[Payback at P25 + P50 baseline, in months]

[Guarantee safety: cleared by Nx at P25 / Mx at P50]
```

## Output format

```markdown
# Red Team C — Statistical Validity + CFO Attack

## Verdict
[GREEN | YELLOW | RED]

## Part 1 — Statistical flaws
1. [Range construction]
2. [Additive aggregation]
3. [Payback claim]
4. [Score interpretation]

## Proposed corrections
- [each numbered fix]

## Part 2 — CFO's 10 questions
For each:
- **Q[N]:** [verbatim question]
- **Exposes:** [what assumption breaks]
- **Best defense:** [Autonomous's response — or "no defense, fix it"]

## Proposed Section 2 / Hero replacement language
[full markdown of new language]
```

# Red Team D — Sene Studio Worked Example

The case that proves this red team has to exist.

## The finding that slipped through (Sene F5, v1)

**Original wording (HIGH severity, $96-216K/yr):**
> "International-copy contradiction loses qualified non-US buyers on every PDP. PDPs display 'custom is US-only, email us' while return policy documents active standard-size shipping to UK/AU/DE/KR/SG/UAE. Largest copy bug in audit. Fix: geo-conditional copy + waitlist capture."

**Why Red Teams A/B/C didn't catch it:**
- Red Team A (baseline): the math respected the ($1.2M-$4.9M) baseline. Within range.
- Red Team B (uplifts): "intl session × bounce reduction × CVR" was internally coherent.
- Red Team C (CFO): a CFO would ask "where did the 15-30% intl session share come from?" but wouldn't catch the *premise* error.

**What a Shopify operator immediately sees:**
The finding maps to **Pattern 1: Configurable / multi-path products.**

Sene's PDP has two purchase paths:
1. **Custom-fit path** — Smart Body Quiz + made-to-measure. Different SKU, different production, different policy. **Genuinely US-only.**
2. **Standard-size path** — off-rack picker on the same PDP. Different SKU, different fulfillment. **Ships to 7 markets + Canada.**

The PDP copy "custom is US-only, email us for your country" refers ONLY to path 1. It is **accurate**. There is no contradiction with the return policy (which describes path 2).

The audit flagged a contradiction that doesn't exist.

## What Red Team D would have produced

```markdown
# Red Team D — Domain Semantic Check (Sene Studio)

## Verdict
RED — Finding F5 is a domain semantic error. Demote required.

## Per-finding domain check

| ID | Finding | Two things compared | Pattern (1-7) | Verdict |
| F5 | International copy contradiction | PDP "custom is US-only" vs return policy "standard ships globally" | **Pattern 1 (multi-path products)** | TWO-PATH-ARTIFACT — not a contradiction |

## Findings to demote

- **F5:** demote HIGH→MEDIUM. Reframe as "merchandising surfacing gap" — global standard-size ship-to-country path is not visible on the PDP at the decision moment, even though it's correctly available. Reduce $ band from $96-216K to $30-84K.

## Reasoning
Sene's PDP shows a fit picker with two parallel paths:
1. Custom-fit (Smart Body Quiz / MTM) — US-only, accurate disclaimer
2. Standard-size (off-rack picker, same PDP) — ships globally per return policy

These are two different SKUs/fulfillment paths with two correctly different geographic policies. Not a contradiction.

The real (smaller) finding is that the PDP doesn't surface the global standard-size path to international visitors — they may read the (accurate) US-only disclaimer as a full dead-end.

## Practitioner sanity scan
None of the other findings flagged contradictions. F5 was the only one this red team would have demoted.
```

## What happened in v1 (without Red Team D)

The audit shipped with F5 at HIGH severity. The client read it, immediately said "the standard sizes do ship globally, only the custom is US-only." We then ran a 7-file cascade fix:
- `module3-conversion.md` (3 spots)
- `module3/cart-copy-offer.md` (full rewrite)
- `SYNTHESIS.md` (cross-correlation #3 + H9 row)
- `QUICK-WINS.json` (QW #5 demoted)
- `REVENUE-PROJECTION-v2.json` (F5 entry + top-5 reshuffle)
- `FACT-CHECK.md` (amended verdict)
- `audits/.../index.html` (Section 2 Alarm card swap, Section 7 finding card, Section 9 top-5 + QW grid)

**Cost:** ~85 line insertions + 87 line deletions across 7 files, ~2 hours of cascade work, plus the credibility hit of the client catching the error before we did.

This is the work Red Team D exists to prevent.

## What this taught us

1. **LLM auditors pattern-match on textual contradiction without domain understanding.** "PDP says X-only, return policy says Y" reads like contradiction. Practitioner-sanity required to disambiguate.
2. **The other red teams don't catch this.** Math/baseline/CFO checks are quantitative. Domain errors are semantic.
3. **HIGH-severity findings that hinge on "contradiction" wording are the highest-risk class.** If the finding doesn't survive a Shopify-operator sanity check, it doesn't ship.
4. **Always ask the client BEFORE publishing if you're flagging a contradiction.** One email saves a 7-file cascade fix.

## Other patterns to look for in future audits

Watch for findings flagging:
- "Pricing inconsistency" → could be MAP-locked SKUs (Pattern 3)
- "Different policies for different customers" → could be B2B vs DTC (Pattern 2)
- "Missing intl expansion" → could be region-locked SKUs (Pattern 4)
- "Lead time vs shipping policy contradiction" → could be pre-order vs in-stock (Pattern 7)
- "Brand price vs Amazon price difference" → deliberate marketplace strategy (Pattern 6)

Every "contradiction" or "inconsistency" finding goes through Red Team D.

---
name: audit-red-team-domain-check
description: Use to catch semantic and domain errors that math/baseline/CFO red teams miss. Specifically probes findings for cases where the audit assumes two policies, products, or concepts are equivalent when a domain practitioner would immediately recognize them as distinct purchase paths or business contexts (custom-fit vs standard-size, BOPIS vs ship-to-home, B2B vs DTC, MAP-priced vs free-priced, configurable vs simple products, region-locked SKUs, white-label vs branded). Triggers on "domain-check this audit", "would a Shopify operator agree with this finding", or as part of /shopify-revenue-audit pipeline.
---

# Red Team D — Domain Semantic Check

You are a Shopify operator with 10+ years experience. Your job: **catch the findings where an LLM auditor read two documents literally and called it a contradiction**, when in fact those documents describe two different purchase paths or business contexts that *correctly* have different policies.

## Why this red team exists

The other three red teams (math, baseline, CFO) catch quantitative errors. They don't catch **domain semantic errors**. The Sene Studio audit had F5 ("PDPs say custom is US-only while return policy ships to UK/AU/DE/KR/SG/UAE — direct contradiction!") originally rated HIGH with $96-216K/yr recovery — until the client clarified that *custom-fit* and *standard-size* are two different purchase paths that legitimately have different geographic policies. No contradiction. The 7-file cascade fix that followed cost real time and credibility.

Math red-team didn't catch it (math was fine). Baseline red-team didn't catch it (baseline wasn't the issue). CFO red-team didn't catch it (the question "is your customer-fit-US-only-but-standard-ships-globally a contradiction?" is operationally obvious, but doesn't surface in the CFO frame).

You catch it.

## When to use

- After Red Teams A/B/C, before Wave 4 HTML build
- Anytime an audit flags a "contradiction" between two documents/policies/copy
- Phrases: "would a domain practitioner agree", "domain-check the findings", "is this really a contradiction"

## What you produce

`projects/<client>/diagnostics/RED-TEAM-D-domain-check.md` with:
- Verdict: **GREEN** | **YELLOW** | **RED**
- Per-"contradiction" finding: domain interpretation + verdict (real contradiction / two-path artifact / unclear-need-client-input)
- Per "trivially obvious" finding: practitioner sanity check (would a Shopify operator say "well, duh, of course it's that way"?)
- Recommended findings to demote, drop, or escalate to client clarification

## The 7 domain-error patterns to probe

### 1. Configurable vs simple products
Many "contradictions" disappear when you realize a product has multiple purchase paths. Examples:
- **Custom-fit vs standard-size** (apparel) — different production, different geography, different lead times. Sene F5 is the canonical case.
- **BOPIS vs ship-to-home** — same SKU, different fulfillment. Different return policies legitimately apply.
- **Subscription vs one-time** — same product, different cadence. Different cancellation policies.
- **Configurable variants** — SKU-level vs product-group-level policies.

If a finding flags "the policy on path A contradicts path B," verify those are actually the same path. Otherwise it's a merchandising surfacing gap (medium severity), not a contradiction (high).

### 2. B2B vs DTC contexts
Same Shopify store can have radically different policies for B2B vs DTC. Examples:
- B2B has Net-30 terms, DTC has card-only — not a "payment policy contradiction"
- B2B has tiered/quote pricing, DTC has fixed — not a "pricing inconsistency"
- B2B ships pallets, DTC ships parcels — not a "fulfillment contradiction"

Check if the merchant has **`b2b`** in their plan / URL paths / customer tags before flagging policy "inconsistencies."

### 3. MAP-priced vs free-priced products
Some product lines are price-locked (Minimum Advertised Price agreements with brand owners). The merchant *cannot* discount these — flagging "no sale on this SKU = missed promotion" is a domain error. Check if the merchant resells branded inventory before flagging discount opportunities.

### 4. Region-locked SKUs
Apparel sizing, supplements (FDA-restricted), alcohol (state-by-state), CBD/hemp (country-by-country), wholesale agreements (territory exclusivity). A SKU not available in country X may be **legally** unavailable, not a missed sales opportunity.

### 5. White-label vs branded inventory
Merchant may sell their branded line + carry resale inventory under different terms. Different return policies, different MOQs, different markup. Not a contradiction — a multi-line operation.

### 6. Marketplace vs DTC channels
A Shopify merchant who *also* sells on Amazon, Walmart, TikTok Shop has different policies per channel. Flagging "your Amazon listing has a different price than your DTC site" may be **deliberate**, not a bug.

### 7. Pre-order vs in-stock products
Lead times, shipping policies, refund windows all differ. A "this product takes 3 weeks" disclaimer next to "ships in 1-3 days" headline isn't a bug — it's pre-order vs in-stock.

## How to apply

For every finding flagged "contradiction", "inconsistency", "bug" in the projection or synthesis, ask:

1. **What two things does this finding compare?** (Quote them.)
2. **Could a Shopify operator legitimately have set them up that way on purpose?** (Map to one of the 7 patterns above.)
3. **If yes — is the finding a contradiction (correct) or a merchandising gap (the two paths exist correctly, but the visitor can't see both)?**
4. **If you can't tell — flag for client clarification, do NOT publish as HIGH.**

For every finding with $ impact > $50K/year, run this check even if "contradiction" isn't in the wording — domain errors hide in confidence levels too.

## Output format

```markdown
# Red Team D — Domain Semantic Check

## Verdict
[GREEN | YELLOW | RED]

## Per-finding domain check (table)
| ID | Finding | Two things compared | Domain pattern (1-7) | Real contradiction? | Recommended action |

## Findings to demote / drop / escalate
- [ID] [demote | drop | escalate] [rationale]

## Practitioner sanity scan
[Any other findings that would make a Shopify operator say "obviously, that's how it works" — i.e. trivially obvious / not a finding]

## Client clarification questions
[List of questions to send to the client BEFORE publishing — for findings the audit can't resolve from public evidence alone]
```

## Canonical example
**Sene Studio F5 (April 2026)**: original v1 finding rated HIGH/$96-216K/yr — "PDPs say custom is US-only while return policy ships to UK/AU/DE/KR/SG/UAE — direct contradiction costing qualified intl buyers."

Red Team D would have caught (and now does): pattern #1 (configurable products / multi-path SKUs). Custom-fit (Smart Body Quiz / made-to-measure) is genuinely US-only. Standard sizes ship to 7 markets. **Two different purchase paths, both correctly policied.** No contradiction.

Verdict: RED. Recommended action: demote F5 from HIGH→MEDIUM, reframe as "merchandising gap — global standard-size shipping not surfaced on PDP." Demote $ band from $96-216K → $30-84K.

This was caught by the *client* on read-through, not by Red Teams A/B/C. That's the gap this skill exists to close.

See `references/example-findings.md` for the full F5 cascade fix.

## Related skills
- `audit-red-team-baseline` (catches different errors)
- `audit-red-team-uplifts` (catches different errors)
- `audit-red-team-cfo` (catches different errors)

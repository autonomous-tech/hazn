# Red Team D — Methodology

Full domain-check playbook. Use after reading SKILL.md.

## The 7 domain-error patterns — full probe

For each pattern, ask the diagnostic questions below. If any finding flags a "contradiction" or "inconsistency," map it to one pattern and verify.

### Pattern 1 — Configurable / multi-path products
**Where it appears:** apparel (custom-fit vs standard-size), furniture (made-to-order vs in-stock), supplements (subscription vs one-time), software (annual vs monthly), bookings (premium vs basic).

**Diagnostic questions:**
- Does the product have variants beyond simple size/color (e.g., Smart Body Quiz, configurator, MTM picker)?
- Do the configurator paths have **different SKUs**, **different lead times**, **different fulfillment policies**?
- Is the "contradiction" actually two policies for two different paths?

**Sene F5 case:** "PDP says custom-only-US, return policy says standard-ships-globally" → flagged as contradiction → actually two paths. Custom-fit (Smart Body Quiz path) is genuinely US-only; standard-size (off-rack picker on the same PDP) ships globally. **Not a contradiction; a merchandising surfacing gap.**

### Pattern 2 — B2B vs DTC
**Where it appears:** wholesale-enabled Shopify (`shop.myshopify.com/wholesale`, custom price lists, B2B portal), Plus stores with B2B addon, multi-channel merchants.

**Diagnostic questions:**
- Does the merchant have a B2B portal / wholesale channel / Net-30 terms?
- Does any flagged "policy contradiction" disappear if you split into B2B context vs DTC context?
- Are different return windows / shipping costs / payment terms legitimate per channel?

**Common false-positive:** "Some customers see Net-30 terms, others see card-only — payment policy is inconsistent!" Reality: B2B has Net-30, DTC has card. Two channels, two policies.

### Pattern 3 — MAP-priced vs free-priced products
**Where it appears:** retailers carrying branded inventory (Apple, Sony, Nike, etc.) where the merchant signed Minimum Advertised Price agreements.

**Diagnostic questions:**
- Does the merchant resell branded inventory (vs sell only their own brand)?
- Does the brand contract restrict discounts on certain SKUs?
- Are flagged "missing promotion opportunities" actually MAP-locked?

**Common false-positive:** "Why isn't this $200 Nike on sale?" → because the merchant signed a MAP agreement and the floor price is locked.

### Pattern 4 — Region-locked SKUs
**Where it appears:** apparel sizing (EU sizes can't ship to US per brand exclusivity), supplements (FDA / Health Canada restrictions), alcohol (state-by-state US, province-by-province CA), CBD/hemp (country-by-country), wholesale agreements (territory exclusivity).

**Diagnostic questions:**
- Are restricted-region SKUs hidden via Shopify Markets / collection-level country gating?
- Is a SKU "missing" in a country because of legal/regulatory/contractual restriction?
- Are flagged "international expansion opportunities" actually blocked by regulation?

**Common false-positive:** "Add this supplement to UK market" → blocked by MHRA approval requirement; not a sales opportunity.

### Pattern 5 — White-label vs branded inventory
**Where it appears:** print-on-demand, dropship-supplemented stores, multi-brand retailers.

**Diagnostic questions:**
- Does the merchant carry their own branded line + resell other inventory?
- Are policy differences (shipping time, returns, MOQ) per-brand or per-SKU-group?
- Is a flagged "policy inconsistency" actually two business lines with different supplier terms?

### Pattern 6 — Marketplace vs DTC channels
**Where it appears:** any Shopify merchant who also sells on Amazon, Walmart Marketplace, TikTok Shop, eBay, Faire.

**Diagnostic questions:**
- Does the merchant sell on third-party channels?
- Are flagged "price inconsistencies between site and listings" deliberate channel pricing strategy?
- Are flagged "missing inventory on marketplace X" intentional channel separation?

**Common false-positive:** "Your Amazon price is $X but your DTC price is $Y" → often deliberate (Amazon takes a 15% cut, DTC has free shipping cost-loaded, etc.).

### Pattern 7 — Pre-order vs in-stock
**Where it appears:** apparel drops, electronics launches, made-to-order (MTM, custom furniture), back-in-stock waitlists.

**Diagnostic questions:**
- Does the PDP indicate "ships in N weeks" or "pre-order" badge?
- Are flagged "shipping policy contradictions" actually pre-order vs in-stock disclosures?
- Is the "lead time" finding actually correct disclosure of pre-order timeline?

**Common false-positive:** "PDP says ships in 1-3 days, this product page says 3 weeks — inconsistent!" → pre-order vs in-stock.

## How to apply (procedural)

For every finding in the projection or synthesis flagged with words like "contradiction," "inconsistency," "bug," "discrepancy":

1. **Quote the two things being compared verbatim.**
2. **Map to one of the 7 patterns above.** (If none fit, it might be a real contradiction. Continue.)
3. **Verify by examining merchant evidence:**
   - Multi-path SKUs → check PDP for configurator/quiz/picker
   - B2B → check `b2b.example.com`, `wholesale` URL, customer-tag-based pricing signals
   - MAP → check brand mix; resold-inventory typical for accessories/electronics
   - Region-locked → check Shopify Markets config, collection-level country gates
   - Marketplace → check social/footer for "Also on Amazon/Walmart" badges
   - Pre-order → check PDP for "ships in N weeks" badge
4. **If the finding survives all 7 patterns,** it's likely a real contradiction. Mark CONFIRMED.
5. **If it maps to a pattern,** mark TWO-PATH-ARTIFACT. Reframe finding (typically demote HIGH→MEDIUM and reduce $).
6. **If unclear,** mark CLIENT-CLARIFICATION-NEEDED. Do NOT publish at HIGH.

## Practitioner sanity scan (separate output)

Beyond explicit "contradiction" flagging, check every HIGH-severity finding for **trivially obvious** content:

- Would a Shopify merchant operator say "duh, of course it's that way"?
- Is the finding describing a deliberate design choice (not an error)?
- Does the recommended fix imply rebuilding something that's standard practice?

If yes, demote or drop. Trivial findings inflate the audit and erode credibility.

## Output format

```markdown
# Red Team D — Domain Semantic Check

## Verdict
[GREEN | YELLOW | RED]

## Per-finding domain check
| ID | Finding | Two things compared | Pattern (1-7) | Verdict |

## Findings to demote/drop/escalate
- F[X]: [demote HIGH→MED | drop entirely | escalate to client]
  Rationale: [pattern N applies; X-Y are not the same path]

## Practitioner sanity scan
- F[X]: trivially obvious — [reason]

## Client clarification questions (must ask before publishing)
1. [verbatim question]
2. ...
```

# Store Diagnostic Pipeline — Full Intelligence Suite

Run the complete free Store Diagnostic on a Shopify store. Combines ALL Intelligence Suite skills with Shopify-specific analysis for maximum evidence on sales calls.

## Usage
```
/hazn-store-diagnostic [URL]
```

Optional: `/hazn-store-diagnostic [URL] --revenue [estimated monthly revenue]`

## Model Routing
- **Sonnet agents** for: `seo-audit`, `conversion-audit`, `shopify-logic-scan`, `shopify-platform-scan`, `shopify-app-ecosystem-scan`, `ai-seo` (require reasoning)
- **Haiku agents** for: `ui-audit`, file writing, data extraction
- **Opus** stays as orchestrator — reads results, synthesizes cross-skill patterns, makes qualification decision
- Launch all 7 skill invocations across 6 tracks in parallel (single message, multiple tool calls)

## What This Does

Runs 7 skill invocations across 6 tracks in parallel, performs cross-skill correlation, then generates a Hormozi-optimized teaser report:

1. `seo-audit` — Technical SEO + Shopify-specific SEO gaps
2. `ai-seo` — AEO/GEO, AI search readiness, LLM visibility
3. `conversion-audit` — CRO + Shopify ecommerce conversion patterns
4. `shopify-logic-scan` + `shopify-platform-scan` — **Compound track.** Logic scan: pricing errors, app conflicts, custom logic, security. Platform scan: legacy architecture, checkout signals, Functions risks, B2B, variant limits, Markets.
5. `ui-audit` — UX, mobile, theme responsiveness, accessibility
6. `shopify-app-ecosystem-scan` — App detection, interaction risks, bloat, missing essentials, duplicates, spend estimation

Then: `diagnostic-teaser-report` — combines ALL outputs with cross-skill correlation into branded sales weapon

## Pipeline

### Step 1: Validate Input

Fetch the URL and check for `cdn.shopify.com` or `window.Shopify` object.
If not Shopify → abort: "This doesn't appear to be a Shopify store."
Extract: domain, myshopify domain, theme name, currency, product count.
If `--revenue` flag provided, pass to all skills for dollar estimates.

### Step 2: Create Project Directory

```bash
mkdir -p projects/[client-slug]/diagnostics
```

Client slug = domain name without TLD (e.g., `containerone` from `containerone.net`).

### Step 3: Run ALL 6 Skill Tracks in Parallel

**Track 1: SEO Audit** (Sonnet)
- Invoke `seo-audit` skill with Shopify context
- Shopify-specific: sitemap structure, canonical patterns, Shopify robots.txt defaults, theme SEO settings, collection/product URL structure, pagination handling
- Save to: `projects/[slug]/diagnostics/seo-audit.md`

**Track 2: AEO/GEO — AI Search Readiness** (Sonnet)
- Invoke `ai-seo` skill OR use AI readiness section from `seo-audit`
- Focus: Is the store cited by ChatGPT/Perplexity/Google AI Overviews? Is content structured for AI extraction? Are AI crawlers blocked?
- Shopify-specific: Check Shopify's default robots.txt AI bot rules, product content extractability, FAQ/structured content, entity presence
- Save to: `projects/[slug]/diagnostics/aeo-geo-audit.md`

**Track 3: CRO / Conversion Audit** (Sonnet)
- Invoke `conversion-audit` skill tailored to Shopify ecommerce
- Shopify CRO checks: product page elements (trust badges, reviews, urgency), add-to-cart flow, cart page optimization, checkout friction, upsell/cross-sell apps, abandoned cart recovery (Klaviyo/Attentive detection), mobile checkout, payment methods visible (Shop Pay, Apple Pay), shipping/returns visibility, social proof placement, buy-now vs add-to-cart
- Save to: `projects/[slug]/diagnostics/conversion-audit.md`

**Track 4: Shopify Deep Scan — COMPOUND TRACK** (Sonnet × 2)

Launch BOTH skills in parallel within this track:

**Track 4a: Shopify Logic Scan** (Sonnet)
- Invoke `shopify-logic-scan` skill (pricing errors, app conflicts, custom logic, security, legacy architecture indicators, interaction risks)
- Now includes: ScriptTag vs Extension ratio, Scripts Sunset Registry cross-reference, Checkout Architecture signals, B2B detection
- Save to: `projects/[slug]/diagnostics/shopify-logic-scan.json`

**Track 4b: Shopify Platform Scan** (Sonnet)
- Invoke `shopify-platform-scan` skill (platform fingerprint, legacy architecture scoring, Functions migration risk, B2B architecture, variant limits, Shopify Markets)
- THIS IS THE NEW DIFFERENTIATOR — platform-specific risks no competitor audits for
- Uses relative dates for all deadlines (reads from references/shopify-platform-reference.md)
- Save to: `projects/[slug]/diagnostics/shopify-platform-scan.json`

**Track 5: UI/UX Audit** (Haiku)
- Invoke `ui-audit` skill
- Shopify-specific: theme responsiveness, navigation depth, collection layout, product image quality, search functionality, filter/sort UX, mega menu behavior, mobile drawer experience
- Save to: `projects/[slug]/diagnostics/ui-audit.json`

**Track 6: App Ecosystem Scan** (Sonnet)
- Invoke `shopify-app-ecosystem-scan` skill (replaces inline MarTech detection)
- **App detection:** Analytics, Marketing, CRO tools, Reviews, Support, Subscription, B2B, Search, Page Builder, Loyalty, Quiz — all via CDN/JS pattern matching from `app-signatures.md`
- **NEW — Interaction risk analysis:** Cross-references co-installed apps against Interaction Risk Matrix. Detects price races, selling_plan conflicts, duplicate widgets, cart latency stacking, analytics inflation. All findings in customer-experience language.
- **NEW — App bloat assessment:** Counts total apps, estimates monthly spend, flags 8+ apps with performance impact estimate
- **NEW — Missing essentials:** Flags ecommerce stores without reviews, email marketing, analytics, search (if 50+ products)
- **NEW — Duplicate detection:** Duplicate GA4, GTM, Pixel IDs, duplicate tools in same category
- Save to: `projects/[slug]/diagnostics/shopify-app-ecosystem.json`

### Step 4: Cross-Skill Correlation (Orchestrator — Opus)

Read ALL 7 outputs (6 tracks, Track 4 has 2 outputs). Look for patterns spanning multiple skills.

**Original correlations (still apply):**
- SEO says no product structured data + Shopify scan says blank categorization → **"Your products are invisible across ALL of Google — organic, Shopping, AND AI answers. Same root cause, three impacts."**
- CRO says no reviews visible + App ecosystem says no reviews app installed → **"No social proof because no reviews system. Tooling gap, not content gap."**
- CRO says poor mobile conversion + UI says mobile UX issues + Shopify scan says mobile pricing mismatch → **"Your mobile experience is broken at every level — speed, UX, and pricing."**
- App ecosystem shows email tool + CRO shows no abandoned cart indication → **"You have Klaviyo but may not be recovering abandoned carts — typically 5-15% of lost revenue."**
- Multiple B2B/wholesale apps detected + Shopify scan shows conflicts → **"Your wholesale apps are fighting each other."**
- SEO says AI crawlers blocked + AEO says zero AI citations → **"You've blocked AI search engines AND you're not appearing in AI answers. Double invisible."**

**NEW — Shopify platform correlations:**
- Platform scan: high legacy architecture score + logic scan: pricing errors → **"Your store runs on legacy Shopify infrastructure AND has active pricing errors. The infrastructure deadline makes fixing this urgent — you're patching a system that's being retired."**
- Platform scan: legacy checkout indicators + app ecosystem: checkout extension apps co-installed → **"Your checkout has customizations from different Shopify eras that may not work together. Some checkout features may silently fail."**
- Platform scan: third-party B2B + logic scan: B2B injection failure → **"Your third-party wholesale app isn't working AND Shopify's native B2B could replace it for free. You're paying for a broken tool when a better one is included."**
- App ecosystem: 3+ cart-modifying apps + logic scan: slow performance → **"[N] apps compete to modify your cart in real time. Each one adds latency — your customers feel this on every add-to-cart click."**
- Platform scan: variant limit risk + app ecosystem: inventory sync app detected → **"You're approaching Shopify's variant limit on [N] products AND running inventory sync. When variants exceed the limit, sync breaks and stock counts go wrong."**
- Platform scan: no Markets + logic scan: multi-currency detected → **"Your store shows prices in multiple currencies without Shopify Markets. Tax calculations, duty estimates, and localized content may be wrong for international customers."**
- Platform scan: Functions migration risk + app ecosystem: multiple discount apps → **"Your discount apps may silently conflict under Shopify's newer infrastructure — it only allows one cart modification at a time. [N-1] of your discount tools would need to be replaced."**
- App ecosystem: interaction risk + logic scan: related pricing issue → **"Your apps are fighting AND it's affecting your prices. [Specific interaction risk] is causing [specific pricing evidence]."** ← This is the MOST powerful finding type.
- App ecosystem: estimated spend > $500/mo + platform scan: third-party B2B or duplicate tools → **"You're spending ~$[X]/month on apps. Some duplicate what Shopify already provides, and others conflict with each other. The paid audit identifies which to keep and which to cut."**

**Correlation priority:** Cross-skill findings are HIGHER priority than single-skill findings — they're harder to dismiss and show systemic problems. Shopify-specific cross-skill findings rank above generic cross-skill findings.

**Alarm selection logic:** When picking the alarm finding for the teaser report:
1. Deadline-based findings always win (platform risk with countdown)
2. Cross-skill Shopify findings next (e.g., "apps fighting AND affecting prices")
3. Single-skill Shopify findings next (pricing errors, broken B2B)
4. Cross-skill generic findings (SEO + categorization)
5. Single-skill generic findings (missing meta descriptions) — NEVER the alarm

### Step 5: Qualification Gate

From combined findings:
- Count total findings across all categories
- Estimate total monthly impact (honest methodology — math chains or "requires revenue data")
- Apply threshold: $7,500+ estimated annual recoverable = PROCEED, $5-7.5K = INVESTIGATE, <$5K = WALK AWAY

**Offer model:** $7,500 one-time. 6 weeks. We fix everything in the report. 10x guarantee ($75K/yr recoverable or full refund). One offer, one price, one decision. No tiers. No retainer pitch in the report — that conversation happens at Week 5 when we have data to show.

### Step 6: Generate Teaser Report

Invoke `diagnostic-teaser-report` skill with ALL 6 outputs + cross-skill findings.
The alarm finding should come from shopify-logic-scan OR a cross-skill correlation.
Output: `projects/[slug]/diagnostics/store-diagnostic-[date].html`

### Step 7: Summary

```
══════════════════════════════════════════════════
  STORE DIAGNOSTIC COMPLETE: [domain]
══════════════════════════════════════════════════

  Skills Run: 6
  ├── SEO Audit:              ✓ [N findings]
  ├── AEO/GEO (AI Search):   ✓ [N findings]
  ├── CRO / Conversion:      ✓ [N findings]
  ├── Shopify Logic Scan:     ✓ [N findings]
  ├── UI/UX Audit:            ✓ [N findings]
  └── MarTech Detection:      ✓ [N apps, M conflicts]

  Scores:
  ├── SEO Health:           [X]/10
  ├── AI Search Ready:      [X]/10
  ├── Conversion:           [X]/10
  ├── Store Logic:          [X]/10  (from shopify-logic-scan)
  ├── App Stack Health:     [X]/10  (from shopify-app-ecosystem-scan)
  └── Shopify Architecture: [X]/10  (from shopify-platform-scan)

  Cross-Skill Patterns: [N] systemic issues found

  Total Findings: [N] (alarm: 1, top: 2-4, gated: 3-5)
  Revenue Leak Estimate: $[X,XXX]/mo
  Qualification: [PROCEED / INVESTIGATE / WALK AWAY]

  Report: projects/[slug]/diagnostics/store-diagnostic-[date].html

  Next Steps:
  1. Capture [SCREENSHOT] placeholders before the call
  2. Walk through alarm + quick wins + top findings LIVE
  3. Email teaser as PDF after the call
  4. If qualified → pitch Revenue Rescue ($7,500)
══════════════════════════════════════════════════
```

## The Revenue Rescue Model ($7,500 / 6 Weeks)

### What the $7,500 Buys
Everything the free diagnostic found. Confirmed, sharpened, and fixed.

The scope is defined by the teaser report: every finding with a packaged solution = included. The deep audit in Week 1-2 confirms these findings with real data and reprioritizes the implementation order — but doesn't change the scope.

### Week-by-Week Structure

**Week 1-2: Deep Audit + Quick Kills**

First thing after signing: get admin access. Run the deep audit across:
- **Shopify Admin:** Orders, AOV, conversion rate, discount codes, customer segments, shipping zones, tax config, metafields, staff accounts
- **Theme Code:** Liquid templates, dead code, custom JS/CSS, theme version, OS 2.0 compliance, hardcoded vs block-based apps
- **Klaviyo:** Flows (abandoned cart, welcome, post-purchase, winback), list health, deliverability, revenue attribution, suppression rates
- **Checkout:** Conversion by step, payment method split, shipping abandonment, post-purchase upsell, checkout customizations
- **Subscription App:** Churn rate, skip rate, pause rate, LTV per cohort
- **Google Search Console / GA4 (if access granted):** Real impressions, clicks, CTR by page, index coverage, Core Web Vitals field data
- **Apps from inside:** Internal dashboards, unused premium tiers, configuration gaps

SIMULTANEOUSLY ship quick kills — don't wait for the audit to finish:
- Analytics goes live (GA4, Meta Pixel)
- Schema deployed (products in Google Shopping within 48hrs)
- Star ratings connected to Google
- JS console errors diagnosed and fixed

**Deliverable: Full Report (end of Week 2)**
The Full Report is a mid-engagement deliverable — NOT a sales document. It replaces every benchmark estimate from the teaser with real numbers from the client's own data.

Structure:
1. What we already shipped (Week 1-2 quick kills, with before/after evidence)
2. What the deep audit found (real numbers: actual conversion rate, actual churn, actual cart abandonment, actual email performance)
3. The 4-week implementation plan (Weeks 3-6) — reprioritized based on real data
4. Expected impact — now with REAL math, not estimates
5. Bucket 2: What the deep audit discovered beyond the original diagnostic scope (NOT billed — presented as information for the Week 5 conversation)

Format: Web-native scrolling document with fixed sidebar navigation. NOT A4 pages. NOT a copy of the teaser.

**Week 3-4: Conversion Surgery**
Fix the bleeders based on deep audit priorities:
- Subscription UX (pre-select, savings badge, Most Popular tag)
- Mobile CRO (sticky ATC, grid fix, touch targets)
- Hero redesign (single CTA, value prop above fold)
- Cart optimization (drawer, recovery, upsell)
- Klaviyo popup reconfiguration
- Nav fixes, free shipping threshold

**Week 5-6: Growth Layer + Retainer Conversation**
Build the compounding layer:
- AI content structure (product descriptions, FAQ schema, HowTo schema)
- Blog restructure (H2/H3, Article schema, top 10 posts)
- Performance (defer/async scripts, image optimization)
- Alt text bulk update
- Hreflang audit and fixes
- /llms.txt and brand positioning

**The Week 5 Conversation:**
Present Bucket 2 findings — the problems discovered by the deep audit that are outside the original diagnostic scope. Present with real data on a screen share:
- "We fixed everything we promised. Here's what we found inside that we couldn't see before."
- "Here's what it's costing you — real numbers from your store."
- "Here's what ongoing optimization looks like."

This is the retainer conversation. It sells itself because you have data. Don't pitch a retainer in any report — let results sell it.

### Delivery Model
AI-first delivery. Content work (product descriptions, FAQ content, HowTo steps, alt text, blog restructure) is generated by AI agents, reviewed by humans. This is what makes 29+ fixes in 6 weeks at $7,500 sustainable:
- Traditional agency: 90-110 hours → $11K+ cost
- AI-first: 50-60 hours human time → $4-5K cost → positive margin

### The Two Buckets
- **Bucket 1:** Everything the free diagnostic found + deep audit confirmations = $7,500 scope. Fixed in 6 weeks.
- **Bucket 2:** New problems discovered by the deep audit (invisible from outside) = next conversation at Week 5. NOT billed during the engagement. NOT a surprise. The teaser tells the prospect "admin access reveals more."

The retainer addresses Bucket 2 findings plus ongoing optimization. Pitched at Week 5 with data. Price: $2,200-3,500/mo depending on scope.

## Full Report (Project Kickoff Document)

The full report is generated AFTER the prospect signs. It is NOT a sales document — it's the working document for the 6-week engagement. It should look and feel completely different from the teaser.

**Format:** Web-native scrolling document with fixed sidebar navigation. NOT A4 pages. NOT a copy of the teaser with more findings.

**Structure:**
1. Cover — "Revenue Rescue — [Client] — 6-Week Implementation Plan"
2. Executive Summary — all 6 scores, total estimated impact, 6-week timeline overview
3. Week-by-Week Roadmap — every fix mapped to a week with expected impact
4. Findings by Category — ALL findings (nothing gated), each with: Problem, Evidence, Solution, Timeline, Expected Impact, screenshots
5. Quick Wins — things that ship in Week 1 first 48 hours
6. What Admin Access Will Reveal — the additional layer they'll see once we're in
7. Appendix — raw scan data, app inventory, technical details for the implementation team

**Key differences from teaser:**
- Nothing is gated — every finding shown in full
- No CTA, no price, no guarantee — they already signed
- The roadmap is the centerpiece, not the alarm
- Technical details are welcome (the team needs them)
- Screenshots are inline throughout, not placeholders

## Notes
- Full diagnostic takes 3-8 minutes (6 parallel skill tracks)
- All external scanning — no admin access used
- Teaser report follows Hormozi rules: alarm-first, visual evidence, revenue language, no padding
- Cross-skill correlation findings are the most powerful — prioritize these
- Max 2 active diagnostics simultaneously until process is documented

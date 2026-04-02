# Intelligence Suite — Implementation Spec
**Version:** 1.0 · **Date:** 2026-04-02  
**Author:** Haaris (based on audit by Sonnet subagent + Rizwan session)  
**Status:** Ready for implementation

---

## 0. Scope

This spec covers the changes required to Hazn's skill set to support the Intelligence Suite product offer:

- **SiteScore** — SEO Audit (Free / Standard / Deep Dive)
- **Revenue Leak Audit** — Attribution & Analytics (Free / Standard / Deep Dive)
- **ConversionIQ** — CRO Audit (Free / Standard / Deep Dive)
- **UX/UI Audit** (Free / Standard / Deep Dive)
- **SiteHealth** — Bundle of all 4 (Standard / Deep Dive)

**Execution model:** Direct only. Rizwan or team messages Hazn in chat. Hazn runs intake, executes, delivers report URL. No webhooks, no job queue, no external API — for now.

---

## 1. Invocation Syntax

Hazn should recognise any of these natural-language patterns and route correctly:

```
"Run SiteScore [Free/Standard/Deep Dive] for [url]"
"Run Revenue Leak Audit Standard for acme.com"
"ConversionIQ Deep Dive — example.com, access: [GA4 token]"
"UX/UI Standard for app.acme.com"
"SiteHealth Standard for acme.com"
"Run a full bundle Deep Dive on acme.com"
```

If tier is not specified, ask. If URL is not provided, ask. Do not guess either.

---

## 2. Shared Intake — Runs First for Every Audit

Before running any product or tier, Hazn asks these questions **in a single message** (not multiple rounds):

```
Before I start, a few quick questions:

1. URL to audit: [if not already provided]
2. Tier: Free / Standard / Deep Dive?
3. Who is this report for?
   a) Autonomous delivery (default)
   b) Partner white-label — which partner? (I'll load their brand config)
   c) End-customer branded — provide: company name, primary colour, logo URL, CTA URL
4. Client contact email (for report delivery note — optional)
5. [Product-specific access questions — see Section 3]
```

**Brand config loading:**
- Option (a): load `~/hazn/brands/autonomous.json` (default)
- Option (b): load `~/hazn/brands/{partner-slug}.json` — if file doesn't exist, run brand setup first
- Option (c): build brand config inline from provided details

**Brand config schema** (`~/hazn/brands/{slug}.json`):
```json
{
  "slug": "partner-name",
  "company_name": "Partner Co.",
  "logo_url": "https://...",
  "logo_base64": "data:image/...",
  "primary_color": "#E8513D",
  "accent_color": "#1E3A8A",
  "background_color": "#F5EFE0",
  "cta_url": "https://partner.com/contact",
  "cta_label": "Book a call →",
  "domain": "reports.partner.com",
  "hide_autonomous": true,
  "font_display": "Fraunces",
  "font_body": "DM Sans"
}
```

Default Autonomous config (`~/hazn/brands/autonomous.json`) uses all current design tokens. Skills fall back to this if no brand config is found.

---

## 3. Product-Specific Intake

### 3.1 SiteScore (SEO)

**All tiers:** URL only (fetched publicly).

**Deep Dive — additional questions:**
```
For Deep Dive, I'll need:
- Google Search Console access: [property URL or verification token]
- GA4 Property ID: [e.g. G-XXXXXXXX]
- Ahrefs API key or confirm I should use the shared Hazn Ahrefs account
- 2–3 competitor domains to benchmark against (optional but recommended)
```

**If Deep Dive access not provided:** Offer to downgrade to Standard automatically.
> "I don't have GSC/GA4 access — I can run a Standard audit instead which uses public signals only. Want me to proceed with Standard?"

---

### 3.2 Revenue Leak Audit (Attribution)

**Free + Standard:** URL only. Standard does not require platform access — it audits from public signals + observable tracking calls.

**Deep Dive — additional questions:**
```
For Deep Dive I'll need:
- GA4 Property ID + admin access (View Access minimum)
- PostHog Project ID + API key (if applicable)
- Which ad platforms are active? (Google Ads / Meta / LinkedIn / other)
- 2–3 competitor domains (optional)
```

**If Deep Dive access not provided:** Offer Standard fallback.
> "Without GA4 admin access I can't run a Deep Dive — I'd be working with the same data as Standard. Want me to run Standard instead?"

---

### 3.3 ConversionIQ (CRO)

**Free + Standard:** URL only. Standard works from public page analysis — no platform access needed.

**Deep Dive — additional questions:**
```
For Deep Dive I'll need:
- GA4 Property ID (for funnel data)
- PostHog access (for session data, if available)
- Primary conversion goal: [demo / signup / purchase / other]
- 2–3 competitor landing pages to benchmark against
```

**If Deep Dive access not provided:** Offer Standard fallback.

---

### 3.4 UX/UI Audit

**All tiers:** URL only. Screenshots captured via browser automation.

**Deep Dive — additional questions:**
```
For Deep Dive I'll need:
- Key user journeys to map (e.g. homepage → pricing → signup)
- Design system / Figma link (optional — for design system consistency review)
- 2–3 competitor sites for UX benchmarks
```

No platform access required. Deep Dive is depth of analysis, not data access.

---

### 3.5 SiteHealth Bundle

Intake combines all four products into one message:

```
For the SiteHealth bundle I need:

1. Primary URL: [if not provided]
2. Tier: Standard or Deep Dive?
3. Brand config: Autonomous / Partner / End-customer?
4. Client email (optional)

[If Deep Dive:]
5. GSC + GA4 access for SiteScore
6. GA4 + PostHog access for Revenue Leak + ConversionIQ
7. Key user journeys for UX/UI Deep Dive
8. Competitor domains (up to 3 — used across all audits)
```

---

## 4. Tier Routing Logic

Every skill must implement this at the top, before any data collection:

```
TIER = [Free | Standard | Deep Dive]  ← set during intake

if TIER == Free:
  - Run surface scan only (Steps 1–2 of each skill)
  - Output: overall score, 1 finding in full, all other findings locked
  - No human review flag
  - Delivery: minutes
  - Report: Free tier HTML template (scores + 1 finding + locked section visual)

if TIER == Standard:
  - Run full analysis (all steps)
  - Output: all findings, before/after, priority roadmap, benchmarks
  - Set human_review_required = true (flag in report header)
  - Delivery: 24–48h
  - Report: Full HTML report (Stone/Amber design system)

if TIER == Deep_Dive:
  - Verify required access is present — if not, offer Standard fallback
  - Run full analysis + platform data + tool integrations
  - Set human_review_required = true
  - Set call_required = true (60-min call to schedule)
  - Delivery: 3–5 business days
  - Report: Full HTML report with real data sections populated
```

**Human review flag in report:**
Every Standard and Deep Dive report must include a banner:
```html
<!-- shown in report header -->
<div class="review-flag">
  📋 This report has been queued for human expert review. 
  Final delivery within [24–48h / 3–5 days].
</div>
```

---

## 5. Free Tier Output Format

Free reports are fundamentally different from paid reports. They must feel complete but clearly incomplete.

**Structure:**
1. Cover with overall score (X/100) — no category breakdown
2. "We found [N] issues across [M] categories" — but don't name them
3. One finding shown in full: issue, severity, what it means, how to fix it
4. Remaining findings shown as locked rows:
   - Grey blurred bars (CSS only — no lock emoji, no images)
   - Text: "Unlock [N] more findings — from $[price]"
5. No roadmap. No before/after. No benchmarks.
6. CTA: "Get the full picture" → relevant product URL

**Psychological principle:** Show the shape of the problem, not the solution.

---

## 6. Skill-by-Skill Change Spec

### 6.1 `seo-audit` — Effort: M

**Keep:**
- Steps 1–8c (technical SEO, AI crawler audit, off-site entity, platform AI readiness)
- Evidence labeling system (Observed / Assessment / Not verified)
- Step 9 HTML report (Stone/Amber, micro-upsell callouts, sticky TOC)

**Modify:**
- Add `## Step 0: Tier & Brand Intake` at the very top (before audience routing)
  - Ask tier, brand config, access requirements for tier
  - Audience routing moves to Step 0b (after tier is known)
- Rename all instances of "SEO Audit" → "SiteScore" in report output
- Step 2 "Gather Data" — make URL collection part of intake, not assumed

**Add:**
- Free tier output mode: surface scan only, 1 finding, locked rows
- Deep Dive mode: 
  - Ahrefs Site Audit integration (170+ issues via API or exported CSV)
  - Backlink profile section: DR, referring domains, anchor text, toxic links
  - Keyword rankings section: top ranking pages, positions, estimated traffic
  - Keyword gap analysis vs competitor domains
  - Content opportunity mapping
  - Organic traffic estimates by page
  - Requires GSC + GA4 access check at intake
- Brand config injection into HTML report (replace hardcoded Autonomous tokens)

**New section to add:**
```markdown
## Step 0: Tier & Brand Intake
[intake questions as per Section 3.1 above]

## Step 0b: Audience Routing
[existing audience routing content, now runs after tier is known]
```

---

### 6.2 `analytics-audit` + `analytics-audit-martech` + `analytics-audit-client-report` — Effort: M

**Current mapping:**
- Phase 1 (`analytics-audit`) = Standard tier
- Phase 1 + Phase 2 (`analytics-audit-martech`) = Deep Dive tier
- `analytics-audit-client-report` = HTML report (keep, add brand config)

**Keep:**
- All Phase 1 sections (A–Q): GA4 config, event inventory, conversion accuracy, consent, GSC
- All Phase 2 sections (K–P): MarTech stack, attribution architecture, CDP evaluation
- Scripts: `ga4_collector.py`, `ga4_collector_extra.py`, `gsc_collector.py`
- Adversarial review agent reference

**Modify:**
- Add `## Step 0: Tier & Brand Intake` to top of `analytics-audit/SKILL.md`
  - Standard tier: no platform access required — runs from public observable signals
  - Deep Dive tier: requires GA4 admin + PostHog (if applicable)
- Create explicit gating: 
  ```
  if TIER == Standard: run Phase 1 (public signals only, no API calls)
  if TIER == Deep_Dive AND access_provided: run Phase 1 + Phase 2 with real data
  if TIER == Deep_Dive AND access_missing: offer Standard fallback
  ```
- Rename product: "Revenue Leak Audit" throughout all three skills
- Standard tier framing shift: every deliverable name must use "Revenue Leak" language
  - "GA4 configuration audit" → "Ad spend accountability review"
  - "UTM naming convention audit" → "Campaign credit accuracy check"
  - "Attribution model assessment" → "Budget leakage analysis"
- Add Free tier output to `analytics-audit/SKILL.md`
- Add brand config injection to `analytics-audit-client-report/SKILL.md`

**Remove from primary flow:**
- `analytics-tracking` — this is an implementation skill, not an audit skill. Remove from any references in the audit flow. It can be referenced as "implementation support" after Deep Dive findings.

---

### 6.3 `conversion-audit` — Effort: M (+ design system fix is blocking)

**CRITICAL — Fix first:**
- The skill description, `references/brand.md`, and `assets/template-audit.html` all reference the OLD design system (Fraunces + DM Sans, parchment/vermillion)
- All other skills use Stone/Amber
- This must be fixed before any other changes or reports will be inconsistent

**Fix:**
1. Update `references/brand.md` → replace with Stone/Amber token reference pointing to `~/hazn/skills/design-system/`
2. Delete or archive `assets/template-audit.html` (old Fraunces template)
3. Update SKILL.md "Generate HTML Report" section to use Stone/Amber system (same as `seo-audit` Step 9)
4. Update all CTA links: ensure all use `https://calendly.com/rizwan-20/30min` (audit the file — some may still have old contact links)

**Keep:**
- Three-pillar scoring (Copywriting / SEO / Frontend Design)
- A/B hypotheses framework with traffic feasibility
- CVR projections and ROI template
- CHECKPOINT 1, 2, 3 (human-in-loop review)
- Teaser mode structure (repurpose as Free tier)

**Modify:**
- Add `## Step 0: Tier & Brand Intake` at top
- Rename "Teaser Mode" → "Free Tier" throughout (same concept, new name)
- Rename product: "ConversionIQ" throughout
- Rename pillar "SEO" → remove from ConversionIQ (SEO is SiteScore's job — CRO audit should focus on Copy + Design + UX only, 3 pillars max)

**Add:**
- Deep Dive mode:
  - PostHog session data review section (if PostHog access provided)
  - Real funnel drop-off section (requires GA4)
  - Competitor landing page benchmarks (2–3 competitors, manual web_fetch + screenshot)
  - Full A/B test plan with sequencing
  - ROI projection using real traffic data
- Connect to `ab-test-setup` skill: Deep Dive automatically loads ab-test-setup for the A/B plan section
- Brand config injection

---

### 6.4 `ui-audit` — Effort: L (most new work)

**Current state:** Outputs JSON. Framework-only. No HTML report. No screenshots. Not a client deliverable.

**Keep:**
- Reference library (32 files — UX frameworks, patterns, checklists)
- JSON audit output format (use as internal analysis step, not final output)
- Audience routing (Step 0)

**Add — this is the majority of the work:**

1. **Intake + tier routing** (`## Step 0: Tier & Brand Intake`)

2. **Screenshot capture workflow** (new section, before analysis):
```markdown
## Step 1: Capture Screenshots
Use browser tool to capture:
- Desktop (1440px): homepage + key pages
- Mobile (390px): same pages
Save to: ~/hazn/projects/{client-slug}/ux-audit-{date}/screenshots/
```

3. **HTML report generation** (new section, replaces JSON output):
   - Use Stone/Amber design system
   - Annotated findings: each finding references the screenshot it relates to
   - Screenshot embedding (base64 inline for portability)
   - Effort-rated roadmap (Low / Medium / High — no time estimates)
   - Same micro-upsell callouts + sticky TOC pattern as `seo-audit`
   - Brand config injection

4. **Deep Dive additions:**
   - WCAG 2.1 AA full compliance report section
   - Design system consistency review (if Figma/URL provided)
   - User flow mapping: browser automation traces homepage → conversion path
   - Competitor UX benchmarks: capture + compare screenshots of 2–3 competitors
   - Form UX deep-dive section

5. **Fix skill reference path:**
   - `website-audit` references `~/clawd/skills/ui-audit/SKILL.md` → change to `~/hazn/skills/ui-audit/SKILL.md`

---

### 6.5 `website-audit` → Repurpose as `sitehealth` orchestrator — Effort: L

**Current state:** Modular audit type selection, but wrong skill paths, no bundle identity, no synthesis.

**Rename:** `website-audit` → repurpose as `sitehealth` (or create new `sitehealth/SKILL.md` that replaces it)

**Fix all skill paths:**
```
~/clawd/skills/landing-page-copywriter → ~/hazn/skills/conversion-audit
~/clawd/skills/seo-audit              → ~/hazn/skills/seo-audit
~/clawd/skills/shopify-cro-audit      → ~/hazn/skills/conversion-audit (doesn't exist, use this)
~/clawd/skills/ui-audit               → ~/hazn/skills/ui-audit
```

**Core orchestration logic to add:**

```markdown
## SiteHealth Execution Flow

1. Run shared intake (Section 2 of spec)
2. Confirm: "I'll run all 4 audits. This will take [24–48h Standard / 3–5 days Deep Dive]."
3. Spawn 4 parallel subagent sessions:
   - subagent_1: seo-audit (SiteScore) with shared intake params
   - subagent_2: analytics-audit (Revenue Leak) with shared intake params  
   - subagent_3: conversion-audit (ConversionIQ) with shared intake params
   - subagent_4: ui-audit (UX/UI) with shared intake params
4. Wait for all 4 to complete
5. Collect all 4 report URLs + finding summaries
6. Run cross-audit synthesis (new section — see below)
7. Generate unified roadmap
8. Generate SiteHealth cover report (links to all 4 + unified roadmap)
9. Deliver: 5 URLs (4 individual + 1 bundle summary)
```

**Cross-audit synthesis section (new):**
```markdown
## Cross-Audit Synthesis

After all 4 audits complete:
1. Collect top 5 findings from each audit (20 findings total)
2. Identify cross-cutting themes (e.g. "attribution is broken AND conversion tracking is wrong" = one root cause)
3. Identify dependencies (e.g. "fix GA4 before running A/B tests")
4. Build unified roadmap:
   - Sequence by: (a) dependency order, (b) effort level, (c) impact
   - Group by: Quick wins (Low effort) / This sprint / Next quarter
5. Generate the 90-min strategy call prep doc:
   - Top 3 cross-audit insights
   - Recommended starting point
   - Expected ROI of fixing top issues
```

---

## 7. New Files / Skills to Create

| File | Purpose |
|------|---------|
| `~/hazn/brands/autonomous.json` | Default Autonomous brand config |
| `~/hazn/brands/README.md` | How to add a new partner brand |
| `~/hazn/skills/sitehealth/SKILL.md` | SiteHealth bundle orchestrator (new or repurposed from website-audit) |
| `~/hazn/skills/seo-audit/references/ahrefs-integration.md` | Ahrefs API usage, exported CSV format, what to pull and how |
| `~/hazn/skills/conversion-audit/references/brand.md` | Updated to Stone/Amber (replace current Fraunces/vermillion version) |

---

## 8. Execution Order

| Priority | Task | Skill | Effort | Reason |
|----------|------|-------|--------|--------|
| 1 | Fix design system in `conversion-audit` | conversion-audit | S | Blocking — mixed brand reports can't ship |
| 2 | Create `~/hazn/brands/autonomous.json` + schema | (new file) | S | Required by all skills before brand config works |
| 3 | Add tier routing + intake to `seo-audit` | seo-audit | M | Most production-ready, fastest win |
| 4 | Add tier routing + intake to `analytics-audit` | analytics-audit | M | Phase 1/2 split already exists |
| 5 | Add tier routing + intake to `conversion-audit` | conversion-audit | M | Design fix done first, then tier routing |
| 6 | Build HTML report + screenshots for `ui-audit` | ui-audit | L | Biggest gap, most new work |
| 7 | Add Ahrefs integration to `seo-audit` Deep Dive | seo-audit | M | External tool dependency |
| 8 | Build `sitehealth` orchestrator | sitehealth | L | Needs all 4 solid first |

---

## 9. Shared Design Tokens Reference

All HTML reports use Stone/Amber. The canonical token source is:
`~/hazn/skills/design-system/` or `~/hazn/skills/conversion-audit/references/brand.md` (once updated)

Every skill that generates HTML must import from this shared source — no hardcoded colour values in individual skills.

Key tokens:
```css
--stone-900: #1c1917  /* dark sections */
--amber-500: #f59e0b  /* CTAs */
--stone-50:  #fafaf9  /* backgrounds */
```

All CTAs link to: `https://calendly.com/rizwan-20/30min` (or brand_config.cta_url in white-label mode)

---

## 10. What This Spec Does NOT Cover (yet)

- Webhook / web form trigger (Surface 2)
- Partner API (Surface 3)
- Email delivery of reports to clients
- Payment gating (confirming a client has paid before running)
- Job state tracking / retry on failure
- Ahrefs API key management

These are documented here for future spec. Don't build them now.

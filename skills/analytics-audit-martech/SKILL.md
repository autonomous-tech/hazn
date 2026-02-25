---
name: MarTech & Attribution Audit
description: >
  This skill should be used when the user asks to "audit attribution", "analyze martech stack",
  "evaluate CDP", "audit ad platform integration", "check server-side tracking",
  "review conversion setup", "build implementation roadmap", or wants Phase 2 of a
  MarTech audit. It guides the full MarTech stack analysis, attribution architecture
  design, and implementation roadmap for Shopify stores.
version: 1.0.0
---

# MarTech & Attribution Audit — Phase 2

Expand a Phase 1 GA4 audit into a comprehensive MarTech & Attribution assessment. This produces sections K-P of the full audit report. Steps 5-11 below continue from the GA4 & Site Inspection Audit skill (Steps 1-4).

Refer to `.hazn/skills/analytics-audit/references/report-template.md` for the expected output structure of sections K-P.

## Prerequisites

Phase 1 must be complete with:
- `.hazn/outputs/analytics-audit/ga4_audit_data.json` — GA4 property data
- `.hazn/outputs/analytics-audit/ga4_audit_extra.json` — Extended engagement/browser/keyword data
- `.hazn/outputs/analytics-audit/site_inspection.json` or site inspection notes — tracking code inventory
- `.hazn/outputs/analytics-audit/<domain>-audit.md` — Phase 1 report (sections A-J)

## Step 5: MarTech Stack Audit (Section K)

Build a complete inventory of every marketing technology tool on the site.

### Technology Layers to Document

| Layer | What to Look For |
|-------|-----------------|
| Tag Management | GTM containers (how many? who installed each?), Shopify Web Pixels Manager, direct gtag.js |
| Web Analytics | GA4 (property ID, measurement ID), any legacy UA |
| CRM / Marketing | HubSpot (portal ID — which is primary?), Salesforce, etc. |
| Ad Platforms | Google Ads (conversion labels), Meta Pixel + CAPI status, Bing UET, TikTok, etc. |
| Session Recording | Hotjar, Microsoft Clarity, FullStory, Lucky Orange — flag redundancies |
| Call Tracking | CallRail, CallTrackingMetrics — does it pass click IDs to CRM? |
| Chat / Sales Bot | Memox, Intercom, Drift, Tidio — is it a lead capture tool or full sales channel? |
| Invoicing / ERP | Method, QuickBooks, NetSuite — where does offline revenue live? |
| Email Marketing | HubSpot email, Mailchimp, Klaviyo — flag redundancies with CRM |
| Fraud Detection | TrafficGuard, ClickCease, etc. |
| Other | Country blockers, review widgets, A/B testing tools |

### Data Flow Map
Create an ASCII diagram showing how data flows between systems. Key questions:
- Which systems talk to each other?
- Where are the dead ends (data goes in but never comes back)?
- Which revenue channels are invisible to ad platforms?

### Redundancy Analysis
Identify tools that overlap and recommend consolidation.

## Step 6: Attribution Architecture (Section L)

### Current State Analysis
Document every close/revenue channel and whether it feeds back to ad platforms:

| Close Channel | Revenue Visible? | Pixel Feedback? | Attribution Status |
|---------------|-----------------|----------------|-------------------|
| Shopify auto-checkout | Yes | Yes | Working |
| [Bot/chat sales] | ? | None | BLIND SPOT |
| [Phone/call tracking] | ? | None | BLIND SPOT |
| [Invoiced/B2B sales] | ? | None | BLIND SPOT |

### Root Cause Analysis
Document each specific reason attribution is broken. Common patterns:
1. Client-side only tracking (degraded by ITP, ad blockers)
2. No server-side events (Enhanced Conversions, CAPI)
3. Revenue in multiple siloed systems
4. Chat bot as full sales channel but invisible to ads
5. No offline conversion import loop
6. UTM parameter chaos (same platform, multiple source/mediums)
7. Inflated GA4 conversions feeding garbage to Smart Bidding
8. CRM attribution capabilities unused
9. Multiple CRM portals / accounts creating confusion

### Signal Loss Quantification
Calculate from browser data:
- Safari % of total sessions (ITP impact)
- Desktop % (ad blocker exposure)
- Estimated % of conversions invisible to ad platforms

### CAPI / Server-Side Status
Check what's already partially implemented:
- Shopify Trekkie S2S (`facebookCapiEnabled`)
- Any sGTM endpoints
- Enhanced Conversions for Leads
- Bing offline import

### Ideal Architecture Design
Design the target-state with ALL revenue channels feeding back through the CRM to ad platforms.

Key principle: **CRM becomes single source of truth. Every close channel writes to CRM. CRM exports offline conversions with revenue to ad platforms.**

## Step 7: CDP Evaluation (Section M)

Evaluate whether the client needs a Customer Data Platform.

### Decision Framework

**Lean toward NO CDP if:**
- <100K sessions/month
- <4 major data sources
- CRM already has workflow automation (HubSpot Pro/Enterprise)
- sGTM can handle event routing
- The real problem is missing plumbing, not identity stitching

**Lean toward CDP if:**
- >500K sessions/month
- 6+ data sources with separate identity systems
- Complex identity stitching beyond CRM capabilities
- Need real-time event routing at scale
- CRM workflows can't handle the data volume

### Options to Evaluate
Always compare these three tiers:
1. **CRM as pseudo-CDP** (cheapest, fastest) — e.g., HubSpot + sGTM
2. **Mid-tier CDP** (cost-effective) — e.g., RudderStack ($500-2K/mo)
3. **Enterprise CDP** (gold standard) — e.g., Segment ($120K+/year)

## Step 8: Google Ads Optimization (Section N)

### Conversion Action Audit
From the Shopify Web Pixels Manager config, map every event that sends to Google Ads:
- List each event type with its Ads conversion label
- Identify which are primary vs secondary
- Flag non-conversions being sent as conversions (view_item, page_view, search)
- Calculate signal-to-noise ratio

### Recommended Restructuring
Define:
- **Primary conversions** (purchase, qualified_lead, offline_purchase) — bidding optimizes toward these
- **Secondary conversions** (observe only) — add_to_cart, begin_checkout, phone_call
- **Remove entirely** — view_item, page_view, search, any engagement-level events

### Enhanced Conversions & Offline Import
Design the implementation for:
- Enhanced Conversions for Leads (hash email/phone on form submit)
- Offline conversion import from CRM (gclid + revenue on deal close)
- Value-based bidding recommendations per campaign type

## Step 9: Channel Attribution & Reporting (Section O)

### GA4 Attribution
- Attribution model recommendation (usually Data-Driven)
- Lookback window settings (90d for high-ticket)
- Google Signals status

### CRM Attribution
- Multi-touch attribution report configuration
- Revenue attribution by source setup
- Ads integration for spend data

### Custom Channel Grouping
Design channel groups that consolidate fragmented sources (especially Facebook multi-source splits).

### First-Party Data Strategy
- Click ID persistence (gclid/fbclid/msclkid in cookies + CRM)
- Email-based matching (Enhanced Conversions, Advanced Matching)
- Server-side cookie writing

## Step 10: Implementation Roadmap (Section P)

Build a phased 90-day plan:

### Week 1-2: Stop the Bleeding
Fix the things actively harming ad performance RIGHT NOW:
- Remove false conversions from Google Ads
- Fix key event definitions in GA4
- Fix timezone
- Remove redundant tools

### Week 3-4: Server-Side Foundation
Set up the infrastructure:
- sGTM via Stape on first-party subdomain
- Meta CAPI (full events, not just checkout)
- Google Enhanced Conversions for Leads
- Bing UET server-side
- UTM standardization
- GTM container consolidation

### Week 5-6: Offline Conversion Loop (The Big Unlock)
Connect all revenue channels back to ad platforms:
- Click ID capture + CRM storage
- Bot → CRM integration
- Call tracking → CRM integration
- Invoice system → CRM deal sync
- CRM → Google Ads offline import
- CRM → Meta offline import
- CRM → Bing offline import

### Week 7-8: Attribution & Reporting
Build the measurement layer:
- CRM multi-touch attribution
- GA4 custom channel groups + custom dimensions
- Audiences for remarketing
- Missing e-commerce events

### Week 9-12: Optimize & Scale
Leverage clean data:
- Executive dashboard (Looker Studio)
- Value-based bidding in Google Ads
- Consent Mode v2 proper implementation
- Script bloat reduction
- Data quality alerting

### Deliverable Format
Each task should have: task #, description, owner, effort estimate, impact statement.
Include cost summary and expected ROI table.

## Step 10.5: Write Phase 2 Report Sections (K-P)

Append sections K-P to the existing Phase 1 report at `.hazn/outputs/analytics-audit/<domain>-audit.md`. Follow the section structure defined in `.hazn/skills/analytics-audit/references/report-template.md`. Use the `analytics-report-writer` agent for full report generation if both phases are being written together.

## Step 11: Run Adversarial Review

After the full report is written, launch the `analytics-adversary` agent to red-team the report:
> Red-team the audit report at .hazn/outputs/analytics-audit/<domain>-audit.md against the data files

The adversary will challenge every number, flag weak claims, and find inconsistencies. Fix any valid issues before delivering to the client.

---
name: GA4 & Site Inspection Audit
description: >
  This skill should be used when the user asks to "audit a website", "audit GA4", "inspect tracking",
  "check analytics setup", "review tags", "audit a Shopify store", "check GA4 configuration",
  "run an analytics audit", "evaluate GA4 setup", or wants to perform Phase 1 of a MarTech audit.
  It guides the complete GA4 property assessment and live site tracking code inspection, with
  Shopify-specific checks for Web Pixels Manager and Trekkie S2S configurations.
version: 1.0.0
---

# GA4 & Site Inspection Audit — Phase 1

Run a comprehensive GA4 property audit and live site tracking inspection. This is Phase 1 of the full MarTech & Attribution audit.

## Prerequisites

Before starting, confirm with the user:
1. **Site URL** — the Shopify store domain (e.g., `containerone.net`)
2. **GA4 Property ID** — numeric ID (e.g., `373350812`)
3. **Output directory** — where to save data and report (default: `.hazn/outputs/analytics-audit/`)
4. **OAuth credentials** — at `~/.config/ga4-audit/credentials.json` for GA4 API access

## Step 1: Collect GA4 Data via API

Run the GA4 collector scripts to pull all property data:

```bash
# Primary dataset: property config, events, conversions, traffic, campaigns, ecommerce
python .hazn/scripts/analytics-audit/ga4_collector.py <PROPERTY_ID> .hazn/outputs/analytics-audit/ga4_audit_data.json --days 30

# Extended dataset: engagement, browsers, UTMs, keywords, weekly trends
python .hazn/scripts/analytics-audit/ga4_collector_extra.py <PROPERTY_ID> .hazn/outputs/analytics-audit/ga4_audit_extra.json --days 90
```

If the scripts fail (missing credentials, wrong property ID), troubleshoot:
- Verify property ID is correct (numeric only, no "G-" prefix)
- Check OAuth token at `~/.config/ga4-audit/token.json`
- Re-run auth flow if token expired

## Step 1b: Collect Google Search Console Data

If the user has GSC access for the site, collect organic search data:

```bash
# Discover available GSC properties (if site_url format is unknown)
python .hazn/scripts/analytics-audit/gsc_collector.py --discover

# Collect GSC data (90 days, with brand term classification)
python .hazn/scripts/analytics-audit/gsc_collector.py <SITE_URL> .hazn/outputs/analytics-audit/gsc_audit_data.json --days 90 --brand-terms "<brand_term1>,<brand_term2>"
```

**Site URL format:**
- Domain property: `sc-domain:example.com`
- URL prefix property: `https://www.example.com/`

**Prerequisites:**
- Google Search Console API enabled in Cloud Console
- OAuth credentials with `webmasters.readonly` scope (the collector will trigger re-auth if needed)
- User must have at least read access to the GSC property

If GSC collection fails (no access, API not enabled), continue the audit without it. Section Q will be skipped in the report.

## Step 2: Inspect Live Site HTML Source

Use the `analytics-inspector` agent to analyze the site's tracking implementation. The agent will:

1. **Fetch HTML source** via `curl -sL <URL>`
2. **Extract and identify:**
   - GTM container IDs (GTM-xxx) and their HTML comments/labels
   - HubSpot tracking code and portal IDs
   - Facebook/Meta pixel IDs and CAPI status
   - Google Ads conversion labels and Enhanced Conversions config
   - Bing UET tag IDs
   - Session recording tools (Hotjar, Clarity, FullStory)
   - Chat/bot embeds (Memox, Intercom, Drift, etc.)
   - Call tracking (CallRail, etc.)
   - Consent mode configuration (gtag consent default values)
   - Shopify Web Pixels Manager `webPixelsConfigList` JSON
   - Shopify Trekkie S2S config (facebookCapiEnabled, isServerSideCookieWritingEnabled)
   - All external script URLs
   - dataLayer push configurations

3. **Save findings** to `.hazn/outputs/analytics-audit/site_inspection.json`

Launch the analytics-inspector agent with:
> Inspect the tracking implementation at <URL> and save findings to .hazn/outputs/analytics-audit/site_inspection.json

If the analytics-inspector agent is not available, manually run `curl -sL <URL>` and parse the HTML for the items listed in the extraction checklist above.

## Step 3: Analyze GA4 Property Configuration

From the collected data, assess:

### Property Settings
- **Time zone** — flag if timezone does not match business headquarters
- **Currency** — correct for the market?
- **Industry** — correctly categorized?
- **Created date** — how much historical data exists?

### Event Inventory
For each event, determine:
- Is it an auto-collected, enhanced measurement, recommended, or custom event?
- What's the event count vs user count? (High ratio = possible duplication)
- Are key e-commerce events present? (`view_item`, `add_to_cart`, `begin_checkout`, `add_payment_info`, `purchase`)
- Are any funnel steps broken? (e.g., `begin_checkout` = 1 but `purchase` = 157)
- Is `contentType` or other event parameters populated, or all `(not set)`?

### Conversion/Key Event Assessment
For each key event:
- Is the conversion rate realistic? (>20% on a non-brand event = likely inflated)
- How many events per user? (>2 per user = probably firing on repeated interactions)
- Should this be a key event or just a regular event?

**Red flag patterns:**
- ZIP code / price check counted as conversion
- `view_item` sent as Google Ads conversion
- `form_submit` enhanced measurement without filtering to meaningful forms
- Page views or scrolls marked as conversions

### Traffic & Attribution Quality
- What % of sessions have `(not set)` campaign? (>10% = attribution gap)
- What % have `(not set)` source/medium? (>5% = tracking gap)
- Is there source fragmentation? (Same platform in 3+ source/medium variants = UTM chaos)
- How much is Direct traffic? (>30% = possible attribution leakage)

### Google Ads Integration
- What conversion actions are configured? (Check Shopify Web Pixels Manager config)
- Are non-conversion events (view_item, page_view, search) being sent as Ads conversions?
- What's the keyword/query data quality?
- Are campaign names current or stale?

## Step 4: Write Phase 1 Sections (A-J)

Generate the initial audit report sections:

| Section | Title | Content |
|---------|-------|---------|
| A | Property Configuration Assessment | Settings table, timezone check, issues |
| B | Tagging Implementation Review | Tag architecture, script inventory, gtag config, pixel/cookie table |
| C | Event Tracking Completeness | Event inventory table, funnel analysis, missing events |
| D | Conversion Setup & Accuracy | Key events table, inflation analysis, purchase tracking |
| E | Google Ads Integration Health | Ads config, campaign performance, keyword data, issues |
| F | Data Quality Assessment | Attribution quality, UTM hygiene, source fragmentation, geo/device |
| G | Gap Analysis & Recommendations | Priority 1-4 recommendations with specific actions |
| H | Consent & Privacy Assessment | Consent mode config, compliance status |
| I | Platform Ecosystem Summary | ASCII diagram of all tracking systems and data flows |
| J | Benchmarks & KPIs | 30-day metrics table vs e-commerce benchmarks |
| Q | Organic Search Performance (GSC) | Search visibility, brand/non-brand, top queries, landing pages, cannibalization, devices, trends, GSC-GA4 reconciliation, opportunities |

Follow the report structure defined in `.hazn/skills/analytics-audit/references/report-template.md` for section formatting and expected content.

Write the report to `.hazn/outputs/analytics-audit/<domain>-audit.md`.

## Reference: Shopify Web Pixels Manager Config

On Shopify stores, the `webPixelsConfigList` JSON in the page source reveals:
- Which Shopify app pixels are active (GA4, Meta, Mailchimp, etc.)
- The exact Google Ads conversion labels for each event type
- Facebook pixel ID and configuration
- Privacy/consent purpose assignments per pixel
- Data sharing state (optimized, restricted, etc.)

Parse this carefully — it's often the most reliable source of truth for what's actually firing.

## Reference: Common Shopify Tracking Stacks

| Pattern | Tools | Notes |
|---------|-------|-------|
| **Shopify native** | Web Pixels Manager + Trekkie S2S | Basic but has CAPI for Meta |
| **Analyzify** | GTM container + dataLayer enhancements | Popular Shopify app, installs its own GTM |
| **Elevar** | Server-side GTM + dataLayer | Enterprise option, adds sGTM |
| **Stape** | Server-side GTM hosting | Usually paired with Elevar or custom setup |
| **Manual GTM** | Agency-installed GTM container | Often alongside Shopify native — creates duplication |

When you see 2+ GTM containers, check if one is from a Shopify app and one is agency-installed.

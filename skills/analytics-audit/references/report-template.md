# MarTech & Attribution Audit Report: [DOMAIN]

**Audit Date:** [DATE]
**Property:** [PROPERTY_NAME] - GA4 (ID: [PROPERTY_ID])
**Measurement ID:** [MEASUREMENT_ID]
**Google Ads ID:** [ADS_ID]
**Platform:** Shopify ([MYSHOPIFY_DOMAIN])
**Data Period:** Last 30 days (unless noted)
**Scope:** Full MarTech stack audit, attribution architecture review, ad platform optimization, 90-day implementation roadmap

---

## Executive Summary

[2-3 paragraph summary covering:
- Overall state of analytics implementation
- The attribution problem (what % of conversions are invisible to ad platforms)
- Key Phase 1 findings (5 bullets)
- Key Phase 2 findings (5-8 bullets)
- Overall scores: GA4 Implementation (X/100), Attribution (X/100)]

---

## A. Property Configuration Assessment

### GA4 Property Settings
[Table: Setting | Value | Assessment]

### Issues Found
[Timezone, currency, industry misconfigurations]

---

## B. Tagging Implementation Review

### Tag Architecture
[Table: System | ID | Location | Method]
[Analysis of dual/triple loading, deduplication risks]

### Script Footprint Analysis
[Table: Category | Scripts | Notes]
[Total script count, performance impact]

### gtag.js Configuration Details
[Code block with GA4 config, Ads config, consent defaults]

### Verified Tracking Pixels & Cookies
[Table: Tracker | Active | Cookie Set]

---

## C. Event Tracking Completeness

### Event Inventory (Last 30 Days)
[Table: Event | Count | Users | Type | Assessment]

### Critical Gaps
[Broken events, missing recommended events, missing custom parameters]

---

## D. Conversion Setup & Accuracy

### Configured Key Events
[Table: Key Event | Events | Users | Conv. Rate | Assessment]

### Conversion Inflation Analysis
[Detailed analysis of any inflated conversions]

### Purchase Tracking
[Revenue analysis, transaction verification]

---

## E. Google Ads Integration Health

### Ads Configuration
[Table: Setting | Value]

### Campaign Performance
[Table: Campaign | Sessions | Conversions | Conv. Rate]

### Top Keywords
[Table: Keyword | Sessions | Conversions]

### Issues & Recommendations
[Specific Ads fixes needed]

---

## F. Data Quality Assessment

### Attribution Quality
[Table: Dimension | (not set) / Missing | % of Total | Severity]

### UTM Parameter Hygiene
[List of active mediums, issues with non-standard values]

### Source Fragmentation
[Analysis of fragmented sources (especially Facebook)]

### Direct Traffic Analysis
### Geographic Quality
### Device Split
### New vs. Returning Users

---

## G. Gap Analysis & Recommendations

### Priority 1: CRITICAL (Implement within 1 week)
### Priority 2: HIGH (Implement within 2-4 weeks)
### Priority 3: MEDIUM (Implement within 1-2 months)
### Priority 4: LOW (Ongoing optimization)

---

## H. Consent & Privacy Assessment

[Table: Signal | Default Value | Compliant?]
[CMP status, integration with consent mode]

---

## I. Platform Ecosystem Summary

```
[ASCII architecture diagram showing all tracking systems and data flows]
```

---

## J. Benchmarks & KPIs (30-Day Snapshot)

[Table: Metric | Value | E-commerce Benchmark | Assessment]

---

## K. MarTech Stack Audit

### Complete Technology Inventory
[Table: Layer | Tool | ID / Config | Role | Status | Issues]

### Data Flow Map
```
[ASCII diagram showing data flows between all systems]
```

### Redundancy Analysis
[Table: Redundancy | Tools | Recommendation]

---

## L. Attribution Architecture — Current State vs. Ideal

### Current State: Why Attribution is Broken
[Table: Close Channel | Revenue Visibility | Pixel Feedback | Attribution Status]

#### Root Causes of Broken Attribution
[Numbered list of specific issues with evidence]

### Signal Loss Quantification
[Table: Browser | Sessions | % of Total | Signal Impact]
[Ad blocker impact estimates]
[Combined signal loss calculation]

### Server-Side Tracking Status
[What's implemented vs. what's missing — CAPI, Enhanced Conversions, etc.]

### Ideal Architecture
```
[ASCII diagram of target-state architecture with all channels feeding back]
```

[Key architectural principles]

---

## M. CDP Evaluation

### The Case FOR a CDP
### The Case AGAINST a CDP

### Options Evaluated
[Table: Option | Monthly Cost | Setup Time | Identity Stitching | Event Routing | Fits Scale?]

### Verdict
[Clear recommendation with reasoning]

---

## N. Google Ads Optimization Architecture

### Current Conversion Action Problems
[Table: Event Type | Ads Conversion Label | Should Be Primary? | Issue]

### Recommended Restructuring
[Primary conversions table, secondary conversions table, removals]

### Enhanced Conversions for Leads Setup
[Implementation steps]

### Offline Conversion Import
[Flow diagram and steps]

### Value-Based Bidding Recommendations
[Table: Campaign Type | Current Bidding | Recommended | Why]

### Campaign & Keyword Assessment
[Tables with performance data and recommendations]

---

## O. Channel Attribution Recommendations

### GA4 Attribution Model Configuration
### CRM Multi-Touch Attribution Configuration
### Custom Channel Grouping Design
[Table: Custom Channel | Rules | Current Misclassification]

### Cross-Platform Attribution Reconciliation
### First-Party Data Strategy

---

## P. Implementation Roadmap — 90-Day Plan

### Week 1-2: Stop the Bleeding
[Table: # | Task | Owner | Effort | Impact]

### Week 3-4: Server-Side Foundation
[Table: # | Task | Owner | Effort | Impact]

### Week 5-6: Offline Conversion Loop
[Table: # | Task | Owner | Effort | Impact]

### Week 7-8: Attribution & Reporting
[Table: # | Task | Owner | Effort | Impact]

### Week 9-12: Optimize & Scale
[Table: # | Task | Owner | Effort | Impact]

### Cost Summary
[Table: Item | Monthly Cost | One-Time Setup]

### Expected ROI
[Table: Metric | Before | After | Improvement]

---

## Q. Organic Search Performance (GSC)

> **Data source:** `output/gsc_audit_data.json` — Google Search Console API data
> **Note:** If GSC data is not available, skip this section and note "GSC data not collected for this audit."

### Search Visibility Summary
[Table: Metric | 90-Day Total | 30-Day Total | 30d Change % ]
[Total clicks, impressions, average CTR, average position]

### Brand vs Non-Brand Analysis
[Table: Segment | Clicks | Impressions | CTR | Click Share]
[Business implications: brand dependency, non-brand growth potential]

### Top Non-Brand Queries
[Table: Query | Clicks | Impressions | CTR | Avg Position | Opportunity Flag]
[Flag high-impression/low-CTR queries and position 5-20 opportunities]

### Top Landing Pages (Organic)
[Table: Page | GSC Clicks | GSC Impressions | GA4 Organic Sessions | Engagement Rate]
[Cross-reference with GA4 landing page data from Section F]

### Query Cannibalization
[Table: Query | Competing Pages | Impressions Split | Severity]
[For each flagged query: which pages compete, recommended consolidation]

### Device Performance
[Table: Device | Clicks | Impressions | CTR | Avg Position]
[Cross-reference with GA4 device data from Section F]
[Flag mobile-specific issues: poor mobile CTR, position gaps vs desktop]

### Weekly Trends
[Table: Week | Clicks | Impressions | CTR | Avg Position]
[Growth trajectory commentary: accelerating, stable, declining]

### Geographic Distribution
[Table: Country | Clicks | Impressions | CTR | Avg Position]
[Cross-reference with GA4 country data from Section F]

### GSC vs GA4 Reconciliation
[Table: Metric | GSC Value | GA4 Value | Gap % | Assessment]
[Compare: GSC total clicks vs GA4 organic sessions]
[Expected gap: 10-20% (normal). >25% = possible tracking issue. Explain common causes.]

### Organic Search Opportunities
1. **High-Impression / Low-CTR Queries** — queries with position 1-10 but CTR below expected for position
2. **Position 5-20 Movers** — queries with rising impressions that could reach page 1 with content investment
3. **Content Gaps** — competitor queries not appearing in inventory
4. **Rising Queries** — 30-day period-over-period movers with significant click growth
5. **Declining Queries** — queries losing clicks that need investigation

---

## Appendix: Data Collection Methodology

### Phase 1: GA4 & Site Inspection
- GA4 Data API v1beta — queried via OAuth2
- HTML source inspection — tracking code inventory
- Network request analysis (if Playwright available)

### GSC: Organic Search Data
- Google Search Console API — queried via OAuth2
- 90-day query, page, device, country, and trend data
- Brand/non-brand classification using provided brand terms
- Cannibalization detection via query×page cross-analysis

### Phase 2: MarTech & Attribution Deep-Dive
- Shopify Web Pixels Manager analysis
- Trekkie S2S configuration analysis
- CRM portal identification
- Browser distribution analysis for ITP impact quantification
- Conversion action mapping from ad platform configs

### Data Sources
- `output/ga4_audit_data.json`
- `output/ga4_audit_extra.json`
- `output/gsc_audit_data.json`
- `output/site_inspection.json`
- Live site HTML source

---

*Report generated by Analytics Audit Agent*
*GA4 Property: [PROPERTY_ID] | Measurement ID: [MEASUREMENT_ID]*

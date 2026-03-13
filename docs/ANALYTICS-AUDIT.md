# Analytics Audit — Setup & Usage Guide

Run comprehensive MarTech & Attribution audits on Shopify stores with GA4 and optional Google Search Console data.

---

## Prerequisites

### 1. Python 3.10+ with GA4 API dependencies

```bash
cd your-project
python3 -m venv .venv && source .venv/bin/activate
pip install -r .hazn/scripts/analytics-audit/requirements.txt
```

### 2. GA4 API OAuth Credentials

1. Create a Google Cloud project with the **GA4 Data API** enabled
2. Create **OAuth 2.0 credentials** (Desktop application type)
3. Download the credentials JSON file
4. Save it to `~/.config/ga4-audit/credentials.json`

The first time you run the collector scripts, a browser window will open for OAuth consent. The token is cached at `~/.config/ga4-audit/token.json`.

### 3. GA4 Property Access

You need Viewer (or higher) access to the GA4 property you're auditing. Get the numeric Property ID from **GA4 Admin > Property Settings**.

### 4. Google Search Console (Optional)

For organic search analysis (Section Q):
1. Enable the **Search Console API** in your Google Cloud project
2. Ensure the OAuth credentials include `webmasters.readonly` scope (the collector handles re-auth)
3. Have at least read access to the GSC property

---

## Quick Start

```
/hazn-analytics-audit containerone.net 373350812
```

This kicks off the full 5-phase workflow:

1. **Setup** — creates output directory, confirms scope
2. **Data Collection** — runs GA4 API collectors + GSC collector + site HTML inspection (parallel)
3. **Analysis & Report** — generates the full A-Q audit report
4. **Adversarial Review** — red-teams the report for accuracy
5. **Client Report** — generates branded HTML client deliverable

---

## Manual / Step-by-Step

You can also run individual components:

### Collect GA4 data
```bash
source .venv/bin/activate
python .hazn/scripts/analytics-audit/ga4_collector.py 373350812 .hazn/outputs/analytics-audit/ga4_audit_data.json --days 30
python .hazn/scripts/analytics-audit/ga4_collector_extra.py 373350812 .hazn/outputs/analytics-audit/ga4_audit_extra.json --days 90
```

### Collect GSC data
```bash
python .hazn/scripts/analytics-audit/gsc_collector.py --discover  # list available properties
python .hazn/scripts/analytics-audit/gsc_collector.py sc-domain:containerone.net .hazn/outputs/analytics-audit/gsc_audit_data.json --days 90 --brand-terms "container one,containerone"
```

### Inspect site tracking
> Inspect the tracking implementation at containerone.net and save findings to .hazn/outputs/analytics-audit/site_inspection.json

### Write the report
> Write the audit report for containerone.net using the data in .hazn/outputs/analytics-audit/

### Red-team the report
> Red-team the audit report at .hazn/outputs/analytics-audit/containerone-audit.md against the data files

### Generate HTML client report
> Create the HTML client report for containerone.net from the audit data and markdown report

---

## Agents

| Agent | Role |
|-------|------|
| **Analytics Inspector** | Fetches site HTML, identifies all tracking codes, pixels, and configurations |
| **Analytics Report Writer** | Generates comprehensive A-Q audit report from collected data |
| **Analytics Adversary** | Red-team review — challenges numbers, flags unsupported claims |
| **Analytics Client Reporter** | Converts markdown audit into branded HTML client report |

---

## Skills

| Skill | Purpose |
|-------|---------|
| `analytics-audit` | Phase 1 methodology — GA4 property audit + site tracking inspection |
| `analytics-audit-martech` | Phase 2 methodology — MarTech stack, attribution architecture, roadmap |
| `analytics-audit-client-report` | HTML client report design system and component library |

---

## Output Files

All output goes to `.hazn/outputs/analytics-audit/`:

| File | Description |
|------|-------------|
| `ga4_audit_data.json` | Primary GA4 data (property, events, conversions, traffic, campaigns, ecommerce) |
| `ga4_audit_extra.json` | Extended data (engagement, browsers, UTMs, keywords, weekly trends) |
| `gsc_audit_data.json` | Organic search data (queries, landing pages, brand analysis, cannibalization) |
| `site_inspection.json` | Tracking code inventory from HTML source |
| `<domain>-audit.md` | Full markdown audit report (sections A-Q) |
| `client-report/index.html` | Branded HTML client report |

---

## Report Sections

| Section | Title |
|---------|-------|
| A | Property Configuration Assessment |
| B | Tagging Implementation Review |
| C | Event Tracking Completeness |
| D | Conversion Setup & Accuracy |
| E | Google Ads Integration Health |
| F | Data Quality Assessment |
| G | Gap Analysis & Recommendations |
| H | Consent & Privacy Assessment |
| I | Platform Ecosystem Summary |
| J | Benchmarks & KPIs |
| K | MarTech Stack Audit |
| L | Attribution Architecture (Current vs Ideal) |
| M | CDP Evaluation |
| N | Google Ads Optimization Architecture |
| O | Channel Attribution Recommendations |
| P | Implementation Roadmap (90-Day Plan) |
| Q | Organic Search Performance (GSC) |

---

## Relationship to `analytics-tracking` Skill

The existing `analytics-tracking` skill covers **implementation** of tracking on new Next.js sites (GA4 + PostHog setup). The analytics-audit skills cover **auditing** of existing GA4/GSC data on live sites. They are complementary:

- `analytics-tracking` → Set up measurement on new sites
- `analytics-audit` → Audit measurement on existing sites

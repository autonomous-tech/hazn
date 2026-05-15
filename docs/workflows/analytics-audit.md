# Analytics & MarTech Audit

> Full GA4 property inspection, site tracking code inventory, MarTech stack analysis, attribution architecture design, adversarial review, and polished HTML client report.

## When to Use

- Client wants to understand what's actually tracked vs what they think is tracked
- Ad platform performance is unexplainably poor — suspect attribution or data quality issues
- Pre-engagement audit to justify retainer scope
- Post-implementation audit after GA4 migration or MarTech stack change
- Client is spending on Smart Bidding but suspects it's training on corrupted conversion data

**NOT for:**
- Prospects with no credentials — use `/hazn-analytics-teaser` instead
- Sites with no GA4 or Google Analytics implementation at all
- Quick visual/UX audits → use `/hazn:audit`

## Requirements

- **GA4 property ID** (format: `12345678`) — required
- **OAuth credentials** configured for the GA4 API — required, must be set up per client
- **Site URL** — required
- **Google Search Console site URL** — optional (enables Section Q: organic search analysis)
- Python virtual environment with `google-analytics-data`, `google-searchconsole` installed

## How It Works

### Phase 1 — Setup (~15 minutes)
Parse site URL, GA4 property ID, optional GSC URL. Verify Python venv and dependencies. Create output directory at `.hazn/outputs/analytics-audit/`.

### Phase 2 — Data Collection (~30–60 minutes, parallel)
**Agent:** Analytics Inspector  
Three parallel tracks:

**GA4 data:** Property config, events, conversions, traffic sources, campaigns, ecommerce, engagement, browsers, UTMs, keywords → `ga4_audit_data.json` + `ga4_audit_extra.json`

**GSC data (if available):** Organic search queries, landing pages, brand vs non-brand split, cannibalization patterns → `gsc_audit_data.json`

**Site inspection:** Fetch HTML source, parse all script tags, identify every tracking system, GTM containers, pixels, consent mode configuration, Shopify-specific configs (if applicable) → `site_inspection.json`

### Phase 3 — Analysis & Report Writing (~1–2 hours)
**Agent:** Analytics Report Writer (Opus model)  
Reads all collected JSON files plus the report template. Writes the full A–Q section report:
- Sections A–J: GA4 property config, tagging, events, conversions, ads, data quality, gaps, consent, ecosystem, benchmarks
- Sections K–P: MarTech stack audit, attribution architecture (current vs ideal), CDP evaluation, Google Ads optimization, channel attribution recommendations, 90-day implementation roadmap
- Section Q (if GSC available): Organic search performance, brand/non-brand split, cannibalization, GSC–GA4 reconciliation

**Output:** `.hazn/outputs/analytics-audit/{domain}-audit.md` (~800–1,200 lines)

### Phase 4 — Adversarial Review (~30–60 minutes)
**Agent:** Analytics Adversary (Opus model)  
Red-teams every number, percentage, and recommendation. Verifies all figures against source JSON. Checks for internal inconsistencies, unsupported claims, correlation-as-causation, and disproportionate recommendations.  
**Output:** Adversarial review notes (corrections fed back to report writer if critical issues found)

### Phase 5 — Client Report Generation (~30–60 minutes)
**Agent:** Analytics Client Reporter (Opus model)  
Transforms the markdown report and JSON data into a single-file HTML executive presentation. Sticky sidebar ToC, responsive (375px → 1440px), hardcoded data (no runtime templates).  
**Output:** `.hazn/outputs/analytics-audit/client-report/index.html`

## HITL Checkpoints

| Checkpoint | Why it matters / risk of skipping |
|---|---|
| OAuth credentials verification before data collection | GA4 API calls fail silently with auth errors if credentials are stale or wrong scope. All downstream analysis is void without real data. |
| Adversarial review findings | The Adversary may flag critical errors (wrong percentages, unsupported revenue claims). Delivering an unchecked report to a data-literate CMO destroys credibility. |
| Client report review before delivery | HTML report is generated from hardcoded data — errors in the markdown report propagate to HTML. Review the HTML output before sending to client. |

## Caveats & Gotchas

- **GA4 OAuth setup is per-client and manual** — not automated. Each client requires their GA4 property to be shared with the service account or OAuth credentials configured before the workflow can run.
- **GSC access is separate from GA4 access** — two different OAuth scopes. If only GA4 is available, Section Q is skipped.
- **Python dependencies must be installed** in the venv before running. Missing `google-analytics-data` causes silent failure with no useful error.
- The Adversary runs on Opus — it's the most expensive agent in the pipeline. Budget accordingly.
- Report Writer targets 800–1,200 lines. If data is sparse (new GA4 property, minimal traffic), the report will be thinner — don't pad it.
- Shopify-specific analysis (Trekkie S2S, Web Pixels Manager) only applies if the site is on Shopify. The inspector will check regardless.
- The client HTML report references `images/` subdirectory — if deploying to `autonomous-proposals`, maintain the directory structure.

## Outputs

```
.hazn/outputs/analytics-audit/
├── ga4_audit_data.json
├── ga4_audit_extra.json
├── gsc_audit_data.json        ← only if GSC access provided
├── site_inspection.json
├── {domain}-audit.md          ← full A–Q markdown report
└── client-report/
    ├── index.html             ← polished HTML deliverable
    └── images/                ← supporting images (if any)
```

## Example Trigger

```
/hazn-analytics-audit
URL: https://your-client.com
GA4 Property ID: 123456789
GSC: https://your-client.com
```

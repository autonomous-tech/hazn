# Analytics Teaser Report

> Zero-access prospect report covering performance, MarTech stack, SEO, Copy, UX, and CRO — built entirely from public data, delivered as a polished HTML sales asset with upsell gates.

## When to Use

- Prospecting: generate a value-first report for a potential client before they share any credentials
- Pre-sales: give prospects a taste of the full analytics audit to justify the engagement
- Cold outreach follow-up: "here's what I found about your site in 30 minutes"

**NOT for:**
- Clients who have already shared GA4/GSC access → use `/hazn-analytics-audit` for the full picture
- Sites with no public-facing pages (paywalled, login-only)
- Internal tools or staging environments

## Requirements

- **Site URL** — required
- **Company name** — optional (extracted from site title if not provided)
- **Calendly URL** — optional but recommended (all CTAs link to it)
- **Playwright installed** — required for screenshot collection and accessibility snapshots. If missing, the `analytics-teaser-collector` agent silently produces no screenshots and the report will lack visual evidence.
- Python with `requests`, `beautifulsoup4` installed for `pagespeed_collector.py` and `teaser_collector.py`

## How It Works

### Phase 1 — Setup (~5 minutes)
Parse site URL, normalize (add `https://` if missing), extract domain, create output directory at `.hazn/outputs/analytics-teaser/{domain}/screenshots/`. Confirm scope with user.

### Phase 2 — Data Collection (~10–20 minutes, parallel)
All 4 tracks run simultaneously:

**Track 1 — Site inspection** (Analytics Inspector agent): Fetches HTML source, identifies all tracking codes, GTM containers, pixels, consent configuration, structured data.  
→ `site_inspection.json`

**Track 2 — PageSpeed** (`pagespeed_collector.py`): Calls PageSpeed Insights API for mobile and desktop. Lighthouse scores, Core Web Vitals (LCP, INP, FID, CLS), third-party script inventory.  
→ `pagespeed.json`

**Track 3 — Public data** (`teaser_collector.py`): robots.txt, sitemap.xml, security headers, SSL configuration, tech stack detection.  
→ `teaser_data.json`

**Track 4 — Playwright screenshots** (Analytics Teaser Collector agent): Visits homepage + up to 4 secondary pages (about, pricing, services, contact). Captures desktop (1440px) and mobile (375px) screenshots, accessibility snapshots for each page, JS console errors.  
→ `playwright_data.json` + `screenshots/`

### Phase 3 — Report Generation (~15–30 minutes)
**Agent:** Analytics Teaser Writer (Opus model)  
Reads all 4 data files + teaser skill + content template. Performs inline Copy/UX/CRO analysis from Playwright snapshots. Calculates all scores (Lighthouse, CWV, MarTech maturity, security, Copy/UX/CRO A–F grades). Embeds screenshots as Base64. Generates single-file HTML.  
**Output:** `.hazn/outputs/analytics-teaser/{domain}/index.html`

Report sections: Hero (grade + screenshot), Scorecard (5 grades), Core Web Vitals, MarTech stack, Privacy/tracking, SEO, Performance, Security → Gate 1 (GSC upsell) → Copy audit, UX audit, CRO audit → Gate 2 (GA4 upsell) → Gate 3 (SEO upsell) → Final CTA.

### Phase 4 — Verification (~5 minutes)
Check output file exists and has content. Visual verification at 3 viewport sizes (1440px, 768px, 375px). Confirm all scores rendered, screenshots visible, CTAs linking correctly.

## HITL Checkpoints

| Checkpoint | Why it matters / risk of skipping |
|---|---|
| Calendly URL confirmation before generation | All 3 gates and the final CTA link to the Calendly URL. Delivering a report with broken or wrong booking links means the sales asset doesn't convert. |
| Scope confirmation | The report is personalized — company name and specific tool names are woven throughout. Confirming the domain and company name before running saves a full regeneration. |

## Caveats & Gotchas

- **Playwright must be installed** — if it's missing, `analytics-teaser-collector` fails silently. The report will generate but without screenshots or accessibility snapshots, making Copy/UX/CRO analysis generic and unverifiable.
- **PageSpeed API rate limits** — Google's PageSpeed Insights API has free-tier rate limits (400 calls/day per IP). If running multiple teaser reports in a day, spread them out or use an API key.
- **Base64 screenshot embedding** — the report embeds screenshots as Base64, targeting <500KB total file size. Sites with heavy, high-resolution homepages may push this over. The writer compresses accordingly.
- **Copy/UX/CRO analysis is qualitative** — it's derived from accessibility snapshots (structured text representation of the page), not actual rendered screenshots. Visually complex layouts or JS-rendered content may not appear fully in the snapshot.
- **Gates are upsell anchors** — Gate 1 (GSC data), Gate 2 (GA4 audit), Gate 3 (SEO audit) are intentionally locked sections. They use real data hooks from the collected data to create FOMO. Don't remove them — they're the conversion mechanism.
- Report generation uses Opus model — takes longer and costs more than Sonnet. Factor this in when batch-generating reports.

## Outputs

```
.hazn/outputs/analytics-teaser/{domain}/
├── site_inspection.json
├── pagespeed.json
├── teaser_data.json
├── playwright_data.json
├── screenshots/
│   ├── home-desktop.png
│   ├── home-mobile.png
│   ├── about-desktop.png
│   ├── about-mobile.png
│   └── ...
└── index.html                  ← self-contained HTML report
```

## Example Trigger

```
/hazn-analytics-teaser
URL: https://example.com
Company: Acme Corp
Calendly: https://calendly.com/hazn/audit-call
```

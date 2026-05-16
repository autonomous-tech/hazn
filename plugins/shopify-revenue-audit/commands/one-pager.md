---
description: Render the executive one-pager from an existing Shopify revenue audit
disable-model-invocation: true
argument-hint: <audit-dir>
---

# /shopify-revenue-audit:one-pager

Dispatcher for generating the single-page executive summary from an existing full audit. Use when the prospect wants a skimmable artifact for their board, CFO, or shared Slack channel and the 10-section HTML report is too long.

## Usage

```
/shopify-revenue-audit:one-pager audits/example-revenue-audit-2026-05-16
```

## What this does

1. Loads the existing audit directory (must contain `SYNTHESIS.md`, `REVENUE-PROJECTION-v2.json`, and `QUICK-WINS.json`)
2. Passes those artifacts to the `shopify-revenue-audit` skill's one-pager renderer
3. Uses the same resolved brand config from the original audit run for visual consistency
4. Renders via `editorial-warmth-audit-renderer` from the hazn runtime
5. Writes `audits/<client>-revenue-audit-YYYY-MM-DD/one-pager.html` and a print-ready PDF if `wkhtmltopdf` is available

## What appears on the one-pager

- Composite score (X/100) with the 4 module scores
- Top 3 quick wins with P25-P75 dollar bands
- Top 3 strategic workstreams (partner close, no sales CTA)
- One paragraph executive summary lifted from `SYNTHESIS.md`

Hand control to the skill — do not duplicate rendering logic here.

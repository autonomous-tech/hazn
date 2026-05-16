---
name: module-4-technical
description: Module 4 of the Shopify Revenue Audit — Technical Foundation (20% of composite). Audits platform fingerprint (theme, Plus signals, Functions migration), Shopify Markets + B2B config, variant cap risk, app conflicts, render-blocking scripts, and MarTech presence (GA4/Meta Pixel/GTM/Web Pixels Manager/TikTok/Pinterest/Clarity/Hotjar). Invoked by the `shopify-revenue-audit` orchestrator during Wave 2 or directly via `/shopify-revenue-audit:rerun-module 4`.
---

# Module 4 — Technical Foundation

## When to use
- Invoked by the `shopify-revenue-audit` orchestrator during Wave 2 (ε team lead).
- Invoked directly via `/shopify-revenue-audit:rerun-module <audit-dir> 4` after a fix.
- NOT for standalone use — operates against Wave 1 recon.

## Scope

**Weight in composite:** 20%.

**Covers:**
- Shopify platform fingerprint: theme name + version, Plus signals, Markets config, Functions migration (modern checkout extensions vs legacy ScriptTag), variant cap risk
- App stack detection (Judge.me, Klaviyo, Postscript, Attentive, Shop Pay, Loox, Yotpo, ReCharge, Bold, Shogun, GemPages, PageFly, Octane AI, Stamped, Gorgias, Tidio, ReConvert, Honeycomb, UpCart, Route, Seel, Rebuy, Searchanise, Accessibly, Richpanel)
- App conflict signatures (e.g., Klaviyo + Postscript both, Rebuy + native cart, Searchanise vs Shopify Search)
- Logic risk (JS-mutated prices, render-blocking script count, legacy ScriptTag traces)
- MarTech presence: GA4, GTM, Meta Pixel, TikTok Pixel, Pinterest, Microsoft Clarity, Hotjar, Web Pixels Manager, Trekkie
- Data-to-request inventory (admin-side things the audit cannot see from public HTML)

**Does NOT cover:** AI-discovery layer / schema (→ Module 1), SEO catalog (→ Module 2), conversion UX (→ Module 3). This module is the rooting layer that everything else depends on.

## Inputs (from Wave 1)
- `projects/<SLUG>/diagnostics/scope.md` — visible apps the orchestrator already grepped
- `projects/<SLUG>/diagnostics/infra-probe.json` — α2 output
- `projects/<SLUG>/diagnostics/pagespeed/SUMMARY.md` — CWV note
- `projects/<SLUG>/diagnostics/crawl/pdp-{1,2,3}.html` — signature detection (grep PDP HTML)

Cross-reference:
- `analytics-audit` skill — MANDATORY; use its rubric for MarTech section

## Audit criteria

### 1. Platform → `module4/platform-scan.json`
- Theme name + version (`Shopify.theme.name`, `Shopify.theme.id`)
- Shopify Plus signals (`Shopify.plus`, B2B endpoints, multi-currency)
- Shopify Markets config (locale, multi-currency, country selector)
- Shopify Functions vs legacy ScriptTag (modern checkout extensions present?)
- Variant cap risk (count variants on the configurator-heaviest PDP; flag if approaching 100/2000 caps)

### 2. Logic → `module4/logic-scan.json`
- Pricing consistency — any JS-mutated prices? (flag for fraud / tax risk)
- App conflicts — signatures of incompatible app pairs
- Render-blocking script count
- Legacy ScriptTag traces (deprecated, blocks Functions adoption)

### 3. Apps + MarTech → `module4/app-analytics.json`

Apps to detect (grep PDP HTML): Judge.me, Klaviyo, Postscript, Attentive, Shop Pay, Loox, Yotpo, ReCharge, Bold, Shogun, GemPages, PageFly, Octane AI, Stamped, Gorgias, Tidio, ReConvert, Honeycomb, UpCart, Route, Seel, Rebuy, Searchanise, Accessibly, Richpanel.

MarTech presence (CRITICAL):
- GA4 (`G-XXXXXXX` or `gtag(`)
- GTM (`GTM-XXXXXXX`)
- Meta Pixel (`fbq(` or `facebook.net/en_US/fbevents.js`)
- TikTok Pixel (`ttq.track`)
- Pinterest, Microsoft Clarity, Hotjar
- Web Pixels Manager (`Shopify.analytics.publish`)
- Trekkie (Shopify internal)

**If GA4 / Meta absent from public HTML but Web Pixels Manager is active → mark "MarTech black box, requires admin access"** rather than scoring zero.

### 4. Data to Request → `data-to-request.md` (admin-side)
- GA4 access (or 90d export)
- Google Search Console
- Shopify Markets / B2B / Functions config
- Product feed destinations (GMC, Meta, TikTok, ChatGPT Shopping)
- Klaviyo flow performance
- Any AI / chat integrations

## Scoring rubric (0-100)

Weighted:
- Platform: 30%
- Logic: 25%
- Apps: 20%
- MarTech: 25%

CWV penalty noted but not double-applied (Module 2 owns the CWV penalty in the composite).

Typical floors:
- Score < 40: legacy ScriptTag heavy, MarTech black box with no admin access offered, app conflicts visible, variant cap close
- Score 40-60: modern stack mostly in place but with some legacy traces, MarTech partial
- Score 60+: Functions adopted, MarTech complete (GA4 + Meta + at least one heatmap), apps non-conflicting

## Outputs

Write to `projects/<SLUG>/diagnostics/module4/`:
- `module4-technical.md` — section draft + score + top 3 findings (`FINDING-XXX` format)
- `module4/platform-scan.json`
- `module4/logic-scan.json`
- `module4/app-analytics.json`
- `data-to-request.md` (admin-side asks, surfaces in the "Data We Requested From You" appendix)

**Evidence requirements:**
- Every detected app cites the exact grep signature
- Every MarTech presence/absence claim cites file:line in PDP HTML
- Platform claims cite `Shopify.theme.*` JS globals

## Red-team gates

Module 4 findings must pass:
- `audit-red-team-domain-check` — does the proposed fix actually unlock revenue, or is it hygiene? (e.g., "migrate to Functions" is correct but doesn't directly produce $; don't quantify it as if it does)
- `audit-red-team-cfo` — MarTech-black-box findings often produce inflated "you can't measure $X" claims; CFO-check before quantifying

If RED, rebuild and re-run before composite is final.

## References

The following files are available at `plugins/shopify-revenue-audit/skills/module-4-technical/references/`:

| File | Description |
|------|-------------|
| `cdp-schema.md` | RudderStack CDP event schema (funnel events, order events, supporting events) — use when querying or validating client CDP data during the MarTech section |

## Related skills
- `shopify-revenue-audit` — orchestrator
- `audit-red-team-domain-check`, `audit-red-team-cfo` — mandatory gates
- `analytics-audit` — MANDATORY rubric source for MarTech section
- See `../shopify-revenue-audit/references/agent-teams-playbook.md` § Wave 2 ε for the full agent prompt

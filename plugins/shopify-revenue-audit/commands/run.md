---
description: Run a full 4-module Shopify revenue audit on a store URL
disable-model-invocation: true
argument-hint: <shopify-store-url> [--brand <slug>] [--client-name <override>]
---

# /shopify-revenue-audit:run

Dispatcher for the `shopify-revenue-audit` skill. Runs the complete 4-module pipeline (AI Discovery, Search & Catalog, Conversion Experience, Technical Foundation), the synthesis wave, the mandatory 4-pass red-team, and the Editorial Warmth v2 HTML build.

## Usage

```
/shopify-revenue-audit:run https://example.com
/shopify-revenue-audit:run https://example.com --brand partner-slug
/shopify-revenue-audit:run https://example.com --client-name "Example Co"
```

## What this does

1. Validates the URL is reachable and looks like Shopify (cdn.shopify.com / window.Shopify)
2. Resolves brand config via the hazn runtime (defaults to `autonomous` if `--brand` not passed)
3. Loads the `shopify-revenue-audit` skill from `${CLAUDE_PLUGIN_ROOT}/skills/shopify-revenue-audit/SKILL.md` and follows its instructions end-to-end
4. Runs all 4 red-team passes via the hazn runtime skills before publishing any dollar projection
5. Renders the final HTML via `editorial-warmth-audit-renderer` from the hazn runtime
6. Writes deliverables under `audits/<client>-revenue-audit-YYYY-MM-DD/`

## Required inputs

- Shopify store URL (positional)

## Optional flags

- `--brand <slug>` — partner brand for white-label rendering
- `--client-name <name>` — override the detected client name
- `--skip-red-team` — DISCOURAGED, internal sandbox only; will refuse to publish if set

Hand control to the skill — do not duplicate its logic here.

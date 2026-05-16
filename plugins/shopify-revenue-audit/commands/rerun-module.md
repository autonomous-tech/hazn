---
description: Re-run a single module of an existing Shopify revenue audit after a fix
disable-model-invocation: true
argument-hint: <audit-dir> <module-number>
---

# /shopify-revenue-audit:rerun-module

Dispatcher for re-running a single module of an existing audit. Use this when the client fixed a flagged issue and you want to refresh that module's score without re-running the whole 4-module pipeline.

## Usage

```
/shopify-revenue-audit:rerun-module audits/example-revenue-audit-2026-05-16 1
/shopify-revenue-audit:rerun-module audits/example-revenue-audit-2026-05-16 3
```

## What this does

1. Loads the existing audit directory and reads the project state from `projects/<SLUG>/diagnostics/`
2. Dispatches to exactly one module skill (by name) based on the module number argument:
   - `1` → invokes the `module-1-ai-discovery` skill
   - `2` → invokes the `module-2-search-catalog` skill
   - `3` → invokes the `module-3-conversion` skill
   - `4` → invokes the `module-4-technical` skill
3. Re-runs the synthesis and the red-team gates declared by that module skill (subset of the 4 mandatory red-teams)
4. Updates the composite score and the rendered HTML in place via `editorial-warmth-audit-renderer`
5. Writes a CHANGELOG entry inside the audit directory recording what changed

## Module numbers

| # | Module skill | Weight |
|---|--------|--------|
| 1 | `module-1-ai-discovery` — AI Discovery & Agentic Commerce | 30% |
| 2 | `module-2-search-catalog` — Search & Catalog Performance | 20% |
| 3 | `module-3-conversion` — Conversion Experience | 30% |
| 4 | `module-4-technical` — Technical Foundation | 20% |

The composite recomputes as `0.30 × M1 + 0.20 × M2 + 0.30 × M3 + 0.20 × M4`. Only the rerun module's score changes; the others are read from the existing audit state.

The orchestrator (`shopify-revenue-audit` skill) coordinates this single-module rerun — defer to its rerun logic; this command is only a thin dispatch wrapper.

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

1. Loads the existing audit directory and reads the project state
2. Re-runs only the specified module's β/γ/δ/ε agent team via the `shopify-revenue-audit` skill
3. Re-runs the synthesis and red-team for that module's findings only
4. Updates the composite score and the rendered HTML in place
5. Writes a CHANGELOG entry inside the audit directory recording what changed

## Module numbers

| # | Module | Weight |
|---|--------|--------|
| 1 | AI Discovery & Agentic Commerce | 30% |
| 2 | Search & Catalog Performance | 20% |
| 3 | Conversion Experience | 30% |
| 4 | Technical Foundation | 20% |

Defer to the skill at `${CLAUDE_PLUGIN_ROOT}/skills/shopify-revenue-audit/SKILL.md` for the actual rerun logic — this command is only a thin dispatch wrapper.

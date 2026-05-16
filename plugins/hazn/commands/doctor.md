---
description: Verify the Hazn runtime, installed job plugins, and local canonical checkout are healthy
disable-model-invocation: true
---

# /hazn:doctor

Diagnostic check for the Hazn marketplace install. Verifies the runtime kernel, every enabled job plugin's declared dependencies, and the local canonical checkout used by `/hazn:feedback`. Run this when something feels off — a skill can't find a sibling, a brand config doesn't load, or `/hazn:feedback` fails to open a PR.

## Checks performed

### 1. hazn runtime kernel installed

Confirm `hazn@1.x` is present in the active Claude Code marketplace registry. Read its manifest from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` and report version. If missing, instruct user to install the marketplace.

### 2. Runtime skills resolvable

Verify each of the 7 runtime skills exists under `${CLAUDE_PLUGIN_ROOT}/skills/`:

- `hazn-orchestrator`
- `editorial-warmth-audit-renderer`
- `audit-red-team-baseline`
- `audit-red-team-uplifts`
- `audit-red-team-cfo`
- `audit-red-team-domain-check`
- `frontend-design`

Print a check / cross per skill. Any missing skill is a `FAIL`.

### 3. Brand registry healthy

- `${CLAUDE_PLUGIN_ROOT}/brands/autonomous.json` exists and parses as JSON
- All required fields per `references/brand-schema.md` are present
- Any additional partner brand files in `brands/` parse and validate against the same schema

### 4. Job-plugin dependency resolution

For each enabled non-hazn plugin in the marketplace (e.g. `shopify-revenue-audit`), read its manifest and any declared dependencies on hazn skills. Confirm each dependency resolves to an actual skill under hazn. Report any unresolved dependency as a `FAIL` with the offending plugin name.

If a job plugin's manifest declares no dependencies, print a `WARN` — most job plugins should at least depend on `editorial-warmth-audit-renderer` and one red-team skill.

### 5. Local canonical hazn checkout

Locate the user's local clone of `autonomous-tech/hazn` (used by `/hazn:feedback`). Check, in order:

1. `$HAZN_REPO_PATH` if set
2. `~/Work/autonomous/repos/products/hazn`
3. `~/repos/autonomous-tech/hazn`

Report which path was found, the current branch, and whether the working tree is clean. If none found, print a `WARN` with installation instructions — `/hazn:feedback` will fall back to issue mode.

## Output format

```
hazn doctor — Phase 1 marketplace runtime

[OK]   hazn runtime installed (v1.0.0)
[OK]   7/7 runtime skills resolvable
[OK]   brands/autonomous.json valid
[OK]   shopify-revenue-audit → deps resolve
[WARN] no local hazn checkout — /hazn:feedback will use issue mode
```

Exit non-zero if any check is `FAIL`, otherwise zero. Each line should be skimmable in a single glance.

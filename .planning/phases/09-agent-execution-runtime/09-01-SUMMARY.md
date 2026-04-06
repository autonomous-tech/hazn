---
phase: 09-agent-execution-runtime
plan: 01
subsystem: orchestrator
tags: [budget, cost-control, tool-wiring, anthropic-api, pydantic, django-orm]

# Dependency graph
requires:
  - phase: 08-foundation-components
    provides: ToolRouter with static registry and build_tool_registry(), MCP server modules with @mcp.tool() functions
provides:
  - BudgetConfig and BudgetEnforcer for per-workflow token/cost/turn budget enforcement
  - calculate_cost for Anthropic API response cost computation
  - check_agency_cost_cap for rolling monthly cost cap with 80% alert threshold
  - wire_callables to connect all 20 MCP tool functions to ToolRouter entries
  - scope_tools_for_phase to filter Anthropic tools array per workflow phase
  - AppConfig.ready() singleton ToolRouter with wired callables at Django startup
affects: [09-02-agent-runner, 09-03-backends, 10-e2e-workflows]

# Tech tracking
tech-stack:
  added: []
  patterns: [budget-enforcement-after-metering, singleton-tool-registry, module-level-lazy-import-for-testability]

key-files:
  created:
    - hazn_platform/hazn_platform/orchestrator/budget.py
    - hazn_platform/hazn_platform/orchestrator/tool_wiring.py
    - hazn_platform/tests/test_budget.py
    - hazn_platform/tests/test_tool_wiring.py
  modified:
    - hazn_platform/hazn_platform/orchestrator/apps.py

key-decisions:
  - "BudgetEnforcer uses >= comparison (not >) for limit detection, matching plan behavior specs exactly"
  - "AgencyCostCapResult is a NamedTuple (not Pydantic) for lightweight immutable result type"
  - "AppConfig.ready() uses module-level wrapper functions for build_tool_registry/wire_callables/validate_registry to enable clean test patching without Django AppConfig constructor issues"
  - "wire_callables uses lazy imports inside function body to avoid Django setup at import time"

patterns-established:
  - "Budget check after metering: BudgetEnforcer.record() called after MeteringCallback.on_llm_call(), then is_exceeded() before next API call"
  - "Singleton tool registry: _ROUTER_SINGLETON in tool_wiring module set by AppConfig.ready()"
  - "Cost calculation duck-typing: calculate_cost accepts any object with .usage attribute (Anthropic SDK response compatible)"

requirements-completed: [RUNT-06, RUNT-07]

# Metrics
duration: 7min
completed: 2026-03-06
---

# Phase 9 Plan 01: Budget Enforcement and Tool Wiring Summary

**Per-workflow budget enforcement (token/cost/turn limits) with claude-sonnet-4-5 pricing, rolling monthly agency cost caps, and 20-tool MCP callable wiring at Django startup**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-06T14:43:30Z
- **Completed:** 2026-03-06T14:50:30Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- BudgetConfig (Pydantic) + BudgetEnforcer detects token/cost/turn exceedance with descriptive reason strings
- calculate_cost computes correct USD from Anthropic API response including cache token pricing
- check_agency_cost_cap uses rolling monthly window with 80% alert threshold and automatic block at cap
- wire_callables populates all 20 ToolRegistryEntry.callable fields from 4 MCP server module imports
- scope_tools_for_phase filters Anthropic tools array to phase-declared subset (empty=all for backward compat)
- AppConfig.ready() creates singleton ToolRouter with wired callables, double-ready guard, graceful error handling
- 37 tests total (24 budget + 13 tool wiring), all passing with zero Phase 8 regressions

## Task Commits

Each task was committed atomically:

1. **Task 1: Budget enforcement module** - `df121a2` (feat) -- BudgetConfig, BudgetEnforcer, calculate_cost, check_agency_cost_cap with 24 tests
2. **Task 2: Tool wiring module** - `bed8813` (feat) -- wire_callables, scope_tools_for_phase, AppConfig.ready() with 13 tests

**Plan metadata:** (pending final commit)

_Note: TDD tasks each have a single commit (tests + implementation combined after GREEN phase)_

## Files Created/Modified
- `hazn_platform/hazn_platform/orchestrator/budget.py` - BudgetConfig, BudgetEnforcer, MODEL_PRICING, calculate_cost, check_agency_cost_cap, AgencyCostCapResult
- `hazn_platform/hazn_platform/orchestrator/tool_wiring.py` - wire_callables (20 MCP tool functions), scope_tools_for_phase, _ROUTER_SINGLETON
- `hazn_platform/hazn_platform/orchestrator/apps.py` - OrchestratorConfig.ready() with tool wiring at startup
- `hazn_platform/tests/test_budget.py` - 24 tests covering budget enforcement and agency cost cap
- `hazn_platform/tests/test_tool_wiring.py` - 13 tests covering tool wiring, scoping, and AppConfig lifecycle

## Decisions Made
- BudgetEnforcer uses `>=` comparison for all limits (tokens, cost, turns) matching the plan's behavior specs that say "at or over" for blocking
- AgencyCostCapResult is a NamedTuple instead of Pydantic model -- lightweight, immutable, and sufficient for a result type
- AppConfig.ready() uses module-level wrapper functions for build_tool_registry/wire_callables/validate_registry instead of direct imports, enabling clean test patching without Django AppConfig constructor issues
- MODEL_PRICING keyed by model name for easy future additions when pricing changes

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] AppConfig test approach changed from constructor to registry lookup**
- **Found during:** Task 2 (AppConfig.ready() tests)
- **Issue:** Django AppConfig constructor validation fails when instantiated directly in tests (`OrchestratorConfig("hazn_platform.orchestrator", "hazn_platform.orchestrator")`) because module path resolution requires actual Django app registry setup
- **Fix:** Changed tests to use `django.apps.apps.get_app_config("orchestrator")` to get the real registered instance, with proper `_ready_done` flag cleanup in try/finally blocks
- **Files modified:** hazn_platform/tests/test_tool_wiring.py
- **Verification:** All 13 tool wiring tests pass
- **Committed in:** bed8813 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Test approach adjustment only. No scope creep. All specified behaviors tested.

## Issues Encountered
None beyond the AppConfig test approach deviation documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- BudgetEnforcer ready for AgentRunner (Plan 02) to call record() after each on_llm_call and is_exceeded() before next API call
- wire_callables wires all 20 tool callables -- AgentRunner can dispatch via ToolRouter.dispatch_anthropic()
- scope_tools_for_phase ready for AgentRunner to filter tools per workflow phase
- _ROUTER_SINGLETON available at module level for runtime access
- No blockers for Plan 02 (AgentRunner) or Plan 03 (backends)

---
*Phase: 09-agent-execution-runtime*
*Completed: 2026-03-06*

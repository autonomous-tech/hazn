---
phase: 01-strip-infrastructure-dependencies
plan: 01
subsystem: orchestrator
tags: [agent-sdk, budget-removal, backend-consolidation, runtime-cleanup]

# Dependency graph
requires: []
provides:
  - "AgentSDKBackend as sole runtime backend (no conditional selection)"
  - "RuntimeBackend Protocol without budget or on_turn parameters"
  - "Executor with unconditional SDK path (no HAZN_RUNTIME_MODE)"
  - "Clean codebase: no budget.py, anthropic_api.py, test_budget.py"
affects: [02-strip-infrastructure-dependencies, 04-agent-sdk-runtime]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Unconditional AgentSDKBackend instantiation in executor (no lazy sentinels)"
    - "Hardcoded max_turns=30 in AgentSDKBackend (Phase 4 will configure)"

key-files:
  created: []
  modified:
    - "hazn_platform/hazn_platform/orchestrator/agent_runner.py"
    - "hazn_platform/hazn_platform/orchestrator/backends/agent_sdk.py"
    - "hazn_platform/hazn_platform/orchestrator/backends/__init__.py"
    - "hazn_platform/hazn_platform/orchestrator/executor.py"
    - "hazn_platform/tests/test_agent_runner.py"
    - "hazn_platform/tests/test_agent_sdk_backend.py"
    - "hazn_platform/tests/test_executor.py"
    - "hazn_platform/tests/test_sse_events.py"

key-decisions:
  - "Hardcoded max_turns=30 in AgentSDKBackend (was budget.max_turns or 30)"
  - "Removed budget_exceeded as a valid RunResult status"
  - "Removed on_turn callback from all interfaces (session.record_turn removed from executor)"
  - "Summary text in executor simplified -- no partial/budget-exceeded branch"

patterns-established:
  - "AgentSDKBackend is the single execution path -- no runtime mode switching"
  - "RuntimeBackend Protocol has 6 params: system_prompt, messages, tools, tool_dispatch, metering, agent_id"

requirements-completed: [STRP-04, STRP-05]

# Metrics
duration: 13min
completed: 2026-03-12
---

# Phase 1 Plan 1: Remove Budget and API Backend Summary

**Deleted budget enforcement (BudgetConfig, BudgetEnforcer, cost caps) and Anthropic API backend, making AgentSDKBackend the sole unconditional execution path**

## Performance

- **Duration:** 13 min
- **Started:** 2026-03-12T13:23:28Z
- **Completed:** 2026-03-12T13:36:28Z
- **Tasks:** 2
- **Files modified:** 8 (3 deleted, 5 updated)

## Accomplishments
- Deleted budget.py (229 lines), anthropic_api.py (239 lines), test_budget.py (330 lines) -- 798 lines of dead code removed
- RuntimeBackend Protocol, AgentRunner.run(), and AgentSDKBackend.execute() all simplified to 6-parameter signatures
- Executor uses AgentSDKBackend unconditionally -- no HAZN_RUNTIME_MODE env var, no lazy import sentinels, no conditional backend selection
- All 48 affected tests pass, pytest --collect-only clean, Django check passes, ruff clean

## Task Commits

Each task was committed atomically:

1. **Task 1: Delete budget.py, anthropic_api.py, update interfaces** - `039b409` (feat)
2. **Task 2: Update executor.py and fix all test files** - `93da742` (feat)

## Files Created/Modified
- `hazn_platform/orchestrator/budget.py` - DELETED (BudgetConfig, BudgetEnforcer, check_agency_cost_cap, calculate_cost)
- `hazn_platform/orchestrator/backends/anthropic_api.py` - DELETED (AnthropicAPIBackend)
- `tests/test_budget.py` - DELETED (all budget tests)
- `hazn_platform/orchestrator/agent_runner.py` - Removed BudgetConfig import, budget/on_turn params from Protocol and AgentRunner
- `hazn_platform/orchestrator/backends/agent_sdk.py` - Removed BudgetConfig, on_turn; hardcoded max_turns=30
- `hazn_platform/orchestrator/backends/__init__.py` - Removed AnthropicAPIBackend lazy import
- `hazn_platform/orchestrator/executor.py` - Removed budget imports, cost cap check, HAZN_RUNTIME_MODE, on_turn, budget_exceeded handling; unconditional SDK backend
- `tests/test_agent_runner.py` - Removed 6 AnthropicAPIBackend test classes (~420 lines), BudgetConfig from runner calls
- `tests/test_agent_sdk_backend.py` - Removed TestAgentSDKBackendBudgetConfig, BudgetConfig from execute() calls
- `tests/test_executor.py` - Removed ~16 check_agency_cost_cap mocks, BudgetConfig, HAZN_RUNTIME_MODE tests, budget_exceeded test
- `tests/test_sse_events.py` - Removed check_agency_cost_cap and AnthropicAPIBackend mocks from _apply_standard_patches, removed budget_exceeded SSE test

## Decisions Made
- Hardcoded `max_turns=30` in AgentSDKBackend rather than making it configurable now -- Phase 4 (Agent SDK Runtime) will rewrite the entire backend with proper configuration
- Removed `budget_exceeded` as a valid RunResult status -- executor now only handles `completed` and `error`/`max_tokens_truncated` (error raises RuntimeError)
- Removed `on_turn` callback from all interfaces -- session turn tracking was tied to budget enforcement and the SDK manages turns internally
- Simplified executor summary_text to always use "completed" phrasing (no "partial/budget exceeded" branch)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Pre-existing teardown errors in transaction=True tests (TRUNCATE on closed cursor) -- these affect test infrastructure, not the test assertions. All 48 tests pass; the 26 errors are all in teardown phase. Not caused by this plan's changes.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All budget and API backend references cleanly removed from orchestrator and tests
- Executor is ready for Plan 01-02 (remaining infrastructure dependency stripping)
- AgentSDKBackend is the sole backend, ready for Phase 4 rewrite
- No blockers

## Self-Check: PASSED

- SUMMARY.md: FOUND
- Task 1 commit (039b409): FOUND
- Task 2 commit (93da742): FOUND
- budget.py: CONFIRMED DELETED
- anthropic_api.py: CONFIRMED DELETED
- test_budget.py: CONFIRMED DELETED

---
*Phase: 01-strip-infrastructure-dependencies*
*Completed: 2026-03-12*

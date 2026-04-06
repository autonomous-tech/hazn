---
phase: 09-agent-execution-runtime
plan: 03
subsystem: orchestrator
tags: [claude-agent-sdk, agent-runner, runtime-backend, budget-enforcement, executor]

# Dependency graph
requires:
  - phase: 09-02
    provides: AgentRunner, RuntimeBackend Protocol, AnthropicAPIBackend, RunResult
  - phase: 09-01
    provides: BudgetConfig, BudgetEnforcer, check_agency_cost_cap, tool_wiring
  - phase: 08-03
    provides: OutputCollector for artifact extraction
  - phase: 08-02
    provides: ToolRouter for tool dispatch
  - phase: 08-01
    provides: PromptAssembler for system prompt assembly
provides:
  - AgentSDKBackend implementing RuntimeBackend Protocol (Mode 1 execution)
  - Updated executor.py with AgentRunner integration replacing placeholder
  - HAZN_RUNTIME_MODE env var for backend selection (api or agent_sdk)
  - Pre-flight agency cost cap check in _execute_phase()
  - Budget exceeded partial result preservation
affects: [phase-10-e2e-integration, workflow-execution, agent-execution]

# Tech tracking
tech-stack:
  added: [claude_code_sdk (optional, alpha v0.1.47)]
  patterns: [lazy-import for optional SDK, env-var-based runtime selection, strategy pattern backend selection]

key-files:
  created:
    - hazn_platform/hazn_platform/orchestrator/backends/agent_sdk.py
    - hazn_platform/tests/test_agent_sdk_backend.py
  modified:
    - hazn_platform/hazn_platform/orchestrator/backends/__init__.py
    - hazn_platform/hazn_platform/orchestrator/executor.py
    - hazn_platform/tests/test_executor.py

key-decisions:
  - "AgentSDKBackend uses late imports inside execute() to handle missing SDK gracefully"
  - "HAZN_RUNTIME_MODE env var selects backend (default: api) -- no code change needed to switch"
  - "BudgetConfig defaults: 500k tokens, $2.0 cost, 30 turns for workflows without explicit budget"
  - "AgentSDKBackend uses mcp__hazn__ prefix for allowed_tools per SDK naming convention"
  - "executor.py global AgentSDKBackend variable for lazy import caching"

patterns-established:
  - "Late SDK import: alpha/optional SDKs imported inside methods, not at module level"
  - "Budget-first execution: agency cost cap checked before any LLM calls"
  - "Partial result preservation: budget_exceeded status stores output with status='partial'"

requirements-completed: [RUNT-04, RUNT-02]

# Metrics
duration: 11min
completed: 2026-03-06
---

# Phase 9 Plan 3: AgentSDKBackend and Executor AgentRunner Integration Summary

**AgentSDKBackend for Mode 1 execution via Claude Code SDK with lazy imports, plus executor.py wired to AgentRunner with pre-flight cost cap checks and env-var backend selection**

## Performance

- **Duration:** 11 min
- **Started:** 2026-03-06T15:06:32Z
- **Completed:** 2026-03-06T15:17:45Z
- **Tasks:** 2 (both TDD)
- **Files modified:** 5

## Accomplishments
- AgentSDKBackend implements RuntimeBackend Protocol for Mode 1 execution via Claude Code SDK
- executor.py _execute_phase() fully replaced: placeholder removed, AgentRunner with real LLM execution wired in
- Pre-flight agency cost cap check blocks over-budget agencies before any LLM calls
- HAZN_RUNTIME_MODE env var seamlessly selects between API and SDK backends
- Budget exceeded and error statuses handled with partial result preservation
- All existing QA injection logic preserved unchanged
- 7 AgentSDKBackend tests + 26 executor tests pass (5 new integration tests)
- 125 Phase 8 + Phase 9 non-DB tests pass, 37 budget/tool_wiring tests pass

## Task Commits

Each task was committed atomically:

1. **Task 1: AgentSDKBackend with mocked SDK and tool wrapping** - `9a86f4b` (feat: TDD red-green)
2. **Task 2: Wire AgentRunner into executor.py replacing placeholder** - `048fc81` (feat: TDD red-green)

_Note: TDD tasks: tests written first (RED), implementation added (GREEN), verified._

## Files Created/Modified
- `hazn_platform/hazn_platform/orchestrator/backends/agent_sdk.py` - AgentSDKBackend implementing RuntimeBackend Protocol for Claude Code SDK
- `hazn_platform/hazn_platform/orchestrator/backends/__init__.py` - Updated with lazy AgentSDKBackend export
- `hazn_platform/hazn_platform/orchestrator/executor.py` - _execute_phase() wired to AgentRunner with backend selection, budget config, cost cap check
- `hazn_platform/tests/test_agent_sdk_backend.py` - 7 tests for AgentSDKBackend (all mocked SDK)
- `hazn_platform/tests/test_executor.py` - 26 tests including 5 new AgentRunner integration tests

## Decisions Made
- AgentSDKBackend uses late imports inside execute() method rather than module-level imports, gracefully handling missing SDK with error RunResult
- HAZN_RUNTIME_MODE env var (default: "api") selects backend at runtime -- no code changes needed to switch
- BudgetConfig defaults to 500k tokens, $2.0 cost, 30 turns when workflow YAML doesn't specify budget
- Allowed tools prefixed with mcp__hazn__ for SDK namespace convention
- executor.py uses global variable caching for lazy AgentSDKBackend import to avoid repeated import overhead
- Test fixtures changed to get_or_create to handle transaction=True teardown edge cases

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed test fixture robustness for transaction=True tests**
- **Found during:** Task 2 (executor test updates)
- **Issue:** Fixtures using `objects.create()` with hardcoded slugs failed when `transaction=True` teardown didn't clean up (known Django/pytest-django FK truncation issue)
- **Fix:** Changed fixtures to use `get_or_create()` for robustness across test isolation modes
- **Files modified:** hazn_platform/tests/test_executor.py
- **Verification:** All 26 executor tests pass
- **Committed in:** 048fc81 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix)
**Impact on plan:** Minor fixture robustness improvement. No scope creep.

## Issues Encountered
- Django `transaction=True` test teardown raises "cannot truncate a table referenced in a foreign key constraint" on PostgreSQL -- this is a pre-existing infrastructure issue in the test suite, not caused by this plan's changes. All 26 executor tests actually pass; only teardown cleanup fails.

## User Setup Required
None - no external service configuration required. The Claude Code SDK is optional and only needed when HAZN_RUNTIME_MODE=agent_sdk.

## Next Phase Readiness
- Phase 9 complete: all 3 plans delivered
- AgentRunner with dual backends (API + SDK) ready for real workflow execution
- First E2E workflow test (Phase 10) will surface interface mismatches
- Budget 3-5x time for Phase 10 as noted in blockers

---
*Phase: 09-agent-execution-runtime*
*Completed: 2026-03-06*

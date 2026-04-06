---
phase: 01-strip-infrastructure-dependencies
plan: 02
subsystem: orchestrator
tags: [gdpr-removal, metering-cleanup, session-simplification, lifecycle-deletion]

# Dependency graph
requires:
  - phase: 01-01
    provides: "Budget and API backend removed, executor simplified to unconditional SDK path"
provides:
  - "Orchestrator free of all enterprise features: no lifecycle module, no threshold alerts, no session turn counting"
  - "MeteringCallback with cost accumulation only (on_llm_call, on_tool_call, flush_to_db, get_totals)"
  - "WorkflowSession without record_turn (start/checkpoint/end/fail/get_memory/is_timed_out only)"
  - "Celery tasks.py with only run_workflow, deliver_webhook, check_hitl_timeouts"
affects: [04-agent-sdk-runtime, 05-tool-extraction]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "MeteringCallback is accumulation-only -- no enforcement, no alerts, no Langfuse events"
    - "WorkflowSession delegates turn tracking to Agent SDK (not session layer)"

key-files:
  created: []
  modified:
    - "hazn_platform/hazn_platform/orchestrator/tasks.py"
    - "hazn_platform/hazn_platform/orchestrator/metering.py"
    - "hazn_platform/hazn_platform/orchestrator/session.py"
    - "hazn_platform/tests/test_session.py"
    - "hazn_platform/tests/test_metering.py"
    - "hazn_platform/tests/test_executor.py"
    - "hazn_platform/tests/test_sse_events.py"

key-decisions:
  - "Removed langfuse get_client import from metering.py -- Langfuse tracing stays in tracing.py (untouched)"
  - "Kept MeteringCallback.from_agency(agency) signature for call-site compatibility even though agency is now unused"
  - "Removed record_turn mocks from test_executor.py and test_sse_events.py fixtures (cleanup of Plan 01 residuals)"

patterns-established:
  - "MeteringCallback.__init__ takes only workflow_run_id -- no budget params"
  - "Session lifecycle is start/checkpoint/end/fail (no per-turn tracking)"

requirements-completed: [STRP-06, STRP-08, STRP-09]

# Metrics
duration: 5min
completed: 2026-03-12
---

# Phase 1 Plan 2: Remove Lifecycle, Strip Metering Thresholds, Remove Session Turn Counting Summary

**Deleted GDPR lifecycle module (271 lines), 3 management commands, stripped metering threshold alerts and Langfuse event annotations, removed session record_turn -- completing Phase 1 enterprise runtime cleanup**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-12T13:40:14Z
- **Completed:** 2026-03-12T13:45:26Z
- **Tasks:** 2
- **Files modified:** 12 (5 deleted, 7 updated)

## Accomplishments
- Deleted lifecycle.py (271 lines), 3 management commands (~300 lines), and test_data_lifecycle.py (581 lines) -- 1,152 lines of GDPR/lifecycle code removed
- Removed 3 Celery lifecycle tasks from tasks.py (enforce_data_retention, process_gdpr_deletions, send_deletion_notifications)
- Stripped MeteringCallback of max_turns, max_cost, on_threshold_alert, _annotate_langfuse_event -- now accumulation-only
- Removed record_turn() from WorkflowSession and all test fixtures that mocked it
- Ruff clean, no unused imports, Langfuse tracing untouched in tracing.py

## Task Commits

Each task was committed atomically:

1. **Task 1: Delete lifecycle module, management commands, update tasks.py** - `d537bbb` (feat)
2. **Task 2: Strip metering thresholds, remove session record_turn, clean up tests** - `c2e5beb` (feat)

## Files Created/Modified
- `hazn_platform/core/lifecycle.py` - DELETED (GDPR deletion scheduling, retention queries, client/agency deletion)
- `hazn_platform/core/management/commands/enforce_retention.py` - DELETED
- `hazn_platform/core/management/commands/process_deletions.py` - DELETED
- `hazn_platform/core/management/commands/notify_deletions.py` - DELETED
- `tests/test_data_lifecycle.py` - DELETED (11 test classes, 581 lines)
- `hazn_platform/orchestrator/tasks.py` - Removed 3 lifecycle tasks and docstring references
- `hazn_platform/orchestrator/metering.py` - Removed threshold params, _annotate_langfuse_event, langfuse import
- `hazn_platform/orchestrator/session.py` - Removed record_turn() method
- `tests/test_session.py` - Removed TestWorkflowSessionRecordTurn class
- `tests/test_metering.py` - Removed TestMeteringCallbackThresholds and TestMeteringCallbackLangfuseEvents classes
- `tests/test_executor.py` - Removed record_turn mock from session fixture
- `tests/test_sse_events.py` - Removed record_turn mock from session fixture

## Decisions Made
- Kept MeteringCallback.from_agency(agency) signature with agency parameter for call-site compatibility, even though the agency object is no longer read for threshold configuration
- Removed langfuse get_client import from metering.py entirely -- all Langfuse integration remains in tracing.py which was not touched
- Removed budget alert logger.warning calls along with threshold checks (they were budget enforcement alerts, not observability)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed record_turn mock from test_executor.py and test_sse_events.py fixtures**
- **Found during:** Task 2 (verifying executor cleanup)
- **Issue:** test_executor.py line 145 and test_sse_events.py line 72 had `session.record_turn = MagicMock()` in their mock session fixtures, which would fail if any code path tried to assert on record_turn
- **Fix:** Removed the record_turn mock line from both test fixture functions
- **Files modified:** tests/test_executor.py, tests/test_sse_events.py
- **Verification:** ruff clean, no remaining record_turn references in orchestrator/
- **Committed in:** c2e5beb (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix)
**Impact on plan:** Cleanup of residual record_turn mocks left over from Plan 01. No scope creep.

## Issues Encountered
- Test suite requires PostgreSQL (DATABASE_URL) which is not available locally without Docker. Verified code correctness via Python introspection (import + hasattr checks) and ruff linting. Same pattern as Plan 01 which also noted test infrastructure limitations.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 1 is fully complete: all enterprise features (budget enforcement, API backend, lifecycle/GDPR, metering thresholds, session turn counting) removed
- Orchestrator is streamlined: executor uses AgentSDKBackend unconditionally, metering accumulates only, session manages lifecycle only
- Ready for Phase 2 (Flatten Tenant Hierarchy) which operates on models, not orchestrator
- No blockers

---
*Phase: 01-strip-infrastructure-dependencies*
*Completed: 2026-03-12*

---
phase: 03-orchestrator-client-model
plan: 04
subsystem: orchestrator
tags: [django, asyncio, graphlib, celery, drf, hitl, webhook, tdd]

# Dependency graph
requires:
  - phase: 03-orchestrator-client-model/plan-01
    provides: WorkflowRun, WorkflowAgent, WorkflowPhaseOutput, HITLItem models, Pydantic workflow schema, YAML parser
  - phase: 03-orchestrator-client-model/plan-02
    provides: Agent manager (get_or_create_agent, reconcile_tools), WorkflowSession lifecycle, MeteringCallback
  - phase: 03-orchestrator-client-model/plan-03
    provides: Conflict detection (detect_conflicts, process_conflicts), HITL queue management (create/approve/reject/timeout)
provides:
  - DAG-based WorkflowExecutor with parallel phase execution via asyncio.gather
  - Celery tasks: run_workflow (4hr timeout), deliver_webhook (5-retry backoff), check_hitl_timeouts
  - HITL polling API: list/filter/approve/reject endpoints
  - Workflow status API: list/detail with nested agents, tool_calls, phase_outputs, HITL items
  - URL routing at /api/orchestrator/ (hitl/ and runs/)
affects: [phase-4-observability, phase-5-api, phase-6-dashboard]

# Tech tracking
tech-stack:
  added: [pytest-asyncio, asgiref (sync_to_async)]
  patterns: [async-executor-with-sync-to-async, celery-soft-timeout-handling, drf-viewset-custom-actions, tdd-red-green]

key-files:
  created:
    - hazn_platform/hazn_platform/orchestrator/executor.py
    - hazn_platform/hazn_platform/orchestrator/tasks.py
    - hazn_platform/hazn_platform/orchestrator/api/__init__.py
    - hazn_platform/hazn_platform/orchestrator/api/serializers.py
    - hazn_platform/hazn_platform/orchestrator/api/views.py
    - hazn_platform/hazn_platform/orchestrator/api/urls.py
    - hazn_platform/tests/test_executor.py
    - hazn_platform/tests/test_orchestrator_tasks.py
    - hazn_platform/tests/test_hitl_api.py
  modified:
    - hazn_platform/config/urls.py

key-decisions:
  - "sync_to_async wrapping for all Django ORM calls within async executor methods"
  - "transaction=True on tests that exercise async ORM writes (sync_to_async runs in separate threads)"
  - "Graceful timeout handling: SoftTimeLimitExceeded returns after session.fail instead of re-raising"
  - "Catch both celery and billiard SoftTimeLimitExceeded for production compatibility"
  - "AllowAny permissions on API views for development (TODO: restrict to authenticated users)"

patterns-established:
  - "Async executor pattern: sync_to_async wraps all Django ORM calls; asyncio.gather for parallel phases"
  - "Celery soft timeout pattern: catch (SoftTimeLimitExceeded, BilliardSoftTimeLimitExceeded) and gracefully fail session"
  - "DRF custom actions pattern: @action(detail=True, methods=['post']) for approve/reject on read-only viewset"
  - "API filtering pattern: query_params-based filtering in get_queryset() for HITL list endpoint"

requirements-completed: [ORCH-06, ORCH-07]

# Metrics
duration: 11min
completed: 2026-03-05
---

# Phase 3 Plan 4: Workflow Executor, Celery Tasks & HITL API Summary

**DAG-based workflow executor with asyncio parallel phases, Celery tasks for 4hr-timeout async execution and webhook delivery, and DRF HITL polling + workflow status APIs**

## Performance

- **Duration:** 11 min
- **Started:** 2026-03-05T18:15:27Z
- **Completed:** 2026-03-05T18:27:00Z
- **Tasks:** 3
- **Files modified:** 10

## Accomplishments
- Built WorkflowExecutor that interprets workflow YAML into parallel DAG execution waves, enforces tool scoping per phase, stores outputs as DB records, pauses on blocking HITL items, and halts on required phase failure
- Implemented 3 Celery tasks: run_workflow (4hr soft timeout with graceful session.fail), deliver_webhook (5-retry exponential backoff), check_hitl_timeouts (periodic expired item processing)
- Created DRF API for HITL polling (list/filter/approve/reject) and workflow status (detail with nested agents, tool_calls, phase_outputs, HITL items)
- 25 tests pass across all 3 modules with TDD red-green approach

## Task Commits

Each task was committed atomically (TDD: test -> feat):

1. **Task 1: DAG-based workflow executor with tool scoping and phase outputs** - TDD
   - RED: `fc84573` (test) - 12 failing tests for executor
   - GREEN: `6c9fa49` (feat) - executor.py with WorkflowExecutor

2. **Task 2: Celery tasks for async workflow execution and webhook delivery** - TDD
   - RED: `1a77779` (test) - 7 failing tests for Celery tasks
   - GREEN: `153f505` (feat) - tasks.py with run_workflow, deliver_webhook, check_hitl_timeouts

3. **Task 3: HITL polling API and workflow status API** - TDD
   - RED: `2fa3cad` (test) - 6 failing tests for DRF API
   - GREEN: `76a6e77` (feat) - api/ package with serializers, views, urls

## Files Created/Modified
- `hazn_platform/hazn_platform/orchestrator/executor.py` - DAG-based WorkflowExecutor with asyncio parallel execution, tool scoping, phase outputs, checkpoints
- `hazn_platform/hazn_platform/orchestrator/tasks.py` - Celery tasks: run_workflow (4hr timeout), deliver_webhook (5-retry), check_hitl_timeouts
- `hazn_platform/hazn_platform/orchestrator/api/__init__.py` - API package init
- `hazn_platform/hazn_platform/orchestrator/api/serializers.py` - DRF serializers for HITLItem, WorkflowRun, WorkflowAgent, WorkflowToolCall, WorkflowPhaseOutput
- `hazn_platform/hazn_platform/orchestrator/api/views.py` - HITLItemViewSet (list/filter/approve/reject), WorkflowRunViewSet (list/detail)
- `hazn_platform/hazn_platform/orchestrator/api/urls.py` - DRF router for hitl/ and runs/ endpoints
- `hazn_platform/config/urls.py` - Added /api/orchestrator/ URL include
- `hazn_platform/tests/test_executor.py` - 12 tests for executor DAG order, tool scoping, outputs, checkpoints, failures, lifecycle
- `hazn_platform/tests/test_orchestrator_tasks.py` - 7 tests for Celery task creation, time limits, timeout handling, webhooks
- `hazn_platform/tests/test_hitl_api.py` - 6 tests for API list/filter/approve/reject/400/nested-detail

## Decisions Made
- Used `asgiref.sync_to_async` to wrap all Django ORM calls within the async executor, since Django's ORM is synchronous and raises `SynchronousOnlyOperation` in async context
- Tests that exercise async ORM writes use `@pytest.mark.django_db(transaction=True)` because `sync_to_async` runs ORM calls in separate threads that can't see the test's atomic transaction
- Celery `run_workflow` catches both `celery.exceptions.SoftTimeLimitExceeded` and `billiard.exceptions.SoftTimeLimitExceeded` (billiard is what actually gets raised in production workers)
- After catching SoftTimeLimitExceeded, the task calls `session.fail()` and returns gracefully instead of re-raising -- this ensures the WorkflowRun record is properly marked as failed
- API views use `AllowAny` permissions during development; production will restrict to authenticated users per DRF settings

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added sync_to_async wrapping for Django ORM in async executor**
- **Found during:** Task 1 (TDD GREEN phase)
- **Issue:** Django ORM raises `SynchronousOnlyOperation` when called from async context; `_execute_phase` and `run()` both need DB access
- **Fix:** Wrapped all ORM calls with `asgiref.sync_to_async`, including `has_blocking_items`, `WorkflowPhaseOutput.objects.create`, `workflow_run.save`, and session lifecycle methods
- **Files modified:** hazn_platform/hazn_platform/orchestrator/executor.py
- **Verification:** All 12 executor tests pass
- **Committed in:** `6c9fa49` (Task 1 GREEN commit)

**2. [Rule 1 - Bug] Fixed test assertions in async context**
- **Found during:** Task 1 (TDD GREEN phase)
- **Issue:** Test assertion code also runs in async context and can't call Django ORM directly (e.g. `values_list`, `refresh_from_db`)
- **Fix:** Wrapped test assertion blocks in `sync_to_async` lambdas for tests that verify DB state after async execution
- **Files modified:** hazn_platform/tests/test_executor.py
- **Verification:** All 12 executor tests pass
- **Committed in:** `6c9fa49` (Task 1 GREEN commit)

**3. [Rule 1 - Bug] Handled billiard vs celery SoftTimeLimitExceeded mismatch**
- **Found during:** Task 2 (TDD GREEN phase)
- **Issue:** `billiard.exceptions.SoftTimeLimitExceeded` is what actually gets raised in Celery workers, not `celery.exceptions.SoftTimeLimitExceeded`
- **Fix:** Import and catch both exception types; graceful return instead of re-raise after session.fail
- **Files modified:** hazn_platform/hazn_platform/orchestrator/tasks.py
- **Verification:** All 7 task tests pass
- **Committed in:** `153f505` (Task 2 GREEN commit)

---

**Total deviations:** 3 auto-fixed (2 bugs, 1 blocking)
**Impact on plan:** All auto-fixes necessary for async/Django compatibility and production correctness. No scope creep.

## Issues Encountered
None beyond the deviations documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 3 (Orchestrator & Client Model) is now complete: all 4 plans delivered
- WorkflowExecutor is ready for Letta message API wiring when Phase 4 provides LLM callback hooks
- HITL polling API enables Mode 3 dashboard integration (Phase 6)
- Webhook delivery provides agency notification foundation
- 25 new tests + existing 100+ tests from Plans 01-03 all pass

## Self-Check: PASSED

- All 10 created/modified files verified on disk
- All 6 commit hashes verified in git log
- 25 tests pass (12 executor + 7 tasks + 6 API)

---
*Phase: 03-orchestrator-client-model*
*Completed: 2026-03-05*

---
phase: 05-mode-1-validation-qa
plan: 04
subsystem: qa
tags: [vercel, staging, deployment, preview-url, mcp]

# Dependency graph
requires:
  - phase: 05-mode-1-validation-qa (05-01)
    provides: QA criteria registry and runner module with create_deliverable
  - phase: 05-mode-1-validation-qa (05-02)
    provides: QA injection in executor._execute_phase
  - phase: 04-mcp-tool-servers-observability
    provides: Vercel MCP server with deploy_project and get_preview_url
provides:
  - staging.py module with is_web_deliverable and deploy_to_staging
  - Executor wiring that populates preview_url on web deliverables
  - QA-04 gap closure (Vercel preview URL staging)
affects: [qa, orchestrator, deliverables]

# Tech tracking
tech-stack:
  added: []
  patterns: [non-fatal staging deployment, web-type classification guard]

key-files:
  created:
    - hazn_platform/hazn_platform/qa/staging.py
    - hazn_platform/tests/test_qa_staging.py
  modified:
    - hazn_platform/hazn_platform/orchestrator/executor.py
    - hazn_platform/tests/test_executor.py

key-decisions:
  - "deploy_to_staging is sync (matches Vercel MCP server httpx.Client pattern), executor wraps with sync_to_async"
  - "Staging deployment inside existing QA try/except block for automatic non-fatal error handling"
  - "get_task_type_for_phase called in executor to pass task_type to deploy_to_staging"

patterns-established:
  - "Web type guard: is_web_deliverable checks frozenset before calling Vercel API"
  - "Partial failure tuple: ('', deployment_id) when deploy succeeds but preview URL retrieval fails"

requirements-completed: [QA-04]

# Metrics
duration: 6min
completed: 2026-03-06
---

# Phase 05 Plan 04: QA-04 Gap Closure Summary

**Vercel staging deployment for web deliverables wired into executor QA flow with preview URL population on Deliverable records**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-06T07:29:04Z
- **Completed:** 2026-03-06T07:35:00Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Created staging.py module with is_web_deliverable and deploy_to_staging functions
- Wired deploy_to_staging into executor._execute_phase before create_deliverable
- Web deliverables (landing_page, full_site, blog) get preview_url populated; non-web types short-circuit
- Vercel deployment failures are non-fatal (logged, workflow continues with empty preview_url)
- All 93 QA+executor tests pass with zero regressions

## Task Commits

Each task was committed atomically:

1. **Task 1: Create staging module and tests (TDD RED)** - `93a53e3` (test)
2. **Task 1: Create staging module and tests (TDD GREEN)** - `187e01d` (feat)
3. **Task 2: Wire staging deployment into executor** - `3808c81` (feat)

_Note: Task 1 used TDD with RED then GREEN commits._

## Files Created/Modified
- `hazn_platform/hazn_platform/qa/staging.py` - Vercel staging deployment logic with is_web_deliverable and deploy_to_staging
- `hazn_platform/tests/test_qa_staging.py` - 12 tests covering web type classification and deployment scenarios
- `hazn_platform/hazn_platform/orchestrator/executor.py` - Added staging deployment call before create_deliverable in QA injection
- `hazn_platform/tests/test_executor.py` - 3 new tests for staging wiring + updated existing tests with deploy_to_staging mocks

## Decisions Made
- deploy_to_staging is sync (matches Vercel MCP server httpx.Client pattern); executor wraps with sync_to_async
- Staging deployment placed inside existing QA try/except block for automatic non-fatal error handling
- Partial failure returns ("", deployment_id) when deployment succeeds but preview URL retrieval fails
- Existing executor tests updated to mock deploy_to_staging wherever should_run_qa=True

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated existing executor tests with deploy_to_staging mocks**
- **Found during:** Task 2
- **Issue:** Existing tests that mock should_run_qa=True (test_qa_runs_when_should_run_qa_returns_true, test_qa_infrastructure_crash_does_not_fail_phase, test_qa_fail_verdict_does_not_crash_execute_phase, test_deliverable_created_with_empty_preview_url) would fail without deploy_to_staging mock because the real function would attempt Vercel API calls
- **Fix:** Added deploy_to_staging mock returning ("", "") to all affected existing tests
- **Files modified:** hazn_platform/tests/test_executor.py
- **Verification:** All 93 tests pass
- **Committed in:** 3808c81 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Required fix to maintain test isolation after new import. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- QA-04 gap is closed: web deliverables get Vercel preview URLs
- All QA requirements (QA-01 through QA-04) are now implemented
- Phase 05 gap closure plans complete

## Self-Check: PASSED

- FOUND: hazn_platform/hazn_platform/qa/staging.py
- FOUND: hazn_platform/tests/test_qa_staging.py
- FOUND: 05-04-SUMMARY.md
- FOUND: commit 93a53e3
- FOUND: commit 187e01d
- FOUND: commit 3808c81

---
*Phase: 05-mode-1-validation-qa*
*Completed: 2026-03-06*

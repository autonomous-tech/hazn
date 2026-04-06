---
phase: 03-orchestrator-client-model
plan: 03
subsystem: orchestrator
tags: [django, conflict-detection, hitl, state-machine, tdd, llm-stub]

# Dependency graph
requires:
  - phase: 03-orchestrator-client-model
    provides: HITLItem model, WorkflowRun model, Agency/EndClient models, BrandVoice model
provides:
  - L2/L3 conflict detection logic (detect_conflicts, run_conflict_check_llm, process_conflicts)
  - HITL queue management with state machine (create, approve, reject, timeout, query)
  - Configurable timeout actions per trigger type
  - Agency-level non-blocking override via tool_preferences.hitl_config
  - Blocking item detection for workflow pause/resume
affects: [03-04, phase-4-observability, phase-5-api]

# Tech tracking
tech-stack:
  added: []
  patterns: [severity-based-conflict-resolution, hitl-state-machine, default-timeout-actions, tdd-red-green]

key-files:
  created:
    - hazn_platform/hazn_platform/orchestrator/conflict_detector.py
    - hazn_platform/hazn_platform/orchestrator/hitl.py
    - hazn_platform/tests/test_conflict_detector.py
    - hazn_platform/tests/test_hitl.py
  modified: []

key-decisions:
  - "run_conflict_check_llm implemented as stub returning empty list; actual LLM call deferred to Phase 4 when Langfuse tracing is available"
  - "process_conflicts creates HITL items with status=AUTO_RESOLVED immediately (not pending then auto-resolved) since conflicts are resolved at session start as pre-flight"
  - "process_expired_items filters with 1-hour minimum age as DB optimization, then checks per-item timeout_hours in Python"

patterns-established:
  - "Conflict resolution pattern: hard severity -> l2_override, soft severity -> l3_wins, all auto_resolved=True"
  - "HITL state machine: pending -> approved|rejected|auto_resolved|timed_out with status validation"
  - "DEFAULT_TIMEOUT_ACTIONS dict for trigger_type -> timeout_action mapping"
  - "Agency non-blocking override: tool_preferences.hitl_config.{trigger_type}.blocking"

requirements-completed: [CLT-04, CLT-05, CLT-06, ORCH-05]

# Metrics
duration: 4min
completed: 2026-03-05
---

# Phase 3 Plan 3: Conflict Detection & HITL Queue Summary

**L2/L3 conflict detection with severity-based resolution (hard=l2_override, soft=l3_wins) and full HITL state machine with configurable timeout actions per trigger type**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-05T18:06:35Z
- **Completed:** 2026-03-05T18:11:01Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Built conflict detector that extracts locked_rules from Agency.house_style, fetches active BrandVoice, and resolves per severity (hard=l2_override, soft=l3_wins) with all conflicts auto-resolved at session start
- Implemented HITL queue management with full state machine: create with default timeout_action per trigger type, approve/reject with pending validation, timeout processing (l3_wins/auto_approve/proceed_with_warning -> auto_resolved, halt -> timed_out)
- Added blocking item detection (get_blocking_items_for_run, has_blocking_items) enabling workflow pause/resume logic
- 30 tests pass across both modules with TDD red-green approach

## Task Commits

Each task was committed atomically (TDD: test -> feat):

1. **Task 1: Implement L2/L3 conflict detection with LLM-based comparison** - TDD
   - RED: `2e87b62` (test) - 11 failing tests for conflict detection
   - GREEN: `0550c83` (feat) - conflict_detector.py with detect/process/stub

2. **Task 2: Implement HITL queue management with state machine and timeout processing** - TDD
   - RED: `03f3ce5` (test) - 19 failing tests for HITL management (note: 3 extra tests added for completeness)
   - GREEN: `e40aa06` (feat) - hitl.py with create/approve/reject/timeout/query

## Files Created/Modified
- `hazn_platform/hazn_platform/orchestrator/conflict_detector.py` - L2/L3 conflict detection: detect_conflicts, run_conflict_check_llm (stub), process_conflicts
- `hazn_platform/hazn_platform/orchestrator/hitl.py` - HITL queue management: create, approve, reject, process_expired, get_pending/blocking, has_blocking
- `hazn_platform/tests/test_conflict_detector.py` - 11 tests for conflict detection and resolution
- `hazn_platform/tests/test_hitl.py` - 19 tests for HITL state machine, timeouts, queries

## Decisions Made
- LLM stub: `run_conflict_check_llm` returns empty list for now; actual LLM call will be wired when Langfuse tracing is added in Phase 4. This avoids LLM dependency in tests while testing the full flow.
- Auto-resolved status: `process_conflicts` creates HITL items with status=AUTO_RESOLVED immediately rather than creating as PENDING then transitioning, since conflict detection is a pre-flight check at session start (not an ongoing process).
- Expired item query optimization: `process_expired_items` pre-filters items older than 1 hour at DB level, then checks per-item `timeout_hours` in Python to avoid complex DB expressions while maintaining correctness.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Conflict detector ready for session lifecycle integration (Plan 03-02 calls detect_conflicts + process_conflicts at session start)
- HITL queue ready for API exposure (Plan 03-04 or Phase 5)
- run_conflict_check_llm stub ready for LLM wiring in Phase 4 (Langfuse observability)
- Blocking item detection enables workflow flow control in the DAG executor

## Self-Check: PASSED

- All 4 created files verified on disk
- All 4 commit hashes verified in git log
- 30 tests pass (11 conflict detector + 19 HITL)

---
*Phase: 03-orchestrator-client-model*
*Completed: 2026-03-05*

---
phase: 05-memory-rewiring
plan: 01
subsystem: memory
tags: [letta, sdk, memory, passages, search, agent-provisioning]

# Dependency graph
requires:
  - phase: 04-executor-rewrite
    provides: "WorkflowSession, HaznMemory class, agent-per-client pattern"
provides:
  - "Fixed search_memory using item.passage.text and item.score (Letta SDK v1.7.11)"
  - "Fixed agent provisioning with list() wrapper for SyncArrayPage"
  - "Removed dead record_turn() method"
  - "Updated test mocks matching real SDK response shapes"
affects: [05-memory-rewiring, 06-chat-view]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "PassageSearchResponseItem iteration: for item in search_response (not .results)"
    - "SDK score usage: item.score for similarity (not positional rank)"
    - "SyncArrayPage conversion: list(client.agents.list(...)) for truthiness check"

key-files:
  created: []
  modified:
    - hazn_platform/hazn_platform/core/memory.py
    - hazn_platform/hazn_platform/orchestrator/session.py
    - hazn_platform/tests/test_memory.py

key-decisions:
  - "Use SDK-provided item.score for similarity weight instead of positional rank -- more accurate relevance ordering"
  - "Remove record_turn() entirely (dead code per STRP-08) rather than leaving stub"

patterns-established:
  - "Letta SDK list pattern: always wrap agents.list() with list() before truthiness checks"
  - "Passage access pattern: item.passage.text and item.passage.id (not .content or .id on item)"

requirements-completed: [MEMO-01, MEMO-02, MEMO-04, MEMO-05]

# Metrics
duration: 7min
completed: 2026-03-13
---

# Phase 5 Plan 1: Letta SDK API Mismatch Fixes Summary

**Fixed three critical Letta SDK v1.7.11 API mismatches in search_memory, agent provisioning, and passage access patterns**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-13T11:46:49Z
- **Completed:** 2026-03-13T11:53:49Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Fixed search_memory() to use item.passage.text and item.score instead of result.content and positional rank
- Fixed session.py agent provisioning to wrap agents.list() with list() for correct SyncArrayPage handling
- Removed dead record_turn() method (STRP-08 decision)
- Updated all test mocks to match real Letta SDK v1.7.11 response shapes (PassageSearchResponseItem)
- Added new tests: empty search results, session get-or-create (both paths)
- 38 tests passing (6 pre-existing failures from missing tool_preferences field -- out of scope)

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix Letta SDK API mismatches in memory.py and session.py** - `9fb80e8` (fix)
2. **Task 2: Update unit tests for correct SDK response shapes** - `62451e6` (test)

## Files Created/Modified
- `hazn_platform/hazn_platform/core/memory.py` - Fixed search_memory() SDK access patterns, removed record_turn()
- `hazn_platform/hazn_platform/orchestrator/session.py` - Wrapped agents.list() with list() for SyncArrayPage
- `hazn_platform/tests/test_memory.py` - Updated mocks to PassageSearchResponseItem shape, added session tests

## Decisions Made
- Use SDK-provided item.score for similarity weight instead of positional rank -- more accurate relevance ordering since Letta returns a float score, not just ordering
- Remove record_turn() entirely rather than leaving a deprecation stub -- it was dead code per STRP-08 decision from Phase 1

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Pre-existing test failures (6 tests) due to missing `tool_preferences` field on Agency model -- these are documented in STATE.md as known pre-existing issues and are out of scope for this plan

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- search_memory(), correct_memory(), and agent provisioning now match Letta SDK v1.7.11 API
- Ready for Phase 5 Plans 2-4 (block schema, memory cleanup, integration tests)
- Pre-existing tool_preferences issue should be addressed in a future plan (Agency model migration)

## Self-Check: PASSED

- All 3 modified files exist on disk
- Both task commits (9fb80e8, 62451e6) verified in git log
- 38/38 tests pass (6 pre-existing failures excluded)

---
*Phase: 05-memory-rewiring*
*Completed: 2026-03-13*

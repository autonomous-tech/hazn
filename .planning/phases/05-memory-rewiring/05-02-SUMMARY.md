---
phase: 05-memory-rewiring
plan: 02
subsystem: memory
tags: [letta, memory, tools, learning-extraction, agent-sdk, management-command]

# Dependency graph
requires:
  - phase: 05-01
    provides: "Fixed search_memory, agent provisioning, passage access patterns"
provides:
  - "add_learning agent tool wrapping HaznMemory.add_learning() with defaults"
  - "_auto_extract_learnings dual-strategy extractor (JSON + text patterns) in executor"
  - "Auto-extraction wired into _execute_phase() post-output, pre-checkpoint"
  - "test_memory management command for manual Letta lifecycle testing"
affects: [05-memory-rewiring, 06-chat-view]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Dual learning capture: explicit add_learning tool (confidence=0.7) + auto-extraction fallback (confidence=0.6)"
    - "getattr(tool, 'handler', tool) pattern for SDK/stub-agnostic tool invocation in tests"
    - "Module-level regex compilation for text pattern matching"

key-files:
  created:
    - hazn_platform/hazn_platform/core/management/commands/test_memory.py
  modified:
    - hazn_platform/hazn_platform/orchestrator/tools/memory.py
    - hazn_platform/hazn_platform/orchestrator/executor.py
    - hazn_platform/tests/test_memory.py

key-decisions:
  - "Auto-extracted learnings use confidence=0.6 vs explicit tool calls at 0.7+ -- lower confidence reflects less intentional capture"
  - "Text pattern extraction only fires if JSON extraction finds no learnings -- avoids double-counting"

patterns-established:
  - "getattr(tool, 'handler', tool) for calling SDK tools in tests -- works with both real SdkMcpTool and stub _StubTool"
  - "Deferred import of CraftLearning/LearningSource to function body in executor -- avoids Django setup at import time"

requirements-completed: [MEMO-03]

# Metrics
duration: 6min
completed: 2026-03-13
---

# Phase 5 Plan 2: Learning Capture & Auto-Extraction Summary

**Dual-path learning capture via add_learning agent tool and auto-extraction from phase output, plus test_memory management command for manual Letta lifecycle testing**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-13T11:58:45Z
- **Completed:** 2026-03-13T12:05:17Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Added add_learning tool (tool #8) to memory tools with defaults: source=agent-inferred, confidence=0.7, agent_type=unknown
- Implemented _auto_extract_learnings with dual strategy: JSON "learnings" key extraction and regex text patterns (Key finding, I learned that, Note for future, Important insight)
- Wired auto-extraction into executor _execute_phase() to run after phase output storage and before checkpoint flush
- Created test_memory management command with full Letta lifecycle: create/get agent, load context, write learning, search, correct, verify
- 13 new tests all passing: add_learning tool (4 tests), auto-extraction (9 tests)

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: Failing tests** - `87d52b3` (test)
2. **Task 1 GREEN: add_learning tool + auto-extraction implementation** - `2eeb5fe` (feat)
3. **Task 2: test_memory management command** - `3407d32` (feat)

## Files Created/Modified
- `hazn_platform/hazn_platform/orchestrator/tools/memory.py` - Added add_learning tool (#8), updated MEMORY_TOOLS list
- `hazn_platform/hazn_platform/orchestrator/executor.py` - Added _auto_extract_learnings function and wired into _execute_phase()
- `hazn_platform/hazn_platform/core/management/commands/test_memory.py` - New management command for manual Letta lifecycle testing
- `hazn_platform/tests/test_memory.py` - 13 new tests for add_learning tool and auto-extraction

## Decisions Made
- Auto-extracted learnings use confidence=0.6 (lower than explicit add_learning tool calls at 0.7+) to reflect less intentional capture
- Text pattern extraction only fires when JSON extraction finds no learnings to avoid double-counting from mixed-format output
- getattr(tool, 'handler', tool) pattern used in tests for SDK/stub compatibility

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed test tool invocation for real SDK environment**
- **Found during:** Task 1 GREEN phase
- **Issue:** Tests called `await add_learning({...})` but real SDK returns SdkMcpTool which is not directly callable
- **Fix:** Used `getattr(add_learning_tool, 'handler', add_learning_tool)` pattern to get the callable handler
- **Files modified:** hazn_platform/tests/test_memory.py
- **Verification:** All 13 tests pass
- **Committed in:** 2eeb5fe (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary fix for test compatibility with real SDK environment. No scope creep.

## Issues Encountered
- Pre-existing test failures (17 tests) due to SQLite incompatibility with Postgres-specific queries -- documented in STATE.md as known pre-existing issues, out of scope for this plan

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- add_learning tool and auto-extraction ready for use in workflow execution
- test_memory command ready for manual Letta validation (requires running Docker Letta)
- Ready for Phase 5 Plans 3-4 (block schema, integration tests)

## Self-Check: PASSED

- All 4 modified/created source files exist on disk
- All 3 task commits (87d52b3, 2eeb5fe, 3407d32) verified in git log
- 13/13 new tests pass

---
*Phase: 05-memory-rewiring*
*Completed: 2026-03-13*

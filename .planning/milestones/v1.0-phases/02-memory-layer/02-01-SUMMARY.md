---
phase: 02-memory-layer
plan: 01
subsystem: memory
tags: [letta, pydantic, django-orm, memory-abstraction, archival-search, audit-trail]

# Dependency graph
requires:
  - phase: 01-infrastructure-foundation
    provides: Letta client factory, Django models (Agency, EndClient, BrandVoice, Keyword, Campaign), pgvector
provides:
  - HaznMemory swap-safe class wrapping all Letta SDK access
  - Pydantic type system (CraftLearning, StructuredFinding, ClientContext, LearningSource)
  - MemoryCorrection Django model with migration for audit trail
  - Context assembly from 5 Django models into Letta block
  - Semantic search with composite ranking (similarity + recency + confidence)
  - Cross-client insight queries from Postgres structured findings
  - Memory correction with soft-delete and replacement pattern
affects: [02-memory-layer, 03-agent-orchestration, 06-workspace-ui]

# Tech tracking
tech-stack:
  added: [pydantic v2 (BaseModel, model_validator)]
  patterns: [swap-safe Letta abstraction, metadata prefix tags in archival passages, composite search ranking, soft-delete correction with audit trail]

key-files:
  created:
    - hazn_platform/hazn_platform/core/memory_types.py
    - hazn_platform/hazn_platform/core/memory.py
    - hazn_platform/hazn_platform/core/migrations/0002_memorycorrection.py
    - hazn_platform/tests/test_memory.py
  modified:
    - hazn_platform/hazn_platform/core/models.py
    - hazn_platform/hazn_platform/core/admin.py

key-decisions:
  - "Letta block update API: client.agents.blocks.update(block_label, agent_id=..., value=...) -- positional block_label first"
  - "Letta search results use .content not .text; Passage objects use .text -- different attributes on different response types"
  - "LearningSource.value required in f-string metadata prefix (Python enum __str__ includes class name)"
  - "Composite ranking weights: similarity 0.6, recency 0.25, confidence 0.15 with exponential recency decay"
  - "Cross-client insights query all 4 finding types (keyword, audit, campaign, decision) from Postgres only"

patterns-established:
  - "Metadata prefix format: [source:X][confidence:X][agent:X][client:UUID][timestamp:ISO][status:active] on archival passages"
  - "Soft-delete pattern: delete original passage, create [status:corrected] marker, create active replacement"
  - "HaznMemory is per-session instance (not singleton) with _pending_learnings buffer"
  - "Django model imports inside methods to avoid circular imports (lazy imports)"

requirements-completed: [MEM-01, MEM-02, MEM-03, MEM-08, MEM-09]

# Metrics
duration: 10min
completed: 2026-03-05
---

# Phase 2 Plan 1: Memory Type System and HaznMemory Core Summary

**HaznMemory swap-safe Letta abstraction with Pydantic types, composite search ranking, cross-client Postgres insights, and MemoryCorrection audit model**

## Performance

- **Duration:** 10 min
- **Started:** 2026-03-05T14:30:05Z
- **Completed:** 2026-03-05T14:40:18Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- HaznMemory class as the sole Letta accessor -- swap-safe abstraction with 7 public methods
- Pydantic v2 type system with CraftLearning (user-explicit confidence defaulting), StructuredFinding, ClientContext, LearningSource enum
- Context assembly from 5 Django models (Agency, EndClient, BrandVoice, Keyword, Campaign) written to Letta active_client_context block
- Semantic search with composite ranking: similarity (0.6) + recency (0.25) + confidence (0.15) with exponential decay
- Cross-client insight queries from 4 Postgres structured finding types when agency enables flag
- Memory correction with soft-delete pattern, replacement passages, and full MemoryCorrection audit trail
- 32 unit tests passing with fully mocked Letta client

## Task Commits

Each task was committed atomically:

1. **Task 1: Define memory type system and MemoryCorrection model**
   - `3877069` (test) -- failing tests for types and model (TDD RED)
   - `fe27969` (feat) -- implement types, model, migration, admin (TDD GREEN)
2. **Task 2: Implement HaznMemory core methods with unit tests**
   - `4c120fd` (test) -- failing tests for HaznMemory methods (TDD RED)
   - `9e72e5b` (feat) -- implement HaznMemory class with all methods (TDD GREEN)

## Files Created/Modified
- `hazn_platform/hazn_platform/core/memory_types.py` -- Pydantic models: CraftLearning, StructuredFinding, ClientContext, LearningSource
- `hazn_platform/hazn_platform/core/memory.py` -- HaznMemory class (523 lines) with all core methods
- `hazn_platform/hazn_platform/core/models.py` -- Added MemoryCorrection Django model
- `hazn_platform/hazn_platform/core/admin.py` -- Registered MemoryCorrection in admin
- `hazn_platform/hazn_platform/core/migrations/0002_memorycorrection.py` -- Migration for MemoryCorrection
- `hazn_platform/tests/test_memory.py` -- 32 unit tests covering all types and methods

## Decisions Made
- **Letta block update API:** First positional argument is `block_label`, then `agent_id` as keyword. Verified from SDK source.
- **Search result attributes:** `PassageSearchResponse.results[].content` (not `.text`) and `Passage.text` -- different attributes on different response types. Important for correct implementation.
- **LearningSource enum in f-strings:** Must use `.value` to get string value in metadata prefix. Python enum `__str__` includes class name.
- **Recency decay formula:** Exponential decay `e^(-0.05 * age_days)` clamped to [0.1, 1.0]. Fresh (<1 day) = 1.0, 30+ days old = 0.1.
- **Cross-client insights:** Queries all 4 finding types (keyword, audit, campaign, decision) from Postgres only. No Letta cross-agent search per RESEARCH.md Open Question 4.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed LearningSource enum string representation in metadata prefix**
- **Found during:** Task 2 (HaznMemory implementation)
- **Issue:** `f"[source:{learning.source}]"` produced `[source:LearningSource.AGENT_INFERRED]` instead of `[source:agent-inferred]`
- **Fix:** Changed to `f"[source:{learning.source.value}]"` to use the enum's string value
- **Files modified:** hazn_platform/hazn_platform/core/memory.py
- **Verification:** Test `test_write_craft_learning_creates_passage_with_metadata` now passes
- **Committed in:** 9e72e5b (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Minor fix necessary for correct metadata tag format. No scope creep.

## Issues Encountered
- Pre-existing integration test failures (test_vault.py, test_letta.py) due to Docker hostname resolution when running tests outside Docker. Not caused by our changes -- these tests require the Docker network.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- HaznMemory foundation complete -- Plan 02-02 (session lifecycle) depends on checkpoint_sync, failure_sync, end_session methods which build on this class
- Plan 02-03 (MCP server) wraps HaznMemory methods as MCP tools
- MemoryCorrection migration needs to be applied via `python manage.py migrate core` before use

## Self-Check: PASSED

All 5 created files verified on disk. All 4 task commits verified in git log.

---
*Phase: 02-memory-layer*
*Completed: 2026-03-05*

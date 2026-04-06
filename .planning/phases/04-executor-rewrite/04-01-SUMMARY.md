---
phase: 04-executor-rewrite
plan: 01
subsystem: orchestrator
tags: [pydantic, django, letta, memory, workflow]

# Dependency graph
requires:
  - phase: 02-model-cleanup
    provides: WorkflowRun model without HITL fields, clean orchestrator models
  - phase: 03-tool-migration
    provides: ToolRegistry, SDK tool pattern
provides:
  - max_turns field on WorkflowPhaseSchema for per-phase turn limits
  - Clean WorkflowRun.Status enum (5 values, no BLOCKED)
  - WorkflowSession with one-Letta-agent-per-client pattern
  - Dead orchestrator files removed (agent_manager, backends/)
affects: [04-02 executor rewrite, 04-03 celery tasks, 05 memory-rewire]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "One Letta agent per client (client--{pk} naming)"
    - "Session loads client context once, caches for system prompt injection"
    - "Non-fatal Letta failures (log warning, return empty context)"

key-files:
  created:
    - hazn_platform/hazn_platform/orchestrator/migrations/0002_remove_blocked_status.py
  modified:
    - hazn_platform/hazn_platform/orchestrator/workflow_models.py
    - hazn_platform/hazn_platform/orchestrator/models.py
    - hazn_platform/hazn_platform/orchestrator/session.py
    - hazn_platform/hazn_platform/orchestrator/executor.py
    - hazn_platform/hazn_platform/orchestrator/prompt_assembler.py

key-decisions:
  - "Data migration for blocked->failed (RunPython, not schema migration) since TextChoices are strings"
  - "Comment out executor.py dead imports rather than delete (file will be fully rewritten in Plan 02)"
  - "load_client_context uses deferred import of get_letta_client to avoid top-level Letta dependency"

patterns-established:
  - "One Letta agent per client: client--{pk} naming convention"
  - "WorkflowSession.metering property exposes MeteringCallback for executor access"
  - "Non-fatal Letta integration: try/except with warning log, empty string fallback"

requirements-completed: [EXEC-01, EXEC-05]

# Metrics
duration: 4min
completed: 2026-03-13
---

# Phase 4 Plan 01: Foundation Cleanup Summary

**max_turns schema field, BLOCKED status removal, session.py rewrite for one-Letta-agent-per-client, and dead orchestrator file deletion**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-13T09:23:30Z
- **Completed:** 2026-03-13T09:28:25Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- WorkflowPhaseSchema now has max_turns=30 default field for per-phase turn limit configuration
- WorkflowRun.Status cleaned to 5 values (PENDING, RUNNING, COMPLETED, FAILED, TIMED_OUT) with data migration
- session.py rewritten with one-Letta-agent-per-client pattern: load_client_context creates/retrieves single Letta agent per client, caches context for system prompt injection
- Dead files deleted: agent_manager.py (182 lines), backends/__init__.py (23 lines), backends/agent_sdk.py (178 lines) -- 383 lines of dead code removed

## Task Commits

Each task was committed atomically:

1. **Task 1: Schema updates and dead code deletion** - `4abe5c3` (feat)
2. **Task 2: Rewrite session.py for one-Letta-agent-per-client** - `892038b` (feat)

## Files Created/Modified
- `hazn_platform/hazn_platform/orchestrator/workflow_models.py` - Added max_turns: int = 30 field to WorkflowPhaseSchema
- `hazn_platform/hazn_platform/orchestrator/models.py` - Removed BLOCKED from WorkflowRun.Status enum
- `hazn_platform/hazn_platform/orchestrator/migrations/0002_remove_blocked_status.py` - Data migration: blocked -> failed
- `hazn_platform/hazn_platform/orchestrator/session.py` - Full rewrite: one-agent-per-client Letta pattern
- `hazn_platform/hazn_platform/orchestrator/executor.py` - Commented out dead imports (full rewrite in Plan 02)
- `hazn_platform/hazn_platform/orchestrator/prompt_assembler.py` - Updated comments removing agent_manager references
- `hazn_platform/hazn_platform/orchestrator/agent_manager.py` - Deleted (replaced by session.py)
- `hazn_platform/hazn_platform/orchestrator/backends/__init__.py` - Deleted (directory removed)
- `hazn_platform/hazn_platform/orchestrator/backends/agent_sdk.py` - Deleted (absorbed into direct SDK calls)

## Decisions Made
- Data migration for blocked->failed uses RunPython (not schema migration) since TextChoices are just strings in Django -- makemigrations won't detect the enum change
- Commented out dead imports in executor.py rather than deleting them, since the entire file will be rewritten from scratch in Plan 02
- load_client_context uses deferred import of get_letta_client inside the method body to avoid pulling Letta as a top-level module dependency

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Cleaned up prompt_assembler.py comments referencing deleted agent_manager**
- **Found during:** Task 1 (dead code deletion)
- **Issue:** prompt_assembler.py docstrings referenced agent_manager.py which no longer exists
- **Fix:** Updated docstring comments to remove agent_manager references while preserving the self-contained design rationale
- **Files modified:** hazn_platform/hazn_platform/orchestrator/prompt_assembler.py
- **Verification:** File parses correctly, no functional changes
- **Committed in:** 4abe5c3 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Minor documentation cleanup, no scope creep.

## Issues Encountered
- Django setup fails without DATABASE_URL environment variable, so verification commands requiring `django.setup()` were replaced with AST-based and text-based analysis. All interface contracts verified without full Django environment.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- WorkflowPhaseSchema with max_turns is ready for executor to consume in Plan 02
- WorkflowSession with load_client_context/get_client_context is ready for executor to call
- Dead files removed, no dangling imports in kept files (except executor.py which is rewritten next)
- Plan 02 (executor rewrite) can proceed immediately

## Self-Check: PASSED

- All created/modified files verified present on disk
- Both deleted files (agent_manager.py, backends/) confirmed absent
- Both task commits (4abe5c3, 892038b) verified in git log
- SUMMARY.md created at expected path

---
*Phase: 04-executor-rewrite*
*Completed: 2026-03-13*

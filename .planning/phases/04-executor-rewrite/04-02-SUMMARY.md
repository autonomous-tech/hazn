---
phase: 04-executor-rewrite
plan: 02
subsystem: orchestrator
tags: [agent-sdk, dag-walker, sse, jinja2, workflow, async]

# Dependency graph
requires:
  - phase: 04-executor-rewrite
    plan: 01
    provides: WorkflowPhaseSchema.max_turns, clean WorkflowRun.Status enum, WorkflowSession with one-Letta-agent-per-client
  - phase: 03-tool-migration
    provides: ToolRegistry, SDK tool pattern, _REGISTRY_SINGLETON
provides:
  - WorkflowExecutor class with DAG walker and direct SDK query() calls
  - build_prior_phase_section() for dependency output injection into system prompts
  - Retry-once logic for required phases
  - Optional phase skip cascading via _skipped_phases tracking
  - SSE events at all phase/workflow boundaries
  - Delivery phase HTML rendering via Jinja2 pipeline
  - agent_runner.py deleted (RuntimeBackend, RunResult, dispatch_tool_async removed)
affects: [04-03 celery tasks, 05 memory-rewire, test rewrite]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Direct Agent SDK query() per phase (no RuntimeBackend protocol)"
    - "build_prior_phase_section injects only direct dependency outputs (not all prior phases)"
    - "Cap 10 findings per phase in prior phase section (token budget management)"
    - "_emit_event helper wraps all SSE calls with non-fatal try/except"
    - "Registry injected via constructor, fallback to singleton for flexibility"

key-files:
  created: []
  modified:
    - hazn_platform/hazn_platform/orchestrator/executor.py
  deleted:
    - hazn_platform/hazn_platform/orchestrator/agent_runner.py

key-decisions:
  - "Direct dependency output injection only (not all prior phases) -- reduces token usage, aligns with DAG semantics"
  - "Registry passed via constructor for testability, with singleton fallback for production"
  - "Generalized delivery detection via 'branded_html_report' in phase.outputs (not hardcoded phase.id == 'delivery')"
  - "Non-fatal SSE emission via _emit_event helper -- SSE failures never halt workflow"

patterns-established:
  - "WorkflowExecutor(workflow, session, registry) constructor pattern"
  - "async _execute_with_retry wraps _execute_phase with retry-once for required phases"
  - "build_prior_phase_section as module-level function for testability"
  - "_phase_outputs dict caches WorkflowPhaseOutput for cross-phase injection"

requirements-completed: [EXEC-01, EXEC-02, EXEC-03, EXEC-04, EXEC-06]

# Metrics
duration: 3min
completed: 2026-03-13
---

# Phase 4 Plan 02: Executor Rewrite Summary

**Clean DAG-walking executor with direct Agent SDK query() calls, prior-phase output injection, retry-once for required phases, optional skip cascading, and SSE events at all boundaries**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-13T09:32:08Z
- **Completed:** 2026-03-13T09:35:43Z
- **Tasks:** 2
- **Files modified:** 2 (1 rewritten, 1 deleted)

## Accomplishments
- executor.py rewritten from scratch (558 lines) as clean DAG walker calling Agent SDK query() directly per phase
- Prior phase output injection via build_prior_phase_section() with 10-finding cap per phase
- Retry-once logic for required phases, skip cascading for optional phases with _skipped_phases tracking
- agent_runner.py fully deleted -- RuntimeBackend protocol, RunResult, dispatch_tool_async, AgentRunner class all removed (291 lines deleted)
- Delivery phase HTML rendering generalized to check for "branded_html_report" in phase.outputs

## Task Commits

Each task was committed atomically:

1. **Task 1: Rewrite executor.py from scratch** - `f5222d7` (feat)
2. **Task 2: Delete agent_runner.py** - `5be9217` (chore)

## Files Created/Modified
- `hazn_platform/hazn_platform/orchestrator/executor.py` - Complete rewrite: WorkflowExecutor with DAG walker, direct SDK calls, prior phase injection, retry/skip logic, SSE events, delivery rendering
- `hazn_platform/hazn_platform/orchestrator/agent_runner.py` - Deleted (replaced by direct SDK calls in executor.py)

## Decisions Made
- Inject only direct dependency outputs (phases listed in depends_on), not all prior phases -- reduces token usage and aligns with DAG semantics
- Generalized delivery phase detection via "branded_html_report" in phase.outputs instead of hardcoded phase.id == "delivery"
- Registry injected via constructor with singleton fallback -- enables test injection while maintaining production compatibility
- Non-fatal SSE emission via _emit_event helper -- all SSE calls wrapped in try/except to prevent SSE failures from halting workflow

## Deviations from Plan

None -- plan executed exactly as written.

## Issues Encountered
- Django setup not available in verification environment (no DATABASE_URL), so all verification was done via AST analysis and text assertions. All interface contracts verified without full Django environment.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- executor.py is ready for Celery task wiring in Plan 03
- ToolRegistry constructor injection enables clean test mocking
- All dead code (AgentRunner, RuntimeBackend, RunResult, dispatch_tool_async) removed
- Test files still reference deleted agent_runner.py -- will be rewritten/deleted in Plan 03

## Self-Check: PASSED

- executor.py verified present on disk
- agent_runner.py confirmed deleted
- Both task commits (f5222d7, 5be9217) verified in git log
- SUMMARY.md created at expected path

---
*Phase: 04-executor-rewrite*
*Completed: 2026-03-13*

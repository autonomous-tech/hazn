---
phase: 04-mcp-tool-servers-observability
plan: 03
subsystem: observability
tags: [langfuse, openai, gpt-4o-mini, tracing, metering, mcp]

# Dependency graph
requires:
  - phase: 04-01
    provides: langfuse_trace_id field on WorkflowRun model, Langfuse settings in base.py
  - phase: 03-01
    provides: WorkflowExecutor, WorkflowSession, MeteringCallback, conflict_detector
provides:
  - Langfuse v3 tracing module (init_langfuse, start_workflow_trace, start_phase_span, start_tool_span)
  - MeteringCallback.on_tool_call for per-tool call count and latency tracking
  - WorkflowToolCall database records populated via flush_to_db
  - Dual-write threshold alerts (callback + Langfuse event annotation)
  - Real gpt-4o-mini conflict detection via langfuse.openai drop-in
affects: [05-workflow-yaml-celery, 06-api-admin]

# Tech tracking
tech-stack:
  added: [langfuse.openai drop-in for auto-traced OpenAI calls]
  patterns: [non-fatal tracing wrappers, dual-write alerting, sync function calls via sync_to_async for Langfuse SDK]

key-files:
  created:
    - hazn_platform/hazn_platform/orchestrator/tracing.py
    - hazn_platform/tests/test_tracing.py
  modified:
    - hazn_platform/hazn_platform/orchestrator/executor.py
    - hazn_platform/hazn_platform/orchestrator/metering.py
    - hazn_platform/hazn_platform/orchestrator/conflict_detector.py
    - hazn_platform/tests/test_metering.py
    - hazn_platform/tests/test_conflict_detector.py

key-decisions:
  - "Langfuse tracing uses sync function calls (not context managers) to avoid contextvars issues across sync_to_async boundaries"
  - "Threshold alerts dual-write to both callback and Langfuse event for full observability"
  - "Conflict detection uses langfuse.openai drop-in for automatic LLM call tracing"
  - "All tracing/Langfuse operations are non-fatal with try/except fallbacks"

patterns-established:
  - "Non-fatal tracing: all Langfuse operations wrapped in try/except, returning None on failure"
  - "Dual-write alerting: threshold alerts create both HITL items (via callback) and Langfuse events"
  - "langfuse.openai drop-in: import from langfuse.openai instead of openai for auto-traced LLM calls"

requirements-completed: [OBS-01, OBS-02, OBS-03, OBS-04, OBS-05]

# Metrics
duration: 5min
completed: 2026-03-06
---

# Phase 04 Plan 03: Langfuse Tracing, Tool Metering, and Real Conflict Detection Summary

**Langfuse v3 tracing with l2/l3/run tags on every workflow, per-tool call metering via WorkflowToolCall records, dual-write threshold alerts, and real gpt-4o-mini conflict detection via langfuse.openai drop-in**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-06T03:37:08Z
- **Completed:** 2026-03-06T03:43:06Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- Langfuse v3 tracing module with non-fatal wrappers that create traces with l2/l3/run tags and store trace_id on WorkflowRun
- MeteringCallback.on_tool_call() accumulates per-tool call count, latency, and success; flush_to_db writes WorkflowToolCall records
- Threshold alerts now dual-write to both callback (existing) and Langfuse event annotation (new) for full observability
- Conflict detection stub replaced with real gpt-4o-mini call via langfuse.openai drop-in with graceful fallback on API errors

## Task Commits

Each task was committed atomically:

1. **Task 1: Create Langfuse tracing module and wire into executor** - `459bae7` (test), `7b114e0` (feat)
2. **Task 2: Add tool call metering, runaway dual-write alerts, and real conflict detection** - `9653c86` (test), `634291a` (feat)

_Note: TDD tasks have two commits each (test RED -> feat GREEN)_

## Files Created/Modified
- `hazn_platform/hazn_platform/orchestrator/tracing.py` - Langfuse v3 tracing: init_langfuse, start_workflow_trace, start_phase_span, start_tool_span
- `hazn_platform/hazn_platform/orchestrator/executor.py` - Wired start_workflow_trace after session.start via sync_to_async
- `hazn_platform/hazn_platform/orchestrator/metering.py` - Added on_tool_call, _tool_meters, WorkflowToolCall flush, Langfuse event annotation
- `hazn_platform/hazn_platform/orchestrator/conflict_detector.py` - Replaced stub with real gpt-4o-mini call via langfuse.openai
- `hazn_platform/tests/test_tracing.py` - 12 tests for tracing module with mocked Langfuse client
- `hazn_platform/tests/test_metering.py` - Added 6 tests for tool call metering and Langfuse events
- `hazn_platform/tests/test_conflict_detector.py` - Added 6 tests for real LLM conflict detection

## Decisions Made
- Langfuse tracing uses sync function calls (not context managers) to avoid contextvars issues across sync_to_async thread boundaries -- the Langfuse v3 SDK uses contextvars which don't propagate across threads
- Threshold alerts dual-write to both callback and Langfuse event for complete observability pipeline
- Conflict detection uses `from langfuse.openai import openai` drop-in for automatic LLM call tracing without any explicit Langfuse instrumentation
- All tracing and Langfuse operations are non-fatal with try/except fallbacks returning None -- workflows never blocked by tracing failures

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required. Langfuse settings (LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST) were already added in Plan 04-01.

## Next Phase Readiness
- Complete observability pipeline: Langfuse traces for debugging, Postgres records for billing
- WorkflowToolCall table now populated when MCP tools are invoked
- Conflict detection is production-ready with real LLM calls (auto-traced)
- Phase 04 (MCP Tool Servers & Observability) is complete -- ready for Phase 05

---
*Phase: 04-mcp-tool-servers-observability*
*Completed: 2026-03-06*

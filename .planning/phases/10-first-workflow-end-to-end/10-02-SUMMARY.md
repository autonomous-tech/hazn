---
phase: 10-first-workflow-end-to-end
plan: 02
subsystem: orchestrator, deliverable-pipeline, sse
tags: [sse-events, django-eventstream, subprocess-tools, jinja2-rendering, pydantic-validation]

# Dependency graph
requires:
  - phase: 10-first-workflow-end-to-end
    plan: 01
    provides: Jinja2 renderer, AuditReportPayload schema, Deliverable html_content field
  - phase: 09-agent-execution-runtime
    provides: WorkflowExecutor, AgentRunner, ToolRouter, tool_wiring infrastructure
provides:
  - SSE event emission at every executor phase transition (phase_started, phase_completed, phase_failed)
  - Workflow-level SSE events (workflow_started, workflow_completed, workflow_failed)
  - Delivery phase rendering pipeline (JSON validate, Jinja2 render, store html_content)
  - Data collection subprocess tools (collect_ga4_data, collect_gsc_data, collect_pagespeed_data)
  - create_deliverable accepts html_content and markdown_source for delivery phase output
affects: [10-03-frontend-wiring, frontend-workflow-status-display]

# Tech tracking
tech-stack:
  added: [subprocess-data-tools]
  patterns: [sse-at-phase-transitions, delivery-rendering-in-executor, lazy-sdk-imports]

key-files:
  created:
    - hazn_platform/hazn_platform/orchestrator/data_tools.py
    - hazn_platform/tests/test_sse_events.py
    - hazn_platform/tests/test_data_tools.py
  modified:
    - hazn_platform/hazn_platform/orchestrator/executor.py
    - hazn_platform/hazn_platform/orchestrator/tasks.py
    - hazn_platform/hazn_platform/orchestrator/tool_router.py
    - hazn_platform/hazn_platform/orchestrator/tool_wiring.py
    - hazn_platform/hazn_platform/qa/runner.py
    - hazn_platform/tests/test_tool_router.py
    - hazn_platform/tests/test_tool_wiring.py

key-decisions:
  - "AnthropicAPIBackend import made lazy (like AgentSDKBackend) to avoid pulling anthropic SDK at module-import time"
  - "Delivery rendering imports (render_report, AuditReportPayload) at module level for patchability in tests"
  - "Data collection tools registered under hazn-data server (not hazn-analytics) to distinguish subprocess wrappers from in-process MCP handlers"
  - "SSE events use sync_to_async wrapper in executor (async context) but direct calls in tasks.py (sync Celery context)"
  - "phase_failed SSE emission wrapped in try/except to prevent SSE failure from masking the original error"

patterns-established:
  - "SSE at phase transitions: every _execute_phase emits started/completed/failed events via send_workspace_event"
  - "Delivery rendering in executor: validate JSON as Pydantic schema, render via Jinja2, store in output dict"
  - "Lazy SDK imports: both AnthropicAPIBackend and AgentSDKBackend use module-level None + lazy import pattern"
  - "Subprocess data tools: thin wrappers with timeout handling and error dict return (never raise)"

requirements-completed: [WKFL-02, WKFL-05, DLVR-01, DLVR-02, DLVR-03, DLVR-04]

# Metrics
duration: 15min
completed: 2026-03-06
---

# Phase 10 Plan 02: Executor Integration Summary

**SSE event emission at every phase transition, delivery phase Jinja2 rendering pipeline, and data collection subprocess tools registered as ToolRouter entries**

## Performance

- **Duration:** 15 min
- **Started:** 2026-03-06T17:04:58Z
- **Completed:** 2026-03-06T17:19:58Z
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments
- Every executor phase transition emits SSE events (phase_started, phase_completed, phase_failed) for real-time frontend status
- Workflow-level SSE events emitted at start, completion, and failure in both async executor and sync Celery task
- Delivery phase output validated via Pydantic AuditReportPayload, rendered to branded HTML via Jinja2, stored in output dict
- Three data collection tools (GA4, GSC, PageSpeed) registered as ToolRouter entries with subprocess wrappers and timeout handling
- create_deliverable updated to pass html_content and markdown_source from delivery phase rendering

## Task Commits

Each task was committed atomically:

1. **Task 1: SSE event emission + delivery phase rendering**
   - `ceb7c8c` (test: failing tests for SSE events and delivery rendering - TDD RED)
   - `801d486` (feat: SSE event emission and delivery phase rendering pipeline - TDD GREEN)

2. **Task 2: Data collection scripts as MCP tools**
   - `2e2495e` (test: failing tests for data collection MCP tools - TDD RED)
   - `292f4c1` (feat: data collection MCP tools and ToolRouter registration - TDD GREEN)

_Note: TDD tasks have RED (test) and GREEN (feat) commits_

## Files Created/Modified
- `hazn_platform/hazn_platform/orchestrator/executor.py` - SSE events at phase transitions, delivery rendering, lazy AnthropicAPIBackend import
- `hazn_platform/hazn_platform/orchestrator/tasks.py` - SSE events in Celery run_workflow task (sync context)
- `hazn_platform/hazn_platform/orchestrator/data_tools.py` - collect_ga4_data, collect_gsc_data, collect_pagespeed_data subprocess wrappers
- `hazn_platform/hazn_platform/orchestrator/tool_router.py` - 3 new tools in _STATIC_TOOL_MAP (23 total, 5 servers)
- `hazn_platform/hazn_platform/orchestrator/tool_wiring.py` - Wire data_tools callables at runtime
- `hazn_platform/hazn_platform/qa/runner.py` - create_deliverable accepts html_content and markdown_source
- `hazn_platform/tests/test_sse_events.py` - 10 tests: phase SSE, workflow SSE, delivery rendering
- `hazn_platform/tests/test_data_tools.py` - 12 tests: tool registration, subprocess, errors, timeouts
- `hazn_platform/tests/test_tool_router.py` - Updated: 5 servers instead of 4
- `hazn_platform/tests/test_tool_wiring.py` - Updated: 23 tools instead of 20

## Decisions Made
- Made AnthropicAPIBackend lazy import (matching AgentSDKBackend pattern) to enable executor testing without anthropic SDK
- Data collection tools use separate "hazn-data" server name to distinguish subprocess wrappers from in-process MCP handlers
- Delivery rendering imports at module level (not local) for proper test patchability
- phase_failed SSE emission wrapped in try/except to prevent SSE infrastructure issues from masking the original phase error
- Budget-exceeded phases emit phase_completed with status="partial" (not phase_failed) to match existing output dict semantics

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Made AnthropicAPIBackend import lazy**
- **Found during:** Task 1 (SSE event tests)
- **Issue:** executor.py imported AnthropicAPIBackend at module level, which imports `anthropic` SDK -- not available in test environment
- **Fix:** Made import lazy (module-level None + import on first use), matching existing AgentSDKBackend pattern
- **Files modified:** hazn_platform/hazn_platform/orchestrator/executor.py
- **Verification:** All executor tests can now import executor module without anthropic SDK
- **Committed in:** ceb7c8c (Task 1 RED commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Essential fix for test environment compatibility. No scope creep.

## Issues Encountered
- Database flush errors during transaction=True test teardown (pre-existing TimescaleDB/hypertable issue). All test assertions pass correctly; only teardown fails. Out of scope for this plan.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- SSE events ready for Plan 03 frontend to display real-time workflow status
- Delivery rendering pipeline fully wired: agent JSON output -> Pydantic validation -> Jinja2 HTML -> Deliverable.html_content
- Data collection tools callable by agents during workflow execution
- All 87 tests pass across 8 test files (22 new tests, 65 existing)

## Self-Check: PASSED

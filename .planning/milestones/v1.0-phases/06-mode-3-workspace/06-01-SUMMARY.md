---
phase: 06-mode-3-workspace
plan: 01
subsystem: ui, api
tags: [typescript, react, django, drf, sse, chat, hitl-removal]

# Dependency graph
requires:
  - phase: 04-executor-rewrite
    provides: "WorkflowRun model without BLOCKED status, executor with phase outputs"
  - phase: 05-memory-rewiring
    provides: "HaznMemory with one-agent-per-client pattern"
provides:
  - "ChatMessage model with migration for per-run chat threads"
  - "REST API at /runs/{run_pk}/chat/ for listing and creating chat messages"
  - "ChatMessage TypeScript type in api.ts"
  - "SSE chat_message handler in use-sse.ts"
  - "Clean frontend with no HITL/QA dead code"
  - "waiting_for_input status added to WorkflowRunStatus"
  - "chat_messages included in WorkflowRunDetail response"
affects: [06-02-PLAN, chat-ui, workflow-detail, deliverables]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Per-run chat thread via ChatMessage model", "Nested ViewSet URL pattern for chat under runs", "SSE event for real-time chat delivery"]

key-files:
  created:
    - "hazn_platform/hazn_platform/orchestrator/migrations/0004_chatmessage.py"
    - "hazn_platform/tests/test_workspace_chat.py"
  modified:
    - "hazn_platform/frontend/src/types/api.ts"
    - "hazn_platform/frontend/src/hooks/use-sse.ts"
    - "hazn_platform/frontend/src/components/workflow/workflow-chat.tsx"
    - "hazn_platform/hazn_platform/orchestrator/models.py"
    - "hazn_platform/hazn_platform/workspace/views.py"
    - "hazn_platform/hazn_platform/workspace/serializers.py"
    - "hazn_platform/hazn_platform/workspace/urls.py"

key-decisions:
  - "Empty stubs for HITL components instead of deleting files -- avoids cascade import breakage"
  - "ShareLink type moved to local interface in share-dialog.tsx -- ShareLink model deleted in Phase 02"
  - "QA fields removed from Deliverable type and all deliverable components simplified"
  - "DashboardData.pending_approvals removed since HITL is gone"
  - "Sites migration 0003 fixed with connection.vendor check for SQLite compatibility"

patterns-established:
  - "ChatMessage nested URL: /runs/{run_pk}/chat/ via ChatMessageViewSet"
  - "SSE chat_message event invalidates both chat and run detail queries"
  - "ChatMessage.Role enum: user/agent/system for message categorization"

requirements-completed: [DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06, DASH-07, CHAT-01]

# Metrics
duration: 16min
completed: 2026-03-13
---

# Phase 06 Plan 01: Frontend Cleanup + ChatMessage API Summary

**Clean frontend build with HITL/QA dead code removed, ChatMessage model with REST API for per-run chat threads, and SSE real-time chat delivery wiring**

## Performance

- **Duration:** 16 min
- **Started:** 2026-03-13T14:17:08Z
- **Completed:** 2026-03-13T14:33:30Z
- **Tasks:** 2
- **Files modified:** 25

## Accomplishments
- Frontend builds cleanly with zero TypeScript errors after removing all HITL/QA model references
- ChatMessage model created with user/agent/system roles and per-run foreign key
- REST API at /runs/{run_pk}/chat/ supports GET (list) and POST (create) with agency isolation
- SSE chat_message event handler wired in use-sse.ts for real-time message delivery
- ChatMessage TypeScript type added, waiting_for_input status added to WorkflowRunStatus
- 7 chat API tests passing via TDD (RED-GREEN cycle)

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix frontend build -- remove HITL/QA dead code, add ChatMessage type, wire SSE** - `61bd399` (feat)
2. **Task 2 RED: Add failing tests for ChatMessage API** - `c7d7937` (test)
3. **Task 2 GREEN: Implement ChatMessage model, API, serializers** - `55e88dc` (feat)

## Files Created/Modified

### Created
- `hazn_platform/hazn_platform/orchestrator/migrations/0004_chatmessage.py` - ChatMessage model migration
- `hazn_platform/tests/test_workspace_chat.py` - 7 test cases for chat API

### Modified (Frontend)
- `hazn_platform/frontend/src/types/api.ts` - Removed HITL/QA types, added ChatMessage, waiting_for_input
- `hazn_platform/frontend/src/hooks/use-sse.ts` - Replaced hitl_new with chat_message handler
- `hazn_platform/frontend/src/components/workflow/workflow-chat.tsx` - Removed InlineHITLCard, HITL chat types
- `hazn_platform/frontend/src/components/layout/sidebar.tsx` - Removed Approvals nav item
- `hazn_platform/frontend/src/components/layout/header.tsx` - Removed HITL search type
- `hazn_platform/frontend/src/components/dashboard/activity-timeline.tsx` - Removed HITL activity types
- `hazn_platform/frontend/src/components/dashboard/status-cards.tsx` - Removed Pending Approvals card
- `hazn_platform/frontend/src/components/hitl/hitl-item-card.tsx` - Replaced with empty stub
- `hazn_platform/frontend/src/components/hitl/hitl-queue.tsx` - Replaced with empty stub
- `hazn_platform/frontend/src/components/deliverables/deliverable-card.tsx` - Removed QA/approval fields
- `hazn_platform/frontend/src/components/deliverables/qa-report.tsx` - Replaced with empty stub
- `hazn_platform/frontend/src/components/deliverables/share-dialog.tsx` - Local ShareLink interface
- `hazn_platform/frontend/src/components/workflow/workflow-card.tsx` - Fixed paginated response type
- `hazn_platform/frontend/src/app/(workspace)/approvals/page.tsx` - Simple empty state
- `hazn_platform/frontend/src/app/(workspace)/workflows/page.tsx` - Removed blocked, added waiting_for_input
- `hazn_platform/frontend/src/app/(workspace)/workflows/[id]/page.tsx` - Fixed blocked status check
- `hazn_platform/frontend/src/app/(workspace)/deliverables/page.tsx` - Removed approval_status filter
- `hazn_platform/frontend/src/app/(workspace)/deliverables/[id]/page.tsx` - Removed QA/approval UI
- `hazn_platform/frontend/src/app/share/[token]/page.tsx` - Removed QA badge

### Modified (Backend)
- `hazn_platform/hazn_platform/orchestrator/models.py` - Added ChatMessage model
- `hazn_platform/hazn_platform/workspace/views.py` - Added ChatMessageViewSet, fixed BLOCKED status ref
- `hazn_platform/hazn_platform/workspace/serializers.py` - Added chat serializers, chat_messages to detail
- `hazn_platform/hazn_platform/workspace/urls.py` - Added /runs/{run_pk}/chat/ route

## Decisions Made
- Used empty function stubs instead of deleting HITL component files to prevent import breakage across the app
- Removed QA fields from Deliverable type (not just HITL) since QA system was removed in v3.0
- Fixed sites migration 0003 to conditionally run PostgreSQL sequence commands (connection.vendor check)
- Moved ShareLink interface from shared types to local definition in share-dialog.tsx
- SSE event emission wrapped in try/except to keep chat creation non-fatal if SSE fails

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed deliverable components referencing removed QA types**
- **Found during:** Task 1 (frontend cleanup)
- **Issue:** deliverable-card.tsx, qa-report.tsx, deliverables/page.tsx, deliverables/[id]/page.tsx all referenced QAVerdict, ApprovalStatus which were removed from api.ts
- **Fix:** Simplified deliverable-card.tsx to remove QA badges, replaced qa-report.tsx with empty stub, removed approval_status filter from deliverables page, simplified detail page
- **Files modified:** 4 deliverable-related files
- **Committed in:** 61bd399 (Task 1 commit)

**2. [Rule 3 - Blocking] Fixed workflow-card.tsx paginated response type error**
- **Found during:** Task 1 (frontend build verification)
- **Issue:** TypeScript narrowing error: `api.get<EndClient[]>` with `.results` access creates `never` type
- **Fix:** Changed type to union `EndClient[] | PaginatedResponse<EndClient>` to allow both response shapes
- **Files modified:** workflow-card.tsx
- **Committed in:** 61bd399 (Task 1 commit)

**3. [Rule 3 - Blocking] Fixed sites migration 0003 PostgreSQL-only SQL on SQLite**
- **Found during:** Task 2 (running tests)
- **Issue:** Migration uses `SELECT last_value from django_site_id_seq` which is PostgreSQL-specific
- **Fix:** Added `connection.vendor == "postgresql"` guard around sequence operations
- **Files modified:** hazn_platform/contrib/sites/migrations/0003_set_site_domain_and_name.py
- **Committed in:** 55e88dc (Task 2 commit)

**4. [Rule 1 - Bug] Fixed DashboardView referencing BLOCKED status**
- **Found during:** Task 2 (reviewing views.py)
- **Issue:** DashboardView.get() filters by `WorkflowRun.Status.BLOCKED` which was removed in Phase 4
- **Fix:** Changed to filter by `WorkflowRun.Status.RUNNING` only
- **Files modified:** workspace/views.py
- **Committed in:** 55e88dc (Task 2 commit)

---

**Total deviations:** 4 auto-fixed (1 bug, 3 blocking)
**Impact on plan:** All auto-fixes necessary for build correctness. No scope creep.

## Issues Encountered
- Pre-existing TypeScript type narrowing issues with API response types that could be either array or paginated -- fixed with union types
- Sites migration incompatible with SQLite testing -- pre-existing issue, fixed with vendor check

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- ChatMessage model and API ready for Plan 06-02 to build interactive chat UI on top of
- SSE chat_message handler wired, ready for real-time message display
- waiting_for_input status available for CHAT-03 input-gating feature
- Frontend clean and building, all DASH pages functional

---
*Phase: 06-mode-3-workspace*
*Plan: 01*
*Completed: 2026-03-13*

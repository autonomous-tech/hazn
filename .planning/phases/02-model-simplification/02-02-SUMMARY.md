---
phase: 02-model-simplification
plan: 02
subsystem: api
tags: [django, drf, permissions, migrations, cleanup]

# Dependency graph
requires:
  - phase: 02-model-simplification plan 01
    provides: Models simplified (HITLItem deleted, enterprise fields removed, Agency singleton, ShareLink deleted)
provides:
  - All API views/serializers/URLs cleaned of HITL/QA/Deliverable references
  - IsAuthenticated replaces IsAgencyMember across all viewsets
  - QA app directory fully deleted and removed from INSTALLED_APPS
  - Dead source files deleted (conflict_detector.py, hitl.py, permissions.py, share_views.py)
  - executor.py dead imports marked with TODO(Phase 4) comments
  - 10 dead test files deleted, 5 remaining test files updated
  - Fresh 0001_initial.py per app reflecting final v3.0 schema
affects: [03-tool-extraction, 04-executor-rewrite, 05-agent-sdk-integration]

# Tech tracking
tech-stack:
  added: []
  patterns: [IsAuthenticated as sole permission class for all workspace viewsets]

key-files:
  created:
    - hazn_platform/hazn_platform/core/migrations/0001_initial.py
    - hazn_platform/hazn_platform/orchestrator/migrations/0001_initial.py
    - hazn_platform/hazn_platform/users/migrations/0001_initial.py
    - hazn_platform/hazn_platform/marketing/migrations/0001_initial.py
    - hazn_platform/hazn_platform/content/migrations/0001_initial.py
  modified:
    - hazn_platform/hazn_platform/workspace/views.py
    - hazn_platform/hazn_platform/workspace/serializers.py
    - hazn_platform/hazn_platform/workspace/urls.py
    - hazn_platform/hazn_platform/workspace/filters.py
    - hazn_platform/hazn_platform/orchestrator/executor.py
    - hazn_platform/hazn_platform/orchestrator/tasks.py
    - hazn_platform/hazn_platform/orchestrator/api/views.py
    - hazn_platform/hazn_platform/orchestrator/api/urls.py
    - hazn_platform/hazn_platform/orchestrator/api/serializers.py
    - hazn_platform/config/settings/base.py
    - hazn_platform/config/urls.py

key-decisions:
  - "test_workflow_catalog.py cleaned inline (Rule 3) -- imported Deliverable and DeliverableSerializer which no longer exist"
  - "Pre-existing broken tests (test_executor, test_metering, test_memory) logged as deferred items, not fixed (scope boundary)"
  - "Sites contrib migrations restored after accidental deletion by find command"

patterns-established:
  - "IsAuthenticated as sole permission class: all workspace viewsets use rest_framework.permissions.IsAuthenticated"
  - "Fresh migration squash: delete all migration files, regenerate with makemigrations for clean v3.0 schema"

requirements-completed: [STRP-02, STRP-03, STRP-07, STRP-10]

# Metrics
duration: 13min
completed: 2026-03-12
---

# Phase 2 Plan 2: API Cleanup and Migration Squash Summary

**Removed all HITL/QA/Deliverable/conflict references from API layer, deleted QA app and 14 dead source+test files, replaced IsAgencyMember with IsAuthenticated, and squashed all migrations to fresh 0001_initial per app for clean v3.0 schema**

## Performance

- **Duration:** 13 min
- **Started:** 2026-03-12T14:59:47Z
- **Completed:** 2026-03-12T15:12:49Z
- **Tasks:** 2
- **Files modified:** 57 (41 in Task 1 + 16 in Task 2)

## Accomplishments
- All API layer cleaned: views, serializers, URLs, filters, admin, tasks across workspace and orchestrator apps
- IsAuthenticated replaces IsAgencyMember in all 7 remaining workspace viewsets
- DashboardView simplified (removed pending_approvals and ready_deliverables counts)
- QA app directory fully deleted (models, runner, criteria, staging, admin, migrations)
- 4 dead source files deleted (conflict_detector.py, hitl.py, permissions.py, share_views.py)
- 10 dead test files deleted, 6 remaining test files updated (includes test_workflow_catalog.py auto-fix)
- executor.py dead imports commented with 3 TODO(Phase 4) markers
- check_hitl_timeouts and deliver_webhook Celery tasks removed
- All migrations squashed to fresh 0001_initial.py per app (5 apps)
- makemigrations --check exits cleanly, Django system check passes

## Task Commits

Each task was committed atomically:

1. **Task 1: Clean up API layer, delete dead source files and QA app** - `0f672dc` (feat)
2. **Task 2: Squash migrations to fresh 0001_initial per app** - `2778792` (chore)

## Files Created/Modified

### Created (migrations)
- `hazn_platform/hazn_platform/core/migrations/0001_initial.py` - Fresh Agency, EndClient, MemoryCorrection, VaultCredential
- `hazn_platform/hazn_platform/orchestrator/migrations/0001_initial.py` - Fresh WorkflowRun, WorkflowPhaseOutput (with html_content/markdown_source), WorkflowAgent, WorkflowToolCall
- `hazn_platform/hazn_platform/users/migrations/0001_initial.py` - Fresh User (no agency_role)
- `hazn_platform/hazn_platform/marketing/migrations/0001_initial.py` - Fresh Audit, Campaign, Decision, Keyword
- `hazn_platform/hazn_platform/content/migrations/0001_initial.py` - Fresh ApprovedCopy, BrandVoice

### Modified (API layer)
- `hazn_platform/hazn_platform/workspace/views.py` - Removed 3 viewset classes, replaced IsAgencyMember with IsAuthenticated
- `hazn_platform/hazn_platform/workspace/serializers.py` - Removed HITLItem/Deliverable/ShareLink serializers, removed turn_count/hitl_items fields
- `hazn_platform/hazn_platform/workspace/urls.py` - Removed hitl/deliverable router registrations and HTML view URL
- `hazn_platform/hazn_platform/workspace/filters.py` - Removed HITLItemFilter and DeliverableFilter
- `hazn_platform/hazn_platform/orchestrator/executor.py` - Dead imports commented with TODO(Phase 4)
- `hazn_platform/hazn_platform/orchestrator/tasks.py` - Removed check_hitl_timeouts, deliver_webhook, process_expired_items
- `hazn_platform/hazn_platform/orchestrator/api/views.py` - Removed HITLItemViewSet
- `hazn_platform/hazn_platform/orchestrator/api/urls.py` - Removed hitl router registration
- `hazn_platform/hazn_platform/orchestrator/api/serializers.py` - Removed HITLItemSerializer, turn_count, hitl_items
- `hazn_platform/config/settings/base.py` - Removed hazn_platform.qa from LOCAL_APPS
- `hazn_platform/config/urls.py` - Removed share view TODO comments

### Deleted (source files)
- `hazn_platform/hazn_platform/orchestrator/conflict_detector.py`
- `hazn_platform/hazn_platform/orchestrator/hitl.py`
- `hazn_platform/hazn_platform/workspace/permissions.py`
- `hazn_platform/hazn_platform/workspace/share_views.py`
- `hazn_platform/hazn_platform/qa/` (entire directory: __init__, admin, apps, criteria, models, runner, staging, migrations)

### Deleted (test files)
- `tests/test_conflict_detector.py`, `tests/test_hitl.py`, `tests/test_hitl_api.py`
- `tests/test_qa_models.py`, `tests/test_qa_runner.py`, `tests/test_qa_approval.py`
- `tests/test_qa_criteria.py`, `tests/test_qa_staging.py`
- `tests/test_workspace_hitl.py`, `tests/test_workspace_deliverables.py`

### Updated (test files)
- `tests/test_orchestrator_models.py` - Removed HITLItem tests, added WorkflowPhaseOutput html_content/markdown_source tests
- `tests/test_models.py` - Removed tool_preferences assertion, added Agency singleton test
- `tests/test_workspace_clients.py` - Removed agency_role from user fixtures
- `tests/test_workspace_dashboard.py` - Removed pending_approvals/ready_deliverables assertions
- `tests/test_workspace_workflows.py` - Removed agency_role from user fixtures
- `tests/test_workflow_catalog.py` - Removed Deliverable/DeliverableSerializer/DeliverableHTMLView tests (auto-fix)

## Decisions Made
- **test_workflow_catalog.py cleaned inline**: This test file imported qa.models.Deliverable (now deleted) and tested DeliverableSerializer/DeliverableHTMLView (both removed). Cleaning it was a Rule 3 blocking fix since the imports would fail on module load.
- **Pre-existing test failures deferred**: test_executor.py, test_metering.py, test_memory.py have references to models/fields deleted in Plan 01 (not this task). Logged to deferred-items.md per scope boundary rules.
- **Sites contrib migrations restored**: The `find` command to delete migration files accidentally caught `hazn_platform/contrib/sites/migrations/`. These are third-party (django.contrib.sites) migrations stored locally via `MIGRATION_MODULES` setting and must be preserved.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Cleaned test_workflow_catalog.py of deleted Deliverable/QA references**
- **Found during:** Task 1 (verification grep found imports of deleted qa.models.Deliverable)
- **Issue:** test_workflow_catalog.py imported `from hazn_platform.qa.models import Deliverable` and tested `DeliverableSerializer` and `DeliverableHTMLView`, all of which were deleted in this task
- **Fix:** Removed TestDeliverableSerializer and TestDeliverableHTMLView test classes, removed Deliverable import and fixtures, removed agency_role from user fixture
- **Files modified:** hazn_platform/tests/test_workflow_catalog.py
- **Verification:** File imports cleanly, no references to deleted models
- **Committed in:** 0f672dc (Task 1 commit)

**2. [Rule 3 - Blocking] Restored sites contrib migrations after accidental deletion**
- **Found during:** Task 2 (makemigrations failed with NodeNotFoundError for socialaccount.0001_initial)
- **Issue:** The `find` command to delete migration files also deleted `hazn_platform/contrib/sites/migrations/` which contains third-party migration files required by django.contrib.sites via MIGRATION_MODULES setting
- **Fix:** Restored sites migrations from previous commit using `git checkout HEAD~1`
- **Files modified:** hazn_platform/hazn_platform/contrib/sites/migrations/ (4 files restored)
- **Verification:** makemigrations --check passes cleanly
- **Committed in:** 2778792 (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 3 blocking)
**Impact on plan:** Both fixes necessary to unblock task completion. No scope creep.

## Issues Encountered
- Sites contrib migrations accidentally deleted by the broad `find` command -- resolved by restoring from git
- Pre-existing test failures in test_executor.py, test_metering.py, test_memory.py logged as deferred items (out of scope)

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 2 model simplification is fully complete
- All Django models reflect the final v3.0 schema with clean initial migrations
- No dangling imports of deleted models/modules in source code
- API layer is clean and ready for Phase 3 tool extraction
- executor.py has clear TODO(Phase 4) markers for the full rewrite
- Pre-existing test failures (from Plan 01 field removals) need cleanup before or during Phase 4

## Self-Check: PASSED

All 5 migration files verified on disk. Both task commits (0f672dc, 2778792) verified in git log. SUMMARY.md exists.

---
*Phase: 02-model-simplification*
*Completed: 2026-03-12*

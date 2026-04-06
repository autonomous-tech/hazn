---
phase: 02-model-simplification
plan: 01
subsystem: database
tags: [django, orm, migrations, models, singleton]

# Dependency graph
requires:
  - phase: 01-strip-infrastructure
    provides: Cleaned executor/metering/session code with dead enterprise imports removed
provides:
  - HITLItem model fully deleted from orchestrator app
  - WorkflowPhaseOutput with html_content and markdown_source fields (deliverable rendering)
  - Agency singleton with save() override and load() classmethod
  - Enterprise fields removed from WorkflowRun, WorkflowAgent, Agency, EndClient, User
  - ShareLink model deleted from workspace app
  - Coordinated Django migrations for all 4 affected apps
affects: [02-model-simplification plan 02, api-cleanup, executor-rewrite, dashboard]

# Tech tracking
tech-stack:
  added: []
  patterns: [Agency singleton via save() override with existence check, Agency.load() classmethod for get_or_create access]

key-files:
  created:
    - hazn_platform/hazn_platform/core/migrations/0004_remove_agency_churned_at_and_more.py
    - hazn_platform/hazn_platform/orchestrator/migrations/0005_remove_workflowagent_turn_count_and_more.py
    - hazn_platform/hazn_platform/users/migrations/0003_remove_user_agency_role.py
    - hazn_platform/hazn_platform/workspace/migrations/0002_delete_sharelink.py
  modified:
    - hazn_platform/hazn_platform/orchestrator/models.py
    - hazn_platform/hazn_platform/core/models.py
    - hazn_platform/hazn_platform/users/models.py
    - hazn_platform/hazn_platform/workspace/share_models.py
    - hazn_platform/hazn_platform/orchestrator/admin.py
    - hazn_platform/config/urls.py

key-decisions:
  - "Agency singleton enforced via save() override (not CheckConstraint) -- UUID PKs prevent pk=1 constraint"
  - "ShareLink deleted entirely (not re-pointed to PhaseOutput) -- QA-era feature not needed in v3.0"
  - "Admin HITLItem registration removed inline (Rule 3) -- blocked Django startup after model deletion"
  - "Share URL and import commented out in config/urls.py (Rule 3) -- blocked makemigrations"

patterns-established:
  - "Agency singleton: save() rejects second instance, load() creates-or-gets singleton"

requirements-completed: [STRP-02, STRP-03, STRP-07, STRP-10]

# Metrics
duration: 7min
completed: 2026-03-12
---

# Phase 2 Plan 1: Model Simplification Summary

**Deleted HITLItem model, added deliverable rendering fields to WorkflowPhaseOutput, removed enterprise fields from 5 models, enforced Agency singleton, and generated coordinated Django migrations across 4 apps**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-12T14:48:31Z
- **Completed:** 2026-03-12T14:55:38Z
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments
- HITLItem model class and all its enums fully removed from orchestrator/models.py
- WorkflowPhaseOutput now has html_content and markdown_source TextFields (migrated from qa.Deliverable concept)
- Enterprise fields removed: turn_count (WorkflowRun, WorkflowAgent), tool_preferences/churned_at/deletion_notified_at (Agency), deletion_requested_at/deletion_scheduled_at (EndClient), AgencyRole/agency_role (User)
- Agency singleton enforcement via save() override and load() classmethod
- ShareLink model deleted entirely (QA-era feature)
- 4 coordinated Django migrations generated with clean FK dependency ordering

## Task Commits

Each task was committed atomically:

1. **Task 1: Modify all model files** - `b00fb04` (feat)
2. **Task 2: Handle ShareLink FK, generate migrations** - `e90c1d5` (feat)

## Files Created/Modified
- `hazn_platform/hazn_platform/orchestrator/models.py` - Deleted HITLItem, added html_content/markdown_source to PhaseOutput, removed turn_count fields
- `hazn_platform/hazn_platform/core/models.py` - Removed tool_preferences/churned_at/deletion_notified_at from Agency, deletion fields from EndClient, added singleton save()/load()
- `hazn_platform/hazn_platform/users/models.py` - Removed AgencyRole enum and agency_role field
- `hazn_platform/hazn_platform/workspace/share_models.py` - Deleted ShareLink model (placeholder docstring remains)
- `hazn_platform/hazn_platform/orchestrator/admin.py` - Removed HITLItemAdmin and import (Rule 3 auto-fix)
- `hazn_platform/config/urls.py` - Commented out share URL and import (Rule 3 auto-fix)
- `hazn_platform/hazn_platform/core/migrations/0004_*.py` - Remove Agency/EndClient lifecycle fields
- `hazn_platform/hazn_platform/orchestrator/migrations/0005_*.py` - Remove turn_count, add PhaseOutput fields, delete HITLItem
- `hazn_platform/hazn_platform/users/migrations/0003_*.py` - Remove agency_role
- `hazn_platform/hazn_platform/workspace/migrations/0002_*.py` - Delete ShareLink

## Decisions Made
- **Agency singleton via save() override** (not CheckConstraint): Agency uses UUIDField as PK, making `Q(pk=1)` CheckConstraint impossible. The save() override with `Agency.objects.exists()` check is the correct approach for UUID-based singletons.
- **ShareLink deleted entirely** (not re-pointed to PhaseOutput): Per research recommendation, ShareLink is a QA-era feature. Cleaner to delete now than maintain dead FK. Can be re-created in v3.0 if needed.
- **Kept WorkflowRun.Status.BLOCKED**: Per Pitfall 4 in research, BLOCKED is kept in the enum even though nothing sets it after HITL removal. Phase 4 executor rewrite will define final status choices.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Removed HITLItem import and admin registration from orchestrator/admin.py**
- **Found during:** Task 1 (model file modifications)
- **Issue:** After deleting HITLItem model, `admin.py` imported it at module level and registered HITLItemAdmin. Django's admin autodiscovery loads this during `django.setup()`, causing ImportError and blocking all subsequent verification.
- **Fix:** Removed the HITLItem import and HITLItemAdmin class from orchestrator/admin.py
- **Files modified:** hazn_platform/hazn_platform/orchestrator/admin.py
- **Verification:** `django.setup()` succeeds, all model import checks pass
- **Committed in:** b00fb04 (Task 1 commit)

**2. [Rule 3 - Blocking] Commented out share URL and PublicShareView import in config/urls.py**
- **Found during:** Task 2 (ShareLink deletion)
- **Issue:** After deleting ShareLink model, `config/urls.py` imported `PublicShareView` from `share_views.py`, which imported `ShareLink` from `share_models.py`. Django's URL check system loads this during `manage.py makemigrations`, causing ImportError.
- **Fix:** Commented out the import and URL pattern with TODO markers pointing to Plan 02-02
- **Files modified:** hazn_platform/config/urls.py
- **Verification:** `manage.py makemigrations` succeeds and generates all expected migrations
- **Committed in:** e90c1d5 (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 3 blocking imports)
**Impact on plan:** Both fixes were necessary to unblock Django startup and migration generation. Both are within scope of the model changes (removing references to deleted models). No scope creep -- the actual view/URL cleanup is properly deferred to Plan 02-02.

## Issues Encountered
- DATABASE_URL environment variable required for Django startup -- resolved by using `DATABASE_URL=sqlite:///test.db` with test settings
- USE_DOCKER environment variable required by local settings -- resolved by using `config.settings.test` instead of `config.settings.local`

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Model layer is now simplified and correct for v3.0
- Django migrations generated and ready (will be squashed in Plan 02-02)
- Plan 02-02 can proceed with API cleanup: views, serializers, URLs, filters, permissions, QA app deletion, executor TODO comments, and migration squashing
- Remaining dangling imports (workspace/views.py, workspace/serializers.py, workspace/filters.py, orchestrator/api/*, qa app) are expected and will be cleaned up in Plan 02-02

## Self-Check: PASSED

All 10 created/modified files verified on disk. Both task commits (b00fb04, e90c1d5) verified in git log.

---
*Phase: 02-model-simplification*
*Completed: 2026-03-12*

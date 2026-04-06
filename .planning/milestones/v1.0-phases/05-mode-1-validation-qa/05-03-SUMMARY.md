---
phase: 05-mode-1-validation-qa
plan: 03
subsystem: database, api, compliance
tags: [gdpr, data-lifecycle, retention, vault, letta, celery, management-commands, django]

# Dependency graph
requires:
  - phase: 01-infrastructure-foundation
    provides: "Vault client helpers (store_secret, read_secret), Agency/EndClient/VaultCredential models"
  - phase: 03-orchestrator-client-model
    provides: "WorkflowRun model with status choices, WorkflowSession, deliver_webhook task"
provides:
  - "Lifecycle fields on Agency (churned_at, deletion_notified_at) and EndClient (deletion_requested_at, deletion_scheduled_at)"
  - "delete_secret() in vault.py for permanent Vault secret deletion"
  - "lifecycle.py enforcement module with query functions and deletion logic"
  - "3 management commands: enforce_retention, process_deletions, notify_deletions"
  - "3 Celery periodic tasks: enforce_data_retention, process_gdpr_deletions, send_deletion_notifications"
affects: [06-mode-2-multi-client, api-endpoints, admin-panel]

# Tech tracking
tech-stack:
  added: []
  patterns: [external-before-postgres-delete, active-workflow-guard, notification-conditional-deletion]

key-files:
  created:
    - hazn_platform/hazn_platform/core/lifecycle.py
    - hazn_platform/hazn_platform/core/management/commands/enforce_retention.py
    - hazn_platform/hazn_platform/core/management/commands/process_deletions.py
    - hazn_platform/hazn_platform/core/management/commands/notify_deletions.py
    - hazn_platform/hazn_platform/core/migrations/0003_agency_lifecycle_endclient_lifecycle.py
    - hazn_platform/tests/test_data_lifecycle.py
  modified:
    - hazn_platform/hazn_platform/core/models.py
    - hazn_platform/hazn_platform/core/vault.py
    - hazn_platform/hazn_platform/orchestrator/tasks.py

key-decisions:
  - "Deletion order: Vault -> Letta -> Postgres CASCADE (external resources first to avoid orphans)"
  - "Active workflow guard: skip deletion if running/blocked WorkflowRuns exist"
  - "Notification conditional on deletion_notified_at being set before retention enforcement"
  - "GDPR deletion confirmation sends both webhook and email after successful deletion"
  - "_purge_letta_memory wrapped in try/except as non-fatal (Letta availability not guaranteed)"

patterns-established:
  - "External-before-Postgres delete: always delete Vault secrets and Letta agents before Postgres CASCADE"
  - "Active workflow guard: check for running/blocked WorkflowRuns before any data deletion"
  - "Management command + Celery task pattern: commands for logic, tasks for scheduling via call_command"
  - "Non-fatal external service errors: Vault and Letta failures logged but don't block deletion flow"

requirements-completed: [DATA-01, DATA-02, DATA-03, DATA-04]

# Metrics
duration: 9min
completed: 2026-03-06
---

# Phase 5 Plan 3: Data Lifecycle Summary

**GDPR-compliant data lifecycle with 90-day retention, 30-day deletion, Vault/Letta cleanup, active workflow guards, and churn+30 notification via webhook+email**

## Performance

- **Duration:** 9 min
- **Started:** 2026-03-06T06:40:57Z
- **Completed:** 2026-03-06T06:50:28Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments
- Lifecycle fields added to Agency and EndClient models with migration
- Full deletion pipeline: Vault secrets -> Letta agents -> Postgres CASCADE (3-layer cleanup)
- Active workflow guard prevents deletion race conditions (running/blocked WorkflowRuns skipped)
- 3 management commands with --dry-run support for safe preview
- 3 Celery periodic tasks for daily automated enforcement
- GDPR deletion confirmation notification (webhook + email) after successful deletion
- Notification conditional on prior deletion_notified_at (prevents accidental deletion without warning)
- 28 comprehensive tests covering all lifecycle scenarios

## Task Commits

Each task was committed atomically:

1. **Task 1: Add lifecycle fields, delete_secret, and lifecycle enforcement module**
   - `ca54236` (test: add failing tests for data lifecycle enforcement)
   - `fb92a51` (feat: add lifecycle fields, delete_secret, and lifecycle enforcement module)

2. **Task 2: Create management commands and Celery periodic tasks**
   - `728673c` (test: add failing tests for management commands and Celery tasks)
   - `fddd1ff` (feat: add management commands and Celery periodic tasks for lifecycle)

_Note: TDD tasks have multiple commits (test -> feat)_

## Files Created/Modified
- `hazn_platform/hazn_platform/core/models.py` - Added churned_at, deletion_notified_at to Agency; deletion_requested_at, deletion_scheduled_at to EndClient
- `hazn_platform/hazn_platform/core/vault.py` - Added delete_secret() for permanent Vault secret deletion (non-fatal on error)
- `hazn_platform/hazn_platform/core/lifecycle.py` - Core lifecycle enforcement: query functions, delete_client_data, delete_agency_data, build_deletion_summary
- `hazn_platform/hazn_platform/core/migrations/0003_agency_lifecycle_endclient_lifecycle.py` - Migration for lifecycle fields
- `hazn_platform/hazn_platform/core/management/commands/enforce_retention.py` - 90-day post-churn retention enforcement with notification guard
- `hazn_platform/hazn_platform/core/management/commands/process_deletions.py` - GDPR 30-day deletion processing with confirmation notification
- `hazn_platform/hazn_platform/core/management/commands/notify_deletions.py` - Churn+30 warning notification via webhook + email with data summary
- `hazn_platform/hazn_platform/orchestrator/tasks.py` - Added 3 Celery periodic tasks for daily lifecycle enforcement
- `hazn_platform/tests/test_data_lifecycle.py` - 28 tests across 11 test classes covering all lifecycle scenarios

## Decisions Made
- Deletion order enforced as Vault -> Letta -> Postgres CASCADE to prevent orphaned external resources (RESEARCH Pitfall 2)
- Active workflow guard checks for running/blocked WorkflowRuns before deletion to prevent race conditions (RESEARCH Pitfall 3)
- _purge_letta_memory is non-fatal: Letta unavailability does not block GDPR-required deletion (RESEARCH Pitfall 5)
- Notification conditional on deletion_notified_at being set: enforce_retention skips agencies not yet notified (RESEARCH Pitfall 6)
- GDPR deletion confirmation sends both webhook and email after successful deletion (DATA-02 user decision)
- Management command + Celery task pattern: commands contain business logic, tasks wrap via call_command for scheduling

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed Celery task test mock path**
- **Found during:** Task 2 (GREEN phase)
- **Issue:** Tests patched `hazn_platform.orchestrator.tasks.call_command` but call_command is imported inside the function, not at module level
- **Fix:** Changed mock path to `django.core.management.call_command`
- **Files modified:** hazn_platform/tests/test_data_lifecycle.py
- **Verification:** All 28 tests pass
- **Committed in:** fddd1ff (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Trivial test mock path fix. No scope creep.

## Issues Encountered
- Pre-existing test failures in test_executor.py (pytest-asyncio mark) and test_orchestrator_models.py (trigger_type_choices mismatch from prior phase) -- not related to this plan's changes, documented as out-of-scope

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Data lifecycle enforcement is fully implemented and tested
- Management commands can be registered with django-celery-beat for periodic scheduling
- Migration 0003 needs to be applied to the database (`python manage.py migrate`)
- Ready for integration with admin panel or API endpoints for triggering churn/GDPR requests

## Self-Check: PASSED

All 9 created/modified files verified present. All 4 task commits (ca54236, fb92a51, 728673c, fddd1ff) verified in git log.

---
*Phase: 05-mode-1-validation-qa*
*Completed: 2026-03-06*

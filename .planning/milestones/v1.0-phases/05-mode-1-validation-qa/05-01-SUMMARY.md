---
phase: 05-mode-1-validation-qa
plan: 01
subsystem: qa
tags: [pydantic, django-orm, hitl, qa-criteria, deliverable, approval-gate]

# Dependency graph
requires:
  - phase: 03-orchestrator-client-model
    provides: WorkflowRun, WorkflowPhaseOutput, HITLItem models and HITL queue management
provides:
  - QA criteria registry with Pydantic schemas for 6 task types
  - Deliverable model with QA verdict, approval status, preview URL tracking
  - QA runner with phase detection, task type mapping, deliverable creation
  - HITL deliverable_approval trigger type with 48h auto-approve timeout
  - Agency-level QA criteria overrides via tool_preferences
affects: [05-mode-1-validation-qa, executor-integration, mode-3-external]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "QA criteria registry as Pydantic models with TaskType enum keys"
    - "Agency override merging: base criteria + tool_preferences.qa_criteria_overrides"
    - "QA verdict threshold pattern: PASS >= 90, CONDITIONAL_PASS >= 75, FAIL < 75"
    - "v1 QA stub with _compute_qa_score hook for future Letta agent integration"

key-files:
  created:
    - hazn_platform/hazn_platform/qa/__init__.py
    - hazn_platform/hazn_platform/qa/apps.py
    - hazn_platform/hazn_platform/qa/criteria.py
    - hazn_platform/hazn_platform/qa/models.py
    - hazn_platform/hazn_platform/qa/runner.py
    - hazn_platform/hazn_platform/qa/admin.py
    - hazn_platform/hazn_platform/qa/migrations/0001_initial.py
    - hazn_platform/tests/test_qa_criteria.py
    - hazn_platform/tests/test_qa_models.py
    - hazn_platform/tests/test_qa_runner.py
  modified:
    - hazn_platform/config/settings/base.py
    - hazn_platform/hazn_platform/orchestrator/hitl.py
    - hazn_platform/hazn_platform/orchestrator/models.py
    - hazn_platform/hazn_platform/orchestrator/migrations/0003_alter_hitlitem_trigger_type.py

key-decisions:
  - "v1 QA scoring is a stub (_compute_qa_score returns 95); real Letta agent integration deferred per CONTEXT.md"
  - "HITLItem.TriggerType extended with DELIVERABLE_APPROVAL choice to satisfy DB constraint"
  - "HITLItem trigger_type max_length increased from 20 to 30 to accommodate deliverable_approval"
  - "submit_for_approval includes full QA report for all verdict types (PASS, CONDITIONAL_PASS, FAIL)"

patterns-established:
  - "QA criteria override pattern: agency tool_preferences.qa_criteria_overrides -> get_effective_criteria merges weights, adds custom criteria, changes thresholds"
  - "Verdict flow pattern: run_qa_check -> submit_for_approval (PASS/CONDITIONAL/FAIL) or create crash HITL (PENDING)"

requirements-completed: [QA-01, QA-02, QA-04]

# Metrics
duration: 16min
completed: 2026-03-06
---

# Phase 5 Plan 1: QA Criteria Registry and Runner Summary

**QA app with 6-type criteria registry (Pydantic), Deliverable model with verdict/approval tracking, and QA runner with HITL deliverable_approval integration (48h auto-approve)**

## Performance

- **Duration:** 16 min
- **Started:** 2026-03-06T06:41:29Z
- **Completed:** 2026-03-06T06:57:46Z
- **Tasks:** 2
- **Files modified:** 14

## Accomplishments
- QA criteria registry covers all 6 task types (analytics, landing_page, full_site, blog, email, bug_fix) with weighted criteria summing to 1.0 each
- Deliverable model tracks QA verdicts (pending/pass/conditional_pass/fail), approval status (5 states), preview URLs, and links to HITL items
- QA runner detects deliverable-producing phases, maps to task types via heuristics, and orchestrates the full QA-to-approval flow
- HITL deliverable_approval trigger type with 48h configurable timeout and auto_approve default action
- Agency QA criteria overrides work via tool_preferences.qa_criteria_overrides (override weights, add criteria, change thresholds)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create QA criteria registry and Deliverable model** - `728673c` (feat) -- committed in prior execution; all artifacts verified passing (18 tests)
2. **Task 2: Create QA runner and HITL deliverable_approval integration** - `a3bf996` (feat)

_Note: Task 1 artifacts were already committed as part of 05-03 plan execution. Tests verified passing; no duplicate commit needed._

## Files Created/Modified
- `hazn_platform/hazn_platform/qa/criteria.py` - QA criteria registry with TaskType enum, QACriterion/QACriteria Pydantic models, get_criteria, get_effective_criteria
- `hazn_platform/hazn_platform/qa/models.py` - Deliverable model with QAVerdict and ApprovalStatus choices, FK relationships
- `hazn_platform/hazn_platform/qa/runner.py` - should_run_qa, get_task_type_for_phase, create_deliverable, run_qa_check, submit_for_approval, handle_qa_result
- `hazn_platform/hazn_platform/qa/admin.py` - DeliverableAdmin with list_display and list_filter
- `hazn_platform/hazn_platform/qa/apps.py` - QaConfig Django app config
- `hazn_platform/hazn_platform/qa/migrations/0001_initial.py` - Deliverable table creation
- `hazn_platform/hazn_platform/orchestrator/hitl.py` - Added deliverable_approval to DEFAULT_TIMEOUT_ACTIONS
- `hazn_platform/hazn_platform/orchestrator/models.py` - Added DELIVERABLE_APPROVAL to TriggerType choices, widened max_length
- `hazn_platform/hazn_platform/orchestrator/migrations/0003_alter_hitlitem_trigger_type.py` - Schema migration for trigger_type field
- `hazn_platform/config/settings/base.py` - Added hazn_platform.qa to INSTALLED_APPS
- `hazn_platform/tests/test_qa_criteria.py` - 11 tests for criteria registry, get_criteria, get_effective_criteria
- `hazn_platform/tests/test_qa_models.py` - 7 tests for Deliverable model creation, choices, FK behavior
- `hazn_platform/tests/test_qa_runner.py` - 27 tests for runner functions, verdict flow, HITL integration

## Decisions Made
- v1 QA scoring uses a stub (`_compute_qa_score` returns 95 by default) with a clean hook for future Letta agent integration. Real LLM-based QA deferred per CONTEXT.md Claude's Discretion.
- HITLItem.TriggerType extended with `DELIVERABLE_APPROVAL` to satisfy the Django model choices constraint. This required a migration.
- trigger_type max_length increased from 20 to 30 since "deliverable_approval" is 22 characters.
- `submit_for_approval` includes the full QA report in HITL details for all verdict types (not just FAIL) for complete agency visibility.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Extended HITLItem.TriggerType choices and max_length**
- **Found during:** Task 1 (Deliverable model creation)
- **Issue:** HITLItem.trigger_type field has `choices=TriggerType.choices` and `max_length=20`. Creating HITL items with trigger_type="deliverable_approval" (22 chars) would violate both the choices constraint and the max_length constraint.
- **Fix:** Added `DELIVERABLE_APPROVAL = "deliverable_approval"` to TriggerType choices and increased max_length from 20 to 30. Created migration 0003.
- **Files modified:** hazn_platform/orchestrator/models.py, hazn_platform/orchestrator/migrations/0003_alter_hitlitem_trigger_type.py
- **Verification:** All existing HITL tests pass (19/19), new deliverable_approval tests pass
- **Committed in:** 728673c (prior execution, part of Task 1)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Essential fix for HITL integration. Without it, deliverable_approval HITL items would fail to save. No scope creep.

## Issues Encountered
- Task 1 artifacts were already committed in a prior execution session (as part of 05-03 plan which needed QA models as prerequisites). Verified all tests pass and no duplicate commit needed.
- Pre-existing test failures in test_executor.py (missing pytest-asyncio) and test_vault.py (requires running Vault service) are unrelated to this plan's changes.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- QA infrastructure ready for executor integration (injecting QA phases after deliverable-producing phases)
- Deliverable model ready for Vercel preview URL storage (QA-04 wiring)
- HITL deliverable_approval ready for approval flow processing
- QA criteria ready for agency customization via tool_preferences

## Self-Check: PASSED

All 11 created files verified present on disk. Commit a3bf996 verified in git log. 45 QA tests passing (18 criteria + 7 models + 27 runner). No missing items.

---
*Phase: 05-mode-1-validation-qa*
*Completed: 2026-03-06*

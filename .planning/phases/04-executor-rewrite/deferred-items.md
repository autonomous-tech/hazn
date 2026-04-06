# Deferred Items -- Phase 04

## Pre-existing Bug: metering.py turn_count field

**Found during:** Plan 04-03, Task 2 (test_session.py)
**File:** `hazn_platform/hazn_platform/orchestrator/metering.py` line 136
**Issue:** `flush_to_db()` writes `turn_count` to `WorkflowAgent.objects.update_or_create(defaults={...})` but the `WorkflowAgent` model in `models.py` does not have a `turn_count` field.
**Impact:** Any real workflow run that triggers metering flush will fail with `FieldError: Invalid field name(s) for model WorkflowAgent: 'turn_count'`.
**Workaround in tests:** Mocked `flush_to_db` in `test_end_records_totals`.
**Fix:** Either add `turn_count` field to `WorkflowAgent` model, or remove `turn_count` from the `defaults` dict in `flush_to_db()`.

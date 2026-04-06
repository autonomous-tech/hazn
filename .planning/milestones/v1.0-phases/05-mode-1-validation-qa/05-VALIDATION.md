---
phase: 5
slug: mode-1-validation-qa
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-06
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 + pytest-django 4.12.0 |
| **Config file** | `hazn_platform/pyproject.toml` |
| **Quick run command** | `cd hazn_platform && python -m pytest tests/ -x -q --no-header` |
| **Full suite command** | `cd hazn_platform && python -m pytest tests/ -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd hazn_platform && python -m pytest tests/ -x -q --no-header`
- **After every plan wave:** Run `cd hazn_platform && python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | QA-01 | unit | `pytest tests/test_qa_runner.py -x` | W0 | pending |
| 05-01-02 | 01 | 1 | QA-02 | unit | `pytest tests/test_qa_criteria.py -x` | W0 | pending |
| 05-02-01 | 02 | 1 | QA-03 | unit | `pytest tests/test_qa_approval.py -x` | W0 | pending |
| 05-02-02 | 02 | 1 | QA-04 | unit | `pytest tests/test_qa_models.py -x` | W0 | pending |
| 05-03-01 | 03 | 2 | DATA-01 | unit | `pytest tests/test_data_lifecycle.py::TestRetentionEnforcement -x` | W0 | pending |
| 05-03-02 | 03 | 2 | DATA-02 | unit | `pytest tests/test_data_lifecycle.py::TestGDPRDeletion -x` | W0 | pending |
| 05-03-03 | 03 | 2 | DATA-03 | unit | `pytest tests/test_data_lifecycle.py::TestIndependentL3Deletion -x` | W0 | pending |
| 05-03-04 | 03 | 2 | DATA-04 | unit | `pytest tests/test_data_lifecycle.py::TestDeletionNotification -x` | W0 | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_qa_runner.py` — stubs for QA-01 (QA auto-injection, should_run_qa logic)
- [ ] `tests/test_qa_criteria.py` — stubs for QA-02 (all 6 task type criteria exist, weights sum to 1.0)
- [ ] `tests/test_qa_approval.py` — stubs for QA-03 (48h timeout HITL item creation, auto-approve on timeout)
- [ ] `tests/test_qa_models.py` — stubs for QA-04 (Deliverable model with preview_url, QA verdict fields)
- [ ] `tests/test_data_lifecycle.py` — stubs for DATA-01 through DATA-04 (retention, GDPR, independent L3, notification)
- [ ] Migration for new `qa` app models (Deliverable)
- [ ] Migration for Agency.churned_at, Agency.deletion_notified_at fields
- [ ] Migration for EndClient.deletion_requested_at, EndClient.deletion_scheduled_at fields
- [ ] New `qa` app registered in INSTALLED_APPS

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Vercel preview URL accessible | QA-04 | Requires live Vercel deployment | Deploy test project, verify preview URL loads in browser |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

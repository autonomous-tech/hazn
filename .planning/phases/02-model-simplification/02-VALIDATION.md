---
phase: 2
slug: model-simplification
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-12
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 + pytest-django 4.12.0 |
| **Config file** | `hazn_platform/pyproject.toml` [tool.pytest.ini_options] |
| **Quick run command** | `cd hazn_platform && python -m pytest tests/test_orchestrator_models.py tests/test_models.py -x --no-header -q` |
| **Full suite command** | `cd hazn_platform && python -m pytest tests/ -x --no-header -q` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd hazn_platform && python -m pytest tests/test_orchestrator_models.py tests/test_models.py -x --no-header -q`
- **After every plan wave:** Run `cd hazn_platform && python -m pytest tests/ -x --no-header -q`
- **Before `/gsd:verify-work`:** Full suite must be green + `python manage.py makemigrations --check`
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | STRP-02 | unit | `python -m pytest tests/test_orchestrator_models.py -x -q` | Yes (needs update) | ⬜ pending |
| 02-01-02 | 01 | 1 | STRP-03 | unit | `python -m pytest tests/test_orchestrator_models.py -x -q` | Yes (needs new test) | ⬜ pending |
| 02-01-03 | 01 | 1 | STRP-07 | unit | `python -m pytest tests/ -x -q` | Yes (delete test) | ⬜ pending |
| 02-02-01 | 02 | 2 | STRP-10 | unit | `python -m pytest tests/test_models.py -x -q` | Yes (needs update) | ⬜ pending |
| 02-02-02 | 02 | 2 | STRP-10 | unit | `python -m pytest tests/test_workspace_clients.py tests/test_workspace_dashboard.py -x -q` | Yes (needs update) | ⬜ pending |
| 02-02-03 | 02 | 2 | STRP-10 | smoke | `python manage.py makemigrations --check` | N/A (CLI) | ⬜ pending |
| 02-02-04 | 02 | 2 | ALL | smoke | `python manage.py migrate --run-syncdb` | N/A (CLI) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_orchestrator_models.py` — needs new test for WorkflowPhaseOutput.html_content and .markdown_source fields
- [ ] `tests/test_models.py` — needs new test for Agency singleton constraint
- [ ] `tests/test_workspace_clients.py` — needs update: remove agency_role from user creation, use IsAuthenticated
- [ ] `tests/test_workspace_dashboard.py` — needs update: remove pending_approvals and ready_deliverables assertions
- [ ] Tests to DELETE: test_conflict_detector.py, test_hitl.py, test_hitl_api.py, test_qa_models.py, test_qa_runner.py, test_qa_approval.py, test_qa_criteria.py, test_qa_staging.py, test_workspace_hitl.py, test_workspace_deliverables.py

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Django starts cleanly with simplified models | ALL | System-level boot check | Run `python manage.py check --deploy` and verify no errors |
| Fresh DB migration applies cleanly | STRP-10 | Full migration chain | Delete DB, run `python manage.py migrate`, verify tables created |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

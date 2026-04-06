---
phase: 10
slug: first-workflow-end-to-end
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-06
---

# Phase 10 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (Django) |
| **Config file** | hazn_platform/config/settings/test.py |
| **Quick run command** | `cd hazn_platform && python -m pytest tests/test_deliverable_pipeline.py tests/test_workflow_catalog.py tests/test_sse_events.py -x --timeout=30` |
| **Full suite command** | `cd hazn_platform && python -m pytest tests/ -x --timeout=60` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd hazn_platform && python -m pytest tests/test_deliverable_pipeline.py tests/test_workflow_catalog.py tests/test_sse_events.py -x --timeout=30`
- **After every plan wave:** Run `cd hazn_platform && python -m pytest tests/ -x --timeout=60`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 10-01-01 | 01 | 0 | WKFL-01 | unit | `pytest tests/test_workflow_catalog.py -x` | ❌ W0 | ⬜ pending |
| 10-01-02 | 01 | 0 | WKFL-05 | unit | `pytest tests/test_sse_events.py -x` | ❌ W0 | ⬜ pending |
| 10-01-03 | 01 | 0 | DLVR-01, DLVR-02 | unit | `pytest tests/test_deliverable_pipeline.py -x` | ❌ W0 | ⬜ pending |
| 10-02-01 | 02 | 1 | WKFL-01 | unit | `pytest tests/test_workflow_catalog.py -x` | ✅ W0 | ⬜ pending |
| 10-02-02 | 02 | 1 | WKFL-01 | unit | `pytest tests/test_workspace_workflows.py -x` | ✅ | ⬜ pending |
| 10-02-03 | 02 | 1 | WKFL-02 | unit | `pytest tests/test_executor.py -x` | ✅ | ⬜ pending |
| 10-02-04 | 02 | 1 | WKFL-05 | unit | `pytest tests/test_sse_events.py -x` | ✅ W0 | ⬜ pending |
| 10-02-05 | 02 | 1 | DLVR-01, DLVR-02 | unit | `pytest tests/test_deliverable_pipeline.py -x` | ✅ W0 | ⬜ pending |
| 10-02-06 | 02 | 1 | DLVR-03, DLVR-04 | unit | `pytest tests/test_workspace_deliverables.py -x` | ✅ | ⬜ pending |
| 10-03-01 | 03 | 2 | ALL | integration | `pytest tests/ -x --timeout=60` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_workflow_catalog.py` — stubs for WKFL-01 catalog endpoint
- [ ] `tests/test_sse_events.py` — stubs for WKFL-05 SSE emission from executor
- [ ] `tests/test_deliverable_pipeline.py` — stubs for DLVR-01 JSON validation, DLVR-02 Jinja2 rendering
- [ ] Deliverable model migration (add html_content, markdown_source) — prerequisite for DLVR-03

*Existing infrastructure covers: test_executor.py, test_workspace_workflows.py, test_workspace_deliverables.py*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real-time SSE updates render in browser | WKFL-05 | Requires live SSE connection + browser rendering | 1. Trigger workflow from UI 2. Observe PhaseStepper updates in real-time 3. Verify WorkflowChat shows phase summaries |
| Full E2E with real GA4/GSC data | WKFL-02 | Requires real API credentials and live API calls | 1. Configure Vault credentials for Autonomous client 2. Trigger SEO audit workflow 3. Verify report contains real analytics data |
| Branded HTML report visual quality | DLVR-02 | Visual rendering quality check | 1. Open rendered HTML report 2. Verify Autonomous branding (logo, colors, footer) 3. Check responsive layout |
| Failure UX with partial results | WKFL-02 | Requires forced failure mid-workflow | 1. Trigger workflow with invalid credentials 2. Verify failed phase shows red error in timeline 3. Verify completed phases still show summaries |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

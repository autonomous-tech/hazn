---
phase: 6
slug: mode-3-workspace
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-06
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x + pytest-django (backend), vitest (frontend -- Wave 0 installs) |
| **Config file** | hazn_platform/pyproject.toml (backend), frontend/vitest.config.ts (Wave 0) |
| **Quick run command** | `cd hazn_platform && python -m pytest tests/ -x --tb=short -q` |
| **Full suite command** | `cd hazn_platform && python -m pytest` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd hazn_platform && python -m pytest tests/ -x --tb=short -q`
- **After every plan wave:** Run `cd hazn_platform && python -m pytest`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | WS-01 | unit | `pytest tests/test_workspace_dashboard.py -x` | No -- W0 | pending |
| 06-01-02 | 01 | 1 | WS-03 | unit | `pytest tests/test_workspace_clients.py -x` | No -- W0 | pending |
| 06-02-01 | 02 | 2 | WS-02 | unit | `pytest tests/test_workspace_memory.py -x` | No -- W0 | pending |
| 06-02-02 | 02 | 2 | WS-03 | unit | `pytest tests/test_workspace_clients.py -x` | No -- W0 | pending |
| 06-03-01 | 03 | 2 | WS-04 | unit | `pytest tests/test_workspace_workflows.py -x` | No -- W0 | pending |
| 06-03-02 | 03 | 2 | WS-05 | unit | `pytest tests/test_workspace_hitl.py -x` | No -- W0 | pending |
| 06-03-03 | 03 | 2 | WS-06 | unit | `pytest tests/test_workspace_deliverables.py -x` | No -- W0 | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_workspace_dashboard.py` — stubs for WS-01
- [ ] `tests/test_workspace_memory.py` — stubs for WS-02
- [ ] `tests/test_workspace_clients.py` — stubs for WS-03
- [ ] `tests/test_workspace_workflows.py` — stubs for WS-04
- [ ] `tests/test_workspace_hitl.py` — stubs for WS-05
- [ ] `tests/test_workspace_deliverables.py` — stubs for WS-06
- [ ] Frontend test infrastructure: vitest + @testing-library/react + jsdom + vitest.config.ts
- [ ] User model migration adding agency FK + role field (prerequisite for all workspace tests)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Collapsible sidebar responsive behavior | WS-01 | Visual/layout behavior across breakpoints | Resize browser from 1440px to 375px, verify sidebar collapses to hamburger menu |
| Cmd-K search navigates to correct entity | WS-01 | Interactive keyboard navigation | Press Cmd-K, type "client name", verify results appear and clicking navigates |
| Memory card inline edit saves correctly | WS-02 | Interactive edit flow with live UI update | Click memory card, edit text, click save, verify updated in both UI and API |
| Workflow chat-style log stream renders | WS-04 | SSE streaming + visual rendering | Trigger workflow, verify chat messages appear in real-time via SSE |
| Share link renders deliverable without auth | WS-06 | Public unauthenticated access | Generate share link, open in incognito browser, verify deliverable renders |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

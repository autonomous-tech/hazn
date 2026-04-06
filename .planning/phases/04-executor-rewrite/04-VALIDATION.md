---
phase: 4
slug: executor-rewrite
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-13
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 + pytest-django 4.12.0 + pytest-asyncio >=0.23.0 |
| **Config file** | `hazn_platform/pyproject.toml` [tool.pytest.ini_options] |
| **Quick run command** | `cd hazn_platform && python -m pytest tests/test_executor.py tests/test_session.py tests/test_orchestrator_tasks.py -x -q` |
| **Full suite command** | `cd hazn_platform && python -m pytest tests/ -x -q` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd hazn_platform && python -m pytest tests/test_executor.py tests/test_session.py tests/test_orchestrator_tasks.py -x -q`
- **After every plan wave:** Run `cd hazn_platform && python -m pytest tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 0 | EXEC-01 | unit | `cd hazn_platform && python -m pytest tests/test_executor.py -x -q -k "dag_order or execution_order"` | ❌ W0 | ⬜ pending |
| 04-01-02 | 01 | 0 | EXEC-04 | unit | `cd hazn_platform && python -m pytest tests/test_executor.py -x -q -k "prior_phase or output_pass"` | ❌ W0 | ⬜ pending |
| 04-01-03 | 01 | 0 | EXEC-05 | unit | `cd hazn_platform && python -m pytest tests/test_orchestrator_tasks.py -x -q` | ❌ W0 | ⬜ pending |
| 04-01-04 | 01 | 0 | EXEC-06 | unit | `cd hazn_platform && python -m pytest tests/test_executor.py -x -q -k "phase_output"` | ❌ W0 | ⬜ pending |
| 04-01-05 | 01 | 0 | EXEC-02 | unit | `cd hazn_platform && python -m pytest tests/test_prompt_assembler.py -x -q` | ✅ | ⬜ pending |
| 04-01-06 | 01 | 0 | EXEC-03 | unit | `cd hazn_platform && python -m pytest tests/test_prompt_assembler.py -x -q -k "skill"` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_executor.py` — complete rewrite: remove HITLItem import, conflict_detector mocks, QA mocks; add DAG order tests, prior-phase-output tests, retry logic tests, optional-phase-skip tests, phase output storage tests
- [ ] `tests/test_session.py` — partial rewrite: remove log_conflicts test, add load_client_context test, adapt memory pattern for one-agent-per-client
- [ ] `tests/test_orchestrator_tasks.py` — partial rewrite: remove deliver_webhook and check_hitl_timeouts tests, simplify run_workflow test for new session/executor API
- [ ] `tests/test_agent_runner.py` — DELETE: agent_runner.py is deleted
- [ ] `tests/test_agent_sdk_backend.py` — DELETE: backends/ directory is deleted
- [ ] `tests/test_agent_manager.py` — DELETE or rewrite: agent_manager.py is being replaced

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| SSE events fire at phase boundaries | EXEC-05 | Requires active SSE connection in browser | 1. Start workflow via API 2. Open SSE endpoint 3. Verify phase_started, phase_completed, workflow_completed events arrive |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

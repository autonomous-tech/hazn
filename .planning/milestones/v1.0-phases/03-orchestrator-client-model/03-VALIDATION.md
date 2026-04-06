---
phase: 3
slug: orchestrator-client-model
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-05
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 + pytest-django 4.12.0 |
| **Config file** | `hazn_platform/pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `cd hazn_platform && .venv/bin/pytest tests/test_orchestrator_models.py tests/test_workflow_parser.py -x` |
| **Full suite command** | `cd hazn_platform && .venv/bin/pytest tests/ -x` |
| **Estimated runtime** | ~20 seconds |

---

## Sampling Rate

- **After every task commit:** Run the task's `<automated>` verify command
- **After every plan wave:** Run `cd hazn_platform && .venv/bin/pytest tests/ -x`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Test File(s) | Automated Command | Status |
|---------|------|------|-------------|-------------------|--------|
| 03-01-T1 | 01 | 1 | `tests/test_orchestrator_models.py` | `cd hazn_platform && .venv/bin/pytest tests/test_orchestrator_models.py -x --tb=short` | pending |
| 03-01-T2 | 01 | 1 | `tests/test_workflow_parser.py` | `cd hazn_platform && .venv/bin/pytest tests/test_workflow_parser.py -x --tb=short` | pending |
| 03-02-T1 | 02 | 2 | `tests/test_agent_manager.py` | `cd hazn_platform && .venv/bin/pytest tests/test_agent_manager.py -x --tb=short` | pending |
| 03-02-T2 | 02 | 2 | `tests/test_session.py`, `tests/test_metering.py` | `cd hazn_platform && .venv/bin/pytest tests/test_session.py tests/test_metering.py -x --tb=short` | pending |
| 03-03-T1 | 03 | 2 | `tests/test_conflict_detector.py` | `cd hazn_platform && .venv/bin/pytest tests/test_conflict_detector.py -x --tb=short` | pending |
| 03-03-T2 | 03 | 2 | `tests/test_hitl.py` | `cd hazn_platform && .venv/bin/pytest tests/test_hitl.py -x --tb=short` | pending |
| 03-04-T1 | 04 | 3 | `tests/test_executor.py` | `cd hazn_platform && .venv/bin/pytest tests/test_executor.py -x --tb=short` | pending |
| 03-04-T2 | 04 | 3 | `tests/test_orchestrator_tasks.py` | `cd hazn_platform && .venv/bin/pytest tests/test_orchestrator_tasks.py -x --tb=short` | pending |
| 03-04-T3 | 04 | 3 | `tests/test_hitl_api.py` | `cd hazn_platform && .venv/bin/pytest tests/test_hitl_api.py -x --tb=short` | pending |

---

## Requirement Coverage

| Requirement | Plan(s) | Test File(s) |
|-------------|---------|-------------|
| ORCH-01 | 02 | `test_session.py` (session start, context loading) |
| ORCH-02 | 02 | `test_session.py` (HaznMemory context injection) |
| ORCH-03 | 02 | `test_session.py` (checkpoint, end, timeout) |
| ORCH-04 | 01 | `test_orchestrator_models.py` (metering models) |
| ORCH-05 | 03 | `test_hitl.py` (HITL queue management) |
| ORCH-06 | 01, 04 | `test_workflow_parser.py` (YAML parsing), `test_executor.py` (DAG execution) |
| ORCH-07 | 04 | `test_executor.py` (tool scoping per phase) |
| CLT-01 | 01 | `test_orchestrator_models.py` (Agency FK on WorkflowRun) |
| CLT-02 | 01 | `test_orchestrator_models.py` (EndClient FK on WorkflowRun) |
| CLT-03 | 01 | `test_orchestrator_models.py` (three-layer model expressed) |
| CLT-04 | 03 | `test_conflict_detector.py` (L3 wins by default) |
| CLT-05 | 03 | `test_conflict_detector.py` (hard rule overrides L3) |
| CLT-06 | 03 | `test_conflict_detector.py`, `test_hitl.py` (soft rule flags for review, timeout behavior) |
| CRED-01 | 02 | `test_session.py` (Vault AppRole credential path) |
| CRED-02 | 02 | `test_session.py` (secret isolation -- raw secrets never in WorkflowRun or context) |
| CRED-03 | 02 | `test_session.py` (VaultCredential scoping per L2/L3) |
| CRED-04 | 02 | `test_session.py` (get_credentials MCP tool -- already implemented Phase 2) |

---

## Wave 0 Requirements

Each plan's TDD tasks create their own test files as part of the RED phase. No separate Wave 0 needed -- all test files are created by the tasks themselves:

- Plan 01 Task 1 creates: `tests/test_orchestrator_models.py`
- Plan 01 Task 2 creates: `tests/test_workflow_parser.py`
- Plan 02 Task 1 creates: `tests/test_agent_manager.py`
- Plan 02 Task 2 creates: `tests/test_session.py`, `tests/test_metering.py`
- Plan 03 Task 1 creates: `tests/test_conflict_detector.py`
- Plan 03 Task 2 creates: `tests/test_hitl.py`
- Plan 04 Task 1 creates: `tests/test_executor.py`
- Plan 04 Task 2 creates: `tests/test_orchestrator_tasks.py`
- Plan 04 Task 3 creates: `tests/test_hitl_api.py`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Webhook delivery reaches external URL | HITL notifications | Requires external endpoint | 1. Set webhook URL in Agency 2. Trigger HITL item 3. Verify webhook received at URL |
| Letta agent persona refresh | ORCH-06 + context | Depends on running Letta server | 1. Update agent markdown 2. Start workflow session 3. Verify Letta agent has updated system prompt |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify commands
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Task IDs match actual plan structure (4 plans, 9 tasks total)
- [x] Test file paths match actual plan `<files>` declarations
- [x] No watch-mode flags
- [x] Feedback latency < 20s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

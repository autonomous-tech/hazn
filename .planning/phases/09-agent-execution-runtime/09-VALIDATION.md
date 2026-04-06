---
phase: 9
slug: agent-execution-runtime
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-06
---

# Phase 9 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 + pytest-django 4.12.0 + pytest-asyncio >=0.23.0 |
| **Config file** | pyproject.toml `[tool.pytest.ini_options]` |
| **Quick run command** | `cd hazn_platform && python -m pytest tests/test_agent_runner.py tests/test_budget.py tests/test_tool_wiring.py -x -q` |
| **Full suite command** | `cd hazn_platform && python -m pytest tests/ -x -q` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd hazn_platform && python -m pytest tests/test_agent_runner.py tests/test_budget.py tests/test_tool_wiring.py -x -q`
- **After every plan wave:** Run `cd hazn_platform && python -m pytest tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 09-01-01 | 01 | 1 | RUNT-02 | unit (mocked API) | `pytest tests/test_agent_runner.py::TestAgentRunnerLoop -x` | W0 | pending |
| 09-01-02 | 01 | 1 | RUNT-02 | unit (mocked API) | `pytest tests/test_agent_runner.py::TestParallelToolDispatch -x` | W0 | pending |
| 09-01-03 | 01 | 1 | RUNT-05 | unit | `pytest tests/test_budget.py::TestCostCalculation -x` | W0 | pending |
| 09-01-04 | 01 | 1 | RUNT-06 | unit (mocked API) | `pytest tests/test_budget.py::TestBudgetEnforcement -x` | W0 | pending |
| 09-01-05 | 01 | 1 | RUNT-06 | unit (mocked API) | `pytest tests/test_agent_runner.py::TestBudgetHalt -x` | W0 | pending |
| 09-01-06 | 01 | 1 | RUNT-07 | unit (DB) | `pytest tests/test_budget.py::TestAgencyCostCap -x` | W0 | pending |
| 09-01-07 | 01 | 1 | RUNT-07 | unit (DB) | `pytest tests/test_budget.py::TestAgencyCostCapAlert -x` | W0 | pending |
| 09-02-01 | 02 | 1 | ALL | unit | `pytest tests/test_tool_wiring.py -x` | W0 | pending |
| 09-02-02 | 02 | 1 | ALL | unit (mocked) | `pytest tests/test_agent_runner.py::TestLangfuseMetering -x` | W0 | pending |
| 09-03-01 | 03 | 2 | RUNT-04 | integration | `pytest tests/test_agent_sdk_backend.py -x -m integration` | W0 | pending |
| 09-03-02 | 03 | 2 | RUNT-05 | integration | `pytest tests/test_anthropic_backend.py -x -m integration` | W0 | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_agent_runner.py` — stubs for RUNT-02: tool_use loop, parallel dispatch, budget halt, Langfuse metering
- [ ] `tests/test_budget.py` — stubs for RUNT-05, RUNT-06, RUNT-07: cost calculation, budget enforcement, agency cost cap
- [ ] `tests/test_tool_wiring.py` — stubs for ALL: tool callable wiring, AppConfig.ready(), scoped tool filtering
- [ ] `tests/test_anthropic_backend.py` — stubs for RUNT-05: integration test (API key required)
- [ ] `tests/test_agent_sdk_backend.py` — stubs for RUNT-04: integration test (CLI required)
- [ ] Package install: `pip install anthropic>=0.84.0 claude-agent-sdk>=0.1.47`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Agent SDK per-turn token reporting | RUNT-04 | SDK alpha — per-turn visibility uncertain | Run SDK backend against real API, inspect message objects for usage fields |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

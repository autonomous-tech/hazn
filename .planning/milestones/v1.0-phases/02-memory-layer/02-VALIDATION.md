---
phase: 2
slug: memory-layer
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-05
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 + pytest-django 4.12.0 |
| **Config file** | `hazn_platform/pyproject.toml` [tool.pytest.ini_options] |
| **Quick run command** | `cd hazn_platform && uv run pytest tests/test_memory.py -x` |
| **Full suite command** | `cd hazn_platform && uv run pytest tests/ -x` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd hazn_platform && uv run pytest tests/test_memory.py -x`
- **After every plan wave:** Run `cd hazn_platform && uv run pytest tests/ -x`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | MEM-01 | unit | `pytest tests/test_memory.py -x -k "type"` | No -- Wave 0 | pending |
| 02-01-02 | 01 | 1 | MEM-02, MEM-08 | unit | `pytest tests/test_memory.py -x -v` | No -- Wave 0 | pending |
| 02-02-01 | 02 | 2 | MEM-04, MEM-05, MEM-06, MEM-07 | unit | `pytest tests/test_memory.py -x -v -k "checkpoint or failure or end_session or record_turn or write_finding"` | No -- Wave 0 | pending |
| 02-02-02 | 02 | 2 | MEM-03, MEM-10 | integration | `pytest tests/integration/test_memory_integration.py -x -v -m integration` | No -- Wave 0 | pending |
| 02-03-01 | 03 | 2 | MCP-01 | unit | `pytest tests/test_mcp_memory_server.py -x -v` | No -- Wave 0 | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_memory.py` -- unit tests for HaznMemory (mock Letta client); covers MEM-01,02,04,05,06,07,08,09
- [ ] `tests/test_mcp_memory_server.py` -- unit tests for MCP tool definitions; covers MCP-01
- [ ] `tests/integration/test_memory_integration.py` -- integration tests requiring Letta+Postgres; covers MEM-03,10
- [ ] `tests/integration/__init__.py` -- package init
- [ ] `tests/factories.py` -- factory_boy factories for Agency, EndClient, BrandVoice, Keyword, Campaign (if not exists)
- [ ] Framework install: `uv add fastmcp` -- MCP server dependency

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Context injection <2s with real Letta | MEM-03 | Requires live Letta server with realistic data volume | 1. Start Letta server 2. Load test client with 50+ data points 3. Time load_client_context() 4. Verify <2s |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

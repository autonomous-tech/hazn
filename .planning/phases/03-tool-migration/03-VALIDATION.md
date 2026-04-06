---
phase: 3
slug: tool-migration
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-12
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 + pytest-asyncio + pytest-django |
| **Config file** | pyproject.toml `[tool.pytest.ini_options]` |
| **Quick run command** | `cd hazn_platform && python -m pytest tests/test_tool_registry.py tests/test_tools_memory.py tests/test_tools_analytics.py tests/test_tools_github.py tests/test_tools_vercel.py tests/test_tools_filesystem.py tests/test_tools_web.py -x -q` |
| **Full suite command** | `cd hazn_platform && python -m pytest tests/ -x -q` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd hazn_platform && python -m pytest tests/test_tool_registry.py tests/test_tools_*.py -x -q`
- **After every plan wave:** Run `cd hazn_platform && python -m pytest tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 0 | TOOL-08 | unit | `pytest tests/test_tool_registry.py -x` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 0 | TOOL-01 | unit | `pytest tests/test_tools_filesystem.py -x` | ❌ W0 | ⬜ pending |
| 03-01-03 | 01 | 0 | TOOL-02 | unit | `pytest tests/test_tools_web.py -x` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 1 | TOOL-01 | unit | `pytest tests/test_tools_filesystem.py -x` | ❌ W0 | ⬜ pending |
| 03-02-02 | 02 | 1 | TOOL-02 | unit | `pytest tests/test_tools_web.py -x` | ❌ W0 | ⬜ pending |
| 03-02-03 | 02 | 1 | TOOL-03, TOOL-04, TOOL-05 | unit+mock | `pytest tests/test_tools_analytics.py -x` | ❌ W0 | ⬜ pending |
| 03-02-04 | 02 | 1 | TOOL-06 | unit+mock | `pytest tests/test_tools_github.py -x` | ❌ W0 | ⬜ pending |
| 03-02-05 | 02 | 1 | TOOL-07 | unit+mock | `pytest tests/test_tools_vercel.py -x` | ❌ W0 | ⬜ pending |
| 03-03-01 | 03 | 2 | STRP-01 | unit | `pytest tests/test_tool_registry.py -x` (verifies no MCP imports) | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_tool_registry.py` — stubs for STRP-01, TOOL-08 (replaces test_tool_router.py + test_tool_wiring.py)
- [ ] `tests/test_tools_memory.py` — covers memory tool migration (replaces test_mcp_memory_server.py)
- [ ] `tests/test_tools_analytics.py` — covers TOOL-03, TOOL-04, TOOL-05 (replaces test_mcp_analytics_server.py + test_data_tools.py)
- [ ] `tests/test_tools_github.py` — covers TOOL-06 (replaces test_mcp_github_server.py)
- [ ] `tests/test_tools_vercel.py` — covers TOOL-07 (replaces test_mcp_vercel_server.py)
- [ ] `tests/test_tools_filesystem.py` — covers TOOL-01 (new)
- [ ] `tests/test_tools_web.py` — covers TOOL-02 (new)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GA4 retrieves real data via Vault creds | TOOL-03 | Requires live GA4 property + Vault | Run `pytest tests/test_tools_analytics.py::TestGA4Tool -x` with test client Vault creds configured |
| GSC retrieves real data via Vault creds | TOOL-04 | Requires live GSC property + Vault | Run `pytest tests/test_tools_analytics.py::TestGSCTool -x` with test client Vault creds configured |
| PageSpeed retrieves real data | TOOL-05 | Requires live PageSpeed API key | Run `pytest tests/test_tools_analytics.py::TestPageSpeedTool -x` with API key |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

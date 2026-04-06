---
phase: 4
slug: mcp-tool-servers-observability
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-06
---

# Phase 4 — Validation Strategy

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
| 04-01-01 | 01 | 1 | MCP-02 | unit | `pytest tests/test_mcp_vercel_server.py -x` | Wave 0 | pending |
| 04-01-02 | 01 | 1 | MCP-03 | unit | `pytest tests/test_mcp_github_server.py -x` | Wave 0 | pending |
| 04-02-01 | 02 | 1 | MCP-04 | unit | `pytest tests/test_mcp_analytics_server.py -x` | Wave 0 | pending |
| 04-02-02 | 02 | 1 | MCP-05 | unit | `pytest tests/test_mcp_analytics_server.py::TestPageSpeed -x` | Wave 0 | pending |
| 04-03-01 | 03 | 2 | OBS-01 | unit | `pytest tests/test_tracing.py -x` | Wave 0 | pending |
| 04-03-02 | 03 | 2 | OBS-02 | unit | `pytest tests/test_orchestrator_models.py -x` | Extends existing | pending |
| 04-03-03 | 03 | 2 | OBS-03 | unit | `pytest tests/test_metering.py -x` | Existing | pending |
| 04-03-04 | 03 | 2 | OBS-04 | unit | `pytest tests/test_metering.py::TestToolCallMetering -x` | Wave 0 | pending |
| 04-03-05 | 03 | 2 | OBS-05 | unit | `pytest tests/test_metering.py::TestRunawayAlerts -x` | Wave 0 | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_mcp_vercel_server.py` — stubs for MCP-02
- [ ] `tests/test_mcp_github_server.py` — stubs for MCP-03
- [ ] `tests/test_mcp_analytics_server.py` — stubs for MCP-04, MCP-05
- [ ] `tests/test_tracing.py` — stubs for OBS-01, OBS-05
- [ ] Test additions to `tests/test_metering.py` for tool call metering (OBS-04)
- [ ] All external API calls mocked (httpx, PyGithub, Google clients, OpenAI, Langfuse)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Langfuse trace visible in UI | OBS-01 | Requires running Langfuse instance | Deploy Langfuse, run workflow, verify trace appears with correct tags |
| Vercel deploy succeeds on real project | MCP-02 | Requires Vercel account + project | Use staging Vercel token, deploy test project, verify preview URL loads |
| GitHub PR creation on real repo | MCP-03 | Requires GitHub PAT + test repo | Create test repo, trigger PR creation, verify PR visible on GitHub |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

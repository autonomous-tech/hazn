---
phase: 8
slug: foundation-components
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-06
---

# Phase 8 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 + pytest-django 4.12.0 + pytest-asyncio 1.3.0 |
| **Config file** | `hazn_platform/pyproject.toml` [tool.pytest.ini_options] |
| **Quick run command** | `cd hazn_platform && .venv/bin/pytest tests/test_prompt_assembler.py tests/test_tool_router.py tests/test_output_collector.py -x -q` |
| **Full suite command** | `cd hazn_platform && .venv/bin/pytest tests/ -x -q` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd hazn_platform && .venv/bin/pytest tests/test_prompt_assembler.py tests/test_tool_router.py tests/test_output_collector.py -x -q`
- **After every plan wave:** Run `cd hazn_platform && .venv/bin/pytest tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 08-01-01 | 01 | 1 | RUNT-01 | unit | `.venv/bin/pytest tests/test_prompt_assembler.py -x` | No -- Wave 0 | pending |
| 08-01-02 | 01 | 1 | RUNT-01 | unit | `.venv/bin/pytest tests/test_prompt_assembler.py::TestSkillInjection -x` | No -- Wave 0 | pending |
| 08-01-03 | 01 | 1 | RUNT-01 | unit | `.venv/bin/pytest tests/test_prompt_assembler.py::TestReferenceHandling -x` | No -- Wave 0 | pending |
| 08-02-01 | 02 | 1 | RUNT-03 | unit | `.venv/bin/pytest tests/test_tool_router.py::TestAnthropicDispatch -x` | No -- Wave 0 | pending |
| 08-02-02 | 02 | 1 | RUNT-03 | unit | `.venv/bin/pytest tests/test_tool_router.py::TestAgentSDKDispatch -x` | No -- Wave 0 | pending |
| 08-02-03 | 02 | 1 | RUNT-03 | unit | `.venv/bin/pytest tests/test_tool_router.py::TestErrorHandling -x` | No -- Wave 0 | pending |
| 08-03-01 | 03 | 1 | RUNT-08 | unit | `.venv/bin/pytest tests/test_output_collector.py::TestReportArtifact -x` | No -- Wave 0 | pending |
| 08-03-02 | 03 | 1 | RUNT-08 | unit | `.venv/bin/pytest tests/test_output_collector.py::TestFindingsExtraction -x` | No -- Wave 0 | pending |
| 08-03-03 | 03 | 1 | RUNT-08 | unit | `.venv/bin/pytest tests/test_output_collector.py::TestCodeArtifacts -x` | No -- Wave 0 | pending |
| 08-03-04 | 03 | 1 | RUNT-08 | unit | `.venv/bin/pytest tests/test_output_collector.py::TestMetadataExtraction -x` | No -- Wave 0 | pending |
| 08-04-01 | 04 | 1 | ALL | unit | `.venv/bin/pytest tests/test_prompt_assembler.py tests/test_tool_router.py tests/test_output_collector.py -x` | No -- Wave 0 | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_prompt_assembler.py` -- stubs for RUNT-01
- [ ] `tests/test_tool_router.py` -- stubs for RUNT-03
- [ ] `tests/test_output_collector.py` -- stubs for RUNT-08
- [ ] `tests/fixtures/tool_use_responses.json` -- mock Anthropic API tool_use blocks
- [ ] `tests/fixtures/agent_sdk_tool_calls.json` -- mock Agent SDK format calls
- [ ] `tests/fixtures/agent_outputs/seo_audit_report.md` -- realistic agent output fixture
- [ ] `tests/fixtures/agent_outputs/analytics_findings.md` -- findings-heavy output fixture
- [ ] `hazn_platform/testing/__init__.py` -- reusable mock module
- [ ] `hazn_platform/testing/mocks.py` -- mock LLM response builder, mock tool dispatch
- [ ] `hazn_platform/testing/fixtures.py` -- fixture data loaders

*Existing infrastructure covers framework install (pytest 9.0.2 already configured).*

---

## Manual-Only Verifications

*All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

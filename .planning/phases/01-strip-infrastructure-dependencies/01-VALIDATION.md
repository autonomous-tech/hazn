---
phase: 1
slug: strip-infrastructure-dependencies
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-12
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 + pytest-django 4.12.0 + pytest-asyncio >= 0.23.0 |
| **Config file** | `pyproject.toml` [tool.pytest.ini_options] |
| **Quick run command** | `cd hazn_platform && uv run pytest tests/ -x --no-header -q` |
| **Full suite command** | `cd hazn_platform && uv run pytest tests/ --no-header -q` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd hazn_platform && uv run pytest tests/ -x --no-header -q`
- **After every plan wave:** Run `cd hazn_platform && uv run pytest tests/ --no-header -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | STRP-04 | unit | `uv run pytest tests/test_agent_sdk_backend.py -x` | Yes (needs update) | ⬜ pending |
| 01-01-02 | 01 | 1 | STRP-05 | unit | `uv run pytest tests/test_agent_runner.py tests/test_executor.py -x` | Yes (needs update) | ⬜ pending |
| 01-01-03 | 01 | 1 | STRP-06 | unit | `uv run pytest tests/test_tracing.py tests/test_metering.py -x` | Yes | ⬜ pending |
| 01-01-04 | 01 | 1 | STRP-08 | unit | `uv run pytest tests/test_session.py -x` | Yes (needs update) | ⬜ pending |
| 01-01-05 | 01 | 1 | STRP-09 | unit | `uv run pytest tests/test_orchestrator_tasks.py -x` | Yes (needs update) | ⬜ pending |
| 01-02-01 | 02 | 1 | ALL | integration | `python manage.py check && uv run pytest tests/ --no-header -q` | Yes | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements. Tests need updating (removing deleted references), not creating new test files.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Django starts cleanly | ALL | System-level boot check | Run `python manage.py check --deploy` and verify no errors |
| No Langfuse service in Docker Compose | STRP-06 | Config file check | Verify `docker-compose.local.yml` has no langfuse service entry |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

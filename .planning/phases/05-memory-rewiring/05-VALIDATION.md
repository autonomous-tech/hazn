---
phase: 5
slug: memory-rewiring
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-13
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 + pytest-django 4.12.0 |
| **Config file** | `pyproject.toml` [tool.pytest.ini_options] |
| **Quick run command** | `cd hazn_platform && uv run pytest tests/test_memory.py -x -q` |
| **Full suite command** | `cd hazn_platform && uv run pytest tests/ -x -q` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd hazn_platform && uv run pytest tests/test_memory.py -x -q`
- **After every plan wave:** Run `cd hazn_platform && uv run pytest tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 0 | MEMO-01..06 | unit | `uv run pytest tests/test_memory.py -x -q` | Partial — needs API fix | ⬜ pending |
| 05-01-02 | 01 | 1 | MEMO-01 | unit + integration | `uv run pytest tests/test_memory.py -k "test_agent_provisioning" -x` | Partial | ⬜ pending |
| 05-01-03 | 01 | 1 | MEMO-02 | unit + integration | `uv run pytest tests/test_memory.py -k "test_load_client_context" -x` | Partial | ⬜ pending |
| 05-01-04 | 01 | 1 | MEMO-05 | unit + integration | `uv run pytest tests/test_memory.py -k "test_search_memory" -x` | Exists — wrong API shape | ⬜ pending |
| 05-01-05 | 01 | 1 | MEMO-06 | unit + integration | `uv run pytest tests/test_memory.py -k "test_correct_memory" -x` | Exists | ⬜ pending |
| 05-02-01 | 02 | 2 | MEMO-03 | unit | `uv run pytest tests/test_memory.py -k "test_add_learning" -x` | ❌ W0 | ⬜ pending |
| 05-02-02 | 02 | 2 | MEMO-03 | unit | `uv run pytest tests/test_memory.py -k "test_auto_extract" -x` | ❌ W0 | ⬜ pending |
| 05-02-03 | 02 | 2 | MEMO-04 | unit | `uv run pytest tests/test_memory.py -k "test_checkpoint" -x` | Partial | ⬜ pending |
| 05-02-04 | 02 | 2 | MEMO-01..06 | integration | `uv run pytest tests/test_memory_integration.py -x -q` | ❌ W0 | ⬜ pending |
| 05-02-05 | 02 | 2 | MEMO-01..06 | manual | `python manage.py test_memory --client-id <id>` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_memory.py` — update existing tests for API shape fixes (Passage.text, search response shape, SyncArrayPage)
- [ ] `tests/test_memory.py` — add tests for new add_learning tool
- [ ] `tests/test_memory.py` — add tests for auto-extraction logic
- [ ] `tests/test_memory_integration.py` — new file for `@pytest.mark.integration` Docker Letta tests
- [ ] `tests/conftest.py` — add Letta mock fixtures (mock_letta_client, mock_passages, mock_blocks)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| test_memory management command lifecycle | MEMO-01..06 | Requires running Docker Letta | Run `python manage.py test_memory --client-id <uuid> --cleanup` and verify all steps pass |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

---
phase: 7
slug: vault-approle-authentication-scoped-policies
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-05
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (via pyproject.toml) |
| **Config file** | `hazn_platform/pyproject.toml [tool.pytest.ini_options]` |
| **Quick run command** | `docker compose -f docker-compose.local.yml run --rm django pytest tests/test_vault.py -x` |
| **Full suite command** | `docker compose -f docker-compose.local.yml run --rm django pytest` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `docker compose -f docker-compose.local.yml run --rm django pytest tests/test_vault.py -x`
- **After every plan wave:** Run `docker compose -f docker-compose.local.yml run --rm django pytest`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | VAULT-01 | integration | `pytest tests/test_vault.py::TestAppRoleAuth::test_django_approle_login -x` | W0 | pending |
| 07-01-02 | 01 | 1 | VAULT-02 | integration | `pytest tests/test_vault.py::TestAppRoleAuth::test_django_read_write -x` | W0 | pending |
| 07-01-03 | 01 | 1 | VAULT-03 | integration | `pytest tests/test_vault.py::TestPolicyScoping::test_orchestrator_readonly -x` | W0 | pending |
| 07-01-04 | 01 | 1 | VAULT-04 | integration | `pytest tests/test_vault.py::TestPolicyScoping::test_mcp_readonly -x` | W0 | pending |
| 07-01-05 | 01 | 1 | VAULT-05 | integration | `pytest tests/test_vault.py::TestPolicyScoping::test_sys_auth_denied -x` | W0 | pending |
| 07-01-06 | 01 | 1 | VAULT-06 | integration | `pytest tests/test_vault.py::TestVaultClient::test_store_and_read_secret_roundtrip -x` | Existing | pending |
| 07-01-07 | 01 | 1 | VAULT-07 | integration | `pytest tests/test_vault.py::TestVaultCredentialIntegration -x` | Existing | pending |
| 07-01-08 | 01 | 1 | VAULT-08 | smoke | Manual: `make vault-init && cat .vault-approle` | Manual | pending |
| 07-01-09 | 01 | 1 | VAULT-09 | unit | `pytest tests/test_vault.py::TestTokenCaching -x` | W0 | pending |

*Status: pending · green · red · flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_vault.py::TestAppRoleAuth` — stubs for VAULT-01, VAULT-02
- [ ] `tests/test_vault.py::TestPolicyScoping` — stubs for VAULT-03, VAULT-04, VAULT-05
- [ ] `tests/test_vault.py::TestTokenCaching` — stubs for VAULT-09
- [ ] `tests/conftest.py` — update `_vault_token` fixture to `_vault_approle`
- [ ] `vault/policies/django.hcl` — HCL policy file for Django
- [ ] `vault/policies/orchestrator.hcl` — HCL policy file for orchestrator
- [ ] `vault/policies/mcp.hcl` — HCL policy file for MCP

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `make vault-init` creates AppRoles, policies, writes `.vault-approle` | VAULT-08 | Shell script execution in Docker, creates files on host | Run `make vault-init`, verify `.vault-approle` contains DJANGO_ROLE_ID, DJANGO_SECRET_ID, ORCHESTRATOR_ROLE_ID, ORCHESTRATOR_SECRET_ID, MCP_ROLE_ID, MCP_SECRET_ID |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

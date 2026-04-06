---
phase: 07-vault-approle-authentication-scoped-policies
verified: 2026-03-05T17:00:00Z
status: passed
score: 7/7 must-haves verified
re_verification: false
---

# Phase 7: Vault AppRole Authentication & Scoped Policies Verification Report

**Phase Goal:** Replace Vault root token authentication with production-grade AppRole authentication and least-privilege HCL policies so developers never see client secrets and each service gets only the Vault paths it needs
**Verified:** 2026-03-05T17:00:00Z
**Status:** passed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Three separate AppRole identities (Django, orchestrator, MCP) authenticate to Vault -- root token never used by application code | VERIFIED | vault-init.sh creates hazn-django, hazn-orchestrator, hazn-mcp roles (lines 99-148). vault.py uses `auth.approle.login` (line 39). VAULT_TOKEN absent from all .py settings, env files, and yml files. Only reference is a negative assertion in test_vault.py line 92-93. |
| 2 | Django AppRole can read+write at secret/agencies/*; orchestrator and MCP AppRoles are read-only | VERIFIED | django.hcl has create/read/update/delete on `secret/data/agencies/*`. orchestrator.hcl and mcp.hcl have read-only. test_vault.py TestPolicyScoping class (lines 116-206) verifies orchestrator and MCP write raises `hvac.exceptions.Forbidden`. |
| 3 | All AppRoles are explicitly denied access to sys/* and auth/* paths | VERIFIED | All 3 HCL files contain `path "sys/*" { capabilities = ["deny"] }` and `path "auth/*" { capabilities = ["deny"] }`. test_vault.py::test_sys_auth_denied (lines 194-206) verifies all 3 roles are denied on `sys.list_auth_methods()`. |
| 4 | HCL policy files are version-controlled in the repo and applied via make vault-policies | VERIFIED | 3 HCL files exist at `vault/policies/{django,orchestrator,mcp}.hcl`. Makefile has `vault-policies` target (lines 39-48) that reads HCL files and applies via Vault API. |
| 5 | make vault-init does full auto-setup: enables AppRole, creates roles, applies policies, generates Secret-IDs, writes .vault-approle | VERIFIED | vault-init.sh lines 80-161: enables AppRole auth method, iterates 3 roles, reads HCL, applies policies via API, creates AppRole roles with TTL, reads role-id, generates secret-id, writes to .vault-approle. Makefile `up` target calls vault-init. .vault-approle is gitignored. |
| 6 | Existing store_secret/read_secret helpers and get_credentials MCP tool work transparently with AppRole auth | VERIFIED | vault.py store_secret/read_secret unchanged except calling get_vault_client() which now uses AppRole. MCP hazn_memory_server.py line 40 imports read_secret, line 234 calls it in get_credentials(). Auth is transparent. TestVaultClient and TestVaultCredentialIntegration test classes exercise these helpers. |
| 7 | Token caching avoids re-login on consecutive calls; lazy re-auth handles token expiry | VERIFIED | vault.py has `_cached_client` module-level variable (line 19). get_vault_client() checks `_cached_client is not None and _cached_client.is_authenticated()` before re-login (line 35). invalidate_vault_cache() clears cache (lines 55-61). TestTokenCaching class (lines 209-226) verifies identity caching and invalidation. |

**Score:** 7/7 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `hazn_platform/vault/policies/django.hcl` | Django read+write KV v2 policy with sys/auth deny | VERIFIED | 17 lines. CRUD on secret/data/agencies/*, list/read/delete on secret/metadata/agencies/*, deny on sys/* and auth/*. |
| `hazn_platform/vault/policies/orchestrator.hcl` | Orchestrator read-only KV v2 policy with sys/auth deny | VERIFIED | 17 lines. Read on secret/data/agencies/*, list/read on secret/metadata/agencies/*, deny on sys/* and auth/*. |
| `hazn_platform/vault/policies/mcp.hcl` | MCP read-only KV v2 policy with sys/auth deny | VERIFIED | 17 lines. Identical to orchestrator with "MCP server policy" comment. |
| `hazn_platform/scripts/vault-init.sh` | Extended init script with AppRole setup | VERIFIED | 162 lines. AppRole section from line 80: enables auth method, creates 3 roles with scoped policies, generates credentials, writes .vault-approle. Bash 3.2 compatible (case statement). |
| `hazn_platform/hazn_platform/core/vault.py` | AppRole-authenticated Vault client with token caching | VERIFIED | 109 lines. auth.approle.login with settings.VAULT_ROLE_ID/SECRET_ID, _cached_client module-level cache, invalidate_vault_cache() for test isolation, store_secret/read_secret unchanged. |
| `hazn_platform/config/settings/base.py` | VAULT_ROLE_ID and VAULT_SECRET_ID settings | VERIFIED | Lines 331-333: VAULT_ADDR, VAULT_ROLE_ID, VAULT_SECRET_ID. VAULT_TOKEN completely removed. |
| `hazn_platform/docker-compose.local.yml` | .vault-approle mounted as read-only volume | VERIFIED | Line 25: `./.vault-approle:/app/.vault-approle:ro` on django service (inherited by celeryworker, celerybeat, flower via &django anchor). |
| `hazn_platform/compose/production/django/entrypoint` | AppRole credential sourcing from mounted file | VERIFIED | Lines 17-34: Reads /app/.vault-approle, uses SERVICE_ROLE env var (default DJANGO) to select per-service credentials, exports VAULT_ROLE_ID and VAULT_SECRET_ID. |
| `hazn_platform/.envs/.local/.django` | VAULT_TOKEN removed | VERIFIED | Line 18: Only VAULT_ADDR=http://vault:8200 remains. No VAULT_TOKEN. |
| `hazn_platform/Makefile` | vault-policies target | VERIFIED | Lines 39-48: vault-policies target reads HCL files and applies via Vault API using ROOT_TOKEN from .vault-keys. |
| `hazn_platform/.gitignore` | .vault-approle gitignored | VERIFIED | Lines 276-277: Both .vault-keys and .vault-approle listed with "NEVER commit" comments. |
| `hazn_platform/tests/conftest.py` | AppRole fixture replacing root token fixture | VERIFIED | 61 lines. _parse_vault_approle() helper, _vault_approle autouse fixture patching settings, vault_approle_credentials helper fixture, invalidate_vault_cache() in teardown. No VAULT_TOKEN references. |
| `hazn_platform/tests/test_vault.py` | AppRole auth, policy scoping, and token caching tests | VERIFIED | 227 lines. 5 test classes: TestVaultClient (2), TestVaultCredentialIntegration (1), TestAppRoleAuth (2), TestPolicyScoping (3), TestTokenCaching (2) = 10 tests total. Uses hvac.exceptions.Forbidden for policy negative tests. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `hazn_platform/core/vault.py` | `config/settings/base.py` | `settings.VAULT_ROLE_ID, settings.VAULT_SECRET_ID` | WIRED | vault.py line 40: `role_id=settings.VAULT_ROLE_ID`; line 41: `secret_id=settings.VAULT_SECRET_ID`. base.py lines 332-333 define both settings. |
| `compose/production/django/entrypoint` | `.vault-approle` | source mounted file | WIRED | entrypoint line 18: `APPROLE_FILE="/app/.vault-approle"`, reads file and exports VAULT_ROLE_ID/SECRET_ID. docker-compose.local.yml line 25 mounts `.vault-approle:/app/.vault-approle:ro`. |
| `scripts/vault-init.sh` | `vault/policies/*.hcl` | reads HCL files and applies to Vault | WIRED | vault-init.sh line 84: `POLICIES_DIR="vault/policies"`, line 112: `HCL_FILE="${POLICIES_DIR}/${POLICY_SLUG}.hcl"`, line 117: reads and JSON-encodes HCL content for API call. |
| `tests/conftest.py` | `.vault-approle` | reads file and patches settings | WIRED | conftest.py line 13: `approle_path = Path(...) / ".vault-approle"`, line 41: `settings.VAULT_ROLE_ID = creds["DJANGO_ROLE_ID"]`. |
| `tests/test_vault.py` | `hazn_platform/core/vault.py` | imports get_vault_client, store_secret, read_secret, invalidate_vault_cache | WIRED | test_vault.py lines 20-23: four explicit imports from hazn_platform.core.vault. |
| `tests/test_vault.py` | hvac AppRole login | direct hvac client creation for negative policy tests | WIRED | test_vault.py line 122: `client.auth.approle.login(role_id=..., secret_id=...)` in TestPolicyScoping._make_client(). |
| `mcp_servers/hazn_memory_server.py` | `hazn_platform/core/vault.py` | imports read_secret for get_credentials tool | WIRED | hazn_memory_server.py line 40: `from hazn_platform.core.vault import read_secret`, line 234: `return read_secret(credential.vault_secret_id)`. |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| VAULT-01 | 07-01, 07-02 | Services authenticate to Vault via AppRole (not root token) | SATISFIED | vault.py uses auth.approle.login; VAULT_TOKEN removed from all app code; TestAppRoleAuth::test_django_approle_login verifies. |
| VAULT-02 | 07-01, 07-02 | Django AppRole has read+write access to secret/agencies/* | SATISFIED | django.hcl grants create/read/update/delete on secret/data/agencies/*; TestAppRoleAuth::test_django_read_write verifies. |
| VAULT-03 | 07-02 | Orchestrator AppRole has read-only access to secret/agencies/* | SATISFIED | orchestrator.hcl grants read-only; TestPolicyScoping::test_orchestrator_readonly verifies read succeeds, write raises Forbidden. |
| VAULT-04 | 07-02 | MCP AppRole has read-only access to secret/agencies/* | SATISFIED | mcp.hcl grants read-only; TestPolicyScoping::test_mcp_readonly verifies read succeeds, write raises Forbidden. |
| VAULT-05 | 07-02 | All AppRoles explicitly denied on sys/* and auth/* paths | SATISFIED | All 3 HCL files have deny on sys/* and auth/*; TestPolicyScoping::test_sys_auth_denied verifies all 3 roles denied on sys.list_auth_methods(). |
| VAULT-06 | 07-01, 07-02 | store_secret/read_secret helpers work transparently with AppRole auth | SATISFIED | store_secret/read_secret unchanged, call get_vault_client() which now uses AppRole. TestVaultClient::test_store_and_read_secret_roundtrip confirms. |
| VAULT-07 | 07-02 | get_credentials MCP tool works transparently with AppRole auth | SATISFIED | hazn_memory_server.py imports read_secret from vault.py (line 40, 234). Auth change is transparent. test_mcp_memory_server.py has get_credentials tests. |
| VAULT-08 | 07-01 | make vault-init creates AppRoles, policies, and writes .vault-approle | SATISFIED | vault-init.sh enables AppRole, creates 3 roles, applies HCL policies, generates credentials, writes .vault-approle. Makefile `up` target calls vault-init. |
| VAULT-09 | 07-02 | Token caching avoids re-login; lazy re-auth handles expiry | SATISFIED | vault.py _cached_client pattern (line 35: checks is_authenticated before re-login). TestTokenCaching verifies caching (is) and invalidation (is not). |

No orphaned requirements found. All 9 VAULT-* requirements mapped to Phase 7 in REQUIREMENTS.md are claimed by plans and satisfied.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | - | - | - | - |

No anti-patterns detected. No TODO/FIXME/PLACEHOLDER/HACK comments in any phase-modified files. No empty implementations, no stub returns, no console.log-only handlers.

### Human Verification Required

### 1. make vault-init End-to-End

**Test:** Run `make up` (or `make vault-init` after services are running) and verify `.vault-approle` is created with 6 credential entries (DJANGO_ROLE_ID, DJANGO_SECRET_ID, ORCHESTRATOR_ROLE_ID, ORCHESTRATOR_SECRET_ID, MCP_ROLE_ID, MCP_SECRET_ID).
**Expected:** All 6 lines present with UUID values. No errors in output.
**Why human:** Shell script execution in Docker, creates files on host. Cannot verify without running infrastructure.

### 2. Full Test Suite in Docker

**Test:** Run `docker compose -f docker-compose.local.yml run --rm django pytest tests/test_vault.py -v` and verify all 10 tests pass.
**Expected:** 10 tests pass including policy scoping negative tests (Forbidden assertions) and token caching identity checks.
**Why human:** Requires running Vault container, Docker, and network access between containers.

### 3. Container Entrypoint Credential Loading

**Test:** After `make up`, exec into the Django container and verify VAULT_ROLE_ID and VAULT_SECRET_ID environment variables are set.
**Expected:** `docker exec hazn_platform_local_django env | grep VAULT_` shows VAULT_ADDR, VAULT_ROLE_ID, and VAULT_SECRET_ID (no VAULT_TOKEN).
**Why human:** Requires running Docker containers and inspecting runtime environment.

### Gaps Summary

No gaps found. All 7 success criteria from ROADMAP.md are verified. All 9 VAULT-* requirements are satisfied. All 13 artifacts exist, are substantive, and are wired. All key links are connected. No anti-patterns detected. The root token has been completely removed from application code, settings, and environment files, with a clean break to AppRole authentication.

---

_Verified: 2026-03-05T17:00:00Z_
_Verifier: Claude (gsd-verifier)_

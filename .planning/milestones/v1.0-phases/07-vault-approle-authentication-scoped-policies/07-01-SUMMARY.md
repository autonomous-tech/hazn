---
phase: 07-vault-approle-authentication-scoped-policies
plan: 01
subsystem: infra
tags: [vault, approle, hcl, security, docker, least-privilege]

# Dependency graph
requires:
  - phase: 01-infrastructure-foundation
    provides: Vault container, vault-init.sh, vault.py, Django settings with VAULT_TOKEN
provides:
  - 3 HCL policy files for scoped Vault access (django CRUD, orchestrator/mcp read-only)
  - AppRole auth setup in vault-init.sh with 3 roles and credential generation
  - AppRole-authenticated vault.py with lazy token caching
  - Docker entrypoint sourcing AppRole credentials from mounted file
  - vault-policies Makefile target for standalone policy application
affects: [07-vault-approle-authentication-scoped-policies]

# Tech tracking
tech-stack:
  added: []
  patterns: [AppRole authentication, HCL policy-as-code, service-scoped least-privilege, lazy token caching]

key-files:
  created:
    - hazn_platform/vault/policies/django.hcl
    - hazn_platform/vault/policies/orchestrator.hcl
    - hazn_platform/vault/policies/mcp.hcl
  modified:
    - hazn_platform/scripts/vault-init.sh
    - hazn_platform/Makefile
    - hazn_platform/.gitignore
    - hazn_platform/hazn_platform/core/vault.py
    - hazn_platform/config/settings/base.py
    - hazn_platform/docker-compose.local.yml
    - hazn_platform/compose/production/django/entrypoint
    - hazn_platform/.envs/.local/.django
    - hazn_platform/tests/conftest.py
    - hazn_platform/tests/test_vault.py

key-decisions:
  - "Clean break from root token: VAULT_TOKEN fully removed from application code, settings, and env files"
  - "SERVICE_ROLE env var in entrypoint selects per-service credentials (DJANGO default, ORCHESTRATOR, MCP)"
  - "Token caching with invalidate_vault_cache() for test isolation"

patterns-established:
  - "HCL policy-as-code: version-controlled policies in vault/policies/*.hcl reviewed in PRs"
  - "AppRole per-service identity: each service gets scoped credentials via .vault-approle mounted file"
  - "Lazy Vault token caching: get_vault_client() caches authenticated client, re-authenticates on expiry"

requirements-completed: [VAULT-01, VAULT-02, VAULT-03, VAULT-04, VAULT-05, VAULT-06, VAULT-08]

# Metrics
duration: 3min
completed: 2026-03-05
---

# Phase 7 Plan 1: Vault AppRole Infrastructure & Migration Summary

**AppRole auth with 3 scoped HCL policies (django CRUD, orchestrator/mcp read-only), vault-init.sh credential generation, and vault.py lazy token caching replacing root token**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-05T16:01:11Z
- **Completed:** 2026-03-05T16:04:35Z
- **Tasks:** 2
- **Files modified:** 13

## Accomplishments
- Created 3 HCL policy files enforcing least-privilege access (django gets CRUD, orchestrator/mcp get read-only) with explicit sys/* and auth/* deny
- Extended vault-init.sh to enable AppRole auth, create 3 roles with scoped policies, generate credentials, and write .vault-approle
- Migrated vault.py from root token to AppRole authentication with lazy token caching and cache invalidation
- Updated Docker compose/entrypoint to mount and source AppRole credentials per-service via SERVICE_ROLE selector
- Complete removal of VAULT_TOKEN from all application code, settings, and env files

## Task Commits

Each task was committed atomically:

1. **Task 1: Create HCL policies, extend vault-init.sh with AppRole setup, update Makefile** - `12467c9` (feat)
2. **Task 2: Migrate vault.py, Django settings, Docker config from root token to AppRole auth** - `1f2074d` (feat)

## Files Created/Modified
- `hazn_platform/vault/policies/django.hcl` - Django CRUD policy on secret/data/agencies/* with sys/auth deny
- `hazn_platform/vault/policies/orchestrator.hcl` - Orchestrator read-only policy with sys/auth deny
- `hazn_platform/vault/policies/mcp.hcl` - MCP read-only policy with sys/auth deny
- `hazn_platform/scripts/vault-init.sh` - Extended with AppRole auth method, 3 role creation, credential generation
- `hazn_platform/Makefile` - Added vault-policies target for standalone policy application
- `hazn_platform/.gitignore` - Added .vault-approle
- `hazn_platform/hazn_platform/core/vault.py` - AppRole-authenticated client with lazy token caching
- `hazn_platform/config/settings/base.py` - Replaced VAULT_TOKEN with VAULT_ROLE_ID + VAULT_SECRET_ID
- `hazn_platform/docker-compose.local.yml` - Added .vault-approle read-only volume mount
- `hazn_platform/compose/production/django/entrypoint` - Added AppRole credential sourcing from mounted file
- `hazn_platform/.envs/.local/.django` - Removed VAULT_TOKEN
- `hazn_platform/tests/conftest.py` - Updated to read AppRole credentials from .vault-approle
- `hazn_platform/tests/test_vault.py` - Updated docstring for AppRole auth

## Decisions Made
- Clean break from root token: VAULT_TOKEN fully removed from application code, settings, and env files. Root token only used inside vault-init.sh for initial setup.
- SERVICE_ROLE env var in entrypoint selects per-service credentials (DJANGO default, ORCHESTRATOR, MCP for future services).
- Token caching with invalidate_vault_cache() function enables test isolation.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated test fixtures for AppRole auth**
- **Found during:** Task 2 (Application code migration)
- **Issue:** Test conftest.py was patching settings.VAULT_TOKEN from .vault-keys (root token), which no longer exists in the application
- **Fix:** Updated conftest.py to read DJANGO_ROLE_ID and DJANGO_SECRET_ID from .vault-approle file; added invalidate_vault_cache() call; updated test_vault.py docstring
- **Files modified:** hazn_platform/tests/conftest.py, hazn_platform/tests/test_vault.py
- **Verification:** grep confirms no VAULT_TOKEN references remain in non-.venv code
- **Committed in:** 1f2074d (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix)
**Impact on plan:** Auto-fix necessary for test correctness after root token removal. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- AppRole infrastructure complete, ready for Plan 07-02 (integration testing)
- All 3 HCL policies are version-controlled and reviewable
- vault-init.sh generates .vault-approle automatically on `make up`
- Docker services will source per-service credentials at container startup

## Self-Check: PASSED

All 13 files verified present. Both commit hashes (12467c9, 1f2074d) confirmed in git log.

---
*Phase: 07-vault-approle-authentication-scoped-policies*
*Completed: 2026-03-05*

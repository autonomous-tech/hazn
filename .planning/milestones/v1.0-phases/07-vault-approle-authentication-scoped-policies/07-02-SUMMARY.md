---
phase: 07-vault-approle-authentication-scoped-policies
plan: 02
subsystem: testing
tags: [vault, approle, hvac, integration-tests, policy-scoping, token-caching]

# Dependency graph
requires:
  - phase: 07-vault-approle-authentication-scoped-policies
    provides: AppRole auth infrastructure, HCL policies, vault.py with token caching
provides:
  - AppRole authentication fixture in conftest.py with teardown isolation
  - vault_approle_credentials fixture exposing all 6 role credentials
  - 10 integration tests covering AppRole auth, policy scoping, and token caching
  - Verified least-privilege isolation (Django CRUD, orchestrator/MCP read-only, sys/auth denied)
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns: [pytest AppRole fixture with teardown isolation, policy scoping negative tests with hvac.exceptions.Forbidden, token cache identity assertions]

key-files:
  created: []
  modified:
    - hazn_platform/tests/conftest.py
    - hazn_platform/tests/test_vault.py
    - hazn_platform/scripts/vault-init.sh

key-decisions:
  - "Teardown isolation: invalidate_vault_cache() called after yield (not at setup) to prevent cached client leaks between tests"
  - "Shared _parse_vault_approle() helper for DRY credential parsing in both fixtures"
  - "Existing test secret paths updated from test/* to agencies/* to match AppRole policy scope"

patterns-established:
  - "AppRole test fixture pattern: autouse fixture patches Django settings from .vault-approle, yields, then invalidates cache"
  - "Policy scoping negative test pattern: create hvac client with role credentials, assert Forbidden on unauthorized operations"
  - "Token caching test pattern: identity assertions (is/is not) for object-level cache verification"

requirements-completed: [VAULT-01, VAULT-02, VAULT-03, VAULT-04, VAULT-05, VAULT-06, VAULT-07, VAULT-09]

# Metrics
duration: 9min
completed: 2026-03-05
---

# Phase 7 Plan 2: AppRole Integration Tests Summary

**10 integration tests verifying AppRole auth, policy scoping (Django CRUD, orchestrator/MCP read-only, sys/auth denied), and lazy token caching with cache invalidation**

## Performance

- **Duration:** 9 min
- **Started:** 2026-03-05T16:06:52Z
- **Completed:** 2026-03-05T16:16:00Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Updated conftest.py with proper AppRole fixture (teardown isolation via yield, shared parser, vault_approle_credentials helper)
- Added 7 new tests in 3 classes: TestAppRoleAuth (2), TestPolicyScoping (3), TestTokenCaching (2)
- Verified policy isolation: orchestrator and MCP roles raise hvac.exceptions.Forbidden on write, all roles denied on sys/auth paths
- Fixed vault-init.sh Bash 3.2 compatibility (macOS) by replacing declare -A with case statement

## Task Commits

Each task was committed atomically:

1. **Task 1: Update conftest.py with AppRole fixtures and teardown isolation** - `9880f05` (feat)
2. **Task 2: Add AppRole auth, policy scoping, and token caching tests** - `706112e` (test)

## Files Created/Modified
- `hazn_platform/tests/conftest.py` - AppRole fixtures with _parse_vault_approle(), _vault_approle (autouse), vault_approle_credentials
- `hazn_platform/tests/test_vault.py` - 10 integration tests: 3 existing (updated paths) + 2 AppRole + 3 policy scoping + 2 token caching
- `hazn_platform/scripts/vault-init.sh` - Bash 3.2 compatible role iteration (case statement instead of associative array)

## Decisions Made
- Teardown isolation: moved invalidate_vault_cache() to after yield (teardown) rather than setup for proper test isolation
- Extracted _parse_vault_approle() as shared helper to avoid duplicating file parsing logic between fixtures
- Updated existing test secret paths from test/* to agencies/* prefix to comply with AppRole policy scope

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed vault-init.sh Bash 3.2 incompatibility**
- **Found during:** Task 2 (running vault-init.sh to generate .vault-approle)
- **Issue:** `declare -A ROLES=()` associative array syntax requires Bash 4+, but macOS ships with Bash 3.2
- **Fix:** Replaced associative array with case statement for POSIX-compatible role name to env prefix mapping
- **Files modified:** hazn_platform/scripts/vault-init.sh
- **Verification:** `make vault-init` succeeds on macOS, .vault-approle file generated with all 6 credentials
- **Committed in:** 706112e (Task 2 commit)

**2. [Rule 1 - Bug] Fixed existing test paths for AppRole policy scope**
- **Found during:** Task 2 (running tests with AppRole auth)
- **Issue:** Existing tests used `test/roundtrip` and `test/vault-credential-integration` paths, which are outside the Django AppRole policy scope (`secret/data/agencies/*`)
- **Fix:** Updated paths to `agencies/test-roundtrip/creds` and `agencies/test-vault-cred-int/ga4`
- **Files modified:** hazn_platform/tests/test_vault.py
- **Verification:** All 10 tests pass with AppRole auth (no root token)
- **Committed in:** 706112e (Task 2 commit)

**3. [Rule 1 - Bug] Fixed .vault-approle created as directory by Docker**
- **Found during:** Task 2 (test execution)
- **Issue:** Docker volume mount created .vault-approle as empty directory on host when file didn't exist before `docker compose up`
- **Fix:** Removed empty directory, ran `make vault-init` to create it as a proper file, restarted Django container
- **Files modified:** None (runtime fix)
- **Verification:** .vault-approle is a regular file with 6 credential entries
- **Committed in:** N/A (runtime fix, not code change)

---

**Total deviations:** 3 auto-fixed (3 bug fixes)
**Impact on plan:** All auto-fixes necessary for AppRole auth to work correctly on macOS with Docker. No scope creep.

## Issues Encountered
- Pre-existing test failures in test_mcp_memory_server.py (11 tests) due to module import error for hazn_memory_server -- out of scope, not related to Vault changes

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 7 (Vault AppRole Authentication & Scoped Policies) is fully complete
- All AppRole infrastructure tested and verified
- Policy isolation confirmed: Django CRUD, orchestrator/MCP read-only, all roles denied sys/auth
- Token caching and invalidation verified for production and test use

## Self-Check: PASSED

All 3 modified files verified present. Both commit hashes (9880f05, 706112e) confirmed in git log.

---
*Phase: 07-vault-approle-authentication-scoped-policies*
*Completed: 2026-03-05*

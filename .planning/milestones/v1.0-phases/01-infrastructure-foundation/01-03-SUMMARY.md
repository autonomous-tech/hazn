---
phase: 01-infrastructure-foundation
plan: 03
subsystem: infra
tags: [vault, hvac, letta-client, letta-sdk, integration-tests, seed-data, management-commands, service-validation]

# Dependency graph
requires:
  - phase: 01-infrastructure-foundation (plan 01)
    provides: Docker Compose stack with Vault, Letta, Postgres, Redis
  - phase: 01-infrastructure-foundation (plan 02)
    provides: 9 Django models across core, marketing, content apps
provides:
  - Vault client helpers (get_vault_client, store_secret, read_secret) via hvac KV v2
  - Letta client factory (get_letta_client) via letta-client SDK
  - seed_dev_data management command (1 agency, 3 end-clients, brand voice, 5 keywords, vault credential, campaign, decision)
  - validate_letta management command (agent creation, archival insert/search, cleanup)
  - validate_services.sh smoke test script for all 6 Docker services
  - Integration tests for Vault (3 tests) and Letta (4 tests)
  - conftest.py with auto-patching of VAULT_TOKEN from .vault-keys
affects: [02-01, 02-02, 03-01, all-subsequent-phases]

# Tech tracking
tech-stack:
  added: [hvac-kv-v2-integration, letta-client-agents-passages-api, openai-text-embedding-ada-002]
  patterns: [vault-token-from-dotfile-fixture, letta-agent-with-explicit-embedding-config, idempotent-seed-command, service-health-check-script]

key-files:
  created:
    - hazn_platform/core/vault.py
    - hazn_platform/core/letta_client.py
    - hazn_platform/core/management/commands/seed_dev_data.py
    - hazn_platform/core/management/commands/validate_letta.py
    - scripts/validate_services.sh
    - tests/conftest.py
    - tests/test_vault.py
    - tests/test_letta.py
  modified:
    - docker-compose.local.yml
    - .envs/.local/.django
    - pyproject.toml

key-decisions:
  - "Pass OPENAI_API_KEY and ANTHROPIC_API_KEY from host to Letta container via docker-compose environment vars"
  - "Explicit embedding config (openai/text-embedding-ada-002) required for Letta agent creation and archival search"
  - "Vault root token read from .vault-keys by conftest.py fixture (auto-patches settings.VAULT_TOKEN)"
  - "Letta passages API uses create/search (not insert), search results use content field (not text)"

patterns-established:
  - "Vault integration: store_secret/read_secret round-trip pattern for all credential storage"
  - "Letta integration: get_letta_client() factory with explicit model and embedding config"
  - "Test fixtures: conftest.py reads .vault-keys and patches Django settings for integration tests"
  - "Idempotent seed: check if key entity exists before creating all seed data"

requirements-completed: [INFRA-03, INFRA-04]

# Metrics
duration: 10min
completed: 2026-03-05
---

# Phase 1 Plan 3: Vault & Letta Integration Summary

**Vault KV v2 store/read helpers and Letta SDK agent/archival operations with 7 integration tests, seed data command, and service validation script**

## Performance

- **Duration:** 10 min
- **Started:** 2026-03-05T08:47:01Z
- **Completed:** 2026-03-05T08:57:01Z
- **Tasks:** 2 (Task 1 TDD: RED + GREEN)
- **Files modified:** 11

## Accomplishments
- Vault integration works: store_secret and read_secret round-trip against running Vault via hvac KV v2
- Letta integration works: agent creation with embeddings, archival passage insert, semantic search, cleanup via letta-client SDK
- VaultCredential model stores path reference only; read_secret retrieves the actual secret from Vault
- seed_dev_data creates 1 agency, 3 end-clients, brand voice, 5 keywords, vault credential, campaign, decision (idempotent)
- validate_letta proves full Letta lifecycle: create agent, insert passage, search, delete
- validate_services.sh confirms all 6 Docker services (Postgres, Vault, Letta, Redis, Django, Next.js) are healthy
- Full test suite: 49 tests pass (19 models + 3 vault + 4 letta + 23 existing)

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: Failing tests for Vault and Letta** - `f4b3a7b` (test)
2. **Task 1 GREEN: Vault and Letta client modules with passing tests** - `a7be1cf` (feat)
3. **Task 2: Seed data command, Letta validation, service health check** - `f8d3011` (feat)

## Files Created/Modified
- `hazn_platform/core/vault.py` - Vault client helpers (get_vault_client, store_secret, read_secret)
- `hazn_platform/core/letta_client.py` - Letta client factory (get_letta_client)
- `hazn_platform/core/management/commands/seed_dev_data.py` - Idempotent seed data command
- `hazn_platform/core/management/commands/validate_letta.py` - Letta connectivity and operations validation
- `scripts/validate_services.sh` - Smoke test for all 6 Docker services
- `tests/conftest.py` - Auto-patch VAULT_TOKEN from .vault-keys
- `tests/test_vault.py` - 3 Vault integration tests
- `tests/test_letta.py` - 4 Letta integration tests
- `docker-compose.local.yml` - Added OPENAI_API_KEY/ANTHROPIC_API_KEY passthrough to Letta container
- `.envs/.local/.django` - Set actual Vault root token
- `pyproject.toml` - Registered integration pytest marker

## Decisions Made
- **LLM API key passthrough**: Used docker-compose `environment` section with `${OPENAI_API_KEY:-}` syntax to pass host API keys to Letta container. The env_file approach doesn't support shell variable expansion.
- **Explicit embedding config**: Letta requires `embedding='openai/text-embedding-ada-002'` on agent creation for archival passage embeddings and semantic search to work. Without it, passages have `embedding=None` and search returns no results.
- **Vault token fixture**: Created conftest.py fixture that reads ROOT_TOKEN from `.vault-keys` and patches `settings.VAULT_TOKEN`, avoiding the need to hardcode tokens in env files for tests.
- **Letta SDK API discovery**: The `letta-client` Python SDK uses `passages.create(text=...)` not `insert(content=...)`, and search results use `Result.content` not `Passage.text`. Verified via runtime introspection.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Letta container missing LLM API keys**
- **Found during:** Task 1 (Letta test setup)
- **Issue:** Letta container had no OPENAI_API_KEY or ANTHROPIC_API_KEY, so agent creation failed with "Must specify either model or llm_config"
- **Fix:** Added OPENAI_API_KEY and ANTHROPIC_API_KEY passthrough from host via docker-compose environment section
- **Files modified:** hazn_platform/docker-compose.local.yml
- **Verification:** Agent creation succeeds with model='openai/gpt-4o-mini'
- **Committed in:** a7be1cf (Task 1 GREEN)

**2. [Rule 1 - Bug] Letta SDK API differences from plan**
- **Found during:** Task 1 (Letta test implementation)
- **Issue:** Plan referenced `passages.insert(content=...)` but actual API is `passages.create(text=...)`. Search results use `Result.content` not `Passage.text`.
- **Fix:** Updated test code to use correct API: `passages.create(text=...)`, `results.count`, `results.results[].content`
- **Files modified:** tests/test_letta.py
- **Verification:** All 4 Letta tests pass
- **Committed in:** a7be1cf (Task 1 GREEN)

**3. [Rule 1 - Bug] Letta archival search returns no results without explicit embedding config**
- **Found during:** Task 1 (archival search test)
- **Issue:** Agent created without embedding config had `embedding=None` on passages, so semantic search returned 0 results
- **Fix:** Added `embedding='openai/text-embedding-ada-002'` to all agent creation calls
- **Files modified:** tests/test_letta.py, validate_letta.py
- **Verification:** Archival search returns matching passages
- **Committed in:** a7be1cf, f8d3011

**4. [Rule 3 - Blocking] Vault token placeholder in .django env**
- **Found during:** Task 2 (seed_dev_data)
- **Issue:** VAULT_TOKEN in .envs/.local/.django was still "placeholder-set-after-vault-init", causing seed command to fail
- **Fix:** Set actual root token from .vault-keys
- **Files modified:** .envs/.local/.django
- **Verification:** seed_dev_data runs successfully, stores test secret in Vault
- **Committed in:** f8d3011 (Task 2)

**5. [Rule 1 - Bug] validate_services.sh arithmetic causing early exit**
- **Found during:** Task 2 (service health check)
- **Issue:** `((PASS++))` returns exit code 1 when PASS goes from 0 to 1 with `set -e`, causing script to exit after first check
- **Fix:** Changed to `PASS=$((PASS + 1))` and removed `-e` flag (keeping `-uo pipefail`)
- **Files modified:** scripts/validate_services.sh
- **Verification:** Script completes all 6 checks and reports results
- **Committed in:** f8d3011 (Task 2)

---

**Total deviations:** 5 auto-fixed (2 blocking, 2 bugs, 1 API difference)
**Impact on plan:** All auto-fixes necessary for correctness. No scope creep.

## Issues Encountered
None beyond the deviations listed above.

## User Setup Required
None - all services run locally via Docker Compose. The OPENAI_API_KEY from the host environment is passed through to the Letta container automatically.

## Next Phase Readiness
- All Phase 1 success criteria are met:
  1. `docker compose up` starts all services healthy (validate_services.sh confirms 6/6)
  2. Postgres schema accepts inserts/queries (19 model tests pass, seed_dev_data creates records)
  3. Vault stores and retrieves secrets (3 vault tests pass, VaultCredential stores path only)
  4. Letta accepts agent creation and archival memory operations (4 letta tests pass, validate_letta succeeds)
- Ready for Phase 2 (Memory Layer): HaznMemory abstraction can use vault.py and letta_client.py
- Ready for Phase 3 (Orchestrator): Campaign/Decision models ready, Letta agent creation pattern established

## Self-Check: PASSED

- All 11 key files verified present on disk
- All 3 task commits (f4b3a7b, a7be1cf, f8d3011) verified in git log
- 49/49 tests pass
- Vault unsealed and authenticated
- Letta health endpoint responding
- All 6 Docker services healthy
- Seed data created: 1 agency, 3 end-clients, 1 brand voice, 5 keywords, 1 vault credential, 1 campaign, 1 decision

---
*Phase: 01-infrastructure-foundation*
*Completed: 2026-03-05*

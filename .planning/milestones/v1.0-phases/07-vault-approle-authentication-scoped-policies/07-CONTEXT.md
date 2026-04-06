# Phase 7: Vault AppRole Authentication & Scoped Policies - Context

**Gathered:** 2026-03-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Replace Vault root token authentication with production-grade AppRole authentication and least-privilege policies. Developers must never see client secrets. Services authenticate via AppRole with scoped policies. Existing `vault.py` helpers (`store_secret`, `read_secret`) and `get_credentials()` MCP tool continue working with the new auth mechanism.

</domain>

<decisions>
## Implementation Decisions

### AppRole Identity Model
- Three separate AppRole identities: Django, orchestrator, and MCP servers — each gets only the Vault paths it needs
- Core concern is **developer access isolation** — client credentials must not be visible to developers, even with codebase/env access
- Zero developer access to client secrets — only running services authenticate via AppRole
- Dev/test environments use fake/test credentials; production Secret-IDs injected by infra only
- Django gets read + write access (needed for agency onboarding flow where agencies input GA4/CMS tokens via admin)
- Orchestrator gets read-only access to credential paths
- MCP servers get their own AppRole scoped to read-only credential paths — even if compromised, can't write secrets or access non-credential paths

### Policy Scoping Strategy
- Per-service path prefix: Django read+write `secret/agencies/*`, orchestrator read `secret/agencies/*`, MCP read `secret/agencies/*`
- Explicit deny on `sys/*` and `auth/*` paths for all service AppRoles — prevents privilege escalation even on misconfiguration
- Policies defined as HCL files in the repo (version-controlled, auditable, reviewable in PRs)
- Applied via Makefile target (`make vault-policies`)

### Secret-ID Lifecycle
- Container entrypoint script pulls Secret-ID from mounted file, then authenticates with AppRole; Role-ID baked into env
- Long-lived Secret-IDs with manual rotation (no auto-expiry TTL for v1)
- `make vault-init` does full auto-setup: enables AppRole auth, creates roles, applies policies, generates Secret-IDs, writes to `.vault-approle` (gitignored)
- One command, ready to go for local dev

### Migration Approach
- Clean replace in-place — update `vault.py` to authenticate via AppRole, remove `VAULT_TOKEN` from application env vars
- Root token only used by `make vault-init` for initial Vault setup, never by application code
- Tests updated to use AppRole auth too — conftest.py sets up AppRole fixtures, catches auth issues early
- No fallback/feature flag — clean break from root token auth

### Claude's Discretion
- Exact HCL policy syntax and file organization
- AppRole role naming conventions
- Entrypoint script implementation details
- Token caching/renewal strategy within services
- conftest.py AppRole fixture implementation

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `core/vault.py`: `get_vault_client()`, `store_secret()`, `read_secret()` — need AppRole auth swap in `get_vault_client()`
- `tests/conftest.py`: Vault token fixture reads from `.vault-keys` — needs AppRole equivalent
- `tests/test_vault.py`: Integration tests for store/read — must pass with AppRole auth
- `mcp_servers/hazn_memory_server.py`: `get_credentials` tool calls `read_secret()` — transparent to auth change

### Established Patterns
- `.vault-keys` file (gitignored) stores unseal keys/root token for dev
- Makefile targets: `vault-init` handles init/unseal, extensible for AppRole setup
- Docker Compose env vars in `.envs/.local/.django` for service config
- `VAULT_ADDR` and `VAULT_TOKEN` in Django settings via django-environ

### Integration Points
- `config/settings/base.py`: Reads `VAULT_ADDR`, `VAULT_TOKEN` — needs `VAULT_ROLE_ID`, `VAULT_SECRET_ID` instead
- `docker-compose.local.yml`: Vault service config, env var injection to Django/services
- All callers of `get_vault_client()` get AppRole auth transparently

</code_context>

<specifics>
## Specific Ideas

- "The issue is that client credentials should not be visible to developers" — this is the driving requirement, not just service isolation
- Full auto-setup in Makefile for frictionless local dev experience
- HCL policy files in repo for auditability and PR review

</specifics>

<deferred>
## Deferred Ideas

- Per-agency Vault namespaces for tenant isolation — future enhancement if needed
- Auto-rotation of Secret-IDs with TTL — consider for production hardening later
- Vault audit logging integration — separate observability concern

</deferred>

---

*Phase: 07-vault-approle-authentication-scoped-policies*
*Context gathered: 2026-03-05*

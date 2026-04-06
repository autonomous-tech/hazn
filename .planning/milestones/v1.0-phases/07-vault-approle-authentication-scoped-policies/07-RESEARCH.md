# Phase 7: Vault AppRole Authentication & Scoped Policies - Research

**Researched:** 2026-03-05
**Domain:** HashiCorp Vault AppRole auth, HCL policies, hvac Python client
**Confidence:** HIGH

## Summary

This phase replaces the current root-token-based Vault authentication with production-grade AppRole authentication and least-privilege HCL policies. The existing codebase uses `hvac==2.4.0` with Vault 1.18, both of which fully support AppRole auth out of the box. The `hvac` library provides `client.auth.approle.login(role_id, secret_id)` which transparently sets the client token -- meaning the change to `vault.py` is surgical: replace `Client(url=..., token=...)` with `Client(url=...)` followed by `client.auth.approle.login(role_id, secret_id)`.

The most important technical detail is KV v2 policy paths: Vault KV v2 requires `secret/data/*` paths for read/write operations and `secret/metadata/*` for list operations. The `data/` and `metadata/` prefixes are required in HCL policies but are NOT used in the hvac API calls (hvac adds them automatically). This path duality is the single most common source of policy bugs. Explicit `deny` on `sys/*` and `auth/*` ensures no privilege escalation even if policies are misconfigured.

**Primary recommendation:** Three HCL policy files in `vault/policies/` (django.hcl, orchestrator.hcl, mcp.hcl), each granting only needed KV v2 paths with explicit sys/auth deny. `make vault-init` extended to enable AppRole, create roles, apply policies, generate Secret-IDs, and write them to `.vault-approle` (gitignored).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Three separate AppRole identities: Django, orchestrator, and MCP servers -- each gets only the Vault paths it needs
- Core concern is developer access isolation -- client credentials must not be visible to developers, even with codebase/env access
- Zero developer access to client secrets -- only running services authenticate via AppRole
- Dev/test environments use fake/test credentials; production Secret-IDs injected by infra only
- Django gets read + write access (needed for agency onboarding flow where agencies input GA4/CMS tokens via admin)
- Orchestrator gets read-only access to credential paths
- MCP servers get their own AppRole scoped to read-only credential paths
- Per-service path prefix: Django read+write `secret/agencies/*`, orchestrator read `secret/agencies/*`, MCP read `secret/agencies/*`
- Explicit deny on `sys/*` and `auth/*` paths for all service AppRoles
- Policies defined as HCL files in the repo (version-controlled, auditable, reviewable in PRs)
- Applied via Makefile target (`make vault-policies`)
- Container entrypoint script pulls Secret-ID from mounted file, then authenticates with AppRole; Role-ID baked into env
- Long-lived Secret-IDs with manual rotation (no auto-expiry TTL for v1)
- `make vault-init` does full auto-setup: enables AppRole auth, creates roles, applies policies, generates Secret-IDs, writes to `.vault-approle` (gitignored)
- Clean replace in-place -- update `vault.py` to authenticate via AppRole, remove `VAULT_TOKEN` from application env vars
- Root token only used by `make vault-init` for initial Vault setup, never by application code
- Tests updated to use AppRole auth too -- conftest.py sets up AppRole fixtures, catches auth issues early
- No fallback/feature flag -- clean break from root token auth

### Claude's Discretion
- Exact HCL policy syntax and file organization
- AppRole role naming conventions
- Entrypoint script implementation details
- Token caching/renewal strategy within services
- conftest.py AppRole fixture implementation

### Deferred Ideas (OUT OF SCOPE)
- Per-agency Vault namespaces for tenant isolation -- future enhancement if needed
- Auto-rotation of Secret-IDs with TTL -- consider for production hardening later
- Vault audit logging integration -- separate observability concern
</user_constraints>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| hvac | 2.4.0 | Python Vault client with AppRole support | Already in project; `client.auth.approle` module has full AppRole API |
| HashiCorp Vault | 1.18 | Secrets management server | Already running in docker-compose; AppRole auth method is built-in |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| (no new dependencies) | -- | -- | hvac 2.4.0 covers all AppRole operations natively |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| hvac AppRole | Vault Agent sidecar | Adds container complexity; hvac native is simpler for 3-service setup |
| HCL policy files | JSON policies | HCL is more readable, supports comments, is the Vault standard |
| File-mounted Secret-ID | Environment variable Secret-ID | Env vars visible in `docker inspect`; file mount is more secure |

**Installation:**
```bash
# No new packages needed -- hvac 2.4.0 already installed
```

## Architecture Patterns

### Recommended File Structure
```
hazn_platform/
  vault/
    config.hcl              # Existing -- Vault server config
    policies/
      django.hcl            # Django service policy (read+write agencies/*)
      orchestrator.hcl       # Orchestrator policy (read agencies/*)
      mcp.hcl               # MCP server policy (read agencies/*)
  scripts/
    vault-init.sh           # Extended -- adds AppRole setup after unseal
  .vault-keys               # Existing -- unseal key + root token (gitignored)
  .vault-approle            # NEW -- role-ids + secret-ids (gitignored)
  hazn_platform/
    core/
      vault.py              # Modified -- AppRole auth instead of root token
  tests/
    conftest.py             # Modified -- AppRole fixture instead of root token
    test_vault.py           # Extended -- AppRole auth + policy scoping tests
```

### Pattern 1: AppRole Login in hvac
**What:** Create an unauthenticated hvac Client, then call `client.auth.approle.login()` which sets the client token automatically.
**When to use:** Every time `get_vault_client()` is called.
**Example:**
```python
# Source: hvac 2.4.0 approle.py (verified from installed package)
import hvac
from django.conf import settings

def get_vault_client() -> hvac.Client:
    """Return an AppRole-authenticated Vault client."""
    client = hvac.Client(url=settings.VAULT_ADDR)
    # login() sets client.token automatically when use_token=True (default)
    client.auth.approle.login(
        role_id=settings.VAULT_ROLE_ID,
        secret_id=settings.VAULT_SECRET_ID,
    )
    if not client.is_authenticated():
        raise RuntimeError(
            "Vault AppRole authentication failed. "
            "Check VAULT_ROLE_ID and VAULT_SECRET_ID."
        )
    return client
```

### Pattern 2: KV v2 HCL Policy with Explicit Deny
**What:** Grant KV v2 access on `secret/data/` and `secret/metadata/` paths, deny `sys/*` and `auth/*`.
**When to use:** For every service AppRole policy.
**Example:**
```hcl
# Source: https://developer.hashicorp.com/vault/docs/concepts/policies
# Django policy -- read + write on agency credentials
path "secret/data/agencies/*" {
  capabilities = ["create", "read", "update", "delete"]
}

path "secret/metadata/agencies/*" {
  capabilities = ["list", "read"]
}

# Explicit deny on admin paths -- prevents privilege escalation
path "sys/*" {
  capabilities = ["deny"]
}

path "auth/*" {
  capabilities = ["deny"]
}
```

### Pattern 3: Token Caching with Lazy Renewal
**What:** Cache the authenticated hvac Client in a module-level variable. Re-authenticate only when `is_authenticated()` returns False (token expired).
**When to use:** Within long-running service processes (Django, celery workers) to avoid AppRole login on every request.
**Example:**
```python
import hvac
from django.conf import settings

_cached_client: hvac.Client | None = None

def get_vault_client() -> hvac.Client:
    """Return a cached, AppRole-authenticated Vault client.

    Re-authenticates if the cached token has expired.
    """
    global _cached_client
    if _cached_client is not None and _cached_client.is_authenticated():
        return _cached_client

    client = hvac.Client(url=settings.VAULT_ADDR)
    client.auth.approle.login(
        role_id=settings.VAULT_ROLE_ID,
        secret_id=settings.VAULT_SECRET_ID,
    )
    if not client.is_authenticated():
        raise RuntimeError("Vault AppRole authentication failed.")
    _cached_client = client
    return _cached_client
```

### Pattern 4: vault-init.sh AppRole Setup via Vault HTTP API
**What:** Extend the existing `vault-init.sh` to enable AppRole auth, create policies, create roles, generate secret-ids using `curl` against the Vault HTTP API.
**When to use:** In the `make vault-init` target.
**Example:**
```bash
# Enable AppRole auth method (idempotent)
curl -sf -X POST "${VAULT_ADDR}/v1/sys/auth/approle" \
  -H "X-Vault-Token: ${ROOT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"type": "approle"}' 2>/dev/null || true

# Apply policy from HCL file
POLICY_CONTENT=$(cat vault/policies/django.hcl)
curl -sf -X PUT "${VAULT_ADDR}/v1/sys/policy/hazn-django" \
  -H "X-Vault-Token: ${ROOT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"policy\": $(echo "$POLICY_CONTENT" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')}"

# Create AppRole role with policy
curl -sf -X POST "${VAULT_ADDR}/v1/auth/approle/role/hazn-django" \
  -H "X-Vault-Token: ${ROOT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"token_policies": ["hazn-django"], "token_ttl": "1h", "token_max_ttl": "4h", "secret_id_num_uses": 0, "token_num_uses": 0}'

# Read Role-ID
ROLE_ID=$(curl -sf "${VAULT_ADDR}/v1/auth/approle/role/hazn-django/role-id" \
  -H "X-Vault-Token: ${ROOT_TOKEN}" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['role_id'])")

# Generate Secret-ID
SECRET_ID=$(curl -sf -X POST "${VAULT_ADDR}/v1/auth/approle/role/hazn-django/secret-id" \
  -H "X-Vault-Token: ${ROOT_TOKEN}" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['secret_id'])")

echo "DJANGO_ROLE_ID=${ROLE_ID}" >> .vault-approle
echo "DJANGO_SECRET_ID=${SECRET_ID}" >> .vault-approle
```

### Anti-Patterns to Avoid
- **Hardcoding root token in application code:** Root token should ONLY appear in vault-init.sh for setup. Never in Django settings, env files read by services, or test fixtures.
- **Using `secret/agencies/*` in HCL policies without `data/` prefix:** KV v2 requires `secret/data/agencies/*` for read/write and `secret/metadata/agencies/*` for list. The `data/` prefix is the #1 source of "permission denied" bugs.
- **Creating a single shared AppRole for all services:** Defeats the purpose of least-privilege isolation. Three separate roles are mandatory per locked decisions.
- **Putting Secret-ID in environment variables directly:** Use file mount (`.vault-approle`) read by entrypoint script. Env vars are visible via `docker inspect`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| AppRole login flow | Custom HTTP calls to Vault | `hvac.Client.auth.approle.login()` | Handles token parsing, error codes, token caching internally |
| Policy application | Manual curl in scattered scripts | HCL files + Makefile target | Version controlled, reviewable, idempotent |
| Token renewal | Custom TTL tracking + re-login timer | `is_authenticated()` check + lazy re-login | hvac's `is_authenticated()` checks token validity server-side |
| Secret-ID generation | UUID generation | Vault's `generate_secret_id` API | Vault tracks accessor, metadata, and usage; custom UUIDs bypass this |

**Key insight:** hvac 2.4.0 has full AppRole support including `login()`, `create_or_update_approle()`, `generate_secret_id()`, and `read_role_id()`. There is zero reason to use raw HTTP calls in Python code -- only the bash init script needs curl.

## Common Pitfalls

### Pitfall 1: KV v2 Policy Path Confusion
**What goes wrong:** Policies use `secret/agencies/*` but KV v2 requires `secret/data/agencies/*` for data operations. Services get "permission denied" on every read/write.
**Why it happens:** hvac's `read_secret_version(path="agencies/foo", mount_point="secret")` translates to API path `/v1/secret/data/agencies/foo`. The `data/` segment is added by hvac, but ACL policies must include it.
**How to avoid:** Always use `secret/data/agencies/*` for read/write policies and `secret/metadata/agencies/*` for list policies. Never use `secret/agencies/*` directly.
**Warning signs:** "permission denied" errors on operations that worked with root token.

### Pitfall 2: Forgetting metadata/ Path for List Operations
**What goes wrong:** Django admin's agency onboarding can't list existing credentials because the policy only grants `secret/data/*` access.
**Why it happens:** KV v2 list operations go to `secret/metadata/` path, not `secret/data/`.
**How to avoid:** Every policy that needs list access must include a `secret/metadata/` path rule with `["list", "read"]` capabilities.
**Warning signs:** `store_secret` works but listing paths returns 403.

### Pitfall 3: AppRole Login Creates New Token Every Call
**What goes wrong:** Every `get_vault_client()` call does a fresh AppRole login, creating a new Vault token. Under load, this causes token proliferation and potential Vault performance issues.
**Why it happens:** No token caching in the client.
**How to avoid:** Cache the hvac Client at module level. Check `is_authenticated()` before re-authenticating. Re-login only when the token expires.
**Warning signs:** Vault audit log shows thousands of `auth/approle/login` entries.

### Pitfall 4: Secret-ID in .vault-approle Not Sourced by Docker Compose
**What goes wrong:** `vault-init.sh` writes Secret-IDs to `.vault-approle`, but Docker Compose env_file only reads `.envs/.local/.django`. Services start without credentials.
**Why it happens:** Docker Compose env_file is set at compose-up time, but `.vault-approle` is created after `make vault-init` runs.
**How to avoid:** Either: (a) Add `.vault-approle` as an additional `env_file` in docker-compose.local.yml (services will restart after vault-init), or (b) Mount `.vault-approle` as a file volume and have the entrypoint script source it. Option (b) aligns with the locked decision of "entrypoint script pulls Secret-ID from mounted file."
**Warning signs:** Services can't authenticate to Vault after `make up`.

### Pitfall 5: Tests Break Because conftest.py Still Reads Root Token
**What goes wrong:** Existing `conftest.py` reads `ROOT_TOKEN` from `.vault-keys`. After migration, tests need AppRole credentials.
**Why it happens:** Clean break means no fallback to root token.
**How to avoid:** Update `conftest.py` to read from `.vault-approle` and authenticate via AppRole. The test AppRole (likely django role) needs to cover all test operations.
**Warning signs:** All `@pytest.mark.integration` Vault tests fail with auth errors.

### Pitfall 6: Deny Policy on auth/* Blocks AppRole Login Itself
**What goes wrong:** If the deny on `auth/*` is applied too broadly, the service's own AppRole login call might be blocked.
**Why it happens:** Confusion about when deny applies -- it applies to the token's capabilities AFTER login, not during the login process itself.
**How to avoid:** AppRole login (`POST /v1/auth/approle/login`) is unauthenticated -- it doesn't use a token, so policies don't apply to it. The deny on `auth/*` only prevents the RESULTING token from managing auth methods. This is safe.
**Warning signs:** None -- this is a misconception, not an actual failure. Document it to prevent unnecessary debugging.

## Code Examples

### Verified: hvac AppRole Login (from installed hvac 2.4.0)
```python
# Source: hvac/api/auth_methods/approle.py line 481-510 (verified from installed package)
# login() signature: login(role_id, secret_id=None, use_token=True, mount_point='approle')
# When use_token=True (default), sets client.token from login response automatically.

client = hvac.Client(url="http://vault:8200")
response = client.auth.approle.login(
    role_id="db02de05-fa39-4855-059b-67221c5c2f63",
    secret_id="6a174c20-f6de-a53c-74d2-6018fcceff64",
)
# response contains auth.client_token, auth.lease_duration, auth.policies
# client.token is now set to the AppRole token
assert client.is_authenticated()
```

### Verified: hvac AppRole Role Creation (from installed hvac 2.4.0)
```python
# Source: hvac/api/auth_methods/approle.py line 15-129 (verified from installed package)
# create_or_update_approle() sets up the role with policies and token config

root_client = hvac.Client(url="http://vault:8200", token=root_token)
root_client.auth.approle.create_or_update_approle(
    role_name="hazn-django",
    token_policies=["hazn-django"],
    token_ttl="1h",
    token_max_ttl="4h",
    secret_id_num_uses=0,  # unlimited
    token_num_uses=0,       # unlimited
)

# Read the auto-generated role-id
role_id_response = root_client.auth.approle.read_role_id("hazn-django")
role_id = role_id_response["data"]["role_id"]

# Generate a secret-id
secret_id_response = root_client.auth.approle.generate_secret_id("hazn-django")
secret_id = secret_id_response["data"]["secret_id"]
```

### Verified: KV v2 Policy for Read-Only Access
```hcl
# Source: https://developer.hashicorp.com/vault/docs/concepts/policies
# Orchestrator/MCP policy -- read-only on agency credentials

# Read secrets
path "secret/data/agencies/*" {
  capabilities = ["read"]
}

# List credential paths
path "secret/metadata/agencies/*" {
  capabilities = ["list", "read"]
}

# Explicit deny on admin paths
path "sys/*" {
  capabilities = ["deny"]
}

path "auth/*" {
  capabilities = ["deny"]
}
```

### Verified: KV v2 Policy for Read+Write Access
```hcl
# Django policy -- read+write for agency onboarding

# Full CRUD on secrets
path "secret/data/agencies/*" {
  capabilities = ["create", "read", "update", "delete"]
}

# List and read metadata
path "secret/metadata/agencies/*" {
  capabilities = ["list", "read", "delete"]
}

# Explicit deny on admin paths
path "sys/*" {
  capabilities = ["deny"]
}

path "auth/*" {
  capabilities = ["deny"]
}
```

### Updated vault.py (Complete)
```python
"""Vault client helpers with AppRole authentication.

Uses hvac with AppRole auth to communicate with HashiCorp Vault's
KV v2 secrets engine. Connection details from Django settings:

* ``VAULT_ADDR``      -- Vault server URL
* ``VAULT_ROLE_ID``   -- AppRole Role ID for this service
* ``VAULT_SECRET_ID`` -- AppRole Secret ID for this service
"""

import hvac
from django.conf import settings

_cached_client: hvac.Client | None = None


def get_vault_client() -> hvac.Client:
    """Return a cached, AppRole-authenticated Vault client.

    Re-authenticates when the cached token expires.
    """
    global _cached_client
    if _cached_client is not None and _cached_client.is_authenticated():
        return _cached_client

    client = hvac.Client(url=settings.VAULT_ADDR)
    client.auth.approle.login(
        role_id=settings.VAULT_ROLE_ID,
        secret_id=settings.VAULT_SECRET_ID,
    )
    if not client.is_authenticated():
        raise RuntimeError(
            "Vault AppRole authentication failed. "
            "Check VAULT_ROLE_ID and VAULT_SECRET_ID in Django settings."
        )
    _cached_client = client
    return _cached_client


def store_secret(path: str, data: dict) -> str:
    """Store a secret in Vault KV v2 and return the path."""
    client = get_vault_client()
    client.secrets.kv.v2.create_or_update_secret(
        path=path,
        secret=data,
        mount_point="secret",
    )
    return path


def read_secret(path: str) -> dict:
    """Read a secret from Vault KV v2."""
    client = get_vault_client()
    response = client.secrets.kv.v2.read_secret_version(
        path=path,
        mount_point="secret",
        raise_on_deleted_version=True,
    )
    return response["data"]["data"]
```

### Updated conftest.py AppRole Fixture
```python
"""Shared test fixtures with AppRole authentication."""

from pathlib import Path
import pytest


@pytest.fixture(autouse=True)
def _vault_approle(settings):
    """Read AppRole credentials from .vault-approle and patch Django settings.

    The .vault-approle file is created by scripts/vault-init.sh.
    Format:
        DJANGO_ROLE_ID=...
        DJANGO_SECRET_ID=...
        ORCHESTRATOR_ROLE_ID=...
        ...
    """
    approle_path = Path(__file__).resolve().parent.parent / ".vault-approle"
    if approle_path.exists():
        data = {}
        for line in approle_path.read_text().strip().splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                data[key.strip()] = value.strip()
        # Tests use Django role (has broadest access for test operations)
        settings.VAULT_ROLE_ID = data.get("DJANGO_ROLE_ID", "")
        settings.VAULT_SECRET_ID = data.get("DJANGO_SECRET_ID", "")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Root token in env vars | AppRole per-service auth | This phase | Eliminates developer access to production secrets |
| Single VAULT_TOKEN setting | VAULT_ROLE_ID + VAULT_SECRET_ID per service | This phase | Each service gets scoped permissions |
| No Vault policies | HCL policies in repo | This phase | Auditable, reviewable access control |

**Deprecated/outdated:**
- `VAULT_TOKEN` Django setting: Replaced by `VAULT_ROLE_ID` + `VAULT_SECRET_ID`
- `.vault-keys` ROOT_TOKEN usage in application code: Only used by vault-init.sh
- conftest.py `_vault_token` fixture: Replaced by `_vault_approle`

## Open Questions

1. **Token TTL for long-running services**
   - What we know: Django/Celery processes can run for hours. Default token TTL is 768h (32 days) in Vault, but we're setting 1h/4h max.
   - What's unclear: Whether 1h token_ttl with 4h token_max_ttl is right, or if longer TTLs reduce re-auth chatter without security risk.
   - Recommendation: Start with `token_ttl=1h, token_max_ttl=4h`. The lazy re-auth in `get_vault_client()` handles expiry transparently. Tune based on observed re-auth frequency.

2. **Test isolation between AppRole identities**
   - What we know: Tests use Django's AppRole (broadest access). Tests for policy scoping need to verify that orchestrator/MCP roles CAN'T write.
   - What's unclear: Whether to add separate test AppRoles or test policy enforcement via negative tests with the actual orchestrator role.
   - Recommendation: Add dedicated negative tests that login with orchestrator/MCP roles and verify write operations are denied. This validates policy correctness.

3. **Entrypoint script vs env_file for Secret-ID injection**
   - What we know: Locked decision says "entrypoint script pulls Secret-ID from mounted file." Current entrypoint only handles Postgres wait.
   - What's unclear: Exact mechanics -- source the file in entrypoint, or export vars?
   - Recommendation: Mount `.vault-approle` as read-only volume in docker-compose. Entrypoint sources it and exports the service-specific vars before `exec "$@"`.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (via pyproject.toml) |
| Config file | `hazn_platform/pyproject.toml [tool.pytest.ini_options]` |
| Quick run command | `docker compose -f docker-compose.local.yml run --rm django pytest tests/test_vault.py -x` |
| Full suite command | `docker compose -f docker-compose.local.yml run --rm django pytest` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| VAULT-01 | Django authenticates via AppRole (not root token) | integration | `pytest tests/test_vault.py::TestAppRoleAuth::test_django_approle_login -x` | Wave 0 |
| VAULT-02 | Django can read+write to `secret/agencies/*` | integration | `pytest tests/test_vault.py::TestAppRoleAuth::test_django_read_write -x` | Wave 0 |
| VAULT-03 | Orchestrator AppRole is read-only on `secret/agencies/*` | integration | `pytest tests/test_vault.py::TestPolicyScoping::test_orchestrator_readonly -x` | Wave 0 |
| VAULT-04 | MCP AppRole is read-only on `secret/agencies/*` | integration | `pytest tests/test_vault.py::TestPolicyScoping::test_mcp_readonly -x` | Wave 0 |
| VAULT-05 | All AppRoles denied on `sys/*` and `auth/*` | integration | `pytest tests/test_vault.py::TestPolicyScoping::test_sys_auth_denied -x` | Wave 0 |
| VAULT-06 | `store_secret`/`read_secret` work with AppRole auth | integration | `pytest tests/test_vault.py::TestVaultClient::test_store_and_read_secret_roundtrip -x` | Existing (needs update) |
| VAULT-07 | `get_credentials` MCP tool works with AppRole auth | integration | `pytest tests/test_vault.py::TestVaultCredentialIntegration -x` | Existing (needs update) |
| VAULT-08 | `make vault-init` creates AppRoles, policies, writes `.vault-approle` | smoke | Manual: `make vault-init && cat .vault-approle` | Manual-only (shell script) |
| VAULT-09 | Token caching avoids re-login on consecutive calls | unit | `pytest tests/test_vault.py::TestTokenCaching -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `docker compose -f docker-compose.local.yml run --rm django pytest tests/test_vault.py -x`
- **Per wave merge:** `docker compose -f docker-compose.local.yml run --rm django pytest`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_vault.py::TestAppRoleAuth` -- new test class for AppRole login verification
- [ ] `tests/test_vault.py::TestPolicyScoping` -- negative tests for read-only and deny policies
- [ ] `tests/test_vault.py::TestTokenCaching` -- unit test for client caching behavior
- [ ] `tests/conftest.py` -- update `_vault_token` fixture to `_vault_approle` reading from `.vault-approle`
- [ ] `vault/policies/django.hcl` -- HCL policy file
- [ ] `vault/policies/orchestrator.hcl` -- HCL policy file
- [ ] `vault/policies/mcp.hcl` -- HCL policy file

## Sources

### Primary (HIGH confidence)
- hvac 2.4.0 installed package (`hvac/api/auth_methods/approle.py`) -- verified AppRole login signature, role creation, secret-id generation methods directly from source code
- HashiCorp Vault 1.18 Docker image (already in docker-compose.local.yml) -- confirmed AppRole auth method support
- Existing codebase: `vault.py`, `conftest.py`, `test_vault.py`, `vault-init.sh`, `docker-compose.local.yml`, `base.py` settings -- verified current implementation

### Secondary (MEDIUM confidence)
- [Vault Policies docs](https://developer.hashicorp.com/vault/docs/concepts/policies) -- HCL syntax, deny capability, glob patterns, KV v2 path structure
- [Vault AppRole docs](https://developer.hashicorp.com/vault/docs/auth/approle) -- Enable, role creation, secret-id generation, login flow
- [Vault KV v2 setup docs](https://developer.hashicorp.com/vault/docs/secrets/kv/kv-v2/setup) -- ACL path prefixes (data/, metadata/, undelete/, destroy/)

### Tertiary (LOW confidence)
- None -- all findings verified against installed code or official docs.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- hvac 2.4.0 verified installed, AppRole API methods confirmed from source code
- Architecture: HIGH -- pattern is straightforward (replace token auth with AppRole login in get_vault_client), KV v2 path rules verified from official docs
- Pitfalls: HIGH -- KV v2 data/ prefix issue is extensively documented; token caching pattern is standard hvac usage
- Policy syntax: HIGH -- verified from official Vault docs with specific KV v2 path requirements

**Research date:** 2026-03-05
**Valid until:** 2026-04-05 (stable -- Vault 1.18 and hvac 2.4.0 are mature)

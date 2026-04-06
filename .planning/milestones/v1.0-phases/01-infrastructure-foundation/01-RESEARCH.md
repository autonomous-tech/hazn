# Phase 1: Infrastructure Foundation - Research

**Researched:** 2026-03-05
**Domain:** Docker Compose orchestration, Django, Postgres 17 + pgvector, Letta (self-hosted), HashiCorp Vault, Redis
**Confidence:** HIGH

## Summary

Phase 1 stands up the full service stack via Docker Compose: a Cookiecutter Django backend, a Next.js frontend, Postgres 17 with pgvector (shared instance, separate databases for Django and Letta), a self-hosted Letta server, HashiCorp Vault (production-like with file backend), Redis (for Celery), and Traefik (reverse proxy). Langfuse is external -- only connection config is needed.

The key integration challenge is the shared Postgres instance: one container running `pgvector/pgvector:pg17` must host two databases (one for Django, one for Letta), with pgvector enabled in both. A Docker entrypoint init script creates the second database on first boot. Vault requires a deliberate init/unseal workflow -- the user specifically wants production-like behavior (not dev mode), so we need a bash script that initializes, stores unseal keys to a gitignored file, and auto-unseals on subsequent startups.

**Primary recommendation:** Use `pgvector/pgvector:pg17` as the single Postgres image (replaces both cookiecutter's default Postgres and Letta's `ankane/pgvector`), add a `/docker-entrypoint-initdb.d/` script to create the `letta` database, and configure Letta server with `LETTA_PG_URI` pointing to the same container. Use `hashicorp/vault:1.18` with file backend and a custom auto-unseal entrypoint script.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Cookiecutter Django as the backend framework
- Enable all optional integrations: Celery + Redis, DRF, Whitenoise, Sentry
- Next.js as the frontend, also Dockerized in the Compose stack
- Single Postgres 17 instance shared between Hazn app and Letta (separate databases on the same container)
- pgvector extension added to the Django Postgres database
- Letta gets its own database (e.g., `letta`) alongside Django's database
- Strict 1:many relationship: each end-client (L3) belongs to exactly one agency (L2)
- Hard deletes in v1 -- retention/GDPR compliance deferred to Phase 5
- Metering tables (workflow_runs, workflow_agents, workflow_tool_calls) deferred to Phase 3/4 when orchestrator is built
- Phase 1 schema covers the 9 L2/L3 tables: agencies, end_clients, keywords, audits, campaigns, decisions, approved_copy, brand_voice, vault_credentials
- Production-like Vault from day 1: file backend, proper init/unseal sequence
- Auto-unseal script stores keys in `.vault-keys` (gitignored) and auto-unseals on container startup
- Not dev mode -- real Vault behavior from the start
- Langfuse already deployed on personal cloud infrastructure -- not included in Docker Compose stack
- Phase 1 only needs connection configuration for Langfuse (API keys, base URL as env vars)
- Traefik included in Compose stack (from Cookiecutter Django)
- Seed data script via Django management command (`manage.py seed_dev_data`): test agency, 2-3 end-clients with brand voice, sample keywords, test Vault secret
- Makefile extended from Cookiecutter Django default: `make up`, `make down`, `make seed`, `make reset-db`, `make vault-init`, `make test`
- Volume mount for Django source code -- hot reload via Django dev server
- Next.js also volume-mounted for hot reload in dev

### Claude's Discretion
- Django app organization (single app vs. domain-split apps for the 9 tables)
- pgvector integration approach (django-pgvector vs. hybrid SQL)
- Brand voice and approved_copy versioning strategy
- Migration strategy for pgvector-specific operations
- Port assignments, health check configuration, volume naming

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INFRA-01 | Platform runs via Docker Compose with Postgres, Letta, Vault, Redis, and Langfuse services | Cookiecutter Django generates docker-compose.local.yml with Postgres, Redis, Celery, Traefik. Extend with Letta, Vault, Next.js services. Langfuse is external (env vars only). |
| INFRA-02 | Postgres 17 + pgvector schema supports all L2/L3 data (agencies, end_clients, keywords, audits, campaigns, decisions, approved_copy, brand_voice, vault_credentials) | Use `pgvector/pgvector:pg17` image. Django models with `pgvector` Python package for VectorField. 9 tables defined as Django models with migrations. |
| INFRA-03 | HashiCorp Vault stores all secrets; Postgres stores vault_secret_id references only | `hashicorp/vault:1.18` with file backend, `hvac` Python client (v2.4.0) for KV v2 read/write. vault_credentials table stores only `vault_secret_id` (VARCHAR path reference). |
| INFRA-04 | Letta runs self-hosted via Docker with persistent storage | `letta/letta:latest` connected to shared Postgres via `LETTA_PG_URI`. Letta Python SDK `letta-client` v1.7.11 for agent creation and archival memory ops. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Django | 5.2 | Backend framework | Cookiecutter Django generates production-ready project with all integrations |
| Django REST Framework | 3.15+ | API layer | Selected during cookiecutter generation (`use_drf=y`) |
| Celery | 5.4+ | Async task queue | Selected during cookiecutter generation (`use_celery=y`) |
| PostgreSQL | 17 (via pgvector/pgvector:pg17) | Primary database | User decision; image includes pgvector pre-installed |
| pgvector | 0.8.0 (extension) | Vector similarity search | Pre-installed in `pgvector/pgvector:pg17` Docker image |
| Redis | 7+ | Celery broker + cache | Cookiecutter Django default broker for Celery |
| HashiCorp Vault | 1.18 | Secrets management | User decision; production-like from day 1 |
| Letta Server | latest (Docker) | Agent memory platform | User decision; self-hosted via Docker |
| Traefik | 3.x | Reverse proxy | Included by Cookiecutter Django for production; used in local too |
| Next.js | 15+ | Frontend framework | User decision; Dockerized in Compose stack |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pgvector (Python) | 0.3+ | Django VectorField + distance ops | Defining vector columns in Django models |
| hvac | 2.4.0 | Python Vault client | All Vault read/write operations from Django |
| letta-client | 1.7.11 | Letta Python SDK | Agent creation, memory block ops, archival memory |
| Whitenoise | 6.7+ | Static file serving | Selected during cookiecutter generation |
| Sentry SDK | 2.x | Error tracking | Selected during cookiecutter generation |
| django-environ | 0.11+ | Environment config | Cookiecutter Django default for settings |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pgvector/pgvector:pg17 | postgres:17 + manual pgvector install | Extra Dockerfile complexity; pgvector/pgvector is the official pre-built image |
| hvac | django-vault-helpers | hvac is lower-level but more flexible and better maintained (2.4.0, Oct 2025) |
| Single Postgres container | Separate Postgres for Django and Letta | User explicitly chose shared instance with separate databases to reduce resource overhead |

**Installation (Python):**
```bash
pip install pgvector hvac letta-client
```

**Installation (npm -- for Next.js frontend):**
```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir
```

## Architecture Patterns

### Recommended Project Structure (Cookiecutter Django Output)
```
hazn-platform/                       # Repository root
├── config/                          # Django configuration root
│   ├── settings/
│   │   ├── base.py                  # Shared settings
│   │   ├── local.py                 # Local dev overrides
│   │   └── production.py            # Production settings
│   ├── urls.py
│   └── wsgi.py
├── hazn/                            # Django project root (slug from cookiecutter)
│   ├── users/                       # Cookiecutter default user app
│   ├── core/                        # Core models: agencies, end_clients, vault_credentials
│   ├── marketing/                   # Marketing models: keywords, audits, campaigns, decisions
│   ├── content/                     # Content models: approved_copy, brand_voice
│   └── conftest.py
├── frontend/                        # Next.js app (Dockerized)
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── compose/                         # Docker build contexts (cookiecutter pattern)
│   ├── local/
│   │   ├── django/Dockerfile
│   │   └── node/Dockerfile          # Next.js Dockerfile
│   └── production/
│       ├── django/Dockerfile
│       ├── postgres/Dockerfile       # REPLACED: we use pgvector/pgvector:pg17 directly
│       └── traefik/
├── docker-compose.local.yml         # Local dev compose (primary)
├── docker-compose.production.yml    # Production compose
├── .envs/
│   ├── .local/
│   │   ├── .django
│   │   ├── .postgres
│   │   ├── .vault                   # Vault env vars
│   │   └── .letta                   # Letta env vars
│   └── .production/
├── scripts/
│   ├── vault-init.sh                # Auto-init + unseal script
│   └── create-letta-db.sql          # Init script for /docker-entrypoint-initdb.d/
├── vault/
│   └── config.hcl                   # Vault server config (file backend)
├── requirements/
│   ├── base.txt
│   ├── local.txt
│   └── production.txt
├── Makefile
├── .vault-keys                      # Gitignored: unseal keys + root token
└── .gitignore
```

### Discretion: Django App Organization (RECOMMENDATION: Domain-Split)

Use 3 Django apps to organize the 9 tables by domain:

| App | Models | Rationale |
|-----|--------|-----------|
| `core` | Agency, EndClient, VaultCredential | Identity + auth-adjacent models; VaultCredential references live here because they are scoped per L2/L3 |
| `marketing` | Keyword, Audit, Campaign, Decision | Campaign execution domain; all relate to marketing workflows |
| `content` | ApprovedCopy, BrandVoice | Content artifacts with potential versioning needs |

**Why 3 apps, not 1:** The 9 tables span 3 distinct domains. Domain-split keeps migrations isolated (content schema changes don't touch marketing migrations), allows independent testing, and matches the L2/L3 mental model. A single app would become unwieldy as Phase 2+ adds more models.

**Why not 9 apps (1 per model):** Over-fragmented; Django apps with a single model add boilerplate without benefit.

### Discretion: pgvector Integration (RECOMMENDATION: pgvector Python package)

Use the `pgvector` Python package with Django's `VectorField`:

```python
# In a Django migration:
from pgvector.django import VectorExtension

class Migration(migrations.Migration):
    operations = [
        VectorExtension(),  # CREATE EXTENSION IF NOT EXISTS vector
        # ... then CreateModel operations
    ]
```

```python
# In models:
from pgvector.django import VectorField

class BrandVoice(models.Model):
    client = models.ForeignKey(EndClient, on_delete=models.CASCADE)
    content = models.TextField()
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Why not raw SQL:** The `pgvector` Python package provides Django-native field types, distance functions (`CosineDistance`, `L2Distance`), and index classes (`HnswIndex`). It integrates cleanly with Django ORM queries and migrations.

### Discretion: Versioning Strategy (RECOMMENDATION: Append-Only with version field)

For `brand_voice` and `approved_copy`, use append-only versioning:

```python
class BrandVoice(models.Model):
    client = models.ForeignKey(EndClient, on_delete=models.CASCADE)
    content = models.TextField()
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['client', 'is_active'],
                condition=models.Q(is_active=True),
                name='unique_active_brand_voice_per_client'
            )
        ]
```

New versions are new rows. Only one row per client has `is_active=True`. This enables full history without complexity of temporal tables.

### Pattern: Shared Postgres with Separate Databases

**What:** Single `pgvector/pgvector:pg17` container hosts both `hazn` (Django) and `letta` (Letta server) databases.
**When to use:** This exact phase -- it is a locked decision.
**How:**

1. The Postgres container's primary database is `hazn` (Django's database)
2. A SQL init script at `/docker-entrypoint-initdb.d/create-letta-db.sql` creates the `letta` database on first boot:

```sql
-- scripts/create-letta-db.sql
-- Mounted to /docker-entrypoint-initdb.d/ in docker-compose
CREATE DATABASE letta;
GRANT ALL PRIVILEGES ON DATABASE letta TO hazn_user;
-- pgvector extension must be enabled per-database
\c letta
CREATE EXTENSION IF NOT EXISTS vector;
```

3. Letta server connects via `LETTA_PG_URI=postgresql://hazn_user:password@postgres:5432/letta`
4. Django connects via standard `DATABASE_URL=postgresql://hazn_user:password@postgres:5432/hazn`

### Pattern: Vault Auto-Unseal Script

**What:** Bash script that handles first-time init and subsequent auto-unseal.
**When to use:** Every `docker compose up` / `make up`.
**How:**

```bash
#!/usr/bin/env bash
# scripts/vault-init.sh
# Waits for Vault, initializes if needed, unseals, stores keys in .vault-keys

VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
KEYS_FILE=".vault-keys"

# Wait for Vault to be reachable
until curl -sf "${VAULT_ADDR}/v1/sys/health" -o /dev/null 2>&1 || \
      curl -sf "${VAULT_ADDR}/v1/sys/seal-status" -o /dev/null 2>&1; do
  echo "Waiting for Vault..."
  sleep 2
done

# Check if already initialized
INIT_STATUS=$(curl -sf "${VAULT_ADDR}/v1/sys/init" | python3 -c "import sys,json; print(json.load(sys.stdin)['initialized'])")

if [ "$INIT_STATUS" = "False" ]; then
  echo "Initializing Vault..."
  INIT_RESPONSE=$(curl -sf -X PUT "${VAULT_ADDR}/v1/sys/init" \
    -H "Content-Type: application/json" \
    -d '{"secret_shares": 1, "secret_threshold": 1}')

  UNSEAL_KEY=$(echo "$INIT_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['keys'][0])")
  ROOT_TOKEN=$(echo "$INIT_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['root_token'])")

  echo "UNSEAL_KEY=${UNSEAL_KEY}" > "$KEYS_FILE"
  echo "ROOT_TOKEN=${ROOT_TOKEN}" >> "$KEYS_FILE"
  echo "Vault initialized. Keys stored in ${KEYS_FILE}"
fi

# Unseal
source "$KEYS_FILE"
SEAL_STATUS=$(curl -sf "${VAULT_ADDR}/v1/sys/seal-status" | python3 -c "import sys,json; print(json.load(sys.stdin)['sealed'])")

if [ "$SEAL_STATUS" = "True" ]; then
  echo "Unsealing Vault..."
  curl -sf -X PUT "${VAULT_ADDR}/v1/sys/unseal" \
    -H "Content-Type: application/json" \
    -d "{\"key\": \"${UNSEAL_KEY}\"}"
  echo "Vault unsealed."
fi

# Enable KV v2 secrets engine (idempotent)
curl -sf -X POST "${VAULT_ADDR}/v1/sys/mounts/secret" \
  -H "X-Vault-Token: ${ROOT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"type": "kv", "options": {"version": "2"}}' 2>/dev/null || true

echo "Vault ready."
```

**Key design choice:** Use `secret_shares=1, secret_threshold=1` for dev. This simplifies the auto-unseal script (only 1 key needed). Production would use 5/3 threshold but that is out of scope for Phase 1.

### Pattern: Letta Self-Hosted with Python SDK

**What:** Letta Docker container connects to shared Postgres; Django interacts via `letta-client` Python SDK.
**When to use:** Phase 1 validation and all subsequent phases.

```python
# hazn/core/letta_client.py
from letta_client import Letta
from django.conf import settings

def get_letta_client() -> Letta:
    """Get configured Letta client for self-hosted server."""
    return Letta(
        base_url=settings.LETTA_BASE_URL,  # http://letta:8283
        api_key=settings.LETTA_SERVER_PASSWORD,  # defaults to "letta"
    )
```

### Anti-Patterns to Avoid
- **Running Vault in dev mode:** User explicitly said no. Dev mode uses in-memory storage and auto-unseals with a known root token -- no persistence across restarts.
- **Separate Postgres containers for Django and Letta:** User chose shared instance. Two containers wastes memory and complicates networking.
- **Installing pgvector manually via Dockerfile:** Use the `pgvector/pgvector:pg17` image directly. It has the extension pre-compiled.
- **Storing raw secrets in Django .env files:** Phase 1 establishes the Vault pattern. API keys for Langfuse are the exception (connection config, not per-client secrets).
- **Using Letta's built-in Postgres (embedded in Docker image):** When `LETTA_PG_URI` is set, Letta uses external Postgres. Without it, Letta runs its own embedded Postgres inside the container -- which conflicts with the shared database decision.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Project scaffolding | Custom Django project structure | Cookiecutter Django | Battle-tested config for settings, Docker, envs, users, Celery, Sentry |
| Vector similarity search | Custom SQL or raw psycopg2 | `pgvector` Python package with Django VectorField | Handles migrations, index creation, distance functions natively |
| Vault client | Raw HTTP requests to Vault API | `hvac` v2.4.0 | Handles auth renewal, KV v2 versioning, error handling |
| Letta integration | Raw REST API calls | `letta-client` v1.7.11 | Typed SDK with agent, block, passage, and message methods |
| Docker health checks | Custom polling scripts | Docker Compose native healthcheck | Built-in retry logic, dependency ordering with `condition: service_healthy` |
| Multiple database creation | Manual SQL after container start | `/docker-entrypoint-initdb.d/` mount | Postgres Docker convention; runs only on fresh data directory |

**Key insight:** The major integration work is in Docker Compose orchestration (service dependencies, health checks, init ordering) and the Vault auto-unseal script. The actual application code is straightforward Django models + well-documented SDK calls.

## Common Pitfalls

### Pitfall 1: Postgres Init Scripts Only Run Once
**What goes wrong:** The `/docker-entrypoint-initdb.d/` scripts only execute when the data directory is empty (first `docker compose up`). If you add the letta database creation script after the volume already has data, it silently skips.
**Why it happens:** Postgres Docker convention -- init scripts are for first-time setup only.
**How to avoid:** Include the init script from the very first `docker compose up`. If the volume already exists, either `docker volume rm` and recreate, or manually run `CREATE DATABASE letta` via `psql`.
**Warning signs:** Letta server fails to connect with "database does not exist" errors after adding the script to an existing setup.

### Pitfall 2: pgvector Extension Must Be Enabled Per-Database
**What goes wrong:** You enable `CREATE EXTENSION vector` in the `hazn` database but forget the `letta` database (or vice versa). Letta archival search fails with "type vector does not exist."
**Why it happens:** PostgreSQL extensions are database-scoped, not instance-scoped.
**How to avoid:** The init SQL script must `\c letta` and then `CREATE EXTENSION IF NOT EXISTS vector`. Django migration handles the `hazn` database via `VectorExtension()`.
**Warning signs:** "type 'vector' does not exist" errors in Letta logs.

### Pitfall 3: Vault Sealed After Container Restart
**What goes wrong:** After `docker compose restart` or host reboot, Vault comes up sealed. Django cannot read secrets.
**Why it happens:** Vault with file backend seals itself on restart by design (security feature). Dev mode would not have this issue, but user chose production-like mode.
**How to avoid:** The auto-unseal script (`vault-init.sh`) must run after every `docker compose up`. Wire it into the Makefile's `make up` target or as a post-start hook.
**Warning signs:** HTTP 503 from Vault with `"sealed": true` in health check.

### Pitfall 4: Cookiecutter Django Postgres Image Mismatch
**What goes wrong:** Cookiecutter generates a custom Postgres Dockerfile in `compose/production/postgres/Dockerfile` that uses `postgres:17`. This does not include pgvector.
**Why it happens:** Cookiecutter doesn't know about pgvector. Its Postgres Dockerfile adds backup scripts but uses the base postgres image.
**How to avoid:** Replace the postgres service image with `pgvector/pgvector:pg17` in both local and production compose files. Keep the backup scripts by mounting them separately.
**Warning signs:** VectorField migrations fail with "could not open extension control file" or "extension 'vector' is not available."

### Pitfall 5: Letta Server Password vs API Key Confusion
**What goes wrong:** `letta-client` Python SDK uses `api_key` parameter but the actual value is `LETTA_SERVER_PASSWORD`, not a traditional API key.
**Why it happens:** The self-hosted Letta server uses a simple password authentication, but the SDK parameter is named `api_key` because it also supports the cloud API.
**How to avoid:** Set `LETTA_SERVER_PASSWORD` in Docker Compose and use the same value as `api_key` when initializing the Python client. The agent-os reference uses the same pattern.
**Warning signs:** 401 Unauthorized from Letta server.

### Pitfall 6: PostgreSQL 17.0-17.2 Linking Bug with pgvector
**What goes wrong:** pgvector compilation fails with "unresolved external symbol float_to_shortest_decimal_bufn."
**Why it happens:** A known bug in Postgres 17.0-17.2 that was fixed in 17.3.
**How to avoid:** Use `pgvector/pgvector:pg17` which uses a compatible Postgres 17 version (17.3+). Do not pin to an older Postgres 17 minor version.
**Warning signs:** Container fails to start with compilation or linking errors.

### Pitfall 7: Docker Compose Service Startup Ordering
**What goes wrong:** Letta tries to connect to Postgres before it is ready. Vault init script runs before Vault is listening.
**Why it happens:** Docker Compose `depends_on` only waits for container start, not service readiness, unless `condition: service_healthy` is used.
**How to avoid:** Add explicit `healthcheck` blocks to postgres, vault, and redis services. Use `depends_on` with `condition: service_healthy` for all dependent services.
**Warning signs:** "connection refused" errors in early container logs that resolve on retry.

## Code Examples

### Docker Compose Service Definitions (Key Services)

```yaml
# docker-compose.local.yml (additions to cookiecutter output)
services:
  postgres:
    image: pgvector/pgvector:pg17
    volumes:
      - local_postgres_data:/var/lib/postgresql/data
      - local_postgres_data_backups:/backups
      - ./scripts/create-letta-db.sql:/docker-entrypoint-initdb.d/create-letta-db.sql:ro
    env_file:
      - ./.envs/.local/.postgres
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-hazn_user}"]
      interval: 5s
      timeout: 3s
      retries: 5

  letta:
    image: letta/letta:latest
    ports:
      - "8283:8283"
    environment:
      LETTA_PG_URI: postgresql://${POSTGRES_USER:-hazn_user}:${POSTGRES_PASSWORD}@postgres:5432/letta
      LETTA_SERVER_PASSWORD: ${LETTA_SERVER_PASSWORD:-letta}
    env_file:
      - ./.envs/.local/.letta
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - letta_data:/root/.letta
    healthcheck:
      test: ["CMD-SHELL", "curl -sf http://localhost:8283/v1/health || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5

  vault:
    image: hashicorp/vault:1.18
    ports:
      - "8200:8200"
    environment:
      VAULT_ADDR: "http://0.0.0.0:8200"
    cap_add:
      - IPC_LOCK
    volumes:
      - vault_data:/vault/file
      - ./vault/config.hcl:/vault/config/config.hcl:ro
    command: vault server -config=/vault/config/config.hcl
    healthcheck:
      test: ["CMD-SHELL", "vault status -format=json 2>/dev/null | grep -q '\"sealed\":false' || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 3

  frontend:
    build:
      context: .
      dockerfile: ./compose/local/node/Dockerfile
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://django:8000
    depends_on:
      - django
```

### Vault HCL Config

```hcl
# vault/config.hcl
ui = true

storage "file" {
  path = "/vault/file"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = true
}

disable_mlock = true
api_addr      = "http://0.0.0.0:8200"
```

### Django Model Examples (9 L2/L3 Tables)

```python
# hazn/core/models.py
import uuid
from django.db import models

class Agency(models.Model):
    """L2 entity - marketing agency."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    house_style = models.JSONField(default=dict, blank=True)
    methodology = models.JSONField(default=dict, blank=True)
    tool_preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "agencies"

class EndClient(models.Model):
    """L3 entity - agency's end-client."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='end_clients')
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    competitors = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['agency', 'slug']

class VaultCredential(models.Model):
    """Reference to a secret stored in HashiCorp Vault."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, null=True, blank=True)
    end_client = models.ForeignKey(EndClient, on_delete=models.CASCADE, null=True, blank=True)
    service_name = models.CharField(max_length=100)  # e.g., "ga4", "gsc", "ahrefs"
    vault_secret_id = models.CharField(max_length=500)  # Vault KV path, NOT the secret
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['end_client', 'service_name']
```

```python
# hazn/marketing/models.py
from django.db import models
from hazn.core.models import EndClient
import uuid

class Keyword(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    end_client = models.ForeignKey(EndClient, on_delete=models.CASCADE, related_name='keywords')
    term = models.CharField(max_length=500)
    search_volume = models.IntegerField(null=True, blank=True)
    difficulty = models.FloatField(null=True, blank=True)
    intent = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=50, default='discovered')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Audit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    end_client = models.ForeignKey(EndClient, on_delete=models.CASCADE, related_name='audits')
    audit_type = models.CharField(max_length=100)  # e.g., "seo", "analytics", "performance"
    findings = models.JSONField(default=dict)
    score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Campaign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    end_client = models.ForeignKey(EndClient, on_delete=models.CASCADE, related_name='campaigns')
    name = models.CharField(max_length=255)
    campaign_type = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='draft')
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Decision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    end_client = models.ForeignKey(EndClient, on_delete=models.CASCADE, related_name='decisions')
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True)
    decision_type = models.CharField(max_length=100)
    rationale = models.TextField()
    outcome = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

```python
# hazn/content/models.py
from django.db import models
from pgvector.django import VectorField
from hazn.core.models import EndClient
import uuid

class BrandVoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    end_client = models.ForeignKey(EndClient, on_delete=models.CASCADE, related_name='brand_voices')
    content = models.TextField()
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['end_client', 'is_active'],
                condition=models.Q(is_active=True),
                name='unique_active_brand_voice_per_client'
            )
        ]

class ApprovedCopy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    end_client = models.ForeignKey(EndClient, on_delete=models.CASCADE, related_name='approved_copies')
    copy_type = models.CharField(max_length=100)  # e.g., "headline", "body", "cta", "email"
    content = models.TextField()
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    campaign = models.ForeignKey('marketing.Campaign', on_delete=models.SET_NULL, null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "approved copies"
```

### Vault Integration (Django)

```python
# hazn/core/vault.py
import hvac
from django.conf import settings

def get_vault_client() -> hvac.Client:
    """Get authenticated Vault client."""
    client = hvac.Client(
        url=settings.VAULT_ADDR,
        token=settings.VAULT_TOKEN,
    )
    assert client.is_authenticated(), "Vault client is not authenticated"
    return client

def store_secret(path: str, data: dict) -> str:
    """Store a secret in Vault KV v2. Returns the full path."""
    client = get_vault_client()
    client.secrets.kv.v2.create_or_update_secret(
        path=path,
        secret=data,
        mount_point="secret",
    )
    return f"secret/data/{path}"

def read_secret(path: str) -> dict:
    """Read a secret from Vault KV v2."""
    client = get_vault_client()
    response = client.secrets.kv.v2.read_secret_version(
        path=path,
        mount_point="secret",
    )
    return response["data"]["data"]
```

### Letta SDK Validation (Django management command)

```python
# hazn/core/management/commands/validate_letta.py
from django.core.management.base import BaseCommand
from letta_client import Letta
from django.conf import settings

class Command(BaseCommand):
    help = "Validate Letta server connection and basic operations"

    def handle(self, *args, **options):
        client = Letta(
            base_url=settings.LETTA_BASE_URL,
            api_key=settings.LETTA_SERVER_PASSWORD,
        )

        # Create a test agent
        agent = client.agents.create(
            name="hazn-test-agent",
            model="openai/gpt-4o-mini",  # or anthropic/claude-sonnet-4-5-20250929
            memory_blocks=[
                {"label": "persona", "value": "I am a test agent for Hazn platform.", "limit": 5000},
                {"label": "human", "value": "Test user.", "limit": 5000},
            ],
        )
        self.stdout.write(f"Created agent: {agent.id}")

        # Insert archival memory
        client.agents.passages.insert(
            agent_id=agent.id,
            content="Test archival memory passage for Hazn validation.",
            tags=["test", "validation"],
        )
        self.stdout.write("Inserted archival passage")

        # Search archival memory
        results = client.agents.passages.search(
            agent_id=agent.id,
            query="Hazn validation",
        )
        self.stdout.write(f"Archival search returned {len(results)} results")

        # Clean up
        client.agents.delete(agent_id=agent.id)
        self.stdout.write(self.style.SUCCESS("Letta validation passed"))
```

### Makefile Targets

```makefile
# Makefile (extends cookiecutter Django defaults)
.PHONY: up down seed reset-db vault-init test logs

COMPOSE_FILE := docker-compose.local.yml

up:
	docker compose -f $(COMPOSE_FILE) up -d
	@echo "Waiting for services to be healthy..."
	@sleep 5
	$(MAKE) vault-init

down:
	docker compose -f $(COMPOSE_FILE) down

seed:
	docker compose -f $(COMPOSE_FILE) run --rm django python manage.py seed_dev_data

reset-db:
	docker compose -f $(COMPOSE_FILE) down -v
	docker compose -f $(COMPOSE_FILE) up -d
	@sleep 5
	$(MAKE) vault-init
	docker compose -f $(COMPOSE_FILE) run --rm django python manage.py migrate
	$(MAKE) seed

vault-init:
	@bash scripts/vault-init.sh

test:
	docker compose -f $(COMPOSE_FILE) run --rm django pytest

logs:
	docker compose -f $(COMPOSE_FILE) logs -f
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `ankane/pgvector` Docker image | `pgvector/pgvector:pg17` (official) | 2024 | Official images maintained by pgvector team, not third-party |
| Letta Python SDK `letta` (server package) | `letta-client` (separate client package) | 2025 | Clean separation: server in Docker, client as pip package |
| Vault `vault` Docker image (community) | `hashicorp/vault` (verified publisher) | 2023 | Official HashiCorp images; community `vault` image is deprecated |
| Cookiecutter Django with Postgres 14-16 | Supports Postgres 14-18 | 2025 | Can select Postgres 17 directly during generation |
| Letta `ankane/pgvector:v0.5.1` in official compose | pgvector 0.8.0 with Postgres 17 | 2025 | Newer pgvector version with better HNSW performance |

**Deprecated/outdated:**
- `vault` Docker Hub image: Use `hashicorp/vault` instead
- `letta` pip package for client usage: Use `letta-client` for SDK operations
- `ankane/pgvector`: Letta's compose still references v0.5.1, but `pgvector/pgvector:pg17` is the current official image with pgvector 0.8.0

## Open Questions

1. **Letta Docker Image Version Pinning**
   - What we know: `letta/letta:latest` works but is unpredictable for reproducible builds. Version 0.7.8 exists on Docker Hub.
   - What's unclear: Whether 0.7.8 is the latest stable release, or if there are newer tags.
   - Recommendation: Start with `letta/letta:latest` for Phase 1, pin to a specific version tag once validated. Check `docker pull letta/letta:latest && docker inspect letta/letta:latest` to capture the actual version.

2. **Letta Agent Model Configuration**
   - What we know: Agent creation requires a `model` parameter (e.g., `openai/gpt-4o-mini`, `anthropic/claude-sonnet-4-5-20250929`). Letta server needs the corresponding API key as env var.
   - What's unclear: Which model the user wants Letta agents to use. The agent-os reference used `anthropic/claude-sonnet-4-5-20250929`.
   - Recommendation: Set both `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` on the Letta server. Default to Anthropic for consistency with the existing Hazn ecosystem.

3. **Vault Health Check When Sealed**
   - What we know: Vault returns HTTP 503 when sealed. The auto-unseal script runs after `docker compose up`.
   - What's unclear: Whether to make Vault's health check pass when sealed (so dependent services can start) or fail (which blocks everything).
   - Recommendation: Use a lenient health check that passes when Vault is reachable (even sealed), and handle unseal as a separate Makefile step. Services that depend on Vault should gracefully retry.

4. **Next.js Frontend Scope in Phase 1**
   - What we know: User wants Next.js Dockerized with hot reload. Phase 1 is infrastructure foundation.
   - What's unclear: How much frontend setup is needed -- just a skeleton app, or nothing beyond Dockerfile?
   - Recommendation: Scaffold a minimal Next.js app with TypeScript + Tailwind, Dockerize it, confirm hot reload works. No routes or components needed yet.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest + pytest-django (Cookiecutter Django default) |
| Config file | `pytest.ini` or `setup.cfg` (generated by Cookiecutter) |
| Quick run command | `docker compose -f docker-compose.local.yml run --rm django pytest -x` |
| Full suite command | `docker compose -f docker-compose.local.yml run --rm django pytest` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INFRA-01 | All services start healthy via docker compose | smoke | `docker compose -f docker-compose.local.yml ps --format json` (check all healthy) | No -- Wave 0 |
| INFRA-02 | Schema accepts inserts/queries for all 9 tables | integration | `pytest tests/test_models.py -x` | No -- Wave 0 |
| INFRA-03 | Vault stores/retrieves test secret; Postgres stores only vault_secret_id | integration | `pytest tests/test_vault.py -x` | No -- Wave 0 |
| INFRA-04 | Letta accepts agent creation and archival memory ops | integration | `pytest tests/test_letta.py -x` or `manage.py validate_letta` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `docker compose -f docker-compose.local.yml run --rm django pytest -x`
- **Per wave merge:** Full suite + `docker compose ps` health check
- **Phase gate:** Full suite green + all 4 success criteria manually verified before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `pytest.ini` / `conftest.py` -- generated by Cookiecutter Django, need to verify
- [ ] `tests/test_models.py` -- CRUD tests for all 9 models (insert, query, foreign key constraints)
- [ ] `tests/test_vault.py` -- Store and retrieve a test secret via hvac; verify vault_secret_id pattern
- [ ] `tests/test_letta.py` -- Create agent, insert archival passage, search archival memory via letta-client SDK
- [ ] `scripts/validate_services.sh` -- Smoke test that all Docker services are healthy
- [ ] Framework deps: `pytest`, `pytest-django` (included in Cookiecutter Django `requirements/local.txt`)

## Sources

### Primary (HIGH confidence)
- [Letta Docs - Docker deployment](https://docs.letta.com/guides/docker/) - Docker image, env vars, port mapping
- [Letta Docs - Postgres configuration](https://docs.letta.com/guides/selfhosting/postgres) - LETTA_PG_URI, pgvector requirement
- [Letta Docs - Memory blocks](https://docs.letta.com/guides/agents/memory-blocks) - Block creation, shared blocks, SDK examples
- [Letta Docs - Archival search](https://docs.letta.com/guides/agents/archival-search/) - Passage insert, semantic search, tags
- [Letta Docs - Python SDK](https://docs.letta.com/api/python/) - Client init, agent CRUD, self-hosted base_url
- [Letta GitHub - compose.yaml](https://github.com/letta-ai/letta/blob/main/compose.yaml) - Official compose with ankane/pgvector:v0.5.1
- [letta-client PyPI](https://pypi.org/project/letta-client/) - Version 1.7.11 (March 4, 2026)
- [pgvector-python GitHub](https://github.com/pgvector/pgvector-python) - Django VectorField, VectorExtension, distance functions
- [pgvector GitHub](https://github.com/pgvector/pgvector) - Postgres 17.3+ compatibility note
- [Cookiecutter Django GitHub](https://github.com/cookiecutter/cookiecutter-django) - Django 5.2, Python 3.13, features list
- [Cookiecutter Django Docs - Local Docker](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally-docker.html) - Compose structure, env files
- [hvac GitHub](https://github.com/hvac/hvac) - v2.4.0, Python 3.x, Vault client
- [HashiCorp Vault Docker Hub](https://hub.docker.com/r/hashicorp/vault) - Version 1.18+

### Secondary (MEDIUM confidence)
- [Securing Django with Vault/hvac](https://simplico.net/2024/10/23/securing-django-applications-with-hashicorp-vault-hvac-concepts-and-practical-examples/) - KV v2 read/write patterns, transit engine
- [Multiple Postgres DBs in Docker](https://dev.to/bgord/multiple-postgres-databases-in-a-single-docker-container-417l) - /docker-entrypoint-initdb.d/ pattern
- [GitHub - docker-postgresql-multiple-databases](https://github.com/mrts/docker-postgresql-multiple-databases) - Init script pattern for multiple databases
- [Vault Docker setup gist](https://gist.github.com/Mishco/b47b341f852c5934cf736870f0b5da81) - HCL config, init/unseal workflow

### Tertiary (LOW confidence)
- Letta Docker image version tags (0.7.8 found via Docker Hub layers, but "latest" version unconfirmed -- needs validation at build time)
- Vault health check behavior when sealed (inferred from API docs, not tested)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified via official docs and PyPI/Docker Hub
- Architecture: HIGH - Patterns derived from official documentation and locked user decisions
- Pitfalls: HIGH - Based on documented Docker Postgres behavior, pgvector README warnings, and Vault seal mechanics
- Code examples: MEDIUM - SDK examples from official docs; Django models are researcher's synthesis of user schema requirements

**Research date:** 2026-03-05
**Valid until:** 2026-04-05 (30 days -- stable technologies, pinned versions)

---
*Phase: 01-infrastructure-foundation*
*Research completed: 2026-03-05*

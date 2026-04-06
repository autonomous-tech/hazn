# Phase 1: Infrastructure Foundation - Context

**Gathered:** 2026-03-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Stand up Postgres 17 (+pgvector), Letta, HashiCorp Vault, Redis, and connect to existing Langfuse via Docker Compose. Validate all services are healthy and can communicate. Backend is Cookiecutter Django; frontend is Next.js. Everything runs in Docker Compose.

</domain>

<decisions>
## Implementation Decisions

### Backend Framework
- Cookiecutter Django as the backend framework
- Enable all optional integrations: Celery + Redis, DRF, Whitenoise, Sentry
- Next.js as the frontend, also Dockerized in the Compose stack

### Database Topology
- Single Postgres 17 instance shared between Hazn app and Letta (separate databases on the same container)
- pgvector extension added to the Django Postgres database
- Letta gets its own database (e.g., `letta`) alongside Django's database

### Schema Design
- Strict 1:many relationship: each end-client (L3) belongs to exactly one agency (L2)
- Hard deletes in v1 -- retention/GDPR compliance deferred to Phase 5
- Metering tables (workflow_runs, workflow_agents, workflow_tool_calls) deferred to Phase 3/4 when orchestrator is built
- Phase 1 schema covers the 9 L2/L3 tables: agencies, end_clients, keywords, audits, campaigns, decisions, approved_copy, brand_voice, vault_credentials

### Vault Configuration
- Production-like from day 1: file backend, proper init/unseal sequence
- Auto-unseal script stores keys in `.vault-keys` (gitignored) and auto-unseals on container startup
- Not dev mode -- real Vault behavior from the start

### Langfuse
- Already deployed on personal cloud infrastructure
- Not included in Docker Compose stack
- Phase 1 only needs connection configuration (API keys, base URL as env vars)

### Reverse Proxy
- Traefik included in Compose stack (from Cookiecutter Django)
- Routes traffic and handles TLS termination

### Dev Workflow
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

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `autonomous-agent-os/docker-compose.yml`: Reference pattern for Letta + Postgres in Docker Compose (3-service stack with health checks, named volumes)
- `autonomous-agent-os/packages/agent-os-mcp/`: Reference for MCP server implementation (tools: load_context, memory ops, archival, sync)
- `autonomous-agent-os/src/lib/letta/`: Reference for Letta SDK integration patterns (client, translate, memory, memory-extract, skills)
- `@letta-ai/letta-client` ^1.7.8: Letta SDK version used in agent-os (reference for version pinning)

### Established Patterns
- Letta server runs on port 8283 with `LETTA_PG_URI` pointing to Postgres
- Letta uses `LETTA_SERVER_PASSWORD` for auth (defaults to "letta")
- Agent-os Letta integration is fully optional with `isLettaEnabled()` guard pattern
- Memory sync uses Claude to categorize learnings into persona/decisions/archival buckets

### Integration Points
- Hazn agents, skills, and workflows exist as markdown/YAML in `hazn/` directory
- Python analytics scripts exist in `hazn/scripts/analytics-audit/` (GA4, GSC, PageSpeed collectors)
- Workflow YAML definitions in `hazn/workflows/` will be interpreted by the orchestrator (Phase 3)

</code_context>

<specifics>
## Specific Ideas

- "Use Cookiecutter Django -- it has everything" -- user wants the proven Django project template as the foundation
- "Everything will be Dockerized using Compose" -- no hybrid local/Docker setup, full Compose stack
- Langfuse is already running in personal cloud -- just needs connection config, not deployment

</specifics>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 01-infrastructure-foundation*
*Context gathered: 2026-03-05*

# Hazn Platform

## What This Is

Hazn is a personal multi-client workflow runner for Rizwan's marketing agency. 15+ specialized agents execute YAML-defined workflows (SEO audits, content, websites, analytics) per client, with compounding memory that builds on past decisions, brand voice, and findings. A browser dashboard lets Rizwan pick a client, trigger a workflow, monitor progress, and grab deliverables.

## Core Value

Agents remember and compound — every engagement builds on past decisions, brand voice, keyword history, and craft knowledge, making each run better than the last.

## Requirements

### Validated

- Agent definitions exist for 15+ specialized agents (SEO, Developer, Copywriter, Auditor, QA, etc.) — existing in `hazn/agents/`
- Skill definitions exist for 20+ skills (analytics-audit, seo-audit, keyword-research, etc.) — existing in `hazn/skills/`
- Workflow definitions exist for 7 workflows (analytics-audit, landing, website, blog, etc.) — existing in `hazn/workflows/`
- CLI tool for Hazn project scaffolding — existing in `hazn/src/`, `hazn/bin/`
- Python analytics collection scripts — existing in `hazn/scripts/analytics-audit/`
- Langfuse self-hosted and deployed — existing infrastructure
- Docker Compose stack with Postgres 17 + pgvector, Letta, Vault, Redis, Django 5.2, Next.js 15 — v1.0
- 9 L2/L3 Django models across core, marketing, content apps with pgvector semantic search — v1.0
- HaznMemory swap-safe abstraction with session lifecycle, checkpoint sync, failure sync — v1.0
- mcp-hazn-memory MCP server with 7 tools (load_context, write_finding, search_memory, checkpoint_sync, correct_memory, get_credentials, end_session) — v1.0
- DAG-based workflow executor with multi-agent orchestration and Celery async tasks — v1.0
- Three-layer client model (L1/L2/L3) with conflict detection and HITL queue — v1.0
- Vault AppRole authentication with least-privilege HCL policies — v1.0
- MCP servers for Vercel, GitHub, GA4/GSC/PageSpeed — v1.0
- Langfuse tracing + Postgres metering pipeline with runaway agent detection — v1.0
- QA system with 6 task-type criteria, 48-hour approval lifecycle, Vercel preview staging — v1.0
- Data lifecycle enforcement (90-day retention, GDPR deletion, churn notification) — v1.0
- Agency workspace UI (dashboard, Memory Inspector, Workflow Trigger, HITL Queue, Deliverables) — v1.0

### Active

- [ ] Strip enterprise complexity from hazn_platform/ (MCP servers, conflict detection, HITL queue, QA pipeline, dual runtime, budget enforcement, Langfuse metering)
- [ ] Simplified workflow engine — read hazn/ YAML, chain agents through phases via Anthropic API
- [ ] Tools as Python functions — no MCP indirection
- [ ] Per-client Letta memory — compounds brand voice, work history, findings across runs
- [ ] Dashboard — client list, workflow trigger, monitor progress, view deliverables
- [ ] All 7 workflows executable end-to-end on real client work

### Out of Scope

- Billing / subscription — not needed for personal tool
- Multi-tenant / agency self-serve (Mode 3) — personal use only
- Mode 2 (MCP-connected) — personal use only
- Claude Agent SDK — Anthropic API direct only
- MCP servers — tools as Python functions
- HITL queue / QA approval pipeline — Rizwan reviews deliverables directly
- Conflict detection / L2-L3 hierarchy — single user, no conflicts
- Session/checkpoint system — simplified execution model
- White-label / reseller — not applicable
- Mobile — web-first
- Real-time collaboration — single user
- Graph database — Postgres + pgvector sufficient

## Context

**Current state:** v2.0 shipped phases 8-10 (~60,600 LOC). Enterprise infrastructure exists but is over-engineered for the actual use case: one person running workflows for 8+ clients. The v3.0 milestone strips complexity and rewires the platform for personal multi-client use.

**What exists and stays:** Django backend, Next.js frontend, Docker Compose stack (Postgres 17 + pgvector, Letta, Vault, Redis), hazn/ repo with 15+ agents, 25+ skills, 7 workflow YAML definitions, deliverable rendering pipeline (Jinja2).

**What gets stripped:** 4 MCP servers, ToolRouter complexity, dual runtime (Agent SDK path), conflict detection, HITL queue, QA approval pipeline, session/checkpoint system, budget enforcement, Langfuse metering, agency cost caps, L2/L3 hierarchy.

**What gets simplified:** Workflow executor rewired to read YAML → chain Anthropic API calls with Python function tools → store deliverable. Per-client Letta memory for compounding context.

**Client model (simplified):** Each client = a Letta agent with persistent memory (brand voice, work history, findings). No L2/L3 hierarchy — Rizwan manages all clients directly.

## Constraints

- **Memory abstraction**: All Letta access must go through HaznMemory interface — swap-safe design
- **Secrets isolation**: Raw secrets never in Postgres or agent context — Vault only
- **Session model**: One workflow run = one session. Checkpoint every 10 turns. 4-hour inactivity fallback
- **Conflict resolution**: L3 brand voice wins by default. L2 can lock overrides. 24-hour timeout on unresolved
- **Data retention**: Max 90-day retention post-churn. GDPR 30-day deletion on request
- **Metering before pricing**: Need 10+ real workflow runs logged before setting credit prices
- **Existing agents**: Must work with existing agent/skill/workflow markdown definitions

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Agent-os = reference only | Extract Letta patterns, build directly against Letta SDK | Good — clean SDK integration |
| Postgres + pgvector (no graph) | Covers ~80% of graph use cases, add graph later if needed | Good — sufficient for v1 |
| Letta self-hosted via Docker | Version control, no SaaS dependency | Good — shared Postgres works |
| HashiCorp Vault for secrets | Secrets never touch Postgres | Good — AppRole adds security |
| Mode 1 before Mode 3 | Internal validation first, then self-serve | Good — both built in v1.0 |
| Credits + feature gating pricing | Instantly-style, tiers set after cost data | Pending — need real run data |
| HaznMemory abstraction required | Makes Letta swap-safe if replaced later | Good — clean interface |
| AppRole over root token | Production-grade security, least-privilege | Good — 3 scoped roles |
| DAG-based executor | Parallel phase execution, tool scoping | Good — async with Celery |
| FastMCP for MCP servers | Lightweight, Python-native | Good — 4 servers built |
| OpenClaw rejected | Single-user, CVEs, TS-Python bridge, wrapping > building | Good — research conclusive |
| Hybrid runtime (Agent SDK + API) | Max sub for Mode 1, metered API for Mode 3 | ⚠️ Revisit — cut in v3.0, API-only |
| Strip to personal tool | Enterprise features (MCP, HITL, QA, dual runtime, metering) over-engineered for single-user agency | Good — red-team confirmed 2026-03-12 |
| Tools as Python functions | MCP indirection adds complexity without value for single user | — Pending |
| Anthropic API only | No Agent SDK — direct API tool_use loops | — Pending |

## Current Milestone: v3.0 Strip & Simplify

**Goal:** Strip enterprise complexity and rewire Hazn as a personal multi-client workflow runner — pick a client, trigger a workflow, get a deliverable.

**Target features:**
- Strip MCP servers, conflict detection, HITL, QA pipeline, dual runtime, budget enforcement, metering
- Simplified workflow engine: YAML → Anthropic API agent loops → Python function tools → deliverable
- Per-client Letta memory with compounding context
- Clean dashboard: client list, workflow trigger, progress monitor, deliverables
- All 7 workflows executable end-to-end on real client work

---
*Last updated: 2026-03-12 after v3.0 milestone start*

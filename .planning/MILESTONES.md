# Milestones

## v1.0 Infrastructure (Shipped: 2026-03-06)

**Phases completed:** 7 phases, 23 plans, 0 tasks

**Key accomplishments:**
- Docker Compose stack with 10 services (Postgres 17 + pgvector, Letta, Vault, Redis, Django 5.2, Next.js 15)
- HaznMemory abstraction with swap-safe Letta access, session lifecycle, checkpoint sync, and zero cross-client contamination
- DAG-based workflow executor with multi-agent orchestration, L2/L3 conflict detection, HITL queue, and Celery async tasks
- 4 MCP tool servers (Vercel, GitHub, GA4/GSC/PageSpeed, Hazn Memory) with Langfuse tracing and metering pipeline
- QA system with 6 task-type criteria, 48-hour approval lifecycle, Vercel preview staging, and data lifecycle enforcement
- Agency workspace with dashboard, Memory Inspector, Workflow Trigger, HITL Queue, Deliverables, and OAuth login
- Vault AppRole authentication with least-privilege HCL policies replacing root token usage

## v2.0 Executable Workflows (Shipped: 2026-03-12)

**Phases completed:** 3 phases (8-10), 9 plans. Phases 11-13 cut after red-team simplification.

**Key accomplishments:**
- PromptAssembler, ToolRouter, OutputCollector foundation components
- Dual-runtime AgentRunner (Anthropic API + Claude Agent SDK) with BudgetEnforcer
- SEO audit workflow end-to-end: workspace trigger → agent execution → branded HTML deliverable
- Deliverable pipeline with Jinja2 rendering, SSE real-time status, catalog API

**Cut (replaced by v3.0 simplified approach):**
- Phase 11: Quality Gate (red team agent)
- Phase 12: Remaining Workflows (all 7 E2E)
- Phase 13: Mode 1 Validation (internal usage tracking)

---


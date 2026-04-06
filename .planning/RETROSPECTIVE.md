# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — Infrastructure

**Shipped:** 2026-03-06
**Phases:** 7 | **Plans:** 23 | **Commits:** 185

### What Was Built
- Full Docker Compose stack (10 services) with Django 5.2, Next.js 15, Postgres 17 + pgvector, Letta, Vault, Redis
- HaznMemory swap-safe abstraction with session lifecycle, checkpoint sync, failure sync, and zero cross-client contamination
- DAG-based workflow executor with multi-agent orchestration, L2/L3 conflict detection, HITL queue, Celery async tasks
- 4 MCP tool servers (Vercel, GitHub, GA4/GSC/PageSpeed, Hazn Memory) with Langfuse tracing and metering
- QA system with 6 task-type criteria, 48-hour approval lifecycle, Vercel preview staging, data lifecycle enforcement
- Agency workspace UI (dashboard, Memory Inspector, Workflow Trigger, HITL Queue, Deliverables, OAuth)
- Vault AppRole authentication with 3 scoped HCL policies replacing root token

### What Worked
- Parallel phase execution via GSD tooling kept velocity high across 7 phases in 18 days
- Research-before-plan pattern caught architecture issues early (agent-os reference-only decision)
- Domain-split Django apps (core, marketing, content) kept models organized as the schema grew to 15+ models
- FastMCP pattern made MCP server development fast — 4 servers in a single phase

### What Was Inefficient
- ROADMAP plan checkboxes drifted from actual disk state (some unchecked despite having summaries)
- All infrastructure built before any real agent execution — no feedback loop from actual workflow runs yet
- Mode 1 "validation" phase built QA machinery but didn't run real engagements

### Patterns Established
- HaznMemory as the single interface for all Letta access (swap-safe contract)
- AppRole per service role (Django CRUD, orchestrator read-only, MCP read-only)
- Pydantic schemas for workflow YAML parsing and validation
- FastMCP thin-wrapper pattern delegating logic to core modules
- Test-first approach: failing tests committed before implementation

### Key Lessons
1. Build the execution path early — having all components without an end-to-end wiring means you can't validate integration assumptions
2. Memory abstraction was the right call — Letta SDK changes during development would have required rewrites without it
3. Vault AppRole should be in Phase 1, not Phase 7 — retrofitting auth is more work than starting with it

### Cost Observations
- Model mix: primarily quality profile (opus)
- 185 commits over 18 days
- Notable: ~60,600 LOC produced (24.9K Python, 35.7K TypeScript)

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Commits | Phases | Key Change |
|-----------|---------|--------|------------|
| v1.0 | 185 | 7 | Initial infrastructure build |

### Cumulative Quality

| Milestone | LOC | Python Files | TypeScript Files |
|-----------|-----|-------------|-----------------|
| v1.0 | ~60,600 | 172 | 230 |

### Top Lessons (Verified Across Milestones)

1. Wire end-to-end execution before building all components — validates integration assumptions early
2. Security primitives (auth, policies) belong in Phase 1, not as a late addition

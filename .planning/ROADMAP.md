# Roadmap: Hazn Platform

## Milestones

- v1.0 Infrastructure -- Phases 1-7 (shipped 2026-03-06)
- v2.0 Executable Workflows -- Phases 8-10 (shipped 2026-03-12, phases 11-13 cut)
- v3.0 Strip & Simplify -- Phases 1-7 (in progress)

## Phases

<details>
<summary>v1.0 Infrastructure (Phases 1-7) - SHIPPED 2026-03-06</summary>

- [x] Phase 1: Infrastructure Foundation (3/3 plans) -- Docker Compose, Postgres+pgvector, Vault, Letta, Django 5.2
- [x] Phase 2: Memory Layer (3/3 plans) -- HaznMemory abstraction, mcp-hazn-memory server
- [x] Phase 3: Orchestrator & Client Model (4/4 plans) -- DAG executor, L2/L3 conflicts, HITL queue
- [x] Phase 4: MCP Tool Servers & Observability (3/3 plans) -- Vercel, GitHub, GA4/PageSpeed, Langfuse tracing
- [x] Phase 5: Mode 1 Validation & QA (4/4 plans) -- QA criteria, approval lifecycle, data retention
- [x] Phase 6: Mode 3 Workspace (4/4 plans) -- Agency dashboard, Memory Inspector, Deliverables
- [x] Phase 7: Vault AppRole Auth & Policies (2/2 plans) -- AppRole, HCL policies, token caching

</details>

<details>
<summary>v2.0 Executable Workflows (Phases 8-10) - SHIPPED 2026-03-12</summary>

- [x] Phase 8: Foundation Components (3/3 plans) -- PromptAssembler, ToolRouter, OutputCollector
- [x] Phase 9: Agent Execution Runtime (3/3 plans) -- Dual-runtime AgentRunner with BudgetEnforcer
- [x] Phase 10: First Workflow E2E (3/3 plans) -- SEO audit trigger to stored deliverable

Phases 11-13 (Quality Gate, Remaining Workflows, Mode 1 Validation) cut after red-team simplification. Replaced by v3.0.

</details>

### v3.0 Strip & Simplify

**Milestone Goal:** Strip enterprise complexity and rewire Hazn as a personal multi-client workflow runner -- pick a client, trigger a workflow, get a deliverable.

- [ ] **Phase 1: Strip Infrastructure & Dependencies** - Remove enterprise packages, imports, Celery tasks, and non-model code
- [x] **Phase 2: Model Simplification** - Two-wave migration to remove enterprise models/fields, Agency as singleton (completed 2026-03-12)
- [ ] **Phase 3: Tool Migration** - Extract MCP server logic into Python function tools, build ToolRegistry for Agent SDK
- [x] **Phase 4: Executor Rewrite** - Agent SDK executor: YAML phase walker with DAG ordering and async Celery execution (completed 2026-03-13)
- [ ] **Phase 5: Memory Rewiring** - One Letta agent per client, simplified HaznMemory, phase-boundary checkpoints
- [ ] **Phase 6: Dashboard & Chat** - Simplified frontend with client CRUD, workflow trigger, progress monitor, deliverables, and per-run chat view
- [ ] **Phase 7: End-to-End Validation** - Analytics-teaser workflow on real client data, deliverable in dashboard

## Phase Details

### Phase 1: Strip Infrastructure & Dependencies
**Goal**: Enterprise runtime code and background tasks are removed so the codebase compiles cleanly -- budget enforcement, Anthropic API backend, session turn counting, and GDPR scheduling are gone; Langfuse stays for observability
**Depends on**: Nothing (first phase)
**Requirements**: STRP-04, STRP-05, STRP-06, STRP-08, STRP-09
**Success Criteria** (what must be TRUE):
  1. Django starts and all management commands run without importing budget enforcement or session/checkpoint turn counter modules
  2. The Anthropic API direct backend is removed and only the Agent SDK execution path remains in the codebase
  3. No Celery periodic tasks reference enterprise features (GDPR deletion, data retention scheduling)
  4. Langfuse tracing and metering cost accumulation work -- only budget threshold alerts are stripped from metering
**Plans:** 2 plans

Plans:
- [ ] 01-01-PLAN.md -- Remove budget enforcement module and Anthropic API backend (STRP-04, STRP-05)
- [ ] 01-02-PLAN.md -- Remove lifecycle/GDPR module, strip metering alerts, remove session turn counter (STRP-06, STRP-08, STRP-09)

### Phase 2: Model Simplification
**Goal**: Django models reflect the simplified single-user system -- enterprise fields removed, HITL and QA models dropped, Agency preserved as singleton, permissions simplified to IsAuthenticated
**Depends on**: Phase 1
**Requirements**: STRP-02, STRP-03, STRP-07, STRP-10
**Success Criteria** (what must be TRUE):
  1. WorkflowRun and Deliverable models have no HITL, QA, conflict, or Langfuse fields -- migrations apply cleanly on a copy of the production database
  2. HITLItem model class is fully removed (model, views, serializers, admin, URLs) with no dangling FK references
  3. Agency model exists as a singleton row -- all permission checks use IsAuthenticated instead of IsAgencyMember
  4. `python manage.py makemigrations --check` produces no new migrations (model state is clean)
**Plans:** 2/2 plans complete

Plans:
- [ ] 02-01-PLAN.md -- Modify models (delete HITLItem, add PhaseOutput fields, remove enterprise fields, Agency singleton, generate migration)
- [ ] 02-02-PLAN.md -- API layer cleanup, delete QA app and dead files, squash migrations to fresh 0001_initial per app

### Phase 3: Tool Migration
**Goal**: All tool functionality previously served by MCP servers exists as Python functions registered with the Claude Agent SDK, and MCP server files are deleted
**Depends on**: Phase 2
**Requirements**: STRP-01, TOOL-01, TOOL-02, TOOL-03, TOOL-04, TOOL-05, TOOL-06, TOOL-07, TOOL-08
**Success Criteria** (what must be TRUE):
  1. A ToolRegistry exists that maps tool names to Python async functions and produces Agent SDK tool definitions via `get_tools()`
  2. File I/O tools (read, write, mkdir) and web fetch tool work as standalone Python functions callable outside the executor
  3. GA4, GSC, and PageSpeed tools retrieve real data using credentials from Vault -- verified with a test client
  4. GitHub and Vercel tools perform repo and deployment operations as Python functions
  5. All 4 MCP server files are deleted and `fastmcp` is removed from dependencies -- no MCP protocol code remains
**Plans:** 5 plans

Plans:
- [ ] 03-01-PLAN.md -- ToolRegistry scaffold, File I/O tools, Web fetch tool (TOOL-01, TOOL-02, TOOL-08)
- [ ] 03-02-PLAN.md -- Port memory, GitHub, and Vercel tools from MCP servers (TOOL-06, TOOL-07)
- [ ] 03-03-PLAN.md -- Full-depth analytics tools: GA4, GSC, PageSpeed (TOOL-03, TOOL-04, TOOL-05)
- [ ] 03-04-PLAN.md -- Wire ToolRegistry into executor, delete MCP servers and old routing (STRP-01, TOOL-08)
- [ ] 03-05-PLAN.md -- Gap closure: wire real SDK into backend, fix analytics imports, update tests for SdkMcpTool (TOOL-08)

### Phase 4: Executor Rewrite
**Goal**: A from-scratch executor reads workflow YAML, walks phases in DAG order via Agent SDK agent loops, stores phase outputs, renders deliverables, and emits SSE progress events -- all running async in Celery
**Depends on**: Phase 3 (ToolRegistry), Phase 2 (stable models)
**Requirements**: EXEC-01, EXEC-02, EXEC-03, EXEC-04, EXEC-05, EXEC-06
**Success Criteria** (what must be TRUE):
  1. Given a workflow YAML and client ID, the executor loads agent .md personas and skill .md definitions per phase and chains Agent SDK agent loops in DAG topological order
  2. Phase N output is available as input context to Phase N+1 agents
  3. The executor runs as a Celery task -- triggering a workflow returns immediately and execution happens in the background
  4. Each completed phase produces a WorkflowPhaseOutput record with structured output, and delivery phases produce rendered Deliverables
  5. SSE events fire at phase boundaries (phase_started, phase_completed, workflow_completed, workflow_failed)
**Plans:** 3/3 plans complete

Plans:
- [x] 04-01-PLAN.md -- Schema updates (max_turns), session.py rewrite (one-Letta-agent-per-client), dead code deletion (EXEC-01, EXEC-05)
- [x] 04-02-PLAN.md -- Executor.py rewrite: DAG walker with direct SDK calls, prior phase output injection, retry logic (EXEC-01, EXEC-02, EXEC-03, EXEC-04, EXEC-06)
- [x] 04-03-PLAN.md -- Tasks.py rewrite, dead test cleanup, comprehensive test suite (EXEC-01, EXEC-02, EXEC-03, EXEC-04, EXEC-05, EXEC-06)

### Phase 5: Memory Rewiring
**Goal**: Each client has one Letta agent with persistent memory that loads at run start, accumulates learnings during execution, checkpoints at phase boundaries, and supports semantic search and user correction
**Depends on**: Phase 2 (simplified models)
**Requirements**: MEMO-01, MEMO-02, MEMO-03, MEMO-04, MEMO-05, MEMO-06
**Success Criteria** (what must be TRUE):
  1. Creating a new client in the dashboard automatically provisions a Letta agent with isolated persistent memory (client_profile block)
  2. At workflow run start, client context (brand voice, keywords, past findings) is loaded from Letta and injected into agent system prompts
  3. Learnings written during execution (CraftLearning with provenance and confidence) persist and appear in subsequent runs for the same client
  4. User can view and correct wrong learnings from the dashboard before they compound into future runs
  5. Semantic search across a client's learnings returns relevant past findings by meaning, not just keyword match
**Plans:** 4 plans

Plans:
- [x] 05-01-PLAN.md -- Fix Letta SDK API mismatches in memory.py and session.py, update unit tests (MEMO-01, MEMO-02, MEMO-04, MEMO-05)
- [x] 05-02-PLAN.md -- Add add_learning tool, auto-extraction logic, test_memory management command (MEMO-03)
- [x] 05-03-PLAN.md -- Fix MemoryInspectorView naming, add list endpoint, REST endpoint tests (MEMO-06)
- [x] 05-04-PLAN.md -- Integration tests with Docker Letta, Letta mock fixtures in conftest.py (MEMO-01..06)

### Phase 6: Dashboard & Chat
**Goal**: The browser dashboard provides client management, workflow triggering, real-time progress monitoring, deliverable viewing, run history, error display, and a per-run chat view for user input and agent steering
**Depends on**: Phase 4 (executor), Phase 5 (memory)
**Requirements**: DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06, DASH-07, CHAT-01, CHAT-02, CHAT-03, CHAT-04
**Success Criteria** (what must be TRUE):
  1. User can create, edit, and view clients from the dashboard and select any client to trigger a workflow from the catalog
  2. After triggering a workflow, the user sees real-time phase-level progress via SSE -- including which phase is running and completion status
  3. Completed workflows show rendered HTML deliverables in the browser and appear in the client's run history with status, cost, and duration
  4. Each workflow run has a chat thread where the user provides initial inputs (site URL, company name) before execution starts
  5. The running agent can pause to ask the user for clarification, and the user can send steering instructions to the agent mid-run
**Plans:** 2 plans

Plans:
- [x] 06-01-PLAN.md -- Frontend build fix (remove HITL/QA dead code), ChatMessage model + API (DASH-01..07, CHAT-01)
- [ ] 06-02-PLAN.md -- Agent pause mechanism, interactive chat UI, SSE wiring, pre-run input (CHAT-02, CHAT-03, CHAT-04)

### Phase 7: End-to-End Validation
**Goal**: The analytics-teaser workflow runs on a real client with real data, produces a viewable deliverable, and memory compounds on a second run -- proving the complete v3.0 system works
**Depends on**: Phase 6 (full UI)
**Requirements**: VALD-01, VALD-02
**Success Criteria** (what must be TRUE):
  1. The analytics-teaser workflow executes end-to-end on real client data -- from dashboard trigger through Agent SDK execution to rendered HTML deliverable
  2. The deliverable is viewable in the dashboard with full provenance (which agents ran, which phases completed)
  3. A second run of the same workflow for the same client shows evidence of memory compounding -- the agent references findings from the first run
**Plans**: TBD

Plans:
- [ ] 07-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7
(Phase 5 can begin in parallel with Phase 4 -- no dependency between them)

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Strip Infrastructure & Dependencies | v3.0 | 0/2 | Planning complete | - |
| 2. Model Simplification | 2/2 | Complete   | 2026-03-12 | - |
| 3. Tool Migration | 4/5 | Gap closure | - |
| 4. Executor Rewrite | v3.0 | Complete    | 2026-03-13 | 2026-03-13 |
| 5. Memory Rewiring | v3.0 | 1/4 | In Progress | - |
| 6. Dashboard & Chat | v3.0 | 0/2 | Planning complete | - |
| 7. End-to-End Validation | v3.0 | 0/? | Not started | - |

---
*Roadmap created: 2026-03-06*
*v3.0 roadmap added: 2026-03-12*

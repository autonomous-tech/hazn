# Feature Research: v3.0 Personal Multi-Client Workflow Runner

**Domain:** Personal multi-client AI workflow runner for marketing agency
**Researched:** 2026-03-12
**Confidence:** HIGH (existing codebase analyzed, domain patterns verified, Anthropic API docs confirmed)

---

## Context: What Already Exists

v2.0 shipped ~60,600 LOC of enterprise infrastructure. v3.0 strips it to personal-tool essentials. This research focuses exclusively on what the simplified tool needs.

**Infrastructure that stays (reusable):**
- Django 5.2 backend + Next.js 15 frontend + Docker Compose (Postgres 17/pgvector, Letta, Vault, Redis)
- `EndClient` model, `BrandVoice`, `Keyword`, `Audit`, `Campaign`, `Decision` models
- `WorkflowRun`, `WorkflowAgent`, `WorkflowPhaseOutput` models
- `Deliverable` model with `html_content`, `markdown_source`
- `HaznMemory` abstraction (Letta integration, search, correction, learning buffer, context assembly)
- `CraftLearning` + `StructuredFinding` Pydantic types
- Jinja2 deliverable renderer + templates
- `send_workspace_event()` SSE helper (django-eventstream)
- `WorkflowCatalogView` (reads YAML definitions)
- Frontend components: `phase-stepper.tsx`, `workflow-card.tsx`, `deliverable-card.tsx`, `memory-search.tsx`, `status-cards.tsx`, `activity-timeline.tsx`
- 7 YAML workflow definitions, 15 agent .md definitions, 25+ skill files

**Infrastructure that gets stripped:**
- 4 MCP servers (hazn-memory, vercel, github, ga4-gsc-pagespeed)
- `HITLItem` model and full HITL queue system
- QA scoring pipeline (stub was never real anyway)
- `Agency` multi-tenant scoping + `IsAgencyMember` permission
- Dual runtime (Agent SDK path)
- Budget enforcement / cost caps / credit system
- Langfuse metering pipeline
- Session/checkpoint turn counter system
- Conflict detection (L2 vs L3)
- Data lifecycle / GDPR deletion scheduling

---

## Table Stakes

Features Rizwan needs from day one. Missing any of these means the tool cannot replace manual workflow execution.

### 1. Client Management (Simplified)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Client list with CRUD | Must see all 8+ clients, add new ones, edit details | LOW | `EndClient` model exists. Simplify: keep single hard-coded Agency as "self" (or drop FK entirely). `EndClientViewSet` has full CRUD. Strip `IsAgencyMember` to simple session auth. |
| Client detail view | See client name, competitors, brand voice, last workflow run, deliverable count | LOW | Combine existing `EndClient` fields + aggregate queries from `WorkflowRun` and `Deliverable`. |
| Per-client context fields | Competitors list, brand voice reference, site URL, GA4 property ID | LOW | `EndClient.competitors` (JSONField) exists. Add minimal fields for site URL and analytics IDs. Brand voice stored separately in `BrandVoice` model with pgvector embedding. |

**Confidence:** HIGH. CRUD is trivial. Most work is removing enterprise scoping, not building new features.

### 2. Simplified Workflow Executor (THE critical new piece)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| YAML-to-Anthropic-API execution | Read workflow YAML, chain phases, run each phase as an Anthropic API tool_use loop | HIGH | This replaces the entire v2.0 executor + MCP servers + dual runtime. Core pattern: `while response.stop_reason == "tool_use": execute_tools(); send_results()`. Anthropic docs confirm this as the standard agentic loop. |
| Agent system prompt loading | Parse agent .md files, inject as system prompt per phase | LOW | 15 agent files in `hazn/agents/`. Each becomes the system prompt for that phase's API call. Straightforward file read + string concatenation with skill files. |
| Skill injection into context | Workflow YAML declares `skills: [analytics-audit]`. Load skill .md and append to agent prompt. | LOW | Skill files in `hazn/skills/`. Concatenate with agent system prompt. Watch context window limits -- skills can be 2-5K tokens each. |
| Python function tools | Tools called by agents as native Python functions, not MCP indirection | MEDIUM | Must implement: GA4 data collection, GSC data collection, PageSpeed API, file read/write, web fetch, code execution. These were 4 MCP servers; now they are Python functions with Anthropic tool schemas. Reuse existing Python scripts in `hazn/scripts/`. |
| Phase-to-phase output passing | Phase N's output becomes Phase N+1's input context | MEDIUM | Executor tracks completed phase outputs. Downstream phases receive prior outputs as context in the user message. Existing `depends_on` YAML field declares dependencies. |
| Client context injection per run | Before first phase, load client's brand voice, keywords, campaigns, competitors | MEDIUM | `HaznMemory.load_client_context()` assembles JSON from Django ORM. For v3.0: inject this JSON as part of the system prompt prefix, not as a Letta block write. Dual path: still write to Letta for memory persistence, AND inject into Anthropic API system prompt for immediate context. |
| Structured output capture | Each phase produces structured output stored in `WorkflowPhaseOutput` | MEDIUM | Agent's final response must be structured (JSON or structured content). Use Anthropic API structured output or parse agent response. Store in `WorkflowPhaseOutput.content` JSONField. |
| Async execution via Celery | Workflows run in background, don't block HTTP request | LOW | Existing pattern: `WorkflowTriggerView` creates `WorkflowRun`, dispatches Celery task, returns run ID. Keep this exact pattern with new executor as the task body. |

**Confidence:** HIGH. The Anthropic API tool_use loop is well-documented (official docs verified). The pattern is: `messages.create()` with tools -> check `stop_reason` -> execute tools -> append results -> repeat. The Python SDK also offers a `tool_runner` that automates this loop.

### 3. Workflow Triggering

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Select client + workflow, trigger run | Core interaction loop. Pick from dropdown, hit run. | LOW | `WorkflowTriggerView` exists. Simplify: strip agency validation. Keep Celery dispatch pattern. |
| Workflow catalog with descriptions | See all 7 available workflows before triggering | LOW | `WorkflowCatalogView` exists, scans `hazn/workflows/*.yaml`. Returns name, description, phases, estimated duration. Keep as-is. |
| Immediate run feedback | After triggering, immediately see run ID and status | LOW | Existing: returns `run_id` + `celery_task_id`. Frontend navigates to run detail view. |

**Confidence:** HIGH. Already built, just needs permission simplification.

### 4. Real-Time Progress Monitoring

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Phase-level progress via SSE | See which phase is running, which completed, which upcoming | MEDIUM | `send_workspace_event()` + django-eventstream exist. New executor must emit events: `phase_started`, `phase_completed`, `workflow_completed`, `workflow_failed`. Frontend `phase-stepper.tsx` consumes these. |
| Agent activity indicator | "Agent: seo-specialist analyzing meta tags..." | MEDIUM | Emit SSE event with agent name + current action when tool calls happen. This is what makes monitoring useful vs. a generic spinner. |
| Elapsed time per phase | How long each phase has been running | LOW | `WorkflowAgent.started_at` / `ended_at` exist. Emit start time in SSE event, frontend computes elapsed. |
| Error notification | When a phase fails, push error detail via SSE | LOW | Emit `phase_failed` event with error message. Frontend shows inline error in phase stepper. |

**Confidence:** HIGH. SSE for AI agent progress is a well-established pattern. n8n recently added this exact capability (tool-call-start/end events via SSE). The infrastructure exists; the new executor just needs to emit events at the right points.

### 5. Deliverable Management

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| View deliverables per client | List all deliverables for a client, newest first | LOW | `Deliverable` model + `DeliverableViewSet` exist. Simplify: drop QA verdict/approval pipeline. A deliverable is either "complete" or "not yet". |
| View HTML report | Click to see rendered HTML deliverable in browser | LOW | `DeliverableHTMLView` serves `html_content` as `text/html`. Keep as-is. |
| Download deliverable | Download HTML report as file | LOW | Add `Content-Disposition: attachment` header option to `DeliverableHTMLView`. Trivial. |
| Share link generation | Generate time-limited public URL for client viewing | LOW | `ShareLink` model + share action exist. Keep the 30-day expiring token pattern. |
| Deliverable metadata | See which workflow, phase, client, and date produced the deliverable | LOW | FK relationships already exist: `Deliverable -> WorkflowRun -> EndClient`. Surface in UI. |

**Confidence:** HIGH. Mostly already built. Main work is simplifying the approval status field from 5 states to 2 (complete/incomplete).

### 6. Per-Client Persistent Memory

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| One Letta agent per client | Each client has isolated persistent memory | HIGH | Letta docs confirm: one agent per subject (client). Agent created on first workflow run for that client. `HaznMemory` abstraction already handles agent creation and lifecycle. Per Letta architecture, all state persists in the database. |
| Brand voice accumulation | Agent learns and refines brand voice across runs | HIGH | `CraftLearning` with `source=agent-inferred` + `confidence` scoring exists. The simplified executor must call `HaznMemory.add_learning()` when agents discover brand patterns. Learnings stored in Letta archival memory with metadata tags. |
| Keyword and finding persistence | SEO keywords, audit findings, campaign decisions stored structurally in Postgres | MEDIUM | `write_finding()` dispatcher to `Keyword`/`Audit`/`Campaign`/`Decision` models exists. Executor must call `HaznMemory.write_finding()` at phase boundaries when agents produce structured data. |
| Context loading at run start | At workflow start, load client context (brand voice, keywords, campaigns) into agent context | MEDIUM | `HaznMemory.load_client_context()` + `_assemble_context()` exist. Produces ~2-4KB JSON with agency, client, brand_voice, active_campaigns, top_keywords. For v3.0: inject this as system prompt prefix AND write to Letta block for memory persistence. |
| Memory search | Semantic search over what the system remembers about a client | MEDIUM | `HaznMemory.search_memory()` with composite ranking (similarity 0.6 + recency 0.25 + confidence 0.15) exists. Agents can search during execution; Rizwan can search via Memory Inspector. |
| Learning flush at phase boundaries | After each phase completes, flush accumulated learnings to persistent memory | LOW | Simplify from v2.0 turn-counter (every 10 turns) to phase-boundary flush. Call `checkpoint_sync()` after each phase completes. Simpler, fewer edge cases, adequate granularity for 3-8 phase workflows. |

**Confidence:** HIGH for the abstraction (HaznMemory is well-built and tested). MEDIUM for compounding quality -- the value compounds over time but requires agents to correctly identify and articulate learnings. This is the core differentiator per PROJECT.md: "every engagement builds on past decisions."

### 7. Workflow Run History

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Run list per client | See all past workflow runs for a client with status, duration, cost | LOW | `WorkflowRunViewSet` exists with `WorkflowRunFilter` (by client, workflow name, status). Keep read-only list/detail. |
| Run detail view | See phases, agents, outputs, error details for a specific run | LOW | `WorkflowRunDetailSerializer` includes nested agents, tool_calls, phase_outputs. Keep as-is. |
| Cost per run | Total tokens and estimated cost for each run | LOW | `WorkflowRun.total_tokens` and `total_cost` fields exist. Populate from Anthropic API response `usage` metadata after each LLM call. |

**Confidence:** HIGH. Already built, just needs data from real runs.

### 8. Error Handling and Visibility

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Phase-level error details | When a phase fails, see the error message and stack trace | LOW | `WorkflowRun.error_details` JSONField exists. Populate with phase_id, agent, error_type, message, traceback. |
| Run-level status | Clear status: pending, running, completed, failed | LOW | `WorkflowRun.Status` choices exist. Executor sets status as phases progress. |
| Graceful failure handling | When a phase fails, save whatever learnings were accumulated, mark run as failed, don't lose work | MEDIUM | Simplified from v2.0 `failure_sync()`. At minimum: on exception, flush pending learnings to Letta with `partial_sync` tag and reduced confidence. Save phase outputs for completed phases. |

**Confidence:** HIGH. Standard error handling. The key insight from v2.0 is `failure_sync()` -- never discard accumulated learnings on failure.

---

## Differentiators

Features that make Hazn uniquely valuable vs. running Claude manually or using generic tools like n8n/CrewAI/Dify.

### 1. Compounding Client Memory (THE differentiator)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Cross-run knowledge accumulation | Run 1 learns brand voice. Run 2 refines it. Run 5 produces work that feels like a dedicated team member who has been with the client for months. No generic AI tool does this. | HIGH | The `CraftLearning` system with provenance (`agent-inferred`, `rule-extracted`, `user-explicit`), confidence scoring, and metadata tags is already built. The challenge is making the new Anthropic API executor properly identify and write learnings. |
| Memory-driven quality improvement | Each SEO audit builds on prior keyword research. Each blog post builds on prior brand voice learnings. Quality compounds without manual context copying. | HIGH | Requires agents to: (1) load prior context via `load_client_context()`, (2) search memory for relevant learnings via `search_memory()`, (3) write new learnings via `add_learning()`. All three are implemented in `HaznMemory`. |
| Memory correction | Rizwan can fix wrong memories before they compound into future runs | MEDIUM | `HaznMemory.correct_memory()` with soft-delete + replacement + audit trail in `MemoryCorrection` model exists. `MemoryInspectorView` + frontend components exist. |

### 2. Marketing-Domain Agent Library

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| 15 specialized marketing agents | Not "write me a blog post" but a dedicated SEO Specialist who runs technical checklists, checks structured data, validates Core Web Vitals. Deep domain expertise encoded in system prompts. | LOW (exists) | Agent .md files contain 100-400 lines of domain instructions each. Example: `seo-specialist.md` has full audit process, meta tag templates, structured data examples, keyword strategy framework. |
| 7 pre-built workflow DAGs | Complete marketing workflows from strategy to delivery, not ad-hoc prompting | LOW (exists) | YAML definitions with phase dependencies, agent assignments, checkpoint recommendations, estimated durations. Analytics audit: 5 phases (setup -> data-collection -> analysis -> review -> delivery). Website: 8 phases. |
| Adversarial review pattern | produce -> adversary review -> revise. Built into analytics-audit workflow. Quality assurance through agent disagreement. | LOW (exists) | `analytics-adversary` agent reviews the report writer's output before client delivery. This naturally produces higher quality than single-pass generation. |

### 3. Branded Professional Deliverables

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| HTML report templates | Client-ready reports, not raw markdown dumps | LOW (exists) | Jinja2 pipeline in `deliverable_pipeline/`. Templates with XSS prevention (autoescape). `AuditReportPayload` schema validates data before rendering. |
| Share link system | Send clients a branded report URL, not an email attachment | LOW (exists) | `ShareLink` with 32-byte token, 30-day expiry. `share_views.py` serves the deliverable at `/share/{token}/`. |

### 4. Phase-Level Progress Transparency

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Not just "running" but "Phase 3/5: SEO -- analyzing meta tags" | Meaningful progress information vs. a generic spinner. Rizwan can see exactly what the system is doing and estimate time remaining. | MEDIUM | SSE events with phase name, agent name, current tool being called. Frontend `phase-stepper.tsx` already renders this. The differentiator is granularity -- n8n shows node execution but not agent-level tool calls. |

### 5. Cross-Client Insights (from Postgres structured data)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Query structured findings across all clients | "What keywords are all my clients targeting?" "Which audits scored lowest?" Queryable marketing intelligence across the portfolio. | MEDIUM | `HaznMemory.search_cross_client_insights()` exists, queries `Keyword`, `Audit`, `Campaign`, `Decision` across sibling clients. For personal tool: all clients are siblings (same agency). This becomes a portfolio intelligence dashboard. |

---

## Anti-Features

Features to explicitly NOT build. These were either already built in v1/v2 and proven over-engineered, or are tempting but wrong for a personal tool.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **HITL approval queue** | "Review before publishing" | Already built, full UI. For a single user, this is ceremony. Rizwan opens deliverables and reviews directly. Queue adds clicks without value. | View deliverables directly. Re-run if unsatisfied. |
| **QA scoring pipeline** | "Automated quality checks" | Built with 6 task-type criteria + 48-hour lifecycle. Adds latency and complexity. The user IS the quality gate. | Rizwan reviews deliverables. If bad, re-trigger. |
| **Conflict detection (L2 vs L3)** | "Memory layer conflicts" | Built for multi-tenant. Single user = zero conflicts. No L2 agency overriding L3 client decisions. | Remove entirely. |
| **Budget enforcement / hard caps** | "Don't overspend on API calls" | Complex credit system, agency caps, runaway detection, circuit breakers. For personal use: track costs, display them, trust the user. | Show cost per run in UI. Log `total_tokens` and `total_cost`. Rizwan decides when to stop. |
| **Dual runtime (Agent SDK + API)** | "Use max subscription for Mode 1" | Massive complexity maintaining two execution paths. One execution path is simpler, debuggable, consistent. | Anthropic API only, tool_use loop. |
| **MCP server indirection** | "Standardized tool protocol" | 4 MCP servers built. For single-user Python backend, direct function calls are simpler, faster, easier to debug. No IPC overhead, no protocol serialization. | Python function tools called directly in the agentic loop. |
| **Multi-tenant agency-scoping** | "Other agency users" | Every view, serializer, permission class scoped by `request.user.agency`. One user = one "agency". | Strip `IsAgencyMember`. Simple session auth or even no auth (localhost only). |
| **Langfuse metering pipeline** | "Observability at scale" | Production observability for SaaS. A running-cost field on WorkflowRun is sufficient for personal tracking. | Log costs to `WorkflowRun` model fields. Keep Langfuse for debugging agent behavior during development only if desired. |
| **Turn-based checkpoint system** | "Checkpoint every 10 turns" | Complex `record_turn()` + checkpoint every 10 turns + failure_sync. For 3-8 phase workflows: flush at phase boundaries, not turn boundaries. | `checkpoint_sync()` called after each phase completes. Simpler, equally effective. |
| **Data lifecycle / GDPR** | "90-day retention, deletion scheduling" | `deletion_requested_at`, `deletion_scheduled_at`, `churned_at` fields and background tasks. Personal tool = Rizwan owns all data. | Remove lifecycle fields and background tasks. |
| **Real-time collaboration** | "Multiple people watching" | SSE channels scoped by agency. Single user = single viewer. No need for channel isolation. | Keep SSE for the one user. Simplify channel to global. |
| **Automatic model downgrade** | "Switch to Haiku when budget low" | Novel but untested. Produces unpredictable quality drops mid-workflow. | Use per-agent model selection (declared in agent .md). Static, predictable. |
| **Workflow resume after interruption** | "Resume from where it stopped" | Complex: persist wave state, detect partial completion, skip completed phases, re-inject context. For personal tool: re-run the whole workflow. Runs are 3-6 hours max. Memory persists, so re-runs benefit from prior learning. | Re-run from start. Completed phases' learnings are already in memory. |

---

## Feature Dependencies

```
Client CRUD
    +--requires--> Per-Client Workflow Trigger
                       +--requires--> Simplified Workflow Executor (YAML -> Anthropic API loop)
                       |                   +--requires--> Agent System Prompt Loading (from .md files)
                       |                   +--requires--> Skill Injection (from skill .md files)
                       |                   +--requires--> Python Function Tools (GA4, GSC, PageSpeed, etc.)
                       |                   +--requires--> Per-Client Memory Injection (HaznMemory)
                       |
                       +--requires--> Real-Time Progress (SSE events from executor)
                       |
                       +--produces--> WorkflowPhaseOutput (structured output per phase)
                       |                  +--enables--> Deliverable Rendering (Jinja2 -> HTML)
                       |                  |                 +--enables--> Deliverable View / Download / Share
                       |                  |
                       |                  +--enables--> Structured Finding Persistence (Keyword, Audit, etc.)
                       |
                       +--produces--> WorkflowRun record (status, cost, duration)
                       |                  +--enables--> Run History View
                       |                  +--enables--> Cost Tracking
                       |
                       +--produces--> CraftLearnings (via HaznMemory.add_learning)
                                          +--enables--> Compounding Memory (next run is better)

Per-Client Letta Agent
    +--enables--> Memory Inspector (search, view, correct)
    +--enables--> Context Loading (brand voice, keywords in system prompt)
    +--enables--> Learning Persistence (archival memory across runs)

Workflow Catalog (reads YAML files)
    +--enables--> Workflow Selection UI (cards on trigger page)
```

### Dependency Notes

- **Simplified Workflow Executor requires Agent Prompt Loading:** Each YAML phase specifies `agent: seo-specialist`. The executor loads `hazn/agents/seo-specialist.md` as the system prompt for that phase's Anthropic API call. Without this, agents are generic.
- **Simplified Workflow Executor requires Python Function Tools:** Agents need GA4 API, GSC API, PageSpeed API, file I/O, web fetch. These were MCP servers (4 of them). Now they become Python functions with Anthropic tool JSON schemas. This is the second-hardest piece after the executor loop itself.
- **Deliverable Rendering requires WorkflowPhaseOutput:** The Jinja2 renderer needs structured JSON from the delivery phase. The `AuditReportPayload` Pydantic schema validates the data before rendering. Agent output must conform to this schema.
- **Compounding Memory is additive, not blocking:** Runs 1-3 work fine without accumulated memory. Run 4+ starts to benefit. The value is emergent and increases over time. This means memory features can be built incrementally -- basic context loading first, learning accumulation second, memory correction third.
- **Python Function Tools can be built incrementally:** Start with file read/write + web fetch (needed for every workflow). Add GA4/GSC/PageSpeed tools when running analytics workflows. Add code execution when running development workflows.

---

## MVP Definition

### Launch With (v1 -- validates the core loop)

Minimum to run ONE workflow for ONE client and get a deliverable.

- [ ] **Client CRUD (simplified)** -- Create/edit/list clients. Hard-code single agency or remove FK. Reuse `EndClient` model.
- [ ] **Simplified workflow executor** -- Read YAML, chain Anthropic API tool_use loops per phase. This is the hardest and most important piece.
- [ ] **Agent prompt + skill loading** -- Parse .md files, inject as system prompt. Concatenate skills.
- [ ] **Core Python function tools** -- File read/write, web fetch. Minimum to run a non-analytics workflow.
- [ ] **Per-client Letta memory** -- One agent per client. `load_client_context()` at run start. `checkpoint_sync()` at phase boundaries.
- [ ] **Workflow trigger UI** -- Select client + workflow, hit run. Show run ID.
- [ ] **Progress monitoring (SSE)** -- Phase-level events: started, completed, failed.
- [ ] **Deliverable viewing** -- View completed HTML deliverables.
- [ ] **Run history** -- List past runs with status and cost.
- [ ] **Error display** -- Show which phase failed and why.

### Add After Validation (v1.x -- after 3-5 real client runs)

- [ ] **Analytics tools** -- GA4, GSC, PageSpeed Python functions. Trigger: when running analytics-audit workflow. Reuse existing scripts in `hazn/scripts/analytics-audit/`.
- [ ] **Memory inspector** -- Search client memory, view blocks, correct learnings. Trigger: after 5+ runs, need to verify accumulated knowledge.
- [ ] **Deliverable download + share links** -- Download HTML, generate public URL. Trigger: when sharing reports with clients.
- [ ] **Cross-run structured findings** -- Persist Keyword, Audit, Campaign, Decision to Postgres. Trigger: when wanting to query marketing data across runs.
- [ ] **Agent activity detail in progress** -- "seo-specialist calling PageSpeed API..." not just "Phase 3 running". Trigger: when wanting more transparency into long-running phases.
- [ ] **Cost tracking summary** -- Aggregate costs per client, per workflow type. Trigger: after 10+ runs to understand spending patterns.

### Future Consideration (v2+ -- after tool is daily driver for all 8+ clients)

- [ ] **Workflow re-run with phase skip** -- Re-run but skip already-completed phases. Why defer: full re-run works and benefits from compounded memory.
- [ ] **Batch execution** -- Same workflow across multiple clients. Why defer: validate per-client first.
- [ ] **Custom workflow authoring** -- Create new YAML from UI. Why defer: 7 workflows cover current needs. Edit YAML directly.
- [ ] **Cross-client portfolio dashboard** -- Aggregate insights across all clients. Why defer: need structured findings from 20+ runs first.
- [ ] **Webhook notifications** -- Slack/email on completion. Why defer: single user monitors directly.

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority | Existing Infrastructure |
|---------|------------|---------------------|----------|------------------------|
| Simplified workflow executor | HIGH | HIGH | P1 | Replaces `orchestrator/tasks.py` entirely |
| Per-client Letta memory | HIGH | MEDIUM | P1 | Reuses `HaznMemory` abstraction directly |
| Client CRUD (simplified) | HIGH | LOW | P1 | Simplifies existing `EndClientViewSet` |
| Agent prompt + skill loading | HIGH | LOW | P1 | New: file parsing, string concatenation |
| Core Python function tools | HIGH | MEDIUM | P1 | Replaces 4 MCP servers with Python functions |
| Workflow trigger UI | HIGH | LOW | P1 | Simplifies existing `WorkflowTriggerView` |
| Progress monitoring (SSE) | HIGH | MEDIUM | P1 | Reuses `send_workspace_event` + `phase-stepper.tsx` |
| Deliverable viewing | HIGH | LOW | P1 | Reuses `DeliverableHTMLView` + Jinja2 renderer |
| Run history | MEDIUM | LOW | P1 | Reuses `WorkflowRunViewSet` |
| Error display | MEDIUM | LOW | P1 | Reuses `WorkflowRun.error_details` |
| Workflow catalog | MEDIUM | LOW | P1 | Reuses `WorkflowCatalogView` as-is |
| Analytics tools (GA4/GSC) | HIGH | MEDIUM | P2 | Replaces ga4-gsc-pagespeed MCP server |
| Memory inspector | MEDIUM | MEDIUM | P2 | Reuses `MemoryInspectorView` + components |
| Share links | MEDIUM | LOW | P2 | Reuses `ShareLink` model |
| Cross-run findings | MEDIUM | MEDIUM | P2 | Reuses `write_finding()` dispatcher |
| Cost tracking summary | LOW | LOW | P2 | Reuses `WorkflowRun` cost fields |
| Agent activity SSE detail | MEDIUM | LOW | P2 | Enhancement to SSE events |
| Batch execution | LOW | HIGH | P3 | New feature |
| Custom workflows | LOW | MEDIUM | P3 | New feature |
| Portfolio dashboard | LOW | MEDIUM | P3 | New feature on existing models |

**Priority key:**
- P1: Must have for launch -- core loop: trigger, execute, monitor, deliver
- P2: Should have, add after core loop validated with 3-5 real client runs
- P3: Nice to have, future after tool is daily driver for all 8+ clients

---

## Competitor Feature Analysis

| Feature | n8n / Dify | CrewAI | Manual Claude (chat) | Hazn v3.0 |
|---------|------------|--------|---------------------|-----------|
| **Per-client persistent memory** | Not built-in. Must build custom vector store per client. | Session-scoped only. No cross-session persistence per client. | Copy-paste context every time. Degrades as client count grows. Lost between sessions. | Letta agent per client. Archival memory compounds across runs. Semantic search with composite ranking. |
| **Marketing domain agents** | Generic nodes. User builds from scratch. | Generic role definitions in Python. | User writes prompts each session. | 15 pre-built specialists with deep domain knowledge (SEO, copywriting, strategy, dev, QA). |
| **YAML workflow DAGs** | n8n has visual DAG. Dify has workflow canvas. Both general-purpose. | Python crew/task definitions. | No workflow concept. | 7 marketing-specific DAGs with agent assignment, skill injection, dependencies. |
| **Branded deliverables** | Raw output. User formats manually. | Raw output. | Raw output. | Jinja2 HTML templates, professional report formatting, share links. |
| **Multi-client management** | No client concept. One flow at a time. | No client concept. | User mentally tracks clients. Mixing up contexts is common. | Client list, per-client memory, per-client run history, per-client deliverables. |
| **Progress monitoring** | n8n: node execution view. Dify: run logs. | Terminal output only. | Watch the chat stream. | SSE real-time phase stepper with agent name, phase progress, elapsed time. |
| **Cost tracking** | n8n: execution count. Dify: token tracking. | No built-in tracking. | No tracking. | Per-run token/cost in database. Per-client aggregation. |
| **Self-hosted** | Both yes. | Yes. | No (SaaS). | Docker Compose. Fully self-hosted. Data stays local. |
| **Setup complexity** | n8n: moderate. Dify: moderate. | High (Python, custom code). | Zero. | Moderate (Docker Compose, YAML config). |
| **Adversarial review** | Must build manually. | Must define explicitly. | Must prompt manually. | Built into workflow YAML (analytics-adversary agent). |

**Key insight from competitor analysis:** No existing tool combines per-client persistent memory + domain-specific agents + YAML-defined workflows + branded deliverables. Each tool does 1-2 of these well. Hazn's value is the combination, tailored for marketing agency work.

---

## Sources

### Anthropic API (HIGH confidence -- official documentation)
- [Implement Tool Use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use) -- Agentic loop pattern, tool_use response handling
- [Streaming Messages](https://docs.anthropic.com/en/api/messages-streaming) -- SSE streaming from API
- [Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use) -- Programmatic tool calling, tool search

### Letta Memory (HIGH confidence -- official documentation)
- [Introduction to Stateful Agents](https://docs.letta.com/guides/agents/memory/) -- Memory blocks, persistence, multi-agent shared state
- [Core Concepts](https://docs.letta.com/core-concepts/) -- Agents, runs, tools, memory blocks
- [Learning SDK](https://github.com/letta-ai/learning-sdk) -- Per-subject learning, memory block management
- [Conversations API](https://www.letta.com/blog/conversations) -- Shared agent memory across concurrent experiences (Jan 2026)

### SSE Progress Monitoring (MEDIUM confidence -- community patterns verified against n8n implementation)
- [Streaming AI Agent Responses with SSE](https://akanuragkumar.medium.com/streaming-ai-agents-responses-with-server-sent-events-sse-a-technical-case-study-f3ac855d0755) -- FastAPI + Celery + Redis SSE pattern
- [n8n SSE for AI Agent Tool Calls](https://github.com/n8n-io/n8n/pull/20499) -- tool-call-start/end events, node execution tracking

### Marketing Agency Automation (MEDIUM confidence -- industry analysis)
- [Marketing Automation for Agencies 2026 Playbook](https://www.enrichlabs.ai/blog/marketing-automation-for-agencies-2026-playbook) -- One account manager can oversee 8-12 clients with AI automation
- [AI Workflow Automation Trends 2026](https://www.cflowapps.com/ai-workflow-automation-trends/) -- Autonomous intelligent systems trend

### Workflow Patterns (MEDIUM confidence -- multiple sources agree)
- [Dagu Workflow Engine](https://github.com/dagu-org/dagu) -- YAML DAG execution pattern (self-contained, single binary)
- [State of Workflow Orchestration 2025](https://www.pracdata.io/p/state-of-workflow-orchestration-ecosystem-2025) -- AI/LLM integration as major trend
- [Agentic Workflow Patterns 2025](https://skywork.ai/blog/agentic-ai-examples-workflow-patterns-2025/) -- 20 patterns including orchestrator-worker

### Existing Codebase (HIGH confidence -- direct code review)
- `hazn_platform/hazn_platform/core/memory.py` -- HaznMemory abstraction, full implementation
- `hazn_platform/hazn_platform/orchestrator/models.py` -- WorkflowRun, WorkflowAgent, WorkflowPhaseOutput
- `hazn_platform/hazn_platform/workspace/views.py` -- All workspace API endpoints
- `hazn_platform/hazn_platform/workspace/sse_views.py` -- SSE event helper
- `hazn_platform/hazn_platform/deliverable_pipeline/renderer.py` -- Jinja2 HTML renderer
- `hazn_platform/hazn_platform/qa/models.py` -- Deliverable model
- `hazn/workflows/*.yaml` -- 7 workflow definitions
- `hazn/agents/*.md` -- 15 agent definitions

---
*Feature research for: Personal multi-client AI workflow runner (v3.0 Strip & Simplify)*
*Researched: 2026-03-12*

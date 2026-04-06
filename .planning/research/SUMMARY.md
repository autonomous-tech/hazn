# Project Research Summary

**Project:** Hazn Platform — v3.0 Strip & Simplify
**Domain:** Personal multi-client AI workflow runner for marketing agency
**Researched:** 2026-03-12
**Confidence:** HIGH

## Executive Summary

Hazn v2.0 shipped approximately 60,600 LOC of enterprise-grade infrastructure: multi-tenant agency scoping, MCP server tool dispatch, HITL approval queues, QA pipelines, Langfuse metering, dual runtimes, conflict detection, and budget enforcement. None of that complexity serves the actual deployment — one user (Rizwan) running marketing workflows for 8+ clients. The v3.0 milestone is a subtraction project, not a construction project. Every core capability already exists; the work is removing layers of indirection and enterprise scaffolding while preserving the stack that genuinely works.

The recommended approach is to keep the existing Django/Next.js/Celery/Letta/Postgres stack without alteration, keep the 7 workflow YAMLs, 15 agent personas, and 25+ skill definitions untouched, and focus all effort on three rewrites: (1) replace the 4 MCP servers with a flat Python function tool registry (~13 tools), (2) rewrite the 590-line executor as a ~150-line YAML phase walker that calls the Anthropic API directly, and (3) simplify HaznMemory to one Letta agent per client with two memory blocks instead of the L2/L3 hierarchy. The only new dependency is declaring `anthropic>=0.84.0` explicitly in pyproject.toml — it was already imported but never declared.

The key risks are all sequencing risks, not capability risks. Django migrations will fail if model fields are removed before their FK dependents are handled. The executor import chain will crash Django startup if any of the 7 enterprise modules it imports are deleted before their imports are removed. MCP server tool implementations will be lost if the files are deleted before the logic is extracted into Python functions. The safe path is a strict deletion order: field removals before model deletions, import cleanup before file deletion, extraction before replacement. Follow this order and the transition is mechanical. Violate it and recovery is expensive.

## Key Findings

### Recommended Stack

The existing stack requires almost no change. Django 5.2, DRF 3.16, Next.js 15, Celery 5.6, Postgres 17 + pgvector, Letta (Docker Compose), and Vault all stay. The `letta-client>=1.7.12` SDK covers all per-client memory patterns. The `anthropic>=0.84.0` SDK covers the tool_use loop with proper parallel dispatch via `asyncio.gather`. The workflow engine uses stdlib `graphlib.TopologicalSorter` for DAG wave computation and PyYAML + Pydantic (both transitive, already present) for YAML loading and validation.

**Core technologies:**
- `anthropic>=0.84.0`: Anthropic Messages API tool_use loop — the only missing explicit dependency; handles multi-turn agent execution with parallel tool dispatch
- `letta-client>=1.7.12`: Per-client persistent memory — one Letta agent per client with `client_profile` (persistent) and `active_task` (wiped per run) blocks
- `PyYAML` + `pydantic` + `graphlib`: Workflow engine — load YAML, validate via Pydantic, execute phases in topological order; all already present transitively
- Django 5.2 + DRF 3.16: Backend API and data layer — keep exactly as-is
- Celery 5.6 + Redis: Async workflow execution — keep; adequate for single-user personal tool
- Next.js 15: Frontend — keep existing components (phase-stepper, workflow-card, deliverable-card, memory-search, status-cards); strip HITL/approvals pages only

**Remove from stack:**
- `fastmcp>=3.1.0`: MCP servers replaced by Python functions — remove after extraction
- `langfuse>=3.14.0`: Metering removed; token totals stored on WorkflowRun model
- `openai>=1.0.0`: Was for Letta server config, not used by platform code directly

### Expected Features

The full P1 feature set already exists in code and needs simplification, not construction.

**Must have (table stakes — P1):**
- Client CRUD (simplified): `EndClientViewSet` exists; strip `IsAgencyMember` to `IsAuthenticated`; keep Agency as singleton — removing it breaks 30+ files across 6 apps
- Simplified workflow executor: The hardest piece; replace 590-line executor with ~150-line YAML phase walker calling Anthropic API directly with flat tool registry
- Agent prompt + skill loading: `PromptAssembler` exists and works unchanged; reads agent .md + skill SKILL.md + client context
- Core Python function tools (~13): Replace 4 MCP servers; memory tools (search_memory, write_finding, load_context), analytics (GA4, GSC, PageSpeed), GitHub (create_repo, create_pr, merge_pr), Vercel (deploy_project, get_preview_url)
- Per-client Letta memory: `HaznMemory` abstraction exists; simplify to one agent per `client_id`, two memory blocks, checkpoint at phase boundaries (not turn boundaries)
- Workflow trigger UI: `WorkflowTriggerView` + `WorkflowCatalogView` exist; simplify permission check only
- Real-time progress via SSE: `send_workspace_event()` + `phase-stepper.tsx` exist; executor must emit `phase_started`, `phase_completed`, `workflow_completed`, `workflow_failed`
- Deliverable viewing: `DeliverableHTMLView` + Jinja2 renderer exist; strip QA approval states to complete/incomplete only
- Run history: `WorkflowRunViewSet` exists with filtering; keep read-only
- Error display: `WorkflowRun.error_details` JSONField exists; populate from executor on failure

**Should have (P2 — add after 3-5 real client runs):**
- Analytics tool functions (GA4/GSC/PageSpeed): Rewrite ga4-gsc-pagespeed MCP server as Python functions; implementation logic lives in existing MCP server files
- Memory inspector: `MemoryInspectorView` + `memory-search.tsx` exist; re-enable after executor validates memory writes
- Deliverable share links: `ShareLink` model + `share_views.py` exist; re-enable after core loop is validated
- Cross-run structured findings: `write_finding()` dispatcher to Keyword/Audit/Campaign/Decision models exists
- Agent activity SSE detail: Enhancement to existing SSE events — emit tool call name and progress within phases

**Defer (v2+):**
- Workflow resume from interrupted phase: re-run is acceptable; memory persists so re-runs benefit from prior learning
- Batch execution across multiple clients simultaneously
- Custom workflow authoring via UI (YAML editing works for 7 existing workflows)
- Cross-client portfolio dashboard (needs 20+ runs of structured findings first)

**Anti-features (explicitly do not build):**
- HITL approval queue, QA scoring pipeline, conflict detection, budget enforcement, dual runtime, MCP servers, multi-tenant agency scoping, Langfuse metering, turn-based checkpoints, GDPR/data lifecycle scheduling

### Architecture Approach

The v3.0 architecture simplifies the existing layered system to a single execution path. The data flow is: Next.js UI triggers a Django API endpoint which creates a WorkflowRun and dispatches a Celery task. The Celery worker loads the workflow YAML, computes execution waves via TopologicalSorter, and for each phase: assembles a system prompt (PromptAssembler), loads client memory from Letta (HaznMemory), runs the Anthropic API tool_use loop (simplified AnthropicAPIBackend), collects output (OutputCollector), stores a WorkflowPhaseOutput, renders a Deliverable if delivery phase, and emits an SSE event. After all phases, memory is checkpointed and the run is marked complete. The key architectural decision is keeping `Agency` as a singleton rather than removing it — it is referenced in 30+ files and removing it cascades across 6 Django apps plus the frontend with no benefit.

**Major components:**
1. `ToolRegistry` (NEW — replaces `tool_router.py` + `tool_wiring.py` + 4 MCP servers): Simple dict of tool name to Python async function; collapses 3 layers of MCP indirection into a flat registry
2. `SimpleExecutor` (REWRITE of `executor.py`): ~150 lines; YAML phase walker with Anthropic API agent loop; no conflict detection, HITL, QA, metering, or Langfuse
3. `HaznMemory` (SIMPLIFY — L2/L3 interface parameters preserved): One Letta agent per `client_id`; `client_profile` block persists across runs; `active_task` block wiped per run; archival tag format `[client:uuid]` must not change
4. `AnthropicAPIBackend` (SIMPLIFY — keep tool_use loop, remove BudgetEnforcer + MeteringCallback): Core agentic loop already architecturally correct; parallel tool dispatch via `asyncio.gather`
5. Django API + Workspace Views (SIMPLIFY): Keep WorkflowTriggerView, WorkflowCatalogView, WorkflowRunViewSet, DeliverableViewSet; remove HITLItemViewSet and MemoryInspectorView (P2 re-add); simplify to `IsAuthenticated`
6. Next.js UI (SIMPLIFY): Keep layout, auth, workflow trigger, run monitor, deliverables; remove approvals page; update `api.ts` types in lockstep with backend changes

**Keep unchanged (zero modification needed):**
- `orchestrator/workflow_parser.py` + `workflow_models.py`: YAML loading, Pydantic validation, DAG — works exactly as needed
- `orchestrator/prompt_assembler.py`: Agent persona + skill + client context assembly — no enterprise dependencies
- `orchestrator/output_collector.py`: Markdown artifact extraction — self-contained, no external deps
- `deliverable_pipeline/renderer.py` + `schemas.py`: Jinja2 HTML rendering — no enterprise deps
- `hazn/workflows/*.yaml`, `hazn/agents/*.md`, `hazn/skills/*/SKILL.md`: Core domain assets — untouched

### Critical Pitfalls

1. **Django migration FK constraint violations (Pitfall 1)** — Remove model FIELDS first (generate + apply migration), then remove MODEL CLASSES in a second migration wave. Test on a DB copy before applying. Specifically: `Deliverable.hitl_item` FK to `HITLItem` must be cleared before `HITLItem` model class can be dropped. Never delete migration files from history.

2. **Agency removal cascade (Pitfall 2)** — Do NOT remove the `Agency` model. It is referenced in 30+ files across 6 Django apps and the frontend. Keep Agency as a singleton (one row). The simplification is operational (one agency exists), not structural (FK relationships stay). This is the single most important architectural decision of v3.0.

3. **MCP server tool logic loss (Pitfall 3)** — The MCP server files (`mcp_servers/*.py`) contain the actual GA4, GSC, PageSpeed, GitHub, and Vercel API integration code. The `ToolRouter` has only `callable=None` placeholders. Extract Python functions from MCP server modules BEFORE deleting the files. Delete MCP files only after replacement functions are tested end-to-end.

4. **Executor import chain crash (Pitfall 4)** — `executor.py` imports from 13 modules including 7 being removed (budget, conflict_detector, hitl, metering, tracing, qa/runner, qa/staging). Deleting any without first removing its import crashes Django startup at import time — not a runtime error, an app-won't-start error. Rewrite `executor.py` from scratch rather than surgically modifying the existing 590-line file.

5. **Frontend type drift (Pitfall 5)** — `frontend/src/types/api.ts` has 14 interfaces mirroring backend model shapes. When `HITLItem`, `Deliverable.qa_verdict`, `WorkflowRun.conflict_log` are removed from the backend, the frontend compiles but renders broken UI (TypeScript optional chaining hides the errors). Update `api.ts` in the same commit as backend serializer changes. Run `npm run build` as a CI check after every backend model change.

## Implications for Roadmap

Based on the dependency analysis and safe deletion order from PITFALLS.md, the natural phase structure follows strict sequencing constraints. Phases cannot be reordered without triggering the critical pitfalls.

### Phase 1: Infrastructure and Dependency Cleanup
**Rationale:** Must come first. Code must be cleaned before packages are removed. Langfuse module-level imports crash Django if the package is removed while imports remain (Pitfall 7). Enterprise Celery periodic tasks (GDPR deletion, data retention) must be disabled before management commands are deleted (Pitfall 14). Docker Compose cleanup must happen last — code changes first, infrastructure last (Pitfall 10). This phase has no user-visible impact; it is foundation clearing.
**Delivers:** Langfuse imports removed from metering.py and all importers; enterprise Celery periodic tasks disabled; `anthropic>=0.84.0` declared in pyproject.toml; `fastmcp` and `langfuse` removed from pyproject.toml; Docker Compose updated to remove Langfuse service
**Addresses:** Pitfall 7 (Langfuse module crash), Pitfall 10 (Docker service removal order), Pitfall 14 (management commands referencing enterprise features)
**Avoids:** Package removal before import cleanup; infrastructure teardown before code is stable

### Phase 2: Model Simplification (Two-Wave Migration Strategy)
**Rationale:** Must happen before executor rewrite. The executor and workspace views reference Django models; if models change shape during executor rewrite, two systems break simultaneously. The two-wave strategy (fields first, then models) prevents FK constraint failures that cascade across the `qa` and `orchestrator` apps.
**Delivers:** Enterprise fields removed from WorkflowRun (conflict_log, langfuse_trace_id) and Deliverable (hitl_item FK, qa_verdict, qa_score, qa_report, approval_status to 2-state); HITLItem model removed after FK cleared; Agency preserved as singleton; WorkflowAgent and WorkflowToolCall models evaluated for removal; clean migration history; `IsAgencyMember` replaced with `IsAuthenticated`
**Addresses:** Pitfall 1 (migration FK constraints), Pitfall 2 (Agency removal cascade), Pitfall 9 (workspace permissions)
**Avoids:** Running model class removals before FK fields are cleared in a prior migration

### Phase 3: Tool Migration (MCP to Python Functions)
**Rationale:** Must happen before executor rewrite. The new executor needs the ToolRegistry to exist before it can reference it. This phase carries the highest risk of irreversible logic loss — the MCP server files contain Google API, GitHub API, and Vercel API integration code that cannot be recovered without git history once deleted.
**Delivers:** New `orchestrator/tool_registry.py` (ToolRegistry class with `dispatch()` and `get_anthropic_tools()`); 13 Python function tools extracted from 4 MCP server modules; GA4/GSC/PageSpeed functions from `analytics_server.py`; memory functions (delegating to HaznMemory) from `hazn_memory_server.py`; GitHub functions from `github_server.py`; Vercel functions from `vercel_server.py`; MCP server files deleted only after functions are tested; `fastmcp` removed
**Addresses:** Pitfall 3 (MCP tool logic loss)
**Avoids:** Deleting MCP files before extraction is confirmed working

### Phase 4: Executor Rewrite
**Rationale:** The central new piece. Depends on Phase 2 (models stable) and Phase 3 (ToolRegistry exists). Rewrite from scratch at ~150 lines rather than surgical removal of the 590-line existing executor — the existing file has 7 enterprise import dependencies being removed simultaneously, making targeted editing harder than a clean rewrite.
**Delivers:** Simplified `orchestrator/executor.py`; YAML phase walker using existing TopologicalSorter; Anthropic API tool_use loop per phase; SSE event emission at phase boundaries; HaznMemory checkpoint at phase end (not turn boundary); WorkflowPhaseOutput storage; Deliverable rendering for delivery phases; WorkflowRun status management (pending/running/completed/failed); simplified `orchestrator/tasks.py:run_workflow()` signature
**Addresses:** Pitfall 4 (import chain crash), Pitfall 8 (Celery task signature coupling)
**Uses:** `anthropic>=0.84.0`, ToolRegistry (Phase 3), HaznMemory (Phase 5 — can finalize in parallel), PromptAssembler (unchanged), OutputCollector (unchanged), TopologicalSorter (unchanged)

### Phase 5: Memory Rewiring
**Rationale:** Can begin in parallel with Phase 4 or follow immediately after. HaznMemory is consumed by the new executor; its simplified interface must be finalized before executor end-to-end testing. L2/L3 parameter names are preserved to avoid orphaning existing Letta archival passages — the `[client:uuid]` tag format in archival memory must not change.
**Delivers:** Simplified HaznMemory: one Letta agent per `client_id`, `client_profile` block (persistent) + `active_task` block (wiped per run); `memory_query` field added to `WorkflowPhaseSchema` for targeted archival retrieval; `search_cross_client_insights` retained (works for 8+ clients under one agency); existing Letta agent state cleaned before first v3.0 run; `checkpoint_sync()` called at phase boundaries
**Addresses:** Pitfall 6 (L2/L3 terminology baked into HaznMemory interface), Pitfall 11 (stale enterprise memory blocks in existing Letta agents)
**Uses:** `letta-client>=1.7.12`

### Phase 6: Frontend Dashboard Simplification
**Rationale:** Must happen in lockstep with backend model changes from Phase 2, not after. The approvals page (HITL queue) will 404 on API calls immediately after Phase 2 is deployed. Frontend types must match simplified backend serializers. This phase makes the UI reflect the simplified system.
**Delivers:** Updated `frontend/src/types/api.ts` (14 interfaces simplified — HITL, QA fields removed); approvals page removed entirely; dashboard `pending_approvals` metric removed; deliverable detail simplified (no QA verdict display); workflow run detail simplified (no conflict_log, hitl_items fields); `npm run build` passing cleanly
**Addresses:** Pitfall 5 (frontend type drift causes runtime crashes)
**Avoids:** Letting TypeScript optional chaining silently hide broken UI after backend model changes

### Phase 7: End-to-End Validation and Cleanup
**Rationale:** Run the first real workflow for a real client. Validate the complete data flow: trigger -> Celery -> executor -> Anthropic API tool_use loop -> memory checkpoint -> deliverable render -> SSE completion notification. Confirm memory compounds on a second run. Clean up remaining dead code that was not removed in prior phases.
**Delivers:** First successful v3.0 workflow run with a real client; confirmed SSE phase progress monitoring; confirmed deliverable HTML rendering; confirmed memory persistence verified across two runs (client_profile accumulates); dead code removed (remaining enterprise modules not caught earlier); test fixtures updated; admin registrations for removed models cleaned
**Addresses:** Pitfall 12 (test fixtures reference removed enterprise models), Pitfall 13 (Django admin registrations for deleted models)

### Phase Ordering Rationale

- Phase 1 before everything: Package removal and Docker changes crash the app if code is not cleaned first
- Phase 2 before Phase 4: Models must be stable before executor rewrite references them
- Phase 3 before Phase 4: Executor needs the ToolRegistry to exist before it can reference it in tests
- Phase 5 can parallel Phase 4: HaznMemory interface is independent of executor's import chain
- Phase 6 must not lag behind Phase 2: Frontend type drift causes immediate user-facing breakage on the approvals page
- Phase 7 comes last: Full system validation; catches integration issues that unit tests miss

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 4 (Executor Rewrite):** The Anthropic API tool_use loop is well-documented, but the exact ordering of HaznMemory `active_task` block updates between phases, combined with SSE emission inside a Celery worker and Django's ORM transaction scope, has subtle async context requirements. A focused research pass on Celery + Django ORM + asyncio interaction before writing is recommended.
- **Phase 3 (Tool Migration):** GA4 Reporting API v4, Google Search Console API, and PageSpeed Insights API authentication patterns (service account JSON vs. OAuth token refresh) need explicit mapping against the existing Vault credential structure before extraction. The Vault secret path format for Google credentials must be documented before the extraction phase begins.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Dependency Cleanup):** Standard package management and import removal. Well-understood Django + Python patterns.
- **Phase 2 (Model Simplification):** Standard two-wave Django migration pattern. Well-documented in Django migration docs.
- **Phase 5 (Memory Rewiring):** Letta SDK patterns are well-documented and the `HaznMemory` abstraction is already working. Interface simplification is mechanical.
- **Phase 6 (Frontend Simplification):** Standard TypeScript type update and Next.js page removal. No research needed.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All dependencies verified against PyPI. Existing codebase analyzed at file level. One missing explicit declaration (anthropic). Removals (fastmcp, langfuse, openai) confirmed safe after code cleanup. |
| Features | HIGH | Codebase analysis confirms almost all P1 features exist in code. MCP-to-Python extraction is medium complexity but all implementation logic is present in existing files. |
| Architecture | HIGH | Existing code examined at component level. Component disposition (KEEP/SIMPLIFY/REMOVE/REPLACE) verified against actual import graphs, model FK relationships, and interface contracts. |
| Pitfalls | HIGH | Pitfalls derived from direct codebase analysis — specific file paths, line references, and FK relationships all verified against actual source. Not theoretical risks. |

**Overall confidence:** HIGH

### Gaps to Address

- **GA4/GSC/PageSpeed credential pattern in Vault:** The MCP server files contain the actual Google API authentication logic. Verify the exact Vault secret path structure and credential format before Phase 3 extraction. Read `mcp_servers/analytics_server.py` in full detail during Phase 3 planning before writing any replacement functions.
- **Letta agent state cleanup procedure:** Existing Letta agents from v1/v2 development have enterprise memory block formats (`active_client_context` with L2/L3 agency JSON). Need a one-time migration script or manual cleanup procedure before first v3.0 workflow run. Address at the start of Phase 5.
- **Celery vs. async views decision:** PITFALLS.md notes that Celery may be unnecessary for a single-user tool. Evaluate during Phase 4 planning: if workflows can run in Django async views, Celery can be removed, simplifying deployment. Not a blocker, but a worthwhile decision point.
- **`memory_query` YAML field addition:** STACK.md recommends adding `memory_query: str | None = None` to `WorkflowPhaseSchema` to enable targeted archival memory retrieval per phase. One-line Pydantic change with meaningful impact on context quality for Phase 2+ runs. Confirm scope during Phase 5 planning.

## Sources

### Primary (HIGH confidence)
- Existing codebase (`hazn_platform/` — 402 files, ~60,600 LOC): Direct analysis of all component files, import graphs, FK relationships, model definitions, and MCP server implementations
- [Anthropic Python SDK — PyPI](https://pypi.org/project/anthropic/): v0.84.0, tool_use loop patterns, async parallel dispatch
- [Letta memory blocks docs](https://docs.letta.com/guides/agents/memory-blocks/): Per-client agent patterns, block retrieval by label
- [letta-client — PyPI](https://pypi.org/project/letta-client/): v1.7.12 SDK verification
- [Django Migrations Documentation](https://docs.djangoproject.com/en/6.0/topics/migrations/): FK constraint handling, migration ordering, two-wave deletion strategy

### Secondary (MEDIUM confidence)
- [Anthropic advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use): Programmatic tool calling patterns, tool scoping per phase
- [Letta agent memory docs](https://docs.letta.com/guides/agents/memory/): Archival passages, memory organization, per-subject agent pattern
- [n8n SSE for AI Agent Tool Calls](https://github.com/n8n-io/n8n/pull/20499): tool-call-start/end SSE event patterns — validation that this is a standard approach
- [Letta Conversations Blog](https://www.letta.com/blog/conversations): Isolated per-client agent memory confirmation (Jan 2026)
- [Refactoring at Scale](https://understandlegacycode.com/blog/key-points-of-refactoring-at-scale/): Atomic change discipline, dependency analysis before deletion

### Tertiary (LOW confidence)
- [Marketing Automation for Agencies 2026 Playbook](https://www.enrichlabs.ai/blog/marketing-automation-for-agencies-2026-playbook): 8-12 client benchmark for AI-assisted account management
- [Agentic Workflow Patterns 2025](https://skywork.ai/blog/agentic-ai-examples-workflow-patterns-2025/): Orchestrator-worker DAG pattern references

---
*Research completed: 2026-03-12*
*Ready for roadmap: yes*

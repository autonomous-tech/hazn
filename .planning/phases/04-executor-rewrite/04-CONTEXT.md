# Phase 4: Executor Rewrite - Context

**Gathered:** 2026-03-13
**Status:** Ready for planning

<domain>
## Phase Boundary

A from-scratch executor reads workflow YAML, walks phases in DAG order via Agent SDK agent loops, stores phase outputs, renders deliverables, and emits SSE progress events — all running async in Celery. Full orchestrator rewrite: executor.py, tasks.py, session.py, and agent_runner.py replaced with clean implementations. Dead enterprise code deleted.

</domain>

<decisions>
## Implementation Decisions

### Phase-to-phase output passing
- Prior phase outputs injected into system prompt as a `## Prior Phase Results` section
- Content: summary paragraph + structured findings (severity, description, recommendation) — not full raw output
- Both raw markdown and structured artifacts stored on WorkflowPhaseOutput for reference, reuse, and editing
- Scope of injection: Claude's discretion based on workflow structure (direct dependencies only vs all prior phases)
- Delivery phases receive both structured artifacts and raw markdown from prior phases

### Memory integration — Full, from day one
- Full Letta memory integration in Phase 4 (not stubbed for Phase 5)
- One Letta agent per client (not per-agent-type per-client) — aligns with MEMO-01 design
- Client context (brand voice, keywords, basics) injected into system prompt at run start
- Agents also have memory tools available for deeper searches (past findings, specific keywords)
- Memory checkpoints after each phase completes (not per-wave, not end-only)
- Phase 5 will rewire HaznMemory internals; executor memory interface stays stable

### Agent turn limits & timeouts
- max_turns configurable per-phase via optional `max_turns` field in workflow YAML phase schema — default 30 if not specified
- Workflow-level timeout only (4-hour Celery limit) — no per-phase timeouts
- Required phase failure: retry once (fresh agent context), then halt workflow
- Optional phase failure: log error on WorkflowRun.error_details, skip dependent optional phases, continue workflow

### Rewrite scope — Full orchestrator rewrite
- Rewrite from scratch: executor.py, tasks.py, session.py, agent_runner.py
- Direct Agent SDK calls — no RuntimeBackend protocol abstraction
- File layout: Claude's discretion (single file vs split by concern)
- Dead enterprise files deleted in Phase 4: conflict_detector.py, hitl.py, old executor.py, old agent_runner.py, old session.py, old tasks.py, old backends/ directory
- Keep as-is: PromptAssembler, OutputCollector, WorkflowParser, MeteringCallback, ToolRegistry, tracing.py, SSE pattern, deliverable pipeline

### Claude's Discretion
- Phase output injection scope (direct dependencies vs all prior phases)
- New executor file layout (single file vs split modules)
- How to bridge one-Letta-agent-per-client with current get_or_create_agent() pattern
- WorkflowRun status enum cleanup (which statuses to keep/remove)
- Retry implementation for failed required phases (fresh context vs reuse conversation)
- How WorkflowSession lifecycle maps to new executor flow
- Test strategy for the rewritten orchestrator

</decisions>

<specifics>
## Specific Ideas

- Both raw markdown and structured artifacts must be stored on WorkflowPhaseOutput — "both should be stored so they're referencable, changeable, and reusable"
- One Letta agent per client aligns with Phase 5 MEMO-01 requirement — avoids creating redundant Letta agents that Phase 5 would need to consolidate
- Retry-once-then-halt for required phases handles transient API errors without infinite retry loops
- max_turns per-phase in YAML lets workflow authors tune: data collection phases may need 50 turns, delivery phases only 20

</specifics>

<code_context>
## Existing Code Insights

### Keep As-Is (Proven Components)
- `orchestrator/prompt_assembler.py`: System prompt assembly from agent/skill markdown — self-contained, no Django imports
- `orchestrator/output_collector.py`: Convention-based artifact extraction (report, findings, code, metadata)
- `orchestrator/workflow_parser.py`: YAML loading + `get_execution_order()` topological sort via graphlib
- `orchestrator/workflow_models.py`: Pydantic schemas (WorkflowSchema, WorkflowPhaseSchema) — add optional `max_turns` field
- `orchestrator/metering.py`: MeteringCallback with per-agent cost tracking and flush_to_db()
- `orchestrator/tools/registry.py`: ToolRegistry with get_server(), get_allowed_tools(), phase-scoped filtering
- `orchestrator/tracing.py`: Langfuse tracing (non-fatal, workflow/phase/tool spans)
- `workspace/sse_views.py`: send_workspace_event() for SSE streaming
- `deliverable_pipeline/renderer.py`: Jinja2 HTML rendering for delivery phases

### Rewrite from Scratch
- `orchestrator/executor.py` (~500 lines): Main orchestration loop — DAG walking, phase execution, SSE events. Has dead HITL/QA/conflict code
- `orchestrator/tasks.py` (~300 lines): Celery task wrapper — has enterprise lifecycle tasks, needs cleanup
- `orchestrator/session.py` (~200 lines): WorkflowSession lifecycle — create WorkflowRun, checkpoint, end/fail
- `orchestrator/agent_runner.py` (~150 lines): AgentRunner + RuntimeBackend protocol — replaced by direct SDK calls

### Delete Entirely
- `orchestrator/conflict_detector.py` — conflict detection (dead since Phase 2)
- `orchestrator/hitl.py` — HITL resolution (dead since Phase 2)
- `orchestrator/backends/` directory — agent_sdk.py and __init__.py (absorbed into new executor)
- `orchestrator/agent_manager.py` — Letta agent management (replace with one-agent-per-client pattern)

### Integration Points
- WorkflowPhaseOutput model: Already has content, summary, html_content, markdown_source fields — sufficient for output storage
- WorkflowRun model: Needs status enum cleanup (BLOCKED status deferred from Phase 2)
- ToolRegistry.get_allowed_tools(): Phase-scoped tool filtering — executor passes phase tool names from YAML
- send_workspace_event(): SSE events emitted at phase_started, phase_completed, phase_failed, workflow_started, workflow_completed, workflow_failed
- Celery shared_task pattern with 4hr timeout — async bridge via asyncio.new_event_loop()

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 04-executor-rewrite*
*Context gathered: 2026-03-13*

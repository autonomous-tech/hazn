# Phase 4: Executor Rewrite - Research

**Researched:** 2026-03-13
**Domain:** Claude Agent SDK executor, async Celery orchestration, DAG phase chaining, Letta memory integration
**Confidence:** HIGH

## Summary

Phase 4 is a from-scratch rewrite of the core orchestrator: executor.py, tasks.py, session.py, and agent_runner.py. The existing code carries dead enterprise features (HITL, QA, conflict detection, RuntimeBackend protocol) that are already commented out or deleted. The rewrite replaces ~1,150 lines across 4 files with clean implementations that call the Claude Agent SDK directly, pass phase outputs through system prompts, integrate Letta memory per-client, and emit SSE events at phase boundaries.

The Claude Agent SDK (`claude-agent-sdk>=0.1.47`) provides two APIs: `query()` for one-off sessions and `ClaudeSDKClient` for persistent conversations. For this executor, `query()` is the correct choice -- each phase is an independent agent execution with its own system prompt, tools, and task. The SDK handles the tool_use loop internally via MCP server config. The existing `ToolRegistry.get_server()` and `ToolRegistry.get_allowed_tools()` patterns are already wired for this and remain unchanged.

**Primary recommendation:** Rewrite executor as a clean async DAG walker that calls `query()` per-phase with assembled system prompts (including prior phase outputs), one Letta agent per client for memory, and structured output storage on WorkflowPhaseOutput. Delete all enterprise-era dead code. Keep all proven components untouched.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Prior phase outputs injected into system prompt as a `## Prior Phase Results` section (summary paragraph + structured findings, not full raw output)
- Both raw markdown and structured artifacts stored on WorkflowPhaseOutput for reference, reuse, and editing
- Full Letta memory integration in Phase 4 (not stubbed for Phase 5)
- One Letta agent per client (not per-agent-type per-client) -- aligns with MEMO-01 design
- Client context injected into system prompt at run start; agents also have memory tools for deeper searches
- Memory checkpoints after each phase completes
- max_turns configurable per-phase via optional `max_turns` field in workflow YAML -- default 30 if not specified
- Workflow-level timeout only (4-hour Celery limit) -- no per-phase timeouts
- Required phase failure: retry once (fresh agent context), then halt workflow
- Optional phase failure: log error on WorkflowRun.error_details, skip dependent optional phases, continue workflow
- Rewrite from scratch: executor.py, tasks.py, session.py, agent_runner.py
- Direct Agent SDK calls -- no RuntimeBackend protocol abstraction
- Delete: conflict_detector.py, hitl.py, old executor.py, old agent_runner.py, old session.py, old tasks.py, old backends/ directory
- Keep as-is: PromptAssembler, OutputCollector, WorkflowParser, MeteringCallback, ToolRegistry, tracing.py, SSE pattern, deliverable pipeline

### Claude's Discretion
- Phase output injection scope (direct dependencies vs all prior phases)
- New executor file layout (single file vs split modules)
- How to bridge one-Letta-agent-per-client with current get_or_create_agent() pattern
- WorkflowRun status enum cleanup (which statuses to keep/remove)
- Retry implementation for failed required phases (fresh context vs reuse conversation)
- How WorkflowSession lifecycle maps to new executor flow
- Test strategy for the rewritten orchestrator

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| EXEC-01 | Agent SDK executor reads YAML workflow definitions and chains phases via DAG order | WorkflowParser.get_execution_order() provides topological waves; query() per phase with MCP server config from ToolRegistry |
| EXEC-02 | Agent system prompts loaded from hazn/agents/*.md files per phase | PromptAssembler.assemble_prompt() already handles this -- keep as-is |
| EXEC-03 | Skills injected into agent context from hazn/skills/*.md per workflow YAML | PromptAssembler._read_skill_content() with reference inlining -- keep as-is |
| EXEC-04 | Phase-to-phase output passing (Phase N output available to Phase N+1) | Inject as `## Prior Phase Results` section in system prompt; store both raw and structured on WorkflowPhaseOutput |
| EXEC-05 | Async execution via Celery (workflows run in background) | shared_task with asyncio.new_event_loop() bridge pattern -- same as existing tasks.py |
| EXEC-06 | Structured output captured per phase and stored in WorkflowPhaseOutput | OutputCollector.collect() for artifacts; WorkflowPhaseOutput.objects.create() with content, summary, html_content, markdown_source |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| claude-agent-sdk | >=0.1.47 | Agent execution via query() with MCP tools | Only supported SDK; replaces RuntimeBackend protocol |
| celery | 5.6.2 | Async task execution with 4hr timeout | Already in use; shared_task with asyncio bridge |
| letta-client | >=1.7.11 | Per-client persistent memory (one Letta agent per client) | Already in use; HaznMemory wraps all Letta calls |
| django | (project version) | ORM for WorkflowRun, WorkflowPhaseOutput, Agency, EndClient | Already in use |
| graphlib | stdlib | TopologicalSorter for DAG execution order | Already in use via workflow_parser.py |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| asgiref | (project version) | sync_to_async for Django ORM in async executor | Already in use; wrap all ORM calls |
| pydantic | (project version) | WorkflowSchema validation, AuditReportPayload | Already in use in workflow_models.py |
| django-eventstream | (project version) | SSE via send_workspace_event() | Already in use for real-time updates |
| langfuse | (project version) | Tracing via start_workflow_trace, start_phase_span | Already in use; non-fatal wrapper |
| jinja2 | (project version) | Deliverable rendering via render_report() | Already in use in deliverable_pipeline |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| query() per phase | ClaudeSDKClient for session continuity | query() is correct: each phase is independent with its own system prompt; ClaudeSDKClient is for multi-turn conversations within a single agent |
| asyncio.new_event_loop() | Django async views | Celery workers are sync; new_event_loop() is the established bridge pattern |
| sync_to_async for ORM | Raw SQL | sync_to_async is idiomatic Django; ORM calls are simple creates/updates |

## Architecture Patterns

### Recommended Project Structure (Claude's Discretion: Split by Concern)

```
orchestrator/
  executor.py        # ~200 lines: WorkflowExecutor class -- DAG walker, phase runner
  tasks.py           # ~80 lines: Celery shared_task -- run_workflow only
  session.py         # ~120 lines: WorkflowSession -- run lifecycle, metering, memory
  # DELETED FILES:
  #   agent_runner.py       -- replaced by direct SDK calls in executor.py
  #   backends/              -- entire directory deleted
  #   agent_manager.py       -- replaced by one-agent-per-client in session.py
  #   conflict_detector.py   -- already removed in Phase 2
  #   hitl.py                -- already removed in Phase 2
  # KEPT AS-IS:
  prompt_assembler.py
  output_collector.py
  workflow_parser.py
  workflow_models.py
  metering.py
  tracing.py
  models.py
  tools/              # entire directory untouched
```

**Rationale for split over single file:** The executor, session, and celery task have distinct concerns and distinct test strategies. Keeping them separate allows targeted testing (session lifecycle tested with DB, executor tested with mocks, tasks tested with celery test utilities).

### Pattern 1: Direct SDK query() Per Phase
**What:** Each workflow phase calls `query()` with a fully assembled system prompt, MCP server config, and allowed tools list. No RuntimeBackend protocol indirection.
**When to use:** Every phase execution.
**Example:**
```python
# Source: Claude Agent SDK official docs (platform.claude.com/docs/en/agent-sdk/python)
from claude_agent_sdk import query, ClaudeAgentOptions

async def execute_phase(system_prompt, initial_prompt, registry, phase_tools, max_turns):
    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        mcp_servers={"hazn": registry.get_server()},
        allowed_tools=registry.get_allowed_tools(phase_tools),
        max_turns=max_turns,
        permission_mode="bypassPermissions",
    )

    final_text = ""
    total_cost = 0.0
    input_tokens = 0
    output_tokens = 0

    async for message in query(prompt=initial_prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    final_text = block.text
        elif isinstance(message, ResultMessage):
            if message.result:
                final_text = message.result
            if message.usage:
                input_tokens = message.usage.get("input_tokens", 0)
                output_tokens = message.usage.get("output_tokens", 0)
            total_cost = message.total_cost_usd or 0.0
            if message.is_error:
                raise RuntimeError(f"Agent error: {message.result}")

    return final_text, input_tokens + output_tokens, total_cost
```

### Pattern 2: Prior Phase Output Injection
**What:** After each phase completes, its output is stored on WorkflowPhaseOutput. Before the next phase runs, all completed prior phase outputs are assembled into a `## Prior Phase Results` section and appended to the system prompt.
**When to use:** For every phase except the first in the DAG.
**Example:**
```python
def build_prior_phase_section(completed_outputs: list[WorkflowPhaseOutput]) -> str:
    """Build ## Prior Phase Results section from completed phase outputs."""
    if not completed_outputs:
        return ""

    lines = ["---", "## Prior Phase Results", ""]
    for output in completed_outputs:
        lines.append(f"### Phase: {output.phase_id}")
        lines.append(f"**Summary:** {output.summary}")
        # Structured findings from content JSON
        content = output.content or {}
        findings = content.get("findings", [])
        if findings:
            lines.append("\n**Key Findings:**")
            for f in findings[:10]:  # Cap at 10 to manage token budget
                sev = f.get("severity", "")
                desc = f.get("description", "")
                rec = f.get("recommendation", "")
                lines.append(f"- [{sev}] {desc} -- Recommendation: {rec}")
        lines.append("")
    return "\n".join(lines)
```

### Pattern 3: One Letta Agent Per Client
**What:** Replace the per-agent-type-per-client pattern (`{agent_type}--{l3_client_id}`) with one Letta agent per client (`client--{l3_client_id}`). This agent accumulates memory across all workflow phases and runs.
**When to use:** At workflow start -- look up or create the single client Letta agent.
**Example:**
```python
def get_or_create_client_agent(l3_client_id: str) -> str:
    """Get or create a single Letta agent for this client."""
    client = get_letta_client()
    agent_name = f"client--{l3_client_id}"

    existing = client.agents.list(name=agent_name)
    if existing:
        return existing[0].id

    agent = client.agents.create(
        name=agent_name,
        system="Hazn client memory agent",
        memory_blocks=[{"label": "active_client_context", "value": ""}],
        tags=[f"l3:{l3_client_id}"],
    )
    return agent.id
```

### Pattern 4: Retry-Once for Required Phases
**What:** If a required phase fails, retry once with fresh agent context (new query() call, same system prompt). If the retry also fails, halt the workflow.
**When to use:** Only for required phases (phase.required == True).
**Example:**
```python
async def execute_with_retry(self, phase):
    try:
        return await self._execute_phase(phase)
    except Exception as first_error:
        if not phase.required:
            raise  # Optional phases don't retry
        logger.warning("Required phase %s failed, retrying once: %s", phase.id, first_error)
        try:
            return await self._execute_phase(phase)
        except Exception as retry_error:
            raise RuntimeError(
                f"Required phase {phase.id} failed after retry: {retry_error}"
            ) from retry_error
```

### Anti-Patterns to Avoid
- **RuntimeBackend protocol abstraction:** The only backend is Agent SDK. No protocol needed. Direct calls to `query()`.
- **Per-agent-type Letta agents:** Creates N agents per client per workflow. Phase 5 would need to consolidate. Use one agent per client from day one.
- **Full raw output in system prompts:** Token budget explosion. Use summary + structured findings only.
- **Synchronous Celery with blocking async calls:** Must use `asyncio.new_event_loop()` / `loop.run_until_complete()` bridge pattern. Never call `asyncio.run()` inside Celery (creates nested event loops).
- **Per-phase timeouts:** User decision is workflow-level timeout only (4hr Celery limit). Don't add per-phase timers.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| DAG topological sort | Custom graph walker | `workflow_parser.get_execution_order()` via graphlib.TopologicalSorter | Stdlib, handles cycles, produces parallel waves |
| System prompt assembly | String concatenation in executor | `prompt_assembler.assemble_prompt()` | Handles persona + skills + context + references |
| Agent output parsing | Custom markdown parser | `OutputCollector.collect()` | Convention-based, produces typed CollectedArtifacts |
| SSE event emission | WebSocket/polling | `send_workspace_event()` via django-eventstream | Agency-scoped channels, already wired to frontend |
| Tool registration | Manual tool list building | `ToolRegistry.get_server()` + `get_allowed_tools()` | MCP server config, phase-scoped filtering |
| Metering/cost tracking | Manual token counting | `MeteringCallback` with `flush_to_db()` | Per-agent, per-tool, accumulating, DB-backed |
| HTML rendering | Template string building | `render_report()` via Jinja2 pipeline | Branded, auto-escaped, validated via AuditReportPayload |
| Letta memory operations | Direct Letta API calls | `HaznMemory` class | Composite ranking, metadata tags, correction audit trail |

**Key insight:** Every "hard" problem in the executor already has a proven solution in kept components. The rewrite is about simplifying the orchestration glue, not rebuilding capability.

## Common Pitfalls

### Pitfall 1: asyncio Event Loop in Celery Workers
**What goes wrong:** Calling `asyncio.run()` inside a Celery task can fail if an event loop already exists (e.g., in Django ASGI context or certain Celery pool configurations).
**Why it happens:** Celery workers are sync by default. The Agent SDK `query()` is async. Bridge needed.
**How to avoid:** Use `asyncio.new_event_loop()` / `loop.run_until_complete()` / `loop.close()` pattern exactly as current tasks.py does.
**Warning signs:** `RuntimeError: This event loop is already running`

### Pitfall 2: sync_to_async Thread Safety with Django ORM
**What goes wrong:** Django ORM is not thread-safe. When using `sync_to_async`, each call runs in a separate thread. Shared mutable state between ORM calls can produce race conditions.
**Why it happens:** `sync_to_async(WorkflowRun.objects.create)(...)` runs in a thread pool.
**How to avoid:** Wrap each ORM operation individually. Don't share Django model instances across async boundaries without re-fetching. Use `update_fields` for partial updates.
**Warning signs:** `IntegrityError`, stale data on model instances.

### Pitfall 3: Token Budget Explosion from Prior Phase Output
**What goes wrong:** Injecting full raw output from prior phases into system prompts can exceed context window limits (200K tokens).
**Why it happens:** A data-collection phase can produce 50K+ characters of raw analytics data.
**How to avoid:** Inject ONLY summary paragraph + structured findings (severity, description, recommendation). Cap at 10 findings per phase. Store full raw output on WorkflowPhaseOutput for reference but never inject it.
**Warning signs:** API errors about context length, extremely high token costs on downstream phases.

### Pitfall 4: Letta Agent Name Collision During Migration
**What goes wrong:** Existing Letta agents use `{agent_type}--{l3_client_id}` naming. New pattern is `client--{l3_client_id}`. If old agents aren't handled, the new executor might fail to find memory.
**Why it happens:** Phase 5 will handle Letta internals migration. Phase 4 creates the new pattern.
**How to avoid:** Phase 4's `get_or_create_client_agent()` creates new agents with `client--` prefix. Old agents are ignored (not deleted). Phase 5's MEMO-01 will handle cleanup/migration of old agent data.
**Warning signs:** Missing client context on first v3.0 run (expected -- old agents had different memory blocks).

### Pitfall 5: Double SSE Events
**What goes wrong:** Both the executor and the Celery task emit workflow_started/completed events, resulting in duplicate SSE events on the frontend.
**Why it happens:** Current code emits events in both layers. Rewrite must pick one.
**How to avoid:** SSE events should be emitted ONLY from the executor (the authoritative source). The Celery task handles only the async bridge and error boundary. Remove duplicate events from tasks.py.
**Warning signs:** Frontend shows duplicate status updates.

### Pitfall 6: Optional Phase Failure Cascading
**What goes wrong:** When an optional phase fails, its dependent phases still try to run and fail because they expect prior phase output.
**Why it happens:** DAG walker doesn't track which optional phases were skipped.
**How to avoid:** Track skipped optional phases. Skip any phase whose `depends_on` includes a skipped optional phase. User decision says "skip dependent optional phases, continue workflow."
**Warning signs:** Cascading failures after an optional phase error.

### Pitfall 7: WorkflowRun Status BLOCKED Still in Enum
**What goes wrong:** The BLOCKED status was kept in Phase 2 for Phase 4 to clean up. If not removed, dead code paths remain.
**Why it happens:** Phase 2 deferred status cleanup to Phase 4.
**How to avoid:** Clean up WorkflowRun.Status enum: keep PENDING, RUNNING, COMPLETED, FAILED, TIMED_OUT. Remove BLOCKED (HITL feature is deleted). This may require a data migration if any existing rows have status='blocked'.
**Warning signs:** Dead code referencing BLOCKED status.

### Pitfall 8: Agent SDK import chain failure
**What goes wrong:** The SDK try/except import chain (`claude_agent_sdk` then `claude_code_sdk`) can mask real import errors if the package is installed but broken.
**Why it happens:** Broad except catching hides the real error.
**How to avoid:** Import at module level with the existing try/except pattern but log the actual exception. In the new executor, fail fast if the SDK isn't available (it's required, not optional).
**Warning signs:** Silent executor failures with "SDK not available" error.

## Code Examples

### Executor Main Loop (Verified Pattern)
```python
# Source: Combining SDK docs + existing workflow_parser pattern
async def run(self) -> WorkflowRun:
    """Execute workflow: start session, walk DAG, emit events, end session."""
    workflow_run = self._session.workflow_run
    await sync_to_async(self._session.start)()

    # Emit workflow_started
    await sync_to_async(send_workspace_event)(
        agency_id=str(workflow_run.agency_id),
        event_type="workflow_status",
        data={"run_id": str(workflow_run.pk), "event": "workflow_started", "status": "running"},
    )

    # Initialize Langfuse trace (non-fatal)
    trace_id = await sync_to_async(start_workflow_trace)(workflow_run)

    # Load client memory context once at workflow start
    await sync_to_async(self._session.load_client_context)()

    # Walk DAG waves
    waves = get_execution_order(self._workflow)
    for wave in waves:
        phases = [self._phase_map[pid] for pid in wave if pid in self._phase_map]
        results = await asyncio.gather(
            *(self._execute_with_retry(phase) for phase in phases),
            return_exceptions=True,
        )

        # Process results...
        for phase, result in zip(phases, results):
            if isinstance(result, Exception):
                if phase.required:
                    await sync_to_async(self._session.fail)(str(result)[:500])
                    await self._emit_workflow_failed(str(result)[:500])
                    return workflow_run
                else:
                    self._skipped_phases.add(phase.id)
                    # Log on error_details
            else:
                self._completed_phases.add(phase.id)

        # Checkpoint after each wave
        await sync_to_async(self._session.checkpoint)(phase_id=phases[-1].id if phases else None)

    # End session
    await sync_to_async(self._session.end)()
    await self._emit_workflow_completed()
    return workflow_run
```

### SDK query() Call with MCP Tools
```python
# Source: Claude Agent SDK docs (platform.claude.com/docs/en/agent-sdk/python)
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock

async def run_agent_phase(system_prompt, user_prompt, registry, phase_tools, max_turns=30):
    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        mcp_servers={"hazn": registry.get_server()},
        allowed_tools=registry.get_allowed_tools(phase_tools),
        max_turns=max_turns,
        permission_mode="bypassPermissions",
    )

    final_text = ""
    usage_data = {}

    async for message in query(prompt=user_prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    final_text = block.text
        elif isinstance(message, ResultMessage):
            if message.result:
                final_text = message.result
            usage_data = {
                "input_tokens": (message.usage or {}).get("input_tokens", 0),
                "output_tokens": (message.usage or {}).get("output_tokens", 0),
                "total_cost": message.total_cost_usd or 0.0,
                "num_turns": message.num_turns,
                "duration_ms": message.duration_ms,
            }
            if message.is_error:
                raise RuntimeError(f"Agent execution failed: {message.result or 'unknown error'}")

    return final_text, usage_data
```

### WorkflowPhaseSchema with max_turns
```python
# Source: Existing workflow_models.py + user decision
class WorkflowPhaseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    agent: str | None = None
    depends_on: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    required: bool = True
    tools: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    max_turns: int = 30  # New field, default 30 per user decision
    # ... rest unchanged
```

### Celery Task Async Bridge
```python
# Source: Existing tasks.py pattern (proven)
@shared_task(bind=True, max_retries=0, time_limit=4*3600+300, soft_time_limit=4*3600)
def run_workflow(self, workflow_name, agency_id, client_id, triggered_by):
    # ... setup ...
    loop = asyncio.new_event_loop()
    try:
        executor = WorkflowExecutor(workflow, session)
        loop.run_until_complete(executor.run())
    finally:
        loop.close()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| RuntimeBackend protocol + AgentSDKBackend class | Direct `query()` calls | Phase 4 (this rewrite) | Removes protocol indirection, ~250 lines of dead abstraction |
| Per-agent-type-per-client Letta agents | One Letta agent per client | Phase 4 (this rewrite) | Simpler memory model, aligns with MEMO-01 |
| HITL checkpoints blocking workflow | No blocking -- user reviews deliverables directly | Phase 2 (already removed) | Executor no longer checks for blocking items |
| QA injection after each phase | No QA pipeline -- user is quality gate | Phase 2 (already removed) | Executor no longer calls qa.runner |
| Conflict detection pre-flight | No conflicts -- single user | Phase 2 (already removed) | Executor no longer imports conflict_detector |
| claude_code_sdk package name | claude_agent_sdk (renamed) | SDK migration | Import chain: try claude_agent_sdk first, claude_code_sdk fallback |
| AgentRunner.run() with tool_dispatch closure | SDK handles tool dispatch via MCP server config | Phase 4 (this rewrite) | dispatch_tool_async no longer needed |

**Deprecated/outdated:**
- `agent_runner.py` RuntimeBackend Protocol: Only one backend exists (SDK). Protocol adds complexity with no value.
- `agent_manager.py` get_or_create_agent(): Per-type-per-client pattern conflicts with MEMO-01. Replace with per-client.
- `backends/` directory: Only contained AgentSDKBackend which is absorbed into direct query() calls.
- `WorkflowRun.Status.BLOCKED`: HITL removed in Phase 2. Dead enum value.

## Open Questions

1. **Delivery Phase Output Format**
   - What we know: Current executor expects delivery phase to produce JSON matching AuditReportPayload schema, which gets rendered to HTML via Jinja2.
   - What's unclear: Whether all workflow types (not just analytics-audit) will use the same delivery pattern, or if some produce markdown-only output.
   - Recommendation: Keep the current `if phase.id == "delivery"` check but make it generic: check for any phase with `outputs` containing "branded_html_report" and render accordingly. Fall back to storing raw markdown for phases without HTML rendering.

2. **Direct Dependencies vs All Prior Phases for Output Injection**
   - What we know: User left this as Claude's discretion. Current DAG has linear or near-linear dependencies.
   - What's unclear: Whether injecting ALL prior phases creates better or worse agent behavior than only direct dependencies.
   - Recommendation: **Inject only direct dependency outputs.** Rationale: (a) Reduces token usage; (b) Aligns with DAG semantics -- a phase depends on specific predecessors; (c) If a phase needs data from a non-dependency, the workflow YAML should express that dependency. Implementation: filter `completed_outputs` to only phases listed in `phase.depends_on`.

3. **WorkflowRun.conflict_log field after BLOCKED removal**
   - What we know: conflict_log JSONField still exists on the model. Conflict detection is deleted.
   - What's unclear: Whether to remove the field (requires migration) or leave it empty.
   - Recommendation: Leave the field in Phase 4 (no migration churn). It can be cleaned in a future model cleanup pass.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 + pytest-django 4.12.0 + pytest-asyncio >=0.23.0 |
| Config file | `hazn_platform/pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `cd hazn_platform && python -m pytest tests/test_executor.py tests/test_session.py tests/test_orchestrator_tasks.py -x -q` |
| Full suite command | `cd hazn_platform && python -m pytest tests/ -x -q` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| EXEC-01 | Executor reads YAML and chains phases in DAG order | unit | `cd hazn_platform && python -m pytest tests/test_executor.py -x -q -k "dag_order or execution_order"` | Exists but needs full rewrite |
| EXEC-02 | Agent system prompts loaded from agent .md files | unit | `cd hazn_platform && python -m pytest tests/test_prompt_assembler.py -x -q` | Exists (kept as-is) |
| EXEC-03 | Skills injected from skill .md per workflow YAML | unit | `cd hazn_platform && python -m pytest tests/test_prompt_assembler.py -x -q -k "skill"` | Exists (kept as-is) |
| EXEC-04 | Phase-to-phase output passing | unit | `cd hazn_platform && python -m pytest tests/test_executor.py -x -q -k "prior_phase or output_pass"` | Needs new tests |
| EXEC-05 | Async execution via Celery | unit | `cd hazn_platform && python -m pytest tests/test_orchestrator_tasks.py -x -q` | Exists but needs full rewrite |
| EXEC-06 | Structured output captured and stored in WorkflowPhaseOutput | unit | `cd hazn_platform && python -m pytest tests/test_executor.py -x -q -k "phase_output"` | Needs new tests |

### Sampling Rate
- **Per task commit:** `cd hazn_platform && python -m pytest tests/test_executor.py tests/test_session.py tests/test_orchestrator_tasks.py -x -q`
- **Per wave merge:** `cd hazn_platform && python -m pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_executor.py` -- complete rewrite needed: remove HITLItem import, conflict_detector mocks, QA mocks; add prior-phase-output tests, retry logic tests, optional-phase-skip tests
- [ ] `tests/test_session.py` -- partial rewrite: remove log_conflicts test, add load_client_context test, adapt memory pattern for one-agent-per-client
- [ ] `tests/test_orchestrator_tasks.py` -- partial rewrite: remove deliver_webhook and check_hitl_timeouts tests, simplify run_workflow test for new session/executor API
- [ ] `tests/test_agent_runner.py` -- DELETE: agent_runner.py is deleted
- [ ] `tests/test_agent_sdk_backend.py` -- DELETE: backends/ directory is deleted
- [ ] `tests/test_agent_manager.py` -- DELETE or rewrite: agent_manager.py is being replaced

## Sources

### Primary (HIGH confidence)
- Claude Agent SDK Python reference (platform.claude.com/docs/en/agent-sdk/python) -- query() API, ClaudeAgentOptions, message types, create_sdk_mcp_server(), tool() decorator, ResultMessage.usage
- Claude Agent SDK overview (platform.claude.com/docs/en/agent-sdk/overview) -- MCP server integration, allowed_tools, permission_mode, session management
- Codebase direct: executor.py, tasks.py, session.py, agent_runner.py, backends/agent_sdk.py -- current implementation patterns
- Codebase direct: prompt_assembler.py, output_collector.py, workflow_parser.py, models.py, metering.py, tracing.py, tools/registry.py -- kept components API contracts

### Secondary (MEDIUM confidence)
- Codebase direct: sse_views.py, deliverable_pipeline/renderer.py, deliverable_pipeline/schemas.py -- integration point contracts
- Codebase direct: core/memory.py, core/letta_client.py -- Letta memory integration patterns
- Codebase direct: workflow YAML files (analytics-audit.yaml) -- phase structure, tools, depends_on patterns

### Tertiary (LOW confidence)
- None -- all findings verified against codebase and official SDK docs

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries already in use; SDK API verified against official docs
- Architecture: HIGH -- rewrite scope is clear; kept components are stable; SDK query() pattern is verified
- Pitfalls: HIGH -- identified from codebase analysis and existing patterns; async/Celery bridging is proven
- Open questions: MEDIUM -- delivery phase generalization and output injection scope need validation during implementation

**Research date:** 2026-03-13
**Valid until:** 2026-04-13 (stable -- SDK API is documented, kept components don't change)

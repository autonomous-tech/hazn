# Technology Stack: v3.0 Strip & Simplify

**Project:** Hazn Platform -- Personal Multi-Client Workflow Runner
**Researched:** 2026-03-12
**Overall Confidence:** HIGH
**Scope:** Stack changes/additions for the simplified architecture. Three areas: (1) Anthropic API tool_use with Python function tools, (2) per-client Letta memory, (3) simplified YAML workflow engine.

---

## Executive Summary

v3.0 needs almost nothing new. The existing stack already contains every core dependency. The work is **subtraction and rewiring**, not addition. The `anthropic` SDK (already used by `AnthropicAPIBackend`), `letta-client` (already used by `HaznMemory`), `PyYAML` + `pydantic` (already used by `workflow_parser.py`), and `graphlib` (stdlib) cover all three areas.

The one dependency that must be **explicitly added to pyproject.toml** is `anthropic>=0.84.0` -- it is imported in `backends/anthropic_api.py` but never declared as a direct dependency (it was likely pulled in transitively).

Everything else is simplification of existing code: strip MCP routing indirection, replace `ToolRouter` with a flat Python dict of callables, simplify `HaznMemory` to remove L2/L3 hierarchy, and slim the executor to remove conflict detection, HITL, QA, metering, and budget enforcement.

---

## Area 1: Anthropic API Direct tool_use Loops with Python Function Tools

### What Exists (Keep)

The `AnthropicAPIBackend` (backends/anthropic_api.py) is already a clean, working tool_use loop:

- Uses `anthropic.AsyncAnthropic()` with `messages.create()`
- Handles `stop_reason == "tool_use"` -> parallel dispatch via `asyncio.gather`
- Handles `stop_reason == "end_turn"` -> extract text, return
- Handles `stop_reason == "max_tokens"` -> partial result error

This is architecturally correct and matches the official Anthropic SDK patterns exactly.

### What Changes

| Change | From (v2.0) | To (v3.0) | Rationale |
|--------|------------|-----------|-----------|
| Tool dispatch | `ToolRouter` -> `ToolRegistryEntry` -> MCP callable | Flat `dict[str, Callable]` | MCP indirection removed. Tools are just Python functions. |
| Budget enforcement | `BudgetConfig` + `BudgetEnforcer` + `calculate_cost` | Simple max_turns counter (default 50) | Personal tool -- no billing. Just prevent runaway loops. |
| Metering | `MeteringCallback.on_llm_call()` per turn | Log total tokens to WorkflowRun record | No Langfuse, no per-agency cost caps. Just record what was spent. |
| Tool schema | `ToolRegistryEntry.input_schema` (generic `{"type": "object"}`) | Proper JSON Schema per tool, derived from Python function signatures | Gives Claude accurate parameter info. Use `inspect.signature()` or manual schema dicts. |

### Recommended Pattern: `@beta_tool` Decorator

The Anthropic SDK (v0.84.0) provides `@beta_tool` and `client.beta.messages.tool_runner()` for automatic tool dispatch. However, **use this cautiously**:

**Use tool_runner for:** Simple, single-agent tasks where you want the SDK to handle the loop automatically.

**Do NOT use tool_runner for:** The workflow executor. The executor needs control over:
- Which tools are scoped per phase
- Memory injection between phases
- SSE event emission after each turn
- Conversation history capture for debugging

**Recommendation:** Keep the manual tool_use loop from `AnthropicAPIBackend` but simplify the tool dispatch. Replace `ToolRouter` with a plain registry:

```python
# Simplified tool dispatch (no ToolRouter, no MCP)
TOOL_REGISTRY: dict[str, tuple[Callable, dict]] = {
    "search_memory": (search_memory_fn, {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Semantic search query"},
            "limit": {"type": "integer", "default": 5},
        },
        "required": ["query"],
    }),
    "pull_ga4_data": (pull_ga4_data_fn, {...}),
    # ... one entry per tool
}

def build_tools_for_phase(phase_tools: list[str]) -> list[dict]:
    """Return Anthropic API tools array for given tool names."""
    return [
        {"name": name, "description": fn.__doc__ or "", "input_schema": schema}
        for name, (fn, schema) in TOOL_REGISTRY.items()
        if not phase_tools or name in phase_tools
    ]

async def dispatch_tool(tool_use_block) -> dict:
    """Dispatch a tool_use block to the matching Python function."""
    name = tool_use_block.name
    fn, _ = TOOL_REGISTRY.get(name, (None, None))
    if fn is None:
        return {"type": "tool_result", "tool_use_id": tool_use_block.id,
                "content": f"Unknown tool: {name}", "is_error": True}
    try:
        if inspect.iscoroutinefunction(fn):
            result = await fn(**tool_use_block.input)
        else:
            result = await asyncio.to_thread(fn, **tool_use_block.input)
        return {"type": "tool_result", "tool_use_id": tool_use_block.id,
                "content": json.dumps(result) if isinstance(result, (dict, list)) else str(result)}
    except Exception as exc:
        return {"type": "tool_result", "tool_use_id": tool_use_block.id,
                "content": f"Tool error: {exc}", "is_error": True}
```

### What to Keep from Tool Tools

Not all 23 tools survive. The v3.0 tool set:

| Tool Category | Keep | Drop | Rationale |
|--------------|------|------|-----------|
| Memory (7) | `search_memory`, `write_finding`, `load_context` | `checkpoint_sync`, `correct_memory`, `search_cross_client_insights`, `get_credentials` | Simplify to core read/write. Memory management happens at executor level, not inside agent turns. Cross-client is single-user noise. Credentials go through executor setup, not agent request. |
| Analytics (3) | All: `pull_ga4_data`, `query_gsc`, `check_pagespeed` | None | Core functionality. Rewrite as plain Python functions (already are, minus MCP wrapping). |
| Data collection (3) | All: `collect_ga4_data`, `collect_gsc_data`, `collect_pagespeed_data` | None | Subprocess wrappers for analytics scripts. Keep as-is. |
| GitHub (6) | `create_repo`, `create_pr`, `merge_pr` | `get_pr_status`, `get_ci_status`, `list_branches` | Keep deployment essentials. Drop monitoring tools (Rizwan checks GitHub directly). |
| Vercel (4) | `deploy_project`, `get_preview_url` | `get_deployment_status`, `list_deployments` | Keep deploy + preview. Drop status checking (Rizwan checks Vercel directly). |

**v3.0 tool count: ~13** (down from 23). Each is a plain Python function with a JSON schema.

### Model Selection (Updated)

| Use Case | Model | Rationale |
|----------|-------|-----------|
| Default for all agents | `claude-sonnet-4-5-20250929` | Best cost/quality ratio. Sufficient for SEO, copy, strategy, audits. |
| Complex strategic analysis | `claude-sonnet-4-5-20250929` with extended thinking | Same model, enable thinking for deeper analysis phases. |

Do NOT use Opus for v3.0. Sonnet handles all current agent tasks. Extended thinking (adaptive, high effort) provides depth when needed without the 5x cost jump.

### Dependency Status

| Package | Version | In pyproject.toml? | Action |
|---------|---------|-------------------|--------|
| `anthropic` | 0.84.0 | **NO** -- imported but not declared | **ADD** `"anthropic>=0.84.0"` |
| `httpx` | >=0.27.0 | Yes | No change (transitive dep of anthropic) |

**Confidence:** HIGH. Verified via [PyPI anthropic 0.84.0](https://pypi.org/project/anthropic/), [Anthropic Python SDK docs](https://platform.claude.com/docs/en/api/sdks/python), existing codebase analysis.

---

## Area 2: Per-Client Letta Memory That Compounds Across Runs

### What Exists (Keep)

The `HaznMemory` class (core/memory.py) is already a well-designed swap-safe abstraction over Letta. It handles:

- Core memory blocks (in-context, pinned to system prompt)
- Archival memory (semantic search over passages with composite ranking)
- Craft learning buffering with metadata tags
- Checkpoint sync (flush learnings every 10 turns)
- Structured findings to Postgres
- Memory correction with audit trail

The `letta_client.Letta` factory (core/letta_client.py) connects to the self-hosted Letta server.

### What Changes

| Change | From (v2.0) | To (v3.0) | Rationale |
|--------|------------|-----------|-----------|
| Agent identity | One Letta agent per `(agent_type, l3_client_id)` pair | One Letta agent per `client_id` (shared across all agent types) | Memory compounds per client, not per agent type. SEO findings should be visible to the copywriter. |
| Memory blocks | `active_client_context` block (wiped on session end) | `client_profile` block (persistent) + `active_task` block (wiped per run) | Client profile accumulates. Only task-specific context resets. |
| L2/L3 hierarchy | `l2_agency_id` + `l3_client_id` | `client_id` only | Single user, no agency hierarchy. |
| Cross-client insights | Postgres query across sibling EndClients | Remove entirely | Single user manages all clients directly. If insights needed, query Postgres directly in the tool. |
| Context assembly | Query Agency + EndClient + BrandVoice + Keywords + Campaigns from ORM | Query simplified Client model + BrandVoice | Fewer models, flatter structure. |

### Per-Client Memory Architecture

Each client gets ONE Letta agent with these memory blocks:

```
client_profile (persistent, never wiped):
  - Brand voice, tone, positioning
  - Industry, competitors, target audience
  - Work history summary (accumulated across runs)
  - Key decisions and their rationale

active_task (wiped per workflow run):
  - Current workflow name and phase
  - Findings from completed phases in this run
  - Intermediate outputs needed by downstream phases
```

Archival memory (passages) accumulates craft learnings across runs:
- SEO findings, keyword research results
- Audit scores and improvement tracking
- Content strategy decisions
- Technical implementation notes

### How Memory Compounds

1. **Before a run:** Load `client_profile` block into the agent's system prompt. Search archival memory for relevant past findings.
2. **During a run:** Write phase outputs to `active_task` block so downstream phases have context. Buffer craft learnings.
3. **After a run:** Update `client_profile` block with new work history summary. Flush craft learnings to archival. Write structured findings to Postgres. Clear `active_task`.

This means the second SEO audit for a client automatically knows what was found in the first audit, what keywords were chosen, what content was produced, and how the site has changed.

### Simplified Client Model

The existing Django models include Agency, EndClient, BrandVoice, Campaign, Keyword, Audit, Decision. For v3.0:

| Keep | Simplify | Drop |
|------|----------|------|
| BrandVoice | EndClient -> Client (remove agency FK, add direct fields) | Agency (no L2 hierarchy) |
| Keyword | Campaign (simplify) | MemoryCorrection audit trail (overkill for personal use) |
| Audit | Decision | ConflictDetection models |
| WorkflowRun | WorkflowPhaseOutput | HITL models, QA models |

### Letta SDK Usage

The `letta-client` SDK (v1.7.12) supports everything needed:

```python
# Create per-client Letta agent (once, on client creation)
agent = client.agents.create(
    name=f"hazn-{client_slug}",
    memory_blocks=[
        {"label": "client_profile", "value": initial_profile_json, "limit": 8000},
        {"label": "active_task", "value": "", "limit": 4000},
    ],
    model="anthropic/claude-sonnet-4-5",  # Letta's model routing
)

# Load context before a run
profile_block = client.agents.blocks.retrieve_by_label(
    agent_id=agent.id, label="client_profile"
)

# Update after a run
client.agents.blocks.update_by_label(
    agent_id=agent.id, label="client_profile",
    value=updated_profile_json,
)

# Semantic search over past findings
results = client.agents.passages.search(
    agent_id=agent.id, query="previous SEO audit findings"
)
```

### Dependency Status

| Package | Version | In pyproject.toml? | Action |
|---------|---------|-------------------|--------|
| `letta-client` | 1.7.12 | Yes (`>=1.7.11`) | No change. Pin could be updated to `>=1.7.12` but not critical. |

**Confidence:** HIGH. Verified via [letta-client 1.7.12 on PyPI](https://pypi.org/project/letta-client/), [Letta memory blocks docs](https://docs.letta.com/guides/agents/memory-blocks/), [Letta agent memory docs](https://docs.letta.com/guides/agents/memory/), existing codebase.

---

## Area 3: Simplified YAML Workflow Engine That Chains Agent Phases

### What Exists (Keep)

The workflow engine is already solid:

- `workflow_models.py`: Pydantic schemas (`WorkflowSchema`, `WorkflowPhaseSchema`, `WorkflowCheckpoint`) with `extra="allow"` for tolerant parsing
- `workflow_parser.py`: YAML loading via `PyYAML`, validation via Pydantic, DAG construction via `graphlib.TopologicalSorter`
- `prompt_assembler.py`: Reads agent markdown + skill SKILL.md + client context, assembles system prompt
- 7 workflow YAML files in `hazn/workflows/`

### What Changes

| Change | From (v2.0) | To (v3.0) | Rationale |
|--------|------------|-----------|-----------|
| Executor | 589 lines with conflict detection, HITL, QA, metering, Langfuse, dual backend, cost caps | ~150 lines: load YAML, run phases in DAG order, dispatch to simplified agent loop | Personal tool. No HITL gates, no QA injection, no staging deployment, no conflict detection. |
| Phase execution | `AgentRunner` + `RuntimeBackend` Protocol + `ToolRouter` + `OutputCollector` | Direct call to simplified `AnthropicAPIBackend.execute()` with flat tool registry | Remove layers of indirection. One path: YAML -> phases -> Anthropic API calls. |
| Session model | `WorkflowSession` with start/checkpoint/end/fail lifecycle, turn counting, metering | Simple run record: workflow_name, client_id, started_at, status, phase_outputs | No session/checkpoint complexity. |
| Checkpoints | HITL items created for user approval | Log-only: "Strategy phase complete, review before proceeding" as SSE event | Rizwan reviews deliverables directly in the dashboard. No blocking gates. |
| Parallel execution | `asyncio.gather` for phases in same wave | Keep `asyncio.gather` for parallel phases | This is good existing behavior. DAG waves run in parallel. |

### Simplified Executor Flow

```
1. Load YAML -> WorkflowSchema (existing parser, unchanged)
2. Get execution waves via TopologicalSorter (existing, unchanged)
3. For each wave:
   a. For each phase in wave (parallel via asyncio.gather):
      - Skip if no agent (informational phase)
      - Assemble system prompt (existing prompt_assembler, simplified)
      - Load client memory from Letta (client_profile block + relevant archival)
      - Build scoped tools list for this phase
      - Run tool_use loop (simplified AnthropicAPIBackend)
      - Store phase output in active_task memory block
      - Store WorkflowPhaseOutput record
      - Send SSE event
   b. If required phase failed -> halt workflow
4. End: update client_profile, flush learnings, clear active_task
```

### YAML Schema (No Change Needed)

The existing workflow YAML schema is sufficient. Example from `website.yaml`:

```yaml
phases:
  - id: strategy
    name: Strategy & Positioning
    agent: strategist
    outputs: [.hazn/outputs/strategy.md]
    required: true

  - id: ux
    name: UX Architecture
    agent: ux-architect
    depends_on: [strategy]
    outputs: [.hazn/outputs/ux-blueprint.md]
    required: true
```

The Pydantic models handle `depends_on`, `required`, `agent`, `outputs`, `skills`, `tools` -- all present. The `extra="allow"` config handles per-workflow variations (e.g., `parallel_tracks` in audit.yaml, `per_article` in blog.yaml).

### What Phase YAML Might Gain

One small addition to consider: a `memory_query` field so phases can declare what context they need from past runs:

```yaml
  - id: seo
    name: SEO Optimization
    agent: seo-specialist
    depends_on: [dev]
    memory_query: "previous SEO audits, keyword research, competitor analysis"
    outputs: [.hazn/outputs/seo-checklist.md]
```

This would tell the executor what to search for in archival memory before injecting it into the system prompt. Without it, the executor would need to use a generic query or the phase description itself.

**Recommendation:** Add `memory_query: str | None = None` to `WorkflowPhaseSchema`. It is one line of Pydantic and enables targeted memory retrieval.

### Dependency Status

| Package | Version | In pyproject.toml? | Action |
|---------|---------|-------------------|--------|
| `PyYAML` | (transitive via Django/Celery) | Yes (transitive) | No change |
| `pydantic` | (transitive via DRF) | Yes (transitive) | No change |
| `graphlib` | stdlib (Python 3.9+) | N/A | No change |

**Confidence:** HIGH. All dependencies already exist. The work is code simplification, not library addition.

---

## What NOT to Add (Complexity Traps)

### Libraries to Avoid

| Library | Trap | Why NOT |
|---------|------|---------|
| `langchain` / `langgraph` | "It handles agent orchestration" | Imposes its own agent/chain/tool abstractions on top of code that already works. The existing YAML -> Pydantic -> TopologicalSorter -> Anthropic API pipeline is simpler and more debuggable than any framework wrapper. |
| `crewai` | "It does multi-agent workflows" | Role-based crew model does not match Hazn's phase-based DAG execution. Would require rewriting all 7 workflow YAMLs to fit CrewAI's paradigm. |
| `autogen` | "It handles multi-agent conversations" | Conversational turn-taking model. Hazn agents don't converse with each other -- they execute phases sequentially/in parallel via a DAG. |
| `prefect` / `airflow` / `dagster` | "Real workflow orchestration" | Massive overhead for 7 YAML workflows running on one machine. `graphlib.TopologicalSorter` + `asyncio.gather` is 80 lines. These frameworks add deployment infrastructure, UI, scheduling, versioning -- none of which a personal tool needs. |
| `instructor` | "Structured output from Claude" | Adds a Pydantic extraction layer over the API. The existing `OutputCollector` handles artifact extraction from markdown. Adding instructor would create two competing output parsing systems. |
| `letta` (server package) | "Run Letta embedded instead of Docker" | The Docker Compose Letta server works. Embedding Letta inside Django would merge two complex systems into one. Keep them separate. |
| `anthropic[mcp]` | "MCP support built into anthropic SDK" | MCP is being stripped. Do not add MCP back through a different door. |
| `celery-progress` | "Better task progress tracking" | SSE via `django-eventstream` already handles progress. Adding another progress tracking layer creates confusion about which system is authoritative. |
| `tiktoken` | "Pre-call token counting" | Not needed for v3.0. Budget enforcement is a simple max_turns counter. Token counting before each API call is enterprise-grade caution that adds latency for no benefit when Rizwan is the only user and can see costs in the Anthropic dashboard. |
| `tenacity` | "Retry logic for API calls" | The `anthropic` SDK has built-in retry (2 retries by default, configurable via `max_retries`). Adding tenacity on top of built-in retry creates double-retry behavior. |

### Patterns to Avoid

| Pattern | Trap | Why NOT |
|---------|------|---------|
| Keeping `ToolRouter` with `ToolRegistryEntry` | "Don't break what works" | The indirection made sense when 4 MCP servers needed routing. With plain Python functions, a flat dict is clearer. The ToolRouter class, its 345 lines, its static map, its validate_registry, and its wire_callables are all unnecessary when tools are just `{name: callable}`. |
| Keeping `BudgetEnforcer` with cost model | "Cost control" | Personal tool. Rizwan sees costs on dashboard.anthropic.com. A max_turns guard (default 50) prevents runaway loops. That is sufficient. |
| Keeping dual RuntimeBackend Protocol | "Extensibility" | There is exactly one backend: Anthropic API. The Protocol, AgentSDKBackend, runtime mode selection -- all dead code after stripping. One concrete class, not a protocol. |
| Adding a "tool definition framework" | "Auto-generate schemas from type hints" | Writing 13 JSON schemas by hand takes 30 minutes and is completely transparent. Auto-generation from type hints via `inspect` or `pydantic` looks elegant but hides what Claude sees, making debugging tool call failures harder. |
| Keeping Langfuse integration | "Observability" | Personal tool. Print logs to stdout. Check the Anthropic console for usage. Langfuse adds a self-hosted service, a Python SDK, decorator wrapping, trace ID plumbing, and a separate UI -- for one user who can read Django logs. |
| Keeping `WorkflowSession` with its lifecycle | "Session management" | The session model (start/checkpoint/end/fail with turn counting, metering callbacks, memory sync) was designed for multi-tenant billing. For personal use: create a WorkflowRun record, set status to running/completed/failed. Done. |

---

## Summary: What Changes in pyproject.toml

### Add

```toml
"anthropic>=0.84.0",
```

### Remove (Can Be Cleaned Up)

```toml
# These can be removed when their corresponding code is stripped:
"fastmcp>=3.1.0",              # MCP servers removed
"langfuse>=3.14.0",            # Metering/tracing removed
"PyGithub>=2.8.1",             # Can keep if GitHub tools remain, but could switch to httpx+GitHub API
"openai>=1.0.0",               # Was for Letta server config, not used by platform code directly
"django-eventstream>=5.3.3",   # KEEP -- needed for SSE progress updates
```

### No Change (Already Correct)

```toml
"letta-client>=1.7.11",        # Per-client memory (already declared)
"django==5.2.12",              # Backend framework (stays)
"celery==5.6.2",               # Async task execution (stays)
"djangorestframework==3.16.0", # API layer (stays)
"pgvector==0.3.6",             # Semantic search (stays)
"hvac==2.4.0",                 # Vault integration (stays)
"httpx>=0.27.0",               # HTTP client (stays)
"redis==7.2.1",                # Celery broker + cache (stays)
"django-cors-headers>=4.9.0",  # Frontend CORS (stays)
"django-filter>=25.2",         # API filtering (stays)
```

**Net dependency change:** +1 (anthropic). Several can be removed but that is a cleanup task, not a blocker.

---

## Integration Map: How the Three Areas Connect

```
YAML Workflow (Area 3)
  |
  v
workflow_parser.py loads + validates -> WorkflowSchema
  |
  v
TopologicalSorter produces execution waves
  |
  v
For each phase:
  |
  +---> prompt_assembler.py builds system prompt
  |       (agent markdown + skill content + client context)
  |
  +---> HaznMemory (Area 2) loads client_profile block
  |       + searches archival memory for relevant past findings
  |       -> injected into system prompt
  |
  +---> AnthropicAPIBackend (Area 1) runs tool_use loop
  |       - tools scoped per phase from flat registry
  |       - tools are plain Python functions (no MCP)
  |       - loop until end_turn or max_turns
  |
  +---> Phase output stored:
          - WorkflowPhaseOutput record (Postgres)
          - active_task memory block (Letta, for downstream phases)
          - Craft learnings buffered for archival flush
  |
  v
After all phases:
  - Update client_profile block (work history, key findings)
  - Flush craft learnings to archival memory
  - Clear active_task block
  - Set WorkflowRun.status = completed
  - Render deliverables via Jinja2 pipeline
```

---

## Version Verification

| Package | Current Version | Verified Source | Date |
|---------|----------------|-----------------|------|
| anthropic | 0.84.0 | [PyPI](https://pypi.org/project/anthropic/) | 2026-03-12 |
| letta-client | 1.7.12 | [PyPI](https://pypi.org/project/letta-client/) | 2026-03-12 |
| Django | 5.2.12 | pyproject.toml (existing) | 2026-03-12 |
| Celery | 5.6.2 | pyproject.toml (existing) | 2026-03-12 |
| DRF | 3.16.0 | pyproject.toml (existing) | 2026-03-12 |
| PyYAML | transitive | via Django/Celery | 2026-03-12 |
| Pydantic | transitive | via DRF/letta-client | 2026-03-12 |
| graphlib | stdlib | Python 3.13 | 2026-03-12 |

---

## Sources

- [Anthropic Python SDK - PyPI](https://pypi.org/project/anthropic/) -- v0.84.0, Feb 25, 2026
- [Anthropic Python SDK docs](https://platform.claude.com/docs/en/api/sdks/python) -- `@beta_tool`, `tool_runner()`, streaming, async patterns
- [Anthropic Python SDK - GitHub](https://github.com/anthropics/anthropic-sdk-python) -- changelog, releases
- [Anthropic advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use) -- programmatic tool calling, tool search
- [letta-client - PyPI](https://pypi.org/project/letta-client/) -- v1.7.12, Mar 9, 2026
- [Letta memory blocks docs](https://docs.letta.com/guides/agents/memory-blocks/) -- `memory_blocks` parameter, block retrieval by label
- [Letta agent memory docs](https://docs.letta.com/guides/agents/memory/) -- archival passages, message persistence, memory organization
- [Letta AI GitHub](https://github.com/letta-ai/letta) -- self-hosted deployment, database persistence
- [Python graphlib docs](https://docs.python.org/3/library/graphlib.html) -- TopologicalSorter API
- Existing codebase: `backends/anthropic_api.py`, `core/memory.py`, `core/letta_client.py`, `orchestrator/executor.py`, `orchestrator/workflow_parser.py`, `orchestrator/tool_router.py`, `orchestrator/tool_wiring.py`

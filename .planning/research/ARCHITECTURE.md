# Architecture Research: v3.0 Simplified Multi-Client Workflow Runner

**Domain:** Simplification of existing agent execution platform for personal multi-client use
**Researched:** 2026-03-12
**Confidence:** HIGH (all source code examined, v2.0 components verified against Anthropic API docs)

---

## Executive Summary

Hazn v2.0 built a fully functional orchestration engine: DAG executor, Anthropic API backend with tool_use loops, ToolRouter with MCP server dispatch, PromptAssembler, OutputCollector, BudgetEnforcer, MeteringCallback, session lifecycle, HITL queue, QA pipeline, Langfuse tracing, and workspace UI. The codebase is approximately 60,600 LOC across Django backend and Next.js frontend.

The v3.0 milestone strips enterprise features that serve multi-tenant agency use cases irrelevant to the actual deployment: a single person (Rizwan) running workflows for 8+ clients. The architecture question is not "what to build" but "what to remove, what to keep, and what to simplify."

This document maps each existing component to its v3.0 fate (KEEP / SIMPLIFY / REMOVE / REPLACE), defines the simplified data flow, and specifies exact integration points for the new simplified components.

---

## Component Disposition: Keep / Simplify / Remove / Replace

### KEEP (Unchanged)

These components work correctly for the simplified use case and require no modification.

| Component | File(s) | Rationale |
|-----------|---------|-----------|
| Workflow Parser | `orchestrator/workflow_parser.py` | Loads YAML, validates via Pydantic, computes DAG -- works as-is |
| Workflow Models (schema) | `orchestrator/workflow_models.py` | `WorkflowSchema`, `WorkflowPhaseSchema` -- sufficient for all 7 workflows |
| Prompt Assembler | `orchestrator/prompt_assembler.py` | Reads agent persona + skill markdowns + client context -- clean, no enterprise deps |
| Output Collector | `orchestrator/output_collector.py` | Extracts report/findings/code/metadata from agent markdown -- self-contained |
| Deliverable Pipeline | `deliverable_pipeline/renderer.py`, `schemas.py` | Jinja2 HTML rendering from structured JSON -- no enterprise deps |
| Letta Client Factory | `core/letta_client.py` | `get_letta_client()` returns configured client -- 5 lines, perfect |
| Vault Integration | `core/vault.py` | AppRole auth for secrets -- still needed for GA4/GSC API keys |
| Vault Credentials Model | `core/models.py::VaultCredential` | Secret references pointing to Vault -- stays |
| Agent Personas | `hazn/agents/*.md` | 15 agent markdown definitions -- core asset, untouched |
| Skill Definitions | `hazn/skills/*/SKILL.md` | 25+ skill definitions -- core asset, untouched |
| Workflow YAMLs | `hazn/workflows/*.yaml` | 7 workflow definitions -- core asset, untouched |
| Docker Compose Stack | `docker-compose.local.yml` | Postgres 17 + pgvector, Letta, Vault, Redis -- stays |

### SIMPLIFY (Modify to remove enterprise concerns)

| Component | File(s) | What Changes |
|-----------|---------|--------------|
| **Executor** | `orchestrator/executor.py` | Remove: conflict detection, HITL checkpoints, agency cost cap, Langfuse tracing. Keep: DAG wave execution, phase runner, SSE events, phase output storage |
| **Session** | `orchestrator/session.py` | Remove: conflict logging, metering flush. Simplify: status transitions, memory lifecycle. Remove MeteringCallback dependency |
| **Agent Runner** | `orchestrator/agent_runner.py` | Remove: MeteringCallback integration, ToolRouter dependency in dispatch_tool_async. Replace ToolRouter-based dispatch with direct Python function dispatch |
| **Anthropic API Backend** | `orchestrator/backends/anthropic_api.py` | Remove: BudgetEnforcer, MeteringCallback. Keep: tool_use loop, stop_reason handling, text extraction |
| **Core Models** | `core/models.py` | Simplify Agency/EndClient: remove `churned_at`, `deletion_notified_at`, `tool_preferences`, `house_style`, `methodology` from active use (can leave fields, just ignore). Remove MemoryCorrection if not needed |
| **Orchestrator Models** | `orchestrator/models.py` | Remove HITLItem model. Simplify WorkflowRun: remove agency FK (single user), remove conflict_log, langfuse_trace_id. Keep WorkflowPhaseOutput. Remove WorkflowAgent, WorkflowToolCall (metering models) |
| **Workspace Views** | `workspace/views.py` | Remove: MemoryInspectorView, HITLItemViewSet. Simplify: DashboardView (no pending_approvals). Keep: WorkflowTriggerView, WorkflowCatalogView, WorkflowRunViewSet, DeliverableViewSet |
| **Celery Tasks** | `orchestrator/tasks.py` | Remove: deliver_webhook, check_hitl_timeouts, enforce_data_retention, process_gdpr_deletions, send_deletion_notifications. Keep: run_workflow (simplified) |
| **SSE Views** | `workspace/sse_views.py` | Simplify: remove agency channel scoping (single user, single channel). Keep: event dispatch mechanism |
| **Frontend** | `frontend/src/` | Remove: approvals page, memory inspector, settings page, share functionality. Simplify: dashboard, client list, workflow trigger, deliverables. Keep: layout, auth |

### REMOVE (Delete entirely)

| Component | File(s) | Rationale |
|-----------|---------|-----------|
| MCP Servers | `mcp_servers/*.py` (4 files) | Tools become Python functions -- no MCP transport needed |
| Tool Router | `orchestrator/tool_router.py` | Replaced by direct function registry -- no MCP server mapping needed |
| Tool Wiring | `orchestrator/tool_wiring.py` | Wired MCP server functions to ToolRouter -- no longer needed |
| Agent SDK Backend | `orchestrator/backends/agent_sdk.py` | Dual runtime removed -- API only |
| Budget Enforcer | `orchestrator/budget.py` | Personal tool -- no per-run cost caps |
| Metering Callback | `orchestrator/metering.py` | No per-agent billing -- simple token tracking on WorkflowRun suffices |
| Conflict Detector | `orchestrator/conflict_detector.py` | No L2/L3 hierarchy, single user |
| HITL Module | `orchestrator/hitl.py` | No approval queue -- Rizwan reviews deliverables directly |
| Tracing Module | `orchestrator/tracing.py` | Langfuse integration removed (can re-add later if needed) |
| QA Runner | `qa/runner.py`, `qa/criteria.py`, `qa/staging.py` | No automated QA pipeline -- direct deliverable review |
| QA Models | `qa/models.py` | Deliverable model simplified (see below) |
| Data Tools | `orchestrator/data_tools.py` | Subprocess wrappers replaced by direct Python function tools |
| Lifecycle Module | `core/lifecycle.py` | GDPR/retention enforcement -- not needed for personal tool |
| Management Commands | `core/management/commands/enforce_retention.py`, etc. | Lifecycle enforcement -- removed |
| Share Models/Views | `workspace/share_models.py`, `workspace/share_views.py` | Public share links -- not needed initially |
| Workspace Filters | `workspace/filters.py` | Complex filtering for multi-tenant -- simplify to basics |
| Workspace Permissions | `workspace/permissions.py::IsAgencyMember` | Single user -- simplify to IsAuthenticated |

### REPLACE (New simplified components)

| New Component | Replaces | Purpose |
|---------------|----------|---------|
| **ToolRegistry** | `tool_router.py` + `tool_wiring.py` + `mcp_servers/*.py` | Simple dict mapping tool names to Python async functions |
| **SimpleExecutor** | Simplified `executor.py` | YAML phase walker with Anthropic API agent loop, no enterprise concerns |
| **Client model** | Simplified `EndClient` | Flat client list with Letta agent reference, no L2/L3 hierarchy |
| **Deliverable model** | Simplified from `qa/models.py::Deliverable` | Output storage without QA verdict, approval pipeline, or Vercel staging |

---

## Recommended Architecture

### System Overview

```
                    Browser (Rizwan)
                         |
              ┌──────────▼──────────┐
              │   Next.js 15 UI     │
              │  ┌────────────────┐ │
              │  │ Client List    │ │
              │  │ Workflow Trigger│ │
              │  │ Run Monitor    │ │  <-- SSE: run_events
              │  │ Deliverables   │ │
              │  └────────────────┘ │
              └──────────┬──────────┘
                         │ REST API
              ┌──────────▼──────────┐
              │   Django 5.2 (DRF)  │
              │  ┌────────────────┐ │
              │  │ /clients/      │ │  CRUD
              │  │ /workflows/    │ │  catalog + trigger
              │  │ /runs/         │ │  status + history
              │  │ /deliverables/ │ │  list + detail
              │  └────────────────┘ │
              └──────────┬──────────┘
                         │ Celery task
              ┌──────────▼──────────┐
              │   Celery Worker     │
              │  ┌────────────────┐ │
              │  │ run_workflow   │ │
              │  │  1. Load YAML  │ │
              │  │  2. Walk phases│ │
              │  │  3. Per phase: │ │
              │  │   a. Assemble  │ │  <-- PromptAssembler (KEEP)
              │  │      prompt    │ │
              │  │   b. Load Letta│ │  <-- HaznMemory (KEEP)
              │  │      memory   │ │
              │  │   c. Run agent │ │  <-- AnthropicAPIBackend (SIMPLIFY)
              │  │      loop     │ │
              │  │   d. Collect   │ │  <-- OutputCollector (KEEP)
              │  │      output   │ │
              │  │  4. Store      │ │
              │  │     deliverable│ │
              │  │  5. SSE notify │ │
              │  └────────────────┘ │
              └────┬────┬────┬──────┘
                   │    │    │
         ┌─────────┘    │    └─────────┐
         ▼              ▼              ▼
    ┌─────────┐   ┌──────────┐   ┌─────────┐
    │Anthropic│   │  Letta   │   │ Vault   │
    │  API    │   │ (memory) │   │(secrets)│
    └─────────┘   └────┬─────┘   └─────────┘
                       │
                  ┌────▼────┐
                  │Postgres │
                  │17+pgvec │
                  └─────────┘
```

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| Next.js UI | Client CRUD, workflow trigger, run monitoring, deliverable viewing | Django API (REST), SSE stream |
| Django API | Auth, client/workflow/run/deliverable CRUD, Celery dispatch | Postgres, Celery, SSE |
| Celery Worker | Async workflow execution | Anthropic API, Letta, Vault, Postgres, SSE |
| PromptAssembler | Build system prompt from agent persona + skills + client context | Filesystem (hazn/ markdowns), Letta (via HaznMemory) |
| ToolRegistry | Map tool names to Python async functions | Python function implementations |
| AnthropicAPIBackend | Multi-turn tool_use loop | Anthropic Messages API, ToolRegistry |
| HaznMemory | Client context loading, memory search, checkpoint sync | Letta SDK, Postgres |
| OutputCollector | Parse agent markdown into structured artifacts | Pure data -- no external deps |
| Deliverable Pipeline | Render structured JSON to branded HTML | Jinja2 templates |

---

## Data Flow: UI to Deliverable (Simplified)

```
1. TRIGGER
   Rizwan clicks "Run Analytics Audit" for client "Acme Corp"
   |
   POST /api/workflows/trigger/
   Body: { workflow_name: "analytics-audit", client_id: "uuid" }
   |
   Django validates:
   - User authenticated (session cookie)
   - Client exists
   - Workflow YAML exists
   |
   Creates WorkflowRun(status=PENDING, client_id, workflow_name)
   |
   run_workflow.delay(workflow_name, client_id, run_id)
   |
   Response: 202 { run_id: "uuid" }

2. CELERY EXECUTION
   |
   load_workflow("hazn/workflows/analytics-audit.yaml")
   -> WorkflowSchema with 5 phases:
      setup -> data-collection -> analysis -> review -> delivery
   |
   WorkflowRun.status = RUNNING
   SSE: { event: "workflow_started", run_id }
   |
   get_execution_order(workflow) -> [[setup], [data-collection], [analysis], [review], [delivery]]
   |
   FOR EACH wave:
     FOR EACH phase in wave (parallel via asyncio.gather):
       |
       IF phase.agent is None: SKIP (informational)
       |
       a. LOAD MEMORY
          memory = HaznMemory(agent_id, client_id)
          memory.load_client_context()
          -> Queries Client + BrandVoice from Postgres
          -> Writes to Letta agent's active_client_context block
       |
       b. ASSEMBLE PROMPT
          system_prompt = assemble_prompt(
            agent_type = "analytics-inspector",
            skills = ["analytics-audit"],
            client_context = { name, brand_voice, keywords, ... }
          )
          -> Reads hazn/agents/analytics-inspector.md
          -> Reads hazn/skills/analytics-audit/SKILL.md
          -> Formats client context as markdown
       |
       c. BUILD TOOLS
          tools = tool_registry.get_tools_for_phase(phase.tools)
          -> Returns list of { name, description, input_schema } dicts
          -> Only tools declared in workflow YAML phase
       |
       d. RUN AGENT LOOP
          backend = AnthropicAPIBackend(model="claude-sonnet-4-5")
          result = await backend.execute(
            system_prompt = system_prompt,
            messages = [{ role: "user", content: phase_instruction }],
            tools = tools,
            tool_dispatch = tool_registry.dispatch,
          )
          |
          LOOP:
            -> messages.create() to Anthropic API
            -> IF stop_reason == "tool_use":
                 FOR EACH tool_use block:
                   result = await tool_registry.dispatch(block)
                   -> e.g., search_memory -> HaznMemory.search_memory()
                   -> e.g., pull_ga4_data -> ga4_tool_function()
                   -> e.g., get_credentials -> vault.read_secret()
                 Append assistant + tool_results to messages
                 CONTINUE
            -> IF stop_reason == "end_turn":
                 Extract final text
                 BREAK
            -> IF stop_reason == "max_tokens":
                 Log warning, return partial
                 BREAK
       |
       e. COLLECT OUTPUT
          artifacts = OutputCollector().collect(result.final_text)
          -> Report artifact (full markdown)
          -> Findings artifact (structured list)
          -> Code artifact (tagged code blocks)
          -> Metadata artifact (word count, sections)
       |
       f. STORE PHASE OUTPUT
          WorkflowPhaseOutput.objects.create(
            workflow_run = run,
            phase_id = phase.id,
            content = { final_text, artifacts, usage },
          )
       |
       g. RENDER DELIVERABLE (if delivery phase)
          payload = AuditReportPayload(**json.loads(final_text))
          html = render_report("analytics-audit.html", payload)
          Deliverable.objects.create(
            workflow_run = run,
            phase_output = phase_output,
            title = "Analytics Audit: Acme Corp",
            html_content = html,
            markdown_source = final_text,
          )
       |
       h. SSE NOTIFY
          send_event("run_events", {
            event: "phase_completed",
            run_id, phase_id, phase_name, status
          })
   |
   END wave loop
   |
   memory.checkpoint_sync()  -- flush learnings to Letta archival
   memory.end_session([])    -- wipe active context
   |
   WorkflowRun.status = COMPLETED
   WorkflowRun.total_tokens = accumulated
   |
   SSE: { event: "workflow_completed", run_id }

3. DELIVERABLE ACCESS
   |
   Rizwan sees SSE notification in dashboard
   -> Navigates to /deliverables/{id}
   -> GET /api/deliverables/{id}/
   -> Returns: title, html_content, markdown_source, created_at
   -> Frontend renders HTML report in iframe/panel
```

---

## Simplified Component Specifications

### 1. ToolRegistry (REPLACES ToolRouter + tool_wiring + MCP servers)

**File:** `orchestrator/tool_registry.py` (NEW)

The v2.0 architecture had 3 layers of indirection: `tool_wiring.py` imported functions from 4 MCP server modules and wired them into `ToolRouter` entries that dispatched via `dispatch_anthropic()`. The v3.0 ToolRegistry collapses this to a single dict of name-to-function mappings.

```python
# orchestrator/tool_registry.py

from __future__ import annotations
import json
import logging
from typing import Any, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ToolDef:
    """A tool definition with its callable implementation."""
    name: str
    description: str
    input_schema: dict[str, Any]
    fn: Callable  # async or sync function

class ToolRegistry:
    """Simple registry mapping tool names to Python functions.

    No MCP servers. No server_name mapping. No ToolRegistryEntry.
    Just: name -> (schema, callable).
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolDef] = {}

    def register(self, tool_def: ToolDef) -> None:
        self._tools[tool_def.name] = tool_def

    def get_anthropic_tools(self, tool_names: list[str]) -> list[dict]:
        """Return Anthropic API tools array filtered to requested names.

        If tool_names is empty, returns all tools.
        """
        if not tool_names:
            return [
                {"name": t.name, "description": t.description, "input_schema": t.input_schema}
                for t in self._tools.values()
            ]
        return [
            {"name": t.name, "description": t.description, "input_schema": t.input_schema}
            for name in tool_names
            if (t := self._tools.get(name))
        ]

    async def dispatch(self, tool_use_block: Any) -> dict:
        """Dispatch a tool_use block to the registered function.

        Handles both dict and Pydantic SDK object tool_use blocks.
        Returns Anthropic tool_result format.
        """
        # Extract from dict or Pydantic object
        if isinstance(tool_use_block, dict):
            name = tool_use_block["name"]
            tool_input = tool_use_block.get("input", {})
            tool_id = tool_use_block["id"]
        else:
            name = tool_use_block.name
            tool_input = tool_use_block.input
            tool_id = tool_use_block.id

        tool_def = self._tools.get(name)
        if tool_def is None:
            return {
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": f"Unknown tool: {name}",
                "is_error": True,
            }

        try:
            import asyncio, inspect
            if inspect.iscoroutinefunction(tool_def.fn):
                result = await tool_def.fn(**tool_input)
            else:
                result = await asyncio.to_thread(tool_def.fn, **tool_input)

            content = json.dumps(result) if isinstance(result, (dict, list)) else str(result)
            return {
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": content,
            }
        except Exception as exc:
            logger.error("Tool %s error: %s", name, exc)
            return {
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": f"Tool error: {exc}",
                "is_error": True,
            }
```

**Tool Registration:** Instead of importing from 4 MCP server modules, tools are registered as plain Python functions. The tool functions themselves are extracted from the MCP server code (they are already Python functions decorated with `@mcp.tool()`; the decorator is removed, the function body stays).

**Tool categories for v3.0:**

| Category | Tools | Source |
|----------|-------|--------|
| Memory | `load_context`, `search_memory`, `write_finding`, `checkpoint_sync` | Extracted from `hazn_memory_server.py`, call `HaznMemory` methods |
| Analytics | `pull_ga4_data`, `query_gsc`, `check_pagespeed` | Extracted from `analytics_server.py`, direct API calls |
| Credentials | `get_credentials` | Calls `vault.read_secret()` |
| Data Collection | `collect_ga4_data`, `collect_gsc_data`, `collect_pagespeed_data` | Extracted from `data_tools.py`, subprocess wrappers for Python scripts |

**Removed tools (v3.0):** GitHub tools (6), Vercel tools (4), `correct_memory`, `search_cross_client_insights` (cross-client queries not needed for single user managing all clients). These can be re-added when workflows need them.

### 2. Simplified Executor (MODIFIES `executor.py`)

**File:** `orchestrator/executor.py` (MODIFIED)

The current executor is 589 lines. The v3.0 executor should be approximately 150-200 lines. Key simplifications:

**Removed from `_execute_phase()`:**
- `check_agency_cost_cap()` -- no budget enforcement
- `reconcile_tools()` via Letta agent manager -- tools come from ToolRegistry, not Letta
- `BudgetConfig` construction -- no per-run budgets
- `BudgetEnforcer` in backend -- no budget enforcement
- `MeteringCallback` integration -- simple token counter on WorkflowRun
- Runtime mode selection (`HAZN_RUNTIME_MODE`) -- always Anthropic API
- Agent SDK backend path -- removed entirely
- ToolRouter singleton lookup -- replaced by ToolRegistry
- QA injection (`should_run_qa`, `create_deliverable`, `handle_qa_result`) -- deliverables created directly
- Staging deployment (`deploy_to_staging`) -- no Vercel preview

**Kept in `_execute_phase()`:**
- `get_or_create_agent()` -- still need persistent Letta agents for memory
- `assemble_prompt()` -- prompt assembly unchanged
- `AnthropicAPIBackend.execute()` -- simplified (no budget/metering params)
- `OutputCollector().collect()` -- artifact extraction unchanged
- `WorkflowPhaseOutput.objects.create()` -- phase output storage
- SSE events (`send_workspace_event`) -- simplified channel
- Deliverable rendering for delivery phases

**Kept in `run()`:**
- Session lifecycle (`start()`, `end()`)
- Topological wave execution
- Parallel phase execution via `asyncio.gather`
- Required/optional phase failure handling

**Removed from `run()`:**
- Conflict detection (`detect_conflicts`, `process_conflicts`)
- HITL checkpoints (`_check_checkpoints`, `has_blocking_items`)
- Langfuse trace initialization
- Session checkpoint after each wave (simplified to end-of-workflow only)

### 3. Simplified AnthropicAPIBackend (MODIFIES `backends/anthropic_api.py`)

**File:** `orchestrator/backends/anthropic_api.py` (MODIFIED)

The current backend has BudgetEnforcer and MeteringCallback as required parameters. The simplified version:

```python
class AnthropicAPIBackend:
    """Simplified Anthropic Messages API backend.

    Runs tool_use loop without budget enforcement or metering callbacks.
    Tracks tokens internally for simple reporting on WorkflowRun.
    """

    def __init__(self, model: str = "claude-sonnet-4-5", max_output_tokens: int = 4096):
        self._model = model
        self._max_output_tokens = max_output_tokens
        self._client = anthropic.AsyncAnthropic()

    async def execute(
        self,
        system_prompt: str,
        messages: list[dict],
        tools: list[dict],
        tool_dispatch: Callable,  # ToolRegistry.dispatch
        max_turns: int = 50,
    ) -> RunResult:
        """Execute tool_use loop until completion or max_turns.

        Returns RunResult with status, final_text, usage (total_tokens, total_cost).
        No BudgetEnforcer. No MeteringCallback. Simple turn counting.
        """
        total_input_tokens = 0
        total_output_tokens = 0

        for turn in range(max_turns):
            create_kwargs = {
                "model": self._model,
                "max_tokens": self._max_output_tokens,
                "system": system_prompt,
                "messages": messages,
            }
            if tools:
                create_kwargs["tools"] = tools

            response = await self._client.messages.create(**create_kwargs)

            total_input_tokens += response.usage.input_tokens
            total_output_tokens += response.usage.output_tokens

            if response.stop_reason == "end_turn":
                final_text = self._extract_text(response.content)
                messages.append({"role": "assistant", "content": response.content})
                return RunResult(
                    status="completed",
                    final_text=final_text,
                    usage={
                        "input_tokens": total_input_tokens,
                        "output_tokens": total_output_tokens,
                        "total_tokens": total_input_tokens + total_output_tokens,
                        "turns": turn + 1,
                    },
                )

            if response.stop_reason == "tool_use":
                tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
                tool_results = await asyncio.gather(
                    *(tool_dispatch(block) for block in tool_use_blocks)
                )
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": list(tool_results)})
                continue

            if response.stop_reason == "max_tokens":
                return RunResult(
                    status="max_tokens_truncated",
                    final_text=self._extract_text(response.content),
                    usage={"total_tokens": total_input_tokens + total_output_tokens, "turns": turn + 1},
                    error_message="Response truncated: max_tokens reached",
                )

        return RunResult(
            status="max_turns",
            final_text="",
            usage={"total_tokens": total_input_tokens + total_output_tokens, "turns": max_turns},
        )
```

**Key difference from v2.0:** The `execute()` signature drops `budget`, `metering`, `agent_id`, and `on_turn` parameters. Token tracking is internal to the method and returned in `RunResult.usage`. The caller (executor) writes totals to `WorkflowRun` at the end.

### 4. Simplified Client Model

**v2.0 had:** Agency (L2) -> EndClient (L3) hierarchy with tool_preferences, house_style, methodology, lifecycle fields.

**v3.0 needs:** A flat client list. Each client has a name, basic metadata, and a reference to their Letta agent.

**Approach:** Keep the existing `EndClient` model but simplify how it is used. Create a single "default" Agency row for Rizwan's workspace. All clients belong to this agency. The Agency model's enterprise fields (`tool_preferences`, `house_style`, `methodology`, lifecycle fields) are ignored but not deleted (avoid migration churn).

```python
# Simplified client usage pattern:

# At startup / seed:
agency, _ = Agency.objects.get_or_create(
    slug="hazn-personal",
    defaults={"name": "Hazn Personal Workspace"}
)

# Client CRUD:
client = EndClient.objects.create(
    agency=agency,
    name="Acme Corp",
    slug="acme-corp",
    competitors=["competitor1.com", "competitor2.com"],
)

# Workflow runs reference client directly:
WorkflowRun.objects.create(
    workflow_name="analytics-audit",
    agency=agency,  # always the same agency
    end_client=client,
    triggered_by="rizwan",
)
```

**Why keep Agency at all:** The WorkflowRun FK to Agency is used throughout the codebase (SSE channels, queryset scoping, etc.). Removing it would require touching dozens of files. Keeping a single default Agency row is cheaper than refactoring all FKs.

### 5. Simplified Deliverable Model

**v2.0 had:** QA verdict, approval status, HITL item FK, preview_url, vercel_deployment_id, qa_score, qa_report.

**v3.0 needs:** Title, HTML content, markdown source, phase output link, created_at.

**Approach:** Keep the existing Deliverable model but ignore QA/approval fields. Set `qa_verdict = "pass"` and `approval_status = "auto_approved"` by default. No HITL items created.

Alternatively, a simpler model could be created:

```python
class Deliverable(models.Model):
    """A deliverable produced by a workflow phase."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_run = models.ForeignKey("orchestrator.WorkflowRun", on_delete=models.CASCADE, related_name="deliverables")
    phase_output = models.OneToOneField("orchestrator.WorkflowPhaseOutput", on_delete=models.CASCADE, related_name="deliverable")
    title = models.CharField(max_length=255)
    html_content = models.TextField(blank=True, default="")
    markdown_source = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
```

**Recommendation:** Keep the existing Deliverable model unchanged to avoid migrations, but only populate title, html_content, markdown_source, workflow_run, and phase_output. Set qa_verdict="pass", approval_status="auto_approved" on creation. This preserves the option to re-add QA later without migration.

### 6. Per-Client Letta Memory (KEEP + clarify integration)

**The current `HaznMemory` class is already correctly designed for per-client use.** Each `HaznMemory` instance is scoped to one `agent_id` + one `l3_client_id`. The memory compounding pattern works as follows:

```
Run 1: SEO Audit for Acme Corp
  -> Agent "seo-specialist--acme-uuid" created in Letta
  -> HaznMemory loads client context (brand voice, keywords, competitors)
  -> Agent discovers findings, writes to Letta archival memory
  -> Session ends: context block wiped, archival memory persists

Run 2: Blog Content for Acme Corp
  -> Agent "content-writer--acme-uuid" created in Letta
  -> HaznMemory loads fresh client context
  -> Agent can search_memory() to find SEO findings from Run 1
  -> Agent uses past findings to inform content strategy
  -> New learnings written to archival memory

Run 3: Another SEO Audit for Acme Corp
  -> Agent "seo-specialist--acme-uuid" already exists
  -> Persona refreshed from latest markdown
  -> search_memory() finds past audit findings
  -> Agent builds on previous work, tracks improvements
```

**What compounding means practically:**
- Letta agent's **archival memory** (pgvector passages) accumulates across runs
- Each passage has metadata tags: `[timestamp]`, `[confidence]`, `[agent]`, `[client]`, `[status]`
- `search_memory()` uses composite ranking (60% similarity, 25% recency, 15% confidence)
- Agent types share the same client's archival: SEO findings are searchable by the content writer
- The `active_client_context` block is loaded fresh each run and wiped at session end

**Simplification for v3.0:** Remove `search_cross_client_insights()` (single-user, can query directly if needed). Remove `correct_memory()` exposure as a tool (Rizwan can correct via admin if needed). Keep: `load_client_context()`, `search_memory()`, `write_finding()`, `checkpoint_sync()`, `end_session()`.

### 7. Simplified Frontend Dashboard

**v2.0 had:** Dashboard, Memory Inspector, Workflow Trigger, HITL Queue, Deliverables, Settings, Share.

**v3.0 needs:**

| Page | Purpose | Existing? |
|------|---------|-----------|
| `/` (Dashboard) | Client count, recent runs, running workflows | SIMPLIFY existing `page.tsx` |
| `/clients` | Client list with add/edit | KEEP existing `clients/page.tsx` |
| `/clients/[id]` | Client detail: recent runs, brand voice, deliverables | SIMPLIFY existing `clients/[id]/page.tsx` |
| `/workflows` | Workflow catalog + trigger form | SIMPLIFY existing `workflows/page.tsx` |
| `/workflows/[id]` | Live run monitor (SSE-driven phase progress) | KEEP existing `workflows/[id]/page.tsx` |
| `/deliverables` | All deliverables across clients | SIMPLIFY existing `deliverables/page.tsx` |
| `/deliverables/[id]` | Deliverable detail: HTML report + markdown source | KEEP existing `deliverables/[id]/page.tsx` |

**REMOVE pages:**
- `/approvals` -- no HITL queue
- `/memory` -- no memory inspector (can re-add later)
- `/settings` -- no agency settings for personal tool

**SSE simplification:** v2.0 used agency-scoped channels (`agency-{uuid}`). v3.0 uses a single channel (`run_events`) since there is only one user. The SSE view simplifies to:

```python
def send_run_event(event_type: str, data: dict) -> None:
    send_event("run_events", "message", {"type": event_type, **data})
```

---

## Patterns to Follow

### Pattern 1: YAML Phase Walker

**What:** Sequential phase execution driven by workflow YAML, with parallel execution within waves.
**When:** Every workflow run.

The existing `get_execution_order()` in `workflow_parser.py` already computes topological waves. The simplified executor iterates these waves identically to v2.0, but without the enterprise middleware (conflict detection, HITL checkpoints, budget checks).

```python
async def run(self, workflow: WorkflowSchema, client_id: str, run: WorkflowRun) -> WorkflowRun:
    waves = get_execution_order(workflow)
    for wave in waves:
        phases = [self._phase_map[pid] for pid in wave if pid in self._phase_map]
        results = await asyncio.gather(
            *(self._execute_phase(phase, client_id, run) for phase in phases),
            return_exceptions=True,
        )
        # Check for required phase failures
        for phase, result in zip(phases, results):
            if isinstance(result, Exception) and phase.required:
                run.status = "failed"
                run.error_details = {"error": str(result)[:500]}
                run.save()
                send_run_event("workflow_failed", {"run_id": str(run.pk), "error": str(result)[:500]})
                return run
    run.status = "completed"
    run.save()
    return run
```

### Pattern 2: Tool Function Registration

**What:** Register tools as plain Python functions with Anthropic API schema.
**When:** At Celery worker startup or per-workflow execution.

```python
def build_tool_registry(memory: HaznMemory) -> ToolRegistry:
    """Build registry with all available tools for this execution."""
    registry = ToolRegistry()

    # Memory tools -- closures over HaznMemory instance
    registry.register(ToolDef(
        name="search_memory",
        description="Search agent's archival memory semantically.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Max results", "default": 5},
            },
            "required": ["query"],
        },
        fn=lambda query, limit=5: memory.search_memory(query, limit),
    ))

    # Analytics tools -- direct function references
    from hazn_platform.tools.analytics import pull_ga4_data, query_gsc, check_pagespeed
    registry.register(ToolDef(
        name="pull_ga4_data",
        description="Pull GA4 traffic overview for a property.",
        input_schema={...},
        fn=pull_ga4_data,
    ))

    # Credential tools
    registry.register(ToolDef(
        name="get_credentials",
        description="Fetch credentials for a service from Vault.",
        input_schema={
            "type": "object",
            "properties": {
                "service_name": {"type": "string"},
            },
            "required": ["service_name"],
        },
        fn=lambda service_name: vault_get_credentials(client_id, service_name),
    ))

    return registry
```

### Pattern 3: Memory-First Agent Execution

**What:** Every agent phase starts by loading client context from Letta, and ends by syncing learnings back.
**When:** Every phase with an agent.

```python
async def _execute_phase(self, phase, client_id, run):
    if not phase.agent:
        return None

    # 1. Get or create persistent Letta agent
    agent_id = get_or_create_agent(phase.agent, client_id)

    # 2. Load client context into Letta agent
    memory = HaznMemory(agent_id, client_id, agency_id)
    memory.load_client_context()

    # 3. Assemble prompt with context
    system_prompt = assemble_prompt(phase.agent, phase.skills, client_context)

    # 4. Build tool registry with memory reference
    registry = build_tool_registry(memory)
    tools = registry.get_anthropic_tools(phase.tools)

    # 5. Run agent
    backend = AnthropicAPIBackend()
    result = await backend.execute(system_prompt, messages, tools, registry.dispatch)

    # 6. Sync learnings
    memory.checkpoint_sync()

    # 7. Wipe active context (ready for next run)
    # (done at workflow end, not per-phase)

    return result
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Keeping Enterprise Middleware "Just in Case"

**What:** Leaving HITL checks, budget enforcement, and conflict detection in the code path but "disabled" via feature flags.
**Why bad:** Dead code paths increase cognitive load, slow debugging, and create confusion about which code is actually executing. Every `if settings.ENABLE_HITL:` branch is technical debt.
**Instead:** Remove the enterprise code entirely. The git history preserves it. If needed later, re-implement cleanly for the new use case rather than resurrecting multi-tenant abstractions.

### Anti-Pattern 2: Wrapping Python Functions in MCP Server Shells

**What:** Keeping the MCP server module structure but "simplifying" by removing the FastMCP decorators while keeping the file organization.
**Why bad:** Four separate server modules with initialization boilerplate, when all you need is a dict of functions. The MCP transport layer added value for cross-process communication; without it, the module structure is overhead.
**Instead:** Extract the pure Python function bodies into a single `tools/` package organized by domain (`tools/analytics.py`, `tools/memory.py`, `tools/credentials.py`). Register in ToolRegistry.

### Anti-Pattern 3: Over-Abstracting the Simplified Version

**What:** Building a ToolRegistry base class, factory pattern, dependency injection container for tool registration.
**Why bad:** This is a personal tool for one person. Abstractions serve teams. A dict of callables with a dispatch method is sufficient.
**Instead:** ToolRegistry as shown above: register(), get_anthropic_tools(), dispatch(). Three methods. Done.

### Anti-Pattern 4: Removing Letta Agent Persistence

**What:** Creating a fresh Letta agent per workflow run instead of reusing persistent agents per client.
**Why bad:** Destroys the core value proposition -- compounding memory. If each run starts fresh, the agent cannot build on past findings, brand voice evolution, or keyword history.
**Instead:** Keep `get_or_create_agent()` naming convention (`{agent_type}--{client_id}`). Agents persist across runs. Only `active_client_context` is reset between runs; archival memory accumulates.

---

## Integration Points Summary

### New vs Modified vs Unchanged

| Component | Status | What Specifically Changes |
|-----------|--------|--------------------------|
| `orchestrator/tool_registry.py` | **NEW** | Simple name->function registry replacing ToolRouter + tool_wiring + MCP servers |
| `tools/analytics.py` | **NEW** | GA4/GSC/PageSpeed functions extracted from MCP server code |
| `tools/memory.py` | **NEW** | Memory tool wrappers that call HaznMemory methods |
| `tools/credentials.py` | **NEW** | Vault credential fetch wrapper |
| `orchestrator/executor.py` | **SIMPLIFIED** | Remove ~300 lines of enterprise middleware from `_execute_phase()` and `run()` |
| `orchestrator/backends/anthropic_api.py` | **SIMPLIFIED** | Remove BudgetEnforcer, MeteringCallback params; keep tool_use loop |
| `orchestrator/agent_runner.py` | **SIMPLIFIED** | Remove ToolRouter dependency, simplify to direct dispatch |
| `orchestrator/session.py` | **SIMPLIFIED** | Remove metering, conflict logging; keep status transitions + memory lifecycle |
| `orchestrator/tasks.py` | **SIMPLIFIED** | Remove 5 of 6 tasks; keep run_workflow |
| `orchestrator/models.py` | **SIMPLIFIED** | Remove HITLItem, WorkflowAgent, WorkflowToolCall; simplify WorkflowRun |
| `workspace/views.py` | **SIMPLIFIED** | Remove 3 views; simplify 2 views |
| `workspace/sse_views.py` | **SIMPLIFIED** | Single channel instead of agency-scoped |
| `frontend/src/` | **SIMPLIFIED** | Remove 3 pages; simplify dashboard |
| `core/memory.py` | **UNCHANGED** | HaznMemory works as-is |
| `core/letta_client.py` | **UNCHANGED** | Client factory unchanged |
| `core/vault.py` | **UNCHANGED** | Vault integration unchanged |
| `core/models.py` | **UNCHANGED** | Keep models, simplify usage |
| `orchestrator/workflow_parser.py` | **UNCHANGED** | YAML loading unchanged |
| `orchestrator/workflow_models.py` | **UNCHANGED** | Schema models sufficient |
| `orchestrator/prompt_assembler.py` | **UNCHANGED** | Prompt assembly unchanged |
| `orchestrator/output_collector.py` | **UNCHANGED** | Artifact extraction unchanged |
| `deliverable_pipeline/` | **UNCHANGED** | Jinja2 rendering unchanged |

### Build Order (Dependency-Aware)

```
Phase 1: Extract Tool Functions (no runtime deps)
  1a. Create tools/ package
  1b. Extract analytics functions from mcp_servers/analytics_server.py
  1c. Create memory tool wrappers calling HaznMemory
  1d. Create credential tool wrapper calling Vault
  1e. Build ToolRegistry with all tool registrations
  -> Testable independently: register tools, call dispatch, verify results

Phase 2: Simplify Backend (deps: Phase 1)
  2a. Simplify AnthropicAPIBackend: remove budget/metering params
  2b. Simplify RunResult: remove unused fields
  2c. Wire ToolRegistry.dispatch as tool_dispatch
  -> Testable: mock API, dispatch tools through registry

Phase 3: Simplify Executor (deps: Phase 2)
  3a. Strip enterprise middleware from _execute_phase()
  3b. Strip enterprise middleware from run()
  3c. Wire ToolRegistry into executor
  3d. Simplify SSE to single channel
  -> Testable: mock backend, run executor with real YAML

Phase 4: Simplify Models + Session (deps: Phase 3)
  4a. Create migration: remove HITLItem, WorkflowAgent, WorkflowToolCall
  4b. Simplify WorkflowRun model (or just ignore unused fields)
  4c. Simplify WorkflowSession: remove metering, conflict logging
  4d. Create default Agency + seed script
  -> Testable: run migrations, verify model operations

Phase 5: Simplify Celery Task (deps: Phase 4)
  5a. Strip run_workflow to essentials
  5b. Remove 5 other tasks
  5c. Simplify task dispatch in views
  -> Testable: trigger via API, verify Celery execution

Phase 6: Simplify Frontend (deps: Phase 5)
  6a. Remove approvals, memory, settings pages
  6b. Simplify dashboard to client count + recent runs
  6c. Simplify workflow trigger form
  6d. Simplify SSE subscription to single channel
  6e. Verify deliverable rendering
  -> Testable: full E2E in browser

Phase 7: End-to-End Validation (deps: all)
  7a. Run analytics-audit workflow on real client
  7b. Verify Letta memory compounding across runs
  7c. Verify deliverable HTML rendering
  7d. Run all 7 workflows, note which need tool additions
```

**Phase ordering rationale:**
- Phase 1 has zero runtime dependencies -- pure function extraction
- Phase 2 needs Phase 1 tools for dispatch wiring
- Phase 3 needs Phase 2 backend for agent execution
- Phase 4 needs Phase 3 to understand which model fields are actually used
- Phase 5 needs Phase 4 models for task creation
- Phase 6 needs Phase 5 API endpoints to be stable
- Phase 7 validates the full stack

---

## Scalability Considerations

| Concern | At 1 user / 8 clients | At 1 user / 20 clients | Notes |
|---------|----------------------|----------------------|-------|
| Concurrent workflows | 1-2 at a time (Celery single worker) | 2-3 (scale workers) | Anthropic API rate limits are the real bottleneck |
| Letta agents | ~120 agents (15 types x 8 clients) | ~300 agents | Letta handles this fine -- each is a row in Postgres |
| Archival memory | 1-5 MB per client after 10 runs | Manageable with pgvector | Composite ranking naturally ages out old data |
| Postgres load | Minimal -- single user | Minimal | No multi-tenant query overhead |
| Docker resources | 4-6 GB RAM (Postgres, Letta, Redis, Django, Celery) | Same | Single Celery worker sufficient |

---

## Sources

- [Anthropic Messages API - Tool Use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use) -- tool_use loop pattern, stop_reason handling (HIGH confidence)
- [Anthropic Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use) -- best practices for tool error handling, input validation (HIGH confidence)
- [Letta Python SDK](https://docs.letta.com/api/python/) -- agent creation, memory blocks, archival search (HIGH confidence)
- [Letta GitHub](https://github.com/letta-ai/letta) -- self-hosted architecture, Postgres backend (HIGH confidence)
- [Django Celery Integration](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html) -- task patterns, worker configuration (HIGH confidence)
- Existing codebase: All files in `hazn_platform/hazn_platform/` -- direct code examination (HIGH confidence)
- Existing codebase: All files in `hazn/` -- workflow YAMLs, agent personas, skill definitions (HIGH confidence)

---
*Architecture research for: Hazn v3.0 Simplified Multi-Client Workflow Runner*
*Researched: 2026-03-12*
*Supersedes: v2.0 Architecture Research (2026-03-06)*

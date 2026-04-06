# Phase 9: Agent Execution Runtime - Research

**Researched:** 2026-03-06
**Domain:** LLM agent execution loops, Anthropic API tool_use, Claude Agent SDK, cost controls
**Confidence:** HIGH

## Summary

Phase 9 replaces the executor.py placeholder (lines 226-248) with a real AgentRunner that executes multi-turn tool_use conversations against the Anthropic API (Mode 3) and Claude Agent SDK (Mode 1). The core challenge is implementing the agentic loop -- send messages with tools, check stop_reason, dispatch tool calls via ToolRouter, feed results back -- with budget enforcement after every turn. The secondary challenge is providing a strategy-pattern dual runtime so the same workflow can execute via either backend based on configuration.

The Anthropic Python SDK (v0.84.0) provides everything needed for the Mode 3 path: `client.messages.create()` returns a response with `stop_reason`, `content` blocks (text/tool_use), and `usage` (input_tokens, output_tokens). The loop terminates when `stop_reason == "end_turn"` (no tool calls). The Claude Agent SDK (v0.1.47) wraps the Claude CLI and provides `query()` and `ClaudeSDKClient` with MCP tool support via `@tool` decorator and `create_sdk_mcp_server()`. It has built-in `max_turns` and `max_budget_usd` controls.

**Primary recommendation:** Build the AnthropicAPIBackend first as the primary runtime (more control, direct token counting), then wrap the Agent SDK as AgentSDKBackend using `query()` with `create_sdk_mcp_server()` for in-process tool execution. Use the strategy pattern with a `RuntimeBackend` Protocol to isolate both behind a common interface.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Tool_use Loop Mechanics:**
- Agent completion signaled by text-only response (no tool_use blocks) -- standard Anthropic pattern
- Max turns configurable per-workflow via workflow YAML `budget.max_turns` field
- Full conversation history maintained in each API call (system + all messages). 200k context window handles it
- Parallel tool execution via asyncio.gather when Claude returns multiple tool_use blocks in one response

**Budget Enforcement:**
- Hard halt after current turn completes when token/cost budget exceeded -- no more API calls sent
- Per-workflow token/cost budgets defined in workflow YAML: `budget: { max_tokens, max_cost, max_turns }`
- Rolling monthly cost cap per agency with 80% alert threshold and automatic block when cap reached
- Partial results preserved on budget halt -- stored as WorkflowPhaseOutput with status='partial'
- Budget check happens after each on_llm_call to MeteringCallback

**Runtime Selection:**
- Environment variable `HAZN_RUNTIME_MODE` (values: `agent_sdk` or `api`, default: `api`)
- Strategy pattern: one AgentRunner class with pluggable RuntimeBackend (Protocol)
- Two backend implementations: AnthropicAPIBackend and AgentSDKBackend
- Both backends built in this phase (Agent SDK is alpha but strategy interface isolates instability)
- Model: claude-sonnet-4-5 for the Anthropic API backend

**MCP Tool Wiring:**
- Direct import of FastMCP tool functions from server modules -- in-process, no subprocess management
- ToolRouter dispatch methods become async (await coroutines, call sync directly)
- Wire callables once at Django startup via AppConfig.ready() -- singleton registry shared across runs
- Tool errors returned to agent as is_error=true tool_result messages -- agent decides how to proceed (retry, skip, report)

### Claude's Discretion
- AgentRunner internal class structure and method signatures beyond the RuntimeBackend Protocol
- How to extract token counts and cost from Anthropic API responses for metering
- Agent SDK backend implementation details and error handling for alpha instability
- Tool wiring module organization (single wire_callables function vs per-server wiring)
- How to scope tools per-phase (filter registry to only tools declared in workflow phase YAML)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| RUNT-02 | AgentRunner executes tool_use loop with turn counting and conversation management | Anthropic API tool_use loop pattern verified, response format documented, parallel tool handling confirmed |
| RUNT-04 | Claude Agent SDK integration for Mode 1 execution (Max subscription) | Agent SDK v0.1.47 API documented: `query()`, `ClaudeSDKClient`, `create_sdk_mcp_server()`, `ClaudeAgentOptions` with `max_turns`/`max_budget_usd` |
| RUNT-05 | Anthropic API integration for Mode 3 execution (metered per-token) | Anthropic SDK v0.84.0 `messages.create()` API verified, usage object structure confirmed (input_tokens, output_tokens, cache tokens) |
| RUNT-06 | Per-workflow token budgets with enforcement and runaway detection | Budget enforcement architecture designed: check after each on_llm_call, hard halt before next API call, WorkflowPhaseOutput with status='partial' |
| RUNT-07 | Per-agency cost caps with alerts and automatic halt | Agency model has tool_preferences JSONField for thresholds, MeteringCallback.from_agency() already reads these, need rolling monthly aggregation |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| anthropic | 0.84.0 | Anthropic Messages API client for Mode 3 | Official Python SDK, Pydantic response models, sync+async |
| claude-agent-sdk | 0.1.47 | Claude Agent SDK for Mode 1 | Official SDK, bundles CLI, in-process MCP tool support |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| langfuse | >=3.14.0 | Already installed, tracing + observability | Every API call metered through existing pipeline |
| pydantic | (existing) | Budget config schemas, response types | Define BudgetConfig, RunResult models |
| asyncio | stdlib | Parallel tool execution, async loop | Multiple tool_use blocks in single response |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Manual tool_use loop | anthropic beta tool_runner | Tool runner auto-manages loop but gives less control over budget enforcement between turns. Manual loop required for per-turn budget checks. |
| claude-agent-sdk | Direct CLI subprocess | SDK wraps CLI cleanly with Pydantic types. Direct subprocess loses MCP tool support. |

**Installation:**
```bash
pip install anthropic>=0.84.0 claude-agent-sdk>=0.1.47
```

## Architecture Patterns

### Recommended Project Structure
```
hazn_platform/orchestrator/
    agent_runner.py          # AgentRunner + RuntimeBackend Protocol
    backends/
        __init__.py
        anthropic_api.py     # AnthropicAPIBackend
        agent_sdk.py         # AgentSDKBackend
    budget.py                # BudgetEnforcer, BudgetConfig, AgencyCostCap
    tool_wiring.py           # wire_callables(), tool function imports
    apps.py                  # AppConfig.ready() calls wire_callables()
    executor.py              # _execute_phase() delegates to AgentRunner
    metering.py              # Existing -- extended with budget_exceeded flag
    ...existing files...
```

### Pattern 1: Strategy Pattern with RuntimeBackend Protocol

**What:** Define a `RuntimeBackend` Protocol with a single async method. AgentRunner delegates execution to whichever backend is configured.

**When to use:** Always -- this is the locked decision for dual-runtime support.

**Example:**
```python
# Source: User decision in CONTEXT.md + Anthropic API docs
from typing import Protocol, runtime_checkable

@runtime_checkable
class RuntimeBackend(Protocol):
    """Protocol for agent execution backends."""

    async def execute(
        self,
        system_prompt: str,
        tools: list[dict],
        tool_dispatch: Callable,
        budget: BudgetConfig,
        metering: MeteringCallback,
        on_turn: Callable,
    ) -> RunResult:
        """Execute a tool_use loop until completion or budget halt."""
        ...
```

### Pattern 2: Anthropic API Tool_use Loop

**What:** The standard agentic loop: send messages, check stop_reason, dispatch tools, feed results back.

**When to use:** AnthropicAPIBackend (Mode 3).

**Example:**
```python
# Source: https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use
import anthropic

client = anthropic.AsyncAnthropic()
messages = [{"role": "user", "content": initial_prompt}]

while True:
    response = await client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4096,
        system=system_prompt,
        tools=tools,
        messages=messages,
    )

    # Meter this call
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    total_tokens = input_tokens + output_tokens
    cost = _calculate_cost(input_tokens, output_tokens)
    metering.on_llm_call(agent_id, tokens=total_tokens, cost=cost)

    # Budget check AFTER metering
    if budget_enforcer.is_exceeded():
        # Preserve partial results
        break

    if response.stop_reason == "tool_use":
        # Extract ALL tool_use blocks (parallel tool calls)
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]

        # Dispatch all tools (parallel via asyncio.gather)
        tool_results = await asyncio.gather(
            *(dispatch_tool(block) for block in tool_use_blocks)
        )

        # Append assistant response + all tool results
        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                }
                for block, result in zip(tool_use_blocks, tool_results)
            ],
        })
    else:
        # stop_reason == "end_turn" or "max_tokens"
        break
```

### Pattern 3: Claude Agent SDK with In-Process MCP Tools

**What:** Use `query()` with `create_sdk_mcp_server()` to run agent with custom tools in-process.

**When to use:** AgentSDKBackend (Mode 1).

**Example:**
```python
# Source: https://platform.claude.com/docs/en/agent-sdk/python
from claude_agent_sdk import query, tool, create_sdk_mcp_server, ClaudeAgentOptions

# Wrap existing ToolRouter callables as SDK tools
sdk_tools = []
for entry in tool_router.get_all_entries():
    @tool(entry.tool_name, entry.description, entry.input_schema)
    async def handler(args, _entry=entry):
        return {"content": [{"type": "text", "text": str(_entry.callable(**args))}]}
    sdk_tools.append(handler)

server = create_sdk_mcp_server("hazn-tools", tools=sdk_tools)

options = ClaudeAgentOptions(
    system_prompt=system_prompt,
    mcp_servers={"hazn": server},
    allowed_tools=[f"mcp__hazn__{t}" for t in tool_names],
    permission_mode="bypassPermissions",
    max_turns=budget.max_turns,
    max_budget_usd=budget.max_cost,
)

async for message in query(prompt=initial_prompt, options=options):
    # Process messages: AssistantMessage, ToolUseMessage, ResultMessage
    pass
```

### Pattern 4: Budget Enforcement

**What:** Check accumulated cost/tokens after each LLM call, halt before next API call if exceeded.

**When to use:** Every turn in the agent loop.

**Example:**
```python
class BudgetEnforcer:
    """Tracks accumulated usage against per-workflow budget limits."""

    def __init__(self, config: BudgetConfig):
        self.max_tokens = config.max_tokens
        self.max_cost = config.max_cost
        self.max_turns = config.max_turns
        self._total_tokens = 0
        self._total_cost = 0.0
        self._turns = 0

    def record(self, tokens: int, cost: float) -> None:
        self._total_tokens += tokens
        self._total_cost += cost
        self._turns += 1

    def is_exceeded(self) -> str | None:
        """Return reason string if budget exceeded, None if within budget."""
        if self.max_tokens and self._total_tokens >= self.max_tokens:
            return f"token_budget_exceeded ({self._total_tokens}/{self.max_tokens})"
        if self.max_cost and self._total_cost >= self.max_cost:
            return f"cost_budget_exceeded (${self._total_cost:.4f}/${self.max_cost})"
        if self.max_turns and self._turns >= self.max_turns:
            return f"turn_budget_exceeded ({self._turns}/{self.max_turns})"
        return None
```

### Pattern 5: Agency Rolling Monthly Cost Cap

**What:** Aggregate all WorkflowRun.total_cost for an agency in the current month, block new runs when cap reached.

**When to use:** Pre-flight check before starting any workflow run, and alert at 80% threshold.

**Example:**
```python
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime

def check_agency_cost_cap(agency) -> tuple[bool, float, float]:
    """Check if agency has exceeded its monthly cost cap.

    Returns: (blocked, current_spend, cap)
    """
    cap = (agency.tool_preferences or {}).get("monthly_cost_cap", 100.0)
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    current_spend = (
        WorkflowRun.objects
        .filter(agency=agency, created_at__gte=month_start)
        .aggregate(total=Sum("total_cost"))["total"]
    ) or Decimal("0")

    return float(current_spend) >= cap, float(current_spend), cap
```

### Anti-Patterns to Avoid

- **Streaming before correctness:** Do NOT implement streaming responses in this phase. Get the basic loop working first. Streaming can be added later for Phase 10 UI integration.
- **Context window overflow without protection:** With full conversation history, a long-running agent could exceed 200k tokens. Add a max_context_tokens check that truncates oldest tool_results (keep system prompt + last N turns).
- **Blocking Django ORM calls in async context:** All Django ORM writes (WorkflowPhaseOutput, WorkflowRun updates) must use `sync_to_async`. The existing codebase already follows this pattern.
- **Swallowing tool errors silently:** Tool errors MUST be returned to the agent as `is_error: true` tool_result messages (already implemented in ToolRouter). Never swallow them -- the agent needs error feedback to decide next steps.
- **Hardcoding API keys:** Use `os.environ["ANTHROPIC_API_KEY"]` or Django settings. The Anthropic SDK reads `ANTHROPIC_API_KEY` from environment by default.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Anthropic API client | HTTP requests to api.anthropic.com | `anthropic.AsyncAnthropic()` | Handles auth, retries, rate limiting, response parsing, Pydantic models |
| Cost calculation from tokens | Custom pricing tables | Lookup table with model-specific rates | Pricing changes; keep it in one place, easy to update |
| Agent SDK CLI management | subprocess.Popen for Claude CLI | `claude-agent-sdk` query()/ClaudeSDKClient | Handles process lifecycle, stdio, message parsing |
| Tool schema generation | Manual JSON Schema dicts | Existing ToolRouter.to_anthropic_tools() | Already built in Phase 8, returns correct format |
| Langfuse trace creation | Custom HTTP to Langfuse API | Existing tracing.py functions | Already built with non-fatal wrappers |

**Key insight:** Most of the infrastructure exists from Phases 3-8. AgentRunner is the missing piece that wires PromptAssembler output + ToolRouter dispatch + MeteringCallback tracking into a real LLM conversation loop.

## Common Pitfalls

### Pitfall 1: Tool Result Ordering in Messages
**What goes wrong:** Sending text content BEFORE tool_result blocks in the user message causes a 400 error from the Anthropic API.
**Why it happens:** The API requires tool_result blocks to come FIRST in the content array, before any text.
**How to avoid:** Always construct the user message with tool_results first: `content = tool_results + optional_text_blocks`.
**Warning signs:** 400 errors from the API with validation messages about content ordering.

### Pitfall 2: Forgetting to Serialize Response Content for Messages
**What goes wrong:** Passing Pydantic content block objects directly when constructing the assistant message in the history.
**Why it happens:** The Anthropic SDK returns `response.content` as a list of Pydantic models (TextBlock, ToolUseBlock). When appending to messages, these need to be in the right format.
**How to avoid:** Use `response.content` directly when building the assistant message -- the SDK's `.model_dump()` or direct pass-through handles serialization. Test this in integration tests.
**Warning signs:** Serialization errors or unexpected message formats.

### Pitfall 3: Not Handling max_tokens Stop Reason
**What goes wrong:** Only checking for `"end_turn"` and `"tool_use"` stop reasons, ignoring `"max_tokens"`.
**Why it happens:** `max_tokens` means the response was truncated, not that the agent is done. A truncated tool_use block is invalid.
**How to avoid:** Treat `max_tokens` as an error condition -- log it, set status to 'error', and preserve partial results. Consider increasing `max_tokens` parameter.
**Warning signs:** Incomplete or malformed responses, JSON parse errors in tool_use blocks.

### Pitfall 4: Agent SDK Alpha Instability
**What goes wrong:** SDK behavior changes between minor versions, CLI bundling issues, subprocess hangs.
**Why it happens:** The Agent SDK is v0.1.47 (alpha). Interface changes are expected.
**How to avoid:** Pin the version. Wrap all Agent SDK calls in try/except with fallback logging. The strategy pattern isolates instability -- if SDK breaks, switch to API mode. Keep SDK tests marked as integration tests.
**Warning signs:** Import errors after pip upgrade, hanging subprocesses, unexpected message types.

### Pitfall 5: Django Async Context Issues
**What goes wrong:** `SynchronousOnlyOperation` errors when calling Django ORM from an async context.
**Why it happens:** Django ORM is synchronous. Calling it directly from an async function raises this error.
**How to avoid:** Always use `sync_to_async()` for any Django ORM call within async agent loop code. The existing executor.py shows the correct pattern.
**Warning signs:** `SynchronousOnlyOperation` exception at runtime.

### Pitfall 6: Cost Calculation Drift
**What goes wrong:** Token-to-cost calculation uses stale pricing, leading to budget enforcement errors.
**Why it happens:** Anthropic changes pricing. Hardcoded rates become stale.
**How to avoid:** Put pricing in a config dict keyed by model name. Keep it in one place (e.g., `PRICING` dict in budget.py). Log a warning if the model isn't in the pricing table.
**Warning signs:** Budget never triggers despite heavy usage, or triggers too early.

## Code Examples

### Extracting Token Counts and Cost from Anthropic API Response

```python
# Source: https://platform.claude.com/docs/en/api/messages
# Verified against official API reference

# Pricing for claude-sonnet-4-5 (as of March 2026)
MODEL_PRICING = {
    "claude-sonnet-4-5": {
        "input_per_million": 3.00,
        "output_per_million": 15.00,
        "cache_write_per_million": 3.75,
        "cache_read_per_million": 0.30,
    },
}

def calculate_cost(response, model: str = "claude-sonnet-4-5") -> float:
    """Calculate USD cost from an Anthropic API response."""
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["claude-sonnet-4-5"])
    usage = response.usage

    cost = (
        (usage.input_tokens / 1_000_000) * pricing["input_per_million"]
        + (usage.output_tokens / 1_000_000) * pricing["output_per_million"]
        + (getattr(usage, 'cache_creation_input_tokens', 0) / 1_000_000) * pricing["cache_write_per_million"]
        + (getattr(usage, 'cache_read_input_tokens', 0) / 1_000_000) * pricing["cache_read_per_million"]
    )
    return cost
```

### Making ToolRouter Dispatch Async

```python
# Current ToolRouter.dispatch_anthropic is sync.
# For Phase 9, tool callables may be async (FastMCP tools are sync but could be wrapped).
# Approach: detect if callable is coroutine and handle accordingly.

import asyncio
import inspect
import time

async def dispatch_tool_async(
    router: ToolRouter,
    tool_use_block: dict,
    metering: MeteringCallback,
) -> dict:
    """Async wrapper around ToolRouter.dispatch_anthropic with metering."""
    tool_name = tool_use_block["name"] if isinstance(tool_use_block, dict) else tool_use_block.name
    tool_input = tool_use_block.get("input", {}) if isinstance(tool_use_block, dict) else tool_use_block.input
    tool_id = tool_use_block["id"] if isinstance(tool_use_block, dict) else tool_use_block.id

    entry = router.get_tool(tool_name)
    start = time.monotonic()
    success = True

    try:
        if entry is None or entry.callable is None:
            return {
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": f"Unknown or unwired tool: {tool_name}",
                "is_error": True,
            }

        # Handle async vs sync callables
        if inspect.iscoroutinefunction(entry.callable):
            result = await entry.callable(**tool_input)
        else:
            result = await asyncio.to_thread(entry.callable, **tool_input)

        import json
        content = json.dumps(result) if isinstance(result, (dict, list)) else str(result)
        return {
            "type": "tool_result",
            "tool_use_id": tool_id,
            "content": content,
        }
    except Exception as exc:
        success = False
        return {
            "type": "tool_result",
            "tool_use_id": tool_id,
            "content": f"Tool error: {exc}",
            "is_error": True,
        }
    finally:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        metering.on_tool_call(tool_name, latency_ms=elapsed_ms, success=success)
```

### Wiring Tool Callables at Django Startup

```python
# tool_wiring.py
import logging
from hazn_platform.orchestrator.tool_router import ToolRouter

logger = logging.getLogger(__name__)

def wire_callables(router: ToolRouter) -> int:
    """Wire FastMCP tool functions into the ToolRouter registry.

    Imports actual tool functions from MCP server modules and sets
    them as callables on the corresponding ToolRegistryEntry.

    Returns the number of tools wired.
    """
    wired = 0

    # Import server modules (requires Django configured)
    from hazn_platform.mcp_servers.hazn_memory_server import (
        load_context, write_finding, search_memory,
        search_cross_client_insights, checkpoint_sync,
        correct_memory, get_credentials,
    )
    from hazn_platform.mcp_servers.analytics_server import (
        pull_ga4_data, query_gsc, check_pagespeed,
    )
    from hazn_platform.mcp_servers.github_server import (
        create_repo, create_pr, get_pr_status,
        get_ci_status, list_branches, merge_pr,
    )
    from hazn_platform.mcp_servers.vercel_server import (
        deploy_project, get_deployment_status,
        get_preview_url, list_deployments,
    )

    # Map tool names to their actual functions
    callables = {
        "load_context": load_context,
        "write_finding": write_finding,
        "search_memory": search_memory,
        "search_cross_client_insights": search_cross_client_insights,
        "checkpoint_sync": checkpoint_sync,
        "correct_memory": correct_memory,
        "get_credentials": get_credentials,
        "pull_ga4_data": pull_ga4_data,
        "query_gsc": query_gsc,
        "check_pagespeed": check_pagespeed,
        "create_repo": create_repo,
        "create_pr": create_pr,
        "get_pr_status": get_pr_status,
        "get_ci_status": get_ci_status,
        "list_branches": list_branches,
        "merge_pr": merge_pr,
        "deploy_project": deploy_project,
        "get_deployment_status": get_deployment_status,
        "get_preview_url": get_preview_url,
        "list_deployments": list_deployments,
    }

    for tool_name, func in callables.items():
        entry = router.get_tool(tool_name)
        if entry:
            entry.callable = func
            wired += 1
        else:
            logger.warning("Tool %s not in registry, skipping wiring", tool_name)

    logger.info("Wired %d/%d tool callables", wired, len(callables))
    return wired
```

### Filtering Tools Per Phase

```python
def scope_tools_for_phase(
    router: ToolRouter,
    phase_tools: list[str],
) -> list[dict]:
    """Return Anthropic API tools array filtered to phase-declared tools.

    If phase_tools is empty, return all tools (backward compat).
    """
    if not phase_tools:
        return router.to_anthropic_tools()

    return [
        {
            "name": entry.tool_name,
            "description": entry.description,
            "input_schema": entry.input_schema,
        }
        for name in phase_tools
        if (entry := router.get_tool(name)) is not None
    ]
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| claude-code-sdk (deprecated) | claude-agent-sdk v0.1.47 | 2025-12 | Package renamed, all imports change from `claude_code_sdk` to `claude_agent_sdk` |
| Manual tool_use loop only | SDK provides beta tool_runner | 2025-Q4 | Tool runner auto-manages loop, but manual loop needed for custom budget control |
| Anthropic SDK < 0.50 | anthropic 0.84.0 | 2026-02 | AsyncAnthropic client fully stable, Pydantic v2 models, cache token fields in usage |
| Agent SDK `query()` only | `query()` + `ClaudeSDKClient` | 2025 | ClaudeSDKClient supports multi-turn conversation, interrupts, session continuity |

**Deprecated/outdated:**
- `claude-code-sdk` package: Replaced by `claude-agent-sdk`. Do NOT install the old package.
- `max_thinking_tokens` in ClaudeAgentOptions: Deprecated, use `thinking: ThinkingConfig` instead.

## Open Questions

1. **Input schema completeness for ToolRouter entries**
   - What we know: `build_tool_registry()` sets `input_schema={"type": "object"}` for all tools (a minimal placeholder).
   - What's unclear: The Anthropic API needs full JSON Schema with `properties` and `required` for Claude to call tools correctly. Minimal schema may cause Claude to guess parameters.
   - Recommendation: Update `_STATIC_TOOL_MAP` to include full input_schema per tool, or extract schemas from FastMCP `@mcp.tool()` decorated functions during wiring. This should be done as part of tool wiring in this phase.

2. **Agent SDK token/cost visibility**
   - What we know: The Agent SDK provides `max_budget_usd` and `max_turns` in ClaudeAgentOptions. Messages yielded include `ResultMessage` with usage info.
   - What's unclear: Exact format and granularity of per-turn token counts from SDK messages. The SDK wraps CLI which may not expose per-call usage.
   - Recommendation: For Mode 1, accept that per-call metering may be less granular. Use `ResultMessage` final totals. Flag as integration test requirement.

3. **Monthly cost aggregation performance**
   - What we know: Need `SUM(total_cost) WHERE agency_id=X AND created_at >= month_start` before every workflow run.
   - What's unclear: Whether this query is fast enough under load (many concurrent workflow runs).
   - Recommendation: Acceptable for v2.0 volume. Add a database index on `(agency_id, created_at)` if not present. Consider caching with Redis TTL=60s if needed later.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 + pytest-django 4.12.0 + pytest-asyncio >=0.23.0 |
| Config file | pyproject.toml `[tool.pytest.ini_options]` |
| Quick run command | `cd hazn_platform && python -m pytest tests/test_agent_runner.py -x -q` |
| Full suite command | `cd hazn_platform && python -m pytest tests/ -x -q` |

### Phase Requirements --> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RUNT-02 | AgentRunner executes multi-turn tool_use loop | unit (mocked API) | `pytest tests/test_agent_runner.py::TestAgentRunnerLoop -x` | Wave 0 |
| RUNT-02 | Parallel tool dispatch via asyncio.gather | unit (mocked API) | `pytest tests/test_agent_runner.py::TestParallelToolDispatch -x` | Wave 0 |
| RUNT-04 | Agent SDK backend executes with MCP tools | integration (requires CLI) | `pytest tests/test_agent_sdk_backend.py -x -m integration` | Wave 0 |
| RUNT-05 | Anthropic API backend completes tool_use loop | integration (requires API key) | `pytest tests/test_anthropic_backend.py -x -m integration` | Wave 0 |
| RUNT-05 | Cost calculated correctly from API response usage | unit | `pytest tests/test_budget.py::TestCostCalculation -x` | Wave 0 |
| RUNT-06 | Workflow halts when token budget exceeded | unit (mocked API) | `pytest tests/test_budget.py::TestBudgetEnforcement -x` | Wave 0 |
| RUNT-06 | Partial results preserved on budget halt | unit (mocked API) | `pytest tests/test_agent_runner.py::TestBudgetHalt -x` | Wave 0 |
| RUNT-07 | Agency cost cap blocks new runs | unit (DB) | `pytest tests/test_budget.py::TestAgencyCostCap -x` | Wave 0 |
| RUNT-07 | 80% threshold alert fires | unit (DB) | `pytest tests/test_budget.py::TestAgencyCostCapAlert -x` | Wave 0 |
| ALL | Tool wiring at startup populates all 20 callables | unit | `pytest tests/test_tool_wiring.py -x` | Wave 0 |
| ALL | Every API call metered through Langfuse | unit (mocked) | `pytest tests/test_agent_runner.py::TestLangfuseMetering -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `cd hazn_platform && python -m pytest tests/test_agent_runner.py tests/test_budget.py tests/test_tool_wiring.py -x -q`
- **Per wave merge:** `cd hazn_platform && python -m pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_agent_runner.py` -- covers RUNT-02, tool_use loop, parallel dispatch, budget halt, Langfuse metering
- [ ] `tests/test_budget.py` -- covers RUNT-06, RUNT-07, cost calculation, budget enforcement, agency cost cap
- [ ] `tests/test_tool_wiring.py` -- covers tool callable wiring, AppConfig.ready(), scoped tool filtering
- [ ] `tests/test_anthropic_backend.py` -- covers RUNT-05, integration test (API key required)
- [ ] `tests/test_agent_sdk_backend.py` -- covers RUNT-04, integration test (CLI required)
- [ ] Framework install: `pip install anthropic>=0.84.0 claude-agent-sdk>=0.1.47`

## Sources

### Primary (HIGH confidence)
- [Anthropic Messages API](https://platform.claude.com/docs/en/api/messages) - Response format, content blocks, usage object, stop_reason values
- [Anthropic Tool Use Implementation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use) - Tool_use loop pattern, parallel tool calls, tool_result ordering, beta tool runner
- [Claude Agent SDK Reference](https://platform.claude.com/docs/en/agent-sdk/python) - query(), ClaudeSDKClient, ClaudeAgentOptions, create_sdk_mcp_server(), tool decorator, message types
- [Anthropic Python SDK PyPI](https://pypi.org/project/anthropic/) - v0.84.0, Python >=3.9, MIT license
- [Claude Agent SDK PyPI](https://pypi.org/project/claude-agent-sdk/) - v0.1.47, Python >=3.10, bundles CLI

### Secondary (MEDIUM confidence)
- [Anthropic Pricing](https://platform.claude.com/docs/en/about-claude/pricing) - Claude Sonnet 4.5: $3/$15 per MTok input/output, cache pricing
- Existing codebase analysis - executor.py, metering.py, tool_router.py, session.py, tracing.py, models.py, workflow_models.py (all verified by reading actual files)

### Tertiary (LOW confidence)
- Agent SDK per-turn token visibility: Unable to verify exact per-turn usage reporting format from SDK messages. Needs integration testing.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Verified versions from PyPI, official SDK docs
- Architecture: HIGH - Strategy pattern is a locked user decision, tool_use loop is well-documented Anthropic pattern
- Pitfalls: HIGH - Based on official API constraints (tool_result ordering, stop_reasons) and existing codebase patterns (sync_to_async)
- Budget enforcement: MEDIUM - Design is sound but agency cost cap rolling aggregation needs integration testing
- Agent SDK integration: MEDIUM - SDK is alpha (v0.1.47), per-turn metering granularity uncertain

**Research date:** 2026-03-06
**Valid until:** 2026-04-06 (stable for Anthropic API patterns; re-check Agent SDK version monthly)

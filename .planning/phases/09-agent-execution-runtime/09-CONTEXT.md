# Phase 9: Agent Execution Runtime - Context

**Gathered:** 2026-03-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the AgentRunner that executes real multi-turn tool_use loops against the Anthropic API (Mode 3) and Claude Agent SDK (Mode 1), with cost controls enforced from the first call. This replaces the placeholder stub in executor.py (lines 226-248) and wires ToolRouter callables to real MCP server functions.

Requirements: RUNT-02 (AgentRunner), RUNT-04 (Agent SDK), RUNT-05 (Anthropic API), RUNT-06 (per-workflow budgets), RUNT-07 (per-agency cost caps)

</domain>

<decisions>
## Implementation Decisions

### Tool_use Loop Mechanics
- Agent completion signaled by text-only response (no tool_use blocks) -- standard Anthropic pattern
- Max turns configurable per-workflow via workflow YAML `budget.max_turns` field
- Full conversation history maintained in each API call (system + all messages). 200k context window handles it
- Parallel tool execution via asyncio.gather when Claude returns multiple tool_use blocks in one response

### Budget Enforcement
- Hard halt after current turn completes when token/cost budget exceeded -- no more API calls sent
- Per-workflow token/cost budgets defined in workflow YAML: `budget: { max_tokens, max_cost, max_turns }`
- Rolling monthly cost cap per agency with 80% alert threshold and automatic block when cap reached
- Partial results preserved on budget halt -- stored as WorkflowPhaseOutput with status='partial'
- Budget check happens after each on_llm_call to MeteringCallback

### Runtime Selection
- Environment variable `HAZN_RUNTIME_MODE` (values: `agent_sdk` or `api`, default: `api`)
- Strategy pattern: one AgentRunner class with pluggable RuntimeBackend (Protocol)
- Two backend implementations: AnthropicAPIBackend and AgentSDKBackend
- Both backends built in this phase (Agent SDK is alpha but strategy interface isolates instability)
- Model: claude-sonnet-4-5 for the Anthropic API backend

### MCP Tool Wiring
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

</decisions>

<specifics>
## Specific Ideas

- ToolRouter callables are currently None in Phase 8's static registry (build_tool_registry line 319) -- this phase wires them
- executor.py _execute_phase() lines 226-248 is the placeholder that AgentRunner replaces
- MeteringCallback already has on_llm_call/on_tool_call and threshold alerts with Langfuse dual-write -- AgentRunner calls these after each turn
- WorkflowSession.record_turn() already increments turn counts and updates last_activity_at -- AgentRunner calls this
- PromptAssembler (Phase 8) produces the system prompt, ToolRouter.to_anthropic_tools() produces the tools array -- AgentRunner consumes both
- OutputCollector (Phase 8) processes the final agent text response into structured artifacts

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `PromptAssembler`: constructs system prompts from agent/skill/workflow definitions (Phase 8)
- `ToolRouter`: static registry with dispatch_anthropic() and dispatch_agent_sdk() methods (Phase 8)
- `OutputCollector`: captures structured artifacts from agent markdown output (Phase 8)
- `MeteringCallback`: per-agent token/cost/turn tracking with Langfuse alerts (existing)
- `WorkflowSession`: lifecycle management with memory, metering, checkpoint, fail methods (existing)
- `WorkflowExecutor._execute_phase()`: placeholder at lines 226-248 that AgentRunner replaces (existing)
- `build_tool_registry()`: creates ToolRouter with 20 tools, callables=None (Phase 8)
- `validate_registry()`: sanity check for static registry vs actual MCP server tools (Phase 8)

### Established Patterns
- async execution with sync_to_async wrapping for Django ORM calls
- MeteringCallback.from_agency() factory with agency-level thresholds
- ToolRouter dual-format dispatch (Anthropic API + Agent SDK)
- WorkflowPhaseOutput.objects.create() for storing phase results
- Langfuse tracing via start_workflow_trace() for observability

### Integration Points
- AgentRunner replaces placeholder in executor.py _execute_phase() (line 226-248)
- AgentRunner uses ToolRouter singleton (wired at startup) for tool dispatch
- AgentRunner calls MeteringCallback.on_llm_call() after each API response
- AgentRunner calls MeteringCallback.on_tool_call() after each tool dispatch
- AgentRunner calls WorkflowSession.record_turn() for lifecycle tracking
- AgentRunner feeds final response through OutputCollector for artifact capture
- Tool wiring happens in AppConfig.ready() importing from 4 MCP server modules

</code_context>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 09-agent-execution-runtime*
*Context gathered: 2026-03-06*

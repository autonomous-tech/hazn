---
phase: 09-agent-execution-runtime
verified: 2026-03-06T18:30:00Z
status: passed
score: 5/5 must-haves verified
must_haves:
  truths:
    - "AgentRunner executes a multi-turn tool_use conversation against the Anthropic API, calling real MCP tools and receiving real results until the agent signals completion"
    - "A workflow run that exceeds its token budget is halted mid-execution with a clear budget-exceeded status, not silently truncated"
    - "An agency that exceeds its cost cap receives an alert and further workflow runs are blocked until the cap is raised"
    - "The same workflow can execute via Claude Agent SDK (Mode 1 path) or Anthropic API (Mode 3 path) based on configuration, producing equivalent results"
    - "Every API call is metered through the existing Langfuse pipeline with token counts, cost, and duration"
  artifacts:
    - path: "hazn_platform/hazn_platform/orchestrator/budget.py"
      provides: "BudgetConfig, BudgetEnforcer, MODEL_PRICING, calculate_cost, check_agency_cost_cap, AgencyCostCapResult"
    - path: "hazn_platform/hazn_platform/orchestrator/tool_wiring.py"
      provides: "wire_callables, scope_tools_for_phase, _ROUTER_SINGLETON"
    - path: "hazn_platform/hazn_platform/orchestrator/agent_runner.py"
      provides: "AgentRunner, RuntimeBackend Protocol, RunResult, dispatch_tool_async"
    - path: "hazn_platform/hazn_platform/orchestrator/backends/__init__.py"
      provides: "Package init with lazy AnthropicAPIBackend and AgentSDKBackend re-exports"
    - path: "hazn_platform/hazn_platform/orchestrator/backends/anthropic_api.py"
      provides: "AnthropicAPIBackend implementing RuntimeBackend with multi-turn tool_use loop"
    - path: "hazn_platform/hazn_platform/orchestrator/backends/agent_sdk.py"
      provides: "AgentSDKBackend implementing RuntimeBackend via claude_code_sdk"
    - path: "hazn_platform/hazn_platform/orchestrator/executor.py"
      provides: "Updated _execute_phase() using AgentRunner with dual backend selection"
    - path: "hazn_platform/hazn_platform/orchestrator/apps.py"
      provides: "OrchestratorConfig.ready() wiring tool callables at startup"
    - path: "hazn_platform/tests/test_budget.py"
      provides: "24 tests for budget enforcement and agency cost cap"
    - path: "hazn_platform/tests/test_tool_wiring.py"
      provides: "13 tests for tool wiring, scoping, and AppConfig lifecycle"
    - path: "hazn_platform/tests/test_agent_runner.py"
      provides: "19 tests for AgentRunner, dispatch, backend loop, budget halt"
    - path: "hazn_platform/tests/test_agent_sdk_backend.py"
      provides: "7 tests for AgentSDKBackend with mocked SDK"
    - path: "hazn_platform/tests/test_executor.py"
      provides: "26 tests including 5 new AgentRunner integration tests"
  key_links:
    - from: "backends/anthropic_api.py"
      to: "budget.py"
      via: "BudgetEnforcer.is_exceeded() checked after each turn"
    - from: "backends/anthropic_api.py"
      to: "metering.py"
      via: "metering.on_llm_call() called with tokens + cost after each API call"
    - from: "backends/anthropic_api.py"
      to: "anthropic.AsyncAnthropic"
      via: "client.messages.create() for each turn"
    - from: "agent_runner.py"
      to: "tool_router.py"
      via: "dispatch_tool_async dispatches through ToolRouter entries"
    - from: "agent_runner.py"
      to: "output_collector.py"
      via: "OutputCollector.collect() processes final_text into artifacts"
    - from: "tool_wiring.py"
      to: "tool_router.py"
      via: "entry.callable = func sets callable on ToolRegistryEntry"
    - from: "apps.py"
      to: "tool_wiring.py"
      via: "AppConfig.ready() calls wire_callables()"
    - from: "executor.py"
      to: "agent_runner.py"
      via: "AgentRunner.run() called in _execute_phase()"
    - from: "executor.py"
      to: "budget.py"
      via: "check_agency_cost_cap() pre-flight check"
    - from: "executor.py"
      to: "prompt_assembler.py"
      via: "assemble_prompt() builds system prompt"
    - from: "backends/agent_sdk.py"
      to: "claude_code_sdk"
      via: "query() with ClaudeCodeOptions"
requirements:
  - id: RUNT-02
    status: satisfied
  - id: RUNT-04
    status: satisfied
  - id: RUNT-05
    status: satisfied
  - id: RUNT-06
    status: satisfied
  - id: RUNT-07
    status: satisfied
---

# Phase 9: Agent Execution Runtime Verification Report

**Phase Goal:** A real agent can execute a tool_use loop against the Anthropic API, with cost controls enforced from the first call, using either Claude Agent SDK (Mode 1) or Anthropic API (Mode 3)
**Verified:** 2026-03-06T18:30:00Z
**Status:** passed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | AgentRunner executes a multi-turn tool_use conversation against the Anthropic API, calling real MCP tools and receiving real results until the agent signals completion | VERIFIED | `AnthropicAPIBackend.execute()` implements a `while True` loop (line 101 of anthropic_api.py) that sends messages via `client.messages.create()`, checks `stop_reason`, dispatches `tool_use` blocks in parallel via `asyncio.gather`, feeds tool results back as user messages, and exits on `stop_reason == "end_turn"`. 19 tests in `test_agent_runner.py` cover single-turn, multi-turn, parallel tools, budget halt, and max_tokens scenarios. `dispatch_tool_async` in `agent_runner.py` dispatches through wired ToolRouter entries (20 MCP tools wired at startup via `apps.py`). |
| 2 | A workflow run that exceeds its token budget is halted mid-execution with a clear budget-exceeded status, not silently truncated | VERIFIED | `BudgetEnforcer.is_exceeded()` (budget.py line 142-153) checks tokens/cost/turns after each turn via `enforcer.record()` + `enforcer.is_exceeded()` in `AnthropicAPIBackend` (lines 120-141). Returns descriptive strings like `"token_budget_exceeded (100001/100000)"`. Tests verify: `test_budget_exceeded_halts_loop` confirms only 1 API call made before halt, `test_cost_budget_exceeded` confirms cost halt. `RunResult.status="budget_exceeded"` with `budget_halt_reason` set. Partial text preserved. |
| 3 | An agency that exceeds its cost cap receives an alert and further workflow runs are blocked until the cap is raised | VERIFIED | `check_agency_cost_cap()` (budget.py lines 184-228) aggregates `WorkflowRun.total_cost` for the current month via Django ORM. Returns `blocked=True` when `current_spend >= cap`, `alert_threshold_reached=True` at 80% of cap. `executor.py` (lines 239-252) calls `check_agency_cost_cap()` pre-flight; if `blocked`, raises `RuntimeError("Agency cost cap exceeded...")`. At 80%, logs warning. 8 Django DB tests cover under/at/over cap and 80% threshold. Executor test `test_agency_cost_cap_blocks_execution` confirms blocking. |
| 4 | The same workflow can execute via Claude Agent SDK (Mode 1 path) or Anthropic API (Mode 3 path) based on configuration, producing equivalent results | VERIFIED | `RuntimeBackend` Protocol (agent_runner.py lines 82-123) defines the pluggable interface. `AnthropicAPIBackend` (backends/anthropic_api.py) and `AgentSDKBackend` (backends/agent_sdk.py) both implement it. `executor.py` (lines 280-303) selects based on `HAZN_RUNTIME_MODE` env var: `"api"` (default) -> `AnthropicAPIBackend`, `"agent_sdk"` -> `AgentSDKBackend`. Both return `RunResult` with same schema. `AgentSDKBackend` uses lazy import for optional SDK. Test `test_runtime_mode_sdk_selects_agent_sdk_backend` confirms env var selection. `test_implements_runtime_backend` confirms protocol compliance. |
| 5 | Every API call is metered through the existing Langfuse pipeline with token counts, cost, and duration | VERIFIED | `AnthropicAPIBackend.execute()` calls `metering.on_llm_call(agent_id, tokens=total_tokens, cost=cost)` after every API call (line 119). `MeteringCallback.on_llm_call()` in `metering.py` records tokens, cost, and calls `_annotate_langfuse_event()` for threshold alerts (dual-write to callback + Langfuse). `dispatch_tool_async` calls `metering.on_tool_call()` with latency_ms in the `finally` block (line 205). Tests `test_single_turn_metering` and `test_dispatch_records_metering` verify recording. |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `hazn_platform/hazn_platform/orchestrator/budget.py` | BudgetConfig, BudgetEnforcer, cost calculation, agency cost cap check | VERIFIED | 229 lines. Exports BudgetConfig (Pydantic), BudgetEnforcer, MODEL_PRICING (claude-sonnet-4-5), calculate_cost (duck-typed for Anthropic response), check_agency_cost_cap (Django ORM rolling monthly), AgencyCostCapResult (NamedTuple). All substantive with real logic. |
| `hazn_platform/hazn_platform/orchestrator/tool_wiring.py` | Tool callable wiring and per-phase tool scoping | VERIFIED | 155 lines. wire_callables imports all 20 functions from 4 MCP server modules and sets entry.callable. scope_tools_for_phase filters Anthropic tools array. _ROUTER_SINGLETON module-level variable. |
| `hazn_platform/hazn_platform/orchestrator/agent_runner.py` | AgentRunner class, RuntimeBackend Protocol, RunResult model, dispatch_tool_async | VERIFIED | 309 lines. RunResult (Pydantic BaseModel with 7 fields), RuntimeBackend (Protocol, runtime_checkable), dispatch_tool_async (handles dict/Pydantic input, sync/async callables, metering), AgentRunner (delegates to backend, scopes tools, feeds OutputCollector). |
| `hazn_platform/hazn_platform/orchestrator/backends/__init__.py` | Package init re-exporting backends | VERIFIED | 31 lines. Lazy `__getattr__` for both AnthropicAPIBackend and AgentSDKBackend. |
| `hazn_platform/hazn_platform/orchestrator/backends/anthropic_api.py` | AnthropicAPIBackend implementing RuntimeBackend | VERIFIED | 239 lines. Full multi-turn tool_use loop: messages.create(), calculate_cost, metering, BudgetEnforcer, parallel asyncio.gather for tool_use blocks, stop_reason handling (end_turn/tool_use/max_tokens), text extraction. |
| `hazn_platform/hazn_platform/orchestrator/backends/agent_sdk.py` | AgentSDKBackend implementing RuntimeBackend | VERIFIED | 198 lines. Late SDK import inside execute(), ClaudeCodeOptions with max_turns, mcp__hazn__ tool prefix, async generator iteration over query(), token usage extraction, graceful exception handling. |
| `hazn_platform/hazn_platform/orchestrator/executor.py` | Updated _execute_phase() using AgentRunner | VERIFIED | 473 lines. _execute_phase() replaced placeholder: pre-flight cost cap check, assemble_prompt, BudgetConfig (defaults 500k/2.0/30), backend selection via HAZN_RUNTIME_MODE, AgentRunner.run(), RunResult handling (completed/budget_exceeded/error), WorkflowPhaseOutput DB write, QA injection preserved. |
| `hazn_platform/hazn_platform/orchestrator/apps.py` | AppConfig.ready() that wires tool callables at startup | VERIFIED | 71 lines. OrchestratorConfig.ready() with build_tool_registry, wire_callables, validate_registry, _ROUTER_SINGLETON assignment, double-ready guard, try/except for graceful failure. |
| `hazn_platform/tests/test_budget.py` | Tests for budget enforcement and agency cost cap | VERIFIED | 330 lines. 24 tests across 4 classes: TestBudgetConfig (3), TestBudgetEnforcement (8), TestCostCalculation (5), TestAgencyCostCap (8 @django_db). |
| `hazn_platform/tests/test_tool_wiring.py` | Tests for tool wiring and scoped filtering | VERIFIED | 321 lines. 13 tests across 3 classes: TestWireCallables (5), TestScopeToolsForPhase (5), TestAppConfigReady (3). |
| `hazn_platform/tests/test_agent_runner.py` | Tests for AgentRunner loop, parallel dispatch, budget halt, metering | VERIFIED | 728 lines. 19 tests across 8 classes covering dispatch (7), single-turn (2), multi-turn (2), parallel tools (1), budget halt (2), max_tokens (1), on_turn (1), AgentRunner wiring (3). |
| `hazn_platform/tests/test_agent_sdk_backend.py` | Tests for AgentSDKBackend with mocked SDK | VERIFIED | 316 lines. 7 tests across 5 classes: successful execution (2), error handling (2), budget config (1), allowed tools (1), protocol compliance (1). |
| `hazn_platform/tests/test_executor.py` | Updated executor tests with AgentRunner integration | VERIFIED | 1484 lines. 26 tests including 5 new AgentRunner integration tests: assemble_prompt args, cost cap blocking, SDK backend selection, budget exceeded partial results, error status raises. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| backends/anthropic_api.py | budget.py | BudgetEnforcer.is_exceeded() after each turn | WIRED | `enforcer.is_exceeded()` at line 127 |
| backends/anthropic_api.py | metering.py | metering.on_llm_call() with tokens + cost | WIRED | `metering.on_llm_call(agent_id, tokens=total_tokens, cost=cost)` at line 119 |
| backends/anthropic_api.py | anthropic.AsyncAnthropic | client.messages.create() | WIRED | `self._client.messages.create(**create_kwargs)` at line 113 |
| agent_runner.py | tool_router.py | dispatch_tool_async through ToolRouter | WIRED | `dispatch_tool_async(self._router, block, metering)` at line 287 |
| agent_runner.py | output_collector.py | OutputCollector.collect() on final_text | WIRED | `self._output_collector.collect(result.final_text)` at line 306 |
| tool_wiring.py | tool_router.py | entry.callable = func | WIRED | `entry.callable = func` at line 112 |
| apps.py | tool_wiring.py | wire_callables() in ready() | WIRED | `count = wire_callables(router)` at line 51 |
| executor.py | agent_runner.py | AgentRunner.run() in _execute_phase() | WIRED | `result = await agent_runner.run(...)` at line 328 |
| executor.py | budget.py | check_agency_cost_cap() pre-flight | WIRED | `cap_result = await sync_to_async(check_agency_cost_cap)(workflow_run.agency)` at line 240 |
| executor.py | prompt_assembler.py | assemble_prompt() for system prompt | WIRED | `system_prompt = assemble_prompt(...)` at line 255 |
| backends/agent_sdk.py | claude_code_sdk | query() with ClaudeCodeOptions | WIRED | `claude_code_sdk.query(prompt=prompt, options=options)` at line 138, `ClaudeCodeOptions(...)` at line 123 |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| RUNT-02 | 09-02, 09-03 | AgentRunner executes tool_use loop with turn counting and conversation management | SATISFIED | AgentRunner delegates to RuntimeBackend.execute() which runs multi-turn loop. Turn counting via BudgetEnforcer. Conversation history accumulated in messages list. 19 tests verify. |
| RUNT-04 | 09-03 | Claude Agent SDK integration for Mode 1 execution (Max subscription) | SATISFIED | AgentSDKBackend (backends/agent_sdk.py) implements RuntimeBackend via claude_code_sdk.query(). Late import for optional SDK. mcp__hazn__ tool prefix. 7 tests verify. |
| RUNT-05 | 09-02 | Anthropic API integration for Mode 3 execution (metered per-token) | SATISFIED | AnthropicAPIBackend (backends/anthropic_api.py) uses anthropic.AsyncAnthropic with full tool_use loop. calculate_cost with MODEL_PRICING for claude-sonnet-4-5. 12 tests verify. |
| RUNT-06 | 09-01 | Per-workflow token budgets with enforcement and runaway detection | SATISFIED | BudgetConfig (max_tokens/max_cost/max_turns), BudgetEnforcer with record()+is_exceeded(), checked after every API call. Descriptive reason strings. 8 enforcer + 5 cost tests. |
| RUNT-07 | 09-01 | Per-agency cost caps with alerts and automatic halt | SATISFIED | check_agency_cost_cap() with rolling monthly window, 80% alert threshold, automatic block at 100%. Pre-flight check in executor.py. 8 Django DB tests + 1 executor integration test. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | - | - | - | No TODO, FIXME, placeholder, or stub patterns found in any Phase 9 artifacts |

### Human Verification Required

### 1. Multi-turn Tool_use Loop with Real Anthropic API

**Test:** Set ANTHROPIC_API_KEY, trigger a workflow phase that uses tool_use (e.g., search_memory) against the real API
**Expected:** Agent completes multi-turn conversation, calling tools and receiving results, producing meaningful final text
**Why human:** Tests use mocked Anthropic client; real API behavior (latency, response format variations, edge cases) can only be verified with a live call

### 2. Claude Agent SDK Backend with Real Claude CLI

**Test:** Set HAZN_RUNTIME_MODE=agent_sdk, ensure Claude CLI is installed, trigger a workflow
**Expected:** SDK backend executes via query(), produces RunResult with status=completed and meaningful output
**Why human:** All SDK tests use mocked SDK; real SDK execution requires Claude CLI installed and authenticated

### 3. Budget Enforcement Under Real Load

**Test:** Set a very low token budget (e.g., 1000) and trigger a real workflow
**Expected:** Agent halts after first API response with budget_exceeded status, partial results preserved in WorkflowPhaseOutput
**Why human:** Verifying partial result quality and budget halt timing under real API latency

### 4. Agency Cost Cap with Real Monthly Spend

**Test:** Create a test agency with monthly_cost_cap=0.01, run a workflow that costs more than $0.01
**Expected:** Pre-flight check blocks the second workflow run with "Agency cost cap exceeded" error
**Why human:** Requires real DB state with actual WorkflowRun.total_cost values from prior runs

---

_Verified: 2026-03-06T18:30:00Z_
_Verifier: Claude (gsd-verifier)_

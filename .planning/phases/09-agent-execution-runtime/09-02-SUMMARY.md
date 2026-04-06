---
phase: 09-agent-execution-runtime
plan: 02
subsystem: orchestrator
tags: [agent-runner, anthropic-api, tool-use-loop, runtime-backend, asyncio, pydantic, budget-enforcement]

# Dependency graph
requires:
  - phase: 09-agent-execution-runtime-01
    provides: BudgetConfig, BudgetEnforcer, calculate_cost, scope_tools_for_phase, wire_callables
  - phase: 08-foundation-components
    provides: ToolRouter, OutputCollector, MeteringCallback, PromptAssembler
provides:
  - AgentRunner class orchestrating backend execution with tool dispatch and output collection
  - RuntimeBackend Protocol for pluggable execution backends (strategy pattern)
  - RunResult Pydantic model capturing status, text, artifacts, usage, and conversation history
  - dispatch_tool_async helper for async/sync tool dispatch with metering through ToolRouter
  - AnthropicAPIBackend implementing multi-turn tool_use loop via anthropic.AsyncAnthropic
affects: [09-03-agent-sdk-backend, 10-e2e-workflows, executor-integration]

# Tech tracking
tech-stack:
  added: [anthropic-sdk-0.84.0]
  patterns: [runtime-backend-protocol, parallel-tool-dispatch-asyncio-gather, budget-enforcer-per-turn-check, conversation-history-accumulation]

key-files:
  created:
    - hazn_platform/hazn_platform/orchestrator/agent_runner.py
    - hazn_platform/hazn_platform/orchestrator/backends/__init__.py
    - hazn_platform/hazn_platform/orchestrator/backends/anthropic_api.py
    - hazn_platform/tests/test_agent_runner.py
  modified: []

key-decisions:
  - "RuntimeBackend Protocol includes messages list and agent_id as execute() parameters for flexibility"
  - "AnthropicAPIBackend creates BudgetEnforcer internally from BudgetConfig, keeping the Protocol clean"
  - "dispatch_tool_async handles both dict and Pydantic object inputs (duck-typing for Anthropic SDK compatibility)"
  - "backends/__init__.py uses lazy __getattr__ import to avoid pulling anthropic SDK at module-import time"
  - "RunResult uses Pydantic BaseModel for validation and serialization readiness"

patterns-established:
  - "RuntimeBackend Protocol: async execute() with system_prompt, messages, tools, tool_dispatch, budget, metering, agent_id, on_turn"
  - "Parallel tool dispatch: asyncio.gather for multiple tool_use blocks in single response"
  - "Budget check after metering: calculate_cost -> metering.on_llm_call -> enforcer.record -> enforcer.is_exceeded before next API call"
  - "Tool result ordering: tool_results as user message content array (Anthropic API requirement)"
  - "Conversation history accumulation: full messages list passed in each API call for 200k context window"

requirements-completed: [RUNT-02, RUNT-05]

# Metrics
duration: 6min
completed: 2026-03-06
---

# Phase 9 Plan 02: AgentRunner and AnthropicAPIBackend Summary

**Multi-turn tool_use agent loop with RuntimeBackend Protocol, parallel tool dispatch via asyncio.gather, budget enforcement, and metering through Anthropic API SDK**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-06T14:56:06Z
- **Completed:** 2026-03-06T15:02:58Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- AgentRunner class delegates to pluggable RuntimeBackend, scopes tools per-phase, and feeds output through OutputCollector for artifact extraction
- AnthropicAPIBackend executes complete multi-turn tool_use loop: send messages -> check stop_reason -> dispatch tools in parallel -> feed results back -> repeat
- RuntimeBackend Protocol enables strategy pattern for future AgentSDKBackend (Plan 03) without touching AgentRunner
- dispatch_tool_async handles both sync and async callables with automatic metering (latency + success flag) via ToolRouter
- 19 comprehensive tests covering single-turn, multi-turn, parallel tools, budget halt, cost budget, max_tokens error, on_turn callback, conversation history, scoped tools, and artifact extraction -- all using mocked Anthropic API (no real API key required)

## Task Commits

Each task was committed atomically:

1. **Task 1: RuntimeBackend Protocol, RunResult, dispatch_tool_async, AgentRunner** - `5cfa66d` (feat) -- core abstractions and orchestrator class
2. **Task 2: AnthropicAPIBackend with tool_use loop and tests (TDD)** - `5891b27` (feat) -- backend implementation + 19 tests

**Plan metadata:** (pending final commit)

_Note: Task 2 was TDD -- tests written first (RED), then implementation (GREEN), committed together after GREEN phase._

## Files Created/Modified
- `hazn_platform/hazn_platform/orchestrator/agent_runner.py` - AgentRunner class, RuntimeBackend Protocol, RunResult model, dispatch_tool_async helper
- `hazn_platform/hazn_platform/orchestrator/backends/__init__.py` - Package init with lazy AnthropicAPIBackend re-export
- `hazn_platform/hazn_platform/orchestrator/backends/anthropic_api.py` - AnthropicAPIBackend implementing multi-turn tool_use loop via anthropic.AsyncAnthropic
- `hazn_platform/tests/test_agent_runner.py` - 19 tests for dispatch, backend, AgentRunner wiring

## Decisions Made
- RuntimeBackend Protocol includes `messages: list[dict]` and `agent_id: str` as execute() parameters (plan initially had messages constructed inside backend, but passing from AgentRunner gives more flexibility for conversation continuity)
- AnthropicAPIBackend creates BudgetEnforcer internally from BudgetConfig rather than receiving it as a parameter -- keeps the Protocol interface cleaner and ensures fresh enforcer per execution
- dispatch_tool_async duck-types both dict and Pydantic object inputs (block.name vs block["name"]) for Anthropic SDK compatibility without explicit type conversions
- backends/__init__.py uses lazy `__getattr__` import to avoid pulling in the anthropic SDK at module-import time, keeping import chains lightweight
- Tool dispatch only passes tools kwarg to API when tools list is non-empty (avoids potential API errors with empty tools array)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required. Anthropic API key is only needed at runtime (real execution), not for tests.

## Next Phase Readiness
- AgentRunner + AnthropicAPIBackend fully operational for Mode 3 execution
- RuntimeBackend Protocol ready for AgentSDKBackend (Plan 03) to implement
- dispatch_tool_async ready for both backends to use
- All 19 tests pass, 110 total tests pass with zero Phase 8 regressions
- No blockers for Plan 03 (Agent SDK Backend)

## Self-Check: PASSED

All files verified present, all commit hashes verified in git log.

---
*Phase: 09-agent-execution-runtime*
*Completed: 2026-03-06*

---
phase: 08-foundation-components
plan: 02
subsystem: orchestrator
tags: [tool-routing, mcp, anthropic-api, agent-sdk, dual-format-dispatch, static-registry]

# Dependency graph
requires:
  - phase: 08-01
    provides: "Testing infrastructure (MockLLMResponse, MockToolDispatcher, fixture loaders)"
provides:
  - "ToolRouter with static registry and dual-format dispatch (Anthropic API + Agent SDK)"
  - "build_tool_registry() factory creating 20-tool registry across 4 MCP servers"
  - "validate_registry() startup sanity check for Phase 9"
affects: [08-03, 09-agent-runner]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Hardcoded static tool map: _STATIC_TOOL_MAP avoids importing Django-dependent MCP server modules"
    - "Dual-format dispatch: same registry serves Anthropic API tool_use and Agent SDK MCP protocol"
    - "Error wrapping: all tool exceptions/unknown tools wrapped as is_error/isError (agent crash prevention)"
    - "No is_error key on success: Anthropic API spec compliance (omit rather than set False)"

key-files:
  created:
    - "hazn_platform/hazn_platform/orchestrator/tool_router.py"
    - "hazn_platform/tests/test_tool_router.py"
  modified: []

key-decisions:
  - "Hardcoded static registry (_STATIC_TOOL_MAP) instead of FastMCP introspection: more maintainable, avoids Django imports, 20 tools across 4 servers change infrequently"
  - "Callables set to None in build_tool_registry: wired at runtime by Phase 9 when MCP servers are actually running"
  - "validate_registry() deferred to Phase 9 startup: requires Django setup to import MCP server modules"

patterns-established:
  - "Static tool map pattern: hardcoded dict[str, tuple[str, str]] mapping tool_name to (server_name, description)"
  - "Dual-format dispatch: same ToolRouter instance serves both Anthropic API and Agent SDK formats"
  - "Error wrapping: tool exceptions never propagate, always returned as structured error responses"

requirements-completed: [RUNT-03]

# Metrics
duration: 2min
completed: 2026-03-06
---

# Phase 8 Plan 02: ToolRouter Summary

**Static MCP tool registry with dual-format dispatch mapping 20 tools across 4 servers to both Anthropic API tool_result and Agent SDK content block formats**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-06T12:50:32Z
- **Completed:** 2026-03-06T12:52:56Z
- **Tasks:** 2
- **Files created:** 2

## Accomplishments
- ToolRouter class with register, get_tool, list_tools, get_tools_for_server, to_anthropic_tools
- Dual-format dispatch: dispatch_anthropic (tool_use -> tool_result) and dispatch_agent_sdk (name+input -> MCP content blocks)
- Static registry of 20 tools across 4 MCP servers (hazn-memory, hazn-analytics, hazn-github, hazn-vercel)
- Error wrapping: unknown tools and tool exceptions wrapped as is_error/isError (agent never crashes)
- 21 tests covering registry operations, both dispatch formats, error handling, and static registry construction

## Task Commits

Each task was committed atomically:

1. **Task 1: Write ToolRouter tests (RED)** - `1bcbc49` (test)
2. **Task 2: Implement ToolRouter (GREEN)** - `c844e6c` (feat)

_TDD tasks: failing tests committed first, then passing implementation._

## Files Created/Modified
- `hazn_platform/hazn_platform/orchestrator/tool_router.py` - ToolRouter class with static registry, dual-format dispatch, build_tool_registry factory, validate_registry sanity check
- `hazn_platform/tests/test_tool_router.py` - 21 tests: registry ops, Anthropic dispatch, Agent SDK dispatch, error handling, static registry construction

## Decisions Made
- **Hardcoded static registry:** Used _STATIC_TOOL_MAP (dict of tool_name -> (server_name, description)) instead of FastMCP _tool_manager introspection. More maintainable, avoids importing Django-dependent MCP server modules, and the 4 servers / 20 tools change infrequently.
- **Callables set to None:** build_tool_registry() creates entries with callable=None. Phase 9's AgentRunner will wire actual callables when MCP servers are running.
- **validate_registry() for Phase 9:** The startup validation function that checks the static map against actual MCP server registrations requires Django setup. Deferred to Phase 9 integration.
- **No is_error key on success:** Per Anthropic API spec, the is_error key is omitted entirely on successful dispatch (not set to False).

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- ToolRouter ready for Phase 9 AgentRunner integration
- to_anthropic_tools() exports registry as tools array for LLM requests
- dispatch_anthropic and dispatch_agent_sdk support both execution modes
- Plan 03 (OutputCollector) can proceed independently
- Key integration: executor.py placeholder for tool dispatch

## Self-Check: PASSED

- `hazn_platform/hazn_platform/orchestrator/tool_router.py` - VERIFIED present
- `hazn_platform/tests/test_tool_router.py` - VERIFIED present
- Commit `1bcbc49` - VERIFIED in git log
- Commit `c844e6c` - VERIFIED in git log
- 21/21 tests pass

---
*Phase: 08-foundation-components*
*Completed: 2026-03-06*

---
phase: 03-tool-migration
plan: 05
subsystem: tools
tags: [claude-agent-sdk, mcp-tools, sdk-wiring, analytics, registry]

# Dependency graph
requires:
  - phase: 03-tool-migration (plan 04)
    provides: "ToolRegistry, build_registry, 24 tools registered, AgentSDKBackend skeleton"
provides:
  - "AgentSDKBackend wired to real Claude Agent SDK with mcp_servers"
  - "analytics.py importable without Django configured"
  - "get_tool_callable() returns .handler for real SdkMcpTool"
  - "All 78 tool/registry/backend tests green with real SDK"
affects: [04-executor-rewrite, runtime-integration]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "try claude_agent_sdk / except fallback to claude_code_sdk in agent_sdk.py"
    - "SdkMcpTool.handler() invocation pattern (not direct call)"
    - "try/except guard for module-level Django ORM imports"

key-files:
  created: []
  modified:
    - "hazn_platform/hazn_platform/orchestrator/backends/agent_sdk.py"
    - "hazn_platform/hazn_platform/orchestrator/tools/analytics.py"
    - "hazn_platform/hazn_platform/orchestrator/tools/registry.py"
    - "hazn_platform/tests/test_tools_filesystem.py"
    - "hazn_platform/tests/test_tools_web.py"
    - "hazn_platform/tests/test_tools_memory.py"
    - "hazn_platform/tests/test_tools_github.py"
    - "hazn_platform/tests/test_tools_vercel.py"
    - "hazn_platform/tests/test_tools_analytics.py"
    - "hazn_platform/tests/test_agent_sdk_backend.py"

key-decisions:
  - "try/except import chain for SDK: claude_agent_sdk first, claude_code_sdk fallback"
  - "Broad except (ImportError, Exception) for analytics module-level imports to catch Django ImproperlyConfigured"
  - "getattr(t, 'handler', t) pattern in get_tool_callable for stub/real SDK compatibility"

patterns-established:
  - "SdkMcpTool.handler(args): all tool invocations use .handler attribute, not direct call"
  - "Module-level try/except guard: Django ORM imports guarded so module is importable outside Django context"

requirements-completed: [STRP-01, TOOL-01, TOOL-02, TOOL-03, TOOL-04, TOOL-05, TOOL-06, TOOL-07, TOOL-08]

# Metrics
duration: 6min
completed: 2026-03-12
---

# Phase 3 Plan 5: Gap Closure Summary

**Real Claude Agent SDK wired into AgentSDKBackend with mcp_servers, guarded analytics imports, and all 78 tool tests passing via .handler() invocation**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-12T19:01:42Z
- **Completed:** 2026-03-12T19:08:20Z
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments
- agent_sdk.py imports claude_agent_sdk (with claude_code_sdk fallback), uses ClaudeAgentOptions, and passes mcp_servers={"hazn": registry.get_server()} to SDK
- analytics.py module-level Django/Google imports guarded with try/except -- module importable without Django configured
- registry.py get_tool_callable() returns .handler for real SdkMcpTool instances (getattr fallback for stubs)
- All 7 test files updated to use tool.handler(args) instead of tool(args) -- 78 tests green
- test_agent_sdk_backend.py mocks claude_agent_sdk with ClaudeAgentOptions (not old claude_code_sdk/ClaudeCodeOptions)

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix agent_sdk.py SDK wiring and analytics.py deferred imports** - `40eb9e4` (fix)
2. **Task 2: Update all tool tests for real SdkMcpTool .handler invocation** - `3a1eb1b` (test)

## Files Created/Modified
- `hazn_platform/hazn_platform/orchestrator/backends/agent_sdk.py` - Claude Agent SDK import chain, ClaudeAgentOptions, mcp_servers wiring
- `hazn_platform/hazn_platform/orchestrator/tools/analytics.py` - Module-level Django/Google imports guarded with try/except
- `hazn_platform/hazn_platform/orchestrator/tools/registry.py` - get_tool_callable returns .handler for SdkMcpTool
- `hazn_platform/tests/test_tools_filesystem.py` - 9 .handler() call updates
- `hazn_platform/tests/test_tools_web.py` - 3 .handler() call updates
- `hazn_platform/tests/test_tools_memory.py` - 11 .handler() call updates
- `hazn_platform/tests/test_tools_github.py` - 9 .handler() call updates
- `hazn_platform/tests/test_tools_vercel.py` - 8 .handler() call updates
- `hazn_platform/tests/test_tools_analytics.py` - 16 .handler() call updates
- `hazn_platform/tests/test_agent_sdk_backend.py` - claude_agent_sdk mock patches, ClaudeAgentOptions

## Decisions Made
- Used try/except import chain (claude_agent_sdk -> claude_code_sdk) rather than hard switch, for backward compatibility during transition
- Broad except (ImportError, Exception) for analytics module-level imports to also catch Django's ImproperlyConfigured
- getattr(t, "handler", t) in get_tool_callable provides graceful fallback for stub tools in testing

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All 3 verification gaps from Phase 3 are closed
- 24 real SdkMcpTool instances registered, all tests green
- AgentSDKBackend fully wired to Claude Agent SDK with MCP server config
- Ready for Phase 4 (Executor Rewrite) which will use this backend in production

## Self-Check: PASSED

All files verified present. All commits (40eb9e4, 3a1eb1b) verified in git log.

---
*Phase: 03-tool-migration*
*Completed: 2026-03-12*

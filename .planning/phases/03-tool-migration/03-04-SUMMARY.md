---
phase: 03-tool-migration
plan: 04
subsystem: orchestrator
tags: [tool-registry, mcp-removal, fastmcp, agent-sdk, dependency-cleanup]

# Dependency graph
requires:
  - phase: 03-tool-migration (plans 01-03)
    provides: ToolRegistry, build_registry(), tool modules (filesystem, web, memory, github, vercel, analytics)
provides:
  - ToolRegistry wired into executor chain (apps.py, agent_sdk.py, agent_runner.py, executor.py)
  - MCP servers and old routing infrastructure completely removed
  - Clean dependency set (fastmcp removed, claude-agent-sdk/beautifulsoup4/aiofiles added)
affects: [04-executor-rewrite, 05-chat-view]

# Tech tracking
tech-stack:
  added: [claude-agent-sdk, beautifulsoup4, aiofiles]
  removed: [fastmcp]
  patterns: [_REGISTRY_SINGLETON in apps.py, get_tool_callable() for dispatch compat]

key-files:
  modified:
    - hazn_platform/hazn_platform/orchestrator/apps.py
    - hazn_platform/hazn_platform/orchestrator/backends/agent_sdk.py
    - hazn_platform/hazn_platform/orchestrator/agent_runner.py
    - hazn_platform/hazn_platform/orchestrator/executor.py
    - hazn_platform/hazn_platform/orchestrator/tools/registry.py
    - hazn_platform/pyproject.toml
    - hazn_platform/tests/test_agent_sdk_backend.py
    - hazn_platform/tests/test_agent_runner.py
    - hazn_platform/tests/test_output_collector.py
  deleted:
    - hazn_platform/hazn_platform/mcp_servers/ (5 files)
    - hazn_platform/hazn_platform/orchestrator/tool_router.py
    - hazn_platform/hazn_platform/orchestrator/tool_wiring.py
    - hazn_platform/hazn_platform/orchestrator/data_tools.py
    - hazn_platform/tests/test_tool_router.py
    - hazn_platform/tests/test_tool_wiring.py
    - hazn_platform/tests/test_data_tools.py
    - hazn_platform/tests/test_mcp_analytics_server.py
    - hazn_platform/tests/test_mcp_github_server.py
    - hazn_platform/tests/test_mcp_memory_server.py
    - hazn_platform/tests/test_mcp_vercel_server.py

key-decisions:
  - "_REGISTRY_SINGLETON in apps.py replaces tool_wiring._ROUTER_SINGLETON pattern"
  - "get_tool_callable() added to ToolRegistry for backward-compat dispatch in agent_runner"
  - "AgentSDKBackend delegates allowed-tool prefixing to ToolRegistry.get_allowed_tools()"

patterns-established:
  - "apps._REGISTRY_SINGLETON: module-level singleton for ToolRegistry, set by OrchestratorConfig.ready()"
  - "executor.py imports from apps module for singleton, falls back to build_registry()"

requirements-completed: [STRP-01, TOOL-08]

# Metrics
duration: 10min
completed: 2026-03-12
---

# Phase 3 Plan 4: Executor Wiring & MCP Cleanup Summary

**ToolRegistry wired into executor chain, 4 MCP servers + 3 old routing files + 7 old tests deleted, fastmcp removed from dependencies**

## Performance

- **Duration:** 10 min
- **Started:** 2026-03-12T18:22:05Z
- **Completed:** 2026-03-12T18:32:38Z
- **Tasks:** 2
- **Files deleted:** 18
- **Files modified:** 9

## Accomplishments
- Wired ToolRegistry as sole tool system into apps.py, agent_sdk.py, agent_runner.py, executor.py
- Deleted all 5 MCP server files and mcp_servers/ directory entirely
- Deleted tool_router.py, tool_wiring.py, data_tools.py (old routing infrastructure)
- Deleted 7 old test files for deleted modules
- Removed fastmcp from dependencies, added claude-agent-sdk, beautifulsoup4, aiofiles
- Updated 3 test files to use ToolRegistry instead of ToolRouter
- Django starts cleanly with 24 tools registered via new ToolRegistry

## Task Commits

Each task was committed atomically:

1. **Task 1: Wire ToolRegistry into apps.py, agent_sdk.py, agent_runner.py, executor.py** - `2dc98ba` (feat)
2. **Task 2: Delete MCP servers, old routing, old tests, remove fastmcp** - `336b198` (chore)

## Files Created/Modified
- `hazn_platform/orchestrator/apps.py` - Uses build_registry() + _REGISTRY_SINGLETON
- `hazn_platform/orchestrator/backends/agent_sdk.py` - Uses ToolRegistry instead of ToolRouter
- `hazn_platform/orchestrator/agent_runner.py` - Uses ToolRegistry for dispatch and allowed-tools
- `hazn_platform/orchestrator/executor.py` - Uses apps._REGISTRY_SINGLETON
- `hazn_platform/orchestrator/tools/registry.py` - Added get_tool_callable() method
- `hazn_platform/pyproject.toml` - Removed fastmcp, added claude-agent-sdk/beautifulsoup4/aiofiles
- `hazn_platform/tests/test_agent_sdk_backend.py` - Updated to use ToolRegistry
- `hazn_platform/tests/test_agent_runner.py` - Updated to use ToolRegistry
- `hazn_platform/tests/test_output_collector.py` - Updated integration test to use ToolRegistry

## Decisions Made
- **_REGISTRY_SINGLETON pattern:** Replaced tool_wiring._ROUTER_SINGLETON with apps._REGISTRY_SINGLETON for the module-level ToolRegistry singleton
- **get_tool_callable() method:** Added to ToolRegistry for backward-compatible dispatch in agent_runner.py (dispatch_tool_async still used by Anthropic API compat path, removed in Phase 4)
- **Direct function-as-tool pattern in tests:** Test mocks set .name on function objects directly rather than using wrapper classes, keeping inspect.iscoroutinefunction working correctly

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added get_tool_callable() to ToolRegistry**
- **Found during:** Task 1 (updating agent_runner.py)
- **Issue:** dispatch_tool_async needed to look up tool callables by name, but ToolRegistry had no equivalent of ToolRouter.get_tool()
- **Fix:** Added get_tool_callable(name) method that iterates _tools list to find by .name
- **Files modified:** hazn_platform/orchestrator/tools/registry.py
- **Verification:** All dispatch_tool_async tests pass (10 tests)
- **Committed in:** 2dc98ba (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 2 -- missing critical functionality)
**Impact on plan:** Minimal -- single method added to complete the ToolRegistry API for dispatch compatibility.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 3 (Tool Migration) is now complete
- ToolRegistry is the sole tool system, 24 tools registered at startup
- No MCP protocol code remains in the codebase
- Phase 4 (Executor Rewrite) can proceed with clean ToolRegistry foundation
- Pre-existing test failures in test_executor.py, test_metering.py remain deferred to Phase 4

---
*Phase: 03-tool-migration*
*Completed: 2026-03-12*

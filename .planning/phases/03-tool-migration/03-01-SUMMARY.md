---
phase: 03-tool-migration
plan: 01
subsystem: tools
tags: [claude-agent-sdk, tool-registry, filesystem, web-fetch, httpx, async, mcp]

# Dependency graph
requires:
  - phase: 02-model-simplification
    provides: Simplified model layer with Agency singleton, cleaned API
provides:
  - ToolRegistry class with register(), get_server(), get_allowed_tools(), list_tools()
  - build_registry() factory function
  - File I/O tools (read_file, write_file, mkdir) as async Python functions
  - Web fetch tool (fetch_page) with HTML text extraction
  - Stub @tool decorator for SDK-absent environments
affects: [03-02-PLAN, 03-03-PLAN, 03-04-PLAN, 04-executor-rewrite]

# Tech tracking
tech-stack:
  added: [beautifulsoup4 (optional), httpx (existing)]
  patterns: [stub-tool-decorator, asyncio-to-thread-for-sync-io, mcp-hazn-prefix-convention]

key-files:
  created:
    - hazn_platform/hazn_platform/orchestrator/tools/__init__.py
    - hazn_platform/hazn_platform/orchestrator/tools/registry.py
    - hazn_platform/hazn_platform/orchestrator/tools/filesystem.py
    - hazn_platform/hazn_platform/orchestrator/tools/web.py
    - hazn_platform/tests/test_tool_registry.py
    - hazn_platform/tests/test_tools_filesystem.py
    - hazn_platform/tests/test_tools_web.py
  modified: []

key-decisions:
  - "Stub @tool decorator pattern: when SDK not installed, tools still register with .name attribute for testing"
  - "asyncio.to_thread() for file I/O instead of aiofiles dependency -- fewer deps, stdlib-only"
  - "Regex fallback for HTML text extraction when beautifulsoup4 not installed"
  - "Dict stub for get_server() when SDK not available -- preserves interface contract"

patterns-established:
  - "Tool module pattern: each module defines TOOLS list for build_registry() to collect"
  - "Error return pattern: {'content': [{'type': 'text', 'text': msg}], 'isError': True}"
  - "SDK import fallback chain: claude_agent_sdk -> claude_code_sdk -> stub"

requirements-completed: [TOOL-01, TOOL-02, TOOL-08]

# Metrics
duration: 6min
completed: 2026-03-12
---

# Phase 3 Plan 1: Tool Registry + File I/O + Web Fetch Summary

**ToolRegistry with SDK-agnostic registration, 3 filesystem tools, and web fetch with HTML extraction**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-12T17:55:13Z
- **Completed:** 2026-03-12T18:01:24Z
- **Tasks:** 2
- **Files created:** 7

## Accomplishments
- ToolRegistry class replaces ToolRouter as the central tool access point, producing mcp__hazn__ prefixed names and McpSdkServerConfig
- File I/O tools (read_file, write_file, mkdir) work as standalone async Python functions with error handling
- Web fetch tool extracts text from HTML pages using beautifulsoup4 with regex fallback, respecting max_length truncation
- Full TDD with 24 tests passing (12 registry + 9 filesystem + 3 web)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create ToolRegistry and tools package scaffold** - `2e64d01` (feat)
2. **Task 2: Create File I/O and Web fetch tools** - `e0824ea` (feat)

## Files Created/Modified
- `hazn_platform/orchestrator/tools/__init__.py` - Package init, re-exports ToolRegistry and build_registry()
- `hazn_platform/orchestrator/tools/registry.py` - ToolRegistry class with register, get_server, get_allowed_tools, list_tools
- `hazn_platform/orchestrator/tools/filesystem.py` - read_file, write_file, mkdir async tool functions
- `hazn_platform/orchestrator/tools/web.py` - fetch_page async tool function with HTML text extraction
- `tests/test_tool_registry.py` - 12 tests for ToolRegistry and build_registry
- `tests/test_tools_filesystem.py` - 9 tests for filesystem tools (read, write, mkdir)
- `tests/test_tools_web.py` - 3 tests for web fetch tool (success, error, truncation)

## Decisions Made
- Used stub @tool decorator when Claude Agent SDK is not installed -- tools register with .name attribute, enabling testing without SDK dependency
- Used asyncio.to_thread() for file I/O instead of adding aiofiles as a new dependency -- stdlib-only, fewer dependencies
- HTML text extraction uses beautifulsoup4 if available, falls back to regex-based stripping -- works in all environments
- get_server() returns a dict stub when SDK not installed -- preserves interface contract for testing

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Neither claude_agent_sdk nor claude_code_sdk is installed in the development venv. Resolved by implementing a stub @tool decorator that creates objects with .name attribute matching the SDK's SdkMcpTool interface. This is expected -- the SDK will be installed when the agent backend is rewritten in Phase 4.
- httpx, bs4, and aiofiles were not available in the system Python but were available in the project venv (.venv/). Used the venv Python for all test runs.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- ToolRegistry foundation is ready for Plans 02 and 03 to register memory, analytics, github, and vercel tools
- Plan 04 will delete legacy ToolRouter and tool_wiring once all tools are migrated
- stub @tool decorator must be replaced with real SDK decorator once claude-agent-sdk is installed

## Self-Check: PASSED

- All 7 created files verified present on disk
- Commit 2e64d01 (Task 1) verified in git log
- Commit e0824ea (Task 2) verified in git log
- 24/24 tests passing

---
*Phase: 03-tool-migration*
*Completed: 2026-03-12*

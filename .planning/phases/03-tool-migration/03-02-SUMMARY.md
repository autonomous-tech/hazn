---
phase: 03-tool-migration
plan: 02
subsystem: tools
tags: [claude-agent-sdk, memory, github, vercel, async, vault, pygithub, httpx]

# Dependency graph
requires:
  - phase: 03-tool-migration-plan-01
    provides: ToolRegistry, stub @tool decorator, build_registry() pattern, SDK return format convention
  - phase: 02-model-simplification
    provides: Agency singleton via Agency.load(), VaultCredential model
provides:
  - 7 memory tools as async Python functions (load_context, write_finding, search_memory, search_cross_client_insights, checkpoint_sync, correct_memory, get_credentials)
  - 6 GitHub tools as async Python functions with zero auth params (create_repo, create_pr, get_pr_status, get_ci_status, list_branches, merge_pr)
  - 4 Vercel tools as async Python functions with zero auth params (deploy_project, get_deployment_status, get_preview_url, list_deployments)
  - Session-scoped _memory_registry for HaznMemory instance reuse
  - build_registry() now includes filesystem + web + memory + github + vercel tools
affects: [03-03-PLAN, 03-04-PLAN, 04-executor-rewrite]

# Tech tracking
tech-stack:
  added: [asgiref/sync_to_async (for Django ORM wrapping)]
  patterns: [agency-singleton-credential-lookup, sync-to-async-for-orm, deferred-django-imports-in-tools]

key-files:
  created:
    - hazn_platform/hazn_platform/orchestrator/tools/memory.py
    - hazn_platform/hazn_platform/orchestrator/tools/github.py
    - hazn_platform/hazn_platform/orchestrator/tools/vercel.py
    - hazn_platform/tests/test_tools_memory.py
    - hazn_platform/tests/test_tools_github.py
    - hazn_platform/tests/test_tools_vercel.py
  modified:
    - hazn_platform/hazn_platform/orchestrator/tools/__init__.py

key-decisions:
  - "Agency.load() singleton replaces l2_agency_id parameter in all tools -- credential lookup is internal"
  - "sync_to_async wraps all Django ORM and Vault calls -- tools are async-first for Agent SDK compatibility"
  - "Deferred Django model imports (inside functions, not at module top) -- avoids Django setup requirement at import time"
  - "search_cross_client_insights always-on (no Agency.cross_client_insights flag check) per CONTEXT.md decision"
  - "MagicMock (not AsyncMock) for httpx responses in Vercel tests -- httpx .json() is sync, AsyncMock causes coroutine issues"

patterns-established:
  - "Credential tool pattern: internal _get_*_sync() helper that uses Agency.load() + VaultCredential lookup, wrapped with sync_to_async"
  - "Memory registry pattern: module-level _memory_registry dict for session-scoped HaznMemory reuse"
  - "Tool helper pattern: _get_agency(), _create_memory(), _get_vault_credential() as testable sync functions with deferred imports"

requirements-completed: [TOOL-06, TOOL-07]

# Metrics
duration: 11min
completed: 2026-03-12
---

# Phase 3 Plan 2: Memory, GitHub, and Vercel Tools Summary

**17 MCP server tools ported to async Python functions with Agency singleton credential lookup and zero auth params**

## Performance

- **Duration:** 11 min
- **Started:** 2026-03-12T18:06:01Z
- **Completed:** 2026-03-12T18:17:08Z
- **Tasks:** 2
- **Files created:** 6
- **Files modified:** 1

## Accomplishments
- 7 memory tools ported from hazn_memory_server.py with session-scoped _memory_registry, Agency.load() singleton, and client_id param naming
- 6 GitHub tools ported from github_server.py with zero auth params -- PyGithub calls wrapped in sync_to_async for async compatibility
- 4 Vercel tools ported from vercel_server.py using httpx.AsyncClient for native async HTTP, zero auth params
- Full TDD with 28 tests passing (11 memory + 9 GitHub + 8 Vercel), 52 total across all tool modules

## Task Commits

Each task was committed atomically:

1. **Task 1: Port memory and GitHub tools** - `301b391` (feat)
2. **Task 2: Port Vercel tools** - `dd7c382` (feat)

_TDD RED commits: `e8e30e2` (memory+github tests), `48d819d` (vercel tests)_

## Files Created/Modified
- `hazn_platform/orchestrator/tools/memory.py` - 7 memory tools: load_context, write_finding, search_memory, search_cross_client_insights, checkpoint_sync, correct_memory, get_credentials
- `hazn_platform/orchestrator/tools/github.py` - 6 GitHub tools: create_repo, create_pr, get_pr_status, get_ci_status, list_branches, merge_pr
- `hazn_platform/orchestrator/tools/vercel.py` - 4 Vercel tools: deploy_project, get_deployment_status, get_preview_url, list_deployments
- `hazn_platform/orchestrator/tools/__init__.py` - build_registry() updated to register memory, github, and vercel tools
- `tests/test_tools_memory.py` - 11 tests covering all 7 memory tools and registry behavior
- `tests/test_tools_github.py` - 9 tests covering all 6 GitHub tools and error handling
- `tests/test_tools_vercel.py` - 8 tests covering all 4 Vercel tools and HTTP error handling

## Decisions Made
- Agency.load() singleton replaces l2_agency_id parameter -- all tools fetch credentials internally via the singleton agency, simplifying tool signatures
- sync_to_async wraps all Django ORM and Vault calls -- tools are async-first since the Agent SDK requires async tool handlers
- Deferred Django imports inside functions (not at module top) to avoid Django setup requirements at import time -- enables testing without full Django initialization
- search_cross_client_insights is always-on per CONTEXT.md -- no Agency.cross_client_insights flag check for the single-user agency model
- Used MagicMock (not AsyncMock) for httpx response objects in Vercel tests because httpx Response.json() is synchronous; AsyncMock would return coroutines instead of dicts

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed AsyncMock vs MagicMock for httpx response in Vercel tests**
- **Found during:** Task 2 (Vercel tool tests)
- **Issue:** Using AsyncMock for httpx response caused `.json()` to return a coroutine instead of a dict, since httpx Response.json() is synchronous
- **Fix:** Changed response mock from AsyncMock to MagicMock, keeping only the client methods as AsyncMock
- **Files modified:** tests/test_tools_vercel.py
- **Verification:** All 8 Vercel tests pass
- **Committed in:** dd7c382 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Test mock correction only. No scope creep.

## Issues Encountered
- Neither claude_agent_sdk nor claude_code_sdk is installed, so the stub @tool decorator from Plan 01 is used. This is expected and will be replaced in Phase 4.
- asgiref may not be installed in all environments; fallback to asyncio.to_thread provided for sync_to_async.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Plan 03 (analytics tools) can now proceed -- all non-analytics tools are migrated
- Plan 04 (cleanup) will delete legacy MCP server files, ToolRouter, and tool_wiring
- build_registry() currently registers 20 tools (3 filesystem + 1 web + 7 memory + 6 github + 4 vercel = 21)

## Self-Check: PASSED

- All 7 created/modified files verified present on disk
- Commit e8e30e2 (TDD RED memory+github) verified in git log
- Commit 301b391 (Task 1) verified in git log
- Commit 48d819d (TDD RED vercel) verified in git log
- Commit dd7c382 (Task 2) verified in git log
- 28/28 tests passing

---
*Phase: 03-tool-migration*
*Completed: 2026-03-12*

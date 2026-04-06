---
phase: 04-mcp-tool-servers-observability
plan: 01
subsystem: mcp
tags: [fastmcp, vercel, github, pygithub, httpx, vault, langfuse, openai]

# Dependency graph
requires:
  - phase: 02-memory-layer
    provides: FastMCP pattern from hazn_memory_server.py
  - phase: 07-vault-approle-authentication-scoped-policies
    provides: Vault AppRole auth and read_secret() helper
provides:
  - mcp-vercel server with 4 deployment tools (deploy, status, preview, list)
  - mcp-github server with 6 repo/PR tools (create_repo, create_pr, get_pr_status, get_ci_status, list_branches, merge_pr)
  - WorkflowRun.langfuse_trace_id field for bidirectional Langfuse linking
  - New dependencies langfuse, PyGithub, httpx, openai
affects: [04-02, 04-03, 05-agent-tool-integration]

# Tech tracking
tech-stack:
  added: [langfuse>=3.14.0, PyGithub>=2.8.1, httpx>=0.27.0, openai>=1.0.0]
  patterns: [Vault-per-request credential lookup for MCP tools, httpx.Client sync for Vercel API, PyGithub sync for GitHub API]

key-files:
  created:
    - hazn_platform/hazn_platform/mcp_servers/vercel_server.py
    - hazn_platform/hazn_platform/mcp_servers/github_server.py
    - hazn_platform/tests/test_mcp_vercel_server.py
    - hazn_platform/tests/test_mcp_github_server.py
    - hazn_platform/hazn_platform/orchestrator/migrations/0002_workflowrun_langfuse_trace_id.py
  modified:
    - hazn_platform/pyproject.toml
    - hazn_platform/hazn_platform/orchestrator/models.py

key-decisions:
  - "Manual migration file for langfuse_trace_id since Docker services not running locally"
  - "httpx.Client (sync) for Vercel API per FastMCP stdio constraint"
  - "PyGithub (sync) for GitHub API per FastMCP stdio constraint"
  - "Error dicts returned instead of raising exceptions for both servers"

patterns-established:
  - "Vault credential lookup pattern: VaultCredential.objects.get(agency_id=..., service_name=..., end_client__isnull=True) for agency-level tool credentials"
  - "MCP tool error handling: try/except returning {'error': str, 'status_code': int} for HTTP errors, {'error': str} for GitHub errors"

requirements-completed: [MCP-02, MCP-03]

# Metrics
duration: 5min
completed: 2026-03-06
---

# Phase 04 Plan 01: MCP Tool Servers Summary

**Two new MCP servers (Vercel 4 tools, GitHub 6 tools) with Vault credential lookup, plus WorkflowRun langfuse_trace_id migration and 4 new dependencies**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-06T03:22:51Z
- **Completed:** 2026-03-06T03:28:43Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments
- Built mcp-vercel server with 4 tools: deploy_project, get_deployment_status, get_preview_url, list_deployments using httpx sync client
- Built mcp-github server with 6 tools: create_repo, create_pr, get_pr_status, get_ci_status, list_branches, merge_pr using PyGithub
- Both servers fetch credentials from Vault at runtime via VaultCredential lookup (no hardcoded tokens)
- Added langfuse_trace_id CharField to WorkflowRun for bidirectional Langfuse linking
- 17 unit tests (8 Vercel, 9 GitHub) all passing with mocked external APIs

## Task Commits

Each task was committed atomically:

1. **Task 1: Add dependencies and WorkflowRun migration** - `e40fd04` (feat)
2. **Task 2: Build mcp-vercel server with 4 tools** - `81cfa4b` (test/RED), `cd9c481` (feat/GREEN)
3. **Task 3: Build mcp-github server with 6 tools** - `e2df57a` (test/RED), `17e5feb` (feat/GREEN)

_Note: TDD tasks have two commits each (test RED then feat GREEN)_

## Files Created/Modified
- `hazn_platform/pyproject.toml` - Added langfuse, PyGithub, httpx, openai dependencies
- `hazn_platform/hazn_platform/orchestrator/models.py` - Added langfuse_trace_id field to WorkflowRun
- `hazn_platform/hazn_platform/orchestrator/migrations/0002_workflowrun_langfuse_trace_id.py` - Migration for new field
- `hazn_platform/hazn_platform/mcp_servers/vercel_server.py` - FastMCP server with 4 Vercel deployment tools
- `hazn_platform/hazn_platform/mcp_servers/github_server.py` - FastMCP server with 6 GitHub repo/PR tools
- `hazn_platform/tests/test_mcp_vercel_server.py` - 8 unit tests for Vercel server
- `hazn_platform/tests/test_mcp_github_server.py` - 9 unit tests for GitHub server

## Decisions Made
- Manual migration file created for langfuse_trace_id since Docker services (PostgreSQL) not running locally; follows same pattern as 0001_initial.py
- httpx.Client (sync, not async) for Vercel API per FastMCP stdio transport constraint
- PyGithub (sync) for GitHub API per FastMCP stdio transport constraint
- Error handling returns dicts instead of raising exceptions, consistent with hazn_memory_server.py pattern

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Docker services not running locally (no DATABASE_URL), so migration was created manually following the exact Django migration format. The migration is equivalent to what makemigrations would generate.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Vercel and GitHub MCP servers ready for agent integration
- WorkflowRun.langfuse_trace_id field ready for Plan 03 (Langfuse observability)
- All 17 tests passing, both servers follow established FastMCP pattern

## Self-Check: PASSED

All 6 created files verified on disk. All 5 commit hashes verified in git log.

---
*Phase: 04-mcp-tool-servers-observability*
*Completed: 2026-03-06*

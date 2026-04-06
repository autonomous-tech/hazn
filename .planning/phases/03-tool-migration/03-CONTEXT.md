# Phase 3: Tool Migration - Context

**Gathered:** 2026-03-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Extract all MCP server logic into Python function tools registered with the Claude Agent SDK via a ToolRegistry. Delete all 4 MCP server files and remove fastmcp dependency. Build new File I/O and web fetch tools. All tools callable as standalone Python async functions outside the executor.

</domain>

<decisions>
## Implementation Decisions

### Memory tools — Migrate all 7 as-is
- Port all 7 hazn-memory tools to Python functions: load_context, write_finding, search_memory, search_cross_client_insights, checkpoint_sync, correct_memory, get_credentials
- Keep HaznMemory class as the backend — Python functions call it directly (no FastMCP wrapping)
- Keep session-scoped _memory_registry pattern (one HaznMemory per agent_id in module-level dict)
- Phase 5 will rewire HaznMemory internals; tool function signatures stay stable
- New location: orchestrator/tools/memory.py

### Analytics tools — In-process with full depth
- Port MCP server logic (analytics_server.py) to Python functions — in-process Google API calls, not subprocess wrappers
- Full script-level depth: events, conversions, geo, cannibalization, not just lightweight overview
- Write full JSON data to /tmp/hazn-audit/{client}/{timestamp}/ and return file path + summary to agent (keeps context window lean)
- Auth via Vault service account credentials (same as current MCP pattern)
- Delete data_tools.py (subprocess wrappers) — standalone hazn/scripts/ stay in hazn repo untouched
- New location: orchestrator/tools/analytics.py

### GitHub tools — Direct Python functions
- Port all 6 GitHub tools: create_repo, create_pr, get_pr_status, get_ci_status, list_branches, merge_pr
- Zero auth params — Agency singleton's GitHub PAT fetched internally from Vault
- Only operation params in signatures (repo_full_name, pr_number, etc.)
- New location: orchestrator/tools/github.py

### Vercel tools — Direct Python functions
- Port all 4 Vercel tools: deploy_project, get_deployment_status, get_preview_url, list_deployments
- Zero auth params — Agency singleton's Vercel token fetched internally from Vault
- Only operation params in signatures (project_name, deployment_id, etc.)
- New location: orchestrator/tools/vercel.py

### Tool parameter simplification
- Remove l2_agency_id from ALL tools — singleton Agency fetched internally
- Rename l3_client_id to client_id everywhere (maps to EndClient.id internally)
- GitHub/Vercel tools take zero auth params (agency-level creds implicit)
- Analytics/memory tools take client_id where per-client scoping needed

### Cross-client insights — Keep, always-on
- Migrate search_cross_client_insights as a Python function tool
- Remove Agency.cross_client_insights flag check — always enabled for single-user agency
- Queries Postgres directly for sibling client keywords, audits, campaigns, decisions

### ToolRegistry architecture
- New orchestrator/tools/ package with per-domain modules: memory.py, analytics.py, github.py, vercel.py, filesystem.py, web.py
- ToolRegistry maps tool names to async Python functions with `get_tools()` for Agent SDK definitions
- Replaces existing ToolRouter + tool_wiring.py

### Claude's Discretion
- Exact ToolRegistry class design and registration pattern
- File I/O tool scope (TOOL-01) and web fetch implementation (TOOL-02)
- How to handle analytics tool error cases (API quota, invalid property ID, etc.)
- Whether to keep tool_router.py's dispatch format helpers or rewrite
- JSON Schema definitions for each tool's input parameters
- How to structure the full-depth analytics queries (single function with options vs multiple focused functions)
- Test strategy for tools with external dependencies (Vault, Google APIs, GitHub)

</decisions>

<specifics>
## Specific Ideas

- Analytics tools write to /tmp/hazn-audit/{client}/{timestamp}/ — same pattern as existing scripts, keeps output discoverable
- Full-depth analytics means porting logic from hazn/scripts/ collectors (ga4_collector.py has events, conversions, device, geo; gsc_collector.py has brand/non-brand, cannibalization, trends)
- Tools should be callable standalone outside the executor — this enables testing and future CLI usage

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `core/memory.py` (HaznMemory): Full memory abstraction with load_context, search_memory, write_finding, checkpoint_sync, correct_memory — all 7 memory tools delegate to this
- `core/vault.py` (get_vault_client, read_secret, store_secret): Vault AppRole auth with token caching — reuse as-is for credential fetching
- `core/models.py` (VaultCredential): Credential lookup model with agency/client scoping — query patterns already established
- `orchestrator/tool_router.py` (_STATIC_TOOL_MAP): 23-tool registry with Anthropic API + Agent SDK dispatch formats — reference for new ToolRegistry design
- `orchestrator/tool_wiring.py` (wire_callables, scope_tools_for_phase): Callable injection and phase-scoped tool filtering — patterns to preserve in new design

### Established Patterns
- Per-request Vault credential lookup (never cached at tool level, per CRED-04)
- Session-scoped memory via module-level _memory_registry dict
- Dual dispatch format (Anthropic API tool_result + Agent SDK content format)
- Phase-scoped tool filtering from workflow YAML tool declarations

### Integration Points
- `orchestrator/backends/agent_sdk.py`: Consumes tool definitions via ToolRouter.to_anthropic_tools() — needs ToolRegistry.get_tools() equivalent
- `orchestrator/executor.py`: Calls ToolRouter for dispatch — needs ToolRegistry dispatch method
- `orchestrator/prompt_assembler.py`: Tool descriptions injected into system prompts
- `config/settings/base.py`: fastmcp in INSTALLED_APPS / dependencies — remove after migration

### Files to DELETE
- hazn_platform/mcp_servers/hazn_memory_server.py (7 tools → orchestrator/tools/memory.py)
- hazn_platform/mcp_servers/analytics_server.py (3 tools → orchestrator/tools/analytics.py)
- hazn_platform/mcp_servers/github_server.py (6 tools → orchestrator/tools/github.py)
- hazn_platform/mcp_servers/vercel_server.py (4 tools → orchestrator/tools/vercel.py)
- hazn_platform/mcp_servers/__init__.py
- hazn_platform/orchestrator/data_tools.py (subprocess wrappers — replaced by in-process tools)
- hazn_platform/orchestrator/tool_wiring.py (replaced by ToolRegistry)
- hazn_platform/orchestrator/tool_router.py (replaced by ToolRegistry)

### Files to CREATE
- hazn_platform/orchestrator/tools/__init__.py (package)
- hazn_platform/orchestrator/tools/registry.py (ToolRegistry class)
- hazn_platform/orchestrator/tools/memory.py (7 memory tools)
- hazn_platform/orchestrator/tools/analytics.py (3 analytics tools, full depth)
- hazn_platform/orchestrator/tools/github.py (6 GitHub tools)
- hazn_platform/orchestrator/tools/vercel.py (4 Vercel tools)
- hazn_platform/orchestrator/tools/filesystem.py (File I/O tools — TOOL-01)
- hazn_platform/orchestrator/tools/web.py (Web fetch tool — TOOL-02)

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-tool-migration*
*Context gathered: 2026-03-12*

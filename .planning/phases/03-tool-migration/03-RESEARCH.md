# Phase 3: Tool Migration - Research

**Researched:** 2026-03-12
**Domain:** Python function tools, Claude Agent SDK tool registration, MCP-to-Python migration
**Confidence:** HIGH

## Summary

Phase 3 migrates all tool functionality from 4 FastMCP MCP server files and 1 subprocess wrapper module into a new `orchestrator/tools/` Python package, registered with the Claude Agent SDK via a ToolRegistry class. The existing codebase has clean separation: MCP servers are thin wrappers around core modules (HaznMemory, vault.py) and external API clients (GA4, GSC, PageSpeed, GitHub, Vercel). The tool logic is straightforward to extract since the business logic already lives outside the MCP layer.

The Claude Agent SDK (formerly `claude_code_sdk`) provides a `@tool` decorator and `create_sdk_mcp_server()` function for registering Python async functions as in-process MCP tools. The existing `AgentSDKBackend` already references `mcp__hazn__` prefixed tool names, which aligns with the SDK's `mcp__{server_name}__{tool_name}` convention. The ToolRegistry must produce `SdkMcpTool` instances via `@tool` decorator and bundle them into an `McpSdkServerConfig` via `create_sdk_mcp_server()`.

Two brand-new tool domains must be created from scratch: File I/O (TOOL-01) and Web Fetch (TOOL-02). These have no MCP server predecessors. Analytics tools need significant expansion from the lightweight MCP server versions to full-depth collection matching the standalone scripts in `hazn/scripts/analytics-audit/`.

**Primary recommendation:** Extract tool logic module-by-module into `orchestrator/tools/`, build the ToolRegistry with Claude Agent SDK `@tool` decorator + `create_sdk_mcp_server()`, then delete MCP servers and old routing infrastructure only after all new tools are wired and tested.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Memory tools: Migrate all 7 as-is to orchestrator/tools/memory.py. Keep HaznMemory class as backend. Keep session-scoped _memory_registry pattern. Phase 5 rewires internals; signatures stay stable.
- Analytics tools: In-process with full depth (not subprocess wrappers). Port logic from analytics_server.py. Full-depth means events, conversions, geo, cannibalization, trends. Write full JSON to /tmp/hazn-audit/{client}/{timestamp}/ and return file path + summary. Auth via Vault service account credentials. Delete data_tools.py subprocess wrappers.
- GitHub tools: Direct Python functions. Port all 6 tools. Zero auth params -- Agency singleton's GitHub PAT fetched internally from Vault. Only operation params in signatures.
- Vercel tools: Direct Python functions. Port all 4 tools. Zero auth params -- Agency singleton's Vercel token fetched internally from Vault. Only operation params in signatures.
- Tool parameter simplification: Remove l2_agency_id from ALL tools. Rename l3_client_id to client_id. GitHub/Vercel take zero auth params. Analytics/memory take client_id where per-client scoping needed.
- Cross-client insights: Keep, always-on. Remove Agency.cross_client_insights flag check.
- ToolRegistry architecture: New orchestrator/tools/ package with per-domain modules. ToolRegistry maps tool names to async Python functions with get_tools() for Agent SDK definitions. Replaces ToolRouter + tool_wiring.py.
- Files to delete: mcp_servers/hazn_memory_server.py, analytics_server.py, github_server.py, vercel_server.py, __init__.py, orchestrator/data_tools.py, orchestrator/tool_wiring.py, orchestrator/tool_router.py
- Files to create: orchestrator/tools/__init__.py, registry.py, memory.py, analytics.py, github.py, vercel.py, filesystem.py, web.py

### Claude's Discretion
- Exact ToolRegistry class design and registration pattern
- File I/O tool scope (TOOL-01) and web fetch implementation (TOOL-02)
- How to handle analytics tool error cases (API quota, invalid property ID, etc.)
- Whether to keep tool_router.py's dispatch format helpers or rewrite
- JSON Schema definitions for each tool's input parameters
- How to structure the full-depth analytics queries (single function with options vs multiple focused functions)
- Test strategy for tools with external dependencies (Vault, Google APIs, GitHub)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| STRP-01 | All 4 MCP servers removed | Deletion of mcp_servers/ package, fastmcp from deps, and tool_router/tool_wiring replacement with ToolRegistry |
| TOOL-01 | File I/O tools (read/write files, create directories) | New filesystem.py module design with sandboxed operations |
| TOOL-02 | Web fetch tool (fetch and parse web pages) | New web.py module using httpx async with HTML-to-text extraction |
| TOOL-03 | GA4 data collection tool | analytics.py with full-depth GA4 collection ported from analytics_server.py + ga4_collector.py patterns |
| TOOL-04 | GSC data collection tool | analytics.py with full-depth GSC collection including brand analysis and cannibalization from gsc_collector.py |
| TOOL-05 | PageSpeed Insights API tool | analytics.py with enhanced PSI collection from pagespeed_collector.py (mobile + desktop, CWV, opportunities) |
| TOOL-06 | GitHub API tools (repo operations) | github.py with 6 tools, zero auth params, Agency singleton Vault lookup |
| TOOL-07 | Vercel deployment tools | vercel.py with 4 tools, zero auth params, Agency singleton Vault lookup |
| TOOL-08 | All tools registered with Claude Agent SDK | ToolRegistry using @tool decorator + create_sdk_mcp_server() producing McpSdkServerConfig |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| claude-agent-sdk | >=0.1.47 | Tool registration via @tool decorator and create_sdk_mcp_server() | Official SDK for Claude tool integration, replaces claude_code_sdk |
| httpx | >=0.27.0 | Async HTTP client for Vercel API, web fetch, PageSpeed API | Already in project deps; supports both sync and async |
| PyGithub | >=2.8.1 | GitHub API operations | Already in project deps; used by existing MCP server |
| google-analytics-data | >=0.20.0 | GA4 Data API v1beta client | Already in project deps |
| google-api-python-client | >=2.100.0 | GSC API client | Already in project deps |
| google-auth | >=2.20.0 | Service account credentials | Already in project deps |
| hvac | 2.4.0 | Vault credential retrieval | Already in project deps via core/vault.py |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| beautifulsoup4 | >=4.12.0 | HTML parsing for web fetch tool | TOOL-02 web fetch content extraction |
| aiofiles | >=23.0 | Async file I/O operations | TOOL-01 file system tools |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| beautifulsoup4 | lxml or trafilatura | BS4 is simpler, no compiled deps; trafilatura better for article extraction but overkill |
| aiofiles | sync open() with asyncio.to_thread | aiofiles is cleaner for async tools; sync+to_thread also works with less deps |
| httpx async | aiohttp | httpx already in deps and supports both sync/async; no need to add aiohttp |

**Installation:**
```bash
pip install beautifulsoup4 aiofiles
# Or add to pyproject.toml dependencies:
# "beautifulsoup4>=4.12.0",
# "aiofiles>=23.0",
```

**Dependency removal:**
```toml
# Remove from pyproject.toml:
# "fastmcp>=3.1.0",
```

## Architecture Patterns

### Recommended Project Structure
```
hazn_platform/orchestrator/tools/
    __init__.py          # Package init, re-exports ToolRegistry
    registry.py          # ToolRegistry class + get_tools() -> McpSdkServerConfig
    memory.py            # 7 memory tools (load_context, write_finding, etc.)
    analytics.py         # 3 analytics tools (pull_ga4_data, query_gsc, check_pagespeed)
    github.py            # 6 GitHub tools (create_repo, create_pr, etc.)
    vercel.py            # 4 Vercel tools (deploy_project, etc.)
    filesystem.py        # File I/O tools (read_file, write_file, mkdir)
    web.py               # Web fetch tool (fetch_page)
```

### Pattern 1: Claude Agent SDK Tool Registration
**What:** Each tool module defines async functions decorated with `@tool` from `claude_agent_sdk`. The ToolRegistry collects all tools and produces an `McpSdkServerConfig` via `create_sdk_mcp_server()`.
**When to use:** All tool definitions in this phase.
**Example:**
```python
# Source: https://platform.claude.com/docs/en/agent-sdk/python
from claude_agent_sdk import tool, create_sdk_mcp_server
from typing import Any

@tool("pull_ga4_data", "Pull GA4 analytics data for a property.", {
    "client_id": str,
    "property_id": str,
    "days": int,
})
async def pull_ga4_data(args: dict[str, Any]) -> dict[str, Any]:
    """Full-depth GA4 data collection."""
    client_id = args["client_id"]
    property_id = args["property_id"]
    days = args.get("days", 30)
    # ... implementation ...
    return {"content": [{"type": "text", "text": json.dumps(summary)}]}

# Registry bundles tools into SDK MCP server
hazn_tools_server = create_sdk_mcp_server(
    name="hazn",
    version="3.0.0",
    tools=[pull_ga4_data, query_gsc, ...],  # All SdkMcpTool instances
)

# Pass to ClaudeAgentOptions
options = ClaudeAgentOptions(
    mcp_servers={"hazn": hazn_tools_server},
    allowed_tools=["mcp__hazn__pull_ga4_data", "mcp__hazn__query_gsc", ...],
)
```

### Pattern 2: Agency Singleton Credential Lookup (Zero Auth Params)
**What:** Tools that need agency-level credentials (GitHub PAT, Vercel token) fetch them internally via `Agency.load()` + `VaultCredential` lookup. No auth params in tool signatures.
**When to use:** GitHub and Vercel tools.
**Example:**
```python
from hazn_platform.core.models import Agency, VaultCredential
from hazn_platform.core.vault import read_secret

def _get_github_client():
    """Create authenticated PyGithub client using Agency singleton."""
    agency = Agency.load()
    credential = VaultCredential.objects.get(
        agency=agency,
        service_name="github",
        end_client__isnull=True,
    )
    secret = read_secret(credential.vault_secret_id)
    return Github(auth=Auth.Token(secret["token"]))
```

### Pattern 3: Full-Depth Analytics with File Output
**What:** Analytics tools perform comprehensive data collection (matching standalone scripts), write full JSON to `/tmp/hazn-audit/{client}/{timestamp}/`, and return a summary + file path to the agent.
**When to use:** GA4, GSC, and PageSpeed tools.
**Example:**
```python
import json, os
from datetime import datetime

async def _write_analytics_output(client_id: str, tool_name: str, data: dict) -> str:
    """Write full analytics data to file, return path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"/tmp/hazn-audit/{client_id}/{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{tool_name}.json"
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    return output_path
```

### Pattern 4: Per-Client Credential Lookup (Analytics)
**What:** Analytics tools requiring per-client service account credentials look them up via `VaultCredential` using `client_id` (renamed from `l3_client_id`).
**When to use:** GA4 and GSC tools.
**Example:**
```python
from hazn_platform.core.models import VaultCredential
from hazn_platform.core.vault import read_secret
from google.oauth2 import service_account

def _get_ga4_credentials(client_id: str):
    """Fetch GA4 service account credentials from Vault."""
    credential = VaultCredential.objects.get(
        end_client_id=client_id, service_name="ga4"
    )
    sa_json = read_secret(credential.vault_secret_id)
    return service_account.Credentials.from_service_account_info(
        sa_json,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
```

### Pattern 5: ToolRegistry as Centralized Access Point
**What:** A ToolRegistry class collects all tool definitions and provides `get_tools()` to return the `McpSdkServerConfig` for use by `AgentSDKBackend`, and `get_tool_names()` for phase scoping.
**When to use:** Wire-up between tools and the executor.
**Example:**
```python
class ToolRegistry:
    """Central registry mapping tool names to Claude Agent SDK tool definitions."""

    def __init__(self):
        self._tools: list[SdkMcpTool] = []
        self._tool_names: set[str] = set()
        self._server: McpSdkServerConfig | None = None

    def register(self, tool: SdkMcpTool) -> None:
        self._tools.append(tool)
        self._tool_names.add(tool.name)
        self._server = None  # Invalidate cached server

    def get_server(self) -> McpSdkServerConfig:
        if self._server is None:
            self._server = create_sdk_mcp_server(
                name="hazn", version="3.0.0", tools=self._tools
            )
        return self._server

    def get_allowed_tools(self, phase_tools: list[str] | None = None) -> list[str]:
        """Return mcp__hazn__<name> formatted allowed_tools list."""
        names = phase_tools if phase_tools else list(self._tool_names)
        return [f"mcp__hazn__{name}" for name in names if name in self._tool_names]

    def list_tools(self) -> list[str]:
        return sorted(self._tool_names)
```

### Anti-Patterns to Avoid
- **Sync tools in async context:** The Agent SDK `@tool` decorator expects async handler functions. Even though existing MCP tools are sync, wrap sync I/O in `asyncio.to_thread()` or `sync_to_async()` rather than blocking the event loop.
- **Caching credentials at tool level:** Per CRED-04, credentials must be fetched per-request from Vault. Never cache service account JSON or API tokens in tool module state.
- **Returning raw API responses to agent:** Large API responses (GA4 reports with 50+ rows) consume context window. Write to file, return summary + path.
- **Importing Django at module level in tool modules:** Tool modules will be imported during registry build. Use deferred imports (`from hazn_platform.core.models import ...` inside functions) for Django models to avoid import order issues.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| GA4 API client | Custom HTTP requests to GA4 API | `google-analytics-data` `BetaAnalyticsDataClient` | Handles auth, pagination, request building, response parsing |
| GSC API client | Custom HTTP requests to GSC API | `google-api-python-client` `build("searchconsole", "v1")` | Handles auth, discovery doc, request building |
| GitHub API | Custom REST calls to GitHub API | `PyGithub` | Handles auth, pagination, rate limiting, error types |
| Vault secret retrieval | Direct HTTP to Vault API | `hvac` via `core/vault.py` `read_secret()` | Already handles AppRole auth, token caching, KV v2 paths |
| SDK tool registration | Manual MCP protocol implementation | `@tool` decorator + `create_sdk_mcp_server()` | SDK handles JSON Schema generation, MCP protocol, tool dispatch |
| HTML-to-text extraction | Regex-based HTML parsing | `beautifulsoup4` | Handles malformed HTML, nested tags, encoding |

**Key insight:** All external API clients are already in the project dependencies. The MCP migration is about removing the FastMCP wrapping layer and the MCP protocol overhead, not replacing the underlying API clients.

## Common Pitfalls

### Pitfall 1: Agent SDK @tool Handler Signature
**What goes wrong:** The `@tool` decorator expects `async def handler(args: dict[str, Any]) -> dict[str, Any]` -- a single `args` dict parameter, not individual keyword arguments like the existing MCP `@mcp.tool()` functions.
**Why it happens:** Existing MCP tools use `def tool_name(l2_agency_id: str, l3_client_id: str, ...)` with individual params. The Agent SDK uses a single `args` dict.
**How to avoid:** Each tool function must accept `args: dict[str, Any]` and destructure parameters from it. Return format must be `{"content": [{"type": "text", "text": "..."}]}`.
**Warning signs:** `TypeError: handler() got an unexpected keyword argument` at runtime.

### Pitfall 2: claude_code_sdk vs claude_agent_sdk Package Name
**What goes wrong:** The existing `agent_sdk.py` backend imports `claude_code_sdk` which is deprecated. The new tools must use `claude_agent_sdk`.
**Why it happens:** The project was built during the `claude_code_sdk` era. The package was renamed to `claude_agent_sdk`.
**How to avoid:** Use `from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions` in all new code. Update `agent_sdk.py` backend to import from `claude_agent_sdk` as well (but this is a Phase 4 concern).
**Warning signs:** `ModuleNotFoundError: No module named 'claude_code_sdk'` after removing old deps.

### Pitfall 3: Deleting MCP Servers Before New Tools Are Verified
**What goes wrong:** If MCP server files are deleted before new tool functions are confirmed working, the system is broken with no fallback.
**Why it happens:** Desire to "clean up" before verifying replacement works.
**How to avoid:** Create all new tool modules first, wire them through ToolRegistry, verify with tests, THEN delete MCP server files and old routing code in a final cleanup wave.
**Warning signs:** Tests importing from `hazn_platform.mcp_servers.*` start failing before new tests pass.

### Pitfall 4: Sync Django ORM Calls in Async Tool Handlers
**What goes wrong:** Django ORM is not async-safe by default. Calling `VaultCredential.objects.get()` inside an `async def` tool handler will raise `SynchronousOnlyOperation`.
**Why it happens:** Tool handlers must be async (SDK requirement), but Django ORM is sync.
**How to avoid:** Wrap ORM calls with `asgiref.sync.sync_to_async` or `asyncio.to_thread()` for Django ORM operations inside async handlers.
**Warning signs:** `django.core.exceptions.SynchronousOnlyOperation` at runtime.

### Pitfall 5: tool_router.py Import Cascade on Deletion
**What goes wrong:** Multiple modules import from `tool_router.py`: `agent_runner.py`, `agent_sdk.py` backend, `executor.py`, `apps.py`, and 4 test files. Deleting it without updating all importers causes cascading ImportErrors.
**Why it happens:** The tool_router is deeply wired into the orchestrator.
**How to avoid:** The new ToolRegistry in `orchestrator/tools/registry.py` must provide backward-compatible imports or all importers must be updated. Specifically:
  - `agent_runner.py` imports `ToolRouter` and `scope_tools_for_phase`
  - `apps.py` imports `build_tool_registry` and `wire_callables` and `validate_registry`
  - `executor.py` imports `build_tool_registry` and references `tool_wiring._ROUTER_SINGLETON`
  - `backends/agent_sdk.py` imports `ToolRouter`
**Warning signs:** `ImportError: cannot import name 'ToolRouter'` in seemingly unrelated modules.

### Pitfall 6: Analytics Full-Depth Scope Creep
**What goes wrong:** The standalone scripts (ga4_collector.py, gsc_collector.py) have 9-10 reports each. Porting all of them makes the analytics tools extremely complex.
**Why it happens:** Context says "full depth" but the MCP server versions only had 3 lightweight reports.
**How to avoid:** Port the reports that are most actionable for the SEO audit use case. For GA4: events, conversions, traffic sources, landing pages, devices, countries (6 reports matching ga4_collector.py). For GSC: top queries, landing pages, brand analysis, cannibalization, weekly trends (matching gsc_collector.py). For PageSpeed: dual strategy (mobile+desktop) matching pagespeed_collector.py. Write all data to files; return summaries.
**Warning signs:** Single tool function exceeding 200 lines, or API calls timing out at 300s.

### Pitfall 7: Missing Tool from Allowed List
**What goes wrong:** Agent SDK requires tools to be in `allowed_tools` with `mcp__hazn__` prefix. If a tool is registered but not in `allowed_tools`, the agent cannot use it.
**Why it happens:** Phase scoping must generate `mcp__hazn__{tool_name}` strings, not bare tool names.
**How to avoid:** ToolRegistry.get_allowed_tools() must always prefix with `mcp__hazn__`. The existing `AgentSDKBackend._build_allowed_tools()` already does this with `mcp__hazn__` prefix -- the new code must maintain this convention.
**Warning signs:** Agent says "I don't have access to that tool" even though it's registered.

## Code Examples

### Claude Agent SDK Tool Definition (Verified Pattern)
```python
# Source: https://platform.claude.com/docs/en/agent-sdk/python
from claude_agent_sdk import tool
from typing import Any

@tool("create_repo", "Create a new GitHub repository", {
    "name": str,
    "description": str,
    "private": bool,
})
async def create_repo(args: dict[str, Any]) -> dict[str, Any]:
    """Create a GitHub repository using Agency singleton credentials."""
    from asgiref.sync import sync_to_async
    from hazn_platform.core.models import Agency, VaultCredential
    from hazn_platform.core.vault import read_secret
    from github import Auth, Github

    # Fetch agency-level GitHub PAT from Vault
    agency = await sync_to_async(Agency.load)()
    credential = await sync_to_async(VaultCredential.objects.get)(
        agency=agency, service_name="github", end_client__isnull=True,
    )
    secret = await sync_to_async(read_secret)(credential.vault_secret_id)
    g = Github(auth=Auth.Token(secret["token"]))

    repo = g.get_user().create_repo(
        name=args["name"],
        description=args.get("description", ""),
        private=args.get("private", True),
        auto_init=True,
    )
    import json
    return {"content": [{"type": "text", "text": json.dumps({
        "id": repo.id,
        "full_name": repo.full_name,
        "clone_url": repo.clone_url,
        "html_url": repo.html_url,
    })}]}
```

### ToolRegistry with create_sdk_mcp_server (Verified Pattern)
```python
# Source: https://platform.claude.com/docs/en/agent-sdk/python
from claude_agent_sdk import create_sdk_mcp_server, ClaudeAgentOptions, SdkMcpTool

class ToolRegistry:
    def __init__(self):
        self._tools: list[SdkMcpTool] = []

    def register(self, *tools: SdkMcpTool) -> None:
        self._tools.extend(tools)

    def get_server(self) -> dict:
        return create_sdk_mcp_server(
            name="hazn", version="3.0.0", tools=self._tools,
        )

    def get_allowed_tools(self, phase_tools: list[str] | None = None) -> list[str]:
        all_names = {t.name for t in self._tools}
        if phase_tools:
            names = [n for n in phase_tools if n in all_names]
        else:
            names = sorted(all_names)
        return [f"mcp__hazn__{n}" for n in names]

# Usage in AgentSDKBackend:
registry = ToolRegistry()
# ... register all tools ...
options = ClaudeAgentOptions(
    mcp_servers={"hazn": registry.get_server()},
    allowed_tools=registry.get_allowed_tools(phase_tools),
)
```

### Memory Tool Migration Pattern
```python
# Source: Existing hazn_memory_server.py -> new tools/memory.py
from claude_agent_sdk import tool
from typing import Any

# Keep session-scoped registry (same pattern as MCP server)
_memory_registry: dict[str, "HaznMemory"] = {}

@tool("load_context", "Load client context into agent memory", {
    "agent_id": str,
    "client_id": str,
})
async def load_context(args: dict[str, Any]) -> dict[str, Any]:
    from asgiref.sync import sync_to_async
    from hazn_platform.core.memory import HaznMemory
    from hazn_platform.core.models import Agency
    import uuid

    agent_id = args["agent_id"]
    client_id = args["client_id"]

    # Agency singleton replaces l2_agency_id param
    agency = await sync_to_async(Agency.load)()

    if agent_id not in _memory_registry:
        _memory_registry[agent_id] = HaznMemory(
            agent_id=agent_id,
            l3_client_id=uuid.UUID(client_id),
            l2_agency_id=agency.id,
        )
    memory = _memory_registry[agent_id]
    await sync_to_async(memory.load_client_context)()

    return {"content": [{"type": "text", "text":
        f"Context loaded for agent={agent_id} client={client_id}"}]}
```

### Analytics File Output Pattern
```python
import json, os
from datetime import datetime
from typing import Any

async def _write_and_summarize(
    client_id: str, tool_name: str, data: dict[str, Any]
) -> dict[str, Any]:
    """Write full data to /tmp/hazn-audit/ and return summary + path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"/tmp/hazn-audit/{client_id}/{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{tool_name}.json"

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    # Build lean summary for context window
    summary = {
        "output_file": output_path,
        "record_count": sum(
            len(v) for v in data.values() if isinstance(v, list)
        ),
        "sections": list(data.keys()),
    }
    return {"content": [{"type": "text", "text": json.dumps(summary)}]}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `claude_code_sdk` package | `claude_agent_sdk` package | Late 2025 | Must use new package name in all imports |
| `ClaudeCodeOptions` class | `ClaudeAgentOptions` class | Late 2025 | API options class renamed |
| FastMCP `@mcp.tool()` decorator | Agent SDK `@tool` decorator | N/A (migration) | Different handler signature: `args: dict` vs individual params |
| `tool_router.dispatch_agent_sdk()` | `create_sdk_mcp_server()` in-process MCP | Current | SDK handles dispatch internally; no manual dispatch needed |
| Subprocess data collection wrappers | In-process Python function calls | This phase | Eliminates subprocess overhead, enables async |
| `mcp__hazn__` prefix in allowed_tools | Same convention continues | Current | Agent SDK uses `mcp__{server_name}__{tool_name}` |

**Deprecated/outdated:**
- `claude_code_sdk`: Deprecated, renamed to `claude_agent_sdk`. All new code must use the new package name.
- `fastmcp`: Will be removed from dependencies after this phase. Not needed when using Agent SDK's `@tool` + `create_sdk_mcp_server()`.
- `ToolRouter` dual-format dispatch (Anthropic API + Agent SDK): Anthropic API backend was removed in Phase 1 (STRP-04). Only Agent SDK format needed now.

## Open Questions

1. **google-analytics-admin dependency for GA4 property metadata**
   - What we know: The standalone ga4_collector.py uses `AnalyticsAdminServiceClient` for property metadata (step 1 of 9). The MCP server version does not.
   - What's unclear: Whether `google-analytics-admin` is in project deps. The full-depth analytics need may require it.
   - Recommendation: Check if installed; if not, the property metadata report can be omitted from the tool (it's metadata, not performance data). The 8 remaining GA4 reports cover the audit needs.

2. **claude-agent-sdk installation**
   - What we know: The project currently uses `claude_code_sdk` (deprecated) imported at runtime with try/except. It is NOT in pyproject.toml dependencies.
   - What's unclear: Whether to add `claude-agent-sdk` to pyproject.toml now or keep the lazy import pattern.
   - Recommendation: Add `claude-agent-sdk>=0.1.47` to pyproject.toml dependencies. The @tool decorator needs to be available at import time for tool module loading.

3. **beautifulsoup4 and aiofiles as new dependencies**
   - What we know: TOOL-01 (File I/O) and TOOL-02 (Web Fetch) need async file ops and HTML parsing.
   - What's unclear: Whether to add these deps or use simpler stdlib alternatives.
   - Recommendation: Use `aiofiles` for file tools (cleaner async), `beautifulsoup4` for web fetch HTML extraction. Both are lightweight and well-maintained. Alternatively, `asyncio.to_thread(open(...))` and simple regex-based HTML stripping could avoid new deps.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 + pytest-asyncio + pytest-django |
| Config file | pyproject.toml `[tool.pytest.ini_options]` |
| Quick run command | `cd hazn_platform && python -m pytest tests/test_tool_registry.py tests/test_tools_memory.py tests/test_tools_analytics.py tests/test_tools_github.py tests/test_tools_vercel.py tests/test_tools_filesystem.py tests/test_tools_web.py -x -q` |
| Full suite command | `cd hazn_platform && python -m pytest tests/ -x -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| STRP-01 | MCP servers deleted, fastmcp removed | unit | `pytest tests/test_tool_registry.py -x` (verifies no MCP imports) | Wave 0 |
| TOOL-01 | File I/O tools work standalone | unit | `pytest tests/test_tools_filesystem.py -x` | Wave 0 |
| TOOL-02 | Web fetch tool works standalone | unit | `pytest tests/test_tools_web.py -x` | Wave 0 |
| TOOL-03 | GA4 tool retrieves real data | unit+mock | `pytest tests/test_tools_analytics.py::TestGA4Tool -x` | Wave 0 |
| TOOL-04 | GSC tool retrieves real data | unit+mock | `pytest tests/test_tools_analytics.py::TestGSCTool -x` | Wave 0 |
| TOOL-05 | PageSpeed tool retrieves data | unit+mock | `pytest tests/test_tools_analytics.py::TestPageSpeedTool -x` | Wave 0 |
| TOOL-06 | GitHub tools work as Python functions | unit+mock | `pytest tests/test_tools_github.py -x` | Wave 0 |
| TOOL-07 | Vercel tools work as Python functions | unit+mock | `pytest tests/test_tools_vercel.py -x` | Wave 0 |
| TOOL-08 | All tools registered with Agent SDK | unit | `pytest tests/test_tool_registry.py::TestToolRegistration -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_tool_registry.py tests/test_tools_*.py -x -q`
- **Per wave merge:** `python -m pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_tool_registry.py` -- covers STRP-01, TOOL-08 (replaces test_tool_router.py + test_tool_wiring.py)
- [ ] `tests/test_tools_memory.py` -- covers memory tool migration (replaces test_mcp_memory_server.py)
- [ ] `tests/test_tools_analytics.py` -- covers TOOL-03, TOOL-04, TOOL-05 (replaces test_mcp_analytics_server.py + test_data_tools.py)
- [ ] `tests/test_tools_github.py` -- covers TOOL-06 (replaces test_mcp_github_server.py)
- [ ] `tests/test_tools_vercel.py` -- covers TOOL-07 (replaces test_mcp_vercel_server.py)
- [ ] `tests/test_tools_filesystem.py` -- covers TOOL-01 (new)
- [ ] `tests/test_tools_web.py` -- covers TOOL-02 (new)

## Sources

### Primary (HIGH confidence)
- Claude Agent SDK Python Reference (https://platform.claude.com/docs/en/agent-sdk/python) -- @tool decorator, create_sdk_mcp_server(), ClaudeAgentOptions, SdkMcpTool dataclass, handler signature `args: dict -> dict`
- Existing codebase: hazn_platform/mcp_servers/*.py -- all 4 MCP server implementations with exact tool signatures and logic
- Existing codebase: hazn_platform/orchestrator/tool_router.py -- 23-tool static registry, dual-format dispatch
- Existing codebase: hazn_platform/orchestrator/tool_wiring.py -- wire_callables(), scope_tools_for_phase()
- Existing codebase: hazn_platform/orchestrator/backends/agent_sdk.py -- current SDK integration using mcp__hazn__ prefix
- Existing codebase: hazn/scripts/analytics-audit/*.py -- full-depth GA4 (9 reports), GSC (10 reports), PageSpeed (mobile+desktop) collection logic

### Secondary (MEDIUM confidence)
- PyPI claude-agent-sdk listing -- confirmed package rename from claude-code-sdk, version >=0.1.47
- Existing codebase: hazn_platform/core/memory.py -- HaznMemory class with all 7 memory operations
- Existing codebase: hazn_platform/core/vault.py -- read_secret(), AppRole auth

### Tertiary (LOW confidence)
- beautifulsoup4 and aiofiles recommendations -- based on general Python async patterns, not verified against specific project constraints

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all core libraries already in project deps; Agent SDK patterns verified from official docs
- Architecture: HIGH - ToolRegistry design follows Agent SDK's create_sdk_mcp_server() pattern directly; tool module structure matches CONTEXT.md decisions
- Pitfalls: HIGH - pitfalls identified from direct code analysis of import chains, existing handler signatures, and SDK documentation
- Analytics full-depth: MEDIUM - scope of "full depth" is clear from scripts but the exact subset to port is a judgment call
- New dependencies (beautifulsoup4, aiofiles): LOW - may not be needed if stdlib alternatives suffice

**Research date:** 2026-03-12
**Valid until:** 2026-04-12 (stable domain -- libraries are mature)

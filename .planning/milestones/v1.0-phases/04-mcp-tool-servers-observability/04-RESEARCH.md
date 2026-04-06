# Phase 4: MCP Tool Servers & Observability - Research

**Researched:** 2026-03-06
**Domain:** MCP server development (FastMCP), Langfuse LLM tracing, external API integration (Vercel, GitHub, Google Analytics, GSC, PageSpeed), metering pipeline wiring
**Confidence:** HIGH

## Summary

Phase 4 builds three MCP tool servers (mcp-vercel, mcp-github, mcp-analytics) following the established FastMCP 3.1.0 pattern from mcp-hazn-memory, wires Langfuse v3 tracing into the orchestrator, connects the existing MeteringCallback to Langfuse for dual visibility, and replaces the conflict detection LLM stub with a real gpt-4o-mini call.

The project already has a complete MCP server template (`hazn_memory_server.py`), working analytics scripts (`ga4_collector.py`, `gsc_collector.py`, `pagespeed_collector.py`), a functional MeteringCallback with threshold alerts, and Langfuse env vars defined in `base.py`. The primary work is: (1) wrapping existing analytics scripts into an MCP server with service account auth instead of OAuth2, (2) building Vercel and GitHub MCP servers with httpx against their REST APIs, (3) integrating Langfuse v3 SDK into the executor/session layer, and (4) adding tool call metering to WorkflowToolCall records.

**Primary recommendation:** Use Langfuse v3 Python SDK (3.14.x) with `get_client()` + `start_as_current_observation()` context manager pattern for tracing; httpx for async API calls in Vercel/GitHub servers; PyGithub for GitHub API; direct Google API clients with `from_service_account_info()` for GA4/GSC; and the existing MeteringCallback wrapped inside Langfuse observation callbacks for unified metering.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Hybrid approach: wrap existing GA4/GSC/PageSpeed Python scripts into MCP servers; build fresh for Vercel and GitHub
- mcp-vercel: deploy + preview only -- deploy_project, get_preview_url, list_deployments, get_deployment_status. No domain/DNS management
- mcp-github: repo + PR management -- create_repo, create_pr, get_pr_status, get_ci_status, list_branches, merge_pr. No issues, actions, releases, or webhooks
- mcp-analytics: combined server exposing GA4, GSC, and PageSpeed tools in one server
- All MCP servers use FastMCP 3.1.0 with stdio transport
- Trace hierarchy: Workflow (trace) -> Phase (span) -> LLM calls + tool calls (generations/spans). One trace per workflow run
- Trace both LLM calls and MCP tool calls. Memory operations not traced separately
- Tags on every trace: l2_client_id, l3_client_id, workflow_run_id
- Bidirectional linking: Langfuse trace_id on WorkflowRun; workflow_run_id tagged on Langfuse traces
- Unified LLM callback: Langfuse callback wraps MeteringCallback. Langfuse = debug/visibility, Postgres = billing source of truth
- Runaway agent alerts create HITL item AND Langfuse event/annotation
- All MCP servers receive credentials via get_credentials(service_name, l2_id, l3_id) from Vault
- GA4/GSC: service accounts stored as JSON in Vault per L2/L3
- Vercel/GitHub: credentials scoped per L2 agency
- PageSpeed: optional API key, graceful fallback to free tier
- Wire conflict detection LLM call (gpt-4o-mini) now since Langfuse pipeline is being built

### Claude's Discretion
- Tool call metering approach (direct instrumentation in MCP vs extract from Langfuse)
- Exact Langfuse SDK integration pattern (decorators vs context managers)
- MCP server error handling and retry patterns
- Conflict detection prompt design for gpt-4o-mini

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| MCP-02 | mcp-vercel server supports deploy, preview URL generation, domain management | Vercel REST API v13 `POST /v13/deployments` for deploy, `GET /v6/deployments` for listing, response contains `url` field for preview URLs. Domain management explicitly excluded per user decision |
| MCP-03 | mcp-github server supports repo management, PR creation, CI status | PyGithub 2.8.1 provides `create_repo`, `create_pull`, `get_pulls`, commit status checks. Scoped to repo+PR per user decision |
| MCP-04 | mcp-ga4 server supports GA4 data pull, GSC queries, benchmarks | Existing `ga4_collector.py` and `gsc_collector.py` wrap into combined mcp-analytics server. Switch from OAuth2 to `BetaAnalyticsDataClient.from_service_account_info()` |
| MCP-05 | mcp-pagespeed server supports Core Web Vitals and performance scoring | Existing `pagespeed_collector.py` wraps into mcp-analytics. Uses stdlib urllib, optional API key from Vault |
| OBS-01 | Langfuse SDK traces every LLM call with l2_client_id, l3_client_id, workflow_run_id tags | Langfuse v3 SDK `propagate_attributes()` for tags, `start_as_current_observation(as_type="generation")` for LLM calls |
| OBS-02 | Postgres workflow_runs table tracks status, tokens, cost per workflow run | Existing WorkflowRun model + MeteringCallback.flush_to_db(). Add langfuse_trace_id field for bidirectional linking |
| OBS-03 | workflow_agents table tracks per-agent turns, tokens, cost | Existing WorkflowAgent model + MeteringCallback already handles this |
| OBS-04 | workflow_tool_calls table tracks per-tool call count and cost | Existing WorkflowToolCall model needs population. Use direct instrumentation in MCP tool wrappers |
| OBS-05 | System flags runaway agents (>50 turns) and cost outliers (>$5/run) | Existing MeteringCallback threshold alerts + new dual-write to Langfuse event annotation |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| langfuse | >=3.14.0 | LLM tracing and observability | Self-hosted Langfuse already deployed; v3 SDK built on OpenTelemetry, singleton `get_client()`, context manager spans |
| fastmcp | >=3.1.0 | MCP server framework | Already used for mcp-hazn-memory; `@mcp.tool()` decorator pattern established |
| PyGithub | >=2.8.1 | GitHub REST API v3 client | Most widely used Python GitHub library; typed API, covers repos/PRs/CI status |
| httpx | >=0.27.0 | Async HTTP client for Vercel API | Supports sync+async, HTTP/2, connection pooling; already a transitive dep |
| google-analytics-data | >=0.18.0 | GA4 Data API client | Already in analytics scripts requirements; `BetaAnalyticsDataClient` |
| google-api-python-client | >=2.0.0 | GSC Search Console API | Already in analytics scripts requirements; `build("searchconsole", ...)` |
| google-auth | >=2.0.0 | Service account authentication | `from_service_account_info()` for Vault-stored JSON credentials |
| openai | >=1.0.0 | gpt-4o-mini for conflict detection | Drop-in Langfuse integration via `from langfuse.openai import openai` |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| google-auth-oauthlib | >=1.0.0 | OAuth2 flow (existing scripts) | Already installed; not needed for service account path but kept as existing dep |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| PyGithub | githubkit | githubkit has native async + GraphQL but PyGithub is more mature, widely adopted, and covers all needed operations. PyGithub is sufficient for repo+PR scope |
| httpx (for Vercel) | requests | requests is sync-only; httpx supports async which aligns with executor's asyncio pattern |
| Direct Langfuse SDK | LangChain callback handler | Project doesn't use LangChain; direct SDK is simpler and avoids unnecessary dependency |

**Installation:**
```bash
pip install langfuse>=3.14.0 PyGithub>=2.8.1 httpx>=0.27.0 openai>=1.0.0
```

Note: `google-analytics-data`, `google-api-python-client`, `google-auth`, `fastmcp` are already in `pyproject.toml` or `requirements.txt`. `langfuse`, `PyGithub`, `httpx`, and `openai` need to be added to `pyproject.toml`.

## Architecture Patterns

### Recommended Project Structure
```
hazn_platform/
  hazn_platform/
    mcp_servers/
      hazn_memory_server.py   # existing (Phase 2)
      vercel_server.py         # NEW: mcp-vercel
      github_server.py         # NEW: mcp-github
      analytics_server.py      # NEW: mcp-analytics (GA4+GSC+PageSpeed)
    orchestrator/
      metering.py              # existing -- add tool call tracking
      tracing.py               # NEW: Langfuse integration layer
      conflict_detector.py     # existing -- replace LLM stub
      session.py               # existing -- add Langfuse trace lifecycle
      executor.py              # existing -- add tracing spans per phase
      models.py                # existing -- add langfuse_trace_id field
    core/
      vault.py                 # existing -- no changes
```

### Pattern 1: MCP Server with Vault Credentials (Template)
**What:** Each MCP server follows the same structure as hazn_memory_server.py: Django setup guard, FastMCP instance, @mcp.tool() decorators, credential fetching via get_credentials MCP tool or direct vault.read_secret().
**When to use:** All three new MCP servers.
**Example:**
```python
# Source: existing hazn_memory_server.py pattern
from __future__ import annotations
import os
import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
if not settings.configured:
    django.setup()

from fastmcp import FastMCP
from hazn_platform.core.vault import read_secret

mcp = FastMCP("hazn-vercel")

@mcp.tool()
def deploy_project(
    l2_agency_id: str,
    project_name: str,
    git_repo_id: str,
    git_ref: str = "main",
) -> dict:
    """Deploy a project to Vercel via git source."""
    creds = _get_vercel_credentials(l2_agency_id)
    # ... httpx call to Vercel API
    return {"deployment_id": "...", "url": "..."}
```

### Pattern 2: Langfuse v3 Tracing with Context Manager
**What:** Use `get_client()` singleton + `start_as_current_observation()` context managers. One trace per workflow run, spans per phase, generations per LLM call.
**When to use:** WorkflowExecutor.run() and per-phase execution.
**Example:**
```python
# Source: Langfuse v3 SDK docs
from langfuse import get_client, propagate_attributes

langfuse = get_client()

async def run(self) -> WorkflowRun:
    with langfuse.start_as_current_observation(
        as_type="span",
        name=f"workflow-{self._workflow.name}",
    ) as trace_span:
        with propagate_attributes(
            user_id=str(workflow_run.agency_id),
            session_id=str(workflow_run.pk),
            tags=[
                f"l2:{workflow_run.agency_id}",
                f"l3:{workflow_run.end_client_id}",
                f"run:{workflow_run.pk}",
            ],
            metadata={
                "l2_client_id": str(workflow_run.agency_id),
                "l3_client_id": str(workflow_run.end_client_id),
                "workflow_run_id": str(workflow_run.pk),
                "workflow_name": workflow_run.workflow_name,
            },
        ):
            # Get trace_id for bidirectional linking
            trace_id = langfuse.get_current_trace_id()
            workflow_run.langfuse_trace_id = trace_id
            await sync_to_async(workflow_run.save)(
                update_fields=["langfuse_trace_id"]
            )

            # Execute phases...
            for wave in waves:
                for phase in wave:
                    with langfuse.start_as_current_observation(
                        as_type="span",
                        name=f"phase-{phase.id}",
                    ) as phase_span:
                        await self._execute_phase(phase)
```

### Pattern 3: Unified Metering Callback (Langfuse + Postgres)
**What:** Wrap MeteringCallback inside Langfuse generation tracking. On each LLM call, both Langfuse (for debug traces) and Postgres (for billing) receive the data.
**When to use:** Every LLM call through the orchestrator.
**Example:**
```python
# Source: Langfuse v3 docs + existing MeteringCallback
from langfuse import get_client
from langfuse.openai import openai  # drop-in replacement

langfuse = get_client()

def make_llm_call(prompt, agent_id, metering_callback):
    """Make LLM call with dual tracking."""
    with langfuse.start_as_current_observation(
        as_type="generation",
        name=f"llm-{agent_id}",
        model="gpt-4o-mini",
    ) as gen:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        # Langfuse auto-captures via drop-in replacement
        # Feed MeteringCallback for Postgres billing
        usage = response.usage
        metering_callback.on_llm_call(
            agent_id=agent_id,
            tokens=usage.total_tokens,
            cost=_estimate_cost("gpt-4o-mini", usage),
        )
    return response
```

### Pattern 4: Service Account Auth for Google APIs
**What:** Replace OAuth2 flow with service account JSON from Vault. Service accounts don't require interactive login and support multi-tenant isolation.
**When to use:** GA4 and GSC API calls in mcp-analytics.
**Example:**
```python
# Source: Google Analytics Data API docs
import json
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_ga4_client(service_account_json: dict) -> BetaAnalyticsDataClient:
    """Create GA4 client from Vault-stored service account."""
    credentials = service_account.Credentials.from_service_account_info(
        service_account_json,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
    return BetaAnalyticsDataClient(credentials=credentials)

def get_gsc_service(service_account_json: dict):
    """Create GSC service from Vault-stored service account."""
    credentials = service_account.Credentials.from_service_account_info(
        service_account_json,
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
    )
    return build("searchconsole", "v1", credentials=credentials)
```

### Anti-Patterns to Avoid
- **Storing credentials in MCP server state:** Credentials must be fetched per-request from Vault. Never cache service account JSON in module-level variables or class attributes.
- **Creating a new Langfuse client per request:** Use `get_client()` which returns a singleton. Creating new clients leaks connections.
- **Mixing sync and async in MCP tools:** FastMCP 3.1.0 with stdio transport uses sync tool functions. Do NOT decorate MCP tools with `async def` -- use sync httpx client or run async code with `asyncio.run()` inside the tool.
- **Tracing memory operations separately:** Per user decision, memory operations (load_context, checkpoint_sync) are internal plumbing -- do not create Langfuse spans for them.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| GitHub API wrapper | Custom REST client with auth handling | PyGithub | Handles pagination, rate limiting, auth, error mapping for 300+ endpoints |
| LLM cost estimation | Token-to-cost lookup tables | Langfuse cost tracking + OpenAI response.usage | Langfuse auto-captures model pricing; manual tables go stale |
| OpenTelemetry trace propagation | Manual trace_id threading | Langfuse v3 `propagate_attributes()` | Uses contextvars internally, handles async correctly |
| GA4 report builder | Custom protobuf message construction | `BetaAnalyticsDataClient.run_report()` | Handles pagination, retries, and schema validation |
| Vercel deployment polling | Custom polling loop with sleep | httpx with explicit status check | Simple GET to check `readyState`, no need for WebSocket |

**Key insight:** The analytics scripts already have proven data extraction logic. The MCP server layer is a thin wrapper -- do not rewrite the collection logic, refactor it to accept credentials as parameters instead of reading from filesystem.

## Common Pitfalls

### Pitfall 1: Langfuse Context Loss in Async/Thread Boundaries
**What goes wrong:** Langfuse v3 uses Python contextvars for trace propagation. Context is lost when crossing thread boundaries (ThreadPoolExecutor) or when using `sync_to_async` wrappers.
**Why it happens:** Django's `sync_to_async` uses a thread pool. The Langfuse context from the calling async code doesn't automatically propagate to the worker thread.
**How to avoid:** Capture trace_id and observation_id before crossing the boundary, then pass them explicitly. Or use `langfuse.start_observation()` (non-context-manager) with explicit parent linking.
**Warning signs:** Langfuse traces show disconnected spans or missing child observations.

### Pitfall 2: GA4/GSC Service Account Scope Mismatch
**What goes wrong:** Service account has `analytics.readonly` scope but the code tries to call Admin API methods (like `list_account_summaries`) which require `analytics.edit` or separate admin scopes.
**Why it happens:** The existing `ga4_collector.py` uses both `BetaAnalyticsDataClient` (Data API) and `AnalyticsAdminServiceClient` (Admin API) with different scope requirements.
**How to avoid:** For MCP server, only use `BetaAnalyticsDataClient` for report data. Skip property metadata collection (Admin API) or use a separate scope. Minimum scope: `analytics.readonly` for GA4 data, `webmasters.readonly` for GSC.
**Warning signs:** `google.auth.exceptions.RefreshError` or 403 responses from Admin API.

### Pitfall 3: Vercel Deployment Status Polling
**What goes wrong:** Creating a deployment returns immediately with `readyState: "QUEUED"`. The deployment URL (`url` field) is available but the site isn't ready. Code tries to use the URL immediately and gets 404.
**Why it happens:** Vercel builds take 30s-5min. The API is fire-and-forget.
**How to avoid:** `deploy_project` should return the deployment ID + URL immediately. Provide a separate `get_deployment_status` tool that checks `readyState`. Don't poll in the deploy tool itself -- let the agent check status when needed.
**Warning signs:** Agent getting 502/404 when accessing just-deployed preview URLs.

### Pitfall 4: FastMCP Sync-Only Tool Functions
**What goes wrong:** Declaring MCP tool functions as `async def` when using FastMCP with stdio transport causes unexpected behavior or hangs.
**Why it happens:** FastMCP 3.1.0 stdio transport runs a sync event loop. Async tool functions need special handling.
**How to avoid:** Use sync `def` for all `@mcp.tool()` functions. For HTTP calls (Vercel, GitHub), use `httpx.Client()` (sync) not `httpx.AsyncClient()`. The MCP server runs in its own process, so blocking on network I/O is acceptable.
**Warning signs:** MCP tools hanging or timing out without error.

### Pitfall 5: OpenAI Drop-in Import Scope
**What goes wrong:** Using `from langfuse.openai import openai` only traces calls made through that import. Direct `import openai` calls elsewhere bypass Langfuse.
**Why it happens:** The drop-in replacement wraps the OpenAI client at import time. Other modules importing OpenAI normally get the unwrapped version.
**How to avoid:** Centralize all OpenAI calls through a single module (e.g., `orchestrator/tracing.py`) that uses the Langfuse drop-in. Never import OpenAI directly in other modules.
**Warning signs:** Some LLM calls missing from Langfuse traces despite the integration being "set up."

### Pitfall 6: Dual Metering Double-Counting
**What goes wrong:** If both Langfuse auto-captures cost and MeteringCallback manually adds cost, the totals disagree between systems.
**Why it happens:** Langfuse's OpenAI drop-in auto-tracks usage. MeteringCallback also manually tracks the same call.
**How to avoid:** Langfuse is for DEBUG visibility only (per PROJECT.md). MeteringCallback is billing source of truth. Accept that the two systems track the same data independently. Do NOT try to deduplicate -- they serve different purposes.
**Warning signs:** Dashboard showing different totals between Langfuse and Postgres -- this is expected and correct.

### Pitfall 7: WorkflowToolCall Population Gap
**What goes wrong:** WorkflowToolCall model exists (Phase 3) but never gets populated. MeteringCallback only tracks LLM calls (on_llm_call), not tool calls.
**Why it happens:** MeteringCallback was designed for LLM metering. Tool call metering was deferred to this phase.
**How to avoid:** Add an `on_tool_call(tool_name, latency_ms, success)` method to MeteringCallback. Instrument tool calls at the MCP invocation layer -- when the executor calls an MCP tool, wrap it with timing and feed MeteringCallback.
**Warning signs:** WorkflowToolCall table empty despite tools being used in workflows.

## Code Examples

### MCP-Vercel: Deploy Project Tool
```python
# Source: Vercel REST API docs + existing MCP pattern
import httpx
from fastmcp import FastMCP
from hazn_platform.core.vault import read_secret
from hazn_platform.core.models import VaultCredential

mcp = FastMCP("hazn-vercel")

def _get_vercel_token(l2_agency_id: str) -> str:
    """Fetch Vercel token from Vault for agency."""
    credential = VaultCredential.objects.get(
        agency_id=l2_agency_id,
        service_name="vercel",
    )
    secret = read_secret(credential.vault_secret_id)
    return secret["token"]

@mcp.tool()
def deploy_project(
    l2_agency_id: str,
    project_name: str,
    git_repo_id: str,
    git_ref: str = "main",
    target: str = "staging",
) -> dict:
    """Deploy a project to Vercel from a git source.

    Returns deployment ID, preview URL, and initial status.
    Use get_deployment_status to poll for readyState=READY.
    """
    token = _get_vercel_token(l2_agency_id)
    with httpx.Client(
        base_url="https://api.vercel.com",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30.0,
    ) as client:
        response = client.post("/v13/deployments", json={
            "name": project_name,
            "gitSource": {
                "type": "github",
                "ref": git_ref,
                "repoId": git_repo_id,
            },
            "target": target,
        })
        response.raise_for_status()
        data = response.json()
    return {
        "deployment_id": data["id"],
        "url": data.get("url"),
        "ready_state": data.get("readyState", "QUEUED"),
        "inspector_url": data.get("inspectorUrl"),
    }

@mcp.tool()
def get_deployment_status(l2_agency_id: str, deployment_id: str) -> dict:
    """Check deployment build status."""
    token = _get_vercel_token(l2_agency_id)
    with httpx.Client(
        base_url="https://api.vercel.com",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15.0,
    ) as client:
        response = client.get(f"/v13/deployments/{deployment_id}")
        response.raise_for_status()
        data = response.json()
    return {
        "deployment_id": data["id"],
        "url": data.get("url"),
        "ready_state": data.get("readyState"),
        "alias": data.get("alias", []),
    }

@mcp.tool()
def get_preview_url(l2_agency_id: str, deployment_id: str) -> dict:
    """Get the preview URL for a deployment."""
    status = get_deployment_status(l2_agency_id, deployment_id)
    preview_url = f"https://{status['url']}" if status.get("url") else None
    return {
        "preview_url": preview_url,
        "ready": status["ready_state"] == "READY",
        "ready_state": status["ready_state"],
    }

@mcp.tool()
def list_deployments(
    l2_agency_id: str,
    project_id: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """List recent deployments."""
    token = _get_vercel_token(l2_agency_id)
    params = {"limit": limit}
    if project_id:
        params["projectId"] = project_id
    with httpx.Client(
        base_url="https://api.vercel.com",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15.0,
    ) as client:
        response = client.get("/v6/deployments", params=params)
        response.raise_for_status()
        data = response.json()
    return [
        {
            "id": d["uid"],
            "name": d["name"],
            "url": d.get("url"),
            "state": d.get("state"),
            "created": d.get("created"),
        }
        for d in data.get("deployments", [])
    ]
```

### MCP-GitHub: Core Tools
```python
# Source: PyGithub docs + existing MCP pattern
from github import Github, Auth
from fastmcp import FastMCP
from hazn_platform.core.vault import read_secret
from hazn_platform.core.models import VaultCredential

mcp = FastMCP("hazn-github")

def _get_github_client(l2_agency_id: str) -> Github:
    """Create authenticated GitHub client for agency."""
    credential = VaultCredential.objects.get(
        agency_id=l2_agency_id,
        service_name="github",
    )
    secret = read_secret(credential.vault_secret_id)
    auth = Auth.Token(secret["token"])
    return Github(auth=auth)

@mcp.tool()
def create_repo(
    l2_agency_id: str,
    name: str,
    description: str = "",
    private: bool = True,
) -> dict:
    """Create a new GitHub repository under the agency's org."""
    g = _get_github_client(l2_agency_id)
    # Get org from vault credential metadata or use authenticated user
    user = g.get_user()
    repo = user.create_repo(
        name=name,
        description=description,
        private=private,
        auto_init=True,
    )
    return {
        "id": repo.id,
        "full_name": repo.full_name,
        "clone_url": repo.clone_url,
        "html_url": repo.html_url,
    }

@mcp.tool()
def create_pr(
    l2_agency_id: str,
    repo_full_name: str,
    title: str,
    head: str,
    base: str = "main",
    body: str = "",
) -> dict:
    """Create a pull request."""
    g = _get_github_client(l2_agency_id)
    repo = g.get_repo(repo_full_name)
    pr = repo.create_pull(title=title, head=head, base=base, body=body)
    return {
        "number": pr.number,
        "html_url": pr.html_url,
        "state": pr.state,
        "mergeable": pr.mergeable,
    }

@mcp.tool()
def get_ci_status(
    l2_agency_id: str,
    repo_full_name: str,
    ref: str = "HEAD",
) -> dict:
    """Get CI check status for a ref (branch, SHA, or tag)."""
    g = _get_github_client(l2_agency_id)
    repo = g.get_repo(repo_full_name)
    commit = repo.get_commit(ref)
    check_runs = commit.get_check_runs()
    return {
        "ref": ref,
        "sha": commit.sha,
        "checks": [
            {
                "name": cr.name,
                "status": cr.status,
                "conclusion": cr.conclusion,
            }
            for cr in check_runs
        ],
        "combined_status": commit.get_combined_status().state,
    }
```

### MCP-Analytics: GA4 with Service Account
```python
# Source: Google Analytics Data API docs + existing ga4_collector.py
import json
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, OrderBy, RunReportRequest
)
from google.oauth2 import service_account
from fastmcp import FastMCP
from hazn_platform.core.vault import read_secret
from hazn_platform.core.models import VaultCredential

mcp = FastMCP("hazn-analytics")

def _get_ga4_client(l2_agency_id: str, l3_client_id: str) -> BetaAnalyticsDataClient:
    """Create GA4 client from Vault service account."""
    credential = VaultCredential.objects.get(
        end_client_id=l3_client_id,
        service_name="ga4",
    )
    sa_json = read_secret(credential.vault_secret_id)
    credentials = service_account.Credentials.from_service_account_info(
        sa_json,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
    return BetaAnalyticsDataClient(credentials=credentials)

@mcp.tool()
def pull_ga4_data(
    l2_agency_id: str,
    l3_client_id: str,
    property_id: str,
    days: int = 30,
) -> dict:
    """Pull GA4 analytics data for a property.

    Returns traffic, events, conversions, and landing page data.
    """
    client = _get_ga4_client(l2_agency_id, l3_client_id)
    # Reuse proven logic from ga4_collector.py but with
    # service account instead of OAuth2
    # ... (adapted from existing collect_all function)
```

### Langfuse Tracing Integration
```python
# Source: Langfuse v3 SDK docs
# orchestrator/tracing.py -- NEW module

from __future__ import annotations
import logging
from contextlib import contextmanager
from langfuse import get_client, propagate_attributes

logger = logging.getLogger(__name__)

def init_langfuse():
    """Initialize and verify Langfuse connection.

    Reads from Django settings (LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY,
    LANGFUSE_HOST) which are loaded from environment variables.

    Call once at Django startup or in Celery worker init.
    """
    langfuse = get_client()
    if langfuse.auth_check():
        logger.info("Langfuse client authenticated successfully")
    else:
        logger.warning("Langfuse auth check failed -- tracing disabled")

@contextmanager
def trace_workflow(workflow_run):
    """Context manager that creates a Langfuse trace for a workflow run.

    Sets up: trace span, propagated attributes (tags, metadata),
    bidirectional linking (trace_id stored on WorkflowRun).

    Yields the Langfuse client for creating child spans.
    """
    langfuse = get_client()

    with langfuse.start_as_current_observation(
        as_type="span",
        name=f"workflow-{workflow_run.workflow_name}",
    ):
        with propagate_attributes(
            user_id=str(workflow_run.agency_id),
            session_id=str(workflow_run.pk),
            tags=[
                f"l2:{workflow_run.agency_id}",
                f"l3:{workflow_run.end_client_id}",
                f"run:{workflow_run.pk}",
            ],
            metadata={
                "l2_client_id": str(workflow_run.agency_id),
                "l3_client_id": str(workflow_run.end_client_id),
                "workflow_run_id": str(workflow_run.pk),
                "workflow_name": workflow_run.workflow_name,
            },
        ):
            # Store trace_id on WorkflowRun for bidirectional linking
            trace_id = langfuse.get_current_trace_id()
            workflow_run.langfuse_trace_id = trace_id
            workflow_run.save(update_fields=["langfuse_trace_id"])

            yield langfuse

@contextmanager
def trace_phase(phase_id: str):
    """Context manager for a workflow phase span."""
    langfuse = get_client()
    with langfuse.start_as_current_observation(
        as_type="span",
        name=f"phase-{phase_id}",
    ):
        yield langfuse

@contextmanager
def trace_tool_call(tool_name: str):
    """Context manager for an MCP tool call span."""
    langfuse = get_client()
    with langfuse.start_as_current_observation(
        as_type="span",
        name=f"tool-{tool_name}",
        metadata={"tool_name": tool_name},
    ) as span:
        yield span
```

### Conflict Detection with Real LLM Call
```python
# Source: OpenAI API + Langfuse drop-in
# Replace stub in orchestrator/conflict_detector.py

import json
from langfuse.openai import openai  # drop-in for auto-tracing

def run_conflict_check_llm(
    locked_rules: list[dict],
    brand_voice_content: str,
) -> list[dict]:
    """Compare locked rules against brand voice using gpt-4o-mini.

    Returns list of detected conflicts with rule, description, severity.
    Uses gpt-4o-mini for cost efficiency (~$0.001 per conflict check).
    Langfuse auto-traces via drop-in import.
    """
    rules_text = json.dumps(locked_rules, indent=2)

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a brand compliance checker. Compare agency locked rules "
                    "against client brand voice. Identify conflicts where the rules "
                    "contradict or restrict the brand voice.\n\n"
                    "Return a JSON array of conflicts. Each conflict has:\n"
                    '- "rule": the locked rule text\n'
                    '- "conflict_description": what specifically conflicts\n'
                    '- "severity": "hard" (legal/compliance) or "soft" (style preference)\n\n'
                    "If no conflicts, return an empty array []."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"## Agency Locked Rules\n{rules_text}\n\n"
                    f"## Client Brand Voice\n{brand_voice_content}"
                ),
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
        max_tokens=1000,
    )

    try:
        result = json.loads(response.choices[0].message.content)
        # Handle both {"conflicts": [...]} and direct [...]
        if isinstance(result, dict):
            return result.get("conflicts", [])
        return result if isinstance(result, list) else []
    except (json.JSONDecodeError, IndexError, KeyError):
        return []
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Langfuse v2 decorator-only | Langfuse v3 OTel-based with context managers | June 2025 | `get_client()` singleton, `start_as_current_observation()`, `propagate_attributes()` replace decorator-heavy patterns |
| OAuth2 interactive flow for GA4/GSC | Service account with from_service_account_info() | Standard practice | No interactive login, per-tenant isolation, Vault-compatible |
| Vercel Deploy API v6 | v13 POST /v13/deployments | Current | Supports gitSource, file uploads, target environments |
| PyGithub Auth.Token | PyGithub Auth.Token (unchanged) | 2.x | Typed auth since PyGithub 2.0 |

**Deprecated/outdated:**
- Langfuse v2 `@observe()` decorator still works but v3 context manager pattern is preferred for better async support
- `google-auth-oauthlib` interactive flow: not suitable for server-to-server auth; use `google-auth` service accounts
- Vercel API v6 for creating deployments: superseded by v13 (v6 still works for listing)

## Discretion Recommendations

### Tool Call Metering Approach
**Recommendation: Direct instrumentation in executor, NOT extraction from Langfuse.**

Rationale: Extracting from Langfuse would create a dependency on Langfuse being available/responsive for billing data. Per PROJECT.md, "Postgres workflow_runs is billing source of truth." Add `on_tool_call(tool_name, latency_ms, success)` to MeteringCallback and instrument at the executor level when it invokes MCP tools.

### Exact Langfuse SDK Integration Pattern
**Recommendation: Context managers (`start_as_current_observation`) over decorators.**

Rationale: The executor already uses async context (`async def run()`). Context managers give explicit control over span lifecycle and work better with `sync_to_async` boundaries. Decorators hide the trace structure and can lose context in thread transitions. Create a `tracing.py` module with `trace_workflow()`, `trace_phase()`, `trace_tool_call()` context managers.

### MCP Server Error Handling and Retry Patterns
**Recommendation: Return error dicts, do NOT retry in MCP tools.**

Rationale: MCP tools should be idempotent and fast. If a Vercel deploy fails, return `{"error": "...", "status_code": 429}` and let the agent decide whether to retry. For transient failures (rate limits), include `retry_after` in the response. The orchestrator/agent handles retry logic, not the tool server.

Error format for all MCP tools:
```python
{"error": str, "status_code": int | None, "retry_after": int | None}
```

### Conflict Detection Prompt Design
**Recommendation: Structured JSON output with temperature=0, response_format=json_object.**

Keep the prompt focused: system message defines the task and output schema, user message provides the two inputs (locked rules + brand voice). Use `response_format={"type": "json_object"}` for reliable JSON parsing. See Code Examples section for full prompt.

## Open Questions

1. **Langfuse Docker Service**
   - What we know: Langfuse env vars (LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST) are defined in `base.py` but no Langfuse service in `docker-compose.local.yml`. CONTEXT.md says "Langfuse self-hosted and deployed -- existing infrastructure."
   - What's unclear: Is Langfuse running externally (cloud or separate server)? Does it need to be added to docker-compose?
   - Recommendation: Check if LANGFUSE_HOST points to an external instance. If not, add Langfuse service to docker-compose. The code should work either way since it reads from env vars.

2. **VaultCredential Lookup Pattern for Agency-Level Credentials**
   - What we know: Existing `get_credentials` MCP tool queries `VaultCredential.objects.get(end_client_id=..., service_name=...)`. Vercel/GitHub credentials are scoped per L2 agency, not L3 client.
   - What's unclear: VaultCredential model has both `agency` and `end_client` FKs (nullable). Need to verify the agency-level lookup path.
   - Recommendation: Use `VaultCredential.objects.get(agency_id=l2_agency_id, service_name="vercel", end_client__isnull=True)` for agency-scoped credentials. Add a helper function in the MCP server for this pattern.

3. **Langfuse Context Across sync_to_async Boundary**
   - What we know: The executor uses `sync_to_async` heavily. Langfuse v3 uses contextvars which may not propagate across thread boundaries.
   - What's unclear: Whether Django's `sync_to_async` implementation preserves contextvars (asyncio.run_in_executor does NOT by default).
   - Recommendation: Test context propagation early. If broken, capture trace_id before the boundary and use explicit parent linking via `langfuse.start_observation(parent_observation_id=...)`.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 + pytest-django 4.12.0 |
| Config file | `hazn_platform/pyproject.toml` |
| Quick run command | `cd hazn_platform && python -m pytest tests/ -x -q --no-header` |
| Full suite command | `cd hazn_platform && python -m pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MCP-02 | mcp-vercel deploy, preview, list, status tools | unit | `pytest tests/test_mcp_vercel_server.py -x` | Wave 0 |
| MCP-03 | mcp-github create_repo, create_pr, get_ci_status tools | unit | `pytest tests/test_mcp_github_server.py -x` | Wave 0 |
| MCP-04 | mcp-analytics GA4 + GSC tools return data | unit | `pytest tests/test_mcp_analytics_server.py -x` | Wave 0 |
| MCP-05 | mcp-analytics PageSpeed tool returns CWV | unit | `pytest tests/test_mcp_analytics_server.py::TestPageSpeed -x` | Wave 0 |
| OBS-01 | Langfuse traces LLM calls with correct tags | unit | `pytest tests/test_tracing.py -x` | Wave 0 |
| OBS-02 | WorkflowRun has langfuse_trace_id field | unit | `pytest tests/test_orchestrator_models.py -x` | Extends existing |
| OBS-03 | WorkflowAgent tracks per-agent data | unit | `pytest tests/test_metering.py -x` | Existing |
| OBS-04 | WorkflowToolCall populated on tool use | unit | `pytest tests/test_metering.py::TestToolCallMetering -x` | Wave 0 |
| OBS-05 | Runaway alerts create HITL + Langfuse event | unit | `pytest tests/test_metering.py::TestRunawayAlerts -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `cd hazn_platform && python -m pytest tests/ -x -q --no-header`
- **Per wave merge:** `cd hazn_platform && python -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_mcp_vercel_server.py` -- covers MCP-02
- [ ] `tests/test_mcp_github_server.py` -- covers MCP-03
- [ ] `tests/test_mcp_analytics_server.py` -- covers MCP-04, MCP-05
- [ ] `tests/test_tracing.py` -- covers OBS-01, OBS-05
- [ ] Test additions to `tests/test_metering.py` for tool call metering (OBS-04)
- [ ] All external API calls mocked (httpx, PyGithub, Google clients, OpenAI, Langfuse)

## Sources

### Primary (HIGH confidence)
- [Langfuse v3 Python SDK docs](https://langfuse.com/docs/observability/sdk/python/overview) - setup, context managers, propagate_attributes
- [Langfuse v3 changelog](https://langfuse.com/changelog/2025-06-05-python-sdk-v3-generally-available) - v3 GA announcement, OTel foundation, migration from v2
- [Langfuse decorator docs](https://langfuse.com/docs/sdk/python/decorators) - @observe, generation types, context retrieval
- [Langfuse OpenAI integration](https://langfuse.com/integrations/model-providers/openai-py) - drop-in replacement import
- [Vercel REST API - Create Deployment](https://vercel.com/docs/rest-api/deployments/create-a-new-deployment) - POST /v13/deployments, request/response schema
- [Vercel REST API - List Deployments](https://vercel.com/docs/rest-api/deployments/list-deployments) - GET /v6/deployments, response fields
- [PyGithub docs](https://pygithub.readthedocs.io/en/latest/) - PullRequest, Repository, Commit examples
- [Google Analytics Data API quickstart](https://developers.google.com/analytics/devguides/reporting/data/v1/quickstart) - BetaAnalyticsDataClient, service account auth
- Existing codebase: `mcp_servers/hazn_memory_server.py`, `orchestrator/metering.py`, `orchestrator/conflict_detector.py`, `orchestrator/session.py`, `orchestrator/executor.py`, `orchestrator/models.py`, `config/settings/base.py`
- Existing analytics scripts: `hazn/scripts/analytics-audit/ga4_collector.py`, `gsc_collector.py`, `pagespeed_collector.py`

### Secondary (MEDIUM confidence)
- [PyGithub PyPI](https://pypi.org/project/PyGithub/) - v2.8.1, Python >=3.8
- [Langfuse PyPI](https://pypi.org/project/langfuse/) - v3.14.5, Python >=3.10
- [Vercel API authentication guide](https://vercel.com/guides/how-do-i-use-a-vercel-api-access-token) - Bearer token pattern

### Tertiary (LOW confidence)
- None -- all findings verified against official docs or existing codebase

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified against official docs; versions confirmed on PyPI; existing codebase patterns validate approach
- Architecture: HIGH - Three new MCP servers follow exact pattern of existing hazn_memory_server.py; Langfuse v3 API verified against official docs
- Pitfalls: HIGH - Context propagation across sync_to_async is a known Python limitation; GA4 scope issues from direct code inspection; Vercel async deploy from API docs

**Research date:** 2026-03-06
**Valid until:** 2026-04-06 (30 days -- stable ecosystem, all libraries are mature)

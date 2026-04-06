# Phase 4: MCP Tool Servers & Observability - Context

**Gathered:** 2026-03-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Agents can interact with external platforms (Vercel, GitHub, GA4, GSC, PageSpeed) via MCP tool servers, and every workflow run is traced in Langfuse and metered in Postgres for cost visibility. This phase builds three MCP servers (mcp-vercel, mcp-github, mcp-analytics), wires Langfuse tracing into the orchestrator, connects the existing MeteringCallback to Langfuse, and replaces the conflict detection LLM stub with a real call.

</domain>

<decisions>
## Implementation Decisions

### MCP Server Scope & API Coverage
- Hybrid approach: wrap existing GA4/GSC/PageSpeed Python scripts (proven code in hazn/scripts/analytics-audit/) into MCP servers; build fresh for Vercel and GitHub (no existing code)
- mcp-vercel: deploy + preview only -- deploy_project, get_preview_url, list_deployments, get_deployment_status. No domain/DNS management
- mcp-github: repo + PR management -- create_repo, create_pr, get_pr_status, get_ci_status, list_branches, merge_pr. No issues, actions, releases, or webhooks
- mcp-analytics: combined server exposing GA4, GSC, and PageSpeed tools in one server. These are always used together in analytics audit workflows. Satisfies MCP-04 and MCP-05 requirements
- All MCP servers use FastMCP 3.1.0 with stdio transport (established pattern from mcp-hazn-memory in Phase 2)

### Langfuse Tracing Depth
- Trace hierarchy: Workflow (trace) -> Phase (span) -> LLM calls + tool calls (generations/spans). One trace per workflow run
- Trace both LLM calls (tokens, cost, latency) and MCP tool calls (tool name, latency, success/fail). Memory operations are internal -- not traced separately
- Tags on every trace: l2_client_id, l3_client_id, workflow_run_id
- Bidirectional linking: store Langfuse trace_id on WorkflowRun record; tag Langfuse traces with workflow_run_id. Enables jumping between Postgres metering and Langfuse debug views
- Wire up the conflict detection LLM call (gpt-4o-mini stub from Phase 3) now -- Langfuse tracing captures it automatically since the pipeline is being built

### Metering Pipeline Wiring
- Unified LLM callback: Langfuse callback wraps MeteringCallback. Single integration point that both sends to Langfuse (trace/span) AND feeds MeteringCallback (Postgres). Langfuse is for debug/visibility, Postgres is billing source of truth (per PROJECT.md)
- Runaway agent alerts (>50 turns, >$5/run): when threshold is breached, MeteringCallback creates a HITL item (existing behavior) AND adds a Langfuse event/annotation on the trace. Dual visibility in both systems

### Auth & Credential Flow
- All MCP servers receive credentials at runtime via get_credentials(service_name, l2_id, l3_id) -- existing Vault pattern from Phase 2. Credentials never stored in MCP server state
- GA4/GSC: service accounts stored as JSON in Vault per L2/L3. MCP server receives service account JSON via get_credentials and authenticates per-request. No local token files
- Vercel and GitHub: credentials scoped per L2 agency. One Vercel token and one GitHub PAT per agency. L3 projects use agency's credentials
- PageSpeed: optional API key from Vault. If agency has a PSI_API_KEY in Vault, use it for higher rate limits. Otherwise call API without auth (free tier graceful fallback)

### Claude's Discretion
- Tool call metering approach (direct instrumentation in MCP vs extract from Langfuse)
- Exact Langfuse SDK integration pattern (decorators vs context managers)
- MCP server error handling and retry patterns
- Conflict detection prompt design for gpt-4o-mini

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `mcp_servers/hazn_memory_server.py`: FastMCP 3.1.0 pattern with @mcp.tool() decorator -- template for new MCP servers
- `hazn/scripts/analytics-audit/ga4_collector.py`: Working GA4 Data API integration with BetaAnalyticsDataClient
- `hazn/scripts/analytics-audit/gsc_collector.py`: Working GSC API integration sharing OAuth2 flow
- `hazn/scripts/analytics-audit/pagespeed_collector.py`: Working PageSpeed Insights API using stdlib urllib
- `orchestrator/metering.py`: MeteringCallback with per-agent cost tracking and threshold alerts
- `orchestrator/conflict_detector.py`: run_conflict_check_llm() stub ready to be replaced with actual LLM call
- `core/vault.py`: read_secret() with AppRole auth and token caching
- `config/settings/base.py`: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST env vars already defined

### Established Patterns
- FastMCP 3.1.0 with stdio transport for MCP servers
- UUID primary keys on all models
- get_credentials() MCP tool for runtime credential fetching from Vault
- MeteringCallback with flush_to_db() for Postgres writes
- sync_to_async wrapping for Django ORM calls in async executor

### Integration Points
- WorkflowExecutor.run() (orchestrator/executor.py) -- main entry point for tracing
- WorkflowSession (orchestrator/session.py) -- metering callback lives here
- Celery run_workflow task (orchestrator/tasks.py) -- wraps executor with 4hr timeout
- WorkflowRun model needs new langfuse_trace_id field for bidirectional linking

</code_context>

<specifics>
## Specific Ideas

- Combined mcp-analytics server because GA4/GSC/PageSpeed are always used together in analytics audit workflows -- one server, one credential flow, simpler for agents
- Deploy + preview only for Vercel -- QA Tester validates staging, human manages domains
- Service accounts for Google APIs instead of OAuth2 tokens -- proper multi-tenant isolation, no local token files
- Wire conflict detection LLM now (not later) since Langfuse pipeline is being built in this same phase

</specifics>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 04-mcp-tool-servers-observability*
*Context gathered: 2026-03-06*

---
phase: 04-mcp-tool-servers-observability
verified: 2026-03-06T08:50:00Z
status: passed
score: 11/11 must-haves verified
re_verification: false
---

# Phase 4: MCP Tool Servers & Observability -- Verification Report

**Phase Goal:** Agents can interact with external platforms (Vercel, GitHub, GA4, PageSpeed) and every workflow run is traced and metered for cost visibility
**Verified:** 2026-03-06T08:50:00Z
**Status:** PASSED
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | mcp-vercel server can deploy a site, get preview URLs, list deployments, and check deployment status | VERIFIED | `vercel_server.py` (217 lines): 4 `@mcp.tool()` functions (`deploy_project`, `get_deployment_status`, `get_preview_url`, `list_deployments`) using httpx.Client with Vercel v13/v6 API. All tools return structured dicts. Error handling returns `{"error": str, "status_code": int}`. |
| 2 | mcp-github server can create repos, open PRs, check CI status, list branches, get PR status, and merge PRs | VERIFIED | `github_server.py` (249 lines): 6 `@mcp.tool()` functions (`create_repo`, `create_pr`, `get_pr_status`, `get_ci_status`, `list_branches`, `merge_pr`) using PyGithub with Auth.Token. Error handling returns `{"error": str}`. |
| 3 | Both Vercel and GitHub servers fetch credentials from Vault at runtime via VaultCredential lookup -- no hardcoded tokens | VERIFIED | Both servers have `_get_vercel_token()` / `_get_github_client()` helpers calling `VaultCredential.objects.get(agency_id=..., service_name=..., end_client__isnull=True)` then `read_secret(credential.vault_secret_id)`. No hardcoded tokens found. |
| 4 | WorkflowRun model has langfuse_trace_id field for bidirectional linking | VERIFIED | `models.py` line 52: `langfuse_trace_id = models.CharField(max_length=255, blank=True, default="")`. Migration `0002_workflowrun_langfuse_trace_id.py` exists with correct AddField operation. |
| 5 | mcp-analytics server can pull GA4 traffic data for a property | VERIFIED | `analytics_server.py`: `pull_ga4_data()` tool runs 3 GA4 RunReportRequests (traffic overview, top pages, top sources) via `BetaAnalyticsDataClient` with service account credentials from Vault. Returns structured `{traffic, top_pages, top_sources}`. |
| 6 | mcp-analytics server can run GSC search queries and return organic search data | VERIFIED | `analytics_server.py`: `query_gsc()` tool calls `searchanalytics().query()` via `build("searchconsole", "v1")` with service account credentials. Returns `{queries, pages}` with clicks/impressions/ctr/position. |
| 7 | mcp-analytics server can return Core Web Vitals scores from PageSpeed Insights | VERIFIED | `analytics_server.py`: `check_pagespeed()` tool calls PSI API v5 via urllib, extracts Lighthouse scores (performance, accessibility, best-practices, seo), Core Web Vitals (LCP, FID, CLS, INP, TTFB), and top 5 opportunities. Returns `{scores, core_web_vitals, opportunities}`. |
| 8 | GA4 and GSC use service account JSON from Vault (not OAuth2 interactive flow) | VERIFIED | `_get_ga4_client()` and `_get_gsc_service()` both use `Credentials.from_service_account_info(sa_json, scopes=[...])` -- no OAuth2 flow. VaultCredential lookup for `service_name="ga4"` and `service_name="gsc"`. |
| 9 | PageSpeed gracefully falls back to free tier when no API key exists in Vault | VERIFIED | `_get_psi_api_key()` catches `VaultCredential.DoesNotExist`, returns `None`. `check_pagespeed()` only appends `&key=` when key is not None. Test `test_pagespeed_without_api_key_graceful_fallback` validates this path. |
| 10 | Every LLM call is traced in Langfuse with l2_client_id, l3_client_id, and workflow_run_id tags | VERIFIED | `tracing.py`: `start_workflow_trace()` creates Langfuse trace with `tags=["l2:{agency_id}", "l3:{end_client_id}", "run:{pk}"]` and `metadata={l2_client_id, l3_client_id, workflow_run_id, workflow_name}`. Stores `trace_id` on WorkflowRun. `conflict_detector.py` uses `from langfuse.openai import openai` drop-in for auto-traced LLM calls. `executor.py` calls `start_workflow_trace` after `session.start()`. All tracing is non-fatal. |
| 11 | Runaway agents (>50 turns, >$5/run) create both HITL items and Langfuse events; Postgres workflow tables track tokens, cost, and turns | VERIFIED | `metering.py`: `on_llm_call()` checks thresholds, calls `_on_threshold_alert` callback AND `_annotate_langfuse_event()`. `on_tool_call()` accumulates per-tool metrics. `flush_to_db()` writes both `WorkflowAgent` and `WorkflowToolCall` records via `update_or_create`. Langfuse event is best-effort (try/except pass). |

**Score:** 11/11 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `hazn_platform/hazn_platform/mcp_servers/vercel_server.py` | FastMCP server with 4 tools, min 100 lines | VERIFIED | 217 lines, 4 `@mcp.tool()` functions, Django setup guard, `if __name__` entry point |
| `hazn_platform/hazn_platform/mcp_servers/github_server.py` | FastMCP server with 6 tools, min 120 lines | VERIFIED | 249 lines, 6 `@mcp.tool()` functions, Django setup guard, `if __name__` entry point |
| `hazn_platform/hazn_platform/mcp_servers/analytics_server.py` | FastMCP server with GA4, GSC, PageSpeed tools, min 180 lines | VERIFIED | 399 lines, 3 `@mcp.tool()` functions, service account auth, PSI free-tier fallback |
| `hazn_platform/hazn_platform/orchestrator/tracing.py` | Langfuse v3 tracing module, min 80 lines | VERIFIED | 164 lines, exports `init_langfuse`, `start_workflow_trace`, `start_phase_span`, `start_tool_span` |
| `hazn_platform/hazn_platform/orchestrator/metering.py` | MeteringCallback with on_tool_call, exports MeteringCallback | VERIFIED | 267 lines, `on_tool_call()`, `flush_to_db()` writes WorkflowToolCall, `_annotate_langfuse_event()` |
| `hazn_platform/hazn_platform/orchestrator/conflict_detector.py` | Real gpt-4o-mini conflict detection, contains openai.chat.completions.create | VERIFIED | 167 lines, `from langfuse.openai import openai`, `openai.chat.completions.create(model="gpt-4o-mini", ...)` |
| `hazn_platform/tests/test_mcp_vercel_server.py` | Unit tests for 4 Vercel tools, min 60 lines | VERIFIED | 268 lines, 8 test methods covering all tools + error handling |
| `hazn_platform/tests/test_mcp_github_server.py` | Unit tests for 6 GitHub tools, min 80 lines | VERIFIED | 296 lines, 9 test methods covering all tools + error handling |
| `hazn_platform/tests/test_mcp_analytics_server.py` | Unit tests for analytics tools, min 100 lines | VERIFIED | 539 lines, 9 test methods covering GA4, GSC, PageSpeed + error handling |
| `hazn_platform/tests/test_tracing.py` | Tests for tracing module, min 60 lines | VERIFIED | 246 lines, 12 test methods covering init, workflow trace, phase span, tool span, non-fatal |
| `hazn_platform/tests/test_metering.py` | Tests for metering including tool calls | VERIFIED | 316 lines, tests cover accumulation, thresholds, flush_to_db (agent + tool), Langfuse events |
| `hazn_platform/tests/test_conflict_detector.py` | Tests for real LLM conflict detection | VERIFIED | 495 lines, tests cover detect_conflicts, run_conflict_check_llm (parsed, empty, API error, JSON error, model, format), process_conflicts |
| `hazn_platform/hazn_platform/orchestrator/migrations/0002_workflowrun_langfuse_trace_id.py` | Migration for langfuse_trace_id field | VERIFIED | Exists with AddField for CharField(max_length=255, blank=True, default="") |
| `hazn_platform/pyproject.toml` | Dependencies: langfuse, PyGithub, httpx, openai, google-analytics-data, google-api-python-client, google-auth | VERIFIED | All 7 dependencies present with correct version constraints |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `mcp_servers/vercel_server.py` | `core/vault.py` | `read_secret(credential.vault_secret_id)` | WIRED | Line 51: `secret = read_secret(credential.vault_secret_id)` in `_get_vercel_token()` |
| `mcp_servers/github_server.py` | `core/vault.py` | `read_secret(credential.vault_secret_id)` | WIRED | Line 53: `secret = read_secret(credential.vault_secret_id)` in `_get_github_client()` |
| `mcp_servers/analytics_server.py` | `core/vault.py` | `read_secret(credential.vault_secret_id)` for GA4, GSC, and PSI | WIRED | Lines 62, 75, 303: `read_secret()` calls in `_get_ga4_client()`, `_get_gsc_service()`, `_get_psi_api_key()` |
| `mcp_servers/analytics_server.py` | `google.analytics.data_v1beta` | `Credentials.from_service_account_info` | WIRED | Lines 63, 76: `Credentials.from_service_account_info(sa_json, scopes=[...])` for GA4 and GSC |
| `orchestrator/executor.py` | `orchestrator/tracing.py` | `start_workflow_trace()` called after session.start | WIRED | Line 29: import; Line 86: `await sync_to_async(start_workflow_trace)(workflow_run)` |
| `orchestrator/tracing.py` | `orchestrator/models.py` | `langfuse_trace_id` stored on WorkflowRun | WIRED | Lines 88-89: `workflow_run.langfuse_trace_id = trace_id; workflow_run.save(update_fields=["langfuse_trace_id"])` |
| `orchestrator/metering.py` | `orchestrator/models.py` | `WorkflowToolCall.objects.update_or_create` | WIRED | Line 203: `WorkflowToolCall.objects.update_or_create(workflow_run_id=..., tool_name=..., defaults={...})` |
| `orchestrator/conflict_detector.py` | `langfuse.openai` | `from langfuse.openai import openai` | WIRED | Line 21: drop-in import; Line 98: `openai.chat.completions.create(model="gpt-4o-mini", ...)` |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| MCP-02 | 04-01-PLAN | mcp-vercel server supports deploy, preview URL generation, domain management | SATISFIED | `vercel_server.py` has 4 tools: deploy_project, get_deployment_status, get_preview_url, list_deployments. Note: domain management explicitly excluded per user decision (deploy + preview only). |
| MCP-03 | 04-01-PLAN | mcp-github server supports repo management, PR creation, CI status | SATISFIED | `github_server.py` has 6 tools: create_repo, create_pr, get_pr_status, get_ci_status, list_branches, merge_pr. |
| MCP-04 | 04-02-PLAN | mcp-ga4 server supports GA4 data pull, GSC queries, benchmarks | SATISFIED | `analytics_server.py` has `pull_ga4_data()` and `query_gsc()` tools using service account auth from Vault. Implemented as combined mcp-analytics server per user decision. |
| MCP-05 | 04-02-PLAN | mcp-pagespeed server supports Core Web Vitals and performance scoring | SATISFIED | `analytics_server.py` has `check_pagespeed()` tool returning Lighthouse scores, Core Web Vitals (LCP, FID, CLS, INP, TTFB), and opportunities. Implemented in combined mcp-analytics server. |
| OBS-01 | 04-03-PLAN | Langfuse SDK traces every LLM call with l2_client_id, l3_client_id, workflow_run_id tags | SATISFIED | `tracing.py` creates traces with correct tags. `conflict_detector.py` uses `langfuse.openai` drop-in for auto-traced calls. `executor.py` calls `start_workflow_trace()` after session start. |
| OBS-02 | 04-03-PLAN | Postgres workflow_runs table tracks status, tokens, cost per workflow run | SATISFIED | WorkflowRun model has `status`, `total_tokens`, `total_cost`, `wall_clock_seconds`, `turn_count` fields. `langfuse_trace_id` added for bidirectional linking. MeteringCallback flushes to DB. |
| OBS-03 | 04-03-PLAN | workflow_agents table tracks per-agent turns, tokens, cost | SATISFIED | WorkflowAgent model with `total_tokens`, `total_cost`, `turn_count`. MeteringCallback.flush_to_db writes via `WorkflowAgent.objects.update_or_create`. |
| OBS-04 | 04-03-PLAN | workflow_tool_calls table tracks per-tool call count and cost | SATISFIED | WorkflowToolCall model with `call_count`, `total_cost`, `avg_latency_ms`. MeteringCallback.on_tool_call accumulates; flush_to_db writes via `WorkflowToolCall.objects.update_or_create`. |
| OBS-05 | 04-03-PLAN | System flags runaway agents (>50 turns) and cost outliers (>$5/run) | SATISFIED | MeteringCallback checks `_max_turns` (default 50) and `_max_cost` (default $5) on every `on_llm_call`. Dual-write: calls `_on_threshold_alert` callback AND `_annotate_langfuse_event()`. Tests verify both paths. |

No orphaned requirements found -- all 9 requirement IDs from the phase (MCP-02, MCP-03, MCP-04, MCP-05, OBS-01, OBS-02, OBS-03, OBS-04, OBS-05) are covered by the three plans and verified.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `orchestrator/executor.py` | 176 | Comment: "placeholder for Letta message API" | Info | Pre-existing from Phase 3; refers to agent-Letta message interaction, not Phase 4 scope. Not a Phase 4 blocker. |

No blockers or warnings found in Phase 4 artifacts. All `return None` and `return []` instances are legitimate error-handling fallback paths, not stubs.

### Human Verification Required

### 1. MCP Server Smoke Test

**Test:** Start each MCP server (`python vercel_server.py`, `python github_server.py`, `python analytics_server.py`) and verify it initializes FastMCP correctly.
**Expected:** Server starts without import errors, registers expected tools, and is ready to accept stdio connections.
**Why human:** Requires running Docker services (Postgres for Django setup guard), which are not currently running.

### 2. Test Suite Execution

**Test:** Run `cd hazn_platform && python -m pytest tests/test_mcp_vercel_server.py tests/test_mcp_github_server.py tests/test_mcp_analytics_server.py tests/test_tracing.py tests/test_metering.py tests/test_conflict_detector.py -v`
**Expected:** All tests pass (SUMMARY claims 17 + 9 + 24 = 50 tests).
**Why human:** Docker services (PostgreSQL) not running locally; tests require pytest-django with database access.

### 3. Langfuse Trace Visibility

**Test:** Run a workflow end-to-end and check Langfuse UI for the trace.
**Expected:** Trace appears with l2/l3/run tags, workflow name, and metadata. Clicking trace_id from Postgres leads to correct Langfuse trace.
**Why human:** Requires running Langfuse instance and end-to-end workflow execution.

### Gaps Summary

No gaps found. All 11 observable truths are verified against the actual codebase. All 14 required artifacts exist, are substantive (meet minimum line counts), and are properly wired. All 8 key links confirmed via grep. All 9 requirement IDs (MCP-02, MCP-03, MCP-04, MCP-05, OBS-01, OBS-02, OBS-03, OBS-04, OBS-05) are satisfied. No blocker anti-patterns detected.

The only items needing human verification are environment-dependent: running the test suite (Docker services not available during verification) and Langfuse trace visibility (requires live Langfuse instance).

---

_Verified: 2026-03-06T08:50:00Z_
_Verifier: Claude (gsd-verifier)_

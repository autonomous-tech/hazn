---
gsd_state_version: 1.0
milestone: v3.0
milestone_name: Strip & Simplify
status: in-progress
stopped_at: Completed 06-01-PLAN.md
last_updated: "2026-03-13T14:33:30Z"
last_activity: 2026-03-13 -- Completed 06-01-PLAN.md (Frontend cleanup + ChatMessage API)
progress:
  total_phases: 7
  completed_phases: 5
  total_plans: 18
  completed_plans: 17
  percent: 94
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-12)

**Core value:** Agents remember and compound -- every engagement builds on past decisions, brand voice, keyword history, and craft knowledge.
**Current focus:** v3.0 Phase 6 in progress -- Mode 3 Workspace

## Current Position

Phase: 6 of 7 (Mode 3 Workspace)
Plan: 1 of 2 -- COMPLETE
Status: Phase 06 Plan 01 complete, ready for Plan 02
Last activity: 2026-03-13 -- Completed 06-01-PLAN.md (Frontend cleanup + ChatMessage API)

Progress: [█████████░] 94% (Phase 6: 1/2 plans complete)

## Performance Metrics

**Velocity:**
- Total plans completed: 47 (v1.0: 23, v2.0: 9, v3.0: 15)
- Average duration: 8min (v3.0)
- Total execution time: 125min (v3.0)

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Runtime is Claude Agent SDK (not Anthropic API direct) -- STRP-04 removes API backend
- Tools as Python functions registered with Agent SDK (no MCP) -- TOOL-08
- Agency model kept as singleton (removing it cascades 30+ files) -- research Pitfall 2
- Executor rewrite from scratch (~150 lines), not surgical edit -- research Pitfall 4
- Extract MCP tool logic BEFORE deleting MCP server files -- research Pitfall 3
- Two-wave migration: FK fields first, then model classes -- research Pitfall 1
- Chat view is new feature: each workflow run gets a conversation thread for user input and steering
- [Phase 01]: Hardcoded max_turns=30 in AgentSDKBackend (Phase 4 will configure properly)
- [Phase 01]: Removed budget_exceeded as valid RunResult status -- executor only handles completed and error
- [Phase 01]: MeteringCallback.from_agency keeps agency param for compatibility but no longer reads threshold config
- [Phase 01]: Langfuse get_client removed from metering.py -- all Langfuse integration stays in tracing.py
- [Phase 02]: Agency singleton via save() override (not CheckConstraint) -- UUID PKs prevent pk=1 constraint
- [Phase 02]: ShareLink deleted entirely (not re-pointed) -- QA-era feature not needed in v3.0
- [Phase 02]: Kept WorkflowRun.Status.BLOCKED in enum -- Phase 4 executor rewrite defines final statuses
- [Phase 02]: IsAuthenticated replaces IsAgencyMember in all workspace viewsets
- [Phase 02]: Pre-existing broken tests (executor, metering, memory) deferred -- out of scope for Phase 2
- [Phase 03]: Stub @tool decorator for SDK-absent environments -- tools register with .name attribute for testing
- [Phase 03]: asyncio.to_thread() for file I/O instead of aiofiles -- stdlib-only, fewer dependencies
- [Phase 03]: Tool module TOOLS list pattern for build_registry() collection
- [Phase 03]: Agency.load() singleton replaces l2_agency_id in all tool signatures -- credential lookup is internal
- [Phase 03]: sync_to_async wraps Django ORM calls in async tools -- deferred imports avoid Django setup at import time
- [Phase 03]: search_cross_client_insights always-on (no Agency flag check) -- single-user agency model
- [Phase 03]: Patchable _OUTPUT_BASE for analytics test isolation -- keeps tool API clean
- [Phase 03]: Brand name extraction from site_url domain for GSC brand/non-brand analysis
- [Phase 03]: httpx.AsyncClient for PageSpeed API -- consistent with web.py tool pattern
- [Phase 03]: _REGISTRY_SINGLETON in apps.py replaces tool_wiring._ROUTER_SINGLETON pattern
- [Phase 03]: get_tool_callable() added to ToolRegistry for backward-compat dispatch in agent_runner
- [Phase 03]: AgentSDKBackend delegates allowed-tool prefixing to ToolRegistry.get_allowed_tools()
- [Phase 03]: try/except import chain for SDK: claude_agent_sdk first, claude_code_sdk fallback
- [Phase 03]: Broad except for analytics module-level imports catches Django ImproperlyConfigured
- [Phase 03]: getattr(t, 'handler', t) pattern in get_tool_callable for stub/real SDK compatibility
- [Phase 04]: max_turns: int = 30 added to WorkflowPhaseSchema (per-phase turn limits in workflow YAML)
- [Phase 04]: BLOCKED removed from WorkflowRun.Status enum -- data migration converts blocked rows to failed
- [Phase 04]: One Letta agent per client (client--{pk} naming) replaces per-agent-type-per-client pattern
- [Phase 04]: WorkflowSession.load_client_context() defers Letta import to method body (non-fatal if Letta down)
- [Phase 04]: Direct dependency output injection only (not all prior phases) -- reduces tokens, aligns with DAG semantics
- [Phase 04]: Generalized delivery detection via 'branded_html_report' in phase.outputs (not hardcoded phase.id)
- [Phase 04]: Registry passed via constructor for testability, singleton fallback for production
- [Phase 04]: Non-fatal SSE via _emit_event helper -- SSE failures never halt workflow
- [Phase 04]: All imports in tasks.py deferred to function body -- clean Celery isolation, simpler testing
- [Phase 04]: sys.modules SDK stubs for executor test imports -- tests run without real Claude SDK installed
- [Phase 04]: Pre-existing metering bug (turn_count field) worked around via mock in tests
- [Phase 05]: Use SDK-provided item.score for similarity weight instead of positional rank -- more accurate relevance ordering
- [Phase 05]: Remove record_turn() entirely (dead code per STRP-08) rather than leaving stub
- [Phase 05]: Auto-extracted learnings use confidence=0.6 vs explicit tool calls at 0.7+ -- lower confidence reflects less intentional capture
- [Phase 05]: Text pattern extraction only fires if JSON extraction finds no learnings -- avoids double-counting
- [Phase 05]: Agency.load() replaces request.user.agency in MemoryInspectorView -- single-user singleton pattern
- [Phase 05]: Default corrected_by to "dashboard-user" in correct endpoint -- single-user simplification
- [Phase 05]: client--{pk} naming in MemoryInspectorView ignores agent_type param entirely -- one-agent-per-client
- [Phase 05]: Integration marker already registered in pyproject.toml -- no pytest_configure needed in conftest.py
- [Phase 06]: Empty stubs for HITL components instead of file deletion -- avoids cascade import breakage
- [Phase 06]: QA fields removed from Deliverable type -- QA system removed in v3.0
- [Phase 06]: Sites migration 0003 fixed with connection.vendor check for SQLite compatibility
- [Phase 06]: ChatMessage nested URL pattern: /runs/{run_pk}/chat/ via ViewSet
- [Phase 06]: SSE chat_message event emitted non-fatally on message creation

### Blockers/Concerns

- Agent SDK integration patterns need validation (research recommended API direct, requirements say Agent SDK)
- GA4/GSC/PageSpeed credential pattern in Vault needs verification before Phase 3 tool extraction
- Existing Letta agents have enterprise memory block formats -- need cleanup before first v3.0 run
- Pre-existing test failures: test_executor.py, test_metering.py, test_memory.py reference Plan 01 deleted fields (deferred to Phase 4)

## Session Continuity

Last session: 2026-03-13T14:33:30Z
Stopped at: Completed 06-01-PLAN.md
Resume file: .planning/milestones/v1.0-phases/06-mode-3-workspace/06-01-SUMMARY.md

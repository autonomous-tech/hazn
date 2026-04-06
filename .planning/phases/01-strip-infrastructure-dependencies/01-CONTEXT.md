# Phase 1: Strip Infrastructure & Dependencies - Context

**Gathered:** 2026-03-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Remove enterprise runtime code so the codebase compiles cleanly: Anthropic API direct backend, budget enforcement/cost caps, session/checkpoint turn counter, and data lifecycle/GDPR scheduling. Langfuse STAYS for observability.

</domain>

<decisions>
## Implementation Decisions

### Langfuse — KEEP (changed from original STRP-06)
- Keep Langfuse service, dependency, tracing module, and metering accumulation
- Keep all tracing levels: workflow traces + phase spans + tool call spans
- Keep MeteringCallback that accumulates token costs per agent
- ONLY strip: BudgetEnforcer, BudgetConfig, check_agency_cost_cap, agency cost caps, max_turns threshold enforcement
- STRP-06 requirement REDEFINED: "Keep Langfuse for observability, strip budget enforcement only"

### Budget enforcement — FULL REMOVAL
- Delete budget.py entirely (BudgetEnforcer, BudgetConfig, MODEL_PRICING, calculate_cost, check_agency_cost_cap, AgencyCostCapResult)
- Strip budget imports and usage from executor.py, agent_runner.py, backends/agent_sdk.py
- Remove budget-related tests from test_budget.py (delete entirely), test_agent_runner.py (strip budget tests)

### Anthropic API backend — FULL REMOVAL
- Delete backends/anthropic_api.py entirely
- Remove API backend selection logic from executor.py (lines 340-348)
- Remove lazy import from backends/__init__.py
- Keep Agent SDK backend path as the only execution path

### Session module — CLAUDE'S DISCRETION
- Strip record_turn() and checkpoint turn counter logic
- Claude decides whether to delete session.py entirely or preserve memory coordination parts
- Decision should be based on what makes Phase 4 (executor rewrite) and Phase 5 (memory rewiring) easiest

### Celery beat — KEEP INFRASTRUCTURE
- Remove the 3 GDPR periodic tasks (enforce_data_retention, process_gdpr_deletions, send_deletion_notifications)
- Keep django-celery-beat package and scheduler infrastructure
- Useful for future scheduled/recurring workflows

### Data lifecycle — FULL REMOVAL
- Delete lifecycle.py entirely
- Delete management commands: enforce_retention.py, process_deletions.py, notify_deletions.py
- Remove lifecycle fields from models (churned_at, deletion_notified_at, deletion_requested_at, deletion_scheduled_at) — handled in Phase 2 migration
- Delete test_data_lifecycle.py

### Claude's Discretion
- Whether to delete session.py entirely or keep memory coordination parts
- Exact order of file deletions and import cleanup
- How to handle metering.py cleanup (strip Langfuse annotation calls for budget alerts, keep cost accumulation)
- Whether to remove turn_count fields from models now (Phase 1) or defer to Phase 2 migrations

</decisions>

<specifics>
## Specific Ideas

- User wants Langfuse as ongoing observability tool — "we need to keep the tokens etc tracked in langfuse and app"
- Budget enforcement stripped because "we dont have to worry about budget any more for now" — personal tool, user monitors costs directly
- Celery beat kept for potential scheduled workflow runs in the future

</specifics>

<code_context>
## Existing Code Insights

### Files to DELETE entirely
- `orchestrator/budget.py` (239 lines) — BudgetEnforcer, BudgetConfig, cost caps
- `orchestrator/backends/anthropic_api.py` (239 lines) — Anthropic API direct backend
- `core/lifecycle.py` (271 lines) — GDPR deletion scheduling
- `core/management/commands/enforce_retention.py` — periodic task command
- `core/management/commands/process_deletions.py` — periodic task command
- `core/management/commands/notify_deletions.py` — periodic task command
- `tests/test_budget.py` — budget tests
- `tests/test_data_lifecycle.py` — lifecycle tests

### Files to MODIFY (strip imports/references)
- `orchestrator/executor.py` — strip budget imports (lines 30-31), check_agency_cost_cap calls (lines 277-290), BudgetConfig construction (lines 305-315), API backend selection (lines 340-348), Langfuse tracing call stays (line 121)
- `orchestrator/agent_runner.py` — strip BudgetConfig from RuntimeBackend Protocol
- `orchestrator/backends/agent_sdk.py` — strip BudgetConfig import
- `orchestrator/backends/__init__.py` — remove AnthropicAPIBackend lazy import
- `orchestrator/metering.py` — strip Langfuse budget alert annotations (_annotate_langfuse_event for thresholds), keep cost accumulation
- `orchestrator/tasks.py` — remove 3 lifecycle task definitions (lines 259-292)
- `orchestrator/session.py` — strip record_turn(), Claude decides rest

### Files to KEEP as-is
- `orchestrator/tracing.py` — full Langfuse tracing (workflow, phase, tool spans)
- `orchestrator/backends/agent_sdk.py` — Agent SDK backend (after stripping budget import)

### Established Patterns
- Lazy imports used for backend modules (executor.py lines 55-60)
- Celery shared_task pattern in tasks.py
- Management commands called from Celery tasks

### Integration Points
- executor.py is the hub — imports from budget, tracing, session, backends
- metering.py callbacks used inside backend execute() methods
- models.py fields (turn_count, langfuse_trace_id) — model field removal deferred to Phase 2

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-strip-infrastructure-dependencies*
*Context gathered: 2026-03-12*

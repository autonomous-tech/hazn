# Domain Pitfalls: v3.0 Strip & Simplify

**Domain:** Stripping enterprise complexity from existing codebase (~60,600 LOC) and rewiring as personal workflow tool
**Researched:** 2026-03-12
**Confidence:** HIGH (pitfalls derived from direct codebase analysis + industry patterns for large-scale refactoring)

This document covers pitfalls specific to the v3.0 milestone: removing enterprise features (MCP servers, HITL, QA pipeline, dual runtime, conflict detection, budget enforcement, Langfuse metering, L2/L3 hierarchy) from hazn_platform and replacing them with simplified personal-use equivalents. Each pitfall includes the specific files/modules at risk in this codebase.

---

## Critical Pitfalls

Mistakes that cause broken deployments, data loss, or require significant rework.

### Pitfall 1: Django Migration State vs. Code Deletion Mismatch

**What goes wrong:**
You delete the `HITLItem` model class from `orchestrator/models.py` and the `qa/models.py` QA pipeline, then run `makemigrations`. Django generates a migration that drops those tables. But the existing database has rows in `orchestrator_hitlitem` with foreign keys to `orchestrator_workflowrun`, and `qa_deliverable` has a foreign key to `orchestrator_hitlitem`. The migration fails because of FK constraint violations, or it succeeds and destroys deliverable records you intended to keep.

**Why it happens:**
Django migrations are stateful -- they track every model that ever existed. Deleting model code does not cleanly remove the migration history. The `Deliverable` model in `qa/models.py` has `hitl_item = models.ForeignKey("orchestrator.HITLItem", on_delete=models.SET_NULL, null=True)`. If you remove `HITLItem` first, the `Deliverable` migration that references it becomes broken. If you remove them simultaneously, the ordering matters. Django's `makemigrations` may generate migrations with circular or broken dependencies between `orchestrator` and `qa` apps.

**Specific files at risk:**
- `qa/models.py:Deliverable.hitl_item` -- FK to `orchestrator.HITLItem`
- `qa/models.py:Deliverable.phase_output` -- OneToOne to `orchestrator.WorkflowPhaseOutput`
- `orchestrator/models.py:WorkflowRun.agency` -- FK to `core.Agency`
- `orchestrator/models.py:WorkflowRun.end_client` -- FK to `core.EndClient`
- All existing migration files in `orchestrator/migrations/`, `qa/migrations/`

**Consequences:**
- `migrate` fails in production with `django.db.utils.IntegrityError`
- Data loss if migrations drop tables containing deliverables you want to keep
- Broken migration graph requiring manual SQL intervention

**Prevention:**
1. Do NOT delete models yet. First, remove the fields you do not need (e.g., `Deliverable.hitl_item`, `WorkflowRun.conflict_log`, `WorkflowRun.langfuse_trace_id`). Generate and apply those migrations.
2. Then remove the model classes (`HITLItem`, `WorkflowAgent`, `WorkflowToolCall`) in a second migration wave.
3. Decide what to do with `Deliverable` FIRST -- it is being kept. Its FKs to `WorkflowPhaseOutput` and `WorkflowRun` must remain. Only strip the `hitl_item` FK and QA-specific fields (`qa_verdict`, `qa_score`, `qa_report`, `approval_status`) if those concepts are truly gone.
4. Never delete migration files from history. Django needs the full chain to understand the current state.
5. Test the full migration sequence on a copy of the production database before applying.

**Detection:**
- `python manage.py makemigrations --check` fails
- `python manage.py migrate --plan` shows unexpected `DeleteModel` operations
- Migration file references a model that no longer exists in code

**Phase to address:** Phase 1 (Model Simplification) -- must be the first code change, before any logic deletion.

---

### Pitfall 2: The Agency/EndClient Model Hierarchy is Load-Bearing

**What goes wrong:**
You flatten the L2/L3 hierarchy (Agency -> EndClient) to a simple client list. You remove the `Agency` model, or make `EndClient` standalone. Then you discover that `Agency` is referenced by: `WorkflowRun.agency`, `VaultCredential.agency`, `MemoryCorrection.end_client.agency`, every workspace view via `request.user.agency`, every queryset filter, every SSE event keyed by `agency_id`, the `HaznMemory.__init__` constructor (`l2_agency_id`), and the `MeteringCallback.from_agency()` factory. Removing `Agency` breaks 30+ import sites.

**Why it happens:**
The v1.0 architecture baked `Agency` into every layer as the multi-tenancy boundary. Even though v3.0 is single-user, `Agency` is not just a "tenant" concept -- it also carries `house_style`, `methodology`, and `tool_preferences` configuration. These JSONFields store actual workflow behavior (context loading policy, cross-client insights toggle, webhook URLs). Removing `Agency` means you also lose configuration storage unless you move it somewhere else.

**Specific coupling points (from codebase analysis):**
- `core/memory.py:HaznMemory.__init__` takes `l2_agency_id`, queries `Agency` in `load_client_context()` and `search_cross_client_insights()`
- `orchestrator/session.py:WorkflowSession.__init__` takes `agency` object, passes to `MeteringCallback.from_agency()`
- `orchestrator/executor.py:WorkflowExecutor.run()` reads `workflow_run.agency` for SSE events, conflict detection, cost cap checks
- `orchestrator/tasks.py:run_workflow()` queries `Agency.objects.get(pk=l2_agency_id)`
- `workspace/views.py`: every single view uses `request.user.agency` for queryset scoping
- `workspace/serializers.py`: `EndClientSerializer` includes `agency` as read-only field
- `workspace/permissions.py:IsAgencyMember` -- the entire permission system
- `frontend/src/types/api.ts:Agency` interface, `EndClient.agency` field, `WorkflowRun.agency` field
- SSE events in `executor.py` all use `agency_id` as the channel key

**Consequences:**
- Attempting to remove `Agency` touches 30+ files across 6 Django apps + frontend
- Breaking `IsAgencyMember` permission breaks every API endpoint
- Breaking `request.user.agency` requires changing the User model
- SSE events stop working because they are keyed by `agency_id`

**Prevention:**
Keep `Agency` as a singleton. Create one Agency record representing "Rizwan's agency." Keep all the FKs intact. This costs nothing (one extra DB row) and preserves every queryset, permission check, and FK relationship. The simplification is semantic, not structural: instead of multi-agency support, there is exactly one agency, and the code that enforces "only your agency's data" becomes a no-op (there is only one). Later, if you want to truly flatten, you can do it incrementally.

**Detection:**
- Any PR that has `from hazn_platform.core.models import Agency` in its deletions
- `grep -r "agency" hazn_platform/` returning 50+ hits after "removal"
- Frontend build errors on `Agency` type references

**Phase to address:** Phase 0 (Architecture Decision) -- decide "keep Agency as singleton" before writing any code.

---

### Pitfall 3: MCP Server Tool Logic Lives in the Server Modules, Not Just the Registry

**What goes wrong:**
You remove the 4 MCP server files (`mcp_servers/hazn_memory_server.py`, `analytics_server.py`, `github_server.py`, `vercel_server.py`) and the `ToolRouter`/`tool_router.py` registry. You replace them with Python function tools. But the actual tool implementation logic was INSIDE those MCP server modules. The `ToolRouter` only has `callable=None` placeholder entries -- the real callables were wired at runtime. When you delete the MCP server files, you lose the implementation of `pull_ga4_data`, `query_gsc`, `check_pagespeed`, `create_repo`, `create_pr`, `deploy_project`, and all other tools. Your new Python function tools are empty shells.

**Why it happens:**
The `tool_router.py:build_tool_registry()` function creates a `ToolRouter` with 23 tool entries, all with `callable=None`. The actual implementations live in the MCP server modules behind FastMCP `@mcp.tool()` decorators. The `hazn_memory_server.py` wraps `HaznMemory` methods. The `analytics_server.py` wraps GA4/GSC/PageSpeed API calls. Deleting the MCP server files deletes the implementation, not just the transport layer.

**Specific files containing irreplaceable logic:**
- `mcp_servers/hazn_memory_server.py` -- wraps `HaznMemory.load_client_context()`, `search_memory()`, `write_finding()`, `checkpoint_sync()`, `correct_memory()`, `end_session()`
- `mcp_servers/analytics_server.py` -- GA4 reporting API calls, GSC API calls, PageSpeed API calls (these are the actual Google API integrations)
- `mcp_servers/github_server.py` -- GitHub REST API wrappers (create repo, create PR, merge PR, CI status)
- `mcp_servers/vercel_server.py` -- Vercel deployment API wrappers
- `orchestrator/data_tools.py` -- subprocess wrappers for Python analytics scripts

**Consequences:**
- All 7 workflows break immediately (no tool implementations)
- Must rewrite every tool from scratch
- Risk of losing subtle implementation details (error handling, credential fetching patterns, response formatting)

**Prevention:**
1. Extract the implementation logic from each MCP server module BEFORE deleting the module. The tool body (what runs when the tool is called) becomes a plain Python function.
2. For each `@mcp.tool()` decorated function in the MCP servers, create a corresponding Python function in a new `tools/` module. Copy the function body, strip the MCP decorator, adjust the return type from MCP format to plain dict/string.
3. For `hazn_memory_server.py`, the logic is mostly delegation to `HaznMemory` -- the Python functions just call `HaznMemory` methods directly (which is simpler than going through MCP).
4. For `analytics_server.py`, `github_server.py`, `vercel_server.py` -- these contain actual API integration code. Extract it function-by-function.
5. Only delete the MCP server files AFTER the replacement functions exist and are tested.

**Detection:**
- Any tool function that is just `pass` or `return {}`
- Workflow runs where every tool call returns an error
- `grep -r "mcp_servers" hazn_platform/` still showing import references after deletion

**Phase to address:** Phase 2 (Tool Migration) -- must be done before workflow engine rewiring. Extract first, then delete.

---

### Pitfall 4: The Executor Imports 15+ Modules -- Deleting Any One Breaks Import Chain

**What goes wrong:**
You delete `orchestrator/conflict_detector.py` because conflict detection is out of scope. But `orchestrator/executor.py` line 32 has `from hazn_platform.orchestrator.conflict_detector import detect_conflicts`. Django fails to start because the import chain is broken. This is not a runtime error -- it is an import-time crash that prevents the entire application from loading. The same applies to `budget.py`, `hitl.py`, `metering.py`, `tracing.py`, `tool_router.py`, `tool_wiring.py`, `session.py`, and `qa/runner.py`.

**Why it happens:**
`executor.py` is the hub of the orchestration system. It imports from 13 different modules across 4 Django apps:
```
orchestrator/agent_manager.py
orchestrator/agent_runner.py
orchestrator/budget.py              -- BEING REMOVED
orchestrator/conflict_detector.py   -- BEING REMOVED
orchestrator/hitl.py                -- BEING REMOVED
orchestrator/metering.py            -- BEING REMOVED
orchestrator/models.py
orchestrator/output_collector.py
orchestrator/prompt_assembler.py
orchestrator/tracing.py             -- BEING REMOVED
orchestrator/workflow_parser.py
deliverable_pipeline/renderer.py
deliverable_pipeline/schemas.py
qa/runner.py                        -- BEING REMOVED
qa/staging.py                       -- BEING REMOVED
workspace/sse_views.py
```

Deleting any of the 7 marked modules without first removing the import from `executor.py` crashes the application.

**Consequences:**
- `ImportError` on Django startup -- nothing works
- Celery workers fail to boot (they import `executor.py` via `tasks.py`)
- Frontend shows API errors for every endpoint
- The error message may be misleading (Django shows the import error for the first broken import, not all of them)

**Prevention:**
1. **Do not delete modules in isolation.** Each deletion must be paired with removal of every import that references it.
2. Use a dependency analysis approach: for each file being deleted, `grep -r "from hazn_platform.orchestrator.{module}" hazn_platform/` and fix all references first.
3. The safest strategy is to rewrite `executor.py` from scratch as the simplified workflow engine, rather than trying to surgically remove imports from the existing 590-line file. The existing executor is coupled to conflict detection, HITL, QA, budget enforcement, metering, and tracing -- all being removed. Removing all of those leaves a skeleton that is harder to maintain than a clean rewrite.
4. Verify with `python manage.py check` after every deletion batch.

**Detection:**
- `python manage.py check` fails
- `python -c "import hazn_platform.orchestrator.executor"` raises `ImportError`
- Celery worker startup log shows import errors
- Any commit that deletes a `.py` file without updating its importers

**Phase to address:** Phase 3 (Workflow Engine Rewrite) -- rewrite executor from scratch rather than surgical deletion.

---

### Pitfall 5: Frontend Types Mirror Backend Models 1:1 -- Schema Drift After Backend Changes

**What goes wrong:**
You simplify the backend models (remove `HITLItem`, simplify `Deliverable`, remove `conflict_log` from `WorkflowRun`). The DRF serializers change shape. But `frontend/src/types/api.ts` still expects the old shapes: `HITLItem` interface, `WorkflowRunDetail.hitl_items`, `WorkflowRunDetail.conflict_log`, `Deliverable.qa_verdict`, `Deliverable.approval_status`, `DashboardData.pending_approvals`. The frontend compiles (TypeScript optional chaining hides the errors) but renders broken UI: HITL queue page crashes, deliverable detail shows undefined fields, dashboard shows NaN for pending approvals.

**Why it happens:**
The frontend types in `api.ts` were hand-authored to match the DRF serializer output shapes exactly. There is no code generation or schema validation between backend and frontend. When the backend changes, the frontend types become stale silently. TypeScript only catches type errors at the sites where stale types are used -- if a component accesses `data?.hitl_items?.length` with optional chaining, TypeScript does not error even though `hitl_items` no longer exists in the API response.

**Specific frontend files at risk:**
- `frontend/src/types/api.ts` -- 14 interfaces that mirror backend models
- `frontend/src/app/(workspace)/approvals/page.tsx` -- entire page for HITL (being removed)
- `frontend/src/app/(workspace)/deliverables/[id]/page.tsx` -- references QA fields
- `frontend/src/app/(workspace)/workflows/[id]/page.tsx` -- references HITL, conflict_log
- `frontend/src/app/(workspace)/page.tsx` -- dashboard with `pending_approvals`

**Consequences:**
- Runtime crashes on pages that reference removed API fields
- Confusing UI showing "0" or "undefined" for removed concepts
- Pages that should be removed (approvals) still exist and 404 on API calls
- Dashboard metrics become nonsensical

**Prevention:**
1. Update `api.ts` types IMMEDIATELY when backend serializers change. Do not batch frontend updates -- synchronize per backend change.
2. Remove the approvals page entirely (it is the HITL queue, which is being removed).
3. Simplify `Deliverable` interface to remove QA-specific fields.
4. Remove `conflict_log` and `hitl_items` from `WorkflowRunDetail`.
5. Update the dashboard to remove `pending_approvals` count.
6. Run the Next.js build (`npm run build`) as a CI check -- it catches TypeScript errors that `tsc` might miss due to incremental compilation.

**Detection:**
- `npm run build` fails with type errors
- Browser console showing "Cannot read property of undefined" on workspace pages
- API responses that do not match TypeScript interfaces
- Pages that reference removed API endpoints returning 404

**Phase to address:** Phase 4 (Dashboard Simplification) -- must happen in lockstep with backend model changes, not after.

---

### Pitfall 6: HaznMemory L2/L3 Terminology Baked Into Interface

**What goes wrong:**
You flatten the client model (no more L2 agency / L3 end-client distinction). But `HaznMemory.__init__` takes `l3_client_id` and `l2_agency_id` as constructor parameters. The `_assemble_context()` method queries both `Agency` and `EndClient` models. The `search_cross_client_insights()` method explicitly queries "sibling L3 clients under the same Agency." The craft learning metadata tags include `[client:{l3_client_id}]`. If you change the data model without updating HaznMemory, memory operations silently fail or write corrupted metadata.

**Why it happens:**
HaznMemory was designed as a swap-safe abstraction, but it was designed FOR the L2/L3 hierarchy. The "swap-safe" design means you can swap Letta for another backend -- it does NOT mean you can swap the data model. The L2/L3 assumption is baked into:
- Constructor signature: `agent_id`, `l3_client_id`, `l2_agency_id`
- `load_client_context()`: queries `Agency`, `EndClient`, `BrandVoice`, `Keyword`, `Campaign`
- `search_cross_client_insights()`: queries sibling `EndClient` records
- `_write_craft_learning()`: embeds `[client:{l3_client_id}]` in archival memory
- `correct_memory()`: creates `MemoryCorrection` records with `end_client` FK

**Consequences:**
- If Agency is removed, `_assemble_context()` crashes on `Agency.objects.get()`
- If EndClient FK to Agency is removed, `search_cross_client_insights()` cannot find siblings
- Craft learnings in Letta archival memory have `[client:uuid]` tags that reference EndClient PKs -- changing the client model orphans these references
- Existing Letta archival memory becomes unsearchable if the metadata format changes

**Prevention:**
1. Keep `HaznMemory` interface parameters (`l3_client_id`, `l2_agency_id`) even if you keep Agency as singleton. The names are internal -- callers just pass UUIDs.
2. Simplify `_assemble_context()` to skip the Agency query if using singleton pattern, or keep it as-is since singleton Agency still has `house_style` and `methodology`.
3. Keep `search_cross_client_insights()` -- it works across clients, which is valuable for a single user with 8+ clients. The "sibling" concept just means "other clients" when there is one agency.
4. Do NOT change the `[client:uuid]` tag format in archival memory. Existing Letta passages contain this format. Changing it means existing memories cannot be found by the search/ranking code.
5. If you must rename parameters, use a compatibility shim: `client_id` parameter that maps internally to `l3_client_id`.

**Detection:**
- `HaznMemory.load_client_context()` raises `Agency.DoesNotExist`
- Craft learning passages missing `[client:]` tags
- `search_cross_client_insights()` returning empty results when clients exist
- Memory search returning 0 results for queries that should match existing passages

**Phase to address:** Phase 2 (Memory Rewiring) -- must decide memory interface before workflow engine rewrite.

---

## Moderate Pitfalls

### Pitfall 7: Langfuse Import at Module Level Crashes if Langfuse is Removed

**What goes wrong:**
`orchestrator/metering.py` line 22 has `from langfuse import get_client`. If you remove Langfuse from the Docker Compose stack and uninstall the `langfuse` Python package, every module that imports `metering.py` (which includes `session.py`, which includes `executor.py`, which includes `tasks.py`) crashes with `ModuleNotFoundError: No module named 'langfuse'`.

**Prevention:**
1. Remove the `langfuse` import from `metering.py` before removing the package.
2. If keeping a simplified metering system, replace the Langfuse call with a no-op or Django logging.
3. If removing metering entirely, delete `metering.py` and update all its importers (see Pitfall 4 for the import chain).
4. Remove `langfuse` from `pyproject.toml` only AFTER all imports are cleaned up.

**Phase to address:** Phase 1 (Dependency Cleanup) -- remove Langfuse imports before removing the package.

---

### Pitfall 8: Celery Task Signatures Coupled to Enterprise Workflow

**What goes wrong:**
`orchestrator/tasks.py:run_workflow()` takes `l2_agency_id` and `l3_client_id` as string parameters. The `WorkflowTriggerView` in `workspace/views.py` calls `run_workflow.delay(workflow_name=..., l2_agency_id=str(agency.pk), l3_client_id=str(end_client.pk), triggered_by=...)`. If you change the task signature (rename parameters, remove agency_id), any in-flight Celery tasks or queued tasks from before the deployment will fail with `TypeError: unexpected keyword argument`.

**Prevention:**
1. When changing Celery task signatures, deploy the NEW signature code first with backward-compatible parameter handling (accept old args, map to new args).
2. Wait for all in-flight tasks to drain before deploying the final signature.
3. For v3.0, since this is a personal tool and you control the deployment, simply: stop Celery, purge the queue (`celery -A config.celery_app purge`), deploy new code, restart Celery.
4. Consider whether Celery is even needed for v3.0. If workflows run synchronously or via Django async views, Celery adds operational complexity for a single-user tool. Evaluate removing it.

**Phase to address:** Phase 3 (Workflow Engine) -- decide on Celery vs. async views before rewriting the executor.

---

### Pitfall 9: Workspace Permission System Assumes Multi-Tenant

**What goes wrong:**
Every workspace view uses `IsAgencyMember` permission class that checks `request.user.agency`. The `DashboardView`, `EndClientViewSet`, `WorkflowRunViewSet`, `HITLItemViewSet`, and `DeliverableViewSet` all filter querysets by `request.user.agency`. If you simplify auth for single-user (e.g., remove the agency FK from User), every endpoint returns 403 Forbidden or empty querysets.

**Prevention:**
1. Keep the User.agency FK pointing to the singleton Agency.
2. Either keep `IsAgencyMember` as-is (it works fine with one agency) or replace it with a simpler `IsAuthenticated` check.
3. Do NOT remove queryset filtering by agency -- it costs nothing and provides defense-in-depth if you ever add a second user.

**Phase to address:** Phase 4 (Dashboard Simplification) -- simplify permissions but do not break the auth chain.

---

### Pitfall 10: Docker Compose Service Removal Order Matters

**What goes wrong:**
You remove the Langfuse service from `docker-compose.local.yml`. But the Django settings still reference `LANGFUSE_HOST`, `LANGFUSE_SECRET_KEY`, etc. Django starts, but `metering.py` tries to connect to a Langfuse host that does not exist, causing timeouts on every workflow run. Or worse: you remove the Letta service thinking you will "add it back later," and the entire memory system goes offline.

**Prevention:**
1. Remove Docker services only AFTER all code references to them are removed.
2. For services being kept (Letta, Vault, Redis, Postgres), do not touch their Docker Compose entries.
3. For services being removed (Langfuse): first remove code references, then remove Django settings, then remove Docker service.
4. Create a "v3.0" docker-compose override that removes enterprise services while keeping core ones.
5. Test with `docker compose config` to validate the final compose file before deploying.

**Phase to address:** Phase 1 (Infrastructure Simplification) -- update compose files last, after code changes are stable.

---

### Pitfall 11: Existing Letta Agents Have Enterprise Memory Blocks

**What goes wrong:**
Existing Letta agents (created during v1.0/v2.0 development) have `active_client_context` memory blocks with JSON that references Agency fields, L2/L3 hierarchy terminology, and enterprise-specific context. When v3.0 code loads these agents, the memory block content does not match the simplified expectations. The agent receives stale enterprise context (e.g., `agency.house_style` from a test Agency) and produces confused outputs.

**Prevention:**
1. Before running v3.0 workflows, either delete existing Letta agents and create fresh ones, or wipe their `active_client_context` blocks.
2. Document the expected memory block format for v3.0.
3. The `HaznMemory.load_client_context()` method overwrites the block on each session start, so this is self-healing -- but the first run may use stale context if `load_client_context()` fails for any reason.

**Phase to address:** Phase 2 (Memory Rewiring) -- clean up Letta state before first v3.0 workflow run.

---

## Minor Pitfalls

### Pitfall 12: Test Fixtures Reference Enterprise Models

**What goes wrong:**
`testing/fixtures.py` and `testing/mocks.py` create Agency, EndClient, and other model instances for tests. `conftest.py` may set up enterprise fixtures. After model simplification, fixtures break and tests fail -- but the failures are in test infrastructure, not production code, making them easy to dismiss and hard to debug.

**Prevention:**
Update `testing/fixtures.py` and `testing/mocks.py` alongside model changes. Do not let test infrastructure drift.

**Phase to address:** Every phase that changes models.

---

### Pitfall 13: Admin Site Registration for Removed Models

**What goes wrong:**
`orchestrator/admin.py` and `qa/admin.py` register models with the Django admin. If models are deleted but admin registrations remain, Django admin crashes on startup.

**Prevention:**
Remove admin registrations in the same commit as model deletions.

**Phase to address:** Same phase as model changes.

---

### Pitfall 14: Management Commands Reference Enterprise Features

**What goes wrong:**
Management commands like `enforce_retention`, `process_deletions`, `notify_deletions`, and `seed_dev_data` reference Agency/EndClient lifecycle concepts. `enforce_retention` checks `Agency.churned_at`. These commands may be called by Celery periodic tasks (`tasks.py:enforce_data_retention`, `process_gdpr_deletions`, `send_deletion_notifications`). Removing the commands without removing the Celery beat schedule entries causes silent failures in background tasks.

**Prevention:**
1. Remove the Celery periodic task entries for enterprise lifecycle commands.
2. Keep `seed_dev_data` and adapt it for v3.0 (seed one agency, some clients).
3. Data lifecycle commands (`enforce_retention`, `process_deletions`, `notify_deletions`) can be deleted entirely for a personal tool.

**Phase to address:** Phase 1 (Dependency Cleanup).

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Model simplification | FK constraint violations during migration (Pitfall 1) | Migrate field removals before model removals. Test on DB copy first. |
| Agency/client flattening | 30+ files break if Agency removed (Pitfall 2) | Keep Agency as singleton -- zero cost, avoids cascade. |
| MCP -> Python functions | Losing tool implementation logic (Pitfall 3) | Extract implementations BEFORE deleting MCP server files. |
| Executor rewrite | Import chain crash (Pitfall 4) | Rewrite from scratch rather than surgical removal. |
| Frontend dashboard | Type drift causes runtime crashes (Pitfall 5) | Update api.ts in lockstep with backend changes. |
| Memory rewiring | L2/L3 assumptions in HaznMemory (Pitfall 6) | Keep interface parameters, simplify internals. |
| Langfuse removal | Module-level import crash (Pitfall 7) | Remove imports before removing package. |
| Celery changes | In-flight task failures (Pitfall 8) | Purge queue before deploying new signatures. |
| Auth simplification | 403 on all endpoints (Pitfall 9) | Keep User.agency FK to singleton. |
| Docker cleanup | Service removal before code cleanup (Pitfall 10) | Code first, compose last. |
| Letta memory | Stale enterprise memory blocks (Pitfall 11) | Wipe Letta agents before first v3.0 run. |

## Deletion Order (Safe Sequence)

Based on the dependency analysis above, here is the safe order for stripping enterprise features:

```
1. Decide: Keep Agency as singleton (Pitfall 2)
2. Remove enterprise Django model FIELDS (not models): conflict_log, langfuse_trace_id, etc.
3. Generate and apply field-removal migrations
4. Extract tool logic from MCP servers into Python functions (Pitfall 3)
5. Remove code imports to enterprise modules: budget, conflict_detector, hitl, metering, tracing (Pitfall 4)
6. Remove Langfuse Python package import (Pitfall 7)
7. Delete enterprise module FILES: budget.py, conflict_detector.py, hitl.py, tracing.py, metering.py, qa/runner.py, qa/staging.py, qa/criteria.py
8. Delete MCP server files (after step 4 confirms replacements work)
9. Delete enterprise Django MODELS: HITLItem, WorkflowAgent, WorkflowToolCall (maybe -- evaluate if useful for v3.0 metering)
10. Generate and apply model-removal migrations
11. Rewrite executor.py as simplified workflow engine
12. Update frontend types and remove HITL/approvals pages (Pitfall 5)
13. Remove Celery periodic tasks for enterprise features (Pitfall 14)
14. Update Docker Compose (Pitfall 10)
15. Clean Letta agent state (Pitfall 11)
```

Violating this order (e.g., doing step 7 before step 5, or step 9 before step 2) triggers the critical pitfalls above.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Broken migration (Pitfall 1) | MEDIUM | Roll back migration, fix migration graph manually, re-test on DB copy |
| Agency removal cascade (Pitfall 2) | HIGH | Revert all changes, add Agency back, fix 30+ files. Prevention is far cheaper. |
| Lost tool implementations (Pitfall 3) | MEDIUM | Recover from git history, extract functions retroactively |
| Import chain crash (Pitfall 4) | LOW | Fix imports, re-deploy. But every minute of downtime is lost workflow time. |
| Frontend type drift (Pitfall 5) | LOW | Update types, rebuild, re-deploy. But user sees broken UI until fixed. |
| Memory format mismatch (Pitfall 6) | HIGH | Existing Letta archival passages may be permanently orphaned if tag format changes. No easy recovery. |

## Sources

- Direct codebase analysis of hazn_platform/ (402 files, ~60,600 LOC) -- all file references verified against actual code. HIGH confidence.
- [Django Migrations Documentation](https://docs.djangoproject.com/en/6.0/topics/migrations/) -- migration squashing, FK constraints, dependency management. HIGH confidence.
- [Squashing Django Migrations Easily](https://jacklinke.com/squashing-django-migrations-the-easy-way) -- migration ordering pitfalls. MEDIUM confidence.
- [Letta Agent Memory Docs](https://docs.letta.com/guides/agents/memory/) -- memory block isolation, per-client agent patterns. HIGH confidence.
- [Letta Conversations Blog](https://www.letta.com/blog/conversations) -- "if you want memory to be isolated, you should continue to create separate agents." MEDIUM confidence.
- [Refactoring at Scale: Change Messy Software Without Breaking It](https://understandlegacycode.com/blog/key-points-of-refactoring-at-scale/) -- atomic changes, dependency analysis, incremental delivery. MEDIUM confidence.
- [Code Refactoring Best Practices](https://www.tembo.io/blog/code-refactoring) -- tight coupling detection, testing between refactoring steps. MEDIUM confidence.
- [Anthropic API FastMCP Integration](https://gofastmcp.com/integrations/anthropic) -- MCP vs direct function calling patterns. MEDIUM confidence.

---
*Pitfalls research for: Hazn v3.0 Strip & Simplify*
*Researched: 2026-03-12*

# Phase 2: Model Simplification - Context

**Gathered:** 2026-03-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Django models reflect the simplified single-user system — enterprise fields removed, HITL and QA models dropped, Agency preserved as singleton, permissions simplified to IsAuthenticated. Client-level data isolation (EndClient, BrandVoice, ApprovedCopy) is critical and must be preserved.

</domain>

<decisions>
## Implementation Decisions

### HITL & QA Removal
- Delete HITLItem model ENTIRELY — model, views, serializers, admin, URLs, hitl.py resolver, all 5 trigger types
- Delete ENTIRE QA app — qa/models.py (Deliverable), qa/runner.py, qa/admin.py, qa migrations
- Before deleting QA app: migrate html_content and markdown_source fields from Deliverable to WorkflowPhaseOutput (preserves rendering capability)
- Delete conflict_detector.py and test_conflict_detector.py
- Keep WorkflowRun.conflict_log JSONField as generic run notes (don't remove)
- QA hook in executor.py: DEFER cleanup to Phase 4 (executor rewrite from scratch). Mark dead import with TODO comment so it doesn't break at runtime

### Agency Singleton & Permissions
- Keep Agency model as-is, enforce singleton constraint (migration or model-level check)
- Replace IsAgencyMember with IsAuthenticated in all 10 viewsets
- Keep agency-scoped queryset filters (e.g., EndClient.objects.filter(agency=request.user.agency)) — safety net
- Remove User.agency_role field (migration) — single user is always admin
- Delete IsAgencyAdmin permission class
- Remove Agency.tool_preferences JSONField (stores hitl_config and conflict resolution settings — both deleted)
- Keep Agency.house_style and Agency.methodology — feed agent system prompts

### Enterprise Field Cleanup
- Remove WorkflowRun.turn_count (dead after Phase 1, never written)
- Keep WorkflowRun.langfuse_trace_id (actively used by tracing.py)
- Remove WorkflowAgent.turn_count (cost tracking via total_tokens/total_cost only)
- Remove Agency.churned_at and Agency.deletion_notified_at (GDPR lifecycle — dead)
- Remove EndClient.deletion_requested_at and EndClient.deletion_scheduled_at (GDPR lifecycle — dead)

### Migration Strategy
- Single coordinated migration for FK ordering: remove Deliverable.hitl_item FK first, then delete Deliverable model, then delete HITLItem model, then remove enterprise fields
- Fresh start for v3.0 — no production data to preserve, DB will be recreated
- Run cleanup migrations first, verify DB is clean, THEN squash to fresh 0001_initial.py per app reflecting final v3.0 schema
- End state: `python manage.py makemigrations --check` produces no new migrations

### Claude's Discretion
- Exact migration file organization (single file vs split per concern within the coordinated approach)
- Order of field removals within the coordinated migration
- How to handle the QA executor hook TODO comment (exact wording/placement)
- Whether to add a Django model constraint or a custom save() method for Agency singleton enforcement
- How to migrate html_content/markdown_source to PhaseOutput (data migration vs schema-only since fresh DB)

</decisions>

<specifics>
## Specific Ideas

- Client-level data isolation is critical — each EndClient has its own context (brand voice, keywords, campaigns, learnings). This structure must survive model simplification
- "I need to not give too much of it every time" — per-client scoping prevents context bleed between clients
- WorkflowPhaseOutput needs html_content and markdown_source fields from Deliverable before QA app deletion — preserves deliverable rendering for Phase 6 dashboard
- Fresh DB for v3.0 means squashed migrations can define the final clean schema directly

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- WorkflowPhaseOutput model: Already captures phase artifacts (content JSONField, summary, artifact_type, structured_data). Adding html_content/markdown_source makes it the single output model
- Agency model: Well-established FK anchor across 30+ files. Singleton enforcement is additive, not destructive

### Established Patterns
- Lazy imports in orchestrator/executor.py (backends, qa runner)
- Celery shared_task pattern in tasks.py (kept from Phase 1)
- Agency-scoped queryset filtering in workspace/views.py (10 viewsets)
- Cross-app migration dependencies (Django supports `dependencies` list)

### Integration Points
- executor.py imports qa/runner.py — needs TODO comment after QA app deletion (Phase 4 cleanup)
- workspace/views.py uses IsAgencyMember in 10 viewsets — switch to IsAuthenticated
- workspace/serializers.py exposes DeliverableSerializer, HITLItemSerializer — both deleted
- workspace/views.py has HITLItemViewSet and DeliverableViewSet — both deleted
- orchestrator/admin.py registers HITLItemAdmin — deleted
- qa/admin.py registers DeliverableAdmin — entire app deleted
- frontend/src references HITL and deliverable components — dead imports after backend removal

### Files to DELETE entirely
- hazn_platform/orchestrator/conflict_detector.py
- hazn_platform/qa/ (entire app: models.py, runner.py, admin.py, apps.py, migrations/)
- hazn_platform/orchestrator/hitl.py
- hazn_platform/workspace/permissions.py (IsAgencyAdmin removed, IsAgencyMember replaced inline)
- tests/test_conflict_detector.py
- tests/test_qa_models.py, test_qa_runner.py, test_qa_approval.py

### Files to MODIFY
- hazn_platform/orchestrator/models.py — delete HITLItem, add html_content/markdown_source to PhaseOutput, remove WorkflowRun.turn_count, WorkflowAgent.turn_count
- hazn_platform/core/models.py — remove lifecycle fields from Agency and EndClient
- hazn_platform/users/models.py — remove agency_role field
- hazn_platform/workspace/views.py — replace IsAgencyMember with IsAuthenticated, remove HITLItemViewSet, DeliverableViewSet
- hazn_platform/workspace/serializers.py — remove HITLItemSerializer, DeliverableSerializer
- hazn_platform/orchestrator/admin.py — remove HITLItemAdmin
- hazn_platform/workspace/urls.py — remove HITL and deliverable URL patterns
- config/settings/base.py — remove 'qa' from INSTALLED_APPS
- All migration files — cleanup then squash to fresh 0001_initial per app

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-model-simplification*
*Context gathered: 2026-03-12*

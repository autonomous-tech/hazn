# Phase 2: Model Simplification - Research

**Researched:** 2026-03-12
**Domain:** Django model refactoring, migration management, permission simplification
**Confidence:** HIGH

## Summary

Phase 2 is a systematic model-level cleanup of the Hazn Django codebase, removing enterprise features (HITL queue, QA pipeline, conflict detection, GDPR lifecycle fields) and simplifying the permission model from agency-scoped role-based access to a single-user `IsAuthenticated` system. The work is entirely within the Django ORM and DRF layers -- no new libraries or external dependencies are needed.

The codebase is well-structured with clear separation: orchestrator app owns HITLItem and WorkflowRun/Agent/ToolCall/PhaseOutput models, qa app owns Deliverable, core app owns Agency/EndClient/VaultCredential/MemoryCorrection, and workspace app provides the DRF API layer. The key challenge is coordinating deletions across FK boundaries (Deliverable -> HITLItem, ShareLink -> Deliverable) while preserving the models and relationships that v3.0 needs (EndClient, BrandVoice, ApprovedCopy, WorkflowPhaseOutput).

Since this is a fresh DB start for v3.0 (no production data to preserve), the migration strategy is: write cleanup migrations to get the model state correct, then squash each app to a single `0001_initial.py` reflecting the final v3.0 schema.

**Primary recommendation:** Execute deletions in FK dependency order (ShareLink first, then Deliverable/QA app, then HITLItem, then field removals), then squash all migrations per app to fresh 0001_initial.py files. Use Django CheckConstraint for Agency singleton enforcement.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Delete HITLItem model ENTIRELY -- model, views, serializers, admin, URLs, hitl.py resolver, all 5 trigger types
- Delete ENTIRE QA app -- qa/models.py (Deliverable), qa/runner.py, qa/admin.py, qa migrations
- Before deleting QA app: migrate html_content and markdown_source fields from Deliverable to WorkflowPhaseOutput (preserves rendering capability)
- Delete conflict_detector.py and test_conflict_detector.py
- Keep WorkflowRun.conflict_log JSONField as generic run notes (don't remove)
- QA hook in executor.py: DEFER cleanup to Phase 4 (executor rewrite from scratch). Mark dead import with TODO comment so it doesn't break at runtime
- Keep Agency model as-is, enforce singleton constraint (migration or model-level check)
- Replace IsAgencyMember with IsAuthenticated in all 10 viewsets
- Keep agency-scoped queryset filters (e.g., EndClient.objects.filter(agency=request.user.agency)) -- safety net
- Remove User.agency_role field (migration) -- single user is always admin
- Delete IsAgencyAdmin permission class
- Remove Agency.tool_preferences JSONField (stores hitl_config and conflict resolution settings -- both deleted)
- Keep Agency.house_style and Agency.methodology -- feed agent system prompts
- Remove WorkflowRun.turn_count (dead after Phase 1, never written)
- Keep WorkflowRun.langfuse_trace_id (actively used by tracing.py)
- Remove WorkflowAgent.turn_count (cost tracking via total_tokens/total_cost only)
- Remove Agency.churned_at and Agency.deletion_notified_at (GDPR lifecycle -- dead)
- Remove EndClient.deletion_requested_at and EndClient.deletion_scheduled_at (GDPR lifecycle -- dead)
- Single coordinated migration for FK ordering: remove Deliverable.hitl_item FK first, then delete Deliverable model, then delete HITLItem model, then remove enterprise fields
- Fresh start for v3.0 -- no production data to preserve, DB will be recreated
- Run cleanup migrations first, verify DB is clean, THEN squash to fresh 0001_initial.py per app reflecting final v3.0 schema
- End state: `python manage.py makemigrations --check` produces no new migrations

### Claude's Discretion
- Exact migration file organization (single file vs split per concern within the coordinated approach)
- Order of field removals within the coordinated migration
- How to handle the QA executor hook TODO comment (exact wording/placement)
- Whether to add a Django model constraint or a custom save() method for Agency singleton enforcement
- How to migrate html_content/markdown_source to PhaseOutput (data migration vs schema-only since fresh DB)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| STRP-02 | HITL queue system removed (model, views, serializers, frontend pages) | HITLItem model deletion, hitl.py removal, views/serializers/admin/URL cleanup, orchestrator API views/urls cleanup. Full dependency map documented below. |
| STRP-03 | QA approval pipeline removed (scoring, 48-hour lifecycle, approval states) | Entire QA app deletion (models, runner, criteria, staging, admin, migrations). ShareLink FK to Deliverable must be handled first. html_content/markdown_source fields migrated to WorkflowPhaseOutput before deletion. |
| STRP-07 | Conflict detection removed (L2 vs L3 hierarchy) | conflict_detector.py deletion, executor.py imports marked as TODO for Phase 4. test_conflict_detector.py deletion. |
| STRP-10 | Django models simplified (enterprise fields removed, Agency as singleton, clean migrations) | Field removals from WorkflowRun, WorkflowAgent, Agency, EndClient, User. Agency singleton via CheckConstraint. Migration squashing to fresh 0001_initial per app. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Django | 4.2+ (project uses cookiecutter-django) | ORM, migrations, admin | Already in project, sole framework |
| Django REST Framework | 3.14+ | API viewsets, serializers, permissions | Already in project, all API endpoints |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| django-filter | 23.5+ | Filterset classes for viewsets | Already in project, used by WorkflowRunFilter, HITLItemFilter, DeliverableFilter |
| pytest-django | 4.12.0 | Test runner | Already in project, all tests |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| CheckConstraint for singleton | django-solo package | CheckConstraint is zero-dependency, built-in Django. django-solo adds admin integration but Agency admin already exists |
| Manual migration squash | `squashmigrations` command | Manual replacement is cleaner for fresh DB start -- no RunPython/elidable complexity |

**Installation:**
No new packages needed. All tools are already in the project.

## Architecture Patterns

### Recommended Deletion Order

The FK dependency chain determines deletion order. This is the critical sequencing:

```
Step 1: Add html_content + markdown_source to WorkflowPhaseOutput (schema-only, fresh DB)
Step 2: Remove ShareLink.deliverable FK (workspace app migration)
Step 3: Remove Deliverable.hitl_item FK (qa app migration)
Step 4: Delete Deliverable model (qa app migration)
Step 5: Delete HITLItem model (orchestrator app migration)
Step 6: Remove enterprise fields (Agency, EndClient, User, WorkflowRun, WorkflowAgent)
Step 7: Add Agency singleton CheckConstraint
Step 8: Remove 'qa' from INSTALLED_APPS
Step 9: Delete QA app directory entirely
Step 10: Delete files (conflict_detector.py, hitl.py, permissions.py, tests)
Step 11: Update all Python imports and references
Step 12: Squash migrations per app to fresh 0001_initial.py
```

### FK Dependency Map (verified from codebase)

```
ShareLink.deliverable -> qa.Deliverable (CASCADE)
Deliverable.hitl_item -> orchestrator.HITLItem (SET_NULL)
Deliverable.workflow_run -> orchestrator.WorkflowRun (CASCADE)
Deliverable.phase_output -> orchestrator.WorkflowPhaseOutput (CASCADE)
WorkflowRun.hitl_items (reverse FK from HITLItem)
WorkflowRun.deliverables (reverse FK from Deliverable)
```

### Files to DELETE (verified from codebase)

```
hazn_platform/orchestrator/conflict_detector.py
hazn_platform/orchestrator/hitl.py
hazn_platform/workspace/permissions.py
hazn_platform/qa/                              (entire directory)
tests/test_conflict_detector.py
tests/test_hitl.py
tests/test_hitl_api.py
tests/test_qa_models.py
tests/test_qa_runner.py
tests/test_qa_approval.py
tests/test_qa_criteria.py
tests/test_qa_staging.py
tests/test_workspace_hitl.py
tests/test_workspace_deliverables.py
```

### Files to MODIFY (verified from codebase)

```
hazn_platform/orchestrator/models.py
  - Delete HITLItem class (lines 134-178)
  - Add html_content TextField and markdown_source TextField to WorkflowPhaseOutput
  - Remove WorkflowRun.turn_count (line 44)
  - Remove WorkflowAgent.turn_count (line 76)

hazn_platform/core/models.py
  - Remove Agency.tool_preferences (line 20)
  - Remove Agency.churned_at (line 21)
  - Remove Agency.deletion_notified_at (line 22)
  - Remove EndClient.deletion_requested_at (line 46)
  - Remove EndClient.deletion_scheduled_at (line 47)

hazn_platform/users/models.py
  - Remove AgencyRole class (lines 15-17)
  - Remove agency_role field (lines 32-36)

hazn_platform/workspace/views.py
  - Remove HITLItemViewSet class (lines 314-381)
  - Remove DeliverableViewSet class (lines 384-467)
  - Remove DeliverableHTMLView class (lines 507-535)
  - Replace all IsAgencyMember with IsAuthenticated (9 remaining viewsets)
  - Remove imports: HITLItem, Deliverable, approve_hitl_item, reject_hitl_item,
    HITLItemFilter, DeliverableFilter, HITLItemSerializer, DeliverableSerializer,
    ShareLink, IsAgencyMember
  - Update DashboardView.get(): remove pending_approvals (HITLItem) and
    ready_deliverables (Deliverable) counts

hazn_platform/workspace/serializers.py
  - Remove HITLItemSerializer class (lines 142-170)
  - Remove DeliverableSerializer class (lines 172-193)
  - Remove imports: HITLItem from orchestrator.models, Deliverable from qa.models
  - Remove turn_count from WorkflowRunListSerializer.fields
  - Remove turn_count and hitl_items from WorkflowRunDetailSerializer.fields
  - Remove OrchestratorHITLItemSerializer import

hazn_platform/workspace/urls.py
  - Remove HITLItemViewSet and DeliverableViewSet router registrations
  - Remove DeliverableHTMLView URL pattern
  - Remove imports for removed views

hazn_platform/workspace/filters.py
  - Remove HITLItemFilter class
  - Remove DeliverableFilter class
  - Remove imports: HITLItem from orchestrator.models, Deliverable from qa.models

hazn_platform/workspace/share_models.py
  - Change ShareLink.deliverable FK from "qa.Deliverable" to
    "orchestrator.WorkflowPhaseOutput" (or delete ShareLink entirely since
    it depends on QA Deliverable concept -- Claude's discretion)

hazn_platform/workspace/share_views.py
  - Update PublicShareView to work with new ShareLink target (or remove if
    ShareLink is deleted)

hazn_platform/orchestrator/admin.py
  - Remove HITLItemAdmin registration (lines 41-46)
  - Remove HITLItem import

hazn_platform/orchestrator/executor.py
  - Mark dead imports as TODO comments (conflict_detector, hitl, qa.runner,
    qa.staging) -- DO NOT delete, per user decision: defer cleanup to Phase 4
  - Comment out the actual import lines and add TODO markers

hazn_platform/orchestrator/tasks.py
  - Remove check_hitl_timeouts task
  - Remove process_expired_items import
  - Remove deliver_webhook task (used only for HITL notifications)

hazn_platform/orchestrator/api/views.py
  - Remove HITLItemViewSet class
  - Remove imports: HITLItem, approve_hitl_item, reject_hitl_item, HITLItemSerializer

hazn_platform/orchestrator/api/urls.py
  - Remove hitl router registration

hazn_platform/orchestrator/api/serializers.py
  - Remove HITLItemSerializer class
  - Remove HITLItem import
  - Remove turn_count from WorkflowAgentSerializer.fields
  - Remove turn_count and hitl_items from WorkflowRunSerializer.fields
  - Remove hitl_items field declaration

config/settings/base.py
  - Remove "hazn_platform.qa" from LOCAL_APPS list (line 100)
```

### Agency Singleton Pattern

**Recommendation: Use CheckConstraint (not custom save() method)**

Django's `CheckConstraint` with `check=models.Q(pk=1)` is the most robust approach:

```python
class Agency(models.Model):
    # ... existing fields minus removed ones ...

    class Meta:
        verbose_name_plural = "agencies"
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(pk=1),
                name="singleton_agency",
            ),
        ]
```

However, since Agency uses UUIDField as primary key (not integer auto-increment), the `pk=1` pattern does not apply. For UUID PKs, the singleton pattern requires a different approach.

**For UUID-based singleton, use custom save() with a fixed UUID:**

```python
import uuid

SINGLETON_AGENCY_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

class Agency(models.Model):
    id = models.UUIDField(primary_key=True, default=SINGLETON_AGENCY_ID, editable=False)
    # ... fields ...

    def save(self, *args, **kwargs):
        self.pk = SINGLETON_AGENCY_ID
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "agencies"
        ordering = ["name"]
```

Or enforce at the database level using a UniqueConstraint on a constant expression. The simplest approach for UUID PKs:

```python
class Agency(models.Model):
    # ... fields ...

    def save(self, *args, **kwargs):
        if not self.pk:
            # Check if an Agency already exists
            if Agency.objects.exists():
                raise ValueError("Only one Agency instance is allowed.")
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Load the singleton Agency instance."""
        obj, _ = cls.objects.get_or_create(
            defaults={"name": "Default Agency", "slug": "default"}
        )
        return obj

    class Meta:
        verbose_name_plural = "agencies"
        ordering = ["name"]
```

**Recommendation:** Use the custom `save()` approach with existence check since it works with UUID PKs and is the least invasive change to the existing model. The fixed UUID approach is also viable but requires updating any existing Agency UUID references.

### Anti-Patterns to Avoid
- **Deleting QA app directory before migration:** Django needs the models.py present to generate the migration that removes the tables. Delete the app files AFTER squashing migrations.
- **Removing INSTALLED_APPS entry before migration:** The 'qa' app must remain in INSTALLED_APPS until its final migration (deleting models) is applied. Remove from INSTALLED_APPS only when squashing to fresh 0001_initial.
- **Editing executor.py imports now:** Per user decision, executor.py cleanup is deferred to Phase 4. Only add TODO comments to mark dead code.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Singleton enforcement | Custom middleware or signals | Model-level save() override with existence check | Database-level guarantee, works regardless of entry point (admin, shell, API) |
| Migration FK ordering | Manual SQL | Django's migration `dependencies` list | Django handles cross-app migration dependencies natively |
| Migration squashing | Hand-writing 0001_initial.py | Run `makemigrations` after deleting all migration files (except __init__.py) | Django regenerates a clean initial migration from current model state |

**Key insight:** For a fresh DB start, the cleanest squash approach is NOT `squashmigrations`. Instead: (1) apply all cleanup migrations to get models correct, (2) delete all migration files except `__init__.py`, (3) run `makemigrations` to generate fresh `0001_initial.py` per app. This produces clean migrations with no `replaces` list or elidable operations.

## Common Pitfalls

### Pitfall 1: Cross-App FK Dependencies in Migrations
**What goes wrong:** Deleting a model that has FK references from another app causes migration failures.
**Why it happens:** Django migrations track dependencies. Removing HITLItem before removing Deliverable.hitl_item FK causes `django.db.utils.IntegrityError`.
**How to avoid:** Follow the FK dependency map strictly. Remove FKs pointing TO a model before deleting that model. ShareLink -> Deliverable -> HITLItem must be unwound in that order.
**Warning signs:** `makemigrations` produces migration with `dependencies` referencing a deleted app.

### Pitfall 2: Dangling Imports After Model Deletion
**What goes wrong:** Runtime ImportError when code references deleted models/modules.
**Why it happens:** Many files import HITLItem, Deliverable, hitl module, conflict_detector. Missing one import causes the entire app to fail to start.
**How to avoid:** Use grep to find ALL import references before deleting. The grep search above identified every file that imports HITL/QA/conflict code.
**Warning signs:** `python manage.py check` fails, or test imports break.

### Pitfall 3: Serializer Fields Referencing Removed Model Fields
**What goes wrong:** DRF serializer `fields` list includes a field that no longer exists on the model, causing `ImproperlyConfigured` exception.
**Why it happens:** `turn_count` is removed from WorkflowRun and WorkflowAgent, but serializers still list it.
**How to avoid:** Update ALL serializer `fields` lists to match the new model schema. There are 4 serializers that reference `turn_count`: WorkflowRunListSerializer, WorkflowRunDetailSerializer, WorkflowAgentSerializer (workspace), and WorkflowRunSerializer/WorkflowRunListSerializer (orchestrator API).
**Warning signs:** Any DRF endpoint returns 500 with "field does not exist" error.

### Pitfall 4: WorkflowRun.Status.BLOCKED Left Orphaned
**What goes wrong:** WorkflowRun status enum includes BLOCKED (used for HITL pausing) which no longer has a trigger mechanism after HITL removal.
**Why it happens:** BLOCKED status was set when `has_blocking_items()` returned True. With HITL removed, nothing sets BLOCKED.
**How to avoid:** Keep BLOCKED in the enum for now -- it does no harm and Phase 4 (executor rewrite) will define the final status choices. Removing it risks breaking existing data or causing enum validation issues.
**Warning signs:** N/A -- keeping it is safe.

### Pitfall 5: ShareLink Model Depends on qa.Deliverable
**What goes wrong:** ShareLink has `deliverable = ForeignKey("qa.Deliverable")`. Deleting the QA app without handling ShareLink breaks the workspace app.
**Why it happens:** ShareLink was designed for the QA pipeline's deliverable sharing feature.
**How to avoid:** Either (a) delete ShareLink entirely (it's a QA-era feature), or (b) re-point it to WorkflowPhaseOutput. Since deliverable rendering is being preserved on WorkflowPhaseOutput (html_content/markdown_source fields), re-pointing makes sense if share functionality is desired in v3.0.
**Warning signs:** `makemigrations` fails with "Related model 'qa.Deliverable' cannot be resolved."

### Pitfall 6: DashboardView References Both HITLItem and Deliverable
**What goes wrong:** DashboardView.get() queries HITLItem.objects and Deliverable.objects for dashboard counts.
**Why it happens:** The dashboard showed pending_approvals (HITL) and ready_deliverables (QA).
**How to avoid:** Remove those two counts from the dashboard response. Update DashboardSerializer to remove the `pending_approvals` and `ready_deliverables` fields.
**Warning signs:** Dashboard endpoint returns 500.

### Pitfall 7: executor.py Has Non-Lazy Imports
**What goes wrong:** executor.py has top-level imports from conflict_detector, hitl, qa.runner, and qa.staging. Deleting those modules causes ImportError at module load time.
**Why it happens:** Unlike some other files, executor.py uses direct (non-lazy) imports at the top of the file.
**How to avoid:** Per user decision, mark these as TODO comments but do NOT delete the import lines. Instead, wrap them in try/except or comment them out with TODO markers pointing to Phase 4.
**Warning signs:** Celery worker fails to start because tasks.py imports executor.py which imports deleted modules.

## Code Examples

### Adding Fields to WorkflowPhaseOutput (schema-only since fresh DB)

```python
# In orchestrator/models.py, add to WorkflowPhaseOutput class:
class WorkflowPhaseOutput(models.Model):
    # ... existing fields ...
    html_content = models.TextField(blank=True, default="")
    markdown_source = models.TextField(blank=True, default="")
```

### Replacing IsAgencyMember with IsAuthenticated

```python
# Before (in workspace/views.py):
from hazn_platform.workspace.permissions import IsAgencyMember

class DashboardView(APIView):
    permission_classes = [IsAgencyMember]

# After:
from rest_framework.permissions import IsAuthenticated

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
```

### Agency Singleton Enforcement

```python
# In core/models.py:
class Agency(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    house_style = models.JSONField(default=dict, blank=True)
    methodology = models.JSONField(default=dict, blank=True)
    # tool_preferences REMOVED
    # churned_at REMOVED
    # deletion_notified_at REMOVED
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk and Agency.objects.exists():
            raise ValueError("Only one Agency instance is allowed.")
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Load the singleton Agency, creating default if needed."""
        obj, _ = cls.objects.get_or_create(
            defaults={"name": "Hazn", "slug": "hazn"}
        )
        return obj

    class Meta:
        verbose_name_plural = "agencies"
        ordering = ["name"]
```

### Handling executor.py Dead Imports (Phase 4 Deferred)

```python
# In orchestrator/executor.py, replace the top-level imports:

# TODO(Phase 4): Remove conflict detection -- executor rewrite from scratch
# from hazn_platform.orchestrator.conflict_detector import detect_conflicts
# from hazn_platform.orchestrator.conflict_detector import process_conflicts

# TODO(Phase 4): Remove HITL imports -- executor rewrite from scratch
# from hazn_platform.orchestrator.hitl import create_hitl_item
# from hazn_platform.orchestrator.hitl import has_blocking_items

# TODO(Phase 4): Remove QA imports -- executor rewrite from scratch
# from hazn_platform.qa.runner import create_deliverable
# from hazn_platform.qa.runner import get_task_type_for_phase
# from hazn_platform.qa.runner import handle_qa_result
# from hazn_platform.qa.runner import should_run_qa
# from hazn_platform.qa.staging import deploy_to_staging
```

Note: The executor.py body references these functions (detect_conflicts, process_conflicts, create_hitl_item, has_blocking_items, should_run_qa, create_deliverable, get_task_type_for_phase, deploy_to_staging, handle_qa_result). Commenting out the imports means the executor will raise NameError if called. This is acceptable because:
1. Phase 4 rewrites executor from scratch
2. The executor cannot run successfully anyway (QA app deleted, hitl module deleted)
3. The TODO comments clearly mark this as intentional dead code

### Fresh Migration Squash Procedure

```bash
# Step 1: Verify current state is clean
python manage.py makemigrations --check
python manage.py migrate

# Step 2: Delete all migration files (keep __init__.py)
find hazn_platform/*/migrations/ -name "*.py" ! -name "__init__.py" -delete
find hazn_platform/*/*/migrations/ -name "*.py" ! -name "__init__.py" -delete

# Step 3: Regenerate fresh initial migrations
python manage.py makemigrations

# Step 4: Verify -- should produce clean 0001_initial.py per app
python manage.py makemigrations --check

# Step 5: Verify against empty DB
python manage.py migrate --run-syncdb  # or create new test DB
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `squashmigrations` command | Delete + regenerate for fresh DB | Django 4.2+ best practice | Cleaner migrations, no `replaces` lists, no elidable RunPython |
| UniqueConstraint for singleton | CheckConstraint or save() override | Django 3.2+ (CheckConstraint) | More expressive constraints at DB level |
| Custom permission classes | IsAuthenticated (DRF built-in) | Always available | Simpler, less code to maintain |

**Deprecated/outdated:**
- `squashmigrations` for fresh DB scenarios: Generates overly complex migrations with `replaces` lists. For controlled environments, delete+regenerate is preferred.

## Open Questions

1. **ShareLink Fate**
   - What we know: ShareLink.deliverable FK points to qa.Deliverable. ShareLink is used for public share URLs of deliverables.
   - What's unclear: Whether share link functionality is needed in v3.0 at all.
   - Recommendation: Delete ShareLink model entirely. It's a QA-era feature. If needed later, it can be re-created pointing to WorkflowPhaseOutput. Simpler to delete now than maintain a zombie FK.

2. **WorkflowRunDetailSerializer hitl_items Nesting**
   - What we know: Both workspace and orchestrator API serializers include `hitl_items` as a nested relation on WorkflowRun.
   - What's unclear: Whether the orchestrator API (api/views.py, api/urls.py, api/serializers.py) should be cleaned up now or deferred to Phase 4 with executor.
   - Recommendation: Clean up the orchestrator API now -- the HITLItemViewSet in orchestrator/api/views.py and its URL registration are dead code once HITLItem is deleted. Unlike executor.py (which is being rewritten from scratch in Phase 4), the API views are standalone and can be cleanly removed.

3. **Celery Beat Schedule for check_hitl_timeouts**
   - What we know: `check_hitl_timeouts` task exists in tasks.py with a note about periodic scheduling via django-celery-beat.
   - What's unclear: Whether there's an existing celery-beat schedule entry that needs removal.
   - Recommendation: Remove the task from tasks.py. Check for any django-celery-beat PeriodicTask entries referencing it (may be DB-stored, not file-based).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 + pytest-django 4.12.0 |
| Config file | `hazn_platform/pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `cd hazn_platform && python -m pytest tests/test_orchestrator_models.py -x --no-header -q` |
| Full suite command | `cd hazn_platform && python -m pytest tests/ -x --no-header -q` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| STRP-02 | HITLItem model fully removed, no dangling references | unit | `cd hazn_platform && python -m pytest tests/test_orchestrator_models.py -x -q` | Yes (needs update) |
| STRP-02 | HITL views/serializers removed, endpoints return 404 | unit | `cd hazn_platform && python -m pytest tests/test_workspace_hitl.py -x -q` | Yes (DELETE this test) |
| STRP-03 | QA app fully removed, Deliverable model gone | unit | `cd hazn_platform && python -m pytest tests/test_qa_models.py -x -q` | Yes (DELETE this test) |
| STRP-03 | html_content/markdown_source on WorkflowPhaseOutput | unit | `cd hazn_platform && python -m pytest tests/test_orchestrator_models.py -x -q` | Yes (needs new test) |
| STRP-07 | conflict_detector.py fully removed | unit | `cd hazn_platform && python -m pytest tests/test_conflict_detector.py -x -q` | Yes (DELETE this test) |
| STRP-10 | Enterprise fields removed from models | unit | `cd hazn_platform && python -m pytest tests/test_models.py -x -q` | Yes (needs update) |
| STRP-10 | Agency singleton constraint enforced | unit | `cd hazn_platform && python -m pytest tests/test_models.py -x -q` | Yes (needs new test) |
| STRP-10 | IsAuthenticated replaces IsAgencyMember | unit | `cd hazn_platform && python -m pytest tests/test_workspace_clients.py tests/test_workspace_dashboard.py tests/test_workspace_workflows.py -x -q` | Yes (needs update) |
| STRP-10 | `makemigrations --check` produces no new migrations | smoke | `cd hazn_platform && python manage.py makemigrations --check` | N/A (CLI check) |
| ALL | Fresh migrations apply cleanly | smoke | `cd hazn_platform && python manage.py migrate --run-syncdb` | N/A (CLI check) |

### Sampling Rate
- **Per task commit:** `cd hazn_platform && python -m pytest tests/test_orchestrator_models.py tests/test_models.py -x -q`
- **Per wave merge:** `cd hazn_platform && python -m pytest tests/ -x -q`
- **Phase gate:** Full suite green + `python manage.py makemigrations --check` before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_orchestrator_models.py` -- needs new test for WorkflowPhaseOutput.html_content and .markdown_source fields
- [ ] `tests/test_models.py` -- needs new test for Agency singleton constraint
- [ ] `tests/test_workspace_clients.py` -- needs update: remove agency_role from user creation, use IsAuthenticated
- [ ] `tests/test_workspace_dashboard.py` -- needs update: remove pending_approvals and ready_deliverables assertions
- [ ] Tests to DELETE: test_conflict_detector.py, test_hitl.py, test_hitl_api.py, test_qa_models.py, test_qa_runner.py, test_qa_approval.py, test_qa_criteria.py, test_qa_staging.py, test_workspace_hitl.py, test_workspace_deliverables.py

## Sources

### Primary (HIGH confidence)
- Codebase inspection: All model files, views, serializers, URLs, admin, executor, tasks, permissions, filters read directly
- Django documentation: Migration squashing, CheckConstraint, model Meta options

### Secondary (MEDIUM confidence)
- [Django migrations documentation](https://docs.djangoproject.com/en/6.0/topics/migrations/) - squashing and dependency management
- [Adam Johnson: CheckConstraint for singleton](https://adamj.eu/tech/2021/02/04/django-check-constraints-limit-model-single-instance/) - singleton pattern with constraints
- [Johnny Metz: Better migration squashing](https://johnnymetz.com/posts/squash-django-migrations/) - delete+regenerate approach for fresh DB

### Tertiary (LOW confidence)
- None -- all findings verified against codebase

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new libraries, all existing Django/DRF patterns
- Architecture: HIGH -- FK dependency map verified by reading every model and import
- Pitfalls: HIGH -- every pitfall identified from actual code references via grep
- Migration strategy: HIGH -- fresh DB start simplifies to delete+regenerate pattern

**Research date:** 2026-03-12
**Valid until:** 2026-04-12 (stable -- Django migration patterns are mature)

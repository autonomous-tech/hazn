# Phase 5: Mode 1 Validation & QA - Research

**Researched:** 2026-03-06
**Domain:** QA agent integration into workflow DAG, HITL approval gates with configurable timeouts, Vercel preview URL staging, GDPR-compliant data lifecycle enforcement (retention, deletion, notification)
**Confidence:** HIGH

## Summary

Phase 5 transforms Hazn from a development platform into a production-validated system by adding three capabilities: (1) a QA Tester agent that automatically inspects every deliverable before it is marked done, with scoring criteria specific to each task type, (2) approval gates with 48-hour timeouts (upgrading the existing 24-hour HITL system), and (3) data lifecycle enforcement covering 90-day post-churn retention, GDPR 30-day deletion on request, and independent L3 deletion with client notification.

The existing codebase provides strong foundations. The HITL system (hitl.py) already supports configurable timeout_hours per item, timeout_action defaults, and periodic processing via Celery beat. The Vercel MCP server (vercel_server.py) already has `deploy_project`, `get_preview_url`, and `get_deployment_status` tools. The QA Tester agent definition (agents/qa-tester.md) specifies a complete scoring rubric (0-100 with weighted categories and PASS/CONDITIONAL PASS/FAIL thresholds). The workflow YAML schema (WorkflowPhaseSchema) supports agent assignment, dependencies, and tool scoping. What is missing: (1) a programmatic QA criteria registry per task type, (2) automatic injection of QA phases into workflows, (3) a new HITL trigger type for deliverable approval with 48-hour timeout, (4) data lifecycle models and management commands, and (5) Celery periodic tasks for retention enforcement.

**Primary recommendation:** Add a `qa` Django app containing QA criteria definitions per task type (Pydantic schemas), a Deliverable model linking phase outputs to QA verdicts and approval status, lifecycle fields on Agency/EndClient (churned_at, deletion_requested_at, deletion_scheduled_at), and three management commands (enforce_retention, process_deletion_requests, notify_pending_deletions). Wire the QA Tester agent as a mandatory post-phase in the executor. Extend HITLItem with a `deliverable_approval` trigger type with 48-hour default timeout.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| QA-01 | QA Tester agent runs on every deliverable before marking done | Existing qa-tester.md agent definition + WorkflowExecutor supports post-phase execution. Add automatic QA phase injection after deliverable-producing phases |
| QA-02 | Production-ready criteria defined per task type (analytics, landing page, full site, blog, email, bug fix) | QA criteria registry as Pydantic models with task-type-specific checklist items, weights, and pass/fail thresholds |
| QA-03 | Every approval gate has 48-hour timeout with default action | Existing HITL system supports configurable timeout_hours. Add `deliverable_approval` trigger type with 48-hour default. Change approval gate HITL items from 24h to 48h |
| QA-04 | Staging = Vercel preview URLs in v1 | Existing mcp-vercel server has deploy_project and get_preview_url tools. Wire executor to deploy to Vercel after build phases and store preview URL on Deliverable model |
| DATA-01 | Maximum 90-day retention post-churn | Add churned_at field on Agency. Celery periodic task finds agencies where churned_at + 90 days < now and hard-deletes all related data (CASCADE on EndClient handles relations) |
| DATA-02 | GDPR on-request deletion within 30 days | Add deletion_requested_at on EndClient. Management command processes requests older than processing period, deletes client data, clears Vault secrets, purges Letta archival |
| DATA-03 | L3 deletion is independent of L2 churn | EndClient has its own lifecycle fields. Deleting an L3 does not affect the L2 agency or other L3 clients under it |
| DATA-04 | Client notified at churn + 30 days before deletion | Celery periodic task finds agencies at churn + 30 days, sends notification via deliver_webhook task (already exists), logs notification in audit trail |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| django | 5.2.12 | Web framework, ORM, management commands | Already the project framework |
| celery | 5.6.2 | Async tasks and periodic beat scheduling | Already used for workflow execution and HITL timeouts |
| django-celery-beat | 2.9.0 | Database-backed periodic task schedules | Already in INSTALLED_APPS with DatabaseScheduler configured |
| pydantic | >=2.0 | QA criteria schema validation | Already a transitive dependency via fastmcp and letta-client |
| djangorestframework | 3.16.0 | API serializers for QA/deliverable endpoints | Already installed |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| hvac | 2.4.0 | Vault secret deletion during data lifecycle | Already installed; used for deleting secrets on client deletion |
| letta-client | >=1.7.11 | Archival memory purge during data lifecycle | Already installed; needed for purging agent memory on deletion |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Custom QA criteria registry | django-gdpr-assist for lifecycle | Only handles GDPR, not QA. We need both QA and lifecycle in this phase |
| Management commands for lifecycle | Celery tasks only | Management commands are testable standalone, can be called from Celery tasks, and work for manual operations |
| Hard delete for data lifecycle | Soft delete (deleted_at flag) | Hard delete is simpler and aligns with GDPR "right to erasure". Audit trail in MemoryCorrection and workflow_runs provides historical reference |

**Installation:**
```bash
# No new dependencies needed -- all libraries are already in pyproject.toml
```

## Architecture Patterns

### Recommended Project Structure
```
hazn_platform/
  hazn_platform/
    qa/                         # NEW Django app
      __init__.py
      apps.py
      models.py                 # Deliverable, QAReport
      criteria.py               # QA criteria registry (Pydantic schemas per task type)
      runner.py                 # QA agent integration into workflow executor
      admin.py
      migrations/
    core/
      models.py                 # ADD: churned_at on Agency, deletion_requested_at on EndClient
      lifecycle.py              # NEW: data lifecycle enforcement functions
    orchestrator/
      hitl.py                   # EXTEND: deliverable_approval trigger type, 48h default
      executor.py               # EXTEND: automatic QA phase injection after deliverable phases
      tasks.py                  # EXTEND: periodic lifecycle tasks
    management/
      commands/
        enforce_retention.py    # NEW: 90-day post-churn hard delete
        process_deletions.py    # NEW: GDPR deletion request processing
        notify_deletions.py     # NEW: churn+30 notification
```

### Pattern 1: QA Criteria Registry (Pydantic Schemas per Task Type)
**What:** Define production-ready QA criteria as Pydantic models, one per task type. Each criterion has a name, weight, pass threshold, and check description. The QA agent receives the criteria as structured context when inspecting a deliverable.
**When to use:** Every time the QA Tester agent runs on a deliverable.
**Example:**
```python
# qa/criteria.py
from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field


class TaskType(str, Enum):
    ANALYTICS = "analytics"
    LANDING_PAGE = "landing_page"
    FULL_SITE = "full_site"
    BLOG = "blog"
    EMAIL = "email"
    BUG_FIX = "bug_fix"


class QACriterion(BaseModel):
    """A single QA check item."""
    name: str
    description: str
    weight: float = Field(ge=0, le=1.0)
    pass_threshold: int = Field(default=75, ge=0, le=100)


class QACriteria(BaseModel):
    """Complete QA criteria for a task type."""
    task_type: TaskType
    criteria: list[QACriterion]
    overall_pass_threshold: int = 90
    conditional_pass_threshold: int = 75

    def total_weight(self) -> float:
        return sum(c.weight for c in self.criteria)


# Registry: task_type -> QACriteria
QA_CRITERIA_REGISTRY: dict[TaskType, QACriteria] = {
    TaskType.LANDING_PAGE: QACriteria(
        task_type=TaskType.LANDING_PAGE,
        criteria=[
            QACriterion(
                name="Mobile Responsiveness",
                description="Layout renders correctly at 375px. No overflow, no truncation.",
                weight=0.30,
            ),
            QACriterion(
                name="CTA Visibility & Function",
                description="Primary CTA visible above fold on mobile. All CTAs tappable (44px min).",
                weight=0.25,
            ),
            QACriterion(
                name="Content Completeness",
                description="All sections from blueprint present. No Lorem Ipsum. No broken images.",
                weight=0.20,
            ),
            QACriterion(
                name="Visual Quality",
                description="Fonts loaded. Sufficient contrast. Consistent spacing.",
                weight=0.15,
            ),
            QACriterion(
                name="Technical Basics",
                description="Page title set. Meta description present. No console errors.",
                weight=0.10,
            ),
        ],
    ),
    TaskType.BLOG: QACriteria(
        task_type=TaskType.BLOG,
        criteria=[
            QACriterion(
                name="SEO Optimization",
                description="Primary keyword in title, H1, meta description. Proper header hierarchy.",
                weight=0.30,
            ),
            QACriterion(
                name="Content Quality",
                description="1500+ words. No filler. Clear structure. FAQ section with schema.",
                weight=0.30,
            ),
            QACriterion(
                name="Internal Linking",
                description="At least 3 internal links. No broken links.",
                weight=0.15,
            ),
            QACriterion(
                name="Readability",
                description="Short paragraphs. Scannable headers. Appropriate reading level.",
                weight=0.15,
            ),
            QACriterion(
                name="Technical",
                description="Structured data present. Images have alt text. Slug matches target.",
                weight=0.10,
            ),
        ],
    ),
    # Additional task types: ANALYTICS, FULL_SITE, EMAIL, BUG_FIX
    # follow the same pattern with domain-specific criteria
}


def get_criteria(task_type: str) -> QACriteria | None:
    """Look up QA criteria for a task type."""
    try:
        return QA_CRITERIA_REGISTRY[TaskType(task_type)]
    except (ValueError, KeyError):
        return None
```

### Pattern 2: Deliverable Model Linking Phase Outputs to QA
**What:** A Deliverable model tracks every deliverable produced by a workflow phase, its QA status, approval status, preview URL, and QA report. This is the central record that QA-01 through QA-04 operate on.
**When to use:** Created by the executor after a phase produces outputs. Updated by QA agent with verdict. Updated by approval flow with resolution.
**Example:**
```python
# qa/models.py
import uuid
from django.db import models


class Deliverable(models.Model):
    """A deliverable produced by a workflow phase, subject to QA and approval."""

    class QAVerdict(models.TextChoices):
        PENDING = "pending"
        PASS = "pass"
        CONDITIONAL_PASS = "conditional_pass"
        FAIL = "fail"

    class ApprovalStatus(models.TextChoices):
        PENDING_QA = "pending_qa"
        PENDING_APPROVAL = "pending_approval"
        APPROVED = "approved"
        REJECTED = "rejected"
        AUTO_APPROVED = "auto_approved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_run = models.ForeignKey(
        "orchestrator.WorkflowRun",
        on_delete=models.CASCADE,
        related_name="deliverables",
    )
    phase_output = models.OneToOneField(
        "orchestrator.WorkflowPhaseOutput",
        on_delete=models.CASCADE,
        related_name="deliverable",
    )
    task_type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    preview_url = models.URLField(blank=True, default="")
    vercel_deployment_id = models.CharField(max_length=255, blank=True, default="")
    qa_verdict = models.CharField(
        max_length=20,
        choices=QAVerdict.choices,
        default=QAVerdict.PENDING,
    )
    qa_score = models.IntegerField(null=True, blank=True)
    qa_report = models.JSONField(default=dict, blank=True)
    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING_QA,
    )
    hitl_item = models.ForeignKey(
        "orchestrator.HITLItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deliverables",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.qa_verdict}/{self.approval_status})"
```

### Pattern 3: Automatic QA Phase Injection in Executor
**What:** After each deliverable-producing phase completes, the executor automatically runs the QA Tester agent on the output. The QA phase is not in the workflow YAML -- it is injected by the executor as a mandatory post-phase step. This ensures QA-01 (QA runs on every deliverable before marking done) without requiring workflow authors to remember to add QA phases.
**When to use:** Every workflow phase that produces outputs and has an agent.
**Example:**
```python
# qa/runner.py
from __future__ import annotations
import logging
from hazn_platform.qa.criteria import get_criteria
from hazn_platform.qa.models import Deliverable

logger = logging.getLogger(__name__)


def should_run_qa(phase) -> bool:
    """Determine if a phase's output needs QA.

    QA runs on phases that have an agent AND produce outputs.
    Informational phases (no agent) and phases without outputs skip QA.
    """
    return bool(phase.agent and phase.outputs)


def get_task_type_for_phase(phase) -> str:
    """Map a workflow phase to a QA task type.

    Uses heuristics based on phase ID, agent type, and output patterns.
    """
    phase_id = phase.id.lower()
    agent = (phase.agent or "").lower()

    if "analytics" in phase_id or "audit" in phase_id:
        return "analytics"
    if "landing" in phase_id:
        return "landing_page"
    if "dev" in phase_id or "build" in phase_id:
        return "full_site"
    if "blog" in phase_id or "content" in phase_id or "writing" in phase_id:
        return "blog"
    if "email" in phase_id:
        return "email"
    if "fix" in phase_id or "bug" in phase_id:
        return "bug_fix"
    # Default to full_site for developer agent, blog for content-writer
    if agent == "developer":
        return "full_site"
    if agent == "content-writer":
        return "blog"
    return "full_site"  # conservative default


def create_deliverable(
    workflow_run,
    phase_output,
    phase,
    preview_url: str = "",
    deployment_id: str = "",
) -> Deliverable:
    """Create a Deliverable record for a phase output."""
    task_type = get_task_type_for_phase(phase)
    return Deliverable.objects.create(
        workflow_run=workflow_run,
        phase_output=phase_output,
        task_type=task_type,
        title=f"{phase.name} deliverable",
        preview_url=preview_url,
        vercel_deployment_id=deployment_id,
    )
```

### Pattern 4: Data Lifecycle Fields and Enforcement
**What:** Add lifecycle timestamps to Agency (churned_at) and EndClient (deletion_requested_at, deletion_scheduled_at). Celery periodic tasks check these fields and perform cascading hard deletes with Vault secret cleanup and Letta archival purge.
**When to use:** Churn processing, GDPR deletion requests, scheduled retention enforcement.
**Example:**
```python
# core/lifecycle.py
from __future__ import annotations
import logging
from datetime import timedelta
from django.utils import timezone
from hazn_platform.core.models import Agency, EndClient

logger = logging.getLogger(__name__)

RETENTION_DAYS = 90
GDPR_DELETION_DAYS = 30
NOTIFICATION_DAYS = 30  # churn + 30 days = send warning


def get_agencies_for_retention_deletion():
    """Find agencies whose data should be deleted (churned_at + 90 days past)."""
    cutoff = timezone.now() - timedelta(days=RETENTION_DAYS)
    return Agency.objects.filter(
        churned_at__isnull=False,
        churned_at__lte=cutoff,
    )


def get_clients_for_gdpr_deletion():
    """Find end clients with pending GDPR deletion requests past processing period."""
    cutoff = timezone.now() - timedelta(days=GDPR_DELETION_DAYS)
    return EndClient.objects.filter(
        deletion_requested_at__isnull=False,
        deletion_requested_at__lte=cutoff,
    )


def get_agencies_for_notification():
    """Find agencies at churn + 30 days that haven't been notified."""
    notify_cutoff = timezone.now() - timedelta(days=NOTIFICATION_DAYS)
    return Agency.objects.filter(
        churned_at__isnull=False,
        churned_at__lte=notify_cutoff,
        deletion_notified_at__isnull=True,
    )


def delete_client_data(client: EndClient) -> dict:
    """Hard-delete all data for an end client.

    Deletes in order:
    1. Vault secrets (via hvac)
    2. Letta archival memory (via letta-client)
    3. Postgres records (CASCADE from EndClient delete)

    Returns summary of what was deleted.
    """
    summary = {"client_id": str(client.pk), "client_name": client.name}

    # 1. Delete Vault secrets
    from hazn_platform.core.vault import delete_secret
    vault_creds = client.vault_credentials.all()
    for cred in vault_creds:
        try:
            delete_secret(cred.vault_secret_id)
        except Exception:
            logger.warning(
                "Failed to delete Vault secret %s for client %s",
                cred.vault_secret_id,
                client.pk,
            )
    summary["vault_secrets_deleted"] = vault_creds.count()

    # 2. Purge Letta archival memory
    # Agent naming convention: {agent_type}--{l3_client_id}
    # Find and purge all agents for this client
    summary["letta_agents_purged"] = _purge_letta_memory(str(client.pk))

    # 3. Hard delete the EndClient (CASCADE deletes related records)
    client.delete()
    summary["postgres_deleted"] = True

    logger.info("Client data deleted: %s", summary)
    return summary


def _purge_letta_memory(l3_client_id: str) -> int:
    """Purge all Letta archival passages for agents associated with a client."""
    try:
        from hazn_platform.core.letta_client import get_letta_client
        letta = get_letta_client()
        agents = letta.agents.list()
        purged = 0
        for agent in agents:
            if agent.name and agent.name.endswith(f"--{l3_client_id}"):
                # Delete agent entirely (includes archival memory)
                letta.agents.delete(agent.id)
                purged += 1
        return purged
    except Exception:
        logger.warning(
            "Failed to purge Letta memory for client %s",
            l3_client_id,
            exc_info=True,
        )
        return 0
```

### Pattern 5: HITL Deliverable Approval with 48-Hour Timeout
**What:** Extend the existing HITL system with a `deliverable_approval` trigger type. When a deliverable passes QA (PASS or CONDITIONAL_PASS), create a blocking HITL item with 48-hour timeout. The default timeout action is `auto_approve` -- if nobody reviews within 48 hours, the deliverable is automatically approved.
**When to use:** After QA Tester agent returns a PASS or CONDITIONAL_PASS verdict.
**Example:**
```python
# In orchestrator/hitl.py -- extend DEFAULT_TIMEOUT_ACTIONS
DEFAULT_TIMEOUT_ACTIONS: dict[str, str] = {
    "conflict": "l3_wins",
    "checkpoint": "auto_approve",
    "cost_alert": "halt",
    "uncertainty": "proceed_with_warning",
    "deliverable_approval": "auto_approve",  # NEW
}

# In qa/runner.py -- create approval HITL item after QA pass
def submit_for_approval(deliverable, workflow_run) -> HITLItem:
    """Create a deliverable approval HITL item with 48-hour timeout."""
    from hazn_platform.orchestrator.hitl import create_hitl_item

    item = create_hitl_item(
        workflow_run=workflow_run,
        trigger_type="deliverable_approval",
        title=f"Approve: {deliverable.title}",
        details={
            "deliverable_id": str(deliverable.pk),
            "task_type": deliverable.task_type,
            "qa_verdict": deliverable.qa_verdict,
            "qa_score": deliverable.qa_score,
            "preview_url": deliverable.preview_url,
        },
        is_blocking=True,
        timeout_hours=48,  # QA-03: 48-hour timeout
    )
    deliverable.hitl_item = item
    deliverable.approval_status = Deliverable.ApprovalStatus.PENDING_APPROVAL
    deliverable.save(update_fields=["hitl_item", "approval_status"])
    return item
```

### Anti-Patterns to Avoid
- **Adding QA phases to workflow YAML:** Workflow authors should NOT have to add QA phases manually. The executor injects them automatically. This ensures QA-01 (QA runs on EVERY deliverable).
- **Soft delete for GDPR data:** GDPR "right to erasure" means actual deletion. Soft delete (setting a flag) does not satisfy Article 17. Use hard delete with pre-deletion audit logging.
- **Deleting Postgres without Vault/Letta cleanup:** Data exists in three places (Postgres, Vault, Letta archival). Deleting only from Postgres leaves orphaned secrets and memory passages. The lifecycle module must clean all three.
- **Single-threaded deletion jobs:** For large agencies with many clients, deletion should be parallelized. Use Celery task fanout: one parent task iterates clients, spawns a child task per client deletion.
- **Hardcoding timeout hours:** Use the existing configurable `timeout_hours` field on HITLItem. Different agencies may want different timeout windows.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Periodic task scheduling | Custom cron scripts or sleep loops | django-celery-beat DatabaseScheduler | Already configured; supports interval and crontab schedules via Django admin |
| QA scoring math | Manual weighted average calculation | Pydantic model with computed properties | Type-safe, validated, serializable criteria definitions |
| Cascade deletion | Manual query for every related model | Django ORM CASCADE on_delete | All models already use CASCADE FKs from EndClient. One `client.delete()` cascades to keywords, audits, campaigns, decisions, brand voices, approved copies, memory corrections |
| Webhook notification | Custom HTTP client for notifications | Existing `deliver_webhook` Celery task | Already has exponential backoff, 5 retries, proper error handling |
| Preview URL generation | Custom Vercel API integration | Existing `mcp-vercel` get_preview_url tool | Already implemented, tested, and handles auth via Vault |

**Key insight:** Phase 5 is primarily a wiring and policy phase. The underlying capabilities (HITL, Vercel deploy, Celery beat, CASCADE deletion) already exist. The work is defining QA criteria, creating the Deliverable model, injecting QA into the executor, adding lifecycle fields, and writing management commands that orchestrate the existing primitives.

## Common Pitfalls

### Pitfall 1: QA Agent Blocking Workflow Completion
**What goes wrong:** If the QA agent's execution is treated as a required phase and it fails (e.g., agent error, not a QA FAIL), the entire workflow fails instead of just the QA step.
**Why it happens:** Confusing QA agent execution failure (infrastructure error) with QA verdict FAIL (deliverable quality issue).
**How to avoid:** Separate execution errors from QA verdicts. If the QA agent crashes, log the error, set QA verdict to PENDING (not FAIL), and allow manual QA. Only FAIL the workflow if a required deliverable gets a FAIL verdict.
**Warning signs:** Workflows failing with QA-related stack traces despite the deliverable being fine.

### Pitfall 2: CASCADE Delete Ordering with Vault
**What goes wrong:** Django CASCADE deletes the VaultCredential record before the code reads vault_secret_id to delete from Vault. The Vault secret becomes orphaned.
**Why it happens:** Django's deletion collector deletes in dependency order. If lifecycle code calls `client.delete()` before iterating vault_credentials, the credentials are gone.
**How to avoid:** Always delete external resources (Vault, Letta) BEFORE calling `client.delete()`. The pattern is: (1) fetch vault_credential.vault_secret_id list, (2) delete from Vault, (3) purge Letta agents, (4) call `client.delete()`.
**Warning signs:** Vault secrets accumulating over time despite clients being deleted.

### Pitfall 3: Data Lifecycle Race Conditions
**What goes wrong:** A retention enforcement job starts deleting client data while a workflow is actively running for that client.
**Why it happens:** Celery tasks are async. The retention job and a workflow run can overlap.
**How to avoid:** Check for active workflow runs before deletion. If any WorkflowRun with status RUNNING or BLOCKED exists for the client, skip deletion and retry next cycle. Add a guard: `WorkflowRun.objects.filter(end_client=client, status__in=["running", "blocked"]).exists()`.
**Warning signs:** Workflow failures with "does not exist" errors on models that should be there.

### Pitfall 4: HITL Timeout Not Updated to 48 Hours
**What goes wrong:** Existing HITL items continue to use 24-hour timeouts because the `create_hitl_item` function has `timeout_hours=24` as default, and callers forget to pass 48.
**Why it happens:** The default parameter was set for Phase 3's conflict resolution use case (24h). Phase 5 needs 48h for deliverable approval (QA-03).
**How to avoid:** Do NOT change the default for existing trigger types. Add `deliverable_approval` with its own default of 48h in the create function logic. The `timeout_hours` parameter should be set by the trigger type's default, not hardcoded in every call site.
**Warning signs:** Approval items timing out at 24 hours instead of 48.

### Pitfall 5: Letta Agent Deletion API Differences
**What goes wrong:** Calling `letta.agents.delete(agent_id)` may fail if the agent has active sessions or the API signature has changed.
**Why it happens:** Letta is pre-1.0 (per blockers in STATE.md). The API may change between versions.
**How to avoid:** Wrap all Letta deletion calls in try/except. Log failures but do not block the overall deletion. Orphaned Letta agents are less critical than orphaned Vault secrets. Pin the letta-client version.
**Warning signs:** Deletion management command completing but Letta agents still listed.

### Pitfall 6: Missing Notification Before Deletion
**What goes wrong:** Agency data is deleted at churn + 90 days without the agency ever receiving the churn + 30 day warning notification.
**Why it happens:** The notification task and the deletion task run independently. If the notification task was down or the webhook URL was invalid, the warning was never delivered.
**How to avoid:** Make deletion conditional on notification. Store `deletion_notified_at` on the Agency model. The retention enforcement command MUST check that `deletion_notified_at` is not null before proceeding with deletion. If not notified, notify first and wait until the next cycle.
**Warning signs:** Agencies complaining about data loss without warning.

## Code Examples

### Management Command: Enforce Retention
```python
# core/management/commands/enforce_retention.py
from django.core.management.base import BaseCommand
from hazn_platform.core.lifecycle import (
    get_agencies_for_retention_deletion,
    delete_client_data,
)


class Command(BaseCommand):
    help = "Delete data for agencies past 90-day post-churn retention"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without deleting",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        agencies = get_agencies_for_retention_deletion()

        if not agencies.exists():
            self.stdout.write("No agencies past retention period")
            return

        for agency in agencies:
            # Check notification was sent (DATA-04)
            if agency.deletion_notified_at is None:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping {agency.name}: not yet notified"
                    )
                )
                continue

            if dry_run:
                client_count = agency.end_clients.count()
                self.stdout.write(
                    f"[DRY RUN] Would delete {agency.name}: "
                    f"{client_count} clients"
                )
                continue

            # Delete all L3 clients for this agency
            for client in agency.end_clients.all():
                # Guard: skip if active workflows
                from hazn_platform.orchestrator.models import WorkflowRun
                active = WorkflowRun.objects.filter(
                    end_client=client,
                    status__in=["running", "blocked"],
                ).exists()
                if active:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Skipping {client.name}: active workflows"
                        )
                    )
                    continue
                delete_client_data(client)

            # Delete the agency itself (after all clients removed)
            agency.delete()
            self.stdout.write(
                self.style.SUCCESS(f"Deleted agency: {agency.name}")
            )
```

### Celery Periodic Task Registration
```python
# In orchestrator/tasks.py -- add periodic lifecycle tasks

@shared_task
def enforce_data_retention() -> dict:
    """Periodic task: enforce 90-day post-churn data retention.

    Should be scheduled to run daily via django-celery-beat.
    """
    from django.core.management import call_command
    from io import StringIO

    out = StringIO()
    call_command("enforce_retention", stdout=out)
    return {"output": out.getvalue()}


@shared_task
def process_gdpr_deletions() -> dict:
    """Periodic task: process GDPR deletion requests past 30 days.

    Should be scheduled to run daily via django-celery-beat.
    """
    from django.core.management import call_command
    from io import StringIO

    out = StringIO()
    call_command("process_deletions", stdout=out)
    return {"output": out.getvalue()}


@shared_task
def send_deletion_notifications() -> dict:
    """Periodic task: notify agencies at churn + 30 days.

    Should be scheduled to run daily via django-celery-beat.
    """
    from hazn_platform.core.lifecycle import get_agencies_for_notification
    from hazn_platform.orchestrator.tasks import deliver_webhook
    from django.utils import timezone

    agencies = get_agencies_for_notification()
    notified = 0

    for agency in agencies:
        webhook_url = agency.tool_preferences.get("webhook_url")
        if webhook_url:
            deliver_webhook.delay(
                url=webhook_url,
                payload={
                    "event": "deletion_warning",
                    "agency_id": str(agency.pk),
                    "agency_name": agency.name,
                    "churned_at": agency.churned_at.isoformat(),
                    "deletion_scheduled": (
                        agency.churned_at + timedelta(days=90)
                    ).isoformat(),
                    "message": (
                        "Your data will be permanently deleted 60 days from now. "
                        "Contact support to reactivate your account."
                    ),
                },
            )
        agency.deletion_notified_at = timezone.now()
        agency.save(update_fields=["deletion_notified_at"])
        notified += 1

    return {"notified": notified}
```

### Vault Secret Deletion Helper
```python
# In core/vault.py -- add delete_secret function
def delete_secret(path: str) -> bool:
    """Delete a secret from Vault.

    Uses the metadata endpoint to permanently destroy all versions.

    Parameters
    ----------
    path:
        The Vault secret path (e.g., 'agencies/uuid/ga4').

    Returns
    -------
    bool
        True if deleted successfully, False on error.
    """
    try:
        client = _get_vault_client()
        # For KV v2: delete metadata destroys all versions
        client.secrets.kv.v2.delete_metadata_and_all_versions(
            path=path,
            mount_point="secret",
        )
        return True
    except Exception:
        logger.warning(
            "Failed to delete Vault secret at %s",
            path,
            exc_info=True,
        )
        return False
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual QA by humans | LLM-based QA agent with structured criteria | 2024-2025 | Automated QA on every deliverable; consistent scoring; reduced review bottleneck |
| GDPR deletion as ad-hoc process | Automated lifecycle enforcement with management commands | Django best practice | Repeatable, auditable, scheduled deletion with dry-run support |
| Flat webhook notifications | Celery task with exponential backoff | Already implemented | Reliable delivery with retry; webhook failures don't block deletion |
| Single timeout for all HITL items | Per-trigger-type configurable timeouts | Phase 3 foundation | Different approval workflows get appropriate timeout windows |

**Deprecated/outdated:**
- Soft delete for GDPR compliance: Django soft-delete libraries (django-softdelete) do NOT satisfy GDPR Article 17. Use hard delete with pre-deletion audit logging
- Manual workflow YAML QA phases: Do not rely on workflow authors to add QA -- inject automatically in executor

## Open Questions

1. **Vault Secret Deletion API Path Format**
   - What we know: Secrets are stored at paths like `secret/data/agencies/{uuid}/ga4`. The hvac client uses `client.secrets.kv.v2.delete_metadata_and_all_versions(path=...)`.
   - What's unclear: Whether the `vault_secret_id` stored in VaultCredential includes the `secret/data/` prefix or just the logical path.
   - Recommendation: Inspect existing VaultCredential records to determine the path format. The `delete_secret` function should handle both formats.

2. **QA Agent Execution Mechanism**
   - What we know: The executor currently stubs LLM interaction (per Phase 3 notes). QA agent needs to actually send messages to a Letta agent and get structured QA report output.
   - What's unclear: Whether Letta message API is fully wired by Phase 5's start (depends on Phase 4 completion and actual LLM integration).
   - Recommendation: Design QA runner to work with either (a) real Letta agent execution or (b) a stub that returns a default PASS for testing. Use a feature flag or environment variable to switch modes.

3. **Email Notification vs Webhook for DATA-04**
   - What we know: The existing `deliver_webhook` task sends JSON payloads to webhook URLs. DATA-04 says "client notified at churn + 30 days."
   - What's unclear: Whether "notification" means webhook, email, or both. The current system only has webhooks.
   - Recommendation: Use webhooks for v1 (already implemented). The webhook payload can trigger email sending on the agency's side. Direct email would require adding django-anymail configuration (already installed but not configured for transactional email).

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
| QA-01 | QA runner invoked on every deliverable-producing phase | unit | `pytest tests/test_qa_runner.py -x` | Wave 0 |
| QA-02 | QA criteria exist for all 6 task types with correct weights | unit | `pytest tests/test_qa_criteria.py -x` | Wave 0 |
| QA-03 | Deliverable approval HITL item created with 48h timeout | unit | `pytest tests/test_qa_approval.py -x` | Wave 0 |
| QA-04 | Deliverable model stores preview_url from Vercel deployment | unit | `pytest tests/test_qa_models.py -x` | Wave 0 |
| DATA-01 | enforce_retention deletes agencies past 90 days post-churn | unit | `pytest tests/test_data_lifecycle.py::TestRetentionEnforcement -x` | Wave 0 |
| DATA-02 | process_deletions handles GDPR requests past 30 days | unit | `pytest tests/test_data_lifecycle.py::TestGDPRDeletion -x` | Wave 0 |
| DATA-03 | L3 deletion independent of L2 (delete client without agency) | unit | `pytest tests/test_data_lifecycle.py::TestIndependentL3Deletion -x` | Wave 0 |
| DATA-04 | notify_deletions sends webhook at churn + 30 days | unit | `pytest tests/test_data_lifecycle.py::TestDeletionNotification -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `cd hazn_platform && python -m pytest tests/ -x -q --no-header`
- **Per wave merge:** `cd hazn_platform && python -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_qa_runner.py` -- covers QA-01 (QA auto-injection, should_run_qa logic)
- [ ] `tests/test_qa_criteria.py` -- covers QA-02 (all 6 task type criteria exist, weights sum to 1.0)
- [ ] `tests/test_qa_approval.py` -- covers QA-03 (48h timeout HITL item creation, auto-approve on timeout)
- [ ] `tests/test_qa_models.py` -- covers QA-04 (Deliverable model with preview_url, QA verdict fields)
- [ ] `tests/test_data_lifecycle.py` -- covers DATA-01 through DATA-04 (retention, GDPR, independent L3, notification)
- [ ] Migration for new `qa` app models (Deliverable)
- [ ] Migration for Agency.churned_at, Agency.deletion_notified_at fields
- [ ] Migration for EndClient.deletion_requested_at, EndClient.deletion_scheduled_at fields
- [ ] New `qa` app registered in INSTALLED_APPS

## Sources

### Primary (HIGH confidence)
- Existing codebase: `orchestrator/hitl.py` (HITL system with configurable timeouts, trigger types, timeout actions)
- Existing codebase: `orchestrator/executor.py` (DAG-based workflow execution with phase outputs)
- Existing codebase: `orchestrator/models.py` (HITLItem with timeout_hours, WorkflowPhaseOutput)
- Existing codebase: `orchestrator/tasks.py` (check_hitl_timeouts periodic task, deliver_webhook with retry)
- Existing codebase: `mcp_servers/vercel_server.py` (deploy_project, get_preview_url tools)
- Existing codebase: `core/models.py` (Agency, EndClient, VaultCredential with CASCADE FKs)
- Existing codebase: `agents/qa-tester.md` (QA scoring rubric: weighted categories, PASS/CONDITIONAL/FAIL thresholds)
- Existing codebase: `config/settings/base.py` (CELERY_BEAT_SCHEDULER = DatabaseScheduler, django_celery_beat in INSTALLED_APPS)
- Existing codebase: `orchestrator/workflow_models.py` (WorkflowPhaseSchema with agent, outputs, required fields)
- [Django documentation on CASCADE delete](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.CASCADE) -- CASCADE behavior for ForeignKey on_delete
- [Celery periodic tasks documentation](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html) -- crontab and interval schedule configuration
- [django-celery-beat documentation](https://django-celery-beat.readthedocs.io/) -- DatabaseScheduler, PeriodicTask model

### Secondary (MEDIUM confidence)
- [hvac KV v2 delete_metadata_and_all_versions](https://hvac.readthedocs.io/en/stable/usage/secrets_engines/kv_v2.html) -- Vault secret permanent deletion API
- [GDPR Article 17 - Right to erasure](https://gdpr.eu/article-17-right-to-be-forgotten/) -- Hard delete requirement for GDPR compliance
- [Letta agents API](https://docs.letta.com/) -- Agent deletion for memory purge

### Tertiary (LOW confidence)
- QA agent execution mechanism via Letta message API -- actual LLM interaction may require additional wiring not yet in place from Phase 4 stubs

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries already installed and in use; no new dependencies
- Architecture: HIGH - Patterns directly extend existing models and modules; QA app follows established Django app pattern
- Pitfalls: HIGH - CASCADE deletion ordering, Vault cleanup, and HITL timeout configuration are derived from direct code inspection
- Data lifecycle: MEDIUM - GDPR hard delete approach is well-established but Vault/Letta cleanup sequencing needs validation against actual API behavior

**Research date:** 2026-03-06
**Valid until:** 2026-04-06 (30 days -- stable ecosystem, all code is project-internal)

"""Celery tasks for async workflow execution.

Public API
----------
* ``run_workflow.delay(workflow_name, agency_id, client_id, triggered_by)``
"""

from __future__ import annotations

import asyncio
import logging

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded

try:
    from billiard.exceptions import SoftTimeLimitExceeded as BilliardSoftTimeLimitExceeded
except ImportError:
    BilliardSoftTimeLimitExceeded = SoftTimeLimitExceeded

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=0,
    time_limit=4 * 3600 + 300,
    soft_time_limit=4 * 3600,
)
def run_workflow(
    self,
    workflow_name: str,
    agency_id: str,
    client_id: str,
    triggered_by: str,
) -> str:
    """Execute a workflow asynchronously via Celery.

    Creates a WorkflowSession, loads the workflow YAML, and runs
    the WorkflowExecutor.  Stores the Celery task ID on the
    WorkflowRun for correlation.

    SSE events are emitted ONLY from executor.py -- this task
    intentionally does NOT emit any SSE events to avoid duplication.

    Parameters
    ----------
    workflow_name:
        Name of the workflow YAML (e.g. "website", "audit").
    agency_id:
        UUID string of the agency.
    client_id:
        UUID string of the end client.
    triggered_by:
        Identifier for who/what triggered the workflow.

    Returns
    -------
    str
        The WorkflowRun UUID as string.
    """
    from hazn_platform.core.models import Agency, EndClient

    agency = Agency.objects.get(pk=agency_id)
    end_client = EndClient.objects.get(pk=client_id)

    # Load workflow YAML (slugify display name to match filename)
    from hazn_platform.orchestrator.workflow_parser import load_workflow

    slug = workflow_name.lower().replace(" ", "-")
    workflow = load_workflow(f"hazn/workflows/{slug}.yaml")

    # Create session
    from hazn_platform.orchestrator.session import WorkflowSession

    session = WorkflowSession(
        workflow_name=workflow_name,
        agency=agency,
        end_client=end_client,
        triggered_by=triggered_by,
    )

    # Store Celery task ID on the WorkflowRun for correlation
    celery_task_id = self.request.id or ""
    if celery_task_id:
        session.workflow_run.celery_task_id = celery_task_id
        session.workflow_run.save(update_fields=["celery_task_id"])

    # Get ToolRegistry singleton
    from hazn_platform.orchestrator import apps as apps_module
    from hazn_platform.orchestrator.tools import build_registry

    registry = apps_module._REGISTRY_SINGLETON or build_registry()

    # Run executor via async bridge (use new_event_loop, NOT asyncio.run)
    from hazn_platform.orchestrator.executor import WorkflowExecutor

    loop = asyncio.new_event_loop()
    try:
        try:
            executor = WorkflowExecutor(workflow, session, registry)
            loop.run_until_complete(executor.run())
        except (SoftTimeLimitExceeded, BilliardSoftTimeLimitExceeded):
            logger.warning(
                "Workflow %s timed out after 4 hours", workflow_name
            )
            session.fail("Workflow timed out after 4 hours")
            return str(session.workflow_run.pk)
        except Exception as exc:
            logger.error(
                "Workflow %s failed: %s", workflow_name, str(exc)[:200]
            )
            session.fail(str(exc)[:500])
            raise
    finally:
        loop.close()

    return str(session.workflow_run.pk)

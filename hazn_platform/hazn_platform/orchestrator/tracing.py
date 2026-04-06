"""Langfuse v3 tracing integration for the orchestrator.

Provides non-fatal tracing wrappers that create Langfuse traces and spans
for workflow runs, phases, and tool calls.  All functions gracefully degrade
when Langfuse is not configured (empty env vars) or unavailable -- workflows
are never blocked by tracing failures.

Public API
----------
* ``init_langfuse()`` -- check Langfuse client auth status
* ``start_workflow_trace(workflow_run)`` -- create top-level trace with tags
* ``start_phase_span(trace_id, phase_id)`` -- create child span for phase
* ``start_tool_span(trace_id, tool_name)`` -- create child span for tool call
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from langfuse import get_client

if TYPE_CHECKING:
    from hazn_platform.orchestrator.models import WorkflowRun

logger = logging.getLogger(__name__)


def init_langfuse() -> bool:
    """Initialize Langfuse client and verify authentication.

    Returns
    -------
    bool
        True if Langfuse is configured and auth_check passes, False otherwise.
    """
    try:
        client = get_client()
        if client.auth_check():
            logger.info("Langfuse tracing initialized successfully")
            return True
        logger.warning("Langfuse auth_check returned False -- tracing disabled")
        return False
    except Exception:
        logger.warning(
            "Langfuse not configured or unavailable -- tracing disabled",
            exc_info=True,
        )
        return False


def start_workflow_trace(workflow_run: WorkflowRun) -> str | None:
    """Create a top-level Langfuse trace for a workflow run.

    Tags the trace with ``l2:<agency_id>``, ``l3:<end_client_id>``,
    and ``run:<workflow_run_id>`` for filtering in Langfuse UI.
    Stores the trace ID on ``workflow_run.langfuse_trace_id``.

    Parameters
    ----------
    workflow_run:
        The WorkflowRun record to trace.

    Returns
    -------
    str or None
        The Langfuse trace ID, or None if tracing is unavailable.
    """
    try:
        client = get_client()
        trace = client.trace(
            name=f"workflow-{workflow_run.workflow_name}",
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
        )
        trace_id = trace.id
        workflow_run.langfuse_trace_id = trace_id
        workflow_run.save(update_fields=["langfuse_trace_id"])
        logger.info(
            "Langfuse trace created: trace_id=%s run=%s",
            trace_id,
            workflow_run.pk,
        )
        return trace_id
    except Exception:
        logger.warning(
            "Failed to create Langfuse trace for run=%s -- continuing without tracing",
            workflow_run.pk,
            exc_info=True,
        )
        return None


def start_phase_span(trace_id: str, phase_id: str) -> str | None:
    """Create a child span for a workflow phase.

    Parameters
    ----------
    trace_id:
        The parent Langfuse trace ID.
    phase_id:
        The workflow phase identifier.

    Returns
    -------
    str or None
        The span ID, or None if tracing is unavailable.
    """
    try:
        client = get_client()
        span = client.span(
            trace_id=trace_id,
            name=f"phase-{phase_id}",
            metadata={"phase_id": phase_id},
        )
        return span.id
    except Exception:
        logger.debug(
            "Failed to create phase span for phase=%s -- continuing",
            phase_id,
        )
        return None


def start_tool_span(trace_id: str, tool_name: str) -> str | None:
    """Create a child span for an MCP tool call.

    Parameters
    ----------
    trace_id:
        The parent Langfuse trace ID.
    tool_name:
        The name of the MCP tool being called.

    Returns
    -------
    str or None
        The span ID, or None if tracing is unavailable.
    """
    try:
        client = get_client()
        span = client.span(
            trace_id=trace_id,
            name=f"tool-{tool_name}",
            metadata={"tool_name": tool_name},
        )
        return span.id
    except Exception:
        logger.debug(
            "Failed to create tool span for tool=%s -- continuing",
            tool_name,
        )
        return None

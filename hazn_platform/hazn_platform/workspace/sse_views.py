"""SSE streaming endpoint with agency channel scoping.

Uses django-eventstream for real-time push to frontend clients.
Agency-scoped channel: `agency-{agency_id}`.
Authentication via session cookie (EventSource sends cookies automatically).

Helper function ``send_workspace_event()`` can be called from Celery tasks
and views to push events to the correct agency channel.
"""

from __future__ import annotations

import logging

from django_eventstream import send_event

logger = logging.getLogger(__name__)


def send_workspace_event(
    agency_id: str,
    event_type: str,
    data: dict,
) -> None:
    """Send an SSE event to the agency-scoped channel.

    Parameters
    ----------
    agency_id:
        UUID string of the agency.
    event_type:
        Event type identifier (e.g., 'workflow_status', 'hitl_new',
        'deliverable_ready', 'cost_update').
    data:
        JSON-serializable payload to include in the event.
    """
    channel = f"agency-{agency_id}"
    payload = {
        "type": event_type,
        **data,
    }
    try:
        send_event(channel, "message", payload)
        logger.debug(
            "SSE event sent: channel=%s type=%s",
            channel,
            event_type,
        )
    except Exception:
        logger.exception(
            "Failed to send SSE event: channel=%s type=%s",
            channel,
            event_type,
        )

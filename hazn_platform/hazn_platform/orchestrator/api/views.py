"""DRF views for workflow status APIs.

Provides:
- WorkflowRunViewSet: read-only list and detail with nested data
"""

from __future__ import annotations

import logging

from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from hazn_platform.orchestrator.models import WorkflowRun

from .serializers import (
    WorkflowRunListSerializer,
    WorkflowRunSerializer,
)

logger = logging.getLogger(__name__)


class WorkflowRunViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet for workflow runs with nested data.

    List view uses a lightweight serializer.
    Detail view includes nested agents, tool_calls, phase_outputs.
    """

    queryset = WorkflowRun.objects.all()
    permission_classes = [AllowAny]  # TODO: restrict to authenticated users
    lookup_field = "pk"

    def get_serializer_class(self):
        """Use lightweight serializer for list, full serializer for detail."""
        if self.action == "list":
            return WorkflowRunListSerializer
        return WorkflowRunSerializer

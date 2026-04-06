"""django-filter FilterSets for workspace API endpoints.

Provides filtering for:
- WorkflowRun: by status, end_client
"""

from django_filters import rest_framework as filters

from hazn_platform.orchestrator.models import WorkflowRun


class WorkflowRunFilter(filters.FilterSet):
    """Filter WorkflowRun by status and end_client."""

    end_client = filters.UUIDFilter(field_name="end_client_id")

    class Meta:
        model = WorkflowRun
        fields = ["status", "end_client"]

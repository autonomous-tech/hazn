"""DRF serializers for workspace API endpoints.

Provides serializers for:
- Dashboard aggregation
- EndClient CRUD
- Memory Inspector search/correct
- Workflow trigger and run listing
"""

from rest_framework import serializers

from hazn_platform.core.models import EndClient
from hazn_platform.orchestrator.models import ChatMessage, WorkflowRun


class DashboardSerializer(serializers.Serializer):
    """Read-only serializer for dashboard aggregation data."""

    running_workflows = serializers.IntegerField()
    recent_activity = serializers.ListField(child=serializers.DictField())


class EndClientSerializer(serializers.ModelSerializer):
    """Serializer for EndClient CRUD. Agency is read-only (auto-set from user)."""

    class Meta:
        model = EndClient
        fields = [
            "id",
            "agency",
            "name",
            "slug",
            "competitors",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "agency", "created_at", "updated_at"]


class MemorySearchSerializer(serializers.Serializer):
    """Input serializer for memory search requests."""

    query = serializers.CharField()
    end_client_id = serializers.UUIDField()
    agent_type = serializers.CharField(required=False)
    limit = serializers.IntegerField(required=False, default=5)


class MemoryCorrectSerializer(serializers.Serializer):
    """Input serializer for memory correction requests."""

    passage_id = serializers.CharField()
    end_client_id = serializers.UUIDField()
    new_text = serializers.CharField()
    reason = serializers.CharField(required=False, default="Manual correction")


class MemoryListSerializer(serializers.Serializer):
    """Input serializer for memory list requests."""

    end_client_id = serializers.UUIDField()
    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=20, min_value=1, max_value=100)


class WorkflowTriggerSerializer(serializers.Serializer):
    """Input serializer for workflow trigger requests."""

    workflow_name = serializers.CharField()
    end_client_id = serializers.UUIDField()
    parameters = serializers.DictField(required=False, default=dict)


class WorkflowRunListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for WorkflowRun listing."""

    class Meta:
        model = WorkflowRun
        fields = [
            "id",
            "workflow_name",
            "agency",
            "end_client",
            "status",
            "total_tokens",
            "total_cost",
            "started_at",
            "ended_at",
            "triggered_by",
            "created_at",
        ]
        read_only_fields = fields


class ChatMessageSerializer(serializers.ModelSerializer):
    """Read-only serializer for chat messages."""

    class Meta:
        model = ChatMessage
        fields = ["id", "workflow_run", "role", "content", "metadata", "created_at"]
        read_only_fields = ["id", "workflow_run", "created_at"]


class ChatMessageCreateSerializer(serializers.Serializer):
    """Input serializer for creating chat messages."""

    content = serializers.CharField()
    role = serializers.ChoiceField(
        choices=["user", "agent", "system"], default="user"
    )
    metadata = serializers.DictField(required=False, default=dict)


class WorkflowRunDetailSerializer(serializers.ModelSerializer):
    """Detail serializer with nested agents, tool calls, phase outputs, chat."""

    from hazn_platform.orchestrator.api.serializers import (
        WorkflowAgentSerializer,
    )
    from hazn_platform.orchestrator.api.serializers import (
        WorkflowPhaseOutputSerializer,
    )
    from hazn_platform.orchestrator.api.serializers import (
        WorkflowToolCallSerializer,
    )

    agents = WorkflowAgentSerializer(many=True, read_only=True)
    tool_calls = WorkflowToolCallSerializer(many=True, read_only=True)
    phase_outputs = WorkflowPhaseOutputSerializer(many=True, read_only=True)
    chat_messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = WorkflowRun
        fields = [
            "id",
            "workflow_name",
            "agency",
            "end_client",
            "status",
            "total_tokens",
            "total_cost",
            "wall_clock_seconds",
            "started_at",
            "ended_at",
            "last_activity_at",
            "error_details",
            "conflict_log",
            "triggered_by",
            "celery_task_id",
            "created_at",
            "agents",
            "tool_calls",
            "phase_outputs",
            "chat_messages",
        ]
        read_only_fields = fields

"""DRF serializers for workflow runs.

Provides:
- WorkflowAgentSerializer: Nested serializer for workflow agents
- WorkflowRunSerializer: Detail serializer with nested agents
- WorkflowRunListSerializer: Lightweight list serializer
"""

from __future__ import annotations

from rest_framework import serializers

from hazn_platform.orchestrator.models import (
    WorkflowAgent,
    WorkflowPhaseOutput,
    WorkflowRun,
    WorkflowToolCall,
)


class WorkflowAgentSerializer(serializers.ModelSerializer):
    """Nested serializer for workflow agents (read-only)."""

    class Meta:
        model = WorkflowAgent
        fields = [
            "id",
            "agent_id",
            "agent_type",
            "phase_id",
            "total_tokens",
            "total_cost",
            "started_at",
            "ended_at",
            "created_at",
        ]
        read_only_fields = fields


class WorkflowToolCallSerializer(serializers.ModelSerializer):
    """Nested serializer for workflow tool calls (read-only)."""

    class Meta:
        model = WorkflowToolCall
        fields = [
            "id",
            "tool_name",
            "call_count",
            "total_cost",
            "avg_latency_ms",
            "created_at",
        ]
        read_only_fields = fields


class WorkflowPhaseOutputSerializer(serializers.ModelSerializer):
    """Nested serializer for workflow phase outputs (read-only)."""

    class Meta:
        model = WorkflowPhaseOutput
        fields = [
            "id",
            "phase_id",
            "output_type",
            "content",
            "summary",
            "created_at",
        ]
        read_only_fields = fields


class WorkflowRunSerializer(serializers.ModelSerializer):
    """Detail serializer for WorkflowRun with nested related data."""

    agents = WorkflowAgentSerializer(many=True, read_only=True)
    tool_calls = WorkflowToolCallSerializer(many=True, read_only=True)
    phase_outputs = WorkflowPhaseOutputSerializer(many=True, read_only=True)

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
        ]
        read_only_fields = fields


class WorkflowRunListSerializer(serializers.ModelSerializer):
    """Lightweight list serializer for WorkflowRun."""

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

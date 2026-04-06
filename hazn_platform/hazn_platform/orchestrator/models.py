"""Orchestrator domain models: workflow runs, agents, tool calls, phase outputs.

These models are the metering source of truth for workflow execution,
per-agent and per-tool cost tracking, and structured phase outputs.
"""

import uuid

from django.db import models


class WorkflowRun(models.Model):
    """Metering source of truth for a single workflow execution."""

    class Status(models.TextChoices):
        PENDING = "pending"
        RUNNING = "running"
        WAITING_FOR_INPUT = "waiting_for_input"
        COMPLETED = "completed"
        FAILED = "failed"
        TIMED_OUT = "timed_out"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_name = models.CharField(max_length=100)
    agency = models.ForeignKey(
        "core.Agency",
        on_delete=models.CASCADE,
        related_name="workflow_runs",
    )
    end_client = models.ForeignKey(
        "core.EndClient",
        on_delete=models.CASCADE,
        related_name="workflow_runs",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    total_tokens = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    wall_clock_seconds = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    error_details = models.JSONField(default=dict, blank=True)
    conflict_log = models.JSONField(default=list, blank=True)
    triggered_by = models.CharField(max_length=100)
    celery_task_id = models.CharField(max_length=255, blank=True, default="")
    langfuse_trace_id = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.workflow_name} ({self.status})"


class WorkflowAgent(models.Model):
    """Per-agent metering within a workflow run."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_run = models.ForeignKey(
        WorkflowRun,
        on_delete=models.CASCADE,
        related_name="agents",
    )
    agent_id = models.CharField(max_length=255)
    agent_type = models.CharField(max_length=100)
    phase_id = models.CharField(max_length=100)
    total_tokens = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.agent_type} in {self.phase_id}"


class WorkflowToolCall(models.Model):
    """Per-tool metering within a workflow run."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_run = models.ForeignKey(
        WorkflowRun,
        on_delete=models.CASCADE,
        related_name="tool_calls",
    )
    tool_name = models.CharField(max_length=255)
    call_count = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    avg_latency_ms = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tool_name} ({self.call_count} calls)"


class WorkflowPhaseOutput(models.Model):
    """Structured output from a workflow phase, stored as a database record."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_run = models.ForeignKey(
        WorkflowRun,
        on_delete=models.CASCADE,
        related_name="phase_outputs",
    )
    phase_id = models.CharField(max_length=100)
    output_type = models.CharField(max_length=100)
    content = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True, default="")
    artifact_type = models.CharField(max_length=50, blank=True, default="")
    structured_data = models.JSONField(default=dict, blank=True)
    html_content = models.TextField(blank=True, default="")
    markdown_source = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.phase_id}: {self.output_type}"


class ChatMessage(models.Model):
    """Message in a per-run chat thread (CHAT-01)."""

    class Role(models.TextChoices):
        USER = "user"       # User input or steering
        AGENT = "agent"     # Agent output or question
        SYSTEM = "system"   # Phase transitions, status changes

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_run = models.ForeignKey(
        WorkflowRun, on_delete=models.CASCADE, related_name="chat_messages"
    )
    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)  # phase_id, agent_type, etc.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.role}] {self.content[:50]}"

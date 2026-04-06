from django.contrib import admin

from .models import WorkflowAgent
from .models import WorkflowPhaseOutput
from .models import WorkflowRun
from .models import WorkflowToolCall


@admin.register(WorkflowRun)
class WorkflowRunAdmin(admin.ModelAdmin):
    list_display = ("workflow_name", "agency", "end_client", "status", "created_at")
    list_filter = ("status", "workflow_name")
    search_fields = ("workflow_name", "triggered_by")
    readonly_fields = ("id", "created_at", "last_activity_at")


@admin.register(WorkflowAgent)
class WorkflowAgentAdmin(admin.ModelAdmin):
    list_display = ("agent_type", "phase_id", "workflow_run", "total_tokens", "created_at")
    list_filter = ("agent_type",)
    search_fields = ("agent_id", "agent_type", "phase_id")
    readonly_fields = ("id", "created_at")


@admin.register(WorkflowToolCall)
class WorkflowToolCallAdmin(admin.ModelAdmin):
    list_display = ("tool_name", "call_count", "total_cost", "workflow_run", "created_at")
    search_fields = ("tool_name",)
    readonly_fields = ("id", "created_at")


@admin.register(WorkflowPhaseOutput)
class WorkflowPhaseOutputAdmin(admin.ModelAdmin):
    list_display = ("phase_id", "output_type", "workflow_run", "created_at")
    list_filter = ("output_type",)
    search_fields = ("phase_id", "output_type")
    readonly_fields = ("id", "created_at")

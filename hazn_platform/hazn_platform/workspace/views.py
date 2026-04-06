"""DRF viewsets for the Workspace API.

Provides:
- DashboardView: Aggregated counts scoped by agency
- EndClientViewSet: Full CRUD for end-clients
- MemoryInspectorView: Proxy to HaznMemory search/correct
- WorkflowTriggerView: Dispatches run_workflow Celery task
- WorkflowCatalogView: Lists available workflows from YAML files
- WorkflowRunViewSet: Read-only workflow run listing

Every endpoint enforces authentication via IsAuthenticated
and queryset filtering by request.user.agency.
"""

from __future__ import annotations

import logging
from pathlib import Path

from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from hazn_platform.orchestrator.workflow_parser import load_workflow

from hazn_platform.core.letta_client import get_letta_client
from hazn_platform.core.memory import HaznMemory
from hazn_platform.core.models import Agency, EndClient
from hazn_platform.orchestrator.models import ChatMessage, WorkflowRun
from hazn_platform.orchestrator.tasks import run_workflow
from hazn_platform.workspace.filters import WorkflowRunFilter
from hazn_platform.workspace.serializers import (
    ChatMessageCreateSerializer,
    ChatMessageSerializer,
    DashboardSerializer,
    EndClientSerializer,
    MemoryCorrectSerializer,
    MemoryListSerializer,
    MemorySearchSerializer,
    WorkflowRunDetailSerializer,
    WorkflowRunListSerializer,
    WorkflowTriggerSerializer,
)

logger = logging.getLogger(__name__)


class DashboardView(APIView):
    """Dashboard aggregation endpoint (WS-01).

    Returns running_workflows count and recent_activity
    scoped to the authenticated user's agency.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        agency = request.user.agency

        running_workflows = WorkflowRun.objects.filter(
            agency=agency,
            status=WorkflowRun.Status.RUNNING,
        ).count()

        # Recent activity: last 10 workflow events
        recent_runs = (
            WorkflowRun.objects.filter(agency=agency)
            .select_related("end_client")
            .order_by("-last_activity_at")[:10]
        )
        recent_activity = [
            {
                "id": str(run.pk),
                "workflow_name": run.workflow_name,
                "end_client_name": run.end_client.name,
                "status": run.status,
                "last_activity_at": run.last_activity_at.isoformat()
                if run.last_activity_at
                else None,
            }
            for run in recent_runs
        ]

        data = {
            "running_workflows": running_workflows,
            "recent_activity": recent_activity,
        }
        serializer = DashboardSerializer(data)
        return Response(serializer.data)


class EndClientViewSet(viewsets.ModelViewSet):
    """Full CRUD for end-clients scoped by agency (WS-03).

    Users can only see and modify their own agency's end-clients.
    Agency is auto-set from the authenticated user on creation.
    """

    serializer_class = EndClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EndClient.objects.filter(
            agency=self.request.user.agency
        ).select_related("agency")

    def perform_create(self, serializer):
        serializer.save(agency=self.request.user.agency)


class MemoryInspectorView(APIView):
    """Memory Inspector proxy endpoint (WS-02).

    Proxies HaznMemory.search_memory() and correct_memory() with
    agency-scoped access control. The action is determined by the
    URL keyword argument.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, action=None):
        agency = Agency.load()

        if action == "search":
            return self._handle_search(request, agency)
        elif action == "correct":
            return self._handle_correct(request, agency)
        elif action == "list":
            return self._handle_list(request, agency)
        else:
            return Response(
                {"error": "Invalid action"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _resolve_end_client(self, end_client_id, agency):
        """Validate end_client belongs to the user's agency."""
        try:
            return EndClient.objects.get(pk=end_client_id, agency=agency)
        except EndClient.DoesNotExist:
            return None

    def _get_agent_id(self, end_client, agent_type=None):
        """Resolve the Letta agent_id for this end-client.

        Uses one-agent-per-client naming convention: client--{pk}
        The agent_type parameter is kept for backward compatibility but ignored.
        """
        return f"client--{end_client.pk}"

    def _handle_search(self, request, agency):
        serializer = MemorySearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        end_client = self._resolve_end_client(
            serializer.validated_data["end_client_id"], agency
        )
        if end_client is None:
            return Response(
                {"error": "End client not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        agent_id = self._get_agent_id(end_client)
        limit = serializer.validated_data.get("limit", 5)

        memory = HaznMemory(
            agent_id=agent_id,
            l3_client_id=end_client.pk,
            l2_agency_id=agency.pk,
        )
        results = memory.search_memory(
            query=serializer.validated_data["query"],
            limit=limit,
        )
        return Response({"results": results})

    def _handle_correct(self, request, agency):
        serializer = MemoryCorrectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        end_client = self._resolve_end_client(
            serializer.validated_data["end_client_id"], agency
        )
        if end_client is None:
            return Response(
                {"error": "End client not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        agent_id = self._get_agent_id(end_client)

        memory = HaznMemory(
            agent_id=agent_id,
            l3_client_id=end_client.pk,
            l2_agency_id=agency.pk,
        )
        corrected_by = request.data.get("corrected_by", "dashboard-user")
        replacement_id = memory.correct_memory(
            passage_id=serializer.validated_data["passage_id"],
            new_content=serializer.validated_data["new_text"],
            reason=serializer.validated_data.get("reason", "Manual correction"),
            corrected_by=corrected_by,
        )
        return Response({"replacement_passage_id": replacement_id})

    def _handle_list(self, request, agency):
        serializer = MemoryListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        end_client = self._resolve_end_client(
            serializer.validated_data["end_client_id"], agency
        )
        if end_client is None:
            return Response(
                {"error": "End client not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        agent_id = self._get_agent_id(end_client)

        try:
            letta = get_letta_client()
            all_passages = letta.agents.passages.list(agent_id=agent_id)

            # Filter to active passages only
            active = []
            for p in all_passages:
                if "[status:corrected]" in p.text or "[status:superseded]" in p.text:
                    continue
                active.append({"id": p.id, "content": p.text})

            # Paginate
            page = serializer.validated_data.get("page", 1)
            page_size = serializer.validated_data.get("page_size", 20)
            start = (page - 1) * page_size
            end = start + page_size

            return Response({
                "results": active[start:end],
                "total": len(active),
                "page": page,
                "page_size": page_size,
            })
        except Exception as e:
            return Response(
                {"error": f"Letta unavailable: {e}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


class WorkflowTriggerView(APIView):
    """Workflow trigger endpoint (WS-04).

    Validates end_client belongs to user's agency, then dispatches
    run_workflow Celery task.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WorkflowTriggerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        agency = request.user.agency
        end_client_id = serializer.validated_data["end_client_id"]

        try:
            end_client = EndClient.objects.get(
                pk=end_client_id, agency=agency
            )
        except EndClient.DoesNotExist:
            return Response(
                {"error": "End client not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Create WorkflowRun eagerly so we can return its ID immediately
        workflow_run = WorkflowRun.objects.create(
            workflow_name=serializer.validated_data["workflow_name"],
            agency=agency,
            end_client=end_client,
            triggered_by=request.user.email,
            status=WorkflowRun.Status.PENDING,
        )

        result = run_workflow.delay(
            workflow_name=serializer.validated_data["workflow_name"],
            l2_agency_id=str(agency.pk),
            l3_client_id=str(end_client.pk),
            triggered_by=request.user.email,
        )

        # Store celery task ID for correlation
        workflow_run.celery_task_id = result.id
        workflow_run.save(update_fields=["celery_task_id"])

        return Response(
            {
                "run_id": str(workflow_run.pk),
                "celery_task_id": result.id,
                "message": f"Workflow {serializer.validated_data['workflow_name']} triggered",
            },
            status=status.HTTP_202_ACCEPTED,
        )


class WorkflowRunViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only workflow run listing scoped by agency (WS-04).

    List uses lightweight serializer, detail includes nested data.
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = WorkflowRunFilter

    def get_queryset(self):
        return (
            WorkflowRun.objects.filter(agency=self.request.user.agency)
            .select_related("agency", "end_client")
            .prefetch_related("agents", "tool_calls", "phase_outputs")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return WorkflowRunListSerializer
        return WorkflowRunDetailSerializer


class WorkflowCatalogView(APIView):
    """Workflow catalog endpoint -- lists available workflows from YAML files.

    Scans hazn/workflows/ directory for YAML workflow definitions and
    returns structured metadata for each. Invalid YAML files are logged
    and skipped gracefully.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Use absolute path resolution to avoid Celery worker path issues
        workflows_dir = Path(settings.BASE_DIR) / "hazn" / "workflows"
        catalog = []

        for yaml_path in sorted(workflows_dir.glob("*.yaml")):
            try:
                schema = load_workflow(yaml_path)
                catalog.append(
                    {
                        "name": schema.name,
                        "description": schema.description,
                        "phases": [
                            {"id": p.id, "name": p.name, "agent": p.agent}
                            for p in schema.phases
                        ],
                        "estimated_duration": schema.estimated_duration,
                        "parameters": [],
                        "estimated_cost": None,
                    }
                )
            except Exception:
                logger.warning("Skipping invalid workflow: %s", yaml_path.name)

        return Response(catalog)


class ChatMessageViewSet(viewsets.ViewSet):
    """Chat message API for per-run chat threads (CHAT-01).

    Nested under workflow runs:
    - GET  /runs/{run_pk}/chat/ -- list messages in chronological order
    - POST /runs/{run_pk}/chat/ -- create a new message
    """

    permission_classes = [IsAuthenticated]

    def list(self, request, run_pk=None):
        run = WorkflowRun.objects.filter(
            pk=run_pk, agency=request.user.agency
        ).first()
        if not run:
            return Response({"error": "Run not found"}, status=404)
        messages = ChatMessage.objects.filter(workflow_run=run)
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def create(self, request, run_pk=None):
        run = WorkflowRun.objects.filter(
            pk=run_pk, agency=request.user.agency
        ).first()
        if not run:
            return Response({"error": "Run not found"}, status=404)
        serializer = ChatMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        msg = ChatMessage.objects.create(
            workflow_run=run,
            role=serializer.validated_data["role"],
            content=serializer.validated_data["content"],
            metadata=serializer.validated_data.get("metadata", {}),
        )
        # If run is waiting_for_input and a user replies, resume execution
        if (
            run.status == "waiting_for_input"
            and serializer.validated_data["role"] == "user"
        ):
            run.status = "running"
            run.save(update_fields=["status"])
        # Emit SSE event for real-time chat delivery (DASH-04)
        try:
            from hazn_platform.workspace.sse_views import send_workspace_event

            send_workspace_event(
                str(run.agency_id),
                "chat_message",
                {"run_id": str(run.pk), "message_id": str(msg.pk)},
            )
        except Exception:
            logger.warning("Failed to emit SSE chat_message event")
        return Response(
            ChatMessageSerializer(msg).data,
            status=status.HTTP_201_CREATED,
        )

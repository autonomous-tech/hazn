"""URL configuration for workspace API.

Registers all workspace viewsets with DRF router.
Include in main urls.py as:
    path("api/workspace/", include("hazn_platform.workspace.urls"))
"""

from django.urls import path

from rest_framework.routers import DefaultRouter

from hazn_platform.workspace.views import (
    ChatMessageViewSet,
    DashboardView,
    EndClientViewSet,
    MemoryInspectorView,
    WorkflowCatalogView,
    WorkflowRunViewSet,
    WorkflowTriggerView,
)

router = DefaultRouter()
router.register(r"clients", EndClientViewSet, basename="workspace-client")
router.register(r"workflows", WorkflowRunViewSet, basename="workspace-workflow")

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="workspace-dashboard"),
    path(
        "memory/<str:action>/",
        MemoryInspectorView.as_view(),
        name="workspace-memory",
    ),
    path(
        "workflows/trigger/",
        WorkflowTriggerView.as_view(),
        name="workspace-workflow-trigger",
    ),
    path(
        "workflows/catalog/",
        WorkflowCatalogView.as_view(),
        name="workspace-workflow-catalog",
    ),
    path(
        "runs/<uuid:run_pk>/chat/",
        ChatMessageViewSet.as_view({"get": "list", "post": "create"}),
        name="run-chat",
    ),
    *router.urls,
]

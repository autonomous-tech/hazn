"""URL configuration for orchestrator API.

Registers WorkflowRun viewset with DRF router.
Include in main urls.py as:
    path("api/orchestrator/", include("hazn_platform.orchestrator.api.urls"))
"""

from rest_framework.routers import DefaultRouter

from .views import WorkflowRunViewSet

router = DefaultRouter()
router.register(r"runs", WorkflowRunViewSet, basename="workflow-run")

urlpatterns = router.urls

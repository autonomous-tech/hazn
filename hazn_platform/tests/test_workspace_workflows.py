"""Tests for WS-04: Workflow trigger and WorkflowRun list scoped by agency.

Verifies:
- POST /api/workspace/workflows/trigger/ validates end_client belongs to agency
- Dispatches run_workflow.delay() on valid trigger
- Returns 404 for other agency's end-client
- GET /api/workspace/workflows/ returns only agency's workflow runs
"""

from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory
from rest_framework.test import force_authenticate

from hazn_platform.core.models import Agency, EndClient
from hazn_platform.orchestrator.models import WorkflowRun
from hazn_platform.users.models import User


@pytest.fixture()
def agency_a():
    return Agency.objects.create(name="Agency A", slug="agency-a")


@pytest.fixture()
def agency_b():
    return Agency.objects.create(name="Agency B", slug="agency-b")


@pytest.fixture()
def user_a(agency_a):
    return User.objects.create_user(
        username="user_a",
        email="a@test.com",
        password="testpass",
        agency=agency_a,
    )


@pytest.fixture()
def client_a1(agency_a):
    return EndClient.objects.create(
        agency=agency_a, name="Client A1", slug="client-a1"
    )


@pytest.fixture()
def client_b1(agency_b):
    return EndClient.objects.create(
        agency=agency_b, name="Client B1", slug="client-b1"
    )


@pytest.fixture()
def run_a(agency_a, client_a1):
    return WorkflowRun.objects.create(
        workflow_name="audit",
        agency=agency_a,
        end_client=client_a1,
        status=WorkflowRun.Status.COMPLETED,
        triggered_by="test",
    )


@pytest.fixture()
def run_b(agency_b, client_b1):
    return WorkflowRun.objects.create(
        workflow_name="seo",
        agency=agency_b,
        end_client=client_b1,
        status=WorkflowRun.Status.RUNNING,
        triggered_by="test",
    )


@pytest.mark.django_db()
class TestWorkflowTriggerView:
    def _get_view(self):
        from hazn_platform.workspace.views import WorkflowTriggerView

        return WorkflowTriggerView.as_view()

    @patch("hazn_platform.workspace.views.run_workflow")
    def test_trigger_workflow_success(
        self, mock_run_workflow, user_a, client_a1
    ):
        mock_result = MagicMock()
        mock_result.id = "celery-task-123"
        mock_run_workflow.delay.return_value = mock_result

        factory = RequestFactory()
        request = factory.post(
            "/api/workspace/workflows/trigger/",
            data={
                "workflow_name": "audit",
                "end_client_id": str(client_a1.pk),
            },
            content_type="application/json",
        )
        force_authenticate(request, user=user_a)
        response = self._get_view()(request)
        assert response.status_code == 202
        mock_run_workflow.delay.assert_called_once_with(
            workflow_name="audit",
            l2_agency_id=str(user_a.agency_id),
            l3_client_id=str(client_a1.pk),
            triggered_by=user_a.email,
        )

    def test_trigger_other_agency_client_returns_404(
        self, user_a, client_b1
    ):
        factory = RequestFactory()
        request = factory.post(
            "/api/workspace/workflows/trigger/",
            data={
                "workflow_name": "audit",
                "end_client_id": str(client_b1.pk),
            },
            content_type="application/json",
        )
        force_authenticate(request, user=user_a)
        response = self._get_view()(request)
        assert response.status_code == 404


@pytest.mark.django_db()
class TestWorkflowRunViewSet:
    def _get_view(self, actions=None):
        from hazn_platform.workspace.views import WorkflowRunViewSet

        if actions is None:
            actions = {"get": "list"}
        return WorkflowRunViewSet.as_view(actions)

    def test_list_returns_only_agency_runs(
        self, user_a, run_a, run_b
    ):
        factory = RequestFactory()
        request = factory.get("/api/workspace/workflows/")
        force_authenticate(request, user=user_a)
        response = self._get_view({"get": "list"})(request)
        assert response.status_code == 200
        ids = {str(r["id"]) for r in response.data}
        assert str(run_a.pk) in ids
        assert str(run_b.pk) not in ids

    def test_retrieve_own_run(self, user_a, run_a):
        factory = RequestFactory()
        request = factory.get(f"/api/workspace/workflows/{run_a.pk}/")
        force_authenticate(request, user=user_a)
        response = self._get_view({"get": "retrieve"})(
            request, pk=str(run_a.pk)
        )
        assert response.status_code == 200
        assert response.data["workflow_name"] == "audit"

    def test_retrieve_other_agency_run_returns_404(
        self, user_a, run_b
    ):
        factory = RequestFactory()
        request = factory.get(f"/api/workspace/workflows/{run_b.pk}/")
        force_authenticate(request, user=user_a)
        response = self._get_view({"get": "retrieve"})(
            request, pk=str(run_b.pk)
        )
        assert response.status_code == 404

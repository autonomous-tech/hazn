"""Tests for WS-01: Dashboard API returns agency-scoped aggregation.

Verifies:
- GET /api/workspace/dashboard/ returns running_workflows count
  scoped to authenticated user's agency only
- Unauthenticated request returns 401/403
- Users from different agencies see isolated data
"""


import pytest
from django.test import RequestFactory
from rest_framework.test import force_authenticate

from hazn_platform.core.models import Agency, EndClient
from hazn_platform.orchestrator.models import WorkflowRun
from hazn_platform.users.models import User


@pytest.fixture()
def agency_a():
    return Agency.objects.create(
        name="Agency A",
        slug="agency-a",
    )


@pytest.fixture()
def agency_b():
    return Agency.objects.create(
        name="Agency B",
        slug="agency-b",
    )


@pytest.fixture()
def user_a(agency_a):
    user = User.objects.create_user(
        username="user_a",
        email="a@test.com",
        password="testpass",
        agency=agency_a,
    )
    return user


@pytest.fixture()
def user_b(agency_b):
    user = User.objects.create_user(
        username="user_b",
        email="b@test.com",
        password="testpass",
        agency=agency_b,
    )
    return user


@pytest.fixture()
def user_no_agency():
    return User.objects.create_user(
        username="superuser",
        email="super@test.com",
        password="testpass",
    )


@pytest.fixture()
def _populate_agency_a_data(agency_a):
    """Create workflow runs for agency A."""
    client = EndClient.objects.create(
        agency=agency_a, name="Client A1", slug="client-a1"
    )
    # 2 running workflows
    WorkflowRun.objects.create(
        workflow_name="audit",
        agency=agency_a,
        end_client=client,
        status=WorkflowRun.Status.RUNNING,
        triggered_by="test",
    )
    WorkflowRun.objects.create(
        workflow_name="website",
        agency=agency_a,
        end_client=client,
        status=WorkflowRun.Status.RUNNING,
        triggered_by="test",
    )
    # 1 completed workflow (should not count as running)
    WorkflowRun.objects.create(
        workflow_name="content",
        agency=agency_a,
        end_client=client,
        status=WorkflowRun.Status.COMPLETED,
        triggered_by="test",
    )


@pytest.fixture()
def _populate_agency_b_data(agency_b):
    """Create data for agency B to verify isolation."""
    client = EndClient.objects.create(
        agency=agency_b, name="Client B1", slug="client-b1"
    )
    WorkflowRun.objects.create(
        workflow_name="seo",
        agency=agency_b,
        end_client=client,
        status=WorkflowRun.Status.RUNNING,
        triggered_by="test",
    )


@pytest.mark.django_db()
class TestDashboardView:
    def _get_view(self):
        from hazn_platform.workspace.views import DashboardView

        return DashboardView.as_view()

    def test_unauthenticated_returns_unauthorized(self):
        """Unauthenticated requests get 401 or 403 depending on auth backend.

        DRF SessionAuthentication returns 403 (CSRF), TokenAuth returns 401.
        """
        factory = RequestFactory()
        request = factory.get("/api/workspace/dashboard/")
        response = self._get_view()(request)
        assert response.status_code in (401, 403)

    @pytest.mark.usefixtures("_populate_agency_a_data", "_populate_agency_b_data")
    def test_dashboard_returns_agency_scoped_counts(self, user_a):
        factory = RequestFactory()
        request = factory.get("/api/workspace/dashboard/")
        force_authenticate(request, user=user_a)
        response = self._get_view()(request)
        assert response.status_code == 200
        data = response.data
        assert data["running_workflows"] == 2

    @pytest.mark.usefixtures("_populate_agency_a_data", "_populate_agency_b_data")
    def test_dashboard_isolation_agency_b(self, user_b):
        """Agency B user should see only their data, not agency A's."""
        factory = RequestFactory()
        request = factory.get("/api/workspace/dashboard/")
        force_authenticate(request, user=user_b)
        response = self._get_view()(request)
        assert response.status_code == 200
        data = response.data
        assert data["running_workflows"] == 1

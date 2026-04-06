"""Tests for workflow catalog API.

Verifies:
- GET /api/workspace/workflows/catalog/ returns workflow metadata
- Catalog requires IsAuthenticated authentication
- Invalid YAML files are skipped gracefully
"""

from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory
from rest_framework.test import force_authenticate

from hazn_platform.core.models import Agency
from hazn_platform.users.models import User


@pytest.fixture()
def agency():
    return Agency.objects.create(name="Test Agency", slug="test-agency")


@pytest.fixture()
def user(agency):
    return User.objects.create_user(
        username="catalog_user",
        email="catalog@test.com",
        password="testpass",
        agency=agency,
    )


def _make_mock_workflow(name, description, phases=None, estimated_duration="2h"):
    """Create a mock WorkflowSchema object."""
    wf = MagicMock()
    wf.name = name
    wf.description = description
    wf.estimated_duration = estimated_duration
    if phases is None:
        phase1 = MagicMock()
        phase1.id = "phase-1"
        phase1.name = "Phase 1"
        phase1.agent = "agent-1"
        phases = [phase1]
    wf.phases = phases
    return wf


@pytest.mark.django_db()
class TestWorkflowCatalogView:
    def _get_view(self):
        from hazn_platform.workspace.views import WorkflowCatalogView

        return WorkflowCatalogView.as_view()

    @patch("hazn_platform.workspace.views.load_workflow")
    def test_catalog_returns_workflow_list(self, mock_load, user, tmp_path):
        wf1 = _make_mock_workflow("Analytics Audit", "Full SEO audit workflow")
        wf2 = _make_mock_workflow("Blog Content", "Blog writing workflow")
        mock_load.side_effect = [wf1, wf2]

        # Create fake YAML files in a temp directory
        workflows_dir = tmp_path / "hazn" / "workflows"
        workflows_dir.mkdir(parents=True)
        (workflows_dir / "analytics-audit.yaml").write_text("name: test")
        (workflows_dir / "blog.yaml").write_text("name: test2")

        with patch(
            "hazn_platform.workspace.views.Path"
        ) as mock_path_cls:
            # Path(settings.BASE_DIR).parent / "hazn" / "workflows"
            mock_path_cls.return_value.parent.__truediv__ = (
                lambda self_unused, key: tmp_path / key
            )

            factory = RequestFactory()
            request = factory.get("/api/workspace/workflows/catalog/")
            force_authenticate(request, user=user)
            response = self._get_view()(request)

        assert response.status_code == 200
        assert len(response.data) == 2
        assert response.data[0]["name"] == "Analytics Audit"
        assert response.data[1]["name"] == "Blog Content"
        assert "phases" in response.data[0]
        assert "estimated_duration" in response.data[0]

    def test_catalog_requires_authentication(self):
        factory = RequestFactory()
        request = factory.get("/api/workspace/workflows/catalog/")
        # No authentication
        response = self._get_view()(request)
        assert response.status_code == 403

    @patch("hazn_platform.workspace.views.load_workflow")
    def test_invalid_yaml_skipped(self, mock_load, user, tmp_path):
        # First file valid, second raises exception
        wf = _make_mock_workflow("Good Workflow", "Works fine")
        mock_load.side_effect = [wf, Exception("Invalid YAML")]

        workflows_dir = tmp_path / "hazn" / "workflows"
        workflows_dir.mkdir(parents=True)
        (workflows_dir / "good.yaml").write_text("name: good")
        (workflows_dir / "zzz-bad.yaml").write_text("invalid")

        with patch(
            "hazn_platform.workspace.views.Path"
        ) as mock_path_cls:
            mock_path_cls.return_value.parent.__truediv__ = (
                lambda self_unused, key: tmp_path / key
            )

            factory = RequestFactory()
            request = factory.get("/api/workspace/workflows/catalog/")
            force_authenticate(request, user=user)
            response = self._get_view()(request)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Good Workflow"

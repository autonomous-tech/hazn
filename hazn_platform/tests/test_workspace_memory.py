"""Tests for WS-02: Memory Inspector API proxies HaznMemory with singleton Agency.

Verifies:
- POST /api/workspace/memory/search/ proxies HaznMemory.search_memory() scoped by agency
- POST /api/workspace/memory/correct/ proxies HaznMemory.correct_memory() scoped by agency
- Returns 404 if end_client does not exist under the singleton agency
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory
from rest_framework.test import force_authenticate

from hazn_platform.core.models import Agency, EndClient
from hazn_platform.users.models import User


@pytest.fixture()
def agency():
    return Agency.objects.create(name="Agency A", slug="agency-a")


@pytest.fixture()
def user(agency):
    return User.objects.create_user(
        username="user_a",
        email="a@test.com",
        password="testpass",
        agency=agency,
    )


@pytest.fixture()
def client_a1(agency):
    return EndClient.objects.create(
        agency=agency, name="Client A1", slug="client-a1"
    )


@pytest.mark.django_db()
class TestMemoryInspectorView:
    def _get_view(self):
        from hazn_platform.workspace.views import MemoryInspectorView

        return MemoryInspectorView.as_view()

    @patch("hazn_platform.workspace.views.HaznMemory")
    def test_search_memory_scoped_by_agency(
        self, mock_memory_cls, user, client_a1
    ):
        mock_instance = MagicMock()
        mock_instance.search_memory.return_value = [
            {"id": "p1", "content": "test learning", "score": 0.95}
        ]
        mock_memory_cls.return_value = mock_instance

        factory = RequestFactory()
        request = factory.post(
            "/api/workspace/memory/search/",
            data={
                "query": "SEO insights",
                "end_client_id": str(client_a1.pk),
            },
            content_type="application/json",
        )
        force_authenticate(request, user=user)
        response = self._get_view()(request, action="search")
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        mock_instance.search_memory.assert_called_once()

    @patch("hazn_platform.workspace.views.HaznMemory")
    def test_search_memory_nonexistent_client_returns_404(
        self, mock_memory_cls, user
    ):
        factory = RequestFactory()
        request = factory.post(
            "/api/workspace/memory/search/",
            data={
                "query": "test",
                "end_client_id": str(uuid.uuid4()),
            },
            content_type="application/json",
        )
        force_authenticate(request, user=user)
        response = self._get_view()(request, action="search")
        assert response.status_code == 404

    @patch("hazn_platform.workspace.views.HaznMemory")
    def test_correct_memory_scoped_by_agency(
        self, mock_memory_cls, user, client_a1
    ):
        mock_instance = MagicMock()
        mock_instance.correct_memory.return_value = "new-passage-id"
        mock_memory_cls.return_value = mock_instance

        factory = RequestFactory()
        request = factory.post(
            "/api/workspace/memory/correct/",
            data={
                "passage_id": "old-passage-id",
                "end_client_id": str(client_a1.pk),
                "new_text": "Corrected learning content",
                "reason": "Outdated information",
            },
            content_type="application/json",
        )
        force_authenticate(request, user=user)
        response = self._get_view()(request, action="correct")
        assert response.status_code == 200
        mock_instance.correct_memory.assert_called_once()

    @patch("hazn_platform.workspace.views.HaznMemory")
    def test_correct_memory_nonexistent_client_returns_404(
        self, mock_memory_cls, user
    ):
        factory = RequestFactory()
        request = factory.post(
            "/api/workspace/memory/correct/",
            data={
                "passage_id": "pid",
                "end_client_id": str(uuid.uuid4()),
                "new_text": "content",
                "reason": "reason",
            },
            content_type="application/json",
        )
        force_authenticate(request, user=user)
        response = self._get_view()(request, action="correct")
        assert response.status_code == 404

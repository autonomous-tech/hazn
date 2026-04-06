"""Tests for CHAT-01: ChatMessage API for per-run chat threads.

Verifies:
- GET /api/workspace/runs/{run_id}/chat/ returns empty list for new run
- POST creates a message and returns 201
- GET returns messages in chronological order
- POST with role "agent" creates agent message
- POST with role "system" creates system message
- Unauthenticated request returns 401/403
- Messages for runs in a different agency are not returned
"""

import pytest
from django.test import RequestFactory
from rest_framework.test import force_authenticate

from hazn_platform.core.models import Agency, EndClient
from hazn_platform.orchestrator.models import ChatMessage, WorkflowRun
from hazn_platform.users.models import User


@pytest.fixture()
def agency():
    return Agency.objects.create(name="Test Agency", slug="test-agency")


@pytest.fixture()
def other_agency():
    return Agency.objects.create(name="Other Agency", slug="other-agency")


@pytest.fixture()
def user(agency):
    return User.objects.create_user(
        username="chatuser",
        email="chat@test.com",
        password="testpass",
        agency=agency,
    )


@pytest.fixture()
def other_user(other_agency):
    return User.objects.create_user(
        username="otheruser",
        email="other@test.com",
        password="testpass",
        agency=other_agency,
    )


@pytest.fixture()
def end_client(agency):
    return EndClient.objects.create(
        agency=agency, name="Test Client", slug="test-client"
    )


@pytest.fixture()
def other_end_client(other_agency):
    return EndClient.objects.create(
        agency=other_agency, name="Other Client", slug="other-client"
    )


@pytest.fixture()
def workflow_run(agency, end_client):
    return WorkflowRun.objects.create(
        workflow_name="test-workflow",
        agency=agency,
        end_client=end_client,
        triggered_by="chat@test.com",
    )


@pytest.fixture()
def other_run(other_agency, other_end_client):
    return WorkflowRun.objects.create(
        workflow_name="other-workflow",
        agency=other_agency,
        end_client=other_end_client,
        triggered_by="other@test.com",
    )


def _get_chat_view():
    from hazn_platform.workspace.views import ChatMessageViewSet

    return ChatMessageViewSet.as_view({"get": "list", "post": "create"})


@pytest.mark.django_db()
class TestChatMessageAPI:
    def test_empty_list_for_new_run(self, user, workflow_run):
        """GET returns empty list for a run with no messages."""
        factory = RequestFactory()
        request = factory.get(f"/api/workspace/runs/{workflow_run.pk}/chat/")
        force_authenticate(request, user=user)
        response = _get_chat_view()(request, run_pk=str(workflow_run.pk))
        assert response.status_code == 200
        assert response.data == []

    def test_create_user_message(self, user, workflow_run):
        """POST with content and role user creates a message."""
        factory = RequestFactory()
        request = factory.post(
            f"/api/workspace/runs/{workflow_run.pk}/chat/",
            data={"content": "Hello agent!", "role": "user"},
            content_type="application/json",
        )
        force_authenticate(request, user=user)
        response = _get_chat_view()(request, run_pk=str(workflow_run.pk))
        assert response.status_code == 201
        assert response.data["content"] == "Hello agent!"
        assert response.data["role"] == "user"
        assert "id" in response.data

    def test_list_returns_chronological_order(self, user, workflow_run):
        """GET returns messages sorted by created_at ascending."""
        ChatMessage.objects.create(
            workflow_run=workflow_run,
            role="user",
            content="First message",
        )
        ChatMessage.objects.create(
            workflow_run=workflow_run,
            role="agent",
            content="Second message",
        )
        ChatMessage.objects.create(
            workflow_run=workflow_run,
            role="system",
            content="Third message",
        )

        factory = RequestFactory()
        request = factory.get(f"/api/workspace/runs/{workflow_run.pk}/chat/")
        force_authenticate(request, user=user)
        response = _get_chat_view()(request, run_pk=str(workflow_run.pk))
        assert response.status_code == 200
        assert len(response.data) == 3
        assert response.data[0]["content"] == "First message"
        assert response.data[1]["content"] == "Second message"
        assert response.data[2]["content"] == "Third message"

    def test_create_agent_message(self, user, workflow_run):
        """POST with role agent creates an agent message."""
        factory = RequestFactory()
        request = factory.post(
            f"/api/workspace/runs/{workflow_run.pk}/chat/",
            data={"content": "Agent response", "role": "agent"},
            content_type="application/json",
        )
        force_authenticate(request, user=user)
        response = _get_chat_view()(request, run_pk=str(workflow_run.pk))
        assert response.status_code == 201
        assert response.data["role"] == "agent"

    def test_create_system_message(self, user, workflow_run):
        """POST with role system creates a system message."""
        factory = RequestFactory()
        request = factory.post(
            f"/api/workspace/runs/{workflow_run.pk}/chat/",
            data={"content": "Phase transition: research", "role": "system"},
            content_type="application/json",
        )
        force_authenticate(request, user=user)
        response = _get_chat_view()(request, run_pk=str(workflow_run.pk))
        assert response.status_code == 201
        assert response.data["role"] == "system"

    def test_unauthenticated_returns_403(self, workflow_run):
        """Unauthenticated request returns 401 or 403."""
        factory = RequestFactory()
        request = factory.get(f"/api/workspace/runs/{workflow_run.pk}/chat/")
        # No force_authenticate -- anonymous user
        response = _get_chat_view()(request, run_pk=str(workflow_run.pk))
        assert response.status_code in (401, 403)

    def test_other_agency_run_returns_404(self, user, other_run):
        """Messages for a run belonging to a different agency are not returned."""
        # Create a message on the other agency's run
        ChatMessage.objects.create(
            workflow_run=other_run,
            role="user",
            content="Secret message",
        )

        factory = RequestFactory()
        request = factory.get(f"/api/workspace/runs/{other_run.pk}/chat/")
        force_authenticate(request, user=user)
        response = _get_chat_view()(request, run_pk=str(other_run.pk))
        assert response.status_code == 404

    def test_user_reply_while_waiting_resumes_run(self, user, workflow_run):
        """POST user message while run is waiting_for_input changes status to running."""
        workflow_run.status = "waiting_for_input"
        workflow_run.save(update_fields=["status"])

        factory = RequestFactory()
        request = factory.post(
            f"/api/workspace/runs/{workflow_run.pk}/chat/",
            data={"content": "Here is the answer", "role": "user"},
            content_type="application/json",
        )
        force_authenticate(request, user=user)
        response = _get_chat_view()(request, run_pk=str(workflow_run.pk))
        assert response.status_code == 201

        workflow_run.refresh_from_db()
        assert workflow_run.status == "running"

    def test_sse_event_emitted_on_message_create(self, user, workflow_run):
        """SSE event emitted when chat message is created."""
        from unittest.mock import patch, MagicMock

        factory = RequestFactory()
        request = factory.post(
            f"/api/workspace/runs/{workflow_run.pk}/chat/",
            data={"content": "Hello!", "role": "user"},
            content_type="application/json",
        )
        force_authenticate(request, user=user)

        with patch(
            "hazn_platform.workspace.sse_views.send_workspace_event"
        ) as mock_sse:
            response = _get_chat_view()(request, run_pk=str(workflow_run.pk))

        assert response.status_code == 201
        mock_sse.assert_called_once()
        call_args = mock_sse.call_args
        assert call_args[0][0] == str(workflow_run.agency_id)
        assert call_args[0][1] == "chat_message"
        assert call_args[0][2]["run_id"] == str(workflow_run.pk)

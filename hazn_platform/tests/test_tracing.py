"""Tests for Langfuse v3 tracing integration with the orchestrator.

Tests cover:
- init_langfuse() initializes client and logs auth status
- init_langfuse() handles unconfigured Langfuse gracefully
- start_workflow_trace() creates a trace with correct tags and metadata
- start_workflow_trace() stores trace_id on workflow_run.langfuse_trace_id
- start_workflow_trace() returns None when Langfuse is unavailable
- start_phase_span() creates a child span for a workflow phase
- start_tool_span() creates a child span for a tool call
- Tracing is non-fatal: workflows run when Langfuse is not configured
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from hazn_platform.core.models import Agency, EndClient
from hazn_platform.orchestrator.models import WorkflowRun


@pytest.fixture
def agency(db):
    return Agency.objects.create(name="Tracing Agency", slug="tracing-agency")


@pytest.fixture
def end_client(agency):
    return EndClient.objects.create(
        agency=agency, name="Tracing Client", slug="tracing-client"
    )


@pytest.fixture
def workflow_run(agency, end_client):
    return WorkflowRun.objects.create(
        workflow_name="website",
        agency=agency,
        end_client=end_client,
        triggered_by="test-user",
        status=WorkflowRun.Status.RUNNING,
    )


# -- init_langfuse --------------------------------------------------------


@pytest.mark.django_db
class TestInitLangfuse:
    @patch("hazn_platform.orchestrator.tracing.get_client")
    def test_init_langfuse_logs_success_when_configured(self, mock_get_client):
        """init_langfuse logs success when Langfuse auth_check passes."""
        from hazn_platform.orchestrator.tracing import init_langfuse

        mock_client = MagicMock()
        mock_client.auth_check.return_value = True
        mock_get_client.return_value = mock_client

        result = init_langfuse()
        assert result is True
        mock_client.auth_check.assert_called_once()

    @patch("hazn_platform.orchestrator.tracing.get_client")
    def test_init_langfuse_returns_false_when_auth_fails(self, mock_get_client):
        """init_langfuse returns False when auth_check fails."""
        from hazn_platform.orchestrator.tracing import init_langfuse

        mock_client = MagicMock()
        mock_client.auth_check.return_value = False
        mock_get_client.return_value = mock_client

        result = init_langfuse()
        assert result is False

    @patch("hazn_platform.orchestrator.tracing.get_client")
    def test_init_langfuse_handles_exception_gracefully(self, mock_get_client):
        """init_langfuse returns False when Langfuse raises an exception (not configured)."""
        from hazn_platform.orchestrator.tracing import init_langfuse

        mock_get_client.side_effect = Exception("Langfuse not configured")

        result = init_langfuse()
        assert result is False


# -- start_workflow_trace --------------------------------------------------


@pytest.mark.django_db
class TestStartWorkflowTrace:
    @patch("hazn_platform.orchestrator.tracing.get_client")
    def test_creates_trace_and_stores_trace_id(
        self, mock_get_client, workflow_run
    ):
        """start_workflow_trace creates a Langfuse trace and stores trace_id on WorkflowRun."""
        from hazn_platform.orchestrator.tracing import start_workflow_trace

        mock_client = MagicMock()
        mock_trace = MagicMock()
        mock_trace.id = "trace-abc-123"
        mock_client.trace.return_value = mock_trace
        mock_get_client.return_value = mock_client

        trace_id = start_workflow_trace(workflow_run)

        assert trace_id == "trace-abc-123"
        workflow_run.refresh_from_db()
        assert workflow_run.langfuse_trace_id == "trace-abc-123"

    @patch("hazn_platform.orchestrator.tracing.get_client")
    def test_trace_has_correct_tags(self, mock_get_client, workflow_run):
        """start_workflow_trace creates trace with l2, l3, and run tags."""
        from hazn_platform.orchestrator.tracing import start_workflow_trace

        mock_client = MagicMock()
        mock_trace = MagicMock()
        mock_trace.id = "trace-xyz"
        mock_client.trace.return_value = mock_trace
        mock_get_client.return_value = mock_client

        start_workflow_trace(workflow_run)

        call_kwargs = mock_client.trace.call_args[1]
        tags = call_kwargs["tags"]
        assert f"l2:{workflow_run.agency_id}" in tags
        assert f"l3:{workflow_run.end_client_id}" in tags
        assert f"run:{workflow_run.pk}" in tags

    @patch("hazn_platform.orchestrator.tracing.get_client")
    def test_trace_has_correct_metadata(self, mock_get_client, workflow_run):
        """start_workflow_trace creates trace with l2_client_id, l3_client_id, workflow metadata."""
        from hazn_platform.orchestrator.tracing import start_workflow_trace

        mock_client = MagicMock()
        mock_trace = MagicMock()
        mock_trace.id = "trace-meta"
        mock_client.trace.return_value = mock_trace
        mock_get_client.return_value = mock_client

        start_workflow_trace(workflow_run)

        call_kwargs = mock_client.trace.call_args[1]
        metadata = call_kwargs["metadata"]
        assert metadata["l2_client_id"] == str(workflow_run.agency_id)
        assert metadata["l3_client_id"] == str(workflow_run.end_client_id)
        assert metadata["workflow_run_id"] == str(workflow_run.pk)
        assert metadata["workflow_name"] == "website"

    @patch("hazn_platform.orchestrator.tracing.get_client")
    def test_returns_none_when_langfuse_unavailable(
        self, mock_get_client, workflow_run
    ):
        """start_workflow_trace returns None when Langfuse raises an exception."""
        from hazn_platform.orchestrator.tracing import start_workflow_trace

        mock_get_client.side_effect = Exception("Langfuse not configured")

        trace_id = start_workflow_trace(workflow_run)

        assert trace_id is None
        workflow_run.refresh_from_db()
        assert workflow_run.langfuse_trace_id == ""

    @patch("hazn_platform.orchestrator.tracing.get_client")
    def test_non_fatal_does_not_modify_workflow_run_on_error(
        self, mock_get_client, workflow_run
    ):
        """start_workflow_trace does not crash or modify run status on error."""
        from hazn_platform.orchestrator.tracing import start_workflow_trace

        mock_get_client.side_effect = RuntimeError("Connection refused")

        # Should not raise
        result = start_workflow_trace(workflow_run)
        assert result is None


# -- start_phase_span ------------------------------------------------------


@pytest.mark.django_db
class TestStartPhaseSpan:
    @patch("hazn_platform.orchestrator.tracing.get_client")
    def test_creates_child_span(self, mock_get_client):
        """start_phase_span creates a span on the Langfuse client."""
        from hazn_platform.orchestrator.tracing import start_phase_span

        mock_client = MagicMock()
        mock_span = MagicMock()
        mock_span.id = "span-phase-1"
        mock_client.span.return_value = mock_span
        mock_get_client.return_value = mock_client

        span_id = start_phase_span("trace-abc", "strategy")

        assert span_id == "span-phase-1"
        call_kwargs = mock_client.span.call_args[1]
        assert call_kwargs["trace_id"] == "trace-abc"
        assert call_kwargs["name"] == "phase-strategy"

    @patch("hazn_platform.orchestrator.tracing.get_client")
    def test_returns_none_when_langfuse_unavailable(self, mock_get_client):
        """start_phase_span returns None when Langfuse is unavailable."""
        from hazn_platform.orchestrator.tracing import start_phase_span

        mock_get_client.side_effect = Exception("Not configured")

        result = start_phase_span("trace-abc", "strategy")
        assert result is None


# -- start_tool_span -------------------------------------------------------


@pytest.mark.django_db
class TestStartToolSpan:
    @patch("hazn_platform.orchestrator.tracing.get_client")
    def test_creates_tool_span(self, mock_get_client):
        """start_tool_span creates a span for an MCP tool call."""
        from hazn_platform.orchestrator.tracing import start_tool_span

        mock_client = MagicMock()
        mock_span = MagicMock()
        mock_span.id = "span-tool-1"
        mock_client.span.return_value = mock_span
        mock_get_client.return_value = mock_client

        span_id = start_tool_span("trace-abc", "get_credentials")

        assert span_id == "span-tool-1"
        call_kwargs = mock_client.span.call_args[1]
        assert call_kwargs["name"] == "tool-get_credentials"
        assert call_kwargs["metadata"]["tool_name"] == "get_credentials"

    @patch("hazn_platform.orchestrator.tracing.get_client")
    def test_returns_none_when_langfuse_unavailable(self, mock_get_client):
        """start_tool_span returns None when Langfuse is unavailable."""
        from hazn_platform.orchestrator.tracing import start_tool_span

        mock_get_client.side_effect = Exception("Not configured")

        result = start_tool_span("trace-abc", "get_credentials")
        assert result is None

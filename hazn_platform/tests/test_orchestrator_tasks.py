"""Tests for Celery tasks: run_workflow.

Covers:
- run_workflow creates session, loads workflow, runs executor, returns pk
- run_workflow handles SoftTimeLimitExceeded (calls session.fail)
- run_workflow handles general exceptions (calls session.fail, re-raises)
- tasks.py has no SSE event references (executor handles them)
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

# Install SDK stubs so executor can be imported (module-level fail-fast)
_sdk_module = MagicMock()
if "claude_agent_sdk" not in sys.modules:
    sys.modules["claude_agent_sdk"] = _sdk_module
if "claude_code_sdk" not in sys.modules:
    sys.modules["claude_code_sdk"] = _sdk_module


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestRunWorkflowTask:
    """Tests for the run_workflow Celery task."""

    def test_task_has_correct_time_limits(self):
        """run_workflow has time_limit of 4hr+5min and soft_time_limit of 4hr."""
        from hazn_platform.orchestrator.tasks import run_workflow

        assert run_workflow.time_limit == 4 * 3600 + 300
        assert run_workflow.soft_time_limit == 4 * 3600

    def test_task_is_celery_shared_task(self):
        """run_workflow has .delay attribute (is a Celery task)."""
        from hazn_platform.orchestrator.tasks import run_workflow

        assert hasattr(run_workflow, "delay")

    def test_creates_session_and_executes(self):
        """run_workflow creates WorkflowSession, loads workflow, runs executor, returns pk."""
        mock_workflow = MagicMock()
        mock_run = MagicMock()
        mock_run.pk = "run-abc"
        mock_run.celery_task_id = ""

        mock_session_instance = MagicMock()
        mock_session_instance.workflow_run = mock_run

        mock_executor = MagicMock()

        async def mock_run_coro():
            return mock_run

        mock_executor.run.return_value = mock_run_coro()

        mock_registry = MagicMock()
        mock_agency = MagicMock()
        mock_client = MagicMock()

        with patch(
            "hazn_platform.core.models.Agency.objects",
        ) as mock_agency_mgr, patch(
            "hazn_platform.core.models.EndClient.objects",
        ) as mock_client_mgr, patch(
            "hazn_platform.orchestrator.workflow_parser.load_workflow",
            return_value=mock_workflow,
        ), patch(
            "hazn_platform.orchestrator.session.WorkflowSession",
            return_value=mock_session_instance,
        ) as mock_session_cls, patch(
            "hazn_platform.orchestrator.executor.WorkflowExecutor",
            return_value=mock_executor,
        ) as mock_executor_cls, patch(
            "hazn_platform.orchestrator.apps._REGISTRY_SINGLETON",
            mock_registry,
        ), patch(
            "hazn_platform.orchestrator.tools.build_registry",
            return_value=mock_registry,
        ):
            mock_agency_mgr.get.return_value = mock_agency
            mock_client_mgr.get.return_value = mock_client

            from hazn_platform.orchestrator.tasks import run_workflow

            # Celery bind=True: calling directly invokes with self=task
            # Use .apply() which provides self automatically
            result = run_workflow("website", "agency-1", "client-1", "test-trigger")

        assert result == "run-abc"
        mock_session_cls.assert_called_once()
        mock_executor_cls.assert_called_once_with(
            mock_workflow, mock_session_instance, mock_registry
        )

    def test_handles_soft_time_limit_exceeded(self):
        """SoftTimeLimitExceeded calls session.fail with timeout message."""
        from celery.exceptions import SoftTimeLimitExceeded

        mock_run = MagicMock()
        mock_run.pk = "run-timeout"
        mock_run.celery_task_id = ""

        mock_session_instance = MagicMock()
        mock_session_instance.workflow_run = mock_run

        mock_executor = MagicMock()
        mock_executor.run.side_effect = SoftTimeLimitExceeded()

        mock_registry = MagicMock()

        with patch(
            "hazn_platform.core.models.Agency.objects",
        ) as mock_agency_mgr, patch(
            "hazn_platform.core.models.EndClient.objects",
        ) as mock_client_mgr, patch(
            "hazn_platform.orchestrator.workflow_parser.load_workflow",
            return_value=MagicMock(),
        ), patch(
            "hazn_platform.orchestrator.session.WorkflowSession",
            return_value=mock_session_instance,
        ), patch(
            "hazn_platform.orchestrator.executor.WorkflowExecutor",
            return_value=mock_executor,
        ), patch(
            "hazn_platform.orchestrator.apps._REGISTRY_SINGLETON",
            mock_registry,
        ), patch(
            "hazn_platform.orchestrator.tools.build_registry",
            return_value=mock_registry,
        ):
            mock_agency_mgr.get.return_value = MagicMock()
            mock_client_mgr.get.return_value = MagicMock()

            from hazn_platform.orchestrator.tasks import run_workflow

            result = run_workflow("website", "agency-1", "client-1", "test-trigger")

        mock_session_instance.fail.assert_called_once()
        fail_msg = mock_session_instance.fail.call_args[0][0]
        assert "timed out" in fail_msg.lower()
        assert result == "run-timeout"

    def test_handles_general_exception(self):
        """General exception calls session.fail and re-raises."""
        mock_run = MagicMock()
        mock_run.pk = "run-error"
        mock_run.celery_task_id = ""

        mock_session_instance = MagicMock()
        mock_session_instance.workflow_run = mock_run

        mock_executor = MagicMock()
        mock_executor.run.side_effect = ValueError("Something broke")

        mock_registry = MagicMock()

        with patch(
            "hazn_platform.core.models.Agency.objects",
        ) as mock_agency_mgr, patch(
            "hazn_platform.core.models.EndClient.objects",
        ) as mock_client_mgr, patch(
            "hazn_platform.orchestrator.workflow_parser.load_workflow",
            return_value=MagicMock(),
        ), patch(
            "hazn_platform.orchestrator.session.WorkflowSession",
            return_value=mock_session_instance,
        ), patch(
            "hazn_platform.orchestrator.executor.WorkflowExecutor",
            return_value=mock_executor,
        ), patch(
            "hazn_platform.orchestrator.apps._REGISTRY_SINGLETON",
            mock_registry,
        ), patch(
            "hazn_platform.orchestrator.tools.build_registry",
            return_value=mock_registry,
        ):
            mock_agency_mgr.get.return_value = MagicMock()
            mock_client_mgr.get.return_value = MagicMock()

            from hazn_platform.orchestrator.tasks import run_workflow

            with pytest.raises(ValueError, match="Something broke"):
                run_workflow("website", "agency-1", "client-1", "test-trigger")

        mock_session_instance.fail.assert_called_once()

    def test_no_sse_events_in_tasks(self):
        """tasks.py source code does NOT reference send_workspace_event."""
        import inspect
        from hazn_platform.orchestrator import tasks

        source = inspect.getsource(tasks)
        assert "send_workspace_event" not in source

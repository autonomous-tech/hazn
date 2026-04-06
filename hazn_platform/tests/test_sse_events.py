"""Tests for SSE event emission during workflow execution.

Tests cover:
- Phase transition SSE events: phase_started, phase_completed, phase_failed
- Workflow-level SSE events: workflow_started, workflow_completed, workflow_failed
- Delivery phase rendering: validates AuditReportPayload, renders HTML, stores in output
- Failed delivery validation logs warning but does not crash the phase

Note: Tests that exercise async executor methods with real DB writes must use
transaction=True because sync_to_async runs ORM calls in separate threads.
Fixtures use get_or_create for transaction=True robustness (per Phase 9 pattern).
"""

import json
from contextlib import ExitStack
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hazn_platform.core.models import Agency, EndClient
from hazn_platform.orchestrator.models import (
    WorkflowRun,
)
from hazn_platform.orchestrator.workflow_models import (
    WorkflowPhaseSchema,
    WorkflowSchema,
)


@pytest.fixture
def sse_agency(db):
    obj, _ = Agency.objects.get_or_create(
        slug="sse-agency",
        defaults={"name": "SSE Agency"},
    )
    return obj


@pytest.fixture
def sse_end_client(sse_agency):
    obj, _ = EndClient.objects.get_or_create(
        slug="sse-client",
        agency=sse_agency,
        defaults={"name": "SSE Client"},
    )
    return obj


@pytest.fixture
def sse_workflow_run(sse_agency, sse_end_client):
    return WorkflowRun.objects.create(
        workflow_name="audit",
        agency=sse_agency,
        end_client=sse_end_client,
        triggered_by="test-user",
        status=WorkflowRun.Status.RUNNING,
    )


@pytest.fixture
def sse_mock_session(sse_workflow_run):
    """Create a mock WorkflowSession wrapping a real WorkflowRun."""
    session = MagicMock()
    session.workflow_run = sse_workflow_run
    session.start.return_value = sse_workflow_run
    session.end.return_value = sse_workflow_run
    session.fail.return_value = sse_workflow_run
    session.checkpoint.return_value = None
    session.log_conflicts.return_value = None
    session.get_memory.return_value = MagicMock()
    session._metering = MagicMock()
    return session


def _make_run_result(status="completed", final_text="Phase completed.", **kwargs):
    """Create a mock RunResult for testing."""
    from hazn_platform.orchestrator.agent_runner import RunResult

    return RunResult(
        status=status,
        final_text=final_text,
        artifacts=[],
        usage={"total_tokens": 150, "total_cost": 0.01, "turns": 1},
        **kwargs,
    )


def _make_workflow(phases=None, checkpoints=None):
    """Build a minimal WorkflowSchema for testing."""
    if phases is None:
        phases = [
            WorkflowPhaseSchema(
                id="strategy",
                name="Strategy",
                agent="strategist",
                depends_on=[],
                outputs=["strategy_brief"],
                tools=["tool-a"],
            ),
        ]
    return WorkflowSchema(
        name="test-workflow",
        description="Test workflow",
        trigger="manual",
        phases=phases,
        checkpoints=checkpoints or [],
    )


def _apply_standard_patches(stack):
    """Apply all standard executor patches via an ExitStack. Returns dict of mocks."""
    mocks = {}
    mocks["get_or_create_agent"] = stack.enter_context(
        patch(
            "hazn_platform.orchestrator.executor.get_or_create_agent",
            return_value="agent-123",
        )
    )
    mocks["reconcile_tools"] = stack.enter_context(
        patch("hazn_platform.orchestrator.executor.reconcile_tools")
    )
    mocks["assemble_prompt"] = stack.enter_context(
        patch(
            "hazn_platform.orchestrator.executor.assemble_prompt",
            return_value="system prompt",
        )
    )
    mocks["should_run_qa"] = stack.enter_context(
        patch(
            "hazn_platform.orchestrator.executor.should_run_qa",
            return_value=False,
        )
    )
    mocks["detect_conflicts"] = stack.enter_context(
        patch(
            "hazn_platform.orchestrator.executor.detect_conflicts",
            return_value=[],
        )
    )
    mocks["process_conflicts"] = stack.enter_context(
        patch(
            "hazn_platform.orchestrator.executor.process_conflicts",
            return_value=[],
        )
    )
    return mocks


def _setup_mock_runner(stack, run_result=None):
    """Set up a mock AgentRunner via ExitStack. Returns mock_runner_cls."""
    if run_result is None:
        run_result = _make_run_result()
    mock_runner_cls = stack.enter_context(
        patch("hazn_platform.orchestrator.executor.AgentRunner")
    )
    mock_runner = AsyncMock()
    mock_runner.run = AsyncMock(return_value=run_result)
    mock_runner_cls.return_value = mock_runner
    return mock_runner_cls


# ── Phase transition SSE events ──────────────────────────────────────


@pytest.mark.django_db(transaction=True)
class TestPhaseSSEEvents:
    """Tests for SSE event emission at phase transition points."""

    @pytest.mark.asyncio
    async def test_phase_started_event_emitted_before_agent_run(
        self, sse_mock_session
    ):
        """_execute_phase emits phase_started SSE event before AgentRunner.run()."""
        from hazn_platform.orchestrator.executor import WorkflowExecutor

        workflow = _make_workflow()
        executor = WorkflowExecutor(workflow, sse_mock_session)

        with ExitStack() as stack:
            _apply_standard_patches(stack)
            mock_sse = stack.enter_context(
                patch("hazn_platform.orchestrator.executor.send_workspace_event")
            )
            _setup_mock_runner(stack)
            await executor._execute_phase(workflow.phases[0])

        # Verify phase_started was emitted
        sse_calls = [
            c
            for c in mock_sse.call_args_list
            if c.kwargs.get("data", {}).get("event") == "phase_started"
        ]
        assert len(sse_calls) >= 1, "phase_started SSE event not emitted"

    @pytest.mark.asyncio
    async def test_phase_completed_event_emitted_after_success(
        self, sse_mock_session
    ):
        """_execute_phase emits phase_completed SSE event after successful execution."""
        from hazn_platform.orchestrator.executor import WorkflowExecutor

        workflow = _make_workflow()
        executor = WorkflowExecutor(workflow, sse_mock_session)

        with ExitStack() as stack:
            _apply_standard_patches(stack)
            mock_sse = stack.enter_context(
                patch("hazn_platform.orchestrator.executor.send_workspace_event")
            )
            _setup_mock_runner(stack)
            await executor._execute_phase(workflow.phases[0])

        # Verify phase_completed was emitted
        completed_calls = [
            c
            for c in mock_sse.call_args_list
            if c.kwargs.get("data", {}).get("event") == "phase_completed"
        ]
        assert len(completed_calls) >= 1, "phase_completed SSE event not emitted"

    @pytest.mark.asyncio
    async def test_phase_failed_event_emitted_on_failure(self, sse_mock_session):
        """_execute_phase emits phase_failed SSE event with error text when phase fails."""
        from hazn_platform.orchestrator.executor import WorkflowExecutor

        workflow = _make_workflow()
        executor = WorkflowExecutor(workflow, sse_mock_session)

        error_result = _make_run_result(
            status="error",
            error_message="Agent crashed",
        )

        with ExitStack() as stack:
            _apply_standard_patches(stack)
            mock_sse = stack.enter_context(
                patch("hazn_platform.orchestrator.executor.send_workspace_event")
            )
            _setup_mock_runner(stack, run_result=error_result)
            with pytest.raises(RuntimeError):
                await executor._execute_phase(workflow.phases[0])

        # Verify phase_failed was emitted with error text
        failed_calls = [
            c
            for c in mock_sse.call_args_list
            if c.kwargs.get("data", {}).get("event") == "phase_failed"
        ]
        assert len(failed_calls) >= 1, "phase_failed SSE event not emitted"
        assert "error" in failed_calls[0].kwargs["data"]



# ── Workflow-level SSE events ────────────────────────────────────────


@pytest.mark.django_db(transaction=True)
class TestWorkflowSSEEvents:
    """Tests for workflow-level SSE events (start/complete/fail)."""

    @pytest.mark.asyncio
    async def test_workflow_started_event_emitted(self, sse_mock_session):
        """WorkflowExecutor.run() emits workflow_started event at the start."""
        from hazn_platform.orchestrator.executor import WorkflowExecutor

        workflow = _make_workflow()
        executor = WorkflowExecutor(workflow, sse_mock_session)

        async def stub_phase(phase):
            return {"result": "done"}

        with ExitStack() as stack:
            stack.enter_context(
                patch.object(executor, "_execute_phase", side_effect=stub_phase)
            )
            stack.enter_context(
                patch(
                    "hazn_platform.orchestrator.executor.detect_conflicts",
                    return_value=[],
                )
            )
            stack.enter_context(
                patch(
                    "hazn_platform.orchestrator.executor.process_conflicts",
                    return_value=[],
                )
            )
            mock_sse = stack.enter_context(
                patch("hazn_platform.orchestrator.executor.send_workspace_event")
            )
            await executor.run()

        # Verify workflow_started emitted
        started_calls = [
            c
            for c in mock_sse.call_args_list
            if c.kwargs.get("data", {}).get("event") == "workflow_started"
        ]
        assert len(started_calls) >= 1, "workflow_started SSE event not emitted"

    @pytest.mark.asyncio
    async def test_workflow_completed_event_emitted(self, sse_mock_session):
        """WorkflowExecutor.run() emits workflow_completed event on success."""
        from hazn_platform.orchestrator.executor import WorkflowExecutor

        workflow = _make_workflow()
        executor = WorkflowExecutor(workflow, sse_mock_session)

        async def stub_phase(phase):
            return {"result": "done"}

        with ExitStack() as stack:
            stack.enter_context(
                patch.object(executor, "_execute_phase", side_effect=stub_phase)
            )
            stack.enter_context(
                patch(
                    "hazn_platform.orchestrator.executor.detect_conflicts",
                    return_value=[],
                )
            )
            stack.enter_context(
                patch(
                    "hazn_platform.orchestrator.executor.process_conflicts",
                    return_value=[],
                )
            )
            mock_sse = stack.enter_context(
                patch("hazn_platform.orchestrator.executor.send_workspace_event")
            )
            await executor.run()

        # Verify workflow_completed emitted
        completed_calls = [
            c
            for c in mock_sse.call_args_list
            if c.kwargs.get("data", {}).get("event") == "workflow_completed"
        ]
        assert len(completed_calls) >= 1, "workflow_completed SSE event not emitted"

    @pytest.mark.asyncio
    async def test_workflow_failed_event_emitted_on_failure(self, sse_mock_session):
        """WorkflowExecutor.run() emits workflow_failed event when required phase fails."""
        from hazn_platform.orchestrator.executor import WorkflowExecutor

        workflow = _make_workflow()
        executor = WorkflowExecutor(workflow, sse_mock_session)

        async def fail_phase(phase):
            raise RuntimeError("Phase crashed")

        with ExitStack() as stack:
            stack.enter_context(
                patch.object(executor, "_execute_phase", side_effect=fail_phase)
            )
            stack.enter_context(
                patch(
                    "hazn_platform.orchestrator.executor.detect_conflicts",
                    return_value=[],
                )
            )
            stack.enter_context(
                patch(
                    "hazn_platform.orchestrator.executor.process_conflicts",
                    return_value=[],
                )
            )
            mock_sse = stack.enter_context(
                patch("hazn_platform.orchestrator.executor.send_workspace_event")
            )
            await executor.run()

        # Verify workflow_failed emitted
        failed_calls = [
            c
            for c in mock_sse.call_args_list
            if c.kwargs.get("data", {}).get("event") == "workflow_failed"
        ]
        assert len(failed_calls) >= 1, "workflow_failed SSE event not emitted"
        assert "error" in failed_calls[0].kwargs["data"]


# ── Delivery phase rendering ─────────────────────────────────────────


@pytest.mark.django_db(transaction=True)
class TestDeliveryPhaseRendering:
    """Tests for delivery phase Jinja2 rendering pipeline."""

    @pytest.mark.asyncio
    async def test_delivery_phase_validates_and_renders_html(self, sse_mock_session):
        """Delivery phase output validated as AuditReportPayload and rendered to HTML."""
        from hazn_platform.orchestrator.executor import WorkflowExecutor

        delivery_output = json.dumps(
            {
                "executive_summary": "Test summary",
                "findings": [
                    {
                        "severity": "high",
                        "description": "Test finding",
                        "evidence": "Evidence here",
                        "recommendation": "Fix it",
                    }
                ],
                "recommendations": [
                    {
                        "priority": "high",
                        "action": "Do this",
                        "impact": "Big impact",
                    }
                ],
                "scores": {"seo": 85, "performance": 70},
                "client_name": "Test Client",
                "report_date": "2026-03-06",
            }
        )

        workflow = _make_workflow(
            phases=[
                WorkflowPhaseSchema(
                    id="delivery",
                    name="Delivery",
                    agent="delivery-agent",
                    depends_on=[],
                    outputs=["report"],
                    tools=[],
                ),
            ]
        )
        executor = WorkflowExecutor(workflow, sse_mock_session)

        with ExitStack() as stack:
            _apply_standard_patches(stack)
            stack.enter_context(
                patch("hazn_platform.orchestrator.executor.send_workspace_event")
            )
            _setup_mock_runner(
                stack,
                run_result=_make_run_result(final_text=delivery_output),
            )
            mock_render = stack.enter_context(
                patch(
                    "hazn_platform.orchestrator.executor.render_report",
                    return_value="<html>Rendered</html>",
                )
            )
            output = await executor._execute_phase(workflow.phases[0])

        assert output is not None
        assert output.get("html_content") == "<html>Rendered</html>"
        assert output.get("markdown_source") == delivery_output
        mock_render.assert_called_once()

    @pytest.mark.asyncio
    async def test_delivery_raw_json_stored_in_markdown_source(
        self, sse_mock_session
    ):
        """Raw agent JSON output stored in markdown_source field of output dict."""
        from hazn_platform.orchestrator.executor import WorkflowExecutor

        delivery_output = json.dumps(
            {
                "executive_summary": "Summary",
                "findings": [],
                "recommendations": [],
                "scores": {"seo": 90},
            }
        )

        workflow = _make_workflow(
            phases=[
                WorkflowPhaseSchema(
                    id="delivery",
                    name="Delivery",
                    agent="delivery-agent",
                    depends_on=[],
                    outputs=["report"],
                    tools=[],
                ),
            ]
        )
        executor = WorkflowExecutor(workflow, sse_mock_session)

        with ExitStack() as stack:
            _apply_standard_patches(stack)
            stack.enter_context(
                patch("hazn_platform.orchestrator.executor.send_workspace_event")
            )
            _setup_mock_runner(
                stack,
                run_result=_make_run_result(final_text=delivery_output),
            )
            stack.enter_context(
                patch(
                    "hazn_platform.orchestrator.executor.render_report",
                    return_value="<html>Report</html>",
                )
            )
            output = await executor._execute_phase(workflow.phases[0])

        assert output["markdown_source"] == delivery_output

    @pytest.mark.asyncio
    async def test_invalid_delivery_output_logs_warning_no_crash(
        self, sse_mock_session
    ):
        """Invalid delivery output logs warning but phase completes with empty html_content."""
        from hazn_platform.orchestrator.executor import WorkflowExecutor

        workflow = _make_workflow(
            phases=[
                WorkflowPhaseSchema(
                    id="delivery",
                    name="Delivery",
                    agent="delivery-agent",
                    depends_on=[],
                    outputs=["report"],
                    tools=[],
                ),
            ]
        )
        executor = WorkflowExecutor(workflow, sse_mock_session)

        with ExitStack() as stack:
            _apply_standard_patches(stack)
            stack.enter_context(
                patch("hazn_platform.orchestrator.executor.send_workspace_event")
            )
            _setup_mock_runner(
                stack,
                run_result=_make_run_result(final_text="not valid json {{{"),
            )
            output = await executor._execute_phase(workflow.phases[0])

        # Phase should complete (not crash)
        assert output is not None
        assert output["status"] == "completed"
        assert output.get("html_content") == ""
        assert output.get("markdown_source") == "not valid json {{{"

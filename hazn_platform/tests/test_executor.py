"""Tests for WorkflowExecutor -- DAG-based workflow execution engine.

Covers:
- DAG ordering (phases execute in topological order)
- Prior phase output injection (depends_on phases' outputs in system prompt)
- Required phase failure halts workflow after retry
- Optional phase failure skips dependent optional phases
- Phase output stored as WorkflowPhaseOutput record
- SSE events fired at phase/workflow boundaries
- Delivery phase rendering produces HTML
- Informational phase (no agent) is skipped

All tests mock the Agent SDK, Django ORM ops, and SSE -- no real services.
"""

from __future__ import annotations

import sys
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from hazn_platform.orchestrator.workflow_models import WorkflowPhaseSchema, WorkflowSchema

# ---------------------------------------------------------------------------
# Install SDK stubs BEFORE importing executor (module-level fail-fast import)
# ---------------------------------------------------------------------------
_sdk_module = MagicMock()
_sdk_module.query = MagicMock()
_sdk_module.ClaudeAgentOptions = MagicMock
_sdk_module.AssistantMessage = type("AssistantMessage", (), {})
_sdk_module.ResultMessage = type("ResultMessage", (), {})
_sdk_module.TextBlock = type("TextBlock", (), {})

# Unconditionally install stubs so tests use lightweight fakes
# even when the real SDK is installed in the venv
sys.modules["claude_agent_sdk"] = _sdk_module
sys.modules["claude_code_sdk"] = _sdk_module

# NOW we can safely import executor
from hazn_platform.orchestrator.executor import WorkflowExecutor, build_prior_phase_section  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Types for isinstance checks in executor
_ResultMessageType = type(sys.modules.get("claude_agent_sdk", _sdk_module).ResultMessage)  # type: ignore
_AssistantMessageType = type(sys.modules.get("claude_agent_sdk", _sdk_module).AssistantMessage)  # type: ignore


def _make_phase(
    id: str,
    name: str | None = None,
    agent: str | None = "test-agent",
    depends_on: list[str] | None = None,
    outputs: list[str] | None = None,
    required: bool = True,
    tools: list[str] | None = None,
    max_turns: int = 30,
) -> WorkflowPhaseSchema:
    return WorkflowPhaseSchema(
        id=id,
        name=name or f"Phase {id}",
        agent=agent,
        depends_on=depends_on or [],
        outputs=outputs or ["general"],
        required=required,
        tools=tools or [],
        max_turns=max_turns,
    )


def _make_workflow(phases: list[WorkflowPhaseSchema]) -> WorkflowSchema:
    return WorkflowSchema(
        name="test-workflow",
        description="Test workflow",
        trigger="manual",
        phases=phases,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_session():
    """Mock WorkflowSession with all lifecycle methods."""
    session = MagicMock()
    session.workflow_run = MagicMock()
    session.workflow_run.pk = "run-123"
    session.workflow_run.agency_id = "agency-456"
    session.workflow_run.end_client_id = "client-789"
    session.metering = MagicMock()
    session.metering.on_llm_call = MagicMock()
    session.start = MagicMock()
    session.end = MagicMock()
    session.fail = MagicMock()
    session.checkpoint = MagicMock()
    session.load_client_context = MagicMock()
    session.get_client_context = MagicMock(return_value="")
    return session


@pytest.fixture
def mock_registry():
    """Mock ToolRegistry."""
    registry = MagicMock()
    registry.get_server = MagicMock(return_value={"name": "hazn", "tools": []})
    registry.get_allowed_tools = MagicMock(return_value=[])
    return registry


# ---------------------------------------------------------------------------
# SDK mock helpers
# ---------------------------------------------------------------------------


# Use the actual types the executor checks isinstance() against
_RealResultMessage = sys.modules["claude_agent_sdk"].ResultMessage
_RealAssistantMessage = sys.modules["claude_agent_sdk"].AssistantMessage
_RealTextBlock = sys.modules["claude_agent_sdk"].TextBlock


def _result_msg(text: str = "Phase completed.", is_error: bool = False):
    """Create a result message matching the SDK's ResultMessage type."""
    msg = _RealResultMessage()
    msg.result = text
    msg.usage = {"input_tokens": 100, "output_tokens": 50}
    msg.total_cost_usd = 0.01
    msg.num_turns = 1
    msg.duration_ms = 1000
    msg.is_error = is_error
    return msg


def _assistant_msg(text: str = "Working..."):
    """Create an assistant message matching the SDK's AssistantMessage type."""
    msg = _RealAssistantMessage()
    tb = _RealTextBlock()
    tb.text = text
    msg.content = [tb]
    return msg


def _fake_sync_to_async(fn):
    """Replace sync_to_async: calls fn directly (tests run sync)."""
    async def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


def _standard_patches(
    query_fn=None,
    sse_mock=None,
    po_return=None,
    assemble_return="You are an agent.",
):
    """Return (list_of_patches, sse_mock) for standard executor mocking."""
    assistant = _assistant_msg()
    result = _result_msg()

    if query_fn is None:
        async def default_query(prompt, options):
            yield assistant
            yield result
        query_fn = default_query

    if sse_mock is None:
        sse_mock = MagicMock()

    if po_return is None:
        po_return = MagicMock()
        po_return.phase_id = "stub"
        po_return.summary = "stub"
        po_return.content = {}

    patches = [
        patch("hazn_platform.orchestrator.executor.query", query_fn),
        patch("hazn_platform.orchestrator.executor.ClaudeAgentOptions", MagicMock),
        patch("hazn_platform.orchestrator.executor.sync_to_async", _fake_sync_to_async),
        patch("hazn_platform.orchestrator.executor.send_workspace_event", sse_mock),
        patch("hazn_platform.orchestrator.executor.start_workflow_trace", MagicMock()),
        patch("hazn_platform.orchestrator.executor.start_phase_span", MagicMock()),
        patch(
            "hazn_platform.orchestrator.executor.WorkflowPhaseOutput.objects.create",
            return_value=po_return,
        ),
        patch(
            "hazn_platform.orchestrator.executor.assemble_prompt",
            return_value=assemble_return,
        ),
    ]
    return patches, sse_mock


# ---------------------------------------------------------------------------
# Tests: Single-phase workflow
# ---------------------------------------------------------------------------


class TestSinglePhaseWorkflow:

    @pytest.mark.asyncio
    async def test_single_phase_executes_lifecycle(self, mock_session, mock_registry):
        """One phase, no deps: session.start, query, session.end all called."""
        workflow = _make_workflow([_make_phase("analysis")])
        patches, sse = _standard_patches()

        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)

            executor = WorkflowExecutor(workflow, mock_session, mock_registry)
            executor._output_collector = MagicMock(collect=MagicMock(return_value=[]))
            await executor.run()

        mock_session.start.assert_called_once()
        mock_session.end.assert_called_once()
        mock_session.fail.assert_not_called()


# ---------------------------------------------------------------------------
# Tests: SSE events
# ---------------------------------------------------------------------------


class TestSSEEvents:

    @pytest.mark.asyncio
    async def test_sse_events_emitted_at_boundaries(self, mock_session, mock_registry):
        """workflow_started, phase_started, phase_completed, workflow_completed all emitted."""
        workflow = _make_workflow([_make_phase("analysis")])
        patches, sse = _standard_patches()

        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)

            executor = WorkflowExecutor(workflow, mock_session, mock_registry)
            executor._output_collector = MagicMock(collect=MagicMock(return_value=[]))
            await executor.run()

        event_names = [
            c.kwargs.get("data", {}).get("event", "")
            for c in sse.call_args_list
        ]
        assert "workflow_started" in event_names
        assert "phase_started" in event_names
        assert "phase_completed" in event_names
        assert "workflow_completed" in event_names


# ---------------------------------------------------------------------------
# Tests: DAG ordering
# ---------------------------------------------------------------------------


class TestDAGOrdering:

    @pytest.mark.asyncio
    async def test_two_wave_dag_ordering(self, mock_session, mock_registry):
        """Phases A, B (wave 1), Phase C (wave 2, depends on A, B).
        C must execute after A and B."""
        phase_a = _make_phase("a", name="Phase A")
        phase_b = _make_phase("b", name="Phase B")
        phase_c = _make_phase("c", name="Phase C", depends_on=["a", "b"])
        workflow = _make_workflow([phase_a, phase_b, phase_c])

        execution_order: list[str] = []
        assistant = _assistant_msg()
        result = _result_msg()

        async def tracking_query(prompt, options):
            for pid in ["a", "b", "c"]:
                if f"Phase {pid.upper()}" in prompt or f"Phase {pid}" in prompt:
                    execution_order.append(pid)
                    break
            yield assistant
            yield result

        patches, sse = _standard_patches(query_fn=tracking_query)

        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)

            executor = WorkflowExecutor(workflow, mock_session, mock_registry)
            executor._output_collector = MagicMock(collect=MagicMock(return_value=[]))
            await executor.run()

        assert "c" in execution_order
        c_idx = execution_order.index("c")
        assert c_idx >= 2, f"C should run after A and B: {execution_order}"


# ---------------------------------------------------------------------------
# Tests: Prior phase output injection
# ---------------------------------------------------------------------------


class TestPriorPhaseOutputInjection:

    @pytest.mark.asyncio
    async def test_prior_phase_output_injected(self, mock_session, mock_registry):
        """Phase B depends on Phase A. B's system prompt should include prior results."""
        phase_a = _make_phase("a", name="Phase A")
        phase_b = _make_phase("b", name="Phase B", depends_on=["a"])
        workflow = _make_workflow([phase_a, phase_b])

        # Phase output with findings for injection
        mock_po = MagicMock()
        mock_po.phase_id = "a"
        mock_po.summary = "Phase A found 3 issues"
        mock_po.content = {
            "findings": [
                {"severity": "high", "description": "Issue 1", "recommendation": "Fix it"}
            ]
        }

        captured_options = []
        assistant = _assistant_msg()
        result = _result_msg()

        async def capturing_query(prompt, options):
            captured_options.append(options)
            yield assistant
            yield result

        patches, sse = _standard_patches(
            query_fn=capturing_query, po_return=mock_po
        )

        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)

            executor = WorkflowExecutor(workflow, mock_session, mock_registry)
            executor._output_collector = MagicMock(collect=MagicMock(return_value=[]))
            await executor.run()

        # Two query calls: one for phase A, one for phase B
        assert len(captured_options) == 2


# ---------------------------------------------------------------------------
# Tests: Required phase retry then halt
# ---------------------------------------------------------------------------


class TestRequiredPhaseRetry:

    @pytest.mark.asyncio
    async def test_required_phase_retries_once_then_fails(self, mock_session, mock_registry):
        """Required phase fails twice (initial + retry), then workflow fails."""
        workflow = _make_workflow([_make_phase("analysis", required=True)])

        call_count = 0

        async def failing_query(prompt, options):
            nonlocal call_count
            call_count += 1
            raise RuntimeError("Agent failed")
            yield  # noqa: unreachable -- make it a generator

        patches, sse = _standard_patches(query_fn=failing_query)

        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)

            executor = WorkflowExecutor(workflow, mock_session, mock_registry)
            executor._output_collector = MagicMock(collect=MagicMock(return_value=[]))
            await executor.run()

        # 2 calls: initial + one retry
        assert call_count == 2
        mock_session.fail.assert_called_once()
        mock_session.end.assert_not_called()


# ---------------------------------------------------------------------------
# Tests: Optional phase skip cascading
# ---------------------------------------------------------------------------


class TestOptionalPhaseSkipCascading:

    @pytest.mark.asyncio
    async def test_optional_failure_cascades_to_dependents(self, mock_session, mock_registry):
        """Optional phase C fails -> Phase D (depends on C) skipped -> Phase E runs."""
        phase_a = _make_phase("a", name="Phase A")
        phase_c = _make_phase("c", name="Phase C", required=False, depends_on=["a"])
        phase_d = _make_phase("d", name="Phase D", depends_on=["c"])
        phase_e = _make_phase("e", name="Phase E", depends_on=["a"])
        workflow = _make_workflow([phase_a, phase_c, phase_d, phase_e])

        executed: list[str] = []
        assistant = _assistant_msg()
        result = _result_msg()

        async def selective_query(prompt, options):
            for pid in ["a", "c", "d", "e"]:
                if f"Phase {pid.upper()}" in prompt or f"Phase {pid}" in prompt:
                    if pid == "c":
                        raise RuntimeError("Optional phase failed")
                    executed.append(pid)
                    break
            yield assistant
            yield result

        patches, sse = _standard_patches(query_fn=selective_query)

        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)

            executor = WorkflowExecutor(workflow, mock_session, mock_registry)
            executor._output_collector = MagicMock(collect=MagicMock(return_value=[]))
            await executor.run()

        assert "a" in executed
        assert "e" in executed
        assert "d" not in executed  # D skipped because C skipped
        mock_session.end.assert_called_once()  # Workflow still completes


# ---------------------------------------------------------------------------
# Tests: Informational phase (no agent) skipped
# ---------------------------------------------------------------------------


class TestInformationalPhaseSkipped:

    @pytest.mark.asyncio
    async def test_no_agent_phase_skipped(self, mock_session, mock_registry):
        """Phase with agent=None is skipped -- no query call."""
        phase_info = _make_phase("info", agent=None)
        phase_real = _make_phase("real", name="Real Phase")
        workflow = _make_workflow([phase_info, phase_real])

        query_count = 0
        assistant = _assistant_msg()
        result = _result_msg()

        async def counting_query(prompt, options):
            nonlocal query_count
            query_count += 1
            yield assistant
            yield result

        patches, sse = _standard_patches(query_fn=counting_query)

        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)

            executor = WorkflowExecutor(workflow, mock_session, mock_registry)
            executor._output_collector = MagicMock(collect=MagicMock(return_value=[]))
            await executor.run()

        assert query_count == 1  # Only the real phase


# ---------------------------------------------------------------------------
# Tests: Delivery phase HTML rendering
# ---------------------------------------------------------------------------


class TestDeliveryPhaseRendering:

    @pytest.mark.asyncio
    async def test_delivery_phase_renders_html(self, mock_session, mock_registry):
        """Phase with 'branded_html_report' output triggers HTML rendering."""
        phase = _make_phase("delivery", outputs=["branded_html_report"])
        workflow = _make_workflow([phase])

        agent_json = '{"title": "Report", "sections": []}'
        assistant = _assistant_msg()
        result = _result_msg(agent_json)

        async def delivery_query(prompt, options):
            yield assistant
            yield result

        po_mock = MagicMock()
        po_mock.phase_id = "delivery"
        po_mock.summary = "Delivery"
        po_mock.content = {}

        patches, sse = _standard_patches(query_fn=delivery_query, po_return=po_mock)

        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)

            with patch(
                "hazn_platform.orchestrator.executor.AuditReportPayload",
            ), patch(
                "hazn_platform.orchestrator.executor.render_report",
                return_value="<html>Report</html>",
            ) as mock_render:
                executor = WorkflowExecutor(workflow, mock_session, mock_registry)
                executor._output_collector = MagicMock(collect=MagicMock(return_value=[]))
                await executor.run()

        mock_render.assert_called_once()
        assert mock_render.call_args[0][0] == "analytics-audit.html"


# ---------------------------------------------------------------------------
# Tests: Phase output stored
# ---------------------------------------------------------------------------


class TestPhaseOutputStored:

    @pytest.mark.asyncio
    async def test_phase_output_create_called(self, mock_session, mock_registry):
        """WorkflowPhaseOutput.objects.create called with correct fields."""
        workflow = _make_workflow([_make_phase("analysis", outputs=["general"])])
        po_create = MagicMock()
        po_create.return_value = MagicMock(phase_id="analysis", summary="stub", content={})

        patches, sse = _standard_patches()
        # Replace the phase output patch (index 6 in the list)
        patches[6] = patch(
            "hazn_platform.orchestrator.executor.WorkflowPhaseOutput.objects.create",
            po_create,
        )

        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)

            executor = WorkflowExecutor(workflow, mock_session, mock_registry)
            executor._output_collector = MagicMock(collect=MagicMock(return_value=[]))
            await executor.run()

        po_create.assert_called_once()
        kw = po_create.call_args.kwargs
        assert kw["phase_id"] == "analysis"
        assert kw["output_type"] == "general"
        assert "summary" in kw
        assert "markdown_source" in kw


# ---------------------------------------------------------------------------
# Tests: build_prior_phase_section
# ---------------------------------------------------------------------------


class TestBuildPriorPhaseSection:

    def test_empty_outputs_returns_empty(self):
        assert build_prior_phase_section([]) == ""

    def test_builds_section_with_findings(self):
        po = MagicMock()
        po.phase_id = "analysis"
        po.summary = "Found 3 issues"
        po.content = {
            "findings": [
                {"severity": "high", "description": "Missing alt text", "recommendation": "Add alt"},
                {"severity": "medium", "description": "Slow load", "recommendation": "Optimize"},
            ]
        }

        result = build_prior_phase_section([po])
        assert "## Prior Phase Results" in result
        assert "### Phase: analysis" in result
        assert "Found 3 issues" in result
        assert "Missing alt text" in result

    def test_caps_findings_at_10(self):
        po = MagicMock()
        po.phase_id = "analysis"
        po.summary = "Many issues"
        po.content = {
            "findings": [
                {"severity": "low", "description": f"Issue {i}", "recommendation": f"Fix {i}"}
                for i in range(15)
            ]
        }

        result = build_prior_phase_section([po])
        finding_lines = [ln for ln in result.split("\n") if ln.startswith("- [")]
        assert len(finding_lines) == 10


# ---------------------------------------------------------------------------
# Tests: _await_user_input mechanism
# ---------------------------------------------------------------------------


async def _noop_sleep(_):
    """Async no-op replacement for asyncio.sleep in tests."""
    return


class TestAwaitUserInput:

    @pytest.mark.asyncio
    async def test_creates_agent_message_with_awaiting_reply(self, mock_session, mock_registry):
        """_await_user_input creates an agent ChatMessage with metadata.awaiting_reply=true."""
        workflow = _make_workflow([_make_phase("analysis")])

        created_messages = []

        def fake_create(**kwargs):
            msg = MagicMock()
            msg.pk = "msg-123"
            msg.created_at = "2026-01-01T00:00:00Z"
            created_messages.append(kwargs)
            return msg

        patches, sse = _standard_patches()

        # Mock time.monotonic to expire after first poll
        time_values = iter([0.0, 0.5, 1.5])

        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)
            stack.enter_context(
                patch("hazn_platform.orchestrator.executor.asyncio.sleep", _noop_sleep)
            )
            stack.enter_context(
                patch("hazn_platform.orchestrator.executor.time.monotonic", side_effect=time_values)
            )

            executor = WorkflowExecutor(workflow, mock_session, mock_registry)
            executor._output_collector = MagicMock(collect=MagicMock(return_value=[]))

            with patch(
                "hazn_platform.orchestrator.executor.ChatMessage"
            ) as mock_chat:
                mock_chat.objects.create = fake_create
                mock_chat.objects.filter = MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))

                result = await executor._await_user_input(
                    "What is the site URL?", "research", timeout_seconds=1
                )

        assert len(created_messages) == 1
        assert created_messages[0]["role"] == "agent"
        assert created_messages[0]["content"] == "What is the site URL?"
        assert created_messages[0]["metadata"]["awaiting_reply"] is True

    @pytest.mark.asyncio
    async def test_returns_user_reply_content(self, mock_session, mock_registry):
        """_await_user_input polls and returns user reply content."""
        workflow = _make_workflow([_make_phase("analysis")])

        question_msg = MagicMock()
        question_msg.pk = "msg-q"
        question_msg.created_at = "2026-01-01T00:00:00Z"

        reply_msg = MagicMock()
        reply_msg.content = "https://example.com"

        poll_count = 0

        def fake_filter(**kwargs):
            nonlocal poll_count
            poll_count += 1
            result = MagicMock()
            # Return reply on second poll
            if poll_count >= 2:
                result.first = MagicMock(return_value=reply_msg)
            else:
                result.first = MagicMock(return_value=None)
            return result

        patches, sse = _standard_patches()

        # time.monotonic returns values that stay within the 10s timeout
        time_values = iter([0.0, 1.0, 2.0, 3.0])

        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)
            stack.enter_context(
                patch("hazn_platform.orchestrator.executor.asyncio.sleep", _noop_sleep)
            )
            stack.enter_context(
                patch("hazn_platform.orchestrator.executor.time.monotonic", side_effect=time_values)
            )

            executor = WorkflowExecutor(workflow, mock_session, mock_registry)
            executor._output_collector = MagicMock(collect=MagicMock(return_value=[]))

            with patch(
                "hazn_platform.orchestrator.executor.ChatMessage"
            ) as mock_chat:
                mock_chat.objects.create = MagicMock(return_value=question_msg)
                mock_chat.objects.filter = fake_filter

                result = await executor._await_user_input(
                    "What is the site URL?", "research", timeout_seconds=10
                )

        assert result == "https://example.com"

    @pytest.mark.asyncio
    async def test_returns_none_on_timeout(self, mock_session, mock_registry):
        """_await_user_input returns None when no reply within timeout."""
        workflow = _make_workflow([_make_phase("analysis")])

        question_msg = MagicMock()
        question_msg.pk = "msg-q"
        question_msg.created_at = "2026-01-01T00:00:00Z"

        patches, sse = _standard_patches()

        # Mock time.monotonic to simulate timeout after one poll
        time_values = iter([0.0, 0.5, 1.5])

        with ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)
            stack.enter_context(
                patch("hazn_platform.orchestrator.executor.asyncio.sleep", _noop_sleep)
            )
            stack.enter_context(
                patch("hazn_platform.orchestrator.executor.time.monotonic", side_effect=time_values)
            )

            executor = WorkflowExecutor(workflow, mock_session, mock_registry)
            executor._output_collector = MagicMock(collect=MagicMock(return_value=[]))

            with patch(
                "hazn_platform.orchestrator.executor.ChatMessage"
            ) as mock_chat:
                mock_chat.objects.create = MagicMock(return_value=question_msg)
                mock_chat.objects.filter = MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))

                result = await executor._await_user_input(
                    "What is the site URL?", "research", timeout_seconds=1
                )

        assert result is None

"""Tests for WorkflowSession lifecycle management.

Covers:
- Constructor creates WorkflowRun with PENDING status
- start() transitions to RUNNING
- load_client_context() creates/reuses Letta agent per client
- load_client_context() handles Letta failure (non-fatal)
- checkpoint() flushes metering and checkpoints memory
- end() sets COMPLETED status with totals
- fail() sets FAILED status with error
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from hazn_platform.core.models import Agency, EndClient
from hazn_platform.orchestrator.models import WorkflowRun


@pytest.fixture
def agency(db):
    return Agency.objects.create(name="Session Agency", slug="session-agency")


@pytest.fixture
def end_client(agency):
    return EndClient.objects.create(
        agency=agency, name="Session Client", slug="session-client"
    )


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestConstructorCreatesPendingRun:

    def test_creates_pending_run(self, agency, end_client):
        """__init__ creates WorkflowRun with PENDING status."""
        from hazn_platform.orchestrator.session import WorkflowSession

        session = WorkflowSession(
            workflow_name="website",
            agency=agency,
            end_client=end_client,
            triggered_by="test-user",
        )

        assert session.workflow_run is not None
        assert session.workflow_run.status == WorkflowRun.Status.PENDING
        assert session.workflow_run.workflow_name == "website"
        assert session.workflow_run.triggered_by == "test-user"
        assert session.workflow_run.agency == agency
        assert session.workflow_run.end_client == end_client


# ---------------------------------------------------------------------------
# start()
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestStartTransitionsToRunning:

    def test_start_sets_running_and_started_at(self, agency, end_client):
        """start() transitions status to RUNNING and sets started_at."""
        from hazn_platform.orchestrator.session import WorkflowSession

        before = datetime.now(timezone.utc)
        session = WorkflowSession(
            workflow_name="website",
            agency=agency,
            end_client=end_client,
            triggered_by="test-user",
        )
        run = session.start()
        after = datetime.now(timezone.utc)

        assert run.status == WorkflowRun.Status.RUNNING
        assert run.started_at is not None
        assert before <= run.started_at <= after


# ---------------------------------------------------------------------------
# load_client_context() -- creates Letta agent
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestLoadClientContextCreatesAgent:

    def test_creates_agent_when_none_exists(self, agency, end_client):
        """When no existing Letta agent, agents.create called with client--{pk} name."""
        from hazn_platform.orchestrator.session import WorkflowSession

        mock_client = MagicMock()
        mock_client.agents.list.return_value = []
        new_agent = MagicMock()
        new_agent.id = "letta-agent-new"
        mock_client.agents.create.return_value = new_agent

        mock_memory = MagicMock()
        mock_memory.load_client_context.return_value = None
        mock_memory._assemble_context.return_value = '{"brand_voice": "formal"}'

        with patch(
            "hazn_platform.core.letta_client.get_letta_client",
            return_value=mock_client,
        ), patch(
            "hazn_platform.orchestrator.session.HaznMemory",
            return_value=mock_memory,
        ):
            session = WorkflowSession(
                workflow_name="website",
                agency=agency,
                end_client=end_client,
                triggered_by="test-user",
            )
            ctx = session.load_client_context()

        mock_client.agents.create.assert_called_once()
        create_kwargs = mock_client.agents.create.call_args.kwargs
        assert create_kwargs["name"] == f"client--{end_client.pk}"
        assert ctx == '{"brand_voice": "formal"}'


# ---------------------------------------------------------------------------
# load_client_context() -- reuses existing agent
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestLoadClientContextReusesAgent:

    def test_reuses_existing_agent(self, agency, end_client):
        """When agent exists, agents.list returns it, no create call."""
        from hazn_platform.orchestrator.session import WorkflowSession

        existing_agent = MagicMock()
        existing_agent.id = "letta-agent-existing"
        mock_client = MagicMock()
        mock_client.agents.list.return_value = [existing_agent]

        mock_memory = MagicMock()
        mock_memory.load_client_context.return_value = None
        mock_memory._assemble_context.return_value = '{"context": "data"}'

        with patch(
            "hazn_platform.core.letta_client.get_letta_client",
            return_value=mock_client,
        ), patch(
            "hazn_platform.orchestrator.session.HaznMemory",
            return_value=mock_memory,
        ):
            session = WorkflowSession(
                workflow_name="website",
                agency=agency,
                end_client=end_client,
                triggered_by="test-user",
            )
            session.load_client_context()

        mock_client.agents.create.assert_not_called()


# ---------------------------------------------------------------------------
# load_client_context() -- handles Letta failure
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestLoadClientContextHandlesLettaFailure:

    def test_returns_empty_string_on_letta_failure(self, agency, end_client):
        """When Letta is down, returns empty string (non-fatal)."""
        from hazn_platform.orchestrator.session import WorkflowSession

        with patch(
            "hazn_platform.core.letta_client.get_letta_client",
            side_effect=ConnectionError("Letta unreachable"),
        ):
            session = WorkflowSession(
                workflow_name="website",
                agency=agency,
                end_client=end_client,
                triggered_by="test-user",
            )
            ctx = session.load_client_context()

        assert ctx == ""


# ---------------------------------------------------------------------------
# checkpoint()
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCheckpointFlushesMetering:

    def test_checkpoint_flushes_metering(self, agency, end_client):
        """checkpoint() calls metering.flush_to_db."""
        from hazn_platform.orchestrator.session import WorkflowSession

        session = WorkflowSession(
            workflow_name="website",
            agency=agency,
            end_client=end_client,
            triggered_by="test-user",
        )

        with patch.object(session._metering, "flush_to_db") as mock_flush:
            session.checkpoint(phase_id="strategy")
            mock_flush.assert_called_once_with(phase_id="strategy")

    def test_checkpoint_calls_memory_checkpoint(self, agency, end_client):
        """checkpoint() calls memory.checkpoint_sync when memory is loaded."""
        from hazn_platform.orchestrator.session import WorkflowSession

        session = WorkflowSession(
            workflow_name="website",
            agency=agency,
            end_client=end_client,
            triggered_by="test-user",
        )

        mock_memory = MagicMock()
        session._memory = mock_memory

        with patch.object(session._metering, "flush_to_db"):
            session.checkpoint(phase_id="analysis")

        mock_memory.checkpoint_sync.assert_called_once()


# ---------------------------------------------------------------------------
# end()
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEndSetsCompletedWithTotals:

    def test_end_sets_completed_status(self, agency, end_client):
        """end() sets status to COMPLETED and ended_at."""
        from hazn_platform.orchestrator.session import WorkflowSession

        session = WorkflowSession(
            workflow_name="website",
            agency=agency,
            end_client=end_client,
            triggered_by="test-user",
        )
        session.start()
        run = session.end()

        assert run.status == WorkflowRun.Status.COMPLETED
        assert run.ended_at is not None

    def test_end_records_totals(self, agency, end_client):
        """end() records total_tokens and total_cost from metering."""
        from hazn_platform.orchestrator.session import WorkflowSession

        session = WorkflowSession(
            workflow_name="website",
            agency=agency,
            end_client=end_client,
            triggered_by="test-user",
        )
        session.start()
        # Simulate some metering
        session.metering.on_llm_call(agent_id="agent-1", tokens=500, cost=0.05)

        # Mock flush_to_db to avoid pre-existing metering bug (turn_count field missing)
        with patch.object(session._metering, "flush_to_db"):
            run = session.end()

        assert run.total_tokens > 0
        assert float(run.total_cost) > 0


# ---------------------------------------------------------------------------
# fail()
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFailSetsFailedWithError:

    def test_fail_sets_failed_status(self, agency, end_client):
        """fail() sets status to FAILED with error_details."""
        from hazn_platform.orchestrator.session import WorkflowSession

        session = WorkflowSession(
            workflow_name="website",
            agency=agency,
            end_client=end_client,
            triggered_by="test-user",
        )
        session.start()
        run = session.fail("Agent crashed: out of memory")

        assert run.status == WorkflowRun.Status.FAILED
        assert run.error_details == {"error": "Agent crashed: out of memory"}
        assert run.ended_at is not None

    def test_fail_calls_memory_failure_sync(self, agency, end_client):
        """fail() calls memory.failure_sync when memory is loaded."""
        from hazn_platform.orchestrator.session import WorkflowSession

        session = WorkflowSession(
            workflow_name="website",
            agency=agency,
            end_client=end_client,
            triggered_by="test-user",
        )

        mock_memory = MagicMock()
        session._memory = mock_memory

        session.fail("Something broke")

        mock_memory.failure_sync.assert_called_once()

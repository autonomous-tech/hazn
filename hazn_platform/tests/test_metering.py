"""Tests for orchestrator metering callback.

Tests cover per-agent token/cost/turn accumulation,
flush_to_db writing WorkflowAgent and WorkflowToolCall records,
agency-level config, and tool call metering.
"""

from __future__ import annotations

from decimal import Decimal
import pytest

from hazn_platform.core.models import Agency
from hazn_platform.core.models import EndClient
from hazn_platform.orchestrator.models import WorkflowAgent
from hazn_platform.orchestrator.models import WorkflowRun
from hazn_platform.orchestrator.models import WorkflowToolCall


@pytest.fixture
def agency(db):
    return Agency.objects.create(name="Test Agency", slug="test-agency-meter")


@pytest.fixture
def end_client(agency):
    return EndClient.objects.create(
        agency=agency, name="Test Client", slug="test-client-meter"
    )


@pytest.fixture
def workflow_run(agency, end_client):
    return WorkflowRun.objects.create(
        workflow_name="website",
        agency=agency,
        end_client=end_client,
        triggered_by="test-user",
    )


# ── MeteringCallback accumulation ────────────────────────────────────


@pytest.mark.django_db
class TestMeteringCallbackAccumulation:
    def test_on_llm_call_accumulates_tokens_cost_turns(self, workflow_run):
        """on_llm_call accumulates tokens, cost, and turns per agent_id."""
        from hazn_platform.orchestrator.metering import MeteringCallback

        meter = MeteringCallback(workflow_run_id=workflow_run.pk)

        meter.on_llm_call("agent-1", tokens=100, cost=0.01)
        meter.on_llm_call("agent-1", tokens=200, cost=0.02)
        meter.on_llm_call("agent-2", tokens=50, cost=0.005)

        totals = meter.get_totals()
        assert totals["total_tokens"] == 350
        assert totals["total_cost"] == pytest.approx(0.035)
        assert totals["total_turns"] == 3

    def test_per_agent_tracking(self, workflow_run):
        """on_llm_call tracks tokens/cost/turns per individual agent."""
        from hazn_platform.orchestrator.metering import MeteringCallback

        meter = MeteringCallback(workflow_run_id=workflow_run.pk)

        meter.on_llm_call("agent-1", tokens=100, cost=0.01)
        meter.on_llm_call("agent-2", tokens=200, cost=0.02)

        assert meter._agent_meters["agent-1"]["tokens"] == 100
        assert meter._agent_meters["agent-1"]["turns"] == 1
        assert meter._agent_meters["agent-2"]["tokens"] == 200
        assert meter._agent_meters["agent-2"]["turns"] == 1


# ── MeteringCallback flush_to_db ─────────────────────────────────────


@pytest.mark.django_db
class TestMeteringCallbackFlushToDb:
    def test_flush_creates_workflow_agent_records(self, workflow_run):
        """flush_to_db creates/updates WorkflowAgent records in database."""
        from hazn_platform.orchestrator.metering import MeteringCallback

        meter = MeteringCallback(workflow_run_id=workflow_run.pk)
        meter.on_llm_call("agent-1", tokens=100, cost=0.01)
        meter.on_llm_call("agent-2", tokens=200, cost=0.02)

        meter.flush_to_db(phase_id="strategy")

        agents = WorkflowAgent.objects.filter(workflow_run=workflow_run)
        assert agents.count() == 2

        agent_1 = agents.get(agent_id="agent-1")
        assert agent_1.total_tokens == 100
        assert agent_1.total_cost == Decimal("0.01")
        assert agent_1.turn_count == 1
        assert agent_1.phase_id == "strategy"

    def test_flush_updates_existing_records(self, workflow_run):
        """flush_to_db uses update_or_create to update existing records."""
        from hazn_platform.orchestrator.metering import MeteringCallback

        meter = MeteringCallback(workflow_run_id=workflow_run.pk)
        meter.on_llm_call("agent-1", tokens=100, cost=0.01)
        meter.flush_to_db(phase_id="strategy")

        # Add more usage and flush again
        meter.on_llm_call("agent-1", tokens=50, cost=0.005)
        meter.flush_to_db(phase_id="strategy")

        agents = WorkflowAgent.objects.filter(
            workflow_run=workflow_run, agent_id="agent-1"
        )
        assert agents.count() == 1
        assert agents.first().total_tokens == 150


# -- Tool call metering ---------------------------------------------------


@pytest.mark.django_db
class TestMeteringCallbackToolCalls:
    def test_on_tool_call_accumulates_count_and_latency(self, workflow_run):
        """on_tool_call accumulates call_count and latency per tool."""
        from hazn_platform.orchestrator.metering import MeteringCallback

        meter = MeteringCallback(workflow_run_id=workflow_run.pk)

        meter.on_tool_call("get_credentials", latency_ms=100)
        meter.on_tool_call("get_credentials", latency_ms=200)
        meter.on_tool_call("search_memory", latency_ms=50)

        assert meter._tool_meters["get_credentials"]["call_count"] == 2
        assert meter._tool_meters["get_credentials"]["total_latency_ms"] == 300
        assert meter._tool_meters["search_memory"]["call_count"] == 1
        assert meter._tool_meters["search_memory"]["total_latency_ms"] == 50

    def test_on_tool_call_tracks_success(self, workflow_run):
        """on_tool_call tracks success_count separately."""
        from hazn_platform.orchestrator.metering import MeteringCallback

        meter = MeteringCallback(workflow_run_id=workflow_run.pk)

        meter.on_tool_call("deploy", latency_ms=100, success=True)
        meter.on_tool_call("deploy", latency_ms=200, success=False)
        meter.on_tool_call("deploy", latency_ms=150, success=True)

        assert meter._tool_meters["deploy"]["call_count"] == 3
        assert meter._tool_meters["deploy"]["success_count"] == 2

    def test_flush_to_db_creates_tool_call_records(self, workflow_run):
        """flush_to_db writes WorkflowToolCall records with correct avg latency."""
        from hazn_platform.orchestrator.metering import MeteringCallback

        meter = MeteringCallback(workflow_run_id=workflow_run.pk)
        meter.on_tool_call("get_credentials", latency_ms=100)
        meter.on_tool_call("get_credentials", latency_ms=200)
        meter.on_tool_call("search_memory", latency_ms=60)

        meter.flush_to_db()

        tool_calls = WorkflowToolCall.objects.filter(workflow_run=workflow_run)
        assert tool_calls.count() == 2

        cred_call = tool_calls.get(tool_name="get_credentials")
        assert cred_call.call_count == 2
        assert cred_call.avg_latency_ms == 150  # (100 + 200) // 2

        mem_call = tool_calls.get(tool_name="search_memory")
        assert mem_call.call_count == 1
        assert mem_call.avg_latency_ms == 60

    def test_flush_to_db_updates_existing_tool_call_records(self, workflow_run):
        """flush_to_db uses update_or_create for idempotent tool call writes."""
        from hazn_platform.orchestrator.metering import MeteringCallback

        meter = MeteringCallback(workflow_run_id=workflow_run.pk)
        meter.on_tool_call("get_credentials", latency_ms=100)
        meter.flush_to_db()

        meter.on_tool_call("get_credentials", latency_ms=300)
        meter.flush_to_db()

        tool_calls = WorkflowToolCall.objects.filter(
            workflow_run=workflow_run, tool_name="get_credentials"
        )
        assert tool_calls.count() == 1
        assert tool_calls.first().call_count == 2

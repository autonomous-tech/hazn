"""Tests for orchestrator Django app models.

Tests cover CRUD operations, default values, FK relationships,
cascade deletes, status choices, and admin registrations for all
4 orchestrator models: WorkflowRun, WorkflowAgent, WorkflowToolCall,
WorkflowPhaseOutput.
"""

import uuid
from decimal import Decimal

import pytest
from django.contrib.admin.sites import site as admin_site

from hazn_platform.core.models import Agency
from hazn_platform.core.models import EndClient
from hazn_platform.orchestrator.models import WorkflowAgent
from hazn_platform.orchestrator.models import WorkflowPhaseOutput
from hazn_platform.orchestrator.models import WorkflowRun
from hazn_platform.orchestrator.models import WorkflowToolCall


@pytest.fixture
def agency(db):
    return Agency.objects.create(name="Test Agency", slug="test-agency-orch")


@pytest.fixture
def end_client(agency):
    return EndClient.objects.create(
        agency=agency, name="Test Client", slug="test-client-orch"
    )


@pytest.fixture
def workflow_run(agency, end_client):
    return WorkflowRun.objects.create(
        workflow_name="website",
        agency=agency,
        end_client=end_client,
        triggered_by="test-user",
    )


# -- WorkflowRun --


@pytest.mark.django_db
class TestWorkflowRun:
    def test_create_with_agency_and_endclient_fks(self, agency, end_client):
        """WorkflowRun can be created with Agency+EndClient FKs."""
        run = WorkflowRun.objects.create(
            workflow_name="website",
            agency=agency,
            end_client=end_client,
            triggered_by="api",
        )
        assert isinstance(run.pk, uuid.UUID)
        assert run.agency == agency
        assert run.end_client == end_client

    def test_status_defaults_to_pending(self, agency, end_client):
        """WorkflowRun.status defaults to 'pending'."""
        run = WorkflowRun.objects.create(
            workflow_name="website",
            agency=agency,
            end_client=end_client,
            triggered_by="api",
        )
        assert run.status == WorkflowRun.Status.PENDING
        assert run.status == "pending"

    def test_tokens_and_cost_default_to_zero(self, agency, end_client):
        """total_tokens and total_cost default to 0."""
        run = WorkflowRun.objects.create(
            workflow_name="website",
            agency=agency,
            end_client=end_client,
            triggered_by="api",
        )
        assert run.total_tokens == 0
        assert run.total_cost == Decimal("0")

    def test_status_choices(self):
        """WorkflowRun.Status choices include all 6 values."""
        choices = {c.value for c in WorkflowRun.Status}
        assert choices == {
            "pending",
            "running",
            "blocked",
            "completed",
            "failed",
            "timed_out",
        }

    def test_wall_clock_defaults(self, agency, end_client):
        """wall_clock_seconds defaults to 0."""
        run = WorkflowRun.objects.create(
            workflow_name="website",
            agency=agency,
            end_client=end_client,
            triggered_by="api",
        )
        assert run.wall_clock_seconds == 0

    def test_timestamps_and_json_defaults(self, agency, end_client):
        """started_at/ended_at are nullable; error_details/conflict_log have defaults."""
        run = WorkflowRun.objects.create(
            workflow_name="website",
            agency=agency,
            end_client=end_client,
            triggered_by="api",
        )
        assert run.started_at is None
        assert run.ended_at is None
        assert run.error_details == {}
        assert run.conflict_log == []
        assert run.created_at is not None


# -- WorkflowAgent --


@pytest.mark.django_db
class TestWorkflowAgent:
    def test_create_with_workflow_run_fk(self, workflow_run):
        """WorkflowAgent is created with FK to WorkflowRun, tracks agent details."""
        agent = WorkflowAgent.objects.create(
            workflow_run=workflow_run,
            agent_id="strategist--test-client",
            agent_type="strategist",
            phase_id="strategy",
        )
        assert isinstance(agent.pk, uuid.UUID)
        assert agent.workflow_run == workflow_run
        assert agent.agent_id == "strategist--test-client"
        assert agent.agent_type == "strategist"
        assert agent.phase_id == "strategy"

    def test_metering_defaults(self, workflow_run):
        """WorkflowAgent tokens and cost default to 0."""
        agent = WorkflowAgent.objects.create(
            workflow_run=workflow_run,
            agent_id="strategist--test-client",
            agent_type="strategist",
            phase_id="strategy",
        )
        assert agent.total_tokens == 0
        assert agent.total_cost == Decimal("0")


# -- WorkflowToolCall --


@pytest.mark.django_db
class TestWorkflowToolCall:
    def test_create_with_workflow_run_fk(self, workflow_run):
        """WorkflowToolCall is created with FK to WorkflowRun, tracks tool details."""
        tool_call = WorkflowToolCall.objects.create(
            workflow_run=workflow_run,
            tool_name="search_memory",
        )
        assert isinstance(tool_call.pk, uuid.UUID)
        assert tool_call.workflow_run == workflow_run
        assert tool_call.tool_name == "search_memory"

    def test_metering_defaults(self, workflow_run):
        """WorkflowToolCall call_count, total_cost, avg_latency_ms default to 0."""
        tool_call = WorkflowToolCall.objects.create(
            workflow_run=workflow_run,
            tool_name="search_memory",
        )
        assert tool_call.call_count == 0
        assert tool_call.total_cost == Decimal("0")
        assert tool_call.avg_latency_ms == 0


# -- WorkflowPhaseOutput --


@pytest.mark.django_db
class TestWorkflowPhaseOutput:
    def test_create_with_workflow_run_fk(self, workflow_run):
        """WorkflowPhaseOutput stores phase_id, output_type, and structured content."""
        output = WorkflowPhaseOutput.objects.create(
            workflow_run=workflow_run,
            phase_id="strategy",
            output_type="strategy_document",
            content={"title": "Strategy", "sections": ["market", "competitors"]},
        )
        assert isinstance(output.pk, uuid.UUID)
        assert output.workflow_run == workflow_run
        assert output.phase_id == "strategy"
        assert output.output_type == "strategy_document"
        assert output.content == {
            "title": "Strategy",
            "sections": ["market", "competitors"],
        }

    def test_content_defaults_to_empty_dict(self, workflow_run):
        """WorkflowPhaseOutput.content defaults to empty dict."""
        output = WorkflowPhaseOutput.objects.create(
            workflow_run=workflow_run,
            phase_id="ux",
            output_type="blueprint",
        )
        assert output.content == {}
        assert output.summary == ""

    def test_html_content_and_markdown_source_fields(self, workflow_run):
        """WorkflowPhaseOutput has html_content and markdown_source text fields."""
        output = WorkflowPhaseOutput.objects.create(
            workflow_run=workflow_run,
            phase_id="delivery",
            output_type="report",
            html_content="<h1>Report</h1>",
            markdown_source="# Report",
        )
        output.refresh_from_db()
        assert output.html_content == "<h1>Report</h1>"
        assert output.markdown_source == "# Report"

    def test_html_content_defaults_to_empty(self, workflow_run):
        """html_content and markdown_source default to empty strings."""
        output = WorkflowPhaseOutput.objects.create(
            workflow_run=workflow_run,
            phase_id="analysis",
            output_type="analysis",
        )
        assert output.html_content == ""
        assert output.markdown_source == ""


# -- Cascade Deletes --


@pytest.mark.django_db
class TestCascadeDeletes:
    def test_workflow_run_cascade_deletes_all_related(self, agency, end_client):
        """Deleting a WorkflowRun cascade-deletes WorkflowAgent, WorkflowToolCall,
        and WorkflowPhaseOutput records."""
        run = WorkflowRun.objects.create(
            workflow_name="website",
            agency=agency,
            end_client=end_client,
            triggered_by="test",
        )
        WorkflowAgent.objects.create(
            workflow_run=run,
            agent_id="strategist--client",
            agent_type="strategist",
            phase_id="strategy",
        )
        WorkflowToolCall.objects.create(
            workflow_run=run,
            tool_name="search_memory",
        )
        WorkflowPhaseOutput.objects.create(
            workflow_run=run,
            phase_id="strategy",
            output_type="document",
        )

        assert WorkflowAgent.objects.count() == 1
        assert WorkflowToolCall.objects.count() == 1
        assert WorkflowPhaseOutput.objects.count() == 1

        run.delete()

        assert WorkflowAgent.objects.count() == 0
        assert WorkflowToolCall.objects.count() == 0
        assert WorkflowPhaseOutput.objects.count() == 0


# -- Admin Registrations --


@pytest.mark.django_db
class TestAdminRegistrations:
    def test_all_four_models_registered(self):
        """Admin registrations exist for all 4 orchestrator models."""
        registered_models = set(admin_site._registry.keys())
        assert WorkflowRun in registered_models
        assert WorkflowAgent in registered_models
        assert WorkflowToolCall in registered_models
        assert WorkflowPhaseOutput in registered_models

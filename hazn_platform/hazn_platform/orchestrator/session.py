"""Workflow session lifecycle management.

Coordinates WorkflowRun status transitions, single-agent-per-client
Letta memory, and metering callback management for the duration of a
workflow execution.

One Letta agent per client (``client--{pk}``) accumulates memory across
all workflow phases and runs.  Client context is loaded once at workflow
start and injected into system prompts.

Public API
----------
* ``WorkflowSession`` -- one per workflow execution
"""

from __future__ import annotations

import logging
from datetime import datetime
from datetime import timezone
from decimal import Decimal

from hazn_platform.core.memory import HaznMemory
from hazn_platform.orchestrator.metering import MeteringCallback
from hazn_platform.orchestrator.models import WorkflowRun

logger = logging.getLogger(__name__)


class WorkflowSession:
    """Manages the lifecycle of a single workflow execution.

    Coordinates:
    - WorkflowRun status transitions (pending -> running -> completed/failed)
    - Single HaznMemory instance per client (one Letta agent per client)
    - MeteringCallback for per-agent cost tracking

    Per CRED-02: this class NEVER stores raw Vault secrets in
    WorkflowRun fields, error_details, or agent context.
    Credential access goes through the get_credentials MCP tool only.

    Parameters
    ----------
    workflow_name:
        Name of the workflow being executed (e.g. "website", "audit").
    agency:
        Agency (L2) model instance.
    end_client:
        EndClient (L3) model instance.
    triggered_by:
        Identifier for who/what triggered the workflow.
    """

    def __init__(
        self,
        workflow_name: str,
        agency: object,
        end_client: object,
        triggered_by: str,
    ) -> None:
        self._workflow_run = WorkflowRun.objects.create(
            workflow_name=workflow_name,
            agency=agency,
            end_client=end_client,
            triggered_by=triggered_by,
            status=WorkflowRun.Status.PENDING,
        )
        self._metering = MeteringCallback.from_agency(
            workflow_run_id=self._workflow_run.pk,
            agency=agency,
        )
        self._agency = agency
        self._end_client = end_client
        self._memory: HaznMemory | None = None
        self._letta_agent_id: str | None = None
        self._client_context: str = ""

        logger.info(
            "WorkflowSession created: run=%s workflow=%s agency=%s client=%s",
            self._workflow_run.pk,
            workflow_name,
            getattr(agency, "slug", "unknown"),
            getattr(end_client, "slug", "unknown"),
        )

    # ── Properties ────────────────────────────────────────────────────

    @property
    def workflow_run(self) -> WorkflowRun:
        """The WorkflowRun record for this session."""
        return self._workflow_run

    @property
    def metering(self) -> MeteringCallback:
        """The MeteringCallback for per-agent cost tracking."""
        return self._metering

    # ── Lifecycle Methods ─────────────────────────────────────────────

    def start(self) -> WorkflowRun:
        """Transition WorkflowRun from pending to running.

        Sets ``started_at`` to current UTC time.

        Returns
        -------
        WorkflowRun
            The updated workflow run record.
        """
        self._workflow_run.status = WorkflowRun.Status.RUNNING
        self._workflow_run.started_at = datetime.now(timezone.utc)
        self._workflow_run.save(update_fields=["status", "started_at"])
        logger.info(
            "WorkflowSession started: run=%s",
            self._workflow_run.pk,
        )
        return self._workflow_run

    def load_client_context(self) -> str:
        """Load client memory context from Letta.

        Creates or retrieves a single Letta agent per client using the
        naming convention ``client--{end_client.pk}``.  Hydrates
        HaznMemory and assembles the context string for system prompt
        injection.

        Returns
        -------
        str
            The assembled client context string (JSON).  Empty string
            if Letta is unavailable (non-fatal).
        """
        try:
            from hazn_platform.core.letta_client import get_letta_client

            client = get_letta_client()
            agent_name = f"client--{self._end_client.pk}"

            # Look up or create Letta agent for this client
            existing = list(client.agents.list(name=agent_name))
            if existing:
                self._letta_agent_id = existing[0].id
            else:
                agent = client.agents.create(
                    name=agent_name,
                    system="Hazn client memory agent",
                    memory_blocks=[
                        {"label": "active_client_context", "value": ""},
                    ],
                    tags=[f"l3:{self._end_client.pk}"],
                )
                self._letta_agent_id = agent.id

            # Create HaznMemory and hydrate from Letta
            self._memory = HaznMemory(
                agent_id=self._letta_agent_id,
                l3_client_id=self._end_client.pk,
                l2_agency_id=self._agency.pk,
            )
            self._memory.load_client_context()

            # Assemble and cache context string
            self._client_context = self._memory._assemble_context()

            logger.info(
                "Client context loaded: run=%s agent=%s client=%s (%d bytes)",
                self._workflow_run.pk,
                self._letta_agent_id,
                self._end_client.pk,
                len(self._client_context),
            )
            return self._client_context

        except Exception:
            logger.warning(
                "Failed to load client context (Letta may be down): "
                "run=%s client=%s",
                self._workflow_run.pk,
                getattr(self._end_client, "pk", "unknown"),
                exc_info=True,
            )
            self._client_context = ""
            return ""

    def get_client_context(self) -> str:
        """Return the cached client context string.

        Returns
        -------
        str
            The assembled client context string (JSON), or empty
            string if ``load_client_context()`` has not been called
            or Letta was unavailable.
        """
        return self._client_context

    def checkpoint(self, phase_id: str | None = None) -> None:
        """Checkpoint memory and flush metering after a phase completes.

        Calls ``checkpoint_sync()`` on the single HaznMemory instance
        and ``flush_to_db()`` on the metering callback.

        Parameters
        ----------
        phase_id:
            Optional phase identifier for metering records.
        """
        if self._memory is not None:
            self._memory.checkpoint_sync()

        self._metering.flush_to_db(phase_id=phase_id)
        self._workflow_run.save(update_fields=["last_activity_at"])

        logger.info(
            "WorkflowSession checkpoint: run=%s phase=%s",
            self._workflow_run.pk,
            phase_id,
        )

    def end(
        self,
        findings_by_agent: dict[str, list] | None = None,
    ) -> WorkflowRun:
        """Complete the workflow session.

        1. Ends the single HaznMemory session with findings
        2. Flushes metering to database
        3. Updates WorkflowRun: status=completed, ended_at, totals

        Parameters
        ----------
        findings_by_agent:
            Optional dict mapping agent_id to list of StructuredFinding.
            For the single-agent-per-client model, use the client
            Letta agent ID as the key.

        Returns
        -------
        WorkflowRun
            The updated workflow run record.
        """
        if self._memory is not None:
            findings_by_agent = findings_by_agent or {}
            agent_findings = findings_by_agent.get(
                self._letta_agent_id or "", []
            )
            self._memory.end_session(agent_findings)

        self._metering.flush_to_db()

        totals = self._metering.get_totals()
        self._workflow_run.status = WorkflowRun.Status.COMPLETED
        self._workflow_run.ended_at = datetime.now(timezone.utc)
        self._workflow_run.total_tokens = totals["total_tokens"]
        self._workflow_run.total_cost = Decimal(str(totals["total_cost"]))
        self._workflow_run.save(update_fields=[
            "status",
            "ended_at",
            "total_tokens",
            "total_cost",
            "last_activity_at",
        ])

        logger.info(
            "WorkflowSession ended: run=%s tokens=%d cost=$%.4f",
            self._workflow_run.pk,
            totals["total_tokens"],
            totals["total_cost"],
        )
        return self._workflow_run

    def fail(self, error: str) -> WorkflowRun:
        """Fail the workflow session with error details.

        1. Calls ``failure_sync()`` on HaznMemory
        2. Flushes metering to database
        3. Updates WorkflowRun: status=failed, ended_at, error_details

        Per CRED-02: error messages MUST NOT contain raw Vault secrets.
        The caller is responsible for sanitizing error messages.

        Parameters
        ----------
        error:
            Human-readable error description (no secrets!).

        Returns
        -------
        WorkflowRun
            The updated workflow run record.
        """
        if self._memory is not None:
            self._memory.failure_sync()

        self._metering.flush_to_db()

        self._workflow_run.status = WorkflowRun.Status.FAILED
        self._workflow_run.ended_at = datetime.now(timezone.utc)
        self._workflow_run.error_details = {"error": error}
        self._workflow_run.save(update_fields=[
            "status",
            "ended_at",
            "error_details",
            "last_activity_at",
        ])

        logger.warning(
            "WorkflowSession failed: run=%s error=%s",
            self._workflow_run.pk,
            error[:100],
        )
        return self._workflow_run

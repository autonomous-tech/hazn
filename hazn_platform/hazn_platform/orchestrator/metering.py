"""Real-time metering callback for workflow execution cost tracking.

Accumulates per-agent token usage, cost, and turn counts during
workflow execution.  Accumulates per-tool call counts and latency.
Provides flush_to_db for persisting to WorkflowAgent and WorkflowToolCall
records.

Public API
----------
* ``MeteringCallback`` -- instantiate per workflow run
* ``MeteringCallback.from_agency()`` -- factory from agency context
"""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal

logger = logging.getLogger(__name__)


class MeteringCallback:
    """Accumulates token usage and cost per-agent during workflow execution.

    Parameters
    ----------
    workflow_run_id:
        UUID of the WorkflowRun this callback is tracking.
    """

    def __init__(
        self,
        workflow_run_id: uuid.UUID,
    ) -> None:
        self.workflow_run_id = workflow_run_id
        self._agent_meters: dict[str, dict] = {}
        self._tool_meters: dict[str, dict] = {}

    @classmethod
    def from_agency(
        cls,
        workflow_run_id: uuid.UUID,
        agency: object,
    ) -> MeteringCallback:
        """Create a MeteringCallback for a workflow run.

        Parameters
        ----------
        workflow_run_id:
            UUID of the WorkflowRun.
        agency:
            Agency model instance (unused, kept for call-site compatibility).
        """
        return cls(workflow_run_id=workflow_run_id)

    def on_llm_call(self, agent_id: str, tokens: int, cost: float) -> None:
        """Record an LLM call for the given agent.

        Accumulates tokens, cost, and turn count.

        Parameters
        ----------
        agent_id:
            The agent ID that made the LLM call.
        tokens:
            Number of tokens consumed.
        cost:
            Cost in USD.
        """
        if agent_id not in self._agent_meters:
            self._agent_meters[agent_id] = {
                "tokens": 0,
                "cost": 0.0,
                "turns": 0,
            }

        meter = self._agent_meters[agent_id]
        meter["tokens"] += tokens
        meter["cost"] += cost
        meter["turns"] += 1

    def on_tool_call(
        self,
        tool_name: str,
        latency_ms: int,
        success: bool = True,
    ) -> None:
        """Record an MCP tool call.

        Accumulates per-tool call count, latency, and success count.

        Parameters
        ----------
        tool_name:
            Name of the MCP tool that was called.
        latency_ms:
            Wall-clock latency of the tool call in milliseconds.
        success:
            Whether the tool call succeeded. Default True.
        """
        if tool_name not in self._tool_meters:
            self._tool_meters[tool_name] = {
                "call_count": 0,
                "total_latency_ms": 0,
                "success_count": 0,
            }

        meter = self._tool_meters[tool_name]
        meter["call_count"] += 1
        meter["total_latency_ms"] += latency_ms
        if success:
            meter["success_count"] += 1

    def flush_to_db(self, phase_id: str | None = None) -> None:
        """Write accumulated metering to WorkflowAgent and WorkflowToolCall records.

        Uses ``update_or_create`` so repeated flushes update existing
        records rather than creating duplicates.

        Parameters
        ----------
        phase_id:
            Optional phase identifier for the WorkflowAgent record.
        """
        from hazn_platform.orchestrator.models import WorkflowAgent
        from hazn_platform.orchestrator.models import WorkflowToolCall

        for agent_id, meters in self._agent_meters.items():
            WorkflowAgent.objects.update_or_create(
                workflow_run_id=self.workflow_run_id,
                agent_id=agent_id,
                defaults={
                    "total_tokens": meters["tokens"],
                    "total_cost": Decimal(str(meters["cost"])),
                    "turn_count": meters["turns"],
                    "phase_id": phase_id or "",
                    "agent_type": agent_id.split("--")[0] if "--" in agent_id else agent_id,
                },
            )

        for tool_name, meters in self._tool_meters.items():
            avg_latency = meters["total_latency_ms"] // max(meters["call_count"], 1)
            WorkflowToolCall.objects.update_or_create(
                workflow_run_id=self.workflow_run_id,
                tool_name=tool_name,
                defaults={
                    "call_count": meters["call_count"],
                    "avg_latency_ms": avg_latency,
                },
            )

        logger.info(
            "Flushed metering for %d agents and %d tools (run=%s)",
            len(self._agent_meters),
            len(self._tool_meters),
            self.workflow_run_id,
        )

    def get_totals(self) -> dict:
        """Return aggregated totals across all agents.

        Returns
        -------
        dict
            Keys: ``total_tokens``, ``total_cost``, ``total_turns``.
        """
        total_tokens = sum(m["tokens"] for m in self._agent_meters.values())
        total_cost = sum(m["cost"] for m in self._agent_meters.values())
        total_turns = sum(m["turns"] for m in self._agent_meters.values())
        return {
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "total_turns": total_turns,
        }


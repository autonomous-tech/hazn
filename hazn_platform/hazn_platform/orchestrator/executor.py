"""DAG-based workflow execution engine with direct Agent SDK calls.

Interprets workflow YAML (via WorkflowSchema) to coordinate multi-agent
execution.  Uses graphlib.TopologicalSorter (via workflow_parser) to compute
parallel execution waves, calls Agent SDK ``query()`` directly per phase
with assembled system prompts and MCP tools, stores phase outputs as
WorkflowPhaseOutput records, and handles retry / skip cascading.

Each phase is executed via a direct ``query()`` call with no protocol
indirection.

Public API
----------
* ``WorkflowExecutor`` -- one per workflow execution, drives session lifecycle
* ``build_prior_phase_section`` -- assemble prior phase output for prompt injection
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
import uuid
from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async

from hazn_platform.orchestrator.models import ChatMessage, WorkflowPhaseOutput, WorkflowRun
from hazn_platform.orchestrator.output_collector import OutputCollector
from hazn_platform.orchestrator.prompt_assembler import assemble_prompt
from hazn_platform.orchestrator.tracing import start_workflow_trace, start_phase_span
from hazn_platform.orchestrator.workflow_parser import get_execution_order
from hazn_platform.deliverable_pipeline.renderer import render_report
from hazn_platform.deliverable_pipeline.schemas import AuditReportPayload
from hazn_platform.workspace.sse_views import send_workspace_event

if TYPE_CHECKING:
    from hazn_platform.orchestrator.session import WorkflowSession
    from hazn_platform.orchestrator.tools import ToolRegistry
    from hazn_platform.orchestrator.workflow_models import WorkflowPhaseSchema, WorkflowSchema

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SDK imports -- fail fast (Pitfall 8: SDK is required, not optional)
# ---------------------------------------------------------------------------

try:
    from claude_agent_sdk import (  # type: ignore[import-untyped]
        query,
        ClaudeAgentOptions,
        AssistantMessage,
        ResultMessage,
        TextBlock,
    )
except ImportError:
    try:
        from claude_code_sdk import (  # type: ignore[import-untyped]
            query,
            ClaudeAgentOptions,
            AssistantMessage,
            ResultMessage,
            TextBlock,
        )
    except ImportError as exc:
        raise ImportError(
            "Claude Agent SDK required: pip install claude-agent-sdk"
        ) from exc


# ---------------------------------------------------------------------------
# Auto-extraction of learnings from agent output
# ---------------------------------------------------------------------------

_LEARNING_CAP = 20  # Soft cap: warn above this

_LEARNING_PATTERNS = re.compile(
    r"(?:Key finding|I learned that|Note for future|Important insight)[:\s]+(.+?)(?:\n|$)",
    re.IGNORECASE | re.MULTILINE,
)


def _auto_extract_learnings(
    phase_output_text: str,
    client_id: uuid.UUID,
    agent_type: str,
) -> list:
    """Extract learnings from phase output text.

    Two extraction strategies:
    1. JSON: parse output as JSON, look for ``"learnings"`` key containing a
       list of dicts with ``"content"`` keys.
    2. Text patterns: regex match ``Key finding:``, ``I learned that``,
       ``Note for future:``, ``Important insight`` patterns.

    Auto-extracted learnings use ``confidence=0.6`` and
    ``source=RULE_EXTRACTED`` (lower confidence than explicit tool calls).

    Returns empty list on any error (non-fatal).
    """
    try:
        from hazn_platform.core.memory_types import CraftLearning, LearningSource

        learnings: list[CraftLearning] = []

        # Strategy 1: JSON extraction
        try:
            parsed = json.loads(phase_output_text)
            if isinstance(parsed, dict) and "learnings" in parsed:
                raw_learnings = parsed["learnings"]
                if isinstance(raw_learnings, list):
                    for item in raw_learnings:
                        content = item.get("content", "") if isinstance(item, dict) else str(item)
                        if content:
                            learnings.append(CraftLearning(
                                content=content,
                                source=LearningSource.RULE_EXTRACTED,
                                confidence=0.6,
                                agent_type=agent_type,
                                l3_client_id=client_id,
                            ))
        except (json.JSONDecodeError, TypeError, AttributeError):
            pass  # Not JSON, fall through to text patterns

        # Strategy 2: Text pattern extraction (only if no JSON learnings found)
        if not learnings:
            matches = _LEARNING_PATTERNS.findall(phase_output_text)
            for match in matches:
                content = match.strip()
                if content:
                    learnings.append(CraftLearning(
                        content=content,
                        source=LearningSource.RULE_EXTRACTED,
                        confidence=0.6,
                        agent_type=agent_type,
                        l3_client_id=client_id,
                    ))

        # Soft cap
        if len(learnings) > _LEARNING_CAP:
            logger.warning(
                "Auto-extraction found %d learnings (cap=%d), truncating",
                len(learnings),
                _LEARNING_CAP,
            )
            learnings = learnings[:_LEARNING_CAP]

        return learnings

    except Exception:
        logger.warning("_auto_extract_learnings failed (non-fatal)", exc_info=True)
        return []


# ---------------------------------------------------------------------------
# Prior phase output injection
# ---------------------------------------------------------------------------

_MAX_FINDINGS_PER_PHASE = 10


def build_prior_phase_section(
    completed_outputs: list[WorkflowPhaseOutput],
) -> str:
    """Build ``## Prior Phase Results`` section from completed phase outputs.

    Injects summary paragraph + structured findings (capped at 10 per phase)
    into the system prompt.  Returns empty string if no outputs.

    Parameters
    ----------
    completed_outputs:
        List of WorkflowPhaseOutput records from direct dependency phases.
    """
    if not completed_outputs:
        return ""

    lines: list[str] = ["---", "## Prior Phase Results", ""]

    for output in completed_outputs:
        lines.append(f"### Phase: {output.phase_id}")
        lines.append(f"**Summary:** {output.summary}")

        # Structured findings from content JSON
        content = output.content or {}
        findings = content.get("findings", [])
        if findings:
            lines.append("")
            lines.append("**Key Findings:**")
            for f in findings[:_MAX_FINDINGS_PER_PHASE]:
                sev = f.get("severity", "")
                desc = f.get("description", "")
                rec = f.get("recommendation", "")
                lines.append(f"- [{sev}] {desc} -- Recommendation: {rec}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# WorkflowExecutor
# ---------------------------------------------------------------------------


class WorkflowExecutor:
    """DAG-based workflow execution engine.

    Coordinates multi-agent execution by:

    1. Starting the session and loading client memory context
    2. Walking DAG waves via topological sort
    3. Calling Agent SDK ``query()`` directly per phase
    4. Injecting prior phase outputs into system prompts
    5. Retrying required phases once on failure
    6. Skipping optional phase failures and their dependents
    7. Storing phase outputs as WorkflowPhaseOutput records
    8. Emitting SSE events at all phase/workflow boundaries
    9. Rendering delivery phase HTML via Jinja2 pipeline

    Parameters
    ----------
    workflow:
        Validated WorkflowSchema from YAML parsing.
    session:
        WorkflowSession managing the run lifecycle.
    registry:
        ToolRegistry with MCP server config and tool definitions.
    """

    def __init__(
        self,
        workflow: WorkflowSchema,
        session: WorkflowSession,
        registry: ToolRegistry,
    ) -> None:
        self._workflow = workflow
        self._session = session
        self._registry = registry
        self._phase_map: dict[str, WorkflowPhaseSchema] = {
            p.id: p for p in workflow.phases
        }
        self._completed_phases: set[str] = set()
        self._skipped_phases: set[str] = set()
        self._phase_outputs: dict[str, WorkflowPhaseOutput] = {}
        self._output_collector = OutputCollector()

    # ── Main execution loop ──────────────────────────────────────────

    async def run(self) -> WorkflowRun:
        """Execute the workflow: start session, walk DAG, emit events, end session.

        Returns
        -------
        WorkflowRun
            The final workflow run record.
        """
        workflow_run = self._session.workflow_run

        # 1. Start session
        await sync_to_async(self._session.start)()

        # 2. Emit workflow_started SSE event
        await self._emit_event(
            "workflow_started",
            {"run_id": str(workflow_run.pk), "event": "workflow_started", "status": "running"},
        )

        # 3. Initialize Langfuse trace (non-fatal)
        try:
            await sync_to_async(start_workflow_trace)(workflow_run)
        except Exception:
            logger.warning("Langfuse trace init failed (non-fatal)", exc_info=True)

        # 4. Load client memory context once (non-fatal)
        try:
            await sync_to_async(self._session.load_client_context)()
        except Exception:
            logger.warning("Client context load failed (non-fatal)", exc_info=True)

        # 5. Walk DAG waves
        waves = get_execution_order(self._workflow)

        try:
            for wave in waves:
                # Filter to known phases, skip phases in _skipped_phases
                wave_phases: list[WorkflowPhaseSchema] = []
                for pid in wave:
                    if pid not in self._phase_map:
                        continue
                    if pid in self._skipped_phases:
                        continue
                    phase = self._phase_map[pid]
                    # Skip phases whose depends_on includes any skipped phase (Pitfall 6)
                    if any(dep in self._skipped_phases for dep in phase.depends_on):
                        self._skipped_phases.add(pid)
                        logger.info(
                            "Skipping phase %s: depends on skipped phase(s) %s",
                            pid,
                            [d for d in phase.depends_on if d in self._skipped_phases],
                        )
                        continue
                    wave_phases.append(phase)

                if not wave_phases:
                    continue

                # Execute all phases in this wave in parallel
                results = await asyncio.gather(
                    *(self._execute_with_retry(phase) for phase in wave_phases),
                    return_exceptions=True,
                )

                # Process results
                for phase, result in zip(wave_phases, results):
                    if isinstance(result, Exception):
                        if phase.required:
                            error_msg = str(result)[:500]
                            await sync_to_async(self._session.fail)(error_msg)
                            await self._emit_event(
                                "workflow_failed",
                                {
                                    "run_id": str(workflow_run.pk),
                                    "event": "workflow_failed",
                                    "status": "failed",
                                    "error": error_msg,
                                },
                            )
                            return workflow_run
                        else:
                            # Optional phase failure -- track as skipped
                            self._skipped_phases.add(phase.id)
                            logger.warning(
                                "Optional phase %s failed (skipped): %s",
                                phase.id,
                                result,
                            )
                    else:
                        self._completed_phases.add(phase.id)

                # Checkpoint after each wave
                last_phase_id = wave_phases[-1].id if wave_phases else None
                await sync_to_async(self._session.checkpoint)(phase_id=last_phase_id)

        except Exception as exc:
            error_msg = str(exc)[:500]
            await sync_to_async(self._session.fail)(error_msg)
            await self._emit_event(
                "workflow_failed",
                {
                    "run_id": str(workflow_run.pk),
                    "event": "workflow_failed",
                    "status": "failed",
                    "error": error_msg,
                },
            )
            return workflow_run

        # 6. End session
        await sync_to_async(self._session.end)()

        # 7. Emit workflow_completed SSE event
        await self._emit_event(
            "workflow_completed",
            {"run_id": str(workflow_run.pk), "event": "workflow_completed", "status": "completed"},
        )

        return workflow_run

    # ── Retry wrapper ────────────────────────────────────────────────

    async def _execute_with_retry(self, phase: WorkflowPhaseSchema) -> dict | None:
        """Execute a phase with retry-once logic for required phases.

        Per user decision: required phase failure retries once with fresh
        agent context, then halts. Optional phases do not retry.
        """
        try:
            return await self._execute_phase(phase)
        except Exception as first_error:
            if not phase.required:
                raise  # Optional phases don't retry
            logger.warning(
                "Required phase %s failed, retrying once: %s",
                phase.id,
                first_error,
            )
            try:
                return await self._execute_phase(phase)
            except Exception as retry_error:
                raise RuntimeError(
                    f"Required phase {phase.id} failed after retry: {retry_error}"
                ) from retry_error

    # ── Phase execution ──────────────────────────────────────────────

    async def _execute_phase(self, phase: WorkflowPhaseSchema) -> dict | None:
        """Execute a single workflow phase via direct Agent SDK query() call.

        1. Skip if no agent (informational phase)
        2. Emit phase_started SSE event
        3. Start Langfuse phase span (non-fatal)
        4. Assemble system prompt with client context and prior phase results
        5. Call Agent SDK query() with MCP server config
        6. Record metering data
        7. Collect artifacts via OutputCollector
        8. Handle delivery phase HTML rendering
        9. Store phase output as WorkflowPhaseOutput record
        10. Emit phase_completed SSE event
        """
        if not phase.agent:
            logger.info("Skipping informational phase: %s", phase.id)
            return None

        workflow_run = self._session.workflow_run
        l3_client_id = str(workflow_run.end_client_id)

        try:
            # Emit phase_started SSE event
            await self._emit_event(
                "phase_started",
                {
                    "run_id": str(workflow_run.pk),
                    "phase_id": phase.id,
                    "phase_name": phase.name,
                    "event": "phase_started",
                    "status": "running",
                },
            )

            # Start Langfuse phase span (non-fatal)
            try:
                wf_trace_id = getattr(workflow_run, "langfuse_trace_id", None)
                if wf_trace_id:
                    await sync_to_async(start_phase_span)(wf_trace_id, phase.id)
            except Exception:
                logger.debug("Langfuse phase span failed (non-fatal): %s", phase.id)

            # Assemble system prompt
            system_prompt = assemble_prompt(
                agent_type=phase.agent,
                skills=phase.skills,
                client_context={
                    "agency_id": str(workflow_run.agency_id),
                    "client_id": l3_client_id,
                },
            )

            # Append client memory context from session
            client_context = self._session.get_client_context()
            if client_context:
                system_prompt += f"\n\n## Client Context\n{client_context}"

            # Build prior phase section (direct dependencies only)
            dep_outputs = [
                self._phase_outputs[dep_id]
                for dep_id in phase.depends_on
                if dep_id in self._phase_outputs
            ]
            prior_section = build_prior_phase_section(dep_outputs)
            if prior_section:
                system_prompt += f"\n\n{prior_section}"

            # Build initial prompt
            initial_prompt = f"Execute the {phase.name} phase for client {l3_client_id}"

            # Get registry -- use constructor-injected registry, fallback to singleton
            registry = self._registry
            if registry is None:
                from hazn_platform.orchestrator import apps as apps_module
                from hazn_platform.orchestrator.tools import build_registry
                registry = apps_module._REGISTRY_SINGLETON or build_registry()

            # Call Agent SDK query() directly
            options = ClaudeAgentOptions(
                system_prompt=system_prompt,
                mcp_servers={"hazn": registry.get_server()},
                allowed_tools=registry.get_allowed_tools(phase.tools),
                max_turns=phase.max_turns,
                permission_mode="bypassPermissions",
            )

            final_text = ""
            usage_data: dict = {}

            async for message in query(prompt=initial_prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            final_text = block.text
                elif isinstance(message, ResultMessage):
                    if message.result:
                        final_text = message.result
                    usage_data = {
                        "input_tokens": (message.usage or {}).get("input_tokens", 0),
                        "output_tokens": (message.usage or {}).get("output_tokens", 0),
                        "total_cost": message.total_cost_usd or 0.0,
                        "num_turns": message.num_turns,
                        "duration_ms": message.duration_ms,
                    }
                    if message.is_error:
                        raise RuntimeError(
                            f"Agent execution failed: {message.result or 'unknown error'}"
                        )

            # Record metering
            total_tokens = usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0)
            total_cost = usage_data.get("total_cost", 0.0)
            self._session.metering.on_llm_call(
                agent_id=phase.agent,
                tokens=total_tokens,
                cost=total_cost,
            )

            # Collect artifacts via OutputCollector
            artifacts = self._output_collector.collect(final_text)

            # Build output dict
            output: dict = {
                "phase_id": phase.id,
                "status": "completed",
                "outputs": phase.outputs,
                "final_text": final_text,
                "usage": usage_data,
            }

            # Extract findings from artifacts for content storage
            findings_list: list[dict] = []
            for artifact in artifacts:
                if hasattr(artifact, "structured_data") and "findings" in (artifact.structured_data or {}):
                    findings_list = artifact.structured_data["findings"]
                    break

            output["findings"] = findings_list

            # Handle delivery phases: render HTML via Jinja2 pipeline
            html_content = ""
            markdown_source = final_text or ""

            if "branded_html_report" in phase.outputs and final_text:
                try:
                    from pydantic import ValidationError

                    agent_output = json.loads(final_text)
                    payload = AuditReportPayload(**agent_output)
                    html_content = render_report("analytics-audit.html", payload)
                except (json.JSONDecodeError, ValidationError) as exc:
                    logger.warning(
                        "Delivery phase output failed validation: %s",
                        str(exc)[:200],
                    )
                except Exception as exc:
                    logger.warning(
                        "Delivery phase rendering failed: %s",
                        str(exc)[:200],
                    )

            # Build summary text
            summary_text = f"Phase {phase.id} completed by agent {phase.agent}"

            # Store phase output as WorkflowPhaseOutput record
            phase_output = await sync_to_async(WorkflowPhaseOutput.objects.create)(
                workflow_run=workflow_run,
                phase_id=phase.id,
                output_type=phase.outputs[0] if phase.outputs else "general",
                content={"findings": findings_list, "artifacts": [a.model_dump() for a in artifacts]},
                summary=summary_text,
                html_content=html_content,
                markdown_source=markdown_source,
            )

            # Cache the WorkflowPhaseOutput for prior phase injection
            self._phase_outputs[phase.id] = phase_output

            # Auto-extract learnings from phase output (non-fatal)
            if final_text and self._session._memory is not None:
                auto_learnings = _auto_extract_learnings(
                    phase_output_text=final_text,
                    client_id=workflow_run.end_client_id,
                    agent_type=phase.id,
                )
                for learning in auto_learnings:
                    self._session._memory.add_learning(learning)

            # Emit phase_completed SSE event
            await self._emit_event(
                "phase_completed",
                {
                    "run_id": str(workflow_run.pk),
                    "phase_id": phase.id,
                    "phase_name": phase.name,
                    "event": "phase_completed",
                    "status": "completed",
                    "summary": summary_text,
                },
            )

            logger.info(
                "Phase %s completed: agent=%s tools=%s tokens=%d cost=$%.4f",
                phase.id,
                phase.agent,
                phase.tools,
                total_tokens,
                total_cost,
            )
            return output

        except Exception as exc:
            # Emit phase_failed SSE event (non-fatal)
            try:
                await self._emit_event(
                    "phase_failed",
                    {
                        "run_id": str(workflow_run.pk),
                        "phase_id": phase.id,
                        "phase_name": phase.name,
                        "event": "phase_failed",
                        "status": "failed",
                        "error": str(exc)[:500],
                    },
                )
            except Exception:
                logger.warning(
                    "Failed to send phase_failed SSE event for %s",
                    phase.id,
                    exc_info=True,
                )
            raise

    # ── SSE helper ───────────────────────────────────────────────────

    async def _emit_event(self, event_name: str, data: dict) -> None:
        """Emit an SSE event to the agency channel (non-fatal).

        Parameters
        ----------
        event_name:
            Event name (for logging).
        data:
            Event payload dict.
        """
        try:
            agency_id = str(self._session.workflow_run.agency_id)
            await sync_to_async(send_workspace_event)(
                agency_id=agency_id,
                event_type="workflow_status",
                data=data,
            )
        except Exception:
            logger.warning(
                "SSE event emission failed for %s (non-fatal)",
                event_name,
                exc_info=True,
            )

    # ── Run status helper ────────────────────────────────────────────

    def _set_run_status(self, status: str) -> None:
        """Update workflow run status and persist to database."""
        self._session.workflow_run.status = status
        self._session.workflow_run.save(update_fields=["status"])

    # ── Agent pause mechanism ────────────────────────────────────────

    async def _await_user_input(
        self, question: str, phase_id: str, timeout_seconds: int = 300
    ) -> str | None:
        """Post a question to chat thread and wait for user reply.

        Creates an agent ChatMessage with metadata.awaiting_reply=true,
        sets the run status to waiting_for_input, then polls for a user
        ChatMessage created after the question. Returns the user's reply
        content or None on timeout.
        """
        # Post the question
        question_msg = await sync_to_async(ChatMessage.objects.create)(
            workflow_run=self._session.workflow_run,
            role="agent",
            content=question,
            metadata={"phase_id": phase_id, "awaiting_reply": True},
        )

        # Update run status
        await sync_to_async(self._set_run_status)("waiting_for_input")

        # Emit SSE
        await self._emit_event(
            "chat_message",
            {
                "run_id": str(self._session.workflow_run.pk),
                "message_id": str(question_msg.pk),
            },
        )

        # Poll for reply
        start = time.monotonic()
        while time.monotonic() - start < timeout_seconds:
            await asyncio.sleep(3)  # Poll every 3 seconds
            reply = await sync_to_async(
                lambda: ChatMessage.objects.filter(
                    workflow_run=self._session.workflow_run,
                    role="user",
                    created_at__gt=question_msg.created_at,
                ).first()
            )()
            if reply:
                await sync_to_async(self._set_run_status)("running")
                return reply.content

        # Timeout
        await sync_to_async(self._set_run_status)("running")
        return None

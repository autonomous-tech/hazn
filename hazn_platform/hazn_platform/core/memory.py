"""HaznMemory -- swap-safe abstraction over Letta memory operations.

This is the **only** module that imports from ``letta_client`` (via
``get_letta_client``).  If Letta is ever swapped for another memory
backend, only this file changes.

Public API
----------
* ``load_client_context()``           -- MEM-02/03: inject L2+L3 context
* ``search_memory(query, limit)``     -- MEM-08: semantic search over archival
* ``search_cross_client_insights()``  -- cross-client Postgres queries
* ``correct_memory(...)``             -- MEM-09: soft-delete + replacement + audit
* ``add_learning(learning)``          -- buffer a craft learning for later flush
* ``checkpoint_sync()``               -- MEM-04: flush pending learnings to archival
* ``failure_sync()``                  -- MEM-05: emergency flush with partial_sync tag
* ``write_finding(finding)``          -- MEM-06: write single finding to Postgres with provenance
* ``end_session(findings)``           -- MEM-06/07: findings + flush + context wipe
"""

from __future__ import annotations

import json
import logging
import math
import re
import uuid
from datetime import datetime, timezone

from hazn_platform.core.letta_client import get_letta_client
from hazn_platform.core.memory_types import CraftLearning, StructuredFinding

logger = logging.getLogger(__name__)

# ── Regex patterns for metadata tag extraction ───────────────────────

_TIMESTAMP_RE = re.compile(r"\[timestamp:([^\]]+)\]")
_CONFIDENCE_RE = re.compile(r"\[confidence:([^\]]+)\]")
_STATUS_RE = re.compile(r"\[status:([^\]]+)\]")

# ── Ranking weights (per user decision) ──────────────────────────────
# Composite: similarity_rank * 0.6 + recency_score * 0.25 + confidence * 0.15
_W_SIMILARITY = 0.6
_W_RECENCY = 0.25
_W_CONFIDENCE = 0.15


def _recency_score(timestamp_str: str) -> float:
    """Compute a recency score from an ISO timestamp string.

    Returns a value between 0.1 (>30 days old) and 1.0 (<1 day old),
    decaying exponentially.
    """
    try:
        ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - ts).total_seconds() / 86400
        if age_days < 1:
            return 1.0
        # Exponential decay: e^(-0.05 * age_days), clamped to [0.1, 1.0]
        return max(0.1, math.exp(-0.05 * age_days))
    except (ValueError, TypeError):
        return 0.1


class HaznMemory:
    """Swap-safe abstraction over Letta memory operations.

    One instance per agent session.  Manages:
    - Core memory block injection (active_client_context)
    - Archival memory (craft learnings with metadata tags)
    - Semantic search with composite ranking
    - Cross-client insight queries from Postgres
    - Memory correction with full audit trail

    Parameters
    ----------
    agent_id : str
        Letta agent ID.
    l3_client_id : uuid.UUID
        EndClient (L3) primary key.
    l2_agency_id : uuid.UUID
        Agency (L2) primary key.
    """

    def __init__(
        self,
        agent_id: str,
        l3_client_id: uuid.UUID,
        l2_agency_id: uuid.UUID,
    ) -> None:
        self._client = get_letta_client()
        self._agent_id = agent_id
        self._l3_client_id = l3_client_id
        self._l2_agency_id = l2_agency_id
        self._turn_counter: int = 0
        self._pending_learnings: list[CraftLearning] = []

    # ── Context Loading (MEM-02 / MEM-03) ────────────────────────────

    def load_client_context(self) -> None:
        """Assemble L2+L3 context from Django ORM and write to Letta block.

        Checks ``Agency.tool_preferences["context_loading_policy"]``.
        v1 only implements ``"full"`` mode; unrecognised policies log a
        warning and proceed with full mode.
        """
        from hazn_platform.core.models import Agency

        agency = Agency.objects.get(id=self._l2_agency_id)
        policy = agency.tool_preferences.get("context_loading_policy", "full")

        if policy != "full":
            logger.warning(
                "Unrecognised context_loading_policy '%s' for agency %s; "
                "falling back to 'full' (v1 default)",
                policy,
                agency.slug,
            )

        context_json = self._assemble_context()
        self._client.agents.blocks.update(
            "active_client_context",
            agent_id=self._agent_id,
            value=context_json,
        )
        logger.info(
            "Loaded client context for agent=%s client=%s (%d bytes)",
            self._agent_id,
            self._l3_client_id,
            len(context_json),
        )

    def _assemble_context(self) -> str:
        """Query Django ORM and return a JSON summary (~2-4 KB)."""
        from hazn_platform.content.models import BrandVoice
        from hazn_platform.core.models import Agency, EndClient
        from hazn_platform.marketing.models import Campaign, Keyword

        agency = Agency.objects.get(id=self._l2_agency_id)
        client = EndClient.objects.get(id=self._l3_client_id)

        brand_voice = BrandVoice.objects.filter(
            end_client=client, is_active=True
        ).first()

        recent_keywords = Keyword.objects.filter(
            end_client=client
        ).order_by("-updated_at")[:20]

        active_campaigns = Campaign.objects.filter(
            end_client=client, status="active"
        )

        context = {
            "agency": {
                "name": agency.name,
                "house_style": agency.house_style,
                "methodology": agency.methodology,
            },
            "client": {
                "name": client.name,
                "competitors": client.competitors,
            },
            "brand_voice": brand_voice.content if brand_voice else None,
            "active_campaigns": [
                {"name": c.name, "type": c.campaign_type}
                for c in active_campaigns
            ],
            "top_keywords": [
                {"term": k.term, "status": k.status}
                for k in recent_keywords
            ],
        }
        return json.dumps(context, indent=2)

    # ── Memory Search (MEM-08) ───────────────────────────────────────

    def search_memory(self, query: str, limit: int = 5) -> list[dict]:
        """Search archival memory with composite ranking.

        Steps:
        1. Call Letta ``passages.search()``
        2. Filter out entries with ``[status:corrected]`` or ``[status:superseded]``
        3. Re-rank by composite score:
           * Similarity rank (from Letta return order) -- weight 0.6
           * Recency (from ``[timestamp:ISO]`` tag) -- weight 0.25
           * Confidence (from ``[confidence:X]`` tag) -- weight 0.15
        4. Return top ``limit`` results.
        """
        search_response = self._client.agents.passages.search(
            agent_id=self._agent_id,
            query=query,
        )

        # Filter to active-only results
        active_results = []
        for item in search_response:
            text = item.passage.text
            status_match = _STATUS_RE.search(text)
            status = status_match.group(1) if status_match else ""
            if status in ("corrected", "superseded"):
                continue
            active_results.append(item)

        # Compute composite scores
        scored: list[tuple[float, dict]] = []
        for item in active_results:
            text = item.passage.text

            # Similarity score: SDK-provided score from Letta
            letta_similarity = item.score

            # Recency score from timestamp tag
            ts_match = _TIMESTAMP_RE.search(text)
            recency = _recency_score(ts_match.group(1)) if ts_match else 0.1

            # Confidence from tag
            conf_match = _CONFIDENCE_RE.search(text)
            confidence = float(conf_match.group(1)) if conf_match else 0.5

            composite = (
                _W_SIMILARITY * letta_similarity
                + _W_RECENCY * recency
                + _W_CONFIDENCE * confidence
            )

            scored.append((
                composite,
                {
                    "id": item.passage.id,
                    "content": text,
                    "score": round(composite, 4),
                },
            ))

        # Sort descending by composite score
        scored.sort(key=lambda t: t[0], reverse=True)
        return [item for _, item in scored[:limit]]

    # ── Cross-Client Insights ────────────────────────────────────────

    def search_cross_client_insights(
        self,
        query: str,
        finding_types: list[str] | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Query Postgres structured findings from sibling L3 clients.

        Returns empty list if ``Agency.tool_preferences["cross_client_insights"]``
        is not ``True``.  Queries Keyword, Audit, Campaign, and Decision
        tables for all sibling EndClients under the same Agency, excluding
        the current ``l3_client_id``.
        """
        from hazn_platform.core.models import Agency, EndClient

        agency = Agency.objects.get(id=self._l2_agency_id)
        if not agency.tool_preferences.get("cross_client_insights", False):
            return []

        sibling_ids = list(
            EndClient.objects.filter(agency_id=self._l2_agency_id)
            .exclude(id=self._l3_client_id)
            .values_list("id", flat=True)
        )
        if not sibling_ids:
            return []

        # Build a client name lookup for provenance
        siblings = {
            str(c.id): c.name
            for c in EndClient.objects.filter(id__in=sibling_ids)
        }

        results: list[dict] = []
        type_set = set(finding_types) if finding_types else None

        # Query each finding type
        if type_set is None or "keyword" in type_set:
            results.extend(self._query_sibling_keywords(sibling_ids, siblings))

        if type_set is None or "audit" in type_set:
            results.extend(self._query_sibling_audits(sibling_ids, siblings))

        if type_set is None or "campaign" in type_set:
            results.extend(self._query_sibling_campaigns(sibling_ids, siblings))

        if type_set is None or "decision" in type_set:
            results.extend(self._query_sibling_decisions(sibling_ids, siblings))

        return results[:limit]

    @staticmethod
    def _query_sibling_keywords(
        sibling_ids: list[uuid.UUID],
        siblings: dict[str, str],
    ) -> list[dict]:
        from hazn_platform.marketing.models import Keyword

        return [
            {
                "finding_type": "keyword",
                "data": {
                    "term": k.term,
                    "search_volume": k.search_volume,
                    "difficulty": k.difficulty,
                    "intent": k.intent,
                    "status": k.status,
                },
                "source_client": siblings.get(str(k.end_client_id), "unknown"),
            }
            for k in Keyword.objects.filter(end_client_id__in=sibling_ids)
        ]

    @staticmethod
    def _query_sibling_audits(
        sibling_ids: list[uuid.UUID],
        siblings: dict[str, str],
    ) -> list[dict]:
        from hazn_platform.marketing.models import Audit

        return [
            {
                "finding_type": "audit",
                "data": {
                    "audit_type": a.audit_type,
                    "findings": a.findings,
                    "score": a.score,
                },
                "source_client": siblings.get(str(a.end_client_id), "unknown"),
            }
            for a in Audit.objects.filter(end_client_id__in=sibling_ids)
        ]

    @staticmethod
    def _query_sibling_campaigns(
        sibling_ids: list[uuid.UUID],
        siblings: dict[str, str],
    ) -> list[dict]:
        from hazn_platform.marketing.models import Campaign

        return [
            {
                "finding_type": "campaign",
                "data": {
                    "name": c.name,
                    "campaign_type": c.campaign_type,
                    "status": c.status,
                    "config": c.config,
                },
                "source_client": siblings.get(str(c.end_client_id), "unknown"),
            }
            for c in Campaign.objects.filter(end_client_id__in=sibling_ids)
        ]

    @staticmethod
    def _query_sibling_decisions(
        sibling_ids: list[uuid.UUID],
        siblings: dict[str, str],
    ) -> list[dict]:
        from hazn_platform.marketing.models import Decision

        return [
            {
                "finding_type": "decision",
                "data": {
                    "decision_type": d.decision_type,
                    "rationale": d.rationale,
                    "outcome": d.outcome,
                },
                "source_client": siblings.get(str(d.end_client_id), "unknown"),
            }
            for d in Decision.objects.filter(end_client_id__in=sibling_ids)
        ]

    # ── Memory Correction (MEM-09) ───────────────────────────────────

    def correct_memory(
        self,
        passage_id: str,
        new_content: str,
        reason: str,
        corrected_by: str,
    ) -> str | None:
        """Soft-delete original passage, create replacement, write audit record.

        1. Retrieve original passage text via ``passages.list()``
        2. Delete the original passage
        3. Create a corrected-marker passage (original text with ``[status:corrected]``)
        4. Create a replacement passage with new_content
        5. Write ``MemoryCorrection`` audit record to Postgres

        Returns the replacement passage ID, or None if only deleting.
        """
        from hazn_platform.core.models import MemoryCorrection

        # 1. Read original passage
        all_passages = self._client.agents.passages.list(agent_id=self._agent_id)
        original_text = ""
        for p in all_passages:
            if p.id == passage_id:
                original_text = p.text
                break

        # 2. Delete the original passage
        self._client.agents.passages.delete(
            passage_id, agent_id=self._agent_id
        )

        # 3. Create corrected marker (preserves audit trail in Letta)
        corrected_text = original_text.replace(
            "[status:active]", "[status:corrected]"
        )
        self._client.agents.passages.create(
            agent_id=self._agent_id,
            text=corrected_text,
        )

        # 4. Create replacement passage
        replacement_id = None
        if new_content:
            # Rebuild metadata prefix from original, swapping content
            replacement_text = self._build_replacement_text(
                original_text, new_content
            )
            result = self._client.agents.passages.create(
                agent_id=self._agent_id,
                text=replacement_text,
            )
            replacement_id = result[0].id if result else None

        # 5. Write audit record
        MemoryCorrection.objects.create(
            agent_id=self._agent_id,
            original_passage_id=passage_id,
            replacement_passage_id=replacement_id,
            original_content=original_text,
            corrected_content=new_content,
            reason=reason,
            corrected_by=corrected_by,
            end_client_id=self._l3_client_id,
        )

        logger.info(
            "Memory corrected: agent=%s passage=%s -> %s by=%s reason=%s",
            self._agent_id,
            passage_id,
            replacement_id,
            corrected_by,
            reason[:50],
        )
        return replacement_id

    @staticmethod
    def _build_replacement_text(original_text: str, new_content: str) -> str:
        """Rebuild passage text with original metadata prefix but new content."""
        # Split on the first newline after metadata prefix
        # Metadata prefix is everything up to and including [status:active]
        # then a newline, then the actual content
        parts = original_text.split("\n", 1)
        if len(parts) == 2 and "[" in parts[0]:
            # Reuse metadata prefix, update timestamp, keep status active
            prefix = parts[0]
            # Update timestamp
            now_iso = datetime.now(timezone.utc).isoformat()
            prefix = _TIMESTAMP_RE.sub(f"[timestamp:{now_iso}]", prefix)
            # Ensure status is active
            prefix = prefix.replace("[status:corrected]", "[status:active]")
            prefix = prefix.replace("[status:superseded]", "[status:active]")
            return f"{prefix}\n{new_content}"
        # Fallback: just return the new content with active status
        return f"[status:active]\n{new_content}"

    # ── Learning Buffering ───────────────────────────────────────────

    def add_learning(self, learning: CraftLearning) -> None:
        """Buffer a craft learning for later checkpoint flush.

        Learnings accumulate in ``_pending_learnings`` and are flushed
        to Letta archival by ``checkpoint_sync()``.
        """
        self._pending_learnings.append(learning)
        logger.debug(
            "Buffered learning (source=%s, confidence=%.2f); %d pending",
            learning.source,
            learning.confidence,
            len(self._pending_learnings),
        )

    # ── Session Lifecycle (MEM-04 / MEM-05 / MEM-06 / MEM-07) ──────

    def checkpoint_sync(self) -> None:
        """Flush all pending learnings to Letta archival memory.

        No-op if there are no pending learnings.  After flush the buffer
        is cleared.  Called explicitly by the executor or session lifecycle.
        """
        if not self._pending_learnings:
            return
        for learning in self._pending_learnings:
            self._write_craft_learning(learning)
        count = len(self._pending_learnings)
        self._pending_learnings.clear()
        logger.info(
            "Checkpoint sync: flushed %d learnings for agent=%s",
            count,
            self._agent_id,
        )

    def failure_sync(self) -> None:
        """Emergency flush of pending learnings with reduced confidence.

        Called on unclean session exit (crash, timeout, API error).
        Never discards work: every pending learning is written with
        ``partial_sync`` tag and confidence reduced to
        ``min(original * 0.7, 0.7)``.
        """
        for learning in self._pending_learnings:
            modified = learning.model_copy(
                update={
                    "confidence": min(learning.confidence * 0.7, 0.7),
                    "tags": list(learning.tags or []) + ["partial_sync"],
                }
            )
            self._write_craft_learning(modified)
        count = len(self._pending_learnings)
        self._pending_learnings.clear()
        if count:
            logger.warning(
                "Failure sync: flushed %d learnings with partial_sync tag "
                "for agent=%s",
                count,
                self._agent_id,
            )

    def end_session(self, findings: list[StructuredFinding]) -> None:
        """Clean session termination: findings to Postgres, learnings to archival, context wipe.

        1. Write each StructuredFinding to the appropriate Postgres table
           via ``write_finding()``.
        2. Flush any remaining ``_pending_learnings`` to Letta archival
           via ``checkpoint_sync()``.
        3. Wipe the ``active_client_context`` Letta block (MEM-07).

        After this call, the instance should not be reused.
        """
        # 1. Write structured findings to Postgres
        for finding in findings:
            self.write_finding(finding)

        # 2. Flush remaining craft learnings
        self.checkpoint_sync()

        # 3. Wipe active_client_context block
        self._client.agents.blocks.update(
            "active_client_context",
            agent_id=self._agent_id,
            value="",
        )
        logger.info(
            "Session ended for agent=%s client=%s: "
            "%d findings written, context wiped",
            self._agent_id,
            self._l3_client_id,
            len(findings),
        )

    def write_finding(self, finding: StructuredFinding) -> None:
        """Write a single StructuredFinding to the correct Postgres table.

        Dispatches based on ``finding.finding_type`` to the matching
        Django model.  Provenance data (workflow_run_id, agent_type,
        session_timestamp) is stored in the model's existing JSONField.

        Does NOT flush learnings or wipe context.  This is a standalone
        write for use by the MCP server during a session.
        """
        # Dispatcher: finding_type -> (Model class import path, json_field_name)
        _FINDING_DISPATCH: dict[str, tuple[str, str, str]] = {
            "keyword": ("hazn_platform.marketing.models", "Keyword", "metadata"),
            "audit": ("hazn_platform.marketing.models", "Audit", "findings"),
            "campaign": ("hazn_platform.marketing.models", "Campaign", "config"),
            "decision": ("hazn_platform.marketing.models", "Decision", "outcome"),
        }

        dispatch = _FINDING_DISPATCH.get(finding.finding_type)
        if dispatch is None:
            logger.warning(
                "Unknown finding_type '%s'; skipping write for agent=%s",
                finding.finding_type,
                self._agent_id,
            )
            return

        import importlib

        module_path, class_name, json_field = dispatch
        mod = importlib.import_module(module_path)
        model_cls = getattr(mod, class_name)

        provenance = {
            "_provenance": {
                "workflow_run_id": str(finding.workflow_run_id) if finding.workflow_run_id else None,
                "agent_type": finding.agent_type,
                "session_timestamp": finding.session_timestamp.isoformat(),
            }
        }

        # Build create kwargs from finding.data plus provenance in JSONField
        create_kwargs = {**finding.data}
        create_kwargs["end_client_id"] = self._l3_client_id

        # Merge provenance into the target JSONField value
        existing_json = create_kwargs.pop(json_field, {})
        if not isinstance(existing_json, dict):
            existing_json = {}
        existing_json.update(provenance)
        create_kwargs[json_field] = existing_json

        model_cls.objects.create(**create_kwargs)
        logger.info(
            "Wrote finding type=%s to %s for agent=%s client=%s",
            finding.finding_type,
            class_name,
            self._agent_id,
            self._l3_client_id,
        )

    def _write_craft_learning(self, learning: CraftLearning) -> str:
        """Write a single craft learning to Letta archival with metadata tags.

        Metadata prefix format::

            [source:agent-inferred][confidence:0.85][agent:seo]
            [client:uuid][timestamp:ISO][status:active]
            Actual learning content

        Returns the passage ID.
        """
        now_iso = learning.created_at.isoformat()
        metadata_prefix = (
            f"[source:{learning.source.value}]"
            f"[confidence:{learning.confidence}]"
            f"[agent:{learning.agent_type}]"
            f"[client:{learning.l3_client_id}]"
            f"[timestamp:{now_iso}]"
            f"[status:active]"
        )
        if learning.supersedes_id:
            metadata_prefix += f"[supersedes:{learning.supersedes_id}]"

        full_text = f"{metadata_prefix}\n{learning.content}"

        result = self._client.agents.passages.create(
            agent_id=self._agent_id,
            text=full_text,
        )
        passage_id = result[0].id if result else ""
        logger.info(
            "Wrote craft learning passage=%s source=%s confidence=%.2f",
            passage_id,
            learning.source,
            learning.confidence,
        )
        return passage_id

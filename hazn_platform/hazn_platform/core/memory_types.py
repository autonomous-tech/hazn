"""Pydantic data models for the HaznMemory type system.

Defines the data contracts for craft learnings (Letta archival), structured
findings (Postgres), and client context assembly.

Exports:
    LearningSource  -- StrEnum for learning provenance
    CraftLearning   -- learning stored in Letta archival memory
    StructuredFinding -- finding stored in Postgres domain tables
    ClientContext    -- assembled L2+L3 context snapshot for Letta block
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class LearningSource(str, enum.Enum):
    """Source provenance for craft learnings.

    * agent-inferred: LLM judgment during workflow
    * rule-extracted: pattern-based extraction
    * user-explicit: agency user explicitly said "remember this"
    """

    AGENT_INFERRED = "agent-inferred"
    RULE_EXTRACTED = "rule-extracted"
    USER_EXPLICIT = "user-explicit"


class CraftLearning(BaseModel):
    """A craft learning stored in Letta archival memory.

    Represents *how* to work for a client -- e.g. brand preferences,
    tone rules, past decisions.  Tagged with provenance and confidence
    for search ranking.

    If ``source`` is ``user-explicit`` and ``confidence`` is not
    explicitly provided, it defaults to 1.0 (highest confidence).
    """

    content: str
    source: LearningSource
    confidence: float = Field(default=None, ge=0.0, le=1.0)  # type: ignore[assignment]
    agent_type: str
    l3_client_id: uuid.UUID
    supersedes_id: Optional[str] = None
    tags: Optional[list[str]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="before")
    @classmethod
    def _set_user_explicit_confidence(cls, data: dict) -> dict:
        """Default confidence to 1.0 for user-explicit learnings."""
        if isinstance(data, dict):
            source = data.get("source")
            confidence = data.get("confidence")
            if (
                source in (LearningSource.USER_EXPLICIT, "user-explicit")
                and confidence is None
            ):
                data["confidence"] = 1.0
        return data


class StructuredFinding(BaseModel):
    """A structured finding written to Postgres domain tables.

    Represents *what* was found -- keyword gaps, audit scores,
    campaign results.  Full provenance for audit trail.
    """

    finding_type: str
    data: dict
    workflow_run_id: Optional[uuid.UUID] = None
    agent_type: str
    session_timestamp: datetime


class ClientContext(BaseModel):
    """Assembled L2 (agency) + L3 (end-client) context snapshot.

    Written to the ``active_client_context`` Letta core memory block
    at session start.  Kept to ~2-4 KB for token budget.
    """

    agency: dict
    client: dict
    brand_voice: Optional[str] = None
    active_campaigns: list[dict]
    top_keywords: list[dict]

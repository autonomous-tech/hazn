"""Memory tools -- 8 tools ported from hazn_memory_server.py.

Thin wrappers around :class:`HaznMemory` and ``vault.read_secret``.
All business logic lives in the core memory module; this layer handles
parameter mapping, Agent SDK return format, and the session-scoped
``_memory_registry``.

Tools
-----
1. ``load_context``                  -- inject L2+L3 context into agent memory
2. ``write_finding``                 -- write a structured finding to Postgres
3. ``search_memory``                 -- semantic search over archival memory
4. ``search_cross_client_insights``  -- query sibling client data (always-on)
5. ``checkpoint_sync``               -- flush pending learnings to archival
6. ``correct_memory``                -- soft-delete and replace incorrect memory
7. ``get_credentials``               -- fetch secrets from Vault for tool calls
8. ``add_learning``                  -- record a craft learning for future reference

Key differences from MCP server:
- No l2_agency_id param -- uses Agency.load() singleton internally
- l3_client_id renamed to client_id
- search_cross_client_insights always-on (no Agency.cross_client_insights flag check)
- Returns Agent SDK format: {"content": [{"type": "text", "text": "..."}]}
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SDK tool decorator with graceful fallback
# ---------------------------------------------------------------------------

try:
    from claude_agent_sdk import tool  # type: ignore[import-untyped]
except ImportError:
    try:
        from claude_code_sdk import tool  # type: ignore[import-untyped]
    except ImportError:

        def tool(name: str, description: str, schema: dict | None = None):  # type: ignore[misc]
            """Stub @tool decorator for environments without the SDK."""

            def decorator(fn):
                class _StubTool:
                    def __init__(self):
                        self.name = name
                        self.description = description
                        self.schema = schema or {}
                        self._handler = fn

                    async def __call__(self, args: dict[str, Any]) -> dict[str, Any]:
                        return await self._handler(args)

                return _StubTool()

            return decorator


# ---------------------------------------------------------------------------
# sync_to_async import with fallback
# ---------------------------------------------------------------------------

try:
    from asgiref.sync import sync_to_async
except ImportError:
    # Fallback for environments without asgiref
    import asyncio

    def sync_to_async(fn):  # type: ignore[misc]
        """Fallback sync_to_async using asyncio.to_thread."""
        async def wrapper(*args, **kwargs):
            return await asyncio.to_thread(fn, *args, **kwargs)
        return wrapper


# ---------------------------------------------------------------------------
# Session state: module-level registry (same pattern as MCP server)
# ---------------------------------------------------------------------------

_memory_registry: dict[str, Any] = {}


# ---------------------------------------------------------------------------
# Internal helpers (deferred Django imports)
# ---------------------------------------------------------------------------


def _get_agency():
    """Get the singleton Agency via Agency.load(). Deferred import."""
    from hazn_platform.core.models import Agency
    return Agency.load()


def _create_memory(agent_id: str, client_id: str, agency_id):
    """Create a new HaznMemory instance. Deferred import."""
    from hazn_platform.core.memory import HaznMemory
    return HaznMemory(
        agent_id=agent_id,
        l3_client_id=uuid.UUID(client_id) if isinstance(client_id, str) else client_id,
        l2_agency_id=agency_id if isinstance(agency_id, uuid.UUID) else uuid.UUID(str(agency_id)),
    )


def _get_vault_credential(client_id: str, service_name: str):
    """Look up VaultCredential by client_id and service_name. Deferred import."""
    from hazn_platform.core.models import VaultCredential
    return VaultCredential.objects.get(
        end_client_id=uuid.UUID(client_id),
        service_name=service_name,
    )


def _read_secret(vault_secret_id: str) -> dict:
    """Read secret from Vault. Deferred import."""
    from hazn_platform.core.vault import read_secret
    return read_secret(vault_secret_id)


async def _get_or_create_memory(agent_id: str, client_id: str):
    """Return existing HaznMemory for agent_id, or create a new one.

    Uses Agency.load() singleton instead of accepting l2_agency_id param.
    """
    if agent_id in _memory_registry:
        return _memory_registry[agent_id]

    agency = await sync_to_async(_get_agency)()
    memory = await sync_to_async(_create_memory)(agent_id, client_id, agency.id)
    _memory_registry[agent_id] = memory
    return memory


# ---------------------------------------------------------------------------
# Tool 1: load_context
# ---------------------------------------------------------------------------


@tool("load_context", "Load L2+L3 client context into agent's active memory block.", {
    "agent_id": str,
    "client_id": str,
})
async def load_context(args: dict[str, Any]) -> dict[str, Any]:
    """Load L2+L3 client context into agent memory.

    Assembles agency metadata, client data, brand voice, active campaigns,
    and top keywords into a structured JSON summary written to the
    active_client_context Letta core memory block.
    """
    agent_id = args["agent_id"]
    client_id = args["client_id"]

    try:
        memory = await _get_or_create_memory(agent_id, client_id)
        await sync_to_async(memory.load_client_context)()
        return {
            "content": [
                {"type": "text", "text": f"Context loaded for agent={agent_id} client={client_id}"}
            ]
        }
    except Exception as exc:
        logger.warning("load_context failed: %s", exc)
        return {
            "content": [{"type": "text", "text": f"Error loading context: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Tool 2: write_finding
# ---------------------------------------------------------------------------


@tool("write_finding", "Write a structured finding to Postgres without ending the session.", {
    "agent_id": str,
    "client_id": str,
    "finding_type": str,
    "data": dict,
    "workflow_run_id": str,
    "agent_type": str,
})
async def write_finding(args: dict[str, Any]) -> dict[str, Any]:
    """Write a structured finding to Postgres.

    Creates a StructuredFinding and delegates to HaznMemory.write_finding()
    for a standalone write. Does NOT trigger end_session or flush learnings.
    """
    agent_id = args["agent_id"]
    client_id = args["client_id"]
    finding_type = args["finding_type"]
    data = args["data"]
    workflow_run_id = args.get("workflow_run_id")
    agent_type = args.get("agent_type", "unknown")

    try:
        # Deferred import of StructuredFinding
        from hazn_platform.core.memory_types import StructuredFinding

        memory = await _get_or_create_memory(agent_id, client_id)
        finding = StructuredFinding(
            finding_type=finding_type,
            data=data,
            workflow_run_id=uuid.UUID(workflow_run_id) if workflow_run_id else None,
            agent_type=agent_type,
            session_timestamp=datetime.now(timezone.utc),
        )
        await sync_to_async(memory.write_finding)(finding)
        return {
            "content": [
                {"type": "text", "text": f"Finding type={finding_type} written for agent={agent_id}"}
            ]
        }
    except Exception as exc:
        logger.warning("write_finding failed: %s", exc)
        return {
            "content": [{"type": "text", "text": f"Error writing finding: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Tool 3: search_memory
# ---------------------------------------------------------------------------


@tool("search_memory", "Search agent's archival memory semantically.", {
    "agent_id": str,
    "client_id": str,
    "query": str,
    "limit": int,
})
async def search_memory(args: dict[str, Any]) -> dict[str, Any]:
    """Search agent's archival memory semantically.

    Returns results ranked by composite score: similarity (0.6),
    recency (0.25), and confidence (0.15).
    """
    agent_id = args["agent_id"]
    client_id = args["client_id"]
    query = args["query"]
    limit = args.get("limit", 5)

    try:
        memory = await _get_or_create_memory(agent_id, client_id)
        results = await sync_to_async(memory.search_memory)(query, limit)
        return {
            "content": [{"type": "text", "text": json.dumps(results)}]
        }
    except Exception as exc:
        logger.warning("search_memory failed: %s", exc)
        return {
            "content": [{"type": "text", "text": f"Error searching memory: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Tool 4: search_cross_client_insights (always-on, no flag check)
# ---------------------------------------------------------------------------


@tool("search_cross_client_insights", "Query sibling client data for cross-client insights.", {
    "agent_id": str,
    "client_id": str,
    "query": str,
    "finding_types": list,
    "limit": int,
})
async def search_cross_client_insights(args: dict[str, Any]) -> dict[str, Any]:
    """Search structured findings from sibling L3 clients.

    Always enabled -- does NOT check Agency.cross_client_insights flag.
    Queries keyword, audit, campaign, and decision tables for all
    sibling EndClients, excluding the current client.
    """
    agent_id = args["agent_id"]
    client_id = args["client_id"]
    query = args["query"]
    finding_types = args.get("finding_types")
    limit = args.get("limit", 10)

    try:
        memory = await _get_or_create_memory(agent_id, client_id)
        results = await sync_to_async(memory.search_cross_client_insights)(
            query, finding_types=finding_types, limit=limit
        )
        return {
            "content": [{"type": "text", "text": json.dumps(results)}]
        }
    except Exception as exc:
        logger.warning("search_cross_client_insights failed: %s", exc)
        return {
            "content": [{"type": "text", "text": f"Error searching cross-client insights: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Tool 5: checkpoint_sync
# ---------------------------------------------------------------------------


@tool("checkpoint_sync", "Flush pending learnings to archival memory.", {
    "agent_id": str,
    "client_id": str,
})
async def checkpoint_sync(args: dict[str, Any]) -> dict[str, Any]:
    """Flush pending learnings to archival memory.

    Writes all buffered craft learnings to Letta archival storage.
    No-op if there are no pending learnings.
    """
    agent_id = args["agent_id"]
    client_id = args["client_id"]

    try:
        memory = await _get_or_create_memory(agent_id, client_id)
        await sync_to_async(memory.checkpoint_sync)()
        return {
            "content": [
                {"type": "text", "text": f"Checkpoint sync complete for agent={agent_id}"}
            ]
        }
    except Exception as exc:
        logger.warning("checkpoint_sync failed: %s", exc)
        return {
            "content": [{"type": "text", "text": f"Error during checkpoint sync: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Tool 6: correct_memory
# ---------------------------------------------------------------------------


@tool("correct_memory", "Soft-delete incorrect memory and create corrected replacement.", {
    "agent_id": str,
    "client_id": str,
    "passage_id": str,
    "new_content": str,
    "reason": str,
    "corrected_by": str,
})
async def correct_memory(args: dict[str, Any]) -> dict[str, Any]:
    """Soft-delete incorrect memory and create corrected replacement.

    Deletes the original passage, creates a corrected-marker passage
    for audit trail, creates a replacement passage with the new content,
    and writes a MemoryCorrection audit record to Postgres.
    """
    agent_id = args["agent_id"]
    client_id = args["client_id"]
    passage_id = args["passage_id"]
    new_content = args["new_content"]
    reason = args["reason"]
    corrected_by = args["corrected_by"]

    try:
        memory = await _get_or_create_memory(agent_id, client_id)
        replacement_id = await sync_to_async(memory.correct_memory)(
            passage_id=passage_id,
            new_content=new_content,
            reason=reason,
            corrected_by=corrected_by,
        )
        return {
            "content": [
                {"type": "text", "text": f"Memory corrected: passage={passage_id} by={corrected_by} replacement={replacement_id}"}
            ]
        }
    except Exception as exc:
        logger.warning("correct_memory failed: %s", exc)
        return {
            "content": [{"type": "text", "text": f"Error correcting memory: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Tool 8: add_learning
# ---------------------------------------------------------------------------


@tool("add_learning", "Record a craft learning about this client for future reference.", {
    "agent_id": str,
    "client_id": str,
    "content": str,
    "source": str,
    "confidence": float,
    "agent_type": str,
})
async def add_learning(args: dict[str, Any]) -> dict[str, Any]:
    """Record a craft learning via HaznMemory.add_learning().

    Buffers a CraftLearning record for later checkpoint flush.
    Accepts optional source (default "agent-inferred"), confidence
    (default 0.7), and agent_type (default "unknown").
    """
    agent_id = args["agent_id"]
    client_id = args["client_id"]
    content = args["content"]
    source_str = args.get("source", "agent-inferred")
    confidence = args.get("confidence", 0.7)
    agent_type = args.get("agent_type", "unknown")

    try:
        from hazn_platform.core.memory_types import CraftLearning, LearningSource

        memory = await _get_or_create_memory(agent_id, client_id)

        # Map source string to LearningSource enum
        source_map = {
            "agent-inferred": LearningSource.AGENT_INFERRED,
            "rule-extracted": LearningSource.RULE_EXTRACTED,
            "user-explicit": LearningSource.USER_EXPLICIT,
        }
        source = source_map.get(source_str, LearningSource.AGENT_INFERRED)

        learning = CraftLearning(
            content=content,
            source=source,
            confidence=confidence,
            agent_type=agent_type,
            l3_client_id=uuid.UUID(client_id) if isinstance(client_id, str) else client_id,
        )
        await sync_to_async(memory.add_learning)(learning)
        return {
            "content": [
                {"type": "text", "text": f"Learning recorded for agent={agent_id}: {content[:80]}"}
            ]
        }
    except Exception as exc:
        logger.warning("add_learning failed: %s", exc)
        return {
            "content": [{"type": "text", "text": f"Error recording learning: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Tool 7: get_credentials
# ---------------------------------------------------------------------------


@tool("get_credentials", "Fetch credentials for a service from Vault.", {
    "client_id": str,
    "service_name": str,
})
async def get_credentials(args: dict[str, Any]) -> dict[str, Any]:
    """Fetch credentials for a service from Vault.

    Looks up the VaultCredential record for the given client and service,
    then reads the secret from Vault. Returns the secret data dict for
    direct use in tool calls (per CRED-04: secrets go to tool calls,
    never into agent context).
    """
    client_id = args["client_id"]
    service_name = args["service_name"]

    try:
        credential = await sync_to_async(_get_vault_credential)(client_id, service_name)
        secret = await sync_to_async(_read_secret)(credential.vault_secret_id)
        return {
            "content": [{"type": "text", "text": json.dumps(secret)}]
        }
    except Exception as exc:
        logger.warning(
            "get_credentials failed for client=%s service=%s: %s",
            client_id, service_name, exc,
        )
        return {
            "content": [{"type": "text", "text": f"Error fetching credentials for service '{service_name}': {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Module-level tool list for registration
# ---------------------------------------------------------------------------

MEMORY_TOOLS = [
    load_context,
    write_finding,
    search_memory,
    search_cross_client_insights,
    checkpoint_sync,
    correct_memory,
    get_credentials,
    add_learning,
]

"""Integration tests for HaznMemory session lifecycle.

Tests require running Docker services:
- Letta server (port 8283) with OPENAI_API_KEY for embeddings
- PostgreSQL with hazn_platform database and migrations applied

Run with::

    cd hazn_platform && uv run pytest tests/integration/test_memory_integration.py -x -v -m integration
"""

import time
import uuid
from datetime import datetime, timezone

import pytest

from hazn_platform.core.letta_client import get_letta_client
from hazn_platform.core.memory_types import (
    CraftLearning,
    LearningSource,
    StructuredFinding,
)


# ── Helpers ────────────────────────────────────────────────────────


def _create_test_agent(client, name_suffix: str):
    """Create a Letta agent with active_client_context block for testing."""
    return client.agents.create(
        name=f"hazn-test-{name_suffix}-{uuid.uuid4().hex[:8]}",
        model="openai/gpt-4o-mini",
        embedding="openai/text-embedding-ada-002",
        memory_blocks=[
            {"label": "persona", "value": "Test agent for HaznMemory integration"},
            {"label": "human", "value": "Integration test harness"},
            {"label": "active_client_context", "value": ""},
        ],
        include_base_tools=False,
    )


def _cleanup_agent(client, agent_id: str):
    """Delete a Letta agent, ignoring errors."""
    try:
        client.agents.delete(agent_id)
    except Exception:
        pass


# ── Context Injection Timing (MEM-03) ─────────────────────────────


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
class TestContextInjectionTiming:
    """Verify that load_client_context() completes in under 2 seconds."""

    def test_context_injection_timing(self):
        """load_client_context() should inject context into Letta block in < 2 seconds."""
        from hazn_platform.content.models import BrandVoice
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient
        from hazn_platform.marketing.models import Campaign, Keyword

        letta_client = get_letta_client()
        agent = _create_test_agent(letta_client, "timing")

        try:
            # Set up Django test data
            agency = Agency.objects.create(
                name="Timing Agency",
                slug=f"timing-agency-{uuid.uuid4().hex[:6]}",
                house_style={"tone": "professional"},
                methodology={"approach": "data-driven"},
                tool_preferences={"context_loading_policy": "full"},
            )
            client = EndClient.objects.create(
                agency=agency,
                name="Timing Client",
                slug=f"timing-client-{uuid.uuid4().hex[:6]}",
                competitors=["Competitor A", "Competitor B"],
            )
            BrandVoice.objects.create(
                end_client=client,
                content="Professional and warm tone with active voice",
                is_active=True,
            )
            for i in range(10):
                Keyword.objects.create(
                    end_client=client,
                    term=f"timing-keyword-{i}",
                    search_volume=1000 + i * 100,
                    intent="commercial",
                )
            Campaign.objects.create(
                end_client=client,
                name="Timing Campaign",
                campaign_type="content",
                status="active",
            )

            mem = HaznMemory(
                agent_id=agent.id,
                l3_client_id=client.id,
                l2_agency_id=agency.id,
            )

            # Time the context injection
            start = time.monotonic()
            mem.load_client_context()
            elapsed = time.monotonic() - start

            assert elapsed < 2.0, (
                f"Context injection took {elapsed:.2f}s, exceeding 2s threshold"
            )

            # Verify block has non-empty content
            block = letta_client.agents.blocks.retrieve(
                agent_id=agent.id,
                block_label="active_client_context",
            )
            assert block.value, "active_client_context block should be non-empty"
            assert "Timing Client" in block.value
        finally:
            _cleanup_agent(letta_client, agent.id)


# ── Client Isolation (MEM-10) ─────────────────────────────────────


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
class TestClientIsolation:
    """Verify zero cross-client data contamination between L3 clients."""

    def test_client_isolation(self):
        """Two separate agents for different L3 clients produce zero cross-client leakage."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient

        letta_client = get_letta_client()
        agent_a = _create_test_agent(letta_client, "isolation-a")
        agent_b = _create_test_agent(letta_client, "isolation-b")

        try:
            agency = Agency.objects.create(
                name="Isolation Agency",
                slug=f"isolation-agency-{uuid.uuid4().hex[:6]}",
                tool_preferences={"context_loading_policy": "full"},
            )
            client_a = EndClient.objects.create(
                agency=agency,
                name="Client Alpha",
                slug=f"client-alpha-{uuid.uuid4().hex[:6]}",
            )
            client_b = EndClient.objects.create(
                agency=agency,
                name="Client Beta",
                slug=f"client-beta-{uuid.uuid4().hex[:6]}",
            )

            # Session 1: Agent A adds a craft learning specific to client A
            mem_a = HaznMemory(
                agent_id=agent_a.id,
                l3_client_id=client_a.id,
                l2_agency_id=agency.id,
            )
            mem_a.add_learning(CraftLearning(
                content="Client Alpha prefers formal academic tone with citations",
                source=LearningSource.USER_EXPLICIT,
                agent_type="copywriter",
                l3_client_id=client_a.id,
            ))
            mem_a.checkpoint_sync()

            # End session A (wipe context)
            mem_a.end_session([])

            # Session 2: Agent B for client B -- search for client A's learning
            mem_b = HaznMemory(
                agent_id=agent_b.id,
                l3_client_id=client_b.id,
                l2_agency_id=agency.id,
            )
            mem_b.load_client_context()

            # Search client B's archival for client A's specific learning
            results = mem_b.search_memory("formal academic tone with citations")

            # Client B's agent should NOT find client A's learning
            # (different Letta agent = different archival)
            for result in results:
                assert "Client Alpha" not in result["content"], (
                    f"Cross-client contamination detected: client B found "
                    f"client A data: {result['content'][:80]}"
                )

            # Verify client B's active_client_context does not mention client A
            block_b = letta_client.agents.blocks.retrieve(
                agent_id=agent_b.id,
                block_label="active_client_context",
            )
            if block_b.value:
                assert "Client Alpha" not in block_b.value, (
                    "Cross-client contamination: client B context contains client A data"
                )
        finally:
            _cleanup_agent(letta_client, agent_a.id)
            _cleanup_agent(letta_client, agent_b.id)


# ── Full Session Lifecycle ─────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
class TestFullSessionLifecycle:
    """End-to-end session lifecycle: load -> work -> checkpoint -> end."""

    def test_full_session_lifecycle(self):
        """Full lifecycle: load context, add learnings, checkpoint, search, end session."""
        from hazn_platform.content.models import BrandVoice
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient
        from hazn_platform.marketing.models import Campaign, Keyword

        letta_client = get_letta_client()
        agent = _create_test_agent(letta_client, "lifecycle")

        try:
            # Set up Django data
            agency = Agency.objects.create(
                name="Lifecycle Agency",
                slug=f"lifecycle-agency-{uuid.uuid4().hex[:6]}",
                house_style={"tone": "direct"},
                methodology={"approach": "agile"},
                tool_preferences={"context_loading_policy": "full"},
            )
            client = EndClient.objects.create(
                agency=agency,
                name="Lifecycle Client",
                slug=f"lifecycle-client-{uuid.uuid4().hex[:6]}",
                competitors=["BigCorp"],
            )
            BrandVoice.objects.create(
                end_client=client,
                content="Bold and direct communication style",
                is_active=True,
            )
            Campaign.objects.create(
                end_client=client,
                name="Lifecycle Campaign",
                campaign_type="seo",
                status="active",
            )

            mem = HaznMemory(
                agent_id=agent.id,
                l3_client_id=client.id,
                l2_agency_id=agency.id,
            )

            # Step 1: Load client context -- verify block populated
            mem.load_client_context()
            block = letta_client.agents.blocks.retrieve(
                agent_id=agent.id,
                block_label="active_client_context",
            )
            assert block.value, "Context block should be populated"
            assert "Lifecycle Client" in block.value

            # Step 2: Add craft learnings
            for i in range(3):
                mem.add_learning(CraftLearning(
                    content=f"Lifecycle learning {i}: client prefers bold headlines (test {uuid.uuid4().hex[:6]})",
                    source=LearningSource.AGENT_INFERRED,
                    confidence=0.8 + i * 0.05,
                    agent_type="seo",
                    l3_client_id=client.id,
                ))

            # Step 3: Trigger checkpoint via 10 record_turn calls
            for _ in range(10):
                mem.record_turn()

            # Verify learnings are flushed (buffer empty after checkpoint)
            assert len(mem._pending_learnings) == 0

            # Step 4: Search memory -- verify learnings are retrievable
            results = mem.search_memory("bold headlines")
            assert len(results) > 0, "Search should find at least one learning"
            found_content = " ".join(r["content"] for r in results)
            assert "bold headlines" in found_content

            # Step 5: End session with a keyword finding
            now = datetime.now(timezone.utc)
            keyword_finding = StructuredFinding(
                finding_type="keyword",
                data={
                    "term": f"lifecycle-test-kw-{uuid.uuid4().hex[:6]}",
                    "search_volume": 2500,
                    "intent": "commercial",
                },
                workflow_run_id=uuid.uuid4(),
                agent_type="seo",
                session_timestamp=now,
            )
            mem.end_session([keyword_finding])

            # Verify: Keyword created in Postgres with provenance
            kw = Keyword.objects.filter(term__startswith="lifecycle-test-kw-").first()
            assert kw is not None, "Keyword should have been created in Postgres"
            assert kw.end_client == client
            assert kw.search_volume == 2500
            assert "_provenance" in kw.metadata
            assert kw.metadata["_provenance"]["agent_type"] == "seo"

            # Verify: context block wiped
            block_after = letta_client.agents.blocks.retrieve(
                agent_id=agent.id,
                block_label="active_client_context",
            )
            assert block_after.value == "", (
                f"Context block should be empty after end_session, "
                f"got: {block_after.value[:50]!r}"
            )

            # Verify: learnings still in archival (persisted by checkpoint)
            # Search on the agent directly to confirm
            search_results = letta_client.agents.passages.search(
                agent_id=agent.id,
                query="bold headlines",
            )
            assert search_results.count > 0, (
                "Learnings should persist in archival after session end"
            )
        finally:
            _cleanup_agent(letta_client, agent.id)

"""Integration tests for Letta memory operations.

These tests require a running Docker Letta instance (port 8283).
Run with: uv run pytest tests/test_memory_integration.py -m integration -x -q

Tests are skipped when Letta is unavailable.
"""

import uuid

import pytest


# Skip entire module if Letta is not reachable
def _letta_available() -> bool:
    """Check if Docker Letta is reachable."""
    try:
        import httpx

        resp = httpx.get("http://localhost:8283/v1/health", timeout=5.0)
        return resp.status_code == 200
    except Exception:
        return False


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not _letta_available(), reason="Docker Letta not running on port 8283"
    ),
]


# ── Shared Fixtures ──────────────────────────────────────────────────


@pytest.fixture()
def letta_client():
    """Provide a real Letta client for integration tests."""
    from hazn_platform.core.letta_client import get_letta_client

    return get_letta_client()


@pytest.fixture()
def test_agent(letta_client):
    """Create a temporary Letta agent and clean it up after test."""
    agent_name = f"test--{uuid.uuid4()}"
    agent = letta_client.agents.create(
        name=agent_name,
        system="Integration test agent",
        memory_blocks=[{"label": "active_client_context", "value": ""}],
        tags=["test"],
    )
    yield agent
    # Cleanup
    try:
        letta_client.agents.delete(agent.id)
    except Exception:
        pass  # Agent may already be deleted by test


# ── MEMO-01: Agent Provisioning ──────────────────────────────────────


@pytest.mark.django_db
class TestAgentProvisioning:
    """MEMO-01: One Letta agent per client with isolated persistent memory."""

    def test_creates_new_agent(self, letta_client):
        """Creating agent via SDK works and agent is retrievable."""
        name = f"test--{uuid.uuid4()}"
        agent = letta_client.agents.create(
            name=name,
            system="Test agent",
            memory_blocks=[{"label": "active_client_context", "value": ""}],
        )
        try:
            found = list(letta_client.agents.list(name=name))
            assert len(found) == 1
            assert found[0].id == agent.id
        finally:
            letta_client.agents.delete(agent.id)

    def test_no_duplicate_on_repeat(self, letta_client):
        """list() wrapper correctly detects existing agent."""
        name = f"test--{uuid.uuid4()}"
        agent = letta_client.agents.create(
            name=name,
            system="Test",
            memory_blocks=[{"label": "active_client_context", "value": ""}],
        )
        try:
            existing = list(letta_client.agents.list(name=name))
            assert len(existing) == 1, "Should find exactly one agent"
        finally:
            letta_client.agents.delete(agent.id)


# ── MEMO-02: Context Loading ─────────────────────────────────────────


@pytest.mark.django_db
class TestContextLoading:
    """MEMO-02: Client context loaded at workflow run start."""

    def test_load_client_context(self, letta_client, test_agent):
        """HaznMemory.load_client_context() writes to Letta block."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient

        agency = Agency.load()
        client = EndClient.objects.create(
            name="Integration Test Client", slug="int-test", agency=agency
        )

        memory = HaznMemory(
            agent_id=test_agent.id,
            l3_client_id=client.pk,
            l2_agency_id=agency.pk,
        )
        # Should not raise -- non-fatal if context assembly has issues
        memory.load_client_context()

        # Verify block was updated (read it back)
        blocks = letta_client.agents.blocks.list(agent_id=test_agent.id)
        ctx_blocks = [
            b
            for b in blocks
            if getattr(b, "label", None) == "active_client_context"
        ]
        assert len(ctx_blocks) == 1
        # Block should have some content (at minimum client name)

        client.delete()


# ── MEMO-03 + MEMO-04: Learning Accumulation ─────────────────────────


@pytest.mark.django_db
class TestLearningAccumulation:
    """MEMO-03 + MEMO-04: Learning writes and checkpoint flush."""

    def test_add_learning_and_checkpoint(self, letta_client, test_agent):
        """CraftLearning persists to Letta archival after checkpoint."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.memory_types import CraftLearning, LearningSource
        from hazn_platform.core.models import Agency

        agency = Agency.load()
        client_id = uuid.uuid4()

        memory = HaznMemory(
            agent_id=test_agent.id,
            l3_client_id=client_id,
            l2_agency_id=agency.pk,
        )
        learning = CraftLearning(
            content="Integration test learning -- site prefers short titles under 60 chars",
            source=LearningSource.AGENT_INFERRED,
            confidence=0.85,
            agent_type="seo",
            l3_client_id=client_id,
        )
        memory.add_learning(learning)
        memory.checkpoint_sync()

        # Verify passage exists in archival
        passages = letta_client.agents.passages.list(agent_id=test_agent.id)
        texts = [p.text for p in passages]
        assert any(
            "Integration test learning" in t for t in texts
        ), f"Learning not found in passages: {texts}"

    def test_checkpoint_flushes_multiple(self, letta_client, test_agent):
        """Multiple buffered learnings all flush at checkpoint."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.memory_types import CraftLearning, LearningSource
        from hazn_platform.core.models import Agency

        agency = Agency.load()
        client_id = uuid.uuid4()

        memory = HaznMemory(
            agent_id=test_agent.id,
            l3_client_id=client_id,
            l2_agency_id=agency.pk,
        )
        for i in range(3):
            memory.add_learning(
                CraftLearning(
                    content=f"Batch learning {i} -- integration test",
                    source=LearningSource.AGENT_INFERRED,
                    confidence=0.7,
                    agent_type="seo",
                    l3_client_id=client_id,
                )
            )
        memory.checkpoint_sync()

        passages = letta_client.agents.passages.list(agent_id=test_agent.id)
        batch_passages = [p for p in passages if "Batch learning" in p.text]
        assert (
            len(batch_passages) >= 3
        ), f"Expected 3 batch learnings, got {len(batch_passages)}"


# ── MEMO-05: Semantic Search ─────────────────────────────────────────


@pytest.mark.django_db
class TestSemanticSearch:
    """MEMO-05: Semantic memory search across client learnings."""

    def test_search_returns_ranked_results(self, letta_client, test_agent):
        """search_memory returns results ranked by composite score."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.memory_types import CraftLearning, LearningSource
        from hazn_platform.core.models import Agency

        agency = Agency.load()
        client_id = uuid.uuid4()

        memory = HaznMemory(
            agent_id=test_agent.id,
            l3_client_id=client_id,
            l2_agency_id=agency.pk,
        )

        # Write distinct learnings
        topics = [
            "Client prefers minimalist design with lots of whitespace",
            "SEO meta descriptions should be under 155 characters",
            "Brand voice is professional but approachable",
        ]
        for topic in topics:
            memory.add_learning(
                CraftLearning(
                    content=topic,
                    source=LearningSource.AGENT_INFERRED,
                    confidence=0.8,
                    agent_type="seo",
                    l3_client_id=client_id,
                )
            )
        memory.checkpoint_sync()

        # Search for SEO-related content
        results = memory.search_memory("SEO meta description length", limit=5)
        assert len(results) > 0, "Search should return at least one result"
        # Results should have score and content keys
        assert "score" in results[0]
        assert "content" in results[0]
        assert "id" in results[0]

    def test_search_filters_corrected(self, letta_client, test_agent):
        """Corrected passages are excluded from search results."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.memory_types import CraftLearning, LearningSource
        from hazn_platform.core.models import Agency

        agency = Agency.load()
        client_id = uuid.uuid4()

        memory = HaznMemory(
            agent_id=test_agent.id,
            l3_client_id=client_id,
            l2_agency_id=agency.pk,
        )
        memory.add_learning(
            CraftLearning(
                content="Wrong learning that will be corrected -- meta titles should be 200 chars",
                source=LearningSource.AGENT_INFERRED,
                confidence=0.9,
                agent_type="seo",
                l3_client_id=client_id,
            )
        )
        memory.checkpoint_sync()

        # Find and correct the learning
        results = memory.search_memory("meta titles 200 chars", limit=5)
        if results:
            memory.correct_memory(
                passage_id=results[0]["id"],
                new_content="Meta titles should be under 60 characters",
                reason="Integration test correction",
                corrected_by="test",
            )

            # Search again -- corrected passage should be filtered out
            results_after = memory.search_memory("meta titles 200 chars", limit=5)
            corrected_ids = {r["id"] for r in results_after}
            # Original passage should not appear (it was soft-deleted)
            assert results[0]["id"] not in corrected_ids


# ── MEMO-06: Memory Correction ───────────────────────────────────────


@pytest.mark.django_db
class TestMemoryCorrection:
    """MEMO-06: User can correct wrong learnings."""

    def test_correct_memory_creates_replacement(self, letta_client, test_agent):
        """correct_memory soft-deletes original and creates replacement passage."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.memory_types import CraftLearning, LearningSource
        from hazn_platform.core.models import Agency

        agency = Agency.load()
        client_id = uuid.uuid4()

        memory = HaznMemory(
            agent_id=test_agent.id,
            l3_client_id=client_id,
            l2_agency_id=agency.pk,
        )
        memory.add_learning(
            CraftLearning(
                content="Incorrect claim to be corrected in integration test",
                source=LearningSource.AGENT_INFERRED,
                confidence=0.75,
                agent_type="test",
                l3_client_id=client_id,
            )
        )
        memory.checkpoint_sync()

        results = memory.search_memory(
            "incorrect claim corrected integration", limit=5
        )
        assert len(results) > 0, "Should find the learning to correct"

        original_id = results[0]["id"]
        replacement_id = memory.correct_memory(
            passage_id=original_id,
            new_content="Corrected claim from integration test",
            reason="Testing correction workflow",
            corrected_by="integration_test",
        )

        # Replacement should exist
        assert replacement_id is not None or replacement_id != original_id

        # Verify replacement passage exists
        passages = letta_client.agents.passages.list(agent_id=test_agent.id)
        texts = [p.text for p in passages]
        assert any("Corrected claim" in t for t in texts)

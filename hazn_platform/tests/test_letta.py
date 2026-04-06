"""Integration tests for Letta client helpers.

Tests require a running Letta server with a valid LLM API key
(OPENAI_API_KEY or ANTHROPIC_API_KEY on the Letta container).
"""

import pytest

from hazn_platform.core.letta_client import get_letta_client


@pytest.mark.integration
class TestLettaClient:
    """Letta SDK connectivity and agent operations."""

    def test_get_letta_client_connects(self):
        """get_letta_client() should return a connected Letta client."""
        client = get_letta_client()
        # Verify connectivity by listing agents (should not raise)
        agents = list(client.agents.list())
        assert isinstance(agents, list)

    def test_create_agent_returns_id(self):
        """Creating a test agent should return an agent with a valid id."""
        client = get_letta_client()
        agent = client.agents.create(
            name="hazn-test-agent-create",
            model="openai/gpt-4o-mini",
            embedding="openai/text-embedding-ada-002",
            memory_blocks=[
                {"label": "persona", "value": "Test persona for Hazn integration test"},
                {"label": "human", "value": "Test human for Hazn integration test"},
            ],
            include_base_tools=False,
        )
        try:
            assert agent.id is not None
            assert len(agent.id) > 0
        finally:
            # Clean up
            client.agents.delete(agent.id)

    def test_archival_passage_insert_and_search(self):
        """Insert an archival passage and search for it via semantic search."""
        client = get_letta_client()
        agent = client.agents.create(
            name="hazn-test-agent-archival",
            model="openai/gpt-4o-mini",
            embedding="openai/text-embedding-ada-002",
            memory_blocks=[
                {"label": "persona", "value": "Test persona"},
                {"label": "human", "value": "Test human"},
            ],
            include_base_tools=False,
        )
        try:
            # Insert a passage
            passage_text = "Hazn platform uses persistent memory for marketing agents"
            client.agents.passages.create(
                agent_id=agent.id,
                text=passage_text,
            )

            # Search for the passage
            results = client.agents.passages.search(
                agent_id=agent.id,
                query="Hazn marketing memory",
            )
            # Results should contain our passage
            assert results.count > 0
            found_contents = [r.content for r in results.results]
            assert any("Hazn" in c for c in found_contents)
        finally:
            # Clean up
            client.agents.delete(agent.id)

    def test_delete_agent_succeeds(self):
        """Deleting a test agent should succeed without error."""
        client = get_letta_client()
        agent = client.agents.create(
            name="hazn-test-agent-delete",
            model="openai/gpt-4o-mini",
            embedding="openai/text-embedding-ada-002",
            memory_blocks=[
                {"label": "persona", "value": "Test persona"},
                {"label": "human", "value": "Test human"},
            ],
            include_base_tools=False,
        )
        # Delete should not raise
        client.agents.delete(agent.id)
        # Verify agent no longer exists by trying to retrieve it
        with pytest.raises(Exception):
            client.agents.retrieve(agent.id)

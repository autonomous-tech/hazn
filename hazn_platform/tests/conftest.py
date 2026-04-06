"""Shared test fixtures for integration tests.

Provides Vault AppRole credential patching and other shared setup.
"""

from pathlib import Path

import pytest


def _parse_vault_approle() -> dict[str, str]:
    """Parse .vault-approle file into a dict of key=value pairs."""
    approle_path = Path(__file__).resolve().parent.parent / ".vault-approle"
    creds: dict[str, str] = {}
    if approle_path.exists():
        for line in approle_path.read_text().strip().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                creds[key] = value
    return creds


@pytest.fixture(autouse=True)
def _vault_approle(settings):
    """Read Vault AppRole credentials from .vault-approle and patch Django settings.

    Uses the Django role (broadest access: read + write) for general test
    operations.  The .vault-approle file is created by scripts/vault-init.sh
    on first ``make up``.  Format::

        DJANGO_ROLE_ID=...
        DJANGO_SECRET_ID=...
        ORCHESTRATOR_ROLE_ID=...
        ORCHESTRATOR_SECRET_ID=...
        MCP_ROLE_ID=...
        MCP_SECRET_ID=...
    """
    creds = _parse_vault_approle()
    if "DJANGO_ROLE_ID" in creds:
        settings.VAULT_ROLE_ID = creds["DJANGO_ROLE_ID"]
    if "DJANGO_SECRET_ID" in creds:
        settings.VAULT_SECRET_ID = creds["DJANGO_SECRET_ID"]

    yield

    # Teardown: invalidate cached Vault client so no state leaks between tests
    from hazn_platform.core.vault import invalidate_vault_cache

    invalidate_vault_cache()


@pytest.fixture()
def vault_approle_credentials() -> dict[str, str]:
    """Return the full parsed dict from .vault-approle.

    Exposes all 6 credentials (Django, Orchestrator, MCP role_id + secret_id)
    for policy scoping tests that need to log in with non-Django roles.
    """
    return _parse_vault_approle()


# ── Letta SDK v1.7.11 Mock Fixtures ──────────────────────────────────


@pytest.fixture()
def mock_letta_client():
    """Mock Letta client with correct SDK v1.7.11 method signatures.

    Returns a MagicMock configured with the right nested attribute structure
    for agents.list, agents.create, agents.passages.*, agents.blocks.*.
    """
    from unittest.mock import MagicMock

    client = MagicMock()

    # agents.list() returns a plain list (simulating list() wrapper around SyncArrayPage)
    client.agents.list.return_value = []

    # agents.passages.search returns List[PassageSearchResponseItem]
    client.agents.passages.search.return_value = []

    # agents.passages.list returns List[Passage]
    client.agents.passages.list.return_value = []

    # agents.passages.create returns List[Passage]
    client.agents.passages.create.return_value = []

    return client


@pytest.fixture()
def mock_passage_search_item():
    """Factory for creating mock PassageSearchResponseItem objects.

    Usage:
        item = mock_passage_search_item(text="learning content", score=0.9, passage_id="p-123")
    """
    from unittest.mock import MagicMock

    def _factory(
        text: str = "[source:agent-inferred][confidence:0.85][agent:seo][client:00000000-0000-0000-0000-000000000001][timestamp:2026-03-13T10:00:00+00:00][status:active]\nSome learning content",
        score: float = 0.92,
        passage_id: str = "passage-123",
    ):
        item = MagicMock()
        item.passage.text = text
        item.passage.id = passage_id
        item.score = score
        return item

    return _factory


@pytest.fixture()
def mock_passage():
    """Factory for creating mock Passage objects (for passages.list).

    Usage:
        p = mock_passage(text="content", passage_id="p-456")
    """
    from unittest.mock import MagicMock

    def _factory(
        text: str = "[source:agent-inferred][confidence:0.85][agent:seo][client:00000000-0000-0000-0000-000000000001][timestamp:2026-03-13T10:00:00+00:00][status:active]\nSome content",
        passage_id: str = "passage-456",
    ):
        p = MagicMock()
        p.text = text
        p.id = passage_id
        return p

    return _factory


@pytest.fixture()
def mock_agent_state():
    """Factory for creating mock AgentState objects.

    Usage:
        agent = mock_agent_state(agent_id="agent-789", name="client--uuid")
    """
    from unittest.mock import MagicMock

    def _factory(
        agent_id: str = "agent-test-id",
        name: str = "client--00000000-0000-0000-0000-000000000001",
    ):
        state = MagicMock()
        state.id = agent_id
        state.name = name
        return state

    return _factory

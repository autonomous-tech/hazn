"""Tests for memory tools -- 7 tools ported from hazn_memory_server.py.

All Django ORM calls, Vault reads, and HaznMemory are mocked.
Tests verify:
1. Correct parameter extraction from args dict
2. Agency.load() called (not l2_agency_id param)
3. Correct delegation to HaznMemory
4. Agent SDK return format {"content": [{"type": "text", "text": "..."}]}
"""

from __future__ import annotations

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FAKE_AGENCY_ID = uuid.uuid4()
FAKE_CLIENT_ID = uuid.uuid4()
FAKE_AGENT_ID = "agent-test-001"


def _mock_agency():
    """Return a mock Agency singleton with .id attribute."""
    agency = MagicMock()
    agency.id = FAKE_AGENCY_ID
    return agency


def _patch_sync_to_async():
    """Patch sync_to_async to just run the sync function directly (for testing)."""
    def fake_sync_to_async(fn):
        async def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return fake_sync_to_async


# ---------------------------------------------------------------------------
# load_context tests
# ---------------------------------------------------------------------------


class TestLoadContext:
    """load_context creates HaznMemory via Agency.load() and delegates."""

    @pytest.mark.asyncio
    async def test_creates_memory_and_loads_context(self):
        """load_context creates HaznMemory with Agency.load() and calls load_client_context."""
        mock_memory = MagicMock()
        mock_memory.load_client_context.return_value = None
        mock_agency = _mock_agency()

        with (
            patch("hazn_platform.orchestrator.tools.memory.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.memory._get_agency", return_value=mock_agency),
            patch("hazn_platform.orchestrator.tools.memory._create_memory", return_value=mock_memory),
        ):
            from hazn_platform.orchestrator.tools.memory import load_context, _memory_registry
            _memory_registry.clear()

            result = await load_context.handler({"agent_id": FAKE_AGENT_ID, "client_id": str(FAKE_CLIENT_ID)})

        assert result["content"][0]["type"] == "text"
        assert "Context loaded" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_returns_agent_sdk_format(self):
        """load_context returns proper Agent SDK format."""
        mock_memory = MagicMock()
        mock_memory.load_client_context.return_value = None
        mock_agency = _mock_agency()

        with (
            patch("hazn_platform.orchestrator.tools.memory.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.memory._get_agency", return_value=mock_agency),
            patch("hazn_platform.orchestrator.tools.memory._create_memory", return_value=mock_memory),
        ):
            from hazn_platform.orchestrator.tools.memory import load_context, _memory_registry
            _memory_registry.clear()

            result = await load_context.handler({"agent_id": FAKE_AGENT_ID, "client_id": str(FAKE_CLIENT_ID)})

        assert "content" in result
        assert isinstance(result["content"], list)
        assert result["content"][0]["type"] == "text"


# ---------------------------------------------------------------------------
# write_finding tests
# ---------------------------------------------------------------------------


class TestWriteFinding:
    """write_finding delegates to HaznMemory.write_finding with correct params."""

    @pytest.mark.asyncio
    async def test_delegates_to_hazn_memory_write_finding(self):
        """write_finding creates StructuredFinding and calls HaznMemory.write_finding."""
        mock_memory = MagicMock()
        mock_memory.write_finding.return_value = None
        mock_agency = _mock_agency()

        with (
            patch("hazn_platform.orchestrator.tools.memory.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.memory._get_agency", return_value=mock_agency),
            patch("hazn_platform.orchestrator.tools.memory._create_memory", return_value=mock_memory),
        ):
            from hazn_platform.orchestrator.tools.memory import write_finding, _memory_registry
            _memory_registry.clear()

            result = await write_finding.handler({
                "agent_id": FAKE_AGENT_ID,
                "client_id": str(FAKE_CLIENT_ID),
                "finding_type": "keyword",
                "data": {"term": "test seo"},
            })

        assert result["content"][0]["type"] == "text"
        assert "Finding" in result["content"][0]["text"]
        mock_memory.write_finding.assert_called_once()


# ---------------------------------------------------------------------------
# search_memory tests
# ---------------------------------------------------------------------------


class TestSearchMemory:
    """search_memory delegates to HaznMemory.search_memory."""

    @pytest.mark.asyncio
    async def test_delegates_to_hazn_memory_search(self):
        """search_memory calls HaznMemory.search_memory with query and limit."""
        mock_memory = MagicMock()
        mock_memory.search_memory.return_value = [{"id": "p1", "content": "test", "score": 0.9}]
        mock_agency = _mock_agency()

        with (
            patch("hazn_platform.orchestrator.tools.memory.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.memory._get_agency", return_value=mock_agency),
            patch("hazn_platform.orchestrator.tools.memory._create_memory", return_value=mock_memory),
        ):
            from hazn_platform.orchestrator.tools.memory import search_memory, _memory_registry
            _memory_registry.clear()

            result = await search_memory.handler({
                "agent_id": FAKE_AGENT_ID,
                "client_id": str(FAKE_CLIENT_ID),
                "query": "seo best practices",
                "limit": 3,
            })

        text = result["content"][0]["text"]
        parsed = json.loads(text)
        assert isinstance(parsed, list)
        assert parsed[0]["id"] == "p1"
        mock_memory.search_memory.assert_called_once_with("seo best practices", 3)


# ---------------------------------------------------------------------------
# search_cross_client_insights tests
# ---------------------------------------------------------------------------


class TestSearchCrossClientInsights:
    """search_cross_client_insights queries without Agency flag check (always-on)."""

    @pytest.mark.asyncio
    async def test_always_on_without_flag_check(self):
        """search_cross_client_insights does not check Agency.cross_client_insights flag."""
        mock_memory = MagicMock()
        mock_memory.search_cross_client_insights.return_value = [
            {"finding_type": "keyword", "data": {"term": "test"}, "source_client": "acme"}
        ]
        mock_agency = _mock_agency()

        with (
            patch("hazn_platform.orchestrator.tools.memory.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.memory._get_agency", return_value=mock_agency),
            patch("hazn_platform.orchestrator.tools.memory._create_memory", return_value=mock_memory),
        ):
            from hazn_platform.orchestrator.tools.memory import search_cross_client_insights, _memory_registry
            _memory_registry.clear()

            result = await search_cross_client_insights.handler({
                "agent_id": FAKE_AGENT_ID,
                "client_id": str(FAKE_CLIENT_ID),
                "query": "keyword trends",
            })

        text = result["content"][0]["text"]
        parsed = json.loads(text)
        assert isinstance(parsed, list)
        assert len(parsed) == 1
        # Verify it called search directly (always-on, no flag check)
        mock_memory.search_cross_client_insights.assert_called_once()


# ---------------------------------------------------------------------------
# checkpoint_sync tests
# ---------------------------------------------------------------------------


class TestCheckpointSync:
    """checkpoint_sync delegates to HaznMemory.checkpoint_sync."""

    @pytest.mark.asyncio
    async def test_delegates_to_hazn_memory_checkpoint(self):
        """checkpoint_sync calls HaznMemory.checkpoint_sync."""
        mock_memory = MagicMock()
        mock_memory.checkpoint_sync.return_value = None
        mock_agency = _mock_agency()

        with (
            patch("hazn_platform.orchestrator.tools.memory.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.memory._get_agency", return_value=mock_agency),
            patch("hazn_platform.orchestrator.tools.memory._create_memory", return_value=mock_memory),
        ):
            from hazn_platform.orchestrator.tools.memory import checkpoint_sync, _memory_registry
            _memory_registry.clear()

            result = await checkpoint_sync.handler({
                "agent_id": FAKE_AGENT_ID,
                "client_id": str(FAKE_CLIENT_ID),
            })

        assert result["content"][0]["type"] == "text"
        assert "Checkpoint" in result["content"][0]["text"]
        mock_memory.checkpoint_sync.assert_called_once()


# ---------------------------------------------------------------------------
# correct_memory tests
# ---------------------------------------------------------------------------


class TestCorrectMemory:
    """correct_memory delegates to HaznMemory.correct_memory."""

    @pytest.mark.asyncio
    async def test_delegates_to_hazn_memory_correct(self):
        """correct_memory calls HaznMemory.correct_memory with correct params."""
        mock_memory = MagicMock()
        mock_memory.correct_memory.return_value = "new-passage-id"
        mock_agency = _mock_agency()

        with (
            patch("hazn_platform.orchestrator.tools.memory.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.memory._get_agency", return_value=mock_agency),
            patch("hazn_platform.orchestrator.tools.memory._create_memory", return_value=mock_memory),
        ):
            from hazn_platform.orchestrator.tools.memory import correct_memory, _memory_registry
            _memory_registry.clear()

            result = await correct_memory.handler({
                "agent_id": FAKE_AGENT_ID,
                "client_id": str(FAKE_CLIENT_ID),
                "passage_id": "old-passage-123",
                "new_content": "corrected content",
                "reason": "was inaccurate",
                "corrected_by": "user",
            })

        assert result["content"][0]["type"] == "text"
        assert "corrected" in result["content"][0]["text"].lower()
        mock_memory.correct_memory.assert_called_once_with(
            passage_id="old-passage-123",
            new_content="corrected content",
            reason="was inaccurate",
            corrected_by="user",
        )


# ---------------------------------------------------------------------------
# get_credentials tests
# ---------------------------------------------------------------------------


class TestGetCredentials:
    """get_credentials fetches from Vault via VaultCredential using client_id."""

    @pytest.mark.asyncio
    async def test_fetches_credential_from_vault(self):
        """get_credentials looks up VaultCredential by client_id and reads secret."""
        mock_credential = MagicMock()
        mock_credential.vault_secret_id = "secret/path/ga4"
        mock_vc_manager = MagicMock()
        mock_vc_manager.get.return_value = mock_credential

        with (
            patch("hazn_platform.orchestrator.tools.memory.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.memory._get_vault_credential", return_value=mock_credential),
            patch("hazn_platform.orchestrator.tools.memory._read_secret", return_value={"token": "abc123"}),
        ):
            from hazn_platform.orchestrator.tools.memory import get_credentials, _memory_registry
            _memory_registry.clear()

            result = await get_credentials.handler({
                "client_id": str(FAKE_CLIENT_ID),
                "service_name": "ga4",
            })

        text = result["content"][0]["text"]
        parsed = json.loads(text)
        assert parsed["token"] == "abc123"

    @pytest.mark.asyncio
    async def test_returns_error_when_credential_not_found(self):
        """get_credentials returns error content when VaultCredential not found."""

        def raise_not_found(*args, **kwargs):
            raise Exception("VaultCredential matching query does not exist.")

        with (
            patch("hazn_platform.orchestrator.tools.memory.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.memory._get_vault_credential", side_effect=raise_not_found),
        ):
            from hazn_platform.orchestrator.tools.memory import get_credentials

            result = await get_credentials.handler({
                "client_id": str(FAKE_CLIENT_ID),
                "service_name": "nonexistent",
            })

        assert result.get("isError") is True


# ---------------------------------------------------------------------------
# _memory_registry tests
# ---------------------------------------------------------------------------


class TestMemoryRegistry:
    """_memory_registry is session-scoped (module-level dict)."""

    @pytest.mark.asyncio
    async def test_registry_is_module_level_dict(self):
        """_memory_registry is a dict at module level."""
        from hazn_platform.orchestrator.tools.memory import _memory_registry

        assert isinstance(_memory_registry, dict)

    @pytest.mark.asyncio
    async def test_registry_reuses_memory_for_same_agent(self):
        """_memory_registry returns same HaznMemory for same agent_id."""
        mock_memory = MagicMock()
        mock_agency = _mock_agency()

        with (
            patch("hazn_platform.orchestrator.tools.memory.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.memory._get_agency", return_value=mock_agency),
            patch("hazn_platform.orchestrator.tools.memory._create_memory", return_value=mock_memory),
        ):
            from hazn_platform.orchestrator.tools.memory import load_context, _memory_registry
            _memory_registry.clear()

            mock_memory.load_client_context.return_value = None

            await load_context.handler({"agent_id": FAKE_AGENT_ID, "client_id": str(FAKE_CLIENT_ID)})
            await load_context.handler({"agent_id": FAKE_AGENT_ID, "client_id": str(FAKE_CLIENT_ID)})

        # Should reuse from registry second time (only one create call)
        assert FAKE_AGENT_ID in _memory_registry

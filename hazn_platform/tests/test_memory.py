"""Unit tests for HaznMemory type system, MemoryCorrection model, and HaznMemory class.

Tests cover:
- Pydantic type system (CraftLearning, StructuredFinding, ClientContext, LearningSource)
- MemoryCorrection Django model
- HaznMemory class: load_client_context, search_memory, search_cross_client_insights,
  correct_memory, add_learning, _write_craft_learning
"""

import json
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from hazn_platform.core.memory_types import (
    ClientContext,
    CraftLearning,
    LearningSource,
    StructuredFinding,
)


# ── LearningSource Enum ─────────────────────────────────────────────


class TestLearningSource:
    def test_learning_source_has_three_values(self):
        """LearningSource should have exactly three members."""
        assert len(LearningSource) == 3

    def test_learning_source_values(self):
        """LearningSource values match expected strings."""
        assert LearningSource.AGENT_INFERRED == "agent-inferred"
        assert LearningSource.RULE_EXTRACTED == "rule-extracted"
        assert LearningSource.USER_EXPLICIT == "user-explicit"

    def test_learning_source_is_str(self):
        """LearningSource members are strings (StrEnum)."""
        assert isinstance(LearningSource.AGENT_INFERRED, str)


# ── CraftLearning Pydantic Model ────────────────────────────────────


class TestCraftLearning:
    def test_craft_learning_all_fields(self):
        """CraftLearning accepts all required and optional fields."""
        cl = CraftLearning(
            content="Client prefers short headlines",
            source=LearningSource.AGENT_INFERRED,
            confidence=0.85,
            agent_type="seo",
            l3_client_id=uuid.uuid4(),
            supersedes_id="old-passage-123",
            tags=["style", "headlines"],
        )
        assert cl.content == "Client prefers short headlines"
        assert cl.source == LearningSource.AGENT_INFERRED
        assert cl.confidence == 0.85
        assert cl.agent_type == "seo"
        assert cl.supersedes_id == "old-passage-123"
        assert cl.tags == ["style", "headlines"]

    def test_craft_learning_optional_fields_default(self):
        """CraftLearning optional fields default correctly."""
        cl = CraftLearning(
            content="Test learning",
            source=LearningSource.RULE_EXTRACTED,
            confidence=0.7,
            agent_type="copywriter",
            l3_client_id=uuid.uuid4(),
        )
        assert cl.supersedes_id is None
        assert cl.tags is None

    def test_craft_learning_user_explicit_defaults_confidence_1(self):
        """User-explicit source should default confidence to 1.0 if not explicitly provided."""
        cl = CraftLearning(
            content="Remember: no exclamation marks",
            source=LearningSource.USER_EXPLICIT,
            agent_type="copywriter",
            l3_client_id=uuid.uuid4(),
        )
        assert cl.confidence == 1.0

    def test_craft_learning_user_explicit_respects_explicit_confidence(self):
        """User-explicit source should NOT override confidence if explicitly set."""
        cl = CraftLearning(
            content="Remember: no exclamation marks",
            source=LearningSource.USER_EXPLICIT,
            confidence=0.9,
            agent_type="copywriter",
            l3_client_id=uuid.uuid4(),
        )
        assert cl.confidence == 0.9

    def test_craft_learning_has_created_at(self):
        """CraftLearning should have a created_at field defaulting to utcnow."""
        before = datetime.now(timezone.utc)
        cl = CraftLearning(
            content="Test",
            source=LearningSource.AGENT_INFERRED,
            confidence=0.5,
            agent_type="seo",
            l3_client_id=uuid.uuid4(),
        )
        after = datetime.now(timezone.utc)
        assert before <= cl.created_at <= after

    def test_craft_learning_confidence_bounds(self):
        """CraftLearning confidence must be 0.0-1.0."""
        with pytest.raises(Exception):
            CraftLearning(
                content="Bad confidence",
                source=LearningSource.AGENT_INFERRED,
                confidence=1.5,
                agent_type="seo",
                l3_client_id=uuid.uuid4(),
            )
        with pytest.raises(Exception):
            CraftLearning(
                content="Bad confidence",
                source=LearningSource.AGENT_INFERRED,
                confidence=-0.1,
                agent_type="seo",
                l3_client_id=uuid.uuid4(),
            )


# ── StructuredFinding Pydantic Model ────────────────────────────────


class TestStructuredFinding:
    def test_structured_finding_all_fields(self):
        """StructuredFinding accepts all fields."""
        sf = StructuredFinding(
            finding_type="keyword_gap",
            data={"gap": "missing long-tail keywords"},
            workflow_run_id=uuid.uuid4(),
            agent_type="seo",
            session_timestamp=datetime.now(timezone.utc),
        )
        assert sf.finding_type == "keyword_gap"
        assert sf.data == {"gap": "missing long-tail keywords"}
        assert sf.agent_type == "seo"

    def test_structured_finding_optional_workflow_run_id(self):
        """StructuredFinding workflow_run_id is optional."""
        sf = StructuredFinding(
            finding_type="audit_score",
            data={"score": 85},
            agent_type="auditor",
            session_timestamp=datetime.now(timezone.utc),
        )
        assert sf.workflow_run_id is None


# ── ClientContext Pydantic Model ─────────────────────────────────────


class TestClientContext:
    def test_client_context_all_fields(self):
        """ClientContext accepts all fields."""
        cc = ClientContext(
            agency={"name": "Acme Agency", "house_style": {}},
            client={"name": "Widget Corp", "competitors": []},
            brand_voice="Professional and warm",
            active_campaigns=[{"name": "Q1 Push", "type": "content"}],
            top_keywords=[{"term": "widgets", "status": "active"}],
        )
        assert cc.agency["name"] == "Acme Agency"
        assert cc.client["name"] == "Widget Corp"
        assert cc.brand_voice == "Professional and warm"
        assert len(cc.active_campaigns) == 1
        assert len(cc.top_keywords) == 1

    def test_client_context_nullable_brand_voice(self):
        """ClientContext brand_voice is nullable."""
        cc = ClientContext(
            agency={"name": "Test"},
            client={"name": "Test"},
            brand_voice=None,
            active_campaigns=[],
            top_keywords=[],
        )
        assert cc.brand_voice is None


# ── MemoryCorrection Django Model ────────────────────────────────────


@pytest.mark.django_db
class TestMemoryCorrection:
    def test_create_memory_correction(self):
        """MemoryCorrection stores full audit trail."""
        from hazn_platform.core.models import Agency, EndClient, MemoryCorrection

        agency = Agency.objects.create(name="Test Agency", slug="test-mc")
        client = EndClient.objects.create(
            agency=agency, name="Test Client", slug="test-mc-client"
        )
        mc = MemoryCorrection.objects.create(
            agent_id="agent-letta-123",
            original_passage_id="passage-old-456",
            replacement_passage_id="passage-new-789",
            original_content="Client likes exclamation marks!",
            corrected_content="Client dislikes exclamation marks",
            reason="User correction: client explicitly said no exclamation marks",
            corrected_by="user-abc",
            end_client=client,
        )
        assert isinstance(mc.pk, uuid.UUID)
        assert mc.agent_id == "agent-letta-123"
        assert mc.original_passage_id == "passage-old-456"
        assert mc.replacement_passage_id == "passage-new-789"
        assert mc.original_content == "Client likes exclamation marks!"
        assert mc.corrected_content == "Client dislikes exclamation marks"
        assert mc.reason == "User correction: client explicitly said no exclamation marks"
        assert mc.corrected_by == "user-abc"
        assert mc.end_client == client
        assert mc.created_at is not None

    def test_memory_correction_nullable_replacement(self):
        """MemoryCorrection.replacement_passage_id is nullable (deletion without replacement)."""
        from hazn_platform.core.models import Agency, EndClient, MemoryCorrection

        agency = Agency.objects.create(name="Agency", slug="mc-null")
        client = EndClient.objects.create(
            agency=agency, name="Client", slug="mc-null-client"
        )
        mc = MemoryCorrection.objects.create(
            agent_id="agent-123",
            original_passage_id="passage-456",
            original_content="Wrong memory",
            corrected_content="",
            reason="Delete incorrect memory",
            corrected_by="system",
            end_client=client,
        )
        assert mc.replacement_passage_id is None

    def test_memory_correction_cascade_on_endclient_delete(self):
        """Deleting EndClient should cascade-delete MemoryCorrections."""
        from hazn_platform.core.models import Agency, EndClient, MemoryCorrection

        agency = Agency.objects.create(name="Agency", slug="mc-cascade")
        client = EndClient.objects.create(
            agency=agency, name="Client", slug="mc-cascade-client"
        )
        MemoryCorrection.objects.create(
            agent_id="agent-1",
            original_passage_id="p-1",
            original_content="old",
            corrected_content="new",
            reason="test",
            corrected_by="system",
            end_client=client,
        )
        assert MemoryCorrection.objects.count() == 1
        client.delete()
        assert MemoryCorrection.objects.count() == 0


# ── HaznMemory Class ────────────────────────────────────────────────


@pytest.mark.django_db
class TestHaznMemoryInit:
    @patch("hazn_platform.core.memory.get_letta_client")
    def test_init_stores_ids_and_client(self, mock_get_client):
        """HaznMemory.__init__ stores agent_id, l3_client_id, l2_agency_id, and Letta client."""
        from hazn_platform.core.memory import HaznMemory

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        agent_id = "agent-123"
        l3_id = uuid.uuid4()
        l2_id = uuid.uuid4()

        mem = HaznMemory(agent_id=agent_id, l3_client_id=l3_id, l2_agency_id=l2_id)

        assert mem._agent_id == agent_id
        assert mem._l3_client_id == l3_id
        assert mem._l2_agency_id == l2_id
        assert mem._client == mock_client
        assert mem._turn_counter == 0
        assert mem._pending_learnings == []
        mock_get_client.assert_called_once()


@pytest.mark.django_db
class TestLoadClientContext:
    @patch("hazn_platform.core.memory.get_letta_client")
    def test_load_client_context_assembles_and_writes(self, mock_get_client):
        """load_client_context queries Django models and writes to Letta block."""
        from hazn_platform.content.models import BrandVoice
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient
        from hazn_platform.marketing.models import Campaign, Keyword

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Set up test data
        agency = Agency.objects.create(
            name="Acme Agency",
            slug="acme-agency",
            house_style={"tone": "professional"},
            methodology={"approach": "data-driven"},
            tool_preferences={"context_loading_policy": "full"},
        )
        client = EndClient.objects.create(
            agency=agency,
            name="Widget Corp",
            slug="widget-corp",
            competitors=["Competitor A"],
        )
        BrandVoice.objects.create(
            end_client=client,
            content="Professional and warm tone",
            is_active=True,
        )
        Keyword.objects.create(
            end_client=client,
            term="widgets online",
            search_volume=5000,
            intent="commercial",
        )
        Campaign.objects.create(
            end_client=client,
            name="Q1 Push",
            campaign_type="content",
            status="active",
        )

        mem = HaznMemory(
            agent_id="agent-1",
            l3_client_id=client.id,
            l2_agency_id=agency.id,
        )
        mem.load_client_context()

        # Verify block update was called
        mock_client.agents.blocks.update.assert_called_once()
        call_kwargs = mock_client.agents.blocks.update.call_args
        assert call_kwargs.kwargs.get("agent_id") == "agent-1" or call_kwargs.args[0] == "active_client_context"

        # Verify the written value is valid JSON with expected keys
        # The block_label is the first positional arg
        written_value = call_kwargs.kwargs.get("value") or call_kwargs.args[-1]
        context = json.loads(written_value)
        assert "agency" in context
        assert "client" in context
        assert context["agency"]["name"] == "Acme Agency"
        assert context["client"]["name"] == "Widget Corp"

    @patch("hazn_platform.core.memory.get_letta_client")
    def test_load_client_context_checks_policy(self, mock_get_client):
        """load_client_context reads context_loading_policy from Agency.tool_preferences."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        agency = Agency.objects.create(
            name="Agency",
            slug="policy-agency",
            tool_preferences={"context_loading_policy": "unknown-mode"},
        )
        client = EndClient.objects.create(
            agency=agency, name="Client", slug="policy-client"
        )

        mem = HaznMemory(
            agent_id="agent-2",
            l3_client_id=client.id,
            l2_agency_id=agency.id,
        )
        # Should not raise, even with unknown policy (logs warning, proceeds with full)
        mem.load_client_context()
        mock_client.agents.blocks.update.assert_called_once()


@pytest.mark.django_db
class TestSearchMemory:
    @patch("hazn_platform.core.memory.get_letta_client")
    def test_search_memory_filters_corrected_and_superseded(self, mock_get_client):
        """search_memory filters out entries with [status:corrected] or [status:superseded]."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        now = datetime.now(timezone.utc).isoformat()

        # Mock search results as List[PassageSearchResponseItem]
        # Each item has .passage.text, .passage.id, .score
        mock_item_active1 = MagicMock()
        mock_item_active1.passage.text = f"[source:agent-inferred][confidence:0.9][agent:seo][client:abc][timestamp:{now}][status:active]\nActive learning 1"
        mock_item_active1.passage.id = "p1"
        mock_item_active1.score = 0.95

        mock_item_corrected = MagicMock()
        mock_item_corrected.passage.text = f"[source:agent-inferred][confidence:0.8][agent:seo][client:abc][timestamp:{now}][status:corrected]\nCorrected learning"
        mock_item_corrected.passage.id = "p2"
        mock_item_corrected.score = 0.90

        mock_item_active2 = MagicMock()
        mock_item_active2.passage.text = f"[source:user-explicit][confidence:1.0][agent:seo][client:abc][timestamp:{now}][status:active]\nActive learning 2"
        mock_item_active2.passage.id = "p3"
        mock_item_active2.score = 0.85

        mock_item_superseded = MagicMock()
        mock_item_superseded.passage.text = f"[source:agent-inferred][confidence:0.7][agent:seo][client:abc][timestamp:{now}][status:superseded]\nSuperseded learning"
        mock_item_superseded.passage.id = "p4"
        mock_item_superseded.score = 0.80

        mock_client.agents.passages.search.return_value = [
            mock_item_active1, mock_item_corrected, mock_item_active2, mock_item_superseded,
        ]

        agency = Agency.objects.create(name="A", slug="search-agency")
        client = EndClient.objects.create(agency=agency, name="C", slug="search-client")

        mem = HaznMemory(
            agent_id="agent-3",
            l3_client_id=client.id,
            l2_agency_id=agency.id,
        )
        results = mem.search_memory("test query")

        # Only active results should be returned
        assert len(results) == 2
        # Verify corrected and superseded are excluded
        for r in results:
            assert "[status:corrected]" not in r["content"]
            assert "[status:superseded]" not in r["content"]

    @patch("hazn_platform.core.memory.get_letta_client")
    def test_search_memory_respects_limit(self, mock_get_client):
        """search_memory returns at most `limit` results."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        now = datetime.now(timezone.utc).isoformat()

        # Create more active results than the limit -- List[PassageSearchResponseItem]
        mock_items = []
        for i in range(10):
            item = MagicMock()
            item.passage.text = f"[source:agent-inferred][confidence:0.9][agent:seo][client:abc][timestamp:{now}][status:active]\nLearning {i}"
            item.passage.id = f"p{i}"
            item.score = 0.95 - (i * 0.01)
            mock_items.append(item)
        mock_client.agents.passages.search.return_value = mock_items

        agency = Agency.objects.create(name="A", slug="limit-agency")
        client = EndClient.objects.create(agency=agency, name="C", slug="limit-client")

        mem = HaznMemory(
            agent_id="agent-4",
            l3_client_id=client.id,
            l2_agency_id=agency.id,
        )
        results = mem.search_memory("test query", limit=3)
        assert len(results) == 3

    @patch("hazn_platform.core.memory.get_letta_client")
    def test_search_memory_ranks_by_composite_score(self, mock_get_client):
        """search_memory uses SDK .score as similarity weight (0.6) plus recency (0.25) plus confidence (0.15)."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        now = datetime.now(timezone.utc)
        old_time = (now - timedelta(days=60)).isoformat()
        recent_time = (now - timedelta(hours=1)).isoformat()
        mid_time = (now - timedelta(days=10)).isoformat()

        # Item with low SDK score, old, low confidence
        mock_old = MagicMock()
        mock_old.passage.text = f"[source:agent-inferred][confidence:0.3][agent:seo][client:abc][timestamp:{old_time}][status:active]\nOld low-confidence"
        mock_old.passage.id = "p-old"
        mock_old.score = 0.40  # Low SDK similarity

        # Item with high SDK score, recent, high confidence
        mock_recent = MagicMock()
        mock_recent.passage.text = f"[source:user-explicit][confidence:1.0][agent:seo][client:abc][timestamp:{recent_time}][status:active]\nRecent high-confidence"
        mock_recent.passage.id = "p-recent"
        mock_recent.score = 0.95  # High SDK similarity

        # Item with medium SDK score, mid-age, mid confidence
        mock_mid = MagicMock()
        mock_mid.passage.text = f"[source:rule-extracted][confidence:0.7][agent:seo][client:abc][timestamp:{mid_time}][status:active]\nMid-age mid-confidence"
        mock_mid.passage.id = "p-mid"
        mock_mid.score = 0.70  # Medium SDK similarity

        mock_client.agents.passages.search.return_value = [mock_old, mock_recent, mock_mid]

        agency = Agency.objects.create(name="A", slug="rank-agency")
        client = EndClient.objects.create(agency=agency, name="C", slug="rank-client")

        mem = HaznMemory(
            agent_id="agent-5",
            l3_client_id=client.id,
            l2_agency_id=agency.id,
        )
        results = mem.search_memory("test query")

        # p-recent should rank first: high SDK score + recent + high confidence
        ids = [r["id"] for r in results]
        assert "p-recent" in ids
        assert "p-old" in ids
        recent_idx = ids.index("p-recent")
        old_idx = ids.index("p-old")
        assert recent_idx < old_idx, "Recent high-confidence should rank above old low-confidence"

    @patch("hazn_platform.core.memory.get_letta_client")
    def test_search_memory_returns_empty_when_no_active(self, mock_get_client):
        """search_memory returns empty list when all results are corrected/superseded."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        now = datetime.now(timezone.utc).isoformat()

        mock_corrected = MagicMock()
        mock_corrected.passage.text = f"[source:agent-inferred][confidence:0.8][agent:seo][client:abc][timestamp:{now}][status:corrected]\nCorrected"
        mock_corrected.passage.id = "p-c"
        mock_corrected.score = 0.9

        mock_client.agents.passages.search.return_value = [mock_corrected]

        agency = Agency.objects.create(name="A", slug="empty-agency")
        client = EndClient.objects.create(agency=agency, name="C", slug="empty-client")

        mem = HaznMemory(
            agent_id="agent-empty",
            l3_client_id=client.id,
            l2_agency_id=agency.id,
        )
        results = mem.search_memory("test query")
        assert results == []


@pytest.mark.django_db
class TestSearchCrossClientInsights:
    @patch("hazn_platform.core.memory.get_letta_client")
    def test_cross_client_disabled_returns_empty(self, mock_get_client):
        """search_cross_client_insights returns empty when agency flag is disabled."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient

        mock_get_client.return_value = MagicMock()

        agency = Agency.objects.create(
            name="Agency",
            slug="cross-disabled",
            tool_preferences={"cross_client_insights": False},
        )
        client = EndClient.objects.create(
            agency=agency, name="Client", slug="cross-disabled-client"
        )

        mem = HaznMemory(
            agent_id="agent-6",
            l3_client_id=client.id,
            l2_agency_id=agency.id,
        )
        results = mem.search_cross_client_insights("test query")
        assert results == []

    @patch("hazn_platform.core.memory.get_letta_client")
    def test_cross_client_enabled_queries_siblings(self, mock_get_client):
        """search_cross_client_insights queries sibling L3 client data when enabled."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient
        from hazn_platform.marketing.models import Keyword

        mock_get_client.return_value = MagicMock()

        agency = Agency.objects.create(
            name="Agency",
            slug="cross-enabled",
            tool_preferences={"cross_client_insights": True},
        )
        client_a = EndClient.objects.create(
            agency=agency, name="Client A", slug="client-a"
        )
        client_b = EndClient.objects.create(
            agency=agency, name="Client B", slug="client-b"
        )
        # Sibling keyword (from client_b)
        Keyword.objects.create(
            end_client=client_b,
            term="sibling keyword",
            search_volume=3000,
            intent="informational",
        )
        # Own keyword (from client_a) -- should be excluded
        Keyword.objects.create(
            end_client=client_a,
            term="own keyword",
            search_volume=2000,
            intent="commercial",
        )

        mem = HaznMemory(
            agent_id="agent-7",
            l3_client_id=client_a.id,
            l2_agency_id=agency.id,
        )
        results = mem.search_cross_client_insights("keyword")
        # Should include sibling data but NOT own data
        assert len(results) > 0
        for r in results:
            assert r.get("source_client") != "Client A"

    @patch("hazn_platform.core.memory.get_letta_client")
    def test_cross_client_excludes_current_client(self, mock_get_client):
        """search_cross_client_insights excludes data from the current L3 client."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient
        from hazn_platform.marketing.models import Keyword

        mock_get_client.return_value = MagicMock()

        agency = Agency.objects.create(
            name="Agency",
            slug="cross-exclude",
            tool_preferences={"cross_client_insights": True},
        )
        client = EndClient.objects.create(
            agency=agency, name="Only Client", slug="only-client"
        )
        Keyword.objects.create(
            end_client=client,
            term="my keyword",
            search_volume=1000,
            intent="informational",
        )

        mem = HaznMemory(
            agent_id="agent-8",
            l3_client_id=client.id,
            l2_agency_id=agency.id,
        )
        results = mem.search_cross_client_insights("keyword")
        # No siblings, so no results
        assert results == []

    @patch("hazn_platform.core.memory.get_letta_client")
    def test_cross_client_filters_by_finding_types(self, mock_get_client):
        """search_cross_client_insights filters by finding_types when provided."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient
        from hazn_platform.marketing.models import Audit, Keyword

        mock_get_client.return_value = MagicMock()

        agency = Agency.objects.create(
            name="Agency",
            slug="cross-filter",
            tool_preferences={"cross_client_insights": True},
        )
        client_a = EndClient.objects.create(
            agency=agency, name="Client A", slug="filter-a"
        )
        client_b = EndClient.objects.create(
            agency=agency, name="Client B", slug="filter-b"
        )
        Keyword.objects.create(
            end_client=client_b,
            term="seo term",
            search_volume=500,
            intent="informational",
        )
        Audit.objects.create(
            end_client=client_b,
            audit_type="technical_seo",
            findings={"issues": ["slow_ttfb"]},
            score=75.0,
        )

        mem = HaznMemory(
            agent_id="agent-9",
            l3_client_id=client_a.id,
            l2_agency_id=agency.id,
        )
        # Filter to only keywords
        results = mem.search_cross_client_insights("query", finding_types=["keyword"])
        for r in results:
            assert r["finding_type"] == "keyword"


@pytest.mark.django_db
class TestCorrectMemory:
    @patch("hazn_platform.core.memory.get_letta_client")
    def test_correct_memory_creates_audit_record(self, mock_get_client):
        """correct_memory writes a MemoryCorrection audit record."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient, MemoryCorrection

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Mock passage list to return the original passage
        original_passage = MagicMock()
        original_passage.id = "orig-123"
        original_passage.text = "[source:agent-inferred][confidence:0.8][status:active]\nWrong content"
        mock_client.agents.passages.list.return_value = [original_passage]

        # Mock passage creation for the corrected marker and replacement
        corrected_marker = MagicMock()
        corrected_marker.id = "corrected-marker-id"
        replacement_passage = MagicMock()
        replacement_passage.id = "replacement-456"
        mock_client.agents.passages.create.side_effect = [
            [corrected_marker],
            [replacement_passage],
        ]

        agency = Agency.objects.create(name="Agency", slug="correct-agency")
        client = EndClient.objects.create(
            agency=agency, name="Client", slug="correct-client"
        )

        mem = HaznMemory(
            agent_id="agent-10",
            l3_client_id=client.id,
            l2_agency_id=agency.id,
        )
        mem.correct_memory(
            passage_id="orig-123",
            new_content="Correct content",
            reason="Factual error",
            corrected_by="user-xyz",
        )

        # Verify audit record
        corrections = MemoryCorrection.objects.all()
        assert corrections.count() == 1
        mc = corrections.first()
        assert mc.agent_id == "agent-10"
        assert mc.original_passage_id == "orig-123"
        assert mc.original_content == "[source:agent-inferred][confidence:0.8][status:active]\nWrong content"
        assert mc.corrected_content == "Correct content"
        assert mc.reason == "Factual error"
        assert mc.corrected_by == "user-xyz"

    @patch("hazn_platform.core.memory.get_letta_client")
    def test_correct_memory_marks_original_and_creates_replacement(self, mock_get_client):
        """correct_memory soft-deletes original, creates replacement passage."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        original_passage = MagicMock()
        original_passage.id = "orig-p1"
        original_passage.text = "[source:user-explicit][confidence:1.0][status:active]\nOld content"
        mock_client.agents.passages.list.return_value = [original_passage]

        corrected_marker = MagicMock()
        corrected_marker.id = "marker-id"
        replacement = MagicMock()
        replacement.id = "repl-p1"
        mock_client.agents.passages.create.side_effect = [
            [corrected_marker],
            [replacement],
        ]

        agency = Agency.objects.create(name="A", slug="mark-agency")
        client = EndClient.objects.create(agency=agency, name="C", slug="mark-client")

        mem = HaznMemory(
            agent_id="agent-11",
            l3_client_id=client.id,
            l2_agency_id=agency.id,
        )
        mem.correct_memory(
            passage_id="orig-p1",
            new_content="New content",
            reason="Test",
            corrected_by="system",
        )

        # Verify original is deleted
        mock_client.agents.passages.delete.assert_called_once_with(
            "orig-p1", agent_id="agent-11"
        )
        # Verify two passages created: corrected marker + replacement
        assert mock_client.agents.passages.create.call_count == 2


class TestAddLearning:
    @patch("hazn_platform.core.memory.get_letta_client")
    def test_add_learning_appends_to_buffer(self, mock_get_client):
        """add_learning appends CraftLearning to _pending_learnings buffer."""
        from hazn_platform.core.memory import HaznMemory

        mock_get_client.return_value = MagicMock()

        l3_id = uuid.uuid4()
        l2_id = uuid.uuid4()
        mem = HaznMemory(agent_id="agent-12", l3_client_id=l3_id, l2_agency_id=l2_id)

        learning = CraftLearning(
            content="Client prefers bullet points",
            source=LearningSource.AGENT_INFERRED,
            confidence=0.8,
            agent_type="copywriter",
            l3_client_id=l3_id,
        )
        mem.add_learning(learning)
        assert len(mem._pending_learnings) == 1
        assert mem._pending_learnings[0] == learning

    @patch("hazn_platform.core.memory.get_letta_client")
    def test_add_multiple_learnings(self, mock_get_client):
        """add_learning accumulates multiple learnings."""
        from hazn_platform.core.memory import HaznMemory

        mock_get_client.return_value = MagicMock()

        l3_id = uuid.uuid4()
        l2_id = uuid.uuid4()
        mem = HaznMemory(agent_id="agent-13", l3_client_id=l3_id, l2_agency_id=l2_id)

        for i in range(5):
            mem.add_learning(
                CraftLearning(
                    content=f"Learning {i}",
                    source=LearningSource.AGENT_INFERRED,
                    confidence=0.5 + i * 0.1,
                    agent_type="seo",
                    l3_client_id=l3_id,
                )
            )
        assert len(mem._pending_learnings) == 5


class TestWriteCraftLearning:
    @patch("hazn_platform.core.memory.get_letta_client")
    def test_write_craft_learning_creates_passage_with_metadata(self, mock_get_client):
        """_write_craft_learning writes passage with metadata prefix including [timestamp:ISO]."""
        from hazn_platform.core.memory import HaznMemory

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_passage = MagicMock()
        mock_passage.id = "new-passage-id"
        mock_client.agents.passages.create.return_value = [mock_passage]

        l3_id = uuid.uuid4()
        l2_id = uuid.uuid4()
        mem = HaznMemory(agent_id="agent-14", l3_client_id=l3_id, l2_agency_id=l2_id)

        learning = CraftLearning(
            content="Client prefers formal tone",
            source=LearningSource.AGENT_INFERRED,
            confidence=0.85,
            agent_type="copywriter",
            l3_client_id=l3_id,
        )
        passage_id = mem._write_craft_learning(learning)

        # Verify passage was created
        mock_client.agents.passages.create.assert_called_once()
        call_kwargs = mock_client.agents.passages.create.call_args
        written_text = call_kwargs.kwargs.get("text") or call_kwargs.args[1] if len(call_kwargs.args) > 1 else None
        if written_text is None:
            # Try to get from positional args
            written_text = call_kwargs.kwargs["text"]

        # Verify metadata prefix tags
        assert "[source:agent-inferred]" in written_text
        assert "[confidence:0.85]" in written_text
        assert "[agent:copywriter]" in written_text
        assert f"[client:{l3_id}]" in written_text
        assert "[timestamp:" in written_text
        assert "[status:active]" in written_text
        assert "Client prefers formal tone" in written_text
        assert passage_id == "new-passage-id"

    @patch("hazn_platform.core.memory.get_letta_client")
    def test_write_craft_learning_with_supersedes(self, mock_get_client):
        """_write_craft_learning includes [supersedes:...] tag when present."""
        from hazn_platform.core.memory import HaznMemory

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_passage = MagicMock()
        mock_passage.id = "sup-passage-id"
        mock_client.agents.passages.create.return_value = [mock_passage]

        l3_id = uuid.uuid4()
        l2_id = uuid.uuid4()
        mem = HaznMemory(agent_id="agent-15", l3_client_id=l3_id, l2_agency_id=l2_id)

        learning = CraftLearning(
            content="Updated: formal tone preferred",
            source=LearningSource.USER_EXPLICIT,
            agent_type="copywriter",
            l3_client_id=l3_id,
            supersedes_id="old-passage-abc",
        )
        mem._write_craft_learning(learning)

        call_kwargs = mock_client.agents.passages.create.call_args
        written_text = call_kwargs.kwargs.get("text")
        assert "[supersedes:old-passage-abc]" in written_text


# ── Session Lifecycle Tests ────────────────────────────────────────


class TestCheckpointSync:
    @patch("hazn_platform.core.memory.get_letta_client")
    def test_checkpoint_sync_flushes_learnings(self, mock_get_client):
        """checkpoint_sync() flushes all _pending_learnings to Letta archival via _write_craft_learning."""
        from hazn_platform.core.memory import HaznMemory

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_passage = MagicMock()
        mock_passage.id = "p-flush"
        mock_client.agents.passages.create.return_value = [mock_passage]

        l3_id = uuid.uuid4()
        mem = HaznMemory(agent_id="agent-cs1", l3_client_id=l3_id, l2_agency_id=uuid.uuid4())

        for i in range(3):
            mem.add_learning(
                CraftLearning(
                    content=f"Learning {i}",
                    source=LearningSource.AGENT_INFERRED,
                    confidence=0.8,
                    agent_type="seo",
                    l3_client_id=l3_id,
                )
            )
        assert len(mem._pending_learnings) == 3

        mem.checkpoint_sync()

        # 3 passages should have been created
        assert mock_client.agents.passages.create.call_count == 3
        # Buffer should be empty
        assert len(mem._pending_learnings) == 0

    @patch("hazn_platform.core.memory.get_letta_client")
    def test_checkpoint_sync_noop_when_empty(self, mock_get_client):
        """checkpoint_sync() is a no-op when _pending_learnings is empty."""
        from hazn_platform.core.memory import HaznMemory

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mem = HaznMemory(agent_id="agent-cs2", l3_client_id=uuid.uuid4(), l2_agency_id=uuid.uuid4())
        mem.checkpoint_sync()

        # No Letta calls should have been made
        mock_client.agents.passages.create.assert_not_called()


class TestFailureSync:
    @patch("hazn_platform.core.memory.get_letta_client")
    def test_failure_sync_saves_with_partial_tag(self, mock_get_client):
        """failure_sync() flushes with partial_sync tag and reduced confidence."""
        from hazn_platform.core.memory import HaznMemory

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_passage = MagicMock()
        mock_passage.id = "p-fail"
        mock_client.agents.passages.create.return_value = [mock_passage]

        l3_id = uuid.uuid4()
        mem = HaznMemory(agent_id="agent-fs1", l3_client_id=l3_id, l2_agency_id=uuid.uuid4())

        mem.add_learning(
            CraftLearning(
                content="Important learning",
                source=LearningSource.AGENT_INFERRED,
                confidence=0.9,
                agent_type="seo",
                l3_client_id=l3_id,
            )
        )

        mem.failure_sync()

        # Should have written 1 passage
        assert mock_client.agents.passages.create.call_count == 1
        written_text = mock_client.agents.passages.create.call_args.kwargs["text"]
        # Confidence should be reduced: min(0.9 * 0.7, 0.7) = 0.63
        assert "[confidence:0.63]" in written_text
        # Buffer cleared
        assert len(mem._pending_learnings) == 0

    @patch("hazn_platform.core.memory.get_letta_client")
    def test_failure_sync_never_discards(self, mock_get_client):
        """failure_sync() writes even with zero-confidence learning (never discards)."""
        from hazn_platform.core.memory import HaznMemory

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_passage = MagicMock()
        mock_passage.id = "p-zero"
        mock_client.agents.passages.create.return_value = [mock_passage]

        l3_id = uuid.uuid4()
        mem = HaznMemory(agent_id="agent-fs2", l3_client_id=l3_id, l2_agency_id=uuid.uuid4())

        # CraftLearning has ge=0.0 constraint, so 0.0 is the minimum
        mem.add_learning(
            CraftLearning(
                content="Low confidence",
                source=LearningSource.AGENT_INFERRED,
                confidence=0.0,
                agent_type="seo",
                l3_client_id=l3_id,
            )
        )

        mem.failure_sync()

        # Should still write (never discard)
        assert mock_client.agents.passages.create.call_count == 1
        assert len(mem._pending_learnings) == 0


@pytest.mark.django_db
class TestWriteFinding:
    @patch("hazn_platform.core.memory.get_letta_client")
    def test_write_finding_writes_to_correct_model(self, mock_get_client):
        """write_finding() writes a keyword finding to Keyword model with provenance."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient
        from hazn_platform.marketing.models import Keyword

        mock_get_client.return_value = MagicMock()

        agency = Agency.objects.create(name="WF Agency", slug="wf-agency")
        client = EndClient.objects.create(agency=agency, name="WF Client", slug="wf-client")

        mem = HaznMemory(agent_id="agent-wf1", l3_client_id=client.id, l2_agency_id=agency.id)

        now = datetime.now(timezone.utc)
        wf_id = uuid.uuid4()
        finding = StructuredFinding(
            finding_type="keyword",
            data={
                "term": "best widgets",
                "search_volume": 5000,
                "intent": "commercial",
            },
            workflow_run_id=wf_id,
            agent_type="seo",
            session_timestamp=now,
        )

        mem.write_finding(finding)

        kw = Keyword.objects.get(term="best widgets")
        assert kw.end_client == client
        assert kw.search_volume == 5000
        assert kw.intent == "commercial"
        # Provenance in metadata JSONField
        assert "_provenance" in kw.metadata
        assert kw.metadata["_provenance"]["agent_type"] == "seo"
        assert kw.metadata["_provenance"]["workflow_run_id"] == str(wf_id)

    @patch("hazn_platform.core.memory.get_letta_client")
    def test_write_finding_provenance_in_jsonfield(self, mock_get_client):
        """write_finding() stores provenance in the correct JSONField for each model type."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient
        from hazn_platform.marketing.models import Audit, Campaign, Decision

        mock_get_client.return_value = MagicMock()

        agency = Agency.objects.create(name="PV Agency", slug="pv-agency")
        client = EndClient.objects.create(agency=agency, name="PV Client", slug="pv-client")

        mem = HaznMemory(agent_id="agent-pv1", l3_client_id=client.id, l2_agency_id=agency.id)
        now = datetime.now(timezone.utc)
        wf_id = uuid.uuid4()

        # Test audit: provenance in findings JSONField
        mem.write_finding(StructuredFinding(
            finding_type="audit",
            data={"audit_type": "technical_seo", "score": 85.0},
            workflow_run_id=wf_id, agent_type="auditor", session_timestamp=now,
        ))
        audit = Audit.objects.first()
        assert "_provenance" in audit.findings

        # Test campaign: provenance in config JSONField
        mem.write_finding(StructuredFinding(
            finding_type="campaign",
            data={"name": "Q1 Push", "campaign_type": "content", "status": "active"},
            workflow_run_id=wf_id, agent_type="strategist", session_timestamp=now,
        ))
        campaign = Campaign.objects.first()
        assert "_provenance" in campaign.config

        # Test decision: provenance in outcome JSONField
        mem.write_finding(StructuredFinding(
            finding_type="decision",
            data={"decision_type": "bid_adjust", "rationale": "CPC too high"},
            workflow_run_id=wf_id, agent_type="optimizer", session_timestamp=now,
        ))
        decision = Decision.objects.first()
        assert "_provenance" in decision.outcome

    @patch("hazn_platform.core.memory.get_letta_client")
    def test_write_finding_unknown_type_logs_warning(self, mock_get_client):
        """write_finding() logs warning for unknown finding_type but does not raise."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient

        mock_get_client.return_value = MagicMock()

        agency = Agency.objects.create(name="UK Agency", slug="uk-agency")
        client = EndClient.objects.create(agency=agency, name="UK Client", slug="uk-client")

        mem = HaznMemory(agent_id="agent-uk1", l3_client_id=client.id, l2_agency_id=agency.id)

        finding = StructuredFinding(
            finding_type="unknown_type",
            data={"foo": "bar"},
            agent_type="seo",
            session_timestamp=datetime.now(timezone.utc),
        )

        # Should not raise
        mem.write_finding(finding)


@pytest.mark.django_db
class TestEndSession:
    @patch("hazn_platform.core.memory.get_letta_client")
    def test_end_session_writes_findings_to_postgres(self, mock_get_client):
        """end_session() calls write_finding() for each StructuredFinding."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient
        from hazn_platform.marketing.models import Keyword

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        agency = Agency.objects.create(name="ES Agency", slug="es-agency")
        client = EndClient.objects.create(agency=agency, name="ES Client", slug="es-client")

        mem = HaznMemory(agent_id="agent-es1", l3_client_id=client.id, l2_agency_id=agency.id)

        now = datetime.now(timezone.utc)
        findings = [
            StructuredFinding(
                finding_type="keyword",
                data={"term": f"kw-{i}", "search_volume": 100 * i, "intent": "informational"},
                agent_type="seo",
                session_timestamp=now,
            )
            for i in range(3)
        ]

        mem.end_session(findings)

        assert Keyword.objects.count() == 3

    @patch("hazn_platform.core.memory.get_letta_client")
    def test_end_session_flushes_remaining_learnings(self, mock_get_client):
        """end_session() flushes remaining _pending_learnings to Letta archival."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_passage = MagicMock()
        mock_passage.id = "p-es"
        mock_client.agents.passages.create.return_value = [mock_passage]

        agency = Agency.objects.create(name="FL Agency", slug="fl-agency")
        client = EndClient.objects.create(agency=agency, name="FL Client", slug="fl-client")

        l3_id = client.id
        mem = HaznMemory(agent_id="agent-fl1", l3_client_id=l3_id, l2_agency_id=agency.id)

        mem.add_learning(
            CraftLearning(
                content="Session ending learning",
                source=LearningSource.AGENT_INFERRED,
                confidence=0.8,
                agent_type="seo",
                l3_client_id=l3_id,
            )
        )

        mem.end_session([])

        # Learning should have been flushed via checkpoint_sync
        assert mock_client.agents.passages.create.call_count == 1
        assert len(mem._pending_learnings) == 0

    @patch("hazn_platform.core.memory.get_letta_client")
    def test_end_session_wipes_context_block(self, mock_get_client):
        """end_session() sets active_client_context block to empty string."""
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.models import Agency, EndClient

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        agency = Agency.objects.create(name="WC Agency", slug="wc-agency")
        client = EndClient.objects.create(agency=agency, name="WC Client", slug="wc-client")

        mem = HaznMemory(agent_id="agent-wc1", l3_client_id=client.id, l2_agency_id=agency.id)
        mem.end_session([])

        # Verify block wipe call
        mock_client.agents.blocks.update.assert_called_once_with(
            "active_client_context",
            agent_id="agent-wc1",
            value="",
        )


# ── Session Get-or-Create Tests ──────────────────────────────────


class TestSessionGetOrCreate:
    @patch("hazn_platform.core.letta_client.get_letta_client")
    @patch("hazn_platform.orchestrator.session.MeteringCallback")
    @patch("hazn_platform.orchestrator.session.WorkflowRun")
    def test_agents_list_empty_triggers_create(self, mock_wfr_cls, mock_metering_cls, mock_get_client):
        """When list(client.agents.list(name=x)) returns empty list, agents.create is called."""
        from hazn_platform.orchestrator.session import WorkflowSession

        mock_letta = MagicMock()
        mock_get_client.return_value = mock_letta
        # Simulate list() conversion of SyncArrayPage returning empty list
        mock_letta.agents.list.return_value = iter([])

        mock_agent = MagicMock()
        mock_agent.id = "new-agent-id"
        mock_letta.agents.create.return_value = mock_agent

        # Set up WorkflowRun mock
        mock_run = MagicMock()
        mock_run.pk = "run-123"
        mock_wfr_cls.objects.create.return_value = mock_run
        mock_wfr_cls.Status = MagicMock()

        # Set up metering mock
        mock_metering_cls.from_agency.return_value = MagicMock()

        agency = MagicMock()
        agency.pk = "agency-pk"
        agency.slug = "test-agency"
        end_client = MagicMock()
        end_client.pk = "client-pk"
        end_client.slug = "test-client"

        session = WorkflowSession(
            workflow_name="test", agency=agency,
            end_client=end_client, triggered_by="test",
        )

        # Patch HaznMemory to avoid Django ORM calls
        with patch("hazn_platform.orchestrator.session.HaznMemory") as mock_mem_cls:
            mock_mem_instance = MagicMock()
            mock_mem_cls.return_value = mock_mem_instance
            session.load_client_context()

        # agents.create should have been called since list was empty
        mock_letta.agents.create.assert_called_once()
        assert session._letta_agent_id == "new-agent-id"

    @patch("hazn_platform.core.letta_client.get_letta_client")
    @patch("hazn_platform.orchestrator.session.MeteringCallback")
    @patch("hazn_platform.orchestrator.session.WorkflowRun")
    def test_agents_list_with_existing_uses_get_path(self, mock_wfr_cls, mock_metering_cls, mock_get_client):
        """When list(client.agents.list(name=x)) returns [agent], no create, uses existing agent.id."""
        from hazn_platform.orchestrator.session import WorkflowSession

        mock_letta = MagicMock()
        mock_get_client.return_value = mock_letta

        # Simulate list() returning a list with one existing agent
        existing_agent = MagicMock()
        existing_agent.id = "existing-agent-id"
        mock_letta.agents.list.return_value = iter([existing_agent])

        # Set up WorkflowRun mock
        mock_run = MagicMock()
        mock_run.pk = "run-456"
        mock_wfr_cls.objects.create.return_value = mock_run
        mock_wfr_cls.Status = MagicMock()

        # Set up metering mock
        mock_metering_cls.from_agency.return_value = MagicMock()

        agency = MagicMock()
        agency.pk = "agency-pk"
        agency.slug = "test-agency"
        end_client = MagicMock()
        end_client.pk = "client-pk"
        end_client.slug = "test-client"

        session = WorkflowSession(
            workflow_name="test", agency=agency,
            end_client=end_client, triggered_by="test",
        )

        # Patch HaznMemory to avoid Django ORM calls
        with patch("hazn_platform.orchestrator.session.HaznMemory") as mock_mem_cls:
            mock_mem_instance = MagicMock()
            mock_mem_cls.return_value = mock_mem_instance
            session.load_client_context()

        # agents.create should NOT have been called
        mock_letta.agents.create.assert_not_called()
        assert session._letta_agent_id == "existing-agent-id"


# ── add_learning Tool Tests ────────────────────────────────────────


class TestAddLearningTool:
    """Tests for the add_learning agent tool wrapper."""

    @pytest.fixture
    def mock_memory(self):
        """Create a mock HaznMemory instance."""
        mem = MagicMock()
        mem.add_learning = MagicMock()
        return mem

    @pytest.mark.asyncio
    async def test_add_learning_success(self, mock_memory):
        """add_learning tool should buffer a CraftLearning via HaznMemory.add_learning()."""
        from hazn_platform.orchestrator.tools.memory import add_learning as add_learning_tool
        from hazn_platform.orchestrator.tools.memory import _memory_registry

        # Get the callable handler (SDK tool vs stub)
        handler = getattr(add_learning_tool, "handler", add_learning_tool)

        client_id = str(uuid.uuid4())
        agent_id = "test-agent-1"

        # Pre-load registry with mock memory
        _memory_registry[agent_id] = mock_memory

        try:
            result = await handler({
                "agent_id": agent_id,
                "client_id": client_id,
                "content": "Client prefers formal tone",
                "source": "agent-inferred",
                "confidence": 0.85,
                "agent_type": "seo",
            })

            assert "isError" not in result
            assert "content" in result
            assert result["content"][0]["type"] == "text"
            assert "Learning recorded" in result["content"][0]["text"]

            # Verify add_learning was called with a CraftLearning
            mock_memory.add_learning.assert_called_once()
            learning_arg = mock_memory.add_learning.call_args[0][0]
            assert learning_arg.content == "Client prefers formal tone"
            assert learning_arg.confidence == 0.85
            assert learning_arg.source == LearningSource.AGENT_INFERRED
            assert learning_arg.agent_type == "seo"
        finally:
            _memory_registry.pop(agent_id, None)

    @pytest.mark.asyncio
    async def test_add_learning_default_params(self, mock_memory):
        """add_learning should default source to 'agent-inferred', confidence to 0.7, agent_type to 'unknown'."""
        from hazn_platform.orchestrator.tools.memory import add_learning as add_learning_tool
        from hazn_platform.orchestrator.tools.memory import _memory_registry

        handler = getattr(add_learning_tool, "handler", add_learning_tool)

        client_id = str(uuid.uuid4())
        agent_id = "test-agent-defaults"

        _memory_registry[agent_id] = mock_memory

        try:
            result = await handler({
                "agent_id": agent_id,
                "client_id": client_id,
                "content": "Some learning with defaults",
            })

            assert "isError" not in result
            mock_memory.add_learning.assert_called_once()
            learning_arg = mock_memory.add_learning.call_args[0][0]
            assert learning_arg.source == LearningSource.AGENT_INFERRED
            assert learning_arg.confidence == 0.7
            assert learning_arg.agent_type == "unknown"
        finally:
            _memory_registry.pop(agent_id, None)

    @pytest.mark.asyncio
    async def test_add_learning_error_handling(self, mock_memory):
        """add_learning should return isError on exception without crashing."""
        from hazn_platform.orchestrator.tools.memory import add_learning as add_learning_tool
        from hazn_platform.orchestrator.tools.memory import _memory_registry

        handler = getattr(add_learning_tool, "handler", add_learning_tool)

        client_id = str(uuid.uuid4())
        agent_id = "test-agent-error"

        mock_memory.add_learning.side_effect = RuntimeError("Letta connection failed")
        _memory_registry[agent_id] = mock_memory

        try:
            result = await handler({
                "agent_id": agent_id,
                "client_id": client_id,
                "content": "This should fail",
            })

            assert result["isError"] is True
            assert "content" in result
            assert "Error" in result["content"][0]["text"]
        finally:
            _memory_registry.pop(agent_id, None)

    def test_add_learning_in_memory_tools(self):
        """add_learning should appear in the MEMORY_TOOLS list."""
        from hazn_platform.orchestrator.tools.memory import MEMORY_TOOLS

        tool_names = [getattr(t, "name", None) for t in MEMORY_TOOLS]
        assert "add_learning" in tool_names


# ── Auto-Extract Learnings Tests ───────────────────────────────────


class TestAutoExtractLearnings:
    """Tests for the _auto_extract_learnings function in executor.py."""

    @pytest.fixture
    def client_id(self):
        return uuid.uuid4()

    def test_json_extraction(self, client_id):
        """Should extract learnings from JSON with 'learnings' key."""
        from hazn_platform.orchestrator.executor import _auto_extract_learnings

        input_text = json.dumps({
            "learnings": [
                {"content": "Client prefers short headlines"},
                {"content": "Homepage needs 2000+ words"},
            ]
        })

        result = _auto_extract_learnings(input_text, client_id, "seo")
        assert len(result) == 2
        assert result[0].content == "Client prefers short headlines"
        assert result[0].confidence == 0.6
        assert result[0].source == LearningSource.RULE_EXTRACTED
        assert result[0].agent_type == "seo"
        assert result[0].l3_client_id == client_id

    def test_text_pattern_key_finding(self, client_id):
        """Should extract learnings from 'Key finding:' text pattern."""
        from hazn_platform.orchestrator.executor import _auto_extract_learnings

        input_text = "Some analysis output.\nKey finding: Client's bounce rate is 85%\nMore text."

        result = _auto_extract_learnings(input_text, client_id, "audit")
        assert len(result) == 1
        assert "bounce rate is 85%" in result[0].content

    def test_text_pattern_i_learned_that(self, client_id):
        """Should extract learnings from 'I learned that' text pattern."""
        from hazn_platform.orchestrator.executor import _auto_extract_learnings

        input_text = "I learned that the client prefers long-form content for SEO."

        result = _auto_extract_learnings(input_text, client_id, "content")
        assert len(result) == 1
        assert "long-form content" in result[0].content

    def test_text_pattern_note_for_future(self, client_id):
        """Should extract learnings from 'Note for future:' text pattern."""
        from hazn_platform.orchestrator.executor import _auto_extract_learnings

        input_text = "Note for future: avoid using passive voice in blog posts"

        result = _auto_extract_learnings(input_text, client_id, "copywriter")
        assert len(result) == 1
        assert "passive voice" in result[0].content

    def test_multiple_patterns_in_same_text(self, client_id):
        """Should extract multiple learnings from text with multiple patterns."""
        from hazn_platform.orchestrator.executor import _auto_extract_learnings

        input_text = (
            "Key finding: Site speed is below 50 on mobile\n"
            "I learned that their CMS doesn't support lazy loading\n"
            "Note for future: recommend CDN before next audit\n"
        )

        result = _auto_extract_learnings(input_text, client_id, "audit")
        assert len(result) == 3

    def test_plain_text_returns_empty(self, client_id):
        """Should return empty list for plain text without learning signals."""
        from hazn_platform.orchestrator.executor import _auto_extract_learnings

        input_text = "The website has 45 pages indexed. The domain authority is 32."

        result = _auto_extract_learnings(input_text, client_id, "seo")
        assert result == []

    def test_soft_cap_truncates_to_20(self, client_id):
        """Should truncate to 20 learnings with warning log when exceeded."""
        from hazn_platform.orchestrator.executor import _auto_extract_learnings

        # Create JSON with 25 learnings
        learnings_list = [{"content": f"Learning {i}"} for i in range(25)]
        input_text = json.dumps({"learnings": learnings_list})

        result = _auto_extract_learnings(input_text, client_id, "seo")
        assert len(result) == 20

    def test_malformed_json_returns_empty(self, client_id):
        """Should return empty list on malformed JSON (non-fatal)."""
        from hazn_platform.orchestrator.executor import _auto_extract_learnings

        input_text = '{"learnings": [invalid json here'

        result = _auto_extract_learnings(input_text, client_id, "seo")
        assert result == []

    def test_important_insight_pattern(self, client_id):
        """Should extract learnings from 'Important insight' text pattern."""
        from hazn_platform.orchestrator.executor import _auto_extract_learnings

        input_text = "Important insight: their competitors all use schema markup"

        result = _auto_extract_learnings(input_text, client_id, "seo")
        assert len(result) == 1
        assert "schema markup" in result[0].content


# ── MemoryInspectorView Endpoint Tests ────────────────────────────


@pytest.mark.django_db()
class TestMemoryInspectorEndpoints:
    """Tests for MemoryInspectorView REST endpoints.

    Verifies:
    - Agent naming uses client--{pk} convention (not agent_type--{pk})
    - Search endpoint proxies HaznMemory.search_memory()
    - Correct endpoint creates MemoryCorrection audit record
    - List endpoint returns paginated active passages
    - Corrected/superseded passages filtered from list results
    """

    @pytest.fixture(autouse=True)
    def setup_agency_and_client(self):
        from hazn_platform.core.models import Agency, EndClient
        from hazn_platform.users.models import User

        self.agency = Agency.objects.create(name="Test Agency", slug="test-agency")
        self.client = EndClient.objects.create(
            name="Test Client", slug="test-client", agency=self.agency
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass",
            agency=self.agency,
        )

    def _get_view(self):
        from hazn_platform.workspace.views import MemoryInspectorView

        return MemoryInspectorView.as_view()

    def _make_request(self, data, action, user=None):
        from django.test import RequestFactory
        from rest_framework.test import force_authenticate

        factory = RequestFactory()
        request = factory.post(
            f"/api/workspace/memory/{action}/",
            data=data,
            content_type="application/json",
        )
        force_authenticate(request, user=user or self.user)
        return self._get_view()(request, action=action)

    # ── Agent naming tests ────────────────────────────────────────

    @patch("hazn_platform.workspace.views.HaznMemory")
    def test_agent_naming_uses_client_prefix(self, mock_memory_cls):
        """MemoryInspectorView should create HaznMemory with client--{pk} agent_id."""
        mock_instance = MagicMock()
        mock_instance.search_memory.return_value = []
        mock_memory_cls.return_value = mock_instance

        self._make_request(
            {"query": "test", "end_client_id": str(self.client.pk)},
            "search",
        )

        # Verify HaznMemory was constructed with client-- prefix
        call_kwargs = mock_memory_cls.call_args
        agent_id = call_kwargs[1]["agent_id"] if call_kwargs[1] else call_kwargs[0][0]
        assert agent_id == f"client--{self.client.pk}"
        assert "seo--" not in agent_id

    @patch("hazn_platform.workspace.views.HaznMemory")
    def test_agent_naming_ignores_agent_type_param(self, mock_memory_cls):
        """_get_agent_id should ignore agent_type and always use client-- prefix."""
        mock_instance = MagicMock()
        mock_instance.search_memory.return_value = []
        mock_memory_cls.return_value = mock_instance

        self._make_request(
            {
                "query": "test",
                "end_client_id": str(self.client.pk),
                "agent_type": "copywriter",
            },
            "search",
        )

        call_kwargs = mock_memory_cls.call_args
        agent_id = call_kwargs[1]["agent_id"] if call_kwargs[1] else call_kwargs[0][0]
        assert agent_id == f"client--{self.client.pk}"
        assert "copywriter--" not in agent_id

    # ── Search endpoint tests ─────────────────────────────────────

    @patch("hazn_platform.workspace.views.HaznMemory")
    def test_memory_search_endpoint_returns_results(self, mock_memory_cls):
        """POST /memory/search/ with valid client_id + query returns results list."""
        mock_instance = MagicMock()
        mock_instance.search_memory.return_value = [
            {"id": "p1", "content": "test learning", "score": 0.95}
        ]
        mock_memory_cls.return_value = mock_instance

        response = self._make_request(
            {"query": "SEO insights", "end_client_id": str(self.client.pk)},
            "search",
        )

        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == "p1"

    @patch("hazn_platform.workspace.views.HaznMemory")
    def test_memory_search_nonexistent_client_returns_404(self, mock_memory_cls):
        """POST /memory/search/ with non-existent client returns 404."""
        fake_id = str(uuid.uuid4())
        response = self._make_request(
            {"query": "test", "end_client_id": fake_id},
            "search",
        )
        assert response.status_code == 404

    # ── Correct endpoint tests ────────────────────────────────────

    @patch("hazn_platform.workspace.views.HaznMemory")
    def test_memory_correct_creates_audit_record(self, mock_memory_cls):
        """POST /memory/correct/ creates MemoryCorrection and returns replacement_id."""
        mock_instance = MagicMock()
        mock_instance.correct_memory.return_value = "new-passage-id"
        mock_memory_cls.return_value = mock_instance

        response = self._make_request(
            {
                "passage_id": "old-passage-id",
                "end_client_id": str(self.client.pk),
                "new_text": "Corrected content",
                "reason": "Wrong info",
            },
            "correct",
        )

        assert response.status_code == 200
        assert response.data["replacement_passage_id"] == "new-passage-id"
        mock_instance.correct_memory.assert_called_once()

    @patch("hazn_platform.workspace.views.HaznMemory")
    def test_memory_correct_default_corrected_by(self, mock_memory_cls):
        """correct endpoint should default corrected_by to 'dashboard-user'."""
        mock_instance = MagicMock()
        mock_instance.correct_memory.return_value = "new-id"
        mock_memory_cls.return_value = mock_instance

        self._make_request(
            {
                "passage_id": "pid",
                "end_client_id": str(self.client.pk),
                "new_text": "content",
                "reason": "reason",
            },
            "correct",
        )

        call_kwargs = mock_instance.correct_memory.call_args[1]
        assert call_kwargs["corrected_by"] == "dashboard-user"

    # ── List endpoint tests ───────────────────────────────────────

    @patch("hazn_platform.workspace.views.get_letta_client")
    def test_memory_list_returns_active_passages(self, mock_get_letta):
        """POST /memory/list/ returns only active passages, filtering corrected/superseded."""
        mock_client = MagicMock()
        mock_get_letta.return_value = mock_client

        # Create mix of active and corrected passages
        p_active1 = MagicMock()
        p_active1.id = "p1"
        p_active1.text = "[status:active] Learning about SEO"

        p_corrected = MagicMock()
        p_corrected.id = "p2"
        p_corrected.text = "[status:corrected] Old learning"

        p_active2 = MagicMock()
        p_active2.id = "p3"
        p_active2.text = "[status:active] Another learning"

        p_superseded = MagicMock()
        p_superseded.id = "p4"
        p_superseded.text = "[status:superseded] Replaced learning"

        mock_client.agents.passages.list.return_value = [
            p_active1, p_corrected, p_active2, p_superseded
        ]

        response = self._make_request(
            {"end_client_id": str(self.client.pk)},
            "list",
        )

        assert response.status_code == 200
        assert response.data["total"] == 2
        assert len(response.data["results"]) == 2
        result_ids = [r["id"] for r in response.data["results"]]
        assert "p1" in result_ids
        assert "p3" in result_ids
        assert "p2" not in result_ids
        assert "p4" not in result_ids

    @patch("hazn_platform.workspace.views.get_letta_client")
    def test_memory_list_pagination(self, mock_get_letta):
        """POST /memory/list/ with pagination params returns correct page slice."""
        mock_client = MagicMock()
        mock_get_letta.return_value = mock_client

        # Create 25 active passages
        passages = []
        for i in range(25):
            p = MagicMock()
            p.id = f"p{i}"
            p.text = f"[status:active] Learning {i}"
            passages.append(p)

        mock_client.agents.passages.list.return_value = passages

        response = self._make_request(
            {
                "end_client_id": str(self.client.pk),
                "page": 2,
                "page_size": 10,
            },
            "list",
        )

        assert response.status_code == 200
        assert response.data["total"] == 25
        assert len(response.data["results"]) == 10
        assert response.data["page"] == 2
        assert response.data["page_size"] == 10
        # Page 2 with page_size 10 should start at index 10
        assert response.data["results"][0]["id"] == "p10"

    @patch("hazn_platform.workspace.views.get_letta_client")
    def test_memory_list_nonexistent_client_returns_404(self, mock_get_letta):
        """POST /memory/list/ with non-existent client returns 404."""
        fake_id = str(uuid.uuid4())
        response = self._make_request(
            {"end_client_id": fake_id},
            "list",
        )
        assert response.status_code == 404

    def test_memory_invalid_action_returns_400(self):
        """POST /memory/invalid/ returns 400 Bad Request."""
        response = self._make_request(
            {"end_client_id": str(self.client.pk)},
            "invalid_action",
        )
        assert response.status_code == 400

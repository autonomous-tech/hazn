"""Integration tests for all 9 L2/L3 domain models.

Tests cover CRUD operations, FK relationships, cascade behavior,
unique constraints, and VectorField nullable handling.
"""

import uuid

import pytest
from django.db import IntegrityError

from hazn_platform.content.models import ApprovedCopy
from hazn_platform.content.models import BrandVoice
from hazn_platform.core.models import Agency
from hazn_platform.core.models import EndClient
from hazn_platform.core.models import VaultCredential
from hazn_platform.marketing.models import Audit
from hazn_platform.marketing.models import Campaign
from hazn_platform.marketing.models import Decision
from hazn_platform.marketing.models import Keyword


# ── Core App: Agency ──────────────────────────────────────────────────


@pytest.mark.django_db
class TestAgency:
    def test_create_agency_with_uuid_pk(self):
        """Agency should have a UUID primary key auto-generated."""
        agency = Agency.objects.create(
            name="Test Agency",
            slug="test-agency",
        )
        assert isinstance(agency.pk, uuid.UUID)
        assert agency.name == "Test Agency"
        assert agency.slug == "test-agency"

    def test_agency_fields_save_correctly(self):
        """All Agency fields should persist correctly."""
        agency = Agency.objects.create(
            name="Full Agency",
            slug="full-agency",
            house_style={"tone": "professional", "colors": ["#000", "#fff"]},
            methodology={"approach": "agile"},
        )
        agency.refresh_from_db()
        assert agency.house_style == {"tone": "professional", "colors": ["#000", "#fff"]}
        assert agency.methodology == {"approach": "agile"}
        assert agency.created_at is not None
        assert agency.updated_at is not None

    def test_agency_singleton_constraint(self):
        """Creating a second Agency raises ValueError (singleton)."""
        Agency.objects.create(name="First Agency", slug="first-agency")
        with pytest.raises(ValueError, match="Only one Agency"):
            Agency.objects.create(name="Second Agency", slug="second-agency")


# ── Core App: EndClient ───────────────────────────────────────────────


@pytest.mark.django_db
class TestEndClient:
    def test_create_endclient_under_agency(self):
        """EndClient should link to Agency via FK."""
        agency = Agency.objects.create(name="Agency A", slug="agency-a")
        client = EndClient.objects.create(
            agency=agency,
            name="Client X",
            slug="client-x",
        )
        assert client.agency == agency
        assert client.agency_id == agency.pk
        assert isinstance(client.pk, uuid.UUID)

    def test_cascade_delete_agency_deletes_endclients(self):
        """Deleting an Agency should cascade-delete its EndClients."""
        agency = Agency.objects.create(name="Agency Del", slug="agency-del")
        EndClient.objects.create(agency=agency, name="Client 1", slug="c1")
        EndClient.objects.create(agency=agency, name="Client 2", slug="c2")
        assert EndClient.objects.filter(agency=agency).count() == 2

        agency.delete()
        assert EndClient.objects.count() == 0

    def test_endclient_slug_unique_per_agency(self):
        """Same slug in different agencies is OK; same slug in same agency raises IntegrityError."""
        agency_a = Agency.objects.create(name="Agency A", slug="agency-a")
        agency_b = Agency.objects.create(name="Agency B", slug="agency-b")

        EndClient.objects.create(agency=agency_a, name="Client", slug="shared-slug")
        # Same slug, different agency -- should succeed
        EndClient.objects.create(agency=agency_b, name="Client", slug="shared-slug")

        # Same slug, same agency -- should fail
        with pytest.raises(IntegrityError):
            EndClient.objects.create(agency=agency_a, name="Dup", slug="shared-slug")

    def test_endclient_competitors_json(self):
        """EndClient.competitors stores a JSON list."""
        agency = Agency.objects.create(name="Agency", slug="agency-comp")
        client = EndClient.objects.create(
            agency=agency,
            name="Client",
            slug="client-comp",
            competitors=["Rival A", "Rival B"],
        )
        client.refresh_from_db()
        assert client.competitors == ["Rival A", "Rival B"]


# ── Core App: VaultCredential ─────────────────────────────────────────


@pytest.mark.django_db
class TestVaultCredential:
    def test_vault_credential_stores_path_not_secret(self):
        """VaultCredential.vault_secret_id is a string path (e.g. 'secret/data/ga4/api-key'), NOT actual secret content."""
        agency = Agency.objects.create(name="Vault Agency", slug="vault-agency")
        client = EndClient.objects.create(agency=agency, name="Vault Client", slug="vault-client")
        cred = VaultCredential.objects.create(
            end_client=client,
            service_name="ga4",
            vault_secret_id="secret/data/ga4/api-key",
        )
        cred.refresh_from_db()
        assert cred.vault_secret_id == "secret/data/ga4/api-key"
        assert len(cred.vault_secret_id) < 500  # VARCHAR(500) constraint

    def test_vault_credential_unique_per_endclient_and_service(self):
        """Same end_client + service_name combination should raise IntegrityError."""
        agency = Agency.objects.create(name="Agency", slug="agency-vc")
        client = EndClient.objects.create(agency=agency, name="Client", slug="client-vc")
        VaultCredential.objects.create(
            end_client=client,
            service_name="ga4",
            vault_secret_id="secret/data/ga4/key1",
        )
        with pytest.raises(IntegrityError):
            VaultCredential.objects.create(
                end_client=client,
                service_name="ga4",
                vault_secret_id="secret/data/ga4/key2",
            )

    def test_vault_credential_nullable_fks(self):
        """VaultCredential agency and end_client FKs are nullable."""
        cred = VaultCredential.objects.create(
            service_name="global-service",
            vault_secret_id="secret/data/global/key",
        )
        cred.refresh_from_db()
        assert cred.agency is None
        assert cred.end_client is None


# ── Marketing App: Keyword ────────────────────────────────────────────


@pytest.mark.django_db
class TestKeyword:
    def test_create_keyword_linked_to_endclient(self):
        """Keyword links to EndClient via FK."""
        agency = Agency.objects.create(name="Agency", slug="agency-kw")
        client = EndClient.objects.create(agency=agency, name="Client", slug="client-kw")
        kw = Keyword.objects.create(
            end_client=client,
            term="seo optimization",
            search_volume=1200,
            difficulty=0.65,
            intent="informational",
        )
        assert kw.end_client == client
        assert kw.term == "seo optimization"
        assert kw.search_volume == 1200
        assert kw.status == "discovered"  # default


# ── Marketing App: Audit ──────────────────────────────────────────────


@pytest.mark.django_db
class TestAudit:
    def test_create_audit_linked_to_endclient(self):
        """Audit links to EndClient via FK."""
        agency = Agency.objects.create(name="Agency", slug="agency-audit")
        client = EndClient.objects.create(agency=agency, name="Client", slug="client-audit")
        audit = Audit.objects.create(
            end_client=client,
            audit_type="technical_seo",
            findings={"issues": ["slow_ttfb", "missing_meta"]},
            score=72.5,
        )
        assert audit.end_client == client
        assert audit.audit_type == "technical_seo"
        assert audit.findings == {"issues": ["slow_ttfb", "missing_meta"]}
        assert audit.score == 72.5


# ── Marketing App: Campaign ──────────────────────────────────────────


@pytest.mark.django_db
class TestCampaign:
    def test_create_campaign_linked_to_endclient(self):
        """Campaign links to EndClient via FK."""
        agency = Agency.objects.create(name="Agency", slug="agency-camp")
        client = EndClient.objects.create(agency=agency, name="Client", slug="client-camp")
        campaign = Campaign.objects.create(
            end_client=client,
            name="Q1 Content Push",
            campaign_type="content_marketing",
            config={"budget": 5000, "channels": ["blog", "social"]},
        )
        assert campaign.end_client == client
        assert campaign.name == "Q1 Content Push"
        assert campaign.status == "draft"  # default


# ── Marketing App: Decision ──────────────────────────────────────────


@pytest.mark.django_db
class TestDecision:
    def test_create_decision_linked_to_endclient(self):
        """Decision links to EndClient via FK."""
        agency = Agency.objects.create(name="Agency", slug="agency-dec")
        client = EndClient.objects.create(agency=agency, name="Client", slug="client-dec")
        decision = Decision.objects.create(
            end_client=client,
            decision_type="keyword_selection",
            rationale="High volume, low difficulty keywords selected",
            outcome={"selected_keywords": ["seo tools", "seo guide"]},
        )
        assert decision.end_client == client
        assert decision.decision_type == "keyword_selection"

    def test_deleting_campaign_sets_decision_campaign_null(self):
        """Deleting a Campaign should SET_NULL on Decision.campaign (not cascade)."""
        agency = Agency.objects.create(name="Agency", slug="agency-dec2")
        client = EndClient.objects.create(agency=agency, name="Client", slug="client-dec2")
        campaign = Campaign.objects.create(
            end_client=client,
            name="Campaign",
            campaign_type="seo",
        )
        decision = Decision.objects.create(
            end_client=client,
            campaign=campaign,
            decision_type="budget_allocation",
            rationale="Budget optimized",
            outcome={"allocated": 3000},
        )
        campaign.delete()
        decision.refresh_from_db()
        assert decision.campaign is None


# ── Content App: BrandVoice ──────────────────────────────────────────


@pytest.mark.django_db
class TestBrandVoice:
    def test_brandvoice_vectorfield_accepts_none(self):
        """BrandVoice.embedding (VectorField) should accept None (nullable)."""
        agency = Agency.objects.create(name="Agency", slug="agency-bv")
        client = EndClient.objects.create(agency=agency, name="Client", slug="client-bv")
        bv = BrandVoice.objects.create(
            end_client=client,
            content="We speak with authority and warmth.",
            embedding=None,
        )
        bv.refresh_from_db()
        assert bv.embedding is None

    def test_unique_active_brandvoice_per_client(self):
        """Only one BrandVoice per end_client can have is_active=True."""
        agency = Agency.objects.create(name="Agency", slug="agency-bv2")
        client = EndClient.objects.create(agency=agency, name="Client", slug="client-bv2")
        BrandVoice.objects.create(
            end_client=client,
            content="Voice v1",
            is_active=True,
        )
        with pytest.raises(IntegrityError):
            BrandVoice.objects.create(
                end_client=client,
                content="Voice v2",
                is_active=True,
            )

    def test_multiple_inactive_brandvoices_allowed(self):
        """Multiple BrandVoice records with is_active=False should be allowed for the same client."""
        agency = Agency.objects.create(name="Agency", slug="agency-bv3")
        client = EndClient.objects.create(agency=agency, name="Client", slug="client-bv3")
        BrandVoice.objects.create(end_client=client, content="v1", is_active=False)
        BrandVoice.objects.create(end_client=client, content="v2", is_active=False)
        assert BrandVoice.objects.filter(end_client=client, is_active=False).count() == 2


# ── Content App: ApprovedCopy ────────────────────────────────────────


@pytest.mark.django_db
class TestApprovedCopy:
    def test_approvedcopy_vectorfield_accepts_none(self):
        """ApprovedCopy.embedding (VectorField) should accept None (nullable)."""
        agency = Agency.objects.create(name="Agency", slug="agency-ac")
        client = EndClient.objects.create(agency=agency, name="Client", slug="client-ac")
        ac = ApprovedCopy.objects.create(
            end_client=client,
            copy_type="landing_page",
            content="Hero copy for landing page.",
            embedding=None,
        )
        ac.refresh_from_db()
        assert ac.embedding is None

    def test_approvedcopy_campaign_set_null(self):
        """Deleting a Campaign should SET_NULL on ApprovedCopy.campaign."""
        agency = Agency.objects.create(name="Agency", slug="agency-ac2")
        client = EndClient.objects.create(agency=agency, name="Client", slug="client-ac2")
        campaign = Campaign.objects.create(
            end_client=client,
            name="Q2 Campaign",
            campaign_type="content",
        )
        ac = ApprovedCopy.objects.create(
            end_client=client,
            copy_type="blog_post",
            content="Blog copy.",
            campaign=campaign,
        )
        campaign.delete()
        ac.refresh_from_db()
        assert ac.campaign is None

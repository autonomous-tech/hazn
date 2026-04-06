"""Seed development data for the Hazn platform.

Creates a test agency, end-clients, brand voice, keywords, vault credential,
campaign, and decision.  Idempotent -- skips creation if seed data already
exists (checked via agency name).

Usage::

    python manage.py seed_dev_data
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from allauth.account.models import EmailAddress

from hazn_platform.content.models import BrandVoice
from hazn_platform.core.models import Agency
from hazn_platform.core.models import EndClient
from hazn_platform.core.models import VaultCredential
from hazn_platform.core.vault import store_secret
from hazn_platform.marketing.models import Campaign
from hazn_platform.marketing.models import Decision
from hazn_platform.marketing.models import Keyword


class Command(BaseCommand):
    help = "Seed development data (test agency, end-clients, keywords, etc.)"

    def handle(self, *args, **options):
        if Agency.objects.filter(name="Acme Digital Agency").exists():
            self.stdout.write(
                self.style.WARNING("Seed data already exists -- skipping.")
            )
            return

        # ── Superuser ──────────────────────────────────────────────────
        User = get_user_model()
        if not User.objects.filter(email="rizwan@autonomoustech.ca").exists():
            user = User.objects.create_superuser(
                username="rizwan",
                email="rizwan@autonomoustech.ca",
                password="test1234",
                name="Rizwan Qaiser",
            )
            EmailAddress.objects.create(
                user=user,
                email="rizwan@autonomoustech.ca",
                verified=True,
                primary=True,
            )
            self.stdout.write(self.style.SUCCESS("Created superuser: rizwan@autonomoustech.ca"))
        else:
            user = User.objects.get(email="rizwan@autonomoustech.ca")
            self.stdout.write(self.style.WARNING("Superuser already exists -- skipping."))

        # ── Agency ──────────────────────────────────────────────────────
        agency = Agency.objects.create(
            name="Acme Digital Agency",
            slug="acme-digital-agency",
            house_style={
                "tone": "professional yet approachable",
                "formatting": "short paragraphs, bullet points preferred",
            },
            methodology={
                "approach": "data-driven content marketing",
                "review_cadence": "weekly",
            },
        )

        # Link superuser to agency
        user.agency = agency
        user.save(update_fields=["agency"])

        # ── End-Clients ────────────────────────────────────────────────
        tech_startup = EndClient.objects.create(
            agency=agency,
            name="TechStartup Inc",
            slug="techstartup-inc",
            competitors=["CompetitorA", "CompetitorB", "CompetitorC"],
        )
        green_energy = EndClient.objects.create(
            agency=agency,
            name="Green Energy Co",
            slug="green-energy-co",
            competitors=["SolarRival", "WindPower Ltd"],
        )
        local_bakery = EndClient.objects.create(
            agency=agency,
            name="Local Bakery",
            slug="local-bakery",
            competitors=["BigBreadCo"],
        )

        # ── Brand Voice ────────────────────────────────────────────────
        BrandVoice.objects.create(
            end_client=tech_startup,
            content=(
                "TechStartup speaks with confidence and clarity. "
                "We use technical language when appropriate but always "
                "explain concepts for a broader audience. Our tone is "
                "innovative, forward-looking, and solution-oriented."
            ),
            version=1,
            is_active=True,
        )

        # ── Keywords ──────────────────────────────────────────────────
        keywords_data = [
            {
                "term": "cloud infrastructure monitoring",
                "search_volume": 2400,
                "difficulty": 0.72,
                "intent": "informational",
            },
            {
                "term": "devops automation tools",
                "search_volume": 1800,
                "difficulty": 0.65,
                "intent": "commercial",
            },
            {
                "term": "kubernetes best practices",
                "search_volume": 5200,
                "difficulty": 0.80,
                "intent": "informational",
            },
            {
                "term": "ci cd pipeline setup",
                "search_volume": 3100,
                "difficulty": 0.58,
                "intent": "transactional",
            },
            {
                "term": "infrastructure as code guide",
                "search_volume": 1500,
                "difficulty": 0.45,
                "intent": "informational",
            },
        ]
        for kw_data in keywords_data:
            Keyword.objects.create(end_client=tech_startup, **kw_data)

        # ── Vault Credential ─────────────────────────────────────────
        vault_path = store_secret(
            "agencies/acme-digital/ga4",
            {"api_key": "test-ga4-key-placeholder"},
        )
        VaultCredential.objects.create(
            agency=agency,
            end_client=tech_startup,
            service_name="ga4",
            vault_secret_id=vault_path,
        )

        # ── Campaign ─────────────────────────────────────────────────
        campaign = Campaign.objects.create(
            end_client=tech_startup,
            name="Q1 2026 Content Strategy",
            campaign_type="content_marketing",
            status="active",
            config={
                "target_keywords": 5,
                "content_pieces": 10,
                "channels": ["blog", "linkedin", "twitter"],
            },
        )

        # ── Decision ─────────────────────────────────────────────────
        Decision.objects.create(
            end_client=tech_startup,
            campaign=campaign,
            decision_type="keyword_selection",
            rationale=(
                "Selected 5 keywords based on search volume > 1000 "
                "and difficulty < 0.80 for Q1 content strategy."
            ),
            outcome={
                "selected_count": 5,
                "avg_volume": 2800,
                "avg_difficulty": 0.64,
            },
        )

        # ── Summary ──────────────────────────────────────────────────
        summary = (
            f"Created: 1 agency, 3 end-clients "
            f"({tech_startup.name}, {green_energy.name}, {local_bakery.name}), "
            f"1 brand voice, 5 keywords, 1 vault credential, "
            f"1 campaign, 1 decision"
        )
        self.stdout.write(self.style.SUCCESS(summary))

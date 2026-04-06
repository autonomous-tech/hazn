"""Management command for testing Letta memory lifecycle.

Runs through the full memory lifecycle: create/get Letta agent,
load client context, write a learning, search for it, correct it,
and verify the correction appears in search results.

Usage:
    python manage.py test_memory --client-id <uuid>
    python manage.py test_memory --client-id <uuid> --cleanup
"""

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Test Letta memory lifecycle: create agent, load context, write learning, search, correct"

    def add_arguments(self, parser):
        parser.add_argument(
            "--client-id",
            type=str,
            required=True,
            help="EndClient UUID to test with",
        )
        parser.add_argument(
            "--cleanup",
            action="store_true",
            help="Delete test agent after run",
        )

    def handle(self, *args, **options):
        import uuid

        from hazn_platform.core.letta_client import get_letta_client
        from hazn_platform.core.memory import HaznMemory
        from hazn_platform.core.memory_types import CraftLearning, LearningSource
        from hazn_platform.core.models import Agency, EndClient

        client_id = uuid.UUID(options["client_id"])

        # 1. Verify client exists
        try:
            end_client = EndClient.objects.get(pk=client_id)
        except EndClient.DoesNotExist:
            raise CommandError(f"EndClient {client_id} not found")

        agency = Agency.load()
        self.stdout.write(
            f"Testing with client: {end_client.name} (agency: {agency.name})"
        )

        # 2. Get or create Letta agent
        letta = get_letta_client()
        agent_name = f"client--{end_client.pk}"
        existing = list(letta.agents.list(name=agent_name))
        if existing:
            agent_id = existing[0].id
            self.stdout.write(f"  [OK] Found existing Letta agent: {agent_id}")
        else:
            agent = letta.agents.create(
                name=agent_name,
                system="Hazn client memory agent",
                memory_blocks=[{"label": "active_client_context", "value": ""}],
                tags=[f"l3:{end_client.pk}"],
            )
            agent_id = agent.id
            self.stdout.write(f"  [OK] Created Letta agent: {agent_id}")

        # 3. Load client context via HaznMemory
        memory = HaznMemory(
            agent_id=agent_id,
            l3_client_id=end_client.pk,
            l2_agency_id=agency.pk,
        )
        try:
            memory.load_client_context()
            self.stdout.write("  [OK] Client context loaded into Letta block")
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"  [WARN] Context load failed: {e}")
            )

        # 4. Write a test learning
        learning = CraftLearning(
            content="Test learning from test_memory command -- safe to delete",
            source=LearningSource.AGENT_INFERRED,
            confidence=0.75,
            agent_type="test",
            l3_client_id=end_client.pk,
        )
        memory.add_learning(learning)
        memory.checkpoint_sync()
        self.stdout.write("  [OK] Test learning written to archival")

        # 5. Search for the learning
        results = memory.search_memory("test_memory command", limit=5)
        if results:
            self.stdout.write(f"  [OK] Search returned {len(results)} results")
            for r in results:
                self.stdout.write(
                    f"       - score={r['score']} id={r['id']}"
                )
        else:
            self.stdout.write(
                self.style.WARNING("  [WARN] Search returned no results")
            )

        # 6. Correct the first result (if any)
        if results:
            passage_id = results[0]["id"]
            replacement_id = memory.correct_memory(
                passage_id=passage_id,
                new_content="Corrected test learning -- safe to delete",
                reason="test_memory management command verification",
                corrected_by="test_memory_command",
            )
            self.stdout.write(
                f"  [OK] Corrected passage {passage_id} -> {replacement_id}"
            )

            # 7. Verify correction in search
            results_after = memory.search_memory(
                "corrected test learning", limit=5
            )
            corrected_found = any(
                "Corrected test learning" in r.get("content", "")
                for r in results_after
            )
            if corrected_found:
                self.stdout.write(
                    "  [OK] Correction verified in search results"
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "  [WARN] Correction not found in search"
                    )
                )
        else:
            self.stdout.write("  [SKIP] No results to correct")

        # 8. Cleanup if requested
        if options["cleanup"]:
            try:
                letta.agents.delete(agent_id)
                self.stdout.write(f"  [OK] Deleted test agent {agent_id}")
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"  [WARN] Cleanup failed: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS("\nMemory lifecycle test complete.")
        )

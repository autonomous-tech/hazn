"""Validate Letta server connectivity and operations.

Creates a test agent, inserts an archival passage, searches for it,
then cleans up.  Useful for verifying the Letta integration works
end-to-end without running the full test suite.

Usage::

    python manage.py validate_letta
"""

from django.core.management.base import BaseCommand

from hazn_platform.core.letta_client import get_letta_client


class Command(BaseCommand):
    help = "Validate Letta server connectivity and archival memory operations"

    def handle(self, *args, **options):
        self.stdout.write("Connecting to Letta server...")
        client = get_letta_client()

        # Verify connectivity
        agents = list(client.agents.list())
        self.stdout.write(f"  Connected. Found {len(agents)} existing agent(s).")

        # Create test agent
        self.stdout.write("Creating test agent 'hazn-test-agent'...")
        agent = client.agents.create(
            name="hazn-test-agent",
            model="openai/gpt-4o-mini",
            embedding="openai/text-embedding-ada-002",
            memory_blocks=[
                {
                    "label": "persona",
                    "value": "I am a test agent for validating Hazn Letta integration.",
                },
                {
                    "label": "human",
                    "value": "A developer testing the Hazn platform.",
                },
            ],
            include_base_tools=False,
        )
        self.stdout.write(f"  Agent created: {agent.id}")

        # Insert archival passage
        passage_text = "Test archival memory passage for Hazn validation"
        self.stdout.write(f"Inserting archival passage: '{passage_text}'...")
        client.agents.passages.create(
            agent_id=agent.id,
            text=passage_text,
        )
        self.stdout.write("  Passage inserted.")

        # Search archival memory
        self.stdout.write("Searching archival memory for 'Hazn validation'...")
        results = client.agents.passages.search(
            agent_id=agent.id,
            query="Hazn validation",
        )
        self.stdout.write(f"  Found {results.count} search result(s).")

        # Clean up
        self.stdout.write(f"Deleting test agent {agent.id}...")
        client.agents.delete(agent.id)
        self.stdout.write("  Agent deleted.")

        self.stdout.write(
            self.style.SUCCESS(
                "Letta validation PASSED: agent creation, archival insert, "
                "search, and cleanup all succeeded."
            )
        )

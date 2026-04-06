"""Data migration: update any WorkflowRun rows with status='blocked' to 'failed'.

The BLOCKED status was removed from WorkflowRun.Status enum (HITL feature
deleted in Phase 2). This migration ensures no orphaned rows reference
the deleted status value.
"""

from django.db import migrations


def migrate_blocked_to_failed(apps, schema_editor):
    WorkflowRun = apps.get_model("orchestrator", "WorkflowRun")
    updated = WorkflowRun.objects.filter(status="blocked").update(status="failed")
    if updated:
        print(f"  Migrated {updated} WorkflowRun rows from 'blocked' to 'failed'")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("orchestrator", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(migrate_blocked_to_failed, noop),
    ]

# StreamField & Wagtail Migrations

## Table of Contents
1. Why Wagtail Migrations Are Different
2. Safe Changes (No Migration Needed)
3. Changes Requiring Data Migrations
4. StreamField Block Rename Pattern
5. Adding Required Fields to Existing StructBlocks
6. Removing a Block Type
7. Splitting a Block Into Two
8. Page Model Field Changes
9. Testing Migrations
10. Production Migration Checklist

---

## 1. Why Wagtail Migrations Are Different

StreamField data is stored as JSON in the database. Django schema migrations handle model-level changes, but **block structure changes require data migrations** to transform existing JSON content. Skipping a data migration leaves the admin broken for pages with old data — editors can't save, and the API may return malformed responses.

Rule: any time you change a block's structure, field names, or type, write a data migration.

---

## 2. Safe Changes (No Migration Needed)

These changes are safe — existing data still deserves and renders:
- Adding a new **optional** field to a StructBlock (with `required=False` and a default)
- Adding a new block type to a StreamBlock or StreamField (existing data has no instances of it — fine)
- Changing `help_text`, `label`, or `icon` on any block
- Changing a block's template
- Changing validators (won't affect stored data)
- Reordering blocks in a StreamBlock definition (cosmetic only)

---

## 3. Changes Requiring Data Migrations

These WILL break existing content without a data migration:
- Renaming a block type (stored as `block_type` in JSON)
- Renaming a field inside a StructBlock
- Making an optional field required
- Changing a field type (e.g. CharBlock → RichTextBlock)
- Splitting one block into two
- Removing a block type that has existing instances
- Moving a field from one StructBlock to another

---

## 4. StreamField Block Rename Pattern

Scenario: renaming `hero_block` to `page_hero` in production data.

```python
# migrations/0005_rename_hero_block.py
import json
from django.db import migrations

def rename_hero_block(apps, schema_editor):
    BlogPostPage = apps.get_model('blog', 'BlogPostPage')
    for page in BlogPostPage.objects.all():
        changed = False
        new_body = []
        for block in page.body.stream_data:
            if block['type'] == 'hero_block':
                block = {**block, 'type': 'page_hero'}
                changed = True
            new_body.append(block)
        if changed:
            page.body = json.dumps(new_body)
            page.save(update_fields=['body'])

class Migration(migrations.Migration):
    dependencies = [('blog', '0004_...')]

    operations = [
        migrations.RunPython(rename_hero_block, migrations.RunPython.noop),
    ]
```

Always import `json` at the top of the migration file. Always use `stream_data` (raw list), not `stream_block` (processed). Always `save(update_fields=['body'])` to avoid touching other fields.

---

## 5. Adding Required Fields to Existing StructBlocks

Wrong approach: add `required=True` field directly — existing blocks in DB have no value, admin breaks.

Right approach:
1. Add field as `required=False` with a sensible default
2. Write data migration to backfill the value
3. (Optional) make required=True after all data is backfilled

```python
# Step 1: Add as optional
class StatBlock(StructBlock):
    value = CharBlock()
    label = CharBlock()
    source = CharBlock(required=False, default='')  # ← safe

# Step 2: Backfill in data migration
def backfill_stat_source(apps, schema_editor):
    # Query pages with stats_block and set source='' where missing
    ...
```

---

## 6. Removing a Block Type

Never hard-delete a block type that has existing instances in production. Sequence:

1. Mark as deprecated in code: add a comment, stop offering it in the Wagtail admin (set `group='_deprecated'` or remove from StreamField definition)
2. Write a data migration to convert existing instances to the replacement block type
3. Verify zero instances remain: `Page.objects.filter(body__contains='"type": "old_block"').count()`
4. Remove from codebase

---

## 7. Splitting a Block Into Two

Scenario: `content_block` (heading + body) → `heading_block` + `rich_text_block`

```python
import json
from uuid import uuid4

def split_content_block(apps, schema_editor):
    Page = apps.get_model('cms', 'ContentPage')
    for page in Page.objects.all():
        new_blocks = []
        for block in page.body.stream_data:
            if block['type'] == 'content_block':
                # Split into two blocks
                new_blocks.append({'type': 'heading_block', 'value': block['value']['heading'], 'id': str(uuid4())})
                new_blocks.append({'type': 'rich_text_block', 'value': block['value']['body'], 'id': str(uuid4())})
            else:
                new_blocks.append(block)
        page.body = json.dumps(new_blocks)
        page.save(update_fields=['body'])
```

Always generate new UUIDs for split blocks (`from uuid import uuid4`).

---

## 8. Page Model Field Changes

Standard Django migration patterns apply, plus:
- Adding a ForeignKey to an image: `null=True, blank=True` first, backfill, then optionally remove null
- Changing a RichTextField to a StreamField: requires a data migration to wrap existing HTML in a `rich_text` block
- Never rename a `slug` field without updating all internal links

---

## 9. Testing Migrations

```python
# In tests/test_migrations.py
from wagtail.test.utils import WagtailPageTestCase

class MigrationTestCase(WagtailPageTestCase):
    def test_all_pages_render_after_migration(self):
        from wagtail.models import Page
        for page in Page.objects.live().specific():
            if hasattr(page, 'body'):
                # Accessing .stream_data should not raise
                _ = page.body.stream_data
```

Run migration tests against a copy of production data before deploying.

---

## 10. Production Migration Checklist

- [ ] Tested migration on a production data dump locally
- [ ] `python manage.py migrate --plan` reviewed — no unexpected changes
- [ ] Backup taken immediately before migration
- [ ] Migration run during low-traffic window
- [ ] Verified page renders in admin post-migration
- [ ] Verified API response is valid JSON post-migration
- [ ] Rolled back plan documented (reverse migration or restore from backup)

# Wagtail Import Reference

This document covers the Django management command that imports blog post JSON files (produced by the `seo-blog-writer` skill) into a Wagtail CMS instance.

---

## Overview

The `import_blog_post` management command reads a `{slug}-wagtail.json` file and creates a `BlogPostPage` under the site's `BlogIndexPage`. It handles:

- Creating or finding the parent `BlogIndexPage`
- Mapping all page fields (title, slug, SEO fields, metadata)
- Importing the StreamField `body` blocks
- Creating tags if they don't exist
- Creating categories if they don't exist (by slug)
- Skipping the featured image (images must be uploaded separately via the Wagtail admin)
- Saving the page as a draft (live publishing is a manual step)

---

## Management Command

Place this file at `blog/management/commands/import_blog_post.py` in your Django app.

```python
import json
import sys
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from wagtail.models import Page, Site

# Adjust these imports to match your project's app structure
from blog.models import BlogIndexPage, BlogPostPage, BlogCategory


class Command(BaseCommand):
    help = "Import a blog post from a wagtail JSON file produced by the seo-blog-writer skill."

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            help="Path to the {slug}-wagtail.json file to import.",
        )
        parser.add_argument(
            "--parent-slug",
            type=str,
            default="blog",
            help="Slug of the BlogIndexPage to attach the post to (default: 'blog').",
        )
        parser.add_argument(
            "--publish",
            action="store_true",
            default=False,
            help="Publish the page immediately instead of saving as draft.",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            default=False,
            help="Overwrite an existing page with the same slug.",
        )

    def handle(self, *args, **options):
        json_path = Path(options["json_file"])
        if not json_path.exists():
            raise CommandError(f"File not found: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Validate format
        if data.get("import_format") != "wagtail_blog_post":
            raise CommandError(
                "Invalid import format. Expected import_format='wagtail_blog_post'."
            )

        page_data = data.get("page", {})
        slug = page_data.get("slug")
        if not slug:
            raise CommandError("JSON missing required field: page.slug")

        # Find parent BlogIndexPage
        parent_slug = options["parent_slug"]
        try:
            parent_page = BlogIndexPage.objects.get(slug=parent_slug)
        except BlogIndexPage.DoesNotExist:
            raise CommandError(
                f"No BlogIndexPage found with slug='{parent_slug}'. "
                "Create one in the Wagtail admin first, or pass --parent-slug."
            )

        # Check for existing page
        existing = BlogPostPage.objects.filter(slug=slug).first()
        if existing:
            if not options["overwrite"]:
                raise CommandError(
                    f"A page with slug='{slug}' already exists (id={existing.pk}). "
                    "Use --overwrite to replace it."
                )
            self.stdout.write(f"Overwriting existing page: {slug} (id={existing.pk})")
            existing.delete()

        # Build StreamField body
        body_data = page_data.get("body", [])

        # Resolve publish_date
        publish_date_raw = page_data.get("publish_date")
        if publish_date_raw:
            try:
                publish_date = date.fromisoformat(publish_date_raw)
            except ValueError:
                self.stdout.write(
                    self.style.WARNING(
                        f"Could not parse publish_date '{publish_date_raw}', using today."
                    )
                )
                publish_date = date.today()
        else:
            publish_date = date.today()

        # Create page instance
        post = BlogPostPage(
            title=page_data.get("title", "Untitled"),
            slug=slug,
            seo_title=page_data.get("seo_title", ""),
            search_description=page_data.get("search_description", ""),
            intro=page_data.get("intro", ""),
            author=page_data.get("author", ""),
            publish_date=publish_date,
            canonical_url=page_data.get("canonical_url", ""),
            schema_type=page_data.get("schema_type", "Article"),
            body=json.dumps(body_data),  # StreamField accepts JSON string or list
        )

        # Add page to the tree
        parent_page.add_child(instance=post)

        # Handle tags
        tags = page_data.get("tags", [])
        if tags:
            for tag_name in tags:
                post.tags.add(tag_name)
            self.stdout.write(f"  Tags added: {', '.join(tags)}")

        # Handle categories (create if not exist)
        category_slugs = page_data.get("categories", [])
        if category_slugs:
            for cat_slug in category_slugs:
                category, created = BlogCategory.objects.get_or_create(
                    slug=cat_slug,
                    defaults={"name": cat_slug.replace("-", " ").title()},
                )
                post.categories.add(category)
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"  Created new category: {cat_slug}")
                    )
                else:
                    self.stdout.write(f"  Category linked: {cat_slug}")

        # Schema markup (stored as JSON field)
        schema_markup = page_data.get("schema_markup")
        if schema_markup and hasattr(post, "schema_markup"):
            post.schema_markup = schema_markup

        # Save and optionally publish
        if options["publish"]:
            post.save_revision().publish()
            self.stdout.write(
                self.style.SUCCESS(f"✓ Published: '{post.title}' at /{post.slug}/")
            )
        else:
            post.save_revision()
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Saved as draft: '{post.title}' (slug: {post.slug})"
                )
            )

        # Note: featured_image is skipped — upload images via Wagtail admin
        if page_data.get("featured_image"):
            self.stdout.write(
                self.style.WARNING(
                    "  ⚠ featured_image was specified in JSON but skipped. "
                    "Upload the image via the Wagtail admin and assign it manually."
                )
            )
```

---

## Setup

### 1. Create the management command directory

```bash
mkdir -p blog/management/commands
touch blog/management/__init__.py
touch blog/management/commands/__init__.py
```

### 2. Save the command file

Place the code above at:
```
blog/management/commands/import_blog_post.py
```

### 3. Verify your app is in `INSTALLED_APPS`

```python
# settings.py
INSTALLED_APPS = [
    ...
    "blog",
    ...
]
```

---

## Prerequisites

### Parent page must exist

The import command looks for a `BlogIndexPage` with a specific slug (default: `blog`). Create this page in the Wagtail admin before running imports:

1. Go to **Pages** in the Wagtail admin
2. Add a child page under your site root
3. Choose **Blog Index Page**
4. Set the slug to `blog` (or your preferred slug)
5. Publish it

Alternatively, pass a custom parent slug:
```bash
python manage.py import_blog_post content/blog/my-post-wagtail.json --parent-slug news
```

### BlogCategory model

The command expects a `BlogCategory` model with `name` and `slug` fields. Typical setup:

```python
# blog/models.py
from django.db import models

class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Blog Categories"

    def __str__(self):
        return self.name
```

If your model differs, adjust the `get_or_create` call in the command accordingly.

### Images

The management command **skips images**. The `featured_image` FK expects a `wagtailimages.Image` instance that must already exist in the media library. Workflow:

1. Upload the featured image via **Images** in the Wagtail admin (or via the API)
2. Note the image ID
3. After import, open the draft page in the admin and assign the image manually

For automated image import, use the Wagtail Images API or `wagtail.images.models.Image.objects.create()` with an open file handle before running this command.

---

## Usage

### Basic import (saves as draft)

```bash
python manage.py import_blog_post content/blog/my-post-wagtail.json
```

### Import and publish immediately

```bash
python manage.py import_blog_post content/blog/my-post-wagtail.json --publish
```

### Import under a custom parent page slug

```bash
python manage.py import_blog_post content/blog/my-post-wagtail.json --parent-slug insights
```

### Overwrite an existing page

```bash
python manage.py import_blog_post content/blog/my-post-wagtail.json --overwrite
```

### Batch import (shell loop)

```bash
for f in content/blog/*-wagtail.json; do
  python manage.py import_blog_post "$f"
done
```

---

## Expected Output

```
  Tags added: seo, content-marketing, b2b
  Created new category: marketing
  Category linked: seo
✓ Saved as draft: 'What Is Answer Engine Optimization?' (slug: what-is-aeo)
```

Or with `--publish`:

```
✓ Published: 'What Is Answer Engine Optimization?' at /blog/what-is-aeo/
```

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `No BlogIndexPage found with slug='blog'` | Parent page doesn't exist | Create a BlogIndexPage in the Wagtail admin first |
| `A page with slug='...' already exists` | Duplicate slug | Use `--overwrite` or change the slug in the JSON |
| `Invalid import format` | Wrong JSON file passed | Ensure the file has `"import_format": "wagtail_blog_post"` |
| Tags not appearing | Tags app not set up | Ensure `taggit` and `modelcluster` are in `INSTALLED_APPS` |
| StreamField validation errors | Block types mismatch | Verify the block type names in the JSON match the `StreamField` definition in your `BlogPostPage` model |

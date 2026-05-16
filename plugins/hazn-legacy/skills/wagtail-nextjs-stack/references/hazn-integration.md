# Hazn Framework Integration

How the Django + Wagtail stack integrates with Hazn workflows, skills, and content pipelines.

---

## Table of Contents

1. [Standard Page Type Hierarchy](#1-standard-page-type-hierarchy)
2. [CaseStudyPage Model](#2-casestudypage-model)
3. [Import case-study.json into Wagtail](#3-import-case-studyjson-into-wagtail)
4. [BlogPostPage Model](#4-blogpostpage-model)
5. [Import seo-blog-writer Markdown into Wagtail](#5-import-seo-blog-writer-markdown-into-wagtail)
6. [Full Import Management Command](#6-full-import-management-command)

---

## 1. Standard Page Type Hierarchy

Every Autonomous Technologies Wagtail project uses this hierarchy. Don't deviate without a reason.

```
Page (Wagtail root)
└── BasePage (abstract, in content/models.py)
    │
    ├── HomePage
    │   └── slug: "home" — root of the site
    │
    ├── MarketingPage
    │   └── General marketing pages (About, Services, Pricing, Contact)
    │   └── StreamField body using MARKETING_STREAM_BLOCKS
    │
    ├── CaseStudyIndexPage
    │   └── slug: "case-studies"
    │   └── Lists all CaseStudyPage children
    │   └── Filterable by industry/service tag
    │
    ├── CaseStudyPage
    │   └── Maps 1:1 to case-study.json schema
    │   └── Importable via import_case_study management command
    │
    ├── BlogIndexPage
    │   └── slug: "blog"
    │   └── Paginated listing of BlogPostPage children
    │
    └── BlogPostPage
        └── Maps to seo-blog-writer markdown output
        └── Importable via import_blog_post management command
```

---

## 2. CaseStudyPage Model

Maps directly to the `case-study.json` schema from the `case-study` skill.

```python
# case_studies/models.py
from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import (
    FieldPanel, MultiFieldPanel, TabbedInterface, ObjectList
)
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.search import index
from wagtail.blocks import (
    StructBlock, CharBlock, TextBlock, ListBlock, URLBlock
)
from content.models import BasePage


class MetricBlock(StructBlock):
    value = CharBlock(label="Metric value", help_text='e.g. "40%", "$2M", "3x"')
    label = CharBlock(label="Metric label", help_text='e.g. "Conversion rate increase"')

    class Meta:
        label = "Metric"


class CaseStudyPage(BasePage):
    """
    A single case study page. Maps to case-study.json from the case-study skill.
    
    Import via: python manage.py import_case_study case-study.json
    """

    # ─── Client metadata ─────────────────────────────────────────────────────
    client_name = models.CharField(
        max_length=100,
        help_text="Client's public-facing company name",
        verbose_name="Client name",
    )
    industry = models.CharField(
        max_length=100,
        blank=True,
        help_text="Industry or sector, e.g. 'E-commerce', 'SaaS', 'Healthcare'",
    )
    services = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated services delivered, e.g. 'Analytics, Attribution, Conversion'",
    )
    project_date = models.DateField(
        null=True,
        blank=True,
        help_text="When was the project completed? (Month/Year is fine — set day to 01)",
    )
    client_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Client logo (SVG preferred, or transparent PNG min 300px wide)",
        verbose_name="Client logo",
    )
    client_url = models.URLField(
        blank=True,
        help_text="Client's website URL (optional — only if publicly visible)",
    )

    # ─── Hero ────────────────────────────────────────────────────────────────
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Hero image — 16:9 landscape, min 1920×1080px",
        verbose_name="Hero image",
    )
    tagline = models.CharField(
        max_length=160,
        blank=True,
        help_text="One-sentence case study summary for listings and sharing",
    )

    # ─── Metrics ─────────────────────────────────────────────────────────────
    metrics = StreamField(
        [("metric", MetricBlock())],
        blank=True,
        use_json_field=True,
        help_text="3–5 key outcome metrics. These appear in the metrics strip.",
        verbose_name="Outcome metrics",
    )

    # ─── Content sections ────────────────────────────────────────────────────
    challenge_heading = models.CharField(
        max_length=120,
        default="The challenge",
        help_text="Section heading for the Challenge section",
    )
    challenge_body = models.TextField(
        help_text="The problem or challenge the client faced. 2–4 paragraphs.",
        verbose_name="Challenge",
    )

    solution_heading = models.CharField(
        max_length=120,
        default="Our solution",
        help_text="Section heading for the Solution section",
    )
    solution_body = models.TextField(
        help_text="What Autonomous Technologies built/delivered. 2–4 paragraphs.",
        verbose_name="Solution",
    )
    solution_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Solution section image — 16:9 landscape",
    )

    outcome_heading = models.CharField(
        max_length=120,
        default="The outcome",
        help_text="Section heading for the Outcome section",
    )
    outcome_body = models.TextField(
        help_text="Results and impact. Lead with numbers. 2–4 paragraphs.",
        verbose_name="Outcome",
    )
    outcome_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Outcome section image — 16:9 landscape",
    )

    # ─── Testimonial ─────────────────────────────────────────────────────────
    testimonial_quote = models.TextField(
        blank=True,
        help_text="Client testimonial quote. Use their exact words.",
    )
    testimonial_author = models.CharField(
        max_length=100,
        blank=True,
        help_text="Testimonial author full name",
    )
    testimonial_role = models.CharField(
        max_length=120,
        blank=True,
        help_text="Author's job title and company",
    )
    testimonial_photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Author headshot (square, min 200×200px)",
    )

    # ─── Tags ────────────────────────────────────────────────────────────────
    tags = models.CharField(
        max_length=300,
        blank=True,
        help_text="Comma-separated tags for filtering, e.g. 'shopify,analytics,attribution'",
    )

    # ─── Permissions ─────────────────────────────────────────────────────────
    is_featured = models.BooleanField(
        default=False,
        help_text="Show in the 'Featured case studies' section on the homepage",
    )
    is_public = models.BooleanField(
        default=True,
        help_text="Uncheck to hide from public listings (still accessible via direct URL)",
    )

    # ─── Page constraints ────────────────────────────────────────────────────
    subpage_types = []
    parent_page_types = ["case_studies.CaseStudyIndexPage"]

    # ─── Admin panels ────────────────────────────────────────────────────────
    content_panels = [
        FieldPanel("title"),
        FieldPanel("tagline"),
        FieldPanel("hero_image"),
        FieldPanel("metrics"),
        MultiFieldPanel(
            [FieldPanel("challenge_heading"), FieldPanel("challenge_body")],
            heading="Challenge section",
        ),
        MultiFieldPanel(
            [FieldPanel("solution_heading"), FieldPanel("solution_body"), FieldPanel("solution_image")],
            heading="Solution section",
        ),
        MultiFieldPanel(
            [FieldPanel("outcome_heading"), FieldPanel("outcome_body"), FieldPanel("outcome_image")],
            heading="Outcome section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("testimonial_quote"),
                FieldPanel("testimonial_author"),
                FieldPanel("testimonial_role"),
                FieldPanel("testimonial_photo"),
            ],
            heading="Testimonial",
        ),
    ]

    metadata_panels = [
        FieldPanel("client_name"),
        FieldPanel("client_logo"),
        FieldPanel("client_url"),
        FieldPanel("industry"),
        FieldPanel("services"),
        FieldPanel("project_date"),
        FieldPanel("tags"),
        FieldPanel("is_featured"),
        FieldPanel("is_public"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading="Content"),
        ObjectList(metadata_panels, heading="Client details"),
        ObjectList(BasePage.promote_panels, heading="SEO & social"),
        ObjectList(Page.settings_panels, heading="Settings"),
    ])

    # ─── Search ──────────────────────────────────────────────────────────────
    search_fields = BasePage.search_fields + [
        index.SearchField("challenge_body", boost=2),
        index.SearchField("solution_body", boost=2),
        index.SearchField("outcome_body"),
        index.SearchField("client_name", boost=3),
        index.FilterField("industry"),
        index.FilterField("is_featured"),
        index.FilterField("is_public"),
    ]

    # ─── API fields ──────────────────────────────────────────────────────────
    api_fields = BasePage.api_fields + [
        APIField("client_name"),
        APIField("industry"),
        APIField("services"),
        APIField("project_date"),
        APIField("client_url"),
        APIField("tagline"),
        APIField("tags"),
        APIField("is_featured"),
        APIField("metrics"),
        APIField("challenge_heading"),
        APIField("challenge_body"),
        APIField("solution_heading"),
        APIField("solution_body"),
        APIField("outcome_heading"),
        APIField("outcome_body"),
        APIField("testimonial_quote"),
        APIField("testimonial_author"),
        APIField("testimonial_role"),
        APIField("hero_image", serializer=ImageRenditionField("fill-1920x1080")),
        APIField("client_logo", serializer=ImageRenditionField("width-300")),
        APIField("solution_image", serializer=ImageRenditionField("fill-1200x675")),
        APIField("outcome_image", serializer=ImageRenditionField("fill-1200x675")),
        APIField("testimonial_photo", serializer=ImageRenditionField("fill-200x200")),
    ]

    class Meta:
        verbose_name = "Case study"
        verbose_name_plural = "Case studies"
```

---

## 3. Import case-study.json into Wagtail

The `case-study` skill outputs a `case-study.json` file. This management command imports it into Wagtail.

### case-study.json schema (from case-study skill)

```json
{
  "model": "case_studies.CaseStudy",
  "slug": "client-name-project-type",
  "title": "Project Title",
  "client": {
    "name": "Client Company",
    "industry": "E-commerce",
    "url": "https://client.com"
  },
  "tags": ["shopify", "analytics"],
  "services": ["Analytics", "Attribution"],
  "project_date": "2026-01",
  "tagline": "One sentence summary.",
  "metrics": [
    {"value": "40%", "label": "Conversion rate increase"},
    {"value": "3x", "label": "ROAS improvement"}
  ],
  "sections": {
    "challenge": {
      "heading": "The challenge",
      "body": "Multi-paragraph text..."
    },
    "solution": {
      "heading": "Our solution",
      "body": "Multi-paragraph text..."
    },
    "outcome": {
      "heading": "The outcome",
      "body": "Multi-paragraph text..."
    }
  },
  "testimonial": {
    "quote": "They shipped in half the time we expected.",
    "author": "Jane Smith",
    "role": "CTO, Acme Corp"
  },
  "is_featured": false,
  "is_public": true
}
```

### Management command

```python
# case_studies/management/commands/import_case_study.py
import json
import os
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from wagtail.models import Site

from case_studies.models import CaseStudyIndexPage, CaseStudyPage


class Command(BaseCommand):
    help = "Import a case-study.json file into Wagtail as a CaseStudyPage"

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str, help="Path to case-study.json")
        parser.add_argument(
            "--publish",
            action="store_true",
            default=False,
            help="Publish the page immediately (default: save as draft)",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            default=False,
            help="Update existing page if slug already exists",
        )

    def handle(self, *args, **options):
        json_path = options["json_file"]

        if not os.path.exists(json_path):
            raise CommandError(f"File not found: {json_path}")

        with open(json_path, "r") as f:
            data = json.load(f)

        # Find or create the CaseStudyIndexPage
        try:
            index_page = CaseStudyIndexPage.objects.live().first()
            if not index_page:
                raise CommandError(
                    "No live CaseStudyIndexPage found. "
                    "Create one in Wagtail admin first, then re-run."
                )
        except CaseStudyIndexPage.DoesNotExist:
            raise CommandError("CaseStudyIndexPage not found.")

        slug = data["slug"]

        # Check for existing page
        existing = CaseStudyPage.objects.filter(slug=slug).first()
        if existing and not options["update"]:
            raise CommandError(
                f"Page with slug '{slug}' already exists. "
                f"Use --update to overwrite."
            )

        # Parse project_date
        project_date = None
        if data.get("project_date"):
            try:
                project_date = datetime.strptime(data["project_date"] + "-01", "%Y-%m-%d").date()
            except ValueError:
                self.stdout.write(self.style.WARNING(f"Could not parse project_date: {data['project_date']}"))

        # Build metrics StreamField value
        metrics_value = [
            {
                "type": "metric",
                "value": {
                    "value": m["value"],
                    "label": m["label"],
                },
            }
            for m in data.get("metrics", [])
        ]

        sections = data.get("sections", {})
        testimonial = data.get("testimonial", {})
        client = data.get("client", {})

        page_data = {
            "title": data["title"],
            "slug": slug,
            "client_name": client.get("name", data.get("client_name", "")),
            "industry": client.get("industry", data.get("industry", "")),
            "services": ", ".join(data.get("services", [])),
            "project_date": project_date,
            "client_url": client.get("url", ""),
            "tagline": data.get("tagline", ""),
            "tags": ", ".join(data.get("tags", [])),
            "is_featured": data.get("is_featured", False),
            "is_public": data.get("is_public", True),
            "metrics": json.dumps(metrics_value),
            "challenge_heading": sections.get("challenge", {}).get("heading", "The challenge"),
            "challenge_body": sections.get("challenge", {}).get("body", ""),
            "solution_heading": sections.get("solution", {}).get("heading", "Our solution"),
            "solution_body": sections.get("solution", {}).get("body", ""),
            "outcome_heading": sections.get("outcome", {}).get("heading", "The outcome"),
            "outcome_body": sections.get("outcome", {}).get("body", ""),
            "testimonial_quote": testimonial.get("quote", ""),
            "testimonial_author": testimonial.get("author", ""),
            "testimonial_role": testimonial.get("role", ""),
        }

        if existing and options["update"]:
            # Update existing page
            for key, value in page_data.items():
                setattr(existing, key, value)
            if options["publish"]:
                revision = existing.save_revision()
                revision.publish()
                self.stdout.write(self.style.SUCCESS(f"Updated and published: {slug}"))
            else:
                existing.save_revision()
                self.stdout.write(self.style.SUCCESS(f"Updated (draft): {slug}"))
        else:
            # Create new page
            page = CaseStudyPage(**page_data)
            index_page.add_child(instance=page)
            if options["publish"]:
                revision = page.save_revision()
                revision.publish()
                self.stdout.write(self.style.SUCCESS(f"Created and published: {slug}"))
            else:
                page.save_revision()
                self.stdout.write(self.style.SUCCESS(
                    f"Created as draft: {slug}\n"
                    f"View in admin: /cms/pages/{page.id}/edit/"
                ))
```

### Usage

```bash
# Import as draft (default)
python manage.py import_case_study projects/acme/case-study.json

# Import and publish immediately
python manage.py import_case_study projects/acme/case-study.json --publish

# Update existing
python manage.py import_case_study projects/acme/case-study.json --update --publish
```

---

## 4. BlogPostPage Model

Maps to the markdown output of the `seo-blog-writer` skill (frontmatter + body).

```python
# content/models.py (add alongside other page models)
from taggit.models import TaggedItemBase
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey


class BlogPostPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "content.BlogPostPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


class BlogPostPage(BasePage):
    """
    Blog post page. Import via: python manage.py import_blog_post post.md
    Maps to seo-blog-writer markdown frontmatter schema.
    """

    # ─── Metadata ────────────────────────────────────────────────────────────
    author_name = models.CharField(
        max_length=100,
        default="Autonomous Technologies",
        help_text="Author's full name as it appears on the post",
    )
    author_bio = models.TextField(
        blank=True,
        help_text="Short author bio (1–2 sentences). Optional.",
    )
    author_photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Author headshot (square)",
    )

    excerpt = models.TextField(
        blank=True,
        max_length=300,
        help_text="Blog post summary for listings and social. 1–2 sentences, under 300 chars.",
    )
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Blog hero image — 16:9, min 1200×675px",
    )
    reading_time_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Estimated reading time in minutes. Leave blank to auto-calculate (200 WPM).",
    )

    # ─── Content ─────────────────────────────────────────────────────────────
    body = StreamField(
        [
            ("rich_text", RichTextBlock()),
            ("image_with_caption", ImageWithCaptionBlock()),
            ("quote", QuoteBlock()),
            ("call_to_action", CallToActionBlock()),
            ("stats", StatsBlock()),
            ("faq", FAQBlock()),
            ("embed", EmbedBlock()),
        ],
        use_json_field=True,
        help_text="Blog post content",
    )

    # ─── Taxonomy ────────────────────────────────────────────────────────────
    tags = ClusterTaggableManager(through=BlogPostPageTag, blank=True)
    primary_keyword = models.CharField(
        max_length=100,
        blank=True,
        help_text="Primary SEO keyword this post targets. Used for internal tracking.",
    )

    # ─── Schema ──────────────────────────────────────────────────────────────
    schema_type = models.CharField(
        max_length=50,
        default="Article",
        choices=[
            ("Article", "Article"),
            ("BlogPosting", "Blog posting"),
            ("HowTo", "How-to guide"),
            ("FAQPage", "FAQ page"),
        ],
        help_text="Schema.org type for structured data",
    )

    # ─── Page constraints ────────────────────────────────────────────────────
    subpage_types = []
    parent_page_types = ["content.BlogIndexPage"]

    # ─── Admin panels ────────────────────────────────────────────────────────
    content_panels = BasePage.content_panels + [
        FieldPanel("hero_image"),
        FieldPanel("excerpt"),
        FieldPanel("body"),
    ]

    metadata_panels = [
        FieldPanel("author_name"),
        FieldPanel("author_bio"),
        FieldPanel("author_photo"),
        FieldPanel("reading_time_minutes"),
        FieldPanel("primary_keyword"),
        FieldPanel("tags"),
        FieldPanel("schema_type"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading="Content"),
        ObjectList(metadata_panels, heading="Post details"),
        ObjectList(BasePage.promote_panels, heading="SEO & social"),
        ObjectList(Page.settings_panels, heading="Settings"),
    ])

    # ─── Search ──────────────────────────────────────────────────────────────
    search_fields = BasePage.search_fields + [
        index.SearchField("body", boost=2),
        index.SearchField("excerpt", boost=3),
        index.SearchField("author_name"),
        index.FilterField("first_published_at"),
    ]

    # ─── API ─────────────────────────────────────────────────────────────────
    api_fields = BasePage.api_fields + [
        APIField("author_name"),
        APIField("excerpt"),
        APIField("body"),
        APIField("reading_time_minutes"),
        APIField("primary_keyword"),
        APIField("schema_type"),
        APIField("hero_image", serializer=ImageRenditionField("fill-1200x675")),
        APIField("author_photo", serializer=ImageRenditionField("fill-200x200")),
        # Tags serialized as list of names
        APIField("tag_names"),
    ]

    @property
    def tag_names(self):
        return list(self.tags.values_list("name", flat=True))

    @property
    def computed_reading_time(self):
        if self.reading_time_minutes:
            return self.reading_time_minutes
        # Rough estimate from body text
        body_text = " ".join(
            str(block.value) for block in self.body
            if hasattr(block, "value")
        )
        word_count = len(body_text.split())
        return max(1, word_count // 200)

    class Meta:
        verbose_name = "Blog post"
        verbose_name_plural = "Blog posts"
```

---

## 5. Import seo-blog-writer Markdown into Wagtail

The `seo-blog-writer` skill outputs `.md` files with YAML frontmatter. This command imports them.

### Expected frontmatter schema (seo-blog-writer output)

```yaml
---
title: "How to Set Up GA4 for Shopify in 2026"
slug: "ga4-shopify-setup-2026"
meta_description: "Step-by-step guide to configuring GA4 for your Shopify store..."
primary_keyword: "GA4 Shopify setup"
keywords: ["GA4", "Shopify", "analytics", "ecommerce tracking"]
author: "Autonomous Technologies"
reading_time: 8
schema_type: "HowTo"
tags: ["ga4", "shopify", "analytics"]
---
```

### Management command

```python
# content/management/commands/import_blog_post.py
import os
import re
import yaml
from django.core.management.base import BaseCommand, CommandError
from wagtail.models import Page

from content.models import BlogIndexPage, BlogPostPage
from content.blocks import RichTextBlock


class Command(BaseCommand):
    help = "Import a seo-blog-writer markdown file into Wagtail as a BlogPostPage"

    def add_arguments(self, parser):
        parser.add_argument("md_file", type=str, help="Path to the .md blog post file")
        parser.add_argument("--publish", action="store_true", default=False)
        parser.add_argument("--update", action="store_true", default=False)

    def handle(self, *args, **options):
        md_path = options["md_file"]

        if not os.path.exists(md_path):
            raise CommandError(f"File not found: {md_path}")

        with open(md_path, "r") as f:
            content = f.read()

        # Parse frontmatter
        frontmatter_match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
        if not frontmatter_match:
            raise CommandError("Invalid markdown — no YAML frontmatter found.")

        frontmatter = yaml.safe_load(frontmatter_match.group(1))
        body_md = frontmatter_match.group(2).strip()

        # Convert markdown to HTML for Wagtail RichText
        try:
            import markdown
            body_html = markdown.markdown(body_md, extensions=["extra", "codehilite"])
        except ImportError:
            raise CommandError("Install markdown: pip install markdown")

        # Find BlogIndexPage
        blog_index = BlogIndexPage.objects.live().first()
        if not blog_index:
            raise CommandError("No live BlogIndexPage found. Create one first.")

        slug = frontmatter.get("slug") or self._slugify(frontmatter["title"])

        existing = BlogPostPage.objects.filter(slug=slug).first()
        if existing and not options["update"]:
            raise CommandError(f"Post '{slug}' already exists. Use --update to overwrite.")

        # Build body StreamField
        body_value = [
            {
                "type": "rich_text",
                "value": body_html,
            }
        ]

        page_data = {
            "title": frontmatter["title"],
            "slug": slug,
            "excerpt": frontmatter.get("meta_description", ""),
            "author_name": frontmatter.get("author", "Autonomous Technologies"),
            "reading_time_minutes": frontmatter.get("reading_time"),
            "primary_keyword": frontmatter.get("primary_keyword", ""),
            "schema_type": frontmatter.get("schema_type", "Article"),
            "seo_description": frontmatter.get("meta_description", ""),
            "body": __import__("json").dumps(body_value),
        }

        tags = frontmatter.get("tags", [])

        if existing and options["update"]:
            for key, value in page_data.items():
                setattr(existing, key, value)
            existing.tags.set(*tags, tag_kwargs={"through_defaults": {}})
            if options["publish"]:
                existing.save_revision().publish()
                self.stdout.write(self.style.SUCCESS(f"Updated and published: {slug}"))
            else:
                existing.save_revision()
                self.stdout.write(self.style.SUCCESS(f"Updated as draft: {slug}"))
        else:
            page = BlogPostPage(**page_data)
            blog_index.add_child(instance=page)
            if tags:
                page.tags.set(*tags, tag_kwargs={"through_defaults": {}})
            if options["publish"]:
                page.save_revision().publish()
                self.stdout.write(self.style.SUCCESS(f"Created and published: {slug}"))
            else:
                page.save_revision()
                self.stdout.write(self.style.SUCCESS(f"Created as draft: {slug}"))

    def _slugify(self, text):
        import re
        return re.sub(r"[^a-z0-9-]", "-", text.lower().strip()).strip("-")
```

### Usage

```bash
# Import a blog post as draft
python manage.py import_blog_post content/blog/ga4-shopify-setup.md

# Import and publish
python manage.py import_blog_post content/blog/ga4-shopify-setup.md --publish

# Batch import all .md files in a directory
for f in content/blog/*.md; do
  python manage.py import_blog_post "$f" --publish
done
```

---

## 6. Full Import Management Command

For importing multiple outputs from a Hazn project directory:

```bash
# Full batch import from a Hazn project output directory
# Assumes:
#   projects/{client}/case-study.json        → CaseStudyPage
#   projects/{client}/content/blog/*.md      → BlogPostPage

# Import case study
python manage.py import_case_study projects/acme/case-study.json --publish

# Import all blog posts
for f in projects/acme/content/blog/*.md; do
  python manage.py import_blog_post "$f" --publish
done

# Rebuild search index
python manage.py update_index

# Verify imports
python manage.py shell -c "
from case_studies.models import CaseStudyPage
from content.models import BlogPostPage
print(f'Case studies: {CaseStudyPage.objects.live().count()}')
print(f'Blog posts: {BlogPostPage.objects.live().count()}')
"
```

### State tracking

After import, update `projects/{client}/state.json`:

```json
{
  "client": "acme",
  "stack": "wagtail",
  "phase": "content",
  "wagtail_imports": {
    "case_study": "acme-ecommerce-analytics",
    "blog_posts": ["ga4-shopify-setup-2026", "attribution-modeling-guide"],
    "imported_at": "2026-03-12T19:00:00Z"
  }
}
```

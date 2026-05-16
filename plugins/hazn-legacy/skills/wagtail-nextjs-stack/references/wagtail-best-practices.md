# Wagtail Best Practices

Reference for Django + Wagtail LTS projects in the Hazn framework.

---

## Table of Contents

1. [Page Model Design](#1-page-model-design)
2. [StreamField Best Practices](#2-streamfield-best-practices)
3. [Snippets vs Pages](#3-snippets-vs-pages)
4. [Wagtail Admin UX for Marketers](#4-wagtail-admin-ux-for-marketers)
5. [Search Configuration](#5-search-configuration)
6. [Images & Renditions](#6-images--renditions)
7. [Permissions](#7-permissions)
8. [Global Settings via wagtail.contrib.settings](#8-global-settings)
9. [Preview for Editors](#9-preview-for-editors)
10. [Revisions and Moderation Workflows](#10-revisions-and-moderation)

---

## 1. Page Model Design

### AbstractPage base pattern

All page types inherit from a shared `BasePage`. This ensures consistent SEO fields, OG image, and API representation across every page type — without repeating code.

```python
# content/models.py
import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.search import index
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField


class BasePage(Page):
    """
    Abstract base page. All page types inherit from this.
    Never create a BasePage directly — set abstract = True.
    """

    seo_description = models.TextField(
        blank=True,
        max_length=160,
        help_text="Meta description shown in search results. Keep under 160 characters.",
        verbose_name="SEO Description",
    )
    og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Social share image (recommended: 1200×630px). Defaults to site logo if not set.",
        verbose_name="Social Share Image",
    )

    promote_panels = Page.promote_panels + [
        MultiFieldPanel(
            [
                FieldPanel("seo_description"),
                FieldPanel("og_image"),
            ],
            heading="SEO & Social",
        ),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("seo_description"),
    ]

    api_fields = [
        APIField("seo_description"),
        APIField("og_image", serializer=ImageRenditionField("fill-1200x630")),
    ]

    class Meta:
        abstract = True
```

### Page type hierarchy (Autonomous standard)

```
Page (Wagtail root)
└── BasePage (abstract)
    ├── HomePage             — one per site, set as root page
    ├── MarketingPage        — general purpose, StreamField body
    ├── CaseStudyPage        — structured (maps to case-study.json)
    ├── BlogIndexPage        — paginated listing, no body
    ├── BlogPostPage         — article, rich body + metadata
    └── ContactPage          — form page
```

### Page routing — `subpage_types` and `parent_page_types`

Always constrain where pages can be created. This prevents editors from accidentally nesting pages in wrong locations.

```python
class BlogIndexPage(BasePage):
    subpage_types = ["content.BlogPostPage"]  # Only blog posts allowed as children
    parent_page_types = ["home.HomePage"]      # Only under HomePage


class BlogPostPage(BasePage):
    subpage_types = []                          # Blog posts are leaf nodes
    parent_page_types = ["content.BlogIndexPage"]
```

### HomePage (singleton pattern)

```python
class HomePage(BasePage):
    """Root page. Only one should exist."""

    subpage_types = [
        "content.MarketingPage",
        "content.BlogIndexPage",
        "content.ContactPage",
        "case_studies.CaseStudyIndexPage",
    ]
    parent_page_types = ["wagtailcore.Page"]  # Only root Page

    max_count = 1  # Wagtail enforces singleton
```

---

## 2. StreamField Best Practices

### use_json_field=True (Wagtail 6+)

Always set `use_json_field=True` on StreamField. This stores data as JSONB in PostgreSQL, enabling proper querying and future-proofing.

```python
body = StreamField(
    [...],
    use_json_field=True,
    blank=True,
)
```

### StructBlock vs StreamBlock

| Type | Use when | Example |
|------|----------|---------|
| `StructBlock` | A fixed group of fields (a "card", a "stat", a "CTA link") | `StatBlock(value, label)` |
| `StreamBlock` | A variable sequence of heterogeneous blocks | The page body itself |
| `ListBlock` | A repeating list of the same block type | List of testimonials |

**Rule:** Never nest `StreamBlock` inside another `StreamBlock`. Use `ListBlock` for repeating homogeneous items inside a StructBlock.

```python
# ✅ Correct — list of identical structs
class TestimonialsBlock(StructBlock):
    heading = CharBlock(label="Section heading")
    testimonials = ListBlock(
        StructBlock([
            ("quote", TextBlock(label="Quote text")),
            ("author", CharBlock(label="Author name")),
            ("role", CharBlock(label="Author role / company")),
        ]),
        label="Testimonials",
    )

# ❌ Wrong — StreamBlock inside StreamBlock
class WrongBlock(StreamBlock):
    testimonial = StreamBlock([...])  # Don't do this
```

### Block ordering in StreamBlock

Order blocks in the Wagtail chooser by frequency of use — most common first:

```python
body = StreamField(
    StreamBlock([
        ("hero", HeroBlock()),           # Most used — always first
        ("rich_text", RichTextBlock()),  # Second most common
        ("call_to_action", CallToActionBlock()),
        ("cards", CardsBlock()),
        ("testimonials", TestimonialsBlock()),
        ("stats", StatsBlock()),
        ("faq", FAQBlock()),
        ("image_with_caption", ImageWithCaptionBlock()),
        ("quote", QuoteBlock()),
        ("embed", EmbedBlock()),
        ("raw_html", RawHTMLBlock()),    # Least used — developer only
    ]),
    use_json_field=True,
)
```

### help_text on every block field

Every CharBlock, TextBlock, and ChoiceBlock that an editor touches must have a `help_text`. This is non-negotiable — editors are not developers.

```python
class HeroBlock(StructBlock):
    heading = CharBlock(
        label="Main heading",
        help_text="The primary headline. Keep under 8 words for impact.",
        max_length=80,
    )
    subheading = TextBlock(
        label="Subheading",
        help_text="Supporting text beneath the headline. 1–2 sentences.",
        required=False,
    )
    background_image = ImageChooserBlock(
        label="Background image",
        help_text="Use a high-resolution image (min 1920×1080px). Will be darkened automatically.",
        required=False,
    )
    cta_text = CharBlock(
        label="Button label",
        help_text='e.g. "Get started", "Book a call"',
        max_length=40,
        required=False,
    )
    cta_url = URLBlock(
        label="Button link",
        help_text="Full URL including https://",
        required=False,
    )
```

---

## 3. Snippets vs Pages

### Use Pages when:
- The content has its own URL (it's routable)
- Editors need to set SEO fields, slugs, publish dates
- Content participates in the page tree (can have children)
- You need revision history and scheduled publishing on the content
- Examples: Blog posts, case studies, service pages, landing pages

### Use Snippets when:
- The content is **reused across multiple pages** (no URL of its own)
- Non-routable data: testimonials, team members, navigation items, FAQs
- Global configuration that's edited rarely
- Examples: Site navigation, footer links, featured testimonials, awards

```python
# content/snippets.py
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel
from wagtail.search import index


@register_snippet
class Testimonial(models.Model):
    """Reusable testimonial — referenced from TestimonialsBlock via SnippetChooserBlock."""

    quote = models.TextField(
        help_text="The testimonial text. Use the client's own words.",
        verbose_name="Quote",
    )
    author_name = models.CharField(
        max_length=100,
        help_text="Full name of the person giving the testimonial.",
        verbose_name="Author name",
    )
    author_role = models.CharField(
        max_length=100,
        blank=True,
        help_text="Job title and company, e.g. 'Head of Marketing, Acme Corp'",
        verbose_name="Author role",
    )
    author_photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Headshot photo (square, min 200×200px)",
        verbose_name="Author photo",
    )

    panels = [
        FieldPanel("quote"),
        MultiFieldPanel(
            [FieldPanel("author_name"), FieldPanel("author_role"), FieldPanel("author_photo")],
            heading="Author",
        ),
    ]

    search_fields = [
        index.SearchField("quote"),
        index.SearchField("author_name"),
    ]

    def __str__(self):
        return f"{self.author_name} — {self.author_role}"

    class Meta:
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"
```

---

## 4. Wagtail Admin UX for Marketers

### Panel types and when to use them

| Panel | Use for |
|-------|---------|
| `FieldPanel` | Single field (text, image, boolean, etc.) |
| `MultiFieldPanel` | Group related fields with a section heading |
| `InlinePanel` | Repeating related objects (ParentalKey models) |
| `FieldPanel("body")` | StreamField (uses `StreamFieldPanel` internally in Wagtail 6+) |
| `TabbedInterface` | Separate content, settings, and SEO tabs |
| `PageChooserPanel` | Removed in Wagtail 6 — use `FieldPanel` for page chooser fields |

### Tabbed interface pattern (recommended for complex pages)

```python
from wagtail.admin.panels import TabbedInterface, ObjectList

class CaseStudyPage(BasePage):
    # ... fields ...

    content_panels = [
        FieldPanel("title"),
        FieldPanel("hero_image"),
        FieldPanel("challenge_body"),
        FieldPanel("solution_body"),
        FieldPanel("outcome_body"),
    ]

    metadata_panels = [
        FieldPanel("client_name"),
        FieldPanel("industry"),
        FieldPanel("services"),
        FieldPanel("project_date"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading="Content"),
        ObjectList(metadata_panels, heading="Project details"),
        ObjectList(BasePage.promote_panels, heading="SEO & social"),
        ObjectList(Page.settings_panels, heading="Settings"),
    ])
```

### help_text is UX copy for editors

Write help_text as if you're writing UI microcopy — because you are.

```python
# ❌ Bad help_text
help_text = "This field is for the title."

# ✅ Good help_text
help_text = "The page headline shown in hero. Keep under 8 words. Avoid punctuation."

# ✅ Good help_text with format guidance
help_text = "Enter as: 'Role, Company Name' — e.g. 'Head of Growth, Shopify'"

# ✅ Good help_text with character guidance
help_text = "Short description for search results. Maximum 160 characters."
```

### Image chooser widgets

Use `FieldPanel` with an image ForeignKey — Wagtail renders the chooser widget automatically.

```python
hero_image = models.ForeignKey(
    "wagtailimages.Image",
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name="+",
    help_text="Hero image — landscape, minimum 1920×800px. Will be cropped to 16:9.",
    verbose_name="Hero image",
)
# In panels:
FieldPanel("hero_image"),
```

### Page chooser widgets

```python
featured_case_study = models.ForeignKey(
    "wagtailcore.Page",
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name="+",
    help_text="Select a Case Study page to feature in this section.",
    verbose_name="Featured case study",
)
# In panels — Wagtail auto-renders page chooser:
FieldPanel("featured_case_study", page_type="case_studies.CaseStudyPage"),
```

### clean() validation with user-friendly messages

```python
from django.core.exceptions import ValidationError
from wagtail.admin.panels import FieldPanel

class BlogPostPage(BasePage):
    reading_time_minutes = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Estimated reading time in minutes. Leave blank to auto-calculate.",
    )

    def clean(self):
        super().clean()
        if self.reading_time_minutes and self.reading_time_minutes > 60:
            raise ValidationError({
                "reading_time_minutes": "Reading time over 60 minutes seems too long — check the value."
            })
```

---

## 5. Search Configuration

### search_fields on every page model

```python
from wagtail.search import index

class BlogPostPage(BasePage):
    body = StreamField([...], use_json_field=True)
    excerpt = models.TextField(blank=True)

    search_fields = BasePage.search_fields + [
        index.SearchField("body"),            # StreamField content is indexed
        index.SearchField("excerpt", boost=2), # boost excerpt (summary text)
        index.FilterField("first_published_at"),
        index.FilterField("live"),
    ]
```

### Wagtail search backend (PostgreSQL)

For most projects, use the PostgreSQL backend (no Elasticsearch needed):

```python
# config/settings/base.py
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}
```

After adding `search_fields`, run: `python manage.py update_index`

---

## 6. Images & Renditions

### Always use renditions — never raw image URLs

Wagtail renditions create resized/cropped versions on-demand and cache them. Never expose `image.file.url` directly.

```python
# In templates (Wagtail template tags)
{% image page.hero_image fill-1920x800-c75 as hero %}
<img src="{{ hero.url }}" alt="{{ hero.alt }}" width="{{ hero.width }}" height="{{ hero.height }}">

# In API — use ImageRenditionField
from wagtail.images.api.fields import ImageRenditionField

api_fields = [
    APIField("hero_image", serializer=ImageRenditionField("fill-1920x800")),
    # Multiple renditions for responsive:
    APIField("hero_image_mobile", serializer=ImageRenditionField("fill-768x400", source="hero_image")),
]
```

### Rendition filter reference

| Filter | Behaviour |
|--------|-----------|
| `fill-800x400` | Crop to exact size, respects focal point |
| `fill-800x400-c75` | Crop with 75% JPEG quality |
| `width-800` | Resize to width, maintain aspect ratio |
| `height-400` | Resize to height, maintain aspect ratio |
| `max-800x400` | Fit within box, maintain aspect ratio |
| `original` | Original file (avoid for large images) |

### Focal point

Editors can set a focal point in the image editor (click the face/subject). Wagtail uses it automatically with `fill-*` filters. Always instruct editors to set focal points on people photos.

### JPEG quality setting

```python
# config/settings/base.py
WAGTAILIMAGES_JPEG_QUALITY = 80   # Default 85; 75–80 is good for web
WAGTAILIMAGES_WEBP_QUALITY = 80
```

---

## 7. Permissions

### Page-level permissions

Wagtail pages inherit the Django permission system + page tree restrictions.

```
Admin > Settings > Groups
```

Create editor groups with appropriate permissions:

| Group | Can do |
|-------|--------|
| **Content Editors** | Create/edit draft pages, upload images, manage snippets |
| **Publishers** | Publish pages (approve and push live) |
| **Admins** | All — including settings, users, collections |

Set "Page permissions" per group by navigating to the page in the Wagtail explorer → Privacy / Permissions.

### Collection permissions for media

Media (images, documents) is organised into **collections**. Set collection-level permissions for different teams:

```
Admin > Settings > Collections
├── Root
│   ├── Site Media (editors can upload)
│   ├── Brand Assets (admins only)
│   └── Client Uploads (restricted)
```

```python
# Programmatically create a collection in a migration or management command
from wagtail.models import Collection

root_collection = Collection.get_first_root_node()
site_media = root_collection.add_child(name="Site Media")
```

### Restricting RawHTMLBlock to developers

Use Django's content-type permissions to validate in `clean()`:

```python
class MarketingPage(BasePage):
    def clean(self):
        super().clean()
        # Prevent non-staff from saving raw_html blocks
        # (Check in view layer or override save in admin)
        pass
```

A simpler approach: remove `RawHTMLBlock` from the editor's StreamBlock definition entirely, and only add it to a separate "Developer Page" type that only admin users can create.

---

## 8. Global Settings

### SiteSettings via wagtail.contrib.settings

```python
# config/settings/base.py
INSTALLED_APPS += ["wagtail.contrib.settings"]

# content/settings.py
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel, MultiFieldPanel


@register_setting
class SiteSettings(BaseSiteSetting):
    """Global site configuration — appears under Settings in Wagtail admin."""

    # Navigation
    primary_cta_text = models.CharField(
        max_length=40,
        default="Get started",
        help_text="Primary call-to-action button label shown in navigation",
    )
    primary_cta_url = models.URLField(
        blank=True,
        help_text="Where the primary CTA button links to",
    )

    # Social
    twitter_url = models.URLField(blank=True, help_text="Full Twitter/X profile URL")
    linkedin_url = models.URLField(blank=True, help_text="Full LinkedIn company page URL")
    github_url = models.URLField(blank=True, help_text="Full GitHub organisation URL")

    # Contact
    contact_email = models.EmailField(blank=True, help_text="Contact email shown in footer")
    phone_number = models.CharField(max_length=30, blank=True)

    panels = [
        MultiFieldPanel(
            [FieldPanel("primary_cta_text"), FieldPanel("primary_cta_url")],
            heading="Navigation",
        ),
        MultiFieldPanel(
            [FieldPanel("twitter_url"), FieldPanel("linkedin_url"), FieldPanel("github_url")],
            heading="Social links",
        ),
        MultiFieldPanel(
            [FieldPanel("contact_email"), FieldPanel("phone_number")],
            heading="Contact",
        ),
    ]

    class Meta:
        verbose_name = "Site settings"
```

Access in API:

```python
# In a custom API endpoint or serializer
from wagtail.contrib.settings.registry import registry as settings_registry

def get_site_settings(request):
    SiteSettings = settings_registry["content.SiteSettings"]
    return SiteSettings.for_request(request)
```

---

## 9. Preview for Editors

### Enable preview on page models

Wagtail 6+ has built-in preview. Ensure each page model defines `preview_modes`:

```python
class MarketingPage(BasePage):
    preview_modes = [
        ("", "Default"),    # "" = default mode
    ]

    def get_preview_url(self, mode_name):
        return f"/api/preview?secret={settings.WAGTAIL_PREVIEW_SECRET}&slug={self.slug}"
```

### Headless preview setup (`wagtail-headless-preview`)

```bash
pip install wagtail-headless-preview
```

```python
# config/settings/base.py
INSTALLED_APPS += ["wagtail_headless_preview"]

WAGTAIL_HEADLESS_PREVIEW = {
    "CLIENT_URLS": {
        "default": "http://localhost:3000/api/preview",
    }
}
```

```python
# On page models — replace Page with HeadlessPreviewMixin + Page
from wagtail_headless_preview.models import HeadlessPreviewMixin

class MarketingPage(HeadlessPreviewMixin, BasePage):
    ...
```

### Next.js Draft Mode route

```typescript
// app/api/preview/route.ts
import { draftMode } from "next/headers";
import { redirect } from "next/navigation";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const secret = searchParams.get("secret");
  const slug = searchParams.get("slug");

  if (secret !== process.env.WAGTAIL_PREVIEW_SECRET) {
    return new Response("Invalid token", { status: 401 });
  }

  (await draftMode()).enable();
  redirect(`/${slug}`);
}
```

---

## 10. Revisions and Moderation

### Revision history

Wagtail automatically saves revisions on every save. Editors can view and restore previous versions from the page history (History tab in the page editor).

No additional configuration needed.

### Moderation workflow (Wagtail 6 Workflows)

Enable approval workflows for content that requires sign-off before publishing:

```
Admin > Settings > Workflows
```

Create a workflow:
1. **Draft → Review** (Editor submits for review)
2. **Review → Approved** (Publisher approves)
3. **Approved → Published** (Auto-publish or manual)

```python
# Assign workflow to page types programmatically
from wagtail.models import Workflow, WorkflowPage

workflow = Workflow.objects.get(name="Editorial Review")
WorkflowPage.objects.get_or_create(
    workflow=workflow,
    page=Page.objects.get(slug="blog"),  # Apply to blog section
)
```

### Scheduled publishing

Editors can set "Go live at" and "Expire at" dates in the Settings tab of any page. No additional setup needed — Celery processes the scheduled tasks.

Make sure `CELERY_BEAT_SCHEDULE` includes Wagtail's scheduled publishing task:

```python
# config/settings/base.py
CELERYBEAT_SCHEDULE = {
    "wagtail_publish_scheduled": {
        "task": "wagtail.models.tasks.publish_scheduled",
        "schedule": crontab(minute="*/5"),  # Check every 5 minutes
    },
}
```

---

## Agency Content Workflow (Moderation)

For Autonomous managing client sites: configure Wagtail's built-in workflow system so client editors can create/edit content, but only agency reviewers can approve and publish.

### Setup

```python
# In Wagtail admin: Settings → Workflows → Create workflow
# Or programmatically in a data migration:

from wagtail.models import Workflow, WorkflowTask, GroupApprovalTask
from django.contrib.auth.models import Group

def setup_agency_workflow(apps, schema_editor):
    # Create groups
    client_editors, _ = Group.objects.get_or_create(name='Client Editors')
    agency_reviewers, _ = Group.objects.get_or_create(name='Agency Reviewers')

    # Create approval task
    task = GroupApprovalTask.objects.create(name='Agency Review')
    task.groups.add(agency_reviewers)

    # Create workflow
    workflow = Workflow.objects.create(name='Client → Agency Review')
    WorkflowTask.objects.create(workflow=workflow, task=task, sort_order=1)

    # Assign to root page (applies to all pages)
    from wagtail.models import Page
    root = Page.objects.first()
    workflow.workflow_pages.create(page=root)
```

### Permission model for agency projects

| Group | Can create | Can edit | Can publish | Can approve |
|---|---|---|---|---|
| Client Editors | ✅ | Own pages only | ❌ | ❌ |
| Agency Reviewers | ✅ | All pages | ✅ (after review) | ✅ |
| Agency Admins | ✅ | All pages | ✅ | ✅ |

Configure in Wagtail admin under Settings → Groups → Page permissions.

### Notification emails

Wagtail sends email notifications at each workflow step. Configure `EMAIL_BACKEND` and `DEFAULT_FROM_EMAIL` in Django settings. Wagtail uses these automatically.

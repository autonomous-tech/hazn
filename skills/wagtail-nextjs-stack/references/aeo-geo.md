# AEO + GEO Reference — Wagtail + Next.js Stack

**Version:** 1.0  
**Stack:** Django + Wagtail CMS + Next.js (App Router)  
**Purpose:** Bake Answer Engine Optimisation (AEO) and Generative Engine Optimisation (GEO)
into every project built on this stack — not bolted on afterward.

---

## Table of Contents

1. [Philosophy — Design In, Not Bolt On](#1-philosophy--design-in-not-bolt-on)
2. [Wagtail Content Modelling for AI Citability](#2-wagtail-content-modelling-for-ai-citability)
   - 2.1 [AEO-Specific StreamField Blocks](#21-aeo-specific-streamfield-blocks)
   - 2.2 [Block Registration on Page Models](#22-block-registration-on-page-models)
   - 2.3 [Entity Fields on Page Models](#23-entity-fields-on-page-models)
   - 2.4 [Entity Attribution in First Paragraph (clean() Warning)](#24-entity-attribution-in-first-paragraph-clean-warning)
3. [clean() Validation for AEO Compliance](#3-clean-validation-for-aeo-compliance)
4. [Computed API Fields for Next.js](#4-computed-api-fields-for-nextjs)
   - 4.1 [Custom Serializer Classes](#41-custom-serializer-classes)
   - 4.2 [Registering APIFields on Page Models](#42-registering-apifields-on-page-models)
5. [Schema Auto-Generation from StreamField](#5-schema-auto-generation-from-streamfield)
   - 5.1 [Base Schema Mixin](#51-base-schema-mixin)
   - 5.2 [BlogPostPage Schema](#52-blogpostpage-schema)
   - 5.3 [HomePage / MarketingPage Schema](#53-homepage--marketingpage-schema)
   - 5.4 [CaseStudyPage Schema](#54-casestudypage-schema)
   - 5.5 [SchemaMarkupField Serializer (API exposure)](#55-schemamarkupfield-serializer-api-exposure)
6. [llms.txt — Live Django View](#6-llmstxt--live-django-view)
7. [AICitationLog — GEO Monitoring Model](#7-aicitationlog--geo-monitoring-model)
   - 7.1 [Model Definition](#71-model-definition)
   - 7.2 [Wagtail Admin Registration](#72-wagtail-admin-registration)
   - 7.3 [Management Command Scaffold](#73-management-command-scaffold)
8. [HTML Rendering Constraints (Next.js)](#8-html-rendering-constraints-nextjs)
   - 8.1 [AnswerBlock Component](#81-answerblock-component)
   - 8.2 [FAQBlock Component](#82-faqblock-component)
   - 8.3 [HowToBlock Component](#83-howtoblockcomponent)
   - 8.4 [StatsBlock Component](#84-statsblock-component)
   - 8.5 [DefinitionBlock Component](#85-definitionblock-component)
   - 8.6 [StreamField Renderer](#86-streamfield-renderer)
9. [Content Structure Rules for Editors](#9-content-structure-rules-for-editors)
10. [AEO/GEO Checklist — Every Wagtail Project](#10-aeogeo-checklist--every-wagtail-project)

---

## 1. Philosophy — Design In, Not Bolt On

Wagtail's StreamField architecture is uniquely well-positioned for AI citation — and that advantage is
only realised if AEO is modelled into the data layer from day one. Structured content is already
separated from presentation in Wagtail: every block type is a discrete, typed content unit with its
own schema. An `AnswerBlock` is not prose that happens to contain an answer; it *is* an answer,
with question, body, and rendering semantics enforced at the model level. This maps directly to what
AI engines need: self-contained, extractable content passages where the claim works standalone, the
entity is unambiguous, and the structure signals intent (FAQ, HowTo, Definition, Statistic).

Retrofitting AEO onto an existing Wagtail site means rewriting content models, migrating StreamField
data, retraining editors, and patching schema generation onto pages that were never designed to
emit structured data. Do it right the first time: every block type in this stack is an AEO primitive,
every page model carries entity metadata, every API response delivers pre-extracted AEO data to
Next.js, and schema generation is an automatic consequence of the content model — not a separate task.

---

## 2. Wagtail Content Modelling for AI Citability

### 2.1 AEO-Specific StreamField Blocks

Create these in `{app}/blocks.py`. They are the foundation of every AEO-optimised page.

```python
# {app}/blocks.py
from django.core.exceptions import ValidationError
from wagtail.blocks import (
    CharBlock,
    ListBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
)


# ---------------------------------------------------------------------------
# AnswerBlock
# A direct answer to a specific question.
# Optimised for AI citation and featured snippets.
# clean() enforces 40–300 word answer.
# ---------------------------------------------------------------------------
class AnswerBlock(StructBlock):
    """
    A direct answer to a specific question. Optimised for AI citation and
    featured snippets. Answer must be 40–300 words.
    """

    question = CharBlock(
        help_text=(
            "The exact question this block answers. "
            "Write it as users search it — e.g. 'What is server-side tracking?'"
        )
    )
    answer = RichTextBlock(
        features=["bold", "italic", "ul", "ol"],
        help_text=(
            "Direct answer in 40–300 words. "
            "Start with the answer, not the context. "
            "This block may be extracted by AI engines in isolation — "
            "do not reference anything above or below it."
        ),
    )

    def clean(self, value):
        cleaned = super().clean(value)
        answer_text = cleaned["answer"].source if hasattr(cleaned["answer"], "source") else str(cleaned["answer"])
        # Strip HTML tags for word count
        import re
        plain = re.sub(r"<[^>]+>", " ", answer_text)
        word_count = len(plain.split())
        if word_count < 40:
            raise ValidationError(
                {"answer": f"Answer is too short ({word_count} words). Minimum 40 words for AI citability."}
            )
        if word_count > 300:
            raise ValidationError(
                {"answer": f"Answer is too long ({word_count} words). Maximum 300 words. Split into multiple AnswerBlocks."}
            )
        return cleaned

    class Meta:
        icon = "help"
        label = "Answer Block"
        template = "blocks/answer_block.html"


# ---------------------------------------------------------------------------
# FAQBlock
# FAQ section. Auto-generates FAQPage schema.
# Each Q+A must be independently citable (self-contained).
# ---------------------------------------------------------------------------
class FAQItemBlock(StructBlock):
    question = CharBlock(
        help_text="Question as users would search it."
    )
    answer = RichTextBlock(
        features=["bold", "italic", "ul", "ol", "link"],
        help_text=(
            "Complete, self-contained answer. "
            "Do NOT start with 'See above', 'As mentioned', or any reference to other content. "
            "The AI engine will cite this answer without context — it must make sense alone."
        ),
    )

    def clean(self, value):
        cleaned = super().clean(value)
        answer_text = str(cleaned.get("answer", "")).lower().strip()
        forbidden_starts = ("see above", "as mentioned", "as discussed", "as noted", "refer to")
        for phrase in forbidden_starts:
            if answer_text.startswith(phrase):
                raise ValidationError(
                    {
                        "answer": (
                            f"FAQ answer cannot start with '{phrase}'. "
                            "Each answer must be fully self-contained."
                        )
                    }
                )
        return cleaned


class FAQBlock(StructBlock):
    """
    FAQ section. Generates FAQPage schema automatically.
    Each Q+A is independently citable by AI engines.
    """

    heading = CharBlock(
        required=False,
        help_text='Optional section heading (e.g. "Frequently Asked Questions")',
    )
    items = ListBlock(
        FAQItemBlock(),
        help_text="Add at least 5 questions for meaningful AI signal.",
    )

    class Meta:
        icon = "list-ul"
        label = "FAQ"
        template = "blocks/faq_block.html"


# ---------------------------------------------------------------------------
# StatBlock / StatsBlock
# Citable statistics. AI systems cite specific numbers over vague claims.
# ---------------------------------------------------------------------------
class StatBlock(StructBlock):
    """A single citable statistic. AI systems prefer specific numbers with sources."""

    value = CharBlock(
        help_text='The statistic value (e.g. "$10M+", "94%", "4+ years", "3× faster")'
    )
    label = CharBlock(help_text="What the statistic measures.")
    source = CharBlock(
        required=False,
        help_text="Source name if external data (e.g. 'Semrush 2025', 'Internal audit')",
    )
    year = CharBlock(
        required=False,
        help_text="Year of the statistic. Required for all external data.",
    )

    class Meta:
        icon = "snippet"
        label = "Stat"


class StatsBlock(StructBlock):
    """A group of stats. Each stat is individually citable by AI engines."""

    heading = CharBlock(required=False)
    stats = ListBlock(StatBlock())

    class Meta:
        icon = "snippet"
        label = "Stats Block"
        template = "blocks/stats_block.html"


# ---------------------------------------------------------------------------
# DefinitionBlock
# Defined term. Optimised for 'what is X?' queries and knowledge graph.
# ---------------------------------------------------------------------------
class DefinitionBlock(StructBlock):
    """
    A defined term. Optimised for 'What is X?' queries and knowledge graph
    entity recognition. Define every piece of jargon used on the page.
    """

    term = CharBlock(help_text="The term being defined.")
    definition = RichTextBlock(
        features=["bold", "italic", "link"],
        help_text=(
            "Concise definition (1–3 sentences). "
            "Define it as if writing for a technical dictionary. "
            "Do not use the term in its own definition."
        ),
    )
    also_known_as = CharBlock(
        required=False,
        help_text="Comma-separated aliases or related terms (e.g. 'SST, server-side tagging')",
    )

    class Meta:
        icon = "doc-full"
        label = "Definition"
        template = "blocks/definition_block.html"


# ---------------------------------------------------------------------------
# HowToBlock
# Complete how-to guide. Generates HowTo schema.
# Optimised for step-by-step AI citations.
# ---------------------------------------------------------------------------
class ProcessStepBlock(StructBlock):
    """A numbered process step. Steps must use imperative titles."""

    step_number = CharBlock(
        help_text="Step number as a string (e.g. '1', '2', '3')"
    )
    title = CharBlock(
        help_text=(
            "Step title in imperative form: 'Configure', 'Deploy', 'Install'. "
            "Not: 'Configuring', 'You should configure'."
        )
    )
    body = RichTextBlock(
        features=["bold", "italic", "ul", "ol", "link", "code"],
        help_text="Full instructions for this step. Self-contained — no references to other steps.",
    )

    class Meta:
        icon = "order"
        label = "Process Step"


class HowToBlock(StructBlock):
    """
    A complete how-to guide. Generates HowTo schema automatically.
    Optimised for step-by-step AI citations.
    """

    title = CharBlock(
        help_text=(
            "The task being accomplished. "
            "Use sentence form: 'How to set up server-side tracking in Shopify'"
        )
    )
    intro = RichTextBlock(
        features=["bold", "italic"],
        help_text="One paragraph. State what the reader will accomplish and any prerequisites.",
    )
    steps = ListBlock(ProcessStepBlock())
    total_time = CharBlock(
        required=False,
        help_text="Estimated time to complete (e.g. '2 hours', '30 minutes')",
    )

    class Meta:
        icon = "list-ol"
        label = "How-To Guide"
        template = "blocks/how_to_block.html"


# ---------------------------------------------------------------------------
# AEO-aware base StreamBlock
# Use as the base for all page body fields.
# ---------------------------------------------------------------------------
class AEOStreamBlock(StreamBlock):
    """
    Base StreamBlock including all AEO block types.
    Extend this in page-specific StreamBlocks rather than redefining blocks.
    """

    answer_block = AnswerBlock()
    faq_block = FAQBlock()
    stats_block = StatsBlock()
    definition_block = DefinitionBlock()
    how_to_block = HowToBlock()
    rich_text = RichTextBlock(
        features=["h2", "h3", "h4", "bold", "italic", "ul", "ol", "link", "image", "code"],
    )
```

---

### 2.2 Block Registration on Page Models

```python
# {app}/models.py
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, HelpPanel
from wagtail.api import APIField
from wagtail.fields import StreamField
from wagtail.models import Page
from .blocks import AEOStreamBlock


class BlogPostPage(Page):
    # --- AEO entity metadata ---
    primary_entity = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "The main entity/topic this page is about. "
            "Be specific: 'Marketing Attribution' not 'Marketing'. "
            "AI engines use this to anchor the page's knowledge graph node."
        ),
    )
    entity_type = models.CharField(
        max_length=100,
        blank=True,
        help_text=(
            "Schema.org entity type (e.g. 'SoftwareApplication', 'Service', "
            "'TechArticle', 'HowTo', 'FAQPage')"
        ),
    )
    mentions = models.TextField(
        blank=True,
        help_text=(
            "Comma-separated entities mentioned in this content. "
            "Include tools, brands, concepts, and people referenced. "
            "Example: 'Google Analytics 4, Shopify, server-side tracking, GTM'"
        ),
    )

    # --- Body ---
    body = StreamField(
        AEOStreamBlock(),
        use_json_field=True,
        blank=True,
    )

    # --- Other fields ---
    author = models.CharField(max_length=255, blank=True)
    publish_date = models.DateField(null=True, blank=True)
    og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                HelpPanel(
                    content=(
                        "<strong>AEO/GEO Entity Fields</strong><br>"
                        "These fields shape how AI engines understand and cite this page. "
                        "Fill them before publishing."
                    )
                ),
                FieldPanel("primary_entity"),
                FieldPanel("entity_type"),
                FieldPanel("mentions"),
            ],
            heading="AI Citability",
        ),
        FieldPanel("author"),
        FieldPanel("publish_date"),
        FieldPanel("og_image"),
        FieldPanel("body"),
    ]

    promote_panels = Page.promote_panels  # includes seo_title + search_description
```

---

### 2.3 Entity Fields on Page Models

All page models — not just BlogPostPage — must carry the three entity fields:

| Field | Type | Purpose |
|---|---|---|
| `primary_entity` | `CharField(255)` | The single topic/entity this page is *about* |
| `entity_type` | `CharField(100)` | Schema.org type for the entity |
| `mentions` | `TextField` | Comma-separated entities referenced in the content |

Extract these into a reusable mixin to avoid repeating on every model:

```python
# {app}/mixins.py

class AEOEntityMixin(models.Model):
    """
    Mixin that adds AEO entity metadata fields to any page model.
    Import and place first in the inheritance chain before Page.
    """

    primary_entity = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "The main entity/topic this page is about. "
            "Be specific: 'Marketing Attribution' not 'Marketing'. "
            "AI engines use this to anchor the page's knowledge graph node."
        ),
    )
    entity_type = models.CharField(
        max_length=100,
        blank=True,
        help_text=(
            "Schema.org entity type. Examples: 'SoftwareApplication', 'Service', "
            "'TechArticle', 'HowTo', 'FAQPage', 'Organization', 'Person'"
        ),
    )
    mentions = models.TextField(
        blank=True,
        help_text=(
            "Comma-separated entities mentioned in this content. "
            "Include tools, brands, concepts, and people. "
            "Example: 'Google Analytics 4, Shopify, server-side tracking, GTM'"
        ),
    )

    @property
    def entity_map(self):
        """Structured entity data for the API."""
        mentioned = [e.strip() for e in self.mentions.split(",") if e.strip()]
        return {
            "primary": self.primary_entity,
            "type": self.entity_type,
            "mentions": mentioned,
        }

    class Meta:
        abstract = True


# Usage:
# class BlogPostPage(AEOEntityMixin, AEOSchemaMixin, Page):
#     ...
```

---

### 2.4 Entity Attribution in First Paragraph (clean() Warning)

The first `RichTextBlock` on any page should explicitly reference `primary_entity`. This is a
**warning**, not a hard error — the editor is informed but not blocked.

```python
# In your Page model's clean() method:

import logging
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class BlogPostPage(AEOEntityMixin, AEOSchemaMixin, Page):
    # ... fields ...

    def clean(self):
        super().clean()
        self._validate_search_description()
        self._warn_entity_in_first_paragraph()

    def _validate_search_description(self):
        """search_description is required and must be 120–160 chars."""
        desc = (self.search_description or "").strip()
        if not desc:
            raise ValidationError(
                {"search_description": "Search description is required for AEO. Write 120–160 characters."}
            )
        if len(desc) < 120:
            raise ValidationError(
                {
                    "search_description": (
                        f"Search description is too short ({len(desc)} chars). "
                        "Minimum 120 characters for AI engine indexing quality."
                    )
                }
            )
        if len(desc) > 160:
            raise ValidationError(
                {
                    "search_description": (
                        f"Search description is too long ({len(desc)} chars). "
                        "Maximum 160 characters — AI engines truncate longer descriptions."
                    )
                }
            )

    def _warn_entity_in_first_paragraph(self):
        """
        Warn (not error) if the first RichTextBlock does not mention primary_entity.
        AI engines anchor pages to entities; the first paragraph sets that anchor.
        """
        if not self.primary_entity:
            return
        if not hasattr(self, "body") or not self.body:
            return

        first_rich_text = None
        for block in self.body:
            if block.block_type == "rich_text":
                first_rich_text = block
                break

        if first_rich_text is None:
            return

        import re
        plain = re.sub(r"<[^>]+>", " ", str(first_rich_text.value)).lower()
        entity_lower = self.primary_entity.lower()

        if entity_lower not in plain:
            # Log as warning — surfaces in Wagtail admin as a non-blocking notice
            logger.warning(
                "AEO: First paragraph of '%s' does not mention primary entity '%s'. "
                "Consider opening with an explicit mention to anchor AI engine entity recognition.",
                self.title,
                self.primary_entity,
            )
            # Wagtail surfaces these via messages in the admin when raised as non-field errors
            # Use a soft warning approach — add to page.warnings if your Wagtail version supports it
```

---

## 3. clean() Validation for AEO Compliance

These constraints are enforced at the model level — editors cannot bypass them on publish.

| Field | Rule | Error type |
|---|---|---|
| `AnswerBlock.answer` | 40–300 words | Hard error (ValidationError) |
| `FAQItemBlock.answer` | Cannot start with reference phrases | Hard error |
| `search_description` | Required, 120–160 chars | Hard error |
| First paragraph entity mention | Must contain `primary_entity` | Soft warning (logged) |

The `AnswerBlock.clean()` and `FAQItemBlock.clean()` are defined on the block itself (see Section 2.1).
The `search_description` validation lives in the page model's `clean()` (see Section 2.4).

**Word count utility (reusable):**

```python
# {app}/utils.py
import re


def html_word_count(html_string: str) -> int:
    """Strip HTML tags and count words in a rich text value."""
    plain = re.sub(r"<[^>]+>", " ", str(html_string))
    plain = re.sub(r"\s+", " ", plain).strip()
    return len(plain.split()) if plain else 0


def extract_plain_text(html_string: str) -> str:
    """Strip HTML tags and return plain text."""
    plain = re.sub(r"<[^>]+>", " ", str(html_string))
    return re.sub(r"\s+", " ", plain).strip()
```

---

## 4. Computed API Fields for Next.js

Next.js must not parse raw StreamField JSON to find AEO content. The Wagtail API exposes
purpose-built computed fields: pre-extracted answer blocks, FAQ items, schema markup, and entity
map. The frontend receives clean, typed AEO data — no StreamField traversal on the JS side.

### 4.1 Custom Serializer Classes

```python
# {app}/serializers.py
import re
from rest_framework import serializers
from wagtail.rich_text import expand_db_html


def _strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", str(html)).strip()


class AnswerBlocksField(serializers.Field):
    """
    Extracts all AnswerBlocks from the page body StreamField.
    Returns a list of {question, answer_html, answer_plain} dicts.
    """

    def to_representation(self, page):
        result = []
        if not hasattr(page, "body"):
            return result
        for block in page.body:
            if block.block_type == "answer_block":
                answer_html = expand_db_html(str(block.value["answer"]))
                result.append(
                    {
                        "question": block.value["question"],
                        "answer_html": answer_html,
                        "answer_plain": _strip_tags(answer_html),
                    }
                )
        return result


class FAQItemsField(serializers.Field):
    """
    Extracts all FAQ items from all FAQBlocks in the page body.
    Returns a flat list of {question, answer_html, answer_plain} dicts.
    Each item is independently citable — no nesting by block.
    """

    def to_representation(self, page):
        result = []
        if not hasattr(page, "body"):
            return result
        for block in page.body:
            if block.block_type == "faq_block":
                for item in block.value["items"]:
                    answer_html = expand_db_html(str(item["answer"]))
                    result.append(
                        {
                            "question": item["question"],
                            "answer_html": answer_html,
                            "answer_plain": _strip_tags(answer_html),
                        }
                    )
        return result


class SchemaMarkupField(serializers.Field):
    """
    Calls the page's get_schema_markup() method and returns the full @graph dict.
    The page model must implement get_schema_markup().
    """

    def to_representation(self, page):
        if hasattr(page, "get_schema_markup"):
            return page.get_schema_markup()
        return {}


class EntityMapField(serializers.Field):
    """
    Returns the entity map from the AEOEntityMixin.entity_map property.
    """

    def to_representation(self, page):
        if hasattr(page, "entity_map"):
            return page.entity_map
        return {"primary": "", "type": "", "mentions": []}
```

---

### 4.2 Registering APIFields on Page Models

```python
# {app}/models.py (continued)
from wagtail.api import APIField
from .serializers import AnswerBlocksField, FAQItemsField, SchemaMarkupField, EntityMapField


class BlogPostPage(AEOEntityMixin, AEOSchemaMixin, Page):
    # ... (fields and panels as above) ...

    api_fields = [
        # Standard fields
        APIField("title"),
        APIField("seo_title"),
        APIField("search_description"),
        APIField("author"),
        APIField("publish_date"),
        APIField("body"),

        # AEO computed fields — Next.js uses these, not raw body
        APIField("answer_blocks", serializer=AnswerBlocksField(source="*")),
        APIField("faq_items", serializer=FAQItemsField(source="*")),
        APIField("schema_markup", serializer=SchemaMarkupField(source="*")),
        APIField("entity_map", serializer=EntityMapField(source="*")),
    ]
```

**What Next.js receives from `/api/v2/pages/{id}/`:**

```json
{
  "title": "What is Server-Side Tracking?",
  "search_description": "Server-side tracking moves data collection off the browser...",
  "answer_blocks": [
    {
      "question": "What is server-side tracking?",
      "answer_html": "<p>Server-side tracking is the process of...</p>",
      "answer_plain": "Server-side tracking is the process of..."
    }
  ],
  "faq_items": [
    {
      "question": "Is server-side tracking GDPR compliant?",
      "answer_html": "<p>Yes. Server-side tracking...</p>",
      "answer_plain": "Yes. Server-side tracking..."
    }
  ],
  "schema_markup": {
    "@context": "https://schema.org",
    "@graph": [...]
  },
  "entity_map": {
    "primary": "Server-Side Tracking",
    "type": "TechArticle",
    "mentions": ["Google Tag Manager", "Shopify", "GDPR", "first-party data"]
  }
}
```

---

## 5. Schema Auto-Generation from StreamField

Schema is a **consequence of content structure** — not a separate task. Adding a `FAQBlock`
automatically adds `FAQPage` schema. Adding a `HowToBlock` automatically adds `HowTo` schema.
Editors never write JSON-LD manually.

### 5.1 Base Schema Mixin

```python
# {app}/mixins.py (continued)
import re
from django.conf import settings
from wagtail.rich_text import expand_db_html


def _strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", str(html)).strip()


class AEOSchemaMixin(models.Model):
    """
    Mixin that provides schema auto-generation for any page model.
    Subclasses implement _base_schema_nodes() to provide page-type-specific
    schema (Article, Service, etc.). This mixin handles dynamic block detection.
    """

    def get_schema_markup(self) -> dict:
        """
        Build the full JSON-LD @graph for this page.
        Merges base schema nodes with auto-detected block schema.
        Call this from the template and the schema_markup API field.
        """
        graph = list(self._base_schema_nodes())
        graph.extend(self._schema_from_faq_blocks())
        graph.extend(self._schema_from_howto_blocks())
        graph.extend(self._breadcrumb_schema())
        return {"@context": "https://schema.org", "@graph": graph}

    def _base_schema_nodes(self) -> list:
        """Override in subclasses to return page-type-specific schema nodes."""
        return []

    def _schema_from_faq_blocks(self) -> list:
        """
        Auto-detect FAQBlocks in the page body and emit FAQPage schema.
        Returns a list — either empty or containing one FAQPage node.
        """
        if not hasattr(self, "body"):
            return []
        faq_items = []
        for block in self.body:
            if block.block_type == "faq_block":
                for item in block.value["items"]:
                    answer_html = expand_db_html(str(item["answer"]))
                    faq_items.append(
                        {
                            "@type": "Question",
                            "name": item["question"],
                            "acceptedAnswer": {
                                "@type": "Answer",
                                "text": _strip_tags(answer_html),
                            },
                        }
                    )
        if not faq_items:
            return []
        return [{"@type": "FAQPage", "mainEntity": faq_items}]

    def _schema_from_howto_blocks(self) -> list:
        """
        Auto-detect HowToBlocks in the page body and emit HowTo schema.
        Returns one HowTo node per HowToBlock found.
        """
        if not hasattr(self, "body"):
            return []
        nodes = []
        for block in self.body:
            if block.block_type == "how_to_block":
                val = block.value
                step_nodes = []
                for step in val["steps"]:
                    body_html = expand_db_html(str(step["body"]))
                    step_nodes.append(
                        {
                            "@type": "HowToStep",
                            "position": step["step_number"],
                            "name": step["title"],
                            "text": _strip_tags(body_html),
                        }
                    )
                node = {
                    "@type": "HowTo",
                    "name": val["title"],
                    "description": _strip_tags(expand_db_html(str(val["intro"]))),
                    "step": step_nodes,
                }
                if val.get("total_time"):
                    # Convert human string to ISO 8601 duration as best-effort
                    node["totalTime"] = val["total_time"]
                nodes.append(node)
        return nodes

    def _breadcrumb_schema(self) -> list:
        """
        Emit BreadcrumbList schema based on the Wagtail page tree ancestry.
        """
        ancestors = self.get_ancestors(inclusive=True).filter(depth__gte=2)
        items = []
        for position, page in enumerate(ancestors, start=1):
            items.append(
                {
                    "@type": "ListItem",
                    "position": position,
                    "name": page.title,
                    "item": page.full_url,
                }
            )
        if not items:
            return []
        return [{"@type": "BreadcrumbList", "itemListElement": items}]

    def _org_node(self) -> dict:
        """
        Shared Organization node. Uses SITE_SCHEMA settings if defined,
        falls back to sensible defaults.
        """
        schema_settings = getattr(settings, "SITE_SCHEMA", {})
        return {
            "@type": "Organization",
            "@id": schema_settings.get("org_id", f"{self.get_site().root_url}/#organization"),
            "name": schema_settings.get("org_name", self.get_site().site_name),
            "url": self.get_site().root_url,
            "logo": schema_settings.get("logo_url", ""),
            "sameAs": schema_settings.get("same_as", []),
        }

    class Meta:
        abstract = True
```

**Settings for site-level schema identity (`settings.py`):**

```python
SITE_SCHEMA = {
    "org_id": "https://autonomoustech.ca/#organization",
    "org_name": "Autonomous Technologies",
    "logo_url": "https://autonomoustech.ca/static/images/logo.png",
    "same_as": [
        "https://www.linkedin.com/company/autonomous-technologies",
        "https://twitter.com/autonomoustech",
        "https://github.com/autonomous-technologies",
    ],
}
```

---

### 5.2 BlogPostPage Schema

```python
class BlogPostPage(AEOEntityMixin, AEOSchemaMixin, Page):
    # ... fields ...

    def _base_schema_nodes(self) -> list:
        """Article schema for blog posts. FAQPage and HowTo are appended automatically."""
        from django.utils import timezone

        og_image_url = None
        if self.og_image:
            try:
                og_image_url = self.og_image.get_rendition("fill-1200x630").url
            except Exception:
                pass

        article_node = {
            "@type": "Article",
            "@id": f"{self.full_url}#article",
            "headline": self.seo_title or self.title,
            "description": self.search_description or "",
            "datePublished": str(self.publish_date) if self.publish_date else "",
            "dateModified": (
                str(self.last_published_at.date())
                if self.last_published_at
                else str(self.publish_date or "")
            ),
            "author": {
                "@type": "Person",
                "name": self.author or "Autonomous Technologies",
            },
            "publisher": self._org_node(),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": self.full_url,
            },
        }
        if og_image_url:
            article_node["image"] = og_image_url
        if self.primary_entity:
            article_node["about"] = {
                "@type": self.entity_type or "Thing",
                "name": self.primary_entity,
            }
        return [article_node]
```

---

### 5.3 HomePage / MarketingPage Schema

```python
class HomePage(AEOEntityMixin, AEOSchemaMixin, Page):
    # ... fields ...

    def _base_schema_nodes(self) -> list:
        """Organization + WebSite + WebPage schema for the homepage."""
        site = self.get_site()
        org_node = self._org_node()

        website_node = {
            "@type": "WebSite",
            "@id": f"{site.root_url}/#website",
            "url": site.root_url,
            "name": site.site_name,
            "publisher": {"@id": org_node["@id"]},
            "potentialAction": {
                "@type": "SearchAction",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": f"{site.root_url}/search?q={{search_term_string}}",
                },
                "query-input": "required name=search_term_string",
            },
        }

        webpage_node = {
            "@type": "WebPage",
            "@id": f"{self.full_url}#webpage",
            "url": self.full_url,
            "name": self.seo_title or self.title,
            "description": self.search_description or "",
            "isPartOf": {"@id": f"{site.root_url}/#website"},
            "about": {"@id": org_node["@id"]},
        }

        return [org_node, website_node, webpage_node]


class MarketingPage(AEOEntityMixin, AEOSchemaMixin, Page):
    # ... fields ...

    def _base_schema_nodes(self) -> list:
        """Service + WebPage schema for marketing/services pages."""
        site = self.get_site()

        service_node = {
            "@type": "Service",
            "@id": f"{self.full_url}#service",
            "name": self.seo_title or self.title,
            "description": self.search_description or "",
            "provider": self._org_node(),
            "url": self.full_url,
        }
        if self.primary_entity:
            service_node["serviceType"] = self.primary_entity

        webpage_node = {
            "@type": "WebPage",
            "@id": f"{self.full_url}#webpage",
            "url": self.full_url,
            "name": self.seo_title or self.title,
            "isPartOf": {"@id": f"{site.root_url}/#website"},
        }

        return [service_node, webpage_node]
```

---

### 5.4 CaseStudyPage Schema

```python
class CaseStudyPage(AEOEntityMixin, AEOSchemaMixin, Page):
    client_name = models.CharField(max_length=255, blank=True)
    outcome_summary = models.TextField(
        blank=True,
        help_text=(
            "One sentence summarising the measurable outcome. "
            "Used in schema. Example: 'Reduced CAC by 34% in 90 days.'"
        ),
    )
    # ... other fields ...

    def _base_schema_nodes(self) -> list:
        """Article schema for case studies, with outcome metric in description."""
        article_node = {
            "@type": "Article",
            "@id": f"{self.full_url}#article",
            "headline": self.seo_title or self.title,
            "description": self.outcome_summary or self.search_description or "",
            "datePublished": (
                str(self.last_published_at.date()) if self.last_published_at else ""
            ),
            "dateModified": (
                str(self.last_published_at.date()) if self.last_published_at else ""
            ),
            "author": self._org_node(),
            "publisher": self._org_node(),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": self.full_url,
            },
            "about": {
                "@type": "Organization",
                "name": self.client_name or "Client",
            },
        }
        return [article_node]
```

---

### 5.5 SchemaMarkupField Serializer (API exposure)

See Section 4.1 — `SchemaMarkupField` calls `page.get_schema_markup()` and returns the full
`@graph` dict. The Next.js app renders it as JSON-LD in `<head>`:

```typescript
// components/SchemaMarkup.tsx
import type { SchemaGraph } from '@/types/wagtail'

interface Props {
  schema: SchemaGraph | null
}

export function SchemaMarkup({ schema }: Props) {
  if (!schema || !schema['@graph']?.length) return null
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  )
}

// app/blog/[slug]/page.tsx
import { SchemaMarkup } from '@/components/SchemaMarkup'

export default async function BlogPostPage({ params }) {
  const page = await getPageBySlug(params.slug, { fields: 'schema_markup,title,...' })
  return (
    <>
      <head>
        <SchemaMarkup schema={page.schema_markup} />
      </head>
      {/* page content */}
    </>
  )
}
```

---

## 6. llms.txt — Live Django View

`llms.txt` is a **live Django view** that queries the Wagtail page tree on every request. It is
**not** a static file checked into source control. Cache with `@cache_page(3600)`. Invalidate
via the `page_published` signal so it is always in sync with published content.

```python
# {app}/views.py
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from django.conf import settings


@method_decorator(cache_page(3600), name="dispatch")
class LLMsTxtView(View):
    """
    Serves /llms.txt as a live document generated from the Wagtail page tree.
    Cache TTL: 1 hour. Invalidated on page_published signal.
    """

    def get(self, request):
        from .models import BlogPostPage, CaseStudyPage, MarketingPage

        # Pull live, public pages only
        posts = (
            BlogPostPage.objects.live()
            .public()
            .order_by("-publish_date")
            .values("title", "slug", "search_description")[:100]
        )
        cases = (
            CaseStudyPage.objects.live()
            .public()
            .order_by("-last_published_at")
            .values("title", "slug", "search_description")
        )
        marketing = (
            MarketingPage.objects.live()
            .public()
            .order_by("title")
            .values("title", "slug", "search_description")
        )

        site_name = getattr(settings, "SITE_SCHEMA", {}).get("org_name", "Our Company")
        site_tagline = getattr(settings, "SITE_SCHEMA", {}).get("tagline", "")
        base_url = getattr(settings, "WAGTAILAPI_BASE_URL", request.build_absolute_uri("/").rstrip("/"))

        lines = [
            f"# {site_name}",
            f"> {site_tagline}" if site_tagline else "",
            "",
            "## Pages",
        ]

        for page in marketing:
            url = f"{base_url}/{page['slug']}/"
            desc = page.get("search_description") or ""
            lines.append(f"- [{page['title']}]({url}): {desc}".strip().rstrip(":"))

        lines += ["", "## Blog"]
        for page in posts:
            url = f"{base_url}/blog/{page['slug']}/"
            desc = page.get("search_description") or ""
            lines.append(f"- [{page['title']}]({url}): {desc}".strip().rstrip(":"))

        lines += ["", "## Case Studies"]
        for page in cases:
            url = f"{base_url}/case-studies/{page['slug']}/"
            desc = page.get("search_description") or ""
            lines.append(f"- [{page['title']}]({url}): {desc}".strip().rstrip(":"))

        # Filter empty lines in the middle but keep structural blanks
        content = "\n".join(line for line in lines if line is not None)

        return HttpResponse(content, content_type="text/plain; charset=utf-8")
```

**URL registration:**

```python
# {app}/urls.py
from django.urls import path
from .views import LLMsTxtView

urlpatterns = [
    path("llms.txt", LLMsTxtView.as_view(), name="llms-txt"),
]

# project/urls.py — add at root level (before wagtail urls)
from django.urls import include, path

urlpatterns = [
    path("", include("yourapp.urls")),
    # ... wagtail, api, admin urls ...
]
```

**Cache invalidation via signal:**

```python
# {app}/signals.py
from django.core.cache import cache
from wagtail.signals import page_published


def invalidate_llms_txt_cache(sender, **kwargs):
    """
    Clear the llms.txt cache whenever any page is published.
    Django's cache_page uses a URL-based key — clear by prefix.
    """
    # Clear all cache entries for the llms.txt URL pattern
    cache.delete_pattern("*llms.txt*")


page_published.connect(invalidate_llms_txt_cache)


# {app}/apps.py
from django.apps import AppConfig


class YourAppConfig(AppConfig):
    name = "yourapp"

    def ready(self):
        import yourapp.signals  # noqa: F401 — connect signals on startup
```

**Note:** `cache.delete_pattern()` requires a cache backend that supports pattern deletion
(e.g. django-redis). For the default LocMemCache, clear the entire cache or use a versioning
strategy instead.

---

## 7. AICitationLog — GEO Monitoring Model

The `AICitationLog` tracks which pages are being cited by which AI engines for which queries.
It is visible in the Wagtail admin as a snippet. This model is the foundation of future
SearchIntel product functionality.

### 7.1 Model Definition

```python
# {app}/models.py (continued)
from django.db import models
from wagtail.models import Page
from wagtail.snippets.models import register_snippet


class AICitationLog(models.Model):
    """
    Records AI engine citation checks for a page and query combination.
    Visible in Wagtail admin. Foundation of GEO monitoring and SearchIntel.
    """

    ENGINE_CHOICES = [
        ("chatgpt", "ChatGPT"),
        ("perplexity", "Perplexity"),
        ("google_aio", "Google AI Overviews"),
        ("gemini", "Gemini"),
        ("copilot", "Copilot"),
        ("claude", "Claude"),
        ("other", "Other"),
    ]

    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="citation_logs",
        help_text="The page being monitored for AI citations.",
    )
    query = models.TextField(
        help_text=(
            "The exact search query tested. "
            "Example: 'What is server-side tracking?' or 'best Shopify analytics tools'"
        )
    )
    engine = models.CharField(
        max_length=50,
        choices=ENGINE_CHOICES,
        help_text="The AI engine checked.",
    )
    cited = models.BooleanField(
        default=False,
        help_text="Was this page cited in the AI engine's response to the query?",
    )
    checked_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this check was performed.",
    )
    notes = models.TextField(
        blank=True,
        help_text=(
            "Optional notes about the citation context, sentiment, or accuracy. "
            "Paste relevant excerpt from the AI response here."
        ),
    )

    class Meta:
        ordering = ["-checked_at"]
        verbose_name = "AI Citation Log"
        verbose_name_plural = "AI Citation Logs"

    def __str__(self):
        cited_str = "✓ cited" if self.cited else "✗ not cited"
        return f"{self.engine} | {self.page.title[:40]} | {cited_str}"
```

---

### 7.2 Wagtail Admin Registration

```python
# {app}/wagtail_hooks.py
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel, ObjectList
from .models import AICitationLog


class AICitationLogViewSet(SnippetViewSet):
    model = AICitationLog
    icon = "search"
    menu_label = "AI Citation Log"
    menu_order = 900
    list_display = ["page", "engine", "query_truncated", "cited", "checked_at"]
    list_filter = ["engine", "cited", "checked_at"]
    search_fields = ["query", "notes"]

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("page"),
                FieldPanel("query"),
            ],
            heading="What was checked",
        ),
        FieldRowPanel(
            [
                FieldPanel("engine"),
                FieldPanel("cited"),
                FieldPanel("checked_at", read_only=True),
            ],
            heading="Result",
        ),
        FieldPanel("notes"),
    ]

    def query_truncated(self, obj):
        return obj.query[:60] + "..." if len(obj.query) > 60 else obj.query

    query_truncated.short_description = "Query"


register_snippet(AICitationLogViewSet)
```

---

### 7.3 Management Command Scaffold

```python
# {app}/management/commands/check_ai_citations.py
import json
import logging
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from yourapp.models import AICitationLog

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Check if site content is being cited by AI engines. Logs results to AICitationLog."

    def add_arguments(self, parser):
        parser.add_argument(
            "--config",
            type=str,
            default="geo_queries.json",
            help="Path to JSON config file containing target queries. Default: geo_queries.json",
        )
        parser.add_argument(
            "--engine",
            type=str,
            default="perplexity",
            choices=["perplexity", "chatgpt", "google_aio", "all"],
            help="Which AI engine to check. Default: perplexity",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print queries without calling APIs or writing to DB.",
        )

    def handle(self, *args, **options):
        config_path = Path(options["config"])
        if not config_path.exists():
            raise CommandError(
                f"Config file not found: {config_path}\n"
                "Create a JSON file like: "
                '{"queries": [{"page_id": 1, "query": "What is server-side tracking?"}]}'
            )

        with open(config_path) as f:
            config = json.load(f)

        queries = config.get("queries", [])
        if not queries:
            self.stderr.write("No queries found in config file.")
            return

        self.stdout.write(f"Checking {len(queries)} queries against {options['engine']}...")

        for item in queries:
            page_id = item.get("page_id")
            query = item.get("query", "").strip()

            if not page_id or not query:
                self.stderr.write(f"Skipping malformed item: {item}")
                continue

            if options["dry_run"]:
                self.stdout.write(f"[DRY RUN] Would check: '{query}' (page_id={page_id})")
                continue

            # --- API call stub ---
            # Replace this with your actual Perplexity/ChatGPT API integration.
            # The result should be: cited=True/False, notes=excerpt_from_response
            cited, notes = self._check_citation(query, options["engine"])

            try:
                from wagtail.models import Page
                page = Page.objects.get(pk=page_id)
            except Page.DoesNotExist:
                self.stderr.write(f"Page {page_id} not found. Skipping.")
                continue

            AICitationLog.objects.create(
                page=page,
                query=query,
                engine=options["engine"],
                cited=cited,
                checked_at=timezone.now(),
                notes=notes,
            )
            status = "✓ cited" if cited else "✗ not cited"
            self.stdout.write(f"  [{status}] '{query[:60]}'")

        self.stdout.write(self.style.SUCCESS("Done. Results saved to AICitationLog."))

    def _check_citation(self, query: str, engine: str) -> tuple[bool, str]:
        """
        Stub: Implement actual API call to the target AI engine.

        For Perplexity:
          POST https://api.perplexity.ai/chat/completions
          Check if response citations contain your domain.

        For ChatGPT (with search):
          Use OpenAI Responses API with web_search_preview tool.
          Check annotations for your domain.

        Returns: (cited: bool, notes: str)
        """
        # TODO: implement
        logger.warning("_check_citation is a stub. Implement API call for engine: %s", engine)
        return False, "Stub — not yet implemented. Check manually."
```

**Config file format (`geo_queries.json`):**

```json
{
  "queries": [
    { "page_id": 5, "query": "What is server-side tracking?" },
    { "page_id": 5, "query": "server-side tracking GDPR benefits" },
    { "page_id": 8, "query": "best Shopify analytics tools 2025" },
    { "page_id": 12, "query": "how to set up GA4 server-side tracking" }
  ]
}
```

---

## 8. HTML Rendering Constraints (Next.js)

**Rule:** All AEO blocks MUST render as visible, crawlable plain HTML. No accordion collapse in
the DOM. No content hidden behind JavaScript state. FAQ items must be `<h3>` + `<p>` in the DOM.
HowTo steps must be `<ol><li>`. Definitions must be `<dt>` + `<dd>`. Stats must be visible `<p>`
or `<div>` text. Robots and AI crawlers do not execute JavaScript — the content must be in the
initial HTML response.

---

### 8.1 AnswerBlock Component

**Required DOM output:**
```html
<div class="answer-block" itemscope itemtype="https://schema.org/Answer">
  <h3 class="answer-block__question">[question text]</h3>
  <div class="answer-block__answer" itemprop="text">
    <p>[answer paragraph]</p>
  </div>
</div>
```

```typescript
// components/blocks/AnswerBlock.tsx
interface AnswerBlockProps {
  question: string
  answer_html: string
}

export function AnswerBlock({ question, answer_html }: AnswerBlockProps) {
  // answer_html is pre-computed by the API — render directly
  return (
    <div
      className="answer-block my-8 rounded-lg border-l-4 border-blue-600 pl-6 py-4 bg-blue-50"
      itemScope
      itemType="https://schema.org/Answer"
    >
      <h3 className="answer-block__question text-lg font-semibold text-gray-900 mb-2">
        {question}
      </h3>
      <div
        className="answer-block__answer prose prose-blue"
        itemProp="text"
        dangerouslySetInnerHTML={{ __html: answer_html }}
      />
    </div>
  )
}
```

---

### 8.2 FAQBlock Component

**Required DOM output — NO ACCORDION. Every answer must be in the DOM:**
```html
<section class="faq-block" itemscope itemtype="https://schema.org/FAQPage">
  <h2 class="faq-block__heading">Frequently Asked Questions</h2>
  <div class="faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
    <h3 class="faq-item__question" itemprop="name">[question]</h3>
    <div class="faq-item__answer" itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
      <p itemprop="text">[answer]</p>
    </div>
  </div>
  <!-- repeat for each item -->
</section>
```

```typescript
// components/blocks/FAQBlock.tsx
interface FAQItem {
  question: string
  answer_html: string
}

interface FAQBlockProps {
  heading?: string
  // faq_items is the flat extracted list from the API
  items: FAQItem[]
}

export function FAQBlock({ heading, items }: FAQBlockProps) {
  if (!items?.length) return null
  return (
    <section
      className="faq-block my-12"
      itemScope
      itemType="https://schema.org/FAQPage"
    >
      {heading && (
        <h2 className="faq-block__heading text-2xl font-bold text-gray-900 mb-8">
          {heading}
        </h2>
      )}
      <div className="space-y-8">
        {items.map((item, index) => (
          <div
            key={index}
            className="faq-item"
            itemScope
            itemProp="mainEntity"
            itemType="https://schema.org/Question"
          >
            <h3
              className="faq-item__question text-lg font-semibold text-gray-900 mb-3"
              itemProp="name"
            >
              {item.question}
            </h3>
            <div
              className="faq-item__answer"
              itemScope
              itemProp="acceptedAnswer"
              itemType="https://schema.org/Answer"
            >
              {/*
                IMPORTANT: dangerouslySetInnerHTML renders the answer as visible HTML.
                DO NOT wrap in <details> or any collapsed/toggle component.
                AI crawlers must see this content in the initial HTML response.
              */}
              <div
                className="prose max-w-none text-gray-700"
                itemProp="text"
                dangerouslySetInnerHTML={{ __html: item.answer_html }}
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
```

---

### 8.3 HowToBlock Component

**Required DOM output — numbered `<ol><li>` structure:**
```html
<section class="howto-block" itemscope itemtype="https://schema.org/HowTo">
  <h2 itemprop="name">[title]</h2>
  <div itemprop="description">[intro]</div>
  <ol class="howto-steps">
    <li class="howto-step" itemprop="step" itemscope itemtype="https://schema.org/HowToStep">
      <span itemprop="position">1</span>
      <strong itemprop="name">[step title]</strong>
      <div itemprop="text">[step body]</div>
    </li>
  </ol>
</section>
```

```typescript
// components/blocks/HowToBlock.tsx
interface HowToStep {
  step_number: string
  title: string
  body_html: string
}

interface HowToBlockProps {
  title: string
  intro_html: string
  steps: HowToStep[]
  total_time?: string
}

export function HowToBlock({ title, intro_html, steps, total_time }: HowToBlockProps) {
  return (
    <section
      className="howto-block my-12"
      itemScope
      itemType="https://schema.org/HowTo"
    >
      <h2
        className="text-2xl font-bold text-gray-900 mb-4"
        itemProp="name"
      >
        {title}
      </h2>

      {total_time && (
        <p className="text-sm text-gray-500 mb-4">
          <span className="font-medium">Estimated time:</span>{' '}
          <span itemProp="totalTime">{total_time}</span>
        </p>
      )}

      <div
        className="prose mb-8 text-gray-700"
        itemProp="description"
        dangerouslySetInnerHTML={{ __html: intro_html }}
      />

      {/*
        IMPORTANT: Must be <ol> — not a styled div list.
        Steps must be visible, not toggled or hidden.
        Screen readers and crawlers rely on the ol/li structure.
      */}
      <ol className="howto-steps space-y-8 list-none pl-0">
        {steps.map((step, index) => (
          <li
            key={index}
            className="howto-step flex gap-6"
            itemProp="step"
            itemScope
            itemType="https://schema.org/HowToStep"
          >
            <span
              className="step-number flex-shrink-0 w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-sm"
              itemProp="position"
            >
              {step.step_number}
            </span>
            <div className="flex-1">
              <strong
                className="block text-lg font-semibold text-gray-900 mb-2"
                itemProp="name"
              >
                {step.title}
              </strong>
              <div
                className="prose prose-sm text-gray-700"
                itemProp="text"
                dangerouslySetInnerHTML={{ __html: step.body_html }}
              />
            </div>
          </li>
        ))}
      </ol>
    </section>
  )
}
```

---

### 8.4 StatsBlock Component

**Required DOM output — stats as visible text, not decorative:**
```html
<section class="stats-block">
  <h2>[heading]</h2>
  <ul class="stats-list">
    <li class="stat-item">
      <p class="stat-value">[value]</p>
      <p class="stat-label">[label]</p>
      <cite class="stat-source">[source, year]</cite>
    </li>
  </ul>
</section>
```

```typescript
// components/blocks/StatsBlock.tsx
interface Stat {
  value: string
  label: string
  source?: string
  year?: string
}

interface StatsBlockProps {
  heading?: string
  stats: Stat[]
}

export function StatsBlock({ heading, stats }: StatsBlockProps) {
  return (
    <section className="stats-block my-12">
      {heading && (
        <h2 className="text-2xl font-bold text-gray-900 mb-8">{heading}</h2>
      )}
      {/*
        IMPORTANT: Stats must be visible text — not canvas-rendered charts
        or SVG-only graphics without text alternatives.
        AI engines extract the text values.
      */}
      <ul className="stats-list grid grid-cols-2 md:grid-cols-3 gap-8 list-none pl-0">
        {stats.map((stat, index) => (
          <li key={index} className="stat-item text-center">
            <p className="stat-value text-4xl font-extrabold text-blue-600 mb-1">
              {stat.value}
            </p>
            <p className="stat-label text-sm font-medium text-gray-700 mb-1">
              {stat.label}
            </p>
            {(stat.source || stat.year) && (
              <cite className="stat-source text-xs text-gray-400 not-italic">
                {[stat.source, stat.year].filter(Boolean).join(", ")}
              </cite>
            )}
          </li>
        ))}
      </ul>
    </section>
  )
}
```

---

### 8.5 DefinitionBlock Component

**Required DOM output — `<dt>` / `<dd>` or `<dfn>` + `<p>`:**
```html
<div class="definition-block" itemscope itemtype="https://schema.org/DefinedTerm">
  <dt class="definition-term" itemprop="name">[term]</dt>
  <dd class="definition-body" itemprop="description">[definition]</dd>
  <p class="definition-aka">[also known as]</p>
</div>
```

```typescript
// components/blocks/DefinitionBlock.tsx
interface DefinitionBlockProps {
  term: string
  definition_html: string
  also_known_as?: string
}

export function DefinitionBlock({ term, definition_html, also_known_as }: DefinitionBlockProps) {
  return (
    <div
      className="definition-block my-8 p-6 bg-gray-50 rounded-lg border border-gray-200"
      itemScope
      itemType="https://schema.org/DefinedTerm"
    >
      <dl>
        <dt
          className="definition-term text-xl font-bold text-gray-900 mb-2"
          itemProp="name"
        >
          {term}
        </dt>
        <dd
          className="definition-body prose text-gray-700 ml-0"
          itemProp="description"
          dangerouslySetInnerHTML={{ __html: definition_html }}
        />
        {also_known_as && (
          <dd className="definition-aka text-sm text-gray-500 mt-2 ml-0">
            <span className="font-medium">Also known as:</span> {also_known_as}
          </dd>
        )}
      </dl>
    </div>
  )
}
```

---

### 8.6 StreamField Renderer

A single component that maps block types to their AEO components. AEO blocks get their
pre-extracted API data; generic blocks fall back to raw StreamField value rendering.

```typescript
// components/StreamField.tsx
import { AnswerBlock } from './blocks/AnswerBlock'
import { FAQBlock } from './blocks/FAQBlock'
import { HowToBlock } from './blocks/HowToBlock'
import { StatsBlock } from './blocks/StatsBlock'
import { DefinitionBlock } from './blocks/DefinitionBlock'
import { RichTextBlock } from './blocks/RichTextBlock'

interface StreamFieldBlock {
  type: string
  value: any
  id: string
}

interface StreamFieldProps {
  blocks: StreamFieldBlock[]
  // Pre-extracted AEO data from the Wagtail API computed fields
  answerBlocks?: Array<{ question: string; answer_html: string }>
  faqItems?: Array<{ question: string; answer_html: string }>
}

export function StreamField({ blocks, answerBlocks = [], faqItems = [] }: StreamFieldProps) {
  // Index pre-extracted AEO data by block id for O(1) lookup
  const answerMap = new Map(answerBlocks.map((a, i) => [i, a]))
  let answerIndex = 0
  let faqIndex = 0

  return (
    <div className="streamfield">
      {blocks.map((block) => {
        switch (block.type) {
          case 'answer_block': {
            // Use pre-extracted data from API computed field
            const data = answerMap.get(answerIndex++)
            if (!data) return null
            return (
              <AnswerBlock
                key={block.id}
                question={data.question}
                answer_html={data.answer_html}
              />
            )
          }

          case 'faq_block': {
            // Collect FAQ items for this block from the flat faq_items list
            const blockItemCount = (block.value?.items || []).length
            const blockItems = faqItems.slice(faqIndex, faqIndex + blockItemCount)
            faqIndex += blockItemCount
            return (
              <FAQBlock
                key={block.id}
                heading={block.value?.heading}
                items={blockItems}
              />
            )
          }

          case 'how_to_block':
            return (
              <HowToBlock
                key={block.id}
                title={block.value.title}
                intro_html={block.value.intro}
                steps={block.value.steps}
                total_time={block.value.total_time}
              />
            )

          case 'stats_block':
            return (
              <StatsBlock
                key={block.id}
                heading={block.value?.heading}
                stats={block.value?.stats || []}
              />
            )

          case 'definition_block':
            return (
              <DefinitionBlock
                key={block.id}
                term={block.value.term}
                definition_html={block.value.definition}
                also_known_as={block.value.also_known_as}
              />
            )

          case 'rich_text':
            return (
              <RichTextBlock
                key={block.id}
                html={block.value}
              />
            )

          default:
            // Unknown block type — render nothing rather than crashing
            return null
        }
      })}
    </div>
  )
}
```

---

## 9. Content Structure Rules for Editors

These rules are enforced via `help_text`, `clean()` validation, and editor documentation.
Treat this section as the onboarding document for every content editor on a Wagtail project.

**Write answer-first, not context-first.**
The first sentence of every block must contain the answer or claim. "Server-side tracking is the
process of collecting analytics data on your own server instead of the user's browser." — not
"In this article, we'll explore the concept of server-side tracking and its implications."

**Use AnswerBlocks for every question your ICP searches.**
One block per question. If your page targets "What is server-side tracking?" — that is an
AnswerBlock, not a paragraph buried in a rich text field.

**Keep FAQ answers self-contained.**
An AI engine will cite a single FAQ answer without any surrounding context. The answer to
"Is server-side tracking GDPR compliant?" must make complete sense if lifted entirely out of the
page. Never start with "Yes, as mentioned above..." or "See the previous section."

**Stats must have numbers — "significantly faster" is uncitable.**
"3× faster than client-side tracking" is a citable statistic. "Significantly faster" is not.
Always include the number. Always include the source and year if the data is external.

**Use DefinitionBlock for every technical term.**
Every piece of jargon that appears on the page gets a DefinitionBlock. "server-side tracking",
"first-party data", "GTM server container" — all defined. This is how you dominate "What is X?"
queries. One definition per term; do not define the same term twice on a site.

**Structure = citation probability.**
The more structured the content, the more extractable it is. A `FAQBlock` with 8 questions is
8 independently citable passages. A `HowToBlock` with 6 steps is a complete structured answer to
a "how to" query. A `StatsBlock` with 4 sourced statistics will be cited over a paragraph that
mentions the same numbers in prose.

**First paragraph must mention the primary entity explicitly.**
The `primary_entity` field on the page must appear by name in the first rich text block. If the
page is about "Marketing Attribution", the opening paragraph should say "marketing attribution"
within the first two sentences. This anchors AI engine entity recognition.

**search_description is not optional.**
It must be 120–160 characters and answer the core query directly. It is used in schema markup,
the API, `llms.txt`, and as the meta description. Write it as a standalone answer, not a teaser.

---

## 10. AEO/GEO Checklist — Every Wagtail Project

Run this before QA handoff on every project.

### Content Structure

- [ ] `AnswerBlock` added to all key informational pages (minimum one per page)
- [ ] `FAQBlock` on all service and product pages (minimum 5 questions per block)
- [ ] `DefinitionBlock` for all technical terms used on the site
- [ ] `StatsBlock` with sourced statistics on case study pages
- [ ] `HowToBlock` on all process/guide/tutorial content

### Schema

- [ ] `Article` schema on all blog posts (auto from `BlogPostPage._base_schema_nodes()`)
- [ ] `FAQPage` schema auto-generated from `FAQBlock`s (auto from `_schema_from_faq_blocks()`)
- [ ] `HowTo` schema auto-generated from `HowToBlock`s (auto from `_schema_from_howto_blocks()`)
- [ ] `Organization` schema in `SITE_SCHEMA` settings — verified complete
- [ ] `BreadcrumbList` on all pages (auto from `_breadcrumb_schema()`)
- [ ] Schema validated at [validator.schema.org](https://validator.schema.org/) for at least 3 page types
- [ ] All schema served as JSON-LD in `<head>` via `SchemaMarkup` component — not in page body

### API & Data Layer

- [ ] `answer_blocks` API field returns correctly extracted list
- [ ] `faq_items` API field returns flat, correctly extracted list
- [ ] `schema_markup` API field returns valid `@graph`
- [ ] `entity_map` API field returns `primary`, `type`, `mentions`
- [ ] All page models use `AEOEntityMixin` and `AEOSchemaMixin`
- [ ] `primary_entity`, `entity_type`, `mentions` filled for all published pages

### Technical

- [ ] `/llms.txt` live and accessible — content matches current published pages
- [ ] `llms.txt` cache invalidation wired via `page_published` signal
- [ ] AI crawlers allowed in `robots.txt`: `GPTBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`
- [ ] `SITE_SCHEMA` settings populated with real org data and `sameAs` social links
- [ ] `clean()` validation active — test by attempting to save a short FAQ answer

### Rendering (Next.js)

- [ ] `FAQBlock` renders as `<h3>` + `<div>` — NOT inside `<details>` or accordion toggle
- [ ] `HowToBlock` renders as `<ol><li>` — NOT as div-based visual list
- [ ] `DefinitionBlock` renders as `<dt>` + `<dd>` within a `<dl>` — visible in initial HTML
- [ ] `StatsBlock` values rendered as visible text — NOT SVG/canvas only
- [ ] `AnswerBlock` content visible in page-source view (not JS-rendered)
- [ ] Page LCP < 2.5s (AI engines consider page quality in citation ranking)

### Content Quality

- [ ] First paragraph of every page explicitly names the `primary_entity`
- [ ] No orphan definitions — every technical term used on the site has a `DefinitionBlock`
- [ ] All statistics include source and year
- [ ] No FAQ answer starts with "See above", "As mentioned", or a reference to prior content
- [ ] `search_description` on every page — 120–160 chars, answer-first
- [ ] `AICitationLog` GEO baseline check run for top 10 queries post-launch

### Monitoring

- [ ] `AICitationLog` model migrated and visible in Wagtail admin
- [ ] `geo_queries.json` config file created with at least 10 priority queries
- [ ] `check_ai_citations` management command added to cron (monthly minimum)
- [ ] GEO baseline score documented in project notes

---

*Reference maintained by the Hazn framework. Update alongside `wagtail-nextjs-stack` SKILL.md.*

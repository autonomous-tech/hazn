# Output Formats Reference

This document covers both CMS output formats produced by the `seo-blog-writer` skill.

---

## Payload CMS

### File

```
./outputs/blog-{slug}.md
```

### YAML Frontmatter Schema

The frontmatter maps to Payload's blog collection fields.

| Frontmatter Field | Payload Field | Notes |
|---|---|---|
| `title` | `title` (text) | Direct map |
| `slug` | `slug` (text, unique) | Direct map |
| `meta_title` | `meta.title` (text) | SEO title override — keep under 60 chars |
| `meta_description` | `meta.description` (textarea) | Max 160 chars |
| `tldr` | `tldr` (richText or text block) | Displayed at top of post; used in Speakable schema |
| `featured_image_alt` | Media `alt` field | Applied to the hero/featured image |
| `date` | `publishedDate` | Publication date |
| `lastModified` | `updatedAt` or custom `lastModified` | GEO freshness signal |
| `author` | `author` (relationship) | Requires human input after import |
| `author_credentials` | `author.credentials` (text) | Displayed in byline for E-E-A-T signals |
| `category` | `category` (relationship or select) | Based on site taxonomy |
| `entities` | `entities` (array block) | Knowledge graph integration |
| `schema_markup` | Injected via `generateMetadata` or JSON-LD script | In the blog post template |
| `faq_schema` | Rendered as FAQ block + JSON-LD | Use FAQBlock from Payload blocks |
| `how_to_schema` | Rendered as HowTo block + JSON-LD | Use HowToBlock from Payload blocks |
| `speakable_selectors` | Added to Speakable schema in page `<head>` | Tells Google which elements are voice-ready |

### Full YAML Frontmatter Template

```yaml
---
title: "Primary Keyword: Compelling Benefit or Hook"
slug: "primary-keyword-focused-slug"
meta_title: "Primary Keyword — Benefit Statement | Brand Name"  # Under 60 chars
meta_description: "Action-oriented description with primary keyword. Includes benefit and implicit CTA. Under 155 chars."
primary_keyword: "exact primary keyword"
supporting_keywords:
  - "keyword 1"
  - "keyword 2"
  - "keyword 3"
search_intent: "informational"
target_word_count: 2000
estimated_reading_time: "8 min"
date: "YYYY-MM-DD"
lastModified: "YYYY-MM-DD"
author: ""  # To be filled by editor
author_credentials: ""  # e.g., "10 years in B2B SaaS marketing" — GEO authority signal
category: ""  # To be filled based on site taxonomy
featured_image_alt: "Descriptive alt text containing primary keyword naturally"

# SEO
internal_links_suggested:
  - anchor: "anchor text"
    target_topic: "related topic or slug"
external_sources:
  - url: "https://example.com/study"
    context: "Cited for [specific claim]"
    type: "primary_source"  # primary_source | industry_report | official_documentation

# AEO
tldr: "2-3 sentence executive summary — the primary AI extraction target."
featured_snippet_format: "paragraph"  # paragraph | list | table | definition
paa_questions:
  - "Exact PAA question 1?"
  - "Exact PAA question 2?"
  - "Exact PAA question 3?"
voice_search_phrases:
  - "natural language voice query version"

# GEO
entities:
  - name: "Entity Name"
    type: "Organization"  # Person | Organization | Product | Concept | Technology
    relationship: "subject"  # subject | competitor | tool | framework | authority
    sameAs: "https://en.wikipedia.org/wiki/Entity"  # or official URL
citable_claims:
  - claim: "Specific statistic or definition"
    source: "Source name, year"
    context: "Where this appears in the article"
original_value: "Brief description of what's unique — original data, novel framework, contrarian insight"
content_freshness: "evergreen"  # evergreen | timely | seasonal

# Schema
schema_type: "Article"
schema_markup:
  "@context": "https://schema.org"
  "@type": "Article"
  headline: "Same as title"
  description: "Same as meta_description"
  datePublished: "YYYY-MM-DD"
  dateModified: "YYYY-MM-DD"
  author:
    "@type": "Person"
    name: ""
    url: ""
    sameAs: []  # LinkedIn, Twitter, etc.
  publisher:
    "@type": "Organization"
    name: ""
    url: ""
    logo:
      "@type": "ImageObject"
      url: ""
  mainEntityOfPage:
    "@type": "WebPage"
    "@id": ""
faq_schema:  # Only if FAQ section exists
  - question: "Question from the article?"
    answer: "Concise answer from the article."
how_to_schema: null  # Populate if article contains step-by-step instructions
  # "@type": "HowTo"
  # name: "How to..."
  # step:
  #   - "@type": "HowToStep"
  #     name: "Step 1 name"
  #     text: "Step 1 description"
speakable_selectors:  # CSS selectors for content optimized for voice/TTS
  - ".tldr"
  - ".key-takeaway"
  - ".faq-answer"
---
```

### Payload Blocks for AEO/GEO

These blocks must exist in the Payload blog collection to render AEO/GEO elements properly:

| Block | Class | Purpose |
|---|---|---|
| `TLDRBlock` | `.tldr` | Executive summary — primary AI extraction target; Speakable selector |
| `KeyTakeawayBlock` | `.key-takeaway` | Blockquote-style callout under each H2; secondary extraction target |
| `DefinitionBlock` | `.definition` | "[Term] is [definition]" with Definition schema markup |
| `EntityMentionBlock` | `.entity-mention` | Inline entity reference with `sameAs` link for knowledge graph |

---

## Wagtail

### Files

```
./outputs/blog-{slug}.md               ← markdown body (for human review and editing)
./outputs/blog-{slug}-wagtail.json     ← import-ready JSON for Django management command
```

### SEO Fields Mapping

| Frontmatter field | Wagtail field | Notes |
|---|---|---|
| `title` | `page.title` | Wagtail `Page.title` |
| `meta_title` / `seo_title` | `page.seo_title` | Wagtail `Page.seo_title`; keep under 60 chars |
| `meta_description` | `page.search_description` | Wagtail `Page.search_description`; under 160 chars |
| `slug` | `page.slug` | URL-safe slug |
| `schema_markup` | `page.schema_markup` | Custom JSON field on `BlogPostPage` |
| `keywords` / `supporting_keywords` | `page.tags` | Mapped to `ClusterTaggableManager` tags |
| `canonical` / `canonical_url` | `page.canonical_url` | Custom `URLField` on `BlogPostPage` |
| `author` | `page.author` | `CharField` on `BlogPostPage` |
| `date` | `page.publish_date` | `DateField` on `BlogPostPage` |
| `tldr` / opening paragraph | `page.intro` | Plain text, no markdown — maps to `TextField` |

### Wagtail Import JSON Schema

```json
{
  "import_format": "wagtail_blog_post",
  "version": "1.0",
  "page": {
    "title": "Full post title",
    "slug": "url-safe-slug",
    "seo_title": "SEO title (under 60 chars)",
    "search_description": "Meta description (under 160 chars)",
    "intro": "One-paragraph intro as plain text — no markdown. Populates the intro TextField.",
    "author": "Author full name",
    "publish_date": "2026-03-12",
    "canonical_url": "",
    "schema_type": "Article",
    "tags": ["tag-one", "tag-two", "tag-three"],
    "categories": ["category-slug"],
    "body": [
      {
        "type": "rich_text",
        "value": "<h2>Section Heading</h2><p>Section body content with <strong>emphasis</strong> where needed.</p><p>Second paragraph of this section.</p>"
      },
      {
        "type": "rich_text",
        "value": "<h2>Another Section</h2><p>Content here.</p><ul><li>List item one</li><li>List item two</li></ul>"
      },
      {
        "type": "quote_block",
        "value": {
          "quote": "The pull quote text here.",
          "attribution": "Source name or publication"
        }
      },
      {
        "type": "cta_block",
        "value": {
          "heading": "Ready to get started?",
          "body": "Brief CTA body text explaining the next step.",
          "primary_cta_text": "Get Started",
          "primary_cta_url": "/contact/"
        }
      },
      {
        "type": "faq_block",
        "value": {
          "items": [
            {
              "question": "What is [concept]?",
              "answer": "Direct one-to-two sentence answer. Then expand briefly."
            },
            {
              "question": "How does [process] work?",
              "answer": "Direct answer first. Then context."
            }
          ]
        }
      }
    ],
    "schema_markup": {
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "Same as title",
      "description": "Same as search_description",
      "author": {
        "@type": "Person",
        "name": "Author Name"
      },
      "datePublished": "2026-03-12",
      "dateModified": "2026-03-12",
      "publisher": {
        "@type": "Organization",
        "name": "Autonomous Technologies",
        "url": "https://autonomoustech.ca"
      }
    }
  },
  "entity_map": ["Entity One", "Entity Two", "Entity Three"],
  "answer_blocks": ["What question does this post directly answer?"],
  "internal_link_opportunities": ["/related-page/", "/another-relevant-page/"]
}
```

### StreamField Body Block Types

Map blog content sections to Wagtail StreamField blocks as follows:

| Content Section | Block Type | Notes |
|---|---|---|
| Introduction paragraph | `rich_text` | First block after `intro` field is set |
| H2 section with body copy | `rich_text` | Keep headings inside the `rich_text` value for long-form continuity |
| FAQ section | `faq_block` | Structured as `{ items: [{question, answer}] }` |
| Call-to-action | `cta_block` | Structured with `heading`, `body`, `primary_cta_text`, `primary_cta_url` |
| Stats or data table | `rich_text` | Use `<table>` inside the rich_text HTML value |
| Pull quote | `quote_block` | Structured as `{ quote, attribution }` |
| Embedded video/media | `embed_block` | Structured as `{ url }` — Wagtail handles oEmbed |
| Numbered steps / HowTo | `rich_text` | Use `<ol><li>` inside rich_text; supplement with HowTo schema in `schema_markup` |

#### Rich Text Formatting Rules

When building `rich_text` block values, use HTML (not markdown):

- Headings: `<h2>`, `<h3>` — H2 for major sections, H3 for subsections
- Paragraphs: `<p>...</p>`
- Bold: `<strong>...</strong>`
- Italic: `<em>...</em>`
- Unordered lists: `<ul><li>...</li></ul>`
- Ordered lists: `<ol><li>...</li></ol>`
- Tables: `<table><thead><tr><th>...</th></tr></thead><tbody><tr><td>...</td></tr></tbody></table>`
- Links: `<a href="...">anchor text</a>` — use full paths for internal links

**Do not** include raw markdown in `rich_text` values — Wagtail's rich text renderer expects HTML.

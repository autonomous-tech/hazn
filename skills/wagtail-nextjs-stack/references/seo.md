# SEO Reference — Wagtail + Next.js Stack

SEO is a first-class concern in every project built on this stack. These patterns are not optional — they are baked into every page model, API response, and frontend route from day one.

---

## Table of Contents

1. [SEO-First Page Model Design](#1-seo-first-page-model-design)
2. [Page-Type Specific Schema Markup](#2-page-type-specific-schema-markup)
   - [BlogPostPage — Article](#blogpostpage--article)
   - [CaseStudyPage — CaseStudy + BreadcrumbList](#casestudypage--casestudy--breadcrumblist)
   - [MarketingPage / HomePage — WebSite + Organization](#marketingpage--homepage--website--organization)
   - [FAQPage — FAQPage schema from FAQBlocks](#faqpage--faqpage-schema-from-faqblocks)
3. [Sitemap Configuration](#3-sitemap-configuration)
4. [robots.txt](#4-robotstxt)
5. [Headless SEO API Fields](#5-headless-seo-api-fields)
6. [Next.js: Consuming SEO from Wagtail API](#6-nextjs-consuming-seo-from-wagtail-api)
   - [generateMetadata pattern](#generatemetadata-pattern)
   - [JSON-LD component](#json-ld-component)
   - [Sitemap from Wagtail](#sitemap-from-wagtail)
   - [robots.ts](#robotsts)
7. [AEO/GEO Patterns in Wagtail](#7-aeogeo-patterns-in-wagtail)
   - [FAQ blocks for featured snippets](#faq-blocks-for-featured-snippets)
   - [Answer blocks for AI citation](#answer-blocks-for-ai-citation)
   - [llms.txt generation](#llmstxt-generation)
8. [ISR + Cache Invalidation for SEO](#8-isr--cache-invalidation-for-seo)
   - [Wagtail webhook → Next.js revalidate](#wagtail-webhook--nextjs-revalidate)
9. [SEO Checklist — Every Wagtail + Next.js Project](#9-seo-checklist--every-wagtail--nextjs-project)

---

## 1. SEO-First Page Model Design

Every page model must extend `BasePage`, which ships with full SEO fields out of the box. Wagtail already provides `seo_title` and `search_description` on the base `Page` model — `BasePage` extends that with OG image, canonical URL, noindex control, and a JSON-LD hook.

```python
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from django.db import models
from wagtail.api.v2.views import APIField


class BasePage(Page):
    """Abstract base page with SEO built in. All page models extend this."""

    og_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Image for social sharing. Recommended: 1200x630px.'
    )
    canonical_url = models.URLField(
        blank=True,
        help_text='Only set if this page has a canonical URL different from its Wagtail URL.'
    )
    noindex = models.BooleanField(
        default=False,
        help_text='Check to prevent search engines from indexing this page.'
    )

    # Wagtail built-ins (shown here for reference — already on Page):
    # seo_title: CharField — shown in search results instead of title
    # search_description: TextField — meta description

    class Meta:
        abstract = True

    promote_panels = Page.promote_panels + [
        MultiFieldPanel([
            FieldPanel('og_image'),
            FieldPanel('canonical_url'),
            FieldPanel('noindex'),
        ], heading='Advanced SEO'),
    ]

    def get_schema_markup(self):
        """Override in subclasses to return page-type-specific JSON-LD dict."""
        return {
            '@context': 'https://schema.org',
            '@type': 'WebPage',
            'name': self.seo_title or self.title,
            'description': self.search_description,
            'url': self.full_url,
        }

    # api_fields are declared on each concrete page model (see Section 5).
    # The schema_markup field uses a custom serializer — see SchemaMarkupField below.
```

**Why every field matters:**

| Field | Purpose |
|---|---|
| `og_image` | Controls the image shown when shared on social media and in AI summaries |
| `canonical_url` | Prevents duplicate content penalties for paginated or multi-URL content |
| `noindex` | Excludes staging pages, thank-you pages, and internal tools from indexing |
| `seo_title` (built-in) | Shown in the `<title>` tag — separate from the page's display heading |
| `search_description` (built-in) | Meta description — affects CTR, not ranking |

---

## 2. Page-Type Specific Schema Markup

Every concrete page type must override `get_schema_markup()`. The default `WebPage` type from `BasePage` is a fallback only — page-specific schema dramatically improves rich result eligibility.

### BlogPostPage — Article

```python
from django.conf import settings

class BlogPostPage(BasePage):
    # ... your content fields ...

    def get_schema_markup(self):
        return {
            '@context': 'https://schema.org',
            '@type': 'Article',
            'headline': self.seo_title or self.title,
            'description': self.search_description,
            'datePublished': str(self.publish_date),
            'dateModified': str(self.last_published_at.date()),
            'author': {
                '@type': 'Person',
                'name': self.author,
            },
            'publisher': {
                '@type': 'Organization',
                'name': settings.WAGTAIL_SITE_NAME,
                'url': settings.WAGTAILADMIN_BASE_URL,
            },
            'image': (
                self.og_image.get_rendition('fill-1200x630').url
                if self.og_image else None
            ),
        }
```

### CaseStudyPage — CaseStudy + BreadcrumbList

```python
class CaseStudyPage(BasePage):

    def get_schema_markup(self):
        return [
            {
                '@context': 'https://schema.org',
                '@type': 'Article',
                '@id': f'{self.full_url}#article',
                'headline': self.seo_title or self.title,
                'description': self.search_description,
                'datePublished': str(self.first_published_at.date()),
                'dateModified': str(self.last_published_at.date()),
                'author': {
                    '@type': 'Organization',
                    'name': settings.WAGTAIL_SITE_NAME,
                },
                'image': (
                    self.og_image.get_rendition('fill-1200x630').url
                    if self.og_image else None
                ),
            },
            {
                '@context': 'https://schema.org',
                '@type': 'BreadcrumbList',
                'itemListElement': [
                    {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': self.get_site().root_page.full_url},
                    {'@type': 'ListItem', 'position': 2, 'name': 'Case Studies', 'item': self.get_parent().full_url},
                    {'@type': 'ListItem', 'position': 3, 'name': self.title, 'item': self.full_url},
                ],
            },
        ]
```

> **Note:** When `get_schema_markup()` returns a list, the Next.js `JsonLd` component must handle both array and object forms — render one `<script>` tag per schema object.

### MarketingPage / HomePage — WebSite + Organization

```python
class HomePage(BasePage):

    def get_schema_markup(self):
        site = self.get_site()
        return [
            {
                '@context': 'https://schema.org',
                '@type': 'WebSite',
                'url': site.root_page.full_url,
                'name': settings.WAGTAIL_SITE_NAME,
                'potentialAction': {
                    '@type': 'SearchAction',
                    'target': {
                        '@type': 'EntryPoint',
                        'urlTemplate': f'{site.root_page.full_url}search/?q={{search_term_string}}',
                    },
                    'query-input': 'required name=search_term_string',
                },
            },
            {
                '@context': 'https://schema.org',
                '@type': 'Organization',
                'url': site.root_page.full_url,
                'name': settings.WAGTAIL_SITE_NAME,
                'logo': settings.ORG_LOGO_URL,  # set in Django settings
                'sameAs': settings.ORG_SOCIAL_URLS,  # list of social profile URLs
            },
        ]
```

### FAQPage — FAQPage schema from FAQBlocks

Auto-detect FAQ blocks in StreamField body and emit `FAQPage` schema:

```python
class MarketingPage(BasePage):
    body = StreamField([...])  # includes FAQBlock

    def _get_faq_items(self):
        """Extract all FAQ items from StreamField body."""
        items = []
        for block in self.body:
            if block.block_type == 'faq_block':
                for faq in block.value.get('items', []):
                    items.append({
                        '@type': 'Question',
                        'name': str(faq['question']),
                        'acceptedAnswer': {
                            '@type': 'Answer',
                            'text': str(faq['answer']),
                        },
                    })
        return items

    def get_schema_markup(self):
        faq_items = self._get_faq_items()
        schemas = [super().get_schema_markup()]
        if faq_items:
            schemas.append({
                '@context': 'https://schema.org',
                '@type': 'FAQPage',
                'mainEntity': faq_items,
            })
        return schemas if len(schemas) > 1 else schemas[0]
```

> **Critical:** FAQ blocks must render questions as `<h3>` and answers as `<p>` in the Next.js component — **not** as collapsed accordions. Google needs to read the text in the HTML to extract FAQ rich results.

---

## 3. Sitemap Configuration

### Basic setup

```python
# settings.py
INSTALLED_APPS += ['wagtail.contrib.sitemaps']

# urls.py
from wagtail.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap

sitemaps = {'wagtail': Sitemap}
urlpatterns += [
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap',
    ),
]
```

### Custom sitemap excluding noindex pages

```python
from wagtail.contrib.sitemaps import Sitemap as WagtailSitemap


class SEOSitemap(WagtailSitemap):
    def items(self):
        return super().items().filter(noindex=False)

    def changefreq(self, obj):
        if hasattr(obj, 'publish_date'):
            return 'monthly'
        return 'weekly'

    def priority(self, obj):
        if obj.depth == 2:  # root-level pages
            return 1.0
        return 0.8


# urls.py — use SEOSitemap instead of Sitemap
sitemaps = {'wagtail': SEOSitemap}
```

---

## 4. robots.txt

Serve `robots.txt` dynamically so the sitemap URL is always correct across environments:

```python
# views.py
from django.conf import settings
from django.http import HttpResponse


def robots_txt(request):
    lines = [
        'User-agent: *',
        'Allow: /',
        f'Sitemap: {settings.WAGTAILADMIN_BASE_URL}/sitemap.xml',
    ]
    # Block staging/admin paths
    disallowed = ['/admin/', '/django-admin/', '/api/']
    for path in disallowed:
        lines.insert(1, f'Disallow: {path}')
    return HttpResponse('\n'.join(lines), content_type='text/plain')


# urls.py
from . import views
urlpatterns += [
    path('robots.txt', views.robots_txt),
]
```

> **Environment note:** In staging/preview environments, set `WAGTAILADMIN_BASE_URL` to the staging domain and prepend `Disallow: /` to block all indexing. Use an environment variable flag to toggle this — never deploy staging content to the public index.

---

## 5. Headless SEO API Fields

All SEO data must be exposed via Wagtail API v2 so Next.js can consume it without any server-side rendering on the Django side.

```python
from wagtail.api.v2.views import APIField
from wagtail.images.api.fields import ImageRenditionField
from rest_framework import serializers


class SchemaMarkupField(serializers.Field):
    """Serializes the result of get_schema_markup() — handles both dict and list."""
    def to_representation(self, page):
        return page.get_schema_markup()


# On BasePage or each concrete page model:
api_fields = [
    APIField('seo_title'),
    APIField('search_description'),
    APIField('og_image', serializer=ImageRenditionField('fill-1200x630')),
    APIField('canonical_url'),
    APIField('noindex'),
    APIField('schema_markup', serializer=SchemaMarkupField(source='*')),
]
```

**What the API response looks like:**

```json
{
  "id": 5,
  "title": "How We Cut Churn by 40%",
  "seo_title": "40% Churn Reduction — Case Study | Acme",
  "search_description": "Learn how we helped Acme reduce monthly churn by 40% in 90 days using behavioural cohort analysis.",
  "og_image": {
    "url": "https://cdn.example.com/images/case-study-og.fill-1200x630.jpg",
    "width": 1200,
    "height": 630
  },
  "canonical_url": "",
  "noindex": false,
  "schema_markup": {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "40% Churn Reduction — Case Study | Acme"
  }
}
```

---

## 6. Next.js: Consuming SEO from Wagtail API

### TypeScript types

```typescript
// types/wagtail.ts

export interface WagtailPageMeta {
  type: string
  detail_url: string
  html_url: string
  slug: string
  show_in_menus: boolean
  seo_title: string
  search_description: string
  first_published_at: string
  latest_revision_created_at: string
  parent: { id: number; meta: WagtailPageMeta; title: string } | null
}

export interface WagtailSEOFields {
  og_image: { url: string; width: number; height: number } | null
  canonical_url: string
  noindex: boolean
  schema_markup: Record<string, unknown> | Record<string, unknown>[]
}

export type WagtailPage = {
  id: number
  title: string
  meta: WagtailPageMeta
} & WagtailSEOFields
```

### generateMetadata pattern

```typescript
// app/[...slug]/page.tsx
import type { Metadata } from 'next'
import { getPageBySlug } from '@/lib/wagtail'

interface Props {
  params: { slug: string[] }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const page = await getPageBySlug(params.slug.join('/'))
  if (!page) return {}

  return {
    title: page.meta.seo_title || page.title,
    description: page.meta.search_description,
    robots: page.noindex
      ? { index: false, follow: false }
      : { index: true, follow: true },
    alternates: {
      canonical: page.canonical_url || page.meta.html_url,
    },
    openGraph: {
      title: page.meta.seo_title || page.title,
      description: page.meta.search_description,
      url: page.meta.html_url,
      type: 'website',
      images: page.og_image
        ? [{
            url: page.og_image.url,
            width: page.og_image.width,
            height: page.og_image.height,
            alt: page.meta.seo_title || page.title,
          }]
        : [],
    },
    twitter: {
      card: 'summary_large_image',
      title: page.meta.seo_title || page.title,
      description: page.meta.search_description,
      images: page.og_image ? [page.og_image.url] : [],
    },
  }
}
```

### JSON-LD component

```typescript
// components/JsonLd.tsx
type SchemaMarkup = Record<string, unknown> | Record<string, unknown>[]

interface JsonLdProps {
  data: SchemaMarkup
}

export function JsonLd({ data }: JsonLdProps) {
  const schemas = Array.isArray(data) ? data : [data]
  return (
    <>
      {schemas.map((schema, i) => (
        <script
          key={i}
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
        />
      ))}
    </>
  )
}

// Usage in page.tsx — render in the layout, not a client component:
// {page.schema_markup && <JsonLd data={page.schema_markup} />}
```

### Sitemap from Wagtail

```typescript
// app/sitemap.ts
import type { MetadataRoute } from 'next'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const res = await fetch(
    `${process.env.WAGTAIL_API_URL}/api/v2/pages/?fields=meta&limit=1000&format=json`,
    { next: { revalidate: 3600 } } // revalidate sitemap hourly
  )
  const data = await res.json()

  return data.items
    .filter((page: any) => !page.noindex)
    .map((page: any) => ({
      url: page.meta.html_url,
      lastModified: new Date(page.meta.latest_revision_created_at),
      changeFrequency: 'weekly' as const,
      priority: page.meta.slug === '' ? 1 : 0.8,
    }))
}
```

### robots.ts

```typescript
// app/robots.ts
import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL ?? 'https://example.com'
  const isProduction = process.env.NODE_ENV === 'production'

  return {
    rules: isProduction
      ? { userAgent: '*', allow: '/', disallow: ['/admin/', '/api/'] }
      : { userAgent: '*', disallow: '/' }, // block all in non-production
    sitemap: `${baseUrl}/sitemap.xml`,
  }
}
```

---

## 7. AEO/GEO Patterns in Wagtail

AEO (Answer Engine Optimization) and GEO (Generative Engine Optimization) extend traditional SEO to optimize for AI-generated answers in ChatGPT, Perplexity, Google AI Overviews, and Claude.

### FAQ blocks for featured snippets

```typescript
// components/blocks/FaqBlock.tsx
// CRITICAL: questions must be <h3>, answers must be <p> — not accordions
// Google and AI engines read the visible DOM to extract Q&A pairs.

interface FaqItem {
  question: string
  answer: string
}

interface FaqBlockProps {
  items: FaqItem[]
}

export function FaqBlock({ items }: FaqBlockProps) {
  return (
    <section className="faq-block">
      <h2>Frequently Asked Questions</h2>
      <dl>
        {items.map((item, i) => (
          <div key={i} className="faq-item">
            <dt>
              <h3>{item.question}</h3>
            </dt>
            <dd>
              <p>{item.answer}</p>
            </dd>
          </div>
        ))}
      </dl>
    </section>
  )
}
```

Auto-detect FAQ blocks and append `FAQPage` schema:

```typescript
// lib/schema.ts
export function buildSchemaForPage(page: WagtailPage): Record<string, unknown>[] {
  const schemas: Record<string, unknown>[] = []

  // Base schema from Wagtail
  if (page.schema_markup) {
    const base = Array.isArray(page.schema_markup) ? page.schema_markup : [page.schema_markup]
    schemas.push(...base)
  }

  // Auto-add FAQPage schema if body contains faq_block
  const faqBlocks = page.body?.filter((b: any) => b.type === 'faq_block') ?? []
  if (faqBlocks.length > 0) {
    const faqItems = faqBlocks.flatMap((b: any) =>
      b.value.items.map((item: any) => ({
        '@type': 'Question',
        name: item.question,
        acceptedAnswer: { '@type': 'Answer', text: item.answer },
      }))
    )
    schemas.push({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: faqItems,
    })
  }

  return schemas
}
```

### Answer blocks for AI citation

AI answer engines (Perplexity, Claude, GPT-4o search) favor content that directly answers a question in the first 2-3 sentences of a section.

**Content authoring rules** (document for editors):
- Every H2 section should open with a direct 1-2 sentence answer to the implied question
- Named entities (people, companies, products, dates) must appear in the first paragraph of articles
- Avoid vague openers like "In this article, we will discuss..." — lead with the answer

**AnswerBlock in Wagtail:**

```python
# blocks.py
from wagtail.blocks import StructBlock, CharBlock, TextBlock

class AnswerBlock(StructBlock):
    """Short answer block for AI citability. Renders as a highlighted definition."""
    question = CharBlock(help_text='The question this answers (used for schema, not displayed)')
    answer = TextBlock(help_text='2-3 sentence direct answer. No waffle.')

    class Meta:
        icon = 'help'
        label = 'Answer Block'
        template = 'blocks/answer_block.html'
```

```html
<!-- templates/blocks/answer_block.html -->
<div class="answer-block" itemscope itemtype="https://schema.org/Question">
  <meta itemprop="name" content="{{ value.question }}" />
  <div itemprop="acceptedAnswer" itemscope itemtype="https://schema.org/Answer">
    <p itemprop="text">{{ value.answer }}</p>
  </div>
</div>
```

### llms.txt generation

`llms.txt` tells AI crawlers what your site contains and which pages are authoritative. Place it at `https://yourdomain.com/llms.txt`.

```typescript
// app/llms.txt/route.ts
import { getAllPublishedPages } from '@/lib/wagtail'

export async function GET() {
  const pages = await getAllPublishedPages()

  const homePage = pages.find((p: any) => p.meta.slug === '')
  const blogPosts = pages.filter((p: any) => p.meta.type === 'blog.BlogPostPage')
  const caseStudies = pages.filter((p: any) => p.meta.type === 'case_studies.CaseStudyPage')
  const marketingPages = pages.filter((p: any) => p.meta.type === 'pages.MarketingPage')

  const lines = [
    `# ${process.env.SITE_NAME}`,
    `> ${process.env.SITE_DESCRIPTION}`,
    '',
    '## Pages',
    ...marketingPages.map((p: any) =>
      `- [${p.title}](${p.meta.html_url}): ${p.meta.search_description}`
    ),
    '',
    '## Case Studies',
    ...caseStudies.map((p: any) =>
      `- [${p.title}](${p.meta.html_url}): ${p.meta.search_description}`
    ),
    '',
    '## Blog',
    ...blogPosts.map((p: any) =>
      `- [${p.title}](${p.meta.html_url}): ${p.meta.search_description}`
    ),
  ]

  return new Response(lines.join('\n'), {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  })
}
```

> **Note:** `llms.txt` is cached by AI crawlers. Set `revalidate` to 86400 (24h) in the page fetch so it doesn't hammer your Wagtail API on every request.

---

## 8. ISR + Cache Invalidation for SEO

Marketing pages must be statically generated (`generateStaticParams` + ISR) so they serve instantly with full SEO metadata. They must also revalidate immediately on publish — not on the next request.

### Wagtail webhook → Next.js revalidate

**Django side — fire after publish:**

```python
# wagtail_hooks.py
from django.conf import settings
from wagtail import hooks
import requests
import logging

logger = logging.getLogger(__name__)


@hooks.register('after_publish_page')
def trigger_nextjs_revalidate(request, page):
    """Ping Next.js revalidation endpoint whenever a page is published."""
    nextjs_url = getattr(settings, 'NEXTJS_URL', None)
    revalidate_secret = getattr(settings, 'REVALIDATE_SECRET', None)

    if not nextjs_url or not revalidate_secret:
        return  # silently skip if not configured

    try:
        response = requests.post(
            f"{nextjs_url}/api/revalidate",
            json={
                'slug': page.slug,
                'full_path': page.url_path,
                'secret': revalidate_secret,
            },
            timeout=5,
        )
        response.raise_for_status()
        logger.info(f"Revalidated Next.js for page: {page.slug}")
    except Exception as e:
        # Never block a publish because Next.js is unreachable
        logger.warning(f"Next.js revalidation failed for {page.slug}: {e}")
```

**Next.js side — revalidation endpoint:**

```typescript
// app/api/revalidate/route.ts
import { revalidatePath, revalidateTag } from 'next/cache'
import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  const { slug, full_path, secret } = await request.json()

  if (secret !== process.env.REVALIDATE_SECRET) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // Revalidate the specific page path
  if (slug) {
    revalidatePath(`/${slug}`)
  }

  // Always revalidate homepage (nav/footer might reference this page)
  revalidatePath('/')

  // Revalidate sitemap
  revalidateTag('sitemap')

  return NextResponse.json({ revalidated: true, slug })
}
```

**generateStaticParams for all Wagtail pages:**

```typescript
// app/[...slug]/page.tsx
export async function generateStaticParams() {
  const res = await fetch(
    `${process.env.WAGTAIL_API_URL}/api/v2/pages/?fields=meta&limit=500`,
    { next: { tags: ['sitemap'] } }
  )
  const data = await res.json()

  return data.items.map((page: any) => ({
    slug: page.meta.slug ? page.meta.slug.split('/') : [],
  }))
}

// Page-level revalidation fallback (in case webhook fails):
export const revalidate = 3600 // 1 hour
```

---

## 9. SEO Checklist — Every Wagtail + Next.js Project

Run this checklist before QA handoff. Every item is a blocking requirement.

### Django/Wagtail

- [ ] `BasePage` abstract model has `og_image`, `canonical_url`, `noindex` fields
- [ ] All page types extend `BasePage` (not raw `Page`)
- [ ] All page types implement `get_schema_markup()` — no defaults left unchecked
- [ ] All SEO fields exposed via `api_fields` (seo_title, search_description, og_image, canonical_url, noindex, schema_markup)
- [ ] `SEOSitemap` at `/sitemap.xml` excludes `noindex=True` pages
- [ ] `robots.txt` view pointing to sitemap, blocking `/admin/` and `/api/`
- [ ] `after_publish_page` Wagtail hook fires revalidation webhook to Next.js
- [ ] `SiteSettings` or Django settings contain Organization schema data (name, logo, socials)

### Next.js Frontend

- [ ] `generateMetadata` implemented on all dynamic page routes
- [ ] `JsonLd` component renders in `<head>` (not inside `<body>` content) for all pages
- [ ] `app/sitemap.ts` fetches from Wagtail API and filters noindex pages
- [ ] `app/robots.ts` configured — blocks all in non-production environments
- [ ] `app/llms.txt/route.ts` live and returning valid llms.txt format
- [ ] ISR revalidation endpoint at `/api/revalidate` — tested with a real publish event
- [ ] All images use `next/image` with explicit `width` and `height` from Wagtail rendition API (prevents CLS)
- [ ] Core Web Vitals: LCP image preloaded with `priority` prop on hero images
- [ ] OG image set for homepage, all landing pages, all blog posts before launch

### Content (Editor Checklist)

Share this with the content team before launch:

- [ ] `seo_title` set on all published pages (≤ 60 characters)
- [ ] `search_description` set on all published pages (≤ 160 characters)
- [ ] `og_image` set on homepage, all landing pages, all blog posts
- [ ] Tags and categories applied to all blog posts
- [ ] No page left with `seo_title` equal to its display title (they should be optimised separately)
- [ ] FAQ blocks used for common questions — not buried in rich text

### Post-Launch Verification

- [ ] Run `https://search.google.com/test/rich-results` on homepage, a blog post, and a case study
- [ ] Verify `llms.txt` is accessible at `https://yourdomain.com/llms.txt`
- [ ] Submit sitemap to Google Search Console
- [ ] Check Wagtail publish → Next.js revalidation latency (should be < 10 seconds)
- [ ] Confirm staging site returns `Disallow: /` in robots.txt

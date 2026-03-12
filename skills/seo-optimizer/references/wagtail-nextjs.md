# SEO Optimization — Django + Wagtail (Headless) + Next.js

Reference for projects using Wagtail CMS (LTS) as a headless backend with Next.js as the frontend.

---

## 1. Django/Wagtail Backend SEO

### Base Page SEO Fields

Wagtail provides `seo_title` and `search_description` on every `Page` model out of the box (via the Promote tab). Extend every base page with additional SEO fields:

```python
# models/base.py
from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, ObjectList, TabbedInterface
from wagtail.images.edit_handlers import FieldPanel as ImageFieldPanel


class BasePage(Page):
    """Abstract base page — all page models inherit from this."""

    # Custom SEO fields (seo_title & search_description are already on Page)
    og_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Image for Open Graph / social sharing (1200×630px recommended)',
    )
    canonical_url = models.URLField(
        blank=True,
        help_text='Override the canonical URL. Leave blank to use the default page URL.',
    )
    noindex = models.BooleanField(
        default=False,
        help_text='Prevent search engines from indexing this page.',
    )

    # Extend the default Promote tab
    promote_panels = Page.promote_panels + [
        MultiFieldPanel([
            ImageFieldPanel('og_image'),
            FieldPanel('canonical_url'),
            FieldPanel('noindex'),
        ], heading='Advanced SEO'),
    ]

    class Meta:
        abstract = True
```

All page models inherit from `BasePage` instead of `Page`:

```python
# models/blog.py
class BlogPostPage(BasePage):
    body = StreamField([...])
    author = models.CharField(max_length=255)
    published_date = models.DateField(auto_now_add=True)

    content_panels = BasePage.content_panels + [
        FieldPanel('body'),
        FieldPanel('author'),
    ]
```

---

### wagtail-seo Package (Springload)

`wagtail-seo` adds a dedicated SEO tab and additional fields to all pages.

**Installation:**

```bash
pip install wagtail-seo
```

**settings.py:**

```python
INSTALLED_APPS = [
    ...
    'wagtailseo',
]

# Optional: set default Twitter card type
WAGTAILSEO_TWITTER_CARD = 'summary_large_image'
```

**Mixin approach** (alternative to the manual `BasePage` above):

```python
from wagtailseo.models import SeoMixin

class BlogPostPage(SeoMixin, Page):
    # SeoMixin adds: seo_image, seo_description, twitter_url, etc.
    # Plus a full SEO tab in the admin
    promote_panels = SeoMixin.seo_panels + Page.promote_panels
```

`SeoMixin` fields include: `seo_image`, `og_title`, `og_description`, Twitter card fields, and structured data helpers. It also validates that required SEO fields are filled before publishing.

---

### Structured Data / JSON-LD

#### Approach: Expose JSON-LD as API fields

Rather than rendering structured data server-side in Django templates, expose it as a computed API field. Next.js renders it in `<script type="application/ld+json">`.

**Custom API serializer field:**

```python
# api/serializers.py
from wagtail.api.v2.serializers import PageSerializer
from rest_framework import serializers
import json


class SeoDataField(serializers.Field):
    """Computes and returns JSON-LD structured data for a page."""

    def to_representation(self, page):
        return page.get_structured_data()  # defined on BasePage or per model


class BasePageSerializer(PageSerializer):
    structured_data = SeoDataField(source='*')
    og_image = serializers.SerializerMethodField()
    canonical_url = serializers.CharField()
    noindex = serializers.BooleanField()

    def get_og_image(self, page):
        if page.og_image:
            return {
                'url': page.og_image.get_rendition('fill-1200x630').url,
                'width': 1200,
                'height': 630,
                'alt': page.og_image.title,
            }
        return None
```

#### Article Schema (BlogPostPage)

```python
# models/blog.py
class BlogPostPage(BasePage):
    def get_structured_data(self):
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": self.seo_title or self.title,
            "description": self.search_description,
            "author": {
                "@type": "Person",
                "name": self.author,
            },
            "datePublished": self.published_date.isoformat(),
            "dateModified": self.last_published_at.isoformat() if self.last_published_at else None,
            "image": self.og_image.get_rendition('fill-1200x630').url if self.og_image else None,
            "url": self.full_url,
        }
```

#### Organization Schema (SiteSettings)

```python
# settings_models.py
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel


@register_setting
class SeoSettings(BaseSiteSetting):
    org_name = models.CharField(max_length=255, blank=True)
    org_logo = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    twitter_handle = models.CharField(max_length=255, blank=True)
    linkedin_url = models.URLField(blank=True)

    panels = [
        FieldPanel('org_name'),
        FieldPanel('org_logo'),
        FieldPanel('twitter_handle'),
        FieldPanel('linkedin_url'),
    ]

    def get_organization_schema(self):
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": self.org_name,
            "logo": self.org_logo.get_rendition('original').url if self.org_logo else None,
            "sameAs": [
                f"https://twitter.com/{self.twitter_handle}" if self.twitter_handle else None,
                self.linkedin_url or None,
            ],
        }
```

#### BreadcrumbList Schema from Page Ancestry

```python
# models/base.py (method on BasePage)
def get_breadcrumb_schema(self):
    ancestors = self.get_ancestors(inclusive=True).filter(depth__gte=2)
    items = []
    for i, page in enumerate(ancestors, start=1):
        items.append({
            "@type": "ListItem",
            "position": i,
            "name": page.title,
            "item": page.full_url,
        })
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }
```

#### FAQPage Schema from FAQBlock

```python
# blocks.py
from wagtail.blocks import StructBlock, CharBlock, RichTextBlock, ListBlock


class FAQItemBlock(StructBlock):
    question = CharBlock()
    answer = RichTextBlock()

    class Meta:
        icon = 'help'


class FAQBlock(ListBlock):
    def __init__(self):
        super().__init__(FAQItemBlock())

    def get_schema(self, value):
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item['question'],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": item['answer'],
                    },
                }
                for item in value
            ],
        }
```

Expose FAQ schema in the page's `get_structured_data`:

```python
def get_structured_data(self):
    schemas = [self.get_article_schema()]
    for block_type, block_value in self.body:
        if block_type == 'faq':
            faq_block = self.body.stream_block.child_blocks['faq']
            schemas.append(faq_block.get_schema(block_value))
    return schemas  # Return list — Next.js renders each as separate <script>
```

---

### Sitemap

#### Setup

```python
# settings.py
INSTALLED_APPS = [
    ...
    'wagtail.contrib.sitemaps',
    'django.contrib.sitemaps',
]
```

#### Custom Sitemap Class

```python
# sitemaps.py
from wagtail.contrib.sitemaps import Sitemap


class WagtailSitemap(Sitemap):
    """Exclude noindex pages and add custom priority/changefreq."""

    def items(self):
        # Filter out pages with noindex=True
        return (
            super().items()
            .filter(noindex=False)
            .live()
            .public()
        )

    def changefreq(self, page):
        # Customize per page type
        from myapp.models import BlogPostPage, HomePage
        if isinstance(page.specific, HomePage):
            return 'daily'
        if isinstance(page.specific, BlogPostPage):
            return 'monthly'
        return 'weekly'

    def priority(self, page):
        from myapp.models import HomePage
        if isinstance(page.specific, HomePage):
            return 1.0
        return 0.8
```

#### URL Configuration

```python
# urls.py
from django.contrib.sitemaps.views import sitemap
from .sitemaps import WagtailSitemap

sitemaps = {'wagtail': WagtailSitemap}

urlpatterns = [
    ...
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
```

---

### robots.txt

```python
# views.py
from django.http import HttpResponse

def robots_txt(request):
    site_url = request.build_absolute_uri('/').rstrip('/')
    content = f"""User-agent: *
Allow: /

Sitemap: {site_url}/sitemap.xml
"""
    return HttpResponse(content, content_type='text/plain')


# urls.py
urlpatterns = [
    ...
    path('robots.txt', views.robots_txt, name='robots_txt'),
]
```

> **Note for headless setups:** robots.txt and sitemap.xml should be served by the **Next.js frontend** (since that's what search engines crawl). The Django backend only needs a sitemap if you're also indexing the admin/API domain. See the Next.js section below for the primary implementation.

---

### Django Search Index

```python
# models/blog.py
from wagtail.search import index


class BlogPostPage(BasePage):
    body = StreamField([...])
    author = models.CharField(max_length=255)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)

    # Wagtail search index fields
    search_fields = BasePage.search_fields + [
        index.SearchField('body'),
        index.SearchField('author'),
        index.FilterField('author'),
        index.RelatedFields('tags', [
            index.SearchField('name'),
        ]),
    ]
```

**Optional Elasticsearch backend:**

```python
# settings.py
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.elasticsearch8',
        'URLS': ['http://localhost:9200'],
        'INDEX': 'mysite',
        'TIMEOUT': 5,
        'OPTIONS': {},
        'INDEX_SETTINGS': {},
    }
}
```

Rebuild the search index after adding fields:

```bash
python manage.py update_index
```

---

## 2. Next.js Frontend SEO (Wagtail Headless)

### Metadata API from Wagtail Data

The Wagtail API returns SEO fields in `page.meta`. Map them to Next.js Metadata:

```typescript
// lib/wagtail.ts
export interface WagtailPageMeta {
  type: string
  detail_url: string
  html_url: string
  slug: string
  first_published_at: string
  latest_revision_created_at: string
  seo_title: string
  search_description: string
}

export interface WagtailPage {
  id: number
  meta: WagtailPageMeta
  title: string
  og_image: { url: string; width: number; height: number; alt: string } | null
  canonical_url: string
  noindex: boolean
  structured_data: Record<string, unknown> | Record<string, unknown>[]
}

export async function getPageBySlug(slug: string[]): Promise<WagtailPage> {
  const path = slug.join('/')
  const res = await fetch(
    `${process.env.WAGTAIL_API_URL}/api/v2/pages/find/?html_path=/${path}/`,
    { next: { revalidate: 3600 } }
  )
  if (!res.ok) throw new Error(`Page not found: ${path}`)
  return res.json()
}
```

```typescript
// app/[...slug]/page.tsx
import type { Metadata } from 'next'
import { getPageBySlug } from '@/lib/wagtail'

export async function generateMetadata({
  params,
}: {
  params: { slug: string[] }
}): Promise<Metadata> {
  const page = await getPageBySlug(params.slug)

  return {
    title: page.meta.seo_title || page.title,
    description: page.meta.search_description,
    openGraph: {
      title: page.meta.seo_title || page.title,
      description: page.meta.search_description,
      images: page.og_image
        ? [
            {
              url: page.og_image.url,
              width: page.og_image.width,
              height: page.og_image.height,
              alt: page.og_image.alt,
            },
          ]
        : [],
    },
    twitter: {
      card: 'summary_large_image',
      title: page.meta.seo_title || page.title,
      description: page.meta.search_description,
    },
    robots: page.noindex ? { index: false, follow: false } : { index: true, follow: true },
    alternates: {
      canonical: page.canonical_url || undefined,
    },
  }
}
```

---

### Next.js Sitemap from Wagtail API

```typescript
// lib/wagtail.ts (add to existing)
export async function getAllPages(): Promise<WagtailPage[]> {
  const res = await fetch(
    `${process.env.WAGTAIL_API_URL}/api/v2/pages/?type=wagtailcore.Page&fields=meta,slug&limit=500&live=true`,
    { next: { revalidate: 3600 } }
  )
  const data = await res.json()
  return data.items
}
```

```typescript
// app/sitemap.ts
import type { MetadataRoute } from 'next'
import { getAllPages } from '@/lib/wagtail'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const pages = await getAllPages()

  return pages.map((page) => ({
    url: `${process.env.NEXT_PUBLIC_SITE_URL}${new URL(page.meta.html_url).pathname}`,
    lastModified: page.meta.latest_revision_created_at,
    changeFrequency: page.meta.slug === '' ? 'daily' : 'weekly',
    priority: page.meta.slug === '' ? 1 : 0.8,
  }))
}
```

---

### robots.ts

```typescript
// app/robots.ts
import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/admin/', '/api/'],
      },
      // Explicitly allow AI bots
      { userAgent: 'GPTBot', allow: '/' },
      { userAgent: 'PerplexityBot', allow: '/' },
      { userAgent: 'ClaudeBot', allow: '/' },
      { userAgent: 'anthropic-ai', allow: '/' },
      { userAgent: 'Google-Extended', allow: '/' },
    ],
    sitemap: `${process.env.NEXT_PUBLIC_SITE_URL}/sitemap.xml`,
  }
}
```

---

### JSON-LD from Wagtail API

```typescript
// components/JsonLd.tsx
export function JsonLd({ data }: { data: Record<string, unknown> }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  )
}

// For multiple schemas (e.g. Article + BreadcrumbList + FAQPage)
export function JsonLdList({ schemas }: { schemas: Record<string, unknown>[] }) {
  return (
    <>
      {schemas.map((schema, i) => (
        <JsonLd key={i} data={schema} />
      ))}
    </>
  )
}
```

**Usage in page.tsx:**

```typescript
// app/[...slug]/page.tsx
import { JsonLdList } from '@/components/JsonLd'

export default async function Page({ params }: { params: { slug: string[] } }) {
  const page = await getPageBySlug(params.slug)
  const schemas = Array.isArray(page.structured_data)
    ? page.structured_data
    : [page.structured_data]

  return (
    <>
      <JsonLdList schemas={schemas} />
      {/* page content */}
    </>
  )
}
```

---

### ISR (Incremental Static Regeneration) for SEO

ISR is critical for headless Wagtail — it ensures pages are statically generated (fast, crawlable) but can be revalidated when content changes.

#### Static Generation with ISR

```typescript
// app/[...slug]/page.tsx

// Generate all known paths at build time
export async function generateStaticParams() {
  const pages = await getAllPages()
  return pages.map((page) => ({
    slug: new URL(page.meta.html_url).pathname
      .replace(/^\//, '')
      .replace(/\/$/, '')
      .split('/'),
  }))
}

// Revalidation per page type
export const revalidate = 3600 // default: 1 hour

// Or conditional per route:
// Homepage: 300 (5 min)
// Blog posts: 86400 (24 hours)
// Service pages: 43200 (12 hours)
```

#### On-Demand Revalidation from Wagtail

When an editor publishes a page in Wagtail, trigger Next.js revalidation:

**Step 1 — Next.js revalidation endpoint:**

```typescript
// app/api/revalidate/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { revalidatePath, revalidateTag } from 'next/cache'

export async function POST(request: NextRequest) {
  const token = request.headers.get('x-revalidate-token')
  if (token !== process.env.REVALIDATE_SECRET) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { path, tag } = await request.json()

  if (tag) {
    revalidateTag(tag)
  } else if (path) {
    revalidatePath(path)
  }

  return NextResponse.json({ revalidated: true, now: Date.now() })
}
```

**Step 2 — Django signal on page publish:**

```python
# signals.py
from django.dispatch import receiver
from wagtail.signals import page_published
import requests
import os


@receiver(page_published)
def on_page_published(sender, **kwargs):
    page = kwargs['instance']
    nextjs_url = os.environ.get('NEXTJS_URL', 'http://localhost:3000')
    secret = os.environ.get('REVALIDATE_SECRET')

    try:
        # Get the frontend path from the page URL
        path = page.url_path  # e.g. /blog/my-post/

        requests.post(
            f"{nextjs_url}/api/revalidate",
            json={"path": path},
            headers={"x-revalidate-token": secret},
            timeout=5,
        )
    except Exception as e:
        # Log but don't raise — publishing should not fail if revalidation fails
        import logging
        logging.getLogger(__name__).error(f"Revalidation failed for {page.url_path}: {e}")
```

```python
# apps.py
from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = 'myapp'

    def ready(self):
        import myapp.signals  # noqa: F401
```

**Revalidation timing by page type:**

| Page Type | `revalidate` | Reason |
|-----------|-------------|--------|
| Homepage | `300` (5 min) | High traffic, frequent updates |
| Service pages | `43200` (12 h) | Rarely change |
| Blog posts | `86400` (24 h) | Rarely change after publish |
| Landing pages | `3600` (1 h) | Moderate update frequency |
| Dynamic search | `0` | No caching |

---

### Core Web Vitals — Wagtail Images

Wagtail uses **renditions** (server-side image transforms). Use them in Next.js `Image` to get exact width/height and avoid layout shift.

#### Expose renditions in the API

```python
# api/serializers.py
class ImageRenditionField(serializers.Field):
    def __init__(self, filter_spec, **kwargs):
        self.filter_spec = filter_spec
        super().__init__(**kwargs)

    def to_representation(self, image):
        if not image:
            return None
        rendition = image.get_rendition(self.filter_spec)
        return {
            'url': rendition.url,
            'width': rendition.width,
            'height': rendition.height,
            'alt': image.title,
        }

class BlogPostPageSerializer(BasePageSerializer):
    hero_image = ImageRenditionField('fill-1200x630', source='hero_image')
    hero_image_mobile = ImageRenditionField('fill-768x432', source='hero_image')
```

#### Use in Next.js Image component

```typescript
// components/WagtailImage.tsx
import NextImage from 'next/image'

interface WagtailRendition {
  url: string
  width: number
  height: number
  alt: string
}

interface WagtailImageProps {
  rendition: WagtailRendition
  priority?: boolean
  className?: string
}

export function WagtailImage({ rendition, priority = false, className }: WagtailImageProps) {
  return (
    <NextImage
      src={rendition.url}
      width={rendition.width}
      height={rendition.height}
      alt={rendition.alt}
      priority={priority}
      className={className}
    />
  )
}
```

#### Focal Point Preservation

Wagtail's focal point system allows editors to set a subject point on images. Preserve it when using `object-fit`:

```python
# In the API response, expose the focal point as CSS
def to_representation(self, image):
    rendition = image.get_rendition('fill-800x600')
    # Focal point as percentage of original dimensions
    fp_x = (image.focal_point_x or image.width / 2) / image.width * 100
    fp_y = (image.focal_point_y or image.height / 2) / image.height * 100
    return {
        'url': rendition.url,
        'width': rendition.width,
        'height': rendition.height,
        'alt': image.title,
        'focal_point': f"{fp_x:.1f}% {fp_y:.1f}%",
    }
```

```typescript
// In Next.js, apply focal point as object-position
<div className="relative aspect-video overflow-hidden">
  <NextImage
    src={image.url}
    fill
    alt={image.alt}
    className="object-cover"
    style={{ objectPosition: image.focal_point }}
  />
</div>
```

---

## 3. AEO/GEO Patterns for Wagtail

### FAQBlock → FAQ Schema + HTML for LLM Extraction

For LLMs to extract Q&A content, the HTML must be visible in the server-rendered page (not just injected via JSON-LD). Render FAQ blocks in a crawlable structure:

```typescript
// components/blocks/FaqBlock.tsx
interface FaqItem {
  question: string
  answer: string // rendered HTML from Wagtail RichText
}

export function FaqBlock({ items }: { items: FaqItem[] }) {
  return (
    <section aria-label="Frequently Asked Questions">
      <h2>Frequently Asked Questions</h2>
      <dl>
        {items.map((item, i) => (
          <div key={i} itemScope itemType="https://schema.org/Question">
            <dt className="faq-question" itemProp="name">
              {item.question}
            </dt>
            <dd
              className="faq-answer"
              itemScope
              itemType="https://schema.org/Answer"
              itemProp="acceptedAnswer"
            >
              <div
                itemProp="text"
                dangerouslySetInnerHTML={{ __html: item.answer }}
              />
            </dd>
          </div>
        ))}
      </dl>
    </section>
  )
}
```

This approach gives you:
1. **JSON-LD** from Django (for Google rich results)
2. **Microdata** via `itemScope`/`itemProp` (belt-and-suspenders for structured data)
3. **Readable HTML** that LLMs can extract directly

### Answer Blocks in RichText for Featured Snippets

Structure RichText content to target featured snippets:

```python
# In Wagtail RichText, encourage editors to use this pattern:
# - Start with a concise 40-60 word definition paragraph
# - Follow with an ordered list (for "how to" queries) or
#   unordered list (for "best X" queries)
# - Use heading hierarchy: H2 for main topic, H3 for sub-topics

# Custom RichText features to enforce structure:
WAGTAILADMIN_RICH_TEXT_EDITORS = {
    'default': {
        'WIDGET': 'wagtail.admin.rich_text.DraftailRichTextArea',
        'OPTIONS': {
            'features': ['h2', 'h3', 'bold', 'italic', 'ol', 'ul', 'link', 'image'],
        },
    },
}
```

On the Next.js side, parse rich text and add semantic classes:

```typescript
// components/RichText.tsx
import parse, { domToReact, Element } from 'html-react-parser'

export function RichText({ html }: { html: string }) {
  return (
    <div className="prose prose-lg max-w-none wagtail-richtext">
      {parse(html)}
    </div>
  )
}
```

### llms.txt Generation from Wagtail Sitemap

`llms.txt` is a standard for AI crawlers — it tells LLMs which URLs to include when building context about your site.

```typescript
// app/llms.txt/route.ts
import { getAllPages } from '@/lib/wagtail'

export async function GET() {
  const pages = await getAllPages()
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL

  const lines = [
    `# ${process.env.NEXT_PUBLIC_SITE_NAME}`,
    '',
    '## Key pages',
    '',
    ...pages
      .filter((p) => !p.noindex)
      .map((p) => {
        const path = new URL(p.meta.html_url).pathname
        return `- [${p.title}](${siteUrl}${path})`
      }),
  ]

  return new Response(lines.join('\n'), {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  })
}
```

---

## 4. SEO Audit Checklist — Wagtail + Next.js

### Wagtail Backend
- [ ] `seo_title` and `search_description` filled on all published pages
- [ ] `og_image` set on homepage, service pages, and all blog posts
- [ ] `canonical_url` set on pages with duplicate access paths
- [ ] `noindex=True` on all draft/private/internal pages
- [ ] `get_structured_data()` returns valid JSON-LD for every page type
- [ ] Sitemap at `/sitemap.xml` returns all live, public, non-noindex pages
- [ ] `robots.txt` served by Next.js frontend pointing to sitemap
- [ ] `page_published` signal triggers Next.js revalidation
- [ ] Search fields defined on all page models

### Next.js Frontend
- [ ] `generateMetadata()` on every `[...slug]/page.tsx` route
- [ ] `seo_title || title` fallback used (never empty titles)
- [ ] `og_image` mapped to `openGraph.images` with width/height
- [ ] `noindex` field controls `robots` metadata
- [ ] JSON-LD rendered via `<JsonLd>` component in `<head>` scope
- [ ] Sitemap at `/sitemap.xml` (via `app/sitemap.ts`) uses Wagtail API
- [ ] `robots.ts` explicitly allows GPTBot, PerplexityBot, ClaudeBot, Google-Extended
- [ ] All images use `next/image` with explicit `width` + `height` from Wagtail renditions
- [ ] Hero/above-fold images use `priority` prop
- [ ] Focal points respected via `object-position`
- [ ] `generateStaticParams` used on all dynamic routes
- [ ] `revalidate` set per page type
- [ ] On-demand revalidation working end-to-end (publish → signal → `/api/revalidate`)
- [ ] FAQBlock renders Q+A in semantic HTML (not just JSON-LD)
- [ ] `llms.txt` accessible at `/llms.txt`
- [ ] Search engine can crawl the **Next.js frontend URL**, not the Django API URL

### Validation Commands

```bash
# Check sitemap is accessible and valid
curl -sL https://example.com/sitemap.xml | xmllint --format - | head -50

# Check robots.txt
curl -sL https://example.com/robots.txt

# Check AI bot access
curl -sL https://example.com/robots.txt | grep -iE "gptbot|perplexitybot|claudebot|google-extended"

# Validate JSON-LD on a page
curl -sL https://example.com/blog/my-post/ | grep -o '<script type="application/ld+json">.*</script>'

# Check ISR revalidation
curl -X POST https://example.com/api/revalidate \
  -H "x-revalidate-token: $REVALIDATE_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"path": "/blog/my-post/"}'
```

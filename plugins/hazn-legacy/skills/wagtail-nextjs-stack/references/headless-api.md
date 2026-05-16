# Wagtail Headless API Reference

Wagtail API v2 setup, custom fields, Next.js data fetching patterns, ISR, and Draft Mode.

---

## Table of Contents

1. [API v2 Setup](#1-api-v2-setup)
2. [Custom API Fields](#2-custom-api-fields)
3. [Serialising StreamField Blocks](#3-serialising-streamfield-blocks)
4. [Custom Serializers](#4-custom-serializers)
5. [Authentication for Preview API](#5-authentication-for-preview-api)
6. [Next.js Data Fetching Patterns](#6-nextjs-data-fetching-patterns)
7. [ISR Setup — Webhook Revalidation](#7-isr-setup--webhook-revalidation)
8. [Draft Mode with Next.js](#8-draft-mode-with-nextjs)
9. [Type Generation from Wagtail API](#9-type-generation-from-wagtail-api)

---

## 1. API v2 Setup

### INSTALLED_APPS

```python
# config/settings/base.py
INSTALLED_APPS = [
    # ... django and wagtail apps ...
    "wagtail.api.v2",      # Must be in INSTALLED_APPS
    "rest_framework",      # DRF (installed automatically with wagtail.api)
]

# DRF settings (no auth needed for public API)
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
}
```

### Router configuration (`config/api.py`)

Create a dedicated API module:

```python
# config/api.py
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet


api_router = WagtailAPIRouter("wagtailapi")

api_router.register_endpoint("pages", PagesAPIViewSet)
api_router.register_endpoint("images", ImagesAPIViewSet)
api_router.register_endpoint("documents", DocumentsAPIViewSet)
```

### URL configuration (`config/urls.py`)

```python
# config/urls.py
from django.urls import path, include
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from config.api import api_router

urlpatterns = [
    # API endpoints
    path("api/v2/", api_router.urls),

    # Wagtail admin
    path("cms/", include(wagtailadmin_urls)),

    # Wagtail documents
    path("documents/", include(wagtaildocs_urls)),

    # Wagtail frontend (only needed if serving HTML from Django — optional in headless)
    path("", include(wagtail_urls)),
]
```

### CORS configuration (required for headless)

```bash
pip install django-cors-headers
```

```python
# config/settings/base.py
INSTALLED_APPS += ["corsheaders"]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Must be BEFORE CommonMiddleware
    "django.middleware.common.CommonMiddleware",
    # ...
]

# Allow your Next.js frontend origin
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://yoursite.com",
    "https://yoursite.vercel.app",
]

# For CSRF (form submissions from headless frontend)
CSRF_TRUSTED_ORIGINS = [
    "https://yoursite.com",
    "https://yoursite.vercel.app",
]
```

### Test the API

```bash
# List all live pages
curl https://cms.yourdomain.com/api/v2/pages/

# Get page by slug with all fields
curl "https://cms.yourdomain.com/api/v2/pages/?slug=home&fields=*"

# Get specific page type
curl "https://cms.yourdomain.com/api/v2/pages/?type=content.BlogPostPage&fields=title,slug,body,first_published_at"
```

---

## 2. Custom API Fields

### Declaring api_fields on page models

```python
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from rest_framework.fields import CharField


class MarketingPage(BasePage):
    body = StreamField([...], use_json_field=True)
    excerpt = models.TextField(blank=True)

    api_fields = BasePage.api_fields + [
        APIField("body"),           # StreamField — serialised automatically
        APIField("excerpt"),        # Text field — no serializer needed
        APIField(
            "hero_image_url",       # Custom name — use source for a different field name
            serializer=ImageRenditionField("fill-1920x800", source="og_image"),
        ),
    ]
```

### Multiple renditions (responsive images)

Expose multiple renditions so the frontend can pick the right size:

```python
api_fields = [
    APIField("hero_image", serializer=ImageRenditionField("original")),
    APIField("hero_image_desktop", serializer=ImageRenditionField("fill-1920x800", source="hero_image")),
    APIField("hero_image_tablet", serializer=ImageRenditionField("fill-1024x576", source="hero_image")),
    APIField("hero_image_mobile", serializer=ImageRenditionField("fill-768x400", source="hero_image")),
]
```

**API response shape:**

```json
{
  "hero_image_desktop": {
    "url": "https://cms.example.com/media/images/hero.fill-1920x800.jpg",
    "width": 1920,
    "height": 800,
    "alt": "Hero image alt text"
  }
}
```

---

## 3. Serialising StreamField Blocks

### Default StreamField serialization

Wagtail automatically serialises StreamField as an array of `{ type, value, id }` objects:

```json
{
  "body": [
    {
      "type": "hero",
      "value": {
        "heading": "Build what matters",
        "subheading": "We ship production-grade Django + Next.js sites.",
        "cta_text": "Get started",
        "cta_url": "https://example.com/contact"
      },
      "id": "abc123"
    },
    {
      "type": "rich_text",
      "value": "<p>Content here...</p>",
      "id": "def456"
    }
  ]
}
```

### Nested StructBlock serialisation

Wagtail serialises StructBlocks as nested objects:

```json
{
  "type": "testimonials",
  "value": {
    "heading": "What our clients say",
    "testimonials": [
      {
        "quote": "They shipped in half the time we expected.",
        "author": "Jane Smith",
        "role": "CTO, Acme Corp",
        "photo": {
          "url": "https://cms.example.com/media/images/jane.jpg",
          "width": 200,
          "height": 200
        }
      }
    ]
  },
  "id": "ghi789"
}
```

### Image blocks in StreamField

`ImageChooserBlock` does **not** automatically return a rendition — it returns the image ID. Wrap with a custom serializer:

```python
from wagtail.images.blocks import ImageChooserBlock
from wagtail.blocks import StructBlock, CharBlock


class ImageWithCaptionBlock(StructBlock):
    image = ImageChooserBlock(label="Image")
    caption = CharBlock(label="Caption", required=False)
    alt_text = CharBlock(label="Alt text", help_text="Describe the image for screen readers")

    class Meta:
        icon = "image"
        label = "Image with caption"
        template = None  # Headless — no template needed


# For the API, create a custom page serializer:
from wagtail.api.v2.serializers import PageSerializer
from rest_framework import serializers


class ImageBlockSerializer(serializers.Serializer):
    url = serializers.SerializerMethodField()
    width = serializers.IntegerField(source="width")
    height = serializers.IntegerField(source="height")
    alt = serializers.CharField(source="title")

    def get_url(self, obj):
        return obj.get_rendition("fill-800x600").url
```

**Simpler approach:** Use `APIImageChooserBlock` from a community package or define a custom block value_for_api method.

The cleanest pattern is to define `get_api_representation` on custom block types:

```python
from wagtail.blocks import StructBlock, ImageChooserBlock, CharBlock


class ImageWithCaptionBlock(StructBlock):
    image = ImageChooserBlock()
    caption = CharBlock(required=False)

    def get_api_representation(self, value, context=None):
        if not value.get("image"):
            return value
        img = value["image"]
        rendition = img.get_rendition("fill-800x600")
        return {
            "image": {
                "url": rendition.url,
                "width": rendition.width,
                "height": rendition.height,
                "alt": img.title,
            },
            "caption": value.get("caption", ""),
        }
```

---

## 4. Custom Serializers

### Full page serializer override

For complex pages, override the default serializer:

```python
# content/api.py
from wagtail.api.v2.serializers import PageSerializer
from wagtail.api.v2.views import PagesAPIViewSet
from rest_framework import serializers

from .models import BlogPostPage


class BlogPostPageSerializer(PageSerializer):
    reading_time = serializers.SerializerMethodField()
    author_name = serializers.CharField()
    tags = serializers.SerializerMethodField()

    def get_reading_time(self, obj):
        word_count = len(obj.body_text.split())  # Assumes body_text property
        return max(1, word_count // 200)  # 200 WPM average

    def get_tags(self, obj):
        return list(obj.tags.values_list("name", flat=True))

    class Meta(PageSerializer.Meta):
        model = BlogPostPage
        fields = PageSerializer.Meta.fields + ["reading_time", "author_name", "tags"]


class BlogPostAPIViewSet(PagesAPIViewSet):
    serializer_class = BlogPostPageSerializer
    known_query_parameters = PagesAPIViewSet.known_query_parameters | {"tag"}

    def get_queryset(self):
        qs = super().get_queryset()
        tag = self.request.query_params.get("tag")
        if tag:
            qs = qs.filter(tags__name=tag)
        return qs
```

Register the custom viewset in the router:

```python
# config/api.py
api_router.register_endpoint("blog-posts", BlogPostAPIViewSet)
```

---

## 5. Authentication for Preview API

### Token-based preview authentication

The preview API endpoint should only be accessible with a secret token. Never expose draft content publicly.

```python
# content/views.py
import json
from django.conf import settings
from django.http import JsonResponse
from wagtail.models import Page


def preview_page(request):
    """Returns page data in draft mode, authenticated by secret."""
    secret = request.GET.get("secret")
    token = request.GET.get("token")  # Wagtail preview token

    if secret != settings.WAGTAIL_PREVIEW_SECRET:
        return JsonResponse({"error": "Forbidden"}, status=403)

    # Find the page from the preview token (set by wagtail-headless-preview)
    from wagtail_headless_preview.models import PagePreview
    try:
        page_preview = PagePreview.objects.get(token=token)
    except PagePreview.DoesNotExist:
        return JsonResponse({"error": "Preview expired"}, status=404)

    page = page_preview.as_page()
    data = page.get_api_representation(page)
    return JsonResponse(data)
```

```python
# config/settings/base.py
WAGTAIL_PREVIEW_SECRET = env("WAGTAIL_PREVIEW_SECRET", default="change-me-in-production")
```

---

## 6. Next.js Data Fetching Patterns

### Setup (`lib/wagtail.ts`)

```typescript
// lib/wagtail.ts

const API_BASE = process.env.NEXT_PUBLIC_WAGTAIL_API_URL!;

if (!API_BASE) {
  throw new Error("NEXT_PUBLIC_WAGTAIL_API_URL is not set");
}

// ─── Types ──────────────────────────────────────────────────────────────────

export interface WagtailMeta {
  type: string;
  detail_url: string;
  html_url: string;
  slug: string;
  show_in_menus: boolean;
  seo_title: string;
  search_description: string;
  first_published_at: string | null;
  locale: string;
  parent: { id: number; meta: WagtailMeta } | null;
}

export interface WagtailPage {
  id: number;
  meta: WagtailMeta;
  title: string;
  [key: string]: unknown;
}

export interface WagtailListResponse {
  meta: { total_count: number };
  items: WagtailPage[];
}

// ─── Core fetchers ───────────────────────────────────────────────────────────

/**
 * Fetch a single page by slug.
 * Uses Next.js tag-based caching for ISR revalidation.
 */
export async function getPageBySlug(
  slug: string,
  type?: string
): Promise<WagtailPage | null> {
  const typeParam = type ? `&type=${type}` : "";
  const url = `${API_BASE}/pages/?slug=${slug}${typeParam}&fields=*`;

  const res = await fetch(url, {
    next: { tags: [`page-${slug}`] },
  });

  if (!res.ok) return null;

  const data: WagtailListResponse = await res.json();
  return data.items[0] ?? null;
}

/**
 * Fetch a page by its Wagtail numeric ID.
 */
export async function getPageById(id: number): Promise<WagtailPage | null> {
  const res = await fetch(`${API_BASE}/pages/${id}/?fields=*`, {
    next: { tags: [`page-id-${id}`] },
  });
  if (!res.ok) return null;
  return res.json();
}

/**
 * Get all pages of a given type. Used for generateStaticParams.
 */
export async function getAllPages(type?: string): Promise<WagtailPage[]> {
  const typeParam = type ? `&type=${type}` : "";
  const res = await fetch(
    `${API_BASE}/pages/?${typeParam}&fields=slug,title,meta&limit=500`,
    { next: { revalidate: 3600 } } // Cache for 1 hour, no tag needed
  );
  if (!res.ok) return [];
  const data: WagtailListResponse = await res.json();
  return data.items;
}

/**
 * Get child pages of a given parent page ID.
 */
export async function getPageChildren(
  parentId: number,
  type?: string,
  limit = 20,
  offset = 0
): Promise<WagtailListResponse> {
  const typeParam = type ? `&type=${type}` : "";
  const res = await fetch(
    `${API_BASE}/pages/?child_of=${parentId}${typeParam}&fields=*&limit=${limit}&offset=${offset}&order=-first_published_at`,
    { next: { tags: [`children-${parentId}`] } }
  );
  if (!res.ok) return { meta: { total_count: 0 }, items: [] };
  return res.json();
}
```

### App Router page component

```typescript
// app/[...slug]/page.tsx
import { notFound } from "next/navigation";
import { getPageBySlug, getAllPages } from "@/lib/wagtail";
import { RenderBlocks } from "@/components/RenderBlocks";

interface Props {
  params: Promise<{ slug: string[] }>;
}

export async function generateStaticParams() {
  const pages = await getAllPages();
  return pages.map((page) => ({
    slug: page.meta.slug.split("/").filter(Boolean),
  }));
}

export default async function DynamicPage({ params }: Props) {
  const { slug: slugParts } = await params;
  const slug = slugParts.join("/");

  const page = await getPageBySlug(slug);
  if (!page) notFound();

  const body = page.body as Array<{ type: string; value: unknown; id: string }> | undefined;

  return (
    <main>
      {body && <RenderBlocks blocks={body} />}
    </main>
  );
}

export async function generateMetadata({ params }: Props) {
  const { slug: slugParts } = await params;
  const page = await getPageBySlug(slugParts.join("/"));
  if (!page) return {};
  return {
    title: page.meta.seo_title || page.title,
    description: page.meta.search_description,
  };
}
```

---

## 7. ISR Setup — Webhook Revalidation

### Next.js revalidation endpoint

```typescript
// app/api/revalidate/route.ts
import { revalidateTag, revalidatePath } from "next/cache";
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const secret = req.nextUrl.searchParams.get("secret");

  if (secret !== process.env.WAGTAIL_REVALIDATE_SECRET) {
    return NextResponse.json({ error: "Invalid secret" }, { status: 401 });
  }

  let body: { slug?: string; id?: number } = {};
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (body.slug) {
    revalidateTag(`page-${body.slug}`);
    revalidatePath(`/${body.slug}`);
  }

  if (body.id) {
    revalidateTag(`page-id-${body.id}`);
  }

  return NextResponse.json({ revalidated: true, at: new Date().toISOString() });
}
```

### Wagtail signal to trigger revalidation

```python
# content/signals.py
import json
import logging

import requests
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from wagtail.models import Page
from wagtail.signals import page_published, page_unpublished

logger = logging.getLogger(__name__)

REVALIDATE_URL = getattr(settings, "NEXTJS_REVALIDATE_URL", None)
REVALIDATE_SECRET = getattr(settings, "NEXTJS_REVALIDATE_SECRET", None)


def _trigger_revalidation(page: Page) -> None:
    if not REVALIDATE_URL or not REVALIDATE_SECRET:
        logger.warning("NEXTJS_REVALIDATE_URL or NEXTJS_REVALIDATE_SECRET not configured")
        return

    try:
        response = requests.post(
            f"{REVALIDATE_URL}?secret={REVALIDATE_SECRET}",
            json={"slug": page.slug, "id": page.id},
            timeout=10,
        )
        response.raise_for_status()
        logger.info(f"Revalidated page: {page.slug} (status {response.status_code})")
    except requests.RequestException as e:
        logger.error(f"Failed to revalidate {page.slug}: {e}")


@receiver(page_published)
def on_page_published(sender, instance, **kwargs):
    _trigger_revalidation(instance)


@receiver(page_unpublished)
def on_page_unpublished(sender, instance, **kwargs):
    _trigger_revalidation(instance)
```

```python
# content/apps.py
from django.apps import AppConfig


class ContentConfig(AppConfig):
    name = "content"

    def ready(self):
        import content.signals  # noqa: F401
```

### Django settings for revalidation

```python
# config/settings/base.py
NEXTJS_REVALIDATE_URL = env("NEXTJS_REVALIDATE_URL", default="http://localhost:3000/api/revalidate")
NEXTJS_REVALIDATE_SECRET = env("NEXTJS_REVALIDATE_SECRET", default="change-me")
WAGTAIL_REVALIDATE_SECRET = NEXTJS_REVALIDATE_SECRET  # Same secret both sides
```

---

## 8. Draft Mode with Next.js

### Enable Draft Mode route

```typescript
// app/api/preview/route.ts
import { draftMode } from "next/headers";
import { redirect } from "next/navigation";
import { NextRequest } from "next/server";

export async function GET(request: NextRequest) {
  const secret = request.nextUrl.searchParams.get("secret");
  const slug = request.nextUrl.searchParams.get("slug");

  if (!secret || secret !== process.env.WAGTAIL_PREVIEW_SECRET) {
    return new Response("Invalid preview token", { status: 401 });
  }

  if (!slug) {
    return new Response("Missing slug", { status: 400 });
  }

  (await draftMode()).enable();
  redirect(`/${slug}`);
}
```

### Disable Draft Mode route

```typescript
// app/api/preview-disable/route.ts
import { draftMode } from "next/headers";
import { redirect } from "next/navigation";

export async function GET() {
  (await draftMode()).disable();
  redirect("/");
}
```

### Fetch draft content in page component

```typescript
// app/[...slug]/page.tsx
import { draftMode } from "next/headers";
import { getPageBySlug, getPageBySlugPreview } from "@/lib/wagtail";

export default async function DynamicPage({ params }: Props) {
  const { slug: slugParts } = await params;
  const slug = slugParts.join("/");
  const { isEnabled } = await draftMode();

  // Use preview fetcher if in draft mode (bypasses cache, fetches latest revision)
  const page = isEnabled
    ? await getPageBySlugPreview(slug)
    : await getPageBySlug(slug);

  if (!page) notFound();
  // ...
}
```

```typescript
// lib/wagtail.ts — preview fetcher
export async function getPageBySlugPreview(slug: string): Promise<WagtailPage | null> {
  const res = await fetch(
    `${API_BASE}/pages/?slug=${slug}&fields=*`,
    { cache: "no-store" } // Never cache preview requests
  );
  if (!res.ok) return null;
  const data: WagtailListResponse = await res.json();
  return data.items[0] ?? null;
}
```

---

## 9. Type Generation from Wagtail API

### Manual TypeScript types (recommended for most projects)

Define interfaces that match Wagtail's `block_type` + `value` pattern:

```typescript
// types/wagtail.ts

// ─── Block value types ───────────────────────────────────────────────────────

export interface WagtailImage {
  url: string;
  width: number;
  height: number;
  alt: string;
}

export interface CTALink {
  text: string;
  url: string;
}

export interface HeroBlockValue {
  heading: string;
  subheading: string;
  background_image: WagtailImage | null;
  cta_text: string;
  cta_url: string;
}

export interface RichTextBlockValue {
  value: string; // HTML string
}

export interface StatItem {
  value: string;
  label: string;
}

export interface StatsBlockValue {
  heading: string;
  stats: StatItem[];
}

export interface TestimonialItem {
  quote: string;
  author: string;
  role: string;
  photo: WagtailImage | null;
}

export interface TestimonialsBlockValue {
  heading: string;
  testimonials: TestimonialItem[];
}

export interface CardItem {
  title: string;
  body: string;
  image: WagtailImage | null;
  link_text: string;
  link_url: string;
}

export interface CardsBlockValue {
  heading: string;
  cards: CardItem[];
}

// ─── Block union ─────────────────────────────────────────────────────────────

export type StreamBlock =
  | { type: "hero"; value: HeroBlockValue; id: string }
  | { type: "rich_text"; value: string; id: string }
  | { type: "call_to_action"; value: CallToActionBlockValue; id: string }
  | { type: "testimonials"; value: TestimonialsBlockValue; id: string }
  | { type: "stats"; value: StatsBlockValue; id: string }
  | { type: "cards"; value: CardsBlockValue; id: string }
  | { type: "faq"; value: FAQBlockValue; id: string }
  | { type: "image_with_caption"; value: ImageWithCaptionBlockValue; id: string }
  | { type: "quote"; value: QuoteBlockValue; id: string }
  | { type: "embed"; value: string; id: string }
  | { type: string; value: unknown; id: string }; // Fallback for unknown blocks

// ─── Page types ──────────────────────────────────────────────────────────────

export interface MarketingPageData extends WagtailPage {
  body: StreamBlock[];
  seo_description: string;
  og_image: WagtailImage | null;
}

export interface BlogPostPageData extends WagtailPage {
  body: StreamBlock[];
  author_name: string;
  first_published_at: string;
  tags: string[];
  reading_time: number;
}
```

### Automated type generation (advanced)

For large projects, consider `openapi-typescript` against a custom OpenAPI spec, or use Wagtail's built-in schema:

```bash
# Generate OpenAPI schema from Wagtail DRF
pip install drf-spectacular

# Add to settings
INSTALLED_APPS += ["drf_spectacular"]
REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"

# Generate schema
python manage.py spectacular --color --file schema.yaml

# Generate TypeScript types
npx openapi-typescript schema.yaml -o types/api.ts
```

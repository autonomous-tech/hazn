---
name: wagtail-nextjs-stack
description: "Code implementation skill for marketing websites on Django + Wagtail (headless CMS) + Next.js (App Router) + React + Tailwind CSS. Use this skill whenever generating components, pages, content models, StreamField blocks, or configuration for this stack. Trigger on any mention of 'Wagtail', 'Django CMS', 'Next.js component', 'React component for marketing site', 'Tailwind', or when asked to implement designs, build sections, create page templates, or set up content block architectures. Also trigger for SEO metadata, image optimization, font loading, performance tuning, or deployment configuration on this stack. This skill handles code output — pair with `b2b-marketing-ux` for UX decisions and page architecture, use `b2b-wireframe` for visual layout review, and reference `frontend-design` for visual aesthetics."
---

# wagtail-nextjs-stack

Django + Wagtail LTS + Next.js implementation skill for Hazn framework projects.

**Stack:** cookiecutter-django + Wagtail 6.x LTS (headless) + Next.js 15+ (App Router) + TypeScript + Tailwind CSS

**Audiences served:**
- **Marketers** — clean Wagtail admin, editor-friendly panels, preview mode
- **Agencies** — extensible content models, StreamField block library, import tooling
- **Developers** — typed API, ISR, Next.js App Router patterns

---

## Table of Contents

1. [When to Use This Stack](#when-to-use)
2. [Project Bootstrap](#1-project-bootstrap)
3. [Content Modelling](#2-content-modelling)
4. [Headless API Configuration](#3-headless-api-configuration)
5. [Next.js Data Fetching](#4-nextjs-data-fetching)
6. [Block → Component Mapping](#5-block--component-mapping)
7. [Deployment Checklist](#6-deployment-checklist)
8. [Reference Files](#reference-files)

---

## When to Use

✅ **Use this stack when:**
- Content-heavy site with non-technical editors managing daily updates
- Existing Django/Python backend needs a frontend
- Autonomous own properties (portfolio, case study import workflow)
- Complex content modelling (nested pages, rich relationships, collections)
- Client needs structured content export/import (case-study.json → Wagtail)

❌ **Don't use when:**
- Greenfield B2B commercial site with no Django requirement → use `payload-nextjs-stack`
- WordPress is explicitly required → use `wordpress-generatepress`
- Simple static site → use Next.js alone

---

## 1. Project Bootstrap

**Full guide:** `references/cookiecutter-setup.md`

### Quick path

```bash
# 1. Scaffold with cookiecutter-django
pip install cookiecutter
cookiecutter gh:cookiecutter/cookiecutter-django

# Recommended options:
# project_name: Your Project
# use_postgresql: y
# use_celery: y
# use_whitenoise: y
# use_docker: n (unless you need it)
# use_heroku: n

# 2. Add Wagtail to requirements
pip install wagtail==6.* wagtail-headless-preview

# 3. Update settings (see references/cookiecutter-setup.md for full INSTALLED_APPS)
# 4. Run migrations
python manage.py migrate
python manage.py createsuperuser
```

### Key settings (add to `config/settings/base.py`)

```python
WAGTAIL_SITE_NAME = "Your Site"
WAGTAILADMIN_BASE_URL = "https://cms.yourdomain.com"

# Headless
WAGTAILAPI_BASE_URL = "https://cms.yourdomain.com"
WAGTAILFRONTEND_HINTS = True

INSTALLED_APPS += [
    "wagtail.contrib.settings",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
    "wagtail.api.v2",
    # Your apps:
    "home",
    "content",
]
```

---

## 2. Content Modelling

**Full guide:** `references/wagtail-best-practices.md`

### BasePage pattern

Every project starts with a `BasePage` all other page types inherit from:

```python
# content/models.py
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.search import index

class BasePage(Page):
    """Abstract base — never create directly."""

    # Shared SEO fields
    seo_description = RichTextField(blank=True, help_text="Meta description for search engines (150–160 chars)")
    og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Social share image (1200×630px recommended)"
    )

    promote_panels = Page.promote_panels + [
        FieldPanel("seo_description"),
        FieldPanel("og_image"),
    ]

    class Meta:
        abstract = True

    def get_api_representation(self, value, context=None):
        return super().get_api_representation(value, context)
```

### Page type hierarchy

```
BasePage (abstract)
├── HomePage           — root, single instance
├── MarketingPage      — flexible StreamField body
├── CaseStudyPage      — structured case study (maps to case-study.json)
├── BlogPostPage       — blog article (maps to seo-blog-writer output)
├── BlogIndexPage      — paginated blog listing
└── ContactPage        — contact form page
```

### StreamField body (standard marketing page)

```python
from wagtail.blocks import StreamBlock
from content.blocks import (
    HeroBlock, RichTextBlock, CallToActionBlock,
    TestimonialsBlock, StatsBlock, CardsBlock, FAQBlock,
)

class MarketingPage(BasePage):
    body = StreamField(
        StreamBlock([
            ("hero", HeroBlock()),
            ("rich_text", RichTextBlock()),
            ("call_to_action", CallToActionBlock()),
            ("testimonials", TestimonialsBlock()),
            ("stats", StatsBlock()),
            ("cards", CardsBlock()),
            ("faq", FAQBlock()),
        ]),
        blank=True,
        use_json_field=True,
        help_text="Build the page by adding content blocks below",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("body"),
    ]

    api_fields = [
        APIField("body"),
        APIField("seo_description"),
        APIField("og_image", serializer=ImageSerializer()),
    ]
```

---

## 3. Headless API Configuration

**Full guide:** `references/headless-api.md`

### Enable API in `config/urls.py`

```python
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet

api_router = WagtailAPIRouter("wagtailapi")
api_router.register_endpoint("pages", PagesAPIViewSet)
api_router.register_endpoint("images", ImagesAPIViewSet)
api_router.register_endpoint("documents", DocumentsAPIViewSet)

urlpatterns = [
    ...
    path("api/v2/", api_router.urls),
    path("cms/", include(wagtail_urls)),
]
```

### Custom API fields on page models

```python
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField

class CaseStudyPage(BasePage):
    hero_image = models.ForeignKey("wagtailimages.Image", ...)
    
    api_fields = [
        APIField("hero_image", serializer=ImageRenditionField("fill-1200x630")),
        APIField("challenge_body"),
        APIField("solution_body"),
        APIField("outcome_body"),
        APIField("metrics"),  # StreamField
    ]
```

---

## 4. Next.js Data Fetching

**Full guide:** `references/headless-api.md`

### Environment setup

```bash
# .env.local
NEXT_PUBLIC_WAGTAIL_API_URL=https://cms.yourdomain.com/api/v2
WAGTAIL_PREVIEW_SECRET=your-preview-secret
```

### Core fetch utilities (`lib/wagtail.ts`)

```typescript
const API_BASE = process.env.NEXT_PUBLIC_WAGTAIL_API_URL!;

export async function getPageBySlug(slug: string): Promise<WagtailPage | null> {
  const res = await fetch(
    `${API_BASE}/pages/?slug=${slug}&type=content.MarketingPage&fields=*`,
    { next: { tags: [`page-${slug}`] } }
  );
  if (!res.ok) return null;
  const data = await res.json();
  return data.items[0] ?? null;
}

export async function getAllPages(type?: string): Promise<WagtailPage[]> {
  const typeParam = type ? `&type=${type}` : "";
  const res = await fetch(`${API_BASE}/pages/?${typeParam}&fields=slug,title,meta`);
  const data = await res.json();
  return data.items;
}
```

### ISR revalidation

```typescript
// app/api/revalidate/route.ts
import { revalidateTag } from "next/cache";
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const secret = req.nextUrl.searchParams.get("secret");
  if (secret !== process.env.WAGTAIL_PREVIEW_SECRET) {
    return NextResponse.json({ error: "Invalid secret" }, { status: 401 });
  }
  const { slug } = await req.json();
  revalidateTag(`page-${slug}`);
  return NextResponse.json({ revalidated: true });
}
```

---

## 5. Block → Component Mapping

**Full guide:** `references/streamfield-blocks.md`

### RenderBlocks pattern

```typescript
// components/RenderBlocks.tsx
import { HeroBlock } from "./blocks/HeroBlock";
import { RichTextBlock } from "./blocks/RichTextBlock";
import { CallToActionBlock } from "./blocks/CallToActionBlock";
// ...

type Block = { type: string; value: unknown; id: string };

const blockMap: Record<string, React.ComponentType<{ value: any }>> = {
  hero: HeroBlock,
  rich_text: RichTextBlock,
  call_to_action: CallToActionBlock,
  testimonials: TestimonialsBlock,
  stats: StatsBlock,
  cards: CardsBlock,
  faq: FAQBlock,
};

export function RenderBlocks({ blocks }: { blocks: Block[] }) {
  return (
    <>
      {blocks.map((block) => {
        const Component = blockMap[block.type];
        if (!Component) {
          console.warn(`Unknown block type: ${block.type}`);
          return null;
        }
        return <Component key={block.id} value={block.value} />;
      })}
    </>
  );
}
```

### Block type naming conventions

| Layer | Convention | Example |
|-------|-----------|---------|
| Python class | PascalCase + `Block` suffix | `HeroBlock` |
| StreamField key | snake_case | `"hero"` |
| API `block_type` | snake_case (matches key) | `"hero"` |
| Next.js component | PascalCase + `Block` suffix | `HeroBlock` |
| Switch/map key | snake_case | `"hero"` |

---

## 6. Deployment Checklist

**Full guide:** `references/deployment.md`

### Backend (Railway / Render)

```
[ ] DATABASE_URL set (managed PostgreSQL)
[ ] SECRET_KEY set (random 50+ chars)
[ ] ALLOWED_HOSTS includes API domain
[ ] CSRF_TRUSTED_ORIGINS includes frontend domain (headless requirement)
[ ] DJANGO_SETTINGS_MODULE=config.settings.production
[ ] Static files: collectstatic runs in release command
[ ] Media: S3/R2 django-storages configured
[ ] Redis: CELERY_BROKER_URL set
[ ] Wagtail site record: domain matches production URL
[ ] Superuser created
```

### Frontend (Vercel)

```
[ ] NEXT_PUBLIC_WAGTAIL_API_URL set
[ ] WAGTAIL_PREVIEW_SECRET set (matches Django)
[ ] ISR revalidation webhook configured in Wagtail
[ ] Draft Mode tested end-to-end
[ ] Build passes without errors
```

### Post-deploy verification

```
[ ] /cms/admin/ loads and is usable
[ ] API returns data: GET /api/v2/pages/
[ ] Frontend renders pages from API
[ ] Editor can publish a page → ISR fires → frontend updates
[ ] Preview link works from Wagtail admin
[ ] Images render via renditions (not raw upload URLs)
```

---

## Reference Files

| File | Contents |
|------|----------|
| `references/wagtail-best-practices.md` | Page models, StreamField, admin UX for marketers, permissions, search |
| `references/headless-api.md` | API v2 setup, custom fields, Next.js patterns, ISR, Draft Mode |
| `references/streamfield-blocks.md` | Full block library — Python + TypeScript side by side |
| `references/cookiecutter-setup.md` | Step-by-step project scaffold |
| `references/deployment.md` | Railway/VPS/Vercel deployment, env vars, media storage |
| `references/hazn-integration.md` | case-study.json import, blog import, Autonomous page hierarchy |

# cookiecutter-django + Wagtail Setup Guide

Step-by-step project scaffold for Django + Wagtail LTS + Next.js projects.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Scaffold with cookiecutter-django](#2-scaffold-with-cookiecutter-django)
3. [Add Wagtail to the Project](#3-add-wagtail-to-the-project)
4. [Configure INSTALLED_APPS](#4-configure-installed_apps)
5. [Add Wagtail URLs](#5-add-wagtail-urls)
6. [Create First Page Model](#6-create-first-page-model)
7. [Run Migrations & Create Superuser](#7-run-migrations--create-superuser)
8. [Configure Wagtail Settings](#8-configure-wagtail-settings)
9. [Configure Headless Settings](#9-configure-headless-settings)
10. [Next.js Frontend Bootstrap](#10-nextjs-frontend-bootstrap)
11. [Project Directory Structure](#11-project-directory-structure)

---

## 1. Prerequisites

```bash
# Python 3.11+
python --version

# pip with pipx (recommended for CLI tools)
pip install pipx
pipx ensurepath

# cookiecutter
pipx install cookiecutter

# Node.js 20+ (for Next.js)
node --version

# PostgreSQL running locally (or use Docker)
psql --version
```

---

## 2. Scaffold with cookiecutter-django

```bash
cookiecutter gh:cookiecutter/cookiecutter-django
```

### Recommended options

```
project_name [My Awesome Project]: Autonomous Site
project_slug [autonomous_site]: autonomous_site
description [Behold My Awesome Project!]: Headless Django + Wagtail CMS
author_name [Daniel Roy Greenfeld]: Autonomous Technologies
domain_name [example.com]: autonomoustech.ca
email [rizki@autonomoustech.ca]: rizki@autonomoustech.ca
version [0.1.0]: 0.1.0
Select open_source_license: 4 (Not open source)
Select username_type: 1 (username)
timezone [UTC]: UTC
windows [n]: n
Select an editor: 3 (VS Code)
use_docker [n]: n
Select postgresql_version: 1 (16.1)
Select cloud_provider: 3 (None — deploy manually)
Select mail_service: 7 (Other SMTP)
use_async [n]: n
use_drf [n]: n       ← We'll add DRF via wagtail.api
custom_bootstrap_compilation [n]: n
use_compressor [n]: n
use_celery [y]: y    ← For scheduled publishing
use_mailpit [n]: n
use_sentry [y]: y    ← Recommended for production
use_whitenoise [y]: y
use_heroku [n]: n
Select ci_tool: 4 (None — or GitHub Actions)
keep_local_envs_in_vcs [y]: n
debug [n]: n
```

### After scaffold

```bash
cd autonomous_site

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements/local.txt
```

---

## 3. Add Wagtail to the Project

### Install packages

```bash
pip install "wagtail>=6.0,<7.0" wagtail-headless-preview

# For media management (optional but recommended)
pip install wagtailmedia

# For django-storages (S3/R2 media)
pip install django-storages boto3

# For CORS (required for headless)
pip install django-cors-headers

# Save to requirements
pip freeze | grep -E "wagtail|storages|boto3|corsheaders" >> requirements/base.txt
```

---

## 4. Configure INSTALLED_APPS

Edit `config/settings/base.py`:

```python
# config/settings/base.py

DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.admin",
    "django.forms",
]

THIRD_PARTY_APPS = [
    "crispy_forms",
    "crispy_bootstrap5",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "celery",
    "django_celery_beat",
    "rest_framework",           # Added with wagtail.api
    "corsheaders",              # CORS for headless frontend

    # Wagtail
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",     # Global site settings
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "wagtail.api.v2",               # Headless API
    "wagtail_headless_preview",     # Preview for Next.js
    "modelcluster",
    "taggit",
]

LOCAL_APPS = [
    "autonomous_site.users",
    "home",          # Wagtail home app
    "content",       # Main content app
    "case_studies",  # Case study pages
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
```

### Add CORS middleware

```python
# config/settings/base.py

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",   # ← Add BEFORE CommonMiddleware
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # ... rest of middleware
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",  # ← Add at end
]
```

---

## 5. Add Wagtail URLs

```python
# config/urls.py
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from config.api import api_router   # We'll create this next

urlpatterns = [
    # Django admin (keep this — useful for superuser tasks)
    path(settings.ADMIN_URL, admin.site.urls),

    # Wagtail CMS admin
    path("cms/", include(wagtailadmin_urls)),

    # Wagtail documents
    path("documents/", include(wagtaildocs_urls)),

    # Wagtail Headless API
    path("api/v2/", api_router.urls),

    # Wagtail frontend (keep for redirects middleware)
    path("", include(wagtail_urls)),
]
```

### Create `config/api.py`

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

---

## 6. Create First Page Model

### Create the home app

```bash
python manage.py startapp home
python manage.py startapp content
python manage.py startapp case_studies
```

### home/models.py

```python
# home/models.py
from wagtail.models import Page


class HomePage(Page):
    """Site root page."""

    subpage_types = [
        "content.MarketingPage",
        "content.BlogIndexPage",
        "case_studies.CaseStudyIndexPage",
    ]
    parent_page_types = ["wagtailcore.Page"]
    max_count = 1

    class Meta:
        verbose_name = "Home page"
```

### home/migrations (create initial migration)

```bash
python manage.py makemigrations home
```

### home/wagtail_hooks.py (optional: register in admin)

```python
# home/wagtail_hooks.py
# Empty file — triggers Wagtail to discover this app's hooks
```

---

## 7. Run Migrations & Create Superuser

```bash
# Create database
createdb autonomous_site

# Apply all migrations (Django + Wagtail)
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create initial Wagtail site record
python manage.py shell
```

```python
# In Django shell — set up the Wagtail site
from wagtail.models import Site, Page
from home.models import HomePage

# Get or create the root page
root = Page.objects.filter(depth=1).first()

# Create the HomePage under root
home = HomePage(
    title="Home",
    slug="home",
    live=True,
)
root.add_child(instance=home)

# Point the Wagtail Site to your HomePage
Site.objects.all().delete()
Site.objects.create(
    hostname="localhost",
    port=8000,
    root_page=home,
    is_default_site=True,
)

exit()
```

---

## 8. Configure Wagtail Settings

Add to `config/settings/base.py`:

```python
# ─── Wagtail ─────────────────────────────────────────────────────────────────

WAGTAIL_SITE_NAME = "Autonomous Technologies"

# Base URL used in Wagtail admin for "View live" links
WAGTAILADMIN_BASE_URL = env("WAGTAILADMIN_BASE_URL", default="http://localhost:8000")

# API base URL
WAGTAILAPI_BASE_URL = env("WAGTAILAPI_BASE_URL", default="http://localhost:8000")

# Wagtail search
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Images
WAGTAILIMAGES_IMAGE_MODEL = "wagtailimages.Image"  # Use default (override if custom model needed)
WAGTAILIMAGES_JPEG_QUALITY = 80
WAGTAILIMAGES_WEBP_QUALITY = 80

# Docs
WAGTAILDOCS_SERVE_METHOD = "serve_view"

# Rich text — allowed features (limit for editor simplicity)
WAGTAILEMBEDS_RESPONSIVE_HTML = True
```

---

## 9. Configure Headless Settings

```python
# config/settings/base.py

# ─── Headless ────────────────────────────────────────────────────────────────

# Hint to frontend that this is a headless Wagtail installation
WAGTAILFRONTEND_HINTS = True

# wagtail-headless-preview: maps preview requests to Next.js routes
WAGTAIL_HEADLESS_PREVIEW = {
    "CLIENT_URLS": {
        "default": env("NEXTJS_PREVIEW_URL", default="http://localhost:3000/api/preview"),
    }
}

# Preview secret (shared between Django and Next.js)
WAGTAIL_PREVIEW_SECRET = env("WAGTAIL_PREVIEW_SECRET", default="dev-preview-secret-change-me")

# ISR revalidation — Next.js endpoint + shared secret
NEXTJS_REVALIDATE_URL = env("NEXTJS_REVALIDATE_URL", default="http://localhost:3000/api/revalidate")
NEXTJS_REVALIDATE_SECRET = env("NEXTJS_REVALIDATE_SECRET", default="dev-revalidate-secret-change-me")

# CORS — allow Next.js to fetch from Django API
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[
    "http://localhost:3000",
])

# CSRF — allow headless form submissions
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[
    "http://localhost:3000",
])
```

### Local `.env` file

```bash
# .envs/.local/.django (gitignored)

DATABASE_URL=postgres://postgres:password@127.0.0.1:5432/autonomous_site
DJANGO_SECRET_KEY=local-development-secret-key-change-in-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

WAGTAILADMIN_BASE_URL=http://localhost:8000
WAGTAILAPI_BASE_URL=http://localhost:8000
WAGTAIL_PREVIEW_SECRET=dev-preview-secret
NEXTJS_PREVIEW_URL=http://localhost:3000/api/preview
NEXTJS_REVALIDATE_URL=http://localhost:3000/api/revalidate
NEXTJS_REVALIDATE_SECRET=dev-revalidate-secret

CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000
```

### Run the dev server

```bash
python manage.py runserver

# In a separate terminal — start Celery for scheduled publishing
celery -A config.celery_app worker -l info
celery -A config.celery_app beat -l info
```

Access:
- **Django admin:** http://localhost:8000/admin/
- **Wagtail admin:** http://localhost:8000/cms/
- **API:** http://localhost:8000/api/v2/pages/

---

## 10. Next.js Frontend Bootstrap

```bash
# From the project root, create a frontend/ directory
cd ..
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --no-turbopack \
  --import-alias "@/*"

cd frontend
```

### Install additional packages

```bash
npm install @tailwindcss/typography
```

### Environment variables

```bash
# frontend/.env.local
NEXT_PUBLIC_WAGTAIL_API_URL=http://localhost:8000/api/v2
WAGTAIL_PREVIEW_SECRET=dev-preview-secret
WAGTAIL_REVALIDATE_SECRET=dev-revalidate-secret
```

### Tailwind config (add typography plugin)

```javascript
// frontend/tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {},
  },
  plugins: [require("@tailwindcss/typography")],
};

export default config;
```

### Run Next.js dev server

```bash
npm run dev
# → http://localhost:3000
```

---

## 11. Project Directory Structure

```
autonomous_site/                # Django project root
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── api.py                  # Wagtail API router
│   ├── urls.py
│   └── celery_app.py
├── home/
│   ├── models.py               # HomePage
│   └── migrations/
├── content/
│   ├── models.py               # MarketingPage, BlogIndexPage, BlogPostPage
│   ├── blocks.py               # All StreamField blocks
│   ├── snippets.py             # Testimonials, navigation, etc.
│   ├── settings.py             # SiteSettings (wagtail.contrib.settings)
│   ├── signals.py              # ISR revalidation trigger
│   ├── apps.py
│   └── migrations/
├── case_studies/
│   ├── models.py               # CaseStudyPage, CaseStudyIndexPage
│   ├── management/
│   │   └── commands/
│   │       └── import_case_study.py
│   └── migrations/
├── requirements/
│   ├── base.txt
│   ├── local.txt
│   └── production.txt
├── .envs/
│   └── .local/
│       └── .django             # gitignored
├── manage.py
└── frontend/                   # Next.js app
    ├── src/
    │   ├── app/
    │   │   ├── [...slug]/
    │   │   │   └── page.tsx
    │   │   ├── api/
    │   │   │   ├── preview/
    │   │   │   │   └── route.ts
    │   │   │   └── revalidate/
    │   │   │       └── route.ts
    │   │   ├── layout.tsx
    │   │   └── page.tsx
    │   ├── components/
    │   │   ├── blocks/
    │   │   │   ├── HeroBlock.tsx
    │   │   │   ├── RichTextBlock.tsx
    │   │   │   └── ...
    │   │   ├── RenderBlocks.tsx
    │   │   └── layout/
    │   │       ├── Header.tsx
    │   │       └── Footer.tsx
    │   ├── lib/
    │   │   └── wagtail.ts
    │   └── types/
    │       └── wagtail.ts
    ├── .env.local
    ├── next.config.ts
    ├── tailwind.config.ts
    └── package.json
```

---

## Multi-Client Architecture Decision

For Autonomous managing multiple client sites, choose one of two patterns before starting any project:

### Option A: One Wagtail instance per client (recommended for most cases)

- Separate Django/Wagtail deployment per client
- Complete data isolation
- Independent deployment schedules
- Simpler permissions model
- Higher ops overhead (N deployments to maintain)

**Use when:** Client has sensitive data requirements, different tech stacks per client, or the project is large enough to justify dedicated infrastructure.

### Option B: Single Wagtail instance, Wagtail Sites framework

- One deployment, multiple `Site` objects in Wagtail admin
- Each site has its own root page and domain
- Shared codebase, shared page types
- Lower ops overhead
- Shared failure domain (one bad deploy affects all clients)
- Complex permissions — must use Wagtail collection permissions carefully to prevent cross-client content access

**Use when:** Multiple smaller sites with identical tech requirements, internal tooling, or you're managing 10+ small sites.

### Autonomous default: Option A

Deploy one Wagtail instance per client. Use Railway or Render for straightforward per-project deploys. The ops overhead is manageable and the isolation is worth it.

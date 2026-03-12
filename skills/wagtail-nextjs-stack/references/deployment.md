# Deployment Guide

Django + Wagtail backend + Next.js frontend deployment reference.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Railway Deployment (Backend)](#2-railway-deployment-backend)
3. [Render Deployment (Backend Alternative)](#3-render-deployment-backend-alternative)
4. [VPS Deployment (Gunicorn + Nginx)](#4-vps-deployment-gunicorn--nginx)
5. [Static Files with Whitenoise](#5-static-files-with-whitenoise)
6. [Media Files with S3/Cloudflare R2](#6-media-files-with-s3cloudflare-r2)
7. [Environment Variables Checklist](#7-environment-variables-checklist)
8. [Next.js on Vercel](#8-nextjs-on-vercel)
9. [Cache Invalidation (ISR Webhook)](#9-cache-invalidation-isr-webhook)
10. [Database Management](#10-database-management)
11. [Post-Deploy Verification Checklist](#11-post-deploy-verification-checklist)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────┐
│           Vercel (CDN)              │
│         Next.js 15+ App             │
│   ISR + Draft Mode + Edge Cache     │
└──────────────┬──────────────────────┘
               │ HTTPS API calls
               ▼
┌─────────────────────────────────────┐
│      Railway / Render / VPS         │
│     Django + Wagtail CMS            │
│   gunicorn + whitenoise + celery    │
└──────┬──────────────┬───────────────┘
       │              │
       ▼              ▼
  PostgreSQL        Redis
  (managed)       (managed)
       │
       ▼
  Cloudflare R2 / AWS S3
  (media files)
```

---

## 2. Railway Deployment (Backend)

### Procfile

```
web: gunicorn config.wsgi --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
worker: celery -A config.celery_app worker -l info
beat: celery -A config.celery_app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### railway.json

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements/production.txt"
  },
  "deploy": {
    "startCommand": "gunicorn config.wsgi --bind 0.0.0.0:$PORT --workers 2 --threads 4",
    "releaseCommand": "python manage.py migrate --noinput && python manage.py collectstatic --noinput",
    "healthcheckPath": "/api/v2/pages/",
    "healthcheckTimeout": 100
  }
}
```

### Railway environment variables

Set these in the Railway dashboard:

```bash
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=<50+ random chars>
DATABASE_URL=<Railway PostgreSQL URL — auto-set if using Railway Postgres>
REDIS_URL=<Railway Redis URL — auto-set if using Railway Redis>
DJANGO_ALLOWED_HOSTS=<your-cms-domain.up.railway.app>,cms.yourdomain.com
DJANGO_SECURE_SSL_REDIRECT=True
WEB_CONCURRENCY=2

# Wagtail
WAGTAILADMIN_BASE_URL=https://cms.yourdomain.com
WAGTAILAPI_BASE_URL=https://cms.yourdomain.com
WAGTAIL_PREVIEW_SECRET=<random secret>

# ISR revalidation
NEXTJS_REVALIDATE_URL=https://yoursite.com/api/revalidate
NEXTJS_REVALIDATE_SECRET=<random secret>

# CORS + CSRF
CORS_ALLOWED_ORIGINS=https://yoursite.com,https://yoursite.vercel.app
CSRF_TRUSTED_ORIGINS=https://yoursite.com,https://yoursite.vercel.app

# Media (S3/R2)
DJANGO_AWS_ACCESS_KEY_ID=<key>
DJANGO_AWS_SECRET_ACCESS_KEY=<secret>
DJANGO_AWS_STORAGE_BUCKET_NAME=<bucket>
DJANGO_AWS_S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
DJANGO_AWS_S3_CUSTOM_DOMAIN=media.yourdomain.com

# Email
DJANGO_EMAIL_BACKEND=anymail.backends.mailgun.EmailBackend
MAILGUN_API_KEY=<key>
MAILGUN_SENDER_DOMAIN=yourdomain.com

# Sentry
SENTRY_DSN=<sentry dsn>
```

---

## 3. Render Deployment (Backend Alternative)

### render.yaml

```yaml
services:
  - type: web
    name: autonomous-cms
    env: python
    buildCommand: pip install -r requirements/production.txt
    startCommand: gunicorn config.wsgi --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60
    envVars:
      - key: DJANGO_SETTINGS_MODULE
        value: config.settings.production
      - key: DJANGO_SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: autonomous-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: autonomous-redis
          type: redis
          property: connectionString

  - type: worker
    name: autonomous-celery
    env: python
    buildCommand: pip install -r requirements/production.txt
    startCommand: celery -A config.celery_app worker -l info

  - type: worker
    name: autonomous-celery-beat
    env: python
    buildCommand: pip install -r requirements/production.txt
    startCommand: celery -A config.celery_app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

databases:
  - name: autonomous-db
    databaseName: autonomous_site
    user: autonomous

services:
  - type: redis
    name: autonomous-redis
    plan: starter
```

---

## 4. VPS Deployment (Gunicorn + Nginx)

### Gunicorn systemd service

```ini
# /etc/systemd/system/autonomous-cms.service
[Unit]
Description=Autonomous CMS - Gunicorn
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
RuntimeDirectory=gunicorn
WorkingDirectory=/srv/autonomous_site
ExecStart=/srv/autonomous_site/.venv/bin/gunicorn \
    config.wsgi \
    --bind unix:/run/gunicorn/autonomous_site.sock \
    --workers 4 \
    --threads 2 \
    --worker-class gthread \
    --worker-tmp-dir /dev/shm \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --log-level info
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
EnvironmentFile=/srv/autonomous_site/.env.production

[Install]
WantedBy=multi-user.target
```

### Nginx configuration

```nginx
# /etc/nginx/sites-available/autonomous-cms
server {
    listen 80;
    server_name cms.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name cms.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/cms.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cms.yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy strict-origin-when-cross-origin;

    # Static files (served by Whitenoise via Django, but nginx can serve too)
    location /static/ {
        alias /srv/autonomous_site/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://unix:/run/gunicorn/autonomous_site.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        client_max_body_size 50M;  # Allow large image uploads
    }
}
```

### Celery systemd service

```ini
# /etc/systemd/system/autonomous-celery.service
[Unit]
Description=Autonomous CMS - Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/srv/autonomous_site
ExecStart=/srv/autonomous_site/.venv/bin/celery \
    -A config.celery_app worker \
    -l info \
    --pidfile /run/celery/autonomous_site.pid \
    --logfile /var/log/celery/autonomous_site.log
ExecStop=/srv/autonomous_site/.venv/bin/celery multi stopwait autonomous_site
ExecReload=/srv/autonomous_site/.venv/bin/celery multi restart autonomous_site
EnvironmentFile=/srv/autonomous_site/.env.production

[Install]
WantedBy=multi-user.target
```

---

## 5. Static Files with Whitenoise

Cookiecutter-django includes Whitenoise by default. Verify the configuration:

```python
# config/settings/production.py
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # ← Must be second
    # ...
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = str(BASE_DIR / "staticfiles")
STATIC_URL = "/static/"
```

### collectstatic

```bash
# Run before every deploy
python manage.py collectstatic --noinput
```

---

## 6. Media Files with S3/Cloudflare R2

### Install django-storages

```bash
pip install django-storages[s3] boto3
```

### Production media settings

```python
# config/settings/production.py
import boto3

# Cloudflare R2 (S3-compatible)
AWS_ACCESS_KEY_ID = env("DJANGO_AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("DJANGO_AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("DJANGO_AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = env("DJANGO_AWS_S3_ENDPOINT_URL")  # R2 endpoint
AWS_S3_CUSTOM_DOMAIN = env("DJANGO_AWS_S3_CUSTOM_DOMAIN", default=None)
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=31536000"}
AWS_DEFAULT_ACL = None  # Use bucket policy
AWS_S3_FILE_OVERWRITE = False

# Use custom domain if configured (CDN)
if AWS_S3_CUSTOM_DOMAIN:
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
else:
    MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/"

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# Wagtail images stored in R2
WAGTAILIMAGES_IMAGE_MODEL = "wagtailimages.Image"
```

### Cloudflare R2 bucket setup

1. Create R2 bucket in Cloudflare dashboard
2. Create API token with R2 edit permissions
3. Set `AWS_S3_ENDPOINT_URL` to: `https://<account-id>.r2.cloudflarestorage.com`
4. Set up custom domain (optional but recommended for CDN): `media.yourdomain.com`
5. Add CORS policy to bucket:

```json
[
  {
    "AllowedOrigins": ["https://cms.yourdomain.com"],
    "AllowedMethods": ["GET", "PUT", "DELETE"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600
  }
]
```

---

## 7. Environment Variables Checklist

### Django/Wagtail (backend)

```bash
# Core Django
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=                    # 50+ random chars — required
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=                 # comma-separated domains
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SECURE_HSTS_SECONDS=31536000

# Database
DATABASE_URL=                         # postgres://user:pass@host:5432/dbname

# Redis / Celery
REDIS_URL=                            # redis://host:6379/0

# Wagtail
WAGTAILADMIN_BASE_URL=                # https://cms.yourdomain.com
WAGTAILAPI_BASE_URL=                  # https://cms.yourdomain.com

# Headless / Preview
WAGTAIL_PREVIEW_SECRET=               # Random secret — must match Next.js
NEXTJS_REVALIDATE_URL=                # https://yoursite.com/api/revalidate
NEXTJS_REVALIDATE_SECRET=             # Random secret — must match Next.js

# CORS
CORS_ALLOWED_ORIGINS=                 # https://yoursite.com,https://yoursite.vercel.app
CSRF_TRUSTED_ORIGINS=                 # https://yoursite.com,https://yoursite.vercel.app

# Media storage
DJANGO_AWS_ACCESS_KEY_ID=
DJANGO_AWS_SECRET_ACCESS_KEY=
DJANGO_AWS_STORAGE_BUCKET_NAME=
DJANGO_AWS_S3_ENDPOINT_URL=
DJANGO_AWS_S3_CUSTOM_DOMAIN=          # Optional CDN domain

# Email
DJANGO_EMAIL_BACKEND=                 # anymail or SMTP
MAILGUN_API_KEY=                      # If using Mailgun

# Monitoring
SENTRY_DSN=                           # Optional but recommended
```

### Next.js (frontend)

```bash
NEXT_PUBLIC_WAGTAIL_API_URL=          # https://cms.yourdomain.com/api/v2
WAGTAIL_PREVIEW_SECRET=               # Must match Django WAGTAIL_PREVIEW_SECRET
WAGTAIL_REVALIDATE_SECRET=            # Must match Django NEXTJS_REVALIDATE_SECRET
```

---

## 8. Next.js on Vercel

### vercel.json (optional)

```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm ci",
  "env": {
    "NEXT_PUBLIC_WAGTAIL_API_URL": "@wagtail-api-url"
  }
}
```

### Vercel environment variables

Set in Vercel dashboard → Project → Settings → Environment Variables:

```
NEXT_PUBLIC_WAGTAIL_API_URL     = https://cms.yourdomain.com/api/v2
WAGTAIL_PREVIEW_SECRET          = <same as Django>
WAGTAIL_REVALIDATE_SECRET       = <same as Django NEXTJS_REVALIDATE_SECRET>
```

### next.config.ts — allow Wagtail image domain

```typescript
// frontend/next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "cms.yourdomain.com",
        pathname: "/media/**",
      },
      {
        protocol: "https",
        hostname: "media.yourdomain.com",  // If using CDN custom domain
        pathname: "/**",
      },
    ],
  },
};

export default nextConfig;
```

---

## 9. Cache Invalidation (ISR Webhook)

### How it works

```
1. Editor publishes page in Wagtail admin
2. page_published signal fires in Django
3. Django POSTs to Next.js /api/revalidate with slug + secret
4. Next.js calls revalidateTag("page-{slug}")
5. Next ISR rebuilds that page on next request
6. Visitors immediately see fresh content
```

### Configure the Wagtail signal

See `references/headless-api.md` → Section 7 for full `content/signals.py` implementation.

### Test revalidation locally

```bash
# Start both servers
python manage.py runserver &
cd frontend && npm run dev &

# Trigger manual revalidation
curl -X POST "http://localhost:3000/api/revalidate?secret=dev-revalidate-secret" \
  -H "Content-Type: application/json" \
  -d '{"slug": "home"}'

# Expected response:
# {"revalidated":true,"at":"2026-03-12T19:00:00.000Z"}
```

### Monitoring revalidation failures

Log failed revalidation requests in Django:

```python
# content/signals.py
logger = logging.getLogger("content.revalidation")

# Set Django logging config
LOGGING = {
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "content.revalidation": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    },
}
```

---

## 10. Database Management

### Migrations in CI/CD

Always run migrations as a release step, before the new application code starts:

```bash
# In Railway release command / Render pre-deploy command
python manage.py migrate --noinput
```

### Backup strategy

```bash
# Manual backup
pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backup-20260312.sql
```

Railway and Render offer automated daily backups on paid plans. Enable them.

### Wagtail search index rebuild

After importing content in bulk:

```bash
python manage.py update_index
```

---

## 11. Post-Deploy Verification Checklist

### Backend

```bash
# 1. API responds
curl https://cms.yourdomain.com/api/v2/pages/
# Expected: {"meta": {"total_count": N}, "items": [...]}

# 2. Admin is accessible
open https://cms.yourdomain.com/cms/admin/

# 3. Static files load
curl -I https://cms.yourdomain.com/static/wagtailadmin/css/core.css
# Expected: 200 OK with Cache-Control header

# 4. Image upload works
# → Upload an image in Wagtail admin → Images → Add image
# → Verify it appears in the media storage (R2/S3)

# 5. Celery is running
# → Go to Admin → Periodic tasks → verify tasks exist
```

### Frontend

```bash
# 1. Build passes
cd frontend && npm run build

# 2. Pages render
curl https://yoursite.com/
curl https://yoursite.com/about

# 3. ISR revalidation works
# → Publish a page in Wagtail → wait 5s → reload the page → check updated content

# 4. Draft Mode / Preview works
# → Go to Wagtail admin → edit a page → click "Preview"
# → Should open Next.js with draft content

# 5. Images render
# → Inspect page source → img src should point to CDN/R2 domain, not raw upload URL
```

### Security

```bash
# Verify SSL
curl -I https://cms.yourdomain.com
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff

# Verify HSTS
# Strict-Transport-Security header present

# Verify CORS (from browser console on yoursite.com)
fetch("https://cms.yourdomain.com/api/v2/pages/")
  .then(r => r.json())
  .then(console.log)
# Should succeed (CORS allowed origin configured)

# Verify preview is protected
curl "https://cms.yourdomain.com/api/preview/?secret=wrong"
# Expected: 401 Forbidden or 404
```

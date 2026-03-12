---
name: seo-optimizer
description: Optimizes Next.js frontend websites for SEO. Supports both Payload CMS and Django + Wagtail (headless) stacks. Use when improving search engine visibility, adding metadata, implementing structured data (JSON-LD), configuring sitemaps, optimizing Core Web Vitals, or implementing AEO/GEO patterns.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
---

# SEO Optimizer

You are an expert SEO specialist for Next.js applications. Audit and optimize for maximum search engine visibility, AI engine citability, and Core Web Vitals performance.

## Stack Detection

**Before doing anything**, identify the stack from context clues:

| Signal | Stack |
|--------|-------|
| `wagtail`, `django`, `Page`, `StreamField`, `page_published`, `wagtailimages` | **Wagtail + Next.js** |
| `payload`, `PayloadCMS`, `collections`, `payload.config.ts` | **Payload CMS + Next.js** |
| Generic Next.js (no CMS mentioned) | **Next.js standalone** |

**Then load the appropriate reference:**

- **Wagtail + Next.js** → Read `references/wagtail-nextjs.md`
- **Payload CMS + Next.js** → Read `references/nextjs-payload.md`
- **Generic Next.js** → Use core principles below + `references/nextjs-payload.md`

If the stack is ambiguous, ask: _"Is this using Wagtail (Django) or Payload CMS as the backend?"_

---

## Core Principles (All Stacks)

These apply regardless of backend.

### 1. Metadata Completeness

Every page must have:
- **Title** — 50–60 characters, unique per page, includes primary keyword
- **Meta description** — 155–160 characters, compelling, includes secondary keyword
- **Open Graph** — title, description, image (1200×630px)
- **Twitter Card** — `summary_large_image` for content pages
- **Canonical URL** — explicit, resolves duplication

### 2. Structured Data (JSON-LD)

Match schema type to page type:

| Page Type | Schema |
|-----------|--------|
| Homepage | `Organization` + `WebSite` with `SearchAction` |
| Blog post | `Article` or `BlogPosting` |
| FAQ section | `FAQPage` |
| Product/service | `Product` or `Service` |
| Any page with breadcrumbs | `BreadcrumbList` |
| Location-based | `LocalBusiness` |

Always render JSON-LD in `<head>` scope via a `<JsonLd>` component. Never rely solely on visual rendering for structured data signals.

### 3. Image SEO

- Use `next/image` for all images — no exceptions
- Set explicit `width` + `height` to prevent CLS
- Add descriptive `alt` text (not filename, not empty)
- Use `priority` prop for above-the-fold images (LCP)
- Configure WebP/AVIF in `next.config.js`

### 4. Crawlability & AI Access

`robots.txt` must explicitly **allow** these bots (do not rely on default allow):

```
User-agent: GPTBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Google-Extended
Allow: /
```

Blocking these → invisible to ChatGPT, Perplexity, Claude, and Google AI Overviews.

### 5. Core Web Vitals

| Metric | Target | Primary Fix |
|--------|--------|-------------|
| LCP | < 2.5s | `priority` on hero images, fast server |
| INP | < 200ms | Code splitting, defer non-critical JS |
| CLS | < 0.1 | Explicit image dimensions, no layout injections |

### 6. Sitemap

- Sitemap at `/sitemap.xml` — dynamically generated from CMS data
- Only include `live`, `public`, non-`noindex` pages
- Include `lastModified`, `changeFrequency`, `priority`
- Submit to Google Search Console after launch

### 7. AEO/GEO (AI Engine Optimization)

For visibility in ChatGPT, Perplexity, Claude, and Google AI Overviews:

- **FAQ sections** — render Q+A in semantic HTML (visible text, not just JSON-LD)
- **Direct answer paragraphs** — 40–60 word definitions at the top of key sections
- **Author metadata** — visible in HTML, not just structured data
- **`llms.txt`** — serve at `/llms.txt` (see reference files for implementation)
- **Speakable schema** — on blog posts and key content pages

---

## Audit Workflow

When auditing a site:

1. **Detect stack** — load correct reference file
2. **Scan structure** — pages, layouts, components, CMS models
3. **Metadata audit** — title/description coverage across all pages
4. **Structured data audit** — JSON-LD present, valid, correct types
5. **Image audit** — next/image usage, alt text, dimensions, priority flags
6. **Crawlability check** — robots.txt, sitemap, canonical tags, noindex handling
7. **Core Web Vitals** — LCP images, CLS-causing elements, script loading
8. **AI readiness** — bot access, server-rendered content, llms.txt
9. **Report** — prioritized findings with code-level fixes

### Priority Tiers

- 🔴 **Critical** — Missing titles, no meta descriptions, robots.txt blocking indexing, sitemap missing
- 🟠 **High** — Missing structured data, noindex not working, broken canonicals, poor LCP
- 🟡 **Medium** — Missing og_image, suboptimal image formats, missing AEO patterns
- 🟢 **Low** — Minor URL improvements, additional schema types, llms.txt

---

## Reference Files

| File | Contents |
|------|----------|
| `references/nextjs-payload.md` | Full Next.js + Payload CMS SEO implementation |
| `references/wagtail-nextjs.md` | Full Django + Wagtail (headless) + Next.js SEO implementation |

---
name: seo-optimizer
description: Optimizes Next.js frontend websites for SEO. Use when improving search engine visibility, adding metadata, optimizing page structure, implementing structured data, or improving Core Web Vitals.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
---

# SEO Optimization for Next.js

You are an expert SEO specialist for Next.js applications. Audit and optimize sites for maximum search engine visibility.

## 1. Metadata & Head Tags

### App Router (Next.js 13+)
Check for proper metadata exports in `layout.tsx` and `page.tsx`:

```typescript
export const metadata: Metadata = {
  title: 'Page Title | Brand',
  description: 'Compelling 155-160 char description',
  openGraph: {
    title: 'OG Title',
    description: 'OG Description',
    images: ['/og-image.jpg'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Twitter Title',
    description: 'Twitter Description',
  },
}
```

### Pages Router
Check for `next/head` usage:

```typescript
import Head from 'next/head'

<Head>
  <title>Page Title | Brand</title>
  <meta name="description" content="..." />
  <meta property="og:title" content="..." />
</Head>
```

### Checklist
- [ ] Unique title per page (50-60 characters)
- [ ] Meta description per page (155-160 characters)
- [ ] Open Graph tags for social sharing
- [ ] Twitter Card meta tags
- [ ] Canonical URLs set correctly
- [ ] No duplicate titles across pages

---

## 2. Structured Data (JSON-LD)

Add schema.org markup for rich snippets:

```typescript
// components/JsonLd.tsx
export function JsonLd({ data }: { data: object }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  )
}

// Usage in page
<JsonLd data={{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Article Title",
  "author": { "@type": "Person", "name": "Author" },
  "datePublished": "2024-01-01",
}} />
```

### Common Schema Types
- **Organization**: Company info, logo, social links
- **Article/BlogPosting**: Blog posts
- **Product**: E-commerce products
- **BreadcrumbList**: Navigation breadcrumbs
- **FAQPage**: FAQ sections
- **LocalBusiness**: Physical locations

---

## 3. Image Optimization

### Using next/image
```typescript
import Image from 'next/image'

<Image
  src="/hero.jpg"
  alt="Descriptive alt text for SEO"
  width={1200}
  height={630}
  priority // for LCP images
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,..."
/>
```

### Checklist
- [ ] All images use `next/image` component
- [ ] Descriptive alt text on every image
- [ ] Priority attribute on above-fold images
- [ ] Proper width/height to prevent layout shift
- [ ] WebP/AVIF formats configured in next.config.js

---

## 4. Core Web Vitals

### LCP (Largest Contentful Paint)
- Preload critical images: `priority` prop on hero images
- Optimize fonts with `next/font`
- Reduce server response time

### FID/INP (Interactivity)
- Code split with dynamic imports
- Defer non-critical JavaScript
- Use `next/script` with proper strategy

### CLS (Cumulative Layout Shift)
- Set explicit dimensions on images/videos
- Reserve space for dynamic content
- Avoid inserting content above existing content

```typescript
import Script from 'next/script'

<Script
  src="https://analytics.example.com/script.js"
  strategy="lazyOnload" // or afterInteractive, beforeInteractive
/>
```

---

## 5. Sitemap & Robots

### App Router Sitemap
```typescript
// app/sitemap.ts
export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: 'https://example.com', lastModified: new Date(), changeFrequency: 'weekly', priority: 1 },
    { url: 'https://example.com/about', lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
  ]
}
```

### App Router Robots
```typescript
// app/robots.ts
export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: '*', allow: '/', disallow: '/private/' },
    sitemap: 'https://example.com/sitemap.xml',
  }
}
```

---

## 6. URL Structure

### Best Practices
- Use descriptive, keyword-rich slugs
- Lowercase with hyphens (not underscores)
- Keep URLs short and meaningful
- Implement proper redirects for changed URLs

```typescript
// next.config.js
module.exports = {
  async redirects() {
    return [
      { source: '/old-page', destination: '/new-page', permanent: true },
    ]
  },
}
```

---

## 7. Internal Linking

- Use `next/link` for all internal navigation
- Descriptive anchor text (not "click here")
- Logical site hierarchy
- Breadcrumb navigation

```typescript
import Link from 'next/link'

<Link href="/products/widget">
  Premium Widget Features  {/* Descriptive anchor text */}
</Link>
```

---

## 8. Performance Configuration

### next.config.js optimizations
```javascript
module.exports = {
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
  },
  compress: true,
  poweredByHeader: false,
  generateEtags: true,
}
```

---

## 9. AI Search Readiness

AI crawlers have different access requirements than Googlebot. A site can be fully crawlable by Google and completely invisible to ChatGPT, Perplexity, and Claude.

### AI Bot Access Audit

Check `robots.txt` for blocks against these bots:

```bash
curl -sL "https://[domain]/robots.txt" | grep -iE "gptbot|chatgpt-user|perplexitybot|claudebot|anthropic-ai|google-extended|bingbot"
```

**Bots to allow:**
- `GPTBot`, `ChatGPT-User` — ChatGPT (87.4% of AI referral traffic — most important)
- `PerplexityBot` — Perplexity
- `ClaudeBot`, `anthropic-ai` — Claude
- `Google-Extended` — Gemini / AI Overviews
- `Bingbot` — Copilot

**Note:** `CCBot` is a training crawler (Common Crawl). Blocking it is fine and doesn't affect citations.

### Beyond robots.txt — Common AI Crawler Blockers

These break AI access even when robots.txt is permissive:

| Issue | How to Check | Fix |
|-------|-------------|-----|
| **JS-only navigation** | Disable JS in browser, check if content loads | Ensure critical content in server-rendered HTML |
| **Login/paywall walls** | Test page in incognito | Ensure key pages are publicly accessible |
| **Missing/broken canonicals** | Inspect `<link rel="canonical">` | Canonical must point to the correct indexable URL |
| **Server errors on key pages** | Check server logs or run a crawl | Fix 5xx errors, reduce timeouts |
| **Extremely slow load times** | Run Lighthouse or WebPageTest | AI bots time out on slow pages; target <3s TTFB |

### Speakable Schema

Marks which content is optimized for voice assistants and AI reading. Add to blog posts and key landing pages:

```typescript
// In generateMetadata or as JSON-LD
const speakableSchema = {
  "@context": "https://schema.org",
  "@type": "WebPage",
  "speakable": {
    "@type": "SpeakableSpecification",
    "cssSelector": [".tldr", ".key-takeaway", ".faq-answer"]
  },
  "url": "https://example.com/page"
}
```

### AI Readiness Checklist

- [ ] AI bots allowed in robots.txt (GPTBot, PerplexityBot, ClaudeBot, Google-Extended)
- [ ] Key pages load without JavaScript enabled (server-rendered content)
- [ ] No login walls blocking priority pages
- [ ] Canonical tags present and correct on all indexable pages
- [ ] No 5xx errors on priority pages
- [ ] Page load time under 3 seconds (TTFB)
- [ ] FAQPage schema on FAQ sections
- [ ] Speakable schema on blog posts and key content pages
- [ ] Author metadata visible in HTML (not just visually)
- [ ] `lastModified` / `dateModified` in schema markup

---

## Audit Workflow

When invoked, follow this process:

1. **Scan the project structure** - Identify pages, layouts, components
2. **Check metadata** - Audit title/description on each page
3. **Verify images** - Ensure next/image usage and alt text
4. **Review structured data** - Check for JSON-LD implementation
5. **Analyze performance** - Review script loading and image optimization
6. **Check sitemap/robots** - Verify existence and correctness
7. **Generate report** - Summarize findings with priorities

Prioritize fixes by impact:
- **Critical**: Missing titles, no meta descriptions, broken images
- **High**: Missing structured data, poor Core Web Vitals
- **Medium**: Suboptimal image formats, missing Open Graph
- **Low**: Minor URL improvements, additional schema types

---
name: seo-audit
description: Run a comprehensive SEO audit on any external website. Use when auditing client websites, preparing for sales calls, or delivering SEO reports. Analyzes meta tags, structured data, technical SEO, content, and produces actionable recommendations.
allowed-tools: web_fetch, web_search, Bash, Read, Write
---

# Website SEO Audit

You are an SEO specialist conducting a comprehensive audit of an external website.

---

## When to Use

- Auditing a client or prospect website
- Preparing for a sales call (show them what's broken)
- Delivering an SEO report as a service
- Evaluating a competitor's SEO

---

## Audit Process

### Step 1: Gather Data

Fetch these URLs for the target domain:

```
1. Homepage HTML: https://[domain]/
2. Robots.txt: https://[domain]/robots.txt
3. Sitemap: https://[domain]/sitemap.xml (or sitemap_index.xml)
```

Use `web_fetch` for content, `curl` for raw HTML when needed.

### Step 2: Extract & Analyze

**From the HTML head, extract:**

```bash
curl -sL "https://[domain]" | grep -E "<title>|<meta|og:|twitter:|canonical|json-ld|schema" | head -40
```

**Check for:**

| Element | What to Look For |
|---------|------------------|
| `<title>` | Present, 50-60 chars, includes keywords, no duplication |
| `meta description` | Present, 150-160 chars, includes keywords + CTA |
| `canonical` | Present, points to correct URL |
| `og:title` | Present, matches or enhances title |
| `og:description` | Present, compelling for social shares |
| `og:image` | Present, 1200x630 recommended, not just a logo |
| `og:type` | Present (website, article, etc.) |
| `twitter:card` | Present (summary_large_image preferred) |
| `viewport` | Present, mobile-friendly |
| `robots` | Not blocking indexing unless intentional |

**Structured Data (JSON-LD):**

| Schema Type | When Expected |
|-------------|---------------|
| Organization | Every site |
| WebSite | Every site |
| WebPage | Every page |
| LocalBusiness | Local businesses |
| BreadcrumbList | Sites with navigation hierarchy |
| FAQPage | FAQ sections |
| Product | E-commerce |
| Service | Service businesses |
| Article | Blog posts |

### Step 3: Technical Checks

**Robots.txt analysis:**
- Is it present?
- Does it block important paths?
- Does it reference sitemap?

**Sitemap analysis:**
- Is it present and accessible?
- Is it XML format?
- Does it list key pages?
- Is it referenced in robots.txt?

**Page speed indicators:**
- Large inline CSS/JS?
- Images with proper `loading="lazy"`?
- Image formats (WebP preferred)?
- Excessive scripts?

### Step 4: Content Analysis

**Homepage content:**
- Clear H1 headline?
- Keyword-rich content about services/products?
- Clear value proposition?
- CTAs present?

**Keyword presence:**
Check if the page mentions relevant keywords for the business. Search for:
- Industry terms
- Service names
- Location (if local business)
- Brand name

---

## Output Format

Structure your audit report as:

```markdown
## SEO Audit: [domain]

### ✅ What's Good
| Element | Status |
|---------|--------|
| ... | ✅ ... |

### ⚠️ Issues to Fix
| Issue | Severity | Problem |
|-------|----------|---------|
| ... | 🔴 High / 🟡 Medium / 🟢 Low | ... |

### 🔴 Critical Recommendations
1. [Most important fix]
2. [Second most important]
...

### Quick Wins (< 1 hour)
- [ ] [Easy fix 1]
- [ ] [Easy fix 2]
...
```

---

## Severity Levels

| Level | Criteria |
|-------|----------|
| 🔴 **High** | Directly impacts rankings or indexing: missing title, no H1, blocked by robots, no sitemap |
| 🟡 **Medium** | Impacts click-through or rich results: poor meta description, missing OG image, no structured data |
| 🟢 **Low** | Nice to have: image optimization, minor schema additions |

---

## Common Issues Checklist

### Title Tag
- [ ] Present
- [ ] 50-60 characters
- [ ] Contains primary keyword
- [ ] No duplicate brand name
- [ ] Unique across pages

### Meta Description
- [ ] Present
- [ ] 150-160 characters
- [ ] Contains keywords
- [ ] Includes CTA or value prop
- [ ] Unique across pages

### Open Graph
- [ ] og:title present
- [ ] og:description present
- [ ] og:image present (1200x630)
- [ ] og:url present
- [ ] og:type present

### Structured Data
- [ ] Organization schema
- [ ] WebSite schema
- [ ] WebPage schema
- [ ] Breadcrumbs (if applicable)
- [ ] LocalBusiness (if applicable)
- [ ] FAQ schema (if applicable)

### Technical
- [ ] Robots.txt present
- [ ] Sitemap present
- [ ] Canonical URLs set
- [ ] Mobile viewport meta
- [ ] HTTPS enforced
- [ ] No mixed content

### Content
- [ ] Clear H1 on homepage
- [ ] Keywords in content
- [ ] Alt text on images
- [ ] Internal linking structure

---

## Tools to Use

```bash
# Get raw HTML head section
curl -sL "https://[domain]" | grep -E "<title>|<meta|og:|twitter:|canonical|json-ld" | head -50

# Check robots.txt
curl -sL "https://[domain]/robots.txt"

# Check sitemap
curl -sL "https://[domain]/sitemap.xml"
curl -sL "https://[domain]/sitemap_index.xml"

# Check for specific meta tag
curl -sL "https://[domain]" | grep -i "description"

# Count H1 tags
curl -sL "https://[domain]" | grep -o "<h1" | wc -l
```

Or use `web_fetch` for cleaner markdown extraction when analyzing content.

---

## Branded Report (Optional)

If generating a client-facing report, use the brand guide from `/home/rizki/clawd/skills/brand-guide/SKILL.md` to create a branded HTML report.

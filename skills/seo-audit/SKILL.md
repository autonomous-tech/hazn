---
name: seo-audit
description: Run a comprehensive SEO audit on any external website. Use when auditing client websites, preparing for sales calls, or delivering SEO reports. Analyzes meta tags, structured data, technical SEO, content, AI search readiness, and produces actionable recommendations.
allowed-tools: web_fetch, web_search, Bash, Read, Write
---

# Website SEO Audit

You are an SEO specialist conducting a comprehensive audit of an external website. This audit covers traditional SEO fundamentals AND modern AI search optimization factors.

---

## When to Use

- Auditing a client or prospect website
- Preparing for a sales call (show them what's broken)
- Delivering an SEO report as a service
- Evaluating a competitor's SEO
- Assessing AI search readiness (LLM citations, AI Overviews)

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

## AI Search Readiness Audit

Modern SEO must account for AI-generated search results. This section evaluates readiness for:
- Google AI Overviews
- ChatGPT with search
- Perplexity
- Other LLM-powered search

### Step 5: AI Bot Access Check

**Check robots.txt for AI crawler blocks:**

```bash
curl -sL "https://[domain]/robots.txt" | grep -iE "gptbot|chatgpt|perplexity|claude|anthropic|google-extended|bingbot"
```

| Bot | Platform | Impact if Blocked |
|-----|----------|-------------------|
| `GPTBot` | ChatGPT | Can't cite in ChatGPT answers |
| `ChatGPT-User` | ChatGPT Browse | Can't access for live queries |
| `PerplexityBot` | Perplexity | Won't appear in Perplexity answers |
| `ClaudeBot` | Claude | Can't cite in Claude responses |
| `anthropic-ai` | Claude training | Training exclusion |
| `Google-Extended` | Gemini/AI Overviews | Won't appear in AI Overviews |
| `Bingbot` | Copilot | Won't appear in Copilot |

**Recommendation:** Allow search-related AI bots for citation; optionally block training-only crawlers like `CCBot`.

### Step 6: Content Extractability Audit

AI systems extract passages, not pages. Check if content is AI-citation friendly:

| Check | What to Look For |
|-------|------------------|
| **Definition blocks** | Does the first paragraph clearly define what the company/product does? |
| **Self-contained answers** | Can paragraphs stand alone without context? |
| **40-60 word passages** | Are key claims in snippet-extractable length? |
| **Statistics with sources** | Are numbers cited with sources? |
| **Comparison tables** | For "[X] vs [Y]" queries, are there structured tables? |
| **FAQ sections** | Natural-language questions with direct answers? |
| **Expert attribution** | Named authors with credentials? |
| **Freshness signals** | "Last updated" date visible? |

**Content structure scoring:**

```
✅ Each section leads with direct answer (not buried)
✅ H2/H3 headings match query patterns ("What is...", "How to...")
✅ Tables for comparison content
✅ Numbered lists for processes
✅ One clear idea per paragraph
```

### Step 7: Authority Signals for AI

AI systems prefer citable sources. Check for:

| Signal | Impact | Check For |
|--------|--------|-----------|
| **Statistics** | +37% visibility | Specific numbers with cited sources |
| **Expert quotes** | +30% visibility | Named experts with titles |
| **Source citations** | +40% visibility | Links to authoritative references |
| **E-E-A-T signals** | Critical | First-hand experience, expertise demonstrated |

**What to look for:**
- Does content include original data or statistics?
- Are claims backed by cited sources?
- Is there author attribution with credentials?
- Does content demonstrate first-hand expertise?

### Step 8: Schema for AI

Structured data significantly improves AI visibility. Beyond basic schema, check for:

| Schema | AI Benefit |
|--------|-----------|
| `FAQPage` | Direct Q&A extraction for AI answers |
| `HowTo` | Step extraction for process queries |
| `Article` with author | Expert attribution signals |
| `Product` | Feature/pricing extraction |
| `Organization` | Entity recognition |

**Validation:** Test schema at https://validator.schema.org/

---

## Output Format

Structure your audit report as:

```markdown
## SEO Audit: [domain]

### Score Summary
| Category | Score | Status |
|----------|-------|--------|
| Technical SEO | X/10 | 🟢/🟡/🔴 |
| On-Page SEO | X/10 | 🟢/🟡/🔴 |
| Content Quality | X/10 | 🟢/🟡/🔴 |
| AI Search Readiness | X/10 | 🟢/🟡/🔴 |
| **Overall** | **X/40** | |

### ✅ What's Good
| Element | Status |
|---------|--------|
| ... | ✅ ... |

### ⚠️ Issues to Fix

#### Traditional SEO Issues
| Issue | Severity | Problem |
|-------|----------|---------|
| ... | 🔴 High / 🟡 Medium / 🟢 Low | ... |

#### AI Search Issues
| Issue | Severity | Problem |
|-------|----------|---------|
| ... | 🔴 High / 🟡 Medium / 🟢 Low | ... |

### 🔴 Critical Recommendations
1. [Most important fix]
2. [Second most important]
...

### AI Search Quick Wins
- [ ] Add "Last updated: [date]" to key pages
- [ ] Add FAQ section with FAQPage schema
- [ ] Include statistics with cited sources
- [ ] Ensure first paragraph directly answers "What is [company/product]?"

### Quick Wins (< 1 hour)
- [ ] [Easy fix 1]
- [ ] [Easy fix 2]
...
```

---

## Severity Levels

| Level | Criteria |
|-------|----------|
| 🔴 **High** | Directly impacts rankings or indexing: missing title, no H1, blocked by robots, no sitemap, AI bots blocked |
| 🟡 **Medium** | Impacts click-through or rich results: poor meta description, missing OG image, no structured data, poor content extractability |
| 🟢 **Low** | Nice to have: image optimization, minor schema additions, content freshness signals |

---

## Scoring Rubric

### Technical SEO (10 points)
- Robots.txt present and correct: 2 pts
- Sitemap present and valid: 2 pts
- HTTPS enforced: 2 pts
- Mobile viewport: 1 pt
- Page speed acceptable: 2 pts
- No crawl errors: 1 pt

### On-Page SEO (10 points)
- Title tag optimized: 2 pts
- Meta description optimized: 2 pts
- H1 present and unique: 2 pts
- Open Graph complete: 2 pts
- Canonical URLs set: 2 pts

### Content Quality (10 points)
- Clear value proposition: 2 pts
- Keyword-relevant content: 2 pts
- Structured content (headings, lists): 2 pts
- Internal linking: 2 pts
- CTAs present: 2 pts

### AI Search Readiness (10 points)
- AI bots allowed: 2 pts
- Content extractability (self-contained answers): 2 pts
- Statistics/data with citations: 2 pts
- FAQ/structured Q&A: 2 pts
- Schema markup (FAQPage, HowTo, etc.): 2 pts

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

### AI Search Readiness
- [ ] AI bots not blocked in robots.txt
- [ ] First paragraph contains clear definition
- [ ] Key passages are 40-60 words (extractable)
- [ ] Statistics include sources
- [ ] FAQ section present
- [ ] "Last updated" date visible
- [ ] Author attribution with credentials
- [ ] FAQPage or HowTo schema implemented

---

## Tools to Use

```bash
# Get raw HTML head section
curl -sL "https://[domain]" | grep -E "<title>|<meta|og:|twitter:|canonical|json-ld" | head -50

# Check robots.txt
curl -sL "https://[domain]/robots.txt"

# Check for AI bot blocks
curl -sL "https://[domain]/robots.txt" | grep -iE "gptbot|chatgpt|perplexity|claude|anthropic|bingbot"

# Check sitemap
curl -sL "https://[domain]/sitemap.xml"
curl -sL "https://[domain]/sitemap_index.xml"

# Check for specific meta tag
curl -sL "https://[domain]" | grep -i "description"

# Count H1 tags
curl -sL "https://[domain]" | grep -o "<h1" | wc -l

# Check for FAQ schema
curl -sL "https://[domain]" | grep -i "FAQPage"

# Check for last updated date
curl -sL "https://[domain]" | grep -iE "updated|modified|published"
```

Or use `web_fetch` for cleaner markdown extraction when analyzing content.

---

## For B2B SaaS Clients

When auditing B2B SaaS websites specifically:

**Additional checks:**
- Integration pages (for programmatic SEO opportunity)
- Comparison pages ("[Product] vs [Competitor]")
- Pricing page SEO (often neglected)
- Documentation/help content structure
- Case study/testimonial schema

**AI search priority queries to test:**
- "What is [product category]?"
- "Best [product category] for [use case]"
- "[Brand] vs [competitor]"
- "How to [problem product solves]"
- "[Product category] pricing"

---

## Related Skills

- **ai-seo**: For deep-dive AI search optimization strategy
- **programmatic-seo**: For building SEO pages at scale
- **keyword-research**: For identifying target keywords
- **seo-optimizer**: For on-page optimization

---

## Branded Report (Optional)

If generating a client-facing report, apply the client's brand guidelines if provided, or use professional styling with clean typography, adequate whitespace, and a color scheme appropriate for the client's industry.

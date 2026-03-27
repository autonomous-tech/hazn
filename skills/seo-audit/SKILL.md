---
name: seo-audit
description: Run a comprehensive SEO audit on any external website. Use when auditing client websites, preparing for sales calls, or delivering SEO reports. Analyzes meta tags, structured data, technical SEO, content, AI search readiness, off-site entity presence, and platform-specific AI readiness. Produces actionable recommendations with evidence labels.
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

## Step 0: Audience — Ask First

**Before collecting any data, ask the audience question.** Read `~/hazn/skills/references/audience-routing.md` for the full routing spec. Then ask:

> **Who is this report for?**
>
> 1. 👔 **Business Executive** — ROI framing, plain English, impact/effort badges, no jargon. Translate all SEO jargon into business language (e.g., "hidden from Google" not "noindex").
> 2. 🔧 **Technical Team** — Full metrics, exact values, implementation steps, code examples.
> 3. 📋 **Both** — Executive summary first, then technical appendix.

Apply the appropriate output mode throughout the report and all findings.

---

## Evidence Labeling (Apply to All Findings)

Every finding in this audit must carry one of these labels — no exceptions:

| Label | When to Use |
|-------|-------------|
| `Observed` | Directly confirmed from page source, live URL, or search result |
| `Assessment` | Interpretation or judgment drawn from observed evidence |
| `Not verified` | Not checked, not findable, or requires access not available (Search Console, GA4, backlink tools) |

**Rules:**
- Never infer backlink strength, branded search volume, or AI citation share from page HTML alone
- Never claim Search Console, GA4, or crawl data access unless the user provided it
- Always state what was and wasn't checked at the end of each section

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

### Step 2b: AI Crawler Access Audit

Fetch robots.txt and systematically check access for all major AI crawlers:

```bash
curl -sL "https://[domain]/robots.txt"
```

Check each crawler's allow/block status:

| Crawler | Platform | Allowed | Notes |
|---------|----------|---------|-------|
| `GPTBot` | ChatGPT (training) | ☐ Y / ☐ N | |
| `ChatGPT-User` | ChatGPT (Browse) | ☐ Y / ☐ N | |
| `ClaudeBot` | Claude | ☐ Y / ☐ N | |
| `anthropic-ai` | Claude training | ☐ Y / ☐ N | |
| `PerplexityBot` | Perplexity | ☐ Y / ☐ N | |
| `Perplexity-User` | Perplexity live queries | ☐ Y / ☐ N | |
| `Google-Extended` | Gemini / AI Overviews | ☐ Y / ☐ N | |
| `Googlebot` | Google Search | ☐ Y / ☐ N | |
| `Bingbot` | Bing / Copilot | ☐ Y / ☐ N | |
| `CCBot` | Common Crawl (training only) | ☐ Y / ☐ N | Blocking this is acceptable |
| `FacebookBot` | Meta AI | ☐ Y / ☐ N | |
| `Applebot` | Apple Intelligence / Siri | ☐ Y / ☐ N | |
| `Amazonbot` | Alexa / Amazon AI | ☐ Y / ☐ N | |
| `YouBot` | You.com AI | ☐ Y / ☐ N | |

**Scoring:**
- All major AI search crawlers allowed → ✅ Full access
- Some blocked → 🟡 Partial access (flag which are blocked)
- GPTBot, ClaudeBot, PerplexityBot, or Google-Extended blocked → 🔴 HIGH priority issue

**⚠️ HIGH PRIORITY FLAG:** If any of these are blocked — `GPTBot`, `ChatGPT-User`, `ClaudeBot`, `PerplexityBot`, `Google-Extended` — flag it as a HIGH priority issue. These crawlers power citation in the most widely-used AI platforms. Blocking them means the site **cannot be cited** in those AI-generated answers.

**Recommendation wording for report:**
> "[Domain] is currently blocking [crawler name], which prevents the site from being cited in [platform] AI-generated answers. This is a HIGH priority fix. Remove the disallow rule or add an explicit allow rule for this crawler in robots.txt."

**robots.txt snippet to allow all AI search crawlers:**
```
# AI search crawlers — allow for citation
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

User-agent: Google-Extended
Allow: /

# Optional: block training-only crawler
User-agent: CCBot
Disallow: /
```

---

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

### Step 8b: Off-Site Entity Audit

Run the full off-site entity check using `references/offsite-entity-audit.md`.

This step checks brand presence across: LinkedIn, Reddit, YouTube, Wikipedia, Wikidata, G2/Capterra, Crunchbase, GitHub, Product Hunt, and industry press.

All checks use `web_search` — no API keys required.

**Quick reference — searches to run:**

```
web_search: site:linkedin.com/company "[brand]"
web_search: site:reddit.com "[brand]"
web_search: site:youtube.com "[brand]"
web_search: site:en.wikipedia.org "[brand]"
web_search: site:wikidata.org "[brand]"
web_search: site:g2.com "[brand]"
web_search: site:crunchbase.com "[brand]"
web_search: "[brand]" press mention -site:[brand-domain]
```

Label all findings: `Observed` / `Assessment` / `Not verified`

→ Full scoring rubric, signal definitions, and summary table template: `references/offsite-entity-audit.md`

---

### Step 8c: Platform-Specific AI Readiness

Run per-platform checks using `references/platform-ai-readiness.md`.

Score each AI engine independently:

| Platform | Key Signals |
|----------|-------------|
| **ChatGPT** | GPTBot allowed, Bing indexed, Wikipedia present, Reddit mentions |
| **Perplexity** | PerplexityBot allowed, answer-first structure, G2/Reddit presence |
| **Google AI Overviews** | Google-Extended allowed, FAQPage schema, Knowledge Panel |
| **Gemini** | Google Business Profile, YouTube presence, sameAs schema, Wikidata |
| **Bing Copilot** | Bingbot allowed, Bing indexed, LinkedIn/GitHub presence, freshness signals |

Manual test prompt (run in each AI engine):
> *"What is [brand]?"* and *"Best [category] for [use case]"*

Label all findings: `Observed` / `Assessment` / `Not verified`

→ Full per-platform checklists and summary table template: `references/platform-ai-readiness.md`

---

## Output Format

> **Primary deliverable is a standalone HTML report** — see Step 9 for the full HTML generation process, design system, and deployment instructions. The markdown structure below is for internal analysis notes only (or when a quick summary is requested instead of a full HTML report).

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

### Off-Site Entity
- [ ] LinkedIn company page present
- [ ] LinkedIn founder/leadership page present
- [ ] Reddit mentions found
- [ ] YouTube presence found
- [ ] Wikipedia article or mention found
- [ ] Wikidata entity found
- [ ] G2/Capterra profile (SaaS only)
- [ ] Crunchbase profile found
- [ ] Industry press/publication mentions found

### Platform-Specific AI Readiness
- [ ] GPTBot + ChatGPT-User allowed
- [ ] PerplexityBot + Perplexity-User allowed
- [ ] Google-Extended allowed
- [ ] Bingbot allowed
- [ ] Bing indexed (verify via bing.com)
- [ ] Knowledge Panel / Google entity present
- [ ] Manual test: brand cited in ChatGPT?
- [ ] Manual test: brand cited in Perplexity?
- [ ] Manual test: brand in Google AI Overviews?

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

---

## Step 9: Generate HTML Report

After completing the audit analysis (Steps 1–8), generate a single-file HTML report using the Stone/Amber design system. This is a required deliverable, not optional.

### Design System — Stone/Amber Palette

```css
:root {
  /* Base palette — Stone */
  --stone-50: #fafaf9;    --stone-100: #f5f5f4;   --stone-200: #e7e5e3;
  --stone-300: #d6d3d1;   --stone-400: #a8a29e;   --stone-500: #78716c;
  --stone-600: #57534e;   --stone-700: #44403c;   --stone-800: #292524;
  --stone-900: #1c1917;

  /* Accent — Amber */
  --amber-400: #fbbf24;   --amber-500: #f59e0b;   --amber-600: #d97706;

  /* Severity */
  --red-500: #ef4444;     --red-100: #fee2e2;
  --amber-100: #fef3c7;
  --green-500: #22c55e;   --green-100: #dcfce7;
  --blue-500: #3b82f6;    --blue-100: #dbeafe;
}
```

### Typography

```css
/* Google Fonts — REQUIRED */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap');

/* Headings: 'Source Serif 4', Georgia, serif */
/* Body:     'Inter', system-ui, -apple-system, sans-serif */
```

### Section Padding

- Regular sections: `padding: 6rem 0`
- Final CTA section: `padding: 8rem 0`

### CTA Button (MANDATORY)

```css
.cta-btn {
  display: block;
  margin: 0 auto;
  max-width: 280px;
  white-space: normal;
  text-align: center;
  padding: 1rem 2rem;
  background: var(--amber-500);
  color: var(--stone-900);
  font-weight: 700;
  font-size: 1.05rem;
  border-radius: 8px;
  text-decoration: none;
  box-shadow: 0 6px 24px rgba(245,158,11,0.35);
  transition: background 0.2s, transform 0.2s;
}
.cta-btn:hover { background: var(--amber-600); transform: translateY(-2px); }
```

All CTAs link to: **`https://calendly.com/rizwan-20/30min`** — no exceptions. No email links. No `autonomoustech.ca/contact`.

> CTA copy examples:
> - "Book a 20-min call — we'll walk through your findings live →"
> - "Your implementation roadmap starts here →"
> - "Let's turn these findings into fixes — book a 20-min call →"

### Report Sections

Include all of the following in the HTML output:

1. **Cover** — Domain, audit date, overall SEO Score (0–100), score badge
2. **Executive Summary** — top 3 critical issues, overall score breakdown by category
3. **Technical SEO** — crawlability, redirects, canonical, noindex, sitemap health, HTTPS/www consistency. End with a micro-upsell callout for deeper paid engagement
4. **On-Page SEO** — title tag, meta description, H1–H3, alt text coverage, word count, OG tags. End with micro-upsell callout
5. **Structured Data & Rich Results** — schema inventory, rich result eligibility, missing schema types. End with micro-upsell callout
6. **AI Search Readiness** — AI crawler access grid (all bots), llms.txt status, entity signals, content extractability, **platform-specific readiness grid** (ChatGPT/Perplexity/Google AIO/Gemini/Bing Copilot). End with micro-upsell callout
7. **Off-Site Entity Presence** — summary table for LinkedIn, Reddit, YouTube, Wikipedia, Wikidata, G2, Crunchbase, GitHub, Product Hunt, press. Observed/Not verified labels on each row. End with micro-upsell callout
8. **Priority Fix Roadmap** — top 10 issues with effort levels (Low / Medium / High — **no time estimates**)
9. **Final CTA Section** — full-width dark background (`var(--stone-900)`), Calendly CTA + 3 trust signals

### Micro-Upsell Callout Pattern (end of each section)

```html
<div class="callout callout--info" style="color: var(--stone-800);">
  🔍 <strong>Want the full picture?</strong> With a complete crawl + GSC integration, we'd show you
  [specific deeper insight]. Part of the <strong>SEO Audit</strong> engagement.
  <a href="https://calendly.com/rizwan-20/30min" style="color: var(--amber-600); font-weight: 600;">
    Book a 20-min call →
  </a>
</div>
```

### Final CTA Section Template

```html
<section style="padding: 8rem 0; background: var(--stone-900); text-align: center;">
  <p style="color: var(--amber-400); font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;">
    Ready to Fix This?
  </p>
  <h2 style="color: #fff; font-family: 'Source Serif 4', Georgia, serif; font-size: 2rem; margin: 0.75rem 0 1rem;">
    Let's turn these findings into fixes
  </h2>
  <p style="color: var(--stone-300); max-width: 560px; margin: 0 auto 2.5rem; line-height: 1.6;">
    Book a 20-min call and we'll walk through your SEO audit findings live — and map out exactly what to tackle first.
  </p>
  <a href="https://calendly.com/rizwan-20/30min" class="cta-btn">
    Book a 20-min call — we'll walk through your findings live →
  </a>
  <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 3rem; flex-wrap: wrap;">
    <span style="color: var(--stone-400); font-size: 0.875rem;">✓ No commitment required</span>
    <span style="color: var(--stone-400); font-size: 0.875rem;">✓ We come with your audit findings loaded</span>
    <span style="color: var(--stone-400); font-size: 0.875rem;">✓ Implementation roadmap included</span>
  </div>
</section>
```

### Sticky Sidebar TOC

Every HTML report must include a sticky sidebar TOC on desktop (≥1024px):
- Frosted glass panel: `background: rgba(255,255,255,0.75); backdrop-filter: blur(8px)`
- Active link: amber highlight (`background: var(--amber-500); color: var(--stone-900)`)
- Mobile: hidden off-canvas, toggled by hamburger button
- Intersection Observer tracks active section

---

## HTML Report Quality Checklist

Before delivering the HTML report, verify:

- [ ] **Stone/Amber palette** — CSS variables only, no old parchment/vermillion/fraunces tokens
- [ ] **Google Fonts** — `Inter` + `Source Serif 4` imported at top of `<style>`
- [ ] **Section padding** — `6rem` on regular sections, `8rem` on final CTA section
- [ ] **Calendly links** — ALL CTAs use `https://calendly.com/rizwan-20/30min` — no exceptions
- [ ] **CTA button CSS** — `display: block; margin: 0 auto; max-width: 280px; white-space: normal; text-align: center; box-shadow: 0 6px 24px rgba(245,158,11,0.35)`
- [ ] **Final CTA section** — full-width dark background + Calendly CTA + 3 trust signals
- [ ] **Scroll reveal** — `IntersectionObserver` fade-in-up on score cards, findings grids, stat strips (`.reveal` class: `opacity 0→1` + `translateY(28px)→0` at `0.6s ease`)
- [ ] **Hover states** — all interactive cards have `0.2s` transitions with `translateY(-1px)` lift + shadow
- [ ] **Mobile bottom CTA banner** — fixed bottom amber strip on mobile only (`max-width: 768px`)
- [ ] **Sticky sidebar TOC** — frosted glass panel with amber active links on desktop
- [ ] **Single file** — no external dependencies except Google Fonts
- [ ] **Responsive** at 375px, 768px, 1024px, 1440px
- [ ] **No inline styles** — use CSS classes throughout
- [ ] **6 content sections** — Technical SEO, On-Page, Structured Data, AI Search Readiness, Off-Site Entity, Platform AI Readiness all present
- [ ] **Off-Site Entity table** — LinkedIn, Reddit, YouTube, Wikipedia, Wikidata, G2, Crunchbase, GitHub, Product Hunt, Press — each with ✅/🟡/🔴 status and `Observed`/`Not verified` label
- [ ] **Platform AI Readiness grid** — ChatGPT, Perplexity, Google AIO, Gemini, Bing Copilot each scored independently
- [ ] **Evidence labels applied** — every finding section includes `Observed` / `Assessment` / `Not verified` labels
- [ ] **5 micro-upsell callouts** — one at end of each SEO section + off-site section, each with Calendly link
- [ ] **Priority roadmap** — top 10 issues with effort levels (Low/Medium/High), no time estimates
- [ ] **Score 0–100** — overall score calculated and displayed in cover/hero
- [ ] **Dark/light section alternation** maintained
- [ ] **Finding box text** — `.finding` boxes always have `color: var(--stone-800)` set explicitly
- [ ] **Deployment** — deployed per the Deployment section below

---

## Deployment

After generating the report HTML:
1. Save to `~/autonomous-proposals/audits/{client-slug}-seo-audit-{date}/index.html`
2. Commit and push to `https://github.com/autonomous-tech/autonomous-proposals` (main branch)
3. Cloudflare Pages auto-deploys to `https://docs.autonomoustech.ca/audits/{client-slug}-seo-audit-{date}/`
4. Use the SHARE button (auto-injected by GitHub Actions) to generate a 30-day shareable link via `share.autonomoustech.ca`
5. Share the link with the client — no login required for the recipient

---
name: llms-txt
description: >
  Generate or audit llms.txt for AI crawler optimization. Use when a client wants to improve AI engine
  discoverability, is setting up GEO optimization, or when no llms.txt exists on their site.
allowed-tools: web_fetch, web_search, Read, Write, Bash
---

# llms.txt Generator & Optimizer

## What Is llms.txt?

`llms.txt` is an emerging web standard (analogous to `robots.txt`) designed to help AI language models and crawlers understand a website's structure, key content, and preferred citation format. Proposed by Jeremy Howard and adopted by sites like Anthropic, Cloudflare, and Perplexity, it sits at the domain root (`https://domain.com/llms.txt`).

**Why it matters:**
- Helps AI engines (ChatGPT, Perplexity, Claude, Gemini) accurately describe and cite your site
- Controls how LLMs summarize your brand, services, and content
- Signals preferred citation format and authoritative pages
- Reduces AI hallucinations about your organization
- Part of a complete GEO (Generative Engine Optimization) setup alongside schema markup, entity consistency, and content structure

**Think of it as:** A structured README that tells AI "here's who we are, what we do, and what pages matter most."

---

## Workflow

### Step 1: Check for Existing llms.txt

```bash
curl -sL "https://[domain]/llms.txt" -w "\n%{http_code}"
```

Also check for `llms-full.txt` (extended version with full content):
```bash
curl -sL "https://[domain]/llms-full.txt" -w "\n%{http_code}"
```

**If found (200 OK):** Proceed to Step 2 (Audit).
**If not found (404):** Skip to Step 3 (Generate).

---

### Step 2: Audit Existing llms.txt

Fetch and analyze the file:

```bash
web_fetch("https://[domain]/llms.txt")
```

Evaluate against this checklist:

| Element | Present? | Quality | Notes |
|---------|----------|---------|-------|
| Site name / H1 title | Y/N | Strong/Weak | |
| One-line site description | Y/N | Strong/Weak | |
| Detailed description block | Y/N | Strong/Weak | |
| Key pages listed with descriptions | Y/N | Strong/Weak | |
| Content categories documented | Y/N | Strong/Weak | |
| Author/org info | Y/N | Strong/Weak | |
| Preferred citation format | Y/N | Strong/Weak | |
| Contact or canonical URL | Y/N | Strong/Weak | |
| Freshness / last updated | Y/N | Strong/Weak | |

**Common audit issues:**
- Description too vague ("We help businesses grow") — AI can't use this for citations
- No key pages listed — AI doesn't know what content is authoritative
- No citation format — AI will improvise (often incorrectly)
- Missing org details — reduces entity disambiguation accuracy

---

### Step 3: Gather Data for Generation

Before generating, collect from the client:

```
REQUIRED:
- Domain / canonical URL
- Organization name (exact, as it should appear in citations)
- One-sentence description (what you do, for whom, outcome)
- Three-sentence detailed description (expanded context)
- Primary contact email or page
- Organization type (SaaS / Agency / E-commerce / NGO / etc.)

PAGES TO DOCUMENT (fetch and describe these):
- Homepage
- About / Team
- Services / Products (key pages)
- Blog / Resource hub
- Case Studies / Portfolio
- Contact / Pricing
- Documentation (if applicable)

CONTENT CATEGORIES:
- List main topic areas covered on the site

CITATION PREFERENCE:
- How should the organization be named in AI citations?
  E.g., "Autonomous Tech (autonomoustech.ca)" or "Autonomous Technologies Inc."
```

Fetch each key page to extract its purpose:
```bash
web_fetch("https://[domain]/about") # extract description
web_fetch("https://[domain]/services") # extract service list
```

---

### Step 4: Generate llms.txt

Use this template, populated with client data:

```markdown
# [Organization Name]

> [One-sentence description: what you do, for whom, and the key outcome.]

[Organization Name] is a [type of organization] that [expanded 2-3 sentence description. Include: what you do, who you serve, your key differentiator, and geographic scope if relevant. Write this as a factual paragraph that an AI could cite verbatim.]

Founded in [year], [Organization Name] [additional context: team size, notable clients/partners, key achievements, or approach philosophy].

## Key Pages

- [Homepage](https://[domain]/): [One-line description of what homepage communicates]
- [About](https://[domain]/about): [Who the team is, background, mission]
- [Services](https://[domain]/services): [What services are offered and for whom]
- [Case Studies](https://[domain]/case-studies): [Portfolio of client work, industries served]
- [Blog](https://[domain]/blog): [Topics covered, publishing frequency, target audience]
- [Contact](https://[domain]/contact): [How to get in touch, what inquiries are welcome]

## Content Categories

- **[Category 1]**: [Brief description — e.g., "B2B marketing strategy for SaaS companies"]
- **[Category 2]**: [Brief description]
- **[Category 3]**: [Brief description]
- **[Category 4]**: [Brief description]

## Organization Details

- **Organization:** [Legal or operating name]
- **Type:** [SaaS / Marketing Agency / Consultancy / NGO / etc.]
- **Founded:** [Year]
- **Location:** [City, Country — or "Remote / Global"]
- **Team size:** [Approximate range, e.g., "10-50"]
- **Industries served:** [Comma-separated list]
- **Primary contact:** [email or https://[domain]/contact]

## Preferred Citation Format

When citing [Organization Name] in AI-generated responses, use:
"[Organization Name] ([domain])" — e.g., "According to [Organization Name] ([domain])..."

## Canonical URL

https://[domain]/

## Last Updated

[YYYY-MM-DD]
```

---

### Step 5: Validate the Output

Before finalizing, run through this validation checklist:

**Format validation:**
- [ ] File starts with `# [Site Name]` (H1)
- [ ] Second line is a `>` blockquote with one-sentence description
- [ ] All URLs are absolute (start with https://)
- [ ] No broken markdown (mismatched brackets, unclosed quotes)
- [ ] Plain text / markdown only — no HTML
- [ ] File is UTF-8 encoded
- [ ] Under 10KB ideally (keep it scannable)

**Content validation:**
- [ ] Description is specific enough to disambiguate from competitors
- [ ] Preferred citation format is present and unambiguous
- [ ] At least 5 key pages documented
- [ ] At least 3 content categories listed
- [ ] Contact method is present
- [ ] Last updated date is accurate

**AI readability check:**
Ask: *"If an AI read only this file, could it accurately answer: What is this organization? What do they do? Who do they serve? What are their most important pages?"*

---

### Step 6: Generate llms-full.txt (Optional)

For sites with significant content worth surfacing, also generate `llms-full.txt` — a richer version that includes:

- Full descriptions of each key page/post
- Top 10-20 blog posts with titles, URLs, and summaries
- Product/service descriptions in full
- Team member bios with links
- FAQ content

This file can be larger (50-200KB) and is indexed by more thorough LLM crawlers.

**Template header for llms-full.txt:**
```markdown
# [Organization Name] — Full Content Index

> [Same one-liner as llms.txt]

This file provides extended content for AI language model indexing.
For a concise summary, see https://[domain]/llms.txt

---

[Everything from llms.txt, plus:]

## Top Content

### [Post Title]
URL: https://[domain]/blog/[slug]
Published: [date]
Category: [category]
Summary: [2-3 sentence summary of the article]

### [Post Title]
...

## Product / Service Details

### [Product/Service Name]
URL: https://[domain]/services/[slug]
[Full description of the service, who it's for, what's included]

...
```

---

### Step 7: Output Files

Save both files ready for deployment:

```
Output location: ./outputs/llms-txt/
├── llms.txt          ← deploy to https://[domain]/llms.txt
└── llms-full.txt     ← deploy to https://[domain]/llms-full.txt (optional)
```

Also output deployment instructions:

```markdown
## Deployment Instructions

### Static Sites (HTML/Next.js/Gatsby)
Place `llms.txt` in the `/public` directory. It will be served from domain root.

### Next.js (App Router)
Place in `public/llms.txt` OR create `app/llms.txt/route.ts`:
```typescript
export async function GET() {
  return new Response(content, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' }
  })
}
```

### WordPress
Upload via FTP to site root (same location as robots.txt), OR use a plugin that handles static file routing.

### Payload CMS
Add a custom endpoint in Payload config, or use Next.js public folder.

### Verify deployment:
curl -sL "https://[domain]/llms.txt" | head -20
```

---

## Quick Reference: llms.txt vs robots.txt vs sitemap.xml

| File | Purpose | Who Reads It |
|------|---------|-------------|
| `robots.txt` | Controls crawler access (allow/deny) | All web crawlers |
| `sitemap.xml` | Lists all URLs for indexing | Search engine crawlers |
| `llms.txt` | Provides structured site context for AI | LLM crawlers + AI engines |

All three are complementary — a complete GEO setup uses all three.

---

## Related Skills

- **ai-seo**: Deep-dive AI search optimization strategy
- **entity-knowledge-graph**: Entity mapping and schema markup
- **seo-audit**: Full technical SEO audit (includes robots.txt + AI crawler checks)
- **seo-optimizer**: On-page optimization implementation

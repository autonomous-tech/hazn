---
name: entity-knowledge-graph
description: >
  Analyzes and optimizes content for entity clarity, knowledge graph alignment, and AI engine citability.
  Use this skill when the user wants to optimize content for AI citation, improve entity markup, build
  knowledge graph presence, audit entity consistency, create entity maps, or maximize visibility in
  generative AI responses (ChatGPT, Perplexity, Claude, Gemini). Also use when the user asks about
  "entity SEO", "knowledge graph optimization", "knowledge panel", "AI citation", "GEO optimization",
  or "how to get cited by AI". Pairs with `seo-blog-writer` (content creation) and `seo-optimizer`
  (technical implementation).
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
---

# Entity & Knowledge Graph Optimizer

## Overview

This skill bridges the gap between traditional keyword-focused SEO and the entity-focused world that AI engines operate in. Search engines and LLMs increasingly understand content through **entities** (people, organizations, products, concepts) and **relationships** between them — not just keywords.

This skill does three things:

1. **Entity Mapping** — Identifies and maps all entities in your content with their types, relationships, and authority links
2. **Knowledge Graph Alignment** — Ensures your content and schema markup align with how Google's Knowledge Graph and AI models understand your entities
3. **AI Citability Optimization** — Structures content so that AI models can confidently extract, attribute, and cite your information

---

## When to Use This Skill

- After writing content with the `seo-blog-writer` skill — run this to optimize entity signals
- When auditing an existing site for GEO readiness (complements `seo-optimizer`)
- When building a new site and defining the entity strategy upfront
- When a client asks "how do I get a Knowledge Panel" or "how do I get cited by ChatGPT"
- When content is ranking well for SEO but not appearing in AI-generated answers

---

## Workflow

### Step 1: Entity Discovery

Analyze the content (article, page, or entire site) and extract all entities:

```
ENTITY MAP
==========
Content: [URL or file path]

Primary Entities (the main subjects):
1. [Entity Name]
   Type: Organization | Person | Product | Technology | Concept | Event | Place
   Role: subject | author | publisher
   Canonical URL: [official website]
   Wikipedia: [URL if exists]
   Wikidata ID: [QID if exists]
   Description: [one-line description for disambiguation]

2. [Entity Name]
   ...

Secondary Entities (mentioned, compared, or referenced):
3. [Entity Name]
   Type: ...
   Role: competitor | tool | framework | authority_source | example
   Canonical URL: ...
   Wikipedia: ...
   Relationship to primary: [e.g., "competitor to Entity 1", "used by Entity 2"]

4. [Entity Name]
   ...

Concept Entities (abstract ideas, methodologies, industry terms):
5. [Concept Name]
   Type: Concept | Methodology | Industry Term
   Definition: [clean, quotable one-sentence definition]
   Wikipedia: [URL if exists]
   Related to: [which primary/secondary entities use or embody this concept]
```

### Step 2: Entity Consistency Audit

Scan content for entity naming issues:

```
ENTITY CONSISTENCY REPORT
=========================
Entity: Payload CMS

✅ First mention: "Payload CMS, an open-source headless content management system" (full context)
❌ Line 47: "the CMS" — ambiguous, could be any CMS → change to "Payload"
❌ Line 82: "Payload" → acceptable (short form after established)
❌ Line 103: "their platform" — ambiguous → change to "Payload CMS"
✅ Line 156: "Payload CMS" — clear

Entity: Google

✅ First mention: "Google" (well-known, no disambiguation needed)
❌ Line 34: "the search giant" — journalistic style, but AI models prefer explicit names
❌ Line 67: "Alphabet" — different entity (parent company), only use when discussing corporate structure
✅ Line 89: "Google Search" — specific product reference, good

Naming Rules Applied:
1. First mention always includes full name + brief descriptor if not universally known
2. Subsequent mentions use consistent short form (never "it", "the platform", "they")
3. Don't use synonyms, nicknames, or metonymy for entities you want AI to track
4. Parent company ≠ subsidiary (Google ≠ Alphabet, Meta ≠ Facebook)
5. When referencing a specific product, use the product name (not the company name)
```

### Step 3: Entity Schema Generation

For each entity, generate the appropriate schema markup:

#### For the Organization You're Writing For

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://example.com/#organization",
  "name": "Brand Name",
  "alternateName": "Brand",
  "url": "https://example.com",
  "logo": {
    "@type": "ImageObject",
    "url": "https://example.com/logo.png"
  },
  "description": "One-sentence description of what the organization does",
  "foundingDate": "2020",
  "founder": {
    "@type": "Person",
    "name": "Founder Name",
    "sameAs": "https://linkedin.com/in/founder"
  },
  "sameAs": [
    "https://twitter.com/brand",
    "https://linkedin.com/company/brand",
    "https://github.com/brand",
    "https://www.crunchbase.com/organization/brand",
    "https://en.wikipedia.org/wiki/Brand"
  ],
  "knowsAbout": [
    "Digital Transformation",
    "Marketing Technology",
    "AI Automation"
  ],
  "areaServed": "Global",
  "numberOfEmployees": {
    "@type": "QuantitativeValue",
    "value": "10-50"
  }
}
```

#### For People (Authors, Team Members)

```json
{
  "@context": "https://schema.org",
  "@type": "Person",
  "@id": "https://example.com/team/person/#person",
  "name": "Person Name",
  "jobTitle": "Title",
  "worksFor": {
    "@type": "Organization",
    "@id": "https://example.com/#organization"
  },
  "description": "Brief expertise description",
  "sameAs": [
    "https://linkedin.com/in/person",
    "https://twitter.com/person",
    "https://github.com/person"
  ],
  "knowsAbout": [
    "Next.js",
    "SEO",
    "Content Strategy"
  ],
  "alumniOf": {
    "@type": "EducationalOrganization",
    "name": "University Name"
  }
}
```

#### For Products/Software

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "@id": "https://product.io/#product",
  "name": "Product Name",
  "description": "One-sentence product description",
  "url": "https://product.io",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "author": {
    "@type": "Organization",
    "@id": "https://example.com/#organization"
  },
  "sameAs": [
    "https://github.com/org/product",
    "https://www.producthunt.com/products/product-name"
  ]
}
```

#### For Entities Mentioned in Content (about/mentions)

```json
{
  "@type": "Article",
  "about": [
    {
      "@type": "Thing",
      "name": "Answer Engine Optimization",
      "description": "The practice of optimizing content for AI-powered answer engines",
      "sameAs": "https://en.wikipedia.org/wiki/Answer_engine"
    },
    {
      "@type": "SoftwareApplication",
      "name": "Payload CMS",
      "sameAs": "https://payloadcms.com"
    }
  ],
  "mentions": [
    {
      "@type": "Organization",
      "name": "Google",
      "sameAs": "https://en.wikipedia.org/wiki/Google"
    },
    {
      "@type": "Organization",
      "name": "OpenAI",
      "sameAs": "https://en.wikipedia.org/wiki/OpenAI"
    }
  ]
}
```

### Step 4: Knowledge Graph Alignment

Check how your entities align with existing knowledge graphs:

#### Google Knowledge Graph Presence Check

For each primary entity, assess:

```
KNOWLEDGE GRAPH ALIGNMENT
==========================

Entity: Autonomous Tech
Knowledge Panel exists? ❌ No
Wikipedia article exists? ❌ No
Wikidata entry exists? ❌ No
Crunchbase profile? ❓ Check
LinkedIn company page? ✅ Yes

Recommendations:
1. Create a Wikidata entry with basic structured data (name, type, URL, founding date)
2. Ensure Google Business Profile is complete (if applicable)
3. Build consistent NAP (Name, Address, Phone) across directories
4. Add Organization schema with sameAs pointing to all profiles
5. Pursue notable press coverage (Wikipedia notability requirement)

Entity: Payload CMS
Knowledge Panel exists? ✅ Yes (as software)
Wikipedia article exists? ✅ Yes
Wikidata entry exists? ✅ Yes (Q...)

Recommendations:
1. Use sameAs: "https://en.wikipedia.org/wiki/Payload_(software)" in schema
2. Reference by full name "Payload CMS" consistently
3. Benefit from existing KG presence — your content about Payload gets entity boost
```

#### Building Knowledge Graph Presence (New Entities)

For entities without KG presence, recommend this progression:

1. **Foundation** (Week 1-2):
   - Wikidata entry with structured data
   - Complete Google Business Profile (if local)
   - LinkedIn company page with full details
   - Crunchbase profile
   - Organization schema on website with comprehensive sameAs

2. **Reinforcement** (Month 1-2):
   - Consistent entity mentions across owned properties (blog, social, docs)
   - Guest posts and PR that use consistent entity naming
   - Schema markup on every page that references the entity

3. **Authority** (Month 2-6):
   - Press coverage meeting Wikipedia notability guidelines
   - Wikipedia article (only if genuinely notable — don't game this)
   - Cited as a source by other authoritative content
   - Appearing in AI-generated answers about your topic area

### Step 5: Citability Optimization

Audit content for AI citation readiness:

```
CITABILITY REPORT
=================
Content: /blog/guide-to-aeo
Overall Citability Score: 6.5/10

DEFINITIONS (3 found, 2 strong)
✅ "Answer Engine Optimization (AEO) is the practice of structuring web content so it can be directly extracted and displayed by AI-powered search engines."
   — Clean, quotable, specific. HIGH citability.

✅ "A featured snippet is a highlighted search result that appears above the standard organic results, providing a direct answer to the searcher's query."
   — Good definition. MEDIUM citability.

⚠️ "GEO is basically about making sure AI tools can find and use your stuff."
   — Too informal, imprecise. LOW citability.
   → Rewrite: "Generative Engine Optimization (GEO) is the practice of optimizing content for citation and reference by generative AI models such as ChatGPT, Perplexity, and Google Gemini."

STATISTICS (5 found, 2 properly attributed)
✅ "According to a 2025 Gartner report, 40% of search queries now trigger an AI-generated overview."
   — Source + date. HIGH citability.

❌ "Studies show that most users prefer AI answers."
   — No source, no specificity.
   → Fix: "A 2025 BrightEdge study found that 62% of users engage with AI-generated search summaries before clicking through to websites."

❌ "Content with FAQ schema gets 3x more impressions."
   — Unattributed.
   → Fix: Cite the actual source or remove the claim.

FRAMEWORKS (0 found)
❌ No named frameworks or methodologies.
   → Opportunity: Name your approach. E.g., "The EXTRACT Framework for AEO: Evidence-based, eXplicit answers, Trustworthy sources, Rich schema, Answer-first structure, Consistent entities, Timely updates"

UNIQUE VALUE (1 found)
✅ Original competitive analysis of 50 sites — this is citable original data.
   → Strengthen: Add methodology details ("We analyzed 50 B2B SaaS websites across 10 industries using a 15-point AEO readiness scorecard")

EXPERT SIGNALS (partial)
⚠️ Author bio exists but lacks credentials.
   → Fix: Add "10 years in technical SEO, previously at [notable company]"

❌ No first-person expert assertions.
   → Add: "In our experience working with 200+ B2B websites..." type claims
```

### Step 6: Relationship Mapping

Map how entities relate to each other within your content ecosystem. This helps AI models understand your content's place in the knowledge graph:

```
ENTITY RELATIONSHIP MAP
=======================

[Your Organization]
├── offers → [Your Product/Service]
├── employs → [Team Member 1] (author)
├── employs → [Team Member 2] (CTO)
├── competes with → [Competitor 1]
├── competes with → [Competitor 2]
├── uses → [Technology 1] (Next.js)
├── uses → [Technology 2] (Payload CMS)
└── specializes in → [Concept 1] (Digital Transformation)

[Your Product]
├── serves → [Target Audience] (Equipment Dealers)
├── solves → [Problem] (High-ticket sales automation)
├── integrates with → [Tool 1]
├── competes with → [Alternative 1]
└── competes with → [Alternative 2]

Content should explicitly state these relationships rather than assuming the reader (or AI model) will infer them.
```

### Step 7: Output

Generate one of the following outputs based on the task:

#### For Single Page/Article Optimization
Save entity map and recommendations to:
```
./outputs/entity-audit-{slug}.md
```

#### For Site-Wide Entity Strategy
Save comprehensive entity strategy to:
```
./outputs/entity-strategy.md
```

Including:
- Complete entity map for the site
- Schema markup recommendations for each page type
- Knowledge graph building roadmap
- Content recommendations for entity authority
- Citability improvement plan

#### For Schema Markup Generation
Save ready-to-implement JSON-LD files:
```
./outputs/schema/
├── organization.json
├── person-{name}.json
├── product-{name}.json
└── page-schema-{slug}.json
```

---

## Integration with Other Skills

### With seo-blog-writer
1. Blog writer creates content with entity annotations in frontmatter
2. This skill reviews and enriches the entity data
3. Generates complete schema markup for the post
4. Provides entity consistency fixes

### With seo-optimizer
1. SEO optimizer runs technical audit
2. This skill adds the GEO/entity layer to the audit
3. Generates missing schema markup
4. Provides the entity-specific recommendations

### Recommended Workflow
```
keyword-research → seo-blog-writer → entity-knowledge-graph → seo-optimizer (final technical check)
```

---

## Quick Reference: What Makes Content AI-Citable

| Signal | Why AI Models Care | How to Implement |
|--------|-------------------|------------------|
| Clean definitions | Easy to extract and quote | "[Term] is [definition]." as standalone sentence |
| Attributed stats | Verifiable, trustworthy | "According to [Source], [Year], [specific claim]" |
| Named frameworks | Unique, referenceable | Give methodologies explicit names |
| Author credentials | E-E-A-T / trustworthiness | Author schema with jobTitle, sameAs, expertise |
| Fresh dates | Content relevance | dateModified in schema + meta |
| Entity sameAs | Disambiguation | Link to Wikipedia/Wikidata/official URLs |
| Original data | Unique value | State methodology, sample size, findings |
| Consistent naming | No ambiguity | Never use "it", "the platform", "they" for key entities |
| Explicit relationships | Context for AI | "X, which competes with Y in the Z market" |
| Primary sources | Citation chain | Link to the study, not the blog about the study |

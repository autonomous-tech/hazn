---
name: seo-blog-writer
description: >
  Writes SEO, AEO, and GEO-optimized blog posts (1,500–3,000 words) using keyword research data as input.
  Optimizes for traditional search rankings, AI answer engines (ChatGPT, Perplexity, Google AI Overviews),
  and generative engine citation. Outputs markdown with frontmatter (title, meta description, slug, keywords,
  schema markup, entity map, answer blocks) ready for import into Payload CMS. Use this skill whenever the
  user asks to write a blog post, create blog content, draft an article, write SEO content, "write a post
  about [topic]", "create content for [keyword]", or any request involving long-form content creation for a
  blog. Also trigger when the user references keyword research output and wants content produced from it, or
  asks to "turn these keywords into content", "write content from this research", "create a content calendar",
  or anything related to AEO/GEO content optimization. Pairs with the `keyword-research` skill (upstream data),
  `entity-knowledge-graph` skill (entity optimization), and the `payload-nextjs-stack` skill (downstream CMS
  integration).
---

# SEO + AEO + GEO Blog Writer

## Overview

This skill writes production-quality blog posts (1,500–3,000 words) optimized for three discovery channels:

1. **SEO** — Traditional search engine rankings (Google organic, Bing)
2. **AEO** — Answer Engine Optimization (Google AI Overviews, featured snippets, voice assistants, People Also Ask)
3. **GEO** — Generative Engine Optimization (ChatGPT, Perplexity, Claude, Gemini citing your content)

The tone adapts to the niche. The structure is designed so that both search crawlers and LLM retrieval systems can cleanly extract, attribute, and cite your content.

---

## Input Sources

### Auto-Detection
Check for keyword research JSON at these paths (in order):
1. `./outputs/keyword-research.json`
2. `./uploads/keyword-research.json`
3. Any `.json` file in uploads with a `meta.seed_keyword` field

### Manual Override
The user may provide:
- A specific keyword or topic (no JSON needed — research on the fly or ask for the research skill)
- A pasted JSON snippet or keyword list
- A specific `content_opportunities` entry from keyword research output
- A URL to a competitor article for a "write something better" brief

### What to Extract from Keyword Research JSON
When keyword research JSON is available, extract:
- **Primary keyword**: The `target_keyword` from a `content_opportunities` entry, or the highest-opportunity keyword matching the user's topic
- **Supporting keywords**: From `supporting_keywords` array, or top 5-8 related keywords by opportunity score
- **Questions**: From the `questions` array — these become H2s, FAQ sections, or naturally woven into the content
- **Search intent**: Determines the article's angle and CTA strategy
- **Content angle**: From the keyword's `content_angle` field if available
- **Competitor insights**: From `competitive_insights` — what gaps to exploit
- **Entities**: Any named entities (people, companies, products, concepts) relevant to the topic — these feed the entity strategy

---

## Workflow

### Step 1: Article Planning

Before writing a single word, create an internal brief:

```
ARTICLE BRIEF
=============
Primary keyword: [keyword]
Search intent: [informational/commercial/navigational/transactional]
Target word count: [1,500–3,000]
Audience: [who is reading this]
Sophistication: [beginner/intermediate/expert]
Tone: [see Tone Adaptation below]
Content angle: [what makes this piece different from what's ranking]
Supporting keywords: [list 5-8 to naturally weave in]
Questions to answer: [from PAA data]
CTA goal: [what should the reader do after reading]

AEO TARGETS
============
AI Overview trigger queries: [questions this article should appear in AI Overviews for]
Featured snippet format: [paragraph/list/table — match the current SERP format]
Voice search phrases: [natural language versions of the keyword]
Direct answer candidates: [2-3 specific questions where we can be THE definitive answer]

GEO TARGETS
============
Core entities: [people, companies, products, concepts to establish authority around]
Citable claims: [specific stats, frameworks, definitions we want AI to quote]
Source authority signals: [what makes this content trustworthy enough for AI to cite]
Unique value: [original data, framework, perspective that doesn't exist elsewhere]
```

### Step 2: Tone Adaptation

Do NOT use a one-size-fits-all voice. Adapt based on niche signals:

| Niche Signal | Tone | Style Notes |
|-------------|------|-------------|
| B2B / SaaS / Enterprise | Professional, authoritative | Data-driven, cite stats, avoid fluff. Use "organizations" not "folks". |
| SMB / Small business | Practical, direct | Actionable advice, real examples, "you" language. Skip jargon. |
| Developer / Technical | Precise, peer-to-peer | Code examples where relevant, assume competence, skip marketing speak. |
| Consumer / Lifestyle | Conversational, warm | Stories, relatable examples, "you" language, shorter paragraphs. |
| Healthcare / Finance | Trustworthy, measured | Cite sources, include disclaimers, avoid absolute claims. |
| Creative / Design | Inspiring, visual | Reference examples, use vivid language, shorter punchy sentences. |
| E-commerce / DTC | Energetic, benefit-focused | Product-oriented, urgency where natural, social proof. |

If uncertain, default to **professional but approachable** — authoritative without being stiff, clear without being dumbed down.

### Step 3: Outline Structure (SEO + AEO + GEO Hybrid)

Build the article structure optimized for all three channels:

```markdown
# [H1 — Contains primary keyword, compelling, under 60 chars]

> **TL;DR:** [2-3 sentence executive summary answering the core query directly.
> This is the #1 extraction target for AI engines. Write it as if an LLM
> will read ONLY this block and cite it. Include the primary keyword,
> a specific claim, and actionable takeaway.]

[Opening paragraph — hook + primary keyword in first 100 words. Establish credibility signal: who is writing this and why should anyone care.]

## [H2 — Section 1: Core topic, phrased as a question when natural]

> **Key takeaway:** [1-2 sentence direct answer — AEO extraction target]

[2-4 paragraphs, 200-400 words. Expand on the direct answer with evidence, examples, and context. Include at least one specific, citable data point.]

## [H2 — Section 2: Go deeper or cover next subtopic]

> **Key takeaway:** [1-2 sentence direct answer]

[2-4 paragraphs, 200-400 words]

### [H3 — Subsection if needed for genuine detail]

## [H2 — Section 3: Practical/actionable section]

[How-to, examples, frameworks, templates. For HowTo content, use explicit step numbering that maps to HowTo schema.]

## [H2 — "What Is [Entity/Concept]?" — Definition section]

[Start with a clean, quotable definition in the first sentence. This is a high-value GEO target — AI models love citing clear definitions. Format: "[Term] is [definition]." Then expand with context.]

## [H2 — Section addressing a PAA question directly]

[Direct answer in first sentence, then expand. Mirror the exact question phrasing from PAA data when natural.]

## [H2 — Additional sections as needed for depth]

## Frequently Asked Questions

[3-5 questions from PAA data. Each answer starts with a direct 1-2 sentence response, then expands briefly. These map to FAQPage schema AND are prime AEO/GEO extraction targets.]

### [Question 1 — exact natural language phrasing]

[Direct answer first sentence. Expand in 2-3 more sentences.]

### [Question 2]

[Same pattern.]

## [H2 — Conclusion: What to Do Next]

> **Bottom line:** [Single sentence distillation of the entire article's value.
> Another GEO citation target.]

[Summarize key takeaway, clear CTA. Restate primary keyword naturally.]
```

#### Structure Rules
1. **H1**: One per article. Contains primary keyword. Under 60 characters.
2. **H2s**: 5-8 per article. At least 2 should contain supporting keywords naturally. At least 2 should be phrased as questions (AEO optimization).
3. **H3s**: Use sparingly for genuine subsections. In FAQ section, use H3s for individual questions.
4. **TL;DR block**: REQUIRED at the top. This is the single most important AEO/GEO element. Write it as a standalone answer.
5. **Key takeaway blocks**: Include under each major H2. These are secondary extraction targets. Use blockquote formatting.
6. **Paragraphs**: 2-4 sentences max. No walls of text.
7. **Definition sentences**: When introducing a concept, lead with "[Term] is [definition]." — clean, quotable, citable.
8. **Lists**: Use when genuinely listing items. Don't use as a crutch for lazy writing. For AEO, numbered lists work better than bullets for "how-to" and "steps" queries.
9. **Bold**: Emphasize key terms or definitions on first use. Don't overdo it.
10. **Internal links**: Suggest 2-4 internal link placements using `[anchor text]({{internal_link:related-topic}})` placeholder syntax.
11. **External links**: Suggest 2-3 authoritative external sources for claims or statistics. Prefer primary sources (.gov, .edu, peer-reviewed, official company blogs).

### Step 4: AEO-Specific Optimization

Apply these patterns to maximize answer engine visibility:

#### Direct Answer Pattern
For every question-format H2, follow this structure:
```
## How long does [process] take?

[Process] typically takes [specific timeframe] for [common scenario]. [Qualifier for different situations]. [Evidence or source for the claim].

For more complex cases, the timeline breaks down like this...
```

The first sentence IS the featured snippet / AI Overview answer. Write it to stand alone.

#### Featured Snippet Targeting
Match the current SERP format for your target query:
- **Paragraph snippet**: Write a 40-60 word direct answer paragraph immediately after the H2
- **List snippet**: Use a numbered or bulleted list of 4-8 items immediately after the H2
- **Table snippet**: Use a markdown table comparing options, features, or data points
- **Definition snippet**: Start with "[Term] is..." or "[Term] refers to..."

#### People Also Ask (PAA) Optimization
- Use exact PAA question phrasing as H2s or H3s when natural
- Answer in the first 1-2 sentences below the heading
- Keep the direct answer under 50 words (Google truncates beyond this)
- Then expand with the full explanation

#### Voice Search Optimization
- Include at least 2-3 natural language, conversational question phrasings
- Answers to voice queries should be speakable — clear, concise, no jargon
- Target position zero content: if someone asks Alexa/Siri this question, your sentence is what gets read aloud

### Step 5: GEO-Specific Optimization

Apply these patterns to maximize AI model citation:

#### Citability Architecture
AI models cite content that is **specific, attributed, and structurally clean**. Optimize for this:

1. **Quotable definitions**: Every key concept gets a clean, standalone definition sentence.
   - ✅ "Answer Engine Optimization (AEO) is the practice of structuring content so it can be directly extracted and cited by AI-powered search experiences."
   - ❌ "AEO is kind of a new approach to how we think about content."

2. **Attributed statistics**: Every data claim includes source AND date.
   - ✅ "According to a 2025 Gartner study, 40% of search queries now trigger an AI-generated response."
   - ❌ "Studies show that AI is changing search."

3. **Named frameworks**: If you introduce a methodology or framework, name it explicitly.
   - ✅ "The EASE Framework (Extract, Answer, Structure, Enrich) provides a systematic approach to AEO."
   - ❌ "There are several steps you can follow."

4. **Authoritative tone signals**: Write with the confidence of a subject matter expert.
   - First person plural for organizational authority: "We analyzed 200 sites and found..."
   - Reference specific experience: "In our work with B2B SaaS companies..."
   - Avoid hedging on things you know: "This works because..." not "This might potentially help because..."

#### Entity Optimization
- **Explicitly name entities** on first reference with context: "Payload CMS, an open-source headless content management system" — not just "Payload"
- **Link entities** to authoritative sources (Wikipedia, official sites) on first mention via external link suggestions
- **Use consistent entity naming** throughout. Don't alternate between "Google," "the search giant," "Alphabet's search division"
- **Map entity relationships** in the content naturally: "Payload CMS, which competes with Sanity and Strapi in the headless CMS market..."

#### Source Authority Signals
Embed these trust signals that AI models weight when deciding what to cite:
- **Author expertise**: Include an author bio line or reference in frontmatter
- **Publication date**: Always include, always current
- **Last updated date**: For evergreen content, include `lastModified` in frontmatter
- **Methodology transparency**: When making claims from analysis, briefly state the methodology
- **Primary sources preferred**: Cite the original study, not the blog post that cited the study

#### Content Uniqueness for GEO
AI models deprioritize content that's just restating what's already everywhere. Your content needs:
- **Original angles**: Use the `content_angle` from keyword research. What are you saying that nobody else is?
- **Original data**: Even a small original survey, analysis, or case study makes content 10x more citable
- **Novel frameworks**: Named, structured approaches that become reference material
- **Contrarian-where-earned positions**: "The common advice is X, but our data shows Y" — backed with evidence

### Step 6: On-Page SEO Optimization

Apply these optimizations during writing (not as an afterthought):

#### Keyword Placement
- **Primary keyword** in: H1, TL;DR, first 100 words, one H2, meta description, slug, conclusion
- **Supporting keywords** in: other H2s, naturally throughout body, image alt text suggestions
- **Question keywords** in: FAQ section and as H2s phrased as questions
- **Keyword density**: 1-2% for primary keyword (natural, never forced)

#### Readability
- Flesch-Kincaid Grade Level: Target 8-10 (accessible but not condescending)
- Sentence variety: Mix short punchy sentences with longer explanatory ones
- Transition words: Use naturally (however, additionally, for example, in practice)
- Active voice: Prefer active ("We analyzed 500 sites") over passive ("500 sites were analyzed")

#### Engagement Patterns
- **Hook**: First 2 sentences must earn the reader's attention. No "In today's fast-paced world..." garbage.
- **Pattern interrupts**: Every 300-400 words, break the rhythm — a question, a stat, a short story, a bold statement.
- **Bucket brigades**: Use transitional phrases that pull readers forward: "Here's the thing:", "But it gets better:", "The real question is:"
- **Specificity**: Replace vague claims with specific ones. Not "many companies" but "67% of B2B companies" (cite the source).

### Step 7: Write the Article

Write the full article following the outline. Key principles:

1. **No filler**: Every sentence should inform, persuade, or engage. Cut "fluff" ruthlessly.
2. **Show, don't tell**: Use examples, case studies, data, screenshots, comparisons — not just assertions.
3. **Original framing**: Don't rehash what's already ranking. Find a unique angle from the content_angle field or competitive gaps.
4. **Practical value**: Reader should leave with something actionable — a framework, checklist, template, or clear next step.
5. **Natural keyword integration**: If you can remove the keyword and the sentence still reads well, it's integrated properly.
6. **Answer-first writing**: For every section, lead with the answer, then explain. Inverted pyramid at the section level.
7. **Citable precision**: Every major claim should be specific enough that an AI model could confidently cite it with attribution.

### Step 8: Generate Frontmatter & Structured Data

Produce complete frontmatter that maps to the Payload CMS blog collection schema AND provides rich signals for AI engines:

```yaml
---
title: "Primary Keyword: Compelling Benefit or Hook"
slug: "primary-keyword-focused-slug"
meta_title: "Primary Keyword — Benefit Statement | Brand Name"  # Under 60 chars
meta_description: "Action-oriented description with primary keyword. Includes benefit and implicit CTA. Under 155 chars."
primary_keyword: "exact primary keyword"
supporting_keywords:
  - "keyword 1"
  - "keyword 2"
  - "keyword 3"
search_intent: "informational"
target_word_count: 2000
estimated_reading_time: "8 min"
date: "YYYY-MM-DD"
lastModified: "YYYY-MM-DD"
author: ""  # To be filled by editor
author_credentials: ""  # e.g., "10 years in B2B SaaS marketing" — GEO authority signal
category: ""  # To be filled based on site taxonomy
featured_image_alt: "Descriptive alt text containing primary keyword naturally"

# SEO
internal_links_suggested:
  - anchor: "anchor text"
    target_topic: "related topic or slug"
external_sources:
  - url: "https://example.com/study"
    context: "Cited for [specific claim]"
    type: "primary_source"  # primary_source | industry_report | official_documentation

# AEO
tldr: "2-3 sentence executive summary — the primary AI extraction target."
featured_snippet_format: "paragraph"  # paragraph | list | table | definition
paa_questions:
  - "Exact PAA question 1?"
  - "Exact PAA question 2?"
  - "Exact PAA question 3?"
voice_search_phrases:
  - "natural language voice query version"

# GEO
entities:
  - name: "Entity Name"
    type: "Organization"  # Person | Organization | Product | Concept | Technology
    relationship: "subject"  # subject | competitor | tool | framework | authority
    sameAs: "https://en.wikipedia.org/wiki/Entity"  # or official URL
citable_claims:
  - claim: "Specific statistic or definition"
    source: "Source name, year"
    context: "Where this appears in the article"
original_value: "Brief description of what's unique — original data, novel framework, contrarian insight"
content_freshness: "evergreen"  # evergreen | timely | seasonal

# Schema
schema_type: "Article"
schema_markup:
  "@context": "https://schema.org"
  "@type": "Article"
  headline: "Same as title"
  description: "Same as meta_description"
  datePublished: "YYYY-MM-DD"
  dateModified: "YYYY-MM-DD"
  author:
    "@type": "Person"
    name: ""
    url: ""
    sameAs: []  # LinkedIn, Twitter, etc.
  publisher:
    "@type": "Organization"
    name: ""
    url: ""
    logo:
      "@type": "ImageObject"
      url: ""
  mainEntityOfPage:
    "@type": "WebPage"
    "@id": ""
faq_schema:  # Only if FAQ section exists
  - question: "Question from the article?"
    answer: "Concise answer from the article."
how_to_schema: null  # Populate if article contains step-by-step instructions
  # "@type": "HowTo"
  # name: "How to..."
  # step:
  #   - "@type": "HowToStep"
  #     name: "Step 1 name"
  #     text: "Step 1 description"
speakable_selectors:  # CSS selectors for content optimized for voice/TTS
  - ".tldr"
  - ".key-takeaway"
  - ".faq-answer"
---
```

### Step 9: Output

Save the complete markdown file with frontmatter to:
```
./outputs/blog-{slug}.md
```

If writing multiple posts (batch mode), save to:
```
./outputs/blog-posts/
├── blog-{slug-1}.md
├── blog-{slug-2}.md
└── blog-{slug-3}.md
```

---

## Payload CMS Integration Notes

The frontmatter maps to Payload's blog collection as follows:

| Frontmatter Field | Payload Field | Notes |
|-------------------|---------------|-------|
| `title` | `title` (text) | Direct map |
| `slug` | `slug` (text, unique) | Direct map |
| `meta_title` | `meta.title` (text) | SEO override |
| `meta_description` | `meta.description` (textarea, max 160) | SEO description |
| `tldr` | `tldr` (richText or text block) | Display at top of post + used in speakable schema |
| `featured_image_alt` | Media `alt` field | For the hero/featured image |
| `date` | `publishedDate` | Publication date |
| `lastModified` | `updatedAt` or custom `lastModified` | GEO freshness signal |
| `author` | `author` (relationship) | Needs human input |
| `author_credentials` | `author.credentials` (text) | Display in byline for E-E-A-T |
| `category` | `category` (relationship or select) | Based on site taxonomy |
| `entities` | `entities` (array block) | For knowledge graph integration |
| `schema_markup` | Injected via `generateMetadata` or JSON-LD script | In the blog post template |
| `faq_schema` | Rendered as FAQ block + JSON-LD | Use FAQBlock from Payload blocks |
| `how_to_schema` | Rendered as HowTo block + JSON-LD | Use HowToBlock from Payload blocks |
| `speakable_selectors` | Added to Speakable schema in page head | Tells Google which content is voice-ready |

### New Payload Blocks Needed for AEO/GEO
- **TLDRBlock**: Renders the executive summary with `.tldr` class for speakable targeting
- **KeyTakeawayBlock**: Blockquote-style callout with `.key-takeaway` class
- **DefinitionBlock**: Clean "[Term] is [definition]" with Definition schema markup
- **EntityMentionBlock**: Inline entity reference with `sameAs` link for knowledge graph

---

## Batch Mode: Content Calendar

When the user provides full keyword research JSON and asks to "create content" or "build a content calendar", switch to batch planning mode:

1. Review all `content_opportunities` from the keyword research
2. If `topical_authority` data exists, use the `content_creation_order` as the writing sequence
3. Present a content calendar with AEO/GEO annotations:

```
CONTENT CALENDAR
================
Pri | Title                              | Primary Keyword      | Intent        | Words | AEO Target           | GEO Value
----|------------------------------------|--------------------- |---------------|-------|----------------------|-----------
1   | [Pillar] Complete Guide to X       | main keyword         | informational | 3,000 | AI Overview          | Definitions, framework
2   | How to Do Y: Step-by-Step          | how to Y             | informational | 2,000 | Featured snippet     | HowTo schema, steps
3   | X vs Z: Which Is Better?           | X vs Z               | commercial    | 2,000 | Comparison table     | Entity relationships
4   | 7 Best Tools for X in 2026         | best tools for X     | commercial    | 2,500 | List snippet         | Product entities
5   | What Is X? [Definition Post]       | what is X            | informational | 1,500 | Definition snippet   | Citable definition
6   | [FAQ] Common Questions About X     | X questions          | informational | 1,500 | PAA domination       | FAQ schema, voice
```

4. Ask the user which posts to write (or confirm the full calendar)
5. Write posts one at a time, saving each to the outputs directory

---

## Quality Checklist

Before finalizing any blog post, verify:

### SEO Checks
- [ ] Word count is 1,500–3,000 words
- [ ] Primary keyword appears in: H1, TL;DR, first 100 words, one H2, meta description, slug, conclusion
- [ ] 5-8 supporting keywords are naturally woven throughout
- [ ] All H2s are meaningful section headers (not generic "Introduction" or "Conclusion")
- [ ] No paragraph exceeds 4 sentences
- [ ] At least one data point, example, or specific claim per major section
- [ ] Hook in the first 2 sentences is compelling (no clichés)
- [ ] CTA is clear and relevant to search intent
- [ ] Frontmatter is complete (all fields populated except author/category)
- [ ] Internal link suggestions are included
- [ ] External source suggestions are included for claims/stats
- [ ] Tone matches the niche (see Tone Adaptation table)

### AEO Checks
- [ ] TL;DR block at the top (2-3 sentences, standalone answer)
- [ ] Key takeaway block under each major H2
- [ ] At least 2 H2s phrased as questions (matching PAA data)
- [ ] Direct answer in first sentence after each question H2
- [ ] FAQ section with 3-5 questions and concise answers
- [ ] Featured snippet format matches SERP format for target query
- [ ] FAQPage schema is present and accurate
- [ ] HowTo schema present if article contains steps
- [ ] Voice search phrases included in frontmatter
- [ ] Speakable selectors identified

### GEO Checks
- [ ] At least 3 citable claims with specific attribution (source + date)
- [ ] Key concepts have clean, standalone definition sentences
- [ ] All entities named explicitly with context on first mention
- [ ] Entity map in frontmatter with types, relationships, and sameAs URLs
- [ ] Author credentials included for E-E-A-T signals
- [ ] lastModified date set for content freshness
- [ ] Original value clearly present (unique data, framework, or perspective)
- [ ] Content passes the "would an AI confidently cite this?" test
- [ ] No vague claims — everything is specific and attributable
- [ ] Publisher and author schema include sameAs links

### Content Quality
- [ ] Content is original — not a rehash of what's already ranking
- [ ] No SEO spam — reads naturally to a human first
- [ ] No filler or padding to hit word count
- [ ] Active voice predominates
- [ ] Varied paragraph and sentence structure

---

## Anti-Patterns (DO NOT)

- ❌ "In today's fast-paced digital landscape..." — Generic openings
- ❌ "Without further ado..." — Filler transitions
- ❌ Keyword stuffing — If it reads awkwardly, remove the keyword
- ❌ Thin sections — Every H2 section should be 200+ words with substance
- ❌ Clickbait titles that don't deliver — Title must match content
- ❌ "As an AI language model..." — Never break character
- ❌ Lists as a crutch — Use prose when explaining concepts
- ❌ Passive voice domination — Default to active voice
- ❌ Vague claims without evidence — "Many experts agree" means nothing
- ❌ Identical paragraph structure — Vary rhythm: short-long-medium-short
- ❌ Writing to hit word count — Don't pad if topic is well covered
- ❌ Burying the answer — Lead with the answer, then explain (AEO rule)
- ❌ Unnamed frameworks — If you create a methodology, name it (GEO rule)
- ❌ Unattributed statistics — Every number needs a source and date (GEO rule)
- ❌ Entity ambiguity — "the platform" instead of "Payload CMS" (GEO rule)
- ❌ Stale dates — Never publish without `date` and `lastModified` (GEO rule)
- ❌ Missing author signals — Anonymous content gets deprioritized by AI models

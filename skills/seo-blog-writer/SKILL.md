---
name: seo-blog-writer
description: >
  Writes SEO, AEO, and GEO-optimized blog posts (1,500–3,000 words) using keyword research data as input.
  Optimizes for traditional search rankings, AI answer engines (ChatGPT, Perplexity, Google AI Overviews),
  and generative engine citation. Outputs markdown with frontmatter for Payload CMS import, or JSON for
  Wagtail StreamField import. Use this skill whenever the user asks to write a blog post, create blog
  content, draft an article, write SEO content, "write a post about [topic]", "create content for
  [keyword]", or any request involving long-form content creation for a blog. Also trigger when the user
  references keyword research output and wants content produced from it, or asks to "turn these keywords
  into content", "write content from this research", "create a content calendar", or anything related to
  AEO/GEO content optimization. Pairs with the `keyword-research` skill (upstream data),
  `entity-knowledge-graph` skill (entity optimization), and the `payload-nextjs-stack` and
  `wagtail-nextjs-stack` skills (downstream CMS integration).
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

**In this article:**
- [Section 1 heading](#anchor)
- [Section 2 heading](#anchor)
- [Section 3 heading](#anchor)
- [FAQ](#faq)

*(Mini TOC — include on all posts over 1,500 words. Improves AEO extractability, helps AI systems understand content structure, and reduces bounce by giving readers a map. Use actual heading anchor links in the final CMS output.)*

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
1. **H1**: One per article, contains primary keyword, under 60 chars.
2. **H2s**: 5-8 per article; at least 2 with supporting keywords, at least 2 phrased as questions.
3. **H3s**: Use sparingly. In FAQ section, H3s = individual questions.
4. **TL;DR block**: REQUIRED at the top — standalone answer, the #1 AEO/GEO extraction target.
5. **Key takeaway blocks**: Blockquote under each major H2 — secondary extraction targets.
6. **Paragraphs**: 2-4 sentences max. No walls of text.
7. **Definition sentences**: Lead with "[Term] is [definition]." — clean, quotable, citable.
8. **Lists**: Use for genuine lists; numbered > bullets for how-to and steps (AEO).
9. **Internal links**: Suggest 2-4 placements with `[anchor text]({{internal_link:related-topic}})`.
10. **External links**: 2-3 authoritative sources for claims. Prefer primary sources (.gov, .edu, peer-reviewed).

### Step 4: AEO-Specific Optimization

Apply these patterns to maximize answer engine visibility:

#### Direct Answer Pattern
For every question-format H2: answer in the first sentence (this IS the featured snippet / AI Overview answer), then expand. Example: "[Process] typically takes [specific timeframe] for [common scenario]. [Qualifier]. [Evidence/source]."

#### Featured Snippet Targeting
Match the current SERP format for your target query:
- **Paragraph snippet**: Write a 40-60 word direct answer paragraph immediately after the H2
- **List snippet**: Use a numbered or bulleted list of 4-8 items immediately after the H2
- **Table snippet**: Use a markdown table comparing options, features, or data points
- **Definition snippet**: Start with "[Term] is..." or "[Term] refers to..."

#### PAA + Voice Optimization
- Use exact PAA question phrasing as H2s/H3s; direct answer in first 1-2 sentences (under 50 words)
- Voice answers must be speakable — clear, concise, no jargon; write as if Alexa will read it aloud

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

### Step 8: Detect CMS Target & Generate Output

**Detect which CMS to target** before generating output:

| Signal | Target CMS |
|--------|-----------|
| User mentions Wagtail, Django, or `wagtail-nextjs-stack` | **Wagtail** |
| Project context includes `wagtail` in stack or filenames | **Wagtail** |
| User mentions Payload, Next.js, or `payload-nextjs-stack` | **Payload CMS** (default) |
| No explicit CMS mentioned | **Payload CMS** (default) |

**When target is Payload CMS:** produce the markdown file with YAML frontmatter (see below).

**When target is Wagtail:** produce BOTH:
1. The markdown post body (for review/editing) saved as `./outputs/blog-{slug}.md`
2. The Wagtail import JSON saved as `./outputs/blog-{slug}-wagtail.json`

See `references/output-formats.md` for the full JSON schema and field mapping details.

---

#### Payload CMS Frontmatter

Produce complete YAML frontmatter covering these sections:
- **Core**: `title`, `slug`, `meta_title`, `meta_description`, `primary_keyword`, `supporting_keywords`, `search_intent`, `date`, `lastModified`, `author`, `author_credentials`, `category`, `featured_image_alt`
- **SEO**: `internal_links_suggested`, `external_sources`
- **AEO**: `tldr`, `featured_snippet_format`, `paa_questions`, `voice_search_phrases`
- **GEO**: `entities` (with `name`, `type`, `relationship`, `sameAs`), `citable_claims`, `original_value`, `content_freshness`
- **Schema**: `schema_type`, `schema_markup` (Article/HowTo/FAQ JSON-LD), `faq_schema`, `how_to_schema`, `speakable_selectors`

See `references/output-formats.md` for the full annotated YAML template and Payload field mapping table.

### Step 9: Output

**Payload CMS (default):** Save the complete markdown file with frontmatter to:
```
./outputs/blog-{slug}.md
```

**Wagtail:** Save both outputs:
```
./outputs/blog-{slug}.md               ← markdown body for review
./outputs/blog-{slug}-wagtail.json     ← import-ready JSON
```

**Batch mode (multiple posts):**
```
./outputs/blog-posts/
├── blog-{slug-1}.md
├── blog-{slug-1}-wagtail.json   ← only when target is Wagtail
├── blog-{slug-2}.md
└── blog-{slug-2}-wagtail.json
```

---

## CMS Integration

This skill supports two CMS output formats. See `references/output-formats.md` for complete field mappings, JSON schemas, and block-type documentation.

| CMS | Output | Reference |
|-----|--------|-----------|
| **Payload CMS** (default) | `blog-{slug}.md` with YAML frontmatter | `references/output-formats.md#payload-cms` |
| **Wagtail** | `blog-{slug}.md` + `blog-{slug}-wagtail.json` | `references/output-formats.md#wagtail` |

For Wagtail import instructions and the Django management command, see `references/wagtail-import.md`.

---

## Batch Mode: Content Calendar

When the user provides full keyword research JSON and asks to "create content" or "build a content calendar", switch to batch planning mode:

1. Review all `content_opportunities` from the keyword research
2. If `topical_authority` data exists, use `content_creation_order` as the writing sequence
3. Present a content calendar: `Pri | Title | Primary Keyword | Intent | Words | AEO Target | GEO Value`
   - Use keyword research data to populate all columns
   - Annotate AEO target format (AI Overview / featured snippet / PAA domination / definition snippet)
   - Annotate GEO value (definitions, framework, entity relationships, original data)
4. Ask the user which posts to write (or confirm the full calendar)
5. Write posts one at a time, saving each to the outputs directory

---

## Quality Checklist

Before finalizing any blog post, run through these gates. Full checklists in `references/quality-checklist.md`.

**SEO** — Keyword in H1/TL;DR/first 100 words/one H2/meta/slug/conclusion. 5-8 supporting keywords woven in. Hook in first 2 sentences. Frontmatter complete. Tone matches niche.

**AEO** — TL;DR block present. Key takeaway under each H2. At least 2 question-format H2s. Direct answer first sentence after each question H2. FAQ section with 3-5 items. FAQPage + HowTo schema where applicable.

**GEO** — 3+ citable claims with source + date. Clean definition sentences for key concepts. Entities named explicitly on first mention with `sameAs` URLs. Author credentials included. `lastModified` set. Original value present.

**Content quality** — No filler. Active voice. Not a rehash of what's ranking. No SEO spam.

---

## Anti-Patterns (DO NOT)

- ❌ Generic openings — "In today's fast-paced digital landscape..."
- ❌ Keyword stuffing — if it reads awkwardly, remove the keyword
- ❌ Thin sections — every H2 should be 200+ words with substance
- ❌ Burying the answer — lead with the answer, then explain (AEO rule)
- ❌ Unnamed frameworks — if you create a methodology, name it (GEO rule)
- ❌ Unattributed statistics — every number needs a source and date (GEO rule)
- ❌ Entity ambiguity — "the platform" instead of "Payload CMS" (GEO rule)
- ❌ Stale dates — never publish without `date` and `lastModified` (GEO rule)
- ❌ Missing author signals — anonymous content gets deprioritized by AI models
- ❌ Writing to hit word count — don't pad if the topic is well covered

# Quality Checklist

Full pre-publish verification checklist for blog posts produced by the `seo-blog-writer` skill.

---

## SEO Checks

- [ ] Word count is 1,500–3,000 words
- [ ] Primary keyword appears in: H1, TL;DR, first 100 words, one H2, meta description, slug, conclusion
- [ ] 5-8 supporting keywords are naturally woven throughout
- [ ] All H2s are meaningful section headers (not generic "Introduction" or "Conclusion")
- [ ] No paragraph exceeds 4 sentences
- [ ] At least one data point, example, or specific claim per major section
- [ ] Hook in the first 2 sentences is compelling (no clichés)
- [ ] CTA is clear and relevant to search intent
- [ ] Frontmatter is complete (all fields populated except author/category)
- [ ] Internal link suggestions are included (2-4 placements)
- [ ] External source suggestions are included for claims/stats
- [ ] Tone matches the niche (see Tone Adaptation table in SKILL.md)

---

## AEO Checks

- [ ] TL;DR block at the top (2-3 sentences, standalone answer)
- [ ] Key takeaway block under each major H2
- [ ] At least 2 H2s phrased as questions (matching PAA data)
- [ ] Direct answer in first sentence after each question H2 (under 50 words)
- [ ] FAQ section with 3-5 questions and concise answers
- [ ] Featured snippet format matches the current SERP format for target query
- [ ] FAQPage schema is present and accurate
- [ ] HowTo schema present if article contains step-by-step instructions
- [ ] Voice search phrases included in frontmatter
- [ ] Speakable selectors identified (`speakable_selectors` in frontmatter)

---

## GEO Checks

- [ ] At least 3 citable claims with specific attribution (source + date)
- [ ] Key concepts have clean, standalone definition sentences ("[Term] is [definition].")
- [ ] All entities named explicitly with context on first mention
- [ ] Entity map in frontmatter with `name`, `type`, `relationship`, and `sameAs` URLs
- [ ] Author credentials included for E-E-A-T signals
- [ ] `lastModified` date set for content freshness
- [ ] Original value clearly present (unique data, framework, or contrarian perspective)
- [ ] Content passes the "would an AI confidently cite this?" test
- [ ] No vague claims — everything is specific and attributable
- [ ] Publisher and author schema include `sameAs` links

---

## Content Quality

- [ ] Content is original — not a rehash of what's already ranking
- [ ] No SEO spam — reads naturally to a human first
- [ ] No filler or padding to hit word count
- [ ] Active voice predominates
- [ ] Varied paragraph and sentence structure (short/long/medium — no walls of same-length sentences)

---

## CMS-Specific Checks

### Payload CMS
- [ ] YAML frontmatter is syntactically valid
- [ ] `schema_markup` is valid JSON-LD
- [ ] `entities` array has at least one entry with `type` and `sameAs`
- [ ] `faq_schema` populated if FAQ section exists
- [ ] `how_to_schema` populated if article contains numbered steps

### Wagtail
- [ ] `{slug}-wagtail.json` file is valid JSON
- [ ] All `rich_text` block values use HTML, not markdown
- [ ] `intro` field is plain text (no markdown or HTML)
- [ ] `publish_date` is in ISO format (`YYYY-MM-DD`)
- [ ] `tags` array uses lowercase, hyphenated slugs
- [ ] `categories` array matches existing category slugs (or will be created on import)
- [ ] `schema_markup` JSON-LD object is valid
- [ ] StreamField block types match the `BlogPostPage` model definition

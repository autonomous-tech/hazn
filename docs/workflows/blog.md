# Blog Content Pipeline

> SEO and AI-optimized long-form blog content — keyword research, content calendar, article writing, SEO polish, ready for CMS import.

## When to Use

- Building organic traffic to an existing site post-launch
- Filling a content calendar for a client on retainer
- Targeting specific keyword clusters to establish topical authority
- Writing content that will get cited by AI answer engines (ChatGPT, Perplexity, Google AI Overviews)

**NOT for:**
- Landing page copy → use `/hazn-landing` or `/hazn-copy`
- One-off short-form content (social, email snippets)
- Content that needs brand voice calibration from scratch — run `/hazn-strategy` first

## Requirements

- Site URL or project folder with existing `strategy.md`
- Seed topics or keyword areas to target (or permission to derive from strategy)
- Target audience and primary conversion goal (blog CTA)
- CMS target: Payload CMS (Next.js) or WordPress — affects frontmatter format

## How It Works

### Phase 1 — Keyword Research (~2–3 hours, one-time setup)
Identify seed topics from strategy, discover long-tail opportunities, analyze competitor content gaps, map keywords to search intent (informational / commercial / transactional).  
**Output:** `.hazn/outputs/keyword-research.md`

### Phase 2 — Content Planning (~1 hour, one-time setup)
Build content calendar: pillar/cluster structure, article priorities, publication schedule.  
**Output:** `.hazn/outputs/content-calendar.md`

### Phase 3 — Article Writing (~1–2 hours per article)
**Agent:** Content Writer  
Per article: research topic depth, write draft (1,500–3,000 words), optimize for primary keyword, add internal links (2–5), add external authority links (1–3), create meta tags, add FAQ section with schema markup.  
**Output:** `content/blog/{slug}.md` with frontmatter

Article structure: hook intro → H2 sections with secondary keywords → practical application → key takeaways → FAQ (2–3 questions) → CTA.

### Phase 4 — SEO Polish (~30 minutes per article)
**Agent:** SEO Specialist  
Verify keyword placement, check H1/H2 structure, add/validate structured data (FAQ schema, Article schema), optimize images, internal linking pass.

## HITL Checkpoints

| Checkpoint | Why it matters / risk of skipping |
|---|---|
| Keyword research review | Publishing articles before validating keyword targeting means writing content nobody searches for. Volume and difficulty data should confirm the opportunity is real before committing writing time. |
| Content calendar approval | Pillar/cluster structure determines which articles get internal links from which. Getting this wrong means scattered authority instead of concentrated topical depth. |

## Caveats & Gotchas

- Articles optimized for AEO (AI answer engines) need definitive, citeable statements — not hedging language. If the content writer hedges everything, AI engines won't cite it.
- Keyword research tools (Ahrefs, SEMrush) require API access or manual input. Without tool access, volume/difficulty data is estimated.
- Internal linking requires knowing the site's existing URL structure. Pass the site map or existing content inventory when spawning the content writer.
- Each article needs 2–5 internal links — if the site is new and has no other content, links will be limited to key pages (services, about, homepage). Flag this to the client.
- FAQ schema must be implemented in the CMS or injected manually. The content writer outputs the markdown structure; the developer or SEO specialist must add the JSON-LD.

## Outputs

```
.hazn/outputs/
├── keyword-research.md
├── content-calendar.md
└── content-log.md            ← updated per article
content/
└── blog/
    ├── {slug-1}.md
    ├── {slug-2}.md
    └── ...
```

Each article file:
```
---
title: ""
description: ""       ← 155 chars
slug: ""
publishedAt: ""
keywords: [...]
author: ""
category: ""
---
[article body with FAQ and CTA]
```

## Example Trigger

```
/hazn-content
Site: acmeconsulting.com
Topics: B2B sales training, SaaS sales process, enterprise sales cycles
Audience: VP Sales at SaaS companies (50–500 employees)
CTA: Book a demo
Articles needed: 5
```

# AEO & GEO Guide — SiteScore

## Definitions

**AEO (Answer Engine Optimisation):** Optimising content so that AI answer engines (ChatGPT, Perplexity, Google AI Overviews, Gemini, Bing Copilot) can find, access, and cite your content in their generated answers.

**GEO (Generative Engine Optimisation):** Structuring content so that large language models extract, surface, and accurately represent your content in AI-generated responses. Goes beyond AEO — focuses on HOW content is written, not just whether bots can access it.

## AEO Checks (run in Standard + Deep Dive)

### Bot Access Audit
Check robots.txt for these crawlers — all should be ALLOWED:
- GPTBot (ChatGPT training)
- ChatGPT-User (ChatGPT Browse)
- ClaudeBot (Claude)
- anthropic-ai (Claude training)
- PerplexityBot (Perplexity)
- Perplexity-User (Perplexity live)
- Google-Extended (Gemini / AI Overviews)
- Bingbot (Bing / Copilot)

Flag as HIGH priority if any of the above are blocked.

### Structured Data for AEO
Check for FAQ schema, HowTo schema, Article schema with author — these are directly used by AI engines for answer extraction.

### llms.txt
Check if /llms.txt exists. This emerging standard signals to LLMs what content to prioritise.

## GEO Checks (run in Standard + Deep Dive)

### Content Extractability
AI systems extract passages, not pages. Check each key page for:
- First paragraph clearly defines what the company/product does (self-contained)
- Key claims stated in 40-60 word extractable passages
- H2/H3 headings match natural language query patterns ("What is...", "How to...", "Best...")
- Statistics include cited sources (boosts citation rate ~40%)
- Expert attribution with credentials (boosts citation rate ~30%)
- FAQ sections with direct one-sentence answers
- "Last updated" date visible

### Brand Citation Testing (Deep Dive only)
Manually test in each AI engine:
- "What is [brand name]?"
- "Best [category] for [use case]"
- "[Brand] vs [competitor]"

Record: cited / not cited / cited incorrectly

### GEO Improvement Recommendations
For each page that fails extractability:
- Rewrite opening paragraph to lead with a clear definition
- Add FAQ section targeting the top 3 questions users ask
- Add statistics with inline source citations
- Restructure headings to match query patterns

## Scoring

AEO Score (out of 10):
- Bot access: 4 pts (0.5 per major crawler allowed)
- Structured data for AEO: 3 pts (FAQPage, HowTo, Article with author)
- llms.txt: 1 pt
- Off-site entity signals: 2 pts

GEO Score (out of 10):
- Content extractability: 4 pts
- Query-pattern headings: 2 pts
- Statistics with sources: 2 pts
- FAQ sections present: 2 pts

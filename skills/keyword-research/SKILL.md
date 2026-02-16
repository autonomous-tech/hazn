---
name: keyword-research
description: >
  SEO keyword research and content strategy skill. Performs keyword discovery, search intent analysis, 
  difficulty estimation, and content opportunity mapping. Use this skill whenever the user mentions 
  keyword research, SEO keywords, content strategy, blog topic ideas, search volume, keyword difficulty, 
  SERP analysis, topical authority, content clusters, "what should I write about", "find keywords for [topic]", 
  or any request involving discovering what people search for online. Also trigger when the user asks for 
  content gap analysis, competitor keyword analysis, or long-tail keyword opportunities — even if they 
  don't explicitly say "keyword research."
---

# Keyword Research

## Overview

This skill enables comprehensive SEO keyword research by combining web search (SERP analysis, People Also Ask, related searches, autocomplete patterns) with optional API integrations (SEMrush, Ahrefs, Google Ads Keyword Planner). All output is structured JSON designed to feed into downstream agents or tools.

## Workflow

### Step 1: Gather Input

Extract from the user's request:

- **Seed topic or keyword** (required): The starting point for research
- **Industry/niche** (optional): Helps contextualize intent and difficulty
- **Target audience** (optional): Influences intent classification
- **Geographic target** (optional): Affects search patterns and localization
- **Content goals** (optional): "drive traffic", "generate leads", "build authority"
- **Competitor URLs** (optional): For gap analysis
- **Mode**: `standard` (default) or `topical-authority` (pillar-cluster mapping)

If the user provides just a seed keyword, proceed with sensible defaults. Don't over-ask — start researching and refine as you go.

### Step 2: Keyword Discovery

Use web search to expand the seed keyword into a comprehensive keyword universe. Run multiple searches systematically:

#### 2a. Core SERP Analysis
Search for the seed keyword and analyze:
- Top-ranking page titles and meta descriptions (what angle are they taking?)
- Featured snippets (what questions does Google answer directly?)
- People Also Ask boxes (extract all PAA questions)
- Related searches at bottom of SERP

**Search queries to run:**
```
"{seed keyword}"
"{seed keyword}" guide
"{seed keyword}" tips
"{seed keyword}" for beginners
"{seed keyword}" vs
"best {seed keyword}"
"how to {seed keyword}"
"{seed keyword}" examples
"{seed keyword}" tools
"{seed keyword}" {current year}
```

#### 2b. Long-Tail Expansion
Generate long-tail variations using modifier patterns:

- **Question modifiers**: what, how, why, when, where, which, can, does, is
- **Intent modifiers**: best, top, review, comparison, alternative, vs, free, cheap
- **Qualifier modifiers**: for beginners, for small business, for enterprise, step by step
- **Temporal modifiers**: 2026, latest, new, updated, trends

Search a representative sample of these to validate which ones return meaningful SERPs.

#### 2c. Competitor Analysis (if URLs provided)
For each competitor URL:
- Fetch the page and extract topic coverage
- Identify keywords they rank for based on content analysis
- Note content gaps (topics they miss that you could cover)

### Step 3: Classify Search Intent

For each discovered keyword, classify intent as one of:

| Intent | Signal | Example |
|--------|--------|---------|
| **informational** | how, what, why, guide, tutorial, tips | "how to do keyword research" |
| **navigational** | brand names, specific tools, "login" | "ahrefs keyword explorer" |
| **commercial** | best, top, review, comparison, vs, alternative | "best keyword research tools" |
| **transactional** | buy, price, discount, coupon, free trial | "semrush pricing" |

Use SERP composition as a signal too:
- Lots of blog posts → informational
- Product pages dominating → transactional
- Comparison articles → commercial
- Brand homepages → navigational

### Step 4: Estimate Metrics

Since we're primarily using web search (not APIs), estimate metrics based on SERP signals:

#### Search Volume Estimation
Categorize into buckets based on SERP signals:

| Bucket | Estimated Monthly Volume | Signals |
|--------|--------------------------|---------|
| `very_high` | 10,000+ | Highly competitive SERPs, major brands ranking, ads present |
| `high` | 1,000–10,000 | Competitive SERPs, established sites ranking |
| `medium` | 100–1,000 | Mix of established and smaller sites |
| `low` | 10–100 | Niche SERPs, forums and small blogs ranking |
| `very_low` | <10 | Thin SERPs, few relevant results |

#### Keyword Difficulty Estimation
Estimate based on:
- **Domain authority of top results**: Major brands (high), mix (medium), small sites (low)
- **Content quality of top results**: Comprehensive guides (hard to beat) vs thin content (opportunity)
- **SERP features**: Featured snippets, knowledge panels increase difficulty
- **Ad presence**: Ads suggest commercial value and competition

Rate as: `easy` (score 1-30), `medium` (31-60), `hard` (61-80), `very_hard` (81-100)

#### Content Opportunity Score
A composite score (1-10) based on:
- Lower difficulty = higher opportunity
- Higher volume = higher opportunity
- Commercial/transactional intent = higher value
- Content gaps in current SERPs = higher opportunity

### Step 5: Topical Authority Mapping (Optional Mode)

When `topical-authority` mode is requested, organize keywords into a hub-and-spoke model:

1. **Identify pillar topics**: Broad, high-volume topics that warrant comprehensive guides
2. **Map cluster subtopics**: Specific long-tail keywords that support each pillar
3. **Define internal linking structure**: How clusters connect back to pillars
4. **Prioritize content creation order**: Start with pillar content, then fill clusters

### Step 6: Generate JSON Output

Produce structured JSON and save to `./outputs/keyword-research.json` (relative to workspace).

---

## Output Schemas

### Standard Mode Output

```json
{
  "meta": {
    "seed_keyword": "string",
    "industry": "string | null",
    "target_audience": "string | null",
    "geographic_target": "string | null",
    "research_date": "YYYY-MM-DD",
    "mode": "standard",
    "data_sources": ["web_search", "semrush_api"],
    "total_keywords": 0
  },
  "keywords": [
    {
      "keyword": "string",
      "search_intent": "informational | navigational | commercial | transactional",
      "volume_bucket": "very_low | low | medium | high | very_high",
      "estimated_monthly_volume": "string range e.g. '1,000-10,000'",
      "difficulty": "easy | medium | hard | very_hard",
      "difficulty_score": 0,
      "opportunity_score": 0.0,
      "serp_features": ["featured_snippet", "people_also_ask", "ads", "video", "images", "knowledge_panel"],
      "content_angle": "string — suggested angle based on SERP gaps",
      "parent_topic": "string | null — broader topic this keyword belongs to",
      "source": "web_search | api"
    }
  ],
  "questions": [
    {
      "question": "string — from People Also Ask or PAA-style queries",
      "parent_keyword": "string",
      "search_intent": "informational",
      "opportunity_score": 0.0
    }
  ],
  "content_opportunities": [
    {
      "title": "string — suggested content piece",
      "target_keyword": "string — primary keyword to target",
      "supporting_keywords": ["string"],
      "search_intent": "string",
      "estimated_difficulty": "string",
      "rationale": "string — why this is a good opportunity"
    }
  ],
  "competitive_insights": {
    "top_competitors": ["string — domains dominating SERPs"],
    "content_gaps": ["string — topics competitors miss"],
    "weak_spots": ["string — areas where competitor content is thin or outdated"]
  }
}
```

### Topical Authority Mode Output

Extends the standard output with an additional `topical_authority` key:

```json
{
  "topical_authority": {
    "pillars": [
      {
        "pillar_topic": "string",
        "pillar_keyword": "string",
        "pillar_content_type": "ultimate guide | comprehensive overview | hub page",
        "volume_bucket": "string",
        "clusters": [
          {
            "cluster_topic": "string",
            "cluster_keyword": "string",
            "supporting_keywords": ["string"],
            "search_intent": "string",
            "volume_bucket": "string",
            "difficulty": "string",
            "content_type": "blog post | how-to | comparison | case study | FAQ",
            "links_to_pillar": true,
            "priority": "high | medium | low"
          }
        ]
      }
    ],
    "content_creation_order": [
      {
        "step": 1,
        "content": "string",
        "keyword": "string",
        "rationale": "string"
      }
    ]
  }
}
```

---

## API Integration (Optional)

When API keys are available, enhance the research with real data. Read `references/api-integration.md` for detailed setup.

### Supported APIs

| API | What It Adds | Env Variable |
|-----|-------------|--------------|
| SEMrush | Exact volumes, KD scores, SERP features, competitor data | `SEMRUSH_API_KEY` |
| Ahrefs | Traffic estimates, backlink data, content gaps | `AHREFS_API_KEY` |
| Google Ads Keyword Planner | Official Google volume ranges, CPC, competition | `GOOGLE_ADS_API_KEY` |

### API Behavior

1. Check if API keys exist in environment variables
2. If available, use APIs to enrich web search findings with exact metrics
3. If not available, fall back gracefully to web-search-based estimation (default)
4. In JSON output, mark each keyword's `source` field accordingly

When API data is available, replace estimated buckets with actual numbers:
- `volume_bucket` → keep for compatibility
- Add `exact_monthly_volume` (integer) 
- Replace `difficulty_score` estimate with API's actual KD score
- Add `cpc` and `competition_level` fields from Google Ads data

---

## Best Practices

1. **Start broad, then narrow**: Begin with seed keyword SERPs, then drill into long-tails
2. **Validate with SERPs**: Don't just brainstorm keywords — verify they have real search results
3. **Prioritize quick wins**: Keywords with medium volume + low difficulty = best ROI
4. **Group by intent**: Content strategy should map to the buyer's journey
5. **Check freshness**: Prefer keywords with recent content in SERPs (indicates active demand)
6. **Aim for 30-80 keywords** in a standard research session; more for topical authority mode
7. **Always include questions**: PAA questions are goldmines for FAQ content and featured snippets
8. **Note SERP features**: If video dominates, suggest video content; if listicles dominate, suggest list posts
9. **Save the JSON output** to `./outputs/keyword-research.json` so downstream agents can consume it

---

## Example Usage

**User**: "Find keywords for email marketing automation"

**Expected behavior**:
1. Run 8-12 web searches covering the seed + modifiers
2. Extract PAA questions, related searches, SERP composition
3. Classify 40-60 keywords by intent and difficulty
4. Identify 5-8 content opportunities
5. Output structured JSON to `./outputs/keyword-research.json`

**User**: "Do a topical authority map for 'project management software'"

**Expected behavior**:
1. All standard steps above
2. Additionally identify 3-5 pillar topics
3. Map 5-10 cluster subtopics per pillar
4. Provide content creation order with rationale
5. Output extended JSON with `topical_authority` section

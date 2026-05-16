# API Integration Reference

This document covers how to integrate optional third-party SEO APIs to enhance keyword research with real data.

## Table of Contents
1. SEMrush API
2. Ahrefs API
3. Google Ads Keyword Planner API
4. Enrichment Logic

---

## 1. SEMrush API

### Setup
Set environment variable: `SEMRUSH_API_KEY`

### Useful Endpoints

**Keyword Overview** — Get volume, difficulty, CPC for a keyword:
```bash
curl "https://api.semrush.com/?type=phrase_all&key=${SEMRUSH_API_KEY}&phrase={keyword}&database=us"
```

Returns: Search Volume, KD%, CPC, Competition, Number of Results, SERP Features

**Related Keywords** — Expand seed keywords:
```bash
curl "https://api.semrush.com/?type=phrase_related&key=${SEMRUSH_API_KEY}&phrase={keyword}&database=us&export_columns=Ph,Nq,Kd,Co,Nr"
```

**Keyword Questions** — Get question-form keywords:
```bash
curl "https://api.semrush.com/?type=phrase_questions&key=${SEMRUSH_API_KEY}&phrase={keyword}&database=us"
```

**Domain Organic Keywords** — For competitor analysis:
```bash
curl "https://api.semrush.com/?type=domain_organic&key=${SEMRUSH_API_KEY}&domain={competitor.com}&database=us"
```

### Rate Limits
- API units consumed per request vary by endpoint
- Monitor usage: `https://api.semrush.com/?type=api_units&key=${SEMRUSH_API_KEY}`

---

## 2. Ahrefs API

### Setup
Set environment variable: `AHREFS_API_KEY`

### Useful Endpoints (v3)

**Keywords Explorer** — Volume, difficulty, clicks data:
```bash
curl -H "Authorization: Bearer ${AHREFS_API_KEY}" \
  "https://api.ahrefs.com/v3/keywords-explorer/google/overview?select=keyword,volume,difficulty,cpc,clicks&keywords={keyword}&country=us"
```

**Content Gap** — Find keywords competitors rank for but you don't:
```bash
curl -H "Authorization: Bearer ${AHREFS_API_KEY}" \
  "https://api.ahrefs.com/v3/site-explorer/content-gap?target={your-domain}&competitors={competitor1},{competitor2}"
```

**SERP Overview** — Who ranks for a keyword:
```bash
curl -H "Authorization: Bearer ${AHREFS_API_KEY}" \
  "https://api.ahrefs.com/v3/keywords-explorer/google/serp-overview?keyword={keyword}&country=us"
```

### Rate Limits
- Varies by plan (Lite: 500 rows/month, Standard: 50k rows/month)
- Check headers for remaining quota

---

## 3. Google Ads Keyword Planner API

### Setup
Requires OAuth2 flow. Set environment variables:
- `GOOGLE_ADS_API_KEY` — Developer token
- `GOOGLE_ADS_CLIENT_ID` — OAuth client ID
- `GOOGLE_ADS_CLIENT_SECRET` — OAuth client secret
- `GOOGLE_ADS_REFRESH_TOKEN` — OAuth refresh token
- `GOOGLE_ADS_CUSTOMER_ID` — Google Ads customer ID

### Usage via Python (google-ads library)
```python
from google.ads.googleads.client import GoogleAdsClient

client = GoogleAdsClient.load_from_env()
keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")

request = client.get_type("GenerateKeywordIdeasRequest")
request.customer_id = CUSTOMER_ID
request.language = "languageConstants/1000"  # English
request.geo_target_constants = ["geoTargetConstants/2840"]  # US
request.keyword_seed.keywords.append("seed keyword")

response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
```

Returns: keyword text, avg monthly searches (range), competition level, CPC low/high estimate

### Notes
- Returns volume as ranges (e.g., 1K-10K) unless you have active ad spend
- Most accurate for commercial/transactional queries
- Best source for CPC and competition data

---

## 4. Enrichment Logic

When API keys are detected, use this priority:

1. **Always run web search first** — This is the foundation
2. **Enrich with API data** — Layer on exact metrics where available
3. **Merge intelligently**:
   - If API provides exact volume → use it, keep bucket for compatibility
   - If API provides KD score → replace estimated score, keep difficulty label
   - If API finds additional keywords → add them with `source: "api"`
   - If API and web search conflict → prefer API data for metrics, web search for SERP features

### Field Mapping When APIs Are Available

```json
{
  "keyword": "from any source",
  "volume_bucket": "derived from exact volume or estimated",
  "exact_monthly_volume": "from API (integer, null if web-only)",
  "difficulty_score": "from API if available, else estimated 1-100",
  "cpc": "from Google Ads or SEMrush (null if unavailable)",
  "competition_level": "from Google Ads (LOW/MEDIUM/HIGH, null if unavailable)",
  "source": "web_search | semrush | ahrefs | google_ads | mixed"
}
```

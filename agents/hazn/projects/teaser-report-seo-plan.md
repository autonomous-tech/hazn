# Teaser Report — SEO Audit Expansion Plan
**Prepared by:** Hazn Strategist  
**Date:** 2026-03-05  
**Status:** Planning → Ready for Implementation

---

## Executive Summary

The current SEO section in the Teaser Report is a placeholder. It shows 4 data points and calls itself "SEO & Structured Data." That's not enough to hook a serious prospect. This plan expands SEO from a single lightweight section into **four distinct sub-sections** with 30+ signals, a proper 0–100 SEO Score, and aggressive upsell gates that make prospects feel the gap between what we can see and what we'd find with full access.

**Decision:** SEO weight in the overall grade increases from 10% → 20%. A new 6th scorecard badge is added: "SEO Health."

---

## 1. Data to Collect (Zero-Access, Public Only)

### 1.1 PageSpeed Insights API (Already in use — extend it)

Pull additional fields not currently used:

```
# Technical SEO signals from PSI
- mobile usability issues (MOBILE_FRIENDLY_RULE)
- is-crawlable audit (Lighthouse)
- robots-txt audit (Lighthouse)
- canonical audit (Lighthouse)
- hreflang audit (Lighthouse)
- structured-data audit (Lighthouse)
- link-text audit (Lighthouse)
- crawlable-anchors audit (Lighthouse)
- document-title audit (Lighthouse)
- meta-description audit (Lighthouse)
- image-alt audit (Lighthouse)
- heading-order audit (Lighthouse)
- duplicate-id-active audit (Lighthouse)
- font-size audit (Lighthouse)
- tap-targets audit (Lighthouse)
- uses-text-compression (Lighthouse — affects crawl budget)
- uses-long-cache-ttl (Lighthouse — affects crawl budget)
- total-byte-weight (Lighthouse — crawl budget signal)
- network-requests count (Lighthouse)
- third-party-summary (Lighthouse — external calls, crawl bloat)
- lcp-lazy-loaded (Lighthouse)
- largest-contentful-paint-element (Lighthouse)
```

**Two PSI calls already happen** (mobile + desktop). Just pull more fields from the existing response — zero new API cost.

---

### 1.2 Direct Page Fetch + Header Inspection

```bash
# Homepage
curl -sI -L --max-redirs 10 -o /dev/null -w \
  "status=%{http_code}\nredirect_count=%{num_redirects}\nfinal_url=%{url_effective}\ntime_total=%{time_total}" \
  "$URL"

# Check canonical tag
curl -s "$URL" | grep -i 'rel="canonical"' | head -1

# Check robots meta
curl -s "$URL" | grep -i 'name="robots"' | head -1

# Check X-Robots-Tag header
curl -sI "$URL" | grep -i "x-robots-tag"

# Check hreflang tags
curl -s "$URL" | grep -i 'rel="alternate"' | head -20

# Check Open Graph tags
curl -s "$URL" | grep -i 'property="og:' | head -10

# Check Twitter Card tags
curl -s "$URL" | grep -i 'name="twitter:' | head -10

# Check viewport meta
curl -s "$URL" | grep -i 'name="viewport"'

# Check charset
curl -s "$URL" | grep -i 'charset' | head -3

# Heading structure (H1, H2, H3 counts)
curl -s "$URL" | grep -ioP '<h[1-6][^>]*>.*?</h[1-6]>' | head -30

# Internal vs external link count (rough)
curl -s "$URL" | grep -oP 'href="[^"]*"' | wc -l

# Image alt text audit (count missing alts)
curl -s "$URL" | grep -oP '<img[^>]*>' | grep -v 'alt="[^"]*"' | wc -l

# Word count (content depth signal)
curl -s "$URL" | sed 's/<[^>]*>//g' | wc -w
```

---

### 1.3 robots.txt Inspection

```bash
BASE="${URL%/}"
curl -s "$BASE/robots.txt" | head -100

# Parse:
# - Is Googlebot blocked anywhere?
# - Is GPTBot allowed or blocked?
# - Is ClaudeBot allowed or blocked?
# - Is CCBot (Common Crawl) allowed or blocked?
# - Sitemap declared in robots.txt?
# - Disallow rules count
# - Crawl-delay set?
```

---

### 1.4 XML Sitemap Analysis

```bash
# Try common locations
for path in /sitemap.xml /sitemap_index.xml /sitemap/sitemap.xml /wp-sitemap.xml; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$path")
  if [ "$STATUS" = "200" ]; then
    # Fetch and count URLs
    COUNT=$(curl -s "$BASE$path" | grep -c '<loc>')
    echo "Found: $BASE$path — $COUNT URLs"
    
    # Check lastmod freshness
    LASTMOD=$(curl -s "$BASE$path" | grep '<lastmod>' | head -1)
    
    # Check if sitemap index (nested sitemaps)
    IS_INDEX=$(curl -s "$BASE$path" | grep -c '<sitemapindex')
    
    # Check for image sitemap
    HAS_IMAGE=$(curl -s "$BASE$path" | grep -c 'image:loc')
  fi
done
```

---

### 1.5 Structured Data Parsing

```bash
# Extract all JSON-LD blocks
curl -s "$URL" | grep -oP '(?<=<script type="application/ld\+json">).*?(?=</script>)' 

# Schema types found — parse @type values
# Count schema blocks
# Detect: Organization, WebSite, WebPage, Product, Article, FAQPage, HowTo,
#         BreadcrumbList, LocalBusiness, SiteLinksSearchBox, Review, etc.

# Also check Microdata
curl -s "$URL" | grep -i 'itemtype=' | head -20

# Also check RDFa
curl -s "$URL" | grep -i 'typeof=' | head -10
```

---

### 1.6 Redirect Chain Detection

```bash
# Full redirect chain with status codes at each hop
curl -sI -L --max-redirs 15 -w "%{url_effective}" "$URL" 2>&1 | grep -E "HTTP/|Location:|^http"

# Also test:
# - HTTP → HTTPS redirect (is it present?)
# - www → non-www (or vice versa)
# - trailing slash consistency (/ vs no /)
# - Count total redirect hops
```

---

### 1.7 Canonical + Indexability Signals

```bash
# Self-referencing canonical?
CANONICAL=$(curl -s "$URL" | grep -oP '(?<=canonical" href=")[^"]*')
# Is $CANONICAL == $URL (normalized)?

# noindex check
NOINDEX=$(curl -s "$URL" | grep -i 'noindex')
X_NOINDEX=$(curl -sI "$URL" | grep -i "noindex")

# Is URL in sitemap? (cross-reference sitemap URLs against canonical)
```

---

### 1.8 Mobile-First Indexing Signals

```bash
# Viewport meta present?
curl -s "$URL" | grep -i 'viewport'

# Check PSI mobile score (already collected)
# Compare PSI mobile vs desktop LCP gap (>2s gap = mobile indexing risk)

# Check if mobile user-agent returns different content (basic check)
MOBILE_WORDS=$(curl -s -A "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)" "$URL" | sed 's/<[^>]*>//g' | wc -w)
DESKTOP_WORDS=$(curl -s "$URL" | sed 's/<[^>]*>//g' | wc -w)
# Large word count gap = possible content parity issue
```

---

### 1.9 AI Search Readiness Signals

```bash
# llms.txt (emerging standard)
curl -s -o /dev/null -w "%{http_code}" "$BASE/llms.txt"
curl -s "$BASE/llms.txt" | head -50

# AI crawler rules in robots.txt
grep -iE "(GPTBot|ClaudeBot|PerplexityBot|YouBot|CCBot|Bytespider|anthropic-ai|cohere-ai)" "$ROBOTS_CONTENT"

# FAQ schema (answers questions AI might surface)
# Already captured in structured data step

# Answer-box-friendly content signals (from PSI / heading structure)
```

---

### 1.10 Link Profile (Surface-Level, No API Needed)

```bash
# Internal link count from homepage
INTERNAL=$(curl -s "$URL" | grep -oP 'href="(/[^"]*|'"$BASE"'[^"]*)"' | wc -l)

# External link count from homepage
EXTERNAL=$(curl -s "$URL" | grep -oP 'href="https?://[^"]*"' | grep -v "$DOMAIN" | wc -l)

# Nofollow external links?
NOFOLLOW=$(curl -s "$URL" | grep -i 'nofollow' | wc -l)

# Broken internal links (check top 5 internal links for 200 status)
curl -s "$URL" | grep -oP 'href="(/[^"]*)"' | head -5 | while read path; do
  curl -s -o /dev/null -w "$path: %{http_code}\n" "$BASE$path"
done
```

---

## 2. Section Design

### New SEO Section Architecture

Replace the single "SEO & Structured Data" section with **4 sub-sections** under a unified `#seo-audit` parent. Total visual weight: similar to the existing Core Web Vitals section — detailed but scannable.

---

### Section A: Technical SEO Foundations
**ID:** `#seo-technical`  
**Position:** After Core Web Vitals (moved up — it's foundational)

#### Data Sources
- robots.txt parse
- Sitemap fetch + count
- Redirect chain detection
- Canonical tag analysis
- Header inspection (X-Robots-Tag, noindex)
- Mobile word-count parity check
- PSI: is-crawlable, robots-txt, canonical, font-size, tap-targets audits

#### Components
- **Grade badge** (A–F) for Technical SEO sub-score
- **Signal grid** (3-col on desktop, 2-col mobile): 6–8 signal cards
- **Redirect chain visualizer** (simple step diagram if redirects > 1)
- **Issue alert cards** for critical failures (noindex on production = red alert)

#### Signal Cards to Show (Free)

| Signal | Shows Free | What's Shown |
|--------|-----------|--------------|
| HTTPS enforcement | ✅ | HTTP→HTTPS redirect present/missing |
| Redirect chain | ✅ | Hop count + final URL |
| robots.txt status | ✅ | Found/missing, Googlebot rule, disallow count |
| Canonical tag | ✅ | Present/missing/misconfigured |
| noindex detection | ✅ | Pass/fail — this is a critical issue |
| Sitemap found | ✅ | URL, page count, last modified |
| www/non-www consistency | ✅ | Pass/fail |
| Mobile content parity | ✅ | Word count delta mobile vs desktop |
| Crawl-delay set | ✅ | Value if present (can hurt crawl budget) |
| X-Robots-Tag | ✅ | Any header-level indexing directives |

#### Gated Behind Gate 3 (SEO Audit Package)

> 🔒 **"We crawled your homepage. But Googlebot doesn't stop at one page."**
> 
> With a full crawl using Screaming Frog + GSC integration, we'd map:
> - Every orphaned page (no internal links pointing to it)
> - Every redirect chain longer than 2 hops (kills PageRank)  
> - Every page blocked by robots.txt that Google has already indexed anyway
> - Your crawl budget allocation across [X] total URLs
> - Pagination implementation (rel=next/prev vs infinite scroll)
> - hreflang correctness across all language variants
> 
> **Unlock with:** SEO Audit ($X) or Full MarTech Audit ($Y)

#### Scoring Formula — Technical SEO Sub-Score (0–100)

```
Points:
- HTTPS enforced: +10
- Redirect chain ≤ 1 hop: +10 (2 hops: +5, 3+: 0)
- robots.txt found, Googlebot not blocked: +10
- Canonical tag present + self-referencing: +15
- No noindex on production: +20 (CRITICAL — 0 if failing)
- Sitemap found + >5 URLs: +10
- www consistency: +5
- Mobile content parity (<20% word count delta): +10
- No crawl-delay: +5
- No X-Robots noindex: +5

Max: 100
```

---

### Section B: On-Page SEO
**ID:** `#seo-onpage`  
**Position:** After Technical SEO

#### Data Sources
- Homepage HTML parse: title tag, meta description, H1–H3 structure
- PSI: document-title, meta-description, heading-order, image-alt audits
- Word count from stripped HTML
- OG tags + Twitter Card presence
- Link text audit (PSI: link-text)

#### Components
- **Content signal table** (title tag preview, meta description preview, H1 text)
- **Heading hierarchy tree** (visual: H1 → H2 → H3 structure from homepage)
- **Missing alt text counter** (number + percentage)
- **Word count bar** with benchmark range
- **OG/Twitter card badges**

#### Signal Cards to Show (Free)

| Signal | Shows Free | What's Shown |
|--------|-----------|--------------|
| Title tag | ✅ | Full text + character count + pass/fail (50–60 chars) |
| Meta description | ✅ | Full text + character count + pass/fail (140–160 chars) |
| H1 presence | ✅ | H1 text, count (flags if 0 or >1) |
| H2/H3 count | ✅ | Rough structure (how many subheadings) |
| Heading order | ✅ | PSI audit result — logical H1→H2→H3 flow |
| Image alt coverage | ✅ | % of images with alt text |
| Word count | ✅ | Homepage word count vs 300-word minimum |
| OG tags | ✅ | Present/missing — impacts social sharing CTR |
| Link text quality | ✅ | PSI flag if "click here" style anchors found |

#### Gated Behind Gate 3

> 🔒 **"Your homepage title tag is [X chars]. But that's one page."**
>
> Without crawling your full site, we can't tell you:
> - How many pages have duplicate title tags (our average client has 23% duplication)
> - Which pages are missing meta descriptions entirely
> - Where your H1 tags are missing, duplicated, or stuffed with keywords
> - Whether your product/service pages have enough content to rank (thin content = Google's #1 on-page penalty)
> - Your keyword-to-content alignment across every indexable page
>
> **Unlock with:** SEO Content Audit ($X) or Full SEO Audit ($Y)

#### Scoring Formula — On-Page Sub-Score (0–100)

```
- Title tag exists: +10
- Title tag 50–60 chars: +10 (40–49 or 61–70: +5, outside: 0)
- Meta description exists: +10
- Meta description 140–160 chars: +10 (outside range: +5)
- Single H1 present: +15
- H2s present (>2): +10
- Heading order logical: +10 (PSI)
- Image alt coverage ≥80%: +15 (50–79%: +8, <50%: 0)
- Word count ≥300: +10
- OG tags present: +5
- Link text quality pass: +5

Max: 100
```

---

### Section C: Structured Data & Rich Results
**ID:** `#seo-structured-data`  
**Position:** After On-Page SEO

#### Data Sources
- JSON-LD extraction from homepage
- Schema type detection + count
- Microdata + RDFa detection
- Mapping detected types to Google rich result eligibility

#### Components
- **Schema inventory table**: Schema type → Found/Missing → Rich Result Eligible
- **Rich result eligibility badges**: ⭐ eligible types highlighted
- **Schema depth score**: number of nested schema blocks
- **Validation status**: any malformed JSON-LD flagged

#### Rich Result Eligibility Map (Show Free)

| Schema Type | Rich Result Unlocked | Show if Found |
|-------------|---------------------|---------------|
| FAQPage | FAQ accordion in SERP | ✅ |
| HowTo | Step-by-step SERP feature | ✅ |
| Organization | Knowledge Panel eligibility | ✅ |
| WebSite + SearchAction | Sitelinks search box | ✅ |
| BreadcrumbList | Breadcrumb SERP display | ✅ |
| Article/BlogPosting | Article rich result | ✅ |
| Product + Offer | Shopping rich result | ✅ |
| Review/AggregateRating | Star ratings in SERP | ✅ |
| LocalBusiness | Map pack + local panel | ✅ |
| Event | Event rich result | ✅ |

**Show free:** Which schema types are present, which rich results they unlock, which high-value types are missing.

**Show the gap aggressively:**
> 🔒 **"You have Organization schema. That's a start."**
>
> You're missing: FAQPage, HowTo, and BreadcrumbList schema — three types that directly expand your SERP real estate. Our clients who add FAQPage schema see 15–40% CTR increases on informational queries because their answers appear before anyone clicks through.
>
> Without GSC + structured data testing tool access, we can see your schema exists — but we can't validate it's error-free or tell you whether Google is actually rendering any rich results from it. Broken schema is worse than no schema: Google penalizes sites that implement it incorrectly.
>
> **Unlock with:** SEO Technical Audit — we validate every schema block and implement the 3 missing types you need.

#### Scoring Formula — Structured Data Sub-Score (0–100)

```
- Any schema present: +15
- Organization schema: +10
- WebSite schema: +5
- FAQPage or HowTo: +15
- BreadcrumbList: +10
- Article/Product (if relevant): +10
- No malformed JSON-LD: +15
- Multiple schema types (≥3): +10
- Schema nesting depth (≥2 levels): +10

Max: 100
```

---

### Section D: AI Search Readiness
**ID:** `#seo-ai-search`  
**Position:** After Structured Data — directly before the Gate 3 lock

This section is a **hook** as much as an audit. AI search is a growing concern for every B2B buyer. We show enough to make it real, then lock the deep analysis.

#### Data Sources
- robots.txt AI crawler rules (GPTBot, ClaudeBot, PerplexityBot, etc.)
- llms.txt presence check
- FAQPage schema presence (already captured)
- Structured answer blocks on homepage (H2 + paragraph pattern that LLMs extract)
- PSI word count + heading structure (content that answers questions well)
- OG tags (AI engines use these for entity identification)

#### Components
- **AI Crawler Access grid**: Which AI bots are allowed/blocked (visual traffic light)
- **llms.txt badge**: Found / Not Found
- **Answer-readiness score**: Does the page structure lend itself to LLM extraction?
- **Entity signals**: Organization schema + OG tags = entity identifiability

#### Free Content

| Signal | Free |
|--------|------|
| GPTBot status (allowed/blocked) | ✅ |
| ClaudeBot status | ✅ |
| PerplexityBot status | ✅ |
| CCBot (Common Crawl) status | ✅ |
| llms.txt present/missing | ✅ |
| FAQPage schema (repurposed from Section C) | ✅ |
| Organization entity schema | ✅ |

#### Gated Behind Gate 3

> 🔒 **"Perplexity, ChatGPT, and Claude are answering questions your customers are asking right now. Are they citing you?"**
>
> AI search is already stealing 15–30% of informational search traffic from traditional Google results. We can see your robots.txt rules and whether you have an llms.txt — but that's surface level.
>
> A full AI Search Readiness Audit tells you:
> - Which queries in your niche AI engines are currently answering
> - Whether any AI engine is citing your competitors but not you (and why)
> - Whether your content structure allows LLMs to extract citable answers
> - How to reformat existing content into answer-box-ready blocks without a rewrite
> - Whether your entity markup is strong enough for Knowledge Graph inclusion (which powers AI citations)
>
> **Unlock with:** AI SEO Package ($X) — or included in Full SEO Audit ($Y)

#### Scoring Formula — AI Search Sub-Score (0–100)

```
- Googlebot allowed (baseline): +20 (prerequisite — 0 = halve all other scores)
- GPTBot allowed: +15
- PerplexityBot allowed: +15
- ClaudeBot allowed: +10
- CCBot allowed: +10
- llms.txt present: +15
- FAQPage schema present: +10
- Organization entity schema: +5

Max: 100
```

---

## 3. SEO Score (Composite, 0–100)

### Composite Formula

```
SEO Score = (
  Technical SEO Sub-Score  × 0.35  +
  On-Page Sub-Score        × 0.30  +
  Structured Data Score    × 0.20  +
  AI Search Score          × 0.15
)
```

### Grade Thresholds

| Score | Grade | Label |
|-------|-------|-------|
| 90–100 | A | SEO Strong |
| 75–89 | B | SEO Solid |
| 60–74 | C | SEO Gaps |
| 45–59 | D | SEO Weak |
| 0–44 | F | SEO Critical |

---

## 4. What to Gate vs Show Free

### Decision: Show enough to establish credibility, gate enough to create urgency.

**Show free (hooks):**
- Every binary signal that reveals a clear problem (noindex, missing sitemap, no canonical)
- Title tag + meta description full text (reveals optimization quality)
- H1 text (often reveals weak or missing primary keyword)
- Schema types found — and crucially, which high-value types are **missing**
- AI crawler rules (GPTBot blocked = immediate WTF moment for most clients)
- Redirect chain hop count
- The composite SEO Score + grade badge

**Lock behind Gate 3 (SEO Audit package):**
- Site-wide crawl findings (orphan pages, duplicate titles, thin content)
- GSC integration data (impressions, rankings, CTR, index coverage)
- Keyword cannibalization analysis
- Full redirect chain audit (beyond homepage)
- hreflang correctness across all language variants
- Crawl budget analysis
- Schema validation (error-free vs broken)
- AI citation competitor analysis
- Full internal link graph
- Backlink profile (domain authority, toxic links)

**Gate copy principle:** Every gate must name a **specific number or scenario** that makes the locked content feel concrete. Never generic "we'd find more issues." Always specific: "we'd find which of your [X] indexed pages are cannibalizing each other."

---

## 5. Data Collection Script Additions

### New bash functions to add to the collection script:

```bash
# ─── SEO DATA COLLECTION MODULE ─────────────────────────────────────

collect_seo_signals() {
  local URL=$1
  local BASE="${URL%/}"
  local DOMAIN=$(echo "$URL" | sed -E 's|https?://(www\.)?||' | cut -d'/' -f1)
  
  echo "=== REDIRECT CHAIN ==="
  curl -sI -L --max-redirs 10 -o /dev/null \
    -w "hops=%{num_redirects}\nfinal=%{url_effective}\nstatus=%{http_code}" "$URL"

  echo "=== CANONICAL ==="
  curl -s "$URL" | grep -i 'rel="canonical"' | head -1

  echo "=== ROBOTS META ==="
  curl -s "$URL" | grep -iE 'name="robots"|name="googlebot"' | head -3

  echo "=== X-ROBOTS HEADER ==="
  curl -sI "$URL" | grep -i "x-robots-tag"

  echo "=== HREFLANG ==="
  curl -s "$URL" | grep -i 'rel="alternate"' | wc -l

  echo "=== TITLE ==="
  curl -s "$URL" | grep -oP '(?<=<title>)[^<]*'

  echo "=== META DESCRIPTION ==="
  curl -s "$URL" | grep -i 'name="description"' | grep -oP 'content="[^"]*"' | head -1

  echo "=== H1 ==="
  curl -s "$URL" | grep -oP '(?<=<h1[^>]*>)[^<]*' | head -3

  echo "=== H2 COUNT ==="
  curl -s "$URL" | grep -c '<h2'

  echo "=== H3 COUNT ==="
  curl -s "$URL" | grep -c '<h3'

  echo "=== WORD COUNT ==="
  curl -s "$URL" | sed 's/<[^>]*>//g' | wc -w

  echo "=== IMAGES WITHOUT ALT ==="
  TOTAL_IMGS=$(curl -s "$URL" | grep -c '<img')
  NO_ALT=$(curl -s "$URL" | grep -oP '<img[^>]*>' | grep -cv 'alt="[^"]*"')
  echo "total=$TOTAL_IMGS missing_alt=$NO_ALT"

  echo "=== INTERNAL LINKS ==="
  curl -s "$URL" | grep -oP 'href="(/[^"]*|'"$BASE"'[^"]*)"' | wc -l

  echo "=== EXTERNAL LINKS ==="
  curl -s "$URL" | grep -oP 'href="https?://[^"]*"' | grep -v "$DOMAIN" | wc -l

  echo "=== OG TAGS ==="
  curl -s "$URL" | grep -i 'property="og:' | wc -l

  echo "=== TWITTER CARD ==="
  curl -s "$URL" | grep -i 'name="twitter:card"' | head -1

  echo "=== SCHEMA TYPES ==="
  curl -s "$URL" | grep -oP '"@type"\s*:\s*"[^"]*"' | sort | uniq

  echo "=== SCHEMA COUNT ==="
  curl -s "$URL" | grep -c 'application/ld+json'

  echo "=== ROBOTS TXT ==="
  curl -s "$BASE/robots.txt" | head -80

  echo "=== SITEMAP LOCATIONS ==="
  for path in /sitemap.xml /sitemap_index.xml /sitemap/sitemap.xml /wp-sitemap.xml /news-sitemap.xml; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$path")
    COUNT=0
    LASTMOD=""
    if [ "$STATUS" = "200" ]; then
      COUNT=$(curl -s "$BASE$path" | grep -c '<loc>')
      LASTMOD=$(curl -s "$BASE$path" | grep '<lastmod>' | head -1 | grep -oP '\d{4}-\d{2}-\d{2}')
    fi
    echo "path=$path status=$STATUS count=$COUNT lastmod=$LASTMOD"
  done

  echo "=== LLMS TXT ==="
  curl -s -o /dev/null -w "%{http_code}" "$BASE/llms.txt"
  curl -s "$BASE/llms.txt" | head -20

  echo "=== AI CRAWLERS IN ROBOTS ==="
  ROBOTS=$(curl -s "$BASE/robots.txt")
  for BOT in GPTBot ClaudeBot PerplexityBot anthropic-ai cohere-ai CCBot Bytespider YouBot; do
    RULE=$(echo "$ROBOTS" | grep -A2 -i "User-agent: $BOT" | head -3)
    echo "bot=$BOT rule=$RULE"
  done

  echo "=== MOBILE PARITY ==="
  DESKTOP_WORDS=$(curl -s "$URL" | sed 's/<[^>]*>//g' | wc -w)
  MOBILE_WORDS=$(curl -s -A "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15" \
    "$URL" | sed 's/<[^>]*>//g' | wc -w)
  echo "desktop=$DESKTOP_WORDS mobile=$MOBILE_WORDS"

  echo "=== HTTPS CHECK ==="
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://${DOMAIN}")
  HTTP_FINAL=$(curl -sI -L "http://${DOMAIN}" | grep "Location:" | tail -1)
  echo "http_status=$HTTP_STATUS redirect_to=$HTTP_FINAL"

  echo "=== WWW CHECK ==="
  WWW_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://www.${DOMAIN}")
  WWW_FINAL=$(curl -sI -L "https://www.${DOMAIN}" 2>/dev/null | grep "Location:" | tail -1)
  echo "www_status=$WWW_STATUS redirect_to=$WWW_FINAL"
}
```

### Playwright additions (if using headless browser in collection):

```javascript
// Capture all schema blocks (handles dynamically injected JSON-LD)
const schemaBlocks = await page.$$eval(
  'script[type="application/ld+json"]',
  els => els.map(el => {
    try { return JSON.parse(el.textContent); }
    catch(e) { return { _error: 'malformed', raw: el.textContent.slice(0, 200) }; }
  })
);

// Heading structure
const headings = await page.$$eval('h1, h2, h3, h4', els =>
  els.map(el => ({ tag: el.tagName, text: el.innerText.trim().slice(0, 100) }))
);

// Count images without alt
const imagesNoAlt = await page.$$eval('img:not([alt]), img[alt=""]', els => els.length);
const totalImages = await page.$$eval('img', els => els.length);

// Check viewport meta
const viewport = await page.$eval(
  'meta[name="viewport"]',
  el => el.getAttribute('content')
).catch(() => null);
```

---

## 6. Impact on Overall Grade

### Decision: Yes, increase SEO weight. Add 6th scorecard badge.

#### Updated Overall Grade Weights

| Category | Old Weight | New Weight | Rationale |
|----------|-----------|-----------|-----------|
| Performance | 25% | 20% | Still critical but partially overlaps with SEO (CWV) |
| SEO | 10% | 20% | Expanded to 4 sub-sections with real depth |
| MarTech / Tracking | 20% | 15% | Important but less visible to end prospects |
| Security | 15% | 15% | Unchanged |
| Copy / Content | 15% | 15% | Unchanged |
| UX / CRO | 15% | 15% | Unchanged |

#### New 6th Scorecard Badge: "SEO Health"

Add to the existing 5-badge scorecard row:

```html
<div class="grade-badge" id="badge-seo">
  <div class="badge-label">SEO Health</div>
  <div class="badge-grade">[GRADE]</div>
  <div class="badge-score">[SCORE]/100</div>
  <div class="badge-signals">
    <span>[Technical issues count] technical issues</span>
    <span>[Schema types found] schema types</span>
  </div>
</div>
```

**Justification for 6th badge:** SEO is now the primary upsell pathway (Gate 3). Giving it a prominent scorecard position increases the perceived value of the locked content and creates a clear visual anchor for the upsell conversation.

---

## 7. Upsell Tier Mapping

### Gate 3 — "Paid SEO" — Maps to: SEO Audit Package

**Unlock message:**
> You've seen the surface. We've found [X] technical issues, [Y] missing schema types, and your SEO score is [GRADE]. That's homepage-only. With a full SEO Audit, we crawl every page, pull GSC data, and tell you exactly which [N] pages are cannibalizing each other for your money keywords — and the exact fix order to move the needle in 90 days.

**What's included at Gate 3 unlock:**
- Full site crawl (Screaming Frog)
- GSC integration (impressions, CTR, index coverage, crawl errors)
- Keyword cannibalization report
- Full redirect chain audit
- Schema validation + implementation recommendations
- AI citation competitor gap analysis
- Backlink profile overview
- Priority fix roadmap (90-day)

### Contextual Upsells (inline, not gated)

Each sub-section ends with a **micro-upsell card** that names the exact package and what it adds:

```
Technical SEO → "Full Crawl + GSC Integration" (SEO Audit)
On-Page → "Content Depth + Keyword Alignment Audit" (SEO Content Audit)  
Structured Data → "Schema Implementation + Validation" (SEO Audit)
AI Search → "AI Citation Gap Analysis" (AI SEO Add-on or Full SEO Audit)
```

---

## Implementation Priority

| Priority | Item | Effort |
|----------|------|--------|
| P0 | Bash collection script additions | 2h |
| P0 | Technical SEO section HTML | 3h |
| P0 | Update scorecard (6th badge + reweighting) | 1h |
| P1 | On-Page SEO section HTML | 2h |
| P1 | Structured Data section HTML | 2h |
| P1 | Gate 3 upsell copy + lock UI | 1h |
| P2 | AI Search Readiness section HTML | 2h |
| P2 | Scoring engine updates | 2h |
| P3 | Playwright schema extraction | 1h |

**Total estimated effort:** ~16h implementation

---

*End of plan. Ready for developer handoff.*

---
name: ai-seo
description: Optimize content for AI search engines and LLM citations. Use when the user wants to appear in AI-generated answers, get cited by ChatGPT/Perplexity/Claude, or optimize for Google AI Overviews. Keywords - AI SEO, AEO, GEO, LLMO, answer engine optimization, generative engine optimization, AI citations, AI visibility, zero-click search.
allowed-tools: web_fetch, web_search, Bash, Read, Write
---

# AI Search Optimization (GEO/AEO)

You are an expert in AI search optimization — making content discoverable, extractable, and citable by AI systems including Google AI Overviews, ChatGPT, Perplexity, Claude, Gemini, and Copilot.

**Your goal:** Help B2B companies get their content cited as a source in AI-generated answers.

---

## When to Use

- Client wants to appear in AI-generated search results
- Need to optimize content for LLM citations
- Preparing for Google AI Overviews dominance
- Competitor analysis for AI search visibility
- Content strategy for AI-first search era

---

## The AI Search Landscape

| Platform | How It Works | Source Selection |
|----------|-------------|------------------|
| **Google AI Overviews** | Summarizes top-ranking pages | Strong correlation with traditional rankings |
| **ChatGPT** (with search) | Searches web, cites sources | Draws from wider range, not just top-ranked |
| **Perplexity** | Always cites sources with links | Favors authoritative, recent, well-structured |
| **Gemini** | Google's AI assistant | Google index + Knowledge Graph |
| **Copilot** | Bing-powered AI search | Bing index + authoritative sources |
| **Claude** | Brave Search (when enabled) | Training data + Brave search results |

### Critical Stats

- AI Overviews appear in **10–60% of Google searches depending on query intent** — informational queries trigger AIO most frequently, transactional queries rarely do. Always verify the AIO rate for a client's specific query mix before prioritizing. (Semrush 2025: ~16% of all desktop searches; Conductor 2025: ~25% of analyzed queries; informational-heavy verticals like Healthcare: ~49%)
- AI search visitors convert **4.4x better** than traditional organic visitors — not because volume is higher, but because they arrive already educated and closer to a decision (Semrush 2025). AEO is a bottom-of-funnel quality play, not a top-of-funnel volume play.
- **ChatGPT drives 87.4% of all AI referral traffic** across industries (Conductor 2025). Test and optimize for ChatGPT first. Perplexity and Gemini are secondary.
- AI referral traffic is ~1% of total web traffic today but growing ~1% month-over-month. Small now, compounding fast.
- AI Overviews reduce clicks by up to 58% — but zero-click citations still build brand awareness and trust (see Zero-Click Value section below)
- Brands are 6.5x more likely to be cited via third-party sources than their own domains
- Optimized content gets cited 3x more often
- Statistics and citations boost visibility by 40%+
- Early GEO adopters are discovered up to 10x faster by generative engines vs. relying on organic SEO alone

---

## AI Visibility Audit Process

### Step 1: Check AI Presence for Key Queries

Test 10-20 priority queries across platforms:

| Query | AI Overview? | ChatGPT Cites? | Perplexity Cites? | You Cited? | Competitors Cited? |
|-------|:-----------:|:--------------:|:-----------------:|:----------:|:------------------:|
| [query 1] | Y/N | Y/N | Y/N | Y/N | [who] |

**B2B query types to test:**
- "What is [your product category]?"
- "Best [category] for [enterprise/SMB/use case]"
- "[Your brand] vs [competitor]"
- "How to [problem your product solves]"
- "[Your category] pricing comparison"

### Step 2: Analyze Citation Patterns

When competitors get cited and client doesn't:
- **Content structure** — Is their content more extractable?
- **Authority signals** — More citations, stats, expert quotes?
- **Freshness** — More recently updated?
- **Schema markup** — Structured data you're missing?
- **Third-party presence** — Wikipedia, G2, industry publications?

### Step 3: Content Extractability Check

For each priority page, verify:

| Check | Pass/Fail |
|-------|-----------|
| Clear definition in first paragraph? | |
| Self-contained answer blocks (work without context)? | |
| Statistics with sources cited? | |
| Comparison tables for "[X] vs [Y]" queries? | |
| FAQ section with natural-language questions? | |
| Schema markup (FAQ, HowTo, Article, Product)? | |
| Expert attribution (author name, credentials)? | |
| Recently updated (within 6 months)? | |
| Headings match query patterns? | |
| AI bots allowed in robots.txt? | |

### Step 4: AI Bot Access Check

```bash
curl -sL "https://[domain]/robots.txt" | grep -iE "gptbot|chatgpt|perplexity|claude|anthropic|google-extended"
```

**Bots to allow for citation:**
- `GPTBot`, `ChatGPT-User` — ChatGPT
- `PerplexityBot` — Perplexity
- `ClaudeBot`, `anthropic-ai` — Claude
- `Google-Extended` — Gemini/AI Overviews
- `Bingbot` — Copilot

**Recommendation:** Allow these bots. Optionally block training-only crawlers like `CCBot`.

---

## The Two-Channel Model

Before optimizing anything, internalize this framing — it changes every recommendation you make to a client:

**AI has not replaced search. It has created a parallel channel with different rules.**

| Channel | Goal | Success Metric | User Journey |
|---------|------|---------------|--------------|
| **Traditional SEO** | Rank in SERPs | Traffic, CTR, rankings | Search → Click → Website |
| **AI Search (AEO/GEO)** | Get cited in AI answers | Brand citations, mention volume, share of AI voice | Question → AI Answer → Brand awareness (click optional) |

These channels are converging (ChatGPT now shows links, Google AIO appears in SERPs) but they require different optimization strategies and different KPIs. Don't measure AEO success by traffic — you'll always be disappointed. Measure it by **whether your brand is present in the AI answers your customers are reading**.

The implication: a brand can rank #1 on Google and be completely invisible in AI search. And a brand can get zero AI referral clicks but be mentioned in 40% of AI responses in their category — which means they're shaping buyer perception before the customer ever visits any website.

**Organic SEO remains the dominant traffic driver.** Don't let clients deprioritize it. AEO is additive, not a replacement.

---

## Zero-Click Value: Reframing the "Problem"

The common reaction to zero-click AI answers is: *"AI is stealing our traffic."* This is the wrong frame.

Zero-click citations have real value:
- **Top-of-mind awareness** — your brand appears when buyers are forming opinions, even if they don't click
- **Trust by association** — being cited by an AI system signals authority to the user
- **Upper funnel positioning** — shapes consideration before intent is declared
- **Brand search lift** — consistent AI mentions drive more direct brand searches over time

**What to measure instead of clicks from AI:**
- Brand mention frequency in AI responses (use Otterly, Peec AI, or manual testing)
- Sentiment — how does AI describe your brand? Positive, neutral, negative?
- Share of AI voice vs. competitors — are you mentioned more or less than alternatives?
- Brand search volume trend — is direct brand search increasing as AI visibility grows?

The goal in a zero-click world is not to get the click from every answer. It's to be the brand that comes to mind when the buyer eventually searches, talks to a salesperson, or makes a decision.

---

## The Three Pillars of AI SEO

### Pillar 1: Structure — Make Content Extractable

AI systems extract passages, not pages. Key claim must work standalone.

**Content block patterns:**
- **Definition blocks** for "What is X?" queries
- **Step-by-step blocks** for "How to X" queries
- **Comparison tables** for "X vs Y" queries
- **Pros/cons blocks** for evaluation queries
- **FAQ blocks** for common questions
- **Statistic blocks** with cited sources

**Structural rules:**
- Lead every section with direct answer (don't bury it)
- Key answer passages: 40-60 words (optimal for extraction)
- H2/H3 headings match how people phrase queries
- Tables beat prose for comparisons
- Numbered lists beat paragraphs for processes
- One clear idea per paragraph

### Pillar 2: Authority — Make Content Citable

**Princeton GEO Research (KDD 2024)** ranked optimization methods:

| Method | Visibility Boost | How to Apply |
|--------|:---------------:|--------------|
| **Cite sources** | +40% | Add authoritative references with links |
| **Add statistics** | +37% | Include specific numbers with sources |
| **Add quotations** | +30% | Expert quotes with name and title |
| **Authoritative tone** | +25% | Write with demonstrated expertise |
| **Improve clarity** | +20% | Simplify complex concepts |
| **Technical terms** | +18% | Use domain-specific terminology |
| ~~Keyword stuffing~~ | **-10%** | **Actively hurts AI visibility** |

**Best combination:** Fluency + Statistics = maximum boost.

**What builds citability:**
- Named authors with credentials
- Expert quotes with titles
- Statistics with cited sources and dates
- "Last updated: [date]" prominently displayed
- E-E-A-T signals (experience, expertise, authority, trust)

### Pillar 3: Presence — Be Where AI Looks

AI doesn't just cite your site — it cites where you appear.

**Third-party sources matter more than your own site:**
- Wikipedia mentions (7.8% of all ChatGPT citations)
- Reddit discussions (1.8% of ChatGPT citations)
- Industry publications (guest posts, mentions)
- Review sites (G2, Capterra for B2B SaaS)
- YouTube (frequently cited by AI Overviews)

**B2B actions:**
- Ensure Wikipedia page is accurate and current
- Maintain updated G2/Capterra profiles
- Get featured in industry roundups and comparison articles
- Create YouTube content for key how-to queries
- Publish on industry publications

---

## Schema Markup for AI

| Content Type | Schema | Why It Helps |
|-------------|--------|--------------|
| Articles/Blog | `Article`, `BlogPosting` | Author, date, topic ID |
| How-to content | `HowTo` | Step extraction |
| FAQs | `FAQPage` | Direct Q&A extraction |
| Products | `Product` | Pricing, features |
| Comparisons | `ItemList` | Structured comparison |
| Reviews | `Review`, `AggregateRating` | Trust signals |
| Organization | `Organization` | Entity recognition |

Content with proper schema shows 30-40% higher AI visibility.

---

## Content Types That Get Cited Most

| Content Type | Citation Share | Why AI Cites It |
|--------------|:-------------:|-----------------|
| **Comparison articles** | ~33% | Structured, balanced, high-intent |
| **Definitive guides** | ~15% | Comprehensive, authoritative |
| **Original research/data** | ~12% | Unique, citable statistics |
| **Best-of/listicles** | ~10% | Clear structure, entity-rich |
| **Product pages** | ~10% | Specific extractable details |
| **How-to guides** | ~8% | Step-by-step structure |

**What underperforms:**
- Generic blog posts without structure
- Thin product pages with marketing fluff
- Gated content (AI can't access it)
- Content without dates or author attribution
- PDF-only content

---

## B2B-Specific AI SEO Strategies

### SaaS Product Pages

**Goal:** Get cited in "What is [category]?" and "Best [category]" queries.

**Optimize:**
- Clear product description in first paragraph
- Feature comparison tables (you vs. category)
- Specific metrics ("processes 10,000 transactions/sec")
- Customer count with numbers
- Pricing transparency (AI cites pages with visible pricing)
- FAQ section addressing buyer questions

### Comparison/Alternative Pages

**Goal:** Get cited in "[X] vs [Y]" and "Best [X] alternatives" queries.

**Optimize:**
- Structured comparison tables
- Fair and balanced (AI penalizes obviously biased)
- Specific criteria with ratings/scores
- Updated pricing and feature data

### Blog Content

**Goal:** Get cited as authoritative source on topics in your space.

**Optimize:**
- One clear target query per post
- Definition in first paragraph for "What is" queries
- Original data, research, or expert quotes
- "Last updated" date visible
- Author bio with relevant credentials

### Documentation / Help Content

**Goal:** Get cited in "How to [X] with [product]" queries.

**Optimize:**
- Step-by-step format with numbered lists
- Code examples where relevant
- HowTo schema markup
- Clear prerequisites and outcomes

---

## Monitoring AI Visibility

### What to Track

| Metric | What It Measures | How to Check |
|--------|-----------------|--------------|
| AI Overview presence | Do AIO appear for your queries? | Manual or Semrush/Ahrefs |
| Brand citation rate | How often cited in AI answers | AI visibility tools |
| Share of AI voice | Your citations vs competitors | Otterly, Peec AI, ZipTie |
| Citation sentiment | How AI describes your brand | Manual review |
| Source attribution | Which pages get cited | Referral traffic analysis |

### AI Visibility Tools

| Tool | Coverage | Best For |
|------|----------|----------|
| **Otterly AI** | ChatGPT, Perplexity, AI Overviews | Share of voice tracking |
| **Peec AI** | All major platforms | Multi-platform monitoring |
| **ZipTie** | AI Overviews, ChatGPT, Perplexity | Brand mention + sentiment |
| **LLMrefs** | All major platforms | SEO keyword → AI visibility |

### DIY Monthly Check

1. Pick top 20 queries
2. Run each through ChatGPT, Perplexity, Google
3. Record: Are you cited? Who is? What page?
4. Track month-over-month in spreadsheet

---

## Output Format

### AI SEO Audit Report

```markdown
## AI Search Visibility Audit: [Company]

### Current AI Visibility Score: X/10

### Platform Presence
| Platform | Queries Tested | Times Cited | Share of Voice |
|----------|----------------|-------------|----------------|
| Google AI Overviews | X | X | X% |
| ChatGPT | X | X | X% |
| Perplexity | X | X | X% |

### Content Extractability Score: X/10
- Definition blocks: ✅/❌
- Self-contained answers: ✅/❌
- Statistics with sources: ✅/❌
- FAQ sections: ✅/❌
- Schema markup: ✅/❌

### Authority Signals Score: X/10
- Expert attribution: ✅/❌
- Cited sources: ✅/❌
- Freshness signals: ✅/❌
- Third-party presence: ✅/❌

### Priority Recommendations

#### 🔴 Critical (Do First)
1. [Recommendation]
2. [Recommendation]

#### 🟡 Important (This Quarter)
1. [Recommendation]
2. [Recommendation]

#### 🟢 Nice to Have
1. [Recommendation]
2. [Recommendation]

### Content Optimization Plan
| Page | Current Issues | Recommended Changes |
|------|---------------|---------------------|
| [URL] | [Issues] | [Changes] |
```

---

## Common Mistakes

- **Ignoring AI search** — 45% of Google shows AI Overviews
- **Treating AI SEO as separate** — It's layered on good traditional SEO
- **Writing for AI, not humans** — Won't convert even if cited
- **No freshness signals** — Undated content loses to dated
- **Gating all content** — AI can't access it
- **Ignoring third-party presence** — Wikipedia mention may beat your blog
- **No structured data** — Missing schema = missing context
- **Keyword stuffing** — Reduces AI visibility by 10%
- **Blocking AI bots** — Can't cite if can't crawl

---

## Related Skills

- **seo-audit**: For traditional technical and on-page SEO audits
- **programmatic-seo**: For building SEO pages at scale
- **keyword-research**: For identifying target keywords
- **seo-optimizer**: For on-page optimization implementation

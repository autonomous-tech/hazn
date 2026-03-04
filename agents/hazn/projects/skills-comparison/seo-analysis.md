# SEO Skills Comparison: HAZN vs MARKETINGSKILLS

**Analysis Date:** January 2025  
**Purpose:** Identify gaps, strengths, and learning opportunities

---

## 1. Overlap Analysis

### Direct Overlaps

| Area | HAZN | MARKETINGSKILLS | Notes |
|------|------|-----------------|-------|
| **Technical SEO Audits** | `seo-audit` | `seo-audit` | Both cover technical SEO. Theirs explicitly includes "on-page" — ours may need to verify scope. |
| **Structured Data** | `seo-optimizer` (includes structured data) | `schema-markup` | We bundle it with optimization; they have dedicated focus. Their specialization likely goes deeper. |

### Partial Overlaps

- **Content Strategy**: Our `keyword-research` includes content strategy elements. They don't have an explicit equivalent, but their `programmatic-seo` handles content at scale differently.

- **Entity SEO**: Our `entity-knowledge-graph` touches structured data concepts that relate to their `schema-markup`, but we focus on knowledge graph/entity relationships while they focus on implementation.

---

## 2. Their Advantages (What We're Missing)

### 🔴 Critical Gap: AI Search Optimization (`ai-seo`)

**What it is:** Optimization for AI-generated search results — Answer Engine Optimization (AEO), Generative Engine Optimization (GEO), LLM Optimization (LLMO).

**Why this matters:**
- ChatGPT, Perplexity, Claude, Google AI Overviews are reshaping search
- Users increasingly get answers without clicking through to sites
- Being cited by LLMs requires different optimization than traditional SEO
- This is the **fastest-growing SEO frontier**

**Concrete techniques we lack:**
- Structuring content for LLM citation (clear, quotable statements)
- Optimizing for "Sources" sections in AI responses
- Tracking AI citation metrics
- Building authority signals LLMs recognize

**Impact:** High. This gap will widen as AI search grows.

---

### 🔴 Critical Gap: Programmatic SEO (`programmatic-seo`)

**What it is:** Creating thousands of pages at scale using templates + data (e.g., "[Tool] vs [Competitor]" pages, location pages, feature comparison pages).

**Why this matters:**
- Captures long-tail traffic at scale
- Powers "vs", "alternatives to", "best X for Y" rankings
- Can generate 10,000+ pages from structured data
- High ROI for SaaS and marketplace sites

**Concrete techniques we lack:**
- Template-based page generation systems
- Data pipeline integration for dynamic SEO content
- Quality control for scaled content
- Internal linking architectures for massive page counts

**Impact:** High for B2B/SaaS clients. This is how Zapier, G2, Capterra dominate.

---

### 🟡 Moderate Gap: Competitor/Alternative Pages (`competitor-alternatives`)

**What it is:** Dedicated skill for "[Brand] alternatives" and "vs" comparison pages.

**Why this matters:**
- Bottom-of-funnel traffic with high conversion intent
- Captures competitor's brand searches
- Essential for SaaS and B2B
- Often combined with programmatic SEO

**Note:** This could be considered a sub-specialty of `programmatic-seo`, but having it explicit shows strategic awareness.

---

### 🟡 Moderate Gap: Schema Markup Depth

**What it is:** Their dedicated `schema-markup` skill vs our bundled approach in `seo-optimizer`.

**Concern:** A dedicated skill likely means:
- Deeper expertise in complex schema types
- Better handling of nested/advanced markup (HowTo, FAQ, Product, Review, Organization)
- Custom schema for specific industries
- Schema validation and debugging expertise

**Our approach:** Bundled into `seo-optimizer` — may be sufficient but could lack depth.

---

## 3. Our Advantages (What They Don't Have)

### 🟢 Major Advantage: Entity & Knowledge Graph SEO (`entity-knowledge-graph`)

**What it is:** Optimizing for Google's Knowledge Graph, building entity authority, and establishing topical expertise.

**Why this matters:**
- Knowledge Graph presence = massive trust signal
- Entity optimization impacts rankings across all queries related to that entity
- E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) directly ties to entity signals
- **Foundational for their `ai-seo` to even work** — LLMs rely on entity understanding

**Concrete techniques they lack:**
- Entity disambiguation and consolidation
- Knowledge panel optimization
- Building entity associations (person ↔ organization ↔ topics)
- Wikidata/Wikipedia optimization strategies
- Topical authority mapping

**Strategic insight:** Entity SEO is *upstream* of AI SEO. Strong entity signals make AI citation more likely. We have the foundation; they have the application layer.

---

### 🟢 Major Advantage: Framework-Specific SEO (`seo-optimizer`)

**What it is:** Specialized optimization for Next.js including metadata, structured data, and Core Web Vitals.

**Why this matters:**
- Next.js is dominant in modern web development
- Framework-specific knowledge = better implementation
- Core Web Vitals directly impact rankings
- Technical debt in SPAs requires specialized approaches

**Concrete techniques they lack:**
- Next.js metadata API optimization
- React hydration impact on CWV
- ISR/SSG/SSR SEO tradeoffs
- App Router vs Pages Router SEO differences
- Image/font optimization specific to Next.js

**Impact:** High for B2B/SaaS clients on modern stacks. Most serious sites are Next.js now.

---

### 🟢 Moderate Advantage: Keyword Research + Content Strategy (`keyword-research`)

**What it is:** Research-driven content planning, not just keyword lists.

**Note:** They don't have an explicit keyword research skill. This could mean:
- They assume it's implicit in other skills
- They outsource this to clients
- Gap in their offering

**Our strength:** Connecting research → strategy → content planning is a complete workflow.

---

## 4. Learning Opportunities (What We Should Adopt)

### Priority 1: Create `ai-seo` Skill

**Action:** Build a dedicated AI search optimization skill.

**Should include:**
- AEO (Answer Engine Optimization) principles
- Content structuring for LLM citation
- Perplexity/ChatGPT/Claude optimization
- Google AI Overview optimization
- Citation tracking methodology
- Brand mention monitoring in AI responses

**Implementation approach:**
- Research current AEO best practices
- Study how Perplexity selects sources
- Analyze patterns in Google AI Overview citations
- Create checklist for AI-optimized content
- Build into content workflow

**Timeline:** High priority — this gap grows daily.

---

### Priority 2: Create `programmatic-seo` Skill

**Action:** Build scaled page generation capability.

**Should include:**
- Template design for SEO pages
- Data source integration patterns
- Quality thresholds for generated content
- Internal linking for large page sets
- Cannibalization prevention
- Indexation management at scale

**Implementation approach:**
- Study programmatic SEO leaders (Zapier, Wise, Nomad List)
- Build template library for common patterns
- Create data pipeline integrations
- Develop quality scoring system

**Timeline:** Medium priority — valuable but more situational.

---

### Priority 3: Expand Schema Depth

**Action:** Enhance `seo-optimizer` or create dedicated `schema-markup` skill.

**Should include:**
- Full Schema.org type coverage
- Industry-specific schema patterns
- Nested/complex schema architectures
- Validation and testing workflows
- Schema monitoring and maintenance

**Timeline:** Lower priority — we have coverage, need depth.

---

## 5. Our Strengths (Where We're Better Positioned)

### Strategic Positioning

| Dimension | HAZN Position | Why It Matters |
|-----------|---------------|----------------|
| **Entity Foundation** | Strong | Entity SEO is prerequisite for AI SEO. We can build on this. |
| **Technical Depth** | Strong (Next.js specific) | Modern stack expertise = better implementation |
| **Research → Strategy Flow** | Complete | End-to-end from research to content plan |
| **E-E-A-T Optimization** | Strong via entity work | Trust signals that persist across algorithm changes |

### Where We Win Head-to-Head

1. **Clients on Next.js** — Our framework expertise is unmatched
2. **Brand/Entity Building** — Our Knowledge Graph work creates lasting authority
3. **Technical SEO + Implementation** — We can audit AND fix in the same stack
4. **Long-term SEO Strategy** — Entity work compounds; programmatic is more transactional

### Complementary Positioning

**Interesting observation:** Our skills and theirs are more complementary than competitive.

- **They focus on:** Scale, AI adaptation, competitive capture
- **We focus on:** Foundation, authority, technical excellence

**Ideal combined stack would be:**
1. Our entity + keyword research (foundation)
2. Our technical audit + optimization (infrastructure)  
3. Their programmatic SEO (scale)
4. Their AI SEO (emerging channels)
5. Combined schema depth

---

## Summary & Recommendations

### Immediate Actions

1. **Add `ai-seo` skill** — Critical gap, high growth area
2. **Study their `programmatic-seo`** — Valuable for certain clients
3. **Document our entity SEO depth** — This is genuinely differentiated

### Strategic Position

**We're positioned as:** Technical SEO + Authority Building specialists
**They're positioned as:** Scale SEO + Emerging Channel specialists

**Our moat:** Entity/Knowledge Graph expertise is rare and foundational
**Their moat:** AI SEO early-mover advantage

### Collaboration Potential

These skill sets would be powerful combined. If this is a potential partner or acquisition target, the overlap is minimal and complementary coverage is high.

---

*Analysis complete. Key takeaway: Prioritize AI SEO skill development — it's the most significant gap with the fastest-growing importance.*

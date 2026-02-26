# Hazn Skills Reference

Hazn includes 25 specialized skills covering the full marketing website lifecycle. Skills are domain expertise encoded as detailed instructions that agents follow.

---

## Skill Index

| Category | Skill | Purpose |
|----------|-------|---------|
| **Strategy** | `b2b-marketing-ux` | UX strategy, page architecture, conversion design |
| | `b2b-ux-reference` | Deep reference for UX decisions, buyer psychology, trust patterns |
| **Content** | `b2b-website-copywriter` | Conversion copy for B2B services websites |
| | `landing-page-copywriter` | High-converting landing page copy (PAS, AIDA, StoryBrand) |
| | `seo-blog-writer` | SEO + AEO + GEO optimized blog posts |
| | `email-sequence` | B2B email automation (welcome, trial, nurture sequences) |
| | `cold-email` | B2B outbound prospecting and follow-up sequences |
| | `copy-editing` | Copy improvement using Seven Sweeps framework |
| **Design** | `b2b-wireframe` | Mid-fidelity HTML wireframes for layout validation |
| | `frontend-design` | Visual aesthetics, avoiding generic AI design |
| | `ui-audit` | UX/UI audits based on design principles |
| **Development** | `payload-nextjs-stack` | Next.js + Payload CMS + Tailwind implementation |
| **SEO** | `keyword-research` | Keyword discovery, intent analysis, content opportunity mapping |
| | `seo-audit` | Technical SEO audits |
| | `seo-optimizer` | On-page and technical SEO implementation |
| | `entity-knowledge-graph` | Entity optimization for AI citation (GEO) |
| | `ai-seo` | AI search optimization (LLM citations, AI Overviews, GEO/AEO) |
| | `programmatic-seo` | Scaled page generation with Next.js + Payload CMS |
| **CRO** | `ab-test-setup` | Experiment design with PostHog integration |
| | `analytics-tracking` | GA4 + PostHog measurement setup for Next.js |
| **Audits** | `conversion-audit` | CRO/conversion audit with branded reports |
| | `website-audit` | Comprehensive multi-dimensional site audits |
| | `analytics-audit` | GA4 property audit, site tracking inspection, attribution analysis |
| | `analytics-audit-martech` | MarTech stack assessment, attribution architecture, roadmap |
| | `analytics-audit-client-report` | Branded HTML client report from audit findings |

---

## Skill Details

### b2b-marketing-ux

**Purpose:** UX strategy, page architecture, and conversion design for B2B services websites.

**When to use:**
- Building a new marketing website for an agency/consultancy
- Redesigning an existing B2B services site
- Defining page structure and content hierarchy
- Planning conversion flows

**Key outputs:**
- Page blueprints (homepage, services, packages, case studies)
- Content hierarchy recommendations
- Trust signal placement
- Responsive design requirements

**Pairs with:** `b2b-wireframe` (downstream), `payload-nextjs-stack` (downstream), `b2b-ux-reference` (deep reference)

---

### b2b-ux-reference

**Purpose:** Comprehensive UX reference covering buyer psychology, trust frameworks, conversion optimization, forms UX, accessibility, and measurement.

**When to use:**
- Need deeper grounding on any UX principle
- Handling complex buyer personas
- Optimizing conversion flows
- Making difficult UX tradeoffs

**Key topics:**
- B2B buyer psychology
- Trust-building patterns
- Form UX best practices
- Mobile UX for B2B
- Accessibility requirements
- Measurement frameworks

**Note:** This is a reference skill — use alongside `b2b-marketing-ux` for deeper context.

---

### b2b-website-copywriter

**Purpose:** Write high-converting copy for B2B services websites.

**When to use:**
- Writing homepage copy
- Creating services page content
- Crafting case study narratives
- Writing packages/pricing page copy
- Developing about page content

**Key outputs:**
- Headlines and value propositions
- Section-by-section copy
- CTA copy
- Social proof framing
- Full page copy documents

**Frameworks:** PAS (Problem-Agitate-Solution), AIDA, StoryBrand, 4U Formula

---

### landing-page-copywriter

**Purpose:** Conversion-focused copy for standalone landing pages.

**When to use:**
- Single landing pages for campaigns
- Lead generation pages
- Product launch pages
- Event registration pages

**Key outputs:**
- Hero copy (headline, subhead, CTA)
- Benefit sections
- Social proof blocks
- FAQ content
- Final CTA sections

---

### seo-blog-writer

**Purpose:** Write blog posts optimized for SEO, Answer Engines (AEO), and Generative Engines (GEO).

**When to use:**
- Creating blog content from keyword research
- Writing thought leadership articles
- Building topical authority
- Content that needs to be cited by AI

**Key outputs:**
- 1,500-3,000 word articles
- Complete frontmatter (meta, schema, entities)
- TL;DR blocks for AI extraction
- FAQ sections with schema
- Internal/external link suggestions

**Pairs with:** `keyword-research` (upstream), `entity-knowledge-graph` (entity optimization)

---

### b2b-wireframe

**Purpose:** Create mid-fidelity HTML wireframes for layout validation before development.

**When to use:**
- After UX strategy, before code
- Getting stakeholder approval on layouts
- Validating responsive behavior
- Reviewing content hierarchy visually

**Key outputs:**
- Standalone HTML wireframe files
- Responsive layouts (mobile, tablet, desktop)
- Section manifest for production handoff
- Realistic placeholder content

**Pairs with:** `b2b-marketing-ux` (upstream), `payload-nextjs-stack` (downstream)

---

### frontend-design

**Purpose:** Create distinctive, production-grade frontend interfaces with high design quality.

**When to use:**
- Avoiding generic AI aesthetics
- Setting visual direction
- Making typography and color decisions
- Creating memorable interfaces

**Key principles:**
- Distinctive over generic
- Typography as personality
- Purposeful color usage
- Intentional whitespace
- Subtle, meaningful animation

---

### ui-audit

**Purpose:** Automated UI audits evaluating interfaces against proven UX principles.

**When to use:**
- Reviewing existing designs
- Quality checking new work
- Identifying UX issues
- Prioritizing design improvements

**Evaluation areas:**
- Visual hierarchy
- Accessibility
- Cognitive load
- Navigation clarity
- Consistency

---

### payload-nextjs-stack

**Purpose:** Production code for marketing websites on Payload CMS + Next.js + Tailwind.

**When to use:**
- Building from approved wireframes
- Creating CMS content models
- Implementing page components
- Setting up SEO and performance

**Key outputs:**
- Payload collection configs
- React section components
- Dynamic page rendering
- SEO metadata setup
- Image optimization

**Pairs with:** `b2b-wireframe` (consumes section manifest), `b2b-marketing-ux` (UX decisions)

---

### keyword-research

**Purpose:** SEO keyword research and content strategy.

**When to use:**
- Starting a content strategy
- Finding blog topics
- Identifying search opportunities
- Competitive content analysis

**Key outputs:**
- Keyword lists with metrics
- Search intent classification
- Content opportunities
- Questions (PAA data)
- Topical authority maps (optional)

**Output format:** JSON at `./outputs/keyword-research.json`

---

### seo-audit

**Purpose:** Technical SEO audits for existing websites.

**When to use:**
- Auditing client sites
- Pre-launch SEO reviews
- Identifying technical issues
- Competitive SEO analysis

**Key outputs:**
- Meta tag analysis
- Heading structure review
- Core Web Vitals assessment
- Schema markup evaluation
- Actionable recommendations

---

### seo-optimizer

**Purpose:** Implement technical SEO optimizations in Next.js sites.

**When to use:**
- Adding meta tags
- Implementing structured data
- Optimizing Core Web Vitals
- Setting up sitemaps and robots.txt

**Key outputs:**
- Metadata configurations
- JSON-LD schema markup
- Image optimization setup
- Font loading optimization

---

### entity-knowledge-graph

**Purpose:** Optimize content for entity clarity, knowledge graph alignment, and AI engine citation.

**When to use:**
- Improving AI citation likelihood
- Entity markup implementation
- Knowledge graph presence
- GEO optimization

**Key outputs:**
- Entity maps
- Schema markup for entities
- Content recommendations for citability
- Same-as link suggestions

---

### ai-seo

**Purpose:** AI search optimization for LLM citations, AI Overviews, and generative engine visibility.

**When to use:**
- Optimizing content for AI citation
- Getting into Google AI Overviews
- GEO (Generative Engine Optimization)
- AEO (Answer Engine Optimization)
- Configuring bot access for AI crawlers

**Key outputs:**
- Content extractability improvements
- AI-friendly content structure
- Bot access configuration (robots.txt, meta tags)
- Citation-optimized formatting
- GEO/AEO audit reports

**Pairs with:** `entity-knowledge-graph` (entity optimization), `seo-blog-writer` (content creation)

---

### programmatic-seo

**Purpose:** Scaled page generation using Next.js and Payload CMS patterns.

**When to use:**
- Creating hundreds/thousands of SEO pages
- Template-based page scaling
- Dynamic route generation
- Location/service/category page matrices

**Key outputs:**
- Next.js dynamic route patterns
- Payload CMS collection configs for scale
- Template architecture
- Data pipeline setup
- Internal linking strategies

**Pairs with:** `payload-nextjs-stack` (implementation), `keyword-research` (opportunity identification)

---

### ab-test-setup

**Purpose:** Experiment design and A/B test implementation with PostHog.

**When to use:**
- Setting up conversion experiments
- Testing landing page variations
- Validating copy or design changes
- Building experiment frameworks

**Key outputs:**
- Hypothesis documentation (problem, hypothesis, metric, success criteria)
- PostHog feature flag setup
- Sample size calculations
- Test duration estimates
- Statistical analysis interpretation
- Experiment reports

**Pairs with:** `analytics-tracking` (measurement), `conversion-audit` (identifying what to test)

---

### analytics-tracking

**Purpose:** Measurement setup for marketing websites using GA4 and PostHog.

**When to use:**
- Setting up analytics on new sites
- Implementing event tracking
- Next.js App Router integration
- GDPR-compliant consent management

**Key outputs:**
- GA4 + PostHog dual-stack configuration
- Next.js App Router integration code
- Consent-aware loading patterns
- Custom event tracking
- Conversion tracking setup
- UTM parameter handling

**Pairs with:** `ab-test-setup` (experiments), `payload-nextjs-stack` (implementation)

---

### email-sequence

**Purpose:** B2B email automation sequences for nurturing and conversion.

**When to use:**
- Building welcome sequences
- Creating trial onboarding flows
- Designing lead nurture sequences
- Re-engagement campaigns

**Key outputs:**
- Sequence architecture (timing, triggers)
- Email copy for each touchpoint
- ESP implementation guides (ConvertKit, ActiveCampaign, etc.)
- Segmentation recommendations
- Deliverability best practices

**Pairs with:** `b2b-website-copywriter` (voice consistency), `cold-email` (outbound sequences)

---

### cold-email

**Purpose:** B2B outbound email prospecting sequences.

**When to use:**
- Building outbound sales sequences
- Cold prospecting campaigns
- Follow-up sequence design
- Domain/sender reputation management

**Key outputs:**
- Prospecting frameworks (BASHO, Challenger, etc.)
- Multi-step follow-up sequences
- Subject line variations
- CAN-SPAM/GDPR compliance checklist
- Domain warmup guidance
- Deliverability optimization

**Pairs with:** `email-sequence` (automation patterns), `b2b-website-copywriter` (voice)

---

### copy-editing

**Purpose:** Systematic copy improvement using the Seven Sweeps framework.

**When to use:**
- Polishing draft copy
- Improving existing website content
- Tightening marketing messages
- B2B-specific copy optimization

**Key outputs:**
- Edited copy with tracked changes
- Seven Sweeps analysis (clarity, concision, flow, tone, proof, action, scan)
- B2B-specific improvements
- Before/after comparisons

**Pairs with:** `b2b-website-copywriter` (initial drafts), `landing-page-copywriter` (landing page polish)

---

### conversion-audit

**Purpose:** Comprehensive conversion/CRO audits with branded HTML reports.

**When to use:**
- Auditing client landing pages
- Sales call preparation
- Delivering value-add reports
- Identifying conversion issues

**Key outputs:**
- Branded HTML audit report
- Scores for Copy, SEO, Design
- Before/after recommendations
- Implementation roadmap
- CVR projections

---

### website-audit

**Purpose:** Comprehensive multi-dimensional website audits combining copy, SEO, visual, and CRO analysis.

**When to use:**
- Full site audits (not just landing pages)
- Multi-page analysis
- Comprehensive client deliverables

**Key outputs:**
- Combined audit report
- Section-by-section analysis
- Prioritized recommendations

---

### analytics-audit

**Purpose:** GA4 property audit covering tracking implementation, data quality, attribution, and site-level tag inspection.

**When to use:**
- Auditing GA4 setup on existing Shopify/ecommerce sites
- Assessing tracking quality and data gaps
- Analyzing traffic sources, conversion paths, and attribution
- Pre-engagement data discovery for clients

**Key outputs:**
- GA4 data collection via Python scripts (events, conversions, sources, pages)
- GSC query/page performance data
- Site HTML inspection for tracking tags
- Markdown audit report (sections A-J, Q)

**Prerequisites:** Python 3.10+, `google-analytics-data`, `google-auth-oauthlib`, GA4 property access

**Pairs with:** `analytics-audit-martech` (downstream), `analytics-audit-client-report` (downstream), `analytics-tracking` (complementary — tracking setup vs audit)

---

### analytics-audit-martech

**Purpose:** MarTech stack assessment, attribution architecture analysis, and optimization roadmap.

**When to use:**
- Evaluating full marketing technology stack
- Attribution model analysis and recommendations
- MarTech consolidation planning
- Post-GA4-audit strategic recommendations

**Key outputs:**
- MarTech stack inventory (sections K-P)
- Attribution architecture assessment
- Tag management evaluation
- Privacy/consent compliance review
- Optimization roadmap with priorities

**Pairs with:** `analytics-audit` (upstream data), `analytics-audit-client-report` (downstream)

---

### analytics-audit-client-report

**Purpose:** Generate branded HTML client reports from analytics audit findings.

**When to use:**
- Converting markdown audit into client-ready deliverable
- Sales call preparation
- Client presentation material
- Stakeholder-friendly audit summary

**Key outputs:**
- Standalone HTML report with embedded CSS
- Executive summary with key metrics
- Visual data cards and finding highlights
- Prioritized recommendations with effort/impact
- Opportunity sizing estimates

**Pairs with:** `analytics-audit` (upstream), `analytics-audit-martech` (upstream)

---

## Skill Workflow

Skills are designed to chain together:

```
Strategy & Research
├── b2b-marketing-ux (page blueprints)
├── keyword-research (content opportunities)
└── b2b-ux-reference (deep context)
        ↓
Content & Design
├── b2b-website-copywriter (page copy)
├── landing-page-copywriter (landing pages)
├── copy-editing (polish & improve)
├── b2b-wireframe (layout validation)
└── frontend-design (visual direction)
        ↓
Development
├── payload-nextjs-stack (production code)
├── seo-optimizer (technical SEO)
├── analytics-tracking (measurement setup)
└── programmatic-seo (scaled pages)
        ↓
Content & Growth
├── seo-blog-writer (blog posts)
├── entity-knowledge-graph (AI citation)
├── ai-seo (AI search optimization)
├── email-sequence (nurture automation)
└── cold-email (outbound sequences)
        ↓
Analysis & Optimization
├── conversion-audit (CRO analysis)
├── ab-test-setup (experiments)
├── website-audit (full audit)
├── seo-audit (technical SEO)
├── ui-audit (UX review)
├── analytics-audit (GA4/GSC data audit)
├── analytics-audit-martech (MarTech assessment)
└── analytics-audit-client-report (HTML client report)
```

---

## Adding Custom Skills

To add a custom skill:

1. Create a folder in `skills/your-skill-name/`
2. Add `SKILL.md` with frontmatter and instructions
3. Optionally add `references/` for supporting docs
4. Optionally add `assets/` for templates

Skill frontmatter format:

```yaml
---
name: your-skill-name
description: "One-line description for skill matching"
---

# Skill Title

[Detailed instructions...]
```

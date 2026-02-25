# Hazn Workflows Reference

Hazn includes 7 structured workflows for common marketing website tasks.

## Workflow Index

| Workflow | Trigger | Purpose | Duration |
|----------|---------|---------|----------|
| **Website** | `/hazn-website` | Full marketing website build | 1-4 weeks |
| **Audit** | `/hazn-audit` | Comprehensive site analysis | 2-4 hours |
| **Blog** | `/hazn-content` | SEO blog content pipeline | 2-3 hours setup, 1-2 hours per article |
| **Landing** | `/hazn-landing` | Quick single landing page | 4-8 hours |
| **Email** | `/hazn-email` | Email campaign design | 2-6 hours |
| **Optimize** | `/hazn-optimize` | Post-launch optimization | Ongoing 2-4 week cycles |
| **Analytics Audit** | `/hazn-analytics-audit` | GA4/GSC MarTech & Attribution audit | 3-6 hours |

---

## Website Workflow

**File:** `workflows/website.yaml`  
**Trigger:** `/hazn-website`

The complete path from strategy to deployed website.

### Phases

| Phase | Agent | Command | Required |
|-------|-------|---------|----------|
| 1. Strategy | Strategist | `/hazn-strategy` | ✓ |
| 2. UX Architecture | UX Architect | `/hazn-ux` | ✓ |
| 3. Copy | Copywriter | `/hazn-copy` | Optional |
| 4. Wireframes | Wireframer | `/hazn-wireframe` | Optional |
| 5. Development | Developer | `/hazn-dev` | ✓ |
| 6. Analytics Setup | Developer | `/hazn-analytics` | ✓ |
| 7. SEO + AI SEO | SEO Specialist | `/hazn-seo` | ✓ |
| 8. Content | Content Writer | `/hazn-content` | Optional |

### Checkpoints

- **After Strategy:** Review `strategy.md` before proceeding
- **After Wireframes:** Get stakeholder approval before development
- **After Development:** Review in browser before SEO optimization
- **After Analytics:** Verify tracking is capturing key events

### Duration Estimates

| Speed | Description | Time |
|-------|-------------|------|
| Quick | Skip wireframes, minimal copy | 2-3 days |
| Standard | Full process | 1-2 weeks |
| Thorough | Extensive copy, multiple revisions | 3-4 weeks |

---

## Audit Workflow

**File:** `workflows/audit.yaml`  
**Trigger:** `/hazn-audit`

Comprehensive website analysis with actionable recommendations.

### Phases

1. **Scope Definition**
   - Confirm URL to audit
   - Select audit types (conversion, copy, visual, SEO, AI visibility)
   - Gather analytics access if available

2. **Analysis**
   - Conversion audit
   - Copy audit
   - Visual/UX audit
   - SEO audit
   - AI Visibility audit (GEO/AEO readiness)

3. **Synthesis**
   - Aggregate scores
   - Prioritize by impact/effort
   - Identify quick wins
   - Generate test recommendations for A/B testing

4. **Report Generation**
   - Branded HTML report
   - Summary markdown
   - Test hypothesis document

### Deliverables

- `audit-report.html` — Full branded report
- `audit-summary.md` — Quick reference
- `test-recommendations.md` — A/B test hypotheses
- Prioritized fix list
- Before/after recommendations
- Implementation roadmap
- AI visibility scorecard

### Duration

2-4 hours depending on site complexity.

---

## Blog Content Workflow

**File:** `workflows/blog.yaml`  
**Trigger:** `/hazn-content` or `/hazn-blog`

SEO-optimized blog content creation pipeline.

### Phases

1. **Keyword Research**
   - Identify seed topics from strategy
   - Discover long-tail opportunities
   - Map keywords to intent

2. **Content Planning**
   - Create content calendar
   - Define pillar/cluster structure
   - Assign priorities

3. **Content Creation** (per article)
   - Research topic depth
   - Write draft (1,500-3,000 words)
   - Optimize for primary keyword
   - Add internal links
   - Create meta tags
   - Add FAQ section with schema

4. **SEO Polish**
   - Verify keyword placement
   - Check header structure
   - Add structured data
   - Internal linking pass

### Output Format

```markdown
---
title: "{title}"
description: "{meta_description}"
slug: "{slug}"
publishedAt: "{date}"
keywords: [{keywords}]
---

{article content}
```

### Duration

- Initial setup: 2-3 hours
- Per article: 1-2 hours

---

## Landing Page Workflow

**File:** `workflows/landing.yaml`  
**Trigger:** `/hazn-landing`

Fast path for single landing pages.

### Phases

| Phase | Duration | Actions |
|-------|----------|---------|
| Brief | 15 min | Offer, audience, desired action, brand guidelines |
| Structure | 30 min | Define 5-7 sections, outline content needs |
| Copy | 1-2 hours | Headlines, body, CTAs, social proof |
| Build | 2-4 hours | Single page component, responsive, form handling |

### Skip for Speed

- Wireframes (go straight to code)
- Extensive keyword research
- Full strategy document

### Duration

4-8 hours total.

---

## Email Campaign Workflow

**File:** `workflows/email.yaml`  
**Trigger:** `/hazn-email`

Design and plan email sequences for lead nurturing and conversion.

### Phases

| Phase | Duration | Actions |
|-------|----------|---------|
| Brief | 15-30 min | Define goals, audience segments, existing assets |
| Strategy | 1-2 hours | Sequence type, email count, timing, triggers |
| Copy | 2-4 hours | Subject lines, body copy, CTAs for each email |
| Optimization Plan | 30 min | A/B test variants, success metrics, iteration plan |

### Sequence Types

- **Welcome Series** — Onboard new subscribers, introduce brand
- **Lead Nurture** — Move prospects through funnel with value content
- **Cold Outbound** — Prospecting sequences for sales teams

### Checkpoints

- **After Strategy:** Confirm sequence structure before writing
- **After Copy:** Review all emails before marking ready for activation

### Deliverables

- `email-sequence.md` — Full sequence with all emails
- Subject line variants for A/B testing
- Send timing recommendations
- Performance tracking plan

### Duration

2-6 hours depending on sequence length.

---

## Post-Launch Optimization Workflow

**File:** `workflows/optimize.yaml`  
**Trigger:** `/hazn-optimize`

Continuous improvement through data-driven A/B testing.

### Phases

| Phase | Duration | Actions |
|-------|----------|---------|
| Baseline Review | 1-2 hours | Analyze current metrics, identify weak points |
| Hypothesis | 1 hour | Form testable hypotheses based on data |
| A/B Test Setup | 1-2 hours | Design variants, define success criteria |
| Implementation | 2-4 hours | Build test variants, configure testing tool |
| Analysis | 1-2 hours | Evaluate results, document learnings |

### Test Elements

- **Headlines** — Value props, emotional triggers, specificity
- **CTAs** — Copy, color, placement, urgency
- **Forms** — Field count, layout, progressive disclosure
- **Social Proof** — Testimonial placement, logos, stats
- **Layouts** — Section order, visual hierarchy, content density

### Checkpoints

- **After Hypothesis:** Confirm test priorities align with business goals
- **Before Implementation:** Approve test designs and success metrics

### Deliverables

- `optimization-log.md` — Running record of all tests
- Test variant designs
- Statistical analysis reports
- Winner implementation notes

### Duration

Ongoing 2-4 week cycles. Each cycle includes one or more tests.

---

## Analytics Audit Workflow

**File:** `workflows/analytics-audit.yaml`
**Trigger:** `/hazn-analytics-audit`

Full MarTech & Attribution audit pipeline for sites with GA4 and optional GSC access.

### Prerequisites
- Python 3.10+ with venv
- `pip install google-analytics-data google-auth-oauthlib google-api-python-client`
- GA4 property ID with Data API access
- Optional: Google Search Console site URL

### Phases

| Phase | Agent | Duration | Actions |
|-------|-------|----------|---------|
| 1. Setup | — | 5 min | Parse inputs, verify Python deps, create output directory |
| 2. Data Collection | Analytics Inspector | 30-60 min | Run GA4 collector, GSC collector, site HTML inspection (parallel) |
| 3. Analysis | Analytics Report Writer | 2-3 hours | Write sections A-Q using collected data + skills |
| 4. Adversarial Review | Analytics Adversary | 30-60 min | Red-team review of claims, math, data accuracy |
| 5. Client Report | Analytics Client Reporter | 30-60 min | Generate branded HTML report from markdown |

### Deliverables
- `.hazn/outputs/analytics-audit/<domain>-audit.md` — Full markdown audit
- `.hazn/outputs/analytics-audit/client-report/index.html` — Branded HTML report
- `.hazn/outputs/analytics-audit/data/` — Raw GA4/GSC JSON data

### Duration
3-6 hours depending on site complexity and data volume.

---

## Running Workflows

### Start a Workflow

In your AI IDE (Claude Code, Cursor, Windsurf):

```
/hazn-website
```

The workflow will guide you through each phase.

### Skip Phases

If you have existing assets:

```
I already have a strategy document. Let's skip to UX.
```

### Get Help

At any point:

```
/hazn-help
```

This shows your current state and recommends next steps.

---

## Customizing Workflows

Workflow definitions are in `.hazn/workflows/`. To customize:

1. Edit the workflow YAML file
2. Add, remove, or reorder phases
3. Modify dependencies between phases

### Workflow YAML Structure

```yaml
name: workflow-name
description: What this workflow does
trigger: /command

phases:
  - id: phase-id
    name: Phase Name
    agent: agent-name
    command: /agent-command
    depends_on: [previous-phase-ids]
    outputs:
      - path/to/output
    required: true|false
    note: Optional notes

checkpoints:
  - after: phase-id
    message: "Review instructions"

estimated_duration:
  quick: "timeframe"
  standard: "timeframe"
```

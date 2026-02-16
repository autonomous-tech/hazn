# Hazn Workflows Reference

Hazn includes 4 structured workflows for common marketing website tasks.

## Workflow Index

| Workflow | Trigger | Purpose | Duration |
|----------|---------|---------|----------|
| **Website** | `/hazn-website` | Full marketing website build | 1-4 weeks |
| **Audit** | `/hazn-audit` | Comprehensive site analysis | 2-4 hours |
| **Blog** | `/hazn-content` | SEO blog content pipeline | 2-3 hours setup, 1-2 hours per article |
| **Landing** | `/hazn-landing` | Quick single landing page | 4-8 hours |

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
| 6. SEO | SEO Specialist | `/hazn-seo` | ✓ |
| 7. Content | Content Writer | `/hazn-content` | Optional |

### Checkpoints

- **After Strategy:** Review `strategy.md` before proceeding
- **After Wireframes:** Get stakeholder approval before development
- **After Development:** Review in browser before SEO optimization

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
   - Select audit types (conversion, copy, visual, SEO)
   - Gather analytics access if available

2. **Analysis**
   - Conversion audit
   - Copy audit
   - Visual/UX audit
   - SEO audit

3. **Synthesis**
   - Aggregate scores
   - Prioritize by impact/effort
   - Identify quick wins

4. **Report Generation**
   - Branded HTML report
   - Summary markdown

### Deliverables

- `audit-report.html` — Full branded report
- `audit-summary.md` — Quick reference
- Prioritized fix list
- Before/after recommendations
- Implementation roadmap

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

# WORKFLOWS.md - Hazn Playbooks

## `/website` — Full Website Build

**Duration:** 1-4 weeks

### Before Starting — Always Ask
> What type of organisation is this?
> - **B2B / commercial** → use `b2b-marketing-ux` skill
> - **NGO / association / political org / international institution** → use `ngo-web-design` skill
> - **E-commerce** → use ecommerce skills

This determines the entire strategy, IA, tone, and compliance requirements.

### Phases

```
1. STRATEGY (required)
   └─→ Spawn: Strategist
   └─→ Output: strategy.md
   └─→ CHECKPOINT: Review strategy before proceeding

2. UX ARCHITECTURE (required)
   └─→ Spawn: UX Architect
   └─→ Input: strategy.md
   └─→ Output: ux-blueprint.md

3. COPY + WIREFRAMES (parallel, optional)
   ├─→ Spawn: Copywriter
   │   └─→ Input: strategy.md, ux-blueprint.md
   │   └─→ Output: copy/*.md
   └─→ Spawn: Wireframer
       └─→ Input: ux-blueprint.md
       └─→ Output: wireframes/*.html
       └─→ CHECKPOINT: Stakeholder approval

4. DEVELOPMENT (required)
   └─→ Ask: WordPress or Next.js?
       ├── WordPress → Spawn: WordPress Developer (sub-agents/wordpress-developer.md)
       │   └─→ Stack: GeneratePress Premium + Meta Box + Filter Everything (see skill)
       │   └─→ Needs: HestiaCP SSH access + domain
       └── Next.js → Spawn: Developer (sub-agents/developer.md)
           └─→ Stack: Next.js + Payload CMS + Tailwind
   └─→ Input: ux-blueprint.md, copy/, wireframes/
   └─→ CHECKPOINT: Review in browser

4.5. QA TESTING (required — no exceptions)
   └─→ Spawn: QA Tester (sub-agents/qa-tester.md)
   └─→ Input: Built site URL, ux-blueprint.md, dev-progress.md
   └─→ Output: qa-report.md (PASS / CONDITIONAL PASS / FAIL)
   └─→ If FAIL → Return to Developer with qa-report.md, do NOT advance
   └─→ If CONDITIONAL PASS → Developer fixes minor issues, re-test
   └─→ If PASS → Advance to SEO
   └─→ ⚠️ Do NOT advance to SEO with a FAIL status. Ever.

5. SEO OPTIMIZATION (required)
   └─→ Spawn: SEO Specialist
   └─→ Input: Built site URL
   └─→ Output: seo-checklist.md, applied optimizations
   └─→ Includes: Yoast config (WP) or metadata (Next.js), schema, AI SEO

6. CONTENT (optional, post-launch)
   └─→ Spawn: Content Writer
   └─→ Ongoing blog pipeline
   └─→ WordPress: output imports directly via WP-CLI (see wordpress-generatepress skill)

7. A/B TEST PLANNING (optional, post-launch)
   └─→ Spawn: Conversion Specialist
   └─→ Input: Analytics baseline, conversion goals
   └─→ Output: ab-test-plan.md
   └─→ Define: Headlines, CTAs, layouts to test
```

---

## `/audit` — Site Audit

**Duration:** 2-4 hours

### Phases

```
1. SCOPE
   └─→ Confirm URL, audit types, conversion goals
   └─→ (You handle this, no sub-agent needed)

2. ANALYSIS (parallel)
   └─→ Spawn: Auditor with parallel tracks:
       ├── Conversion audit
       ├── Copy audit
       ├── Visual/UX audit
       ├── SEO audit
       └── AI Visibility audit (LLM discoverability, entity presence)

3. ANALYTICS REVIEW
   └─→ Review GA4/analytics data (if access provided)
   └─→ Identify: Traffic patterns, drop-off points, conversion rates
   └─→ Output: analytics-insights.md

4. SYNTHESIS
   └─→ Aggregate scores, prioritize by impact
   └─→ Identify quick wins
   └─→ Generate test recommendations (what to A/B test)

5. REPORT
   └─→ Output: audit-report.html, audit-summary.md
   └─→ Includes: test-recommendations.md (prioritized A/B test ideas)
```

---

## `/content` — Blog Pipeline

**Duration:** 1-2 hours per article

### Phases

```
1. RESEARCH
   └─→ Spawn: SEO Specialist (keyword research mode)
   └─→ Output: keyword-research.md

2. PLANNING
   └─→ Create content calendar
   └─→ Define pillar/cluster structure
   └─→ Output: content-calendar.md

3. WRITING (per article)
   └─→ Spawn: Content Writer
   └─→ Input: keyword target, topic brief
   └─→ Output: content/blog/{slug}.md

4. OPTIMIZATION
   └─→ Spawn: SEO Specialist
   └─→ Polish, internal linking, schema
```

---

## `/landing` — Quick Landing Page

**Duration:** 4-8 hours

### Before Starting
Ask: **Public or private?**
- Public → deploy to `landing-pages` repo → `pages.autonomoustech.ca/{client}/`
- Private → deploy to `autonomous-proposals` repo → `docs.autonomoustech.ca/{client}/`

See `TOOLS.md` for repo details.

### Phases

```
1. BRIEF (15 min)
   └─→ Gather: Offer, audience, desired action, brand, public/private
   └─→ (You handle this)

2. STRUCTURE (30 min)
   └─→ Spawn: UX Architect
   └─→ Output: landing-blueprint.md

3. COPY (1-2 hours)
   └─→ Spawn: Copywriter
   └─→ Output: copy/landing.md

4. BUILD (2-4 hours)
   └─→ Spawn: Developer
   └─→ Output: Single page component

5. DEPLOY
   └─→ Copy to correct repo under {client}/ folder
   └─→ Add share button if private (autonomous-proposals)
   └─→ Push to main → auto-deploys
```

**Note:** Skip wireframes for speed. Use `/website` for anything larger.

---

## `/email` — Email Campaign Design

**Duration:** 2-6 hours per sequence

### Sequence Types

```
WELCOME SEQUENCE (new subscribers)
├── Email 1: Welcome + value prop
├── Email 2: Quick win / resource
├── Email 3: Story / credibility
├── Email 4: Case study
└── Email 5: Soft CTA

LEAD NURTURE (MQL to SQL)
├── Problem-aware content
├── Solution education
├── Social proof / case studies
├── Objection handling
└── Demo/call invitation

COLD OUTBOUND (prospect acquisition)
├── Pattern interrupt opener
├── Value-first follow-up
├── Social proof drop
└── Breakup email
```

### Phases

```
1. BRIEF
   └─→ Gather: Goal, audience segment, existing sequences, brand voice
   └─→ (You handle this)
   └─→ CHECKPOINT: Confirm sequence type and goals

2. STRATEGY
   └─→ Spawn: Strategist (email mode)
   └─→ Map: Buyer journey stage, pain points, triggers
   └─→ Output: email-strategy.md

3. COPY (per sequence)
   └─→ Spawn: Email Specialist
   └─→ Input: email-strategy.md, brand voice
   └─→ Output: email-sequences/{sequence-name}/*.md
   └─→ CHECKPOINT: Review emails before handoff

4. OPTIMIZATION PLAN
   └─→ Define: Subject line variants, CTA tests
   └─→ Output: email-test-plan.md
```

---

## `/optimize` — Post-Launch Optimization

**Duration:** Ongoing (2-4 week cycles)

### Phases

```
1. BASELINE REVIEW
   └─→ Review: Current analytics, conversion rates, user behavior
   └─→ Identify: Underperforming pages, drop-off points
   └─→ Output: baseline-metrics.md
   └─→ CHECKPOINT: Align on optimization priorities

2. HYPOTHESIS GENERATION
   └─→ Based on: Audit findings, analytics data, best practices
   └─→ Prioritize: Impact × Confidence × Ease
   └─→ Output: optimization-hypotheses.md

3. A/B TEST SETUP (per test)
   └─→ Define: Control vs. variant
   └─→ Test elements:
       ├── Headlines / value props
       ├── CTA copy and placement
       ├── Form length / fields
       ├── Social proof placement
       └── Page layout / above-fold content
   └─→ Output: tests/{test-name}.md (hypothesis, variants, success metric)
   └─→ CHECKPOINT: Approve test before implementation

4. IMPLEMENTATION
   └─→ Spawn: Developer (if code changes needed)
   └─→ Or: Configure in A/B testing tool
   └─→ Set: Traffic split, duration, statistical significance target

5. ANALYSIS & ITERATION
   └─→ Review: Test results after statistical significance reached
   └─→ Document: Winner, learnings, next steps
   └─→ Output: test-results/{test-name}.md
   └─→ Feed learnings into next hypothesis cycle
```

### Optimization Cycle Cadence

```
Week 1: Review + Hypothesis
Week 2-3: Run tests
Week 4: Analyze + Plan next cycle
→ Repeat
```

---

---

## `/case-study` — Case Study & Portfolio Builder

**Duration:** 1-3 hours  
**Skill:** `case-study`  
**Outputs:** `index.html` (sales page) + `case-study.json` (Wagtail CMS import)

### Before Starting
Ask: **Public or private?**
- Public (share freely, send to prospects) → deploy to `landing-pages` repo → `pages.autonomoustech.ca/audits/{client-slug}-case-study/`
- Private (confidential client, auth-gated) → deploy to `autonomous-proposals` repo → `docs.autonomoustech.ca/{client-slug}/`

### Phases

```
1. INTERVIEW (required — never skip)
   └─→ Spawn: Case Study Builder
   └─→ 5 question groups, one at a time
   └─→ Groups: Project Basics, Problem, Solution, Outcome, Permissions
   └─→ Wait for full answers before writing anything

2. IMAGE GENERATION
   └─→ Imagen 3 via Vertex AI (3 images: hero, solution, outcome)
   └─→ Style: Editorial Warmth v2 aesthetic — parchment/midnight tones
   └─→ No people, no text, 16:9

3. DUAL OUTPUT GENERATION (parallel)
   ├── index.html — Standalone sales page
   │   └─→ Design: Editorial Warmth v2 (Fraunces + DM Sans + JetBrains Mono)
   │   └─→ Sections: Nav → Hero → Metrics Strip → Challenge → Before/After SVG
   │              → Solution → Outcome → Testimonial → Footer CTA
   │   └─→ All CSS inline, no external deps except Google Fonts
   └── case-study.json — Wagtail StreamField import
       └─→ Model: case_studies.CaseStudy
       └─→ Sections: challenge_section, solution_section, outcome_section

4. QUALITY CHECK
   └─→ Copy: no em-dashes, JTBD framing, real metrics or flagged placeholders
   └─→ HTML: correct CSS tokens, typography, squiggles, responsive
   └─→ JSON: URL-safe slug, lowercase tags, no em-dashes
   └─→ CHECKPOINT: confirm all placeholders — ask creator to fill gaps now

5. DEPLOY
   └─→ Copy files to correct repo (per public/private decision above)
   └─→ Push to main → auto-deploys
   └─→ Add share button if deploying to autonomous-proposals
```

### Output Location

```
projects/{client-slug}-case-study/
├── index.html
├── case-study.json
└── images/
    ├── hero.png
    ├── solution.png
    ├── outcome.png
    └── client-logo.svg (if provided)
```

---

## Ad-Hoc Sub-Agent Use

Not everything needs a workflow. Spawn individual agents for:
- Quick copy review → Copywriter
- SEO check on existing page → SEO Specialist
- Content ideas → Content Writer
- UX feedback → UX Architect
- Email sequence review → Email Specialist
- Conversion analysis → Conversion Specialist

Just spawn with a clear, focused task.

---

## `/analytics-audit` — Full MarTech & Attribution Audit

**Duration:** 3-6 hours  
**Requires:** GA4 property ID, GSC access (optional)

### Phases
```
1. SETUP — parse URL, GA4 property, create output dir
2. DATA COLLECTION (parallel) — GA4 + GSC + site inspection
   └─→ Agent: analytics-inspector
   └─→ Scripts: ga4_collector.py, gsc_collector.py
3. ANALYSIS — analytics-report-writer + skills: analytics-audit, analytics-audit-martech
   └─→ Output: .hazn/outputs/analytics-audit/<domain>-audit.md
4. ADVERSARIAL REVIEW — analytics-adversary challenges findings
5. CLIENT REPORT — analytics-client-reporter generates HTML report
   └─→ Output: .hazn/outputs/analytics-audit/client-report/index.html
```

---

## `/analytics-teaser` — Zero-Access Prospect Teaser Report

**Duration:** 30-60 minutes  
**Requires:** Just a URL — no GA4/GSC access needed

### Phases
```
1. SETUP — parse URL, normalize, create output dir
2. DATA COLLECTION (parallel) — PageSpeed + public data + Playwright screenshots
   └─→ Agents: analytics-inspector, analytics-teaser-collector
   └─→ Scripts: pagespeed_collector.py, teaser_collector.py
3. REPORT GENERATION — analytics-teaser-writer + analytics-teaser-report skill
   └─→ Output: .hazn/outputs/analytics-teaser/<domain>/index.html
4. VERIFICATION — 3 viewport checks, content verification
```

---

## `/ngo` — NGO / Association / Institutional Website

**Duration:** 3 days – 4 weeks  
**Skill:** ngo-web-design (mandatory — NOT b2b-marketing-ux)

### Phases
```
1. STRATEGY — mission, audience hierarchy, action hierarchy
2. COMPLIANCE — Impressum, DSGVO, BITV 2.0, cookie consent
3. UX — transparency-first IA (not conversion funnels)
4. COPY (optional) — trustworthy, warm, not startup-speak
5. WIREFRAME (optional)
6. DEV — WordPress or static, must include all legal pages
7. ACCESSIBILITY AUDIT — WCAG 2.1 AA mandatory
8. SEO — discoverability, schema, RSS for journalists
```

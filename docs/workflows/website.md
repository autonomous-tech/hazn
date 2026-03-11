# Full Website Build

> Complete B2B/commercial marketing website from strategy to deployment — strategy → UX → copy → wireframes → dev → SEO.

## When to Use

- Building a new marketing site for a B2B service, agency, SaaS, or productized service business
- Rebuilding an existing commercial site from foundations
- Client needs a full content strategy, not just a template dropped into code

**NOT for:**
- NGOs, associations, political orgs, or international institutions → use `/hazn-ngo` instead
- Single landing pages (no strategy needed) → use `/hazn-landing`
- E-commerce sites

## Requirements

- Client brief: what the company does, primary audience, conversion goal, pages needed
- Brand assets if available (logo, colors, fonts) — not required to start
- Hosting environment decision: Vercel (Next.js) or HestiaCP (WordPress)
- Stack decision: Next.js + Payload CMS vs WordPress + GeneratePress

## How It Works

### Phase 0 — Organisation Type Check (~5 minutes)
**Agent:** Strategist  
Confirm this is a B2B/commercial project. If NGO/institutional, redirect to `/hazn-ngo` immediately.

### Phase 1 — Strategy (~1–3 hours)
**Agent:** Strategist  
Discovery Q&A, competitive analysis, ICP definition, positioning, conversion path.  
**Output:** `.hazn/outputs/strategy.md`

> ⏸ **CHECKPOINT** — Review strategy before proceeding.

### Phase 2 — UX Architecture (~1–2 hours)
**Agent:** UX Architect  
Consumes `strategy.md`. Produces site map, page blueprints, section briefs, CTA hierarchy, user flows.  
**Output:** `.hazn/outputs/ux-blueprint.md`

### Phase 3 — Copy + Wireframes (parallel, ~2–4 hours each)
**Agent (Copy):** Copywriter — consumes `strategy.md` + `ux-blueprint.md`  
**Agent (Wireframe):** Wireframer — consumes `ux-blueprint.md` + copy if available  
Both tracks run independently. Copy is not required before wireframes start.  
**Output:** `.hazn/outputs/copy/{page}.md`, `.hazn/outputs/wireframes/{page}.html`

> ⏸ **CHECKPOINT** — Stakeholder approval of wireframes before development starts.

### Phase 4 — Development (~1–5 days)
**Agent:** Developer  
Consumes `ux-blueprint.md` + `copy/` + `wireframes/` (optional). Builds full site.  
Stack selection: Next.js + Payload CMS or WordPress + GeneratePress per `strategy.md`.  
**Output:** Built site at staging URL, `dev-progress.md`

### Phase 5 — QA Gate (~1–2 hours)
**Agent:** QA Tester  
Screenshots at desktop (1280px) and mobile (375px). Scores mobile responsiveness (30%), CTA visibility (25%), content completeness (20%), visual quality (15%), technical basics (10%).  
- 90+ → PASS  
- 75–89 → CONDITIONAL PASS  
- Below 75 → FAIL → back to Developer (max 3 cycles)  
**Output:** `qa-report.md`

> ⏸ **CHECKPOINT** — QA must PASS before SEO runs. No exceptions.

### Phase 6 — SEO Optimization (~2–4 hours)
**Agent:** SEO Specialist  
Runs only after QA PASS. Meta tags, structured data, sitemap, robots.txt, Core Web Vitals, entity optimization for AI visibility.  
**Output:** `seo-checklist.md`, applied optimizations to codebase

### Phase 7 — Blog Content (ongoing, optional)
**Agent:** Content Writer  
Keyword-targeted articles (1,500–3,000 words) seeded from `strategy.md` + `seo-checklist.md`.  
**Output:** `content/blog/{slug}.md`

## HITL Checkpoints

| Checkpoint | Why it matters / risk of skipping |
|---|---|
| After strategy | Strategy lock-in — copy, UX, and dev all derive from this. Wrong positioning = wasted weeks. |
| After wireframes | Layout decisions that are cheap to change in HTML become expensive in code. Stakeholders who say "I didn't visualise it that way" after dev is done cause rewrites. |
| After QA PASS | SEO applied to a broken mobile layout or incomplete content is wasted effort. Structured data on unfinalised copy must be redone. |

## Caveats & Gotchas

- Developer needs to know the stack choice (Next.js vs WordPress) before starting — don't let this be decided mid-build.
- QA uses the browser tool to take screenshots — this requires a live URL (localhost or staging). A filesystem path won't work.
- If QA fails 3 cycles, escalate to the user — do not keep looping.
- Copy and wireframes are marked optional in the workflow YAML but significantly improve development quality. Skip them only when explicitly pressed for speed.
- Payload CMS 3.x is Next.js-native — don't mix Payload 2.x patterns into a 3.x project.
- WordPress track uses GeneratePress Premium ($59/yr) — confirm the license is available before starting the WordPress path.

## Outputs

```
projects/{client}/
├── state.json
├── strategy.md
├── ux-blueprint.md
├── copy/
│   ├── homepage.md
│   ├── services.md
│   └── about.md
├── wireframes/
│   ├── homepage.html
│   ├── services.html
│   └── index.html
├── dev-progress.md
├── qa-report.md
└── seo-checklist.md
content/
└── blog/
    └── {slug}.md
```

## Example Trigger

```
/hazn-website
Client: Acme Consulting
What they do: B2B sales training for SaaS companies
Goal: Inbound demo requests
Tech preference: Next.js
```

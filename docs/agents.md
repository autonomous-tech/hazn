# Hazn Agents Reference

This document describes all 15 agents. Use it when deciding which agent to spawn in ambiguous situations.

---

## Strategist

**Trigger:** `/hazn:strategy`  
**Used in:** website, ngo-website, blog (implicitly), landing (skipped)  
**Skills:** `b2b-marketing-ux`, `b2b-ux-reference` (B2B track); `ngo-web-design` (NGO track)

**When to spawn:** Project kickoff for any website build. Also spawn when the current project folder has no `strategy.md` and another agent is blocked waiting for it.

**Input required:**
- Organisation type (B2B/commercial vs NGO/institutional)
- What the org does (one sentence)
- Primary audience (role, company size or org type)
- Primary conversion/action goal
- Competitors (optional, will ask)

**Output:** `.hazn/outputs/strategy.md` containing: positioning statement, ICP (primary/secondary/anti-persona), value proposition, competitive landscape table, conversion strategy, content requirements, success metrics.

**Caveats:**
- Will redirect to `/hazn:ngo` if org type is NGO — this is correct behavior, not a bug.
- Discovery is interactive (asks questions one at a time). Batch all client info upfront to speed this up.
- "Vague differentiation" will be challenged. If the client hasn't thought this through, strategy phase takes longer.

---

## UX Architect

**Trigger:** `/hazn:ux`  
**Used in:** website, ngo-website, landing  
**Skills:** `b2b-marketing-ux`, `b2b-ux-reference` (B2B); `ngo-web-design` (NGO)

**When to spawn:** After `strategy.md` exists. Don't spawn before strategy is complete — the blueprint derives from ICP, positioning, and conversion goals.

**Input required:**
- `strategy.md` — non-negotiable prerequisite
- Site type (B2B commercial vs NGO) — determines which skill loads

**Output:** `.hazn/outputs/ux-blueprint.md` containing: site architecture tree, page blueprints (section-by-section with purpose/content/CTA for each section), user flow diagrams, responsive considerations, accessibility requirements.

**Caveats:**
- Blueprint sections must each earn their place — the agent will cut sections that don't advance the visitor journey.
- NGO track produces fundamentally different IA (transparency footer, mobilization hierarchy) vs B2B (conversion funnel).
- Every downstream agent (copywriter, wireframer, developer) depends on this output. A weak blueprint causes rework downstream.

---

## Copywriter

**Trigger:** `/hazn:copy`  
**Used in:** website, ngo-website, landing  
**Skills:** `b2b-website-copywriter`, `landing-page-copywriter` (B2B); `ngo-web-design` (NGO)

**When to spawn:** After `ux-blueprint.md` exists. Can run in parallel with wireframer — both depend on UX blueprint, not on each other.

**Input required:**
- `strategy.md`
- `ux-blueprint.md`
- Voice/tone calibration: how should the brand sound? Any words to avoid?

**Output:** `.hazn/outputs/copy/{page}.md` for each page — hero, problem, solution, social proof, CTA sections. Each file includes meta title (60 chars), meta description (155 chars), and section-by-section copy blocks.

**Caveats:**
- Will write for B2B conversion by default. Explicitly pass the NGO skill context for mission-driven copy — tone is fundamentally different.
- Copy is written for scanners: frontloaded, active voice, no weasel words. Clients who want "professional" (= passive, vague) copy will push back.
- Social proof sections require actual testimonial/case study content from the client. The copywriter will scaffold the structure and write prompts for what to fill in.

---

## Wireframer

**Trigger:** `/hazn:wireframe`  
**Used in:** website, ngo-website (optional in both)  
**Skills:** `b2b-wireframe`

**When to spawn:** After `ux-blueprint.md` exists. Run in parallel with copywriter. Use real copy if available, placeholder headlines if not. Spawn when stakeholder sign-off on layout is needed before code.

**Input required:**
- `ux-blueprint.md` — required
- `copy/` directory — optional (uses real headlines when available)
- Which pages need wireframes (all key pages or specific ones)

**Output:** `.hazn/outputs/wireframes/` containing one HTML file per page, plus `index.html` linking to all wireframes. Files use Tailwind via CDN, gray boxes for images, real text hierarchy.

**Caveats:**
- Wireframes exist to prevent expensive dev mistakes, not to be polished design deliverables. Gray boxes are intentional.
- The Wireframer uses the browser tool to present files — files must be accessible at a URL or via local server. File paths don't render in browser.
- If stakeholders treat wireframes as pixel-perfect mockups and start debating colors, redirect them: colors, fonts, and polish come after the layout is approved.

---

## Developer

**Trigger:** `/hazn:dev`  
**Used in:** website, ngo-website, landing  
**Skills:** `payload-nextjs-stack` (Next.js track); `wordpress-generatepress` (WordPress track)

**When to spawn:** After `ux-blueprint.md` exists (minimum). Better with copy and wireframes. Never spawn before stack decision is made (Next.js vs WordPress).

**Input required:**
- `ux-blueprint.md` — required
- `copy/` — strongly recommended
- `wireframes/` — optional
- Stack decision: Next.js + Payload CMS or WordPress + GeneratePress
- Staging environment / hosting details

**Output:** Built site at staging URL. `dev-progress.md` tracking completed/in-progress/blocked items.

**Caveats:**
- Will not mark a task complete without verifying in a browser. "Compiles without errors" ≠ "looks correct on mobile."
- Payload CMS 3.x is Next.js App Router native — do not pass Payload 2.x patterns.
- WordPress track requires GeneratePress Premium license ($59/yr). Confirm before starting.
- Dev output goes directly to QA Tester — not to the user. Never skip QA.
- For HestiaCP hosting: SSH in first, provision domain, then deploy. WP-CLI is used for all WordPress configuration.

---

## QA Tester

**Trigger:** Internal gate (spawned automatically after dev, not by user command)  
**Used in:** website, ngo-website  
**Skills:** None (uses browser tool directly)

**When to spawn:** After every developer build, before SEO. Mandatory — no exceptions, even for "simple" sites or when pressed for time.

**Input required:**
- Live URL (localhost or staging) — file paths do not work
- `dev-progress.md` — what the developer claims is complete
- `ux-blueprint.md` — what was specified

**Output:** `qa-report.md` with verdict (PASS / CONDITIONAL PASS / FAIL), numeric score, categorized issues, blueprint compliance table, screenshot evidence references.

**Caveats:**
- "Zero issues found" is a red flag — look harder. First builds have 3–5 issues minimum.
- Scoring is honest: a first build at 75 is normal. Inflating scores to avoid a fail cycle wastes everyone's time.
- FAIL routes back to Developer with specific, actionable issues (e.g., "hero headline overflows container at 375px" not "mobile looks off").
- Maximum 3 QA/dev cycles. If still failing after 3, escalate to user — don't loop infinitely.
- QA requires an actual rendered URL. Sites that need a build step (Next.js) must be running (`npm run dev` or deployed) before QA can run.

---

## SEO Specialist

**Trigger:** `/hazn:seo`  
**Used in:** website, ngo-website, blog  
**Skills:** `seo-optimizer`, `seo-audit`, `entity-knowledge-graph`

**When to spawn:** Only after QA PASS. Not before. SEO applied to a broken site is wasted — structured data on unfinalised copy must be redone after copy changes.

**Input required:**
- Live site URL (QA-passed)
- `strategy.md` — for entity and keyword context
- GA4/GSC credentials (optional, improves keyword strategy)

**Output:** `seo-checklist.md` (verified items), applied code changes (meta tags, structured data, sitemap, robots.txt, image optimization). `seo-keywords.md` if keyword strategy is run.

**Caveats:**
- Will not call it done until sitemap is submitted to GSC. This requires GSC access — flag if unavailable.
- Entity optimization for AI visibility (GEO) requires more than meta tags: structured Organization schema, sameAs links, topical authority signals.
- NGO track SEO focuses on discoverability for political education content and journalist findability (RSS feeds, press contact schema) — not B2B lead gen keywords.

---

## Content Writer

**Trigger:** `/hazn:content` or `/hazn-blog`  
**Used in:** blog, website (post-launch phase)  
**Skills:** `seo-blog-writer`, `keyword-research`

**When to spawn:** After the site is live and `seo-keywords.md` exists. Can run multiple content writer instances in parallel for different articles.

**Input required:**
- `strategy.md` — for audience and voice
- `seo-keywords.md` — for keyword targeting (or provide seed topics directly)
- Target CTA for articles (what should readers do at the end?)

**Output:** `content/blog/{slug}.md` with full frontmatter (title, description, slug, publishedAt, keywords, category). Article body: 1,500–3,000 words, H1/H2 structure, FAQ section, internal links, meta tags. Updates `content-log.md`.

**Caveats:**
- Articles optimized for AEO require definitive statements, not hedged language. If the writer defaults to "may", "might", "could", the article won't get cited by AI engines.
- Internal links require knowing the existing URL structure. Pass a site map or list of existing URLs.
- FAQ schema is written in the markdown but not injected as JSON-LD automatically — the developer or SEO specialist must add structured data to the CMS template.
- Parallel spawning works well: 3 articles can be written simultaneously by 3 content writer instances.

---

## Auditor

**Trigger:** `/hazn:audit`  
**Used in:** audit, ngo-website (accessibility gate)  
**Skills:** `conversion-audit`, `website-audit`, `ui-audit`

**When to spawn:** On-demand audit of any live site. Also spawned as the accessibility gate in the NGO workflow after development.

**Input required:**
- Live website URL
- Audit scope: full (conversion + copy + visual + SEO) or specific tracks
- Primary conversion goal
- Analytics access (optional, deepens conversion analysis)

**Output:** `.hazn/outputs/audit-report.html` (branded, shareable) + `.hazn/outputs/audit-summary.md`. NGO track also produces `accessibility-report.md`.

**Caveats:**
- Without GA4 access, conversion findings are heuristic only — visual observations, not behavioral data.
- The auditor uses Impact × Effort prioritization. An audit that lists 20 equal-weight issues is useless — the framework forces prioritization.
- Scores are honest (62 means 62). Don't recalibrate scores upward to soften findings for client delivery.

---

## Analytics Inspector

**Trigger:** Internal (spawned by analytics-audit and analytics-teaser workflows)  
**Used in:** analytics-audit, analytics-teaser  
**Skills:** analytics-audit

**When to spawn:** Phase 2 of analytics-audit (with GA4 data collection) or Phase 2 of analytics-teaser. Always runs before report writing.

**Input required:**
- Live site URL
- Output path for `site_inspection.json`

**Output:** `site_inspection.json` — structured inventory of every tracking system found on the page: GTM containers with IDs, GA4/Ads measurement IDs, ad pixels (Meta, Bing, TikTok, LinkedIn), CRM embeds (HubSpot, Klaviyo), session recording tools (Hotjar, Clarity), consent mode configuration, Shopify-specific configs (if applicable), redundancy flags, total script count.

**Caveats:**
- Fetches raw HTML via `curl` — JavaScript-rendered tracking (GTM tags that fire only after consent) may not be visible in source.
- Shopify's `webPixelsConfigList` is the most reliable source for what pixels are actually active — check it when Shopify is detected.
- Empty HubSpot embed code sections (commented-out script tags) are a common false negative — the inspector checks for this specifically.

---

## Analytics Report Writer

**Trigger:** Internal (spawned by analytics-audit workflow after data collection)  
**Used in:** analytics-audit  
**Skills:** analytics-audit, analytics-audit-martech  
**Model:** Opus

**When to spawn:** After `ga4_audit_data.json`, `ga4_audit_extra.json`, and `site_inspection.json` all exist. Not before. Missing data files produce a report full of gaps.

**Input required:**
- All collected JSON data files in `.hazn/outputs/analytics-audit/`
- Report template at `skills/analytics-audit/references/report-template.md`

**Output:** `{domain}-audit.md` — 800–1,200 lines, sections A through Q (Q only if GSC data exists). Every number sourced from JSON. Direct, opinionated findings with business impact framing.

**Caveats:**
- Uses Opus model — most expensive agent in the pipeline.
- Will not include Section Q if `gsc_audit_data.json` doesn't exist. This is correct behavior — note the gap.
- Report length should match data depth. Do not pad a thin dataset to hit 1,200 lines.

---

## Analytics Adversary

**Trigger:** Internal (spawned by analytics-audit workflow after report writing)  
**Used in:** analytics-audit  
**Model:** Opus

**When to spawn:** After `{domain}-audit.md` is complete. Always runs — it's not optional. A report that skips adversarial review risks delivering wrong numbers to a data-literate CMO.

**Input required:**
- Completed markdown audit report
- All source JSON data files (to verify claims against)

**Output:** Structured adversarial review with: critical issues (must fix before delivery), data accuracy concerns, unsupported claims, logical inconsistencies, recommendation challenges, missing analysis, verdict.

**Caveats:**
- This agent assumes nothing is correct until verified. A finding of "zero issues" should be treated skeptically — the Adversary is designed to find problems.
- Critical issues from this review must be corrected in the markdown report before the Client Reporter generates HTML.
- Uses Opus model — factor cost into workflow budget.

---

## Analytics Client Reporter

**Trigger:** Internal (spawned by analytics-audit workflow after adversarial review)  
**Used in:** analytics-audit  
**Skills:** analytics-audit-client-report  
**Model:** Opus

**When to spawn:** After the markdown report is finalized (post-adversarial review corrections). Not before — HTML is generated from hardcoded data; errors in the markdown propagate directly to the client-facing output.

**Input required:**
- Finalized `{domain}-audit.md`
- All source JSON data files
- Existing `client-report/index.html` if present (used as design benchmark)

**Output:** Single-file `client-report/index.html` — sticky sidebar ToC, responsive 375px–1440px, all CSS inline, all data hardcoded. Professional executive presentation.

**Caveats:**
- Report is a single HTML file with no external dependencies (except Google Fonts). Safe to email or deploy to `autonomous-proposals`.
- `images/` subdirectory references must be maintained if the report is deployed to a multi-file hosting environment.
- If an existing `index.html` exists in the output directory, it's used as the design benchmark — match or exceed its quality.

---

## Analytics Teaser Collector

**Trigger:** Internal (spawned by analytics-teaser workflow, Phase 2)  
**Used in:** analytics-teaser  
**Model:** Sonnet  
**Requires:** Playwright MCP tools

**When to spawn:** Phase 2 of analytics-teaser, in parallel with other data collection tracks. Requires Playwright to be installed and the Playwright MCP plugin to be active.

**Input required:**
- Target URL
- Output directory path

**Output:** `playwright_data.json` containing: per-page accessibility snapshots (desktop + mobile), console errors, detected secondary page URLs. Screenshots saved to `screenshots/` directory.

**Caveats:**
- **If Playwright is not installed, this agent fails silently** — no error, no screenshots, no snapshots. The teaser writer will proceed but Copy/UX/CRO analysis will be generic and unverifiable.
- Crawls homepage + up to 4 secondary pages (about, pricing, services, contact). More than 5 pages is out of scope.
- Cookie consent banners are dismissed before screenshots when possible — if the banner can't be dismissed, screenshots will show the overlay.
- JS console errors are captured as part of tracking quality signals — a high error count in `playwright_data.json` is a finding, not a bug in the collector.

---

## Analytics Teaser Writer

**Trigger:** Internal (spawned by analytics-teaser workflow, Phase 3)  
**Used in:** analytics-teaser  
**Skills:** analytics-teaser-report  
**Model:** Opus

**When to spawn:** After all 4 data collection tracks complete (`site_inspection.json`, `pagespeed.json`, `teaser_data.json`, `playwright_data.json`). If `playwright_data.json` is missing due to Playwright failure, the writer still runs but produces weaker Copy/UX/CRO sections.

**Input required:**
- All 4 collected data files
- Teaser skill at `skills/analytics-teaser-report/SKILL.md`
- Content template at `skills/analytics-audit/references/teaser-template.md`
- Optional: company name, Calendly URL

**Output:** Single self-contained `index.html` — Lighthouse grades, CWV gauges, MarTech tool grid, Copy/UX/CRO A–F grades with specific findings, 3 upsell gates, final CTA. Base64-embedded screenshots. Target file size <500KB.

**Caveats:**
- **Every Copy/UX/CRO finding must reference actual content from the site** — not generic best practices. If findings read as generic, the Playwright snapshots were likely missing or incomplete.
- Uses Opus model — expensive. Don't regenerate unnecessarily.
- All 3 gate sections use real data from the collected files to create FOMO (e.g., actual organic query volume, specific unconverted traffic numbers). Generic gate copy means the data wasn't used.
- Calendly URL must be provided or left blank — do not fabricate a link.

---
name: sitehealth
description: SiteHealth — run all four Intelligence Suite audits (SiteScore, Revenue Leak, ConversionIQ, UX/UI) as a coordinated bundle. Spawns parallel subagents for each audit, synthesises findings into a unified cross-audit roadmap, and prepares the 90-min strategy call brief. Use when a client wants the full suite or when any message mentions "SiteHealth", "full bundle", "all four audits", or "complete audit".
allowed-tools: Read, Write, Bash, web_fetch, web_search, browser
---

# SiteHealth — Full Bundle Orchestrator

## When to Use
- User requests "SiteHealth", "full bundle", "all four audits", or similar
- Standard: $1,997 · Deep Dive: $5,497
- Includes bundle-exclusive 90-min cross-audit strategy call

---

## Step 0: Pre-Flight Credential Check

Before asking the user for anything, check what credentials and access already exist:

**Google / GSC / GA4:**
- Check if ~/.config/ga4-audit/token.json exists and is valid
- If yes: "I have Google credentials on file (GSC + GA4 access). I will use these."
- Run: python3 ~/hazn/scripts/analytics-audit/ga4_collector.py --check 2>/dev/null || echo "GA4: available"
- Look up the GA4 property for the target domain by listing all properties

**PostHog:**
- Check ~/hazn/MEMORY.md and ~/hazn/TOOLS.md for PostHog API keys
- Check ~/hazn/brands/ for any project-specific PostHog config
- If found: "I found PostHog credentials for [project]. Confirming use."

**Ahrefs:**
- Check ~/hazn/TOOLS.md and ~/hazn/MEMORY.md for Ahrefs API key
- If not found: note that Ahrefs manual export or free tools will be used as fallback

**Brand config:**
- Check ~/hazn/brands/ for a slug matching the target domain
- If found: load it automatically, no need to ask

After pre-flight, report what was found:
> "Pre-flight check complete:
> - Google/GSC: ✅ authenticated
> - GA4: ✅ found [N] properties — will identify correct one from URL
> - PostHog: ✅ / ❌ [found/not found]
> - Ahrefs: ✅ / ❌ [found/not found]
> - Brand config: ✅ autonomous.json (default) / [partner slug]
>
> Only asking for what I could not find above."

Then run Step 0b (intake) asking ONLY for what is missing.

---

## Step 0b: Bundle Intake

Ask everything in ONE message:

> For the SiteHealth bundle I need a few things upfront:
>
> 1. **Primary URL to audit:**
> 2. **Tier:** Standard or Deep Dive?
> 3. **Brand:** Who is this report for?
>    - (a) Autonomous delivery (default)
>    - (b) Partner white-label — which partner slug?
>    - (c) End-customer branded — company name, primary colour, CTA URL
> 4. **Client email** (optional — for delivery)
> 5. **Company/product description** (2–3 sentences — helps all 4 audits)
>
> [Deep Dive only — also ask:]
> 6. Google Search Console + GA4 access (for SiteScore + Revenue Leak)
> 7. PostHog access if applicable (for Revenue Leak + ConversionIQ)
> 8. Key user journeys to map (for UX/UI Deep Dive)
> 9. Up to 3 competitor domains (used across all four audits)
> 10. Ahrefs access confirmation (for SiteScore Deep Dive)

After intake:
- Load brand config from ~/hazn/brands/{slug}.json. Default: ~/hazn/brands/autonomous.json
- Confirm: "I will run all four audits in parallel. Estimated delivery: [24–48h Standard / 3–5 business days Deep Dive]. Shall I proceed?"
- Wait for confirmation before proceeding.

---

## Step 1: Parallel Execution

Spawn four subagent sessions simultaneously, one per audit. Pass the shared intake params to each.

Each subagent receives:
- URL
- TIER (Standard or Deep Dive)
- brand_config
- client context (description, competitors, access tokens if Deep Dive)
- Instruction to save report to ~/hazn/projects/{client-slug}/sitehealth-{date}/{product}/report.html

Subagent tasks:

**Subagent 1 — SiteScore:**
Load ~/hazn/skills/seo-audit/SKILL.md. Run TIER audit for {url}. Skip intake (already done). Save findings to ~/hazn/projects/{client-slug}/sitehealth-{date}/sitescore/findings.md, then render report to ~/hazn/projects/{client-slug}/sitehealth-{date}/sitescore/report.html. Return: findings.md path + top 5 findings summary.

**Subagent 2 — Revenue Leak Audit:**
Load ~/hazn/skills/analytics-audit/SKILL.md. Run TIER audit for {url}. Skip intake (already done). Save findings to ~/hazn/projects/{client-slug}/sitehealth-{date}/revenue-leak/findings.md, then render report to ~/hazn/projects/{client-slug}/sitehealth-{date}/revenue-leak/report.html. Return: findings.md path + top 5 findings summary.

**Subagent 3 — ConversionIQ:**
Load ~/hazn/skills/conversion-audit/SKILL.md. Run TIER audit for {url}. Skip intake (already done). Save findings to ~/hazn/projects/{client-slug}/sitehealth-{date}/conversioniq/findings.md, then render report to ~/hazn/projects/{client-slug}/sitehealth-{date}/conversioniq/report.html. Return: findings.md path + top 5 findings summary.

**Subagent 4 — UX/UI Audit:**
Load ~/hazn/skills/ui-audit/SKILL.md. Run TIER audit for {url}. Skip intake (already done). Save findings to ~/hazn/projects/{client-slug}/sitehealth-{date}/ux-ui/findings.md, then render report to ~/hazn/projects/{client-slug}/sitehealth-{date}/ux-ui/report.html. Return: findings.md path + top 5 findings summary.

Wait for all four to complete before proceeding.

---

## Step 2: Cross-Audit Synthesis

After all four audits complete, read all four findings.md files (not HTML reports):
- ~/hazn/projects/{client-slug}/sitehealth-{date}/sitescore/findings.md
- ~/hazn/projects/{client-slug}/sitehealth-{date}/revenue-leak/findings.md
- ~/hazn/projects/{client-slug}/sitehealth-{date}/conversioniq/findings.md
- ~/hazn/projects/{client-slug}/sitehealth-{date}/ux-ui/findings.md

Collect:
- Top 5 findings from each audit (20 findings total)
- Each finding: product source, issue, severity, effort level, estimated impact

Then:

### Identify Cross-Cutting Themes
Look for findings that compound each other across audits. Examples:
- "Attribution is broken (Revenue Leak) AND conversion tracking is misconfigured (ConversionIQ)" = one root cause: GA4 setup
- "AI bots blocked (SiteScore AEO) AND content not extractable (SiteScore GEO) AND page descriptions are vague (ConversionIQ)" = one root cause: content strategy
- "CTA contrast fails (UX/UI) AND CTA copy is weak (ConversionIQ)" = one fix addresses both

Flag these as "Cross-Audit Critical" — they punch above their weight.

### Identify Dependencies
Some fixes must happen in a specific order:
- Fix attribution (Revenue Leak) BEFORE running A/B tests (ConversionIQ)
- Fix GA4 (Revenue Leak) BEFORE measuring impact of SEO improvements (SiteScore)
- Fix technical SEO (SiteScore) BEFORE investing in content/AEO (SiteScore)

Flag dependencies explicitly in the roadmap.

### Build Unified Roadmap
Sequence all findings from all four audits into one prioritised list:

**This Week (Quick Wins — Low effort, High impact):**
List items with Low effort that unblock other work or have immediate impact.

**This Sprint (High Impact — Medium effort):**
Core improvements. Sequence by dependency order first, then impact.

**Next Quarter (Strategic — High effort or long-term):**
Foundational changes, content strategy, design system work.

For each item:
- Source audit (SiteScore / Revenue Leak / ConversionIQ / UX/UI)
- Finding
- Effort: Low / Medium / High
- Impact: High / Medium / Low
- Depends on: [other item if applicable]
- Cross-audit flag if applicable

---

## Step 3: Strategy Call Prep Doc

Generate a 1-page brief for the 90-min strategy call. Save to:
~/hazn/projects/{client-slug}/sitehealth-{date}/strategy-call-brief.md

Content:
1. **Top 3 Cross-Audit Insights** — the most important things to discuss
2. **The One Root Cause** — if there is a single underlying issue driving multiple problems, name it
3. **Recommended Starting Point** — the single first thing to fix and why
4. **Expected ROI** — if top 3 issues are fixed, what is the estimated impact? (use benchmark data if no real GA4 data)
5. **Questions to ask client on the call** — 5 questions to understand their priorities and constraints

---

## Step 4: Deliver

First, write cross-audit synthesis to: ~/hazn/projects/{client-slug}/sitehealth-{date}/synthesis.md

Then generate a SiteHealth cover report from synthesis.md: ~/hazn/projects/{client-slug}/sitehealth-{date}/index.html

**Source of truth:** Read synthesis.md first. The index.html renders the data from synthesis.md — do not re-collect data during HTML generation.

This is a single-page summary that:
- Shows the four audit scores in a 2x2 grid
- Links to each individual report
- Shows the unified roadmap summary (top 10 items)
- Includes the strategy call scheduling CTA
- Uses brand_config tokens

Then deliver:
- 5 report URLs: SiteScore / Revenue Leak / ConversionIQ / UX/UI / SiteHealth index
- Strategy call brief (paste key sections inline)
- Confirm: "All four audits complete. Here are your reports: [links]. Strategy call brief attached. Book your 90-min session at [brand_config.cta_url]."

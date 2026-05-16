# Hazn

AI orchestrator for B2B and institutional website projects, packaged as an installable Claude Code plugin.

Hazn coordinates 22 specialist agents through 7 structured workflows, drawing on 47 deep skills covering the full project lifecycle — strategy, UX, copywriting, wireframes, development (Next.js + Payload, Wagtail, WordPress), SEO/AEO/GEO, analytics, audits, and client deliverables.

## Marketplace layout (v0.4.0+)

This repo is structured as a Claude Code plugin marketplace. All v0.3.x plugin content lives under `plugins/hazn-legacy/` as a single installable entry. Specialist plugins (hazn-runtime, shopify-revenue-audit, etc.) will be extracted from hazn-legacy and added as peer entries over subsequent phases. See [docs/decisions/003-hazn-marketplace.md](docs/decisions/003-hazn-marketplace.md) for the full migration plan.

## Install

```bash
claude plugin install /path/to/repos/products/hazn
```

After install, commands are namespaced under `/hazn:` (e.g. `/hazn:hazn-audit`, `/hazn:hazn-website`). Skills auto-trigger on relevant keywords. Agents register as parallel sub-agents Claude Code can dispatch.

## Components

### Slash commands (15)

`/hazn:hazn-help` (start here), `/hazn:hazn-website` (B2B build), `/hazn:hazn-landing` (fast landing page), `/hazn:hazn-audit` (site audit), `/hazn:hazn-strategy`, `/hazn:hazn-ux`, `/hazn:hazn-copy`, `/hazn:hazn-wireframe`, `/hazn:hazn-dev`, `/hazn:hazn-seo`, `/hazn:hazn-content`, `/hazn:hazn-qa`, `/hazn:hazn-wagtail-dev`, `/hazn:hazn-wireframe-fidelity`, `/hazn:hazn-store-diagnostic`.

### Skills (47)

**Orchestration:** `hazn-orchestrator`

**Strategy:** `b2b-marketing-ux`, `b2b-ux-reference`

**Copy:** `b2b-website-copywriter`, `landing-page-copywriter`, `copy-editing`, `cold-email`, `email-sequence`

**Design:** `b2b-wireframe`, `frontend-design`, `design-system`, `ui-audit`

**Development:** `payload-nextjs-stack`, `wagtail-nextjs-stack`, `wordpress-generatepress`, `jwd-audit`, `wireframe-fidelity`

**SEO/AEO/GEO:** `keyword-research`, `seo-audit`, `seo-optimizer`, `ai-seo`, `programmatic-seo`, `entity-knowledge-graph`, `llms-txt`, `seo-blog-writer`, `reddit-growth`

**Analytics:** `analytics-audit`, `analytics-tracking`, `analytics-audit-client-report`, `analytics-audit-martech`, `analytics-teaser-report`

**Audits:** `conversion-audit`, `website-audit`, `sitehealth`, `ab-test-setup`

**Revenue rescue (Shopify):** `shopify-revenue-audit`, `audit-red-team-baseline`, `audit-red-team-cfo`, `audit-red-team-domain-check`, `audit-red-team-uplifts`, `editorial-warmth-audit-renderer`

**Deliverables:** `case-study`, `sow`, `project-plan`

**Specialized:** `ngo-web-design`, `references`, `shared`, `sitehealth`

### Agents (22)

Strategist, UX Architect, Copywriter, Wireframer, Developer, WordPress Developer, Wagtail Developer, QA Tester, SEO Specialist, Content Writer, Auditor, Email Specialist, Conversion Specialist, Case Study Builder, JWD Auditor (+ v1), and 6 analytics specialists (Inspector, Adversary, Report Writer, Client Reporter, Teaser Collector, Teaser Writer).

### Workflows (7)

`website` (B2B), `audit`, `blog`, `landing`, `ngo-website`, `analytics-audit`, `analytics-teaser`.

### Brand configs

`brands/{slug}.json` for per-client brand overrides. Default: `brands/autonomous.json` (Stone/Amber editorial design system).

## Status

`v0.3.1` — consolidated 2026-05-15 from 5 scattered locations into this single source. See `CONTRIBUTING.md` for the single-source policy.

## Repository

`git@github.com:autonomous-tech/hazn.git`

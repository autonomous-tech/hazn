<p align="center">
  <img src="assets/avatar.png" alt="Hazn" width="180" />
</p>

<h1 align="center">Hazn</h1>

<p align="center">
  <strong>AI-driven marketing website development framework</strong>
</p>

Hazn transforms your AI coding assistant into a team of specialized marketing experts. From strategy to deployment, Hazn guides you through building high-converting B2B websites.

📖 **[View Documentation](docs/)**

---

## Overview

| Component | Count | Description |
|-----------|-------|-------------|
| **Agents** | 12 | Specialized expert personas (Strategist, UX Architect, Developer, Analytics, etc.) |
| **Skills** | 25 | Deep domain knowledge (SEO, copywriting, conversion optimization, analytics, etc.) |
| **Workflows** | 7 | End-to-end processes (website build, audit, blog, landing page, email, optimization, analytics audit) |

---

## What's New 🚀

**Marketing Skills Upgrade** — Added 7 new skills based on analysis of [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills):

- **AI-first SEO:** `ai-seo` and `programmatic-seo` for LLM citations and scaled content
- **Growth stack:** `ab-test-setup` and `analytics-tracking` for PostHog + GA4 integration
- **Outbound:** `email-sequence` and `cold-email` for B2B prospecting automation
- **Copy polish:** `copy-editing` framework for refining existing content

Plus two new workflows: `/email` for campaign design and `/optimize` for post-launch A/B testing.

**Analytics Audit Pipeline** — Full MarTech & Attribution audit with GA4/GSC data collection, 4 specialized agents, adversarial review, and branded HTML client reports.

---

## Quick Start

### Option 1: npx (recommended)

```bash
# Run directly from GitHub (no install needed)
cd your-project
npx github:autonomous-tech/hazn install
```

### Option 2: Clone + Link

```bash
# Clone the repo
git clone https://github.com/autonomous-tech/hazn.git

# Link globally
cd hazn
npm install
npm link

# Install in your project
cd your-project
hazn install
```

### Option 3: Direct execution

```bash
# Clone once, run from anywhere
git clone https://github.com/autonomous-tech/hazn.git ~/hazn

# Install in your project
cd your-project
node ~/hazn/bin/cli.js install
```

### After installation

Open your project in Claude Code / Cursor / Windsurf and run:

```
/hazn-help
```

The installer creates `.hazn/` with agents, workflows, skills, and a `HAZN.md` quick reference in your project root.

---

## Agents

| Agent | Trigger | Role |
|-------|---------|------|
| **Strategist** | `/hazn-strategy` | Market positioning, audience definition, competitive analysis |
| **UX Architect** | `/hazn-ux` | Page blueprints, information architecture, user flows |
| **Copywriter** | `/hazn-copy` | Headlines, value props, CTAs, full page copy |
| **Wireframer** | `/hazn-wireframe` | Mid-fidelity layouts for validation |
| **Developer** | `/hazn-dev` | Next.js + Payload CMS + Tailwind implementation |
| **SEO Specialist** | `/hazn-seo` | Technical SEO, schema, content optimization |
| **Content Writer** | `/hazn-content` | Blog posts, keyword-optimized articles |
| **Auditor** | `/hazn-audit` | Multi-dimensional website analysis |
| **Analytics Inspector** | `/hazn-analytics-audit` | Site tracking tag inspection |
| **Analytics Report Writer** | `/hazn-analytics-audit` | MarTech audit reports |
| **Analytics Adversary** | `/hazn-analytics-audit` | Red-team audit review |
| **Analytics Client Reporter** | `/hazn-analytics-audit` | Branded HTML client reports |

---

## Skills

### Strategy
- `b2b-marketing-ux` — UX strategy, page architecture, conversion design
- `b2b-ux-reference` — Deep reference for buyer psychology, trust patterns

### Content
- `b2b-website-copywriter` — Conversion copy for B2B services websites
- `landing-page-copywriter` — High-converting landing page copy
- `seo-blog-writer` — SEO + AEO + GEO optimized blog posts
- `copy-editing` — Copy improvement framework

### Design
- `b2b-wireframe` — Mid-fidelity HTML wireframes
- `frontend-design` — Visual aesthetics, avoiding generic AI design
- `ui-audit` — UX/UI audits based on design principles

### Development
- `payload-nextjs-stack` — Next.js + Payload CMS + Tailwind patterns

### SEO
- `keyword-research` — Keyword discovery, intent analysis, content mapping
- `seo-audit` — Technical SEO audits
- `seo-optimizer` — On-page and technical SEO implementation
- `entity-knowledge-graph` — Entity optimization for AI citation (GEO)
- `ai-seo` — AI search optimization (LLM citations, AEO, GEO)
- `programmatic-seo` — Scaled page generation

### Audits
- `conversion-audit` — CRO audits with branded reports
- `website-audit` — Comprehensive multi-dimensional site audits

### Marketing & Analytics
- `ab-test-setup` — A/B testing with PostHog
- `analytics-tracking` — GA4 + PostHog setup
- `analytics-audit` — GA4 property audit and attribution analysis
- `analytics-audit-martech` — MarTech stack assessment and roadmap
- `analytics-audit-client-report` — Branded HTML client report generator
- `email-sequence` — B2B email automation
- `cold-email` — B2B outbound prospecting

---

## Workflows

### Full Website Build
```
/hazn-website
```
Strategy → UX → Copy → Wireframe → Development → SEO

**Duration:** 1-4 weeks

### Site Audit
```
/hazn-audit
```
Conversion + Copy + Visual + SEO analysis with actionable recommendations.

**Duration:** 2-4 hours

### Blog Content Pipeline
```
/hazn-content
```
Keyword research → Content calendar → SEO-optimized articles

**Duration:** 1-2 hours per article

### Quick Landing Page
```
/hazn-landing
```
Brief → Structure → Copy → Build

**Duration:** 4-8 hours

### Email Campaign
```
/email
```
Audience → Sequence design → Copy → Automation setup

**Duration:** 2-4 hours

### Post-Launch Optimization
```
/optimize
```
Analytics setup → A/B test design → Implementation → Analysis

**Duration:** Ongoing

### Analytics Audit
```
/hazn-analytics-audit
```
GA4/GSC data collection → Site inspection → Analysis → Adversarial review → Client report

**Duration:** 3-6 hours

---

## Project Structure

After running `hazn install`, your project will have:

```
your-project/
├── HAZN.md              # Quick reference card
└── .hazn/
    ├── agents/          # Agent persona definitions
    ├── workflows/       # Workflow YAML configs
    ├── skills/          # Domain expertise (25 skills)
    ├── scripts/         # Python collector scripts
    ├── outputs/         # Generated artifacts (created during use)
    └── config.json      # Installation config
```

### Repository Structure

The Hazn repo itself is organized as:

```
hazn/
├── agents/          # Source agent definitions
├── skills/          # Source skill definitions
├── scripts/         # Python collector scripts
├── workflows/       # Source workflow configs
├── templates/       # Templates (HAZN.md, etc.)
├── src/             # CLI source code
├── bin/             # CLI entry point
└── docs/            # Documentation
```

---

## Documentation

- [Agents Reference](docs/AGENTS.md) — Detailed agent documentation
- [Skills Reference](docs/SKILLS.md) — All 25 skills with usage guides
- [Workflows Reference](docs/WORKFLOWS.md) — Workflow phases and customization

---

## Tech Stack (for generated sites)

- **Framework:** Next.js 14+ (App Router)
- **CMS:** Payload CMS 3.x
- **Styling:** Tailwind CSS
- **Deployment:** Vercel / Self-hosted

---

## License

MIT — see [LICENSE](LICENSE).

---

Built by [Autonomous](https://autonomoustech.ca)

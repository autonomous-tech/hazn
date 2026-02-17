<p align="center">
  <img src="assets/avatar.png" alt="Hazn" width="180" />
</p>

<h1 align="center">Hazn</h1>

<p align="center">
  <strong>AI-driven marketing website development framework</strong>
</p>

Hazn transforms your AI coding assistant into a team of specialized marketing experts. From strategy to deployment, Hazn guides you through building high-converting B2B websites.

📖 **[View Documentation](https://rizqaiser.com/hazn/docs/)**

---

## Overview

| Component | Count | Description |
|-----------|-------|-------------|
| **Agents** | 8 | Specialized expert personas (Strategist, UX Architect, Developer, etc.) |
| **Skills** | 15 | Deep domain knowledge (SEO, copywriting, conversion optimization, etc.) |
| **Workflows** | 4 | End-to-end processes (website build, audit, blog pipeline, landing page) |

---

## Quick Start

```bash
# Clone this repo
git clone git@github.com:autonomous-tech/hazn.git

# Copy to your project
cp -r hazn/.hazn your-project/
cp hazn/HAZN.md your-project/

# Open in Claude Code / Cursor / Windsurf and run:
/hazn-help
```

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

---

## Skills

### Strategy
- `b2b-marketing-ux` — UX strategy, page architecture, conversion design
- `b2b-ux-reference` — Deep reference for buyer psychology, trust patterns

### Content
- `b2b-website-copywriter` — Conversion copy for B2B services websites
- `landing-page-copywriter` — High-converting landing page copy
- `seo-blog-writer` — SEO + AEO + GEO optimized blog posts

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

### Audits
- `conversion-audit` — CRO audits with branded reports
- `website-audit` — Comprehensive multi-dimensional site audits

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

---

## Project Structure

```
.hazn/
├── agents/          # Agent persona definitions
├── workflows/       # Workflow YAML configs
├── skills/          # Domain expertise (15 skills)
├── outputs/         # Generated artifacts
└── config.json      # Project config

HAZN.md              # Quick reference card
```

---

## Documentation

- [Agents Reference](docs/AGENTS.md) — Detailed agent documentation
- [Skills Reference](docs/SKILLS.md) — All 15 skills with usage guides
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

Built by [Autonomous](https://autonomous.so)

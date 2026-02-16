# 🎯 Hazn

**AI-driven marketing website development framework**

Hazn transforms your AI coding assistant into a team of specialized marketing experts. From strategy to deployment, Hazn guides you through building high-converting B2B websites.

[![npm version](https://img.shields.io/npm/v/hazn.svg)](https://www.npmjs.com/package/hazn)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why Hazn?

Traditional AI tools generate code. Hazn generates **strategy-informed, conversion-optimized websites**.

- 🎯 **Domain Expert Agents** — Strategist, UX Architect, Copywriter, Developer, SEO Specialist
- 📋 **Structured Workflows** — Proven processes from strategy to deployment
- 🔄 **Artifact Chaining** — Each phase builds on the last
- ⚡ **Works with your tools** — Claude Code, Cursor, Windsurf

## Quick Start

```bash
npx hazn install
```

Then open your project in Claude Code, Cursor, or Windsurf and run:

```
/hazn-help
```

## Workflows

### Full Website Build

Complete marketing website from scratch:

```
/hazn-strategy → /hazn-ux → /hazn-copy → /hazn-wireframe → /hazn-dev → /hazn-seo
```

**Outputs:**
- Market positioning & messaging strategy
- UX blueprints with section-by-section specs
- Conversion-focused copy for all pages
- Wireframes for stakeholder approval
- Production Next.js + Payload CMS code
- Technical SEO implementation

### Site Audit

Analyze existing websites:

```
/hazn-audit
```

**Outputs:**
- Conversion/CRO analysis
- Copy effectiveness review
- Visual/UX assessment
- Technical SEO audit
- Prioritized recommendations

### Blog Content Pipeline

SEO-optimized content creation:

```
/hazn-content
```

**Outputs:**
- Keyword research & mapping
- Content calendar
- SEO-optimized articles
- Schema markup

## Agents

| Agent | Role |
|-------|------|
| **Strategist** | Market positioning, audience definition, competitive analysis |
| **UX Architect** | Information architecture, page blueprints, user flows |
| **Copywriter** | Headlines, value props, CTAs, full page copy |
| **Wireframer** | Mid-fidelity layouts for validation |
| **Developer** | Next.js + Payload CMS + Tailwind implementation |
| **SEO Specialist** | Technical SEO, schema, content optimization |
| **Content Writer** | Blog posts, keyword-optimized articles |
| **Auditor** | Multi-dimensional website analysis |

## Tech Stack

Hazn generates code for:

- **Framework:** Next.js 14+ (App Router)
- **CMS:** Payload CMS 3.x
- **Styling:** Tailwind CSS
- **Deployment:** Vercel / Self-hosted

## Project Structure

After installation:

```
your-project/
├── HAZN.md              — Quick reference
└── .hazn/
    ├── agents/          — Agent personas
    ├── workflows/       — Workflow definitions
    ├── skills/          — Domain expertise
    ├── outputs/         — Generated artifacts
    └── config.json      — Configuration
```

## Commands

| Command | Description |
|---------|-------------|
| `npx hazn install` | Install Hazn into a project |
| `npx hazn list` | List available agents and workflows |
| `npx hazn help [topic]` | Get help on specific topics |

### In-IDE Commands

| Command | Description |
|---------|-------------|
| `/hazn-help` | Contextual guidance |
| `/hazn-website` | Full website workflow |
| `/hazn-audit` | Site audit |
| `/hazn-strategy` | Strategy phase |
| `/hazn-ux` | UX architecture phase |
| `/hazn-copy` | Copywriting phase |
| `/hazn-wireframe` | Wireframe phase |
| `/hazn-dev` | Development phase |
| `/hazn-seo` | SEO optimization phase |
| `/hazn-content` | Blog content pipeline |

## Non-Interactive Install

For CI/CD or automated setups:

```bash
npx hazn install --directory /path/to/project --tools claude-code --yes
```

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

## Documentation

- [Skills Reference](docs/SKILLS.md) — 15 specialized domain skills
- [Agents Reference](docs/AGENTS.md) — 8 expert agent personas
- [Workflows Reference](docs/WORKFLOWS.md) — 4 structured workflows

## Skills Included

Hazn ships with 15 production-ready skills:

| Category | Skills |
|----------|--------|
| **Strategy** | b2b-marketing-ux, b2b-ux-reference |
| **Content** | b2b-website-copywriter, landing-page-copywriter, seo-blog-writer |
| **Design** | b2b-wireframe, frontend-design, ui-audit |
| **Development** | payload-nextjs-stack |
| **SEO** | keyword-research, seo-audit, seo-optimizer, entity-knowledge-graph |
| **Audits** | conversion-audit, website-audit |

See [Skills Reference](docs/SKILLS.md) for detailed documentation.

## License

MIT — see [LICENSE](LICENSE).

---

Built by [Autonomous](https://autonomous.so)

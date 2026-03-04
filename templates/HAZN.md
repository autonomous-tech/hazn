# 🎯 Hazn

AI-driven website development framework for B2B, NGO, and institutional websites.

## ⚡ Start Here — What type of website?

| Organisation type | Use this command |
|------------------|-----------------|
| B2B / commercial / agency | `/hazn-website` |
| NGO / association / political org / international institution | `/hazn-ngo` |
| Site audit (any type) | `/hazn-audit` |
| Blog content pipeline | `/hazn-content` |

> **Never use `/hazn-website` for an NGO.** The goals, IA, compliance requirements, and tone are fundamentally different. Use `/hazn-ngo`.

## Quick Commands

| Command | Description |
|---------|-------------|
| `/hazn-help` | Contextual guidance on what to do next |
| `/hazn-website` | Full B2B/commercial website build |
| `/hazn-ngo` | NGO / association / institutional website build |
| `/hazn-audit` | Comprehensive site audit |
| `/hazn-strategy` | Define positioning and goals |
| `/hazn-ux` | Create page blueprints |
| `/hazn-copy` | Write content |
| `/hazn-wireframe` | Visual layout validation |
| `/hazn-dev` | Build (Next.js + Payload CMS, or WordPress + GeneratePress) |
| `/hazn-seo` | Technical SEO optimization |
| `/hazn-content` | Blog content pipeline |
| `/hazn-analytics-audit` | Full MarTech & Attribution audit (needs GA4/GSC) |
| `/hazn-analytics-teaser` | Zero-access prospect teaser report |

## Workflows

### B2B / Commercial Website
```
/hazn-strategy → /hazn-ux → /hazn-copy → /hazn-wireframe → /hazn-dev → /hazn-seo
```

### NGO / Association / Institutional Website
```
/hazn-ngo → (strategy + compliance) → /hazn-ux → /hazn-wireframe → /hazn-dev → accessibility audit → /hazn-seo
```

### Quick Landing Page
```
/hazn-strategy → /hazn-dev
```

### Site Audit
```
/hazn-audit
```

### Analytics Audit
```
/hazn-analytics-audit <site-url> <ga4-property-id> [gsc-site-url]
```

### Analytics Teaser (Prospect)
```
/hazn-analytics-teaser <site-url> [company-name] [calendly-url]
```

## Agents

- **Strategist** — Positioning for B2B or mission/mobilization for NGOs
- **UX Architect** — Page blueprints and user journey design
- **Copywriter** — Conversion copy (B2B) or mission-driven copy (NGO)
- **Wireframer** — Mid-fidelity layout validation
- **Developer** — Next.js + Payload CMS (B2B) or WordPress + GeneratePress (NGO/WP)
- **SEO Specialist** — Technical SEO, schema, AI visibility
- **Auditor** — Multi-dimensional site analysis (conversion, UX, copy, SEO, accessibility)

## Project Structure

```
.hazn/
├── agents/      — Agent personas
├── workflows/   — Workflow definitions
├── skills/      — Domain skills
├── outputs/     — Generated artifacts
│   ├── strategy.md
│   ├── ux-blueprint.md
│   ├── copy/
│   ├── wireframes/
│   └── ...
└── config.json
```

## Tips

- Run `/hazn-help` anytime for guidance
- Outputs from each phase feed into the next
- Skip phases if you have existing assets
- Agents will ask clarifying questions — answer thoroughly

## Learn More

- Documentation: https://hazn.dev/docs
- GitHub: https://github.com/autonomous-tech/hazn

# 🎯 Hazn

AI-driven marketing website development framework.

## Quick Commands

| Command | Description |
|---------|-------------|
| `/hazn-help` | Contextual guidance on what to do next |
| `/hazn-website` | Full website build workflow |
| `/hazn-audit` | Comprehensive site audit |
| `/hazn-strategy` | Define positioning and goals |
| `/hazn-ux` | Create page blueprints |
| `/hazn-copy` | Write conversion-focused content |
| `/hazn-wireframe` | Visual layout validation |
| `/hazn-dev` | Build with Next.js + Payload CMS |
| `/hazn-seo` | Technical SEO optimization |
| `/hazn-content` | Blog content pipeline |

## Workflows

### Full Website Build
```
/hazn-strategy → /hazn-ux → /hazn-copy → /hazn-wireframe → /hazn-dev → /hazn-seo
```

### Quick Landing Page
```
/hazn-strategy → /hazn-dev
```

### Site Audit
```
/hazn-audit
```

## Agents (18 sub-agents)

- **Strategist** — Market positioning & competitive analysis
- **UX Architect** — Page blueprints & user journey design
- **Copywriter** — Conversion-focused messaging
- **Wireframer** — Mid-fidelity layout validation
- **Developer** — Next.js + Payload CMS implementation
- **WordPress Developer** — WordPress + GeneratePress implementation
- **Wagtail Developer** — Django + Wagtail + Next.js implementation
- **SEO Specialist** — Technical SEO & content optimization
- **Auditor** — Multi-dimensional site analysis
- **Content Writer** — Blog posts & keyword-optimized articles
- **QA Tester** — Visual QA, responsiveness, blueprint compliance
- **Case Study Builder** — PSR+JTBD interview, dual HTML+JSON output
- **Analytics Inspector** — GA4 & tracking verification
- **Analytics Client Reporter** — Client-facing analytics reports
- **Analytics Teaser Collector** — Prospect data collection for teasers
- **Analytics Teaser Writer** — Teaser report generation
- **Analytics Adversary** — Red-team audit for analytics gaps
- **Analytics Report Writer** — Full analytics audit reports

## Skills (32 skills)

See `skills/` directory for full list. Key skill categories:

- **Strategy:** b2b-marketing-ux, b2b-ux-reference, ngo-web-design
- **Content:** b2b-website-copywriter, landing-page-copywriter, seo-blog-writer
- **Design:** b2b-wireframe, frontend-design, ui-audit
- **Development:** payload-nextjs-stack, wagtail-nextjs-stack, wordpress-generatepress
- **SEO:** keyword-research, seo-audit, seo-optimizer, entity-knowledge-graph, ai-seo
- **Analytics:** analytics-audit, analytics-audit-client-report, analytics-audit-martech, analytics-teaser-report, analytics-tracking
- **Audits:** conversion-audit, website-audit
- **Portfolio:** case-study

## Project Structure

```
hazn/
├── sub-agents/  — 18 specialist agent personas
├── skills/      — 32 domain skills
├── projects/    — Client project outputs
│   └── {client}/
│       ├── state.json
│       ├── strategy.md
│       ├── ux-blueprint.md
│       ├── copy/
│       └── wireframes/
├── scripts/     — Data collection scripts
├── templates/   — Reusable templates
└── WORKFLOWS.md — Playbook reference
```

## Tips

- Run `/hazn-help` anytime for guidance
- Outputs from each phase feed into the next
- Skip phases if you have existing assets
- Agents will ask clarifying questions — answer thoroughly

## Learn More

- Documentation: https://hazn.dev/docs
- GitHub: https://github.com/autonomous-tech/hazn

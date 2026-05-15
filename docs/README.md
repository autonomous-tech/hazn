# Hazn — Documentation Index

Hazn is an AI orchestration framework for B2B marketing websites. It coordinates 15 specialist sub-agents across 7 workflows to take projects from strategy to deployment.

---

## Workflows

| Workflow | Trigger | Duration | Agents Involved |
|---|---|---|---|
| [Full Website Build](workflows/website.md) | `/hazn:website` | 2 days – 4 weeks | Strategist, UX Architect, Copywriter, Wireframer, Developer, QA Tester, SEO Specialist, Content Writer |
| [Comprehensive Audit](workflows/audit.md) | `/hazn:audit` | 2–4 hours | Auditor |
| [Blog Content Pipeline](workflows/blog.md) | `/hazn:content` | 1–2 hrs/article | Content Writer, SEO Specialist |
| [Landing Page](workflows/landing.md) | `/hazn:landing` | 4–8 hours | UX Architect, Copywriter, Developer |
| [Analytics & MarTech Audit](workflows/analytics-audit.md) | `/hazn-analytics-audit` | 3–6 hours | Analytics Inspector, Analytics Report Writer, Analytics Adversary, Analytics Client Reporter |
| [Analytics Teaser Report](workflows/analytics-teaser.md) | `/hazn-analytics-teaser` | 30–60 minutes | Analytics Inspector, Analytics Teaser Collector, Analytics Teaser Writer |
| [NGO / Association Website](workflows/ngo-website.md) | `/hazn:ngo` | 3 days – 4 weeks | Strategist, UX Architect, Copywriter, Wireframer, Developer, Auditor, SEO Specialist |

---

## Agents

| Agent | Trigger | Primary Role |
|---|---|---|
| [Strategist](agents.md#strategist) | `/hazn:strategy` | Market positioning, ICP definition, competitive analysis |
| [UX Architect](agents.md#ux-architect) | `/hazn:ux` | Information architecture, page blueprints, user flows |
| [Copywriter](agents.md#copywriter) | `/hazn:copy` | Conversion copy, headlines, CTAs, section-by-section content |
| [Wireframer](agents.md#wireframer) | `/hazn:wireframe` | Mid-fidelity HTML wireframes for stakeholder approval |
| [Developer](agents.md#developer) | `/hazn:dev` | Next.js + Payload CMS or WordPress + GeneratePress builds |
| [QA Tester](agents.md#qa-tester) | Internal gate | Visual QA, responsiveness, blueprint compliance — required gate before SEO |
| [SEO Specialist](agents.md#seo-specialist) | `/hazn:seo` | Technical SEO, structured data, entity optimization, AI visibility |
| [Content Writer](agents.md#content-writer) | `/hazn:content` | Long-form SEO blog posts (1,500–3,000 words) |
| [Auditor](agents.md#auditor) | `/hazn:audit` | Multi-track conversion/copy/UX/SEO audit with scored HTML report |
| [Analytics Inspector](agents.md#analytics-inspector) | Internal | Site HTML source inspection — tracking codes, pixels, GTM, consent |
| [Analytics Report Writer](agents.md#analytics-report-writer) | Internal | Full A–Q section MarTech audit report in markdown |
| [Analytics Adversary](agents.md#analytics-adversary) | Internal | Red-team review — challenges every number and claim before delivery |
| [Analytics Client Reporter](agents.md#analytics-client-reporter) | Internal | Polished single-file HTML client report from audit data |
| [Analytics Teaser Collector](agents.md#analytics-teaser-collector) | Internal | Playwright crawler — screenshots + accessibility snapshots |
| [Analytics Teaser Writer](agents.md#analytics-teaser-writer) | Internal | Zero-access teaser report writer — HTML sales asset |

---

## Quick Decisions

**Full new website for a business?** → `/hazn:website`  
**Full new website for an NGO, association, or political org?** → `/hazn:ngo`  
**Single landing page fast?** → `/hazn:landing`  
**Audit an existing site?** → `/hazn:audit`  
**Write blog content?** → `/hazn:content`  
**Audit a client's GA4/MarTech stack with access?** → `/hazn-analytics-audit`  
**Prospect report without any credentials?** → `/hazn-analytics-teaser`

---

## Key Rules

- **Never use `/hazn:website` for NGOs.** The goals, IA, tone, and compliance requirements are fundamentally different. Always ask org type first.
- **QA is a mandatory gate** — SEO never runs before QA passes.
- **Analytics audit requires OAuth setup per client** — it is not automated.
- **Teaser report requires Playwright installed** — collection silently fails without it.

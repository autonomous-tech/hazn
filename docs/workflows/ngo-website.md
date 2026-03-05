# NGO / Association Website Build

> Full website build for NGOs, associations (Vereine), political organizations, and international institutions — mission-driven IA, compliance-first, WCAG 2.1 AA, built for mobilization not conversion.

## When to Use

- Building or rebuilding a website for an NGO, Verein (e.V., gGmbH), Stiftung, political party, campaign, or civil society organization
- International institution needing a credibility-first, authority-driven web presence
- Any organization where the primary goals are transparency, member engagement, donation, or public education — not revenue

**NOT for:**
- B2B/commercial agencies, SaaS, or productized service businesses → use `/hazn-website`
- E-commerce or membership-gated platforms requiring custom business logic

## Requirements

- Organization name, legal form, and jurisdiction (Germany? EU? International?)
- Mission statement and primary audiences (supporters, members, funders, media, public)
- Action hierarchy: what's the most important thing visitors should do? (donate, join, sign, attend)
- Pages required (minimum: Home, About/Über uns, Work/Themen, Join/Mitmachen, News/Aktuelles, Contact/Imprint)
- Stack preference: WordPress (more accessible for non-technical org teams) or static (Astro/Next.js for performance)
- Compliance jurisdiction — determines legal page requirements

## How It Works

### Phase 1 — Mission & Audience Strategy (~1–2 hours)
**Agent:** Strategist (with `ngo-web-design` skill)  
Focus: mission alignment, audience hierarchy, action hierarchy, legal form, compliance requirements. This is NOT a conversion funnel exercise. Output defines mobilization goals, not revenue targets.  
**Output:** `.hazn/outputs/strategy.md`

> ⏸ **CHECKPOINT** — Review mission alignment and compliance requirements before proceeding.

### Phase 2 — Legal & Compliance Checklist (~30–60 minutes)
**Agent:** Strategist  
Germany-based orgs: Impressum (§5 TMG), Datenschutzerklärung (DSGVO), Cookie consent, Accessibility statement (BITV 2.0), Satzung page, Jahresbericht link.  
International orgs: equivalent requirements scoped per jurisdiction.  
**Output:** `.hazn/outputs/compliance-checklist.md`

> ⏸ **CHECKPOINT** — Compliance scope must be locked before design. Legal pages are not optional add-ons.

### Phase 3 — Information Architecture (~1–2 hours)
**Agent:** UX Architect (with `ngo-web-design` skill)  
Structure around: transparency, trust, mobilization. Standard structure: Über uns/About, Themen/Work, Mitmachen/Join, Spenden/Donate, Aktuelles/News, Kontakt/Presse. Mandatory: full transparency footer (Satzung, Jahresbericht, Finanzen, Impressum, Datenschutz).  
**Output:** `.hazn/outputs/ux-blueprint.md`

### Phase 4 — Copy + Wireframes (parallel, ~2–4 hours each)
**Agent (Copy):** Copywriter (with `ngo-web-design` skill)  
Tone: trustworthy, warm, urgent but not manipulative. No startup-speak. No growth-hacking language.  
**Agent (Wireframe):** Wireframer — optional but recommended for board approval  
**Outputs:** `.hazn/outputs/copy/`, `.hazn/outputs/wireframes/`

> ⏸ **CHECKPOINT** — Get board/stakeholder approval on wireframes before development. NGO boards often have strong opinions about presentation.

### Phase 5 — Development (~2–5 days)
**Agent:** Developer  
CMS options: WordPress (easier for non-technical org staff to maintain) or static (Astro/Next.js for performance). Must include: Impressum page, Datenschutz page, accessibility statement, cookie consent, privacy-friendly analytics (Matomo or Plausible — not GA4 for DSGVO-strict orgs).  
**Output:** Built site at staging URL, `dev-progress.md`

### Phase 6 — Accessibility Audit (~1–2 hours) — MANDATORY
**Agent:** Auditor  
WCAG 2.1 AA minimum. Checks: keyboard navigation, screen reader compatibility, color contrast ratios, heading hierarchy, focus indicators, alt text. This is a mandatory gate for NGOs — especially German ones subject to BITV 2.0.  
**Output:** `.hazn/outputs/accessibility-report.md`

> ⏸ **CHECKPOINT** — Accessibility must pass before launch. Non-compliance exposes German public bodies and some NGOs to legal risk.

### Phase 7 — SEO & Discoverability (~1–2 hours)
**Agent:** SEO Specialist  
Focus: political education content discoverability, schema for Organization/Event/Person, RSS feed for journalists, sitemap, GEO (generative engine visibility for AI citations).  
**Output:** `seo-checklist.md`

## HITL Checkpoints

| Checkpoint | Why it matters / risk of skipping |
|---|---|
| After strategy | NGO strategy misaligned to mission = wrong page structure, wrong CTAs, wrong tone. Correcting this after UX is done means full IA rework. |
| After compliance checklist | Missing Impressum or DSGVO-compliant Datenschutz on a German org site is an immediate legal liability. Scoping this after design wastes redesign effort. |
| After wireframes | NGO boards and governance bodies often require sign-off on visual presentation. Skipping this causes political friction post-build that delays launch by weeks. |
| After accessibility audit | BITV 2.0 non-compliance for publicly funded German NGOs is a legal violation, not just best practice. Catching this before launch is far cheaper than retrofitting. |

## Caveats & Gotchas

- **Never apply B2B framing to an NGO.** No "conversion funnels," no "ROI," no "growth hacking." The Strategist and Copywriter must both load the `ngo-web-design` skill — not `b2b-marketing-ux`.
- **GA4 is problematic for DSGVO-strict German NGOs** — use Matomo (self-hosted) or Plausible as the default analytics choice. Document this decision in compliance-checklist.md.
- **WordPress is often the right choice** even though it's not the developer's preference — NGO staff need to update news and events without developer help. Evaluate this honestly before choosing Next.js.
- **Donation integration** (e.g., Stripe, Fundraisingbox, Altruja) is a separate scoping item. The workflow does not include payment integration by default — add it explicitly.
- **Multilingual sites** (EN + DE + others) significantly increase timeline. The standard estimate assumes one language.
- **Member portal features** (login, member management, event registration) are not included in the standard workflow. Scope separately.
- Accessibility audit uses the Auditor with a WCAG-focused brief — not a specialized a11y tool. For BITV 2.0 formal compliance certification, a dedicated accessibility audit firm may still be needed.

## Outputs

```
projects/{client}/
├── state.json
├── strategy.md
├── compliance-checklist.md
├── ux-blueprint.md
├── copy/
│   ├── homepage.md
│   ├── about.md
│   ├── themen.md
│   ├── mitmachen.md
│   └── impressum.md
├── wireframes/
│   └── *.html
├── dev-progress.md
├── accessibility-report.md
└── seo-checklist.md
```

## Example Trigger

```
/hazn-ngo
Organisation: Demokratie Jetzt e.V.
Legal form: eingetragener Verein (e.V.), Germany
Mission: Political education and civic participation
Primary audiences: Young people (18–35), educators, funders
Key action: Sign up for events and newsletter
Stack preference: WordPress (org staff must be able to edit)
Compliance: German (DSGVO, BITV 2.0, TMG)
```

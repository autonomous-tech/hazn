# Quick Landing Page

> Fast path for a single landing page — brief → structure → copy → build, no strategy document required.

## When to Use

- One-time offer, campaign, or event landing page
- Paid ad destination that needs to go live quickly (4–8 hours)
- Testing a new service or positioning before committing to a full site build

**NOT for:**
- Multi-page websites → use `/hazn:website`
- Situations where the offer, audience, or positioning are unclear — run `/hazn:strategy` first
- NGO or institutional landing pages with compliance requirements → use `/hazn:ngo`

## Requirements

- The offer: what is being promoted?
- The audience: who is this page for?
- The desired action: what should visitors do? (book a call, fill a form, download, buy)
- Brand guidelines or existing site to match (if applicable)
- Form/CRM destination if a form is needed

## How It Works

### Phase 1 — Quick Brief (~15 minutes)
Capture the offer, audience, desired action, and brand context. No strategy document needed — this is a brief, not a discovery session.

### Phase 2 — Page Structure (~30 minutes)
**Agent:** UX Architect  
Define 5–7 sections, outline content needs per section. Output is a lean landing blueprint — no full site map.  
**Output:** `.hazn/outputs/landing-blueprint.md`

### Phase 3 — Copy (~1–2 hours)
**Agent:** Copywriter  
Headlines and subheads, body copy per section, CTA copy, social proof framing.  
**Output:** `.hazn/outputs/copy/landing.md`

### Phase 4 — Build (~2–4 hours)
**Agent:** Developer  
Single page component, responsive design, form handling (if needed), basic SEO meta.  
**Output:** `app/landing/page.tsx` (Next.js) or equivalent

## HITL Checkpoints

| Checkpoint | Why it matters / risk of skipping |
|---|---|
| Brief confirmation | Spending 2–4 hours building the wrong offer for the wrong audience. Landing pages live or die on targeting — 15 minutes confirming the brief prevents a full rebuild. |

## Caveats & Gotchas

- This workflow intentionally skips wireframes and keyword research. If stakeholder approval is needed before build, add a wireframe step manually — it takes 30 minutes and prevents costly dev revisions.
- Form handling is scaffolded, not production-wired. The developer builds the form component; connecting it to HubSpot, Mailchimp, or a custom API requires explicit instruction.
- No QA gate is built into this workflow. If the page is going to paid traffic, run a manual browser check (mobile + desktop) before activating campaigns.
- SEO is minimal — basic meta tags only. If this page needs to rank, escalate to `/hazn:website` for a full SEO pass.
- Speed is the point. If the brief is incomplete or the offer is unclear, don't guess — ask before building.

## Outputs

```
.hazn/outputs/
├── landing-blueprint.md
└── copy/
    └── landing.md
app/
└── landing/
    └── page.tsx
```

## Example Trigger

```
/hazn:landing
Offer: Free 30-minute audit call for SaaS companies
Audience: Founders and VPs of Sales at Series A SaaS (10–50 employees)
Action: Book a call via Calendly
Brand: Match acmeconsulting.com
```

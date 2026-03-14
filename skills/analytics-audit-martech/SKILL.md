---
name: MarTech & Attribution Audit
description: >
  This skill should be used when the user asks to "audit attribution", "analyze martech stack",
  "evaluate CDP", "audit ad platform integration", "check server-side tracking",
  "review conversion setup", "build implementation roadmap", or wants Phase 2 of a
  MarTech audit. It guides the full MarTech stack analysis, attribution architecture
  design, and implementation roadmap for Shopify stores.
version: 1.0.0
---

# MarTech & Attribution Audit — Phase 2

Expand a Phase 1 GA4 audit into a comprehensive MarTech & Attribution assessment. This produces sections K-P of the full audit report. Steps 5-11 below continue from the GA4 & Site Inspection Audit skill (Steps 1-4).

Refer to `.hazn/skills/analytics-audit/references/report-template.md` for the expected output structure of sections K-P.

## Step 0: Audience — Ask First (if not already set in Phase 1)

If the audience wasn't established during Phase 1, ask now. Read `~/hazn/skills/references/audience-routing.md` for the full routing spec. Then ask:

> **Who is this report for?**
>
> 1. 👔 **Business Executive** — ROI framing, plain English, impact/effort badges, no jargon
> 2. 🔧 **Technical Team** — Full metrics, code examples, implementation detail
> 3. 📋 **Both** — Executive summary first, then technical appendix

Apply the appropriate output mode throughout all sections.

---

## Prerequisites

Phase 1 must be complete with:
- `.hazn/outputs/analytics-audit/ga4_audit_data.json` — GA4 property data
- `.hazn/outputs/analytics-audit/ga4_audit_extra.json` — Extended engagement/browser/keyword data
- `.hazn/outputs/analytics-audit/site_inspection.json` or site inspection notes — tracking code inventory
- `.hazn/outputs/analytics-audit/<domain>-audit.md` — Phase 1 report (sections A-J)

## Step 5: MarTech Stack Audit (Section K)

Build a complete inventory of every marketing technology tool on the site.

### Technology Layers to Document

| Layer | What to Look For |
|-------|-----------------|
| Tag Management | GTM containers (how many? who installed each?), Shopify Web Pixels Manager, direct gtag.js |
| Web Analytics | GA4 (property ID, measurement ID), any legacy UA |
| CRM / Marketing | HubSpot (portal ID — which is primary?), Salesforce, etc. |
| Ad Platforms | Google Ads (conversion labels), Meta Pixel + CAPI status, Bing UET, TikTok, etc. |
| Session Recording | Hotjar, Microsoft Clarity, FullStory, Lucky Orange — flag redundancies |
| Call Tracking | CallRail, CallTrackingMetrics — does it pass click IDs to CRM? |
| Chat / Sales Bot | Memox, Intercom, Drift, Tidio — is it a lead capture tool or full sales channel? |
| Invoicing / ERP | Method, QuickBooks, NetSuite — where does offline revenue live? |
| Email Marketing | HubSpot email, Mailchimp, Klaviyo — flag redundancies with CRM |
| Fraud Detection | TrafficGuard, ClickCease, etc. |
| Other | Country blockers, review widgets, A/B testing tools |

### Data Flow Map
Create an ASCII diagram showing how data flows between systems. Key questions:
- Which systems talk to each other?
- Where are the dead ends (data goes in but never comes back)?
- Which revenue channels are invisible to ad platforms?

### Redundancy Analysis
Identify tools that overlap and recommend consolidation.

## Step 6: Attribution Architecture (Section L)

### Current State Analysis
Document every close/revenue channel and whether it feeds back to ad platforms:

| Close Channel | Revenue Visible? | Pixel Feedback? | Attribution Status |
|---------------|-----------------|----------------|-------------------|
| Shopify auto-checkout | Yes | Yes | Working |
| [Bot/chat sales] | ? | None | BLIND SPOT |
| [Phone/call tracking] | ? | None | BLIND SPOT |
| [Invoiced/B2B sales] | ? | None | BLIND SPOT |

### Root Cause Analysis
Document each specific reason attribution is broken. Common patterns:
1. Client-side only tracking (degraded by ITP, ad blockers)
2. No server-side events (Enhanced Conversions, CAPI)
3. Revenue in multiple siloed systems
4. Chat bot as full sales channel but invisible to ads
5. No offline conversion import loop
6. UTM parameter chaos (same platform, multiple source/mediums)
7. Inflated GA4 conversions feeding garbage to Smart Bidding
8. CRM attribution capabilities unused
9. Multiple CRM portals / accounts creating confusion

### Signal Loss Quantification
Calculate from browser data:
- Safari % of total sessions (ITP impact)
- Desktop % (ad blocker exposure)
- Estimated % of conversions invisible to ad platforms

### CAPI / Server-Side Status
Check what's already partially implemented:
- Shopify Trekkie S2S (`facebookCapiEnabled`)
- Any sGTM endpoints
- Enhanced Conversions for Leads
- Bing offline import

### Ideal Architecture Design
Design the target-state with ALL revenue channels feeding back through the CRM to ad platforms.

Key principle: **CRM becomes single source of truth. Every close channel writes to CRM. CRM exports offline conversions with revenue to ad platforms.**

## Step 7: CDP Evaluation (Section M)

Evaluate whether the client needs a Customer Data Platform.

### Decision Framework

**Lean toward NO CDP if:**
- <100K sessions/month
- <4 major data sources
- CRM already has workflow automation (HubSpot Pro/Enterprise)
- sGTM can handle event routing
- The real problem is missing plumbing, not identity stitching

**Lean toward CDP if:**
- >500K sessions/month
- 6+ data sources with separate identity systems
- Complex identity stitching beyond CRM capabilities
- Need real-time event routing at scale
- CRM workflows can't handle the data volume

### Options to Evaluate
Always compare these three tiers:
1. **CRM as pseudo-CDP** (cheapest, fastest) — e.g., HubSpot + sGTM
2. **Mid-tier CDP** (cost-effective) — e.g., RudderStack ($500-2K/mo)
3. **Enterprise CDP** (gold standard) — e.g., Segment ($120K+/year)

## Step 8: Google Ads Optimization (Section N)

### Conversion Action Audit
From the Shopify Web Pixels Manager config, map every event that sends to Google Ads:
- List each event type with its Ads conversion label
- Identify which are primary vs secondary
- Flag non-conversions being sent as conversions (view_item, page_view, search)
- Calculate signal-to-noise ratio

### Recommended Restructuring
Define:
- **Primary conversions** (purchase, qualified_lead, offline_purchase) — bidding optimizes toward these
- **Secondary conversions** (observe only) — add_to_cart, begin_checkout, phone_call
- **Remove entirely** — view_item, page_view, search, any engagement-level events

### Enhanced Conversions & Offline Import
Design the implementation for:
- Enhanced Conversions for Leads (hash email/phone on form submit)
- Offline conversion import from CRM (gclid + revenue on deal close)
- Value-based bidding recommendations per campaign type

## Step 9: Channel Attribution & Reporting (Section O)

### GA4 Attribution
- Attribution model recommendation (usually Data-Driven)
- Lookback window settings (90d for high-ticket)
- Google Signals status

### CRM Attribution
- Multi-touch attribution report configuration
- Revenue attribution by source setup
- Ads integration for spend data

### Custom Channel Grouping
Design channel groups that consolidate fragmented sources (especially Facebook multi-source splits).

### First-Party Data Strategy
- Click ID persistence (gclid/fbclid/msclkid in cookies + CRM)
- Email-based matching (Enhanced Conversions, Advanced Matching)
- Server-side cookie writing

## Step 10: Implementation Roadmap (Section P)

Build a phased 90-day plan:

### Week 1-2: Stop the Bleeding
Fix the things actively harming ad performance RIGHT NOW:
- Remove false conversions from Google Ads
- Fix key event definitions in GA4
- Fix timezone
- Remove redundant tools

### Week 3-4: Server-Side Foundation
Set up the infrastructure:
- sGTM via Stape on first-party subdomain
- Meta CAPI (full events, not just checkout)
- Google Enhanced Conversions for Leads
- Bing UET server-side
- UTM standardization
- GTM container consolidation

### Week 5-6: Offline Conversion Loop (The Big Unlock)
Connect all revenue channels back to ad platforms:
- Click ID capture + CRM storage
- Bot → CRM integration
- Call tracking → CRM integration
- Invoice system → CRM deal sync
- CRM → Google Ads offline import
- CRM → Meta offline import
- CRM → Bing offline import

### Week 7-8: Attribution & Reporting
Build the measurement layer:
- CRM multi-touch attribution
- GA4 custom channel groups + custom dimensions
- Audiences for remarketing
- Missing e-commerce events

### Week 9-12: Optimize & Scale
Leverage clean data:
- Executive dashboard (Looker Studio)
- Value-based bidding in Google Ads
- Consent Mode v2 proper implementation
- Script bloat reduction
- Data quality alerting

### Deliverable Format
Each task should have: task #, description, owner, effort estimate, impact statement.
Include cost summary and expected ROI table.

---

## Design System

All HTML output for sections K-P must use the **Stone/Amber** design system. This ensures visual continuity with Phase 1 and the teaser report.

### Colors

```css
:root {
  /* Base palette — Stone */
  --stone-50: #fafaf9;    --stone-100: #f5f5f4;   --stone-200: #e7e5e3;
  --stone-300: #d6d3d1;   --stone-400: #a8a29e;   --stone-500: #78716c;
  --stone-600: #57534e;   --stone-700: #44403c;   --stone-800: #292524;
  --stone-900: #1c1917;

  /* Accent — Amber */
  --amber-400: #fbbf24;   --amber-500: #f59e0b;   --amber-600: #d97706;

  /* Severity */
  --red-500: #ef4444;     --red-100: #fee2e2;
  --amber-100: #fef3c7;
  --green-500: #22c55e;   --green-100: #dcfce7;
  --blue-500: #3b82f6;    --blue-100: #dbeafe;
}
```

### Typography

```css
/* Import — always include this at the top of the <style> block */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap');

/* Headings */
font-family: 'Source Serif 4', Georgia, serif;

/* Body */
font-family: 'Inter', system-ui, -apple-system, sans-serif;
```

### Component Standards

Use these shared component classes inherited from the client-report skill:
`.section`, `.section--dark`, `.finding`, `.finding--warn`, `.finding--good`, `.tool-card`, `.tool-card__dot--red/amber/green`, `.callout`, `.callout--danger`, `.stat-strip`, `.metric-card`, `.data-table`

> ⚠️ Always set `color: var(--stone-800)` explicitly on `.finding`, `.before`, `.after` — light-background components inside `.section--dark` will bleed white text without it.

### CTA Button

```css
.cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2.5rem;
  background: var(--amber-500);
  color: var(--stone-900);
  font-weight: 700;
  font-size: 1.1rem;
  border-radius: 8px;
  text-decoration: none;
  transition: background 0.2s, transform 0.2s;
  white-space: nowrap;
  box-shadow: 0 6px 24px rgba(245,158,11,0.35);
}
.cta-btn:hover { background: var(--amber-600); transform: translateY(-2px); }
```

---

## CTA Strategy — Implementation-Hire Framing

> **All CTAs must link to:** `https://calendly.com/rizwan-20/30min`
>
> Frame every recommendation as "let's implement this together" — not "you should fix this."
> Never say "this takes 30 mins" or "a quick 2-hour fix." Use effort levels only: **Low / Medium / High**.

### Micro-Upsell Callouts

Each major section (K-P) must end with a micro-upsell `.callout` block naming the exact implementation service and linking to Calendly. Use this HTML pattern:

```html
<div class="callout callout--cta" style="background: var(--amber-100); border-left: 4px solid var(--amber-500); padding: 1.25rem 1.5rem; border-radius: 8px; margin-top: 2rem;">
  <p style="margin: 0; font-size: 0.95rem; color: var(--stone-800);">
    🔗 <strong>Attribution Architecture</strong> — We design and implement your full multi-touch
    attribution model. <a href="https://calendly.com/rizwan-20/30min" style="color: var(--amber-600); font-weight: 600;">Book a 20-min call to map it out →</a>
  </p>
</div>
```

#### Required Micro-Upsells by Section

| Section | Emoji | Service Name | Framing |
|---------|-------|-------------|---------|
| K — MarTech Stack | 🧰 | *MarTech Stack Consolidation* | We audit, rationalise, and rewire your stack into a clean, non-redundant setup. |
| L — Attribution Architecture | 🔗 | *Attribution Architecture* | We design and implement your full multi-touch attribution model. Book a 20-min call to map it out → |
| M — CDP Evaluation | 🔄 | *CDP Integration* | Connects your tools into a single customer view. We scope and implement the right tier for your volume. Book a call → |
| N — Google Ads | 🎯 | *Google Ads Conversion Setup* | We restructure your conversion actions, wire Enhanced Conversions, and configure offline import. Book a call → |
| O — Channel Attribution | 📊 | *Attribution & Reporting Build* | We build the CRM attribution model, GA4 channel groups, and Looker Studio dashboard. Book a call → |
| P — Implementation Roadmap | ⚙️ | *Server-Side Tracking Implementation* | Removes ad blockers from your signal loss equation. We handle sGTM, CAPI, and the full offline conversion loop. Book a call → |

### Final Section CTA (End of Section P)

Section P must close with a **full-width dark CTA block**:

```html
<section class="section section--dark" style="text-align: center; padding: 8rem 2rem; background: var(--stone-900);">
  <p class="section__label" style="color: var(--amber-400); font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 1rem;">
    Ready to fix this?
  </p>
  <h2 style="font-family: 'Source Serif 4', Georgia, serif; font-size: 2.25rem; color: #fff; max-width: 640px; margin: 0 auto 1.25rem;">
    Your MarTech stack is only as good as its implementation. Let's audit it together.
  </h2>
  <p style="color: var(--stone-400); max-width: 520px; margin: 0 auto 2.5rem; font-size: 1.05rem; line-height: 1.6;">
    We've identified the gaps. The next step is a 20-minute call to walk through your stack live — and scope exactly what we'd implement first.
  </p>
  <a href="https://calendly.com/rizwan-20/30min" class="cta-btn">
    Book a 20-min call →
  </a>
</section>
```

---

## Step 10.5: Write Phase 2 Report Sections (K-P)

Append sections K-P to the existing Phase 1 report at `.hazn/outputs/analytics-audit/<domain>-audit.md`. Follow the section structure defined in `.hazn/skills/analytics-audit/references/report-template.md`. Use the `analytics-report-writer` agent for full report generation if both phases are being written together.

## Step 11: Run Adversarial Review

After the full report is written, launch the `analytics-adversary` agent to red-team the report:
> Red-team the audit report at .hazn/outputs/analytics-audit/<domain>-audit.md against the data files

The adversary will challenge every number, flag weak claims, and find inconsistencies. Fix any valid issues before delivering to the client.

---

## Quality Checklist

Before finalising sections K-P, verify:

- [ ] **All CTAs use** `https://calendly.com/rizwan-20/30min` — no other Calendly or booking URL
- [ ] **Micro-upsell callouts** present at the end of each major section: K (MarTech), L (Attribution), M (CDP), N (Google Ads), O (Channel Attribution), P (Roadmap)
- [ ] **Implementation framing** — every recommendation ends with "we can implement this" not just "you should fix this"
- [ ] **No time estimates** — use effort levels only: **Low / Medium / High** (never "30 mins", "a quick fix", "a few hours")
- [ ] **Stone/Amber design system** applied — Stone-50/900 palette, Amber-400/500/600 accents, severity colors
- [ ] **Typography** — `Inter` for body, `Source Serif 4` for headings, Google Fonts import at top of `<style>`
- [ ] **Scroll reveal** — `IntersectionObserver` fade-in-up (`.reveal` class: `opacity 0→1` + `translateY(28px)→0` at `0.6s ease`) on all new component sections (tool grid, findings, stat strips, roadmap cards)
- [ ] **Hover states** on tool cards and finding cards — smooth `0.2s` transition with `translateY(-1px)` or `translateY(-2px)` lift + shadow
- [ ] **Final dark CTA block** — full-width `var(--stone-900)` section at end of Section P with Calendly link and "Let's audit it together" framing
- [ ] **No inline styles for repeated patterns** — extract to CSS classes; use utility classes for margin variations
- [ ] **Finding text contrast** — `.finding`, `.before`, `.after` always have `color: var(--stone-800)` to prevent white text on light backgrounds inside dark sections
- [ ] **Single file output** — no external dependencies except Google Fonts
- [ ] **Adversarial review passed** — `analytics-adversary` agent ran and all valid issues resolved

---

## Deployment

After generating the full audit report (Phases 1+2):

1. Save to `~/autonomous-proposals/docs/{client-slug}-analytics-audit-{date}/index.html`
2. Commit and push to `https://github.com/autonomous-tech/autonomous-proposals` (main branch)
3. Cloudflare Pages auto-deploys to `https://docs.autonomoustech.ca/docs/{client-slug}-analytics-audit-{date}/`
4. Use the **SHARE** button (auto-injected by GitHub Actions) to generate a 30-day shareable link via `share.autonomoustech.ca`
5. Share the link with the client

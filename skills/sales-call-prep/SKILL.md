---
name: sales-call-prep
description: Create branded sales strategy documents and call prep guides for prospect meetings. Use when preparing for sales calls, client pitches, partnership meetings, cold outreach prep, or prospect conversations. Generates two HTML deliverables — a strategy doc (research, financials, objection handling) and a call guide (minute-by-minute conversation script with discovery questions). Styled with Autonomous brand guide.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
---

# Sales Call Prep

Generate two branded HTML documents for sales meetings:

1. **Strategy Doc** — Deep research, financial model, service fit, objection handling, risk analysis
2. **Call Guide** — Minute-by-minute conversation script, discovery questions, positioning, close

## Process

### 1. Gather Intel

Interview the user. Ask in batches (don't overwhelm):

**About the prospect:**
- Company name, size, revenue, industry
- Key contact (name, title, background)
- Their services, clients, tech stack
- Known pain points or intent signals
- How the meeting was set up (warm/cold, context)

**About the pitch:**
- What services are we pitching?
- What's our differentiator for this prospect?
- Ideal engagement size and model (retainer, project, audit)
- Have we worked with similar companies?
- What's the goal of this meeting? (close, qualify, learn, position)

**About the call:**
- How long is the call?
- Who's on their side?
- What do THEY think the meeting is about?

If the user provides a research doc, analyze it and ask targeted follow-ups only.

### 2. Research

If not already provided:
- `web_search` the prospect company, key contact, recent news
- `web_fetch` their website, services page, case studies
- Check LinkedIn profiles if accessible
- Note: tech stack clues, client logos, positioning language

### 3. Generate Strategy Doc

Build the HTML strategy document. Load `assets/template-strategy.html` as the base template. See `references/doc-structure.md` for section structure and content guidance.

Key sections: Executive Summary → Company Overview → The Gap → Service Opportunities → Financial Impact → Engagement Plan → Objection Handling → Risk Factors

### 4. Generate Call Guide

Build the HTML call guide. Load `assets/template-call.html` as the base template. See `references/doc-structure.md` for section structure.

Structure the call as time blocks based on total call length:
- **10% Open** — Rapport, warm-up
- **50% Discover** — Questions that get them talking (aim for 70/30 talk ratio)
- **20% Position** — Mirror their pain back, then 60-second pitch
- **13% Offer** — Zero-risk next step (free audit, sample, etc.)
- **7% Close** — Lock next meeting, get email, confirm deliverable

### 5. Save & Deliver

Save both documents to the autonomous-proposals repo:

```bash
# Save documents
mkdir -p ~/clawd/autonomous-proposals/sales-prep
# Write strategy: ~/clawd/autonomous-proposals/sales-prep/{prospect}-strategy-{date}.html
# Write call guide: ~/clawd/autonomous-proposals/sales-prep/{prospect}-call-guide-{date}.html

# Deploy to docs site
cd ~/clawd/autonomous-proposals
git add sales-prep/
git commit -m "Add {prospect} sales prep docs"
git pull --rebase origin main && git push origin main
```

**URLs:**
- Strategy: `https://docs.autonomoustech.ca/sales-prep/{prospect}-strategy-{date}.html`
- Call Guide: `https://docs.autonomoustech.ca/sales-prep/{prospect}-call-guide-{date}.html`

**Alternative:** Use `canvas action=present` to display documents inline if immediate preview is needed.

## Key Principles

- **Ask, don't assume.** Interview the user thoroughly before generating.
- **Mirror prospect's language.** Use their terminology, not generic consulting-speak.
- **Discovery > Pitching.** The call guide should be 50%+ questions.
- **Price for value, not cost.** Never position as the cheap option.
- **Always include a zero-risk offer.** Free audit, sample, Blueprint — lower the barrier.
- **Adapt to call length.** Scale sections proportionally.

## References

- `references/doc-structure.md` — Detailed section templates for both documents
- `references/brand.md` — Colors, fonts, CSS variables, component styles
- `references/discovery-frameworks.md` — Question frameworks by industry/scenario

## Assets

- `assets/template-strategy.html` — Base HTML template for strategy docs
- `assets/template-call.html` — Base HTML template for call guides

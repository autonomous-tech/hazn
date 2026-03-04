# Hazn Augmentation Plan
*Synthesizing agency-agents strengths into our B2B delivery system*

---

## Guiding Principle

We don't copy what they built. We take **their patterns** and apply them **to our domain**.
They're wide + personality-rich. We're deep + infrastructure-rich.
The goal: keep our depth, add their quality culture and missing functional coverage.

---

## Phase 1 — Quality Culture (Week 1)
*Biggest gap. Zero QA today. This breaks the delivery chain.*

### 1A. Build `qa-tester.md` sub-agent
Inspired by their Evidence Collector + Reality Checker, but B2B website-specific.

**What it does:**
- Takes a built URL (localhost or live)
- Screenshots desktop / tablet / mobile via browser tool
- Checks: responsive layout, CTA visibility, form function, Core Web Vitals, accessibility, meta tags
- Default posture: "find 3-5 issues" — no more fantasy sign-offs
- Outputs `projects/{client}/qa-report.md` + screenshots
- Blocks developer handoff until QA passes

**Trigger:** Auto-spawned after Developer completes — before SEO, before any client presentation

### 1B. Add QA checkpoint to WORKFLOWS.md + SOUL.md
Insert QA gate between Developer → SEO Specialist in the `/website` workflow.
No exceptions. This is a process change, not just a new agent.

### 1C. Add "Reality Check" mindset to Developer sub-agent
Add self-check section: before completing, run own checklist. Don't hand off broken work.

---

## Phase 2 — Personality Layer (Week 1-2)
*Their agents have character. Ours are technical briefs. Models follow personality cues.*

### 2A. Add Identity blocks to all sub-agents

Each sub-agent gets a `## 🧠 Identity & Memory` section:
- Role + one-line personality description
- A belief/mantra that drives their decisions
- What they've "seen fail" (experience heuristics)
- How they communicate (tone, format preferences)

**Example for Strategist:**
> You're **the Strategist** — a market positioning specialist who's seen too many B2B websites that talk about themselves instead of the buyer's problem. You default to customer language, not founder language. You ask "so what?" after every claim.

**Example for Developer:**
> You're **the Developer** — a Next.js engineer who ships clean, typed, semantic code. You've seen too many "quick fixes" that become technical debt. You don't pass broken builds. You test on mobile before calling anything done.

**Example for Copywriter:**
> You're **the Copywriter** — a conversion-obsessed writer who cuts every word that doesn't earn its place. You've seen too many B2B sites that lead with features and bury benefits. You write for the reader's problem, not the client's ego.

Do this for all 9 sub-agents. Low effort, measurable improvement in output quality.

---

## Phase 3 — Post-Launch Coverage (Week 2)
*We currently dead-end at "site is live." No analytics, no A/B, no iteration.*

### 3A. Build `analytics.md` sub-agent
**What it does:**
- GA4 + GTM setup (configuration audit and implementation guide)
- Conversion event mapping (form submits, CTA clicks, scroll depth)
- UTM tracking framework per campaign
- Monthly dashboard template (Looker Studio)
- Outputs `projects/{client}/analytics-setup.md`

**When spawned:** After SEO Specialist, as part of `/website` workflow final phase

### 3B. Build `conversion-specialist.md` sub-agent (upgrade from placeholder)
Currently mentioned in SOUL.md but doesn't exist.
Inspired by their Experiment Tracker — adapted for B2B CRO, not SaaS growth loops.

**What it does:**
- A/B test hypothesis generation from audit findings
- Priority matrix: what to test first (impact × confidence)
- Test design: variant brief, success metric, sample size estimate
- Monthly optimization cycle: test → learn → implement
- Outputs `projects/{client}/tests/` directory

**When spawned:** Post-launch, triggered by `/optimize` workflow

---

## Phase 4 — Engineering Breadth (Week 3)
*We dead-end if a client needs something outside Next.js/Payload*

### 4A. Build `wordpress-developer.md` — already exists, needs upgrade
Current `wordpress-developer.md` exists but may be thin. Beef it up with:
- Full WP-CLI provisioning sequence
- GeneratePress Premium setup
- ACF/block patterns
- Connects to HestiaCP tooling in TOOLS.md

### 4B. Add `devops.md` sub-agent
Lightweight — just enough for our stack:
- GitHub Actions for Cloudflare Pages deploys
- Environment variables management
- Domain + SSL setup on HestiaCP
- Staging → production promotion

This fills the gap when the Developer finishes but deployment needs attention.

---

## Phase 5 — Workflow Tightening (Week 3-4)
*Our workflow docs are good but have gaps in handoff quality*

### 5A. Add structured handoff contracts between sub-agents

Each sub-agent should document its **outputs as explicit contracts** the next agent consumes.

```
Strategist → outputs: strategy.md (sections: ICP, positioning, competitors, tone)
UX Architect → consumes: strategy.md → outputs: ux-blueprint.md (sections: page map, section briefs, CTA hierarchy)
Copywriter → consumes: strategy.md + ux-blueprint.md → outputs: copy/{page}.md
Developer → consumes: ux-blueprint.md + copy/ → outputs: built site URL + dev-progress.md
QA Tester → consumes: built site URL → outputs: qa-report.md (PASS/FAIL gate)
SEO Specialist → consumes: built site URL (post-QA) → outputs: seo-report.md + schema markup
Analytics → consumes: live URL → outputs: analytics-setup.md
```

This prevents the "I don't know what the previous agent gave me" failure mode.

### 5B. Upgrade `state.json` schema
Add: `qa_status`, `analytics_configured`, `current_agent`, `blocked_reason`

```json
{
  "client": "acme-corp",
  "phase": "qa",
  "qa_status": "pending",
  "analytics_configured": false,
  "completed_phases": ["strategy", "ux", "copy", "wireframe", "development"],
  "current_agent": "qa-tester",
  "blocked_reason": null,
  "urls": {
    "staging": "http://localhost:3000",
    "production": null
  }
}
```

### 5C. Add retry logic to orchestrator (SOUL.md)
Inspired by their AgentsOrchestrator's "max 3 retries per task" rule.
If a sub-agent comes back with QA failures, route back to Developer with specific feedback.
Orchestrator (us) manages this loop, not the user.

---

## Phase 6 — Skills We're Missing (Ongoing)
*Gaps that can be filled with skills, not sub-agents*

| Missing skill | What it covers | Source inspiration |
|---|---|---|
| `playwright-qa` | Browser automation for visual QA | Evidence Collector |
| `ga4-gtm-setup` | Analytics configuration | Analytics Reporter |
| `ab-test-design` | Test design + stat significance | Experiment Tracker |
| `devops-cloudflare` | Cloudflare Pages + Workers | DevOps Automator |
| `social-proof-research` | Competitor social, review mining | Trend Researcher |

These are skills (reusable playbooks), not full sub-agents — fits our architecture better than theirs.

---

## Summary: Build Order

| # | Deliverable | Effort | Impact |
|---|---|---|---|
| 1 | `qa-tester.md` sub-agent | Medium | 🔴 Critical |
| 2 | QA checkpoint in WORKFLOWS.md | Low | 🔴 Critical |
| 3 | Identity/personality blocks in all 9 sub-agents | Low | 🟠 High |
| 4 | `analytics.md` sub-agent | Medium | 🟠 High |
| 5 | `conversion-specialist.md` sub-agent | Medium | 🟠 High |
| 6 | Handoff contracts in sub-agent files | Low | 🟠 High |
| 7 | `state.json` schema upgrade | Low | 🟡 Medium |
| 8 | Retry logic in SOUL.md | Low | 🟡 Medium |
| 9 | `devops.md` sub-agent | Medium | 🟡 Medium |
| 10 | Missing skills (playwright-qa, ga4-gtm, etc.) | High | 🟡 Medium |

---

## What We're NOT Taking From Them

- Social media agents (Twitter, TikTok, Instagram) — not our use case
- Spatial/XR agents — not our domain
- General engineering (Mobile, AI Engineer) — out of scope
- Their personality format verbatim — we adapt it to our voice

---

## Execution Mode

**Phase 1+2:** Do now, manually — fast changes to existing files + 1 new sub-agent
**Phase 3:** Spawn sub-agents to write `analytics.md` + `conversion-specialist.md`
**Phase 4+5:** Can be parallelized with sub-agents once Phase 1+2 are live
**Phase 6:** Ongoing, skill by skill as projects need them

---
*Created: 2026-03-04 | Owner: Rizwan*

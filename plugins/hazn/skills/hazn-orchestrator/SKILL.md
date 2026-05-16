---
name: hazn-orchestrator
description: >
  Hazn project orchestrator for B2B website builds, audits, and content pipelines.
  Use when the user asks to "build a website", "run an audit", "create a landing page",
  "write blog content", "generate a case study", "create an SOW", "run an analytics audit",
  or any multi-phase marketing/web project. Also trigger on "/website", "/audit", "/landing",
  "/content", "/email", "/optimize", "/case-study", "/sow". Coordinates specialist sub-agents
  through structured workflows with handoff contracts and quality gates.
---

# Hazn Orchestrator

Read the following references before starting any project:

1. `references/soul.md` — Role, personality, agent roster, checkpoint rules
2. `references/agents.md` — Sub-agent protocol, spawning format, handoff contracts, output locations
3. `references/workflows.md` — Step-by-step playbooks for each workflow type

## Available Workflows

| Command | Workflow | Duration |
|---------|----------|----------|
| `/website` | Full website build | 1-4 weeks |
| `/audit` | Comprehensive site audit | 2-4 hours |
| `/content` | Blog content pipeline | 1-2 hrs/article |
| `/landing` | Quick landing page | 4-8 hours |
| `/email` | Email campaign design | 2-6 hours |
| `/optimize` | Post-launch optimization | Ongoing cycles |
| `/case-study` | Case study & portfolio builder | 1-3 hours |
| `/sow` | Statement of Work generator | 10-15 minutes |

## Key Rules

1. Always ask the organization type first (B2B / NGO / institutional / e-commerce) and load the right skill.
2. Never skip the QA gate. QA must pass before SEO.
3. Pause for user approval at every checkpoint (after strategy, wireframes, QA pass, email sequences, before publishing).
4. Track project state in `projects/{client}/state.json`.
5. Pass all relevant prior outputs when spawning sub-agents — context is their lifeline.
6. Spawn parallel work when dependencies allow (e.g., Copywriter + Wireframer after UX).

## Sub-Agent Templates

Sub-agent role briefs are documented in `references/agents.md`. The orchestrator composes each brief inline when spawning — no separate `agents/` directory ships with this plugin.

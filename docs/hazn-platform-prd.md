# Hazn Platform PRD

**Status:** Research & Architecture Phase
**Owner:** Rizwan Qaiser
**Date:** 2026-03-04
**Audience:** This document is written for a coding agent (Claude Code + GSD). It defines what we're building, what decisions are open, and what research tasks need to be completed before architecture is locked. Read it fully before starting any spike.

---

## Context: What Hazn Is

Hazn is a coordinated AI marketing team — 15+ specialized agents (Strategist, Copywriter, SEO Specialist, Developer, Analytics Auditor, etc.) that work together like a senior marketing team. It is not a chatbot or prompt toolkit.

Hazn is used by **Autonomous** (the company) to deliver marketing work for clients. It currently works. Agents execute workflows, produce deliverables, and ship real work. The problem is it's stateless — every engagement starts from zero.

### The Three-Layer Client Model

This is the most important context to understand before reading anything else.

```
Layer 1: AUTONOMOUS
  └── Uses Hazn internally to deliver work

Layer 2: AUTONOMOUS'S CLIENTS (e.g. a marketing agency, a B2B SaaS company)
  └── Gets deliverables from Autonomous / uses Hazn to run their own marketing
  └── Has their own brand, style, preferences, approved copy, tools

Layer 3: CLIENT'S CLIENTS (e.g. the agency's end customers)
  └── Each has their own brand, campaigns, keywords, history
  └── The client uses Hazn to serve these end customers
  └── Agents must know: "whose style am I working in, for whose end customer?"
```

**Example:** Autonomous onboards a marketing agency (Layer 2). That agency uses Hazn to run campaigns for 12 of their own clients (Layer 3). Each Layer 3 client has different brand voices, different keyword targets, different campaign histories. The agency has its own house style and methodology it applies across all of them.

This means knowledge must be scoped at two levels:
- **Agency-level (Layer 2):** house style, methodology, approved templates, tooling preferences
- **End-client-level (Layer 3):** brand voice, keyword history, campaign decisions, competitor intel, past audits

Agents need to know which scope they're operating in at runtime and pull the right context.

---

## The Core Problem

Today's Hazn agents are stateless. No memory survives between sessions. This means:
- Every engagement starts from zero
- Agents don't know past decisions for a client
- Brand voice has to be re-explained every time
- Keyword history is lost
- Agents can't improve with experience
- There's no lock-in — clients can walk

**What must be built:** A runtime where agents have persistent memory scoped to the right level (agency + end-client), dedicated tool access per agent type, and a delivery surface clients can interact with.

---

## Decisions Already Made

These are locked. Don't re-research them.

| Decision | Choice | Rationale |
|---|---|---|
| Memory approach | Letta (agent-scoped) + Knowledge Graph (org-scoped) | Both serve different needs — see architecture |
| Product type | Platform (not just a framework) | Autonomous uses it internally AND clients will access it |
| Delivery modes | Consulting-led → MCP-connected → Self-serve (in that order) | Build internal first, then power users, then UI |
| Build order | Memory layer first, then tooling/MCP, then client workspace | Can't build the right tooling until memory model is clear |

---

## Architecture

### The Knowledge Scoping Model

```
┌─────────────────────────────────────────────────────────────┐
│                     HAZN ORCHESTRATOR                        │
│  Knows: which Layer 2 client, which Layer 3 end-client      │
│  Loads: correct memory scope before spawning any agent       │
└────────────────────────────┬────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
       ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼───────┐
       │ SEO Agent   │ │  Dev Agent │ │Copy Agent  │
       │             │ │            │ │            │
       │ Letta mem.  │ │ Letta mem. │ │ Letta mem. │
       │ (agent      │ │ (agent     │ │ (agent     │
       │  craft +    │ │  craft +   │ │  craft +   │
       │  prefs)     │ │  prefs)    │ │  prefs)    │
       └──────┬──────┘ └─────┬──────┘ └────┬───────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
            ┌────────────────▼─────────────────┐
            │         KNOWLEDGE GRAPH           │
            │                                   │
            │  Agency (L2)                      │
            │  ├── house_style                  │
            │  ├── methodology                  │
            │  ├── approved_templates           │
            │  └── tooling_prefs               │
            │       │                           │
            │  End-Client (L3)                  │
            │  ├── brand_voice                  │
            │  ├── campaigns[]                  │
            │  ├── keywords[]                   │
            │  ├── decisions[]                  │
            │  ├── competitors[]                │
            │  └── audits[]                     │
            └───────────────────────────────────┘
```

### Memory Layer: Two Systems, Two Scopes

**Letta (MemGPT) — Agent-scoped**
- One Letta deployment per agent type (not per client — agents are shared, context is loaded)
- Memory blocks: `craft_knowledge`, `preferences`, `active_client_context`, `task_board`
- Archival: past work samples, patterns that worked, lessons learned across all engagements
- Auto-sync: every 10 turns or session end, Claude categorizes learnings and writes to the right block
- What this solves: agents improve their craft over time across all clients

**Knowledge Graph — Org-scoped (Layer 2 + Layer 3)**
- Models: `Agency`, `EndClient`, `Brand`, `Campaign`, `Keyword`, `Decision`, `Competitor`, `Audit`, `Content`, `ApprovedCopy`
- Relationships are temporal — tracks what changed and when
- At session start: orchestrator queries graph for relevant context, injects into agent's `active_client_context` Letta block
- What this solves: org-specific knowledge persists, accumulates, creates lock-in

**How they work together at runtime:**
```
1. Orchestrator receives task: "run SEO audit for Agency X, end-client Y"
2. Graph query: pull Agency X house style + EndClient Y keyword history + last audit
3. Inject into SEO Agent's active_client_context Letta block
4. SEO Agent runs with full context
5. Session end: new findings written back to graph (keywords, audit results)
                new craft learnings written to SEO Agent's Letta archival
```

### Agent Spaces: Tooling Per Agent

Each agent needs specific tools. These are delivered via MCP servers.

| Agent | Required Tools | Storage Scope |
|---|---|---|
| **SEO Specialist** | Ahrefs/Semrush API, GSC, PageSpeed | Keyword DB, audit history, ranking snapshots (per L3 client) |
| **Developer** | GitHub API, Vercel API, staging envs, domain mgmt | Generated code, deploy history, preview URLs (per L3 client) |
| **Blog Writer** | CMS write access (Payload/WordPress), image gen | Draft storage, content calendar, published index (per L3 client) |
| **Analytics** | GA4 OAuth, GSC, Tag Manager | Benchmark snapshots, audit outputs (per L3 client) |
| **Copywriter** | None (LLM-native) | Approved copy library, brand voice (L2 + L3 scoped) |
| **Strategist** | Web research, competitor scraping | Strategy docs, positioning decisions (per L3 client) |
| **Auditor** | Playwright, PageSpeed, crawler | Audit reports, before/after comparisons (per L3 client) |
| **Email Specialist** | ESP API (Klaviyo, Mailchimp) | Sequence library, send history (per L3 client) |

### MCP Layer

MCP servers are how agents access tools at runtime. Credentials are scoped per client.

**Priority 1 — Build or configure first:**
- `mcp-vercel` — deploy, preview, domain management
- `mcp-github` — repo management, PR creation, CI status
- `mcp-ga4` — GA4 data pull, GSC queries, benchmarks
- `mcp-pagespeed` — Core Web Vitals, performance scoring
- `mcp-hazn-memory` — read/write to Letta blocks + knowledge graph (the critical one)

**Priority 2:**
- `mcp-ahrefs` or `mcp-semrush` — keyword data, backlinks, competitor analysis
- `mcp-cms` — write to Payload CMS or WordPress
- `mcp-image-gen` — generate images for content

**Priority 3:**
- `mcp-client-workspace` — trigger workflows, manage approvals, share deliverables

### Product Delivery Modes (build order)

**Mode 1: Consulting-Led (now → 3 months)**
Autonomous team runs Hazn for clients. Clients get deliverables. Memory accumulates. No client-facing UI yet.

**Mode 2: MCP-Connected (3–6 months)**
Technical clients (agencies, founders) plug Hazn into their Claude Code / Cursor setup via MCP. Agents run in their environment, pull from shared knowledge graph. No UI needed.

**Mode 3: Self-Serve (6+ months)**
Clients get a workspace — dashboard, memory inspector, workflow trigger, HITL queue, deliverables. Requires: auth, multi-tenancy, billing, onboarding.

### Client Workspace (Mode 3 — future)

When built, this is what Layer 2 clients see:
- **Dashboard** — active projects, running workflows, deliverables
- **Memory Inspector** — what agents know about their org and their clients
- **End-Client Manager** — manage Layer 3 client profiles, brand docs, tool connections
- **Workflow Trigger** — run workflows from UI
- **HITL Queue** — approve before agents proceed
- **Deliverables** — view, approve, share outputs

---

## Research Spikes

**These must be completed before any code is written.** Each spike has a clear question, tasks, and decision criteria. Time-box strictly.

---

### Spike 1: Letta + Graph — Does the Two-System Model Actually Work?
**Question:** Can Letta's active context blocks + a knowledge graph deliver the right context to an agent at session start, reliably, for both L2 and L3 scopes?

**Tasks:**
1. Run agent-os locally (`docker compose up` in `/home/rizki/autonomous-agent-os` or clone `autonomous-tech/autonomous-agent-os`)
2. Deploy one Hazn agent (SEO Specialist) into agent-os
3. Create a fake Agency (L2) with house style + 2 fake EndClients (L3) with keyword history
4. At session start: query the graph for L2 + L3 context, inject into agent's `active_client_context` block
5. Run a workflow. After session end, write findings back to graph.
6. Run a second session. Does the agent have the right context? Does it NOT bleed L3 client A's data into L3 client B?

**Decision criteria:**
- Context injection works cleanly → proceed with two-system model
- Context bleeds across clients OR injection is too slow/complex → simplify to single system

**Time box:** 2 days

---

### Spike 2: Knowledge Graph — Graphiti vs Neo4j vs Postgres+pgvector

**Question:** Which technology for the knowledge graph?

**Tasks:**
1. **Graphiti (Zep):** `pip install graphiti-core`. Model Agency → EndClient → Campaign → Keyword → Decision. Insert 6 months of fake data. Query: "what keywords worked for this client in Q4?" Evaluate: query quality, Python API, self-hosting, cost.
2. **Postgres + pgvector:** Same schema in Postgres. Store keyword/decision embeddings in pgvector. Query same question with hybrid search. Evaluate: does vector search cover graph traversal well enough?
3. **Neo4j:** Same schema in Cypher. Evaluate: overkill? Licensing cost?

**Decision criteria:** Simplest option that handles temporal relational queries well, can be self-hosted, and has a clean Python API.

**Time box:** 1 day

---

### Spike 3: MCP Server Inventory

**Question:** Before building MCP servers, what already exists and is usable?

**Tasks:**
1. Search MCP server registry / GitHub for: Vercel, GitHub, GA4/GSC, Ahrefs, Semrush, Payload CMS, WordPress, Klaviyo, Mailchimp, Playwright
2. For each: does it exist? Is it maintained? Does it cover our use case? Can it be self-hosted or configured without forking?
3. Build a matrix: Agent → Tool → Existing MCP (yes/no/partial) → Build effort (hours/days)

**Output:** Filled matrix. Determines build vs. configure for each tool.

**Time box:** 1 day

---

### Spike 4: Credential Architecture

**Question:** Each L2 client has different Ahrefs seats. Each L3 client has different GA4 properties, CMS logins, Vercel tokens. How do agents get the right credentials at runtime?

**Tasks:**
1. Map all credential types by agent (from Section: Agent Spaces table)
2. Evaluate three options:
   - **Option A:** Per-client env file loaded at session start (simple, doesn't scale past ~10 clients)
   - **Option B:** Credential stored in knowledge graph node, retrieved at runtime, passed as MCP env vars
   - **Option C:** OAuth token stored in client workspace, agents request via API at runtime
3. Prototype whichever looks most viable. Can agents actually receive and use injected credentials via MCP?

**Decision criteria:** Must work for L2 and L3 scope. Must work in consulting-led mode (Autonomous manages creds) and eventually self-serve (clients auth their own tools).

**Time box:** 1 day

---

### Spike 5: Agent-os — Backbone, Reference, or Ignore?

**Question:** `autonomous-tech/autonomous-agent-os` has Letta integration, MCP server, skills-to-archival loading, workspace UI. How much is reusable for Hazn?

**Tasks:**
1. Run locally: `docker compose up` (app + Letta + Postgres)
2. Deploy SEO Specialist agent from `hazn/sub-agents/seo-specialist.md`
3. Load `hazn/skills/seo-audit/SKILL.md` into archival memory at deploy time
4. Connect to a Claude Code session via `npx agent-os-mcp --url http://localhost:3000`
5. Run a fake SEO workflow. Does Letta memory persist across two separate sessions?
6. Assess: workspace UI — is it usable as the Layer 2 client dashboard or is it too generic?

**Decision criteria:**
- Memory works end-to-end AND UI is extensible → use agent-os as the backbone, extend it
- Memory works but UI is wrong → extract Letta integration code, build our own UI
- Neither works well → build from scratch using Letta SDK directly

**Time box:** 2 days

---

## What Is NOT In Scope

- Billing / subscription management
- Multi-tenant auth (needed for Mode 3, not yet)
- White-label / reseller product
- Mobile
- Real-time collaboration
- Analytics dashboard for Hazn's own performance

---

## Success Criteria for Research Phase

After all 5 spikes, you must be able to fill in this table:

| Question | Answer |
|---|---|
| Memory: Letta only, graph only, or both? | |
| Graph technology: Graphiti, Neo4j, or Postgres+pgvector? | |
| MCP: what do we build vs configure? | |
| Credential model: which option? | |
| Agent-os: backbone, reference, or ignore? | |
| L2/L3 context injection: does it work cleanly? | |

When this table is filled, produce:
1. **Architecture Decision Record (ADR)** — one page, each decision + rationale
2. **Sprint plan** — what gets built in what order, with dependencies

Research phase time box: **1 week maximum.**

---

## Repo Reference

All source files for context:

| What | Where |
|---|---|
| Hazn agents | `hazn/sub-agents/*.md` |
| Hazn workflows | `hazn/workflows/*.yaml` |
| Hazn skills | `hazn/skills/*/SKILL.md` |
| Agent-os source | `autonomous-tech/autonomous-agent-os` (GitHub) |
| Existing docs | `hazn/docs/` |
| Hazn orchestrator soul | `hazn/SOUL.md` |

# Hazn Platform PRD
**Status:** Research & Architecture Phase  
**Owner:** Rizwan Qaiser  
**Date:** 2026-03-04  

---

## 1. Vision

Hazn is a coordinated AI marketing team that delivers production-ready work for technical founders and B2B companies. It is not a chatbot, a prompt toolkit, or a single agent. It is 15+ specialized agents — Strategist, Copywriter, SEO Specialist, Developer, Analytics, and more — that work together the way a senior marketing team does.

The platform delivers work in three modes:
- **Consulting-led:** Autonomous delivers engagements using Hazn; clients get deliverables
- **Self-serve:** Clients access a workspace to trigger workflows, inspect agent memory, and run audits themselves
- **CLient's Clients:** Clients serve their own clients via hazn where they have a style that they work through themselves, but also something specific to their client.

The long-term moat is **institutional knowledge** — every engagement makes the agents smarter, and that accumulated knowledge (org-specific, client-specific, domain-specific) is hard to migrate away from.

---

## 2. The Core Problem We're Solving

Today, Hazn agents are stateless. Every engagement starts from zero. Agents have no memory of:
- Past decisions made for a client
- Brand voice and approved copy
- Keyword history and what worked
- Competitor intelligence gathered over time
- Preferences learned through iteration

This means agents can't get better over time. The work is good but not compounding. There's no lock-in. There's no platform — just a framework.

**What we need to build:** A runtime where agents have persistent memory, org-specific knowledge, dedicated tool access, and a delivery surface for clients.

---

## 3. What We're Building

### 3.1 The Memory Layer

Two complementary systems — not one or the other:

**Letta (MemGPT) — Agent-scoped memory**
- Each Hazn agent (SEO Specialist, Copywriter, etc.) gets a Letta deployment
- Memory blocks per agent: `identity`, `craft_knowledge`, `client_context`, `preferences`, `task_board`
- Archival memory: past audits, approved copy, keyword databases, campaign history
- Auto-sync: after each session, Claude categorizes learnings and writes back to the right block
- Agent gets smarter with every engagement, across all clients

**Knowledge Graph — Org-scoped relational knowledge**
- Entities: Client, Brand, Campaign, Page, Keyword, Decision, Competitor, Audit, Content
- Relationships: Client → Campaigns → Keywords → Decisions → Approved Copy
- Temporal: tracks what changed, when, and why
- Powers: "what keywords have we targeted for this client before?", "what brand decisions are locked?", "what did the last audit find?"
- Candidate: Graphiti (Zep) or Neo4j — **this is a research spike (see Section 6)**

### 3.2 Agent Spaces

Each agent type needs a dedicated execution environment with its own tooling:

| Agent | Tools Needed | Storage Needed |
|---|---|---|
| **SEO Specialist** | Ahrefs/Semrush API, Google Search Console, PageSpeed | Keyword DB, audit history, ranking snapshots |
| **Developer** | GitHub API, Vercel API, staging environments, domain management | Generated code, deploy history, preview URLs |
| **Blog Writer** | CMS write access (Payload, WordPress), image gen | Draft storage, published content index, content calendar |
| **Analytics** | GA4 OAuth per client, GSC, Tag Manager | Benchmark snapshots, audit outputs, report history |
| **Copywriter** | None (LLM-native) | Approved copy library, brand voice store, A/B variants |
| **Strategist** | Web research, competitor scraping | Strategy docs, positioning decisions, audience intel |
| **Auditor** | Playwright (screenshots), PageSpeed, crawler | Audit reports, before/after comparisons |
| **Email Specialist** | ESP API (Klaviyo, Mailchimp, etc.) | Sequence library, performance history |

### 3.3 The MCP Layer

MCP servers are how agents access their tools. We need to build:

**Priority 1 — Foundation MCPs:**
- `mcp-vercel` — deploy, preview, domain management
- `mcp-github` — repo management, PR creation, CI status
- `mcp-ga4` — GA4 data pull, GSC queries, benchmarks
- `mcp-pagespeed` — Core Web Vitals, performance scoring

**Priority 2 — SEO & Content MCPs:**
- `mcp-ahrefs` or `mcp-semrush` — keyword data, backlinks, competitor analysis
- `mcp-cms` — write to Payload CMS or WordPress
- `mcp-image-gen` — generate images for content

**Priority 3 — Client Delivery MCPs:**
- `mcp-hazn-memory` — read/write to Letta + knowledge graph (bridges agents to persistent memory)
- `mcp-client-workspace` — trigger workflows, share deliverables, manage approvals

### 3.4 The Client Workspace

What clients (or the Autonomous team running engagements) actually interact with:

- **Dashboard** — active projects, running workflows, recent deliverables
- **Memory Inspector** — view what the agents know about your org (brand voice, decisions, keyword history)
- **Workflow Trigger** — run `/analytics-teaser`, `/audit`, `/content` etc. from UI
- **Deliverables** — view, approve, share outputs (audit reports, pages, content)
- **Agent Activity** — what's running, what completed, what needs human review
- **HITL Queue** — approvals required before agents proceed

### 3.5 Institutional Knowledge = The Moat

What accumulates over time and creates lock-in:

- **Brand knowledge:** approved tone, copy patterns, visual language, what's been rejected and why
- **Keyword intelligence:** what's been targeted, what ranked, what failed, competitive gaps
- **Decision log:** every strategic choice made, with rationale
- **Audience intelligence:** ICP refinements, messaging that resonated
- **Technical preferences:** stack decisions, component patterns, deploy configurations
- **Audit baselines:** before/after data across all site changes

This data, structured in a knowledge graph and linked to agent memory, is what makes Hazn more valuable at month 6 than month 1 — and painful to leave.

---

## 4. Product Modes

### Mode 1: Consulting-Led (now)
Autonomous team uses Hazn to deliver client work. Clients get deliverables. Agents accumulate knowledge per client. This is the current model — extend it with memory and tooling.

### Mode 2: Self-Serve (future)
Clients get a workspace. They trigger workflows, inspect memory, approve outputs. Requires: auth, multi-tenancy, billing, onboarding flow.

### Mode 3: MCP-Connected (future)
Hazn exposes an MCP server. Technical founders plug it into their own Claude Code / Cursor workflow. Agents run in their environment, pull from shared knowledge graph. No UI needed.

**The build order:** Mode 1 → Mode 3 → Mode 2. Start with internal use, then enable technical power users via MCP, then build self-serve UI.

---

## 5. Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   CLIENT WORKSPACE                   │
│         Dashboard | Memory | Workflows | HITL        │
└─────────────────────────┬───────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────┐
│                  HAZN ORCHESTRATOR                   │
│         Spawns agents, manages workflows,            │
│         handles checkpoints, routes outputs          │
└──────┬──────────────────┬────────────────┬──────────┘
       │                  │                │
┌──────▼──────┐  ┌────────▼──────┐  ┌──────▼──────┐
│   AGENT     │  │    AGENT      │  │   AGENT     │
│  SEO Spec.  │  │  Developer    │  │  Copywriter │
│             │  │               │  │             │
│ Letta mem.  │  │  Letta mem.   │  │  Letta mem. │
│ + MCP tools │  │  + MCP tools  │  │  + MCP tools│
└──────┬──────┘  └───────┬───────┘  └──────┬──────┘
       │                 │                  │
       └─────────────────┼──────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│              KNOWLEDGE GRAPH (org-scoped)            │
│   Client → Brand → Campaigns → Keywords → Decisions  │
│                  Graphiti / Neo4j                    │
└─────────────────────────────────────────────────────┘
```

---

## 6. Research Spikes (What GSD Needs to Figure Out)

These are open questions that must be answered before architecture gets locked. Each is a time-boxed research task.

### Spike 1: Letta vs Knowledge Graph — Complementary or Pick One?
**Question:** Letta handles agent-scoped memory well (preferences, craft knowledge). A graph handles org-scoped relational knowledge (client → campaigns → decisions). Do we need both? Does Letta's archival memory (with semantic search) cover the graph use case well enough?  
**Research tasks:**
- Build a toy Letta deployment. Store 3 months of fake SEO audit history. Query it. Does it surface the right things?
- Build the same in Graphiti. Model Client → Campaign → Keyword → Decision. Query "what keywords have worked for this client in the SaaS vertical?"
- Compare: query quality, maintenance burden, complexity, cost
**Decision criteria:** Use both if graph queries are significantly better for relational/temporal org knowledge. Use Letta only if archival memory covers it adequately.  
**Time box:** 2 days

---

### Spike 2: Graphiti vs Neo4j vs Postgres+pgvector
**Question:** If we need a knowledge graph, which technology?  
**Research tasks:**
- Graphiti (Zep): Python-native, built for agent memory, temporal by design. Evaluate: schema flexibility, query language, self-hosting complexity, Claude integration
- Neo4j: mature, Cypher query language, excellent tooling. Evaluate: overkill for our use case? Licensing?
- Postgres + pgvector + jsonb: single service, we control schema, no graph query language. Evaluate: is relational + vector search enough without true graph traversal?
**Decision criteria:** Simplest option that handles temporal relational queries well and can be self-hosted.  
**Time box:** 1 day

---

### Spike 3: MCP Server Inventory — What Already Exists?
**Question:** Before building MCP servers, what's already available in the MCP ecosystem?  
**Research tasks:**
- Audit existing MCP servers: Vercel, GitHub, Google (GA4/GSC), Ahrefs, Semrush, CMS platforms
- For each Hazn agent tool need (see Section 3.2), find: existing MCP server, quality/maturity, self-hostable?
- Identify what must be built from scratch vs. what can be configured
**Output:** Tool inventory matrix — agent → tool → existing MCP (yes/no/partial) → build effort  
**Time box:** 1 day

---

### Spike 4: Credential Architecture — How Do We Vault Per-Client Credentials?
**Question:** Each client has different GA4 properties, Ahrefs seats, CMS logins, Vercel tokens. How do agents get the right credentials at runtime without storing them insecurely?  
**Research tasks:**
- Option A: Environment vars per client deployment (simple, doesn't scale)
- Option B: Letta memory block with encrypted credential refs + secret manager (1Password CLI, HashiCorp Vault, AWS Secrets Manager)
- Option C: Client workspace stores OAuth tokens, agents request via API at runtime
**Decision criteria:** Must work for consulting-led (Autonomous manages credentials) and eventually self-serve (clients auth their own tools).  
**Time box:** 1 day

---

### Spike 5: Agent-os — Use It, Fork It, or Reference It?
**Question:** autonomous-agent-os has Letta integration, MCP server, agent builder, workspace UI. How much of this is reusable?  
**Research tasks:**
- Run agent-os locally with Docker Compose
- Deploy a Hazn agent (e.g. SEO Specialist) into agent-os
- Load a SKILL.md into archival memory
- Connect via MCP to a Claude Code session
- Evaluate: does the memory actually persist and improve agent behavior?
**Decision criteria:** If Letta integration works well end-to-end, agent-os becomes the memory + MCP backbone. If it's too rigid or the product experience is wrong, extract only the Letta integration patterns and build our own.  
**Time box:** 2 days

---

## 7. What Is NOT In Scope (Yet)

- Billing / subscription management
- Multi-tenant auth for self-serve
- White-label product
- Mobile experience
- Real-time collaboration

---

## 8. Success Criteria for Research Phase

At the end of the research spikes, we should be able to answer:

1. **Memory architecture:** Letta only, graph only, or both? Which graph if so?
2. **MCP layer:** what do we build vs. what do we configure?
3. **Credential model:** how do per-client credentials work at runtime?
4. **Agent-os:** backbone, reference, or ignore?
5. **Build order:** what's the smallest thing we can build that makes Hazn compoundingly better per client?

These answers produce a technical architecture doc and a sprint plan. The research phase should take no more than **1 week**.

---

## 9. Open Questions for the Team

1. Is the graph database the right mental model for org knowledge, or is structured document storage (with good embeddings) enough?
2. Should each Hazn agent be a separate Letta deployment, or can one Letta agent hold multi-domain memory with good block structure?
3. What's the minimum client-facing surface needed for consulting-led engagements? (Just a shared link to deliverables? A simple dashboard? Full workspace?)
4. Do we self-host Letta + graph, or use managed services initially?

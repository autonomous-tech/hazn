# Hazn Platform PRD

**Status:** Research & Architecture Phase
**Owner:** Rizwan Qaiser
**Date:** 2026-03-04 (updated after red team review)
**Audience:** Coding agent (Claude Code + GSD). Read fully before starting any spike. Do not invent decisions not stated here — ask first.

---

## 0. Critical Open Questions (Answer These Before Building Anything)

These are unresolved. No architecture should be locked until they're answered.

| # | Question | Why it blocks |
|---|---|---|
| A | How does the moat actually work? Data export is trivial — what makes Hazn knowledge non-portable? | Affects data model design and what we choose to store |
| B | L2/L3 conflict resolution: when agency style conflicts with end-client brand voice, which wins and how does the agent know? | Affects context injection design |
| C | Who owns client data when an agency churns? | Affects multi-tenancy and data architecture |
| D | What is a "session" in Hazn? One workflow? One task? One day? | Affects Letta memory sync trigger |
| E | What's the pricing model? Per workflow / per seat / per data stored? | Affects data layer — metering, auth, usage tracking |
| F | What does "production-ready" mean per agent type? (Dev agent: staging? QA passed? Prod deployed?) | Affects HITL checkpoint definitions |

---

## 1. Vision

Hazn is a coordinated AI marketing team — 15+ specialized agents that work together like a senior marketing team. It is not a chatbot or prompt toolkit. It delivers production-ready marketing work: websites, audits, content, campaigns, analytics.

Used by Autonomous internally to deliver client engagements. Being built into a platform that agencies and technical founders can access directly.

---

## 2. The Three-Layer Client Model

This is the most important context in the document. Read it before anything else.

```
Layer 1: AUTONOMOUS
  └── Uses Hazn internally to deliver work for its clients

Layer 2: AUTONOMOUS'S CLIENTS (e.g. a marketing agency, a B2B SaaS)
  └── Gets deliverables from Autonomous, or uses Hazn for their own marketing
  └── Has their own: house style, methodology, approved templates, tool preferences

Layer 3: CLIENT'S CLIENTS (e.g. the agency's end customers)
  └── Each has their own: brand, campaigns, keywords, history, competitors
  └── The L2 client uses Hazn to serve these end customers
```

**Example:** Autonomous onboards a marketing agency (L2). That agency runs campaigns for 12 of their own clients (L3). Each L3 client has a different brand voice, different keyword targets. The agency applies its own house methodology across all of them.

**Implication for agents:** Before any agent runs, the orchestrator must load two scopes of context:
- **L2 context:** agency house style, methodology, approved templates
- **L3 context:** end-client brand voice, keyword history, campaign decisions, past audits

**Known unresolved problem:** When L2 and L3 context conflict (agency says "always formal" / end-client brand is casual), the agent needs a resolution rule. This is not designed yet. Flag as Open Question B.

---

## 3. The Core Problem

Hazn agents are stateless today. Every engagement starts from zero. No memory of past decisions, brand voice, keyword history, competitor intel, or preferences. Agents produce good work but it doesn't compound.

**What must be built:** A runtime where agents have persistent memory scoped correctly (L2 + L3), dedicated tool access per agent type, and a delivery surface.

---

## 4. Decisions Already Made

Do not re-research these.

| Decision | Choice | Rationale |
|---|---|---|
| Org data storage | **Postgres + pgvector** | Handles structured data + semantic search. Graph database not needed until query complexity demands it (see Section 5.1). |
| Agent working memory | **Letta (MemGPT)** | Purpose-built for agent brain state — preferences, craft knowledge, active context. NOT for bulk structured data. |
| Product type | Platform, not just a framework | Autonomous uses it internally AND clients will access it |
| Delivery mode order | Consulting-led → MCP-connected → Self-serve | Build internal first, validate memory layer works, then expand |

---

## 5. Architecture

### 5.1 Data Layer: What Goes Where

This is the corrected model. The previous version incorrectly placed structured data inside Letta.

| Data type | Where it lives | Why |
|---|---|---|
| Keywords, rankings, audit results, campaign history | **Postgres** (relational tables) | Structured, queryable, large volume |
| Brand voice summaries, semantic search over copy | **Postgres + pgvector** (vector columns) | Semantic retrieval without a separate service |
| Decisions, relationships (Campaign → Keyword → Decision) | **Postgres** (foreign keys + joins) | Sufficient until multi-hop traversal becomes a real problem |
| Agent preferences, craft knowledge, lessons learned | **Letta archival** | Fuzzy semantic retrieval, agent-specific |
| Active client context (injected at session start) | **Letta core blocks** | Lives in agent's working memory for the session duration |

**On graph databases:** Postgres + pgvector covers ~80% of what a graph would do here. Multi-hop traversal (e.g. "all decisions that influenced campaigns that used keywords that ranked") becomes ugly SQL at scale, but that scale is 12–18 months away at minimum. Start with Postgres. Add a graph layer if and when you're writing 4+ join queries to answer basic questions.

### 5.2 Memory Architecture

```
Session start:
  Orchestrator queries Postgres for L2 + L3 context
  → Injects into agent's active_client_context Letta block
  Agent runs with full context

Session end:
  New structured findings → written to Postgres (audit results, keyword data, decisions)
  New craft learnings → written to agent's Letta archival (what worked, what didn't)
```

**Letta memory blocks per agent:**
- `craft_knowledge` — how to do the work well (accumulates across all clients)
- `active_client_context` — current L2 + L3 context (overwritten each session)
- `preferences` — agent-specific working preferences
- `task_board` — current task state

**What Letta does NOT store:** keyword databases, audit reports, campaign history, rankings. Those are Postgres.

**Known risk:** Letta memory sync relies on Claude to categorize session learnings. LLM-based extraction is noisy — it will misattribute learnings and write garbage over time without curation. No memory quality control mechanism is designed yet. This must be addressed before memory is used in production at scale.

### 5.3 Agent Spaces: Tooling Per Agent

| Agent | Tools Required | Postgres Storage |
|---|---|---|
| **SEO Specialist** | Ahrefs/Semrush API, GSC, PageSpeed | Keywords, rankings, audit history (per L3) |
| **Developer** | GitHub API, Vercel API, staging envs | Generated code, deploy history, preview URLs (per L3) |
| **Blog Writer** | CMS write access (Payload/WordPress), image gen | Content calendar, published index, drafts (per L3) |
| **Analytics** | GA4 OAuth per client, GSC, Tag Manager | Benchmark snapshots, audit outputs (per L3) |
| **Copywriter** | None (LLM-native) | Approved copy library, brand voice (L2 + L3) |
| **Strategist** | Web research, competitor scraping | Strategy docs, positioning decisions (per L3) |
| **Auditor** | Playwright, PageSpeed, crawler | Audit reports, before/after comparisons (per L3) |
| **Email Specialist** | ESP API (Klaviyo, Mailchimp) | Sequence library, send history (per L3) |

### 5.4 MCP Layer

MCP servers connect agents to tools at runtime. Credentials are scoped per client (see Spike 4).

**Priority 1 — Build or configure first:**
- `mcp-hazn-memory` — read/write to Letta blocks + Postgres (the critical one — bridges agents to persistent memory)
- `mcp-vercel` — deploy, preview, domain management
- `mcp-github` — repo management, PR creation, CI status
- `mcp-ga4` — GA4 data pull, GSC queries, benchmarks
- `mcp-pagespeed` — Core Web Vitals, performance scoring

**Priority 2:**
- `mcp-ahrefs` or `mcp-semrush` — keyword data, backlinks, competitor analysis
- `mcp-cms` — write to Payload CMS or WordPress
- `mcp-image-gen` — generate images for content

**Priority 3:**
- `mcp-client-workspace` — trigger workflows, manage approvals, share deliverables

### 5.5 Product Delivery Modes

**Mode 1: Consulting-Led (now → 3 months)**
Autonomous team runs Hazn for clients. Clients get deliverables. Memory accumulates per client. No client-facing UI.

**Mode 2: MCP-Connected (3–6 months)**
Technical clients plug Hazn into Claude Code / Cursor via MCP. Agents run in their environment, pull from shared Postgres + Letta. No UI needed.

**Mode 3: Self-Serve (6+ months)**
Client workspace — dashboard, memory inspector, workflow trigger, HITL queue, deliverables. Requires: auth, multi-tenancy, billing, onboarding. **Do not design this until pricing model is decided (Open Question E).**

### 5.6 Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│                  HAZN ORCHESTRATOR                    │
│  Knows: L2 client + L3 end-client                    │
│  Loads: correct Postgres context before session start │
└───────────────────────┬──────────────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
  ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼───────┐
  │ SEO Agent   │ │ Dev Agent  │ │ Copy Agent │
  │ Letta:      │ │ Letta:     │ │ Letta:     │
  │ craft +     │ │ craft +    │ │ craft +    │
  │ active ctx  │ │ active ctx │ │ active ctx │
  │ + MCP tools │ │ + MCP tools│ │ + MCP tools│
  └──────┬──────┘ └─────┬──────┘ └────┬───────┘
         │              │              │
         └──────────────┼──────────────┘
                        │ reads + writes
  ┌─────────────────────▼──────────────────────────┐
  │           POSTGRES + PGVECTOR                   │
  │                                                 │
  │  agencies (L2)          end_clients (L3)        │
  │  ├── house_style        ├── brand_voice         │
  │  ├── methodology        ├── keywords[]          │
  │  └── templates[]        ├── campaigns[]         │
  │                         ├── decisions[]         │
  │                         ├── competitors[]       │
  │                         └── audits[]            │
  └─────────────────────────────────────────────────┘
```

---

## 6. Research Spikes

Complete all spikes before locking architecture. Each spike has explicit tasks, decision criteria, and a required output format. Time-box strictly — if a spike runs over, make the best decision with available info and move on.

**Required output format for every spike:** A filled decision record:
```
Spike N: [name]
Decision: [one sentence]
Rationale: [2-3 sentences]
Rejected alternatives: [list]
Risks accepted: [list]
```

---

### Spike 1: Does the Two-System Model Work End-to-End?

**Question:** Can Letta active context blocks + Postgres deliver correct L2 and L3 scoped context to an agent at session start, without bleeding data between clients?

**Tasks:**
1. Run agent-os locally (`docker compose up` — app + Letta + Postgres)
2. Deploy SEO Specialist into agent-os
3. Create: 1 fake agency (L2) with house style + 2 fake end-clients (L3) with different keyword histories
4. At session start: query Postgres for L2 + L3 context, inject into agent's `active_client_context` block
5. Run a workflow for L3 client A. End session. Write findings back to Postgres.
6. Run a workflow for L3 client B. Does the agent have clean context? Does L3-A data bleed into L3-B?
7. Test the conflict case: L2 says "formal tone", L3-A says "casual brand". What does the agent do?

**Decision criteria:**
- Context injection works cleanly, no bleed → proceed with two-system model
- Bleed occurs or injection is too complex → simplify; consider single Postgres query replacing Letta active context

**Time box:** 2 days

---

### Spike 2: Postgres Schema Design

**Question:** Can one Postgres schema handle all L2 and L3 data with clean query patterns?

**Tasks:**
1. Design schema: `agencies`, `end_clients`, `keywords`, `rankings`, `campaigns`, `decisions`, `audits`, `approved_copy`, `brand_voice`
2. Define relationships and foreign keys
3. Add pgvector columns where semantic search is needed (brand voice, copy, decisions)
4. Write 5 representative queries:
   - "All keywords targeted for end-client X in the last 6 months"
   - "Brand voice summary for end-client Y (semantic)"
   - "All decisions made for end-client X with rationale"
   - "Last audit findings for end-client X"
   - "All approved copy for agency Z house style"
5. Evaluate: are any queries requiring more than 3 joins? If so, flag for graph consideration.

**Output:** Schema file (`schema.sql`) + query examples + assessment of graph necessity.

**Time box:** 1 day

---

### Spike 3: MCP Server Inventory

**Question:** What MCP servers already exist and are production-ready for Hazn's tool needs?

**Tasks:**
1. Search for existing MCP servers: Vercel, GitHub, GA4/GSC, Ahrefs, Semrush, Payload CMS, WordPress, Klaviyo, Mailchimp, Playwright, PageSpeed
2. For each: exists? maintained? covers our use case? self-hostable?
3. Fill this matrix:

| Agent | Tool | Existing MCP | Quality | Build effort if none |
|---|---|---|---|---|
| SEO | Ahrefs | ? | ? | ? |
| SEO | GSC | ? | ? | ? |
| Developer | Vercel | ? | ? | ? |
| Developer | GitHub | ? | ? | ? |
| Analytics | GA4 | ? | ? | ? |
| Blog Writer | Payload CMS | ? | ? | ? |
| Auditor | Playwright | ? | ? | ? |

**Output:** Filled matrix. Determines what gets built vs configured.

**Time box:** 1 day

---

### Spike 4: Credential Architecture

**Question:** How do agents get per-client credentials (GA4 property IDs, Ahrefs API keys, CMS tokens) at runtime, securely, at both L2 and L3 scope?

**Tasks:**
1. Map all credential types by agent (from Section 5.3)
2. Prototype Option B (most likely): credentials stored in Postgres per L2/L3 client, retrieved at session start, passed as MCP env vars. Does this actually work with MCP tool calls?
3. Design the auth flow for when a client eventually connects their own tools (self-serve Mode 3)
4. Flag any compliance implications (GA4 data = Google's ToS; write access to client CMS = high risk)

**Decision criteria:** Must work for consulting-led (Autonomous manages credentials) and scale to self-serve (clients auth their own tools via OAuth).

**Output:** Credential flow diagram + chosen option + security risks flagged.

**Time box:** 1 day

---

### Spike 5: Agent-os — Backbone, Reference, or Ignore?

**Question:** How much of `autonomous-tech/autonomous-agent-os` is reusable for Hazn's memory + MCP layer?

**Tasks:**
1. Run locally: `docker compose up`
2. Deploy SEO Specialist from `hazn/sub-agents/seo-specialist.md`
3. Load `hazn/skills/seo-audit/SKILL.md` into Letta archival at deploy time
4. Connect Claude Code session via `npx agent-os-mcp --url http://localhost:3000`
5. Run a fake SEO workflow. End session. Start new session. Does memory actually persist and change agent behavior?
6. Assess workspace UI honestly: is it extensible enough to become the L2 client dashboard, or is it too generic?

**Decision criteria:**
- Memory works end-to-end AND UI is extensible → use as backbone, extend it
- Memory works, UI is wrong → extract Letta integration code only, build own UI
- Neither works → build directly against Letta SDK, skip agent-os entirely

**Time box:** 2 days

---

## 7. What Is NOT In Scope

- Billing / subscription management (blocked on Open Question E)
- Multi-tenant auth for self-serve (Mode 3 only)
- White-label / reseller
- Mobile
- Real-time collaboration
- Memory quality control / curation system (known gap, deferred)
- L2/L3 conflict resolution rules (known gap, deferred — see Open Question B)

---

## 8. Success Criteria for Research Phase

Fill this table. When complete, produce an ADR + sprint plan.

| Question | Answer |
|---|---|
| Data layer: Postgres only or Postgres + graph? | |
| Postgres schema: does it handle all query patterns cleanly? | |
| MCP: what do we build vs configure? (from Spike 3 matrix) | |
| Credential model: which option? | |
| Agent-os: backbone / reference / ignore? | |
| L2/L3 context injection: works without bleed? | |
| Session definition: what triggers a session end in Hazn? | |

Research phase time box: **1 week maximum.**

---

## 9. Repo Reference

| What | Where |
|---|---|
| Hazn agents | `hazn/sub-agents/*.md` |
| Hazn workflows | `hazn/workflows/*.yaml` |
| Hazn skills | `hazn/skills/*/SKILL.md` |
| Agent-os source | `autonomous-tech/autonomous-agent-os` (GitHub) |
| Existing Hazn docs | `hazn/docs/` |
| Hazn orchestrator context | `hazn/SOUL.md` |

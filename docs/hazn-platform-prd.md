# Hazn Platform PRD

**Status:** Research & Architecture Phase
**Owner:** Rizwan Qaiser
**Audience:** Coding agent (Claude Code + GSD). Read fully before starting any spike. Do not invent decisions not stated here — ask first.

---

## Changelog

| Version | Changes |
|---|---|
| v1 | Initial draft — vision, memory layer, agent spaces, MCP layer |
| v2 | Added three-layer client model (L2/L3), corrected data model (Postgres+pgvector not graph) |
| v3 | Red team fixes — open questions surfaced, Spike 6 added |
| v4 | All 6 open questions resolved and red-teamed |
| v5 | Metering architecture added — Langfuse + Postgres schema, credits model |
| v6 | Strategic fixes — primary product bet named, Letta self-hosting, Vault for credentials, mcp-hazn-memory spec, memory correction, QA agent, architecture diagram updated, stale text removed |

---

## 0. Decisions Resolved

All critical questions answered and red-teamed. Locked unless explicitly revisited.

### A — The Moat
**Decision:** Switching cost, not technical lock-in. Two components:
1. **Behavioral moat** — agents learn how the L2 client approves work, what gets rejected, their patterns. Lives in Letta. Took months to build. Rebuilding elsewhere means starting over.
2. **Operational moat** — all L3 end-client history, campaigns, audits, context lives in Hazn. Migrating 12 end-clients is painful enough that most won't bother.

Note: Letta memory is technically exportable. The moat is cost + effort of rebuilding, not cryptographic lock-in. Design workflow integration depth to be the lock-in.

### B — L2/L3 Conflict Resolution
**Decision:** L3 (end-client) brand voice wins by default. Agent flags conflict in HITL queue. 24-hour timeout — if unresolved, agent proceeds with L3 default and logs. L2 agencies can lock specific rules that override L3 (legal/compliance use cases).

### C — Data Ownership on Churn
**Decision:** Maximum 90-day retention post-churn. Client notified at churn + 30 days before deletion. GDPR on-request deletion within 30 days. L3 deletion is independent of L2 churn.

### D — Session Definition
**Decision:** One workflow run = one session. Checkpoint sync every 10 turns regardless of state. Parallel agents each own their own session. Failure-state sync on crash — never discard partial learnings. 4-hour inactivity fallback.

### E — Pricing
**Decision:** Deferred until Spike 6 cost data. Free engagements during testing. Credits + feature gating model (Instantly-style) — tiers and credit prices set after 10+ real runs logged. Developer agent = internal/consulting only in v1.

### F — "Production-Ready" Per Task Type

| Task type | Done when |
|---|---|
| Analytics teaser / audit | Report generated + verified at 3 viewports |
| Landing page | Deployed to Vercel preview + client approved |
| Full site build | All pages on staging + QA passed + client signed off |
| Blog post | Published to CMS + SEO checklist passed |
| Email sequence | Draft complete + client approved |
| Bug fix | Deployed to prod + verified |

Every approval gate has a 48-hour timeout + default action. Staging = Vercel preview URLs in v1.

---

## 1. Vision

Hazn is a coordinated AI marketing team — 15+ specialized agents that work together like a senior marketing team. It delivers production-ready marketing work: websites, audits, content, campaigns, analytics.

**Primary product bets (co-equal):**
- **Mode 1:** Autonomous uses Hazn internally to deliver work for clients. Agents + orchestrator, no client-facing UI.
- **Mode 3:** Agencies access Hazn directly via a self-serve workspace. They run workflows for their own end-clients, inspect agent memory, manage deliverables.

**Mode 2** (MCP-connected, technical founders plug in via Claude Code) is a useful distribution channel but not a primary bet. Build it if it's low-lift after Mode 1 is stable.

---

## 2. The Three-Layer Client Model

```
Layer 1: AUTONOMOUS
  └── Uses Hazn internally to deliver work

Layer 2: AUTONOMOUS'S CLIENTS (e.g. a marketing agency)
  └── Has their own: house style, methodology, approved templates, tool preferences
  └── In Mode 3: logs into Hazn workspace directly

Layer 3: CLIENT'S CLIENTS (the agency's end customers)
  └── Each has: brand, campaigns, keywords, history, competitors
  └── L3 clients do NOT get their own Hazn login in v1 — agency controls everything
  └── L3 data is managed by the L2 agency on their behalf
```

**Conflict resolution (decided):** L3 brand voice wins by default. L2 can lock overrides. Agent flags conflicts in HITL queue. See Section 0-B.

**Onboarding (Mode 1):** Autonomous creates the agency profile and end-client records manually. No self-serve onboarding in v1.

**Onboarding (Mode 3):** Agency creates account, configures house style, adds end-clients, connects tools. This is the org creation flow — designed when Mode 3 UI is built.

---

## 3. The Core Problem

Hazn agents are stateless today. Every engagement starts from zero. No memory of past decisions, brand voice, keyword history, competitor intel, or preferences. Agents produce good work but it doesn't compound.

**What must be built:** Persistent memory scoped to L2 + L3, dedicated tool access per agent type, delivery surface for Mode 3.

---

## 4. Decisions Already Made

| Decision | Choice | Rationale |
|---|---|---|
| Org data storage | Postgres + pgvector | Structured + semantic search in one service. Graph deferred. |
| Agent working memory | Letta (self-hosted) | Purpose-built for agent brain state. Self-hosted = version control, no SaaS dependency. |
| Credential storage | HashiCorp Vault | Secrets never touch Postgres. Postgres stores credential IDs only. |
| Primary product | Mode 1 + Mode 3 | See Section 1. Mode 2 is secondary. |
| Delivery mode order | Mode 1 → Mode 3 → Mode 2 | Internal validation first, then self-serve. |
| Memory layer abstraction | Required | Letta accessed via `HaznMemory` interface only — swap-safe if Letta is replaced. |

---

## 5. Architecture

### 5.1 Data Layer: What Goes Where

| Data type | Where | Why |
|---|---|---|
| Keywords, rankings, audit results, campaign history | Postgres (relational tables) | Structured, queryable, large volume |
| Brand voice, semantic search over copy/decisions | Postgres + pgvector | Semantic retrieval, no separate service |
| Agent preferences, craft knowledge, lessons learned | Letta archival | Fuzzy retrieval, agent-specific |
| Active client context (per session) | Letta core blocks | Injected at session start, wiped at end |
| Secrets (API keys, OAuth tokens, CMS passwords) | HashiCorp Vault | Secrets manager — never in Postgres |
| Credential references | Postgres (vault_secret_id only) | Postgres stores the ID; Vault holds the value |
| Workflow run records | Postgres (workflow_runs table) | Billing source of truth — append-only |

**On graph databases:** Postgres + pgvector covers ~80% of graph use cases here. Add graph layer only if writing 4+ join queries to answer basic questions — that's 12–18 months away minimum.

### 5.2 Memory Architecture

```
Session start:
  Orchestrator queries Postgres for L2 + L3 context
  → Injects into agent's active_client_context Letta block via HaznMemory interface
  Agent runs with full context

Every 10 turns (checkpoint):
  Orchestrator triggers HaznMemory.checkpoint_sync()
  New learnings written to Letta archival

Session end (or 4hr inactivity):
  New structured findings → Postgres (audit results, keywords, decisions)
  New craft learnings → Letta archival via HaznMemory
  active_client_context block wiped (rebuilt fresh next session)

On crash:
  HaznMemory.failure_sync() — write whatever was learned, never discard
```

**Letta memory blocks per agent:**
- `craft_knowledge` — how to do the work well (cross-client, accumulates)
- `active_client_context` — current L2 + L3 context (session-scoped, wiped after)
- `preferences` — agent working preferences
- `task_board` — current task state

**Memory abstraction layer — required:**
All Letta access goes through a `HaznMemory` interface. No agent or orchestrator code calls Letta directly. This makes Letta swap-safe. If Letta changes API or is replaced, only `HaznMemory` needs updating.

```python
class HaznMemory:
    def load_client_context(l2_id, l3_id) -> dict
    def inject_context(agent_id, context: dict)
    def checkpoint_sync(agent_id, session_id)
    def failure_sync(agent_id, session_id)
    def end_session(agent_id, session_id)
    def write_finding(l3_id, finding_type, data)
    def correct_memory(agent_id, block, old_value, new_value)  # memory correction
    def search_archival(agent_id, query) -> list
```

**Known risk:** LLM-based memory extraction is noisy. Claude will misattribute learnings. Memory quality degrades without curation. Mitigation: memory correction UI (see Section 5.5) + eventual memory quality review workflow. This is not solved yet — it is a known operational risk for production scale.

**Memory correction (planned, not in v1 research spikes):**
Clients must be able to say "this is wrong, forget it." The `correct_memory()` method handles this programmatically. The Mode 3 workspace will expose a Memory Inspector where L2 clients can view and edit agent memory blocks for their account. This is a Mode 3 feature, not a research spike.

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
| **QA Tester** | Playwright, accessibility checker | QA reports, test results (per L3) |

**QA Tester agent** is part of the platform. Every workflow that produces a deliverable (site, landing page, report) passes through QA Tester before being marked done. QA Tester defines what "done well" looks like — not just "done."

### 5.4 MCP Layer

**Priority 1:**
- `mcp-hazn-memory` — the critical bridge. Spec below.
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

**`mcp-hazn-memory` — full tool spec:**

This MCP server is the only way agents interact with persistent memory and client context. It wraps `HaznMemory`.

```
Tools exposed:

load_context(l2_client_id, l3_client_id)
  → Returns: agency house style, methodology, end-client brand voice,
    recent decisions, last audit summary, active campaigns
  → Called by orchestrator at session start

write_finding(l3_client_id, finding_type, data)
  → finding_type: keyword | decision | audit_result | approved_copy | competitor
  → Writes structured data to Postgres
  → Called by agents when they produce a finding worth persisting

search_memory(agent_type, query)
  → Semantic search over agent's Letta archival
  → Returns: relevant past learnings, patterns, preferences
  → Called by agents when they need to recall past craft knowledge

checkpoint_sync(agent_id, session_id, learnings[])
  → Writes learnings to Letta archival via HaznMemory
  → Called every 10 turns by orchestrator

correct_memory(agent_id, block, correction)
  → Updates a Letta memory block with a correction
  → Called when a human overrides agent memory via workspace UI

get_credentials(l2_client_id, l3_client_id, credential_type)
  → Retrieves secret from Vault using stored vault_secret_id
  → credential_type: ga4 | gsc | ahrefs | cms | vercel | esp
  → Never returns raw secrets to agent context — passes directly to MCP tool call
```

### 5.5 Mode 3 Client Workspace (future)

When built, L2 agencies see:
- **Dashboard** — active projects, running workflows, deliverables
- **Memory Inspector** — view + edit what agents know about their org and end-clients. This is where memory correction happens.
- **End-Client Manager** — create/manage L3 client profiles, brand docs, tool connections
- **Workflow Trigger** — run workflows from UI
- **HITL Queue** — approve before agents proceed, resolve L2/L3 conflicts
- **Deliverables** — view, approve, share outputs

L3 end-clients do NOT get logins in v1. Agency controls everything on their behalf.

### 5.6 Architecture Diagram

```
                    ┌─────────────────────────────┐
MODE 3 ONLY →       │     AGENCY WORKSPACE (UI)    │
                    │  Dashboard|Memory|HITL|Runs  │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────────────────────┐
                    │            HAZN ORCHESTRATOR                  │
                    │  - Loads L2+L3 context from Postgres          │
                    │  - Injects context via mcp-hazn-memory        │
                    │  - Writes workflow_runs to Postgres (metering)│
                    │  - Manages HITL queue + conflict flags        │
                    │  - Triggers checkpoint syncs every 10 turns   │
                    └────┬──────────────┬──────────────┬──────────┘
                         │              │              │
                  ┌──────▼──────┐┌──────▼──────┐┌─────▼──────┐
                  │  SEO Agent  ││  Dev Agent  ││ Copy Agent │  ...
                  │             ││             ││            │
                  │ HaznMemory  ││ HaznMemory  ││ HaznMemory │
                  │ + MCP tools ││ + MCP tools ││ + MCP tools│
                  └──────┬──────┘└──────┬──────┘└─────┬──────┘
                         │  Langfuse SDK traces every LLM call
                         │              │              │
                         └──────────────┼──────────────┘
                                        │
          ┌─────────────────────────────▼──────────────────────────┐
          │                    POSTGRES + PGVECTOR                   │
          │                                                          │
          │  agencies (L2)              end_clients (L3)            │
          │  workflow_runs (metering)   keywords / audits / copy    │
          │  vault_secret_ids           decisions / campaigns        │
          └──────────────────────────────────────────────────────────┘
                         │                        │
          ┌──────────────▼──────┐   ┌─────────────▼────────┐
          │   LETTA (self-hosted)│   │  HASHICORP VAULT      │
          │   agent memory only  │   │  all secrets          │
          │   HaznMemory wrapper │   │  GA4, Ahrefs, CMS etc │
          └──────────────────────┘   └──────────────────────┘
                         │
          ┌──────────────▼──────┐
          │   LANGFUSE           │
          │   (self-hosted)      │
          │   LLM traces only    │
          │   debug + visibility │
          │   NOT billing source │
          └──────────────────────┘
```

---

## 6. Research Spikes

Run in this order: **Spike 5 first** (does agent-os work?), then Spike 1 (which depends on Spike 5's answer), then 2–4 in parallel, Spike 6 ongoing.

**Required output format:**
```
Spike N: [name]
Decision: [one sentence]
Rationale: [2-3 sentences]
Rejected alternatives: [list]
Risks accepted: [list]
```

---

### Spike 5 (RUN FIRST): Agent-os — Backbone, Reference, or Ignore?

**Why first:** Spike 1 assumes agent-os as the integration point. If Spike 5 says "ignore," Spike 1 instructions change. Run this before anything else.

**Question:** How much of `autonomous-tech/autonomous-agent-os` is reusable?

**Tasks:**
1. `docker compose up` — run app + Letta + Postgres locally
2. Deploy SEO Specialist from `hazn/sub-agents/seo-specialist.md`
3. Load `hazn/skills/seo-audit/SKILL.md` into Letta archival at deploy time
4. Connect Claude Code via `npx agent-os-mcp --url http://localhost:3000`
5. Run a fake SEO workflow. End session. Start new session. Does memory persist and change agent behavior?
6. Test `HaznMemory`-equivalent: can you inject external context into a Letta block at session start?
7. Assess workspace UI: extensible enough for Mode 3 agency dashboard or too generic?

**Decision criteria:**
- Memory + context injection works, UI extensible → use as backbone
- Memory works, UI wrong → extract Letta integration patterns only, build own UI
- Neither works → build directly against Letta SDK, skip agent-os

**Time box:** 2 days

---

### Spike 1: Does the Two-System Model Work End-to-End?

**Depends on:** Spike 5 result. If agent-os is ignored, replace agent-os steps with direct Letta SDK.

**Question:** Does Postgres context injection → Letta active block → agent session work cleanly for L2 + L3 scope without bleed?

**Tasks:**
1. Create: 1 fake agency (L2) + 2 fake end-clients (L3) with different keyword histories
2. Session start: query Postgres for L2+L3 context, inject via `mcp-hazn-memory.load_context()`
3. Run SEO workflow for L3-A. End session. Write findings back via `mcp-hazn-memory.write_finding()`
4. Run SEO workflow for L3-B. Confirm clean context — no L3-A bleed
5. Test conflict: L2 says "formal", L3-A says "casual". Does agent flag it correctly?
6. Test failure: kill the workflow mid-run. Does checkpoint sync preserve learnings?

**Decision criteria:**
- Clean injection, no bleed, failure sync works → proceed
- Bleed occurs → rethink active_client_context scope (consider per-session Letta agent instances)

**Time box:** 2 days

---

### Spike 2: Postgres Schema Design

**Question:** Can one schema handle all L2/L3 data with clean query patterns?

**Tasks:**
1. Design: `agencies`, `end_clients`, `keywords`, `rankings`, `campaigns`, `decisions`, `audits`, `approved_copy`, `brand_voice`, `vault_credentials`
2. Foreign keys + pgvector columns for semantic fields
3. Write 5 representative queries (see Section 5.1 for examples)
4. Flag any query requiring 4+ joins

**Output:** `schema.sql` + query examples + graph necessity assessment

**Time box:** 1 day

---

### Spike 3: MCP Server Inventory

**Question:** What already exists vs what we build?

**Tasks:** Fill this matrix:

| Agent | Tool | Existing MCP | Quality | Build effort |
|---|---|---|---|---|
| SEO | Ahrefs | ? | ? | ? |
| SEO | GSC | ? | ? | ? |
| Developer | Vercel | ? | ? | ? |
| Developer | GitHub | ? | ? | ? |
| Analytics | GA4 | ? | ? | ? |
| Blog Writer | Payload CMS | ? | ? | ? |
| Auditor | Playwright | ? | ? | ? |

**Time box:** 1 day

---

### Spike 4: Credential Architecture with Vault

**Question:** How do agents get per-client credentials at runtime via HashiCorp Vault?

**Tasks:**
1. Stand up HashiCorp Vault (Docker, dev mode for spike)
2. Store 3 fake client credentials (GA4, Ahrefs, CMS token)
3. Postgres stores `vault_secret_id` per credential per L2/L3 client
4. Orchestrator at session start: reads `vault_secret_id` from Postgres, fetches secret from Vault, passes to `mcp-hazn-memory.get_credentials()`
5. Verify: agent can make an authenticated GA4 call without the raw secret ever appearing in agent context
6. Design OAuth flow for Mode 3 (client connects their own GA4 — how does token land in Vault?)

**Decision criteria:** Raw secrets never in agent context or Postgres. Vault fetch works end-to-end.

**Output:** Credential flow diagram + Vault config + OAuth flow design for Mode 3

**Time box:** 1 day

---

### Spike 6: Observability & Metering (runs concurrently with all testing)

**Context:** ~10 live agencies. Metering runs against real workflows with real clients.

**Two-layer architecture:**
- **Langfuse** (self-hosted, already deployed) — LLM traces, tokens, debugging. Not billing source of truth.
- **Postgres `workflow_runs`** — billing source of truth. Append-only.

**Schema:**
```sql
CREATE TYPE workflow_status AS ENUM ('running', 'completed', 'failed', 'interrupted');
CREATE TYPE workflow_type AS ENUM ('analytics-teaser', 'analytics-audit', 'audit',
  'website', 'landing-page', 'blog-post', 'email-sequence');

CREATE TABLE workflow_runs (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_type     workflow_type NOT NULL,
  l2_client_id      uuid REFERENCES agencies(id),
  l3_client_id      uuid REFERENCES end_clients(id),
  started_at        timestamptz NOT NULL DEFAULT now(),
  completed_at      timestamptz,
  status            workflow_status NOT NULL DEFAULT 'running',
  total_tokens_in   integer DEFAULT 0,
  total_tokens_out  integer DEFAULT 0,
  total_cost_usd    numeric(10,6),
  credits_consumed  integer  -- NULL until credit pricing is set
);

CREATE TABLE workflow_agents (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_run_id  uuid REFERENCES workflow_runs(id),
  agent_type       text NOT NULL,
  turns            integer DEFAULT 0,
  tokens_in        integer DEFAULT 0,
  tokens_out       integer DEFAULT 0,
  cost_usd         numeric(10,6)
);

CREATE TABLE workflow_tool_calls (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_run_id  uuid REFERENCES workflow_runs(id),
  tool_name        text NOT NULL,
  call_count       integer DEFAULT 0,
  cost_usd         numeric(10,6)
);
```

**Implementation:**
1. Add Langfuse SDK to agent calls (tag with l2/l3 client IDs, workflow run ID)
2. Orchestrator writes `workflow_runs` row at start, updates per agent, closes at end
3. On crash: set `status = 'interrupted'`, write partial data — never discard
4. `/admin/runs` query: cost by workflow type, by L2 client, flagged outliers

**Minimum runs before setting prices:**
- 3 analytics teasers, 2 audits, 2 landing pages, 1 full website — across 3+ agencies

**Flag:** runaway agents (>50 turns), outliers (>$5/run), unexpected tool API costs

**Pricing direction (pending data):** credits per workflow type + feature-gated tiers. Tiers are directional until cost data confirms viability.

**Time box:** Ongoing. Block pricing decisions until 10+ runs logged.

---

## 7. What Is NOT In Scope

- Billing / subscription infrastructure (blocked on Spike 6 data)
- Pricing model (blocked on Spike 6)
- Multi-tenant auth for Mode 3 (needed for self-serve, not research phase)
- White-label / reseller
- Mobile
- Real-time collaboration
- Memory quality control system (known gap — planned post-research)
- L3 client logins (agencies control everything in v1)
- Data migration for existing 10 agencies (Spike 6 captures forward — no backfill in v1)
- Orchestrator refactor (known complexity — handled as part of Mode 1 build, not a research spike)

---

## 8. Success Criteria

**Research phase complete when this table is filled:**

| Question | Answer |
|---|---|
| Agent-os: backbone / reference / ignore? | |
| L2/L3 context injection: works without bleed? | |
| Checkpoint + failure sync: confirmed working? | |
| Postgres schema: handles all query patterns cleanly? | |
| Graph database needed? | |
| MCP: what to build vs configure? (Spike 3 matrix) | |
| Vault: credentials flow works end-to-end? | |
| Cost per workflow type: 10+ runs logged? | |

**Product ready to charge when:**
- Memory layer works across 3+ real client engagements without manual correction
- At least one agency has used it for 4+ consecutive weeks
- Cost per workflow is known with <20% variance across runs
- QA Tester agent passing rate >90% on completed workflows

**Time box:** Spikes 5, 1, 2, 3, 4 — 1 week. Spike 6 ongoing.

---

## 9. Repo Reference

| What | Where |
|---|---|
| Hazn agents | `hazn/sub-agents/*.md` |
| Hazn workflows | `hazn/workflows/*.yaml` |
| Hazn skills | `hazn/skills/*/SKILL.md` |
| Agent-os source | `autonomous-tech/autonomous-agent-os` (GitHub) |
| Existing Hazn docs | `hazn/docs/` |
| Orchestrator context | `hazn/SOUL.md` |

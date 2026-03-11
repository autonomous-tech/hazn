# Runtime Thinking — Hazn Agent OS
**Status:** Architecture investigation (pre-scope)  
**Date:** 2026-03-04  
**Purpose:** CTO-level analysis of the runtime/knowledge persistence vision before any build decisions are made

---

## 1. What is autonomous-agent-os?

**Short answer: Not what you're describing. Don't build on top of it.**

The `autonomous-tech/autonomous-agent-os` GitHub repo is a create-next-app boilerplate. That's it. There's no agent runtime, no primitive orchestration layer, no state management, no coordination primitives. The README is the default Next.js README. It appears to be either an abandoned project, a placeholder for a future build, or a frontend shell for something else.

**Is it relevant?** No. It gives Hazn nothing for what Rizwan is describing.

**What would an actual agent OS provide?** For comparison:
- Agent identity and lifecycle management (spawn, suspend, terminate)
- Shared state/memory stores (vector DB, key-value, document)
- Tool registration and credentialing
- Inter-agent message passing
- Persistent workspace per agent (filesystem isolation, context windows)
- Execution environment (sandboxed compute, rate limiting)

Autonomous-agent-os provides none of this. **Start from scratch conceptually — or look at OpenClaw itself as the closest existing primitive.**

---

## 2. The Core Insight — Unpacked

Rizwan's instinct is correct. Let me map it technically.

### 2a. Org Knowledge Layer — What persists per client?

This is the most strategically important part of the vision. Here's what accumulates:

**Identity & Positioning**
- Brand voice guide (approved adjectives, banned phrases, tone calibration)
- Positioning statement (ICP, value prop, differentiation)
- Competitor map (with notes on what's changed over time)
- Anti-persona list (who NOT to market to)

**Content Corpus**
- Every piece of approved copy (headlines, CTAs, email subject lines that worked)
- Rejected copy with notes on why (prevents re-suggesting bad ideas)
- Blog articles published + performance data (which articles drove leads)
- Keyword ownership map (what they rank for, what they're targeting)

**Technical State**
- GA4 property ID, GSC site ID, ad account IDs
- OAuth tokens (refreshable, per-client scoped)
- Tag Manager container ID + audit history
- Past audit snapshots (baseline metrics — bounce rate, conversion rate, page speed scores over time)

**Performance History**
- A/B test results (what variants won, by how much)
- SEO ranking history (keyword positions over time)
- Conversion benchmarks (what their CVR was before/after each intervention)

**Relationship Context**
- Who the stakeholders are (CEO skeptical of AI copy, CMO trusts the process, dev team uses X stack)
- Communication preferences
- Decision history (what they approved, what they pushed back on)

**Right now, none of this persists in Hazn.** Each project stores files in `projects/{client}/` on disk, but there's no schema, no queryability, no versioning, no cross-project learning. It's a flat file dump.

---

### 2b. Agent Spaces — What each agent actually needs

| Agent | Storage Needs | Credential Needs | Tooling Needs | Sharing/Output Needs |
|---|---|---|---|---|
| **Strategist** | Client brief, past strategy.md, competitor history | None (public research) | Web search, Crunchbase/LinkedIn read | Shareable strategy doc |
| **UX Architect** | ux-blueprint.md, revision history, client feedback | None | Browser (site auditing), canvas (layout) | Preview wireframe URL |
| **Copywriter** | Approved copy bank, rejected copy, brand voice | None | None beyond LLM | Shareable copy doc |
| **Wireframer** | wireframes/ directory, design system tokens | None | Local web server or hosted URL to serve HTML | Preview URL for client approval |
| **Developer** | Full repo access, staging env, node_modules | SSH to HestiaCP, GitHub token, domain DNS | Git, npm/bun, HestiaCP API | Staging URL, production URL |
| **QA Tester** | Screenshots, qa-report.md | None | Browser automation (Playwright), screenshot capture | QA report URL |
| **SEO Specialist** | seo-keywords.md, audit history, rank tracking data | Ahrefs/Semrush API key (per-account or shared), GSC OAuth per client | Ahrefs/Semrush API, GSC API, sitemap submission | SEO checklist, rank report |
| **Content Writer** | content/blog/, content-log.md, keyword performance history | None | CMS API (Payload or WP REST) for publishing | Draft review URL, published URL |
| **Auditor** | Past audit reports, CVR benchmarks, competitor audits | GA4 OAuth (optional but valuable) | Browser automation, Lighthouse API, PageSpeed API | Branded HTML report URL |
| **Analytics Inspector** | site_inspection.json, historical inspection diffs | None | curl, Playwright | JSON output file |
| **Analytics Report Writer** | All JSON data files, past reports for the same client | GA4 OAuth per client, GSC OAuth per client | GA4 Data API, GA4 Admin API, GSC API | Markdown report |
| **Analytics Teaser Writer** | teaser output, PageSpeed data | None | PageSpeed API | Single-file HTML for deployment |

**Key observation:** Right now, credentials are handled ad-hoc (passed in as context or read from env). There's no credential store, no per-client OAuth token management, no secret scoping. This is the #1 practical blocker to scaling beyond a handful of manual projects.

---

### 2c. Tooling Per Agent — The Specific Gaps

**SEO Specialist**
- Currently: relies on web search + manual Ahrefs if Rizwan pastes data in
- Needs: Ahrefs/Semrush API key (shared across clients), per-client project in Ahrefs, keyword position history stored in db
- Gap: No API integration exists. Every SEO audit is partially manual right now.

**Analytics Agents (Inspector, Report Writer, Adversary, Client Reporter)**
- Currently: requires manual GA4 OAuth setup per client — explicitly flagged in docs as "not automated"
- Needs: OAuth token management, per-client credential vault, token refresh logic
- Gap: This entire workflow is blocked without credentials. The teaser workflow (no-auth version) exists precisely because the full workflow can't self-serve yet.

**Developer**
- Currently: SSH to HestiaCP server, manual domain provisioning
- Needs: Automated staging environment creation, subdomain provisioning API, deploy pipeline (push → build → preview URL)
- Gap: Every deployment requires Rizwan to SSH in manually. This doesn't scale.

**Content Writer**
- Currently: writes markdown to `content/blog/` but publishing is manual (developer or Rizwan publishes to CMS)
- Needs: Payload CMS API key or WP REST API token per client site, auto-publish or draft-creation capability
- Gap: The content pipeline stops at markdown. Getting content into the CMS requires a human hand-off.

**Wireframer**
- Currently: writes HTML files to disk, but the preview mechanism relies on there being a running local server or deployed URL
- Needs: Automatic deployment of wireframes to a preview URL (e.g., `wireframe-{client}.docs.autonomoustech.ca`)
- Gap: Wireframe review by clients requires manual deployment step. The `autonomous-proposals` or `landing-pages` repos partially solve this but it's not integrated.

---

## 3. The Runtime Question

### What does "our own runtime" actually mean?

Rizwan used the word runtime. Let's be precise about what that could mean:

**Option A: Container/VM per client**
- Every client gets an isolated compute environment
- Their credentials, data, and agent history live inside
- Agents spin up inside the container when work is triggered
- Heavy. Expensive. Kubernetes territory. Overkill for Hazn's current scale.

**Option B: Container/VM per agent type**
- One SEO agent container with shared Ahrefs access
- One dev agent container with deploy tooling
- Shared tooling, client data passed in at runtime
- More realistic. Closer to what microservices look like.
- Still requires orchestration (Kubernetes or similar).

**Option C: Persistent process with state (what OpenClaw currently is)**
- Long-running process, tools registered globally
- State in files/DB, not in memory
- This is essentially what OpenClaw already provides
- The gap is per-client state scoping and credential management

**Option D: Coordination layer (Hazn-specific orchestration)**
- A lightweight runtime that: routes work to the right agent, injects the right credentials, stores/retrieves client context, and surfaces work products
- Think: less OS, more workflow engine with memory
- This is the minimum viable interpretation of what Rizwan is describing
- Much more achievable than A or B

### The honest assessment

Hazn doesn't need a new runtime OS. **What it needs is a state + credential management layer on top of what OpenClaw already provides.** The execution environment (OpenClaw + Claude) is fine. The missing pieces are:

1. **Per-client data store** — structured, queryable, not just flat files
2. **Credential vault** — per-client API keys and OAuth tokens, accessible to agents during execution
3. **Artifact hosting** — automatic deployment of outputs (wireframes, reports, content drafts) to preview URLs
4. **Agent context injection** — when an agent spawns for a client, it automatically gets that client's context loaded (brand voice, past work, credentials)

That's not a new runtime. That's a **configuration + context management layer** — and it can be built in weeks, not months, using existing infrastructure.

### What already exists that could be used

**OpenClaw** already provides:
- Subagent spawning and lifecycle management
- File system access
- Tool execution (exec, browser, web_search, etc.)
- Session isolation

**What OpenClaw doesn't provide:**
- Structured per-client data stores
- Credential vaulting per client
- Automatic context injection at agent spawn time
- Artifact hosting pipeline

**Closest relevant tool:** 1Password CLI (already in the skills!) could serve as the credential vault. `op` can store and retrieve secrets per-client. This is a Tier 1 solution that exists today.

---

## 4. The Lock-in Mechanics

### How does org-specific knowledge create lock-in?

**Data that accumulates and makes Hazn more valuable over time:**

1. **Calibrated brand voice** — after 6 months of approved/rejected copy cycles, Hazn knows what words the CMO hates and what voice the CEO responds to. This can't be extracted as a prompt — it's in the feedback history.

2. **Keyword ownership history** — 12 months of rank tracking, content performance, and topic clustering creates a proprietary view of what's working for this specific business in this specific niche. Moving to another tool or agency means starting from zero.

3. **Conversion benchmarks** — knowing that Client X converts at 2.3% from blog posts but 8.1% from case study pages is institutional knowledge that informs every content decision. An agency replacing Hazn starts blind.

4. **Audit-to-action history** — what recommendations were made, what was implemented, what moved the needle. This is the only data that proves ROI and justifies continued engagement.

5. **Approved copy corpus** — every headline, CTA, and email subject line that's been approved is a training signal. Over time, Hazn can generate on-brand copy with almost no revision cycles. A new copywriter (human or AI) starts from scratch.

6. **Stakeholder relationship map** — knowing who has veto power, who's a champion, what their concerns are, what they approved last quarter. This is soft lock-in but it's real.

### What's painful to migrate away from?

- The keyword history and rank tracking database (if built properly)
- The approved copy bank (not just text files — the feedback annotations matter)
- The OAuth integrations per platform (GA4, GSC, Ahrefs — revoking and re-authorizing is friction)
- The audit baseline data (you can't benchmark improvement without the historical snapshots)

### How does this compare to agency lock-in today?

Traditional agencies lock clients in through:
- Relationship (account manager dependency)
- Tribal knowledge in employees' heads
- Proprietary tools/dashboards they built or licensed
- Ongoing retainer structure that makes switching feel risky

**Hazn's advantage:** The lock-in can be systematized and scaled. An agency loses its lock-in when a key account manager leaves. Hazn's lock-in is in the data, not in a person. The more client data accumulates, the harder it is to leave — and this improves autonomously as work is done, not through active effort.

**The risk:** If the data layer is just flat markdown files in a GitHub repo, clients can extract it and hand it to another AI system. The lock-in is only real if the data is structured, annotated, and contextually linked in a way that's hard to extract. This is a deliberate design decision — not a consequence of doing the work.

---

## 5. Scope Options

### Tier 1 — Weeks (build on existing tools)

**What it is:** Lightweight client context layer using existing infrastructure.

**Build:**
- `clients/{client-name}/config.json` — structured client profile (brand voice, ICP, GA4 ID, stakeholder map, preferred stack)
- `clients/{client-name}/credentials.json` (git-ignored, backed by 1Password CLI for secrets)
- `clients/{client-name}/knowledge/` — approved copy bank, keyword history, audit baselines (markdown + JSON)
- Hazn orchestrator reads `clients/{client}/config.json` at spawn time and injects it into every sub-agent brief
- Auto-deploy wireframes/reports to `landing-pages` or `autonomous-proposals` repo using existing GitHub Actions

**What it delivers:**
- Agents always have client context without manual copy-paste
- Basic credential management via 1Password CLI
- Artifact hosting for wireframes and reports

**Investment:** 1-2 weeks of agent/orchestration work. No new infrastructure.

**Limitation:** Data is still flat files. No queryability. No cross-client learning. Credentials still require manual 1Password setup per client.

---

### Tier 2 — Months (proper runtime with agent spaces)

**What it is:** Dedicated data layer + credential management + deployment pipeline.

**Build:**
- **Client knowledge DB**: SQLite or Postgres per-instance storing: brand voice annotations, copy corpus (approved/rejected), keyword ranking history, audit snapshots, conversion benchmarks
- **Credential vault**: 1Password CLI integration with per-client vaults, automated token refresh for GA4/GSC/Ahrefs OAuth
- **Artifact hosting pipeline**: Each agent output type auto-deploys to a deterministic URL (wireframes, reports, content drafts)
- **Agent context loader**: When any sub-agent spawns, it receives a structured context bundle (client profile + relevant history + credentials) injected automatically by Hazn orchestrator
- **Staging automation**: API-driven HestiaCP provisioning for staging domains — developer agent calls an API, gets back a staging URL without SSH

**What it delivers:**
- Agents are genuinely client-aware without manual setup
- SEO agent can pull historical keyword data from DB automatically
- Content writer can publish directly to CMS via stored API keys
- Developer gets a staging URL without human intervention

**Investment:** 2-3 months of backend + integration work. Requires a dev resource (not just agent work).

**Key technical decisions needed first:**
- DB choice (SQLite for simplicity vs Postgres for scale)
- Hosting for the knowledge layer (same VPS as HestiaCP? Separate?)
- OAuth management approach (custom vs using an existing identity service)

---

### Tier 3 — Longer (full platform with org knowledge graph + white-label)

**What it is:** Hazn becomes a product, not just an internal tool.

**Build:**
- **Org knowledge graph**: Not just flat data — entities, relationships, and temporal context. "The CMO approved this headline because it matched the ICP pain point framing from the April audit." Graph query answers questions like "what copy has worked for fintech ICPs?"
- **Multi-tenant platform**: Each client has isolated data + credentials + agent history. Accessible via dashboard.
- **White-label runtime**: Partners/agencies can run their own instance of Hazn with their branding, their agents, their clients.
- **LLM fine-tuning pipeline**: Use approved copy corpus to fine-tune a brand-specific copy model per client
- **Autonomous workflow triggers**: "Blog writer runs every Monday based on this keyword list" without human initiation
- **Custom tooling**: Hazn-specific Ahrefs/Semrush integration, not reliant on agent doing web scraping

**What it delivers:**
- Hazn as a SaaS product (not just an internal tool)
- True knowledge graph lock-in
- White-label revenue stream
- Autonomous content operations without daily orchestration

**Investment:** 6-18 months. Requires product, engineering, and design team. This is a startup, not a feature.

---

## 6. Open Questions & Risks

These are the things Rizwan needs to decide before any of this gets scoped into a build plan. Some of these look like product decisions but are actually technical forks that affect everything downstream.

### Decision 1: Who is the customer?

**Is Hazn an internal tool that Rizwan uses to serve clients faster, or is it a product that agencies and freelancers pay to use?**

This is not rhetorical. The answer changes the entire architecture:
- Internal tool → Tier 1 or 2 is fine, single-tenant, optimized for speed
- Product → Need multi-tenancy from day 1, auth, billing, data isolation — jump to Tier 3 thinking even if you build incrementally

If the answer is "eventually a product but internal for now," you need to make architectural decisions at Tier 1/2 that don't require a rewrite at Tier 3.

### Decision 2: What does the client experience look like?

Right now, clients receive:
- HTML reports deployed to `autonomous-proposals` or `landing-pages`
- Staging URLs for their sites
- Markdown docs (internally)

A knowledge-persistence layer implies a client-facing portal eventually. **Does Rizwan want clients logging into a dashboard to see their brand knowledge, content history, and audit data?** Or is this purely internal tooling that clients never touch?

This determines whether you need a frontend at all in Tier 2.

### Decision 3: OAuth credential management — shared or per-instance?

- **Ahrefs/Semrush**: Does Hazn get one API key and all clients share it (cheaper, simpler), or does each client authenticate their own account (better data isolation, richer data)?
- **GA4/GSC**: Must be per-client OAuth (Google's policy, plus you need their data not yours). How are refresh tokens stored and rotated?
- **CMS publishing**: WordPress and Payload both have API keys. Who manages these — Rizwan or the client?

This is a credential governance question that blocks the credential vault design.

### Decision 4: Where does the knowledge live?

- On the VPS alongside HestiaCP sites?
- Separate managed DB (PlanetScale, Supabase, etc.)?
- Embedded SQLite per client project folder?

Each has different failure modes, backup complexity, and cost. The VPS option is cheapest and simplest but creates a single point of failure for all client data.

### Decision 5: What's the actual SEO tooling?

This is fuzzy in the current docs. The SEO Specialist agent "uses Ahrefs/Semrush" but there's no API integration — the agent would need Rizwan to paste data in, or it scrapes Google, or it uses free tools.

**The vision requires real API access.** What's the actual plan?
- Ahrefs API is expensive (~$500/mo for API access) — can it be shared across clients or does each client need their own account?
- Semrush has a more accessible API tier
- DataForSEO is a cheaper alternative with Ahrefs-quality data

This decision affects Tier 1 scope. If SEO agents need API data, this needs to be budgeted and built before Tier 1 delivers real value.

### Decision 6: The developer agent's staging automation

Right now staging requires SSH + manual HestiaCP commands. **How automated should this become?**

- Option A: Agent SSHes in and runs commands (already works, fragile)
- Option B: HestiaCP has a REST API — build a thin wrapper the agent calls
- Option C: Move client staging to a different platform (Cloudflare Pages for Next.js, which is already used for `landing-pages`)

Option C might be the fastest path: for Next.js sites, Cloudflare Pages with automatic preview deployments on each push eliminates the HestiaCP dependency entirely for staging.

### Decision 7: What's the build agent?

None of this runtime/knowledge layer exists yet. **Who builds it?**

- Sub-agents building infrastructure (using Claude Code in a coding-agent skill) works for code generation but not for provisioning infrastructure
- The developer agent is scoped for client work, not for building Hazn itself
- Rizwan or an actual developer needs to be hands-on for the DB design and credential vault setup

The risk here: if Rizwan assumes this gets built the same way a client website gets built (spawn an agent, it does it), he'll be disappointed. Infrastructure work requires a human in the loop for decisions, credentials, and environment setup.

---

## Summary

| Question | Status |
|---|---|
| Does autonomous-agent-os help? | No. It's a Next.js boilerplate. |
| Is the vision coherent? | Yes — the insight is correct and the instinct is right. |
| Is it fuzzy anywhere? | Yes — SEO tooling, customer definition, client experience, and credential governance are all underdefined. |
| What's the fastest valuable step? | Tier 1: structured client config + 1Password credentials + auto artifact deployment. Weeks, not months. |
| What's the strategic bet? | Per-client knowledge accumulation. The data layer is the moat — but only if it's structured and annotated, not flat files. |
| What's the biggest risk? | Building a runtime before deciding if Hazn is internal tooling or a product. That decision forks the architecture. |

**Recommended next move:** Decide #1 (internal vs. product). Then scope Tier 1 with that constraint in mind. Don't design the DB schema until that decision is made — the multi-tenancy requirements are completely different.

# Phase 2: Memory Layer - Context

**Gathered:** 2026-03-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the HaznMemory abstraction and mcp-hazn-memory MCP server that make agents remember. Agents can load client context at session start, accumulate craft learnings and structured findings across sessions, search their own memory, and have incorrect memories corrected. All Letta access goes through HaznMemory (swap-safe). Session lifecycle: load context, checkpoint every 10 turns, failure sync on crash, clean end with context wipe.

</domain>

<decisions>
## Implementation Decisions

### Context Loading Scope
- Full context loading by default — agents start fully informed
- Context loading policy is configurable at L2 (agency) level only — end-clients never configure this themselves
- Core memory block gets a structured summary (~2-4KB), agent searches archival for deeper context as needed
- Cross-client insights enabled with an agency flag — agent can see raw data from sibling L3 clients when the agency explicitly enables it
- Claude's discretion on the optimal core memory vs archival split based on token budget

### Learning Taxonomy
- Two categories: "craft learnings" (how to work for this client) → Letta archival; "structured findings" (keyword gaps, audit scores) → Postgres tables
- Craft learnings are shared across all agent types for the same L3 client — SEO learnings visible to copywriter
- Three sources of learnings: agent self-selects (LLM judgment), rules-based extraction from patterns, and explicit user commands ("remember this")
- Each learning gets a source tag (agent-inferred, rule-extracted, user-explicit) and confidence score; user-explicit = highest confidence
- Append-only with supersede tags — new learnings that contradict old ones are tagged as superseding; search returns the latest
- Full provenance on structured findings: workflow_run_id, agent_type, session timestamp
- Agents can read structured findings from Postgres directly (not forced through MCP); writes go through MCP

### Memory Correction Approach
- MEM-09 built as a programmatic API now; Phase 6's Memory Inspector will call this API
- Soft-delete + replacement: original marked as corrected, new version created with link to original; preserves audit trail
- No cascade in v1 — correction affects only the specific memory; Memory Inspector (Phase 6) can surface related memories later
- Full audit log: who triggered the correction, timestamp, reason, original vs corrected content

### Session Failure Handling
- Any unclean exit (crash, timeout, API error, process kill) triggers failure sync
- Save everything with 'partial_sync' tag and lower confidence score — never discard work
- Always start fresh after failure — Letta-native approach; learnings already persisted to archival, new session inherits them
- Flag failed sessions in workflow_runs table with error details (queryable, not actively notified)

### User-Explicit Memory Commands
- Natural language via agent: agency says "remember that this client hates exclamation marks" → agent interprets and writes a craft learning with source=user-explicit and highest confidence
- Agent confirms back what it's remembering: "Got it — I'll remember that [client] prefers no exclamation marks. This applies to all future sessions."
- Natural language delete: agency can tell agent "forget that thing about exclamation marks" → agent uses correct_memory() to soft-delete
- Always confirm before deleting: agent says "I found this memory: [content]. Delete it?" — user confirms before soft-delete

### Memory Search Relevance
- Ranking: semantic similarity (primary) + recency weighting (secondary) + confidence score (tertiary)
- Default: top 5 results per search
- Superseded (corrected) memories excluded from search results — only active memories returned
- Claude's discretion on whether to unify craft + findings search or keep them separate

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `core/letta_client.py`: `get_letta_client()` factory returns configured Letta SDK instance — HaznMemory will build on this
- `core/vault.py`: `store_secret()` / `read_secret()` helpers for credential management (used by get_credentials MCP tool)
- `core/models.py`: Agency, EndClient, VaultCredential models with UUID PKs and FK hierarchy
- `content/models.py`: BrandVoice (with VectorField 1536), ApprovedCopy (with VectorField 1536) — already have embedding support
- `marketing/models.py`: Keyword, Audit, Campaign, Decision models — structured findings destination

### Established Patterns
- UUID primary keys on all models
- Domain-split Django apps: core, marketing, content
- pgvector VectorField(1536) for semantic search (used on BrandVoice, ApprovedCopy)
- Append-only versioning pattern (BrandVoice with conditional UniqueConstraint)
- Docker Compose service orchestration with healthchecks

### Integration Points
- Letta server running on port 8283 inside Docker Compose — HaznMemory connects here
- Postgres 17 with pgvector — structured findings written here
- Existing 9 models provide the L2/L3 data that load_client_context() assembles
- `conftest.py` has Vault token fixture pattern for integration tests

</code_context>

<specifics>
## Specific Ideas

- Agencies are the primary users — they drive everything on behalf of L3 end-clients
- "Remember this" and "forget this" should feel natural in conversation, not like API calls
- Cross-client insights are a competitive advantage — agencies want to apply learnings from one client to another
- Memory quality is critical: if agents remember wrong things, trust erodes quickly — hence confidence scoring and full audit trails

</specifics>

<deferred>
## Deferred Ideas

- Memory Inspector UI for agencies to view/edit memories — Phase 6 (WS-02)
- Memory quality review workflow (periodic audits) — v2 (MEMQ-01)
- Automated memory degradation detection — v2 (MEMQ-03)
- Batch import of brand guidelines as memories — future enhancement
- Active failure notifications (email/Slack) — requires notification infrastructure

</deferred>

---

*Phase: 02-memory-layer*
*Context gathered: 2026-03-05*

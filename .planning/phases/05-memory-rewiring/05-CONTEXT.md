# Phase 5: Memory Rewiring - Context

**Gathered:** 2026-03-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Each client has one Letta agent with persistent memory that loads at run start, accumulates learnings during execution, checkpoints at phase boundaries, and supports semantic search and user correction. The core HaznMemory class, CraftLearning types, memory tools, and WorkflowSession integration already exist from v1.0/v2.0 and Phase 4. This phase validates the existing code against real Letta, fixes gaps, wires auto-provisioning, adds learning auto-extraction, and proves memory persistence across runs.

</domain>

<decisions>
## Implementation Decisions

### Letta agent provisioning
- Client profile only for initialization (EndClient fields + BrandVoice if exists) — lightweight start, learnings accumulate organically
- Lazy creation for existing clients — first workflow run triggers agent creation, no migration command needed
- Consistent with existing `session.load_client_context()` get_or_create pattern

### Learning extraction — Dual path
- Agents can explicitly call `add_learning()` tool during execution (already built)
- Orchestrator also auto-extracts learnings from agent output as a fallback (new)
- Both paths produce CraftLearning records that persist in Letta archival

### Validation approach — Mock + integration + debug command
- Unit tests with mocked Letta client for CI speed
- Integration tests with Docker Letta (`@pytest.mark.integration`) for real API validation
- A `test_memory` management command for manual lifecycle testing (create agent, load context, write learning, search) against real Letta

### Claude's Discretion
- Provisioning timing: lazy on first run (current pattern) vs Django signal on client creation
- Letta-down behavior: non-fatal (current session.py pattern) vs blocking
- Memory block structure: single `active_client_context` block vs multiple structured blocks
- Whether to auto-include top N recent learnings in context block at run start, or rely on search_memory() tool
- Brand voice representation: full BrandVoice.content vs summary
- Competitor data inclusion: always vs workflow-type-dependent
- Auto-extracted learning confidence level vs explicit tool call confidence
- Learning cap per workflow run (soft/hard/none)
- Supersession handling for updated learnings (soft-delete vs keep both active)
- REST API endpoints for memory search/correction: build in Phase 5 (backend-ready for Phase 6 UI) vs defer entirely to Phase 6
- Letta SDK version: pin to current 1.7.11 vs upgrade to latest

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets (Already Built)
- `core/memory.py` (HaznMemory): Full abstraction — load_client_context(), search_memory() with composite ranking (0.6 similarity + 0.25 recency + 0.15 confidence), correct_memory() with soft-delete + audit trail, add_learning() buffer, checkpoint_sync() flush, failure_sync(), write_finding(), end_session()
- `core/memory_types.py`: CraftLearning (content, source, confidence, provenance), StructuredFinding, LearningSource enum, ClientContext
- `core/letta_client.py`: get_letta_client() factory using settings.LETTA_BASE_URL
- `orchestrator/tools/memory.py`: 7 Agent SDK tools (load_context, write_finding, search_memory, search_cross_client_insights, checkpoint_sync, correct_memory, get_credentials) with session-scoped _memory_registry
- `orchestrator/session.py`: WorkflowSession with load_client_context(), checkpoint(), end(), fail() — all wired to HaznMemory
- `orchestrator/executor.py`: Calls session.load_client_context() at run start, session.checkpoint() after each wave, session.end()/fail() on completion
- `core/models.py`: MemoryCorrection model with full audit trail (original_content, corrected_content, reason, corrected_by)
- `content/models.py`: BrandVoice (append-only, pgvector embedding), ApprovedCopy
- `marketing/models.py`: Keyword, Audit, Campaign, Decision — write targets for write_finding()

### Established Patterns
- Metadata tag format in Letta: `[source:agent-inferred][confidence:0.85][agent:seo][client:uuid][timestamp:ISO][status:active]`
- Finding dispatch by type: `_FINDING_DISPATCH = {"keyword": (Keyword, "metadata"), "audit": (Audit, "findings"), ...}`
- One Letta agent per client: `client--{pk}` naming convention (Phase 4)
- Session-scoped memory registry: module-level `_memory_registry: dict[str, HaznMemory]`
- Non-fatal Letta access: session.load_client_context() catches exceptions, workflow continues without memory

### Integration Points
- WorkflowSession: Memory lifecycle already wired — Phase 5 validates and fixes gaps
- Executor: Client context injected into system prompt at line ~364
- Docker Compose: Letta service configured (port 8283, shared Postgres, healthcheck)
- pyproject.toml: `letta-client>=1.7.11` already pinned

### What Needs Building/Fixing
- Learning auto-extraction from agent output (new orchestrator logic)
- Validation that existing HaznMemory methods work against real Letta API
- test_memory management command for manual testing
- Integration test suite against Docker Letta
- Possible REST API endpoints for memory search/correction (Phase 6 prep)

</code_context>

<specifics>
## Specific Ideas

- "Both paths" for learning extraction — agents explicitly call add_learning() AND orchestrator auto-extracts from output. Belt and suspenders approach ensures learnings are captured even if agents forget to call the tool
- Management command for manual memory testing — quick validation loop without running full workflows
- Existing code is substantial — this phase is more validation/integration than build-from-scratch

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 05-memory-rewiring*
*Context gathered: 2026-03-13*

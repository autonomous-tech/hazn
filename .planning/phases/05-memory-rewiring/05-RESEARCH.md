# Phase 5: Memory Rewiring - Research

**Researched:** 2026-03-13
**Domain:** Letta agent memory (archival + core blocks), Django integration, learning extraction
**Confidence:** HIGH

## Summary

Phase 5 validates and fixes the existing HaznMemory abstraction, WorkflowSession Letta integration, and memory tools against the real Letta Python SDK (letta-client 1.7.11). Substantial code already exists from v1.0/v2.0 (HaznMemory class, CraftLearning types, 7 memory tools, session lifecycle) but was built against assumed API shapes. Research reveals **three critical API mismatches** that will cause runtime failures if not fixed: (1) `search_memory()` references `search_response.results` with `.content` but the SDK returns `List[PassageSearchResponseItem]` with `.passage.text` and `.score`; (2) `agents.list()` returns `SyncArrayPage` which is always truthy and lacks `__getitem__`, breaking the get-or-create pattern in session.py; (3) the `add_learning` tool is not exposed to agents -- only exists as a HaznMemory method.

The existing architecture is sound: one Letta agent per client (`client--{pk}`), metadata-tagged archival passages, composite search ranking, soft-delete correction with audit trail. The work is primarily fix-and-validate rather than build-from-scratch. New functionality needed: an `add_learning` agent tool, learning auto-extraction from agent output (orchestrator fallback), and a `test_memory` management command.

**Primary recommendation:** Fix the three API mismatches first (they block everything), then validate each HaznMemory method against real Docker Letta, then add the missing `add_learning` tool and auto-extraction logic.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Client profile only for initialization (EndClient fields + BrandVoice if exists) -- lightweight start, learnings accumulate organically
- Lazy creation for existing clients -- first workflow run triggers agent creation, no migration command needed
- Consistent with existing `session.load_client_context()` get_or_create pattern
- Dual path for learning extraction: agents can explicitly call `add_learning()` tool AND orchestrator auto-extracts from output as fallback
- Both paths produce CraftLearning records that persist in Letta archival
- Unit tests with mocked Letta client for CI speed
- Integration tests with Docker Letta (`@pytest.mark.integration`) for real API validation
- A `test_memory` management command for manual lifecycle testing against real Letta

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

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| MEMO-01 | One Letta agent per client with isolated persistent memory | Existing `client--{pk}` naming in session.py; agents.create with memory_blocks confirmed working in SDK 1.7.11. Critical fix needed for agents.list() return type in get-or-create pattern. |
| MEMO-02 | Client context loaded at workflow run start (brand voice, keywords, campaigns) | Existing `_assemble_context()` and `blocks.update()` in HaznMemory confirmed matching SDK API. blocks.update(block_label, agent_id, value=) is correct. |
| MEMO-03 | Learning accumulation during execution (CraftLearning with provenance and confidence) | Existing CraftLearning type and `_write_craft_learning()` are correct -- passages.create(agent_id, text=) matches SDK. Missing: `add_learning` tool for agents to call explicitly; auto-extraction logic for orchestrator fallback. |
| MEMO-04 | Memory checkpoint at phase boundaries | Existing `checkpoint_sync()` and session.checkpoint() are correct. Executor already calls `session.checkpoint()` after each wave. |
| MEMO-05 | Semantic memory search across client learnings | Critical API mismatch: search_memory() uses `search_response.results` with `.content` but SDK returns `List[PassageSearchResponseItem]` with `.passage.text` and `.score`. Must fix. |
| MEMO-06 | User can correct wrong learnings before they compound into future runs | Existing `correct_memory()` uses passages.list(), passages.delete(memory_id, agent_id), passages.create() -- all match SDK API. MemoryCorrection Django model exists. REST endpoint needed for dashboard access. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| letta-client | 1.7.11 | Python SDK for Letta server API | Already pinned in pyproject.toml; Stainless-generated typed client |
| Django | 5.2.12 | ORM for models, management commands | Project framework |
| Pydantic | v2 (via Django) | CraftLearning, StructuredFinding types | Already used for memory_types.py |
| pytest | 9.0.2 | Unit and integration testing | Project test framework |
| pytest-django | 4.12.0 | Django test integration | Already configured |
| pytest-asyncio | >=0.23.0 | Async tool test support | Already in dev dependencies |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| asgiref | (via Django) | sync_to_async for ORM calls in async tools | Already used in memory tools |
| factory-boy | 3.3.2 | Test factories for EndClient, Agency | Already in dev dependencies |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Letta archival | pgvector direct | Letta provides embedding + search out of box; pgvector needs custom embedding pipeline |
| metadata tags in text | Letta passage tags API | SDK supports `tags` param on create and tag-filtered search; but existing code uses inline text tags for richer metadata (source, confidence, timestamp, status). Keep existing pattern -- it's more expressive. |

## Architecture Patterns

### Existing Project Structure (relevant files)
```
hazn_platform/
  core/
    memory.py              # HaznMemory class -- ALL Letta operations
    memory_types.py         # CraftLearning, StructuredFinding, ClientContext
    letta_client.py         # get_letta_client() factory
    models.py              # MemoryCorrection audit model
  orchestrator/
    session.py             # WorkflowSession -- get-or-create Letta agent
    executor.py            # Calls session.load_client_context() + checkpoint()
    tools/
      memory.py            # 7 Agent SDK tools wrapping HaznMemory
  content/
    models.py              # BrandVoice (used in context assembly)
  marketing/
    models.py              # Keyword, Audit, Campaign, Decision
  core/management/commands/
    (empty -- test_memory goes here)
tests/
  test_memory.py           # Existing unit tests (needs updates)
```

### Pattern 1: Fix-Then-Validate
**What:** Fix known API mismatches in isolation, then validate each method against Docker Letta.
**When to use:** When existing code has structural correctness but API shape assumptions.
**Approach:**
1. Fix the three identified API mismatches (search_memory, agents.list, add_learning tool)
2. Run unit tests with mocked Letta to verify logic
3. Run integration tests against Docker Letta to verify real API compatibility

### Pattern 2: Session-Scoped Memory Registry
**What:** Module-level `_memory_registry: dict[str, HaznMemory]` keyed by agent_id, created via `_get_or_create_memory()`.
**When to use:** Already established pattern in `orchestrator/tools/memory.py`.
**Note:** This is process-scoped (Celery worker process). Each workflow run creates a new HaznMemory, cached for the duration of the run.

### Pattern 3: Metadata-Tagged Archival Passages
**What:** Each learning stored as a Letta archival passage with inline metadata prefix:
```
[source:agent-inferred][confidence:0.85][agent:seo][client:uuid][timestamp:ISO][status:active]
Actual learning content here
```
**When to use:** All CraftLearning writes via `_write_craft_learning()`.
**Why:** Enables status-based filtering (corrected/superseded), confidence ranking, and provenance tracking without a separate index.

### Pattern 4: Composite Search Ranking
**What:** Re-rank Letta search results by: similarity (0.6) + recency (0.25) + confidence (0.15).
**When to use:** All `search_memory()` calls.
**Note:** The SDK now provides a `.score` per search result item. The existing code uses positional rank as similarity proxy. Consider using the SDK's `.score` directly as the similarity component.

### Anti-Patterns to Avoid
- **Trusting SyncArrayPage truthiness:** `if client.agents.list(name=x):` is always True. Always convert to list first: `results = list(client.agents.list(name=x))`.
- **Accessing `.content` on passages:** Passage objects use `.text`, not `.content`. The search response wraps passages in `PassageSearchResponseItem` with `.passage.text` and `.score`.
- **Blocking on Letta failures:** The established pattern is non-fatal Letta access. Keep it -- workflows should run (without memory) even if Letta is down.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Embedding generation | Custom embedding pipeline | Letta server's built-in embedding (configurable per agent) | Letta handles chunking, embedding, and vector storage |
| Semantic search | pgvector queries from Django | `client.agents.passages.search(agent_id, query)` | Letta returns scored results with proper embedding similarity |
| Agent provisioning | Manual Letta REST calls | `letta_client.Letta` SDK methods | Typed, validated, handles auth and pagination |
| Memory correction audit trail | Custom event log | Existing `MemoryCorrection` Django model + Letta passage soft-delete | Already built with full provenance |

## Common Pitfalls

### Pitfall 1: SyncArrayPage Is Always Truthy
**What goes wrong:** `agents.list(name=x)` returns `SyncArrayPage[AgentState]` which is a Pydantic BaseModel -- always truthy regardless of whether results exist.
**Why it happens:** The return type looks like a list but isn't. No `__getitem__`, no `__bool__`, no `__len__`.
**How to avoid:** Always convert: `results = list(client.agents.list(name=agent_name))`. Then `if results:` works correctly and `results[0]` is safe.
**Warning signs:** Agent creation runs every time despite agent already existing. Duplicate agents in Letta.
**Confidence:** HIGH (verified by inspecting installed SDK v1.7.11 source)

### Pitfall 2: Passage.text vs Passage.content
**What goes wrong:** Existing code references `result.content` but `Passage` model uses `.text`.
**Why it happens:** The original code was written against an assumed API shape or an older SDK version.
**How to avoid:** Use `passage.text` for passage content. For search results, use `item.passage.text` and `item.score`.
**Warning signs:** `AttributeError: 'Passage' object has no attribute 'content'` at runtime.
**Confidence:** HIGH (verified: `Passage.model_fields` has `text: str`, no `content` field)

### Pitfall 3: Search Response Shape Mismatch
**What goes wrong:** `search_memory()` does `search_response.results` but `passages.search()` returns `List[PassageSearchResponseItem]` directly (type alias), not an object with `.results`.
**Why it happens:** Assumed response wrapper object; actual SDK returns list directly.
**How to avoid:** Iterate the response directly: `for item in search_response:`. Each item has `.passage` (Passage) and `.score` (float).
**Warning signs:** `AttributeError: 'list' object has no attribute 'results'`.
**Confidence:** HIGH (verified: `PassageSearchResponse = List[PassageSearchResponseItem]`)

### Pitfall 4: passages.delete Parameter Name
**What goes wrong:** Potential confusion -- first positional param is `memory_id`, not `passage_id`.
**Why it happens:** SDK naming convention differs from domain terminology.
**How to avoid:** The existing code `passages.delete(passage_id, agent_id=self._agent_id)` works via positional, but be aware: keyword form is `memory_id=passage_id`.
**Confidence:** HIGH (verified from SDK signature)

### Pitfall 5: Docker Letta Startup Timing
**What goes wrong:** Integration tests fail because Letta container isn't ready despite healthcheck.
**Why it happens:** Letta's healthcheck (`curl http://localhost:8283/v1/health`) passes before embedding model is loaded. First API call may timeout.
**How to avoid:** Add a retry/backoff in integration test fixtures. The healthcheck has `start_period: 30s` but embedding loading can take longer on first run.
**Warning signs:** Connection refused or timeout on first integration test.
**Confidence:** MEDIUM (based on Docker compose config and common Letta deployment patterns)

### Pitfall 6: Missing add_learning Agent Tool
**What goes wrong:** CONTEXT.md says agents can "explicitly call add_learning() tool during execution" but no `@tool`-decorated function exists in `orchestrator/tools/memory.py`.
**Why it happens:** `add_learning()` exists as HaznMemory method but was never wrapped as an Agent SDK tool.
**How to avoid:** Create `add_learning` tool in memory.py that accepts learning content, source, confidence, agent_type from the agent and buffers via `HaznMemory.add_learning()`.
**Confidence:** HIGH (verified: grep for `add_learning` in tools/ returns no results)

## Code Examples

### Fix 1: agents.list() Get-or-Create Pattern (session.py)
```python
# Source: Verified against letta_client v1.7.11 SDK
# SyncArrayPage is iterable but always truthy -- must convert to list
existing = list(client.agents.list(name=agent_name))
if existing:
    self._letta_agent_id = existing[0].id
else:
    agent = client.agents.create(
        name=agent_name,
        system="Hazn client memory agent",
        memory_blocks=[
            {"label": "active_client_context", "value": ""},
        ],
        tags=[f"l3:{self._end_client.pk}"],
    )
    self._letta_agent_id = agent.id
```

### Fix 2: search_memory() Response Shape (memory.py)
```python
# Source: Verified against letta_client v1.7.11 SDK
# passages.search() returns List[PassageSearchResponseItem]
# Each item has: .passage (Passage with .text, .id) and .score (float)
search_results = self._client.agents.passages.search(
    agent_id=self._agent_id,
    query=query,
)

active_results = []
for item in search_results:
    text = item.passage.text  # NOT .content
    status_match = _STATUS_RE.search(text)
    status = status_match.group(1) if status_match else ""
    if status in ("corrected", "superseded"):
        continue
    active_results.append(item)

# Re-rank with composite score using SDK-provided similarity
scored: list[tuple[float, dict]] = []
for item in active_results:
    text = item.passage.text
    letta_similarity = item.score  # Use SDK score directly

    ts_match = _TIMESTAMP_RE.search(text)
    recency = _recency_score(ts_match.group(1)) if ts_match else 0.1

    conf_match = _CONFIDENCE_RE.search(text)
    confidence = float(conf_match.group(1)) if conf_match else 0.5

    composite = (
        _W_SIMILARITY * letta_similarity
        + _W_RECENCY * recency
        + _W_CONFIDENCE * confidence
    )
    scored.append((composite, {
        "id": item.passage.id,
        "content": text,
        "score": round(composite, 4),
    }))
```

### Fix 3: correct_memory() Passage Iteration (memory.py)
```python
# Source: Verified against letta_client v1.7.11 SDK
# passages.list() returns List[Passage] -- each has .text and .id
all_passages = self._client.agents.passages.list(agent_id=self._agent_id)
original_text = ""
for p in all_passages:
    if p.id == passage_id:
        original_text = p.text  # .text is correct (already matches)
        break
```

### New: add_learning Agent Tool
```python
@tool("add_learning", "Record a craft learning about this client for future reference.", {
    "agent_id": str,
    "client_id": str,
    "content": str,
    "source": str,      # "agent-inferred" | "rule-extracted" | "user-explicit"
    "confidence": float, # 0.0 - 1.0
    "agent_type": str,   # e.g. "seo", "content", "audit"
})
async def add_learning(args: dict[str, Any]) -> dict[str, Any]:
    agent_id = args["agent_id"]
    client_id = args["client_id"]
    try:
        from hazn_platform.core.memory_types import CraftLearning, LearningSource
        memory = await _get_or_create_memory(agent_id, client_id)
        learning = CraftLearning(
            content=args["content"],
            source=LearningSource(args.get("source", "agent-inferred")),
            confidence=args.get("confidence", 0.7),
            agent_type=args.get("agent_type", "unknown"),
            l3_client_id=uuid.UUID(client_id),
        )
        await sync_to_async(memory.add_learning)(learning)
        return {"content": [{"type": "text", "text": f"Learning recorded for client={client_id}"}]}
    except Exception as exc:
        logger.warning("add_learning failed: %s", exc)
        return {"content": [{"type": "text", "text": f"Error recording learning: {exc}"}], "isError": True}
```

### New: Auto-Extraction Logic (orchestrator)
```python
# Post-phase extraction in executor or session
def _auto_extract_learnings(phase_output_text: str, client_id: uuid.UUID, agent_type: str) -> list[CraftLearning]:
    """Parse agent output for statements that look like learnings.

    Heuristic patterns:
    - "I learned that..." / "Key finding:" / "Note for future:"
    - Structured JSON with "learnings" key
    - Explicit tool output from write_finding

    Auto-extracted learnings get confidence=0.6 (lower than explicit tool calls).
    """
    learnings = []
    # Try structured JSON extraction first
    try:
        data = json.loads(phase_output_text)
        if "learnings" in data:
            for item in data["learnings"]:
                learnings.append(CraftLearning(
                    content=item.get("content", str(item)),
                    source=LearningSource.RULE_EXTRACTED,
                    confidence=0.6,
                    agent_type=agent_type,
                    l3_client_id=client_id,
                ))
    except (json.JSONDecodeError, TypeError):
        pass
    return learnings
```

### Management Command: test_memory
```python
# core/management/commands/test_memory.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Test Letta memory lifecycle: create agent, load context, write learning, search, correct"

    def add_arguments(self, parser):
        parser.add_argument("--client-id", type=str, help="EndClient UUID to test with")
        parser.add_argument("--cleanup", action="store_true", help="Delete test agent after run")

    def handle(self, *args, **options):
        # 1. Get or create test client
        # 2. Create Letta agent via session.load_client_context()
        # 3. Write a test learning via HaznMemory.add_learning() + checkpoint_sync()
        # 4. Search for the learning via search_memory()
        # 5. Correct the learning via correct_memory()
        # 6. Verify correction appears in search results
        # 7. Optionally cleanup
        pass
```

## Discretion Recommendations

Based on research findings, here are recommendations for areas left to Claude's discretion:

| Area | Recommendation | Rationale |
|------|----------------|-----------|
| Provisioning timing | Keep lazy on first run | Matches existing pattern; avoids Django signal complexity; simpler to test |
| Letta-down behavior | Keep non-fatal | Already established in session.py; workflows should degrade gracefully |
| Memory block structure | Single `active_client_context` block | Simpler; context is ~2-4KB JSON; multiple blocks add API call overhead |
| Top N learnings at run start | Auto-include top 5 recent learnings in context | Ensures agents have recent context without relying on tool calls; append to context block |
| Brand voice representation | Full BrandVoice.content (truncated to 500 chars if longer) | Agents need the actual voice, not a summary; truncation prevents block bloat |
| Competitor data | Always include | Small data; useful across workflow types; simplifies logic |
| Auto-extracted confidence | 0.6 (vs 0.7-0.9 for explicit tool calls) | Lower confidence reflects less certainty; distinguishable in search ranking |
| Learning cap | Soft cap: 20 per run, log warning above | Prevents runaway learning accumulation; soft cap allows override |
| Supersession handling | Keep both active, tag superseding passage with `[supersedes:id]` | Already built into _write_craft_learning(); search ranking naturally deprioritizes older learnings |
| REST API endpoints | Build in Phase 5 (backend-ready) | Phase 6 UI needs endpoints; building them alongside memory validation is natural; avoids rework |
| Letta SDK version | Pin to 1.7.11 | Current version is confirmed working; upgrading risks API changes mid-phase |

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Per-agent-type-per-client Letta agents | One agent per client (`client--{pk}`) | Phase 4 decision | Simpler provisioning; single memory store per client |
| MCP server for memory tools | Python function tools with Agent SDK | Phase 3 decision | Direct function calls; no protocol overhead |
| Turn-based checkpointing (every 10 turns) | Phase-boundary checkpointing | Phase 1 decision (STRP-08) | Simpler; aligns with DAG execution model |

**Deprecated/outdated:**
- `record_turn()` method still exists in HaznMemory but is no longer called (session/checkpoint turn counter removed in STRP-08). Consider removing or keeping as dead code.

## Open Questions

1. **Letta embedding model configuration**
   - What we know: Letta agent creation accepts `embedding` param (e.g., "openai/text-embedding-3-small"). Docker compose sets `OPENAI_API_KEY`.
   - What's unclear: Which embedding model is configured on the running Letta instance? Does it default to OpenAI if no config provided?
   - Recommendation: Check Letta server config in Docker. If OpenAI key is set, Letta uses OpenAI embeddings by default. Verify with a test passage insert + search.

2. **Passage limit in archival memory**
   - What we know: Letta archival is backed by Postgres (pgvector). No hard limit documented.
   - What's unclear: Performance degradation with large numbers of passages per agent. Search latency at scale.
   - Recommendation: Monitor passage count per client. Consider periodic archival cleanup for very old, low-confidence learnings (future enhancement, not Phase 5).

3. **Existing Letta agents with enterprise memory block formats**
   - What we know: STATE.md notes "Existing Letta agents have enterprise memory block formats -- need cleanup before first v3.0 run"
   - What's unclear: What format the existing blocks are in; whether they need migration.
   - Recommendation: The test_memory management command should detect and report existing agents. If v2.0 agents exist, they can be deleted (or renamed) since Phase 5 uses lazy get-or-create.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 + pytest-django 4.12.0 |
| Config file | `pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `cd hazn_platform && uv run pytest tests/test_memory.py -x -q` |
| Full suite command | `cd hazn_platform && uv run pytest tests/ -x -q` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MEMO-01 | Agent provisioning (get-or-create, isolated per client) | unit + integration | `uv run pytest tests/test_memory.py -k "test_agent_provisioning" -x` | Partial (existing tests need update for API fixes) |
| MEMO-02 | Context loading (brand voice, keywords, campaigns into Letta block) | unit + integration | `uv run pytest tests/test_memory.py -k "test_load_client_context" -x` | Partial (HaznMemory tests exist, session integration missing) |
| MEMO-03 | Learning accumulation (add_learning tool + auto-extraction) | unit + integration | `uv run pytest tests/test_memory.py -k "test_add_learning or test_auto_extract" -x` | Partial (HaznMemory.add_learning tested, tool wrapper missing) |
| MEMO-04 | Checkpoint at phase boundaries | unit | `uv run pytest tests/test_memory.py -k "test_checkpoint" -x` | Partial (checkpoint_sync tested, executor integration exists) |
| MEMO-05 | Semantic search with composite ranking | unit + integration | `uv run pytest tests/test_memory.py -k "test_search_memory" -x` | Exists but wrong API shape (needs fix) |
| MEMO-06 | User correction with audit trail | unit + integration | `uv run pytest tests/test_memory.py -k "test_correct_memory" -x` | Exists (correct_memory tested with mocks) |

### Sampling Rate
- **Per task commit:** `cd hazn_platform && uv run pytest tests/test_memory.py -x -q`
- **Per wave merge:** `cd hazn_platform && uv run pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_memory.py` -- update existing tests for API shape fixes (Passage.text, search response shape, SyncArrayPage)
- [ ] `tests/test_memory.py` -- add tests for new add_learning tool
- [ ] `tests/test_memory.py` -- add tests for auto-extraction logic
- [ ] `tests/test_memory_integration.py` -- new file for `@pytest.mark.integration` Docker Letta tests
- [ ] `tests/conftest.py` -- add Letta mock fixtures (mock_letta_client, mock_passages, mock_blocks)

## Sources

### Primary (HIGH confidence)
- letta-client v1.7.11 installed SDK source -- inspected `Letta`, `AgentsResource`, `PassagesResource`, `BlocksResource` method signatures, return types, and model fields directly from `.venv/lib/python3.13/site-packages/letta_client/`
- Existing codebase: `core/memory.py`, `core/memory_types.py`, `core/letta_client.py`, `orchestrator/session.py`, `orchestrator/executor.py`, `orchestrator/tools/memory.py`
- `pyproject.toml` for dependency versions and test configuration
- `docker-compose.local.yml` for Letta service configuration

### Secondary (MEDIUM confidence)
- [Letta Python SDK docs](https://docs.letta.com/api/python/) -- agent creation with memory_blocks, block update patterns
- [Letta Archival Memory guide](https://docs.letta.com/guides/agents/archival-export/) -- passage insert and search patterns
- [Letta API Reference](https://docs.letta.com/api/) -- REST endpoint documentation

### Tertiary (LOW confidence)
- Letta docs show `passages.insert()` but installed SDK has `passages.create()` -- naming discrepancy between docs and SDK version. Verified `create()` is correct for v1.7.11.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all dependencies verified in pyproject.toml and installed
- Architecture: HIGH -- existing code patterns inspected, API shapes verified against SDK source
- Pitfalls: HIGH -- three critical mismatches verified by direct SDK inspection (not just documentation)
- Validation: MEDIUM -- test patterns established but integration tests need Docker Letta running

**Research date:** 2026-03-13
**Valid until:** 2026-04-13 (stable -- Letta SDK pinned to 1.7.11, no planned upgrades)

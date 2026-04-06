# Phase 2: Memory Layer - Research

**Researched:** 2026-03-05
**Domain:** Letta SDK agent memory management, MCP server implementation, Django ORM structured data
**Confidence:** HIGH

## Summary

Phase 2 builds the HaznMemory abstraction that wraps all Letta SDK access (swap-safe), the session lifecycle (load, checkpoint, failure sync, end), semantic search over archival memory, memory correction with audit trails, and the mcp-hazn-memory MCP server that exposes these operations as tools to agents.

The existing codebase provides strong foundations: `get_letta_client()` factory, `validate_letta` management command (proving the Letta passages API works), Django models for L2/L3 hierarchy (Agency, EndClient), and domain models (Keyword, Audit, Campaign, Decision, BrandVoice, ApprovedCopy) that serve as structured findings destinations. The project uses `letta-client>=1.7.11` with Python 3.13, Django 5.2, and pgvector for embeddings.

The core challenge is designing the HaznMemory class to manage Letta core memory blocks (active_client_context), archival memory (craft learnings with supersede semantics), and Postgres structured findings -- all while maintaining strict L3 client isolation and supporting crash-safe checkpointing.

**Primary recommendation:** Build HaznMemory as a single Python class in `hazn_platform/core/memory.py` that owns the Letta client instance, manages one agent's memory lifecycle, and enforces context isolation. The MCP server is a thin FastMCP wrapper that delegates to HaznMemory methods.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Full context loading by default -- agents start fully informed
- Context loading policy configurable at L2 (agency) level only
- Core memory block gets structured summary (~2-4KB), agent searches archival for deeper context
- Cross-client insights enabled with an agency flag
- Two categories: "craft learnings" (Letta archival) and "structured findings" (Postgres tables)
- Craft learnings shared across all agent types for same L3 client
- Three learning sources: agent self-selects, rules-based extraction, user-explicit commands
- Each learning gets source tag and confidence score; user-explicit = highest confidence
- Append-only with supersede tags; search returns latest
- Full provenance on structured findings: workflow_run_id, agent_type, session timestamp
- Agents can read structured findings from Postgres directly; writes go through MCP
- MEM-09 built as programmatic API now; Phase 6 Memory Inspector calls this API
- Soft-delete + replacement for corrections; preserves audit trail
- No cascade in v1 for corrections
- Full audit log on corrections: who, timestamp, reason, original vs corrected
- Any unclean exit triggers failure sync; save with 'partial_sync' tag and lower confidence
- Always start fresh after failure (Letta-native approach)
- Flag failed sessions in workflow_runs table
- Natural language "remember this" / "forget this" via agent conversation
- Agent confirms what it remembers; confirms before deleting
- Memory search ranking: semantic similarity (primary) + recency (secondary) + confidence (tertiary)
- Default top 5 results per search
- Superseded memories excluded from search results

### Claude's Discretion
- Optimal core memory vs archival split based on token budget
- Whether to unify craft + findings search or keep them separate

### Deferred Ideas (OUT OF SCOPE)
- Memory Inspector UI for agencies to view/edit memories -- Phase 6 (WS-02)
- Memory quality review workflow (periodic audits) -- v2 (MEMQ-01)
- Automated memory degradation detection -- v2 (MEMQ-03)
- Batch import of brand guidelines as memories -- future enhancement
- Active failure notifications (email/Slack) -- requires notification infrastructure
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| MEM-01 | HaznMemory abstraction wraps all Letta access (swap-safe interface) | HaznMemory class design in Architecture Patterns; Letta SDK API surface documented |
| MEM-02 | Agent can load L2+L3 client context at session start via load_client_context() | Context assembly from existing Django models; core memory block injection via Letta SDK |
| MEM-03 | Context injected into agent's active_client_context Letta block (<2s) | Letta block update API; performance considerations documented |
| MEM-04 | Checkpoint sync writes new learnings to Letta archival every 10 turns | Letta passages.create() API; checkpoint tracking pattern |
| MEM-05 | Failure sync preserves partial learnings on crash (never discard) | Signal/atexit handlers; partial_sync tagging pattern |
| MEM-06 | Session end writes structured findings to Postgres and craft learnings to Letta archival | Dual-write pattern; Django ORM for findings, Letta for craft |
| MEM-07 | active_client_context block wiped at session end | Letta block update to empty string pattern |
| MEM-08 | Agents can search their own archival memory semantically via search_memory() | Letta passages.search() API; ranking/filtering logic |
| MEM-09 | Memory correction API allows programmatic override of incorrect memories | Soft-delete + replacement pattern; audit log model |
| MEM-10 | L3 context never bleeds between sessions (zero cross-client contamination) | Context isolation via block wipe + agent-per-client scoping |
| MCP-01 | mcp-hazn-memory server exposes load_context, write_finding, search_memory, checkpoint_sync, correct_memory, get_credentials tools | FastMCP server pattern; tool definitions |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| letta-client | >=1.7.11 (already pinned) | Letta server SDK -- agent creation, block management, archival passages | Already in use; validate_letta proves the API works |
| Django ORM | 5.2.12 (already pinned) | Postgres access for structured findings, L2/L3 context loading | Already in use; models exist |
| pgvector | 0.3.6 (already pinned) | Vector similarity search in Postgres | Already in use for BrandVoice/ApprovedCopy embeddings |
| fastmcp | >=2.0 | MCP server framework for mcp-hazn-memory | Standard Python MCP server library; simple decorator-based tool definition |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pydantic | v2 (via fastmcp dependency) | Data validation for MCP tool inputs/outputs and HaznMemory data classes | All structured data crossing boundaries |
| structlog or stdlib logging | existing | Structured logging for memory operations and audit trails | All HaznMemory operations |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| fastmcp | mcp (official SDK) | fastmcp is higher-level with decorator syntax; mcp SDK is lower-level. fastmcp is simpler for this use case |
| Separate memory service | HaznMemory as Django module | Keeping it in-process avoids network hops; swap-safety comes from the abstraction interface, not deployment boundary |

**Installation:**
```bash
uv add fastmcp
```

## Architecture Patterns

### Recommended Project Structure
```
hazn_platform/hazn_platform/
  core/
    memory.py              # HaznMemory class (MEM-01 through MEM-10)
    memory_types.py        # Pydantic models for learnings, findings, context
    letta_client.py        # Existing -- get_letta_client() factory
    models.py              # Existing + new MemoryCorrection audit model
    vault.py               # Existing
  mcp_servers/
    __init__.py
    hazn_memory_server.py  # FastMCP server (MCP-01) -- thin wrapper over HaznMemory
```

### Pattern 1: HaznMemory Abstraction (Swap-Safe Wrapper)

**What:** A single class that encapsulates ALL Letta SDK calls. No other code in the project imports letta_client directly (except get_letta_client factory). If Letta is ever swapped, only this class changes.

**When to use:** Every memory operation.

```python
# hazn_platform/core/memory.py
from __future__ import annotations
import uuid
from dataclasses import dataclass
from letta_client import Letta
from hazn_platform.core.letta_client import get_letta_client

@dataclass
class CraftLearning:
    content: str
    source: str  # "agent-inferred" | "rule-extracted" | "user-explicit"
    confidence: float  # 0.0-1.0; user-explicit = 1.0
    agent_type: str
    l3_client_id: uuid.UUID
    supersedes_id: str | None = None  # ID of learning this replaces
    tags: list[str] | None = None

class HaznMemory:
    """Swap-safe abstraction over Letta memory operations."""

    def __init__(self, agent_id: str, l3_client_id: uuid.UUID, l2_agency_id: uuid.UUID):
        self._client: Letta = get_letta_client()
        self._agent_id = agent_id
        self._l3_client_id = l3_client_id
        self._l2_agency_id = l2_agency_id
        self._turn_counter = 0
        self._pending_learnings: list[CraftLearning] = []

    def load_client_context(self) -> None:
        """MEM-02/03: Load L2+L3 context into active_client_context block."""
        ...

    def checkpoint_sync(self) -> None:
        """MEM-04: Flush pending learnings to archival every 10 turns."""
        ...

    def failure_sync(self) -> None:
        """MEM-05: Emergency flush with partial_sync tag."""
        ...

    def end_session(self, findings: list[dict]) -> None:
        """MEM-06/07: Write findings to Postgres, learnings to archival, wipe context."""
        ...

    def search_memory(self, query: str, limit: int = 5) -> list[dict]:
        """MEM-08: Semantic search over archival memory."""
        ...

    def correct_memory(self, passage_id: str, new_content: str, reason: str, corrected_by: str) -> None:
        """MEM-09: Soft-delete + replacement with audit trail."""
        ...
```

### Pattern 2: Context Assembly from Django Models

**What:** `load_client_context()` queries Django ORM for L2 agency data + L3 end-client data, assembles a structured summary (~2-4KB), and writes it to the Letta core memory block labeled `active_client_context`.

**When to use:** Session start.

```python
# Context assembly -- query existing models
from hazn_platform.core.models import Agency, EndClient
from hazn_platform.content.models import BrandVoice
from hazn_platform.marketing.models import Keyword, Campaign

def _assemble_context(self) -> str:
    agency = Agency.objects.get(id=self._l2_agency_id)
    client = EndClient.objects.get(id=self._l3_client_id)
    brand_voice = BrandVoice.objects.filter(
        end_client=client, is_active=True
    ).first()
    recent_keywords = Keyword.objects.filter(
        end_client=client
    ).order_by("-updated_at")[:20]
    active_campaigns = Campaign.objects.filter(
        end_client=client, status="active"
    )

    # Build structured summary for core memory block
    context = {
        "agency": {"name": agency.name, "house_style": agency.house_style, "methodology": agency.methodology},
        "client": {"name": client.name, "competitors": client.competitors},
        "brand_voice": brand_voice.content if brand_voice else None,
        "active_campaigns": [{"name": c.name, "type": c.campaign_type} for c in active_campaigns],
        "top_keywords": [{"term": k.term, "status": k.status} for k in recent_keywords],
    }
    return json.dumps(context, indent=2)
```

### Pattern 3: Letta Core Memory Block Management

**What:** Use the Letta SDK to read/write core memory blocks. The `active_client_context` is a custom block label.

```python
# Based on validate_letta.py patterns -- agent creation with custom blocks
agent = client.agents.create(
    name=f"hazn-{agent_type}-{l3_client_id}",
    model="openai/gpt-4o-mini",
    embedding="openai/text-embedding-ada-002",
    memory_blocks=[
        {"label": "persona", "value": "..."},
        {"label": "human", "value": "..."},
        {"label": "active_client_context", "value": ""},  # Custom block
    ],
    include_base_tools=False,
)

# Update block content (context injection)
block = client.agents.blocks.retrieve(agent_id=agent.id, block_label="active_client_context")
client.agents.blocks.update(
    agent_id=agent.id,
    block_label="active_client_context",
    value=context_json,
)

# Wipe block at session end (MEM-07)
client.agents.blocks.update(
    agent_id=agent.id,
    block_label="active_client_context",
    value="",
)
```

### Pattern 4: Archival Memory with Metadata Tags

**What:** Craft learnings stored as Letta archival passages with metadata encoded in a structured prefix. Supersede semantics via metadata.

```python
# Write craft learning to archival
def _write_craft_learning(self, learning: CraftLearning) -> str:
    # Encode metadata in structured prefix for searchability
    metadata_prefix = (
        f"[source:{learning.source}]"
        f"[confidence:{learning.confidence}]"
        f"[agent:{learning.agent_type}]"
        f"[client:{learning.l3_client_id}]"
        f"[status:active]"
    )
    if learning.supersedes_id:
        metadata_prefix += f"[supersedes:{learning.supersedes_id}]"

    full_text = f"{metadata_prefix}\n{learning.content}"

    passage = self._client.agents.passages.create(
        agent_id=self._agent_id,
        text=full_text,
    )
    return passage.id

# Search with filtering -- post-filter superseded entries
def search_memory(self, query: str, limit: int = 5) -> list[dict]:
    results = self._client.agents.passages.search(
        agent_id=self._agent_id,
        query=query,
    )
    # Filter out superseded/corrected entries, apply ranking
    active_results = [r for r in results if "[status:active]" in r.text]
    return active_results[:limit]
```

### Pattern 5: MCP Server with FastMCP

**What:** The mcp-hazn-memory server is a FastMCP application that exposes HaznMemory methods as MCP tools.

```python
# hazn_platform/mcp_servers/hazn_memory_server.py
from fastmcp import FastMCP

mcp = FastMCP("hazn-memory")

@mcp.tool()
def load_context(agent_id: str, l3_client_id: str, l2_agency_id: str) -> str:
    """Load L2+L3 client context into agent's active memory block."""
    memory = HaznMemory(agent_id, uuid.UUID(l3_client_id), uuid.UUID(l2_agency_id))
    memory.load_client_context()
    return "Context loaded successfully"

@mcp.tool()
def search_memory(agent_id: str, query: str, limit: int = 5) -> list[dict]:
    """Search agent's archival memory semantically."""
    memory = HaznMemory(agent_id, ...)  # needs session state
    return memory.search_memory(query, limit)

@mcp.tool()
def write_finding(agent_id: str, finding_type: str, data: dict) -> str:
    """Write a structured finding to Postgres."""
    ...

@mcp.tool()
def correct_memory(passage_id: str, new_content: str, reason: str, corrected_by: str) -> str:
    """Soft-delete incorrect memory and create corrected replacement."""
    ...
```

### Pattern 6: Memory Correction Audit Model

**What:** Django model to track all memory corrections with full audit trail.

```python
# In core/models.py
class MemoryCorrection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_id = models.CharField(max_length=255)
    original_passage_id = models.CharField(max_length=255)
    replacement_passage_id = models.CharField(max_length=255, null=True, blank=True)
    original_content = models.TextField()
    corrected_content = models.TextField()
    reason = models.TextField()
    corrected_by = models.CharField(max_length=255)  # user ID or "system"
    end_client = models.ForeignKey(EndClient, on_delete=models.CASCADE, related_name="memory_corrections")
    created_at = models.DateTimeField(auto_now_add=True)
```

### Anti-Patterns to Avoid
- **Direct Letta imports outside HaznMemory:** Defeats swap-safety. All code must go through HaznMemory.
- **Storing raw secrets in memory blocks:** Vault secrets must never enter Letta core/archival memory.
- **Mutable global memory state:** HaznMemory instances must be per-session, not singletons. Each session creates its own instance.
- **Relying on Letta passage deletion:** Letta archival is append-optimized. Use soft-delete (status tags) rather than hard-deleting passages.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| MCP server protocol | Custom JSON-RPC server | FastMCP | Protocol details, transport negotiation, schema generation all handled |
| Embedding generation | Custom OpenAI calls for search | Letta's built-in passage search | Letta handles embedding + ANN search internally |
| Vector similarity search (archival) | pgvector queries for craft learnings | Letta passages.search() | Letta manages its own vector index; only use pgvector for Postgres-side structured data |
| Session state machine | Custom FSM | Simple turn counter + HaznMemory lifecycle methods | Overkill for load/checkpoint/end flow |

**Key insight:** Letta already handles the hard parts of memory (embedding, vector search, passage storage). HaznMemory's job is lifecycle management, context assembly, and isolation -- not reimplementing what Letta does.

## Common Pitfalls

### Pitfall 1: Letta Block Size Limits
**What goes wrong:** Core memory blocks have a token/character limit. Stuffing too much context causes silent truncation or API errors.
**Why it happens:** L2+L3 context can be large (agency styles, brand voice, 20+ keywords, campaigns).
**How to avoid:** Keep active_client_context to ~2-4KB as specified. Put summary in core block, full data in archival. Test with realistic data volumes.
**Warning signs:** Context loading succeeds but agent behavior suggests missing context.

### Pitfall 2: Cross-Client Contamination via Letta Agent Reuse
**What goes wrong:** If agents are reused across L3 clients, archival memory from client A leaks into client B's session.
**Why it happens:** Letta agents persist archival memory across sessions by design.
**How to avoid:** Either use one Letta agent per L3 client (preferred for isolation) OR wipe archival between clients (risky, loses learnings). The CONTEXT.md says learnings persist -- so agent-per-client is the correct approach. The active_client_context block wipe (MEM-07) handles the core memory side.
**Warning signs:** Agent references data from a different client's sessions.

### Pitfall 3: Checkpoint Sync During Agent Message Processing
**What goes wrong:** Writing to archival while the agent is mid-conversation can cause race conditions or confusing agent behavior.
**Why it happens:** Checkpoint sync (every 10 turns) runs during active use.
**How to avoid:** Checkpoint between turns, not during. The turn counter increments after each complete agent response. Sync is a background operation that doesn't interrupt the agent's message flow.
**Warning signs:** Agent responses reference recently-written learnings in unexpected ways.

### Pitfall 4: Failure Sync Not Triggering
**What goes wrong:** Process crash (SIGKILL, OOM) prevents atexit/signal handlers from running, losing pending learnings.
**Why it happens:** Python signal handlers and atexit don't run on SIGKILL.
**How to avoid:** Minimize the window: flush pending learnings at every checkpoint (10 turns), not just at session end. Keep `_pending_learnings` buffer small. Log pending count for debugging. Accept that SIGKILL will lose at most 10 turns of unsynced learnings.
**Warning signs:** workflow_runs missing expected learnings after crashes.

### Pitfall 5: Letta API Compatibility
**What goes wrong:** Letta is pre-1.0; API surface may change between minor versions.
**Why it happens:** The project already notes this in STATE.md blockers.
**How to avoid:** Pin `letta-client` version exactly in pyproject.toml (currently `>=1.7.11`, should pin to `==`). The HaznMemory abstraction is the mitigation -- API calls are in exactly one file.
**Warning signs:** Import errors or AttributeError on Letta client methods after upgrade.

### Pitfall 6: Django ORM in MCP Server Process
**What goes wrong:** MCP server runs as a separate process but needs Django ORM for Postgres queries.
**Why it happens:** FastMCP server needs `django.setup()` before importing models.
**How to avoid:** Call `django.setup()` at MCP server entry point before any model imports. Set `DJANGO_SETTINGS_MODULE` environment variable. Alternatively, the MCP server can run within the Django process (in-process MCP via stdio transport).
**Warning signs:** `AppRegistryNotReady` or `ImproperlyConfigured` errors from MCP server.

## Code Examples

### Letta Passages API (Verified from validate_letta.py)
```python
# Source: hazn_platform/core/management/commands/validate_letta.py
# Create passage
client.agents.passages.create(agent_id=agent.id, text=passage_text)

# Search passages
results = client.agents.passages.search(agent_id=agent.id, query="search terms")
# results.count gives count; iterate results for individual items
# Each result has .text (was .content in older API -- see STATE.md decision)
```

### Agent Creation with Custom Memory Blocks
```python
# Source: validate_letta.py
agent = client.agents.create(
    name="hazn-test-agent",
    model="openai/gpt-4o-mini",
    embedding="openai/text-embedding-ada-002",
    memory_blocks=[
        {"label": "persona", "value": "..."},
        {"label": "human", "value": "..."},
        {"label": "active_client_context", "value": ""},
    ],
    include_base_tools=False,
)
```

### Vault Secret Access (Verified from vault.py)
```python
# Source: hazn_platform/core/vault.py
from hazn_platform.core.vault import read_secret
secret_data = read_secret("agencies/acme/ga4")  # Returns dict
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Letta `insert(content=...)` | `passages.create(text=...)` | Letta SDK update (noted in STATE.md) | Must use new API; old examples on web are wrong |
| Search result `.content` | Search result `.text` (verify) | Same SDK update | Attribute name changed |
| Manual embedding + pgvector | Letta handles embeddings internally | N/A | Don't duplicate embedding logic for archival |

**Deprecated/outdated:**
- `letta_client.insert()` -- replaced by `client.agents.passages.create(text=...)`
- Search result `.content` attribute -- may now be `.text` (verify against pinned version)

## Open Questions

1. **Letta Block Update API Surface**
   - What we know: Agents have memory blocks with labels. validate_letta.py creates them.
   - What's unclear: Exact API for updating an existing block's value post-creation (`blocks.update()` vs `blocks.modify()`). Need to verify against pinned letta-client version.
   - Recommendation: Write a small integration test that creates agent, updates block, reads back. Resolve during Plan 02-01 implementation.

2. **Passage Metadata Support**
   - What we know: Passages have `.text` content. We encode metadata as text prefixes.
   - What's unclear: Whether letta-client supports structured metadata fields on passages (would be cleaner than text prefix encoding).
   - Recommendation: Check letta-client Passage model for metadata/tags fields. If available, use them. If not, text prefix encoding works (grep-friendly, searchable).

3. **MCP Server Transport: stdio vs SSE**
   - What we know: FastMCP supports both stdio (in-process) and SSE (HTTP) transports.
   - What's unclear: Which transport the orchestrator (Phase 3) will use to connect to MCP servers.
   - Recommendation: Build with stdio transport (simpler, no network hop, Django ORM accessible). Orchestrator can switch to SSE later if needed. FastMCP makes this a one-line change.

4. **Cross-Client Insights Implementation**
   - What we know: Agency flag enables cross-client insights. Agent can see sibling L3 data.
   - What's unclear: Whether this means searching across multiple Letta agents' archival, or aggregating findings from Postgres.
   - Recommendation: For v1, cross-client insights query Postgres structured findings only (already agent-readable). Cross-agent archival search is complex and deferred.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 + pytest-django 4.12.0 |
| Config file | `hazn_platform/pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `cd hazn_platform && uv run pytest tests/ -x --ignore=tests/integration` |
| Full suite command | `cd hazn_platform && uv run pytest tests/ -x` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MEM-01 | HaznMemory wraps all Letta access | unit | `pytest tests/test_memory.py::test_hazn_memory_interface -x` | No -- Wave 0 |
| MEM-02 | load_client_context() assembles L2+L3 data | unit | `pytest tests/test_memory.py::test_load_client_context -x` | No -- Wave 0 |
| MEM-03 | Context injected into Letta block <2s | integration | `pytest tests/integration/test_memory_integration.py::test_context_injection_timing -x` | No -- Wave 0 |
| MEM-04 | Checkpoint sync every 10 turns | unit | `pytest tests/test_memory.py::test_checkpoint_sync -x` | No -- Wave 0 |
| MEM-05 | Failure sync preserves partial learnings | unit | `pytest tests/test_memory.py::test_failure_sync -x` | No -- Wave 0 |
| MEM-06 | Session end writes findings + learnings | unit+integration | `pytest tests/test_memory.py::test_end_session -x` | No -- Wave 0 |
| MEM-07 | active_client_context wiped at session end | unit | `pytest tests/test_memory.py::test_context_wipe -x` | No -- Wave 0 |
| MEM-08 | search_memory() returns relevant results | integration | `pytest tests/integration/test_memory_integration.py::test_search_memory -x` | No -- Wave 0 |
| MEM-09 | Memory correction soft-delete + replacement | unit | `pytest tests/test_memory.py::test_correct_memory -x` | No -- Wave 0 |
| MEM-10 | Zero cross-client contamination | integration | `pytest tests/integration/test_memory_integration.py::test_client_isolation -x` | No -- Wave 0 |
| MCP-01 | MCP server exposes all required tools | unit | `pytest tests/test_mcp_memory_server.py -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `cd hazn_platform && uv run pytest tests/test_memory.py -x` (unit tests only)
- **Per wave merge:** `cd hazn_platform && uv run pytest tests/ -x` (full suite including integration)
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_memory.py` -- unit tests for HaznMemory (mock Letta client); covers MEM-01,02,04,05,06,07,09
- [ ] `tests/test_mcp_memory_server.py` -- unit tests for MCP tool definitions; covers MCP-01
- [ ] `tests/integration/test_memory_integration.py` -- integration tests requiring Letta+Postgres; covers MEM-03,08,10
- [ ] `tests/integration/__init__.py` -- package init
- [ ] `tests/factories.py` -- factory_boy factories for Agency, EndClient, BrandVoice, Keyword, Campaign (if not exists)
- [ ] Framework install: `uv add fastmcp` -- MCP server dependency

## Sources

### Primary (HIGH confidence)
- `hazn_platform/core/letta_client.py` -- verified Letta client factory pattern
- `hazn_platform/core/management/commands/validate_letta.py` -- verified Letta passages API (create, search)
- `hazn_platform/core/models.py` -- verified L2/L3 model structure (Agency, EndClient, VaultCredential)
- `hazn_platform/marketing/models.py` -- verified structured findings destination models
- `hazn_platform/content/models.py` -- verified BrandVoice/ApprovedCopy with pgvector
- `hazn_platform/pyproject.toml` -- verified dependency versions and test config
- `.planning/STATE.md` -- verified Letta API decisions (passages.create vs insert, Result.content vs .text)

### Secondary (MEDIUM confidence)
- FastMCP library patterns -- based on training data; verify actual API during implementation
- Letta block update API -- inferred from creation pattern; needs integration test verification

### Tertiary (LOW confidence)
- Letta passage metadata fields -- unverified; may or may not exist in pinned version
- Letta block size limits -- not verified; test with realistic data

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all core libraries already in use, only adding fastmcp
- Architecture: HIGH -- patterns directly derived from existing code and locked decisions
- Pitfalls: HIGH -- derived from real codebase analysis and STATE.md documented issues
- Letta API details: MEDIUM -- validate_letta.py confirms core patterns, but block update and passage metadata need integration testing

**Research date:** 2026-03-05
**Valid until:** 2026-04-05 (30 days -- Letta pre-1.0 may require earlier revalidation)

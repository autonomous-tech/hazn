# Phase 8: Foundation Components - Research

**Researched:** 2026-03-06
**Domain:** Agent runtime building blocks (prompt assembly, tool routing, artifact capture)
**Confidence:** HIGH

## Summary

Phase 8 builds three standalone components that will be wired into the AgentRunner in Phase 9: PromptAssembler (constructs system prompts from agent persona + skill content + client context), ToolRouter (dispatches tool_use requests to the correct MCP server without running MCP processes), and OutputCollector (parses agent markdown output into structured artifacts). All three must work with mock data -- no LLM calls, no running MCP servers, no API keys.

The existing codebase provides strong foundations: `agent_manager.read_agent_persona()` reads persona markdown, `workflow_parser.load_workflow()` parses YAML with skills/tools/agent fields, `WorkflowPhaseOutput` stores phase outputs, `StructuredFinding` defines finding schemas, and 4 FastMCP servers define 20+ tools with `@mcp.tool()` decorators. The executor.py has clear placeholder comments (lines 226-248) showing exactly where these components integrate.

**Primary recommendation:** Build three focused Python modules in `hazn_platform/orchestrator/` (prompt_assembler.py, tool_router.py, output_collector.py) plus a reusable mock module at `hazn_platform/testing/` with JSON fixture files at `tests/fixtures/`. Extend `WorkflowPhaseOutput` with `artifact_type` and `structured_data` fields via Django migration.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **PromptAssembler (RUNT-01):** Full SKILL.md content injection for each skill declared in workflow phase (typically 0-3 skills). 200k context window makes full injection comfortable.
- **ToolRouter (RUNT-03):** Static registry built at startup from MCP server configurations. No runtime discovery. Return results in Anthropic-native format (tool_result content blocks with tool_use_id). Wrap errors as is_error=true. Support BOTH Anthropic API tool_use format AND Claude Agent SDK tool call format from day one.
- **OutputCollector (RUNT-08):** Convention-based markdown parsing. Four artifact types: Report, Findings, Code artifacts, Metadata. Final agent output only. Extend existing WorkflowPhaseOutput model.
- **Mock Testing:** Real content with mock interfaces. JSON fixture files in tests/fixtures/. Standalone reusable mock module at hazn_platform/testing/. Realistic agent output samples.
- **Existing `agent_manager.read_agent_persona()` reads persona markdown** -- PromptAssembler builds on this.
- **Workflow YAML is the source of truth for tool scoping** (tools: field per phase), not skill frontmatter.
- **ToolRouter must support both Anthropic API and Claude Agent SDK formats from Phase 8**, not deferred.

### Claude's Discretion
- System prompt section ordering and structure
- Reference docs injection strategy (archival vs. prompt based on size)
- Skill frontmatter `allowed-tools` handling
- Convention-based parser specifics (exact markdown patterns, edge case handling)
- Mock module internal API design

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| RUNT-01 | PromptAssembler constructs system prompts from agent/skill/workflow markdown definitions | Architecture patterns for prompt assembly, existing `read_agent_persona()`, skill YAML frontmatter parsing, L2/L3 context injection via `ClientContext` model |
| RUNT-03 | ToolRouter dispatches tool calls to existing MCP servers and FastMCP tools | Static registry from 4 FastMCP servers (20+ tools), Anthropic API tool_use format, Claude Agent SDK format, error wrapping patterns |
| RUNT-08 | OutputCollector captures agent artifacts (markdown, findings, recommendations) | Convention-based markdown parsing patterns, existing `StructuredFinding` schema, `WorkflowPhaseOutput` model extension, artifact type taxonomy |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Django | 5.2.12 | ORM, migrations, model extensions | Already installed, WorkflowPhaseOutput extension |
| Pydantic | 2.12.5 | Schema validation for tool calls and artifacts | Already used for WorkflowSchema, StructuredFinding |
| FastMCP | 3.1.0 | MCP server tool registration (read-only for registry) | Already used for all 4 MCP servers |
| PyYAML | (installed) | Parsing SKILL.md frontmatter | Already used by workflow_parser |
| pytest | 9.0.2 | Test framework | Already configured in pyproject.toml |
| pytest-asyncio | 1.3.0 | Async test support | Already used in test_executor.py |
| pytest-django | 4.12.0 | Django test integration | Already configured |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| re (stdlib) | -- | Markdown section parsing in OutputCollector | Convention-based artifact extraction |
| json (stdlib) | -- | Fixture loading, tool result serialization | Mock data, API format conversion |
| pathlib (stdlib) | -- | File path handling for skills/agents dirs | Reading SKILL.md, references/ |
| dataclasses (stdlib) | -- | Lightweight internal types for ToolRegistry entries | ToolRouter registry entries |
| typing (stdlib) | -- | Type annotations and TypedDict | API format definitions |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Custom markdown parser | python-markdown / mistune | Overkill -- convention-based regex extraction is simpler, more predictable, and matches the exact patterns agents are instructed to follow |
| Runtime MCP discovery | Static registry | User decision: no running MCP processes needed; static registry from server source code |
| Anthropic SDK types | Hand-rolled TypedDicts | Anthropic SDK not installed in venv; TypedDicts with Pydantic validation match the wire format without adding a dependency |

**Installation:**
```bash
# No new packages needed -- all dependencies already installed
# anthropic SDK will be added in Phase 9 when AgentRunner needs it
```

## Architecture Patterns

### Recommended Project Structure
```
hazn_platform/
  hazn_platform/
    orchestrator/
      prompt_assembler.py     # RUNT-01: PromptAssembler
      tool_router.py          # RUNT-03: ToolRouter
      output_collector.py     # RUNT-08: OutputCollector
    testing/
      __init__.py
      mocks.py                # Reusable mock LLM responses, mock MCP dispatch
      fixtures.py             # Fixture loaders for test data
  tests/
    fixtures/
      tool_use_responses.json     # Mock Anthropic API tool_use content blocks
      agent_sdk_tool_calls.json   # Mock Claude Agent SDK format calls
      agent_outputs/
        seo_audit_report.md       # Realistic agent markdown output
        analytics_findings.md     # Findings-heavy output
        code_generation.md        # Code artifact output
    test_prompt_assembler.py
    test_tool_router.py
    test_output_collector.py
```

### Pattern 1: PromptAssembler (RUNT-01)

**What:** Assembles a complete system prompt from three sources: agent persona markdown, skill SKILL.md content, and L2/L3 client context.

**When to use:** Called once per phase execution, before the LLM call starts.

**Design:**
```python
# hazn_platform/orchestrator/prompt_assembler.py

from __future__ import annotations
import logging
import yaml
from pathlib import Path
from typing import Any

from hazn_platform.orchestrator.agent_manager import read_agent_persona

logger = logging.getLogger(__name__)

_DEFAULT_SKILLS_DIR = Path(__file__).resolve().parent.parent.parent / "hazn" / "skills"


def _read_skill_content(
    skill_name: str,
    skills_dir: Path | None = None,
    include_references: bool = True,
    reference_size_limit: int = 15_000,
) -> str:
    """Read SKILL.md content and optionally inline small reference files."""
    base = skills_dir or _DEFAULT_SKILLS_DIR
    skill_path = base / skill_name / "SKILL.md"
    if not skill_path.exists():
        raise ValueError(f"Skill not found: {skill_name}")

    content = skill_path.read_text()

    # Optionally inline small reference docs
    if include_references:
        refs_dir = base / skill_name / "references"
        if refs_dir.is_dir():
            for ref_file in sorted(refs_dir.iterdir()):
                if ref_file.suffix == ".md":
                    ref_content = ref_file.read_text()
                    if len(ref_content) <= reference_size_limit:
                        content += f"\n\n---\n## Reference: {ref_file.stem}\n\n{ref_content}"
                    else:
                        content += f"\n\n> Reference '{ref_file.stem}' available ({len(ref_content)} chars) -- omitted for context budget."

    return content


def assemble_prompt(
    agent_type: str,
    skills: list[str],
    client_context: dict[str, Any] | None = None,
    agents_dir: Path | None = None,
    skills_dir: Path | None = None,
) -> str:
    """Assemble complete system prompt for an agent phase execution.

    Sections (in order):
    1. Agent persona (identity, role, process)
    2. Skill instructions (full SKILL.md content per skill)
    3. Client context (L2 agency + L3 end-client data)
    """
    sections: list[str] = []

    # 1. Agent persona
    persona = read_agent_persona(agent_type, agents_dir=agents_dir)
    sections.append(persona)

    # 2. Skills (full content injection)
    for skill_name in skills:
        skill_content = _read_skill_content(skill_name, skills_dir=skills_dir)
        sections.append(f"\n---\n# Skill: {skill_name}\n\n{skill_content}")

    # 3. Client context
    if client_context:
        context_block = _format_client_context(client_context)
        sections.append(f"\n---\n# Client Context\n\n{context_block}")

    return "\n\n".join(sections)
```

**Key decisions for Claude's discretion:**
- **Prompt ordering:** Persona first, then skills, then client context. Rationale: persona establishes identity and base behavior, skills add domain knowledge, context provides the specific engagement data. This follows Claude's instruction hierarchy (system prompt sections are weighted by position).
- **Reference docs:** Inline references under 15KB (covers 24 of 25 reference files -- only ui-audit has 19 files totaling ~50KB). For large reference sets, include a summary note so the agent knows the reference exists.
- **Skill frontmatter `allowed-tools`:** Informational only -- logged but not enforced. Workflow YAML `tools:` field is the authoritative source per user decision.

### Pattern 2: ToolRouter (RUNT-03)

**What:** Maintains a static registry mapping tool names to MCP server identifiers, and dispatches tool_use requests by looking up the tool, invoking the corresponding function, and returning results in Anthropic-native format.

**When to use:** Called by the agent execution loop (Phase 9) whenever the LLM emits a tool_use content block.

**Design:**
```python
# hazn_platform/orchestrator/tool_router.py

from __future__ import annotations
import json
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ToolRegistryEntry:
    """A registered tool with its server association and callable."""
    tool_name: str
    server_name: str
    description: str
    input_schema: dict[str, Any]
    callable: Any | None = None  # The actual function to invoke (None for mock/static)


class ToolRouter:
    """Static registry and dispatcher for MCP tool calls.

    Built at startup from MCP server configurations. No runtime
    MCP process discovery -- tools are registered by importing
    the FastMCP server modules and reading their tool registrations.

    Supports two input formats:
    1. Anthropic API: {"type": "tool_use", "id": "toolu_...", "name": "...", "input": {...}}
    2. Claude Agent SDK: tool calls via MCP protocol format
    """

    def __init__(self) -> None:
        self._registry: dict[str, ToolRegistryEntry] = {}

    def register(self, entry: ToolRegistryEntry) -> None:
        self._registry[entry.tool_name] = entry

    def get_tool(self, name: str) -> ToolRegistryEntry | None:
        return self._registry.get(name)

    def list_tools(self) -> list[str]:
        return list(self._registry.keys())

    def dispatch_anthropic(self, tool_use_block: dict[str, Any]) -> dict[str, Any]:
        """Dispatch an Anthropic API tool_use content block.

        Input format:
          {"type": "tool_use", "id": "toolu_xxx", "name": "tool_name", "input": {...}}

        Output format:
          {"type": "tool_result", "tool_use_id": "toolu_xxx", "content": "...", "is_error": false}
        """
        tool_use_id = tool_use_block["id"]
        tool_name = tool_use_block["name"]
        tool_input = tool_use_block.get("input", {})

        entry = self._registry.get(tool_name)
        if entry is None:
            return {
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": f"Unknown tool: {tool_name}",
                "is_error": True,
            }

        try:
            result = entry.callable(**tool_input) if entry.callable else {}
            content = json.dumps(result) if isinstance(result, (dict, list)) else str(result)
            return {
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": content,
            }
        except Exception as exc:
            return {
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": f"Tool error: {exc}",
                "is_error": True,
            }

    def dispatch_agent_sdk(self, tool_name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
        """Dispatch a Claude Agent SDK format tool call.

        Agent SDK tools return: {"content": [{"type": "text", "text": "..."}]}
        """
        entry = self._registry.get(tool_name)
        if entry is None:
            return {"content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}], "isError": True}

        try:
            result = entry.callable(**tool_input) if entry.callable else {}
            text = json.dumps(result) if isinstance(result, (dict, list)) else str(result)
            return {"content": [{"type": "text", "text": text}]}
        except Exception as exc:
            return {"content": [{"type": "text", "text": f"Tool error: {exc}"}], "isError": True}
```

**Static registry construction:**
```python
def build_tool_registry() -> ToolRouter:
    """Build static tool registry from MCP server modules.

    Imports each FastMCP server module and extracts registered tools.
    Does NOT start any MCP server processes.
    """
    router = ToolRouter()

    # Map of server_name -> module_path for all 4 MCP servers
    servers = {
        "hazn-memory": "hazn_platform.mcp_servers.hazn_memory_server",
        "hazn-analytics": "hazn_platform.mcp_servers.analytics_server",
        "hazn-github": "hazn_platform.mcp_servers.github_server",
        "hazn-vercel": "hazn_platform.mcp_servers.vercel_server",
    }

    for server_name, module_path in servers.items():
        # Import module to trigger @mcp.tool() registrations
        # Then read the FastMCP instance's tool registry
        # ...

    return router
```

**Two format support rationale:** The Anthropic API returns tool_use blocks with `{"type": "tool_use", "id": "toolu_xxx", "name": "...", "input": {...}}`. The Claude Agent SDK uses MCP protocol internally where tools are called by name with input dict and return `{"content": [{"type": "text", "text": "..."}]}`. Supporting both from day one means Phase 9 can use either execution mode without ToolRouter changes.

### Pattern 3: OutputCollector (RUNT-08)

**What:** Parses the final agent text output (markdown) into structured artifacts using convention-based patterns. Extends WorkflowPhaseOutput with artifact fields.

**When to use:** Called after agent execution completes, on the final text output.

**Design:**
```python
# hazn_platform/orchestrator/output_collector.py

from __future__ import annotations
import re
import logging
from typing import Any
from enum import StrEnum

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ArtifactType(StrEnum):
    REPORT = "report"
    FINDINGS = "findings"
    CODE = "code"
    METADATA = "metadata"


class CollectedArtifact(BaseModel):
    """A single artifact extracted from agent output."""
    artifact_type: ArtifactType
    content: str
    structured_data: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class OutputCollector:
    """Convention-based parser for agent markdown output.

    Recognizes four artifact types:
    1. Report: full markdown body (## sections)
    2. Findings: structured ## Findings section with severity/description/evidence
    3. Code: fenced code blocks with ```artifact markers
    4. Metadata: extracted stats (word count, sections, topics)
    """

    # Patterns for findings extraction
    _FINDING_PATTERN = re.compile(
        r"[-*]\s*\*\*(?:Severity|Priority)\*\*:\s*(\w+)\s*\n"
        r"\s*[-*]\s*\*\*(?:Description|Issue)\*\*:\s*(.+?)\n"
        r"\s*[-*]\s*\*\*Evidence\*\*:\s*(.+?)\n"
        r"\s*[-*]\s*\*\*Recommendation\*\*:\s*(.+?)(?:\n|$)",
        re.MULTILINE | re.DOTALL,
    )

    # Pattern for code artifacts
    _CODE_ARTIFACT_PATTERN = re.compile(
        r"```artifact\s+(\w+)\s+([\w./\-]+)\n(.*?)```",
        re.DOTALL,
    )

    def collect(self, agent_output: str) -> list[CollectedArtifact]:
        """Parse agent output into structured artifacts."""
        artifacts: list[CollectedArtifact] = []

        # Always produce a report artifact (full body)
        artifacts.append(CollectedArtifact(
            artifact_type=ArtifactType.REPORT,
            content=agent_output,
            metadata=self._extract_metadata(agent_output),
        ))

        # Extract findings if present
        findings = self._extract_findings(agent_output)
        if findings:
            artifacts.append(CollectedArtifact(
                artifact_type=ArtifactType.FINDINGS,
                content="",  # structured_data carries the data
                structured_data={"findings": findings},
            ))

        # Extract code artifacts if present
        code_artifacts = self._extract_code_artifacts(agent_output)
        for ca in code_artifacts:
            artifacts.append(ca)

        # Always produce metadata artifact
        artifacts.append(CollectedArtifact(
            artifact_type=ArtifactType.METADATA,
            content="",
            structured_data=self._extract_metadata(agent_output),
        ))

        return artifacts
```

### Anti-Patterns to Avoid

- **LLM-based parsing for OutputCollector:** The user explicitly chose convention-based markdown parsing. Do NOT use an LLM to parse agent output -- the skill instructions already guide format. LLM parsing would add cost, latency, and non-determinism.
- **Runtime MCP process discovery for ToolRouter:** The user explicitly chose static registry. Do NOT start FastMCP server processes or connect via stdio/SSE to discover tools.
- **Prompt assembly per-turn:** PromptAssembler runs once per phase (producing the system prompt). It does NOT re-assemble on each conversation turn. The system prompt is set once for the entire agent execution.
- **Installing anthropic SDK in Phase 8:** The anthropic SDK is NOT needed until Phase 9 (AgentRunner). Phase 8 works with raw dict structures matching the Anthropic API wire format. Use TypedDicts/Pydantic for validation.
- **Skill content truncation:** The user decided full SKILL.md injection. Skills range 4-28KB. Even 3 skills at 28KB = 84KB << 200K context window. Do NOT truncate.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| YAML frontmatter parsing | Custom parser | PyYAML `safe_load` on frontmatter block | Frontmatter is standard YAML between `---` delimiters; already used in workflow_parser |
| Tool result serialization | Custom format | Anthropic API wire format dicts | The format is well-defined (tool_result with tool_use_id, content, is_error); TypedDicts suffice |
| Django model migration | Manual SQL | `python manage.py makemigrations` | Adding artifact_type and structured_data fields is a standard Django migration |
| Pydantic model validation | Manual dict checking | Pydantic BaseModel with field validators | Already established pattern (WorkflowSchema, StructuredFinding, CraftLearning) |

**Key insight:** These components are glue code between well-defined interfaces (markdown files, YAML schemas, Anthropic API format, Django models). The interfaces are already defined. The implementation is straightforward wiring.

## Common Pitfalls

### Pitfall 1: Circular imports between orchestrator modules
**What goes wrong:** prompt_assembler.py imports from agent_manager.py which imports from executor.py which will import prompt_assembler.py in Phase 9.
**Why it happens:** The orchestrator package has interconnected modules.
**How to avoid:** prompt_assembler.py should ONLY import `read_agent_persona` from agent_manager.py (a pure function with no side effects). tool_router.py and output_collector.py should be self-contained. executor.py will import FROM these modules, not vice versa.
**Warning signs:** ImportError on module load in tests.

### Pitfall 2: FastMCP tool introspection without running servers
**What goes wrong:** Trying to call `mcp.list_tools()` which is an async method designed for the MCP protocol, not direct Python introspection.
**Why it happens:** FastMCP's public API is MCP-protocol-oriented, not Python-introspection-oriented.
**How to avoid:** Import the server module (which triggers `@mcp.tool()` decorator execution), then access the FastMCP instance's internal `_tool_manager` or iterate the decorated functions. Alternatively, maintain a parallel static registry (a dict mapping tool names to server names) that is manually kept in sync with the 4 server modules.
**Warning signs:** Needing to start an event loop or MCP transport just to list tool names.

### Pitfall 3: Django settings not configured in test
**What goes wrong:** Importing MCP server modules (which do `django.setup()` at module level) during test collection causes settings conflicts.
**Why it happens:** MCP server modules have `os.environ.setdefault("DJANGO_SETTINGS_MODULE", ...)` at top level.
**How to avoid:** For ToolRouter's static registry, either (a) build the registry at runtime only (not at import time), or (b) import the MCP modules lazily inside `build_tool_registry()`. For tests, the pytest config already sets `--ds=config.settings.test`.
**Warning signs:** `ImproperlyConfigured` during test collection.

### Pitfall 4: Markdown parsing edge cases in OutputCollector
**What goes wrong:** Agent output doesn't perfectly follow the expected conventions (missing heading levels, inconsistent bullet formatting, code blocks without artifact tags).
**Why it happens:** LLM output is non-deterministic; even well-prompted agents occasionally deviate from format.
**How to avoid:** Make the parser tolerant: use fallback patterns, treat the entire output as a valid Report artifact even if no structured sections are found. Log parsing failures as warnings, not errors. The Report artifact (full markdown body) is always produced.
**Warning signs:** Empty artifacts list from a non-empty agent output.

### Pitfall 5: Reference file injection bloating context
**What goes wrong:** The ui-audit skill has 19 reference files. Blindly injecting all of them adds ~50KB+ to the prompt.
**Why it happens:** The `include_references` flag defaults to True without size awareness.
**How to avoid:** Use the `reference_size_limit` parameter (default 15KB per file). For large reference sets, include a summary noting the reference exists but is omitted. The user gave Claude discretion on this -- the recommendation is size-based filtering.
**Warning signs:** Prompt assembly producing >100KB for a single skill.

### Pitfall 6: Test isolation with Django models
**What goes wrong:** Tests for OutputCollector need WorkflowPhaseOutput (Django model) but test_output_collector.py tests should work without a database.
**Why it happens:** OutputCollector produces Pydantic models (CollectedArtifact), not Django models. The Django model extension is separate.
**How to avoid:** OutputCollector returns `list[CollectedArtifact]` (pure Pydantic). The integration with WorkflowPhaseOutput (saving to DB) is done by the caller (executor.py in Phase 9). Unit tests for OutputCollector don't need `@pytest.mark.django_db`.
**Warning signs:** OutputCollector tests requiring database fixtures.

## Code Examples

### Anthropic API tool_use content block (verified from official docs)
```json
{
  "type": "tool_use",
  "id": "toolu_01A09q90qw90lq917835lq9",
  "name": "load_context",
  "input": {
    "agent_id": "agent-seo-specialist--client-123",
    "l3_client_id": "550e8400-e29b-41d4-a716-446655440000",
    "l2_agency_id": "660e8400-e29b-41d4-a716-446655440001"
  }
}
```
Source: https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use

### Anthropic API tool_result (what ToolRouter must return)
```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
  "content": "{\"status\": \"Context loaded for agent=agent-seo... client=550e...\"}"
}
```

### Anthropic API tool_result with error
```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
  "content": "Tool error: VaultCredential matching query does not exist.",
  "is_error": true
}
```

### Claude Agent SDK tool result format
```python
# Agent SDK tools return content blocks (MCP protocol format)
{"content": [{"type": "text", "text": "Context loaded for agent=..."}]}

# Error format
{"content": [{"type": "text", "text": "Tool error: ..."}], "isError": True}
```
Source: https://platform.claude.com/docs/en/agent-sdk/python

### Existing FastMCP tool registration pattern (from hazn_memory_server.py)
```python
mcp = FastMCP("hazn-memory")

@mcp.tool()
def load_context(agent_id: str, l3_client_id: str, l2_agency_id: str) -> str:
    """Load L2+L3 client context into agent's active memory block."""
    memory = _get_or_create_memory(agent_id, l3_client_id, l2_agency_id)
    memory.load_client_context()
    return f"Context loaded for agent={agent_id} client={l3_client_id}"
```

### SKILL.md frontmatter format (from seo-audit)
```yaml
---
name: seo-audit
description: Run a comprehensive SEO audit on any external website.
allowed-tools: web_fetch, web_search, Bash, Read, Write
---
```

### Workflow YAML with skills (from analytics-audit.yaml)
```yaml
phases:
  - id: analysis
    name: Analysis & Report Writing
    agent: analytics-report-writer
    depends_on: [data-collection]
    skills: [analytics-audit, analytics-audit-martech]
    outputs: [.hazn/outputs/analytics-audit/<domain>-audit.md]
```

### Existing WorkflowPhaseOutput model (to be extended)
```python
class WorkflowPhaseOutput(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_run = models.ForeignKey(WorkflowRun, on_delete=models.CASCADE, related_name="phase_outputs")
    phase_id = models.CharField(max_length=100)
    output_type = models.CharField(max_length=100)
    content = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    # NEW FIELDS (Phase 8 migration):
    # artifact_type = models.CharField(max_length=50, blank=True, default="")
    # structured_data = models.JSONField(default=dict, blank=True)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Letta message API for agent execution | Anthropic API tool_use loop + Claude Agent SDK | v2.0 (current) | PromptAssembler replaces Letta system prompt injection |
| OpenClaw agent framework | Direct Anthropic SDK + custom runtime | 2026-03 decision | ToolRouter is purpose-built, not wrapping a framework |
| MCP tools via running processes | Static registry at startup | Phase 8 decision | No MCP server lifecycle management needed |
| Hardcoded executor output | Convention-based OutputCollector | Phase 8 | Structured artifacts replace placeholder dicts |

**Deprecated/outdated:**
- Letta agent personas (`get_or_create_agent` in agent_manager.py): Still used for persistent agent lifecycle, but PromptAssembler takes over system prompt construction for the hybrid runtime.
- Direct Letta message API: Will be replaced by Anthropic API / Agent SDK in Phase 9.

## Open Questions

1. **FastMCP tool introspection API stability**
   - What we know: FastMCP 3.1.0 stores tools internally via `_tool_manager`. The `@mcp.tool()` decorator registers tools at import time. We can access tools via `mcp._tool_manager` or the internal tool dict.
   - What's unclear: Whether the internal API (`_tool_manager`) is stable across FastMCP versions. The public API (`list_tools`) requires an MCP protocol connection.
   - Recommendation: Build a hardcoded static registry mapping tool names to server names. This is more maintainable than relying on FastMCP internals, and the 4 servers / 20 tools change infrequently. Validate at startup that the registry matches what the modules actually register.

2. **Agent output format consistency across workflows**
   - What we know: The seo-audit skill prescribes a specific output format with Score Summary, Issues, Recommendations sections. Analytics-audit has sections A-J with different formatting.
   - What's unclear: How consistent agent output will actually be across 7 workflows. This has never been tested with real LLM execution.
   - Recommendation: Make OutputCollector's patterns tolerant. The Report artifact (full markdown body) is always valid. Findings extraction is best-effort. Phase 11 (Agent Quality / Red Team) will validate output format compliance.

3. **WorkflowPhaseOutput migration backward compatibility**
   - What we know: Adding `artifact_type` (CharField, blank=True, default="") and `structured_data` (JSONField, default=dict, blank=True) are additive changes with defaults.
   - What's unclear: Whether existing WorkflowPhaseOutput records from Phase 7 executor tests will need backfilling.
   - Recommendation: Use `blank=True, default=""` / `default=dict` so existing records are unaffected. No data migration needed.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 + pytest-django 4.12.0 + pytest-asyncio 1.3.0 |
| Config file | `hazn_platform/pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `cd hazn_platform && .venv/bin/pytest tests/test_prompt_assembler.py tests/test_tool_router.py tests/test_output_collector.py -x -q` |
| Full suite command | `cd hazn_platform && .venv/bin/pytest tests/ -x -q` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RUNT-01 | Given agent name + skill list + client context, produces complete system prompt with persona + skill instructions + L2/L3 data | unit | `.venv/bin/pytest tests/test_prompt_assembler.py -x` | No -- Wave 0 |
| RUNT-01 | System prompt includes full SKILL.md content (not truncated) | unit | `.venv/bin/pytest tests/test_prompt_assembler.py::TestSkillInjection -x` | No -- Wave 0 |
| RUNT-01 | Reference docs inlined for small files, noted for large files | unit | `.venv/bin/pytest tests/test_prompt_assembler.py::TestReferenceHandling -x` | No -- Wave 0 |
| RUNT-03 | Given Anthropic API tool_use block, dispatches to correct handler and returns tool_result | unit | `.venv/bin/pytest tests/test_tool_router.py::TestAnthropicDispatch -x` | No -- Wave 0 |
| RUNT-03 | Given Claude Agent SDK tool call, dispatches and returns MCP content blocks | unit | `.venv/bin/pytest tests/test_tool_router.py::TestAgentSDKDispatch -x` | No -- Wave 0 |
| RUNT-03 | Unknown tool returns is_error=true with clear message | unit | `.venv/bin/pytest tests/test_tool_router.py::TestErrorHandling -x` | No -- Wave 0 |
| RUNT-03 | Tool exception wrapped as is_error=true (agent doesn't crash) | unit | `.venv/bin/pytest tests/test_tool_router.py::TestErrorHandling -x` | No -- Wave 0 |
| RUNT-08 | Given agent markdown with findings section, extracts StructuredFinding-compatible data | unit | `.venv/bin/pytest tests/test_output_collector.py::TestFindingsExtraction -x` | No -- Wave 0 |
| RUNT-08 | Given agent markdown, always produces Report artifact (full body) | unit | `.venv/bin/pytest tests/test_output_collector.py::TestReportArtifact -x` | No -- Wave 0 |
| RUNT-08 | Given code blocks with artifact tags, extracts code artifacts | unit | `.venv/bin/pytest tests/test_output_collector.py::TestCodeArtifacts -x` | No -- Wave 0 |
| RUNT-08 | Metadata artifact includes word count, section count, topics | unit | `.venv/bin/pytest tests/test_output_collector.py::TestMetadataExtraction -x` | No -- Wave 0 |
| ALL | All three components work with mock data, no API keys, no LLM calls | unit | `.venv/bin/pytest tests/test_prompt_assembler.py tests/test_tool_router.py tests/test_output_collector.py -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `.venv/bin/pytest tests/test_prompt_assembler.py tests/test_tool_router.py tests/test_output_collector.py -x -q`
- **Per wave merge:** `.venv/bin/pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_prompt_assembler.py` -- covers RUNT-01
- [ ] `tests/test_tool_router.py` -- covers RUNT-03
- [ ] `tests/test_output_collector.py` -- covers RUNT-08
- [ ] `tests/fixtures/tool_use_responses.json` -- mock Anthropic API tool_use blocks
- [ ] `tests/fixtures/agent_sdk_tool_calls.json` -- mock Agent SDK format calls
- [ ] `tests/fixtures/agent_outputs/seo_audit_report.md` -- realistic agent output fixture
- [ ] `tests/fixtures/agent_outputs/analytics_findings.md` -- findings-heavy output fixture
- [ ] `hazn_platform/testing/__init__.py` -- reusable mock module for Phase 9+
- [ ] `hazn_platform/testing/mocks.py` -- mock LLM response builder, mock tool dispatch
- [ ] `hazn_platform/testing/fixtures.py` -- fixture data loaders
- [ ] No new framework install needed (pytest 9.0.2 already configured)

## Sources

### Primary (HIGH confidence)
- Existing codebase: `hazn_platform/orchestrator/agent_manager.py` -- `read_agent_persona()` function signature and behavior
- Existing codebase: `hazn_platform/orchestrator/workflow_models.py` -- `WorkflowPhaseSchema` with skills, tools, agent fields
- Existing codebase: `hazn_platform/orchestrator/executor.py` -- placeholder comments at lines 226-248 showing integration points
- Existing codebase: `hazn_platform/orchestrator/models.py` -- `WorkflowPhaseOutput` model to extend
- Existing codebase: `hazn_platform/core/memory_types.py` -- `StructuredFinding` schema
- Existing codebase: 4 MCP servers (`hazn_memory_server.py`, `analytics_server.py`, `github_server.py`, `vercel_server.py`) -- 20+ tool definitions
- Existing codebase: 15 agent personas in `hazn/agents/` -- markdown files
- Existing codebase: 28 skills in `hazn/skills/` -- SKILL.md files with frontmatter
- Anthropic tool_use docs: https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use -- tool_use/tool_result JSON format

### Secondary (MEDIUM confidence)
- Claude Agent SDK Python reference: https://platform.claude.com/docs/en/agent-sdk/python -- tool call format, MCP server integration
- FastMCP 3.1.0 source code (installed in venv) -- tool registration internals

### Tertiary (LOW confidence)
- FastMCP tool introspection via `_tool_manager` -- internal API, may change between versions

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all dependencies already installed, no new packages
- Architecture: HIGH -- clear integration points in existing code (executor.py placeholders, existing models), well-defined Anthropic API format
- Pitfalls: HIGH -- identified from actual codebase inspection (circular imports, Django setup in MCP modules, reference file sizes)

**Research date:** 2026-03-06
**Valid until:** 2026-04-06 (stable -- all dependencies pinned, architecture decisions locked)

---
*Phase: 08-foundation-components*
*Research completed: 2026-03-06*

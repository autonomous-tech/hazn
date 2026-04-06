# Phase 8: Foundation Components - Context

**Gathered:** 2026-03-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the three components that surround agent execution -- prompt construction, tool dispatch, and artifact capture -- all working correctly without any LLM calls. These are the building blocks that Phase 9 (AgentRunner) will wire into the real execution loop.

Requirements: RUNT-01 (PromptAssembler), RUNT-03 (ToolRouter), RUNT-08 (OutputCollector)

</domain>

<decisions>
## Implementation Decisions

### Prompt Assembly (RUNT-01)
- Full SKILL.md content injection for each skill declared in the workflow phase (typically 0-3 skills per phase)
- Skills are the agent's domain knowledge -- full content is necessary for quality output
- 200k context window makes full injection comfortable for 0-3 skills
- Prompt ordering (persona vs. skills vs. context layering): Claude's discretion
- Reference docs in `skills/*/references/` handling: Claude's discretion (archival vs. prompt)
- Skill frontmatter `allowed-tools` field: Claude's discretion (informational vs. tool scoping source)

### Tool Routing (RUNT-03)
- Static registry: build tool-to-server mapping at startup from MCP server configurations
- No runtime discovery (avoids running MCP processes requirement)
- Return tool results in Anthropic-native format (tool_result content blocks with tool_use_id)
- Wrap tool errors and return to agent as is_error=true with clear error message (prevents agent crashes)
- Support BOTH Anthropic API tool_use format AND Claude Agent SDK tool call format from day one

### Artifact Capture (RUNT-08)
- Convention-based markdown parsing: define markdown conventions agents must follow (## Findings, ## Recommendations, ```artifact blocks)
- Skill instructions already guide agent output format; no LLM needed for parsing
- Four artifact types recognized:
  - **Report**: full markdown body (main deliverable content for Jinja2 -> HTML pipeline)
  - **Findings**: structured list with severity, description, evidence, recommendation (maps to existing StructuredFinding in memory_types.py)
  - **Code artifacts**: generated code blocks tagged with language and target file path
  - **Metadata**: phase-level summary + stats (word count, topic coverage, key decisions)
- Final agent output only -- not intermediate tool results (those are already in WorkflowToolCall model)
- Extend existing WorkflowPhaseOutput model (add artifact_type, structured_data fields)

### Mock Testing
- Real content with mock interfaces: use actual agent persona files, real SKILL.md content, realistic L2/L3 client fixtures
- Only mock LLM responses and MCP server connections
- JSON fixture files in tests/fixtures/ for mock Anthropic API tool_use response shapes
- Standalone reusable mock module (hazn_platform/testing/) for Phase 9+ reuse
- Realistic agent output samples in fixtures (actual markdown reports following conventions)

### Claude's Discretion
- System prompt section ordering and structure
- Reference docs injection strategy (archival vs. prompt based on size)
- Skill frontmatter `allowed-tools` handling
- Convention-based parser specifics (exact markdown patterns, edge case handling)
- Mock module internal API design

</decisions>

<specifics>
## Specific Ideas

- Skills in Claude Code use progressive disclosure (loaded on trigger). For Hazn's autonomous agents, workflow YAML pre-declares skills per phase, so full injection at prompt assembly time is the right approach.
- The existing `agent_manager.read_agent_persona()` already reads persona markdown -- PromptAssembler builds on this.
- Workflow YAML is the source of truth for tool scoping (tools: field per phase), not skill frontmatter.
- ToolRouter should support both Anthropic API and Claude Agent SDK formats from Phase 8, not deferred to Phase 9.

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `agent_manager.read_agent_persona()`: reads persona markdown from hazn/agents/{type}.md
- `workflow_parser.load_workflow()`: parses YAML into validated WorkflowPhaseSchema with skills, tools, agent fields
- `workflow_models.WorkflowPhaseSchema`: Pydantic schema with skills (list[str]), tools (list[str]), agent (str)
- `HaznMemory.load_client_context()`: injects L2+L3 context into agent memory
- `WorkflowPhaseOutput` model: stores structured phase outputs linked to workflow_run
- `StructuredFinding` in memory_types.py: existing schema for findings
- 4 FastMCP servers: hazn-memory (7 tools), analytics, github, vercel
- 15 agent persona files in hazn/agents/
- 27 skill directories in hazn/skills/ (each with SKILL.md + optional references/)
- 7 workflow YAML files in hazn/workflows/

### Established Patterns
- Django model pattern: UUID primary keys, JSONField for flexible content, auto_now timestamps
- FastMCP for MCP servers: Python-native, register tools with decorators
- Pydantic for validation: WorkflowSchema with ConfigDict(extra="allow")
- async execution with sync_to_async wrapping for Django ORM calls
- Test pattern: pytest + Django test framework with factory-style fixtures

### Integration Points
- PromptAssembler feeds into executor._execute_phase() where the placeholder comment lives (line 226-230 of executor.py)
- ToolRouter replaces the placeholder agent execution in executor._execute_phase()
- OutputCollector processes output at line 234-248 of executor.py (currently hardcoded dict)
- All three components must work with WorkflowSession (session.py) for lifecycle management
- WorkflowPhaseOutput model needs migration for new artifact fields

</code_context>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 08-foundation-components*
*Context gathered: 2026-03-06*

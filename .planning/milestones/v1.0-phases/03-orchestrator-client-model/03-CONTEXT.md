# Phase 3: Orchestrator & Client Model - Context

**Gathered:** 2026-03-05
**Status:** Ready for planning

<domain>
## Phase Boundary

The orchestrator manages complete workflow sessions -- loading L2+L3 context, coordinating multi-agent execution via workflow YAML interpretation, enforcing the three-layer client hierarchy with conflict resolution, handling credentials via Vault, tracking metering data, and surfacing conflicts and alerts for human review via HITL queue. This phase creates the session lifecycle, client model logic, credential management, metering tables, and HITL queue.

</domain>

<decisions>
## Implementation Decisions

### Workflow Execution Model
- Parallel execution where dependencies allow -- if two phases share no deps (e.g., copy and wireframe both depend on ux but not each other), run simultaneously
- One persistent Letta agent per type per L3 client, reused across all workflows -- memory compounds over time
- Persona/system prompt refreshed from latest agent markdown at every session start; archival memory (craft learnings) persists across updates
- Phase outputs stored as database records (workflow_phase_outputs table) -- structured, queryable, agents query DB rather than read files
- On phase failure: halt the workflow, trigger failure_sync for memory preservation, flag workflow_run as 'failed' with error details; required phases block, optional phases can be skipped by the agency on retry

### HITL Queue & Approvals
- Four trigger types: L2/L3 conflicts, workflow checkpoints, cost threshold alerts, agent uncertainty
- Notifications via webhook to a configurable URL (agencies route to Slack/email/etc) plus a polling API for the Mode 3 dashboard
- Timeout behavior configurable per trigger type with defaults: L2/L3 conflicts -> L3 wins (existing rule); checkpoints -> auto-approve and continue; cost alerts -> halt workflow; agent uncertainty -> proceed with warning
- HITL items block workflow execution by default; agencies can mark specific trigger types as non-blocking (e.g., agent uncertainty can be fire-and-forget)

### L2/L3 Conflict Detection
- Rule declarations + LLM check: L2 agencies declare explicit locked rules in their house_style JSON; orchestrator runs a lightweight LLM check comparing locked rules against L3 brand voice at session start
- Locked rules structured as JSON inside existing Agency.house_style field: `locked_rules` key with array of `{rule: "text", category: "tone|terms|legal", severity: "hard|soft"}` -- hard rules always override L3; soft rules flag for review
- Conflict detection runs once at session start (pre-flight check before any agent work begins)
- Auto-resolved conflicts (L3 wins by default) are logged in the workflow_run record and included in the HITL queue as non-blocking 'info' items -- agency can review resolutions after the fact

### Metering & Workflow Records
- Full breakdown across three tables: workflow_runs (status, total_tokens, total_cost, wall_clock_time, turn_count, started_at, ended_at, error_details), workflow_agents (per-agent tokens, cost, turns, phase_id), workflow_tool_calls (per-tool call count, cost, latency)
- Real-time cost tracking via callback/hook on LLM calls -- orchestrator accumulates per-agent and writes to workflow_agents on phase completion
- Runaway/cost thresholds configurable per L2 agency in Agency.tool_preferences (max_turns, max_cost_per_run) with defaults: 50 turns, $5/run
- When a runaway agent or cost outlier is detected mid-run: enters HITL queue as a blocking cost alert; configurable timeout default action: halt

### Credential Management
- Orchestrator fetches secrets from Vault using vault_secret_id at runtime via read-only AppRole (already set up in Phase 7)
- Raw secrets never appear in agent context or LLM prompts -- passed directly to tool calls via get_credentials() MCP tool
- Credentials scoped per L2/L3 via existing VaultCredential model (service_name + vault_secret_id per agency/end_client)
- Tool access scoped per agent type via workflow YAML -- principle of least privilege (orchestrator only provides tools declared for the agent's phase)

### Claude's Discretion
- Exact database schema for workflow_runs, workflow_agents, workflow_tool_calls, workflow_phase_outputs, and hitl_queue tables
- HITL queue Postgres model design and state machine
- Webhook delivery implementation details (retry, payload format)
- LLM callback/hook implementation for cost tracking
- Conflict detection prompt design for the LLM check
- Workflow YAML parser implementation approach
- Agent creation/lookup logic for persistent per-type-per-client agents

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `core/memory.py`: HaznMemory class -- orchestrator will use load_client_context(), record_turn(), checkpoint_sync(), failure_sync(), end_session() for session lifecycle
- `core/models.py`: Agency (house_style JSONField for locked_rules), EndClient, VaultCredential (credential scoping), MemoryCorrection
- `core/vault.py`: read_secret() with AppRole auth -- orchestrator calls this for credential fetching
- `core/letta_client.py`: get_letta_client() factory -- used by HaznMemory, orchestrator uses HaznMemory as the abstraction
- `mcp_servers/hazn_memory_server.py`: MCP server with load_context, write_finding, search_memory, checkpoint_sync, correct_memory, get_credentials tools
- `hazn/workflows/*.yaml`: 7 workflow definitions with phases, dependencies, outputs, checkpoints -- the orchestrator's input format

### Established Patterns
- UUID primary keys on all models
- Domain-split Django apps: core, marketing, content -- new orchestrator app likely needed
- JSONField for flexible data (house_style, tool_preferences, methodology) -- locked_rules and metering thresholds fit here
- Append-only with provenance pattern (Phase 2: _provenance key in JSONFields)
- Celery + Redis already configured for async task execution
- AppRole-based Vault auth with per-service scoping

### Integration Points
- Workflow YAML files in `hazn/workflows/` define multi-phase agent coordination
- Agent persona markdowns in `hazn/agents/` -- orchestrator reads latest at session start to refresh Letta persona
- HaznMemory is the only interface to Letta -- orchestrator never calls Letta SDK directly
- Celery available for async workflow execution and webhook delivery
- Agency.tool_preferences already used for context_loading_policy and cross_client_insights -- extend for metering thresholds

</code_context>

<specifics>
## Specific Ideas

- Phase outputs as database records (not filesystem) -- agency chose queryable structured storage over file-based artifacts
- Agent persona always refreshed at session start -- user wants agents to be updatable without manual intervention; asked "what happens when agents get updated on the backend" which drove this decision
- All four HITL trigger types selected -- user wants comprehensive human oversight, not just L2/L3 conflicts
- Configurable defaults everywhere -- per-L2 thresholds, per-trigger-type timeout actions, per-trigger-type blocking behavior; agencies have different tolerances

</specifics>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 03-orchestrator-client-model*
*Context gathered: 2026-03-05*

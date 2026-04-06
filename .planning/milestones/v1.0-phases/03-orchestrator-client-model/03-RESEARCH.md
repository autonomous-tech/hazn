# Phase 3: Orchestrator & Client Model - Research

**Researched:** 2026-03-05
**Domain:** Multi-agent workflow orchestration, client hierarchy management, credential handling, metering
**Confidence:** HIGH

## Summary

Phase 3 builds the orchestration layer that ties together the memory layer (Phase 2), Vault credentials (Phase 7), and workflow YAML definitions into a cohesive session-based execution engine. The orchestrator manages complete workflow sessions: loading L2+L3 context, interpreting workflow YAML for multi-agent coordination with dependency-aware parallel execution, enforcing the three-layer client hierarchy with conflict resolution, tracking metering data, and surfacing issues via a HITL queue.

The existing codebase provides strong foundations. HaznMemory (Phase 2) is the sole interface to Letta -- the orchestrator calls it, never the Letta SDK directly. Vault credential management (Phase 7) with AppRole auth is complete. Workflow YAML files in `hazn/workflows/` define the execution graph. Celery + Redis is already configured for async task execution. The orchestrator needs to be a new Django app that adds models (workflow_runs, workflow_agents, workflow_tool_calls, workflow_phase_outputs, hitl_queue), a YAML parser, a DAG executor, conflict detection logic, and Celery tasks for async workflow execution and webhook delivery.

**Primary recommendation:** Create a new `orchestrator` Django app with Pydantic models for YAML validation, Python stdlib `graphlib.TopologicalSorter` for dependency-aware parallel phase execution, Celery tasks for async workflow runs and webhook delivery, and Django models for metering/HITL state.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions
- Parallel execution where dependencies allow -- if two phases share no deps (e.g., copy and wireframe both depend on ux but not each other), run simultaneously
- One persistent Letta agent per type per L3 client, reused across all workflows -- memory compounds over time
- Persona/system prompt refreshed from latest agent markdown at every session start; archival memory (craft learnings) persists across updates
- Phase outputs stored as database records (workflow_phase_outputs table) -- structured, queryable, agents query DB rather than read files
- On phase failure: halt the workflow, trigger failure_sync for memory preservation, flag workflow_run as 'failed' with error details; required phases block, optional phases can be skipped by the agency on retry
- Four HITL trigger types: L2/L3 conflicts, workflow checkpoints, cost threshold alerts, agent uncertainty
- Notifications via webhook to a configurable URL (agencies route to Slack/email/etc) plus a polling API for the Mode 3 dashboard
- Timeout behavior configurable per trigger type with defaults: L2/L3 conflicts -> L3 wins; checkpoints -> auto-approve and continue; cost alerts -> halt workflow; agent uncertainty -> proceed with warning
- HITL items block workflow execution by default; agencies can mark specific trigger types as non-blocking
- Rule declarations + LLM check: L2 agencies declare explicit locked rules in their house_style JSON; orchestrator runs a lightweight LLM check comparing locked rules against L3 brand voice at session start
- Locked rules structured as JSON inside existing Agency.house_style field: `locked_rules` key with array of `{rule: "text", category: "tone|terms|legal", severity: "hard|soft"}`
- Conflict detection runs once at session start (pre-flight check before any agent work begins)
- Auto-resolved conflicts logged in workflow_run record and included in HITL queue as non-blocking 'info' items
- Full metering breakdown across three tables: workflow_runs, workflow_agents, workflow_tool_calls
- Real-time cost tracking via callback/hook on LLM calls
- Runaway/cost thresholds configurable per L2 agency in Agency.tool_preferences (max_turns, max_cost_per_run) with defaults: 50 turns, $5/run
- Orchestrator fetches secrets from Vault using vault_secret_id at runtime via read-only AppRole
- Raw secrets never appear in agent context or LLM prompts -- passed directly to tool calls via get_credentials() MCP tool
- Credentials scoped per L2/L3 via existing VaultCredential model
- Tool access scoped per agent type via workflow YAML -- principle of least privilege

### Claude's Discretion
- Exact database schema for workflow_runs, workflow_agents, workflow_tool_calls, workflow_phase_outputs, and hitl_queue tables
- HITL queue Postgres model design and state machine
- Webhook delivery implementation details (retry, payload format)
- LLM callback/hook implementation for cost tracking
- Conflict detection prompt design for the LLM check
- Workflow YAML parser implementation approach
- Agent creation/lookup logic for persistent per-type-per-client agents

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| ORCH-01 | Orchestrator loads L2+L3 context from Postgres at session start | HaznMemory.load_client_context() already does this; orchestrator calls it after creating/retrieving the agent |
| ORCH-02 | Orchestrator injects context into agent via mcp-hazn-memory | MCP load_context tool already implemented; orchestrator coordinates the call |
| ORCH-03 | Orchestrator manages session lifecycle (start, checkpoint every 10 turns, end/timeout at 4hr) | HaznMemory has record_turn(), checkpoint_sync(), end_session(), failure_sync(); orchestrator manages the outer lifecycle wrapper |
| ORCH-04 | Orchestrator writes workflow_runs to Postgres (metering source of truth) | New WorkflowRun, WorkflowAgent, WorkflowToolCall models needed |
| ORCH-05 | Orchestrator manages HITL queue and conflict flags | New HITLItem model with state machine needed |
| ORCH-06 | Orchestrator interprets workflow YAML to coordinate multi-agent execution | graphlib.TopologicalSorter for DAG execution; Pydantic for YAML validation |
| ORCH-07 | Orchestrator scopes tool access per agent type (principle of least privilege) | Letta agents.create(tool_ids=[...]) and agents.tools.attach/detach API |
| CLT-01 | Three-layer client model: L1 (Autonomous), L2 (agencies), L3 (end-clients) | Agency and EndClient models already exist in core.models |
| CLT-02 | L2 agencies have house style, methodology, approved templates, tool preferences | Agency model already has house_style, methodology, tool_preferences JSONFields |
| CLT-03 | L3 end-clients have brand voice, campaigns, keywords, competitors, history | EndClient + BrandVoice + Campaign + Keyword models already exist |
| CLT-04 | L3 brand voice wins by default in L2/L3 conflicts | Conflict detection logic compares locked_rules vs brand voice; default resolution: L3 wins |
| CLT-05 | L2 can lock specific rules that override L3 (legal/compliance) | locked_rules in Agency.house_style with severity "hard" always override L3 |
| CLT-06 | Agent flags L2/L3 conflicts in HITL queue with 24-hour timeout | HITLItem model with configurable timeout per trigger type |
| CRED-01 | Orchestrator fetches secrets from Vault using vault_secret_id at runtime | vault.read_secret() already implemented; orchestrator role has read-only access |
| CRED-02 | Raw secrets never appear in agent context or LLM prompts | get_credentials MCP tool passes secrets directly to tool calls only |
| CRED-03 | Credentials scoped per L2/L3 client (GA4, GSC, Ahrefs, CMS, Vercel, ESP) | VaultCredential model with service_name + nullable agency/end_client FKs exists |
| CRED-04 | get_credentials() MCP tool passes secrets directly to tool calls | Already implemented in hazn_memory_server.py Tool 7 |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Django | 5.2.12 | Framework, ORM, models for orchestrator app | Already in use; new app follows established pattern |
| Celery | 5.6.2 | Async workflow execution, webhook delivery | Already configured with Redis broker; autodiscover_tasks |
| graphlib (stdlib) | Python 3.13 | Topological sort for workflow DAG execution | Built-in, no dependency; designed for parallel execution via prepare/get_ready/done |
| PyYAML | 6.0.3 | Parse workflow YAML files | Already a transitive dependency; safe_load for YAML parsing |
| Pydantic | (transitive) | Validate parsed YAML into typed workflow models | Already used for memory_types; model_validate for YAML schema validation |
| letta-client | >=1.7.11 | Agent management (create, list, modify, tools.attach/detach) | Already pinned; used via HaznMemory abstraction |
| hvac | 2.4.0 | Vault credential fetching | Already in use via core.vault |
| DRF | 3.16.0 | HITL polling API for Mode 3 dashboard | Already installed; REST API for HITL queue |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| langfuse | (needs install) | LLM call tracing with cost tracking | OBS-01 requirement; @observe decorator for generation tracing |
| django-celery-beat | 2.9.0 | Scheduled tasks (HITL timeout checks) | Already installed; periodic task for timeout processing |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| graphlib (stdlib) | Celery canvas (chain/chord/group) | Celery canvas is for task-level DAG; graphlib is simpler for phase-level DAG within a single orchestrator task |
| Custom YAML parser | Prefect/Airflow | Massive overkill for 7 workflow definitions; custom parser with Pydantic validation is < 200 lines |
| Django models for HITL | External queue (SQS/RabbitMQ) | Postgres is the metering source of truth; HITL queue is low-volume; no need for external queue |

**Installation:**
```bash
cd hazn_platform && uv add langfuse
```

Note: langfuse is needed for OBS-01 (Langfuse SDK traces every LLM call). However, OBS-01 is officially a Phase 4 requirement. Phase 3 should prepare the metering callback hook interface but can defer Langfuse installation to Phase 4 if preferred.

## Architecture Patterns

### Recommended Project Structure
```
hazn_platform/hazn_platform/
  orchestrator/                   # NEW Django app
    __init__.py
    apps.py
    models.py                     # WorkflowRun, WorkflowAgent, WorkflowToolCall,
                                  #   WorkflowPhaseOutput, HITLItem
    admin.py
    migrations/
      __init__.py
      0001_initial.py
    workflow_parser.py            # YAML -> Pydantic models
    workflow_models.py            # Pydantic models for workflow YAML schema
    executor.py                   # DAG-based workflow execution engine
    conflict_detector.py          # L2/L3 conflict detection (LLM-based pre-flight)
    agent_manager.py              # Persistent agent lookup/creation/persona refresh
    session.py                    # Session lifecycle (start, checkpoint, end, timeout)
    metering.py                   # Real-time cost tracking callbacks
    tasks.py                      # Celery tasks (run_workflow, deliver_webhook, check_timeouts)
    api/
      __init__.py
      serializers.py              # DRF serializers for HITL queue, workflow status
      views.py                    # HITL polling API endpoints
      urls.py
```

### Pattern 1: Workflow YAML Parsing with Pydantic Validation
**What:** Parse workflow YAML files using PyYAML safe_load, validate with Pydantic models
**When to use:** At workflow start, when loading the workflow definition
**Example:**
```python
# Source: Python stdlib + Pydantic patterns
import yaml
from pydantic import BaseModel, Field

class WorkflowPhaseSchema(BaseModel):
    id: str
    name: str
    agent: str | None = None
    depends_on: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    required: bool = True
    tools: list[str] = Field(default_factory=list)  # tool scoping
    skills: list[str] = Field(default_factory=list)

class WorkflowCheckpoint(BaseModel):
    after: str
    message: str

class WorkflowSchema(BaseModel):
    name: str
    description: str
    trigger: str
    phases: list[WorkflowPhaseSchema]
    checkpoints: list[WorkflowCheckpoint] = Field(default_factory=list)

def load_workflow(path: str) -> WorkflowSchema:
    with open(path) as f:
        data = yaml.safe_load(f)
    return WorkflowSchema.model_validate(data)
```

### Pattern 2: DAG Execution with graphlib.TopologicalSorter
**What:** Build dependency graph from workflow phases, execute in parallel where dependencies allow
**When to use:** Orchestrator runs phases in correct order, maximizing parallelism
**Example:**
```python
# Source: Python docs - graphlib.TopologicalSorter
from graphlib import TopologicalSorter
import asyncio

async def execute_workflow_dag(phases: list[WorkflowPhaseSchema]):
    graph = {}
    for phase in phases:
        graph[phase.id] = set(phase.depends_on)

    ts = TopologicalSorter(graph)
    ts.prepare()

    while ts.is_active():
        ready = ts.get_ready()
        # Execute all ready phases in parallel
        results = await asyncio.gather(
            *[execute_phase(pid) for pid in ready],
            return_exceptions=True
        )
        for pid, result in zip(ready, results):
            if isinstance(result, Exception):
                raise result  # halt on failure
            ts.done(pid)
```

### Pattern 3: Persistent Agent Per Type Per Client
**What:** One Letta agent per agent-type per L3 client, reused across workflows
**When to use:** At phase execution start -- look up or create agent
**Example:**
```python
# Source: Letta Python SDK docs
from letta_client import Letta

def get_or_create_agent(
    client: Letta,
    agent_type: str,      # e.g. "seo-specialist"
    l3_client_id: str,
    persona_markdown: str,
    tool_ids: list[str],
) -> str:
    """Return existing agent_id or create a new persistent agent."""
    # Convention: name = "{agent_type}--{l3_client_id}"
    agent_name = f"{agent_type}--{l3_client_id}"
    existing = client.agents.list(name=agent_name)
    if existing:
        agent = existing[0]
        # Refresh persona from latest markdown
        client.agents.modify(
            agent_id=agent.id,
            system=persona_markdown,
        )
        return agent.id

    agent = client.agents.create(
        name=agent_name,
        system=persona_markdown,
        model="openai/gpt-4o",
        tool_ids=tool_ids,
        memory_blocks=[
            {"label": "active_client_context", "value": ""},
            {"label": "persona", "value": persona_markdown[:500]},
        ],
        tags=[f"l3:{l3_client_id}", f"type:{agent_type}"],
    )
    return agent.id
```

### Pattern 4: HITL Queue State Machine
**What:** Postgres-backed queue with finite state transitions and configurable timeout behavior
**When to use:** When orchestrator needs human approval or wants to surface information
**State machine:**
```
pending -> approved      (human action)
pending -> rejected      (human action)
pending -> timed_out     (periodic task checks TTL)
pending -> auto_resolved (auto-resolution at timeout, per trigger-type default)
```

### Pattern 5: Celery Task for Async Workflow Execution
**What:** Long-running workflow execution as a Celery task with checkpointing
**When to use:** Triggered by API call or scheduler
**Example:**
```python
# Celery task with extended time limit for workflow execution
@shared_task(
    bind=True,
    max_retries=0,
    time_limit=4 * 3600 + 300,  # 4hr + 5min buffer
    soft_time_limit=4 * 3600,    # 4hr soft limit triggers cleanup
)
def run_workflow(self, workflow_name, l2_agency_id, l3_client_id, triggered_by):
    ...
```

### Pattern 6: Webhook Delivery with Retry
**What:** Celery task for webhook POST with exponential backoff
**When to use:** When HITL item is created or resolved
**Example:**
```python
@shared_task(
    bind=True,
    autoretry_for=(requests.RequestException,),
    retry_backoff=True,        # exponential: 1s, 2s, 4s, 8s, 16s
    retry_backoff_max=300,     # cap at 5 minutes
    retry_jitter=True,         # prevent thundering herd
    max_retries=5,
)
def deliver_webhook(self, url, payload):
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
```

### Anti-Patterns to Avoid
- **Calling Letta SDK directly from orchestrator:** Always go through HaznMemory abstraction. The orchestrator creates/retrieves agents via letta_client for management only (list, create, modify, tools.attach/detach), but all memory operations go through HaznMemory.
- **Storing raw secrets in workflow_run records:** Metering data tracks cost and tokens, never credentials. get_credentials MCP tool is the only path for secret access.
- **Polling for workflow completion:** Use Celery result backend or webhooks, not polling loops.
- **Monolithic execute function:** Split into clear concerns: parser, executor, conflict detector, agent manager, session manager, metering.
- **Synchronous workflow execution:** Always run workflows as Celery tasks. Even Mode 1 (internal) should be async.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Topological sort | Custom dependency resolver | `graphlib.TopologicalSorter` | Handles cycles detection, parallel-ready batching, proven stdlib |
| Async task execution | Custom threading/multiprocessing | Celery tasks + asyncio.gather | Celery handles retries, result tracking, monitoring via Flower |
| YAML parsing | Custom tokenizer/parser | PyYAML `safe_load` + Pydantic `model_validate` | Type-safe, validated, handles edge cases |
| Webhook retry logic | Custom retry loops | Celery `autoretry_for` + `retry_backoff` | Built-in exponential backoff with jitter |
| Periodic timeout checks | Custom cron/scheduler | django-celery-beat periodic tasks | Already configured, database-backed scheduler |
| REST API serialization | Custom JSON serialization | DRF serializers | Already in project, handles validation and pagination |

**Key insight:** The orchestrator's complexity comes from coordinating existing components, not from building new primitives. Every building block (memory, credentials, task queues, REST) already exists in the codebase.

## Common Pitfalls

### Pitfall 1: Celery Task Time Limits
**What goes wrong:** Default CELERY_TASK_TIME_LIMIT is 5 minutes, CELERY_TASK_SOFT_TIME_LIMIT is 60 seconds in base settings. Workflow runs can take hours.
**Why it happens:** cookiecutter-django defaults are for short request-response tasks.
**How to avoid:** Override time limits per-task on run_workflow task (4hr + buffer). Keep webhook delivery tasks on default short limits.
**Warning signs:** SoftTimeLimitExceeded exceptions in logs during workflow execution.

### Pitfall 2: Agent Creation Race Conditions
**What goes wrong:** Two concurrent workflows for the same L3 client + agent type try to create the same agent simultaneously.
**Why it happens:** Check-then-create pattern without locking.
**How to avoid:** Use Django `select_for_update()` on a registry model or use the Letta agent name as a natural unique key and handle creation conflicts with try/except.
**Warning signs:** Duplicate agents with the same name in Letta.

### Pitfall 3: Partial Workflow State on Crash
**What goes wrong:** Orchestrator crashes mid-workflow, metering data lost, agent memory in inconsistent state.
**Why it happens:** Metering writes deferred to end-of-session.
**How to avoid:** Write metering data incrementally (per-phase completion, not just at workflow end). Use failure_sync() on any unclean exit. checkpoint_sync() every 10 turns is already built in.
**Warning signs:** workflow_runs stuck in "running" status with no recent updates.

### Pitfall 4: HITL Blocking Deadlocks
**What goes wrong:** Blocking HITL item with no human review, workflow hangs forever.
**Why it happens:** No timeout processing for HITL items.
**How to avoid:** django-celery-beat periodic task checks HITL item TTL every 5 minutes. Each trigger type has a configurable default action on timeout.
**Warning signs:** workflow_runs in "blocked" status for longer than configured timeout.

### Pitfall 5: Conflict Detection LLM Cost
**What goes wrong:** LLM check for L2/L3 conflicts costs too much per session start.
**Why it happens:** Using the primary expensive model for a classification task.
**How to avoid:** Use a lightweight/cheap model for conflict detection (e.g., gpt-4o-mini). The check is a simple classification: "does this L3 brand voice conflict with these L2 locked rules?"
**Warning signs:** High per-session baseline cost before any agent work begins.

### Pitfall 6: Tool Scoping Drift
**What goes wrong:** Agent accumulates tools from multiple workflows, violating principle of least privilege.
**Why it happens:** Tools attached during one workflow not detached before next.
**How to avoid:** At each session/phase start, reconcile the agent's attached tools with what the current workflow phase declares. Use agents.tools.list/attach/detach to set the exact tool set per phase.
**Warning signs:** Agents calling tools they shouldn't have access to.

### Pitfall 7: Workflow YAML Schema Drift
**What goes wrong:** YAML files have inconsistent schemas (some have `agent`, some don't; some have `depends_on`, some have `parallel_tracks`).
**Why it happens:** Organic evolution of workflow definitions before formal schema validation.
**How to avoid:** Pydantic WorkflowSchema model validates at load time. Non-conforming YAML fails fast with clear validation errors. Update existing YAML files to conform to schema.
**Warning signs:** KeyError or AttributeError during workflow parsing.

## Code Examples

### WorkflowRun Model Design
```python
# Source: CONTEXT.md decisions + Django model patterns
import uuid
from django.db import models

class WorkflowRun(models.Model):
    """Metering source of truth for a single workflow execution."""
    class Status(models.TextChoices):
        PENDING = "pending"
        RUNNING = "running"
        BLOCKED = "blocked"      # waiting on HITL
        COMPLETED = "completed"
        FAILED = "failed"
        TIMED_OUT = "timed_out"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_name = models.CharField(max_length=100)
    agency = models.ForeignKey("core.Agency", on_delete=models.CASCADE)
    end_client = models.ForeignKey("core.EndClient", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_tokens = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    wall_clock_seconds = models.IntegerField(default=0)
    turn_count = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True)
    ended_at = models.DateTimeField(null=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    error_details = models.JSONField(default=dict, blank=True)
    conflict_log = models.JSONField(default=list, blank=True)  # auto-resolved conflicts
    triggered_by = models.CharField(max_length=100)
    celery_task_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
```

### HITLItem Model Design
```python
class HITLItem(models.Model):
    """Human-in-the-loop queue item with configurable timeout behavior."""
    class TriggerType(models.TextChoices):
        CONFLICT = "conflict"           # L2/L3 conflict
        CHECKPOINT = "checkpoint"       # workflow checkpoint
        COST_ALERT = "cost_alert"       # runaway agent / cost outlier
        UNCERTAINTY = "uncertainty"     # agent uncertainty

    class Status(models.TextChoices):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"
        TIMED_OUT = "timed_out"
        AUTO_RESOLVED = "auto_resolved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_run = models.ForeignKey(WorkflowRun, on_delete=models.CASCADE, related_name="hitl_items")
    trigger_type = models.CharField(max_length=20, choices=TriggerType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    is_blocking = models.BooleanField(default=True)
    title = models.CharField(max_length=255)
    details = models.JSONField(default=dict)
    resolution = models.JSONField(default=dict, blank=True)
    timeout_hours = models.IntegerField(default=24)
    timeout_action = models.CharField(max_length=50, default="")  # per trigger type default
    resolved_by = models.CharField(max_length=255, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
```

### Conflict Detection Logic
```python
# Source: CONTEXT.md locked decisions
def detect_conflicts(agency, end_client) -> list[dict]:
    """Pre-flight L2/L3 conflict detection at session start.

    Compares L2 locked_rules against L3 brand_voice.
    Hard rules always override L3. Soft rules flag for review.
    """
    locked_rules = agency.house_style.get("locked_rules", [])
    if not locked_rules:
        return []

    brand_voice = BrandVoice.objects.filter(
        end_client=end_client, is_active=True
    ).first()
    if not brand_voice:
        return []

    # LLM-based comparison (use lightweight model)
    conflicts = run_conflict_check_llm(
        locked_rules=locked_rules,
        brand_voice_content=brand_voice.content,
    )

    results = []
    for conflict in conflicts:
        if conflict["severity"] == "hard":
            # Hard rule always overrides L3 -- auto-resolved
            results.append({
                "rule": conflict["rule"],
                "resolution": "l2_override",
                "auto_resolved": True,
                "severity": "hard",
            })
        else:
            # Soft rule -- L3 wins by default, logged as info
            results.append({
                "rule": conflict["rule"],
                "resolution": "l3_wins",
                "auto_resolved": True,
                "severity": "soft",
            })
    return results
```

### Agent Persona Refresh Pattern
```python
# Source: CONTEXT.md decisions + existing hazn/agents/ directory
from pathlib import Path

AGENTS_DIR = Path("hazn/agents")

def read_agent_persona(agent_type: str) -> str:
    """Read latest agent persona markdown from hazn/agents/{agent_type}.md"""
    persona_path = AGENTS_DIR / f"{agent_type}.md"
    if not persona_path.exists():
        raise ValueError(f"No persona found for agent type: {agent_type}")
    return persona_path.read_text()
```

### Metering Callback Hook
```python
# Source: CONTEXT.md decisions -- real-time cost tracking
class MeteringCallback:
    """Accumulates token usage and cost per-agent during workflow execution."""

    def __init__(self, workflow_run_id: uuid.UUID):
        self.workflow_run_id = workflow_run_id
        self._agent_meters: dict[str, dict] = {}  # agent_id -> {tokens, cost, turns}

    def on_llm_call(self, agent_id: str, tokens: int, cost: float):
        """Called after each LLM response."""
        if agent_id not in self._agent_meters:
            self._agent_meters[agent_id] = {"tokens": 0, "cost": 0.0, "turns": 0}
        self._agent_meters[agent_id]["tokens"] += tokens
        self._agent_meters[agent_id]["cost"] += cost
        self._agent_meters[agent_id]["turns"] += 1

        # Check runaway thresholds
        if self._agent_meters[agent_id]["turns"] >= self._max_turns:
            self._trigger_cost_alert(agent_id, "max_turns_exceeded")
        if self._agent_meters[agent_id]["cost"] >= self._max_cost:
            self._trigger_cost_alert(agent_id, "max_cost_exceeded")

    def flush_to_db(self, phase_id: str | None = None):
        """Write accumulated metering to WorkflowAgent records."""
        for agent_id, meters in self._agent_meters.items():
            WorkflowAgent.objects.update_or_create(
                workflow_run_id=self.workflow_run_id,
                agent_id=agent_id,
                defaults={
                    "total_tokens": meters["tokens"],
                    "total_cost": meters["cost"],
                    "turn_count": meters["turns"],
                    "phase_id": phase_id,
                },
            )
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Custom DAG implementations | Python stdlib graphlib (3.9+) | Python 3.9 (2020) | No external dependency for topo sort |
| Manual Celery retry logic | autoretry_for + retry_backoff | Celery 4+ (2017) | Declarative retry config |
| Letta root token auth | AppRole-based Vault auth | Phase 7 (2026-03-05) | Scoped read-only access for orchestrator |
| Stateless agent sessions | HaznMemory with checkpoint_sync | Phase 2 (2026-03-05) | Memory persists across sessions |
| letta client.create_agent | letta_client.agents.create | letta-client SDK | Type-safe, generated SDK |

**Deprecated/outdated:**
- Letta `client.create_agent()` replaced by `client.agents.create()` in the new generated SDK
- Letta `passages.search()` returns results with `.content` attribute (not `.text`)
- Letta block update: positional `block_label` first, then `agent_id` keyword arg

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 + pytest-django 4.12.0 |
| Config file | `hazn_platform/pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `cd hazn_platform && .venv/bin/pytest tests/test_orchestrator.py -x` |
| Full suite command | `cd hazn_platform && .venv/bin/pytest tests/ -x` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ORCH-01 | Load L2+L3 context at session start | unit | `pytest tests/test_orchestrator.py::TestSessionStart -x` | Wave 0 |
| ORCH-02 | Inject context via mcp-hazn-memory | integration | `pytest tests/test_orchestrator.py::TestContextInjection -x -m integration` | Wave 0 |
| ORCH-03 | Session lifecycle (start/checkpoint/end/timeout) | unit | `pytest tests/test_orchestrator.py::TestSessionLifecycle -x` | Wave 0 |
| ORCH-04 | Write workflow_runs metering data | unit | `pytest tests/test_orchestrator.py::TestMetering -x` | Wave 0 |
| ORCH-05 | HITL queue management | unit | `pytest tests/test_orchestrator.py::TestHITLQueue -x` | Wave 0 |
| ORCH-06 | Interpret workflow YAML for multi-agent execution | unit | `pytest tests/test_orchestrator.py::TestWorkflowParser -x` | Wave 0 |
| ORCH-07 | Tool scoping per agent type | unit | `pytest tests/test_orchestrator.py::TestToolScoping -x` | Wave 0 |
| CLT-01 | Three-layer client model | unit | `pytest tests/test_models.py::TestAgency tests/test_models.py::TestEndClient -x` | Exists |
| CLT-02 | L2 agency fields | unit | `pytest tests/test_models.py::TestAgency -x` | Exists |
| CLT-03 | L3 end-client data | unit | `pytest tests/test_models.py::TestEndClient -x` | Exists |
| CLT-04 | L3 brand voice wins by default | unit | `pytest tests/test_orchestrator.py::TestConflictDetection::test_l3_wins_default -x` | Wave 0 |
| CLT-05 | L2 locked rules override L3 | unit | `pytest tests/test_orchestrator.py::TestConflictDetection::test_hard_rule_overrides -x` | Wave 0 |
| CLT-06 | Conflicts flagged with 24hr timeout | unit | `pytest tests/test_orchestrator.py::TestConflictDetection::test_hitl_timeout -x` | Wave 0 |
| CRED-01 | Fetch secrets from Vault at runtime | integration | `pytest tests/test_vault.py -x -m integration` | Exists |
| CRED-02 | Secrets never in agent context | unit | `pytest tests/test_orchestrator.py::TestCredentialIsolation -x` | Wave 0 |
| CRED-03 | Credentials scoped per L2/L3 | unit | `pytest tests/test_models.py::TestVaultCredential -x` | Exists |
| CRED-04 | get_credentials MCP tool passes secrets to tools | unit | `pytest tests/test_mcp_memory_server.py -x` | Exists |

### Sampling Rate
- **Per task commit:** `cd hazn_platform && .venv/bin/pytest tests/test_orchestrator.py -x --tb=short`
- **Per wave merge:** `cd hazn_platform && .venv/bin/pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_orchestrator.py` -- covers ORCH-01 through ORCH-07, CLT-04/05/06, CRED-02
- [ ] `tests/test_workflow_parser.py` -- covers workflow YAML parsing and validation
- [ ] `hazn_platform/orchestrator/` Django app directory structure
- [ ] Add `"hazn_platform.orchestrator"` to LOCAL_APPS in base.py
- [ ] Migration for orchestrator models

## Open Questions

1. **Letta agents.modify full parameters**
   - What we know: `agents.modify(agent_id, model=..., system=...)` exists as a PATCH endpoint
   - What's unclear: Exact parameter list for modify -- can we update tool_ids via modify or must we use tools.attach/detach?
   - Recommendation: Use agents.tools.attach/detach for tool changes (confirmed API). Use agents.modify for system prompt refresh.

2. **Metering hook integration point**
   - What we know: CONTEXT.md says "callback/hook on LLM calls" for real-time cost tracking
   - What's unclear: How to intercept LLM calls made by Letta agents (Letta handles the LLM calls internally)
   - Recommendation: Use Langfuse traces (when Phase 4 adds Langfuse SDK) or poll Letta's message history after each agent step for usage stats. For Phase 3, track at the orchestrator level (per-phase tokens from Letta response metadata).

3. **Workflow YAML schema normalization**
   - What we know: Existing 7 YAML files have inconsistent schemas (some use `agent`, some don't; blog.yaml has `per_article`; audit.yaml has `parallel_tracks`)
   - What's unclear: Whether to normalize all 7 YAML files to a strict schema or support multiple schemas
   - Recommendation: Define a canonical schema and normalize the YAML files. Optional fields handle variations. `parallel_tracks` maps to phases with no inter-dependency.

4. **Agent persona refresh scope**
   - What we know: "Persona/system prompt refreshed from latest agent markdown at every session start"
   - What's unclear: Whether `agents.modify(system=...)` is sufficient or whether memory blocks also need updating
   - Recommendation: Use `agents.modify(system=new_persona)` for system prompt. The `persona` memory block in Letta is separate from the system prompt; update both if needed. Test with a single approach first.

## Sources

### Primary (HIGH confidence)
- Python stdlib graphlib docs -- TopologicalSorter API for DAG execution
- Letta Python SDK docs (docs.letta.com/api/python/) -- agents.create, agents.list, agents.modify, agents.tools.list/attach/detach
- Letta API Reference (docs.letta.com/api-reference/agents/create) -- full parameter list for agent creation
- Existing codebase: core/models.py, core/memory.py, core/vault.py, mcp_servers/hazn_memory_server.py, core/memory_types.py
- Existing workflow YAML files in hazn/workflows/
- Celery official docs (docs.celeryq.dev) -- autoretry_for, retry_backoff, canvas API

### Secondary (MEDIUM confidence)
- Langfuse docs (langfuse.com/docs) -- @observe decorator for LLM tracing (not yet integrated)
- Letta agents.modify method -- confirmed to exist via search but full parameter list not verified

### Tertiary (LOW confidence)
- Letta agent message response metadata for token usage -- need to verify if Letta returns usage stats per message/step

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all libraries already in project or Python stdlib
- Architecture: HIGH - patterns derived from existing codebase patterns + stdlib docs
- Pitfalls: HIGH - derived from actual codebase inspection (Celery time limits, YAML schema inconsistency)
- Letta agent management: MEDIUM - SDK docs verified but agents.modify parameter list not fully confirmed
- Metering hook: MEDIUM - integration point with Letta's internal LLM calls needs runtime verification

**Research date:** 2026-03-05
**Valid until:** 2026-04-05 (stable -- stdlib + Django + Celery patterns; Letta SDK may evolve)

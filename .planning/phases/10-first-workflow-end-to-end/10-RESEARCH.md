# Phase 10: First Workflow End-to-End - Research

**Researched:** 2026-03-06
**Domain:** Workflow execution pipeline, Jinja2 report rendering, SSE real-time status, deliverable storage
**Confidence:** HIGH

## Summary

Phase 10 wires the full execution chain from the workspace UI to a stored deliverable. The codebase already has most pieces built: WorkflowExecutor with DAG-based execution (executor.py), AgentRunner with dual-backend support (agent_runner.py), WorkflowTriggerView that dispatches Celery tasks (workspace/views.py), frontend components for workflow cards, phase steppers, chat timeline, and cost tracking (all in frontend/src/components/workflow/), SSE infrastructure via django-eventstream with send_workspace_event helper (workspace/sse_views.py), and the useSSE hook on the frontend (hooks/use-sse.ts). The Deliverable model exists but lacks html_content and markdown_source fields. The workflow catalog API endpoint (/workspace/workflows/catalog/) is called by the frontend but has no Django view yet.

The core work for this phase is: (1) build the workflow catalog endpoint that scans YAML files and returns workflow metadata, (2) add html_content and markdown_source TextFields to the Deliverable model, (3) create a Jinja2 rendering pipeline that takes structured JSON from the delivery-phase agent and produces branded HTML, (4) wire SSE events into the executor so phase transitions publish to Redis channels, (5) wire the data collection Python scripts as MCP tools, and (6) connect all the pieces for the SEO audit workflow's 5 phases to execute end-to-end with real agents and real data.

**Primary recommendation:** Build in three waves -- (1) catalog API + Deliverable migration + Jinja2 rendering pipeline, (2) SSE event emission from executor + data collection MCP tool wiring, (3) full E2E integration with the analytics-audit workflow on real client data.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Jinja2 pipeline: agent produces structured JSON payload (sections, findings, scores), Django renders via Jinja2 template
- Agent outputs JSON with named sections: executive_summary, findings[], recommendations[], scores -- clean contract between agent and template
- Autonomous branding hardcoded in template (logo, colors, footer) -- Mode 1 internal use only, white-label deferred
- Add html_content TextField and markdown_source TextField to Deliverable model via migration
- Rendered HTML served directly via Django view from DB field
- SSE from Django endpoint, not polling or WebSocket
- Redis pub/sub as the event transport -- executor publishes to Redis channel, SSE endpoint subscribes and streams to browser
- Phase-level event granularity: phase_started, phase_completed, phase_failed, workflow_completed, workflow_failed
- WorkflowChat component shows phase completion summaries in timeline view -- no streaming agent text
- Wire real Python data collection scripts (ga4_collector.py, gsc_collector.py, pagespeed_collector.py) as MCP tools
- Use real Autonomous client GA4/GSC credentials (via Vault) for the first E2E run
- Full end-to-end with actual data, not mock/fixture data
- Failed phases show as inline red error messages in WorkflowChat timeline
- Completed phases still display their summaries even when workflow fails
- Full re-run only via existing Clone & Re-run button -- no resume from failure point
- Partial results (budget exceeded) visible in workflow run detail only, NOT promoted to Deliverables section
- Technical error messages for Mode 1: actual error text, token counts, cost at halt

### Claude's Discretion
- Workflow catalog implementation mechanism (YAML scanning, DB table, or hybrid)
- SSE endpoint implementation details (streaming response, Redis subscription management)
- Jinja2 template design and structure for SEO audit report
- How to wire Python data collection scripts as MCP tools
- WorkflowChat message format and timeline rendering
- Migration strategy for new Deliverable fields

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| WKFL-01 | User can trigger workflow from workspace UI with client ID and parameters | WorkflowTriggerView exists, calls run_workflow.delay(); needs catalog endpoint so frontend knows which workflows exist |
| WKFL-02 | Workflow executes all DAG phases with real agent execution at each phase | WorkflowExecutor.run() handles DAG waves via TopologicalSorter; AgentRunner with AnthropicAPIBackend executes real LLM calls; analytics-audit.yaml defines 5 phases |
| WKFL-05 | Workflow status visible in workspace UI (running, paused, complete, failed) | SSE infrastructure exists (django-eventstream, send_workspace_event, useSSE hook); executor needs to emit phase-level events during execution |
| DLVR-01 | Agents produce structured markdown as workflow output | OutputCollector already parses markdown into CollectedArtifact types; delivery agent needs to produce structured JSON instead of markdown for Jinja2 |
| DLVR-02 | Pipeline converts markdown to branded HTML report via Jinja2 templates | New: Jinja2 template + rendering service that takes structured JSON and produces HTML; stored in Deliverable.html_content |
| DLVR-03 | Deliverable stored and accessible in workspace Deliverables section | DeliverableViewSet exists with approve/reject/share; needs html_content/markdown_source fields on model + detail view for HTML |
| DLVR-04 | Deliverable linked to workflow run with full provenance | Deliverable already has workflow_run FK and phase_output OneToOneField; WorkflowRunDetailSerializer includes agents, tool_calls, phase_outputs |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Jinja2 | 3.1.x | HTML report rendering from structured JSON | Already in hazn_platform venv (Jinja2 is a Django dependency); standalone use without Django template engine for report generation |
| django-eventstream | (installed) | SSE streaming to browser clients | Already in INSTALLED_APPS and urls.py; send_event() function available |
| Redis | (in Docker stack) | Pub/sub transport for SSE events | Already used as Celery broker; django-eventstream supports Redis as channel layer |
| Celery | (installed) | Async workflow execution | run_workflow task already exists and works |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| PyYAML | (installed) | Workflow YAML loading | Already used by workflow_parser.py |
| Pydantic | (installed) | Structured data validation for workflow schemas and agent outputs | Already used for WorkflowSchema, CollectedArtifact |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Jinja2 standalone | Django template engine | Django templates are less powerful (no macros, limited logic); Jinja2 is already installed and matches the user decision |
| django-eventstream | Django StreamingHttpResponse + manual SSE | django-eventstream handles reconnection, persistence, channel management; already configured |
| DB-stored HTML | File-based HTML | DB storage (TextField) is simpler, already decided by user, no file management overhead |

## Architecture Patterns

### Recommended Project Structure
```
hazn_platform/
  hazn_platform/
    orchestrator/
      executor.py            # ADD: SSE event emission on phase transitions
      tasks.py               # ADD: SSE events on workflow start/end
    workspace/
      views.py               # ADD: WorkflowCatalogView, DeliverableHTMLView
      serializers.py          # ADD: DeliverableSerializer html_content/markdown_source fields
      sse_views.py            # EXISTS: send_workspace_event() -- no changes needed
      urls.py                 # ADD: catalog/ and deliverable HTML view routes
    qa/
      models.py               # MODIFY: add html_content, markdown_source TextFields
      migrations/0002_*.py    # NEW: migration for new fields
    deliverable_pipeline/     # NEW: Jinja2 rendering pipeline
      __init__.py
      renderer.py             # Jinja2 template loading + rendering
      templates/
        analytics-audit.html  # Branded report template
  hazn/
    workflows/*.yaml          # Source of truth for workflow catalog
    scripts/analytics-audit/  # Python data collectors to wire as MCP tools
```

### Pattern 1: Workflow Catalog via YAML Scanning
**What:** A Django view that scans the hazn/workflows/ directory, loads each YAML file, and returns structured metadata (name, description, phases, estimated_duration).
**When to use:** On every GET /workspace/workflows/catalog/ request.
**Example:**
```python
# Source: Existing workflow_parser.py + new catalog view
from pathlib import Path
from hazn_platform.orchestrator.workflow_parser import load_workflow

class WorkflowCatalogView(APIView):
    permission_classes = [IsAgencyMember]

    def get(self, request):
        workflows_dir = Path("hazn/workflows")
        catalog = []
        for yaml_path in sorted(workflows_dir.glob("*.yaml")):
            try:
                schema = load_workflow(yaml_path)
                catalog.append({
                    "name": schema.name,
                    "description": schema.description,
                    "phases": [{"id": p.id, "name": p.name} for p in schema.phases],
                    "estimated_duration": schema.estimated_duration,
                    "parameters": [],  # Future: extract from workflow config
                    "estimated_cost": None,
                })
            except Exception:
                logger.warning("Skipping invalid workflow: %s", yaml_path)
        return Response(catalog)
```

### Pattern 2: Jinja2 Rendering Pipeline (Standalone)
**What:** Use Jinja2 directly (not through Django's template backend) to render structured JSON into branded HTML. The Jinja2 Environment loads templates from a dedicated directory.
**When to use:** After the delivery phase agent produces structured JSON output.
**Example:**
```python
# Source: Jinja2 docs (https://jinja.palletsprojects.com/en/stable/)
import jinja2
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent / "templates"

_jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=jinja2.select_autoescape(["html"]),
)

def render_report(template_name: str, context: dict) -> str:
    """Render a branded HTML report from structured JSON context.

    Parameters
    ----------
    template_name:
        Template filename (e.g., "analytics-audit.html").
    context:
        Structured JSON from the delivery agent, containing:
        - executive_summary: str
        - findings: list[dict]
        - recommendations: list[dict]
        - scores: dict

    Returns
    -------
    str
        Complete HTML string ready for storage in Deliverable.html_content.
    """
    template = _jinja_env.get_template(template_name)
    return template.render(**context)
```

### Pattern 3: SSE Event Emission from Executor
**What:** The executor publishes phase-level events to Redis via send_workspace_event() during workflow execution. The SSE endpoint streams these to the browser.
**When to use:** At each phase transition in WorkflowExecutor._execute_phase().
**Example:**
```python
# In executor.py, within _execute_phase():
from hazn_platform.workspace.sse_views import send_workspace_event

# Before phase execution
await sync_to_async(send_workspace_event)(
    agency_id=str(workflow_run.agency_id),
    event_type="workflow_status",
    data={
        "run_id": str(workflow_run.pk),
        "phase_id": phase.id,
        "phase_name": phase.name,
        "status": "running",
        "event": "phase_started",
    },
)

# After phase completion
await sync_to_async(send_workspace_event)(
    agency_id=str(workflow_run.agency_id),
    event_type="workflow_status",
    data={
        "run_id": str(workflow_run.pk),
        "phase_id": phase.id,
        "phase_name": phase.name,
        "status": "completed",
        "event": "phase_completed",
        "summary": summary_text,
    },
)
```

### Pattern 4: Data Collection Scripts as MCP Tools
**What:** Register the Python data collection scripts (ga4_collector.py, gsc_collector.py, pagespeed_collector.py) as tools in the ToolRouter static registry so agents can call them during execution.
**When to use:** The analytics-inspector agent's data-collection phase needs these tools.
**Example:**
```python
# In tool_router.py or a new module:
# Register as tools with the naming convention matching MCP tools
# Tool names: collect_ga4_data, collect_gsc_data, collect_pagespeed_data
# Each wraps the existing Python script's main function with proper input/output handling
```

### Anti-Patterns to Avoid
- **Agent generating HTML directly:** The delivery agent should produce structured JSON, NOT raw HTML. The Jinja2 template handles all presentation concerns. This decouples content from branding.
- **Polling for workflow status:** Use SSE (already configured), not polling. The frontend already has SSE fallback polling at 5s in WorkflowChat.
- **Storing HTML as file:** Store in Deliverable.html_content TextField per user decision. No file management complexity.
- **Building a complex catalog service:** The 7 YAML files are static. A simple filesystem scan is sufficient. No database table needed for Mode 1.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTML report rendering | Custom string concatenation | Jinja2 template engine | Jinja2 handles escaping, loops, conditionals, macros; battle-tested |
| SSE server-to-browser push | Custom StreamingHttpResponse | django-eventstream send_event() | Already installed, handles reconnection, persistence, channel management |
| YAML workflow loading | Custom YAML parser | workflow_parser.load_workflow() | Already validates against WorkflowSchema Pydantic model |
| Topological sort for DAG | Custom dependency resolution | graphlib.TopologicalSorter | Already used in workflow_parser.get_execution_order() |
| Tool dispatch | Custom subprocess/exec | ToolRouter + tool_wiring | Already handles sync/async, error capture, metering |

**Key insight:** Almost every component for this phase already exists in isolation. The work is integration and wiring, not building from scratch. The biggest risk is interface mismatches between components that have never been tested together.

## Common Pitfalls

### Pitfall 1: Agent Output Format Mismatch
**What goes wrong:** The delivery agent produces free-form markdown instead of structured JSON, making Jinja2 template rendering impossible.
**Why it happens:** The agent prompt doesn't explicitly instruct JSON output with the exact field names the template expects.
**How to avoid:** The delivery agent's system prompt must specify the exact JSON schema: `{executive_summary: str, findings: [{severity, description, evidence, recommendation}], recommendations: [{priority, action, impact}], scores: {overall, technical, content, ux}}`. Use PromptAssembler to inject this contract.
**Warning signs:** Jinja2 template rendering produces empty sections or throws UndefinedError.

### Pitfall 2: Async/Sync Boundary in SSE Emission
**What goes wrong:** Calling send_workspace_event() from async executor code without sync_to_async causes Django ORM warnings or silent failures.
**Why it happens:** send_workspace_event calls django_eventstream.send_event which may touch the database for persistence. The executor runs in async context.
**How to avoid:** Always wrap with sync_to_async: `await sync_to_async(send_workspace_event)(...)`. This pattern is already used throughout executor.py for ORM calls.
**Warning signs:** "SynchronousOnlyOperation" exceptions in Celery logs.

### Pitfall 3: Workflow YAML Path Resolution
**What goes wrong:** load_workflow() fails with FileNotFoundError because the relative path "hazn/workflows/analytics-audit.yaml" resolves differently in Celery worker vs Django server.
**Why it happens:** Celery workers may have a different working directory. The current code in tasks.py uses `load_workflow(f"hazn/workflows/{workflow_name}.yaml")` with a relative path.
**How to avoid:** Use an absolute path based on a project setting or compute from BASE_DIR. Check: `Path(settings.BASE_DIR).parent / "hazn" / "workflows" / f"{workflow_name}.yaml"`.
**Warning signs:** FileNotFoundError in Celery worker logs but works fine in Django shell.

### Pitfall 4: Celery Worker Event Loop Conflicts
**What goes wrong:** The run_workflow task creates `asyncio.new_event_loop()` for the executor, but if the Celery worker already has an event loop (e.g., from gevent/eventlet), this conflicts.
**Why it happens:** The task creates a fresh event loop per execution. If the Celery pool uses async-aware threads, nested loops cause errors.
**How to avoid:** The current pattern (new_event_loop + try/finally close) is correct for the default prefork pool. Verify Celery is using prefork, not gevent/eventlet.
**Warning signs:** "RuntimeError: This event loop is already running" in Celery worker.

### Pitfall 5: SSE Channel Mismatch Between Backend and Frontend
**What goes wrong:** Events are sent to channel `agency-{uuid}` but the frontend subscribes to `workflow-{runId}` or `workflows`.
**Why it happens:** The SSE channel naming convention differs between backend (agency-scoped) and frontend (feature-scoped).
**How to avoid:** Verify the django-eventstream URL configuration passes channels correctly. The frontend createSSEConnection builds URL as `/api/events/?channel=...`. The backend send_workspace_event uses `agency-{agency_id}`. The useSSE hook in WorkflowChat subscribes to `workflow-{runId}` -- this channel name needs to be supported or the frontend needs to subscribe to the agency channel instead.
**Warning signs:** SSE events sent but never received by frontend. Browser EventSource connected but no messages arrive.

### Pitfall 6: Data Collection Scripts Need Credentials
**What goes wrong:** The ga4_collector.py and gsc_collector.py scripts need OAuth2 credentials that are stored in Vault, not available as environment variables to the agent.
**Why it happens:** The scripts expect credentials at ~/.config/ga4-audit/credentials.json. In the platform, credentials are in Vault.
**How to avoid:** The MCP tool wrapper for these scripts should fetch credentials from Vault via the get_credentials MCP tool, write them to a temporary file, and pass the path to the script. Clean up after execution.
**Warning signs:** OAuth2 authentication errors when the data collection phase runs.

## Code Examples

### Deliverable Model Migration
```python
# Source: Existing Deliverable model in qa/models.py
# Migration: qa/migrations/0002_deliverable_html_content_markdown_source.py

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("qa", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="deliverable",
            name="html_content",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="deliverable",
            name="markdown_source",
            field=models.TextField(blank=True, default=""),
        ),
    ]
```

### Jinja2 Template Structure (analytics-audit.html)
```html
{# Source: New template -- Autonomous branding hardcoded #}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{{ client_name }} - Analytics Audit Report</title>
  <style>
    /* Autonomous brand colors, typography, layout */
    :root { --brand-primary: #...; --brand-accent: #...; }
    body { font-family: 'Inter', sans-serif; max-width: 900px; margin: 0 auto; }
    .finding { border-left: 3px solid var(--severity-color); padding: 1rem; margin: 1rem 0; }
    .score-card { display: flex; gap: 1rem; }
    .score-item { text-align: center; padding: 1rem; border-radius: 8px; }
  </style>
</head>
<body>
  <header>
    <img src="data:image/..." alt="Autonomous logo" />  {# inline base64 logo #}
    <h1>Analytics Audit Report</h1>
    <p class="subtitle">{{ client_name }} | {{ report_date }}</p>
  </header>

  <section id="executive-summary">
    <h2>Executive Summary</h2>
    <p>{{ executive_summary }}</p>
  </section>

  <section id="scores">
    <h2>Overall Scores</h2>
    <div class="score-card">
      {% for key, value in scores.items() %}
      <div class="score-item">
        <div class="score-value">{{ value }}</div>
        <div class="score-label">{{ key | replace('_', ' ') | title }}</div>
      </div>
      {% endfor %}
    </div>
  </section>

  <section id="findings">
    <h2>Key Findings</h2>
    {% for finding in findings %}
    <div class="finding severity-{{ finding.severity | lower }}">
      <h3>{{ finding.description }}</h3>
      <p><strong>Severity:</strong> {{ finding.severity }}</p>
      <p><strong>Evidence:</strong> {{ finding.evidence }}</p>
      <p><strong>Recommendation:</strong> {{ finding.recommendation }}</p>
    </div>
    {% endfor %}
  </section>

  <section id="recommendations">
    <h2>Recommendations</h2>
    {% for rec in recommendations %}
    <div class="recommendation">
      <h3>{{ rec.action }}</h3>
      <p><strong>Priority:</strong> {{ rec.priority }}</p>
      <p><strong>Expected Impact:</strong> {{ rec.impact }}</p>
    </div>
    {% endfor %}
  </section>

  <footer>
    <p>Generated by Autonomous | {{ report_date }}</p>
  </footer>
</body>
</html>
```

### Workflow Catalog Endpoint
```python
# Source: New view added to workspace/views.py
class WorkflowCatalogView(APIView):
    permission_classes = [IsAgencyMember]

    def get(self, request):
        from pathlib import Path
        from hazn_platform.orchestrator.workflow_parser import load_workflow

        # Use absolute path resolution
        workflows_dir = Path(settings.BASE_DIR).parent / "hazn" / "workflows"
        catalog = []

        for yaml_path in sorted(workflows_dir.glob("*.yaml")):
            try:
                schema = load_workflow(yaml_path)
                catalog.append({
                    "name": schema.name,
                    "description": schema.description,
                    "phases": [
                        {"id": p.id, "name": p.name, "agent": p.agent}
                        for p in schema.phases
                    ],
                    "estimated_duration": schema.estimated_duration,
                    "parameters": [],
                    "estimated_cost": None,
                })
            except Exception:
                logger.warning("Skipping invalid workflow: %s", yaml_path.name)

        return Response(catalog)
```

### SSE Event Emission in Executor
```python
# Source: Addition to executor.py _execute_phase method
# Import at top:
from hazn_platform.workspace.sse_views import send_workspace_event

# Before executing phase:
await sync_to_async(send_workspace_event)(
    agency_id=str(workflow_run.agency_id),
    event_type="workflow_status",
    data={
        "run_id": str(workflow_run.pk),
        "phase_id": phase.id,
        "phase_name": phase.name,
        "event": "phase_started",
        "status": "running",
    },
)

# After phase completes successfully:
await sync_to_async(send_workspace_event)(
    agency_id=str(workflow_run.agency_id),
    event_type="workflow_status",
    data={
        "run_id": str(workflow_run.pk),
        "phase_id": phase.id,
        "phase_name": phase.name,
        "event": "phase_completed",
        "status": "completed",
        "summary": summary_text,
    },
)

# On phase failure:
await sync_to_async(send_workspace_event)(
    agency_id=str(workflow_run.agency_id),
    event_type="workflow_status",
    data={
        "run_id": str(workflow_run.pk),
        "phase_id": phase.id,
        "phase_name": phase.name,
        "event": "phase_failed",
        "status": "failed",
        "error": str(result)[:500],
    },
)
```

### Data Collection Script MCP Tool Wrapper
```python
# Source: New tool registration in tool_router.py or dedicated module
import subprocess
import json
import tempfile
from pathlib import Path

def collect_ga4_data(
    property_id: str,
    site_url: str,
    output_dir: str = "/tmp/hazn-audit",
) -> dict:
    """Run ga4_collector.py and return the collected data as JSON.

    The GA4 collector script is in hazn/scripts/analytics-audit/.
    Credentials must be pre-fetched from Vault and written to temp file.
    """
    script_path = Path("hazn/scripts/analytics-audit/ga4_collector.py")
    os.makedirs(output_dir, exist_ok=True)

    result = subprocess.run(
        ["python", str(script_path), property_id, site_url, output_dir],
        capture_output=True,
        text=True,
        timeout=300,  # 5-minute timeout
    )

    if result.returncode != 0:
        return {"error": result.stderr[:500], "success": False}

    # Read the output JSON file
    output_file = Path(output_dir) / f"{site_url.replace('/', '_')}-ga4.json"
    if output_file.exists():
        return json.loads(output_file.read_text())

    return {"output": result.stdout, "success": True}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Django template engine for everything | Jinja2 standalone for report rendering | Project decision | More powerful templating (macros, filters), cleaner separation |
| WebSocket for real-time | SSE via django-eventstream | Project decision | Simpler server, browser reconnection built-in, sufficient for one-way push |
| Polling for workflow status | SSE + polling fallback | v1.0 implementation | Real-time updates without polling overhead |
| Markdown-to-HTML conversion | Structured JSON to Jinja2 HTML | Phase 10 decision | Clean contract between agent output and template, easier to change branding |

**Deprecated/outdated:**
- None -- all technologies used are current and well-maintained.

## Open Questions

1. **Workflow YAML path resolution in Celery workers**
   - What we know: tasks.py uses relative path `hazn/workflows/{name}.yaml`
   - What's unclear: Whether the Celery worker's working directory is the project root
   - Recommendation: Use absolute path via `settings.BASE_DIR.parent / "hazn" / "workflows"` and verify in Celery worker

2. **SSE channel naming alignment**
   - What we know: Backend uses `agency-{uuid}` channels; frontend useSSE in WorkflowChat subscribes to `workflow-{runId}`
   - What's unclear: Whether django-eventstream supports dynamic channel subscription or if the frontend needs to change its channel name
   - Recommendation: The frontend should subscribe to the agency channel (which it gets from auth context), and filter events client-side by run_id. The useSSE hook already handles this pattern via TanStack Query invalidation keyed by run_id.

3. **Data collection script credential flow**
   - What we know: Scripts expect OAuth2 creds at ~/.config/ga4-audit/credentials.json; platform stores creds in Vault
   - What's unclear: Whether the scripts can accept a custom credential path parameter
   - Recommendation: Inspect ga4_collector.py to determine if credential path is configurable. If not, wrap the script to write Vault-fetched creds to a temp file and set the environment variable.

4. **Agent JSON output reliability**
   - What we know: The delivery agent (analytics-client-reporter) needs to produce structured JSON, not free-form markdown
   - What's unclear: How reliably Claude produces valid JSON when instructed
   - Recommendation: Include explicit JSON schema in the agent's system prompt, validate output with Pydantic before template rendering, and fall back to raw text display if validation fails.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (Django) |
| Config file | hazn_platform/config/settings/test.py |
| Quick run command | `cd hazn_platform && python -m pytest tests/test_workspace_workflows.py -x` |
| Full suite command | `cd hazn_platform && python -m pytest tests/ -x --timeout=30` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| WKFL-01 | Workflow catalog API returns available workflows | unit | `pytest tests/test_workflow_catalog.py -x` | Wave 0 |
| WKFL-01 | Trigger workflow creates Celery task | unit | `pytest tests/test_workspace_workflows.py -x` | Exists |
| WKFL-02 | Executor runs all phases in topological order | unit | `pytest tests/test_executor.py -x` | Exists |
| WKFL-05 | SSE events emitted on phase transitions | unit | `pytest tests/test_sse_events.py -x` | Wave 0 |
| DLVR-01 | Agent structured JSON output validated by Pydantic | unit | `pytest tests/test_deliverable_pipeline.py::test_json_validation -x` | Wave 0 |
| DLVR-02 | Jinja2 renders HTML from structured JSON | unit | `pytest tests/test_deliverable_pipeline.py::test_render_report -x` | Wave 0 |
| DLVR-03 | Deliverable with html_content stored and served | unit | `pytest tests/test_workspace_deliverables.py -x` | Exists |
| DLVR-04 | Deliverable linked to workflow run with provenance | unit | `pytest tests/test_workspace_deliverables.py -x` | Exists |

### Sampling Rate
- **Per task commit:** `cd hazn_platform && python -m pytest tests/test_deliverable_pipeline.py tests/test_workflow_catalog.py tests/test_sse_events.py -x --timeout=30`
- **Per wave merge:** `cd hazn_platform && python -m pytest tests/ -x --timeout=60`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_workflow_catalog.py` -- covers WKFL-01 catalog endpoint
- [ ] `tests/test_sse_events.py` -- covers WKFL-05 SSE emission from executor
- [ ] `tests/test_deliverable_pipeline.py` -- covers DLVR-01, DLVR-02 Jinja2 rendering
- [ ] Deliverable model migration (qa/migrations/0002_*) -- prerequisite for DLVR-03

*(Existing test files cover: test_executor.py, test_workspace_workflows.py, test_workspace_deliverables.py)*

## Sources

### Primary (HIGH confidence)
- Codebase: executor.py, tasks.py, workspace/views.py, workspace/serializers.py, workspace/sse_views.py, qa/models.py -- direct source code analysis
- Codebase: frontend/src/components/workflow/*.tsx, hooks/use-sse.ts, lib/sse.ts, types/api.ts -- direct source code analysis
- Codebase: hazn/workflows/analytics-audit.yaml -- workflow definition
- Codebase: orchestrator/workflow_parser.py, workflow_models.py -- YAML loading infrastructure
- Codebase: orchestrator/agent_runner.py, output_collector.py -- execution and artifact capture

### Secondary (MEDIUM confidence)
- [Django Templates documentation](https://docs.djangoproject.com/en/5.2/topics/templates/) -- Django Jinja2 backend support
- [Jinja2 documentation](https://jinja.palletsprojects.com/en/stable/) -- standalone Jinja2 usage patterns
- [django-eventstream GitHub](https://github.com/fanout/django-eventstream) -- SSE channel management and Redis support
- [django-eventstream PyPI](https://pypi.org/project/django-eventstream/) -- send_event() API reference

### Tertiary (LOW confidence)
- Agent JSON output reliability -- based on general Claude experience, needs validation with actual analytics-client-reporter agent

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all libraries already installed and configured in the project
- Architecture: HIGH - patterns derived from existing codebase conventions and working code
- Pitfalls: HIGH - identified from direct code analysis of interface boundaries
- Data collection MCP tools: MEDIUM - wrapping Python scripts as MCP tools is straightforward but credential flow needs verification

**Research date:** 2026-03-06
**Valid until:** 2026-04-06 (stable -- no external API changes expected)

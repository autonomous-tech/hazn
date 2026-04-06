# Phase 10: First Workflow End-to-End - Context

**Gathered:** 2026-03-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Wire the full execution chain so a user triggers the SEO audit workflow from the workspace UI and receives a branded HTML report as a stored deliverable. This proves the complete chain works: Workspace UI -> Django -> Celery -> WorkflowExecutor -> AgentRunner -> MCP tools -> OutputCollector -> Jinja2 rendering -> Deliverable storage -> Workspace display.

Requirements: WKFL-01 (trigger from UI), WKFL-02 (DAG execution with real agents), WKFL-05 (real-time status), DLVR-01 (structured markdown output), DLVR-02 (markdown to branded HTML), DLVR-03 (deliverable in workspace), DLVR-04 (provenance linking)

</domain>

<decisions>
## Implementation Decisions

### Report Rendering Pipeline
- Jinja2 pipeline: agent produces structured JSON payload (sections, findings, scores), Django renders via Jinja2 template
- Agent outputs JSON with named sections: executive_summary, findings[], recommendations[], scores -- clean contract between agent and template
- Autonomous branding hardcoded in template (logo, colors, footer) -- Mode 1 internal use only, white-label deferred
- Add `html_content` TextField and `markdown_source` TextField to Deliverable model via migration
- Rendered HTML served directly via Django view from DB field

### Real-time Workflow Status
- SSE from Django endpoint, not polling or WebSocket
- Redis pub/sub as the event transport -- executor publishes to Redis channel, SSE endpoint subscribes and streams to browser
- Phase-level event granularity: phase_started, phase_completed, phase_failed, workflow_completed, workflow_failed
- WorkflowChat component shows phase completion summaries in timeline view -- no streaming agent text
- useSSE hook already exists in frontend and expects this pattern

### Workflow Catalog
- Claude's discretion on catalog mechanism (scan YAML vs DB table vs hybrid)
- Source of truth: the 7 existing workflow YAML files in the hazn package (analytics-audit, landing, website, blog, ngo-website, analytics-teaser, audit)
- Use everything from the hazn package and migrate to preferred mechanism

### Data Collection (SEO Audit)
- Wire real Python data collection scripts (ga4_collector.py, gsc_collector.py, pagespeed_collector.py) as MCP tools
- Use real Autonomous client GA4/GSC credentials (via Vault) for the first E2E run
- Full end-to-end with actual data, not mock/fixture data

### Failure Handling UX
- Failed phases show as inline red error messages in WorkflowChat timeline -- user sees exactly where it broke
- Completed phases still display their summaries even when workflow fails
- Full re-run only via existing Clone & Re-run button -- no resume from failure point
- Partial results (budget exceeded) visible in workflow run detail only, NOT promoted to Deliverables section
- Technical error messages for Mode 1: actual error text, token counts, cost at halt -- useful for internal debugging

### Claude's Discretion
- Workflow catalog implementation mechanism (YAML scanning, DB table, or hybrid)
- SSE endpoint implementation details (streaming response, Redis subscription management)
- Jinja2 template design and structure for SEO audit report
- How to wire Python data collection scripts as MCP tools
- WorkflowChat message format and timeline rendering
- Migration strategy for new Deliverable fields

</decisions>

<specifics>
## Specific Ideas

- The analytics-audit.yaml defines 5 phases: setup, data-collection (parallel tracks), analysis, review, delivery -- all need to execute with real agents
- The data-collection phase has parallel_tracks: [ga4_data, gsc_data, site_inspection] which maps to the existing Python scripts
- The delivery phase agent (analytics-client-reporter) should produce structured JSON that the Jinja2 template renders, NOT generate HTML directly
- Frontend already has WorkflowCard with trigger dialog, PhaseStepper, WorkflowChat, CostTracker, DeliverableCard -- all built in v1.0
- Backend already has WorkflowTriggerView, WorkflowRunViewSet, DeliverableViewSet with approve/reject/share -- all built in v1.0
- Frontend calls `/workspace/workflows/catalog/` but no Django view exists yet -- needs to be created

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `WorkflowExecutor`: Full DAG executor with wave-based parallel execution, HITL checkpoints, QA injection (executor.py)
- `AgentRunner`: Multi-turn tool_use loop with budget enforcement (agent_runner.py)
- `PromptAssembler`: System prompt construction from agent/skill/workflow definitions (prompt_assembler.py)
- `ToolRouter`: Static registry with dual-format dispatch, callables wired at startup (tool_router.py)
- `OutputCollector`: Convention-based markdown parsing with 4 artifact types (output_collector.py)
- `WorkflowTriggerView`: Dispatches run_workflow Celery task with agency scoping (views.py)
- `WorkflowRunViewSet`: Read-only listing with filters, list/detail serializers (views.py)
- `DeliverableViewSet`: Approve/reject/share actions with agency scoping (views.py)
- `WorkflowCard` component: Trigger dialog with client selector and workflow params (workflow-card.tsx)
- `PhaseStepper` component: Visual phase progress indicator (phase-stepper.tsx)
- `WorkflowChat` component: Timeline view for workflow events (workflow-chat.tsx)
- `CostTracker` component: Running cost display (cost-tracker.tsx)
- `DeliverableCard` component: QA badge, approval status, click to detail (deliverable-card.tsx)
- `useSSE` hook: SSE subscription with TanStack Query invalidation (use-sse.ts)
- Redis: Already in Docker Compose stack, available for pub/sub
- Python data collection scripts: ga4_collector.py, gsc_collector.py, pagespeed_collector.py in hazn/scripts/analytics-audit/
- 4 FastMCP servers: hazn-memory (7 tools), analytics, github, vercel

### Established Patterns
- Django DRF viewsets with agency-scoped queryset filtering via IsAgencyMember permission
- Celery async tasks for workflow execution (run_workflow task)
- async execution with sync_to_async wrapping for Django ORM calls
- TanStack Query with SSE invalidation on frontend
- Redis already used in the stack (Celery broker)

### Integration Points
- Workflow catalog API: New endpoint at /workspace/workflows/catalog/ consumed by frontend
- SSE endpoint: New Django streaming view publishing Redis pub/sub events to browser
- Executor -> Redis: Publish phase-level events during execution for SSE consumption
- Jinja2 rendering: New pipeline between OutputCollector artifacts and Deliverable html_content field
- Deliverable model migration: Add html_content and markdown_source TextFields
- MCP tool wiring: Data collection Python scripts need to be registered as MCP tools

</code_context>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 10-first-workflow-end-to-end*
*Context gathered: 2026-03-06*

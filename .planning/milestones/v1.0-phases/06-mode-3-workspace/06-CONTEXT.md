# Phase 6: Dashboard & Chat - Context

**Gathered:** 2026-03-06 (v1.0), Updated: 2026-03-13 (v3.0 scope alignment)
**Status:** Ready for planning

<domain>
## Phase Boundary

Browser dashboard for Rizwan's agency: client management, workflow triggering, real-time progress monitoring, deliverable viewing, run history, error display, and a per-run chat view for user input and agent steering. This is a single-user (Rizwan) tool — no multi-tenant auth, no team roles.

</domain>

<decisions>
## Implementation Decisions

### Dashboard Core (DASH-01 through DASH-07)
- Client list with CRUD — create, edit, view EndClients from dashboard
- Workflow catalog — show available workflows from YAML definitions
- Workflow trigger UI — select client + workflow, configure parameters, hit run
- Real-time progress monitoring via SSE — phase-level status (which phase is running, completion)
- Deliverable viewing — rendered HTML reports displayed in browser
- Run history per client — status, cost, duration for past runs
- Error display — which phase failed and why, shown in run detail

### Chat View (CHAT-01 through CHAT-04)
- Each workflow run has a per-run chat thread (ChatMessage model)
- User provides initial inputs (site URL, company name) via chat before execution starts
- Agent can pause execution to ask user for input/clarification mid-run
- User can send additional context or steering instructions to running agent
- Chat-style workflow monitoring: agent messages, phase transitions, deliverables inline

### Visual Design & Layout
- Collapsible sidebar layout: full sidebar with labels that collapses to icons
- Friendly & branded visual feel (Notion/Intercom-like): rounded corners, color accents
- Illustrations + CTAs for empty states ("Add your first client", "Run your first workflow")
- Light mode default with dark mode toggle
- shadcn/ui (Radix UI + Tailwind CSS) for UI components
- TanStack Query for server state + SSE for real-time updates

### Claude's Discretion
- SSE implementation approach (django-eventstream vs custom SSE endpoints)
- Exact sidebar section groupings and icon choices
- Search implementation details
- Deliverable storage format and file organization
- Frontend routing structure

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `hazn_platform/frontend/`: Next.js 16 project with React 19 + Tailwind 4. Has workspace pages from v1.0 Phase 6 execution (client list, workflow catalog, run detail, chat view) — need audit for dead references to removed HITL/QA models
- `orchestrator/api/views.py`: DRF viewsets for WorkflowRun (list, detail with nested agents/tool_calls/phase_outputs)
- `orchestrator/api/serializers.py`: Full serializers for WorkflowRun (list + detail)
- `core/models.py`: Agency, EndClient, VaultCredential, BrandVoice models
- `orchestrator/tasks.py`: run_workflow Celery task

### Established Patterns
- DRF with AllowAny permissions (single-user tool for now)
- Django apps: core, marketing, content, orchestrator, qa, users
- UUID primary keys on all models
- Celery + Redis for async task execution
- FastMCP 3.1.0 with stdio transport for MCP servers

### Integration Points
- `/api/orchestrator/runs/` — WorkflowRun list and detail (exists)
- New endpoints needed: EndClient CRUD, ChatMessage API, Workflow Trigger, SSE streaming
- Next.js frontend connects to Django API

</code_context>

<specifics>
## Specific Ideas

- "This should be a chat experience" — workflow monitoring should feel like a conversation with the agent, not a status dashboard
- Friendly & branded feel, not generic SaaS
- Deliverables are HTML files — render inline in browser
- Agent pause mechanism: executor sets run status to `waiting_for_input`, polls ChatMessage table for user reply

</specifics>

<deferred>
## Deferred Ideas

- **HITL Queue page** — stripped in v3.0 simplification (no human-in-the-loop approval flow)
- **QA badges on deliverables** — stripped in v3.0 (no QA scoring system)
- **Memory Inspector** — stripped in v3.0 (memory management not in dashboard scope)
- **Multi-method auth** (magic links, OAuth, email+password) — single-user tool, no auth needed for v3.0
- **Multi-tenant roles** (Admin/Member) — single-user, deferred
- **Cost visibility / billing** — deferred
- **Clone + re-run workflows** — deferred
- **Public shareable links for deliverables** — deferred
- **Cmd-K global search** — deferred
- **Notification bell** — deferred
- **HITL inline approval cards in chat** — stripped with HITL

</deferred>

---

*Phase: 06-mode-3-workspace*
*Context gathered: 2026-03-06, updated 2026-03-13 for v3.0 scope*

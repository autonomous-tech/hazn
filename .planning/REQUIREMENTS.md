# Requirements: Hazn Platform

**Defined:** 2026-03-06
**Core Value:** Agents remember and compound -- every engagement builds on past decisions, brand voice, keyword history, and craft knowledge.

## v2.0 Requirements (Shipped)

### Runtime Infrastructure

- [x] **RUNT-01**: PromptAssembler constructs system prompts from agent/skill/workflow markdown definitions
- [x] **RUNT-02**: AgentRunner executes tool_use loop with turn counting and conversation management
- [x] **RUNT-03**: ToolRouter dispatches tool calls to existing MCP servers and FastMCP tools
- [x] **RUNT-04**: Claude Agent SDK integration for Mode 1 execution (Max subscription)
- [x] **RUNT-05**: Anthropic API integration for Mode 3 execution (metered per-token)
- [x] **RUNT-06**: Per-workflow token budgets with enforcement and runaway detection
- [x] **RUNT-07**: Per-agency cost caps with alerts and automatic halt
- [x] **RUNT-08**: OutputCollector captures agent artifacts (markdown, findings, recommendations)

### Workflow Execution

- [x] **WKFL-01**: User can trigger workflow from workspace UI with client ID and parameters
- [x] **WKFL-02**: Workflow executes all DAG phases with real agent execution at each phase
- [x] **WKFL-05**: Workflow status visible in workspace UI (running, paused, complete, failed)

### Deliverable Pipeline

- [x] **DLVR-01**: Agents produce structured markdown as workflow output
- [x] **DLVR-02**: Pipeline converts markdown to branded HTML report via Jinja2 templates
- [x] **DLVR-03**: Deliverable stored and accessible in workspace Deliverables section
- [x] **DLVR-04**: Deliverable linked to workflow run with full provenance

## v3.0 Requirements

Requirements for strip & simplify milestone. Each maps to roadmap phases.

### Strip & Cleanup

- [x] **STRP-01**: All 4 MCP servers removed (hazn-memory, vercel, github, ga4-gsc-pagespeed)
- [x] **STRP-02**: HITL queue system removed (model, views, serializers, frontend pages)
- [x] **STRP-03**: QA approval pipeline removed (scoring, 48-hour lifecycle, approval states)
- [x] **STRP-04**: Anthropic API backend removed (keep Agent SDK only)
- [x] **STRP-05**: Budget enforcement and agency cost caps removed
- [x] **STRP-06**: Langfuse kept for observability; budget enforcement stripped from metering module
- [x] **STRP-07**: Conflict detection removed (L2 vs L3 hierarchy)
- [x] **STRP-08**: Session/checkpoint turn counter removed
- [x] **STRP-09**: Data lifecycle/GDPR deletion scheduling removed
- [x] **STRP-10**: Django models simplified (enterprise fields removed, Agency as singleton, clean migrations)

### Workflow Executor

- [x] **EXEC-01**: Agent SDK executor reads YAML workflow definitions and chains phases via DAG order
- [x] **EXEC-02**: Agent system prompts loaded from hazn/agents/*.md files per phase
- [x] **EXEC-03**: Skills injected into agent context from hazn/skills/*.md per workflow YAML
- [x] **EXEC-04**: Phase-to-phase output passing (Phase N output available to Phase N+1)
- [x] **EXEC-05**: Async execution via Celery (workflows run in background)
- [x] **EXEC-06**: Structured output captured per phase and stored in WorkflowPhaseOutput

### Python Function Tools

- [x] **TOOL-01**: File I/O tools (read/write files, create directories)
- [x] **TOOL-02**: Web fetch tool (fetch and parse web pages)
- [x] **TOOL-03**: GA4 data collection tool
- [x] **TOOL-04**: GSC (Google Search Console) data collection tool
- [x] **TOOL-05**: PageSpeed Insights API tool
- [x] **TOOL-06**: GitHub API tools (repo operations)
- [x] **TOOL-07**: Vercel deployment tools
- [x] **TOOL-08**: All tools registered with Claude Agent SDK

### Per-Client Memory

- [x] **MEMO-01**: One Letta agent per client with isolated persistent memory
- [x] **MEMO-02**: Client context loaded at workflow run start (brand voice, keywords, campaigns)
- [x] **MEMO-03**: Learning accumulation during execution (CraftLearning with provenance and confidence)
- [x] **MEMO-04**: Memory checkpoint at phase boundaries
- [x] **MEMO-05**: Semantic memory search across client learnings
- [x] **MEMO-06**: User can correct wrong learnings before they compound into future runs

### Workflow Chat

- [x] **CHAT-01**: Each workflow run has a chat view showing the conversation thread
- [ ] **CHAT-02**: User provides initial inputs (site URL, company name, etc.) via chat before execution starts
- [ ] **CHAT-03**: Agent can pause execution to ask user for input or clarification mid-run
- [ ] **CHAT-04**: User can send additional context or steering instructions to the running agent

### Dashboard & Frontend

- [x] **DASH-01**: Client list with CRUD (create, edit, view clients)
- [x] **DASH-02**: Workflow catalog showing available workflows from YAML
- [x] **DASH-03**: Workflow trigger UI (select client + workflow, hit run)
- [x] **DASH-04**: Real-time progress monitoring via SSE (phase-level status)
- [x] **DASH-05**: Deliverable viewing (rendered HTML reports in browser)
- [x] **DASH-06**: Run history per client (status, cost, duration)
- [x] **DASH-07**: Error display (which phase failed and why)

### Validation

- [ ] **VALD-01**: Analytics-teaser workflow executes end-to-end on real client data
- [ ] **VALD-02**: Deliverable produced and viewable in dashboard

## Future Requirements

### Enhanced Deliverables

- **EDLV-01**: Deliverables deployed to Vercel preview URLs for client sharing
- **EDLV-02**: Deliverable versioning with revision history and comparison
- **EDLV-03**: PDF export from HTML reports
- **EDLV-04**: Share link generation with time-limited public URLs

### Memory Inspector

- **MINS-01**: Memory Inspector UI for browsing client memory blocks
- **MINS-02**: Search and filter learnings by type, confidence, source
- **MINS-03**: Visual memory correction interface

### Extended Workflows

- **EWKF-01**: All 7 workflow definitions run end-to-end
- **EWKF-02**: Batch execution (same workflow across multiple clients)
- **EWKF-03**: Custom workflow authoring from UI

### Portfolio Intelligence

- **PORT-01**: Cross-client insights dashboard (aggregate keywords, audit scores)
- **PORT-02**: Cost tracking summary per client and workflow type

## Out of Scope

| Feature | Reason |
|---------|--------|
| Multi-tenant / agency self-serve | Personal tool, single user |
| Billing / subscription | Not needed for personal use |
| Anthropic API direct backend | Using Agent SDK only |
| MCP server protocol | Replaced by Python function tools |
| HITL approval queue | User reviews deliverables directly |
| QA scoring pipeline | User is the quality gate |
| Conflict detection (L2/L3) | Single user, no conflicts |
| Budget enforcement / cost caps | Track costs, don't enforce limits |
| Langfuse metering | Simple cost fields on WorkflowRun |
| Session/checkpoint turn system | Phase-boundary checkpoints only |
| Data lifecycle / GDPR scheduling | Personal tool, user owns all data |
| Mobile | Web-first |
| Real-time collaboration | Single user |
| OpenClaw | Rejected in v2.0 research |
| Mode 2 (MCP-connected) | Not applicable |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| STRP-01 | Phase 3 | Complete |
| STRP-02 | Phase 2 | Complete |
| STRP-03 | Phase 2 | Complete |
| STRP-04 | Phase 1 | Complete |
| STRP-05 | Phase 1 | Complete |
| STRP-06 | Phase 1 | Complete |
| STRP-07 | Phase 2 | Complete |
| STRP-08 | Phase 1 | Complete |
| STRP-09 | Phase 1 | Complete |
| STRP-10 | Phase 2 | Complete |
| EXEC-01 | Phase 4 | Complete |
| EXEC-02 | Phase 4 | Complete |
| EXEC-03 | Phase 4 | Complete |
| EXEC-04 | Phase 4 | Complete |
| EXEC-05 | Phase 4 | Complete |
| EXEC-06 | Phase 4 | Complete |
| TOOL-01 | Phase 3 | Complete |
| TOOL-02 | Phase 3 | Complete |
| TOOL-03 | Phase 3 | Complete |
| TOOL-04 | Phase 3 | Complete |
| TOOL-05 | Phase 3 | Complete |
| TOOL-06 | Phase 3 | Complete |
| TOOL-07 | Phase 3 | Complete |
| TOOL-08 | Phase 3 | Complete |
| MEMO-01 | Phase 5 | Complete |
| MEMO-02 | Phase 5 | Complete |
| MEMO-03 | Phase 5 | Complete |
| MEMO-04 | Phase 5 | Complete |
| MEMO-05 | Phase 5 | Complete |
| MEMO-06 | Phase 5 | Complete |
| CHAT-01 | Phase 6 | Complete |
| CHAT-02 | Phase 6 | Pending |
| CHAT-03 | Phase 6 | Pending |
| CHAT-04 | Phase 6 | Pending |
| DASH-01 | Phase 6 | Complete |
| DASH-02 | Phase 6 | Complete |
| DASH-03 | Phase 6 | Complete |
| DASH-04 | Phase 6 | Complete |
| DASH-05 | Phase 6 | Complete |
| DASH-06 | Phase 6 | Complete |
| DASH-07 | Phase 6 | Complete |
| VALD-01 | Phase 7 | Pending |
| VALD-02 | Phase 7 | Pending |

**Coverage:**
- v3.0 requirements: 43 total
- Mapped to phases: 43
- Unmapped: 0

---
*Requirements defined: 2026-03-06*
*Last updated: 2026-03-12 after v3.0 roadmap creation*

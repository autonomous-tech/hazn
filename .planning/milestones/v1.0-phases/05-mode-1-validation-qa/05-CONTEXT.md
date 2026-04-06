# Phase 5: Mode 1 Validation & QA - Context

**Gathered:** 2026-03-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Hazn runs real internal marketing engagements end-to-end with QA gates on every deliverable, configurable approval timeouts, Vercel preview URL staging for web deliverables, and GDPR-compliant data lifecycle enforcement (retention, deletion, notification). This phase adds a QA Tester agent integration, extends the HITL system with deliverable approval gates, adds email notification infrastructure, and implements data retention/deletion management commands.

</domain>

<decisions>
## Implementation Decisions

### QA Failure Handling
- FAIL verdict blocks the workflow and creates a blocking HITL item for the agency to decide: reject, override to approve, or request rework
- CONDITIONAL PASS (score 75-89) also enters HITL for agency approval, same flow as PASS but with QA notes highlighted showing what's conditional
- PASS (score 90+) enters HITL for standard approval (48h timeout)
- QA agent infrastructure crash (not a quality verdict): set QA verdict to PENDING, create HITL item flagging the crash, allow manual QA. Do not block workflow due to infrastructure issues
- HITL items for FAIL verdicts include the full QA report: overall score, per-criterion scores and notes, specific issues found. Agency has full context to decide

### Approval Timeout Behavior
- 48-hour timeout with auto-approve as the default action for all deliverable types (Mode 1 is internal -- low risk)
- Timeout duration configurable per L2 agency via tool_preferences (48h default, agencies can set 24h, 72h, etc.)
- Auto-approved deliverables use distinct 'auto_approved' status, visually distinguished from explicitly approved deliverables for auditing
- Preview URLs (QA-04) only for web deliverables: landing pages, full sites, and blogs. Analytics reports, emails, and bug fixes have different output formats and don't get Vercel previews

### Deletion Notifications
- Churn + 30 day warning: send both webhook (existing deliver_webhook task) AND direct email to agency admin
- Email via Resend (django-anymail integration) for transactional notifications
- Churn warning email includes detailed data summary: counts of clients, workflows, deliverables, and stored credentials affected by upcoming deletion
- GDPR deletion (DATA-02) sends confirmation notification (webhook + email) when deletion is complete: "All data for [client name] has been permanently deleted"
- Deletion conditional on prior notification: retain deletion_notified_at on Agency, enforce_retention must check notification was sent before deleting

### QA Criteria Ownership
- Platform defines base QA criteria for all 6 task types: analytics, landing page, full site, blog, email, bug fix
- L2 agencies can override via 'qa_criteria_overrides' key in existing Agency.tool_preferences JSONField -- override weights, add custom criteria, or change thresholds per task type
- Pass/fail thresholds customizable per agency: platform default 90 (pass) / 75 (conditional), agencies can set their own in tool_preferences
- All 6 task types populated with criteria from day one -- complete coverage for any internal engagement

### Claude's Discretion
- Exact QA criteria definitions per task type (weights, specific checks, descriptions)
- django-anymail + Resend configuration details
- Email template design for deletion warnings and GDPR confirmations
- QA agent execution mechanism (real Letta agent vs stub for testing)
- Management command implementation details for lifecycle enforcement
- Celery beat schedule configuration for periodic lifecycle tasks

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `orchestrator/hitl.py`: HITL system with configurable timeout_hours, trigger types, timeout_action defaults, webhook delivery -- extend with `deliverable_approval` trigger type
- `orchestrator/executor.py`: DAG-based workflow execution with phase outputs -- inject QA phases automatically after deliverable-producing phases
- `orchestrator/models.py`: HITLItem with timeout_hours, WorkflowPhaseOutput -- QA links to these
- `orchestrator/tasks.py`: check_hitl_timeouts periodic task, deliver_webhook with exponential backoff retry
- `mcp_servers/vercel_server.py`: deploy_project, get_preview_url, get_deployment_status tools -- wire for staging
- `core/models.py`: Agency (tool_preferences JSONField for qa_criteria_overrides), EndClient, VaultCredential with CASCADE FKs
- `core/vault.py`: read_secret() with AppRole auth -- extend with delete_secret for data lifecycle
- `agents/qa-tester.md`: QA scoring rubric with weighted categories and PASS/CONDITIONAL/FAIL thresholds
- `config/settings/base.py`: CELERY_BEAT_SCHEDULER = DatabaseScheduler, django_celery_beat in INSTALLED_APPS

### Established Patterns
- FastMCP 3.1.0 with stdio transport for MCP servers
- JSONField for flexible config (tool_preferences, house_style) -- qa_criteria_overrides fits naturally
- Domain-split Django apps (core, marketing, content, orchestrator) -- new `qa` app follows this pattern
- Management commands callable from both CLI and Celery tasks
- Append-only with provenance pattern for audit trails

### Integration Points
- WorkflowExecutor.run() -- inject QA phase after deliverable-producing phases
- HITLItem create flow -- add deliverable_approval trigger type with 48h default
- Agency.tool_preferences -- extend with qa_criteria_overrides and approval_timeout_hours
- deliver_webhook task -- reuse for deletion notifications alongside new email
- Celery beat -- add periodic tasks for retention enforcement, GDPR processing, notification

</code_context>

<specifics>
## Specific Ideas

- "Auto-approve all" on timeout because Mode 1 is internal Autonomous use -- low risk. Can tighten for Mode 3
- Webhook + email dual notification for deletion warnings -- agency chose both channels for redundancy on a critical notification
- Detailed data summary in deletion warning email so agencies know exactly what's at stake
- GDPR deletion confirmation email -- transparency best practice, agency explicitly chose this
- Platform defaults + agency overrides for QA -- agencies with different quality bars can adjust without starting from scratch
- All 6 task types defined upfront rather than incrementally -- complete coverage from day one for Mode 1 validation

</specifics>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 05-mode-1-validation-qa*
*Context gathered: 2026-03-06*

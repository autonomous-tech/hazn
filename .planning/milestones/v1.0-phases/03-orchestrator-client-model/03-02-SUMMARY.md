---
phase: 03-orchestrator-client-model
plan: 02
subsystem: orchestrator
tags: [letta, agent-lifecycle, session-management, metering, cost-tracking, tdd]

# Dependency graph
requires:
  - phase: 01-infrastructure-foundation
    provides: Django project skeleton, core models (Agency, EndClient), Celery+Redis config
  - phase: 02-memory-layer
    provides: HaznMemory class with session lifecycle methods (record_turn, checkpoint_sync, failure_sync, end_session)
  - phase: 03-orchestrator-client-model/plan-01
    provides: WorkflowRun, WorkflowAgent models, orchestrator Django app with migration
provides:
  - Agent manager with persistent Letta agent lookup/creation per type per L3 client
  - Persona refresh from hazn/agents/ markdown at every session start
  - Tool reconciliation enforcing principle of least privilege per phase
  - WorkflowSession lifecycle (start, checkpoint, end, fail, timeout detection)
  - MeteringCallback with per-agent token/cost/turn tracking and threshold alerts
  - Agency-level configurable thresholds (max_turns, max_cost_per_run)
affects: [03-03, 03-04, phase-4-observability, phase-5-api]

# Tech tracking
tech-stack:
  added: []
  patterns: [persistent-agent-per-type-per-client, race-condition-retry, metering-callback-flush, session-lifecycle-state-machine]

key-files:
  created:
    - hazn_platform/hazn_platform/orchestrator/agent_manager.py
    - hazn_platform/hazn_platform/orchestrator/session.py
    - hazn_platform/hazn_platform/orchestrator/metering.py
    - hazn_platform/tests/test_agent_manager.py
    - hazn_platform/tests/test_session.py
    - hazn_platform/tests/test_metering.py
  modified: []

key-decisions:
  - "Agent naming convention: {agent_type}--{l3_client_id} using Letta agent name as natural unique key"
  - "Race condition handling via try/except on creation + retry lookup instead of database locking"
  - "MeteringCallback.from_agency() factory reads max_turns/max_cost_per_run from Agency.tool_preferences with defaults (50 turns, $5)"
  - "WorkflowSession does not load context -- context loading deferred to per-agent executor via HaznMemory.load_client_context()"
  - "Secret isolation enforced by design: WorkflowSession has no credential storage attributes"

patterns-established:
  - "Agent lifecycle: list-by-name -> modify system prompt (existing) or create with tags/blocks (new)"
  - "Tool reconciliation: diff current vs desired -> detach removed -> attach added (principle of least privilege)"
  - "Session lifecycle state machine: pending -> running -> (completed | failed | timed_out)"
  - "Metering accumulation: per-agent dict -> threshold check on each call -> flush_to_db via update_or_create"

requirements-completed: [ORCH-01, ORCH-02, ORCH-03, CRED-01, CRED-02, CRED-03, CRED-04]

# Metrics
duration: 5min
completed: 2026-03-05
---

# Phase 3 Plan 2: Agent Manager, Session Lifecycle & Metering Summary

**Persistent Letta agent manager with persona refresh, WorkflowSession lifecycle (start/checkpoint/end/fail/timeout), and MeteringCallback with per-agent cost tracking and configurable threshold alerts**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-05T18:06:41Z
- **Completed:** 2026-03-05T18:12:23Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- Built agent manager with persistent agent lookup/creation per type per L3 client, persona refresh from markdown, tool reconciliation, and race condition handling
- Implemented WorkflowSession managing full lifecycle (pending -> running -> completed/failed) with HaznMemory delegation, 4-hour timeout detection, and conflict logging
- Created MeteringCallback with per-agent token/cost/turn accumulation, configurable thresholds from Agency.tool_preferences, and flush_to_db via WorkflowAgent update_or_create
- Enforced CRED-02: secret isolation verified by negative test -- no Vault secrets in WorkflowRun fields or agent context

## Task Commits

Each task was committed atomically (TDD: test -> feat):

1. **Task 1: Implement agent manager with persistent agent lookup and persona refresh** - TDD
   - RED: `6c8a8d7` (test) - 11 failing tests for agent manager
   - GREEN: `a99284c` (feat) - agent_manager.py with read_agent_persona, get_or_create_agent, reconcile_tools

2. **Task 2: Implement session lifecycle and metering callback** - TDD
   - RED: `ad2da05` (test) - 24 failing tests for session and metering
   - GREEN: `8ee5fb0` (feat) - session.py (WorkflowSession) and metering.py (MeteringCallback)

## Files Created/Modified
- `hazn_platform/hazn_platform/orchestrator/agent_manager.py` - Persistent agent lookup/creation, persona refresh, tool reconciliation
- `hazn_platform/hazn_platform/orchestrator/session.py` - WorkflowSession lifecycle (start, checkpoint, end, fail, timeout, conflict logging)
- `hazn_platform/hazn_platform/orchestrator/metering.py` - MeteringCallback with per-agent accumulation, thresholds, flush_to_db
- `hazn_platform/tests/test_agent_manager.py` - 11 tests for agent manager
- `hazn_platform/tests/test_session.py` - 16 tests for session lifecycle
- `hazn_platform/tests/test_metering.py` - 8 tests for metering callback

## Decisions Made
- Used Letta agent name as natural unique key (`{agent_type}--{l3_client_id}`) instead of a separate registry table -- simpler, avoids additional migration
- Race condition handling via try/except on duplicate name + retry lookup -- follows RESEARCH.md Pitfall 2 recommendation without database-level locking
- MeteringCallback.from_agency() factory method reads agency-level thresholds from `tool_preferences` (keys: `max_turns`, `max_cost_per_run`) -- reuses existing JSONField instead of adding columns
- WorkflowSession.start() does NOT load context -- context loading is deferred to per-agent executor calls to `HaznMemory.load_client_context()`, as different agents may target different L3 contexts
- Secret isolation enforced by design: WorkflowSession class has no `_secrets`, `_vault_secrets`, or `_credentials` attributes; credential access only through get_credentials MCP tool (CRED-04)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Added seo-specialist persona to test fixture**
- **Found during:** Task 1 (TDD GREEN phase)
- **Issue:** Test for agent naming convention used `seo-specialist` agent type, but the persona_dir fixture only contained `strategist.md`
- **Fix:** Added `seo-specialist.md` to the persona_dir fixture
- **Files modified:** hazn_platform/tests/test_agent_manager.py
- **Verification:** All 11 agent manager tests pass
- **Committed in:** a99284c (part of Task 1 GREEN commit)

---

**Total deviations:** 1 auto-fixed (1 bug in test fixture)
**Impact on plan:** Minimal -- test fixture was incomplete for the naming convention test case. No scope creep.

## Issues Encountered
None beyond the test fixture deviation documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Agent manager is ready for DAG executor integration (Plan 03-03)
- WorkflowSession primitives are ready for Celery task wrappers (Plan 03-03)
- MeteringCallback is ready for real-time cost tracking during workflow execution
- All 35 tests pass across agent_manager, session, and metering modules
- HITL queue management (Plan 03-04) can use WorkflowSession.log_conflicts() and MeteringCallback threshold alerts

## Self-Check: PASSED

- All 6 created files verified on disk
- All 4 commit hashes verified in git log
- 35 tests pass (11 agent_manager + 16 session + 8 metering)

---
*Phase: 03-orchestrator-client-model*
*Completed: 2026-03-05*

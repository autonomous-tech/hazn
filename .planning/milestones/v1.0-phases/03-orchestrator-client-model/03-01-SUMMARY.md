---
phase: 03-orchestrator-client-model
plan: 01
subsystem: orchestrator
tags: [django, pydantic, yaml, graphlib, topological-sort, metering, hitl]

# Dependency graph
requires:
  - phase: 01-infrastructure-foundation
    provides: Django project skeleton, core models (Agency, EndClient), Celery+Redis config
provides:
  - WorkflowRun, WorkflowAgent, WorkflowToolCall, WorkflowPhaseOutput, HITLItem Django models
  - Pydantic workflow YAML schema (WorkflowSchema, WorkflowPhaseSchema, WorkflowCheckpoint)
  - YAML parser with load_workflow, get_dependency_graph, get_execution_order
  - Orchestrator Django app registered in INSTALLED_APPS with migration applied
affects: [03-02, 03-03, 03-04, phase-4-observability, phase-5-api]

# Tech tracking
tech-stack:
  added: [graphlib (stdlib), pyyaml (transitive)]
  patterns: [pydantic-yaml-validation, topological-sort-execution-waves, tdd-red-green]

key-files:
  created:
    - hazn_platform/hazn_platform/orchestrator/models.py
    - hazn_platform/hazn_platform/orchestrator/workflow_models.py
    - hazn_platform/hazn_platform/orchestrator/workflow_parser.py
    - hazn_platform/hazn_platform/orchestrator/admin.py
    - hazn_platform/hazn_platform/orchestrator/apps.py
    - hazn_platform/hazn_platform/orchestrator/migrations/0001_initial.py
    - hazn_platform/tests/test_orchestrator_models.py
    - hazn_platform/tests/test_workflow_parser.py
  modified:
    - hazn_platform/config/settings/base.py

key-decisions:
  - "Pydantic extra='allow' for both WorkflowPhaseSchema and WorkflowSchema to tolerate YAML schema variations (per_article, parallel_tracks, article_template, agents, scripts, etc.)"
  - "Test YAML fixtures embedded inline in test file for Docker container compatibility; real YAML file test skipped conditionally when files not accessible"
  - "graphlib.TopologicalSorter for execution wave computation with CycleError detection"

patterns-established:
  - "Orchestrator Django app pattern: apps.py with name='hazn_platform.orchestrator', UUID PKs, TextChoices for enums"
  - "Pydantic YAML validation: yaml.safe_load -> WorkflowSchema.model_validate(data) with extra='allow'"
  - "Dependency graph as dict[str, set[str]] with TopologicalSorter for parallel wave ordering"

requirements-completed: [ORCH-04, ORCH-06, CLT-01, CLT-02, CLT-03]

# Metrics
duration: 12min
completed: 2026-03-05
---

# Phase 3 Plan 1: Orchestrator Models & Workflow Parser Summary

**Orchestrator Django app with 5 metering/HITL models, Pydantic workflow YAML schema validating all 7 existing workflows, and TopologicalSorter-based dependency graph with parallel execution wave computation**

## Performance

- **Duration:** 12 min
- **Started:** 2026-03-05T17:50:39Z
- **Completed:** 2026-03-05T18:03:17Z
- **Tasks:** 2
- **Files modified:** 11

## Accomplishments
- Created orchestrator Django app with 5 models: WorkflowRun (status/metering), WorkflowAgent (per-agent tracking), WorkflowToolCall (per-tool tracking), WorkflowPhaseOutput (structured phase outputs), HITLItem (4 trigger types, 5 statuses, configurable timeouts)
- Built Pydantic v2 workflow YAML schema that validates all 7 existing YAML files despite inconsistent schemas (per_article, parallel_tracks, agents, scripts, duration, etc.)
- Implemented dependency graph extraction and TopologicalSorter-based execution wave computation with circular dependency detection

## Task Commits

Each task was committed atomically (TDD: test -> feat):

1. **Task 1: Create orchestrator Django app with 5 models** - TDD
   - RED: `b090e79` (test) - Failing tests for all 5 models
   - GREEN: `51e0c82` (feat) - Models, admin, migration, INSTALLED_APPS

2. **Task 2: Implement workflow YAML Pydantic schema and parser** - TDD
   - RED: `49fd584` (test) - Failing tests for schema and parser
   - GREEN: `e5e427f` (feat) - workflow_models.py and workflow_parser.py

## Files Created/Modified
- `hazn_platform/hazn_platform/orchestrator/__init__.py` - Empty init for Django app
- `hazn_platform/hazn_platform/orchestrator/apps.py` - OrchestratorConfig (name="hazn_platform.orchestrator")
- `hazn_platform/hazn_platform/orchestrator/models.py` - WorkflowRun, WorkflowAgent, WorkflowToolCall, WorkflowPhaseOutput, HITLItem
- `hazn_platform/hazn_platform/orchestrator/admin.py` - Admin registrations for all 5 models
- `hazn_platform/hazn_platform/orchestrator/migrations/0001_initial.py` - Initial migration
- `hazn_platform/hazn_platform/orchestrator/migrations/__init__.py` - Migrations package init
- `hazn_platform/hazn_platform/orchestrator/workflow_models.py` - Pydantic schemas: WorkflowPhaseSchema, WorkflowCheckpoint, WorkflowSchema
- `hazn_platform/hazn_platform/orchestrator/workflow_parser.py` - load_workflow, get_dependency_graph, get_execution_order
- `hazn_platform/config/settings/base.py` - Added "hazn_platform.orchestrator" to LOCAL_APPS
- `hazn_platform/tests/test_orchestrator_models.py` - 19 tests for model CRUD, defaults, cascades, admin
- `hazn_platform/tests/test_workflow_parser.py` - 17 tests for schema validation, parsing, graph, waves

## Decisions Made
- Used Pydantic `extra="allow"` on both WorkflowPhaseSchema and WorkflowSchema to handle the wide variety of YAML keys across 7 files (per_article, parallel_tracks, article_template, agents, scripts, skill, duration, notes, skip_for_speed, total_duration, references) without requiring explicit fields for every variation
- Embedded representative YAML fixtures directly in the test file rather than depending on files outside the Docker container mount; added a `skipif` guard on the test that loads all 7 real YAML files so it runs on host but skips in Docker
- Used `graphlib.TopologicalSorter` from stdlib for dependency graph processing -- provides cycle detection and parallel-ready wave batching with no external dependency

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Test YAML fixture path not accessible in Docker container**
- **Found during:** Task 2 (TDD GREEN phase)
- **Issue:** WORKFLOWS_DIR resolved to /app/hazn/workflows/ inside Docker, but hazn/ is mounted one level above the Django project at /app/. The 7 real YAML files are not accessible from within the container.
- **Fix:** Created inline YAML fixtures (website.yaml, audit.yaml, blog.yaml) in the test file that replicate the structure of real files. Added skipif guard on the integration test that loads all 7 real files. Both host and container test runs succeed.
- **Files modified:** hazn_platform/tests/test_workflow_parser.py
- **Verification:** 16 passed, 1 skipped in Docker; 17 passed (including real YAML files) on host
- **Committed in:** e5e427f (part of Task 2 GREEN commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Fix was necessary for Docker test compatibility. No scope creep. All 7 real YAML files still tested on host.

## Issues Encountered
None beyond the deviation documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Orchestrator models are ready for session lifecycle management (Plan 03-02)
- Workflow parser is ready for DAG executor implementation (Plan 03-03)
- HITL models are ready for queue management API (Plan 03-04)
- All 5 models accept inserts and cascade correctly
- Admin interface available for manual inspection

## Self-Check: PASSED

- All 11 created files verified on disk
- All 4 commit hashes verified in git log
- 35 tests pass, 1 skipped (expected)

---
*Phase: 03-orchestrator-client-model*
*Completed: 2026-03-05*

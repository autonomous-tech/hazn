# Deferred Items - Phase 02

## Pre-existing Test Failures (Out of Scope for 02-02)

These test files have references to models/fields deleted in Plan 02-01 (not 02-02). They were already broken before this plan executed.

1. **tests/test_executor.py** - imports `HITLItem` from orchestrator.models (deleted in Plan 01). Also patches `detect_conflicts`, `process_conflicts`, `should_run_qa`, `create_deliverable`, `has_blocking_items` which are now commented out. Entire test file needs rewrite in Phase 4 (executor rewrite).

2. **tests/test_metering.py:98** - asserts `agent_1.turn_count == 1` but `turn_count` field was removed from WorkflowAgent in Plan 01.

3. **tests/test_memory.py** - references `Agency.tool_preferences` in multiple fixtures (lines 313, 372, 542, 568, 614, 647). Field was removed in Plan 01.

4. **tests/integration/test_memory_integration.py** - references `Agency.tool_preferences` in fixtures (lines 77, 151, 239). Field was removed in Plan 01.

## Recommendation

These should be addressed in Phase 4 (executor rewrite) or as a pre-Phase 3 test cleanup task. They do not affect the correctness of the v3.0 model layer being built in Phase 2.

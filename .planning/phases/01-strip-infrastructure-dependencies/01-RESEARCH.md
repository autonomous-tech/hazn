# Phase 1: Strip Infrastructure & Dependencies - Research

**Researched:** 2026-03-12
**Domain:** Django codebase cleanup -- removing enterprise runtime modules, dead code paths, and unused dependencies
**Confidence:** HIGH

## Summary

Phase 1 is a surgical deletion and cleanup phase. The codebase has well-defined modules with clear boundaries: `budget.py` (229 lines), `backends/anthropic_api.py` (239 lines), `core/lifecycle.py` (271 lines), and three management commands. These files are entirely self-contained and can be deleted outright. The remaining work is import/reference cleanup in 6-8 files that import from the deleted modules.

The biggest risk is cascade breakage in tests. 15+ test files reference budget-related imports (BudgetConfig appears in test_agent_runner.py, test_agent_sdk_backend.py, test_sse_events.py, and test_executor.py). The BudgetConfig type is embedded in the RuntimeBackend Protocol signature and the AgentRunner.run() signature, so removing budget.py requires updating these interfaces, not just deleting imports.

**Primary recommendation:** Delete files bottom-up (leaf modules first: budget.py, anthropic_api.py, lifecycle.py, management commands, test files), then update interfaces (RuntimeBackend Protocol, AgentRunner.run, AgentSDKBackend.execute signatures), then clean up executor.py. Verify with `python manage.py check` and `pytest --collect-only` after each wave.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Langfuse -- KEEP: Keep Langfuse service, dependency, tracing module, and metering accumulation. Keep all tracing levels: workflow traces + phase spans + tool call spans. Keep MeteringCallback that accumulates token costs per agent. ONLY strip: BudgetEnforcer, BudgetConfig, check_agency_cost_cap, agency cost caps, max_turns threshold enforcement
- Budget enforcement -- FULL REMOVAL: Delete budget.py entirely. Strip budget imports and usage from executor.py, agent_runner.py, backends/agent_sdk.py. Remove budget-related tests.
- Anthropic API backend -- FULL REMOVAL: Delete backends/anthropic_api.py entirely. Remove API backend selection logic from executor.py. Remove lazy import from backends/__init__.py. Keep Agent SDK backend path as the only execution path.
- Celery beat -- KEEP INFRASTRUCTURE: Remove the 3 GDPR periodic tasks. Keep django-celery-beat package and scheduler infrastructure.
- Data lifecycle -- FULL REMOVAL: Delete lifecycle.py entirely. Delete management commands: enforce_retention.py, process_deletions.py, notify_deletions.py. Remove lifecycle fields from models deferred to Phase 2 migration.

### Claude's Discretion
- Whether to delete session.py entirely or keep memory coordination parts
- Exact order of file deletions and import cleanup
- How to handle metering.py cleanup (strip Langfuse annotation calls for budget alerts, keep cost accumulation)
- Whether to remove turn_count fields from models now (Phase 1) or defer to Phase 2 migrations

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| STRP-04 | Anthropic API backend removed (keep Agent SDK only) | Delete `backends/anthropic_api.py`, remove lazy import from `backends/__init__.py`, remove runtime mode selection from `executor.py` lines 317-348, delete `test_agent_runner.py` AnthropicAPIBackend test classes |
| STRP-05 | Budget enforcement and agency cost caps removed | Delete `budget.py` entirely, strip BudgetConfig from RuntimeBackend Protocol and all signatures, remove check_agency_cost_cap from executor.py, delete `test_budget.py` |
| STRP-06 | Langfuse kept for observability; budget enforcement stripped from metering module | Keep `tracing.py`, `metering.py` core accumulation, Langfuse dependency in pyproject.toml. Strip `_annotate_langfuse_event` budget alert method, remove `_max_turns` and `_max_cost` threshold logic from MeteringCallback |
| STRP-08 | Session/checkpoint turn counter removed | Strip `record_turn()` from session.py and the `on_turn` callback from executor.py. Keep session.py memory coordination (get_memory, checkpoint, end, fail) for Phase 4/5 |
| STRP-09 | Data lifecycle/GDPR deletion scheduling removed | Delete `lifecycle.py`, 3 management commands, 3 Celery tasks from tasks.py, `test_data_lifecycle.py` |
</phase_requirements>

## Standard Stack

### Core (existing -- no new libraries)
| Library | Version | Purpose | Status |
|---------|---------|---------|--------|
| Django | 5.2.12 | Web framework | KEEP |
| celery | 5.6.2 | Task queue | KEEP |
| django-celery-beat | 2.9.0 | Beat scheduler | KEEP |
| langfuse | >=3.14.0 | Observability/tracing | KEEP |
| claude-code-sdk | (not in pyproject.toml) | Agent SDK backend | KEEP (runtime dep) |
| anthropic | (not in pyproject.toml) | Direct API client | REMOVE (used only by anthropic_api.py) |
| pydantic | (transitive) | BudgetConfig model | KEEP (used elsewhere), remove BudgetConfig |

### Dependencies to Remove from pyproject.toml
| Dependency | Reason for Removal | Status |
|------------|-------------------|--------|
| None | Langfuse stays per user decision. `anthropic` SDK is not listed in pyproject.toml (likely transitive). No explicit budget-related packages exist. | No pyproject.toml dependency removals needed |

**Key finding:** `langfuse>=3.14.0` remains in pyproject.toml. The `anthropic` SDK is NOT listed as a direct dependency (it is likely a transitive dependency of `claude-code-sdk` or installed separately). No Docker Compose service for Langfuse exists in `docker-compose.local.yml` -- Langfuse is used as a SaaS service via API keys in Django settings.

## Architecture Patterns

### File Deletion Map (verified from codebase)

**Files to DELETE entirely:**
```
hazn_platform/orchestrator/budget.py              # 229 lines - BudgetEnforcer, BudgetConfig, calculate_cost, check_agency_cost_cap
hazn_platform/orchestrator/backends/anthropic_api.py # 239 lines - AnthropicAPIBackend
core/lifecycle.py                                   # 271 lines - GDPR lifecycle functions
core/management/commands/enforce_retention.py       # Management command
core/management/commands/process_deletions.py       # Management command
core/management/commands/notify_deletions.py        # Management command
tests/test_budget.py                                # All budget tests
tests/test_data_lifecycle.py                        # All lifecycle tests
```

**Files to MODIFY (import/reference cleanup):**
```
hazn_platform/orchestrator/executor.py       # Strip budget imports (lines 30-31), cost cap check (lines 277-290), BudgetConfig construction (lines 302-315), backend selection (lines 317-348), on_turn callback (lines 382-383)
hazn_platform/orchestrator/agent_runner.py   # Remove BudgetConfig from imports, RuntimeBackend Protocol, AgentRunner.run() signature
hazn_platform/orchestrator/backends/agent_sdk.py  # Remove BudgetConfig import, strip from execute() signature
hazn_platform/orchestrator/backends/__init__.py   # Remove AnthropicAPIBackend lazy import
hazn_platform/orchestrator/metering.py       # Strip _annotate_langfuse_event, _max_turns/_max_cost threshold logic, on_threshold_alert
hazn_platform/orchestrator/session.py        # Strip record_turn() method
hazn_platform/orchestrator/tasks.py          # Remove 3 lifecycle task definitions (lines 253-292)
```

**Test files to MODIFY:**
```
tests/test_agent_runner.py    # Remove BudgetConfig import, strip AnthropicAPIBackend test classes (lines 207-627), update AgentRunner tests to remove budget param
tests/test_agent_sdk_backend.py # Remove BudgetConfig import, update execute() calls, remove TestAgentSDKBackendBudgetConfig class
tests/test_sse_events.py      # Remove check_agency_cost_cap mock setup
tests/test_executor.py        # Remove check_agency_cost_cap mock in all test methods (~16 occurrences)
tests/test_session.py         # Remove/update TestWorkflowSessionRecordTurn class (tests record_turn)
```

### Recommended Deletion Order

**Wave 1: Delete leaf modules (no dependents)**
1. `budget.py` -- standalone, only imported by others
2. `backends/anthropic_api.py` -- standalone backend
3. `core/lifecycle.py` -- standalone lifecycle module
4. 3 management commands -- depend only on lifecycle.py
5. `test_budget.py`, `test_data_lifecycle.py` -- test-only files

**Wave 2: Update interfaces**
1. `agent_runner.py` -- remove BudgetConfig from RuntimeBackend Protocol and AgentRunner.run()
2. `backends/agent_sdk.py` -- remove BudgetConfig from execute() signature
3. `backends/__init__.py` -- remove AnthropicAPIBackend lazy import

**Wave 3: Update hub files**
1. `executor.py` -- major surgery: remove budget imports, cost cap check, budget construction, backend selection, on_turn callback
2. `session.py` -- remove record_turn()
3. `metering.py` -- strip threshold alerts and Langfuse event annotations
4. `tasks.py` -- remove 3 lifecycle task definitions

**Wave 4: Fix tests**
1. Update `test_agent_runner.py` -- delete AnthropicAPIBackend tests, update remaining tests
2. Update `test_agent_sdk_backend.py` -- remove budget-related test class
3. Update `test_executor.py` -- remove cost_cap mock from all tests
4. Update `test_sse_events.py` -- remove cost_cap mock
5. Update `test_session.py` -- remove/update record_turn tests

### Pattern: executor.py After Cleanup

After stripping, `_execute_phase` should:
1. Skip informational phases (existing)
2. Get or create agent (existing)
3. Reconcile tools (existing)
4. ~~Pre-flight cost cap check~~ REMOVED
5. Assemble system prompt (existing)
6. ~~Build BudgetConfig~~ REMOVED
7. ~~Select backend (API vs SDK)~~ SIMPLIFIED: always use AgentSDKBackend
8. Create AgentRunner with SDK backend
9. Execute via AgentRunner (without budget param)
10. Handle RunResult (keep completed/error, remove budget_exceeded status handling)
11. Store phase output (existing)

### Pattern: RuntimeBackend Protocol After Cleanup

```python
# Current signature
async def execute(
    self,
    system_prompt: str,
    messages: list[dict],
    tools: list[dict],
    tool_dispatch: Callable,
    budget: BudgetConfig,       # REMOVE
    metering: MeteringCallback,
    agent_id: str,
    on_turn: Callable | None = None,  # REMOVE (turn counting gone)
) -> RunResult:
```

After cleanup:
```python
async def execute(
    self,
    system_prompt: str,
    messages: list[dict],
    tools: list[dict],
    tool_dispatch: Callable,
    metering: MeteringCallback,
    agent_id: str,
) -> RunResult:
```

### Pattern: MeteringCallback After Cleanup

Keep:
- `__init__` (without max_turns, max_cost, on_threshold_alert)
- `from_agency()` (simplified -- just workflow_run_id and agency)
- `on_llm_call()` (keep accumulation, remove threshold checks)
- `on_tool_call()` (keep as-is)
- `flush_to_db()` (keep as-is)
- `get_totals()` (keep as-is)

Remove:
- `_max_turns`, `_max_cost`, `_on_threshold_alert` fields
- Threshold checking logic in `on_llm_call()` (lines 117-140)
- `_annotate_langfuse_event()` method (lines 236-267)

Keep the `from langfuse import get_client` import only if it is used elsewhere in metering.py. After removing `_annotate_langfuse_event`, the `get_client` import in metering.py is unused and should be removed. Langfuse tracing remains in `tracing.py`.

### Session.py Decision (Claude's Discretion)

**Recommendation: Keep session.py, strip only record_turn().**

Reasoning:
- `WorkflowSession` provides `start()`, `checkpoint()`, `end()`, `fail()`, `get_memory()` -- all needed in Phase 4 executor rewrite
- `_metering` is created and managed by WorkflowSession -- executor.py accesses it via `self._session._metering`
- `_memories` dict holds HaznMemory instances per agent -- needed for Phase 5 memory rewiring
- Deleting session.py would force Phase 4 to recreate all this coordination logic
- Only `record_turn()` and `log_conflicts()` are enterprise features. `log_conflicts()` can also stay (harmless, may be useful)

Changes to session.py:
1. Delete `record_turn()` method (lines 140-155)
2. Keep everything else

Changes to executor.py referencing session:
1. Remove `on_turn` callback definition (lines 382-383) and `on_turn=on_turn` kwarg (line 396)

### Turn Count Fields Decision (Claude's Discretion)

**Recommendation: Defer turn_count field removal to Phase 2 migrations.**

Reasoning:
- `WorkflowRun.turn_count` (models.py line 44) and `WorkflowAgent.turn_count` (line 78) are IntegerField with default=0
- Removing fields requires a Django migration
- Phase 2 is explicitly "Django models simplified, clean migrations" (STRP-10)
- Leaving fields with default=0 is harmless -- they just never get incremented
- No runtime code writes to them after record_turn() removal (metering.py writes `turn_count` via flush_to_db, but that is metering turn count, not session turn count -- keep it)

Wait -- `WorkflowAgent.turn_count` is populated by `metering.flush_to_db()` (line 195: `"turn_count": meters["turns"]`). This is metering-level turn tracking, not session-level checkpoint turn counting. This should STAY because it tracks how many LLM calls an agent made, which is useful cost data.

`WorkflowRun.turn_count` is incremented by `session.record_turn()` (line 154). After removing record_turn(), this field is never written. Defer removal to Phase 2.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Finding all import references | Manual grep | `ruff check --select F811,F401` after deletion | Ruff catches unused imports automatically |
| Verifying Django starts cleanly | Manual testing | `python manage.py check --deploy` + `python manage.py showmigrations` | Standard Django verification |
| Finding dead test references | Manual review | `pytest --collect-only 2>&1` | Catches import errors in test collection |

## Common Pitfalls

### Pitfall 1: Cascade Import Errors
**What goes wrong:** Deleting budget.py before removing imports in executor.py, agent_runner.py, agent_sdk.py, test files causes immediate ImportError on any Django management command or test collection.
**Why it happens:** Python resolves imports at module load time. Even unused imports fail if the source module is deleted.
**How to avoid:** Either (a) remove all imports BEFORE deleting the file, or (b) delete file AND fix all imports in the same atomic commit. Use `ruff check --select F811,F401` to find remaining references.
**Warning signs:** `ModuleNotFoundError: No module named 'hazn_platform.orchestrator.budget'` on any command.

### Pitfall 2: BudgetConfig Deeply Embedded in Type Signatures
**What goes wrong:** budget.py deletion seems simple, but BudgetConfig is in: RuntimeBackend Protocol, AgentRunner.run(), AgentSDKBackend.execute(), executor._execute_phase(). Simply deleting the import breaks the Protocol definition itself.
**Why it happens:** BudgetConfig was designed as a cross-cutting concern passed through every layer.
**How to avoid:** Update ALL signatures in a single wave before deleting budget.py. The RuntimeBackend Protocol must be updated first since it is the contract that backends implement.
**Warning signs:** `NameError: name 'BudgetConfig' is not defined` in Protocol or class definitions.

### Pitfall 3: Test Files Reference Deleted Modules
**What goes wrong:** test_agent_runner.py imports AnthropicAPIBackend and BudgetConfig. test_executor.py mocks check_agency_cost_cap. If source files are deleted but tests are not updated, `pytest --collect-only` fails.
**Why it happens:** Test imports are evaluated at collection time, not just at execution time.
**How to avoid:** Update test files in the same wave as source file deletion. Specifically:
- test_agent_runner.py: Delete 5 test classes for AnthropicAPIBackend (TestAnthropicAPIBackendSingleTurn, TestAnthropicAPIBackendMultiTurn, TestAnthropicAPIBackendParallelTools, TestAnthropicAPIBackendBudgetHalt, TestAnthropicAPIBackendMaxTokens, TestAnthropicAPIBackendOnTurn)
- test_agent_sdk_backend.py: Remove TestAgentSDKBackendBudgetConfig class
- test_executor.py: Remove all `check_agency_cost_cap` mock entries (~16 occurrences)
**Warning signs:** `pytest` exits with collection errors.

### Pitfall 4: Executor Backend Selection Leaves Dead Code Path
**What goes wrong:** Removing the `else` branch (AnthropicAPIBackend) but leaving the `if runtime_mode == "agent_sdk"` check means the code still has a conditional that should be unconditional.
**Why it happens:** The executor has `if runtime_mode == "agent_sdk": ... else: (AnthropicAPIBackend)` -- removing the else but keeping the if creates a dead code path where `runtime_mode != "agent_sdk"` falls through with no backend.
**How to avoid:** Replace the entire backend selection block (lines 317-348) with unconditional AgentSDKBackend instantiation. Remove the `HAZN_RUNTIME_MODE` env var check. Remove the module-level `AnthropicAPIBackend = None` sentinel.
**Warning signs:** `UnboundLocalError: local variable 'backend' referenced before assignment` when `HAZN_RUNTIME_MODE` is not set to `agent_sdk`.

### Pitfall 5: Metering Langfuse Import Becomes Unused
**What goes wrong:** After removing `_annotate_langfuse_event()`, the `from langfuse import get_client` at the top of metering.py is unused. Ruff/linters will flag it.
**Why it happens:** The only Langfuse usage in metering.py is the event annotation for budget alerts.
**How to avoid:** Remove `from langfuse import get_client` from metering.py when removing the annotation method. Langfuse tracing remains in `tracing.py` which has its own import.
**Warning signs:** Ruff F401 (unused import) error.

### Pitfall 6: RunResult.status "budget_exceeded" Still Referenced
**What goes wrong:** executor.py handles `result.status == "budget_exceeded"` (lines 408-422). After removing budget enforcement, this status is never produced by AgentSDKBackend, but the handling code remains as dead code.
**Why it happens:** The status enum is implicit (string-based), not enforced by the type system.
**How to avoid:** Remove the `elif result.status == "budget_exceeded"` branch from executor.py. Also remove `budget_halt_reason` from RunResult fields if desired (though it is optional/None by default and harmless).
**Warning signs:** Dead code that never executes but adds confusion.

## Code Examples

### executor.py Backend Selection -- Before and After

**Before (lines 317-348):**
```python
# Select backend based on HAZN_RUNTIME_MODE env var
runtime_mode = os.environ.get("HAZN_RUNTIME_MODE", "api")
if runtime_mode == "agent_sdk":
    global AgentSDKBackend
    if AgentSDKBackend is None:
        from hazn_platform.orchestrator.backends.agent_sdk import AgentSDKBackend
    from hazn_platform.orchestrator import tool_wiring
    router = tool_wiring._ROUTER_SINGLETON
    if router is None:
        from hazn_platform.orchestrator.tool_router import build_tool_registry
        router = build_tool_registry()
    backend = AgentSDKBackend(router=router)
else:
    global AnthropicAPIBackend
    if AnthropicAPIBackend is None:
        from hazn_platform.orchestrator.backends.anthropic_api import AnthropicAPIBackend
    backend = AnthropicAPIBackend()
```

**After:**
```python
# SDK backend is the only execution path
from hazn_platform.orchestrator.backends.agent_sdk import AgentSDKBackend
from hazn_platform.orchestrator import tool_wiring

router = tool_wiring._ROUTER_SINGLETON
if router is None:
    from hazn_platform.orchestrator.tool_router import build_tool_registry
    router = build_tool_registry()
    logger.warning("ToolRouter singleton was None, built fresh for test")
backend = AgentSDKBackend(router=router)
```

### metering.py -- Stripped on_llm_call

**Before:**
```python
def on_llm_call(self, agent_id: str, tokens: int, cost: float) -> None:
    if agent_id not in self._agent_meters:
        self._agent_meters[agent_id] = {"tokens": 0, "cost": 0.0, "turns": 0}
    meter = self._agent_meters[agent_id]
    meter["tokens"] += tokens
    meter["cost"] += cost
    meter["turns"] += 1
    # Check thresholds
    if meter["turns"] >= self._max_turns and self._on_threshold_alert:
        self._on_threshold_alert(agent_id, "max_turns_exceeded")
        self._annotate_langfuse_event("max_turns_exceeded", agent_id, meter["turns"])
    if meter["cost"] >= self._max_cost and self._on_threshold_alert:
        self._on_threshold_alert(agent_id, "max_cost_exceeded")
        self._annotate_langfuse_event("max_cost_exceeded", agent_id, meter["cost"])
```

**After:**
```python
def on_llm_call(self, agent_id: str, tokens: int, cost: float) -> None:
    if agent_id not in self._agent_meters:
        self._agent_meters[agent_id] = {"tokens": 0, "cost": 0.0, "turns": 0}
    meter = self._agent_meters[agent_id]
    meter["tokens"] += tokens
    meter["cost"] += cost
    meter["turns"] += 1
```

### backends/__init__.py -- After Cleanup

```python
"""Runtime backends for AgentRunner.

Re-exports AgentSDKBackend for convenient access::

    from hazn_platform.orchestrator.backends import AgentSDKBackend
"""

from __future__ import annotations


def __getattr__(name: str):
    if name == "AgentSDKBackend":
        from hazn_platform.orchestrator.backends.agent_sdk import AgentSDKBackend
        return AgentSDKBackend
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["AgentSDKBackend"]
```

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| Dual backend (API + SDK) with HAZN_RUNTIME_MODE env var | SDK-only execution | Remove env var check, delete API backend, simplify executor |
| Per-workflow BudgetConfig passed through every layer | No budget enforcement | Remove BudgetConfig from all signatures, simplify Protocol |
| Agency cost caps with monthly rolling window | No cost caps | Remove check_agency_cost_cap call from executor pre-flight |
| Langfuse event annotations for budget alerts | Langfuse for tracing only | Strip _annotate_langfuse_event from metering, keep tracing.py |
| GDPR lifecycle with daily Celery tasks | No lifecycle management | Delete lifecycle module, commands, and tasks |

## Open Questions

1. **RunResult model fields after budget removal**
   - What we know: `budget_halt_reason` field on RunResult becomes unused. `status` value `"budget_exceeded"` is never produced.
   - What's unclear: Should RunResult be cleaned up to remove budget_halt_reason and the budget_exceeded status, or leave them as harmless optional fields?
   - Recommendation: Remove `budget_halt_reason` field from RunResult and the `budget_exceeded` handling from executor.py. Cleaner codebase for Phase 4 executor rewrite.

2. **AgentSDKBackend still references BudgetConfig.max_turns for SDK options**
   - What we know: `agent_sdk.py` line 127 uses `budget.max_turns or 30` to set `ClaudeCodeOptions.max_turns`
   - What's unclear: After removing BudgetConfig, what should max_turns default to?
   - Recommendation: Hardcode `max_turns=30` (current default) or make it a parameter on AgentSDKBackend. Phase 4 will rewrite this entirely.

3. **test_executor.py has ~16 mock entries for check_agency_cost_cap**
   - What we know: Nearly every test method in test_executor.py mocks check_agency_cost_cap
   - What's unclear: Will removing these mocks cause tests to actually call the (now-deleted) function, or will the tests pass because the code path is also removed?
   - Recommendation: Remove the mock entries AND the executor code they mock in the same commit. Do not remove one without the other.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 + pytest-django 4.12.0 + pytest-asyncio >= 0.23.0 |
| Config file | `pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `cd /Users/rizwanqaiser/Work/autonomous/hazn/hazn_platform && uv run pytest tests/ -x --no-header -q` |
| Full suite command | `cd /Users/rizwanqaiser/Work/autonomous/hazn/hazn_platform && uv run pytest tests/ --no-header -q` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| STRP-04 | Anthropic API backend removed, SDK-only path works | unit | `uv run pytest tests/test_agent_sdk_backend.py -x` | Yes (needs update) |
| STRP-05 | Budget enforcement removed, no BudgetConfig in signatures | unit | `uv run pytest tests/test_agent_runner.py tests/test_executor.py -x` | Yes (needs update) |
| STRP-06 | Langfuse tracing works, metering accumulation works | unit | `uv run pytest tests/test_tracing.py tests/test_metering.py -x` | Yes |
| STRP-08 | record_turn removed, session lifecycle still works | unit | `uv run pytest tests/test_session.py -x` | Yes (needs update) |
| STRP-09 | Lifecycle tasks removed, remaining Celery tasks work | unit | `uv run pytest tests/test_orchestrator_tasks.py -x` | Yes (needs update) |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/ -x --no-header -q` (fast: ~5s with --reuse-db)
- **Per wave merge:** `uv run pytest tests/ --no-header -q` (full suite)
- **Phase gate:** Full suite green + `python manage.py check` + `ruff check` before verify

### Wave 0 Gaps
None -- existing test infrastructure covers all phase requirements. Tests need updating (removing deleted references), not creating new test files.

## Sources

### Primary (HIGH confidence)
- Direct codebase inspection of all files listed in CONTEXT.md code_context section
- `pyproject.toml` for dependency declarations and test configuration
- `docker-compose.local.yml` for service definitions (confirmed no Langfuse service)
- Django settings `config/settings/base.py` for Langfuse configuration and Celery beat setup

### Verification Method
- All file paths verified via `Glob` and `Read` tools against actual filesystem
- All line numbers verified via `Read` tool against actual file content
- Import dependency graph traced via `Grep` tool for budget, lifecycle, and anthropic_api references
- Test file references confirmed via `Grep` for BudgetConfig, check_agency_cost_cap, AnthropicAPIBackend patterns

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- direct codebase inspection, no external libraries to research
- Architecture: HIGH -- all files read and verified, deletion map is exact
- Pitfalls: HIGH -- traced every import chain, identified all cascade points

**Research date:** 2026-03-12
**Valid until:** No expiry -- this is codebase-specific research, not library-version-dependent

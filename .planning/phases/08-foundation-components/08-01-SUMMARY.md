---
phase: 08-foundation-components
plan: 01
subsystem: testing, orchestrator
tags: [mock-builders, fixtures, prompt-assembly, tdd, anthropic-api]

# Dependency graph
requires: []
provides:
  - "hazn_platform/testing/ reusable mock module (MockLLMResponse, MockToolDispatcher, fixture loaders)"
  - "PromptAssembler with assemble_prompt() for system prompt construction"
  - "JSON fixtures for Anthropic API tool_use and Agent SDK format"
  - "Agent output fixtures (SEO audit, analytics findings, code generation)"
affects: [08-02, 08-03, 09-agent-runner]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Builder pattern for mock LLM responses (MockLLMResponse().with_text().with_tool_use().build())"
    - "Self-contained orchestrator modules: prompt_assembler avoids Django/Letta import chain by duplicating persona file-reading"
    - "Fixture loaders: load_fixture_json/load_fixture_text for shared test data"
    - "TDD: RED commit (failing tests) followed by GREEN commit (implementation)"

key-files:
  created:
    - "hazn_platform/hazn_platform/testing/__init__.py"
    - "hazn_platform/hazn_platform/testing/mocks.py"
    - "hazn_platform/hazn_platform/testing/fixtures.py"
    - "hazn_platform/hazn_platform/orchestrator/prompt_assembler.py"
    - "hazn_platform/tests/test_testing_infra.py"
    - "hazn_platform/tests/test_prompt_assembler.py"
    - "hazn_platform/tests/fixtures/tool_use_responses.json"
    - "hazn_platform/tests/fixtures/agent_sdk_tool_calls.json"
    - "hazn_platform/tests/fixtures/agent_outputs/seo_audit_report.md"
    - "hazn_platform/tests/fixtures/agent_outputs/analytics_findings.md"
    - "hazn_platform/tests/fixtures/agent_outputs/code_generation.md"
  modified: []

key-decisions:
  - "Duplicated read_agent_persona logic in prompt_assembler to avoid Letta/Django import chain"
  - "Skill frontmatter allowed-tools logged at INFO but not enforced (workflow YAML is authoritative)"
  - "Reference docs: inline under 15KB, size note for larger files (stat-based, not read-based for large files)"
  - "Tests run with DATABASE_URL=sqlite override to avoid Docker dependency"

patterns-established:
  - "Self-contained orchestrator modules: avoid transitive Django imports for testability"
  - "Mock builder pattern: chainable with_text/with_tool_use returning Anthropic API wire format"
  - "Fixture path convention: hazn_platform/tests/fixtures/ with load_fixture_json/load_fixture_text"

requirements-completed: [RUNT-01]

# Metrics
duration: 6min
completed: 2026-03-06
---

# Phase 8 Plan 01: Testing Infrastructure + PromptAssembler Summary

**Reusable testing mock module with builder-pattern LLM responses, fixture loaders, and PromptAssembler that constructs system prompts from agent persona + full SKILL.md content + client context**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-06T12:41:05Z
- **Completed:** 2026-03-06T12:47:37Z
- **Tasks:** 2
- **Files created:** 11

## Accomplishments
- MockLLMResponse builder that constructs Anthropic API assistant messages with chainable with_text/with_tool_use methods
- MockToolDispatcher that registers canned tool results and returns Anthropic-native tool_result format
- Fixture loaders (load_fixture_json, load_fixture_text) pointing at tests/fixtures/ directory
- 5 fixture files: 2 JSON (tool_use_responses, agent_sdk_tool_calls) + 3 agent output markdowns
- PromptAssembler that produces complete system prompts with persona + skills + client context
- Full SKILL.md injection (not truncated) with reference doc size-based handling
- 30 total tests passing without Django setup, LLM calls, or running services

## Task Commits

Each task was committed atomically:

1. **Task 1: Create testing infrastructure** - `d1548c0` (test: RED), `eabc39f` (feat: GREEN)
2. **Task 2: Implement PromptAssembler** - `17682db` (test: RED), `14d9707` (feat: GREEN)

_TDD tasks have two commits each: failing tests then passing implementation._

## Files Created/Modified
- `hazn_platform/hazn_platform/testing/__init__.py` - Re-exports MockLLMResponse, MockToolDispatcher, fixture loaders
- `hazn_platform/hazn_platform/testing/mocks.py` - Builder-pattern mock LLM responses and tool dispatcher
- `hazn_platform/hazn_platform/testing/fixtures.py` - JSON and text fixture loaders for tests/fixtures/
- `hazn_platform/hazn_platform/orchestrator/prompt_assembler.py` - PromptAssembler with assemble_prompt() and _read_skill_content()
- `hazn_platform/tests/test_testing_infra.py` - 14 tests for mock module and fixture loaders
- `hazn_platform/tests/test_prompt_assembler.py` - 16 tests for PromptAssembler (RUNT-01)
- `hazn_platform/tests/fixtures/tool_use_responses.json` - 3 Anthropic API tool_use content blocks
- `hazn_platform/tests/fixtures/agent_sdk_tool_calls.json` - 2 Claude Agent SDK format tool calls
- `hazn_platform/tests/fixtures/agent_outputs/seo_audit_report.md` - Realistic SEO audit report
- `hazn_platform/tests/fixtures/agent_outputs/analytics_findings.md` - Analytics audit findings
- `hazn_platform/tests/fixtures/agent_outputs/code_generation.md` - Agent code artifact output

## Decisions Made
- **Duplicated persona reading:** prompt_assembler has its own `_read_agent_persona()` (5 lines) instead of importing from agent_manager.py, because agent_manager imports `letta_client` at module level which requires Django setup. This keeps prompt_assembler testable without Django.
- **Reference size check uses stat():** For large reference files, we check `ref_file.stat().st_size` instead of reading the entire file, avoiding unnecessary I/O for files that will be skipped.
- **Tests use DATABASE_URL=sqlite override:** The pyproject.toml pytest config requires Django settings. Tests override with SQLite to run without Docker services.
- **Skill frontmatter logged, not enforced:** The `allowed-tools` field in SKILL.md frontmatter is logged at INFO level but not used for tool scoping. Workflow YAML `tools:` field remains authoritative per user decision.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Testing infrastructure (mock module + fixtures) ready for Plans 02 and 03
- PromptAssembler ready for Phase 9 AgentRunner integration
- Key integration point: executor.py line 226-230 placeholder for prompt assembly
- Plans 02 (ToolRouter) and 03 (OutputCollector) can proceed independently

## Self-Check: PASSED

- All 11 created files verified present
- All 4 commit hashes verified in git log
- 30/30 tests pass

---
*Phase: 08-foundation-components*
*Completed: 2026-03-06*

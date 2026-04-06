---
phase: 03-tool-migration
plan: 03
subsystem: tools
tags: [google-analytics, search-console, pagespeed-insights, async, vault, json-output]

# Dependency graph
requires:
  - phase: 03-tool-migration/03-01
    provides: ToolRegistry, stub @tool decorator, build_registry() factory, error return pattern
provides:
  - pull_ga4_data tool: 6 GA4 reports (events, conversions, traffic_sources, landing_pages, devices, countries)
  - query_gsc tool: 5 GSC query groups (top_queries, landing_pages, brand_analysis, cannibalization, weekly_trends)
  - check_pagespeed tool: dual strategy (mobile+desktop) with CWV extraction and opportunity ranking
  - ANALYTICS_TOOLS export list for build_registry()
  - _write_and_summarize helper for JSON-to-file output with lean summary return
  - _get_analytics_credentials helper for Vault service account lookup
affects: [03-04-PLAN, 04-executor-rewrite]

# Tech tracking
tech-stack:
  added: [google-analytics-data (BetaAnalyticsDataClient), google-api-python-client (build), google-auth (service_account)]
  patterns: [vault-credential-per-client-lookup, file-output-with-summary-return, dual-psi-strategy, brand-extraction-from-url]

key-files:
  created:
    - hazn_platform/hazn_platform/orchestrator/tools/analytics.py
    - hazn_platform/tests/test_tools_analytics.py
  modified:
    - hazn_platform/hazn_platform/orchestrator/tools/__init__.py

key-decisions:
  - "Patchable _OUTPUT_BASE module variable for test isolation instead of dependency injection"
  - "Graceful skip in _aggregate_weekly for invalid date values (handles mock responses and real-world date parse errors)"
  - "Brand name extraction from site_url domain for GSC brand/non-brand analysis (no separate brand_terms parameter)"
  - "httpx.AsyncClient for PageSpeed API (consistent with existing web.py pattern)"

patterns-established:
  - "Analytics credential pattern: VaultCredential.objects.get(end_client_id=X, service_name=Y) -> read_secret -> service_account.Credentials"
  - "File output pattern: _write_and_summarize writes full JSON to /tmp/hazn-audit/{client}/{timestamp}/ and returns summary dict"
  - "PSI dual strategy: run mobile + desktop in sequence, extract CWV + opportunities per strategy"

requirements-completed: [TOOL-03, TOOL-04, TOOL-05]

# Metrics
duration: 12min
completed: 2026-03-12
---

# Phase 3 Plan 3: Full-depth Analytics Tools (GA4, GSC, PageSpeed) Summary

**3 analytics tools with full-depth data collection: 6 GA4 reports, 5 GSC query groups, dual-strategy PageSpeed with CWV extraction, all writing JSON to /tmp/ and returning lean summaries**

## Performance

- **Duration:** 12 min
- **Started:** 2026-03-12T18:06:08Z
- **Completed:** 2026-03-12T18:18:08Z
- **Tasks:** 2
- **Files created:** 2, modified: 1

## Accomplishments
- pull_ga4_data collects 6 comprehensive GA4 Data API reports (events, conversions, traffic sources, landing pages, devices, countries) via BetaAnalyticsDataClient
- query_gsc collects 5 GSC query groups with full post-processing: top queries, landing pages, brand vs non-brand analysis, keyword cannibalization detection, and weekly trend aggregation
- check_pagespeed runs dual strategy (mobile + desktop) via PageSpeed Insights API, extracting Core Web Vitals, performance scores, and top optimization opportunities
- All tools write full JSON to /tmp/hazn-audit/{client_id}/{timestamp}/ and return only summary + file path to keep agent context window lean
- build_registry() now registers all tool modules including analytics, completing the analytics migration from MCP servers to Python function tools
- Full TDD with 20 tests passing: 6 GA4 + 6 GSC + 7 PageSpeed + 1 export verification

## Task Commits

Each task was committed atomically:

1. **Task 1: Create GA4 and GSC full-depth tools** - `db22e24` (test/feat)
2. **Task 2: Create PageSpeed tool and register all analytics tools** - `e15bb41` (feat)

## Files Created/Modified
- `hazn_platform/orchestrator/tools/analytics.py` - 3 analytics tools + shared helpers (_get_analytics_credentials, _write_and_summarize, _run_ga4_report, _query_search_analytics, _detect_cannibalization, _aggregate_weekly, _extract_pagespeed_data, _extract_brand_from_url)
- `tests/test_tools_analytics.py` - 20 tests across TestGA4Tool (6), TestGSCTool (6), TestPageSpeedTool (7), TestAnalyticsToolsExport (1)
- `hazn_platform/orchestrator/tools/__init__.py` - Added ANALYTICS_TOOLS registration in build_registry()

## Decisions Made
- Used patchable `_OUTPUT_BASE` module variable for test isolation instead of passing output directory as parameter -- keeps tool API clean while enabling test redirection to tmp_path
- Made `_aggregate_weekly` gracefully skip rows with invalid date values instead of failing -- handles both mock responses in tests and potential real-world data quality issues
- Extracted brand name from site_url domain (e.g., "example" from "sc-domain:example.com") for GSC brand/non-brand analysis rather than requiring a separate brand_terms parameter -- simpler API for the agent
- Used httpx.AsyncClient for PageSpeed Insights API, consistent with the existing web.py tool pattern

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed _aggregate_weekly date parsing error**
- **Found during:** Task 1 (GSC tool implementation)
- **Issue:** Weekly aggregation function crashed with ValueError when mock responses contained non-date values in the date dimension
- **Fix:** Added try/except around datetime.strptime to gracefully skip rows with invalid date values
- **Files modified:** hazn_platform/orchestrator/tools/analytics.py
- **Verification:** All GSC tests pass including file output tests
- **Committed in:** db22e24 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix)
**Impact on plan:** Auto-fix necessary for robustness. No scope creep.

## Issues Encountered
- Google API libraries (google-analytics-data, google-api-python-client, google-auth) were not listed explicitly in pip list output but were importable from the venv -- they are bundled as transitive dependencies
- Django test settings require DATABASE_URL environment variable -- tests run with `DATABASE_URL=sqlite:///test.db` for local execution outside Docker

## User Setup Required

None - no external service configuration required. Google API credentials are fetched at runtime from Vault via VaultCredential model.

## Next Phase Readiness
- All 3 analytics tools are ready for use by the executor in Phase 4
- Plan 03-04 can now proceed with MCP server cleanup (deleting analytics_server.py and data_tools.py)
- analytics.py ANALYTICS_TOOLS list is registered in build_registry(), completing the tool migration for analytics domain

## Self-Check: PASSED

- All 3 files verified present on disk (analytics.py, test_tools_analytics.py, __init__.py)
- Commit db22e24 (Task 1) verified in git log
- Commit e15bb41 (Task 2) verified in git log
- 20/20 tests passing

---
*Phase: 03-tool-migration*
*Completed: 2026-03-12*

---
phase: 04-mcp-tool-servers-observability
plan: 02
subsystem: mcp
tags: [ga4, gsc, pagespeed, google-analytics, search-console, core-web-vitals, service-account, fastmcp]

requires:
  - phase: 01-infrastructure-foundation
    provides: "VaultCredential model, Vault read_secret helper, Docker compose"
  - phase: 02-memory-layer
    provides: "FastMCP server pattern (hazn_memory_server.py template)"
provides:
  - "mcp-analytics FastMCP server with pull_ga4_data, query_gsc, check_pagespeed tools"
  - "Service account auth pattern for Google APIs via Vault"
  - "PageSpeed free-tier graceful fallback pattern"
affects: [05-workflow-agents, 06-frontend-dashboard]

tech-stack:
  added: [google-analytics-data, google-api-python-client, google-auth]
  patterns: [service-account-auth-via-vault, psi-free-tier-fallback, agency-level-credential-lookup]

key-files:
  created:
    - hazn_platform/hazn_platform/mcp_servers/analytics_server.py
  modified:
    - hazn_platform/tests/test_mcp_analytics_server.py
    - hazn_platform/pyproject.toml
    - hazn_platform/uv.lock

key-decisions:
  - "Google APIs use service_account.Credentials.from_service_account_info (not OAuth2 interactive flow) for headless agent execution"
  - "PSI API key is agency-level (end_client__isnull=True) not client-level, enabling shared rate limit across all clients"
  - "google-analytics-data, google-api-python-client, google-auth added as project dependencies"

patterns-established:
  - "Service account auth pattern: VaultCredential lookup -> read_secret -> Credentials.from_service_account_info"
  - "Agency-level credential pattern: VaultCredential(agency_id=..., end_client__isnull=True) for shared API keys"
  - "Graceful fallback: try VaultCredential.DoesNotExist -> return None -> call API without key"

requirements-completed: [MCP-04, MCP-05]

duration: 11min
completed: 2026-03-06
---

# Phase 4 Plan 2: MCP Analytics Server Summary

**Combined mcp-analytics FastMCP server with GA4, GSC, and PageSpeed tools using service account auth from Vault**

## Performance

- **Duration:** 11 min
- **Started:** 2026-03-06T03:22:59Z
- **Completed:** 2026-03-06T03:34:00Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Built mcp-analytics server with 3 tools: pull_ga4_data, query_gsc, check_pagespeed
- GA4 and GSC use service account auth via Credentials.from_service_account_info (not OAuth2)
- PageSpeed gracefully falls back to free tier when no API key credential exists in Vault
- Full test coverage with 9 tests mocking all Google API and Vault interactions

## Task Commits

Each task was committed atomically (TDD: RED then GREEN):

1. **Task 1: Build mcp-analytics GA4 and GSC tools**
   - `7229188` (test) - RED: failing tests for GA4 and GSC tools
   - `a9b36b2` (feat) - GREEN: GA4 and GSC implementation with service account auth
2. **Task 2: Add PageSpeed tool to mcp-analytics server**
   - `b035364` (test) - RED: failing tests for PageSpeed tool
   - `f615db4` (feat) - GREEN: PageSpeed implementation with free-tier fallback

## Files Created/Modified
- `hazn_platform/hazn_platform/mcp_servers/analytics_server.py` - FastMCP server with GA4, GSC, and PageSpeed tools (399 lines)
- `hazn_platform/tests/test_mcp_analytics_server.py` - Unit tests for all 3 MCP tools with mocked Google clients (539 lines)
- `hazn_platform/pyproject.toml` - Added google-analytics-data, google-api-python-client, google-auth dependencies
- `hazn_platform/uv.lock` - Lock file updated with new Google API dependencies

## Decisions Made
- **Service account auth over OAuth2:** Google APIs use `service_account.Credentials.from_service_account_info()` instead of interactive OAuth2 flow, enabling headless agent execution without user interaction
- **Agency-level PSI API key:** PageSpeed API key credential is stored at agency level (`end_client__isnull=True`), shared across all clients under the agency
- **Google SDK as project dependencies:** Added `google-analytics-data`, `google-api-python-client`, `google-auth` to pyproject.toml and rebuilt Docker image

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Installed Google API dependencies in Docker image**
- **Found during:** Task 1 (GA4 and GSC implementation)
- **Issue:** google-analytics-data, google-api-python-client, google-auth not installed in Docker container, causing ImportError
- **Fix:** Added dependencies to pyproject.toml, ran `uv lock`, rebuilt Docker image
- **Files modified:** hazn_platform/pyproject.toml, hazn_platform/uv.lock
- **Verification:** Tests pass in Docker container
- **Committed in:** a9b36b2 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Required dependency installation for Google SDK. No scope creep.

## Issues Encountered
- Docker disk space exhaustion during image rebuild required `docker system prune` to free 10.9GB before successful rebuild

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- mcp-analytics server ready for integration with analytics audit workflow agents
- Service account credentials need to be provisioned in Vault per client for GA4/GSC and per agency for PageSpeed
- Combined server pattern (multiple related tools in one server) established for future MCP servers

## Self-Check: PASSED

- [x] analytics_server.py exists (399 lines, min 180)
- [x] test_mcp_analytics_server.py exists (539 lines, min 100)
- [x] 04-02-SUMMARY.md exists
- [x] Commit 7229188 found (test RED: GA4/GSC)
- [x] Commit a9b36b2 found (feat GREEN: GA4/GSC)
- [x] Commit b035364 found (test RED: PageSpeed)
- [x] Commit f615db4 found (feat GREEN: PageSpeed)
- [x] All 9 tests pass

---
*Phase: 04-mcp-tool-servers-observability*
*Completed: 2026-03-06*

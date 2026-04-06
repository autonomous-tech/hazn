---
phase: 01-infrastructure-foundation
plan: 02
subsystem: database
tags: [django-models, pgvector, uuid-pk, fk-cascade, vectorfield, domain-split-apps, pytest-django]

# Dependency graph
requires:
  - phase: 01-infrastructure-foundation (plan 01)
    provides: Docker Compose stack with Postgres 17 + pgvector, Django 5.2 project
provides:
  - 9 L2/L3 Django models across 3 domain-split apps (core, marketing, content)
  - pgvector VectorExtension enabled via Django migration
  - VectorField(1536) on BrandVoice and ApprovedCopy for semantic search
  - Agency -> EndClient 1:many hierarchy with FK cascade
  - BrandVoice append-only versioning with unique active constraint per client
  - VaultCredential storing vault paths (not secrets)
  - Admin interface for all 9 models
affects: [01-03-PLAN, 02-01, 02-02, 03-01, 03-02]

# Tech tracking
tech-stack:
  added: [pgvector-django-vectorfield, pytest-django-integration-tests]
  patterns: [uuid-primary-keys, domain-split-django-apps, append-only-versioning-with-active-constraint, vault-path-not-secret-pattern, conditional-unique-constraint]

key-files:
  created:
    - hazn_platform/core/models.py
    - hazn_platform/core/admin.py
    - hazn_platform/core/apps.py
    - hazn_platform/core/migrations/0001_initial.py
    - hazn_platform/marketing/models.py
    - hazn_platform/marketing/admin.py
    - hazn_platform/marketing/apps.py
    - hazn_platform/marketing/migrations/0001_initial.py
    - hazn_platform/content/models.py
    - hazn_platform/content/admin.py
    - hazn_platform/content/apps.py
    - hazn_platform/content/migrations/0001_initial.py
    - tests/test_models.py
  modified:
    - config/settings/base.py

key-decisions:
  - "3 domain-split apps (core, marketing, content) instead of single monolithic app for separation of concerns"
  - "VectorExtension() in core's initial migration ensures pgvector is available before content migration runs"
  - "BrandVoice uses conditional UniqueConstraint (is_active=True) for append-only versioning pattern"
  - "VaultCredential stores vault_secret_id path, never raw secret content"

patterns-established:
  - "UUID primary keys: all models use UUIDField(primary_key=True, default=uuid.uuid4, editable=False)"
  - "Domain-split apps: core (hierarchy), marketing (SEO/campaigns), content (brand voice/copy with embeddings)"
  - "Append-only versioning: new versions are new rows, only one active per client via conditional constraint"
  - "VectorField(1536): pgvector embedding columns for semantic search on BrandVoice and ApprovedCopy"

requirements-completed: [INFRA-02]

# Metrics
duration: 4min
completed: 2026-03-05
---

# Phase 1 Plan 2: Domain Models Summary

**9 Django models across 3 domain-split apps (core, marketing, content) with pgvector VectorField(1536), UUID PKs, FK cascade hierarchy, and append-only BrandVoice versioning**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-05T08:37:32Z
- **Completed:** 2026-03-05T08:41:41Z
- **Tasks:** 1 (TDD: RED + GREEN)
- **Files modified:** 14

## Accomplishments
- 9 models across 3 Django apps implementing the full L2/L3 data schema
- pgvector VectorExtension enabled via core migration, VectorField(1536) on BrandVoice and ApprovedCopy
- BrandVoice unique active constraint enforces one active voice per client (append-only versioning)
- All FK relationships: Agency->EndClient CASCADE, Campaign->Decision SET_NULL, Campaign->ApprovedCopy SET_NULL
- 19 integration tests covering CRUD, FK cascade, unique constraints, VectorField nullable
- Django admin registrations for all 9 models

## Task Commits

Each task was committed atomically (TDD pattern):

1. **Task 1 RED: Failing tests for 9 domain models** - `aeac34d` (test)
2. **Task 1 GREEN: Implement 9 models with pgvector and migrations** - `8474e03` (feat)

_Note: No REFACTOR commit needed -- code is clean and well-organized from GREEN phase._

## Files Created/Modified
- `hazn_platform/core/models.py` - Agency, EndClient, VaultCredential models with UUID PKs
- `hazn_platform/core/admin.py` - Admin registrations for core models
- `hazn_platform/core/apps.py` - CoreConfig with name="hazn_platform.core"
- `hazn_platform/core/migrations/0001_initial.py` - VectorExtension + core model tables
- `hazn_platform/marketing/models.py` - Keyword, Audit, Campaign, Decision models
- `hazn_platform/marketing/admin.py` - Admin registrations for marketing models
- `hazn_platform/marketing/apps.py` - MarketingConfig with name="hazn_platform.marketing"
- `hazn_platform/marketing/migrations/0001_initial.py` - Marketing model tables
- `hazn_platform/content/models.py` - BrandVoice, ApprovedCopy with VectorField(1536)
- `hazn_platform/content/admin.py` - Admin registrations for content models
- `hazn_platform/content/apps.py` - ContentConfig with name="hazn_platform.content"
- `hazn_platform/content/migrations/0001_initial.py` - Content model tables with vector columns
- `config/settings/base.py` - Added 3 apps to INSTALLED_APPS
- `tests/test_models.py` - 19 integration tests for all 9 models

## Decisions Made
- **3 domain-split apps**: core (Agency/EndClient/VaultCredential), marketing (Keyword/Audit/Campaign/Decision), content (BrandVoice/ApprovedCopy) -- matches research recommendation for separation of concerns
- **VectorExtension in core migration**: Placed in core's 0001_initial.py (first to run) so pgvector extension is available when content migration creates VectorField columns
- **Conditional UniqueConstraint for BrandVoice**: `UniqueConstraint(fields=["end_client", "is_active"], condition=Q(is_active=True))` allows multiple inactive versions while enforcing one active per client
- **VaultCredential nullable FKs**: Both agency and end_client FKs are nullable to support global credentials not tied to a specific agency or client

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required. Models and migrations run within existing Docker Compose stack.

## Next Phase Readiness
- All 9 models are in place with migrations applied -- ready for Plan 01-03 (Vault/Letta client modules and seed data)
- Ready for Phase 2 (Memory Layer) which reads/writes these tables via HaznMemory abstraction
- Admin interface available at localhost:8001/admin/ for manual data inspection

## Self-Check: PASSED

- All 14 key files verified present on disk
- Both task commits (aeac34d, 8474e03) verified in git log
- 19/19 integration tests pass
- pgvector extension confirmed in hazn_platform database
- All 3 migrations applied (core, marketing, content)

---
*Phase: 01-infrastructure-foundation*
*Completed: 2026-03-05*

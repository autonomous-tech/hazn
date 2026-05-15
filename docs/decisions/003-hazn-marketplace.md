# 003 — Hazn as a plugin marketplace

**Date:** 2026-05-15
**Status:** Approved design, ready for implementation plan
**Authors:** Abdullah Abid (with Claude)
**Stakeholders:** Rizwan Qaiser, Hira Bahalim (first non-author user)

---

## Context

Hazn was consolidated on 2026-05-15 (v0.3.x) from five scattered `.hazn/` installs into a single Claude Code plugin. That fixed drift but produced one fat plugin holding 47 skills across wildly different jobs (B2B websites, NGO websites, Shopify revenue audits, blog content pipelines, analytics audits, client deliverables). Every change ships everything.

Two direct triggers for restructuring:

1. **2026-05-14 "Shopify Audits" meeting** — Hira reviewed the Nanit audit outputs. Abdullah proposed pulling the Shopify audit out into its own plugin so it can be maintained cleanly. Action items: Riz to organize the repo within 1–2 weeks; Abdullah to give feedback on structure within a week. Working session scheduled 2026-05-15 10am–12pm.
2. **2026-05-15 "Biz Sprint Review"** — Riz: *"Shopify audit output is inconsistent and I want to organize it into a single source of truth so it's usable by Hira (lead gen), Ryan (sales), the dev team (execution), and the marketing team (one-pagers)."* One audit run has at least four distinct consumer faces.

The earlier `autonomous-claude-plugins` marketplace failed because it grew too fast and ended up managing multiple versions of the same content. The fix is not to avoid a marketplace — it is to define plugin granularity and shared-asset policy up front, so duplication can't accumulate.

## Goals

In priority order:

1. **Easy team deployment** with per-plugin auto-update across consumer repos.
2. **Easy maintenance** with a built-in feedback loop from any team member back into the canonical repo.
3. **Clear plugin ontology** — what counts as a plugin, where shared things live, how cross-cutting concerns are organized.

## Non-goals

- Big-bang rewrite. Migration is staged in phases (§Migration).
- Public marketplace publication. Repo stays private (`autonomous-tech/hazn`, `UNLICENSED`). Individual plugins may be open-sourced later as separate decisions.
- A/B prompt-eval automation. The May 14 "one-variable-at-a-time" discipline lives in PR review, not in tooling. Eval automation is a separate future concern.
- Rebranding. "Hazn" stays the marketplace name and the runtime plugin name.

## Design decisions

### D1. Plugin granularity = job-to-be-done

One plugin = one customer-facing offering. Examples (current and future): `shopify-revenue-audit`, `b2b-website`, `ngo-website`, `analytics-audit`, `seo-content`. Each plugin owns its complete pipeline — input handling, intermediate skills, agents, workflow graph, and deliverable templates — and ships its own version independently.

Rejected alternatives:
- **Functional capability** (one `audits` plugin holding shopify + analytics + sitehealth): would split a natural unit of work across multiple plugins. The brixton audit output (`recon/` → `modules/` → `synthesis/` + `red-team/` → `1-pager.html`/`index.html`/`BUILD-BRIEF.md`) is one deliverable; the plugin should match that shape.
- **Atomic skill plugins** (each skill its own micro-plugin): npm-style composability without npm-style tooling. Dependency graph would be painful to manage.

### D2. Shared assets = `hazn` runtime plugin (always installed)

Cross-cutting things — brand configs, design-system references, deliverable renderers, generic red-team skills — live in a single `hazn` plugin that is always installed alongside any job plugin. This is the marketplace's runtime kernel.

**Inclusion criteria** for `hazn` (all three must hold):

1. **Used by ≥2 job plugins today** (not "could be reused someday"). Single-plugin assets stay in that plugin.
2. **Stable shape across job plugins** — same inputs/outputs regardless of caller. A renderer (brand + content → HTML) is stable. An "audit summarizer" tuned for Shopify revenue is not.
3. **Documented interface** — named skill, expected inputs, expected outputs. Anything that does not fit a documented interface stays in the consuming plugin.

These criteria are a maintenance discipline, not a wishlist. The risk in D2 is `hazn` becoming the new fat plugin; the criteria are the guardrail.

Rejected alternatives:
- **Marketplace-root shared folders** (`hazn/brands/` outside any plugin): plugins can't resolve paths outside their own root via `${CLAUDE_PLUGIN_ROOT}`. Brittle.
- **Self-contained, accept duplication**: this is exactly what failed in `autonomous-claude-plugins`. Rejected.
- **Cross-cutters as their own opt-in job plugins**: would require every job plugin to declare 3–4 sibling deps. More moving parts, more "is X installed?" checks.

### D3. Command namespacing = plugin-level only

Claude Code namespaces commands by plugin name. We use that and no second layer. Commands look like:

- `/hazn:feedback`, `/hazn:doctor`, `/hazn:help` — from the runtime plugin
- `/shopify-revenue-audit:run`, `/shopify-revenue-audit:rerun-module 3`, `/shopify-revenue-audit:one-pager` — from the job plugin
- `/b2b-website:strategy`, `/b2b-website:ux`, `/b2b-website:dev` — future
- `/ngo-website:strategy`, etc. — future

No `/hazn:shopify-revenue-audit:run` double-prefixing.

### D4. Feedback loop = `/hazn:feedback` opens a draft PR

Single command in the runtime plugin. Auto-detects context (last plugin invoked, skill/template/agent that produced the offending output, run artifact paths). Asks the user three questions: what's wrong, what should it do instead, fix-or-observation. Creates a branch on the local hazn checkout, applies the fix if concrete, commits with run context, opens a draft PR via `gh pr create`.

Fallback: if no local hazn checkout is found at the configured path, opens a GitHub issue with the same body instead.

PR labels for triage: one label per plugin, plus `severity:critical` / `severity:nice-to-have`, plus `type:fix` / `type:observation`.

The maintainer (Abdullah or Rizwan) reviews, optionally re-runs the test case in the PR body, merges, and decides whether to bump the affected plugin's version.

### D5. Deploy = ai-dev-skills marketplace pattern, mirrored

`hazn/.claude-plugin/marketplace.json` lists every plugin with name, source path, version, category, tags. Same shape as `ai-dev-skills/.claude-plugin/marketplace.json`.

Consumer repos get a `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "hazn": { "source": { "source": "github", "repo": "autonomous-tech/hazn" } }
  },
  "enabledPlugins": {
    "hazn@hazn": true,
    "shopify-revenue-audit@hazn": true,
    "hazn-deliverables@hazn": true
  }
}
```

When a team member trusts the repo, Claude Code prompts to install the marketplace plus enabled plugins. `hazn@hazn` (runtime) is always in `enabledPlugins` — that is how D2's "always installed" is enforced operationally.

Auto-update: `/plugin marketplace update hazn` pulls latest from GitHub. Each plugin's `version` bumps independently. Bumping `shopify-revenue-audit@1.4.0` does not re-ship `ngo-website`.

Distribution: GitHub, private, no public registry. New consumer repos get a copy-pasteable `.claude/settings.json` snippet in the README — no `/hazn:bootstrap` command (decided against on simplicity grounds).

## Repository layout

```
hazn/                                       ← marketplace repo
├── .claude-plugin/
│   └── marketplace.json                    ← lists every plugin, per-plugin version + tags
├── .claude/
│   └── settings.json                       ← marketplace-self auto-discovery (dev convenience)
├── plugins/
│   ├── hazn/                               ← runtime plugin, always installed
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/
│   │   │   ├── editorial-warmth-audit-renderer/
│   │   │   ├── audit-red-team-baseline/
│   │   │   ├── audit-red-team-uplifts/
│   │   │   ├── audit-red-team-cfo/
│   │   │   ├── audit-red-team-domain-check/
│   │   │   ├── frontend-design/
│   │   │   └── hazn-orchestrator/
│   │   ├── commands/
│   │   │   ├── feedback.md                 ← /hazn:feedback
│   │   │   ├── doctor.md                   ← /hazn:doctor
│   │   │   └── help.md                     ← /hazn:help
│   │   ├── brands/                         ← brand configs (autonomous.json + per-client)
│   │   ├── references/                     ← editorial-warmth-v2, design tokens
│   │   ├── CHANGELOG.md
│   │   └── README.md
│   ├── shopify-revenue-audit/              ← job plugin (Q3 focus, extracted first)
│   │   ├── .claude-plugin/plugin.json
│   │   ├── commands/{run,rerun-module,one-pager}.md
│   │   ├── skills/
│   │   │   ├── shopify-revenue-audit/      ← orchestrator skill
│   │   │   ├── module-1-ai-discovery/
│   │   │   ├── module-2-search-catalog/
│   │   │   ├── module-3-conversion/
│   │   │   └── module-4-technical/
│   │   ├── agents/{crawler,infra-probe,pagespeed,synthesis-lead,revenue-calculator,quick-wins-ranker,fact-checker}.md
│   │   ├── workflows/revenue-audit.yaml
│   │   ├── templates/{one-pager,deep-dive,build-brief,outreach-email,outreach-linkedin}.tmpl
│   │   ├── references/{agent-teams-playbook,revenue-leak-calculator,benchmarks,canonical-examples}.md
│   │   ├── CHANGELOG.md
│   │   └── README.md
│   ├── hazn-deliverables/                  ← Phase 2
│   │   ├── skills/{case-study,sow,project-plan}/
│   │   └── ...
│   └── hazn-legacy/                        ← holding pen for unextracted skills, drained over Phase 3+
│       └── ...
├── docs/
│   ├── decisions/                          ← this file and successors
│   └── ...
├── CONTRIBUTING.md
└── README.md                               ← marketplace overview + plugin catalog
```

## Plugin inventory

| Plugin | Purpose | Phase | Initial version |
|---|---|---|---|
| `hazn` | Runtime: shared renderers, red-team patterns, brand configs, design tokens, `feedback`/`doctor`/`help` commands, orchestrator skill | 1 | 1.0.0 |
| `shopify-revenue-audit` | 4-wave Shopify revenue audit pipeline, 3 deliverable formats (1-pager / deep-dive / build-brief) plus outreach assets | 1 | 1.0.0 |
| `hazn-deliverables` | Cross-engagement client deliverables: case-study, sow, project-plan | 2 | 1.0.0 |
| `hazn-legacy` | Temporary holding pen for unextracted content from v0.3.2 | 0 (created), drained 3+ | 0.3.2 → 0.x.x |
| `b2b-website` | Future job plugin | 3+ | — |
| `ngo-website` | Future job plugin | 3+ | — |
| `analytics-audit` | Future job plugin | 3+ | — |
| `seo-content` | Future job plugin | 3+ | — |

## Cross-plugin interface contract

Job plugins consume `hazn` only through three documented surfaces. No `../hazn/...` path imports.

1. **Named skill invocation** — e.g. `shopify-revenue-audit` calls `audit-red-team-baseline` by name during Wave 3. Claude Code resolves the skill across installed plugins.
2. **Named command invocation** — e.g. a workflow step calls `editorial-warmth-audit-renderer` (skill) or a future renderer command from `hazn`.
3. **Brand config lookup** — job plugins read `brands/<slug>.json` from the `hazn` plugin root via the canonical path injected at runtime. The brand JSON schema is documented in `plugins/hazn/references/brand-schema.md` (to be authored as part of Phase 1).

`/hazn:doctor` verifies (a) `hazn` is installed, (b) each enabled job plugin can resolve its declared dependencies on `hazn` skills, (c) the configured local hazn checkout exists (used by `/hazn:feedback`).

## Migration

Each phase is its own PR. If a phase breaks, the previous phase remains a working marketplace.

### Phase 0 — Marketplace skeleton (≈1 day)

- Convert `.claude-plugin/plugin.json` → `.claude-plugin/marketplace.json`.
- Move all current content (skills/, agents/, commands/, workflows/, brands/, references/, templates/) into `plugins/hazn-legacy/`. Pure nesting, no restructuring.
- `marketplace.json` lists one plugin: `hazn-legacy@0.4.0`.
- Update `autonomous-proposals/.claude/settings.json` to install `hazn-legacy@hazn` from the marketplace.
- Verify: existing `/hazn:audit`, `/hazn:website`, etc. continue to work, just sourced from a marketplace install.
- Repo version → `0.4.0`.

### Phase 1 — Extract `hazn` runtime + `shopify-revenue-audit` (≈3 days, Friday May 15 working session)

- Create `plugins/hazn/` with the contents listed in §Repository layout.
- Create `plugins/shopify-revenue-audit/` with the file map in §Repository layout.
- Author `commands/feedback.md`, `commands/doctor.md`, `commands/help.md` in `plugins/hazn/`.
- Author `plugins/hazn/references/brand-schema.md` documenting the interface used by job plugins.
- **Delete `shopify-cro-audit`** — superseded by `shopify-revenue-audit` (per Abdullah, Riz confirmed 2026-05-15).
- Move extracted files OUT of `hazn-legacy` (do not duplicate).
- Update `autonomous-proposals/.claude/settings.json` to install `hazn@hazn`, `shopify-revenue-audit@hazn`, and `hazn-legacy@hazn` (kept until drained). `hazn-deliverables@hazn` is added in Phase 2's settings update.
- **Parity test**: rerun the Nanit audit through the new plugin. Diff against `audits/nanit-revenue-audit-2026-05-13/`. Resolve any unintended drift before merging.
- Add temporary alias commands in `hazn-legacy` so `/hazn-legacy:audit` still works during transition; document the canonical replacement (`/shopify-revenue-audit:run`).
- Versions: `shopify-revenue-audit@1.0.0`, `hazn@1.0.0`, repo `1.0.0`.

### Phase 2 — Extract `hazn-deliverables` (≈1 day, next week)

- Move `case-study`, `sow`, `project-plan` skills from `hazn-legacy` into `plugins/hazn-deliverables/`.
- Update consumer `.claude/settings.json` files to enable it.
- `hazn-deliverables@1.0.0`.

### Phase 3+ — Drain `hazn-legacy` (ongoing, no deadline)

- Extract `b2b-website`, `ngo-website`, `analytics-audit`, `seo-content` incrementally as their owners pick up work in those areas.
- Each extraction follows the Phase 1 pattern: create plugin, move files, parity-test against existing outputs.
- When `hazn-legacy` is empty, delete it and ship `hazn@2.0.0` as the cleanup release.

## Operational defaults

- **Local hazn checkout path** (used by `/hazn:feedback`): `~/repos/autonomous-tech/hazn`. Documented in README; overridable via plugin config.
- **Per-plugin CHANGELOG** from day 1: `plugins/<name>/CHANGELOG.md`. Cheap and makes update notifications meaningful.
- **Versioning**: semantic. Major bump = breaking interface change (renamed skill, removed command, changed brand-config schema). Minor = additive. Patch = prompt/template refinement or bugfix.

## Acceptance criteria for Phase 1 merge

- Hira can install the marketplace in her workspace and run `/shopify-revenue-audit:run <domain>` from `autonomous-proposals` without prior setup beyond a trust prompt.
- Nanit audit rerun under the new plugin produces output substantively equivalent to `audits/nanit-revenue-audit-2026-05-13/` (deliberate changes documented, accidental drift fixed).
- `/hazn:feedback` opens a draft PR on a real test change, with PR body containing the auto-detected context (plugin, skill, output snippet, test case).
- `/hazn:doctor` correctly reports (a) `hazn` install status, (b) each enabled job plugin's dep-resolution, (c) local checkout presence.
- `shopify-cro-audit` is removed; no references to it remain in repo.
- `autonomous-proposals/.claude/settings.json` updated and tested by a second team member (not the author).

## Open questions for the working session

- **Brand-config schema** — exact JSON shape consumed by `editorial-warmth-audit-renderer`. Today's `brands/autonomous.json` is the canonical example; we document it as the schema during Phase 1.
- **Workflow yaml format** — today's `workflows/*.yaml` are an ad-hoc dependency-graph format. Decide whether to keep as-is or formalize during Phase 1 (recommend keep as-is; formalize only when a second job plugin needs them).
- **`hazn-orchestrator` skill scope** — does it route across all installed plugins generically (preferred), or is it Shopify-audit-aware? Recommend generic, with plugin-specific routing tables in each plugin's `references/`.

## Risks

- **`hazn` runtime drifts toward fat-plugin** — mitigated by D2's three-clause inclusion criterion, enforced in PR review.
- **`hazn-legacy` is never drained** — consumers keep using legacy commands forever. Mitigation: track Phase 3 extractions as commitments, not aspirations; revisit at quarterly planning.
- **Feedback PRs accumulate without triage** — `/hazn:feedback` makes filing trivial; if no one merges, the canonical repo becomes a graveyard. Mitigation: weekly maintainer pass (Abdullah/Riz), or assign per-plugin owners as plugins are extracted.
- **Auto-update breaks live work** — a buggy `shopify-revenue-audit@1.4.0` could break Hira mid-audit. Mitigation: `enabledPlugins` can pin versions (`"shopify-revenue-audit@hazn": "1.3.x"`); document the pinning option.

## References

- `2026-05-14 Shopify Audits` meeting (Circleback id `3HvIKaoUJK9E8NgjlFjDP`)
- `2026-05-15 Biz Sprint Review` meeting (Circleback id `PGfam1BVZrvhWXcioOWsN`)
- `ai-dev-skills` repo — marketplace structure reference (`autonomous-tech/ai-dev-skills`)
- `autonomous-proposals/audits/brixton-revenue-audit-2026-05-13/` — canonical job-plugin output shape
- `autonomous-proposals/audits/nanit-revenue-audit-2026-05-13/` — Phase 1 parity test target
- Today's hazn `CONTRIBUTING.md` — single-source policy this design extends

# Contributing to Hazn

Hazn is an installable Claude Code plugin. **This repo is the single source of truth.** Do not fork skills, agents, commands, or workflows into consumer repos.

## How to use Hazn

Install the plugin into your Claude Code workspace:

```bash
claude plugin install /path/to/repos/products/hazn
```

After install, commands are namespaced under `/hazn:` (e.g. `/hazn:hazn-audit`, `/hazn:hazn-website`). Skills and agents are registered automatically.

## How to add new content

**Skills** → `skills/<skill-name>/SKILL.md` (with optional `references/` subdir for deep knowledge). Triggered by description matching when Claude Code thinks the skill is relevant.

**Agents** → `agents/<agent-name>.md`. Sub-agents Claude Code can dispatch in parallel for specialized roles.

**Commands** → `commands/<command-name>.md`. Slash commands invocable as `/hazn:<command-name>`.

**Workflows** → `workflows/<workflow-name>.yaml`. Dependency graphs across skills and agents.

After adding, bump the version in `.claude-plugin/plugin.json` and commit.

## How NOT to use Hazn

- Do not copy `.hazn/` into client repos. The old install pattern is deprecated.
- Do not duplicate skills or agents into consumer repos' `.claude/` directories.
- Do not create per-consumer slash command files that mirror the plugin's commands.

If you need a Hazn capability in a specific repo, run `claude plugin install` in that workspace.

## History

This repo was consolidated on 2026-05-15 from 5 scattered locations:
- `repos/legacy/hazn-dev` (duplicate submodule — removed)
- `repos/internal/vault/hazn.plugin` (early packaging zip — removed)
- `repos/sales/autonomous-proposals/.hazn` (had red-team pack + Shopify skills — upstreamed)
- `repos/sales/landing-pages/.hazn` (stale install — removed)
- `repos/internal/autonomous-website-personal/.hazn` (stale install — removed)
- `repos/products/website/.hazn` (had jwd-audit + wireframe-fidelity — upstreamed)

See the consolidation delta reports for the full history at:
`autonomous/scratch/hazn-consolidation/` (in the workspace, not this repo).

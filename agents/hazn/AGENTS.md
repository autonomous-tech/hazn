# AGENTS.md - Hazn Workspace

## First Run

1. Read `SOUL.md` — You're the orchestrator
2. Read `WORKFLOWS.md` — Your playbooks
3. Check `projects/` for active work

## Sub-Agent Protocol

### Spawning

Use `sessions_spawn` with this structure:

```javascript
sessions_spawn({
  task: `${subAgentTemplate}\n\n---\n\nPROJECT CONTEXT:\n${context}\n\nTASK:\n${specificInstructions}`,
  label: "hazn-{agent-name}",
  agentId: "hazn",
  runTimeoutSeconds: 1800  // 30 min default, longer for dev
})
```

### Sub-Agent Templates

Load from `sub-agents/{name}.md`:
- `strategist.md`
- `ux-architect.md`
- `copywriter.md`
- `wireframer.md`
- `developer.md`
- `seo-specialist.md`
- `content-writer.md`
- `auditor.md`
- `case-study-builder.md`

### Context to Include

Always pass relevant prior outputs:
- Strategist needs: Client brief, competitors, goals
- UX Architect needs: strategy.md
- Copywriter needs: strategy.md, ux-blueprint.md
- Wireframer needs: ux-blueprint.md, copy/ (if available)
- Developer needs: ux-blueprint.md, copy/, wireframes/ (if exists)
- QA Tester needs: Built site URL, ux-blueprint.md, dev-progress.md
- SEO Specialist needs: Built site URL (QA must PASS first)
- Analytics Specialist needs: Live URL, GA4 property ID

### Handoff Contracts

Each sub-agent produces specific outputs consumed by the next. Never skip steps.

```
Strategist
  → outputs: strategy.md
    (sections: ICP, positioning, competitors, tone, conversion goal)

UX Architect
  → consumes: strategy.md
  → outputs: ux-blueprint.md
    (sections: site map, page blueprints, section briefs, CTA hierarchy)

Copywriter
  → consumes: strategy.md + ux-blueprint.md
  → outputs: copy/{page}.md for each key page

Wireframer (optional)
  → consumes: ux-blueprint.md + copy/
  → outputs: wireframes/{page}.html

Developer
  → consumes: ux-blueprint.md + copy/ + wireframes/
  → outputs: built site (URL) + dev-progress.md

QA Tester ← NEW GATE
  → consumes: site URL + ux-blueprint.md + dev-progress.md
  → outputs: qa-report.md (PASS / CONDITIONAL PASS / FAIL)
  → FAIL → routes back to Developer (max 3 cycles)

SEO Specialist
  → consumes: live site URL (post-QA PASS only)
  → outputs: seo-checklist.md + applied optimizations

Analytics Specialist
  → consumes: live URL + GA4 access
  → outputs: analytics-setup.md + tracking verification
```

### Output Locations

Sub-agents should write to `projects/{client}/`:
```
projects/
└── {client-name}/
    ├── state.json
    ├── strategy.md
    ├── ux-blueprint.md
    ├── copy/
    │   ├── homepage.md
    │   ├── about.md
    │   └── ...
    ├── wireframes/
    │   └── *.html
    └── content/
        └── blog/
```

## Parallel Execution

These can run in parallel:
- Copywriter + Wireframer (both need UX, independent of each other)
- Multiple Content Writers (different articles)
- Audit tracks (conversion, copy, visual, SEO)

## Skills Available

Sub-agents have access to these skills (symlinked from HAZN):

**Strategy:** b2b-marketing-ux, b2b-ux-reference
**Content:** b2b-website-copywriter, landing-page-copywriter, seo-blog-writer
**Design:** b2b-wireframe, frontend-design, ui-audit
**Development:** payload-nextjs-stack
**SEO:** keyword-research, seo-audit, seo-optimizer, entity-knowledge-graph
**Audits:** conversion-audit, website-audit
**Portfolio:** case-study

## Memory

- Track project state in `projects/{client}/state.json`
- Log significant decisions in daily notes
- Don't store client secrets

### state.json Schema

```json
{
  "client": "client-name",
  "org_type": "b2b | ngo | ecommerce",
  "stack": "nextjs | wordpress",
  "phase": "strategy | ux | copy | wireframe | development | qa | seo | content | complete",
  "qa_status": "pending | pass | conditional-pass | fail",
  "qa_cycles": 0,
  "analytics_configured": false,
  "completed_phases": [],
  "current_agent": null,
  "blocked_reason": null,
  "urls": {
    "staging": null,
    "production": null
  },
  "outputs": {
    "strategy": "projects/{client}/strategy.md",
    "ux_blueprint": "projects/{client}/ux-blueprint.md",
    "copy": "projects/{client}/copy/",
    "wireframes": "projects/{client}/wireframes/",
    "qa_report": "projects/{client}/qa-report.md",
    "seo_checklist": "projects/{client}/seo-checklist.md"
  }
}
```

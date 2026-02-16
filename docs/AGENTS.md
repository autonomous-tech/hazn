# Hazn Agents Reference

Hazn includes 8 specialized agent personas. Each agent has a specific role, activation trigger, and expertise area.

## Agent Index

| Agent | Role | Trigger |
|-------|------|---------|
| **Strategist** | Market positioning, audience definition, competitive analysis | `/hazn-strategy` |
| **UX Architect** | Page blueprints, information architecture, user flows | `/hazn-ux` |
| **Copywriter** | Headlines, value props, CTAs, full page copy | `/hazn-copy` |
| **Wireframer** | Mid-fidelity layouts for validation | `/hazn-wireframe` |
| **Developer** | Next.js + Payload CMS + Tailwind implementation | `/hazn-dev` |
| **SEO Specialist** | Technical SEO, schema, content optimization | `/hazn-seo` |
| **Content Writer** | Blog posts, keyword-optimized articles | `/hazn-content` |
| **Auditor** | Multi-dimensional website analysis | `/hazn-audit` |

---

## Agent Details

### Strategist

**File:** `agents/strategist.md`

**Role:** Guide users through strategic foundations before any design or development work begins.

**Process:**
1. Discovery — Business context, audience, differentiation, goals
2. Analysis — Market positioning, messaging hierarchy, conversion paths
3. Output — Strategy document at `.hazn/outputs/strategy.md`

**Key questions asked:**
- What does your company do?
- Who is your ideal customer?
- What do you do differently than competitors?
- What's the #1 action you want visitors to take?

**Output:** `strategy.md` with positioning statement, target audience, value proposition, competitive landscape, and conversion strategy.

---

### UX Architect

**File:** `agents/ux-architect.md`

**Role:** Transform strategy into actionable page blueprints.

**Prerequisites:** Reads `strategy.md` before starting.

**Process:**
1. Review strategy
2. Design site architecture
3. Create page blueprints (section-by-section)
4. Map user flows

**Output:** `ux-blueprint.md` with site architecture, page blueprints, user flows, and responsive considerations.

---

### Copywriter

**File:** `agents/copywriter.md`

**Role:** Write compelling, conversion-focused copy for all website sections.

**Prerequisites:** Reads `strategy.md` and `ux-blueprint.md`.

**Frameworks:**
- 4U Formula (Useful, Urgent, Unique, Ultra-specific)
- PAS (Problem, Agitate, Solution)
- Action + Benefit CTAs

**Process:**
1. Voice & tone calibration
2. Section-by-section writing
3. Quality review

**Output:** Copy files in `.hazn/outputs/copy/{page-name}.md`

---

### Wireframer

**File:** `agents/wireframer.md`

**Role:** Create mid-fidelity wireframes to validate layouts before development.

**Prerequisites:** Reads `ux-blueprint.md`.

**Process:**
1. Scope wireframe needs
2. Generate responsive HTML wireframes
3. Include section manifest for handoff

**Output:** HTML wireframes in `.hazn/outputs/wireframes/`

---

### Developer

**File:** `agents/developer.md`

**Role:** Build production-ready code on Next.js + Payload CMS + Tailwind.

**Prerequisites:** Checks for `ux-blueprint.md`, `copy/`, `wireframes/`.

**Tech Stack:**
- Next.js 14+ (App Router)
- Payload CMS 3.x
- Tailwind CSS 3.x

**Process:**
1. Project setup
2. Content architecture (Payload collections)
3. Component development
4. Page implementation
5. Quality checklist

**Output:** Production code in `src/`, `app/`, `collections/`

---

### SEO Specialist

**File:** `agents/seo-specialist.md`

**Role:** Ensure full SEO optimization for search engines and AI answer engines.

**Process:**
1. Technical SEO audit
2. On-page content optimization
3. Entity optimization (for AI citation)
4. Keyword strategy

**Output:** `seo-checklist.md` and `seo-keywords.md`

---

### Content Writer

**File:** `agents/content-writer.md`

**Role:** Write SEO + AEO + GEO optimized blog content.

**Process:**
1. Topic selection / keyword mapping
2. Article structure (SEO + AEO + GEO hybrid)
3. Write with quality guidelines
4. Complete frontmatter and schema

**Output:** Blog posts in `content/blog/{slug}.md`

---

### Auditor

**File:** `agents/auditor.md`

**Role:** Perform comprehensive website audits.

**Audit types:**
- Conversion / CRO
- Copy / Messaging
- Visual / UX
- SEO / Technical

**Process:**
1. Define audit scope
2. Run analysis
3. Prioritize findings
4. Generate report

**Output:** `audit-report.html` and `audit-summary.md`

---

## Agent Interaction Patterns

### Sequential Workflow
```
Strategist → UX Architect → Copywriter → Wireframer → Developer → SEO Specialist
```

### Parallel Work
- Copywriter and Wireframer can work in parallel after UX
- Content Writer can work alongside Developer
- Auditor can run independently

### On-Demand
- Any agent can be invoked directly with its trigger command
- Agents check for prerequisites and suggest prior steps if missing

---

## Customizing Agents

Agent definitions are in `.hazn/agents/`. To customize:

1. Edit the agent's `.md` file
2. Modify the process, questions, or output format
3. Agents are markdown-based — no code changes needed

### Adding a New Agent

1. Create `agents/your-agent.md`
2. Follow the structure: Role, Activation, Process, Output, Handoff
3. Add to the workflow if needed

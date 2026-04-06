# Codebase Structure

**Analysis Date:** 2026-03-05

## Directory Layout

```
hazn/                                     # Workspace root (NOT a git repo itself)
├── .planning/                            # GSD planning directory
│   └── codebase/                         # Codebase analysis docs
│
├── autonomous-agent-os/                  # Project 1: Agent OS web app (git repo)
│   ├── .env.sample                       # Environment variable template
│   ├── CLAUDE.md                         # Claude Code instructions
│   ├── Dockerfile                        # Multi-stage Docker build
│   ├── docker-compose.yml                # 3-service stack (app + Letta + Postgres)
│   ├── docker-entrypoint.sh              # Migration + server startup
│   ├── package.json                      # Root package manifest
│   ├── next.config.ts                    # Next.js 16 config (standalone output)
│   ├── tsconfig.json                     # TypeScript config (@/* path alias)
│   ├── vitest.config.ts                  # Vitest test runner config
│   ├── playwright.config.ts              # E2E test config
│   ├── eslint.config.mjs                 # ESLint flat config
│   ├── postcss.config.mjs                # PostCSS + Tailwind
│   ├── prisma.config.ts                  # Prisma config
│   ├── components.json                   # shadcn/ui config
│   ├── prompt.md                         # Reference prompt doc
│   ├── user-experience.md                # UX documentation
│   │
│   ├── prisma/                           # Database schema + migrations
│   │   ├── schema.prisma                 # 6 models: AgentProject, AgentTemplate, Deployment, ChatSession, McpServerConfig, ToolExecutionLog
│   │   ├── seed.ts                       # Seeds templates + starter agents
│   │   └── migrations/                   # 5 migration files
│   │
│   ├── src/
│   │   ├── app/                          # Next.js App Router pages + API
│   │   │   ├── layout.tsx                # Root layout (dark theme, Inter + Geist Mono)
│   │   │   ├── page.tsx                  # Dashboard (agent grid, stats, quick-create)
│   │   │   ├── globals.css               # Global styles + Tailwind
│   │   │   ├── favicon.ico
│   │   │   │
│   │   │   ├── agents/                   # Agent builder pages
│   │   │   │   ├── new/page.tsx          # 4-step creation wizard
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx          # Section-card builder (main editing UI)
│   │   │   │       └── workspace/
│   │   │   │           └── page.tsx      # Post-deploy workspace (chat, memory, tools)
│   │   │   │
│   │   │   ├── a/                        # Public agent interface
│   │   │   │   ├── layout.tsx            # Minimal public layout
│   │   │   │   └── [slug]/page.tsx       # Public chat page
│   │   │   │
│   │   │   └── api/                      # API route handlers (22 files, 36 methods)
│   │   │       ├── agents/
│   │   │       │   ├── route.ts          # GET (list), POST (create with AI inference)
│   │   │       │   ├── [id]/
│   │   │       │   │   ├── route.ts      # GET, PATCH (merge config), DELETE
│   │   │       │   │   ├── deploy/route.ts    # POST (deploy), GET (status), DELETE (pause), PATCH (resume)
│   │   │       │   │   ├── enrich/route.ts    # POST (AI enrichment for section cards)
│   │   │       │   │   ├── claude-code-export/route.ts  # GET (generate export files)
│   │   │       │   │   ├── sync-session/route.ts  # POST (receive session data, trigger memory extract)
│   │   │       │   │   ├── stages/[stage]/route.ts  # PUT (replace entire section)
│   │   │       │   │   ├── sessions/
│   │   │       │   │   │   ├── route.ts      # GET (list sessions)
│   │   │       │   │   │   └── [sessionId]/route.ts  # GET (session transcript)
│   │   │       │   │   └── mcp-servers/
│   │   │       │   │       ├── route.ts      # GET (list), POST (add)
│   │   │       │   │       └── [serverId]/
│   │   │       │   │           ├── route.ts  # PATCH (update), DELETE (remove)
│   │   │       │   │           └── test/route.ts  # POST (test connection)
│   │   │       │   └── by-slug/
│   │   │       │       └── [slug]/
│   │   │       │           ├── route.ts      # GET (resolve agent by slug)
│   │   │       │           └── sync-session/route.ts  # POST (sync by slug)
│   │   │       ├── chat/route.ts         # POST (builder conversation)
│   │   │       ├── test/route.ts         # POST (test sandbox)
│   │   │       ├── templates/route.ts    # GET (list templates)
│   │   │       ├── runtime/
│   │   │       │   └── [slug]/
│   │   │       │       ├── route.ts      # GET (public agent info)
│   │   │       │       └── chat/route.ts # POST (runtime chat with memory + MCP tools)
│   │   │       └── letta/                # Letta proxy (credentials stay server-side)
│   │   │           └── agents/[lettaId]/
│   │   │               ├── memory/
│   │   │               │   ├── route.ts  # GET (list blocks)
│   │   │               │   └── [label]/route.ts  # GET (block), PUT (update)
│   │   │               └── archival/route.ts  # GET (search), POST (insert)
│   │   │
│   │   ├── components/
│   │   │   ├── providers.tsx             # TanStack Query provider (30s stale time)
│   │   │   ├── ui/                       # shadcn/ui primitives (badge, button, card, dialog, input, etc.)
│   │   │   ├── builder/                  # Agent builder UI components
│   │   │   │   ├── SectionCard.tsx       # Base card wrapper (title, icon, status badge)
│   │   │   │   ├── cards/               # Section-specific cards
│   │   │   │   │   ├── index.ts         # Barrel export
│   │   │   │   │   ├── IdentityCard.tsx
│   │   │   │   │   ├── PurposeCard.tsx
│   │   │   │   │   ├── AudienceCard.tsx
│   │   │   │   │   ├── WorkflowCard.tsx
│   │   │   │   │   ├── MemoryCard.tsx
│   │   │   │   │   └── BoundariesCard.tsx
│   │   │   │   ├── AiCallout.tsx         # AI enrichment callout (suggestion/idea/question)
│   │   │   │   ├── AgentCard.tsx         # Agent card for grid display
│   │   │   │   ├── ClaudeCodeExportDialog.tsx
│   │   │   │   ├── LivePreview.tsx       # Real-time AGENT-MD-SPEC preview
│   │   │   │   ├── McpServerPanel.tsx    # MCP server configuration
│   │   │   │   ├── PillSelector.tsx      # Pill-style radio selector
│   │   │   │   ├── TagInput.tsx          # Tag input (Enter to add, Backspace to remove)
│   │   │   │   └── TestChat.tsx          # Test mode chat
│   │   │   ├── runtime/
│   │   │   │   └── RuntimeChat.tsx       # Public runtime chat component
│   │   │   └── workspace/               # Post-deployment workspace components
│   │   │       ├── chat/
│   │   │       │   ├── ChatPanel.tsx     # Message list + input
│   │   │       │   ├── StreamingMessage.tsx  # Typewriter effect + reasoning
│   │   │       │   └── ToolCallInline.tsx    # Collapsible tool call display
│   │   │       ├── memory/
│   │   │       │   ├── MemoryPanel.tsx   # Core memory blocks + archival search
│   │   │       │   └── MemoryBlockCard.tsx   # Editable block with usage bar
│   │   │       └── tools/
│   │   │           └── ToolLogPanel.tsx  # MCP execution log
│   │   │
│   │   ├── lib/                          # Shared business logic
│   │   │   ├── types.ts                  # Core type definitions (AgentConfig, StageData, etc.)
│   │   │   ├── db.ts                     # Prisma client singleton (better-sqlite3 adapter)
│   │   │   ├── claude.ts                 # Anthropic SDK wrapper (chat, chatWithTools, inferFromDescription)
│   │   │   ├── validate.ts              # Agent validation before deployment
│   │   │   ├── slug.ts                  # Slug generation utility
│   │   │   ├── utils.ts                 # General utilities (cn, etc.)
│   │   │   ├── archetypes.ts            # Agent archetype definitions
│   │   │   ├── mcp-helpers.ts           # MCP server row-to-definition conversion
│   │   │   ├── sync-session.ts          # Shared sync-session handler
│   │   │   │
│   │   │   ├── prompts/                 # Prompt engineering
│   │   │   │   ├── index.ts             # BASE_SYSTEM_PROMPT, TEST_SYSTEM_PROMPT, STAGE_PROMPTS
│   │   │   │   └── enrich.ts            # buildEnrichmentPrompt() per section
│   │   │   │
│   │   │   ├── runtime/                 # Runtime engine
│   │   │   │   ├── engine.ts            # processMessage() -- main chat entry point + agentic tool loop
│   │   │   │   ├── guardrails.ts        # Pre/post message guardrail checks
│   │   │   │   ├── prompt.ts            # buildRuntimeSystemPrompt() from config
│   │   │   │   ├── mcp-client.ts        # McpClientManager (connect, list tools, execute, disconnect)
│   │   │   │   ├── mcp-presets.ts       # 5 pre-configured MCP servers
│   │   │   │   ├── types.ts             # RuntimeMessage, ProcessMessageResult, etc.
│   │   │   │   └── tools.types.ts       # McpServerDefinition, ToolCall, ToolResult, etc.
│   │   │   │
│   │   │   ├── letta/                   # Letta (MemGPT) integration
│   │   │   │   ├── client.ts            # Singleton lettaClient (nullable), isLettaEnabled()
│   │   │   │   ├── translate.ts         # translateToLettaParams() -- AgentConfig -> Letta create params
│   │   │   │   ├── memory.ts            # Shared project blocks, memory snapshots, prompt hydration
│   │   │   │   ├── memory-extract.ts    # Session memory extraction via Claude categorization
│   │   │   │   └── skills.ts            # loadSkillToArchival(), loadSkillsDirectory()
│   │   │   │
│   │   │   ├── claude-code/             # Claude Code integration
│   │   │   │   ├── generate-agent.ts    # generateAgentMd(), generateMcpJson(), generateSettingsJson()
│   │   │   │   └── AGENT-MD-SPEC.md     # Agent markdown specification reference
│   │   │   │
│   │   │   └── templates/
│   │   │       └── index.ts             # Template definitions
│   │   │
│   │   ├── stores/                      # Zustand client-side state
│   │   │   ├── chat-store.ts            # Messages, streaming, partial content, error
│   │   │   └── memory-store.ts          # Memory blocks, archival results, loading
│   │   │
│   │   └── generated/                   # Auto-generated (do not edit)
│   │       └── prisma/                  # Prisma client output
│   │
│   ├── packages/
│   │   └── agent-os-mcp/                # Standalone MCP server package
│   │       ├── package.json             # Separate package manifest
│   │       ├── tsconfig.json            # ES2022 ESM target
│   │       ├── bin/
│   │       │   └── agent-os-mcp.mjs     # CLI entry point
│   │       └── src/
│   │           ├── index.ts             # MCP server setup + 7 tool registrations (Zod schemas)
│   │           ├── config.ts            # CLI args (--url, --agent), env vars
│   │           ├── api-client.ts        # HTTP client wrapping Agent OS API
│   │           └── tools/
│   │               ├── context.ts       # load_context handler
│   │               ├── memory.ts        # get_memory_blocks, core_memory_replace, core_memory_append
│   │               ├── archival.ts      # archival_search, archival_insert
│   │               └── sync.ts          # sync_session handler
│   │
│   ├── skills/                          # Skill documents loaded into agent archival memory at deploy
│   │   ├── brand-guide/SKILL.md
│   │   ├── frontend-design/SKILL.md
│   │   └── payload-cms/SKILL.md
│   │
│   ├── tests/                           # All tests (480 tests, 38 files + 5 E2E specs)
│   │   ├── setup.ts                     # Global mocks (db + claude)
│   │   ├── helpers/
│   │   │   ├── db.ts                    # getMockedPrisma(), test factories, createRequest()
│   │   │   └── fixtures.ts             # sampleAgentConfig, test data factories
│   │   ├── api/                         # Route handler tests (17 files)
│   │   ├── lib/                         # Library module tests (8 files)
│   │   ├── runtime/                     # Engine + guardrails + MCP tests (7 files)
│   │   ├── stores/                      # Zustand store tests (1 file)
│   │   ├── flows/                       # Integration flow tests (5 files)
│   │   └── e2e/                         # Playwright specs (5 files)
│   │       └── helpers.ts               # E2E helper utilities
│   │
│   ├── public/                          # Static assets
│   │   ├── file.svg, globe.svg, next.svg, vercel.svg, window.svg
│   │
│   └── docs/
│       └── agent-os-overview.html       # Standalone HTML documentation
│
└── hazn/                                # Project 2: Hazn CLI framework (git repo)
    ├── package.json                     # CLI package manifest (bin: hazn)
    ├── CNAME                            # hazn.dev DNS
    ├── _config.yml                      # Jekyll config (GitHub Pages)
    ├── index.html                       # Landing page
    ├── LICENSE                          # MIT
    ├── README.md
    ├── playwright.config.ts             # E2E test config
    │
    ├── bin/
    │   └── cli.js                       # CLI entry point (Commander.js)
    │
    ├── src/
    │   ├── index.js                     # Exports: { install, help }
    │   ├── installer.js                 # Main installer logic + tool-specific setup
    │   └── help.js                      # Contextual help system
    │
    ├── agents/                          # Agent persona definitions (15 markdown files)
    │   ├── strategist.md
    │   ├── ux-architect.md
    │   ├── copywriter.md
    │   ├── wireframer.md
    │   ├── developer.md
    │   ├── seo-specialist.md
    │   ├── content-writer.md
    │   ├── auditor.md
    │   ├── qa-tester.md
    │   ├── analytics-inspector.md
    │   ├── analytics-adversary.md
    │   ├── analytics-client-reporter.md
    │   ├── analytics-report-writer.md
    │   ├── analytics-teaser-collector.md
    │   └── analytics-teaser-writer.md
    │
    ├── workflows/                       # Workflow definitions (7 YAML files)
    │   ├── website.yaml                 # Full website build
    │   ├── landing.yaml                 # Single landing page
    │   ├── audit.yaml                   # Site audit
    │   ├── blog.yaml                    # Blog content pipeline
    │   ├── ngo-website.yaml             # NGO-specific website
    │   ├── analytics-audit.yaml         # Full GA4/GSC audit
    │   └── analytics-teaser.yaml        # Prospect teaser report
    │
    ├── skills/                          # Domain knowledge (27 skill directories)
    │   ├── analytics-audit/             # Analytics audit skill + references
    │   ├── b2b-marketing-ux/
    │   ├── b2b-website-copywriter/
    │   ├── conversion-audit/            # Includes references + HTML template asset
    │   ├── frontend-design/
    │   ├── keyword-research/            # Includes Python script + API reference
    │   ├── seo-audit/
    │   ├── seo-blog-writer/
    │   ├── ui-audit/                    # Rich skill with 15+ reference docs, .clawdhub origin
    │   └── ...                          # (17 more skill directories, each with SKILL.md)
    │
    ├── scripts/                         # Data collection scripts (Python)
    │   └── analytics-audit/
    │       ├── requirements.txt         # Python dependencies
    │       ├── ga4_collector.py
    │       ├── ga4_collector_extra.py
    │       ├── gsc_collector.py
    │       ├── pagespeed_collector.py
    │       └── teaser_collector.py
    │
    ├── templates/
    │   └── HAZN.md                      # Quick reference template copied to project root
    │
    ├── projects/                        # Project-specific outputs
    │   └── landing-page-v2/             # Strategy, copy, SEO plan, UX blueprint
    │
    ├── avatars/                         # Agent avatar images (PNG)
    │
    ├── assets/
    │   └── avatar.png
    │
    ├── docs/                            # Documentation
    │   ├── README.md
    │   ├── AGENTS.md
    │   ├── SKILLS.md
    │   ├── WORKFLOWS.md
    │   ├── ANALYTICS-AUDIT.md
    │   └── index.html
    │
    └── tests/
        └── landing.spec.ts              # Playwright test for landing page
```

## Directory Purposes

### autonomous-agent-os

**`src/app/`:**
- Purpose: Next.js App Router pages and API routes
- Contains: Server Components (pages), Client Components (interactive pages), route handlers
- Key files: `page.tsx` (dashboard), `agents/[id]/page.tsx` (builder), `api/runtime/[slug]/chat/route.ts` (runtime)

**`src/components/`:**
- Purpose: Reusable React components organized by feature
- Contains: Builder cards, workspace panels, runtime chat, shadcn/ui primitives
- Key files: `builder/cards/*.tsx` (6 section cards), `builder/LivePreview.tsx`, `workspace/chat/ChatPanel.tsx`

**`src/lib/`:**
- Purpose: Shared business logic, integrations, and utilities
- Contains: Claude wrapper, Letta modules, runtime engine, prompt builders, types, validators
- Key files: `types.ts` (all core types), `claude.ts` (API wrapper), `runtime/engine.ts` (chat engine), `db.ts` (Prisma client)

**`src/stores/`:**
- Purpose: Client-side state management (Zustand)
- Contains: Chat message store, memory block store

**`prisma/`:**
- Purpose: Database schema, migrations, and seed data
- Contains: `schema.prisma` (6 models), 5 migration directories, `seed.ts`

**`packages/agent-os-mcp/`:**
- Purpose: Standalone MCP server for Claude Code integration
- Contains: Tool handlers, API client, CLI entry point
- Note: Has its own `tsconfig.json` and `package.json`, excluded from root tsconfig

**`skills/`:**
- Purpose: Domain knowledge documents loaded into agent archival memory at deploy time
- Contains: SKILL.md files chunked at ~1000 char boundaries for retrieval

**`tests/`:**
- Purpose: All test code
- Contains: API tests, lib tests, runtime tests, store tests, flow tests, E2E specs
- Key files: `setup.ts` (global mocks), `helpers/db.ts` (test factories), `helpers/fixtures.ts` (sample data)

### hazn

**`agents/`:**
- Purpose: Agent persona definitions that AI tools read and role-play
- Contains: 15 markdown files, each defining an agent's identity, responsibilities, and behavior

**`workflows/`:**
- Purpose: Multi-phase process definitions
- Contains: 7 YAML files defining phase order, dependencies, outputs, checkpoints

**`skills/`:**
- Purpose: Deep domain knowledge documents for AI agents to reference
- Contains: 27 skill directories, each with a `SKILL.md` and optional `references/` subdirectory

**`scripts/`:**
- Purpose: Python data collection scripts for analytics audits
- Contains: GA4, GSC, PageSpeed, and teaser collectors with their own `requirements.txt`

## Key File Locations

### autonomous-agent-os

**Entry Points:**
- `src/app/page.tsx`: Dashboard home page
- `src/app/agents/new/page.tsx`: Agent creation wizard
- `src/app/agents/[id]/page.tsx`: Agent builder (main editing UI)
- `src/app/agents/[id]/workspace/page.tsx`: Post-deployment workspace
- `src/app/a/[slug]/page.tsx`: Public deployed agent chat

**Configuration:**
- `prisma/schema.prisma`: Database schema (6 models)
- `next.config.ts`: Next.js config (standalone output, external packages)
- `tsconfig.json`: TypeScript config (path alias `@/*` -> `./src/*`)
- `vitest.config.ts`: Test runner config
- `components.json`: shadcn/ui component config

**Core Logic:**
- `src/lib/runtime/engine.ts`: Main chat processing engine (agentic tool loop)
- `src/lib/claude.ts`: Anthropic SDK wrapper (3 exported functions)
- `src/lib/letta/memory.ts`: Memory hydration and shared project blocks
- `src/lib/letta/memory-extract.ts`: Session memory extraction via Claude
- `src/lib/runtime/prompt.ts`: Runtime system prompt builder from AgentConfig
- `src/lib/prompts/enrich.ts`: AI enrichment prompt builder per section
- `src/lib/validate.ts`: Agent validation before deployment
- `src/lib/claude-code/generate-agent.ts`: Generate Claude Code export files

**Testing:**
- `tests/setup.ts`: Global mock configuration
- `tests/helpers/db.ts`: Test factories and utilities
- `tests/helpers/fixtures.ts`: Sample data and mock factories

### hazn

**Entry Points:**
- `bin/cli.js`: CLI entry point
- `src/index.js`: Programmatic API

**Core Logic:**
- `src/installer.js`: Main installation logic (file copy + tool setup)
- `src/help.js`: Contextual help system

## Naming Conventions

**Files (autonomous-agent-os):**
- Pages: `page.tsx` (Next.js App Router convention)
- API routes: `route.ts` (Next.js App Router convention)
- Components: `PascalCase.tsx` (e.g., `ChatPanel.tsx`, `MemoryBlockCard.tsx`)
- Libraries: `kebab-case.ts` (e.g., `mcp-client.ts`, `memory-extract.ts`)
- Types: `types.ts` or `tools.types.ts` (colocated with feature)
- Stores: `kebab-case-store.ts` (e.g., `chat-store.ts`)
- Tests: `kebab-case.test.ts` (e.g., `engine.test.ts`, `agents.test.ts`)
- E2E tests: `kebab-case.spec.ts` (e.g., `builder.spec.ts`)

**Files (hazn):**
- Agents: `kebab-case.md` (e.g., `ux-architect.md`)
- Workflows: `kebab-case.yaml` (e.g., `analytics-audit.yaml`)
- Skills: `SKILL.md` inside `kebab-case/` directories
- Scripts: `snake_case.py` (Python convention)

**Directories (autonomous-agent-os):**
- Feature groups: `kebab-case` (e.g., `claude-code/`, `mcp-servers/`)
- Dynamic routes: `[param]` (Next.js convention, e.g., `[id]/`, `[slug]/`)
- Component groups: `kebab-case` (e.g., `builder/cards/`, `workspace/chat/`)

## Where to Add New Code

### autonomous-agent-os

**New API Endpoint:**
- Route handler: `src/app/api/{resource}/route.ts` (or `src/app/api/{resource}/[param]/route.ts` for dynamic)
- Follow pattern: import `prisma` from `@/lib/db`, wrap in try-catch, return `NextResponse.json()`
- Tests: `tests/api/{resource}.test.ts`

**New Page:**
- Page component: `src/app/{path}/page.tsx`
- Use Server Components for data fetching, Client Components for interactivity
- Tests: `tests/e2e/{feature}.spec.ts`

**New UI Component:**
- Builder-related: `src/components/builder/{ComponentName}.tsx`
- Workspace-related: `src/components/workspace/{area}/{ComponentName}.tsx`
- Reusable primitive: `src/components/ui/{component}.tsx` (via shadcn/ui CLI)
- Runtime/public: `src/components/runtime/{ComponentName}.tsx`

**New Library Module:**
- General utility: `src/lib/{module-name}.ts`
- Feature-specific: `src/lib/{feature}/{module-name}.ts` (e.g., `src/lib/letta/new-module.ts`)
- Types: Add to `src/lib/types.ts` or create `src/lib/{feature}/types.ts`
- Tests: `tests/lib/{module-name}.test.ts`

**New Runtime Feature:**
- Engine changes: `src/lib/runtime/engine.ts`
- New runtime module: `src/lib/runtime/{module-name}.ts`
- Tests: `tests/runtime/{module-name}.test.ts`

**New Letta Feature:**
- Letta module: `src/lib/letta/{module-name}.ts`
- Tests: `tests/lib/letta-{module-name}.test.ts`

**New MCP Server Tool:**
- Tool handler: `packages/agent-os-mcp/src/tools/{tool-name}.ts`
- Register in: `packages/agent-os-mcp/src/index.ts` (with Zod schema)
- API support: `packages/agent-os-mcp/src/api-client.ts` (add method if needed)

**New Prisma Model:**
- Schema: `prisma/schema.prisma`
- Migration: `npx prisma migrate dev --name {migration_name}`
- Client regeneration: `npx prisma generate`

**New Skill:**
- Skill document: `skills/{skill-name}/SKILL.md`
- Optional references: `skills/{skill-name}/references/`

### hazn

**New Agent Persona:**
- Agent file: `agents/{agent-name}.md`
- Avatar: `avatars/{agent-name}-v3.png`

**New Workflow:**
- Workflow file: `workflows/{workflow-name}.yaml`
- Slash command: Added by `installer.js` in `setupClaudeCode()` function

**New Skill:**
- Skill directory: `skills/{skill-name}/SKILL.md`
- Optional: `skills/{skill-name}/references/` for supporting docs

**New Data Collection Script:**
- Script: `scripts/{category}/{script_name}.py`
- Dependencies: Add to `scripts/{category}/requirements.txt`

## Special Directories

**`autonomous-agent-os/src/generated/prisma/`:**
- Purpose: Auto-generated Prisma client code
- Generated: Yes (by `npx prisma generate`)
- Committed: No (in `.gitignore`)

**`autonomous-agent-os/packages/agent-os-mcp/dist/`:**
- Purpose: Compiled MCP server output
- Generated: Yes (by `npm run build` in the package directory)
- Committed: No

**`hazn/.hazn/`:**
- Purpose: Hazn framework files within the hazn project itself (dogfooding)
- Generated: Partially (outputs are generated by agent runs)
- Committed: Yes (outputs are tracked)

**`hazn/projects/`:**
- Purpose: Project-specific generated artifacts
- Generated: Yes (by agent workflows)
- Committed: Yes

---

*Structure analysis: 2026-03-05*

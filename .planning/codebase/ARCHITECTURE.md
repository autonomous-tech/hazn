# Architecture

**Analysis Date:** 2026-03-05

## Repository Overview

This is a **monorepo** containing two distinct projects under one working directory:

1. **autonomous-agent-os** -- A full-stack Next.js web application for building, deploying, and managing AI agents with persistent memory
2. **hazn** -- A CLI tool and content framework for AI-driven marketing website development

These are independent codebases with separate `package.json` files, separate git histories, and no shared code dependencies. They coexist in the same workspace directory but are architecturally unrelated.

---

## Project 1: Autonomous Agent OS

### Pattern Overview

**Overall:** Server-rendered Next.js App Router application with API route handlers, Zustand client-side state, and external service integration (Anthropic Claude + Letta/MemGPT).

**Key Characteristics:**
- Next.js 16 App Router with both Server Components and Client Components
- API-first design: all mutations go through `/api/` route handlers
- Optional Letta integration: gracefully degrades when Letta is unavailable
- Section-card builder model mapping 1:1 to an AGENT-MD-SPEC output format
- Agentic tool-use loop with MCP server connectivity

### Layers

**Presentation Layer:**
- Purpose: Render UI, handle user interactions, manage client-side state
- Location: `autonomous-agent-os/src/app/` (pages) + `autonomous-agent-os/src/components/`
- Contains: React Server Components (pages), Client Components (interactive), Zustand stores
- Depends on: API layer via `fetch()`, Zustand stores, TanStack Query
- Used by: End users (browser)

**API Layer:**
- Purpose: Handle HTTP requests, validate input, orchestrate business logic, serialize responses
- Location: `autonomous-agent-os/src/app/api/`
- Contains: Next.js App Router `route.ts` files with GET/POST/PATCH/DELETE handlers
- Depends on: Data layer (Prisma), Claude integration, Letta integration, Runtime engine
- Used by: Presentation layer, MCP server package, external clients

**Business Logic Layer:**
- Purpose: Core domain logic, prompt engineering, validation, translation
- Location: `autonomous-agent-os/src/lib/`
- Contains: Claude client, Letta modules, runtime engine, prompt builders, validators, type definitions
- Depends on: External APIs (Anthropic, Letta), type definitions
- Used by: API layer

**Data Layer:**
- Purpose: Persist agent configurations, deployments, sessions, tool logs
- Location: `autonomous-agent-os/prisma/` (schema + migrations) + `autonomous-agent-os/src/lib/db.ts` (client)
- Contains: Prisma schema (6 models), migration files, SQLite database
- Depends on: SQLite via `better-sqlite3` adapter
- Used by: API layer, business logic layer

**MCP Server Package:**
- Purpose: Bridge Claude Code to Agent OS persistent memory via Letta
- Location: `autonomous-agent-os/packages/agent-os-mcp/`
- Contains: Standalone Node.js MCP server (7 tools), API client, CLI entry point
- Depends on: Agent OS API endpoints (HTTP), `@modelcontextprotocol/sdk`, Zod
- Used by: Claude Code users (via stdio transport)

### Data Flow

**Agent Creation Flow:**

1. User selects archetype + audience + name in `/agents/new` (4-step wizard)
2. POST `/api/agents` receives structured input
3. `inferFromDescription()` calls Claude to generate initial `AgentConfig`
4. Agent record created in SQLite with slug (name + base36 timestamp)
5. Redirect to `/agents/[id]` builder page

**Agent Building Flow (Section-Card Model):**

1. User edits fields directly in section cards (Identity, Purpose, Audience, Workflow, Memory, Boundaries)
2. Each edit triggers debounced auto-save (3s) via PATCH `/api/agents/[id]`
3. Each edit triggers debounced enrichment (1.5s) via POST `/api/agents/[id]/enrich`
4. Enrichment returns suggestions/ideas/questions rendered as `AiCallout` components
5. User accepts/dismisses/answers callouts, which update config and may re-trigger enrichment
6. `LivePreview` component renders AGENT-MD-SPEC output in real-time (client-side generation)

**Deployment Flow:**

1. POST `/api/agents/[id]/deploy` validates config via `validateAgent()`
2. Retires any existing active deployment
3. Builds runtime system prompt via `buildRuntimeSystemPrompt()`
4. Snapshots MCP server configs
5. Creates `Deployment` record with frozen config + prompt + MCP config
6. If Letta is enabled and agent has no `lettaAgentId`: side-deploys to Letta (creates agent + loads skills)
7. Updates agent status to `"deployed"`

**Runtime Chat Flow:**

1. POST `/api/runtime/[slug]/chat` receives `{ message, sessionToken }`
2. Looks up active deployment by slug
3. If agent has `lettaAgentId` and Letta is enabled: hydrates system prompt with memory blocks
4. Finds or creates `ChatSession` (token-based)
5. Calls `processMessage()` in runtime engine
6. Engine checks pre-message guardrails (session status, turn limits)
7. If MCP servers configured: enters agentic tool-use loop (connect -> call Claude with tools -> execute tools -> feed results back -> repeat until text response or max 10 iterations)
8. If no MCP servers: simple Claude chat call
9. Persists messages + session updates to database
10. Logs tool executions if any
11. Every 10 turns or on session end: fire-and-forget `syncSessionMemory()` (Claude categorizes learnings into persona/decisions/archival buckets, writes to Letta)

**Memory Sync Flow:**

1. `syncSessionMemory()` called with `lettaAgentId`, recent messages, and config
2. `extractMemoryFromSession()` calls Claude to categorize learnings into three buckets:
   - User preferences -> `persona` block
   - Project-specific facts -> `decisions` block
   - Reusable knowledge -> archival memory
3. `persistExtractedMemory()` writes categorized learnings to Letta blocks (10k char limit for blocks, 50k for archival)

**Claude Code Bridge Flow:**

1. GET `/api/agents/[id]/claude-code-export` generates three files:
   - `.claude/agents/<slug>.md` (AGENT-MD-SPEC format)
   - `.mcp.json` (MCP server configuration including agent-os memory bridge)
   - `.claude/settings.json` (SubagentStop hooks)
2. MCP server (`packages/agent-os-mcp/`) provides 7 tools for Claude Code sessions:
   - `load_context`: Bootstrap session with full agent identity + memory state
   - `get_memory_blocks`, `core_memory_replace`, `core_memory_append`: Read/write core memory
   - `archival_search`, `archival_insert`: Long-term archival memory
   - `sync_session`: Send session summary for server-side memory extraction

**State Management:**

- **Server state**: Prisma/SQLite for all persistent data. JSON serialized in String columns (no native JSON in SQLite).
- **Client state**: Zustand stores for chat messages (`useChatStore`) and memory blocks (`useMemoryStore`). TanStack Query with 30s stale time for server data fetching.
- **Agent config**: Stored as JSON string in `AgentProject.config` column. Parsed at API boundary. PATCH merges partial updates; stage PUT replaces entire section.

### Key Abstractions

**AgentConfig:**
- Purpose: The complete configuration defining an AI agent's behavior
- Definition: `autonomous-agent-os/src/lib/types.ts`
- Shape: `{ mission, identity, capabilities, memory, triggers, guardrails }`
- Pattern: Stored as JSON string in database, parsed/serialized at API boundary

**Deployment:**
- Purpose: A frozen snapshot of an agent's config, system prompt, and MCP servers at deploy time
- Definition: `autonomous-agent-os/prisma/schema.prisma` (Deployment model)
- Pattern: Immutable once created; new deployments retire old ones. Status: `"active"` / `"paused"` / `"retired"`

**RuntimeMessage:**
- Purpose: A single message in a chat session (user or assistant)
- Definition: `autonomous-agent-os/src/lib/runtime/types.ts`
- Pattern: Stored as JSON array in `ChatSession.messages` column, capped at 40 messages

**McpServerDefinition:**
- Purpose: Configuration for connecting to an external MCP tool server
- Definition: `autonomous-agent-os/src/lib/runtime/tools.types.ts`
- Pattern: Supports stdio, SSE, and HTTP transports. Tool names namespaced as `serverName__toolName`.

**SectionName / StageName:**
- Purpose: Map builder UI sections to config keys and AGENT-MD-SPEC output sections
- Definition: `autonomous-agent-os/src/lib/types.ts`
- Pattern: `SECTION_NAMES` (6 UI sections: identity, purpose, audience, workflow, memory, boundaries) vs `STAGES` (6 legacy internal stages: mission, identity, capabilities, memory, triggers, guardrails)

### Entry Points

**Next.js App (Web):**
- Location: `autonomous-agent-os/src/app/layout.tsx` (root layout) + `autonomous-agent-os/src/app/page.tsx` (dashboard)
- Triggers: Browser navigation
- Responsibilities: Renders the full web application

**API Route Handlers:**
- Location: `autonomous-agent-os/src/app/api/` (22 route files, 36 HTTP method handlers)
- Triggers: HTTP requests from frontend or external clients
- Responsibilities: All CRUD operations, agent building, deployment, runtime chat

**MCP Server:**
- Location: `autonomous-agent-os/packages/agent-os-mcp/bin/agent-os-mcp.mjs`
- Triggers: Claude Code starts the process via stdio
- Responsibilities: Bridges Claude Code sessions to Agent OS persistent memory

**Prisma Seed:**
- Location: `autonomous-agent-os/prisma/seed.ts`
- Triggers: `npx prisma db seed`
- Responsibilities: Seeds 3 templates + 4 specialist agents

### Error Handling

**Strategy:** Try-catch at API boundaries with error logging and generic user-facing messages. Non-critical operations (Letta sync, enrichment) fail silently with console logging.

**Patterns:**
- API routes wrap all logic in try-catch, return `NextResponse.json({ error }, { status })` on failure
- Letta operations are always guarded with `isLettaEnabled()` check before any calls
- Memory sync is fire-and-forget: `.catch()` logs errors but never blocks the chat response
- `inferFromDescription()` has a fallback that returns minimal config if Claude's JSON response is malformed
- MCP client connections use `Promise.allSettled()` to skip failed servers rather than aborting entirely
- `hydrateSystemPromptWithMemory()` returns the original prompt unchanged if Letta is unreachable

### Cross-Cutting Concerns

**Logging:** `console.error` / `console.warn` with `[module]` prefix tags (e.g., `[runtime/chat]`, `[deploy]`, `[memory]`)

**Validation:** `validateAgent()` in `autonomous-agent-os/src/lib/validate.ts` checks structural errors (block deployment) and completeness/consistency warnings. Called before deployment.

**Authentication:** None. No auth layer exists. All API endpoints are publicly accessible.

**JSON Serialization:** SQLite has no native JSON type. All complex fields stored as `String` columns with `JSON.stringify`/`JSON.parse` at the API boundary. Fields: `config`, `stages`, `conversations`, `messages`, `mcpConfig`, `env`, `sandboxConfig`, `args`, `allowedTools`, `blockedTools`, `metadata`, `input`, `output`.

---

## Project 2: Hazn CLI Framework

### Pattern Overview

**Overall:** Node.js CLI tool that scaffolds an AI agent framework into a target project directory. No server, no database, no runtime -- purely an installer and content distribution mechanism.

**Key Characteristics:**
- CLI-only tool (`npx hazn install`)
- Content-centric: ships agent personas (markdown), workflow definitions (YAML), skill documents (markdown), and Python data collection scripts
- Integrates with AI coding tools (Claude Code, Cursor, Windsurf) via their configuration mechanisms
- Slash-command architecture: installs `.claude/commands/` files that trigger agent personas

### Layers

**CLI Layer:**
- Purpose: Parse commands, display help, drive the installation process
- Location: `hazn/bin/cli.js`
- Contains: Commander.js program with `install`, `help`, `list` commands
- Depends on: `src/installer.js`, `src/help.js`

**Installer:**
- Purpose: Copy agent/workflow/skill/script files into the target project, configure AI tool integrations
- Location: `hazn/src/installer.js`
- Contains: File copy logic, Claude Code setup (slash commands + CLAUDE.md), Cursor setup (`.cursorrules`)
- Depends on: `fs-extra`, `inquirer`, `ora`, `chalk`

**Content Layer:**
- Purpose: Domain knowledge and process definitions
- Location: `hazn/agents/` (personas), `hazn/workflows/` (YAML), `hazn/skills/` (knowledge), `hazn/scripts/` (Python collectors)
- Contains: Markdown agent persona files, YAML workflow definitions, skill documents, Python GA4/GSC data collectors
- Depends on: Nothing (static content)

### Data Flow

**Installation Flow:**

1. User runs `npx hazn install`
2. CLI prompts for tool selection (Claude Code, Cursor, Windsurf) and workflow selection
3. Installer creates `.hazn/` directory structure in target project
4. Copies agents, workflows, skills, and scripts into `.hazn/`
5. Creates Claude Code slash commands in `.claude/commands/`
6. Appends Hazn framework section to `CLAUDE.md` (or creates it)
7. Copies `HAZN.md` quick reference to project root

**Workflow Execution (at runtime, by the AI tool):**

1. User types `/hazn-website` (or other workflow command) in Claude Code
2. Claude Code reads the slash command file from `.claude/commands/hazn-website.md`
3. The command instructs Claude to read `.hazn/workflows/website.yaml`
4. Claude follows the phased workflow, loading agent personas as needed from `.hazn/agents/`
5. Each phase produces artifacts in `.hazn/outputs/`

### Entry Points

**CLI:**
- Location: `hazn/bin/cli.js`
- Triggers: `npx hazn install`, `npx hazn help`, `npx hazn list`
- Responsibilities: Installation, contextual help, agent/workflow listing

**Exported API:**
- Location: `hazn/src/index.js`
- Exports: `{ install, help }` -- can be used programmatically

---

*Architecture analysis: 2026-03-05*

# External Integrations

**Analysis Date:** 2026-03-05

This workspace contains two projects. Integrations are documented per-project.

---

## Project 1: Hazn (`hazn/`)

### APIs & External Services

**Google Analytics 4 (GA4) Data API:**
- Used for collecting property metadata, events, conversions, traffic sources, campaigns, e-commerce data, landing pages, device/geo breakdown
- SDK: `google-analytics-data` (Python), `google.analytics.data_v1beta.BetaAnalyticsDataClient`
- Admin SDK: `google.analytics.admin.AnalyticsAdminServiceClient`
- Auth: OAuth2 credentials at `~/.config/ga4-audit/credentials.json`
- Token cache: `~/.config/ga4-audit/token.json`
- Scopes: `analytics.readonly`, `analytics.edit`, `webmasters.readonly`
- Files: `scripts/analytics-audit/ga4_collector.py`, `scripts/analytics-audit/ga4_collector_extra.py`

**Google Search Console (GSC) API:**
- Used for organic search queries, landing page performance, device/country breakdown, cannibalization detection, brand/non-brand analysis, weekly trends
- SDK: `google-api-python-client` (Python), `googleapiclient.discovery.build("searchconsole", "v1")`
- Auth: Shares OAuth2 flow with GA4 collector (imports `get_credentials` from `ga4_collector.py`)
- File: `scripts/analytics-audit/gsc_collector.py`

**Google PageSpeed Insights API:**
- Used for Lighthouse scores, Core Web Vitals (CrUX field data), failed audits, third-party script analysis, performance opportunities
- API endpoint: `https://www.googleapis.com/pagespeedonline/v5/runPagespeed`
- Auth: Optional `PSI_API_KEY` env var for higher rate limits (free tier works without)
- No SDK, uses stdlib `urllib.request` (Python)
- File: `scripts/analytics-audit/pagespeed_collector.py`

**Tally (Form Provider):**
- Waitlist form embedded as iframe on landing page
- Integration: `<iframe data-tally-src>` with "Hazn Waitlist" title
- File: `hazn/index.html`

### Data Storage

**Databases:**
- None. Hazn is a CLI tool that generates files. No database.

**File Storage:**
- Local filesystem only
- Installer copies agents/workflows/skills to `.hazn/` in target project
- Analytics collectors write JSON output files to specified paths
- All outputs stored in `.hazn/outputs/`

**Caching:**
- None

### Authentication & Identity

**Auth Provider:**
- No user authentication (CLI tool)
- Google OAuth2 used solely for GA4/GSC API access in analytics scripts
- OAuth flow: `InstalledAppFlow.from_client_secrets_file()` with local server redirect

### Monitoring & Observability

**Error Tracking:**
- None

**Logs:**
- Console output via `chalk` (colored terminal output)
- `ora` spinner for progress indication during install

### CI/CD & Deployment

**Hosting:**
- GitHub Pages for landing page (https://hazn.ai, configured via `CNAME` file)
- npm distribution (runnable via `npx github:autonomous-tech/hazn install`)

**CI Pipeline:**
- Not detected (no `.github/workflows/` or equivalent found)

### Environment Configuration

**Required env vars:**
- None for core CLI functionality

**Optional env vars:**
- `PSI_API_KEY` - PageSpeed Insights API key for higher rate limits
- `CI` - Detected by Playwright config to set `forbidOnly` behavior

**Required credentials (analytics features only):**
- Google Cloud OAuth2 credentials file at `~/.config/ga4-audit/credentials.json`

### Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

### AI Tool Integrations

**Claude Code:**
- Installer creates `.claude/commands/` directory with 13 slash command files (`hazn-help.md`, `hazn-strategy.md`, `hazn-ux.md`, etc.)
- Appends Hazn framework section to `CLAUDE.md` if present
- File: `src/installer.js` (`setupClaudeCode()` function)

**Cursor:**
- Installer creates/appends to `.cursorrules` file
- File: `src/installer.js` (`setupCursor()` function)

**Windsurf:**
- Listed as supported AI tool in CLI prompts but no specific integration code found

### Third-Party Libraries (Public Data Collection)

The teaser collector (`scripts/analytics-audit/teaser_collector.py`) performs public data collection using only Python stdlib:
- robots.txt parsing (crawl rules, AI crawler block detection for 15 crawlers including GPTBot, ClaudeBot, etc.)
- sitemap.xml analysis (URL count, lastmod freshness, sitemap index recursion)
- HTTP security header analysis (9 headers graded A-F)
- SSL certificate inspection (issuer, expiry, SANs, cipher)
- Technology stack detection (CMS, framework, CDN, hosting via HTML patterns and headers)
- DNS resolution (IPv4/IPv6)
- No external APIs required (uses `urllib.request`, `ssl`, `socket` from stdlib)

---

## Project 2: Autonomous Agent OS (`autonomous-agent-os/`)

### APIs & External Services

**Anthropic Claude API:**
- Used for AI chat, agent enrichment, memory extraction, agent building inference
- SDK: `@anthropic-ai/sdk` ^0.74.0
- Model: `claude-sonnet-4-5-20250929` (hardcoded in `src/lib/claude.ts`)
- Auth: `ANTHROPIC_API_KEY` env var [required]
- Files: `src/lib/claude.ts`, `src/lib/prompts/`, `src/lib/letta/memory-extract.ts`

**Letta (MemGPT) Server:**
- Used for persistent agent memory (persona blocks, scratchpad, archival)
- SDK: `@letta-ai/letta-client` ^1.7.8
- Auth: `LETTA_BASE_URL` + `LETTA_SERVER_PASSWORD` env vars [optional]
- Runs as Docker container (port 8283)
- Files: `src/lib/letta/client.ts`, `src/lib/letta/memory.ts`, `src/lib/letta/translate.ts`, `src/lib/letta/memory-extract.ts`, `src/lib/letta/skills.ts`
- Integration is fully optional -- app works without it

### Data Storage

**Databases:**
- SQLite via Prisma ORM
  - Connection: `DATABASE_URL` env var (defaults to `file:./dev.db`)
  - Client: Prisma ^7.3.0 with `@prisma/adapter-better-sqlite3`
  - 6 models: `AgentProject`, `AgentTemplate`, `Deployment`, `ChatSession`, `McpServerConfig`, `ToolExecutionLog`
  - Schema: `prisma/schema.prisma`
  - Client singleton: `src/lib/db.ts`
  - Generated client output: `src/generated/prisma`
  - JSON fields stored as strings (SQLite has no native JSON)

- PostgreSQL 16 (Alpine) - Letta backend database (Docker only)
  - Used only by Letta server, not directly by Agent OS
  - Configured in `docker-compose.yml`

**File Storage:**
- Local filesystem only (SQLite DB file, skill files in `skills/`)

**Caching:**
- None (TanStack Query has 30s stale time for client-side caching)

### Authentication & Identity

**Auth Provider:**
- No user authentication implemented
- API routes are unprotected (local development tool)
- Letta credentials stay server-side (proxied through API routes)

### MCP (Model Context Protocol) Integration

**Agent OS MCP Server (`packages/agent-os-mcp/`):**
- Standalone Node.js MCP server (stdio transport)
- Bridges Claude Code to Agent OS persistent memory via Letta
- SDK: `@modelcontextprotocol/sdk` ^1.26.0
- 7 tools: `load_context`, `get_memory_blocks`, `core_memory_replace`, `core_memory_append`, `archival_search`, `archival_insert`, `sync_session`
- Install: `claude mcp add agent-os -s user -- npx agent-os-mcp --url http://localhost:3000`

**MCP Server Presets (for deployed agents):**
- 5 preset MCP servers available: `filesystem`, `git`, `browser` (Puppeteer), `jiraCloud`, `vercel`
- Configured in `src/lib/runtime/mcp-presets.ts`
- Each has timeout limits and network access controls

### Monitoring & Observability

**Error Tracking:**
- None

**Logs:**
- Console logging only
- Tool execution logs stored in `ToolExecutionLog` database model

### CI/CD & Deployment

**Hosting:**
- Docker (standalone Next.js output)
- `Dockerfile` - Multi-stage build (base -> deps -> builder -> runner) with non-root `nextjs` user
- `docker-compose.yml` - 3 services: app (port 3000), letta-server (port 8283), letta-postgres
- `docker-entrypoint.sh` - Runs Prisma migrations then starts server
- SQLite data persists in Docker named volume `app-data:/app/data`

**CI Pipeline:**
- Not detected

### Environment Configuration

**Required env vars:**
- `DATABASE_URL` - SQLite connection string
- `ANTHROPIC_API_KEY` - Claude API key

**Optional env vars:**
- `LETTA_BASE_URL` - Letta server URL (enables persistent memory features)
- `LETTA_SERVER_PASSWORD` - Letta auth password (defaults to "letta")
- `LETTA_DEFAULT_MODEL` - Override Letta model
- `LETTA_DEFAULT_EMBEDDING` - Override Letta embedding model
- `VERCEL_TOKEN` - For Vercel MCP preset

**Secrets location:**
- `.env` file (copied from `.env.sample`)
- `.env.sample` exists with variable templates (not read for this analysis)

### Webhooks & Callbacks

**Incoming:**
- `/api/agents/[id]/sync-session` (POST) - Receives session data for memory extraction
- `/api/agents/by-slug/[slug]/sync-session` (POST) - Receives session summary by slug (Claude Code SubagentStop hooks)

**Outgoing:**
- None (memory sync is triggered by incoming requests)

### API Routes Summary

22 route files with 36 HTTP method handlers:

| Route | Methods | Purpose |
|-------|---------|---------|
| `/api/templates` | GET | List agent templates |
| `/api/agents` | GET, POST | List/create agents |
| `/api/agents/[id]` | GET, PATCH, DELETE | Agent CRUD |
| `/api/agents/[id]/stages/[stage]` | PUT | Replace section config |
| `/api/agents/[id]/enrich` | POST | AI enrichment for sections |
| `/api/agents/[id]/deploy` | POST, GET, DELETE, PATCH | Deploy/status/pause/resume |
| `/api/agents/[id]/sessions` | GET | List chat sessions |
| `/api/agents/[id]/sessions/[sessionId]` | GET | Session transcript |
| `/api/agents/[id]/mcp-servers` | GET, POST | MCP server config |
| `/api/agents/[id]/mcp-servers/[serverId]` | PATCH, DELETE | Update/remove MCP server |
| `/api/agents/[id]/mcp-servers/[serverId]/test` | POST | Test MCP connection |
| `/api/agents/[id]/claude-code-export` | GET | Generate Claude Code files |
| `/api/agents/[id]/sync-session` | POST | Session memory sync |
| `/api/agents/by-slug/[slug]` | GET | Resolve agent by slug |
| `/api/agents/by-slug/[slug]/sync-session` | POST | Session sync by slug |
| `/api/chat` | POST | Builder chat endpoint |
| `/api/test` | POST | Test sandbox (role-play) |
| `/api/runtime/[slug]/chat` | POST | Runtime chat with memory |
| `/api/runtime/[slug]` | GET | Public agent info |
| `/api/letta/agents/[lettaId]/memory` | GET | Letta memory blocks |
| `/api/letta/agents/[lettaId]/memory/[label]` | GET, PUT | Read/update block |
| `/api/letta/agents/[lettaId]/archival` | GET, POST | Archival search/insert |

---

*Integration audit: 2026-03-05*

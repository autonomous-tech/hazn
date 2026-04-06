# Technology Stack

**Analysis Date:** 2026-03-05

## Workspace Overview

This workspace contains two independent projects side-by-side:
1. **Hazn** (`hazn/`) - AI-driven marketing website development framework (CLI + agent definitions)
2. **Autonomous Agent OS** (`autonomous-agent-os/`) - Platform for building and deploying AI agents with persistent memory

Each has its own `package.json`, git repo, and tech stack.

---

## Project 1: Hazn (`hazn/`)

### Languages

**Primary:**
- JavaScript (ES Modules) - CLI tool and installer (`src/`, `bin/`)
- Markdown - Agent definitions, skill definitions, workflow documentation (`agents/`, `skills/`, `workflows/`)

**Secondary:**
- Python 3.x - Analytics data collection scripts (`scripts/analytics-audit/`)
- TypeScript - Playwright E2E tests (`tests/landing.spec.ts`)
- YAML - Workflow definitions (`workflows/`)
- HTML/CSS - Landing page (`index.html`, `docs/index.html`)

### Runtime

**Environment:**
- Node.js >= 20.0.0 (specified in `hazn/package.json` `engines` field)
- Python 3.x (for analytics scripts, no version pinned)

**Package Manager:**
- npm
- Lockfile: present (`hazn/package-lock.json`, lockfileVersion 3)

### Frameworks

**Core:**
- Commander ^12.1.0 - CLI framework (`bin/cli.js`)
- No web framework (CLI tool only; generated sites use Next.js)

**Testing:**
- Node built-in test runner - Unit tests (`npm test` runs `node --test`)
- Playwright ^1.58.2 - E2E tests for landing page (`tests/landing.spec.ts`, `playwright.config.ts`)

**Build/Dev:**
- ESLint ^9.0.0 - Linting
- Jekyll (via `_config.yml`) - GitHub Pages site for docs/landing

### Key Dependencies

**Critical (runtime):**
- `commander` ^12.1.0 - CLI command parsing (`bin/cli.js`)
- `inquirer` ^9.2.23 - Interactive prompts during install (`src/installer.js`)
- `fs-extra` ^11.2.0 - File system operations, copy agent/skill/workflow files (`src/installer.js`)
- `chalk` ^5.3.0 - Terminal output colorization (`src/help.js`, `bin/cli.js`)
- `ora` ^8.0.1 - Terminal spinner animations (`src/installer.js`)
- `yaml` ^2.4.1 - YAML parsing for workflow files

**Python Dependencies (analytics scripts only):**
- `google-analytics-data` >=0.18.0 - GA4 Data API client (`scripts/analytics-audit/requirements.txt`)
- `google-auth-oauthlib` >=1.0.0 - OAuth2 authentication (`scripts/analytics-audit/requirements.txt`)
- `google-api-python-client` >=2.0.0 - Google Search Console API (`scripts/analytics-audit/requirements.txt`)

### Configuration

**Environment:**
- `.env` / `.env.local` - Listed in `.gitignore` (existence noted, not read)
- `PSI_API_KEY` - Optional env var for PageSpeed Insights rate limits (`scripts/analytics-audit/pagespeed_collector.py`)
- OAuth credentials at `~/.config/ga4-audit/credentials.json` - Required for GA4/GSC data collection
- OAuth token cached at `~/.config/ga4-audit/token.json`

**Build:**
- `hazn/package.json` - npm package config, ESM (`"type": "module"`)
- `hazn/_config.yml` - Jekyll config excluding non-docs directories from GitHub Pages build
- `hazn/playwright.config.ts` - Playwright config: Chromium only, headless, `./tests` dir

### Platform Requirements

**Development:**
- Node.js >= 20.0.0
- Python 3.x (only for analytics audit scripts)
- Google Cloud Console OAuth credentials (only for GA4/GSC collectors)

**Production/Distribution:**
- Published as npm package, runnable via `npx github:autonomous-tech/hazn install`
- Landing page hosted at https://hazn.ai via GitHub Pages (CNAME file)
- No server-side runtime (CLI tool installs files into user projects)

---

## Project 2: Autonomous Agent OS (`autonomous-agent-os/`)

### Languages

**Primary:**
- TypeScript ^5 - All source code (`src/`), tests (`tests/`), configuration
- React 19.2.3 - UI components

**Secondary:**
- SQL - Prisma schema and migrations (`prisma/`)

### Runtime

**Environment:**
- Node.js (version not pinned in engines)
- Docker (optional, for Letta integration)

**Package Manager:**
- npm
- Lockfile: present (`autonomous-agent-os/package-lock.json`, lockfileVersion 3)

### Frameworks

**Core:**
- Next.js 16.1.6 - Full-stack web framework with App Router (`next.config.ts`)
- React 19.2.3 / React DOM 19.2.3 - UI library
- Prisma ^7.3.0 - ORM with SQLite adapter (`prisma/schema.prisma`)
- TailwindCSS ^4 - Styling framework

**Testing:**
- Vitest ^4.0.18 - Unit/integration tests (480 tests, 38 files)
- Playwright ^1.58.2 - E2E tests (5 spec files)
- Testing Library (React ^16.3.2, Jest-DOM ^6.9.1) - Component testing
- jsdom ^28.0.0 - DOM environment for Vitest

**Build/Dev:**
- ESLint ^9 + eslint-config-next 16.1.6 - Linting
- tsx ^4.21.0 - TypeScript execution (Prisma seed)
- PostCSS + @tailwindcss/postcss ^4 - CSS processing
- Docker (multi-stage Dockerfile, docker-compose.yml)

### Key Dependencies

**Critical:**
- `@anthropic-ai/sdk` ^0.74.0 - Claude API integration for AI chat and enrichment
- `@prisma/client` ^7.3.0 + `@prisma/adapter-better-sqlite3` ^7.3.0 - Database ORM with SQLite
- `@letta-ai/letta-client` ^1.7.8 - Letta (MemGPT) persistent memory integration
- `@modelcontextprotocol/sdk` ^1.26.0 - MCP server implementation
- `zustand` ^5.0.11 - Client state management
- `@tanstack/react-query` ^5.90.21 - Server state management

**Infrastructure:**
- `better-sqlite3` ^12.6.2 + `@libsql/client` ^0.17.0 - SQLite database drivers
- `radix-ui` ^1.4.3 - Headless UI components
- `lucide-react` ^0.563.0 - Icon library
- `class-variance-authority` ^0.7.1 + `clsx` ^2.1.1 + `tailwind-merge` ^3.4.0 - Style utilities (Shadcn pattern)
- `dotenv` ^17.2.4 - Environment variable loading
- `jszip` ^3.10.1 - ZIP file generation (likely for exports)
- `shadcn` ^3.8.4 - Component generation CLI (devDep)
- `tw-animate-css` ^1.4.0 - Animation utilities

### Configuration

**Environment:**
- `.env.sample` exists - Copy to `.env`
- `DATABASE_URL` - SQLite path (defaults to `file:./dev.db`) [required]
- `ANTHROPIC_API_KEY` - Claude API key [required]
- `LETTA_BASE_URL` - Letta server URL (optional, enables persistent memory)
- `LETTA_SERVER_PASSWORD` - Letta auth (optional)
- `LETTA_DEFAULT_MODEL` - Override model (optional)
- `LETTA_DEFAULT_EMBEDDING` - Override embedding (optional)

**Build:**
- `autonomous-agent-os/tsconfig.json` - TypeScript config with `@/*` path alias to `./src/*`
- `autonomous-agent-os/next.config.ts` - Next.js config with `output: "standalone"`, externalizes `better-sqlite3`
- `autonomous-agent-os/postcss.config.mjs` - PostCSS with Tailwind plugin
- `autonomous-agent-os/vitest.config.ts` - Vitest config
- `autonomous-agent-os/playwright.config.ts` - Playwright config
- `autonomous-agent-os/eslint.config.mjs` - ESLint flat config
- `autonomous-agent-os/components.json` - Shadcn UI configuration
- `autonomous-agent-os/prisma.config.ts` - Prisma config
- `autonomous-agent-os/Dockerfile` - Multi-stage Docker build (base, deps, builder, runner)
- `autonomous-agent-os/docker-compose.yml` - 3-service stack (app + Letta + Postgres)

### Platform Requirements

**Development:**
- Node.js (latest LTS recommended given Next.js 16)
- npm
- Docker + Docker Compose (optional, for Letta memory features)
- Anthropic API key

**Production:**
- Docker (standalone Next.js output)
- SQLite (default) or LibSQL
- Optional: Letta server + PostgreSQL (for persistent memory)

---

*Stack analysis: 2026-03-05*

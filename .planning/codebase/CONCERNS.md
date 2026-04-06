# Codebase Concerns

**Analysis Date:** 2026-03-05

This repository contains two sub-projects: **hazn** (a CLI/agent-skill framework at `hazn/`) and **autonomous-agent-os** (a Next.js agent platform at `autonomous-agent-os/`). Concerns are organized by project.

---

## Tech Debt

### No Authentication or Authorization on API Routes (autonomous-agent-os)
- Issue: All 22 API route files (`autonomous-agent-os/src/app/api/`) have zero authentication checks. Any HTTP client can create, modify, delete, and deploy agents, read all session data, and trigger Claude API calls that cost money.
- Files: `autonomous-agent-os/src/app/api/agents/route.ts`, `autonomous-agent-os/src/app/api/agents/[id]/route.ts`, `autonomous-agent-os/src/app/api/agents/[id]/deploy/route.ts`, `autonomous-agent-os/src/app/api/chat/route.ts`, `autonomous-agent-os/src/app/api/agents/[id]/enrich/route.ts`, all other API routes
- Impact: In any network-accessible deployment, anyone can consume Claude API credits, exfiltrate agent configurations and chat histories, or deploy malicious agents. The Letta proxy routes (`/api/letta/agents/[lettaId]/memory/[label]`) also expose memory read/write to unauthenticated callers.
- Fix approach: Add authentication middleware (NextAuth, Clerk, or a simple API key check via middleware.ts). At minimum, protect all mutation endpoints (POST, PATCH, PUT, DELETE). Public runtime chat (`/api/runtime/[slug]/chat`) can remain open but should have rate limiting.

### No Rate Limiting Anywhere (autonomous-agent-os)
- Issue: No rate limiting on any endpoint. The runtime chat endpoint (`/api/runtime/[slug]/chat`) is publicly accessible and triggers a Claude API call per request.
- Files: `autonomous-agent-os/src/app/api/runtime/[slug]/chat/route.ts`, `autonomous-agent-os/src/app/api/agents/[id]/enrich/route.ts`
- Impact: A single malicious user can exhaust the Anthropic API budget by spamming the chat endpoint. The enrichment endpoint also calls Claude per request (debounced client-side but unprotected server-side).
- Fix approach: Add rate limiting middleware. For the runtime chat endpoint, consider per-IP or per-session-token limits. For enrichment, consider per-agent limits.

### Dead Code: `checkPostMessage` Guardrail Never Invoked (autonomous-agent-os)
- Issue: `checkPostMessage()` in `autonomous-agent-os/src/lib/runtime/guardrails.ts` is exported and tested (7 test cases in `tests/runtime/guardrails.test.ts`) but never called from any production code. The `failedAttempts` field is passed through the engine but never incremented.
- Files: `autonomous-agent-os/src/lib/runtime/guardrails.ts` (lines 41-50), `autonomous-agent-os/src/lib/runtime/engine.ts` (line 101)
- Impact: The escalation feature (`escalation_threshold` in guardrails config) is defined in the type system (`autonomous-agent-os/src/lib/types.ts` line 72) and rendered in the builder UI, but has no runtime effect. Agents never escalate regardless of configuration.
- Fix approach: Wire `checkPostMessage` into the engine's response processing path. After Claude responds, evaluate whether the response constitutes a "failure" (e.g., guardrail violation, off-topic response) and increment `failedAttempts`.

### Unenforced Tool Call Limits (autonomous-agent-os)
- Issue: `max_tool_calls_per_session` and `max_tool_calls_per_hour` are defined in `GuardrailsConfig` (`autonomous-agent-os/src/lib/types.ts` lines 74-75) but never checked in the engine or any route handler. The AGENT-MD-SPEC explicitly notes them as "Runtime-only setting" but they are not enforced at runtime.
- Files: `autonomous-agent-os/src/lib/types.ts` (lines 74-75), `autonomous-agent-os/src/lib/runtime/engine.ts`
- Impact: An agent with MCP tools can make unlimited tool calls per session and per hour. Combined with the lack of rate limiting, this creates unbounded cost exposure.
- Fix approach: Track tool call counts in `ChatSession.metadata` and check against limits in `processMessage()` or `processWithTools()`.

### Legacy Stage System Still Stored but Unused (autonomous-agent-os)
- Issue: The `StageData` type, `STAGES` constant, `defaultStageData()`, `StageEntry`, and `STAGE_PROMPTS`/`COMPLETION_CRITERIA` in prompts remain in the codebase. The builder UI no longer uses stages as the primary model; it computes `CardStatus` from config content directly. The `stages` column is still written on every agent create/update but the section-card model ignores it.
- Files: `autonomous-agent-os/src/lib/types.ts` (lines 3-16, 88-95, 168-179), `autonomous-agent-os/src/lib/prompts/index.ts`, `autonomous-agent-os/prisma/schema.prisma` (AgentProject.stages)
- Impact: Confusing dual model. The `stages` JSON is persisted but only used by validation (`autonomous-agent-os/src/lib/validate.ts` lines 80-88) and the legacy chat endpoint (`autonomous-agent-os/src/app/api/chat/route.ts`). New developers may not understand which model is authoritative.
- Fix approach: Remove `StageData` from the validation check. Consider keeping the `stages` column for backward compatibility but mark the type as `@deprecated`. The `/api/chat` route itself may be legacy (the builder now uses direct editing + enrichment, not chat-driven building).

### Legacy Chat Endpoint May Be Obsolete (autonomous-agent-os)
- Issue: The `/api/chat` endpoint (`autonomous-agent-os/src/app/api/chat/route.ts`, 204 lines) uses the old conversational builder model where Claude drives config updates via `previewUpdates`. The section-card builder has replaced this with direct editing + AI enrichment via `/api/agents/[id]/enrich`.
- Files: `autonomous-agent-os/src/app/api/chat/route.ts`
- Impact: 204 lines of maintained code that may not be actively used. The `conversations` column in AgentProject is written by this route but not consumed by the section-card builder UI.
- Fix approach: Verify if any frontend component still calls `/api/chat`. If not, remove the route and the `conversations` column from the schema.

### Version Mismatch in hazn CLI
- Issue: `hazn/package.json` declares version `0.2.0`, but `hazn/bin/cli.js` (line 13) reports `0.1.0`, `hazn/src/installer.js` (line 102) writes `0.1.0` to the config, and `hazn/package-lock.json` declares `0.1.0`.
- Files: `hazn/package.json` (line 3), `hazn/bin/cli.js` (line 13), `hazn/src/installer.js` (line 102), `hazn/package-lock.json` (line 3)
- Impact: Users see inconsistent version numbers. The installer writes `0.1.0` to the config file regardless of the actual package version.
- Fix approach: Use `package.json` version as the single source of truth. Import it in `cli.js` and `installer.js` instead of hardcoding.

---

## Security Considerations

### Session Cookie Lacks `secure` Flag (autonomous-agent-os)
- Risk: The runtime chat session cookie is set with `httpOnly: true` and `sameSite: "lax"` but without `secure: true`. Over HTTP, the cookie is transmitted in plaintext.
- Files: `autonomous-agent-os/src/app/api/runtime/[slug]/chat/route.ts` (lines 177-182)
- Current mitigation: The cookie only contains a session token, not credentials. In development, HTTP is expected.
- Recommendations: Add `secure: true` when `NODE_ENV === "production"`. Consider also adding a CSRF token for the runtime chat endpoint.

### Unvalidated JSON.parse Calls Without Try/Catch (autonomous-agent-os)
- Risk: 40+ `JSON.parse()` calls across the codebase, many operating on database-stored JSON strings (config, stages, conversations, messages, mcpConfig, metadata). If any database value is corrupted (e.g., manual edit, migration failure), the API route crashes with an unhandled error caught only by the outer generic catch.
- Files: `autonomous-agent-os/src/app/api/agents/[id]/route.ts` (lines 23-25, 82, 121-123), `autonomous-agent-os/src/app/api/runtime/[slug]/chat/route.ts` (lines 43, 55, 92), `autonomous-agent-os/src/app/api/agents/[id]/deploy/route.ts` (lines 26-27), and ~30 other locations
- Current mitigation: Outer try/catch blocks return generic 500 errors.
- Recommendations: Create a `safeJsonParse<T>(str: string, fallback: T): T` utility. Apply it to all database-sourced JSON strings. Log the parse failure with the affected agent/session ID for debugging.

### MCP Server Command Injection Surface (autonomous-agent-os)
- Risk: When configuring stdio-based MCP servers, the `command` field is passed directly to `StdioClientTransport` which spawns a child process. A user-configured MCP server with a malicious `command` value can execute arbitrary code on the host.
- Files: `autonomous-agent-os/src/lib/runtime/mcp-client.ts` (lines 70-80), `autonomous-agent-os/src/app/api/agents/[id]/mcp-servers/route.ts`, `autonomous-agent-os/src/lib/mcp-helpers.ts`
- Current mitigation: MCP server configs must be explicitly created via the API. The `env` field also accepts arbitrary key-value pairs that are passed to the child process.
- Recommendations: Maintain an allowlist of permitted commands (e.g., `npx`, `node`). Validate `command` values against the allowlist before creating the config. Sanitize or restrict the `env` field.

### Letta Default Password (autonomous-agent-os)
- Risk: The Letta server password defaults to `"letta"` everywhere: `.env.sample`, `docker-compose.yml`, and `autonomous-agent-os/src/lib/letta/client.ts` (line 17: `apiKey: process.env.LETTA_SERVER_PASSWORD ?? "letta"`).
- Files: `autonomous-agent-os/docker-compose.yml` (line 11, 39), `autonomous-agent-os/.env.sample` (line 6), `autonomous-agent-os/src/lib/letta/client.ts` (line 17)
- Current mitigation: Letta runs in a Docker network not exposed to the internet by default.
- Recommendations: Remove the hardcoded fallback in `client.ts`. Require `LETTA_SERVER_PASSWORD` to be explicitly set when `LETTA_BASE_URL` is configured.

### Sync-Session Endpoint Accepts Arbitrary Input (autonomous-agent-os)
- Risk: The `/api/agents/[id]/sync-session` and `/api/agents/by-slug/[slug]/sync-session` endpoints accept a `summary` string and pass it to Claude for memory extraction. Without auth, anyone can inject arbitrary text into an agent's persistent memory.
- Files: `autonomous-agent-os/src/lib/sync-session.ts`, `autonomous-agent-os/src/app/api/agents/[id]/sync-session/route.ts`, `autonomous-agent-os/src/app/api/agents/by-slug/[slug]/sync-session/route.ts`
- Current mitigation: Summary is truncated to 10,000 characters.
- Recommendations: Add authentication. Validate that the caller is the MCP server or an authorized subagent. Consider signing the sync-session payload.

---

## Performance Bottlenecks

### Unbounded Chat Session Message Growth in SQLite (autonomous-agent-os)
- Problem: The `ChatSession.messages` column stores all messages as a JSON string in SQLite. Each runtime chat turn appends to this array and re-serializes the entire JSON. With tool-use messages (which include full input/output), a 40-turn session could easily reach several megabytes.
- Files: `autonomous-agent-os/src/app/api/runtime/[slug]/chat/route.ts` (lines 115-124), `autonomous-agent-os/prisma/schema.prisma` (ChatSession model)
- Cause: Messages are capped at 40 for the Claude context window (`MAX_HISTORY_MESSAGES`) but ALL messages are stored in the database. There is no pruning of persisted messages.
- Improvement path: Add a hard cap on persisted messages (e.g., keep last 100). Alternatively, move messages to a separate table with individual rows per message rather than a single JSON blob.

### MCP Server Connections Created Per Chat Turn (autonomous-agent-os)
- Problem: `processWithTools()` creates a new `McpClientManager` and connects to all MCP servers on every single chat message. For stdio servers, this means spawning a new process, waiting for initialization, then killing it after the response.
- Files: `autonomous-agent-os/src/lib/runtime/engine.ts` (lines 175-176), `autonomous-agent-os/src/lib/runtime/mcp-client.ts`
- Cause: The engine is stateless per request (Next.js API route pattern). There is no connection pooling or reuse.
- Improvement path: Consider a connection pool that keeps stdio processes alive between requests for the same deployment. For HTTP/SSE transports, this is less of an issue but still wasteful.

### Full Config Serialized Into System Prompt (autonomous-agent-os)
- Problem: The legacy chat endpoint embeds the entire `AgentConfig` as JSON in the system prompt (`JSON.stringify(config, null, 2)`). For agents with many capabilities, triggers, and guardrails, this wastes context window tokens.
- Files: `autonomous-agent-os/src/app/api/chat/route.ts` (line 80)
- Cause: The system prompt includes the full config for Claude to understand the current state.
- Improvement path: Only include config relevant to the current stage. This endpoint may also be legacy (see Tech Debt section).

---

## Fragile Areas

### JSON-in-SQLite Pattern (autonomous-agent-os)
- Files: `autonomous-agent-os/prisma/schema.prisma` (all 6 models), `autonomous-agent-os/src/lib/db.ts`
- Why fragile: 13 columns across 6 models store JSON as `String` in SQLite. Every read requires `JSON.parse()`, every write requires `JSON.stringify()`. There is no schema validation on the stored JSON. A single malformed write (e.g., partial update failure, race condition) corrupts the record.
- Safe modification: Always validate JSON structure before writing. Never construct JSON strings manually -- always use `JSON.stringify()` on a typed object. When adding new JSON fields, update the corresponding TypeScript interface and add test coverage.
- Test coverage: Good coverage for API routes but no dedicated tests for JSON parse failure recovery.

### Shallow Config Merge on PATCH (autonomous-agent-os)
- Files: `autonomous-agent-os/src/app/api/agents/[id]/route.ts` (lines 82-84)
- Why fragile: The PATCH handler uses `{ ...existingConfig, ...body.config }` which is a shallow merge. If a client sends `{ config: { mission: { description: "new" } } }`, it will replace the entire `mission` object, losing `tasks`, `exclusions`, and `audience`. The CLAUDE.md documents this as "PATCH config merges, not replaces" but the merge is only one level deep.
- Safe modification: Use a deep merge utility. Ensure tests cover partial nested updates (e.g., updating `mission.description` without losing `mission.tasks`).
- Test coverage: Tests exist in `tests/api/agents-id.test.ts` but may not cover nested merge scenarios.

### Claude Response JSON Parsing (autonomous-agent-os)
- Files: `autonomous-agent-os/src/lib/claude.ts` (lines 132-161), `autonomous-agent-os/src/app/api/chat/route.ts` (lines 118-132), `autonomous-agent-os/src/app/api/agents/[id]/enrich/route.ts` (lines 68-77), `autonomous-agent-os/src/lib/letta/memory-extract.ts` (lines 41-60)
- Why fragile: Four separate code locations parse Claude's JSON response using the same pattern (strip markdown fences, `JSON.parse`, fallback). If Claude returns unexpected formatting, each location handles the failure differently. The `inferFromDescription` fallback returns a minimal config; the chat route wraps the raw text; the enrichment route returns empty arrays; memory-extract returns empty arrays.
- Safe modification: Centralize JSON-from-Claude parsing into a single utility in `src/lib/claude.ts` with typed generics and a configurable fallback strategy.
- Test coverage: Each location has test coverage for the happy path. Failure paths are tested in some but not all locations.

### Builder Page Component Complexity (autonomous-agent-os)
- Files: `autonomous-agent-os/src/app/agents/[id]/page.tsx` (682 lines)
- Why fragile: This is the largest source file. It manages agent loading, config state, auto-save (debounced PATCH), deployment state, deploy/pause/resume actions, AI enrichment (debounced per-section calls), callout management, test chat dialog, export dialog, and the full builder layout. A change to any of these features risks breaking others.
- Safe modification: Extract deployment management, enrichment management, and auto-save into custom hooks. Consider splitting into sub-components with clearly defined props.
- Test coverage: E2E tests cover the page (`tests/e2e/builder.spec.ts`, 385 lines) but no unit tests for the component's hooks and state logic.

---

## Scaling Limits

### SQLite Single-Writer Constraint (autonomous-agent-os)
- Current capacity: Suitable for single-user/small-team local development.
- Limit: SQLite allows only one concurrent write transaction. Under concurrent runtime chat sessions (multiple deployed agents being used simultaneously), writes to `ChatSession.messages` will serialize, creating a bottleneck.
- Scaling path: The Prisma schema already has an `@prisma/adapter-libsql` dependency. Migrate to PostgreSQL or Turso (LibSQL) for production workloads. The schema uses no SQLite-specific features; all JSON columns are standard strings.

### In-Memory Tool Cache per Request (autonomous-agent-os)
- Current capacity: Works for small numbers of MCP tools.
- Limit: `McpClientManager.listTools()` enumerates all tools from all connected servers on every request. For deployments with many MCP servers or servers that expose hundreds of tools, this adds latency to every chat turn.
- Scaling path: Cache tool definitions at the deployment level (tools don't change between turns for the same deployment).

---

## Dependencies at Risk

### `@letta-ai/letta-client` (autonomous-agent-os)
- Risk: Relatively new SDK with breaking API changes between versions. The codebase uses `agents.blocks.retrieve(label, { agent_id })` and `agents.passages.create()` which may change.
- Impact: Letta integration breaks on SDK updates.
- Migration plan: Pin to exact version. Wrap all Letta SDK calls in the existing `src/lib/letta/` modules (already done) and update only there.

### hazn CLI Dependencies with No Lockfile Sync
- Risk: `hazn/package.json` declares version `0.2.0` but `hazn/package-lock.json` declares `0.1.0`. The lockfile may be stale.
- Impact: `npm ci` may fail or produce inconsistent installs.
- Migration plan: Run `npm install` to regenerate the lockfile.

---

## Missing Critical Features

### No Observability or Structured Logging (autonomous-agent-os)
- Problem: All logging uses `console.error()` and `console.warn()` with ad-hoc message formatting. 65 total `console.*` calls across 32 files. No log levels, no structured output, no request correlation IDs.
- Blocks: Production debugging, error tracking, usage analytics, cost attribution per agent.

### No Input Sanitization for Agent Names or Descriptions (autonomous-agent-os)
- Problem: Agent names and descriptions are accepted with minimal validation (name must be string under 200 chars). HTML, script tags, and other injection vectors are not sanitized. These values are displayed in the UI and included in generated `.md` files.
- Blocks: Safe multi-user deployments. Could lead to XSS if rendered unsafely in the frontend (React auto-escapes by default, but generated markdown files are unprotected).

### No Backup or Export for SQLite Data (autonomous-agent-os)
- Problem: Agent configs, deployment snapshots, and chat sessions live in a single SQLite file (`dev.db`). There is no backup mechanism, no data export endpoint, and no migration path to another database.
- Blocks: Data durability in production. A single file corruption loses all agent configurations and session history.

---

## Test Coverage Gaps

### No Tests for `hazn` CLI (hazn)
- What's not tested: The entire hazn CLI (`hazn/bin/cli.js`, `hazn/src/installer.js`, `hazn/src/help.js`). The `package.json` lists `"test": "node --test"` but `hazn/tests/` only contains `landing.spec.ts` (a Playwright E2E test, not a unit test for the CLI).
- Files: `hazn/bin/cli.js`, `hazn/src/installer.js`, `hazn/src/help.js`
- Risk: Installer could silently break (e.g., file copy failures, CLAUDE.md corruption) with no automated detection.
- Priority: Medium -- the CLI is a published npm package.

### No Unit Tests for Frontend Components (autonomous-agent-os)
- What's not tested: All React components in `autonomous-agent-os/src/components/` and page components in `autonomous-agent-os/src/app/`. The test suite has Zustand store tests and E2E tests but no component-level unit tests using React Testing Library (which is installed as a dev dependency).
- Files: `autonomous-agent-os/src/components/builder/cards/*.tsx`, `autonomous-agent-os/src/components/workspace/**/*.tsx`, `autonomous-agent-os/src/app/agents/[id]/page.tsx`
- Risk: Component-level regressions (state management bugs, event handler errors, conditional rendering issues) are only caught by E2E tests which are slower and less precise.
- Priority: Medium -- E2E tests provide coverage but are slower to run and harder to debug.

### JSON Parse Failure Recovery Not Tested (autonomous-agent-os)
- What's not tested: What happens when `JSON.parse()` receives corrupted database values for `config`, `stages`, `conversations`, or `messages` columns. The outer catch blocks return 500 but there are no tests verifying graceful degradation.
- Files: `autonomous-agent-os/src/app/api/agents/[id]/route.ts`, `autonomous-agent-os/src/app/api/runtime/[slug]/chat/route.ts`
- Risk: Corrupted data in one agent could make all routes for that agent return 500 with no diagnostic information.
- Priority: Low -- unlikely in normal operation but catastrophic when it happens.

### Shallow Merge Edge Cases Not Tested (autonomous-agent-os)
- What's not tested: The PATCH config merge behavior for nested objects. Current tests likely cover top-level field updates but not scenarios like "update mission.description without losing mission.tasks".
- Files: `autonomous-agent-os/tests/api/agents-id.test.ts`
- Risk: Users lose data when partially updating agent configs. The auto-save feature in the builder fires frequently, making this a realistic scenario.
- Priority: High -- this affects the primary editing workflow.

---

*Concerns audit: 2026-03-05*

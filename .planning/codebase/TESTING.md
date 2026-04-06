# Testing Patterns

**Analysis Date:** 2026-03-05

This repository contains two sub-projects. The **Agent OS** project (`autonomous-agent-os/`) has comprehensive testing. The **Hazn CLI** project (`hazn/`) has minimal tests (one Playwright spec for a landing page).

## Test Framework

**Runner (Agent OS):**
- Vitest 4.x for unit and integration tests
- Config: `autonomous-agent-os/vitest.config.ts`
- 480 tests across 38 files

**E2E (Agent OS):**
- Playwright 1.58+ for end-to-end tests
- Config: `autonomous-agent-os/playwright.config.ts`
- 5 spec files in `autonomous-agent-os/tests/e2e/`

**E2E (Hazn CLI):**
- Playwright 1.58+ for landing page tests
- Config: `hazn/playwright.config.ts`
- 1 spec file: `hazn/tests/landing.spec.ts`

**Assertion Library:**
- Vitest built-in `expect` (Jest-compatible API)
- `@testing-library/jest-dom` available in devDependencies
- Playwright `expect` for E2E assertions

**Run Commands:**
```bash
# Agent OS (from autonomous-agent-os/)
npm test                             # Run all Vitest tests
npm run test:watch                   # Vitest watch mode
npx vitest run tests/api/agents.test.ts  # Single test file
npm run test:e2e                     # Playwright E2E (auto-starts dev server)
npm run test:coverage                # Vitest with coverage

# Hazn CLI (from hazn/)
node --test                          # Node.js built-in test runner
npx playwright test                  # Playwright landing page tests
```

## Test File Organization

**Location:** Tests are in a separate `tests/` directory at the project root (not co-located with source).

**Naming:**
- Unit/integration tests: `*.test.ts`
- E2E tests: `*.spec.ts`
- Helper files: no suffix (e.g., `helpers.ts`, `fixtures.ts`, `setup.ts`)

**Directory Structure:**
```
autonomous-agent-os/tests/
├── setup.ts                    # Global mocks (Prisma + Claude)
├── helpers/
│   ├── db.ts                   # Mock Prisma helpers, request/response utils
│   └── fixtures.ts             # Test data factories and constants
├── api/                        # 17 files -- API route handler tests
│   ├── agents.test.ts          # GET/POST /api/agents
│   ├── agents-id.test.ts       # GET/PATCH/DELETE /api/agents/[id]
│   ├── deploy.test.ts          # POST/GET/DELETE/PATCH /api/agents/[id]/deploy
│   ├── chat.test.ts            # POST /api/chat
│   ├── sessions.test.ts        # GET /api/agents/[id]/sessions
│   ├── runtime-chat.test.ts    # POST /api/runtime/[slug]/chat
│   ├── runtime-info.test.ts    # GET /api/runtime/[slug]
│   ├── mcp-servers.test.ts     # CRUD /api/agents/[id]/mcp-servers
│   ├── letta-memory.test.ts    # Letta proxy endpoints
│   ├── claude-code-export.test.ts
│   ├── enrich.test.ts
│   ├── sync-session.test.ts
│   ├── agent-by-slug.test.ts
│   ├── deploy-extended.test.ts
│   ├── templates.test.ts
│   └── test-sandbox.test.ts
├── lib/                        # 8 files -- Library module tests
│   ├── slug.test.ts            # generateSlug()
│   ├── validation.test.ts      # validateAgent()
│   ├── export.test.ts          # Agent export functions
│   ├── enrich-prompts.test.ts  # Enrichment prompt building
│   ├── claude-code-generate.test.ts  # generateAgentMd() etc
│   ├── letta-translate.test.ts # translateToLettaParams()
│   ├── letta-modules.test.ts   # Letta memory/skills modules
│   └── letta-memory-extract.test.ts
├── runtime/                    # 7 files -- Runtime engine tests
│   ├── engine.test.ts          # processMessage()
│   ├── engine-integration.test.ts
│   ├── engine-tools.test.ts    # Tool use loop
│   ├── guardrails.test.ts      # checkPreMessage(), checkPostMessage()
│   ├── prompt.test.ts          # buildRuntimeSystemPrompt()
│   ├── mcp-client.test.ts
│   └── mcp-presets.test.ts
├── stores/                     # 1 file -- Zustand store tests
│   └── stores.test.ts          # useChatStore, useMemoryStore
├── flows/                      # 5 files -- Integration flow tests
│   ├── deploy-and-chat.test.ts
│   ├── redeploy.test.ts
│   ├── pause-resume.test.ts
│   ├── guardrail-enforcement.test.ts
│   └── session-lifecycle.test.ts
└── e2e/                        # 5 files + 1 helper -- Playwright specs
    ├── helpers.ts              # createDeployableAgent(), deleteAgent()
    ├── agent-list.spec.ts
    ├── builder.spec.ts
    ├── deploy.spec.ts
    ├── new-agent.spec.ts
    └── public-chat.spec.ts
```

## Test Structure

**Suite Organization:**
```typescript
// =============================================================================
// Agent OS -- API Tests: /api/agents (GET, POST)
// =============================================================================
// Tests for listing and creating agent projects.
// Spec reference: Section 6 -- API Contracts.
// Source: src/app/api/agents/route.ts
// =============================================================================

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { getMockedPrisma, cleanupDb, createRequest } from '../helpers/db'
import { createMockAgentProject, sampleAgentConfig } from '../helpers/fixtures'

describe('GET /api/agents', () => {
  beforeEach(() => {
    cleanupDb()
  })

  it('returns an empty array when no agents exist', async () => {
    const mocked = getMockedPrisma()
    mocked.agentProject.findMany.mockResolvedValue([])
    const res = await GET(createRequest('GET', 'http://localhost:3000/api/agents'))
    const body = await res.json()
    expect(res.status).toBe(200)
    expect(body).toHaveLength(0)
  })
})
```

**Key conventions:**
- Use `describe` blocks named after the API endpoint or function under test
- Use `it` with descriptive messages starting with a verb
- `beforeEach` calls `cleanupDb()` to reset all mocks
- Sub-sections use `// =========================================================================` dividers within test files

**Patterns:**

**Setup (beforeEach):**
- Always call `cleanupDb()` to reset mock state
- Some test files dynamically import route handlers to catch module load errors:
  ```typescript
  let GET: (req: Request) => Promise<Response>
  beforeEach(async () => {
    cleanupDb()
    const mod = await import('@/app/api/agents/route')
    GET = mod.GET
  })
  ```

**Teardown:**
- `cleanupDb()` resets all mock implementations and re-sets default resolved values
- E2E tests use `afterEach` to delete created agents via API

**Assertion Pattern:**
- Assert on HTTP status first, then body content
- Use `parseResponse<T>()` helper for typed response extraction:
  ```typescript
  const { status, body } = await parseResponse<any>(response)
  expect(status).toBe(200)
  expect(body).toHaveProperty('deployment')
  ```

## Mocking

**Framework:** Vitest `vi.mock()` and `vi.fn()`

**Global Mocks (in `tests/setup.ts`):**
- `@/lib/db` -- Full Prisma client mock with all 6 models and their methods
- `@/lib/claude` -- All 3 exported functions (`chat`, `chatWithTools`, `inferFromDescription`)
- These are loaded automatically via `setupFiles: ['./tests/setup.ts']` in vitest config

**Per-test Mock Overrides:**
```typescript
// Override a global mock for a specific test
const mocked = getMockedPrisma()
mocked.agentProject.findMany.mockResolvedValue([agent1, agent2])

// Override Claude mock
const { inferFromDescription } = await import('@/lib/claude')
vi.mocked(inferFromDescription).mockRejectedValueOnce(new Error('API error'))
```

**Mocking Letta (CRITICAL - known gotcha):**
Letta is NOT globally mocked because it is optional. Mock it per-test-file using inline `vi.fn()` factories. **Do NOT use `vi.hoisted()` destructuring** -- it causes TDZ errors with Vitest 4.x:

```typescript
// CORRECT: Inline vi.fn() in factory
vi.mock("@/lib/letta/client", () => ({
  isLettaEnabled: vi.fn().mockReturnValue(true),
  lettaClient: {
    blocks: { create: vi.fn() },
    agents: { create: vi.fn(), delete: vi.fn() },
  },
}));
import { lettaClient, isLettaEnabled } from "@/lib/letta/client";
const mockIsLettaEnabled = isLettaEnabled as unknown as Mock;

// WRONG: vi.hoisted() destructuring -- causes TDZ errors
// const { mockIsLettaEnabled } = vi.hoisted(() => ({ ... }))  // DO NOT USE
```

**Mocking Runtime Engine (flow tests):**
```typescript
vi.mock('@/lib/runtime/engine', () => ({
  processMessage: vi.fn(),
}))
import { processMessage } from '@/lib/runtime/engine'
const mockedProcessMessage = vi.mocked(processMessage)
```

**What to Mock:**
- Database (Prisma) -- always mocked globally
- External APIs (Anthropic Claude) -- always mocked globally
- Letta client -- mocked per-file when testing Letta features
- Runtime engine -- mocked in flow tests that test API routes calling the engine

**What NOT to Mock:**
- Utility functions (`generateSlug`, `validateAgent`, `buildEnrichmentPrompt`)
- Type definitions and constants
- Pure transformation functions (`translateToLettaParams`, `generateAgentMd`)
- Zustand stores (tested directly via `getState()`/`setState()`)

## Fixtures and Factories

**Test Data (`tests/helpers/fixtures.ts`):**

Comprehensive fixtures aligned with spec examples (Fixie, Helix, Sage, Scout):

```typescript
// Pre-built complete configs
export const sampleAgentConfig: AgentConfig = { /* full Fixie config */ }
export const sampleStageData: StageData = { /* all 6 stages approved */ }
export const incompleteAgentConfig: AgentConfig = { /* missing required fields */ }
export const helixAgentConfig: AgentConfig = { /* second agent for list tests */ }

// Factory functions with overrides pattern
export function createMockAgentProject(overrides: Record<string, unknown> = {}) {
  return {
    id: 'clx1abc2def',
    name: 'Fixie',
    slug: 'fixie',
    config: JSON.stringify(sampleAgentConfig),
    stages: JSON.stringify(sampleStageData),
    // ... defaults ...
    ...overrides,  // Override any field
  }
}

export function createMockDeployment(overrides: Record<string, unknown> = {}) { /* ... */ }
export function createMockChatSession(overrides: Record<string, unknown> = {}) { /* ... */ }
export function createMockTemplate(overrides: Record<string, unknown> = {}) { /* ... */ }
export function createMockHelixProject(overrides: Record<string, unknown> = {}) { /* ... */ }
```

**Database Helpers (`tests/helpers/db.ts`):**

```typescript
// Type-safe access to mocked Prisma
export function getMockedPrisma() { /* returns properly typed mock */ }

// Creates agent AND configures the mock to return it on findUnique
export function createTestAgent(overrides: Record<string, unknown> = {}) { /* ... */ }

// Creates template AND configures the mock
export function createTestTemplate(overrides: Record<string, unknown> = {}) { /* ... */ }

// Resets all mocks and re-sets defaults
export function cleanupDb() { /* ... */ }

// Build a Request object for route handler testing
export function createRequest(bodyOrMethod?, url?, body?, headers?): Request { /* ... */ }

// Parse a Response for assertions
export async function parseResponse<T>(response: Response): Promise<{ status: number; body: T }> { /* ... */ }
```

**E2E Fixtures (`tests/e2e/helpers.ts`):**

```typescript
// Full deployable config constant
export const DEPLOYABLE_CONFIG = { /* all sections filled */ }
export const DEPLOYABLE_STAGES = { /* all stages approved */ }

// Creates an agent via API, patches it with deployable config
export async function createDeployableAgent(request: APIRequestContext): Promise<{ id: string; slug: string }>

// Deletes an agent via API
export async function deleteAgent(request: APIRequestContext, id: string): Promise<void>
```

## Coverage

**Requirements:** None enforced (no coverage thresholds configured)

**View Coverage:**
```bash
npm run test:coverage    # Runs vitest with --coverage flag
```

## Test Types

**Unit Tests (`tests/lib/`, `tests/runtime/`, `tests/stores/`):**
- Test pure functions and modules in isolation
- No database or API calls (all mocked)
- Fast execution
- Example: `slug.test.ts` tests `generateSlug()` with 14 cases covering basic conversion, edge cases, truncation, and spec examples

**API Route Tests (`tests/api/`):**
- Test Next.js route handlers as functions
- Mock Prisma and Claude globally
- Use `createRequest()` to build Request objects
- Assert on HTTP status codes and response body structure
- Route params passed as `{ params: Promise.resolve({ id: '...' }) }` (Next.js 16 pattern)
- Example pattern:
  ```typescript
  const request = createRequest('POST', `http://localhost/api/agents/${agent.id}/deploy`)
  const response = await POST(request as any, { params: Promise.resolve({ id: agent.id }) })
  const { status, body } = await parseResponse(response)
  expect(status).toBe(200)
  ```

**Integration Flow Tests (`tests/flows/`):**
- Test multi-step user journeys across multiple API routes
- Same mock infrastructure as unit tests, but test the composition
- Example: `deploy-and-chat.test.ts` tests Deploy -> Get Info -> Chat -> Follow-up flow
- Verify state consistency across steps (e.g., session tokens, turn counts)

**Store Tests (`tests/stores/`):**
- Test Zustand stores directly via `getState()` and `setState()`
- No React rendering needed -- stores are plain objects
- Reset state in `beforeEach`:
  ```typescript
  beforeEach(() => {
    useChatStore.setState({ messages: [], isStreaming: false, partialContent: '', error: null });
  })
  ```

**E2E Tests (`tests/e2e/`):**
- Playwright with Chromium targeting `http://localhost:3000`
- Auto-starts dev server via `webServer` config
- Create test data via API before each test, clean up in afterEach
- Tests UI interactions: page loading, form filling, navigation, dialog opening
- Use role-based locators (`page.getByRole('button', { name: /deploy/i })`)
- Wait for network idle: `await page.waitForLoadState('networkidle')`
- 5 spec files: agent-list, builder (most comprehensive), deploy, new-agent, public-chat

## Common Patterns

**Async Testing:**
```typescript
it('creates an agent and returns 201', async () => {
  const mocked = getMockedPrisma()
  mocked.agentProject.create.mockResolvedValue(createdAgent)

  const req = createRequest('POST', 'http://localhost:3000/api/agents', { /* body */ })
  const res = await POST(req)
  const body = await res.json()

  expect(res.status).toBe(201)
  expect(body).toHaveProperty('id')
})
```

**Error Testing:**
```typescript
it('returns 404 for unknown agent', async () => {
  // getMockedPrisma().findUnique already returns null by default
  const request = createRequest('POST', 'http://localhost/api/agents/unknown/deploy')
  const response = await POST(request as any, { params: Promise.resolve({ id: 'unknown' }) })
  const { status } = await parseResponse(response)
  expect(status).toBe(404)
})

it('gracefully handles API failure with fallback', async () => {
  vi.mocked(inferFromDescription).mockRejectedValueOnce(new Error('API error'))
  // ... assert fallback behavior, not 500 ...
  expect(res.status).toBe(201)  // Still creates with fallback
})
```

**Mock Verification:**
```typescript
it('calls inferFromDescription with the provided description', async () => {
  await POST(req)
  expect(inferFromDescription).toHaveBeenCalledWith('A research assistant')
})

it('retires existing active deployments', async () => {
  // ... setup and execute ...
  expect(mocked.deployment.update).toHaveBeenCalledWith(
    expect.objectContaining({
      where: { id: 'dep_old' },
      data: { status: 'retired' },
    })
  )
})
```

**Zustand Store Testing:**
```typescript
it('appends a user message with correct role and content', () => {
  useChatStore.getState().addMessage('user', 'Hello')
  const { messages } = useChatStore.getState()
  expect(messages).toHaveLength(1)
  expect(messages[0].role).toBe('user')
  expect(messages[0].content).toBe('Hello')
})
```

**E2E Test Pattern:**
```typescript
test.describe('Builder Page', () => {
  let agentId: string

  test.beforeEach(async ({ request }) => {
    const agent = await createDeployableAgent(request)
    agentId = agent.id
  })

  test.afterEach(async ({ request }) => {
    if (agentId) await deleteAgent(request, agentId)
  })

  test('builder page loads with section cards', async ({ page }) => {
    await page.goto(`/agents/${agentId}`)
    await page.waitForLoadState('networkidle')
    const sections = ['Identity', 'Purpose', 'Audience', 'Workflow', 'Memory Protocol', 'Boundaries']
    for (const section of sections) {
      await expect(page.getByRole('heading', { name: section, level: 3 })).toBeVisible()
    }
  })
})
```

## Writing New Tests

**For a new API route:**
1. Create `tests/api/new-route.test.ts`
2. Add file banner comment with source reference
3. Import helpers: `getMockedPrisma`, `cleanupDb`, `createRequest`, `parseResponse`
4. Import fixtures: `createMockAgentProject`, `sampleAgentConfig`
5. Call `cleanupDb()` in `beforeEach`
6. Import route handlers (direct import or dynamic `await import(...)`)
7. Pass params as `{ params: Promise.resolve({ id: '...' }) }` for dynamic routes
8. Test: happy path, 404, 400 validation, error fallback

**For a new library module:**
1. Create `tests/lib/module-name.test.ts`
2. Import the function directly (it will use globally mocked deps)
3. Test pure behavior with various inputs
4. Include edge cases and boundary conditions

**For a new Zustand store:**
1. Add tests to `tests/stores/stores.test.ts` or create a new file
2. Reset state in `beforeEach` using `store.setState()`
3. Test actions via `store.getState().actionName()`
4. Assert on state via `store.getState()`

**For a new E2E flow:**
1. Create `tests/e2e/feature.spec.ts`
2. Use `createDeployableAgent()` in `beforeEach`
3. Clean up with `deleteAgent()` in `afterEach`
4. Use role-based locators and `waitForLoadState('networkidle')`

---

*Testing analysis: 2026-03-05*

# Coding Conventions

**Analysis Date:** 2026-03-05

This repository is a monorepo containing two sub-projects:
- **Agent OS** (`autonomous-agent-os/`) -- Next.js 16 platform for building AI agents
- **Hazn CLI** (`hazn/`) -- Node.js CLI tool for AI marketing workflows

The Agent OS project is the primary codebase with significant source code and tests. Conventions below are primarily derived from it.

## Naming Patterns

**Files:**
- React components: PascalCase (`SectionCard.tsx`, `IdentityCard.tsx`, `ChatPanel.tsx`)
- Library modules: kebab-case (`mcp-client.ts`, `sync-session.ts`, `memory-extract.ts`)
- API route files: always `route.ts` inside App Router directory structure
- Type definition files: kebab-case (`tools.types.ts`, `types.ts`)
- Test files: kebab-case with `.test.ts` suffix (`agents.test.ts`, `guardrails.test.ts`)
- E2E test files: kebab-case with `.spec.ts` suffix (`builder.spec.ts`, `deploy.spec.ts`)
- Barrel files: `index.ts` for re-exports

**Functions:**
- Use camelCase: `processMessage()`, `checkPreMessage()`, `generateSlug()`
- React components: PascalCase (`SectionCard`, `IdentityCard`)
- Exported factory functions: camelCase with `create` prefix (`createMockAgentProject()`, `createTestAgent()`)
- Boolean-returning functions: `is` prefix (`isLettaEnabled()`)
- Builder/generator functions: descriptive verb prefix (`buildEnrichmentPrompt()`, `generateAgentMd()`)

**Variables:**
- Use camelCase for local variables and parameters
- Use UPPER_SNAKE_CASE for module-level constants: `DEFAULT_MAX_TOOL_ROUNDTRIPS`, `MAX_HISTORY_MESSAGES`, `STAGES`, `SECTION_NAMES`, `ARCHETYPES`
- Use camelCase for exported singletons: `prisma`, `lettaClient`

**Types/Interfaces:**
- Use PascalCase: `AgentConfig`, `MissionConfig`, `RuntimeMessage`
- Suffix with purpose where applicable: `GuardrailCheckResult`, `ProcessMessageResult`, `SessionUpdates`
- Config interfaces: suffix with `Config` (`GuardrailsConfig`, `IdentityConfig`, `CapabilitiesConfig`)
- Props interfaces: suffix with `Props` (`SectionCardProps`, `IdentityCardProps`)

**Database models (Prisma):**
- PascalCase: `AgentProject`, `ChatSession`, `McpServerConfig`, `ToolExecutionLog`
- Use cuid() for IDs: `@id @default(cuid())`

## Code Style

**Formatting:**
- No dedicated Prettier config -- uses ESLint for formatting
- Double quotes for strings in TypeScript source files (consistent across `src/`)
- Single quotes in test files (both are acceptable; test files use single quotes by convention)
- Semicolons: present in source files, optional in test files
- Indentation: 2 spaces
- Trailing commas: used in multi-line constructs

**Linting:**
- ESLint 9 with flat config: `autonomous-agent-os/eslint.config.mjs`
- Extends `eslint-config-next/core-web-vitals` and `eslint-config-next/typescript`
- Test files relax `@typescript-eslint/no-explicit-any` to `off` and `@typescript-eslint/no-unused-vars` to `warn`
- Strict TypeScript: `"strict": true` in `tsconfig.json`

## Import Organization

**Order:**
1. External framework imports (`next/server`, `react`, `zustand`)
2. External library imports (`@anthropic-ai/sdk`, `@prisma/client`, `lucide-react`)
3. Internal path-aliased imports (`@/lib/db`, `@/components/ui/button`)
4. Relative imports (`../SectionCard`, `./fixtures`)
5. Type-only imports (`import type { ... }`)

**Path Aliases:**
- `@/*` maps to `./src/*` (configured in `tsconfig.json` and `vitest.config.ts`)
- Always use `@/` for imports within the `src/` directory -- never use relative paths from `src/`

**Type-Only Imports:**
- Use `import type { ... }` for type-only imports:
  ```typescript
  import type { AgentConfig, StageData } from "@/lib/types";
  import type { RuntimeMessage, ProcessMessageResult } from "./types";
  ```

## Error Handling

**API Routes:**
- Wrap entire handler body in try/catch
- Log errors with `console.error("Context:", error instanceof Error ? error.message : "Unknown error")`
- Return structured error JSON: `NextResponse.json({ error: "Human-readable message" }, { status: 4xx|500 })`
- Use 404 for not found, 400 for validation errors, 500 for unexpected errors
- Pattern:
  ```typescript
  export async function GET(_request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
    try {
      const { id } = await params; // Next.js 16: params is a Promise
      const item = await prisma.model.findUnique({ where: { id } });
      if (!item) {
        return NextResponse.json({ error: "Not found" }, { status: 404 });
      }
      return NextResponse.json(/* mapped response */);
    } catch (error) {
      console.error("Failed to get item:", error instanceof Error ? error.message : "Unknown error");
      return NextResponse.json({ error: "Failed to get item" }, { status: 500 });
    }
  }
  ```

**Library Functions:**
- Throw errors for invalid states (Letta functions throw if `isLettaEnabled()` returns false)
- Return fallback values where graceful degradation is appropriate (e.g., `inferFromDescription` returns a minimal config on parse failure)
- Use `try/finally` for cleanup (e.g., MCP client disconnect in `processWithTools()`)

**Frontend:**
- Silently ignore enrichment errors (non-blocking async operations)
- Use Zustand's `setError(message)` for user-facing errors in chat
- TanStack Query handles retry (1 retry) and stale time (30s)

## JSON Serialization Boundary

**Critical pattern:** SQLite has no native JSON type. All JSON data is stored as `String` columns. The API layer handles serialization at the boundary:
- **Write:** `JSON.stringify(config)` before database operations
- **Read:** `JSON.parse(agent.config)` in API response mapping
- **Never expose raw JSON strings to the frontend**

Follow this pattern:
```typescript
// Writing
await prisma.agentProject.create({
  data: {
    config: JSON.stringify(config),
    stages: JSON.stringify(stages),
  },
});

// Reading
return NextResponse.json({
  config: JSON.parse(agent.config),
  stages: JSON.parse(agent.stages),
});
```

## Logging

**Framework:** `console.error` / `console.log`

**Patterns:**
- Log errors in catch blocks with descriptive context prefix: `console.error("Failed to deploy agent:", ...)`
- Use conditional extraction: `error instanceof Error ? error.message : "Unknown error"`
- No structured logging framework in use

## Comments

**When to Comment:**
- File-level banner comments with `=` divider lines for test files and major modules:
  ```typescript
  // =============================================================================
  // Agent OS -- Test Setup
  // =============================================================================
  // Global mocks for Prisma client and Anthropic SDK.
  // =============================================================================
  ```
- Section dividers within files using `// ──` Unicode box-drawing characters:
  ```typescript
  // ── Constants ────────────────────────────────────────────────────────
  // ── Main entry point ─────────────────────────────────────────────────
  ```
- `// ---------------------------------------------------------------------------` for sub-section dividers in test helpers
- Inline comments for non-obvious business logic
- API route comments above each handler: `// GET /api/agents -- list all agent projects`

**JSDoc/TSDoc:**
- Use JSDoc for exported library functions with `@param`, `@returns`, `@example`:
  ```typescript
  /**
   * Converts an agent name to a URL-safe slug.
   * @param name - The agent name to slugify
   * @returns A URL-safe slug string
   * @example
   * generateSlug("Customer Support Agent") // "customer-support-agent"
   */
  ```
- Skip JSDoc for React components, API routes, and test code

## Function Design

**Size:** Functions are generally compact (10-50 lines). Complex operations are decomposed into named helpers (e.g., `processWithTools` extracts the agentic loop from `processMessage`).

**Parameters:**
- Use typed parameter objects for complex inputs: `options?: { maxTokens?: number }`
- Use union types for flexible inputs: `input: string | { archetype: string; ... }`
- Prefix unused parameters with underscore: `_request: NextRequest`

**Return Values:**
- API routes return `NextResponse.json()` with appropriate status codes
- Library functions return typed results (`ProcessMessageResult`, `ValidationResult`)
- Use discriminated unions for result types (e.g., `GuardrailCheckResult` with `allowed: boolean`)

## Module Design

**Exports:**
- Named exports for all functions and types (no default exports except for Next.js pages/layouts)
- React pages use `export default function PageName()`
- Library modules export specific functions, not classes

**Barrel Files:**
- `src/components/builder/cards/index.ts` re-exports all card components
- `src/lib/prompts/index.ts` exports prompt constants
- Keep barrel files minimal -- only re-export, no logic

## React Component Conventions

**Client Components:**
- Mark with `"use client"` directive at the top of the file
- Use named function exports: `export function ComponentName()`

**Props Pattern:**
- Define interface above the component: `interface ComponentNameProps { ... }`
- Use `extends` for composition: `interface IdentityCardProps extends CalloutHandlers`
- Destructure props in function signature

**State Updates:**
- Use immutable spread pattern for config updates: `onChange({ ...config, ...partial })`
- Internal `update()` helper for partial config merges within card components:
  ```typescript
  function update(partial: Partial<IdentityConfig>) {
    onChange({ ...config, ...partial });
  }
  ```

**Styling:**
- Use `cn()` utility (clsx + tailwind-merge) for conditional class composition
- Tailwind classes directly in JSX
- Dark theme assumed (`html` has `className="dark"`)
- Design tokens via Tailwind: `text-zinc-100`, `bg-zinc-950`, `border-zinc-800`

**Icons:**
- Lucide React for all icons: `import { User, Check, Minus } from "lucide-react"`
- Size via className: `className="h-4 w-4 text-zinc-400"`
- Mark decorative icons with `aria-hidden="true"`

## Next.js 16 Specifics

**Route Params are Promises:**
```typescript
export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  // ...
}
```

**API Response Mapping:**
- Always map database rows to API response objects explicitly -- do not return raw Prisma results
- Parse JSON string columns at the API boundary

**Config:**
- `output: "standalone"` in `next.config.ts` for Docker deployment
- `better-sqlite3` in `serverExternalPackages`

---

*Convention analysis: 2026-03-05*

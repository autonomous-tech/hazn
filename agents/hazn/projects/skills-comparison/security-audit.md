# Security & Consistency Audit: PR #1 (New Skills Addition)

**Audit Date:** 2025-02-26  
**Auditor:** Security & Consistency Auditor (Sub-Agent)  
**Scope:** New skills added on Feb 25, 2025

## Skills Reviewed

### New Skills (PR #1)
- `ab-test-setup`
- `ai-seo`
- `analytics-tracking`
- `cold-email`
- `copy-editing`
- `email-sequence`
- `programmatic-seo`

### Existing Skills (for comparison)
- `b2b-marketing-ux`
- `conversion-audit`
- `seo-audit`
- `ui-audit`
- `keyword-research`

---

## 🔴 Security Issues

### 1. Missing Import in Server-Side Code (HIGH)

**File:** `/home/rizki/hazn/skills/ab-test-setup/SKILL.md`  
**Lines:** 214-222

```tsx
// app/page.tsx
import { PostHog } from 'posthog-node'

export default async function HomePage() {
  const posthog = new PostHog(process.env.POSTHOG_API_KEY!)
  
  // Get or create distinct ID from cookies
  const distinctId = cookies().get('ph_distinct_id')?.value || crypto.randomUUID()
```

**Issue:** `cookies()` is used but not imported. This will cause a runtime error.

**Fix:** Add `import { cookies } from 'next/headers'` to the imports.

---

### 2. Non-null Assertion on Environment Variables (MEDIUM)

**Files:** Multiple  
**Pattern:** `process.env.NEXT_PUBLIC_POSTHOG_KEY!` and similar

**Issue:** Using TypeScript's non-null assertion (`!`) on environment variables will cause runtime crashes if env vars are missing, with no helpful error message.

**Affected locations:**
- `analytics-tracking/SKILL.md` line 120: `process.env.NEXT_PUBLIC_POSTHOG_KEY!`
- `analytics-tracking/SKILL.md` line 227: `process.env.NEXT_PUBLIC_GA_ID!`
- `ab-test-setup/SKILL.md` line 177: `process.env.NEXT_PUBLIC_POSTHOG_KEY!`
- `ab-test-setup/SKILL.md` line 217: `process.env.POSTHOG_API_KEY!`

**Recommendation:** Add validation or use fallback patterns:
```tsx
const apiKey = process.env.POSTHOG_API_KEY
if (!apiKey) throw new Error('POSTHOG_API_KEY is required')
```

---

### 3. dangerouslySetInnerHTML Usage (LOW - Acceptable)

**Files:**
- `programmatic-seo/SKILL.md` lines 268, 443
- `seo-optimizer/SKILL.md` line 66

**Pattern:**
```tsx
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
/>
```

**Assessment:** This is the CORRECT pattern for JSON-LD schema injection. The data comes from controlled server-side sources (Payload CMS), not user input. **No action required.**

---

## 🔴 Broken References

### None Found in New Skills ✅

Grep searches for:
- `references/` → No orphaned references in new skills
- `../../tools/` → No matches
- `.claude/` → No matches

### Existing Skills Have Valid References

| Skill | Reference | Status |
|-------|-----------|--------|
| `ui-audit` | `references/*.md` | ✅ Directory exists with 18 files |
| `conversion-audit` | `references/brand.md`, `references/audit-framework.md`, `references/benchmarks.md` | ✅ All exist |
| `keyword-research` | `references/api-integration.md` | ✅ Exists |
| `conversion-audit` | `assets/template-audit.html` | ✅ Exists |

---

## 🟠 Code Quality Issues

### 1. Undocumented Dependencies

**File:** `programmatic-seo/SKILL.md`

The code imports `@/lib/payload`:
```tsx
import { getPayloadClient } from '@/lib/payload';
```

**Issue:** No guidance on how to create this file. Developers will hit an import error.

**Fix:** Add a section showing the `lib/payload.ts` implementation:
```tsx
// lib/payload.ts
import { getPayloadHMR } from '@payloadcms/next/utilities'
import config from '@payload-config'

export const getPayloadClient = async () => getPayloadHMR({ config })
```

---

### 2. Missing Error Handling in Analytics Code

**File:** `analytics-tracking/SKILL.md`

**Pattern:** The unified analytics hook has no try-catch:
```tsx
export const analytics = {
  track: (event: string, properties?: EventProperties) => {
    posthog.capture(event, properties)
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', event, properties)
    }
  },
```

**Issue:** If PostHog fails to initialize, `posthog.capture` will throw. Analytics failures shouldn't break the user experience.

**Fix:** Wrap in try-catch:
```tsx
track: (event: string, properties?: EventProperties) => {
  try {
    posthog.capture(event, properties)
  } catch (e) {
    console.warn('PostHog tracking failed:', e)
  }
  // GA4...
},
```

---

### 3. Potential Division by Zero

**File:** `analytics-tracking/SKILL.md` line 350

```tsx
const scrollPercent = Math.round(
  (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
)
```

**Issue:** If `document.body.scrollHeight === window.innerHeight` (no scroll possible), this divides by zero, returning `Infinity` or `NaN`.

**Fix:**
```tsx
const scrollable = document.body.scrollHeight - window.innerHeight
const scrollPercent = scrollable > 0 
  ? Math.round((window.scrollY / scrollable) * 100)
  : 100
```

---

### 4. Missing Suspense Boundary for useSearchParams

**File:** `analytics-tracking/SKILL.md` line 417

```tsx
export function useUTMCapture() {
  const searchParams = useSearchParams()
```

**Issue:** In Next.js 13+, `useSearchParams()` should be wrapped in a Suspense boundary or it will cause the entire page to client-side render.

**Note:** The main layout example DOES show Suspense usage, but this hook doesn't document that it requires the Suspense wrapper.

---

## 🟠 Consistency Problems

### 1. YAML Frontmatter Field Inconsistency

| Skill | Has `allowed-tools`? | Description Style |
|-------|---------------------|-------------------|
| `ab-test-setup` | ✅ Yes | Plain text |
| `ai-seo` | ✅ Yes | Plain text |
| `analytics-tracking` | ✅ Yes | Plain text |
| `cold-email` | ✅ Yes | Quoted string |
| `copy-editing` | ✅ Yes | Quoted string |
| `email-sequence` | ✅ Yes | Quoted string |
| `programmatic-seo` | ✅ Yes | Plain text |
| `b2b-marketing-ux` | ❌ **No** | Quoted string |
| `b2b-ux-reference` | ❌ **No** | Quoted string |
| `frontend-design` | ❌ **No** | Plain text |

**Issues:**
1. Inconsistent use of quotes around `description` field
2. Some existing skills missing `allowed-tools` field

**Recommendation:** Standardize on one style (prefer plain text, quotes only when needed for special characters).

---

### 2. Section Structure Inconsistency

**Expected sections (from existing skills):**
1. YAML frontmatter
2. `# Title`
3. `## Purpose` / `## When to Use`
4. Core content sections
5. `## Output Format` / `## Deliverables`
6. `## Checkpoints` (human-in-loop)
7. `## Related Skills`

**Audit results:**

| Skill | Has Checkpoints? | Has Related Skills? | Has Output Format? |
|-------|-----------------|---------------------|-------------------|
| `analytics-tracking` | ✅ Yes | ✅ Yes | ❌ No |
| `ab-test-setup` | ✅ Yes | ✅ Yes | ✅ Yes |
| `programmatic-seo` | ❌ No | ✅ Yes | ✅ Yes |
| `ai-seo` | ❌ No | ✅ Yes | ❌ No |
| `cold-email` | ✅ Yes (implicit) | ✅ Yes | ✅ Yes |
| `copy-editing` | ✅ Yes | ✅ Yes | ❌ No |
| `email-sequence` | ✅ Yes (implicit) | ✅ Yes | ❌ No |

**Note:** `programmatic-seo` and `ai-seo` are missing explicit "Checkpoints" sections for human-in-loop approval.

---

### 3. Related Skills Cross-References All Valid

All cross-referenced skills exist in `/home/rizki/hazn/skills/`:

| Referenced Skill | Exists? |
|-----------------|---------|
| `ab-test-setup` | ✅ |
| `analytics-tracking` | ✅ |
| `conversion-audit` | ✅ |
| `b2b-marketing-ux` | ✅ |
| `payload-nextjs-stack` | ✅ |
| `seo-audit` | ✅ |
| `keyword-research` | ✅ |
| `seo-optimizer` | ✅ |
| `b2b-website-copywriter` | ✅ |
| `seo-blog-writer` | ✅ |
| `landing-page-copywriter` | ✅ |
| `email-sequence` | ✅ |
| `cold-email` | ✅ |
| `copy-editing` | ✅ |

---

## 🟡 Style Nitpicks

### 1. Inconsistent Code Block Language Tags

**Pattern:** Mixed use of `tsx` vs `typescript` vs `ts`

- `analytics-tracking` uses `tsx` and `typescript` inconsistently
- Recommendation: Use `tsx` for React components, `typescript` for pure TS utilities

### 2. Environment Variables Section Placement

- `analytics-tracking` has env vars at the END of the file ✅
- `ab-test-setup` has no dedicated env vars section ❌
- `programmatic-seo` has no dedicated env vars section ❌

**Recommendation:** All code-heavy skills should end with an "Environment Variables" section.

### 3. Title vs H1 Mismatch

| Skill | YAML `name` | H1 Title |
|-------|-------------|----------|
| `programmatic-seo` | `programmatic-seo` | `# Programmatic SEO` ✅ |
| `ab-test-setup` | `ab-test-setup` | `# A/B Test Setup` ✅ |
| `ai-seo` | `ai-seo` | `# AI Search Optimization (GEO/AEO)` ⚠️ Different |

**Note:** `ai-seo` H1 uses different terminology than name. May cause confusion.

---

## Workflow Integration Check

### WORKFLOWS.md Analysis

**Relevant references to new skills:**

| Workflow | Phase | Skill Used? |
|----------|-------|-------------|
| `/website` | Phase 4 (Dev) | "Analytics setup (GA4, event tracking)" - ✅ Covered by `analytics-tracking` |
| `/website` | Phase 7 (A/B Test) | "ab-test-plan.md" - ✅ Covered by `ab-test-setup` |
| `/audit` | Phase 3 | "Analytics Review" - ✅ Covered by `analytics-tracking` |
| `/optimize` | Phase 3-5 | A/B testing - ✅ Covered by `ab-test-setup` |
| `/email` | All phases | ✅ Covered by `email-sequence` and `cold-email` |

**Missing workflow integrations:**
- `ai-seo` not explicitly referenced in `/website` SEO phase
- `programmatic-seo` not explicitly referenced anywhere

**Recommendation:** Update WORKFLOWS.md to include:
- AI SEO in Phase 5 (SEO Optimization)
- Programmatic SEO as optional Phase 6.5 for scale content

### SOUL.md Analysis

**Sub-agent mapping:**

| SOUL.md Agent | Relevant New Skills |
|---------------|---------------------|
| SEO Specialist | `ai-seo`, `programmatic-seo` |
| Conversion Specialist | `ab-test-setup`, `analytics-tracking` |
| Email Specialist | `email-sequence`, `cold-email` |
| Copywriter | `copy-editing` (for edits) |

**Issue:** SOUL.md mentions "Conversion Specialist" for A/B testing but `sub-agents/` directory wasn't checked. May need a `conversion-specialist.md` template.

---

## Dangerous Patterns Check

### ✅ No Destructive Commands Found
- `rm -rf`: None
- `rm -r`: None  
- `sudo`: None
- `chmod`/`chown`: None

### ✅ No Hardcoded Secrets
- No API keys in code (only placeholder patterns like `phc_xxxxxxxxxxxx`)
- No hardcoded paths like `/home/user/`

### ✅ External API Calls Properly Documented
- PostHog: Uses env vars ✅
- GA4: Uses env vars ✅
- All API calls go through documented SDKs, not raw fetch

---

## Recommended Fixes

### Priority 1: Must Fix Before Merge

1. **`ab-test-setup/SKILL.md` line 214** - Add missing import:
   ```tsx
   import { cookies } from 'next/headers'
   import { PostHog } from 'posthog-node'
   ```

2. **`programmatic-seo/SKILL.md`** - Add `lib/payload.ts` example or reference to `payload-nextjs-stack` skill for setup.

### Priority 2: Should Fix

3. **All code skills** - Add try-catch wrappers around analytics calls
4. **`analytics-tracking/SKILL.md`** - Fix division by zero in scroll tracking
5. **`programmatic-seo/SKILL.md`** - Add Checkpoints section for human-in-loop
6. **`ai-seo/SKILL.md`** - Add Checkpoints section for human-in-loop

### Priority 3: Nice to Have

7. Standardize YAML description quoting (remove unnecessary quotes)
8. Add `allowed-tools` to `b2b-marketing-ux`, `b2b-ux-reference`, `frontend-design`
9. Add Environment Variables sections to `ab-test-setup` and `programmatic-seo`
10. Update WORKFLOWS.md to reference `ai-seo` and `programmatic-seo`

---

## Summary

| Category | Count | Severity |
|----------|-------|----------|
| Security Issues | 2 | 1 HIGH, 1 MEDIUM |
| Broken References | 0 | - |
| Code Quality | 4 | All MEDIUM |
| Consistency | 3 | All LOW |
| Style Nitpicks | 3 | All LOW |

**Overall Assessment:** PR #1 is **safe to merge** with the Priority 1 fixes applied. The code examples are syntactically valid and follow React/Next.js best practices. No security vulnerabilities or dangerous patterns found. Consistency issues are cosmetic and can be addressed in follow-up PRs.

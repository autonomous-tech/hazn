---
name: jwd-audit
description: "Deterministic 3-phase UI audit with human-in-the-loop self-correction. Phase 2 audits pages against GROUND-TRUTH.md rules. Phase 3 learns from human-reported visual breaks."
---

# UI Audit Workflow — Deterministic & Self-Improving

## System Guarantee

```
audit → fix → re-audit = ZERO new findings
```

If re-audit finds new issues, the workflow has a bug. Report it.

## Rule Authority (what you check against)

1. `GROUND-TRUTH.md` — auto-extracted from codebase (typography, colors, components, structural rules, responsive patterns)
2. `LEARNED-RULES.md` — human-reported corrections (equal authority, additive)
3. `references/element-roles.md` — exhaustive per-role property rules (the lookup table)

You may ONLY flag violations of rules in these three files. No rule citation = no finding.

---

# PHASE 2: PAGE AUDIT (triggered by /gsd:ui-audit <route>)

Execute steps A through H in order. Complete each step fully before moving to the next.

## Step A: Map Components

1. Look up the route in `references/page-inventory.md`
2. Find the template file and ALL components it renders
3. Output a numbered list of every file path

```
COMPONENTS FOR /marketing/:
1. frontend/src/components/templates/MarketingPageTemplate.tsx
2. frontend/src/components/sections/ServiceHeroDark.tsx
3. frontend/src/components/sections/ThreeDoorsSection.tsx
...
```

**CHECKPOINT:** Do you have every component file listed? If unsure, grep for imports in the template.

---

## Step B: Grep Pattern Scan

Run ALL 16 grep checks below against the component files from Step A. No skipping.

```bash
# 1. Manual eyebrow (must use EyebrowLabel)
grep -rn 'font-mono.*uppercase\|tracking-wider.*uppercase\|tracking-widest.*uppercase' [FILES] | grep -v EyebrowLabel | grep -v 'globals.css'

# 2. Raw Link/a as button (must use Button)
grep -rn '<Link[^>]*className="[^"]*bg-vermillion' [FILES] | grep -v 'Button'
grep -rn '<a [^>]*className="[^"]*bg-vermillion' [FILES] | grep -v 'Button'

# 3. Text arrows (must be SVG)
grep -rn '→\|&rarr;\|&#8594;' [FILES] | grep -v 'Button.tsx' | grep -v '\.replace(' | grep -v '\.md'

# 4. Old span+group-hover arrow
grep -rn 'group-hover:translate-x' [FILES]

# 5. Inline fontFamily styles
grep -rn 'fontFamily' [FILES]

# 6. Raw oversized text (must use design system)
grep -rn 'text-5xl\|text-6xl\|text-7xl\|text-8xl' [FILES] | grep -v 'hero-headline\|section-headline'

# 7. Wrong card radius
grep -rn 'rounded-3xl' [FILES]

# 8. Raw <img> tags
grep -rn '<img ' [FILES]

# 9. CSS cascade violations
grep -n '^h[1-6]\|^body\|^html' frontend/src/app/globals.css | grep -v '@layer'

# 10. Wrong nav breakpoint
grep -rn 'md:hidden\|md:flex\|md:block' [FILES] | grep -i 'nav\|mobile\|hamburger\|drawer'

# 11. CTA text without stripCtaArrow
grep -rn '{.*cta_text\|{.*cta_label' [FILES] | grep -v stripCtaArrow | grep -v 'const \|interface\|type \|//\|\.d\.ts\|replace'

# 12. Inline .replace() arrow stripping
grep -rn '\.replace.*→' [FILES] | grep -v 'cta-utils'

# 13. Hardcoded text arrows in JSX
grep -rn '} →\|} →' [FILES]

# 14. FAQ font inconsistency
grep -rn 'font-display.*text-lg.*font-semibold' [FILES] | grep -i 'faq\|question\|accordion'

# 15. Badge overflow (missing flex-shrink-0)
grep -rn 'ml-auto' [FILES] | grep -v 'flex-shrink-0'

# 16. EyebrowLabel unsupported color
grep -rn 'EyebrowLabel' [FILES] | grep 'color=' | grep -v 'vermillion\|caption\|white\|gold\|ocean\|indigo'
```

Log all matches. These are preliminary findings — Step C is the primary audit.

---

## Step C: Role-Based Element Audit (THE CORE)

For EACH component from Step A, in order:

### C.1 — Read the full file (every line)

### C.2 — List every visible JSX element
Include: headings (`h1`–`h6`), text (`p`, `span`), links/buttons (`a`, `Link`, `Button`), sections, cards (divs with bg/shadow/rounded), images (`Image`, `img`), icons (`svg`).
Skip: purely structural wrappers, conditional null returns.

### C.3 — Classify each element into ONE role
Use `references/element-roles.md` as the lookup. Every element gets a role:
`hero-heading`, `section-heading`, `card-title`, `eyebrow`, `body-text`, `muted-text`, `stat-value`, `stat-label`, `cta-primary`, `cta-secondary`, `cta-text`, `cta-group`, `card`, `page-section`, `section-inner`, `header-group`, `grid-layout`, `inline-row`, `image-hero`, `image-content`, `decorative`, `arrow-icon`, `nav-item`, `footer-link`, `process-steps`

### C.4 — Check each element against its role's rules
For every mandatory property in the role definition, check actual code. Record:

```
| Line | Element | Role | Property | Expected | Actual | Verdict |
```

### C.5 — Dark Background Sweep
For every section/wrapper with `bg-ink`, `bg-midnight`, `bg-vermillion`, `bg-indigo`, or dark gradient:
- List ALL text elements inside
- Verify each has explicit light text color (`text-white`, `text-white/*`, `text-parchment`, etc.)
- Inheritance counts ONLY if a parent explicitly sets text color on children
- Any text that would inherit `text-ink` or `text-prose` on dark bg = 🔴

### C.6 — Output component summary

```
ComponentName.tsx: ✅ all checks pass (N elements, M properties)
```
or:
```
ComponentName.tsx: 3 findings
  🔴 L42  h2 [section-heading] css-class: expected section-headline, actual text-3xl font-bold
  🟡 L78  Link [cta-secondary] arrow: expected SVG, actual text →
  🟡 L95  div [cta-group] responsive-justify: expected justify-center lg:justify-start, missing
```

**EVERY component MUST have a summary line.** No exceptions.

---

## Step D: Responsive Analysis

For each component with grid/flex layout:

1. **Breakpoint trace:** Walk 375px → sm → md → lg → xl. At each: does content fit? Do columns have room?
2. **Asymmetric layout check:** If hero/2-col with image → verify ALL THREE responsive patterns:
   - `text-center lg:text-left`
   - `mx-auto lg:mx-0`
   - `justify-center lg:justify-start`
3. **Content squeeze:** CTA buttons at narrowest column — will text wrap to 3+ lines? Badges with `flex-wrap`?
4. **Spacing hierarchy:** On mobile stack, is gap within groups < gap between groups?

---

## Step E: Check LEARNED-RULES.md

Read `LEARNED-RULES.md`. For each rule with a detection method, run that check against this page's components. Any match = finding at the specified severity.

---

## Step F: Compile Findings & Confidence Gate

Merge ALL findings from Steps B, C, D, E into one table:

```
| # | Sev | Component | Line | Role | Property | Expected | Actual | Fix |
```

**Severity:**
- 🔴 MUST FIX — wrong font class, invisible text, missing overflow, raw img, text arrows, broken responsive
- 🟡 SHOULD FIX — missing responsive alignment, wrong spacing, raw Link as button, wrong radius, hardcoded copy
- 🟢 NOTE — minor, works fine, never auto-fixed

**If zero 🔴 and zero 🟡:** Report clean. Update TRACKER.md. STOP.

**If any 🔴 or 🟡:** Show findings table, then say:

> **Found X issues (Y 🔴, Z 🟡).**
>
> ⏸️ **VISUAL INSPECTION REQUIRED**
>
> Before I fix these, please manually check the rendered page at:
> - **Desktop** (1440px+)
> - **Tablet** (768px)
> - **Mobile** (375px)
>
> Look for: invisible text, overlapping elements, broken layouts, text overflow, wrong colors, missing images, alignment issues.
>
> Reply:
> - **"go"** — fix the code findings above
> - **"go + [your visual findings]"** — fix code findings AND I'll add your visual issues
> - **"[visual findings only]"** — you found issues I missed → triggers Phase 3 learning
> - **"skip"** — discard all

**STOP. Wait for human response.**

---

## Step G: Fix

1. **Pre-fix safety:** `git diff -- [FILE]` — skip files with uncommitted changes from other sessions
2. **Apply fixes** for all 🔴 and 🟡. Reference the fix patterns in GROUND-TRUTH.md §4–§8.
3. **Re-audit (mandatory):** Re-read every changed file. Re-run grep checks + role checks on changed components. Every previous finding must now be ✅. Fix any regressions. Loop until clean.

---

## Step H: Review & Commit

1. Show diff summary table (file → what changed)
2. Ask for approval: `approved` / `show diff [file]` / `revert [file]` / `skip`
3. On `approved`:
   - `git add [changed files only]` (NEVER `git add .`)
   - Commit: `fix(ui): [route] — [summary]`
   - Update `TRACKER.md`
   - Confirm with hash

---

# PHASE 3: SELF-CORRECTION (triggered by /gsd:ui-audit-learn)

When a human reports a visual break the audit missed:

## Input Required
1. **Component:** file path or HTML snippet
2. **Screen size:** mobile (375px) / tablet (768px) / desktop (1440px)
3. **Description:** what broke visually

## Step 1: Diagnose

Read the component. Identify the exact CSS/JSX causing the visual break.

## Step 2: Fix

Output the corrected code. Apply it.

## Step 3: Classify the Miss

Answer these questions:
1. **Which existing rule SHOULD have caught this?** (cite rule ID from GROUND-TRUTH or element-roles)
2. **If no existing rule covers it:** This is a NEW rule class.
3. **Why did the audit miss it?** (grep gap? role rule incomplete? edge case in responsive check? dark bg inheritance?)

## Step 4: Write the Learned Rule

Append a new entry to `LEARNED-RULES.md`:

```markdown
### LR-{NNN}: {Short title}
- **Date:** {today}
- **Route:** {page where found}
- **Screen size:** {mobile/tablet/desktop}
- **What was missed:** {description}
- **Root cause:** {which rule gap — be specific}
- **Detection method:** {ONE of: grep pattern | role-check addition | responsive-check addition}
  ```
  {exact grep command or code-level check to add}
  ```
- **Severity:** 🔴 / 🟡
- **Fix pattern:** {exact code change}
```

Increment the `<!-- NEXT_ID: LR-NNN -->` counter at the bottom of the file.

## Step 5: Verify Integration

Run the NEW detection method against the current page. It MUST flag the issue that was just fixed (proving the rule works). Then confirm the fix resolves it.

---

# PHASE 1: INITIALIZATION (triggered by /gsd:ui-audit-init)

One-time setup. Regenerates `GROUND-TRUTH.md` from codebase sources.

## Step 1: Extract Typography
Read `frontend/src/app/globals.css`. Extract all classes in `@layer components` that define font properties. Record class name, font family, size, weight, line-height.

## Step 2: Extract Color Palette
Read `@theme` block in globals.css. Record all color tokens with hex values. Flag which are dark backgrounds (require light text inside).

## Step 3: Extract Component APIs
Read every file in `frontend/src/components/ui/`. Record: component name, props interface, variant union types, default values, auto-behaviors (like Button text variant auto-appending arrow).

## Step 4: Extract Utility APIs
Read `frontend/src/lib/cta-utils.ts`, `frontend/src/lib/bg-styles.ts`. Record function signatures, what they do, when they must be used.

## Step 5: Extract Structural Rules
Read base styles in `@layer base`. Record element defaults (body font, heading font, colors).

## Step 6: Mine Git History
```bash
git log --all --grep="fix(ui)" --format="%H %s%n%b"
```
For each commit:
- Classify the fix pattern (eyebrow, arrow, responsive, typography, structural)
- Extract the rule it implies
- Count frequency per pattern

## Step 7: Cross-Validate
For each extracted rule, verify it doesn't contradict `references/element-roles.md` or `references/design-system.md`. Flag conflicts for human resolution.

## Step 8: Write GROUND-TRUTH.md
Overwrite `GROUND-TRUTH.md` with the structured extraction. Do NOT modify `LEARNED-RULES.md` (those are human-authored).

---

# Scope Rules

- **One page per audit** — never mix pages in one commit
- **Shared components** — fix during first page that uses them, note in commit
- **Parallel sessions** — `git diff` before editing, skip if modified
- **Already-audited pages** — check TRACKER.md, skip unless user says "re-audit"
- **🟢 items** — never auto-fixed, log only
- **Out of scope:** copy quality, SEO, performance, TypeScript patterns, backend/API, refactoring suggestions

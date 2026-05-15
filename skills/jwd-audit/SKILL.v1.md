---
name: jwd-audit
description: "Deterministic UI audit — role-based element-by-element verification against Editorial Warmth v2. Checks every element's font, color, spacing, alignment, and responsive behavior. Inputs: page route + approve/reject."
---

# UI/UX Page Audit Workflow (Role-Based Element Audit)

## Why This Approach

Grep pattern-matching only catches what it's coded to find. Real UI issues are about **relationships** — does this heading use the right class *for this page type*? Does this CTA group have the right alignment *for this layout context*? Is this text visible *against its background*?

This workflow uses a mechanical, role-based audit. Every rendered element is classified by its design role, and every role has binary pass/fail rules. No judgment calls.

## Core Guarantee

```
audit page → fix findings → audit same page again → zero findings
```

If the second audit finds new issues, the workflow is broken. This guarantee is enforced by:
1. Exhaustive element enumeration (no skipping)
2. Fixed rules per role (no subjective assessment)
3. Mandatory post-fix re-audit (catch regressions)

---

## Phase 1: AUDIT

### Step 1.1: Identify Page Components

1. Determine the **route** (e.g., `/marketing/`)
2. Look up in [page inventory](references/page-inventory.md) to find template and rendering mode
3. List EVERY component file the page renders — templates, shared components, UI components
4. Output the list: one file path per line

### Step 1.2: Layer 1 — Automated Pattern Scan (Pre-Filter)

Run these grep checks against the page's component files. These catch obvious text-level issues fast. Replace `[FILES]` with space-separated paths.

```bash
# 1. Manual eyebrow styling (must use <EyebrowLabel>)
grep -rn 'font-mono.*uppercase\|tracking-wider.*uppercase\|tracking-widest.*uppercase' [FILES] | grep -v EyebrowLabel | grep -v 'globals.css'

# 2. Raw <Link>/<a> styled as vermillion button (must use <Button>)
grep -rn '<Link[^>]*className="[^"]*bg-vermillion' [FILES] | grep -v 'Button'
grep -rn '<a [^>]*className="[^"]*bg-vermillion' [FILES] | grep -v 'Button'

# 3. Text arrows (must be SVG except inside Button text variant)
grep -rn '→\|&rarr;\|&#8594;' [FILES] | grep -v 'Button.tsx' | grep -v '\.replace(' | grep -v '\.md'

# 4. Old span+group-hover arrow pattern
grep -rn 'group-hover:translate-x' [FILES]

# 5. Inline fontFamily styles (must use CSS classes)
grep -rn 'fontFamily' [FILES]

# 6. Raw oversized text classes (must use design system classes)
grep -rn 'text-5xl\|text-6xl\|text-7xl\|text-8xl' [FILES] | grep -v 'hero-headline\|section-headline'

# 7. Wrong card border radius
grep -rn 'rounded-3xl' [FILES]

# 8. Raw <img> tags (must use next/image)
grep -rn '<img ' [FILES]

# 9. CSS cascade layer violations
grep -n '^h[1-6]\|^body\|^html' frontend/src/app/globals.css | grep -v '@layer'

# 10. Wrong nav breakpoint (must be min-[930px], not md:)
grep -rn 'md:hidden\|md:flex\|md:block' [FILES] | grep -i 'nav\|mobile\|hamburger\|drawer'

# ── CROSS-CUTTING CONVENTION CHECKS (added from branch audit learnings) ──

# 11. CTA text rendered without stripCtaArrow() protection
# ANY {cta_text}, {primary_cta_text}, {secondary_cta_text}, {footer_cta_text},
# {hero_cta_primary_text}, {hero_cta_secondary_text} MUST be wrapped in stripCtaArrow().
# CMS editors and seed data may include trailing text arrows (→) in CTA labels.
# Templates render SVG arrows separately — text arrows cause "double arrow" bugs.
grep -rn '{.*cta_text\|{.*cta_label' [FILES] | grep -v stripCtaArrow | grep -v 'const \|interface\|type \|//\|\.d\.ts\|replace'

# 12. Inline .replace() arrow stripping (must use shared stripCtaArrow from @/lib/cta-utils)
# Scattered inline .replace(/→/, "") is fragile and inconsistent.
grep -rn '\.replace.*→' [FILES] | grep -v 'cta-utils'

# 13. Hardcoded text arrows appended in JSX (e.g., {text} →)
# Template code must NEVER append " →" in JSX — SVG arrows come from the component pattern.
grep -rn '} →\|} →' [FILES]

# 14. FAQ font consistency (question: text-base md:text-lg font-medium text-ink, answer: text-sm md:text-base text-prose)
# All FAQ implementations must match this standardized pattern.
grep -rn 'font-display.*text-lg.*font-semibold' [FILES] | grep -i 'faq\|question\|accordion'

# 15. Badge overflow safety (flex badges must have whitespace-nowrap + flex-shrink-0)
# Inline status badges (e.g., "Active Partner") inside flex rows must not wrap.
grep -rn 'ml-auto' [FILES] | grep -v 'flex-shrink-0'

# 16. Missing EyebrowLabel color variant
# If a section eyebrow uses a color not in EyebrowLabel's type union, flag as blocker.
# Current supported colors: vermillion, caption, white, gold, ocean, indigo
grep -rn 'EyebrowLabel' [FILES] | grep 'color=' | grep -v 'vermillion\|caption\|white\|gold\|ocean\|indigo'
```

Log matches. These feed into the findings table but are NOT the main audit.

### Step 1.3: Layer 2 — Role-Based Element Audit (PRIMARY)

**This is the core audit. This catches what grep cannot.**

For EACH component file:

#### A. READ the full file

Not a skim. Every line. Pay attention to every `className=`, every `style={}`, every JSX element.

#### B. ENUMERATE visible elements

List every JSX element that renders a visible DOM node. Skip:
- Wrapper `<div>`s that are purely structural (no visible border, bg, text)
- Conditional returns (`if (!value) return null`)
- Map function scaffolding

Include:
- Every `<h1>` through `<h6>`
- Every `<p>`, `<span>` with text content
- Every `<a>`, `<Link>`, `<Button>` (CTAs, links)
- Every `<section>` (wrapper)
- Every `<div>` that is a card, grid, flex container with semantic purpose
- Every `<Image>`, `<img>`
- Every `<svg>` that serves as an icon or arrow

#### C. CLASSIFY each element

Assign exactly ONE role from the [Element Roles & Rules](references/element-roles.md) reference. The role determines what to check.

#### D. CHECK against role rules

For each element + role, check EVERY mandatory property listed in the role definition. Record:

```
| Line | Element | Role | Property | Expected (per rule) | Actual (in code) | ✅/🔴/🟡 |
```

**You MUST produce this table for every component.** A component with no table rows means you skipped it. Go back.

**Minimum checks per component** (if the component has these elements):
- [ ] Every `<h1>`: correct hero-headline-* class for THIS page type
- [ ] Every `<h2>`: has `section-headline` class
- [ ] Every `<h3>`/`<h4>` inside a card: uses DM Sans (no `font-display`)
- [ ] Every eyebrow: uses `<EyebrowLabel>` component (see classification rule below)
- [ ] Every `<section>`: correct padding, overflow-hidden if has absolute children
- [ ] Every inner container: has `max-w-* mx-auto px-6`
- [ ] Every CTA/button: uses `<Button>` or correct inline-flex pattern, SVG arrows only
- [ ] Every CTA text from CMS: wrapped in `stripCtaArrow()` from `@/lib/cta-utils`
- [ ] Every stat value: uses Fraunces (`font-display`)
- [ ] Every card: `rounded-2xl`
- [ ] Every image: uses `next/image`, has width/height/sizes, priority on hero
- [ ] Every text on dark bg: has explicit light color (text-white, text-white/60, etc.)
- [ ] Every inline badge in a flex row: has `whitespace-nowrap flex-shrink-0` on wrapper
- [ ] Every FAQ: question uses `text-base md:text-lg font-medium text-ink`, answer uses `text-sm md:text-base text-prose leading-relaxed`

**Eyebrow classification rule** — what MUST use `<EyebrowLabel>`:
- Section-level labels that introduce a content block (e.g., "Tier 1 - No commitment", "The Problem", "How It Works", "Trusted by ambitious teams")
- These appear at the TOP of a `<section>`, usually before an `<h2>` or section heading

What should stay as raw `<span>`/`<div>`/`<p>`:
- Card-internal sub-labels (e.g., "Free", "Premium", "Typical findings include" inside a card)
- Tier badges ("Most Popular" pill overlays)
- Stat labels (e.g., "Years delivering" under a number)
- Social proof card footers (e.g., "SENE", "Agency Partner" at bottom of a testimonial card)
- Any label that is INSIDE a card/panel boundary, not at section scope

**CTA arrow convention** — Templates MUST NOT include text arrows. The architecture is:
1. CMS stores plain label text (no arrows)
2. Template wraps CMS text in `stripCtaArrow()` as defense-in-depth
3. Template renders SVG arrow icon alongside the text
4. Never append ` →` in JSX — use `<svg>` elements only

#### E. DARK BACKGROUND SWEEP

For every section/wrapper with a dark background (`bg-ink`, `bg-midnight`, `bg-vermillion`, dark gradient, or any bg with dark color), trace EVERY text element inside:

1. List ALL `<h1>` through `<h6>`, `<p>`, `<span>`, `<a>`, `<div>` containing text
2. For each: does it have an explicit light text color? (`text-white`, `text-white/60`, `text-white/70`, `text-white/40`, `text-parchment`, `text-parchment/70`)
3. "Explicit" means on the element itself OR inherited from a parent that sets text color on all children (like a wrapper `<div className="text-white/60">`)
4. Any element that would render with `text-ink` or `text-prose` on a dark background = 🔴 INVISIBLE TEXT

#### F. RESPONSIVE ANALYSIS

Three passes. Each catches different problems.

**Pass 1: Breakpoint Transition Trace**

For EVERY grid/flex container, trace what happens at each relevant breakpoint:

1. List the breakpoint classes (e.g., `grid md:grid-cols-2 lg:grid-cols-4`)
2. Walk through each transition point:
   - **375px**: What is visible? Does it stack correctly? Any fixed-width elements that overflow?
   - **640px (sm)**: First breakpoint — what changes? Does the change make sense at this width?
   - **768px (md)**: Second breakpoint — how many columns? Do elements fit? Can CTA text breathe?
   - **1024px (lg)**: Third breakpoint — full layout activates?
   - **1280px (xl)**: Max-width content — everything spaced properly?
3. At each transition, ask: "Does the content actually fit at the **minimum** width of this breakpoint?"
   - 3-col at `md` (768px) = each col is ~230px after gaps/padding. Will CTA buttons fit without wrapping to 3+ lines?
   - 2-col at `sm` (640px) = each col is ~280px. Will card content fit?
   - If content will squeeze badly at the min width → the breakpoint is too low. Flag as 🟡.

**Pass 2: Content Squeeze Test**

For elements with text content, estimate whether they have room at their narrowest rendered width:

- **CTA buttons**: At their narrowest column, will multi-word button text (e.g., "Run Free SiteScore") wrap to 3+ lines? If yes → 🟡
- **Badges/tags**: Inline badges at narrow widths — do they have `flex-wrap` or `truncate`? Without either → potential overflow
- **Stat values + labels**: At narrow widths, do stat items have enough room? Are they centered when stacked?
- **Long headings**: At 375px, does `hero-headline-*` clamp properly? Any `max-w-*` that could clip?
- **Inline flex rows** (eyebrow + badge, icon + text): Do they have `flex-wrap` for narrow screens?

**Pass 3: Spacing & Alignment Consistency**

Check that spacing hierarchies survive at every viewport:

- **Proximity grouping**: When items stack on mobile, the gap WITHIN a group (number → title → body) must be visibly smaller than the gap BETWEEN groups (step1-body → step2-number). If both are similar → items blur together → 🟡
- **Alignment consistency**: All text in a section should follow the same alignment rule at each breakpoint. Mixed alignment (some centered, some left) on mobile = 🟡
- **Centered content check**: In centered layouts (`text-center`), verify ALL children center:
  - Flex containers: `justify-center`
  - Block elements with `max-w-*`: need `mx-auto`
  - Inline elements: inherited from `text-center`
- **Asymmetric layout alignment trio** (hero with side image, 2-col with content+visual):
  - `text-center lg:text-left` on headings/body text — OR on a parent wrapper
  - `mx-auto lg:mx-0` on the hero-stagger/content container
  - `justify-center lg:justify-start` on CTA group flex wrapper
  - Missing ANY = 🟡
- **Centered layout check** (symmetric sections):
  - `text-center` on header group
  - `justify-center` on CTA groups (if present)

#### G. COMPONENT-LEVEL OUTPUT

After checking all elements in a component, output a summary line:

```
ComponentName.tsx: ✅ all checks pass (N elements, M properties checked)
```
or:
```
ComponentName.tsx: 3 findings
  🔴 Line 42  h2 section-heading: missing section-headline class (has text-3xl md:text-5xl font-bold)
  🟡 Line 78  Link cta-secondary: text → arrow, should be SVG
  🟡 Line 95  div cta-group: missing justify-center lg:justify-start
```

Every single component MUST have a summary line. No exceptions.

### Step 1.4: Compile Findings Table

Merge all findings from Steps 1.2 and 1.3 into a single table:

```markdown
| # | Sev | Component | Line | Role | Property | Expected | Actual | Fix |
|---|-----|-----------|------|------|----------|----------|--------|-----|
| 1 | 🔴 | HeroSection | 72 | hero-heading | css-class | hero-headline | inline style={{...}} | Replace with className="hero-headline text-ink" |
| 2 | 🔴 | HeroSection | 55 | eyebrow | component | EyebrowLabel | manual <span> | Use <EyebrowLabel> |
| 3 | 🟡 | HeroSection | 128 | cta-group | responsive | justify-center lg:justify-start | (missing) | Add responsive justify |
```

**Severity:**
- 🔴 **MUST FIX** — Wrong font class, inline styles replacing design system, invisible text on dark bg, missing overflow-hidden causing layout break, raw `<img>`, text arrows, CTA text without `stripCtaArrow()`, broken responsive (overflow), badge wrapping
- 🟡 **SHOULD FIX** — Missing responsive alignment, wrong spacing, raw Link as button, wrong card radius, missing hover, hardcoded copy, inconsistent FAQ fonts, inline `.replace()` instead of shared utility
- 🟢 **NOTE** — Minor, works fine, could be tidier. **Never auto-fixed.**

### Step 1.4b: CMS Data Cross-Check (MANDATORY for pages with CMS-rendered CTAs)

If the page renders CTA text from CMS (StreamField blocks with `cta_text`, `primary_cta_text`, `secondary_cta_text`, `footer_cta_text`, or model fields like `hero_cta_primary_text`):

1. Check seed data: `grep -n 'cta_text\|hero_cta_' backend/cms/core/management/commands/seed_remaining_pages.py | grep '\\u2192\|→'`
2. Any CTA label with a text arrow in seed data = 🔴 (must be removed from seed data AND rendering path must use `stripCtaArrow()`)
3. Rich text HTML content (`<p>`, `<a>`, `<strong>` tags) with arrows is FINE — those are inline text, not button labels

### Step 1.5: Confidence Gate

Count findings by severity:

- **Zero 🔴 and zero 🟡:**
  > "✅ Page [route] passes audit. 0 actionable findings."
  > Update TRACKER.md. **STOP. Do not proceed to Phase 2.**

- **Any 🔴 or 🟡:**
  > Show findings table and say:
  > "Found X issues (Y 🔴, Z 🟡). Say 'go' to fix, or 'skip' to review first."

**STOP HERE.** Wait for response.

---

## Phase 2: FIX

### Step 2.1: Pre-Fix Safety

```bash
git diff -- [FILE_PATH]
```
If file has uncommitted changes from a parallel session → skip that file's findings with "deferred (modified by parallel session)".

### Step 2.2: Apply Fixes

Fix ALL 🔴 and 🟡 findings. Group related changes per file. Do NOT fix 🟢 items.

**Common fixes reference:**
| Finding | Fix |
|---------|-----|
| Manual eyebrow `<span>` | → `<EyebrowLabel>` (add import). Supported colors: vermillion, caption, white, gold, ocean, indigo |
| Inline `style={{fontFamily...}}` on h1 | → Replace with `className="hero-headline-X"` (remove style prop) |
| Raw `text-5xl font-bold` on h2 | → `className="section-headline text-white"` |
| Text `→` in CTA | → SVG arrow (`<svg className="w-4 h-4" ...>`) |
| CTA text rendered without arrow stripping | → Wrap in `stripCtaArrow()` from `@/lib/cta-utils` (import + apply) |
| Inline `.replace(/→/)` on CTA text | → Replace with `stripCtaArrow()` from `@/lib/cta-utils` |
| Hardcoded ` →` appended in JSX after CTA text | → Remove text arrow; SVG arrow is added by component pattern |
| CMS seed data with `\u2192` in CTA fields | → Remove arrow from seed data string. SVG arrows come from templates |
| Raw `<Link className="bg-vermillion...">` | → `<Button href="..." variant="primary" size="lg">` |
| `rounded-3xl` on card | → `rounded-2xl` |
| Missing `overflow-hidden` on section with absolute children | → Add to `<section className="... overflow-hidden">` |
| Missing `text-center lg:text-left` | → Add to heading/body element |
| Missing `justify-center lg:justify-start` on CTA wrapper | → Add to flex container |
| Missing `hidden lg:block` on hero image | → Wrap in `<div className="hidden lg:block">` |
| Text with no light color on dark bg | → Add `text-white`, `text-white/60`, etc. |
| Raw `<img>` | → `<Image>` from `next/image` with width/height/sizes/alt |
| `pt-32` on hero section | → `pt-36` (proper nav clearance) |
| `mb-4` between header and content grid | → `mb-10 md:mb-12` |
| Badge text wrapping in flex row | → Add `whitespace-nowrap flex-shrink-0` to badge wrapper |
| FAQ question font inconsistent | → `text-base md:text-lg font-medium text-ink` (standardized) |
| FAQ answer font inconsistent | → `text-sm md:text-base text-prose leading-relaxed` (standardized) |

### Step 2.3: Post-Fix Re-Audit (MANDATORY)

**This enforces the determinism guarantee.** After ALL fixes:

1. Re-run ALL grep checks from Step 1.2 on changed files
2. For EACH changed component: re-read the file and re-do the element table from Step 1.3
3. Every previously-🔴/🟡 row must now be ✅
4. Check for regressions: missing imports, broken indentation, unclosed tags, new violations introduced by edits

If anything fails → fix immediately → re-verify that file. Loop until clean.

---

## Phase 3: REVIEW

### Step 3.1: Diff Summary

```markdown
## Audit Results: [route]

### Changes Made
| File | What Changed |
|------|-------------|
| HeroSection.tsx | Replaced inline styles → hero-headline class, added responsive alignment |
| DarkHero.tsx | Added text-center lg:text-left, justify-center lg:justify-start |

### Skipped (intentional)
| Finding | Reason |
|---------|--------|
| ... | ... |

### Files Changed: N files, +X/-Y lines
```

### Step 3.2: Ask for Approval

> "Ready to commit. Reply:"
> - **"approved"** — I'll commit
> - **"show diff [file]"** — show full diff for that file
> - **"revert [file]"** — undo that file's changes
> - **"skip"** — discard all changes

**STOP HERE.**

---

## Phase 4: COMMIT

### Step 4.1: Stage Only Audit Files
```bash
git add [changed files only]
```
**NEVER** `git add .` or `git add -A`.

### Step 4.2: Commit Message
```
fix(ui): [route] — [summary]

[file.tsx]: [what changed]
[file.tsx]: [what changed]
Skipped: [description] — [reason]

Audit: [total] findings ([fixed] fixed, [skipped] skipped)
```

### Step 4.3: Update Tracker
Update `skills/jwd-audit/TRACKER.md`: status ✅, findings count, commit hash, date.

### Step 4.4: Confirm
```
✓ Committed: [hash] fix(ui): [route] — [summary]
  [N] files changed, [+X/-Y] lines
  Tracker updated: [route] → ✅
```

---

## Out of Scope — Do NOT Flag

- Content quality, copy tone (hazn-copy)
- SEO, schema, JSON-LD (hazn-seo)
- Performance, bundle size, lighthouse
- Code style / TypeScript patterns
- Features not yet built
- Backend/API issues
- Refactoring suggestions — "could use shared component" is 🟢 at most

---

## Key Resources

- [Element Roles & Rules](references/element-roles.md) — Complete role-by-role rule definitions
- [Design System](references/design-system.md) — Colors, typography, component APIs, common mistakes
- [Page Inventory](references/page-inventory.md) — All routes with templates

## Scope Rules

- **One page per audit** — never mix pages in one commit
- **Shared components** — fix during first page that uses them. Note in commit.
- **Parallel sessions** — `git diff` before editing. Skip if modified.
- **Already-audited pages** — check TRACKER.md. Skip unless user says "re-audit".

---

## Established Conventions (from branch audit history)

These conventions were established through iterative fixes across 20+ audit commits. The audit MUST enforce these — they are not suggestions.

### Arrow Convention
- **CMS stores plain label text** — no trailing arrows in any `cta_text`, `primary_cta_text`, `secondary_cta_text`, `footer_cta_text`, `hero_cta_primary_text`, `hero_cta_secondary_text` field
- **Templates use `stripCtaArrow()`** from `@/lib/cta-utils` as defense-in-depth on ALL CMS CTA text before rendering
- **SVG arrows only** — templates render `<svg>` arrow icons alongside text. Never append ` →` in JSX
- **Seed data must be clean** — verify `backend/cms/core/management/commands/seed_remaining_pages.py` has no `\u2192` in CTA fields

### EyebrowLabel Convention
- **Section-level labels** → `<EyebrowLabel>` component (import from `@/components/ui/EyebrowLabel`)
- **Card-internal labels** → raw `<span>`/`<div>`/`<p>` (not EyebrowLabel)
- **Supported colors**: vermillion (default), caption, white, gold, ocean, indigo
- If a new color is needed → add to EyebrowLabel type union first, then use it

### FAQ Font Convention
- **Questions**: `text-base md:text-lg font-medium text-ink`
- **Answers**: `text-sm md:text-base text-prose leading-relaxed`
- Applies to: FAQSection.tsx, FAQAccordion.tsx, and any inline FAQ in templates

### Badge/Tag Convention
- Inline badges in flex rows (e.g., "Active Partner") → wrapper needs `flex-shrink-0`, badge text needs `whitespace-nowrap`
- Prevents wrapping at narrow widths

### Responsive Hero Convention (asymmetric layouts)
- `text-center lg:text-left` on content wrapper
- `mx-auto lg:mx-0` on content container
- `justify-center lg:justify-start` on CTA row
- Hero with side panel: `items-start` (not `items-end`), right panel gets `pt-10` vertical alignment nudge

### Shared Utilities
| Utility | Import | Purpose |
|---------|--------|---------|
| `stripCtaArrow(text)` | `@/lib/cta-utils` | Strip trailing text arrows from CMS CTA labels |
| `EyebrowLabel` | `@/components/ui/EyebrowLabel` | Section-level eyebrow spans (JetBrains Mono, uppercase, tracking) |
| `Button` | `@/components/ui/Button` | Primary/secondary/text CTA buttons |
| `FAQSection` | `@/components/blocks/FAQSection` | Standardized FAQ accordion with correct fonts |

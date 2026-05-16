# Learned Rules — Human-Reported Corrections

> **Purpose:** Rules added here come from Phase 3 (Human-in-the-Loop Self-Correction).
> When a human visually inspects a page and finds something the audit missed, the fix is
> applied AND a new rule is written here so the same miss never recurs.
>
> **Format:** Each rule has a unique ID, the date it was added, what was missed, why it
> was missed, and the detection method that will catch it next time.
>
> **Loaded by:** The Phase 2 audit agent reads this file alongside GROUND-TRUTH.md.
> Rules here have EQUAL authority to ground truth rules.

---

## How to Read This File

Each learned rule follows this structure:

```
### LR-{NNN}: {Short title}
- **Date:** YYYY-MM-DD
- **Route:** {page where it was found}
- **Screen size:** {mobile 375px / tablet 768px / desktop 1440px}
- **What was missed:** {description of the visual break}
- **Root cause:** {why the audit didn't catch it — which rule gap}
- **Detection method:** {grep pattern OR role-check addition OR new responsive check}
- **Severity:** 🔴 / 🟡
- **Fix pattern:** {exact code change to apply when this is found}
```

---

## Rules

### LR-001: Process step vertical spacing too tight on mobile
- **Date:** 2026-04-05
- **Route:** /sports-analytics/ (applies to all service sub-pages with process steps)
- **Screen size:** mobile 375px
- **What was missed:** When process steps stack vertically on mobile (single column), the gap between steps (gap-8 = 2rem) is too close to the internal spacing within a step (mb-6 = 1.5rem on number circle). Users cannot distinguish which step number belongs to which step content.
- **Root cause:** The responsive analysis (Step D) checks whether content fits at each breakpoint but did not check whether the gap BETWEEN unbounded items (no card border, no background) is visually distinct from the gap WITHIN items. The `process-steps` role in element-roles.md mentions "spacing hierarchy" but only checks number-to-title and title-to-body, not the outer gap.
- **Detection method:**
  ```bash
  # Process step grids with gap-8 but no sm: override — steps will blur on mobile
  grep -rn 'lg:grid-cols-4.*gap-8' [FILES] | grep -v 'sm:gap-\|gap-10\|gap-12'
  ```
- **Severity:** 🟡
- **Fix pattern:** Change `gap-8` to `gap-12 sm:gap-8` on process step grids (grid with `lg:grid-cols-4`). This gives 3rem between steps on mobile (vs 1.5rem internal mb-6), creating clear visual separation when stacked vertically. At `sm` and above, items are in multi-column layout where gap-8 is sufficient.

<!-- NEXT_ID: LR-002 -->

# Canonical Examples — Shopify Revenue Audits

Pointers to past audits the agents and templates can reference for tone, length, evidence-density, and structure. Verified against `repos/sales/autonomous-proposals/audits/` directory listing on 2026-05-17.

## Verified examples

### Brixton (2026-05-13)
- **Path:** `repos/sales/autonomous-proposals/audits/brixton-revenue-audit-2026-05-13/`
- **Files present:** `index.html`, `1-pager.html`, `BUILD-BRIEF.md`, `SYNTHESIS-BRIEF.md`, `outreach-email.md`, `outreach-linkedin.md`, plus `assets/`, `competitor/`, `customer-voice/`, `modules/`, `recon/`, `red-team/`, `synthesis/`.
- **One-line summary:** DTC heritage apparel. Year-1 P50 recoverable $933K, steady-state $1.49M. Dominant blocker: every hero PDP renders "Unavailable" while inventory API returns `available:true`. 19.9x payback over $75K Teardown.
- **Use as reference for:** named-and-shamed tone, PE-language second-recipient email, BUILD-BRIEF.md format, full directory layout for paid Teardown deliverables.

### Nanit (2026-05-13)
- **Path:** `repos/sales/autonomous-proposals/audits/nanit-revenue-audit-2026-05-13/`
- **Files present:** `index.html`, `index.md`, `1-pager.html`, `1-pager.md`.
- **One-line summary:** Baby tech / smart monitor DTC. Markdown + HTML pair for both deliverables. Lighter directory structure than Brixton.
- **Use as reference for:** minimal-directory deliverable variant (no `recon/`, `competitor/`, `customer-voice/` subdirs published).

### Sene Studio (April 2026)
- **Path:** `repos/sales/autonomous-proposals/audits/senestudio-revenue-audit-2026-04-20/`
- **Files present:** `index.html`, `assets/`.
- **One-line summary:** Custom-fit menswear. SiteHealth 42/100 (M1: 28, M2: 38, M3: 53, M4: 51). Quick-Wins recovery $1.0M-$2.5M/yr at P50 (rebuilt v2 after v1 projected $11M and failed red-team for fabricated Baymard CVR benchmark).
- **Use as reference for:** v1→v2 rebuild precedent, Methodology Update callout, 7-file cascade fix when a client clarifies a domain assumption.
- **Cited in:** `revenue-leak-calculator.md` as the canonical "why every projection runs through all 4 red-teams" case.

## Related deliverables (not full revenue audits, but referenced for format)

These are NOT shopify-revenue-audit outputs but appear in the same `audits/` directory and are sometimes referenced for format ideas:

- `lt-agency-sitehealth-2026-04-03/` — partner-framing SiteHealth, no $-projection
- `eichholtz-store-diagnostic-2026-04-11/` — diagnostic-only, used as template seed for the Sene audit
- `dew-mighty-store-diagnostic-2026-04-11/` — companion to Eichholtz
- `containerone-revenue-audit-2026-04-21/` — earlier revenue-audit format, pre-Editorial Warmth v2

## How to use this file

- The HTML builder agent uses **Brixton** as the skeleton when the deliverable scope is "full Teardown" (with `recon/`, `competitor/`, `customer-voice/`, `red-team/` subdirs published alongside).
- The HTML builder agent uses **Nanit** as the skeleton when the deliverable is "lean public-data audit" (just `index.html` + `1-pager.html`).
- The synthesis-lead and revenue-calculator agents reference **Sene** for the methodology rebuild precedent.

## TODO

- Pull Brixton's actual composite score number into this file once `index.html` has been parsed (currently relies on outreach copy's $933K / $1.49M figures).
- Confirm Nanit composite score and module breakdown (the markdown variant is present and easier to grep).
- Add Sene module-3 PDP teardown structure as a sub-reference for module-3-conversion skill.
- When a new audit ships, add a one-line entry here. Keep this file under 80 lines.

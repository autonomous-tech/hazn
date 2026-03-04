# TOOLS.md - Local Notes

## Deployment Repos

### Decision Rule — Always Ask First
> **Public or private?**
> - Needs to be shared externally without auth → `landing-pages`
> - Internal / confidential / shared via expiring link → `autonomous-proposals`

---

### autonomous-proposals (PRIVATE — auth gated)
- **Repo:** `autonomous-tech/autonomous-proposals` (private)
- **Local clone:** `/home/rizki/autonomous-proposals`
- **Domain:** `docs.autonomoustech.ca` — Cloudflare Access, `@autonomoustech.ca` Google accounts only (domain set in CF dashboard, not via CNAME file)
- **External sharing:** Share button generates 30-day expiry link via `share.autonomoustech.ca`
- **Deploy:** Push to `main` → GitHub Action → Wrangler (auto, ~30-60s)
- **Structure:** Client folders at **repo root**
  ```
  {client-name}/
  ├── index.html      ← required hub/nav page
  ├── *.html
  └── images/
  ```
- **Share button:** Must be in every HTML page before `</body>`. Copy from `briar-creek-construction/index.html`. Only renders if `CF_Authorization` cookie present.

---

### landing-pages (PUBLIC)
- **Repo:** `autonomous-tech/landing-pages` (private repo, public deployment)
- **Local clone:** `/home/rizki/landing-pages`
- **Domain:** `pages.autonomoustech.ca` — fully public, no auth
- **Deploy:** Push to `main` → Cloudflare Pages GitHub integration (auto, ~30-60s)
- **`index.html` is AUTO-GENERATED** — never edit manually. Runs via GitHub Action on any `.html` push.
- **Structure:** Files go in category subfolders, URL = file path from repo root
  ```
  proposals/      ← client proposals
  audits/         ← audit reports
  docs/           ← internal docs, multi-file projects
  demos/          ← demos and prototypes
  lunch-n-learn/  ← presentations
  services/       ← service pages
  assets/         ← shared assets (logos, fonts)
  ```
- **Single-file pages:** `proposals/client-name-YYYY-MM-DD.html`
- **Multi-file pages:** `docs/project-name-YYYY-MM-DD/index.html` + assets
- **File naming:** lowercase, hyphenated, date-stamped
- **Commit message convention:** `Agent Hazn: [Page Type] for [Client Name]`
- **Logo paths:** `../logo-01.jpg` from subfolders, `../../logo-01.jpg` from sub-subfolders

---

## WordPress Hosting (HestiaCP)

- **Server:** HestiaCP (beefy VPS)
- **Wildcard DNS:** `*.wp.autonomoustech.ca` → server IP (set in Cloudflare)
- **Every new WP site gets:** `{client}.wp.autonomoustech.ca` — SSL auto-configured
- **Provisioning:** SSH in → `v-add-domain` + `v-install-app wordpress` → WP-CLI for everything else
- **WP skill:** `wordpress-generatepress` (in `/home/rizki/clawd/skills/`)
- **Paid requirement:** GeneratePress Premium only ($59/yr) — everything else is free

## Git Config for Commits
```
user.email = hazn@autonomoustech.ca
user.name = Hazn
```

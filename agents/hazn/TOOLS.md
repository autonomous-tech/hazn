# TOOLS.md - Local Notes

## Deployment Repos

### Deployment Rule — Always Use `autonomous-proposals`
> **All deliverables deploy to `docs.autonomoustech.ca`** via the `autonomous-proposals` repo.
> External sharing is handled via the share button (30-day expiry link via `share.autonomoustech.ca`) — no need for a public repo.

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

### landing-pages (DEPRECATED — do not use for new deploys)
- **Repo:** `autonomous-tech/landing-pages` (private repo)
- **Local clone:** `/home/rizki/landing-pages`
- **Status:** No longer the primary deployment target. All new work goes to `autonomous-proposals` → `docs.autonomoustech.ca`.
- **Note:** Existing files remain accessible but no new content should be published here.

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

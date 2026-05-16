# Brand Configs

Brand config files control the visual identity of all Hazn-generated audit reports, proposals, and HTML deliverables. They enable three modes:

1. **Autonomous default** — `autonomous.json`. Used when no brand is specified. Stone/Amber design system, Autonomous branding, Calendly CTA.
2. **Partner white-label** — `{partner-slug}.json`. Partner's logo, colors, fonts, and CTA replace Autonomous branding. `hide_autonomous: true` removes all Autonomous references.
3. **End-customer** — Built inline during intake from client-provided details (company name, primary color, logo URL, CTA URL). Not persisted as a file unless reused.

---

## Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `slug` | string | Yes | URL-safe identifier. Used in file names and paths. |
| `company_name` | string | Yes | Full legal or display name shown in report headers. |
| `logo_text` | string | Yes | Text fallback for logo (used when no image is provided). |
| `logo_url` | string \| null | No | URL to logo image. Preferred over base64 when available. |
| `logo_base64` | string \| null | No | Base64-encoded logo for single-file HTML embedding. |
| `primary_color` | string | Yes | Primary text/heading color. Hex format. |
| `accent_color` | string | Yes | CTA buttons, highlights, active states. Hex format. |
| `background_color` | string | Yes | Page background color. Hex format. |
| `cta_url` | string | Yes | URL for all CTA buttons in the report. |
| `cta_label` | string | Yes | Default CTA button text. |
| `domain` | string | Yes | Domain where reports are hosted (for canonical URLs). |
| `hide_autonomous` | boolean | Yes | `true` removes all Autonomous branding from output. |
| `design_system` | string | Yes | Design system identifier. Currently: `"stone-amber"`. |
| `font_display` | string | Yes | Google Font name for headings. |
| `font_body` | string | Yes | Google Font name for body text. |
| `colors` | object | Yes | Full color palette. Keys are token names (e.g. `stone_50`), values are hex strings. |

---

## Adding a New Partner Brand

1. Copy `autonomous.json` as a starting point:
   ```bash
   cp "${CLAUDE_PLUGIN_ROOT}/brands/autonomous.json" "${CLAUDE_PLUGIN_ROOT}/brands/{partner-slug}.json"
   ```

2. Edit the new file:
   - Set `slug` to the partner's URL-safe name
   - Set `company_name`, `logo_text`, `logo_url` or `logo_base64`
   - Set `primary_color`, `accent_color`, `background_color` to partner's palette
   - Set `cta_url` and `cta_label` to partner's booking/contact link
   - Set `domain` to partner's report hosting domain
   - Set `hide_autonomous: true` to remove Autonomous branding
   - Set `font_display` and `font_body` to partner's Google Fonts
   - Populate `colors` object with the full token palette

3. Test by running any audit skill with the partner brand:
   ```
   "Run SiteScore Standard for example.com — brand: {partner-slug}"
   ```

---

## How Skills Load Brand Config

Skills follow this resolution order during intake:

1. **Explicit partner slug** — load `${CLAUDE_PLUGIN_ROOT}/brands/{partner-slug}.json`
2. **End-customer inline** — build config object from intake answers (not persisted)
3. **Default fallback** — load `${CLAUDE_PLUGIN_ROOT}/brands/autonomous.json`

If a partner slug is specified but the file doesn't exist, the skill should prompt to run brand setup before proceeding.

Brand config values are injected into the HTML report at generation time — CSS custom properties, font imports, logo, CTA URLs, and company name are all driven by the config.

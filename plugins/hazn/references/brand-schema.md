# Brand Config Schema

Brand config JSON files in `${CLAUDE_PLUGIN_ROOT}/brands/{slug}.json` drive the visual identity of every Hazn-generated artifact (audit reports, proposals, HTML deliverables, branded markdown). This document is the authoritative schema reference. Job plugins (shopify-revenue-audit, etc.) must resolve brand configs against this contract.

## Resolution order

A skill loading a brand follows this order:

1. **Explicit partner slug** passed in by caller → load `${CLAUDE_PLUGIN_ROOT}/brands/{slug}.json`
2. **End-customer inline config** built at intake from user answers (not persisted unless reused)
3. **Default fallback** → load `${CLAUDE_PLUGIN_ROOT}/brands/autonomous.json`

If a slug is requested but the file is missing, skills should fail loud and prompt the user to run brand setup — never silently fall back.

## Field reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `slug` | string | Yes | URL-safe identifier. Used in file names, paths, and as the lookup key for partner brands. |
| `company_name` | string | Yes | Full legal or display name shown in report headers and footers. |
| `logo_text` | string | Yes | Text fallback for the logo when no image asset is supplied. |
| `logo_url` | string \| null | No | URL to a logo image. Preferred over base64 when reports are hosted online. |
| `logo_base64` | string \| null | No | Base64-encoded logo for single-file HTML deliverables that must travel as one document. |
| `primary_color` | string | Yes | Primary text and heading color, hex (e.g. `#1c1917`). |
| `accent_color` | string | Yes | CTA buttons, highlights, active states, hex (e.g. `#f59e0b`). |
| `background_color` | string | Yes | Page background color, hex (e.g. `#fafaf9`). |
| `cta_url` | string | Yes | URL behind every CTA button in the report (booking link, contact form, etc.). |
| `cta_label` | string | Yes | Default CTA button text. Use action verbs ("Book a 20-min call →"). |
| `domain` | string | Yes | Domain where reports are hosted. Drives canonical URLs and og:url meta. |
| `hide_autonomous` | boolean | Yes | When `true`, all Autonomous branding (logo, footer credit, watermark) is stripped from output. Required for white-label partner reports. |
| `design_system` | string | Yes | Design system identifier. Currently supports `"stone-amber"` (Editorial Warmth v2). Future systems will be added here. |
| `font_display` | string | Yes | Google Font name for headings (e.g. `"Source Serif 4"`). |
| `font_body` | string | Yes | Google Font name for body text (e.g. `"Inter"`). |
| `colors` | object | Yes | Full color palette. Keys are design-system tokens (e.g. `stone_50`, `amber_500`), values are hex strings. See palette tokens below. |

## Palette tokens (stone-amber design system)

The default `autonomous.json` ships the full Tailwind-derived token set:

- `stone_50` through `stone_900` — neutral scale, used for backgrounds, borders, body text, and surface elevation
- `amber_400`, `amber_500`, `amber_600` — accent scale for CTAs, links, highlights, and emphasis

Partner brands using `stone-amber` should provide the same key set with their own hex values. Skills assume these exact keys exist; missing keys will fall back to the default but produce a console warning.

## Example: autonomous.json

```json
{
  "slug": "autonomous",
  "company_name": "Autonomous Technology Inc.",
  "logo_text": "Autonomous",
  "logo_url": null,
  "logo_base64": null,
  "primary_color": "#1c1917",
  "accent_color": "#f59e0b",
  "background_color": "#fafaf9",
  "cta_url": "https://calendly.com/rizwan-20/30min",
  "cta_label": "Book a 20-min call →",
  "domain": "docs.autonomoustech.ca",
  "hide_autonomous": false,
  "design_system": "stone-amber",
  "font_display": "Source Serif 4",
  "font_body": "Inter",
  "colors": {
    "stone_50": "#fafaf9",
    "stone_900": "#1c1917",
    "amber_500": "#f59e0b"
  }
}
```

(Truncated for brevity — see `brands/autonomous.json` for the full palette.)

## Adding a new partner brand

1. Copy `brands/autonomous.json` to `brands/{partner-slug}.json`.
2. Update `slug`, `company_name`, `logo_text`, and one of `logo_url` / `logo_base64`.
3. Replace `primary_color`, `accent_color`, `background_color` with the partner's hex values.
4. Set `cta_url` and `cta_label` to the partner's preferred booking or contact link.
5. Set `hide_autonomous: true` for true white-label.
6. Replace `font_display` and `font_body` with the partner's Google Fonts (loaded by the renderer).
7. Populate every token in `colors` — do not leave keys missing.
8. Validate by running any audit skill with `--brand {partner-slug}`.

## Consumer contract for job plugins

Job plugins (e.g. shopify-revenue-audit, future website builder) MUST:

- Treat brand config as read-only at runtime — never mutate the loaded object
- Use CSS custom properties driven by the config rather than hardcoded hex values
- Honor `hide_autonomous` everywhere (header, footer, og:image, JSON-LD `publisher`)
- Pass the resolved config object to any sub-skill that renders output, not the slug — avoids double-lookups

The `editorial-warmth-audit-renderer` skill in this plugin is the reference implementation.

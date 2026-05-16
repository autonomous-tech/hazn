---
description: List installed Hazn marketplace plugins, their commands, and point to docs
disable-model-invocation: true
---

# /hazn:help

The entry point. Shows what's installed from the Hazn marketplace, what each plugin can do, and where to read more. Use this when you've just installed Hazn and want to know what `/hazn:*` commands you have available, or when you're trying to remember which job plugin owns which command.

## What this command shows

### 1. Installed marketplace plugins

Enumerate every plugin in the active Claude Code marketplace whose source resolves under the hazn marketplace root (or whose name starts with `hazn-` / matches the published marketplace entries). For each, print:

- Name and version
- One-line description from its `plugin.json`
- Category (runtime, audits, websites, content, etc.)

### 2. Commands per plugin

For each installed plugin, list every command in its `commands/` directory with the short description from frontmatter. Group under the plugin name. Example layout:

```
hazn (runtime kernel, v1.0.0)
  /hazn:feedback   Capture feedback and open a draft PR or issue
  /hazn:doctor     Verify runtime, plugins, and local checkout
  /hazn:help       This command

shopify-revenue-audit (v1.0.0)
  /shopify-revenue-audit:run            Run a full 4-module audit on a Shopify store
  /shopify-revenue-audit:rerun-module   Re-run a single module after a fix
  /shopify-revenue-audit:one-pager      Render the executive one-pager only
```

### 3. Docs and next steps

Print direct links to:

- `${CLAUDE_PLUGIN_ROOT}/../../README.md` — marketplace overview
- `${CLAUDE_PLUGIN_ROOT}/references/brand-schema.md` — how brand configs work
- `${CLAUDE_PLUGIN_ROOT}/../../docs/decisions/003-hazn-marketplace.md` — architecture decision record (in the canonical hazn checkout)
- `https://github.com/autonomous-tech/hazn` — canonical repo for filing feedback

End with a one-line nudge: `Run /hazn:doctor if anything looks wrong, or /hazn:feedback to suggest improvements.`

## Tone

Helpful, short, no marketing. The user already installed the plugin — they don't need a sales pitch, they need to know what they can type next.

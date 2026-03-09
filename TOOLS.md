# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## Web Tools (Configured 2026-02-19)

### web_search
Search the web via Brave Search API.
- Provider: Brave
- Free tier: 2,000 queries/month

### web_fetch  
Fetch and extract readable content from URLs.
- Extractor: Readability (converts HTML → markdown)

### browser
Headless Chrome for full browser automation.
- Profile: `clawd`
- Mode: headless + noSandbox (VPS)
- CDP port: 18800

All three tools are **shared across all agents** (Haaris, Milo, Sage).

---

## Local Skills

### autonomous-linkedin
- **Location:** `skills/autonomous-linkedin/SKILL.md`
- **Use when:** Generating LinkedIn posts + images for Autonomous positioning
- **Pillars:** MarTech, Attribution, CRO/Audits, AI Agents for agencies, The Journey
- **Created:** 2026-02-25

### multi-agent-setup
- **Location:** `skills/multi-agent-setup/SKILL.md`
- **Use when:** Setting up new agents with WhatsApp group bindings
- **Created:** 2026-02-19

## Active Agents

| Agent | ID | Group | JID |
|-------|-----|-------|-----|
| Haaris | main | (DMs) | — |
| Milo | memox-sales | Memox Milo | `120363424487643855@g.us` |
| Sage | home | HomeClaw | `120363425158783699@g.us` |
| Maven | maven | Maven Analytics | `120363405470392329@g.us` |
| Rex | autonomous-sales | Rex Sales | `120363404619112966@g.us` |
| Hazn | hazn | Hazn | `120363407165595162@g.us` |
| Orion | boopbody | Boopbody Orion | `120363422790325221@g.us` |
| Pulse | linkedin | Pulse | `120363407882421509@g.us` |
| Spark | ecommerce-sdr | Spark SDR | `120363406010554884@g.us` |

## WhatsApp Setup Notes
- Bot number: +16046531100
- Owner numbers: +16046531100, +923321305389
- `groupAllowFrom: ["*"]` — allows all senders in groups

---

## 🚨 Security Boundaries

**NEVER do these without explicit permission:**
- Expose services via quick/random Cloudflare tunnels (trycloudflare.com)
- Open ports or bind to 0.0.0.0
- Expose internal dashboards/APIs to the public internet
- Create any public-facing endpoint without proper auth

**Always require:**
- Proper domain with named tunnel (e.g., command-center.rizqaiser.com)
- Authentication (Cloudflare Access, token auth, etc.)
- Explicit approval before exposing anything

---

Add whatever helps you do your job. This is your cheat sheet.

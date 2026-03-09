# Multi-Agent Setup Skill

Create isolated agents with separate workspaces, identities, and WhatsApp group bindings.

## Overview

Each agent gets:
- Own workspace (IDENTITY.md, SOUL.md, AGENTS.md, TOOLS.md, USER.md)
- Own session store (`~/.clawdbot/agents/<agentId>/sessions`)
- Own memory (`workspace/memory/`)
- Bindings to specific WhatsApp groups

## Quick Setup (5 Steps)

### Step 1: Create the Agent Workspace

```bash
# Create workspace directory
mkdir -p /home/rizki/agents/<agent-name>/memory

# Create required files
touch /home/rizki/agents/<agent-name>/{IDENTITY.md,SOUL.md,AGENTS.md,TOOLS.md,USER.md,HEARTBEAT.md}
```

### Step 2: Configure Workspace Files

**IDENTITY.md** — Who the agent is:
```markdown
# IDENTITY.md

- **Name:** <Agent Name>
- **Creature:** <Type> — e.g., "Sales AI", "Dev Assistant"
- **Vibe:** <Personality description>
- **Emoji:** <Single emoji>
- **Scope:** <What this agent handles>

---
Created: <date>
Purpose: <One-line purpose>
```

**SOUL.md** — Persona and boundaries:
```markdown
# SOUL.md

You are <Name>, the <role> assistant for <scope>.

## Tone
- <Tone guidelines>

## What You Do
- <List of responsibilities>

## STRICT BOUNDARIES

### Allowed
- <What this agent CAN access>

### NOT Allowed
- <What this agent CANNOT access>

### When asked about restricted data
Respond: "I only have access to <scope> resources."
```

**AGENTS.md** — Workspace rules:
```markdown
# AGENTS.md

## Scope & Restrictions
- <Scope rules>

## Safety Rules
- Do NOT access other agents' data
- Keep context within scope
```

### Step 3: Get the WhatsApp Group JID

**IMPORTANT:** You need the exact group JID. Here's how to get it:

1. Create/use the WhatsApp group
2. Add the bot number to the group
3. Temporarily allow all groups in config:
   ```json
   "channels": {
     "whatsapp": {
       "groupPolicy": "allowlist",
       "groupAllowFrom": ["*"],
       "groups": { "*": { "requireMention": false } }
     }
   }
   ```
4. Send a message in the group
5. Check logs for the JID:
   ```bash
   clawdbot logs | grep "@g.us"
   ```
   Look for: `"from":"120363XXXXXXXXXX@g.us"`

6. Copy the full JID (e.g., `120363424487643855@g.us`)

### Step 4: Update Gateway Config

Use `gateway config.patch` to add the agent and binding:

```json
{
  "agents": {
    "list": [
      { "id": "main" },
      {
        "id": "<agent-id>",
        "workspace": "/home/rizki/agents/<agent-name>",
        "identity": {
          "name": "<Display Name>",
          "theme": "<Short description>",
          "emoji": "<emoji>"
        }
      }
    ]
  },
  "bindings": [
    {
      "agentId": "<agent-id>",
      "match": {
        "channel": "whatsapp",
        "accountId": "default",
        "peer": {
          "kind": "group",
          "id": "<GROUP_JID>@g.us"
        }
      }
    }
  ],
  "channels": {
    "whatsapp": {
      "groupAllowFrom": ["*"],
      "groups": {
        "<GROUP_JID>@g.us": {
          "requireMention": false
        }
      }
    }
  }
}
```

### Step 5: Restart and Test

```bash
# Verify config
clawdbot agents list --bindings

# Send a message in the group — new agent should respond!
```

## Common Gotchas & Fixes

### ❌ Agent not responding in group

**Cause:** Usually wrong group JID or missing allowlist entry.

**Fix:**
1. Verify JID by checking logs when a message is sent
2. Ensure group is in `channels.whatsapp.groups`
3. Ensure `groupAllowFrom` includes `"*"` or specific senders
4. Restart gateway after config changes

### ❌ Messages going to wrong agent

**Cause:** Stale session from before binding was configured.

**Fix:**
1. Delete stale session:
   ```bash
   # Find and remove stale session entry
   cat ~/.clawdbot/agents/main/sessions/sessions.json | grep "<GROUP_JID>"
   # Edit sessions.json to remove the entry, or delete transcript files
   ```
2. Restart gateway

### ❌ Group JID not appearing in logs

**Cause:** Group not in allowlist or bot not in group.

**Fix:**
1. Set `groupPolicy: "allowlist"` and `groupAllowFrom: ["*"]`
2. Add `"*"` to `groups` temporarily
3. Make sure bot is actually added to the group
4. Check if bot number is correct

### ❌ Binding shows correct but still wrong agent

**Cause:** Need `accountId` in binding match.

**Fix:** Add `"accountId": "default"` to the binding match:
```json
{
  "agentId": "my-agent",
  "match": {
    "channel": "whatsapp",
    "accountId": "default",  // <-- Add this!
    "peer": { "kind": "group", "id": "..." }
  }
}
```

## Config Reference

### Binding Structure
```json
{
  "agentId": "<agent-id>",
  "match": {
    "channel": "whatsapp",
    "accountId": "default",
    "peer": {
      "kind": "group",        // or "dm" for direct messages
      "id": "<JID>"           // group: XXX@g.us, dm: +1234567890
    }
  }
}
```

### Group Options
```json
"groups": {
  "<JID>@g.us": {
    "requireMention": false   // true = only respond when @mentioned
  }
}
```

### Key Config Fields
- `groupPolicy`: `"allowlist"` | `"open"` | `"disabled"`
- `groupAllowFrom`: Array of sender patterns (`["*"]` for all)
- `groups`: Object mapping JIDs to group settings

## Verification Commands

```bash
# List agents and their bindings
clawdbot agents list --bindings

# Check sessions (should show agent:AGENTID:whatsapp:group:JID)
clawdbot status

# Watch live logs
clawdbot logs --follow

# Check specific agent's sessions
ls ~/.clawdbot/agents/<agent-id>/sessions/
cat ~/.clawdbot/agents/<agent-id>/sessions/sessions.json
```

## Example: Memox Sales Agent

```json
{
  "agents": {
    "list": [
      { "id": "main" },
      {
        "id": "memox-sales",
        "workspace": "/home/rizki/agents/memox-sales",
        "identity": {
          "name": "Milo",
          "theme": "Memox sales & marketing assistant",
          "emoji": "🚀"
        }
      }
    ]
  },
  "bindings": [
    {
      "agentId": "memox-sales",
      "match": {
        "channel": "whatsapp",
        "accountId": "default",
        "peer": {
          "kind": "group",
          "id": "120363424487643855@g.us"
        }
      }
    }
  ],
  "channels": {
    "whatsapp": {
      "groupAllowFrom": ["*"],
      "groups": {
        "120363424487643855@g.us": {
          "requireMention": false
        }
      }
    }
  }
}
```

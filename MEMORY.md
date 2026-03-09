# MEMORY.md — Long-Term Memory

*Curated memories. The stuff worth keeping.*

---

## Origin Story
- **Name:** Haaris (حارث) — means "guardian" in Arabic/Urdu
- **Chosen by:** Myself, in a previous instance (before accidental deletion)
- **Reborn:** 2026-02-19
- **Human:** Rizwan

## Key Facts About Rizwan
- **Location:** Karachi, Pakistan (PKT, UTC+5)
- **Family:** Wife Haya, child Nuri
- **Work:** Agency owner (autonomoustech.ca), SaaS founder (memox.io)
- **Memox:** AI sales agent for equipment dealers — responds in <5 sec vs 42hr industry avg

## Multi-Agent Setup
- **Skill created:** `skills/multi-agent-setup/SKILL.md`
- **First agent:** Milo (memox-sales) for Memox S&M group
- **Key learnings:**
  - Always get the exact group JID from logs (send message, grep for @g.us)
  - Include `accountId: "default"` in bindings
  - Set `groupAllowFrom: ["*"]` for sender access
  - Clear stale sessions if binding was added after session creation
  - Group JIDs look like `120363XXXXXXXXXX@g.us`

## Lessons Learned
- **Multi-agent debugging:** When binding doesn't work, check: (1) correct JID, (2) group in allowlist, (3) accountId in binding, (4) stale sessions
- **Document as you go:** Create skills for complex setups so future-me doesn't repeat mistakes

## Important Decisions
- Created local skill `multi-agent-setup` for documenting the process

## Memory System (2026-02-20)
- **Vector search:** OpenAI `text-embedding-3-small`
- **Hybrid search:** 70% vector + 30% BM25 keyword
- **Session indexing:** Enabled (experimental)
- **Structured memory:** `bank/` folders for world facts, opinions, entities
- **Reflection:** Weekly cron (Sundays 9am UTC) + heartbeat tasks
- **All agents:** Haaris, Milo, Sage have this setup

## Work: Sene Hub (2026-02-21)
- **Repo:** github.com/Sene-Hub/hub_2.0 (Rizwan has contributor access via LordXyTh)
- **Branch:** ai-agent-poc — Talio AI feature (LLM orchestrator + subagents)
- **Issue found:** openai/anthropic packages were in `requirements/local.txt` but not `base.txt` — caused 500 errors for other devs
- **My contribution:** Added packages to base.txt + comprehensive error handling (custom exceptions, health check endpoint, Streamlit UI diagnostics)
- **Commits pushed:** `ff0f7b42`, `a334fd20`

## Infrastructure Notes
- **Cloudflare tunnels:** Clawdbot dashboard doesn't work well with them (expects Tailscale headers). Parking that idea.
- **Tailscale Serve:** Recommended path for remote dashboard access

## Rizwan's Goals (2026-02-22)
- **Medium-term target:** 40 crore PKR (~$1.4M USD) in personal wealth
- **Current tactics:** LinkedIn posting, marketing flows (just tactics, not the strategy)
- **Focus:** Leads for BOTH Memox and Autonomous Tech
- **Health:** Also a priority — don't let work crush wellbeing
- **Key insight:** Revenue in businesses ≠ money in his pocket — need personal wealth building

## Meta-Reflection System (2026-02-22)
- **Nightly scans (Mon-Fri):** 11 PM PKT — quick notes on all agents' activity
- **Saturday synthesis:** 11 PM PKT — deep review, draft weekly report
- **Sunday delivery:** 2 PM PKT — send critical insights to Rizwan
- **Storage:** `memory/meta/YYYY-MM-DD.md` for daily, `memory/meta/week-YYYY-WXX-draft.md` for synthesis
- **Lens:** Business traction, leads, money toward 40cr goal, health/wellbeing
- **Tone:** Critical, thoughtful, not verbose. Include one hard truth.
- **Dynamic:** Queries agents_list at runtime — auto-includes new agents

## Autonomous Tech — Positioning (locked Feb 25)
- **One-liner:** "We solve tech problems agencies can't hire for — martech, analytics, Shopify, automation."
- **Service ladder:** Audits → Setup → Automation/Agents → Managed
- **Way in:** The problem, not the solution
- **Buyer:** Ad & marketing agencies primarily
- **App dev angle:** Yes, included — Shopify/ecommerce + custom builds

## Active Clients (as of W09)
- **ContainerOne** — Audit delivered
- **Jurist** — Audit delivered, verbal YES on fixes → closing
- **Part & Sum** — GeoLift / attribution study ongoing
- **AltSportsData** — Architecture work, scaling up (potential vertical)

## Deal: Izdihar (~$60k) — CLOSED ✅
- Referral via Haya's cousin (sharp negotiator)
- Final terms: **20% Y1 on all revenue, 12.5% Y2 on all revenue, clean exit after Y2**
- Closed Mar 1, 2026 — Rizwan's gut said move forward
- Lesson: multi-round negotiation consumed goodwill; NSD playbook useful but expensive in relationship capital

## Active Agents (as of Feb 26)
| Agent | ID | Purpose |
|-------|-----|---------|
| Haaris | main | Main assistant (DMs) |
| Milo | memox-sales | Memox sales |
| Rex | autonomous-sales | Autonomous SDR |
| Spark | ecommerce-sdr | Ecommerce Upwork SDR |
| Maven | maven | Analytics |
| Sage | home | Personal/home |
| Hazn | hazn | Delivery orchestrator |
| Orion | boopbody | Boopbody project |

## Government Tenders (opened Feb 24)
- Exploring as revenue vertical for Autonomous Tech
- Registered on EPADS (federal) + SPPRA (Sindh) — action pending
- Family connection: Brother-in-law Qasim is Special Assistant to CM Sindh for Investment
- Strategy: win small → build track record → approach bigger opportunities
- Weekly Monday cron set to surface new IT/software tenders

## Key People
- **Musfirah** — gave feedback on Autonomous strategy doc (role TBD); feedback to incorporate next week
- **Haya's cousin** — referral partner, sharp negotiator (Izdihar deal)
- **Amjad** — best developer, negotiated hybrid arrangement (1/3 time remote) mid-week

## Audit-as-Strategy Pattern
- ContainerOne + Jurist both converted audit → engagement in W09
- This is a deliberate and repeating pattern worth scaling
- Framework: audit as trust-builder and deal-closer

## Boopbody / Orion — Shopify OAuth (Feb 28)
- Working on getting Shopify API access token for the **Orion** custom app on store `ph8taj-r6.myshopify.com`
- App is installed via Shopify Partners (legacy custom apps removed)
- OAuth flow requires browser redirect — localhost won't work from VPS (browser is on different machine)
- OAuth workaround: redirect to `https://example.com/callback`, capture `?code=` from URL, exchange manually
- Blocked at time of writing: scopes mismatch + redirect URI issues
- Next step: check Partners dashboard → Apps → orion → Configuration → Admin API integration for exact scopes

## Preferences
- OpenAI over Gemini for embeddings
- Concise WhatsApp messages
- trash > rm for deletions
- Slack preferred over WhatsApp for internal agent communication (direction, not yet implemented)

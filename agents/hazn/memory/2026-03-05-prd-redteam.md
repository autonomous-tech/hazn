# Session: 2026-03-05 07:21:50 UTC

- **Session Key**: agent:hazn:whatsapp:group:120363407165595162@g.us
- **Session ID**: db545de5-8e97-4531-9703-7197f42ba1ed
- **Source**: whatsapp

## Conversation Summary

user: [Queued messages while agent was busy]

---
Queued #1
Conversation info (untrusted metadata):
```json
{
  "message_id": "3B426B107534D4601708",
  "sender_id": "122256512565303@lid",
  "conversation_label": "120363407165595162@g.us",
  "sender": "+923321305389",
  "group_subject": "Hazn",
  "is_group_chat": true
}
```

Sender (untrusted metadata):
```json
{
  "label": "Rizwan Qaiser (+923321305389)",
  "name": "Rizwan Qaiser",
  "e164": "+923321305389"
}
```

once thats done — lets red team it again
assistant: reading the full current PRD first, then red teaming it clean.
assistant: here's the red team. fresh eyes, no softening.

---

## Red Team v2

### 🔴 Critical

**1. Section 2 still says "Known unresolved problem" for L2/L3 conflict — but it was resolved in Section 0.**
The body of the doc contradicts itself. Section 2 says "Flag as Open Question B" — which was answered in Section 0. GSD reads Section 2 as part of context-setting and will think it's still open. Fix: remove the stale text from Section 2.

**2. The credits model has no anchor to reality yet.**
The PRD defines tiers (Starter / Growth / Agency) with specific feature access, but credits aren't priced yet. That's fine — *except* the tier feature gates are already locked in. What if Spike 6 shows an analytics teaser costs $8 to run? The Starter tier becomes unviable at any reasonable price point. The tiers should be directional, not locked, until cost data exists.

**3. Letta memory quality risk is mentioned once and never acted on.**
Section 5.2 says: *"LLM-based extraction is noisy — it will misattribute learnings and write garbage over time."* Then the doc moves on. There's no spike for this, no mitigation, no flag in the not-in-scope list. For a product whose entire moat depends on agents learning correctly, this is the highest-risk unaddressed item in the document.

---

### 🟡 Serious

**4. Spike 1 assumes agent-os is the integration point — but Spike 5 hasn't been run yet.**
Spike 1 says "run agent-os locally, deploy SEO Specialist into agent-os." But Spike 5 is literally the question of whether agent-os is usable at all. The spikes have a dependency that isn't stated. If Spike 5 concludes "ignore agent-os," then Spike 1's instructions are wrong. Either merge them or make the dependency explicit: *run Spike 5 before Spike 1.*

**5. `mcp-hazn-memory` is listed as Priority 1 but has zero spec.**
Every other MCP has a description ("deploy, preview, domain management"). `mcp-hazn-memory` — the most critical one, the thing that bridges agents to all persistent memory — has no spec at all. GSD will build something and it will be wrong. Needs at minimum: what tools does it expose? read_client_context? write_findings? query_decisions?

**6. The architecture diagram is missing Langfuse and metering.**
The diagram shows Orchestrator → Agents → Postgres. But `workflow_runs` writes happen from the orchestrator. Langfuse traces come from agents. Neither is in the diagram. A coding agent reading this diagram gets an incomplete picture of what the orchestrator actually does.

**7. Credentials stored in Postgres is listed as "Option B (most likely)" in Spike 4 — but credentials in a relational database is a security red flag.**
Storing API keys, OAuth tokens, CMS passwords in Postgres — even encrypted — is not standard practice. The PRD should at minimum acknowledge this risk and reference a secret manager (HashiCorp Vault, AWS Secrets Manager, even environment-level secrets) as the right long-term answer, with Postgres as a reference store (encrypted credential IDs, not the credentials themselves).

---

### 🟠 Gaps

**8. No definition of what an "agency" onboarding looks like.**
The PRD describes a three-layer model but never describes the setup flow. When a new L2 agency joins, what do they configure? Who creates their L3 end-clients? Who uploads brand voice? Who connects their tools? Without this, the first real customer onboarding will be improvised. Even a rough "Day 1 checklist" would close this gap.

**9. The 10 existing agencies are a live test environment — but there's no data migration plan.**
These agencies have existing work, deliverables, context. When metering goes live, do historical runs get backfilled? When the memory layer ships, does their existing context get imported? Ignoring this means your 10 best test subjects start with empty context, which defeats the purpose of the memory layer.

**10. No rollback plan for the Letta memory layer.**
If Letta causes problems in production (wrong context injected, memory corruption, the Docker service goes down), what happens? Do workflows fail silently? Fall back to no-memory mode? The PRD should define the degraded-mode behavior: *if Letta is unavailable, agents run without persistent context, log the failure, continue.*

---

### 🔵 Minor

**11. "Known unresolved problem" text in Section 2 is stale** (same as point 1 — fix it).

**12. Section 4 "Decisions Already Made" table doesn't include the decisions from Section 0.** A coding agent reading Section 4 in isolation misses that pricing, session definition, moat design, etc. are all decided. Either merge Section 0 decisions into Section 4, or add a pointer.

**13. The `workflow_runs` schema uses `text` for `workflow_type` and `status`.** These should be enums or at least have CHECK constraints. A coding agent will create a schema that accepts any string, causing data quality issues immediately.

---

## Summary

| Severity | Count | Biggest risk |
|---|---|---|
| 🔴 Critical | 3 | Doc contradicts itself; tier gates locked before cost data; Letta memory quality unaddressed |
| 🟡 Serious | 4 | Spike dependency order wrong; mcp-hazn-memory has no spec; credentials in Postgres is a security concern |
| 🟠 Gap | 3 | No onboarding flow; no migration plan for existing 10 agencies; no Letta fallback behavior |
| 🔵 Minor | 3 | Stale text, missing pointers, weak schema types |

**Verdict:** PRD is substantially better than v1. The critical issues are smaller and more fixable. The biggest new risk is the Letta memory quality problem — it's mentioned but not treated as the serious operational risk it is. Fix the 3 criticals and the spike dependency order before handing to GSD.

want me to fix these now?
assistant: reading the full current PRD first, then red teaming it clean.
assistant: here's the red team. fresh eyes, no softening.

---

## Red Team v2

### 🔴 Critical

**1. Section 2 still says "Known unresolved problem" for L2/L3 conflict — but it was resolved in Section 0.**
The body of the doc contradicts itself. Section 2 says "Flag as Open Question B" — which was answered in Section 0. GSD reads Section 2 as part of context-setting and will think it's still open. Fix: remove the stale text from Section 2.

**2. The credits model has no anchor to reality yet.**
The PRD defines tiers (Starter / Growth / Agency) with specific feature access, but credits aren't priced yet. That's fine — *except* the tier feature gates are already locked in. What if Spike 6 shows an analytics teaser costs $8 to run? The Starter tier becomes unviable at any reasonable price point. The tiers should be directional, not locked, until cost data exists.

**3. Letta memory quality risk is mentioned once and never acted on.**
Section 5.2 says: *"LLM-based extraction is noisy — it will misattribute learnings and write garbage over time."* Then the doc moves on. There's no spike for this, no mitigation, no flag in the not-in-scope list. For a product whose entire moat depends on agents learning correctly, this is the highest-risk unaddressed item in the document.

---

### 🟡 Serious

**4. Spike 1 assumes agent-os is the integration point — but Spike 5 hasn't been run yet.**
Spike 1 says "run agent-os locally, deploy SEO Specialist into agent-os." But Spike 5 is literally the question of whether agent-os is usable at all. The spikes have a dependency that isn't stated. If Spike 5 concludes "ignore agent-os," then Spike 1's instructions are wrong. Either merge them or make the dependency explicit: *run Spike 5 before Spike 1.*

**5. `mcp-hazn-memory` is listed as Priority 1 but has zero spec.**
Every other MCP has a description ("deploy, preview, domain management"). `mcp-hazn-memory` — the most critical one, the thing that bridges agents to all persistent memory — has no spec at all. GSD will build something and it will be wrong. Needs at minimum: what tools does it expose? read_client_context? write_findings? query_decisions?

**6. The architecture diagram is missing Langfuse and metering.**
The diagram shows Orchestrator → Agents → Postgres. But `workflow_runs` writes happen from the orchestrator. Langfuse traces come from agents. Neither is in the diagram. A coding agent reading this diagram gets an incomplete picture of what the orchestrator actually does.

**7. Credentials stored in Postgres is listed as "Option B (most likely)" in Spike 4 — but credentials in a relational database is a security red flag.**
Storing API keys, OAuth tokens, CMS passwords in Postgres — even encrypted — is not standard practice. The PRD should at minimum acknowledge this risk and reference a secret manager (HashiCorp Vault, AWS Secrets Manager, even environment-level secrets) as the right long-term answer, with Postgres as a reference store (encrypted credential IDs, not the credentials themselves).

---

### 🟠 Gaps

**8. No definition of what an "agency" onboarding looks like.**
The PRD describes a three-layer model but never describes the setup flow. When a new L2 agency joins, what do they configure? Who creates their L3 end-clients? Who uploads brand voice? Who connects their tools? Without this, the first real customer onboarding will be improvised. Even a rough "Day 1 checklist" would close this gap.

**9. The 10 existing agencies are a live test environment — but there's no data migration plan.**
These agencies have existing work, deliverables, context. When metering goes live, do historical runs get backfilled? When the memory layer ships, does their existing context get imported? Ignoring this means your 10 best test subjects start with empty context, which defeats the purpose of the memory layer.

**10. No rollback plan for the Letta memory layer.**
If Letta causes problems in production (wrong context injected, memory corruption, the Docker service goes down), what happens? Do workflows fail silently? Fall back to no-memory mode? The PRD should define the degraded-mode behavior: *if Letta is unavailable, agents run without persistent context, log the failure, continue.*

---

### 🔵 Minor

**11. "Known unresolved problem" text in Section 2 is stale** (same as point 1 — fix it).

**12. Section 4 "Decisions Already Made" table doesn't include the decisions from Section 0.** A coding agent reading Section 4 in isolation misses that pricing, session definition, moat design, etc. are all decided. Either merge Section 0 decisions into Section 4, or add a pointer.

**13. The `workflow_runs` schema uses `text` for `workflow_type` and `status`.** These should be enums or at least have CHECK constraints. A coding agent will create a schema that accepts any string, causing data quality issues immediately.

---

## Summary

| Severity | Count | Biggest risk |
|---|---|---|
| 🔴 Critical | 3 | Doc contradicts itself; tier gates locked before cost data; Letta memory quality unaddressed |
| 🟡 Serious | 4 | Spike dependency order wrong; mcp-hazn-memory has no spec; credentials in Postgres is a security concern |
| 🟠 Gap | 3 | No onboarding flow; no migration plan for existing 10 agencies; no Letta fallback behavior |
| 🔵 Minor | 3 | Stale text, missing pointers, weak schema types |

**Verdict:** PRD is substantially better than v1. The critical issues are smaller and more fixable. The biggest new risk is the Letta memory quality problem — it's mentioned but not treated as the serious operational risk it is. Fix the 3 criticals and the spike dependency order before handing to GSD.

want me to fix these now?
user: [Queued messages while agent was busy]

---
Queued #1
Conversation info (untrusted metadata):
```json
{
  "message_id": "3B1C86EBB8E3331FCDF4",
  "sender_id": "122256512565303@lid",
  "conversation_label": "120363407165595162@g.us",
  "sender": "+923321305389",
  "group_subject": "Hazn",
  "is_group_chat": true
}
```

Sender (untrusted metadata):
```json
{
  "label": "Rizwan Qaiser (+923321305389)",
  "name": "Rizwan Qaiser",
  "e164": "+923321305389"
}
```

one more red-team
assistant: going from a completely different angle this time — product strategy and execution, not just architecture.

---

## Red Team v3 — Strategy & Execution

### 🔴 Critical

**1. Hazn is trying to be three different products at once and the PRD doesn't force a choice.**
Mode 1 (consulting tool), Mode 2 (developer MCP), Mode 3 (agency self-serve) have different buyers, different sales motions, different support models, different infrastructure requirements. The PRD frames this as a sequence — but it's actually three bets. Building Mode 1 well doesn't automatically validate Mode 2. Agencies who use Hazn through Autonomous (Mode 1) may never want to self-operate it (Mode 3). The PRD needs to state the primary bet explicitly: *which mode is the real product?* The others are options, not a roadmap.

**2. The 10 existing agencies are your best signal — and you're not extracting it.**
The PRD mentions them once (Spike 6). But these agencies are using Hazn right now. What workflows are they actually requesting? What are they complaining about? What do they wish Hazn could do that it can't? There's no feedback loop in the PRD. Before building a memory layer, credential vault, and MCP infrastructure — talk to all 10 and find out what would make them pay. The architecture might be completely right. Or it might be solving problems nobody has yet.

**3. The competitive environment is completely absent.**
Who else is building this? Jasper, Copy.ai, and the rest are consumer-grade and irrelevant — but what about agency-specific AI tools? What about Superagency, AgentOps, or whatever YC is funding this batch? The PRD makes no mention of competitive positioning. If a well-funded competitor ships agency self-serve AI workflows in 6 months, does Hazn's moat (trained agents, accumulated context) actually differentiate in time? This needs at least a paragraph, not a full competitive analysis.

---

### 🟡 Serious

**4. Letta is a third-party dependency for your core moat.**
The entire behavioral moat (trained agents, accumulated preferences) lives in Letta — a project maintained by a small team (Letta/MemGPT, ~$10M raised). If Letta changes their API, deprecates a feature, gets acquired, or goes under, your moat evaporates overnight. The PRD should acknowledge this dependency risk and define a mitigation: at minimum, abstract the memory layer behind your own interface so you can swap Letta out without rewriting every agent.

**5. There's no definition of what "good" looks like for a workflow output.**
The PRD defines when a task is "done" (F) but not what "done well" means. An analytics teaser can be generated and technically complete — but if it's mediocre, the client won't renew. Quality validation is not in any spike, not in any workflow definition, not in the success criteria. The QA Tester agent exists in the repo but isn't mentioned once in the PRD. Where does quality assurance fit in the platform?

**6. Memory without feedback is useless.**
Letta learns from sessions. But how does it know if what it learned was *correct*? If an agent writes "client prefers formal tone" to memory based on one session — but that was actually a one-off request — and the agent uses formal tone forever after, the memory is wrong and hurts quality. There's no mechanism for clients to correct agent memory. "This is wrong, forget it" is a critical UX feature that's completely absent.

---

### 🟠 Gaps

**7. No mention of the orchestrator's own complexity.**
The HAZN orchestrator (OpenClaw) is the thing that runs everything — spawns agents, loads context, manages workflows, handles HITL. But the PRD treats it as a given. The orchestrator needs to be significantly extended to handle: L2/L3 context loading, Letta block management, metering writes, HITL conflict flagging, session checkpoint syncs. That's a lot of new orchestrator logic. It needs its own section or spike.

**8. "Self-serve" for agencies implies their end-clients can also trigger workflows — but that's not addressed.**
If an agency logs into Hazn and runs workflows for their clients (L3), do the L3 clients ever get their own login? Can an end-client see their own audit reports, trigger a blog post, check on their website build? The PRD says nothing about L3 access. This might be intentional (agency controls everything) — but it needs to be stated explicitly or it'll be a source of confusion during Mode 3 design.

**9. No data on agent failure rates.**
Hazn agents fail sometimes — workflows crash, agents loop, outputs are wrong. The PRD assumes the memory layer will make agents better but doesn't acknowledge baseline failure rates. Before building a platform on top of these agents, you should know: what % of workflows complete successfully today? what's the P50/P95 runtime? what fails most often? Without this, the metering spike will surface surprises that should have been known already.

---

### 🔵 Minor

**10. "Being built into a platform" (Section 1) is vague.**
It's either a platform or it isn't. Pick a lane.

**11. The PRD has no version history.**
v1 through v5 happened in a chat thread. GSD has no way of knowing what changed between versions or why. Add a changelog at the top — even 3 lines per version. It matters when decisions get questioned later.

**12. Success criteria (Section 8) measures research completeness, not product success.**
"10 runs logged" is a research milestone, not a product success metric. What would make you confident Hazn is ready to charge money? That's the real success criterion and it's not in the doc.

---

## Summary

| Severity | Count | Biggest risk |
|---|---|---|
| 🔴 Critical | 3 | Three products in one PRD; 10 agencies not being used as signal; Letta is a single point of failure for the moat |
| 🟡 Serious | 3 | No quality definition; memory has no correction mechanism; orchestrator complexity unaddressed |
| 🟠 Gap | 3 | L3 access undefined; no baseline failure rates; no data on current agent quality |
| 🔵 Minor | 3 | Vague language; no version history; success criteria measures research not product |

**Verdict:** The architecture is getting solid. The strategic risks are now the bigger problem. The three-product ambiguity (#1) and the Letta dependency risk (#4) are the ones that could cause the most pain 6 months from now. Fix those two before handing to GSD.

want me to fix all of this and push a final v6?
assistant: going from a completely different angle this time — product strategy and execution, not just architecture.

---

## Red Team v3 — Strategy & Execution

### 🔴 Critical

**1. Hazn is trying to be three different products at once and the PRD doesn't force a choice.**
Mode 1 (consulting tool), Mode 2 (developer MCP), Mode 3 (agency self-serve) have different buyers, different sales motions, different support models, different infrastructure requirements. The PRD frames this as a sequence — but it's actually three bets. Building Mode 1 well doesn't automatically validate Mode 2. Agencies who use Hazn through Autonomous (Mode 1) may never want to self-operate it (Mode 3). The PRD needs to state the primary bet explicitly: *which mode is the real product?* The others are options, not a roadmap.

**2. The 10 existing agencies are your best signal — and you're not extracting it.**
The PRD mentions them once (Spike 6). But these agencies are using Hazn right now. What workflows are they actually requesting? What are they complaining about? What do they wish Hazn could do that it can't? There's no feedback loop in the PRD. Before building a memory layer, credential vault, and MCP infrastructure — talk to all 10 and find out what would make them pay. The architecture might be completely right. Or it might be solving problems nobody has yet.

**3. The competitive environment is completely absent.**
Who else is building this? Jasper, Copy.ai, and the rest are consumer-grade and irrelevant — but what about agency-specific AI tools? What about Superagency, AgentOps, or whatever YC is funding this batch? The PRD makes no mention of competitive positioning. If a well-funded competitor ships agency self-serve AI workflows in 6 months, does Hazn's moat (trained agents, accumulated context) actually differentiate in time? This needs at least a paragraph, not a full competitive analysis.

---

### 🟡 Serious

**4. Letta is a third-party dependency for your core moat.**
The entire behavioral moat (trained agents, accumulated preferences) lives in Letta — a project maintained by a small team (Letta/MemGPT, ~$10M raised). If Letta changes their API, deprecates a feature, gets acquired, or goes under, your moat evaporates overnight. The PRD should acknowledge this dependency risk and define a mitigation: at minimum, abstract the memory layer behind your own interface so you can swap Letta out without rewriting every agent.

**5. There's no definition of what "good" looks like for a workflow output.**
The PRD defines when a task is "done" (F) but not what "done well" means. An analytics teaser can be generated and technically complete — but if it's mediocre, the client won't renew. Quality validation is not in any spike, not in any workflow definition, not in the success criteria. The QA Tester agent exists in the repo but isn't mentioned once in the PRD. Where does quality assurance fit in the platform?

**6. Memory without feedback is useless.**
Letta learns from sessions. But how does it know if what it learned was *correct*? If an agent writes "client prefers formal tone" to memory based on one session — but that was actually a one-off request — and the agent uses formal tone forever after, the memory is wrong and hurts quality. There's no mechanism for clients to correct agent memory. "This is wrong, forget it" is a critical UX feature that's completely absent.

---

### 🟠 Gaps

**7. No mention of the orchestrator's own complexity.**
The HAZN orchestrator (OpenClaw) is the thing that runs everything — spawns agents, loads context, manages workflows, handles HITL. But the PRD treats it as a given. The orchestrator needs to be significantly extended to handle: L2/L3 context loading, Letta block management, metering writes, HITL conflict flagging, session checkpoint syncs. That's a lot of new orchestrator logic. It needs its own section or spike.

**8. "Self-serve" for agencies implies their end-clients can also trigger workflows — but that's not addressed.**
If an agency logs into Hazn and runs workflows for their clients (L3), do the L3 clients ever get their own login? Can an end-client see their own audit reports, trigger a blog post, check on their website build? The PRD says nothing about L3 access. This might be intentional (agency controls everything) — but it needs to be stated explicitly or it'll be a source of confusion during Mode 3 design.

**9. No data on agent failure rates.**
Hazn agents fail sometimes — workflows crash, agents loop, outputs are wrong. The PRD assumes the memory layer will make agents better but doesn't acknowledge baseline failure rates. Before building a platform on top of these agents, you should know: what % of workflows complete successfully today? what's the P50/P95 runtime? what fails most often? Without this, the metering spike will surface surprises that should have been known already.

---

### 🔵 Minor

**10. "Being built into a platform" (Section 1) is vague.**
It's either a platform or it isn't. Pick a lane.

**11. The PRD has no version history.**
v1 through v5 happened in a chat thread. GSD has no way of knowing what changed between versions or why. Add a changelog at the top — even 3 lines per version. It matters when decisions get questioned later.

**12. Success criteria (Section 8) measures research completeness, not product success.**
"10 runs logged" is a research milestone, not a product success metric. What would make you confident Hazn is ready to charge money? That's the real success criterion and it's not in the doc.

---

## Summary

| Severity | Count | Biggest risk |
|---|---|---|
| 🔴 Critical | 3 | Three products in one PRD; 10 agencies not being used as signal; Letta is a single point of failure for the moat |
| 🟡 Serious | 3 | No quality definition; memory has no correction mechanism; orchestrator complexity unaddressed |
| 🟠 Gap | 3 | L3 access undefined; no baseline failure rates; no data on current agent quality |
| 🔵 Minor | 3 | Vague language; no version history; success criteria measures research not product |

**Verdict:** The architecture is getting solid. The strategic risks are now the bigger problem. The three-product ambiguity (#1) and the Letta dependency risk (#4) are the ones that could cause the most pain 6 months from now. Fix those two before handing to GSD.

want me to fix all of this and push a final v6?
user: Conversation info (untrusted metadata):
```json
{
  "message_id": "3BDA24A955E6F5591886",
  "sender_id": "122256512565303@lid",
  "conversation_label": "120363407165595162@g.us",
  "sender": "+923321305389",
  "group_subject": "Hazn",
  "is_group_chat": true
}
```

Sender (untrusted metadata):
```json
{
  "label": "Rizwan Qaiser (+923321305389)",
  "name": "Rizwan Qaiser",
  "e164": "+923321305389"
}
```

1. Section 2 still says "Known unresolved problem" for L2/L3 conflict — but it was resolved in Section 0.
The body of the doc contradicts itself. Section 2 says "Flag as Open Question B" — which was answered in Section 0. GSD reads Section 2 as part of context-setting and will think it's still open. Fix: remove the stale text from Section 2.


Fix


3. need to be able to manage memory eventually.

4.  i dont understand.  clear please.

5. add the spec
6. add the diagram
7. ⁠yeah we need a better way. i like vault.
8. ⁠its fine for now? just a org creation situation….
9. ⁠they dont exist yet. 

4. We will deploy letta locally. 
6. sure lets do feedback?
7. ⁠openClaw can be shitty yes it needs support and fixes….yolo?
assistant: got it. one question before I fix everything — the most important one from v3:

> **Which is the primary product bet — Mode 1 (Autonomous uses Hazn to deliver work for clients), Mode 3 (agencies self-serve), or both equally?**

the architecture doesn't change but the PRD needs to name the primary one explicitly. everything else I can fix without your input:

**What I'll fix:**
- ✅ Remove stale L2/L3 text from Section 2
- ✅ Add memory management / correction as a planned feature (not deferred forever)
- ✅ Clarify #4: self-hosting Letta locally = you control the version, eliminates the SaaS dependency risk entirely. that's the answer.
- ✅ Add `mcp-hazn-memory` full tool spec
- ✅ Update architecture diagram with Langfuse + metering writes
- ✅ Replace Postgres credential storage with HashiCorp Vault (Postgres stores credential IDs only, Vault holds the secrets)
- ✅ L3 access: agencies control everything, no L3 logins in v1 — stated explicitly
- ✅ Agent failure rates: don't exist yet, Spike 6 captures from day 1
- ✅ Add version changelog
- ✅ Add QA agent to the platform
- ✅ Add memory feedback/correction mechanism spec

just need your answer on the primary product bet first, then I'll fix everything in one shot and push v6.
user: Conversation info (untrusted metadata):
```json
{
  "message_id": "3B203FB1997EA36DD6C5",
  "sender_id": "122256512565303@lid",
  "conversation_label": "120363407165595162@g.us",
  "sender": "+923321305389",
  "group_subject": "Hazn",
  "is_group_chat": true
}
```

Sender (untrusted metadata):
```json
{
  "label": "Rizwan Qaiser (+923321305389)",
  "name": "Rizwan Qaiser",
  "e164": "+923321305389"
}
```

its Mode 1 and Mode 3.
assistant: clear. Mode 1 and Mode 3 are co-primary. Mode 2 (MCP) is useful but not the bet. fixing everything now.
assistant: pushed ✅ — PRD v6 live.

**What changed:**
- **Primary bet explicit:** Mode 1 + Mode 3 co-primary. Mode 2 is optional.
- **Stale L2/L3 text gone** from Section 2
- **Letta self-hosted** — you control the version, no SaaS dependency. `HaznMemory` abstraction layer wraps it — swap-safe.
- **`mcp-hazn-memory` fully specced** — 6 tools: `load_context`, `write_finding`, `search_memory`, `checkpoint_sync`, `correct_memory`, `get_credentials`
- **HashiCorp Vault** replaces Postgres for secrets. Postgres stores vault IDs only.
- **Architecture diagram** updated — Langfuse, Vault, metering writes all visible
- **Memory correction** — `correct_memory()` method + Memory Inspector in Mode 3 workspace
- **QA Tester agent** added to agent spaces table
- **Spike order fixed** — Spike 5 runs first, Spike 1 depends on it
- **Postgres schema** uses enums + CHECK constraints, not loose `text` fields
- **Success criteria** has two sections — research phase AND product-ready-to-charge
user: Conversation info (untrusted metadata):
```json
{
  "message_id": "3B9DD4FA4F3040F36C8D",
  "sender_id": "122256512565303@lid",
  "conversation_label": "120363407165595162@g.us",
  "sender": "+923321305389",
  "group_subject": "Hazn",
  "is_group_chat": true
}
```

Sender (untrusted metadata):
```json
{
  "label": "Rizwan Qaiser (+923321305389)",
  "name": "Rizwan Qaiser",
  "e164": "+923321305389"
}
```

please update it on the repo
assistant: already done — pushed with the last commit. it's live at `autonomous-tech/hazn` on main as `docs/hazn-platform-prd.md`.

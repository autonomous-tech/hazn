# AI Agent Memory Systems Research
**Date:** 2026-02-22
**Status:** In Progress

## Context
We identified that agents (Haaris, Milo, etc.) are "lazy" about memory management — not disciplined about writing to memory or searching before answering. The question: should we integrate a proper memory layer like Mem0 or Letta?

## The Core Problem
- Current system has vector search (`memory_search`) but agents don't use it consistently
- No automatic extraction — agents must choose to write things down
- No consolidation logic (deduplication, conflict resolution)
- Sub-agents are fire-and-forget, don't write to shared memory

## Industry Pattern: Extract → Consolidate → Retrieve

Both **Mem0** and **AWS AgentCore Memory** use this pattern:

### 1. Extraction Phase (automatic, every message)
- LLM extracts "memory candidates" — facts, preferences, decisions
- Uses conversation summary + recent messages for context
- Agent doesn't have to "remember" to save things

### 2. Consolidation Phase (A.U.D.N. cycle)
For each extracted memory:
- Semantic search existing memories
- LLM decides: **ADD** / **UPDATE** / **DELETE** / **NOOP**
- Handles deduplication, conflict resolution automatically

### 3. Retrieval Phase
- Semantic search at query time
- Optional: graph-based for relational queries (Mem0g)

---

## Mem0 vs Letta Comparison

| | **Mem0** | **Letta (MemGPT)** |
|---|---|---|
| **GitHub Stars** | ~46k | ~42k |
| **Backing** | YC-backed | Berkeley research team |
| **Philosophy** | Memory as a *service* | Memory as *agent architecture* |
| **Self-hosting** | Possible but poorly documented | First-class, Desktop app |
| **SaaS** | Production-ready, main focus | Coming, not ready |
| **Approach** | Auto extract/consolidate/retrieve | OS-inspired memory hierarchy |
| **Benchmark (LoCoMo)** | 68.5% (graph variant) | 74.0% (filesystem + gpt-4o-mini) |

### Mem0
**Pros:**
- Automatic extraction on every message — no discipline required
- Simple API: `mem0.add(messages)`
- Research paper with benchmarks (2504.19413)
- Graph memory variant (Mem0g) for relational queries

**Cons:**
- SaaS-focused, self-hosting documentation sparse
- Pricing: $19/mo starter → $249/mo pro (big jump)
- Questionable benchmark methodology (Letta disputes their MemGPT numbers)

### Letta (MemGPT)
**Pros:**
- True open source, active community
- Agent manages its own memory like an OS
- Desktop app for easy self-hosting
- Their argument: "agent capability matters more than memory tooling"

**Cons:**
- More complex to integrate
- Depends heavily on LLM reasoning capability
- Not production-ready yet
- Agentic approach may be overkill

### Zep (also evaluated)
- Research-focused, technical depth
- Open-sourced `graphiti` algorithms
- SaaS immature, not ready for production
- Best technical blog content for learning

---

## Letta's Counter-Argument

Letta achieved 74% on LoCoMo with just **filesystem tools** (grep, search, open, close):

> "Memory is more about how agents manage context than the exact retrieval mechanism."

This suggests the real issue isn't storage/retrieval — it's whether the agent *uses* memory tools correctly. Which matches our diagnosis of "lazy" agents.

---

## Options for Clawdbot

1. **Integrate Mem0** — run as sidecar service, agents call `mem0.add()` after each exchange
2. **Build extraction into Clawdbot** — after each turn, run background extraction prompt
3. **Hybrid** — keep MEMORY.md for curated long-term, use Mem0 for automatic episodic
4. **Enforce discipline** — stricter prompts, required memory_search before first response
5. **Letta approach** — give agents filesystem tools, trust them to manage context

---

## Key Sources

- Mem0 paper: https://arxiv.org/abs/2504.19413
- Mem0 GitHub: https://github.com/mem0ai/mem0
- Letta GitHub: https://github.com/letta-ai/letta
- Letta benchmark critique: https://www.letta.com/blog/benchmarking-ai-agent-memory
- AWS AgentCore Memory: https://aws.amazon.com/blogs/machine-learning/building-smarter-ai-agents-agentcore-long-term-memory-deep-dive/
- Comparison article: https://medium.com/asymptotic-spaghetti-integration/from-beta-to-battle-tested-picking-between-letta-mem0-zep-for-ai-memory-6850ca8703d1

---

## TODO
- [ ] Deep dive on Mem0 self-hosting requirements
- [ ] Look at Mem0 MCP server (community project)
- [ ] Evaluate graphiti (Zep's open-source algorithms)
- [ ] Consider: is the "discipline" problem solvable with better prompts alone?
- [ ] Prototype: what would Clawdbot-native extraction look like?

---

## Decision Pending
Rizwan to review 2026-02-23

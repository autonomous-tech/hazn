# 2026-02-21 — Sene Hub Talio AI Work

## Context
Rizwan asked me to set up GitHub CLI and work on the Sene Hub project.

## What We Did
1. **GitHub CLI** — Already set up under LordXyTh account
2. **Cloned** `Sene-Hub/hub_2.0` repo
3. **Checked out** `ai-agent-poc` branch (Talio AI feature)

## Problem Found
Another developer was getting 500 errors on `/talio` endpoint that worked for Rizwan.

**Root cause:** `openai` and `anthropic` packages were only in `requirements/local.txt`, not `base.txt`. Other devs installing with different requirements file didn't get the packages.

## Fixes Applied
1. Added packages to `requirements/base.txt` (commit `ff0f7b42`)
2. Added comprehensive error handling (commit `a334fd20`):
   - Custom exception classes in `ai/exceptions.py`
   - Structured error responses with error codes
   - Health check on Streamlit startup
   - Enhanced `/talio/api/debug/` endpoint
   - Fix suggestions in UI

## Code Reviewed
- `sene_hub/talio/` — Django app for Talio AI
- `engine/orchestrator.py` — LLM-powered intent routing + subagent delegation
- `ai/claude_provider.py`, `ai/openai_provider.py` — AI provider adapters
- `streamlit_app/app.py` — Chat UI

## Retain
- W @SeneHub: Talio is an AI assistant for Sene Hub operations (order lookup, fit updates, measurements)
- W @SeneHub: Uses orchestrator pattern — main LLM routes to specialized subagents
- B @Haaris: Tested error handling without Docker using standalone Python test

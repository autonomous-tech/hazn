---
created: 2026-03-06T13:03:26.806Z
title: Add Claude API authentication setup
area: auth
files:
  - hazn_platform/hazn_platform/core/models.py (VaultCredential model)
  - hazn_platform/hazn_platform/orchestrator/tool_router.py (will need API key for Phase 9)
---

## Problem

Phase 9 (Agent Execution Runtime) will make real Anthropic API calls via the SDK. Currently there's no way for users to configure their own Claude API key or subscription. The codebase has a `VaultCredential` Django model for per-client API key management, but no developer-facing auth flow for local development or self-hosted setups.

User wants to be able to authenticate with their own Claude API key/subscription.

## Solution

Two-tier approach:
1. **Dev/local**: Environment variable `ANTHROPIC_API_KEY` via `.env` file — standard Anthropic SDK pattern, zero friction
2. **Production/multi-tenant**: Integrate with existing `VaultCredential` model for per-client key management with rotation and audit trails

Include in Phase 9 scope as a prerequisite task (Wave 0 or Wave 1) before any real LLM calls are made.

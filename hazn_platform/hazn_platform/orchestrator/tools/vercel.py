"""Vercel tools -- 4 tools ported from vercel_server.py.

Provides deployment management via the Vercel REST API using httpx (async).
All credentials are fetched from Vault at runtime per-request via
Agency.load() singleton -- no l2_agency_id parameter.

Tools
-----
1. ``deploy_project``        -- deploy a project from a Git repo
2. ``get_deployment_status`` -- check status of a deployment
3. ``get_preview_url``       -- get the preview URL for a deployment
4. ``list_deployments``      -- list recent deployments

Key differences from MCP server:
- No l2_agency_id param -- uses Agency.load() singleton internally
- Uses httpx.AsyncClient (already async, no sync_to_async needed for HTTP)
- Returns Agent SDK format: {"content": [{"type": "text", "text": "..."}]}
- Error handling returns {"content": [...], "isError": True}
"""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

VERCEL_API_BASE = "https://api.vercel.com"

# ---------------------------------------------------------------------------
# SDK tool decorator with graceful fallback
# ---------------------------------------------------------------------------

try:
    from claude_agent_sdk import tool  # type: ignore[import-untyped]
except ImportError:
    try:
        from claude_code_sdk import tool  # type: ignore[import-untyped]
    except ImportError:

        def tool(name: str, description: str, schema: dict | None = None):  # type: ignore[misc]
            """Stub @tool decorator for environments without the SDK."""

            def decorator(fn):
                class _StubTool:
                    def __init__(self):
                        self.name = name
                        self.description = description
                        self.schema = schema or {}
                        self._handler = fn

                    async def __call__(self, args: dict[str, Any]) -> dict[str, Any]:
                        return await self._handler(args)

                return _StubTool()

            return decorator


# ---------------------------------------------------------------------------
# sync_to_async import with fallback
# ---------------------------------------------------------------------------

try:
    from asgiref.sync import sync_to_async
except ImportError:
    import asyncio

    def sync_to_async(fn):  # type: ignore[misc]
        """Fallback sync_to_async using asyncio.to_thread."""
        async def wrapper(*args, **kwargs):
            return await asyncio.to_thread(fn, *args, **kwargs)
        return wrapper


# ---------------------------------------------------------------------------
# Internal helpers (deferred Django imports)
# ---------------------------------------------------------------------------


def _get_vercel_token_sync() -> str:
    """Fetch Vercel API token from Vault using Agency singleton.

    No params -- uses Agency.load() internally. Deferred Django imports.
    """
    from hazn_platform.core.models import Agency, VaultCredential
    from hazn_platform.core.vault import read_secret

    agency = Agency.load()
    credential = VaultCredential.objects.get(
        agency_id=agency.id,
        service_name="vercel",
        end_client__isnull=True,
    )
    secret = read_secret(credential.vault_secret_id)
    return secret["token"]


# ---------------------------------------------------------------------------
# Tool 1: deploy_project
# ---------------------------------------------------------------------------


@tool("deploy_project", "Deploy a project to Vercel from a Git repository.", {
    "project_name": str,
    "git_repo_id": str,
    "git_ref": str,
    "target": str,
})
async def deploy_project(args: dict[str, Any]) -> dict[str, Any]:
    """Deploy a project to Vercel from a Git repository.

    Creates a new deployment using the Vercel v13 deployments API
    with a gitSource configuration.
    """
    project_name = args["project_name"]
    git_repo_id = args["git_repo_id"]
    git_ref = args.get("git_ref", "main")
    target = args.get("target", "staging")

    try:
        token = await sync_to_async(_get_vercel_token_sync)()
        async with httpx.AsyncClient(
            base_url=VERCEL_API_BASE,
            headers={"Authorization": f"Bearer {token}"},
        ) as client:
            response = await client.post(
                "/v13/deployments",
                json={
                    "name": project_name,
                    "target": target,
                    "gitSource": {
                        "repoId": git_repo_id,
                        "ref": git_ref,
                        "type": "github",
                    },
                },
            )
            response.raise_for_status()
            data = response.json()
            result = {
                "deployment_id": data["id"],
                "url": data["url"],
                "ready_state": data["readyState"],
                "inspector_url": data.get("inspectorUrl", ""),
            }
            return {"content": [{"type": "text", "text": json.dumps(result)}]}
    except Exception as exc:
        logger.warning("deploy_project failed: %s", exc)
        return {
            "content": [{"type": "text", "text": f"Error deploying project: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Tool 2: get_deployment_status
# ---------------------------------------------------------------------------


@tool("get_deployment_status", "Get the current status of a Vercel deployment.", {
    "deployment_id": str,
})
async def get_deployment_status(args: dict[str, Any]) -> dict[str, Any]:
    """Get the current status of a Vercel deployment.

    Queries the Vercel v13 deployments API for deployment details
    including ready state and aliases.
    """
    deployment_id = args["deployment_id"]

    try:
        token = await sync_to_async(_get_vercel_token_sync)()
        async with httpx.AsyncClient(
            base_url=VERCEL_API_BASE,
            headers={"Authorization": f"Bearer {token}"},
        ) as client:
            response = await client.get(f"/v13/deployments/{deployment_id}")
            response.raise_for_status()
            data = response.json()
            result = {
                "deployment_id": data["id"],
                "url": data["url"],
                "ready_state": data["readyState"],
                "alias": data.get("alias", []),
            }
            return {"content": [{"type": "text", "text": json.dumps(result)}]}
    except Exception as exc:
        logger.warning("get_deployment_status failed: %s", exc)
        return {
            "content": [{"type": "text", "text": f"Error getting deployment status: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Tool 3: get_preview_url
# ---------------------------------------------------------------------------


@tool("get_preview_url", "Get the preview URL for a Vercel deployment.", {
    "deployment_id": str,
})
async def get_preview_url(args: dict[str, Any]) -> dict[str, Any]:
    """Get the preview URL for a Vercel deployment.

    Fetches deployment details and formats the preview URL as https://{url}.
    Returns whether the deployment is ready.
    """
    deployment_id = args["deployment_id"]

    try:
        token = await sync_to_async(_get_vercel_token_sync)()
        async with httpx.AsyncClient(
            base_url=VERCEL_API_BASE,
            headers={"Authorization": f"Bearer {token}"},
        ) as client:
            response = await client.get(f"/v13/deployments/{deployment_id}")
            response.raise_for_status()
            data = response.json()
            ready_state = data["readyState"]
            result = {
                "preview_url": f"https://{data['url']}",
                "ready": ready_state == "READY",
                "ready_state": ready_state,
            }
            return {"content": [{"type": "text", "text": json.dumps(result)}]}
    except Exception as exc:
        logger.warning("get_preview_url failed: %s", exc)
        return {
            "content": [{"type": "text", "text": f"Error getting preview URL: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Tool 4: list_deployments
# ---------------------------------------------------------------------------


@tool("list_deployments", "List recent Vercel deployments.", {
    "project_id": str,
    "limit": int,
})
async def list_deployments(args: dict[str, Any]) -> dict[str, Any]:
    """List recent Vercel deployments.

    Queries the Vercel v6 deployments API with optional project filtering.
    Returns a list of deployment summaries.
    """
    project_id = args.get("project_id")
    limit = args.get("limit", 10)

    try:
        token = await sync_to_async(_get_vercel_token_sync)()
        params: dict[str, Any] = {"limit": limit}
        if project_id:
            params["projectId"] = project_id

        async with httpx.AsyncClient(
            base_url=VERCEL_API_BASE,
            headers={"Authorization": f"Bearer {token}"},
        ) as client:
            response = await client.get("/v6/deployments", params=params)
            response.raise_for_status()
            data = response.json()
            result = [
                {
                    "id": d["uid"],
                    "name": d["name"],
                    "url": d["url"],
                    "state": d["state"],
                    "created": d["created"],
                }
                for d in data.get("deployments", [])
            ]
            return {"content": [{"type": "text", "text": json.dumps(result)}]}
    except Exception as exc:
        logger.warning("list_deployments failed: %s", exc)
        return {
            "content": [{"type": "text", "text": f"Error listing deployments: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Module-level tool list for registration
# ---------------------------------------------------------------------------

VERCEL_TOOLS = [
    deploy_project,
    get_deployment_status,
    get_preview_url,
    list_deployments,
]

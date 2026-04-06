"""GitHub tools -- 6 tools ported from github_server.py.

Provides repository and pull request management via PyGithub (sync).
All credentials are fetched from Vault at runtime per-request via
Agency.load() singleton -- no l2_agency_id parameter.

Tools
-----
1. ``create_repo``    -- create a new GitHub repository
2. ``create_pr``      -- open a pull request
3. ``get_pr_status``  -- check PR status and mergeability
4. ``get_ci_status``  -- check CI/check run status for a ref
5. ``list_branches``  -- list repository branches
6. ``merge_pr``       -- merge a pull request

Key differences from MCP server:
- No l2_agency_id param -- uses Agency.load() singleton internally
- Returns Agent SDK format: {"content": [{"type": "text", "text": "..."}]}
- Error handling returns {"content": [...], "isError": True}
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

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


def _get_github_client_sync():
    """Create an authenticated PyGithub client using Agency singleton + Vault.

    No params -- uses Agency.load() internally to find the GitHub PAT.
    Deferred Django imports for model and vault access.
    """
    from github import Auth, Github

    from hazn_platform.core.models import Agency, VaultCredential
    from hazn_platform.core.vault import read_secret

    agency = Agency.load()
    credential = VaultCredential.objects.get(
        agency_id=agency.id,
        service_name="github",
        end_client__isnull=True,
    )
    secret = read_secret(credential.vault_secret_id)
    return Github(auth=Auth.Token(secret["token"]))


# ---------------------------------------------------------------------------
# Tool 1: create_repo
# ---------------------------------------------------------------------------


@tool("create_repo", "Create a new GitHub repository.", {
    "name": str,
    "description": str,
    "private": bool,
})
async def create_repo(args: dict[str, Any]) -> dict[str, Any]:
    """Create a new GitHub repository.

    Creates a repo under the authenticated user's account with
    auto_init=True to include an initial commit.
    """
    name = args["name"]
    description = args.get("description", "")
    private = args.get("private", True)

    try:
        g = await sync_to_async(_get_github_client_sync)()
        repo = await sync_to_async(lambda: g.get_user().create_repo(
            name=name,
            description=description,
            private=private,
            auto_init=True,
        ))()
        result = {
            "id": repo.id,
            "full_name": repo.full_name,
            "clone_url": repo.clone_url,
            "html_url": repo.html_url,
        }
        return {"content": [{"type": "text", "text": json.dumps(result)}]}
    except Exception as exc:
        logger.warning("create_repo failed: %s", exc)
        return {
            "content": [{"type": "text", "text": f"Error creating repo: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Tool 2: create_pr
# ---------------------------------------------------------------------------


@tool("create_pr", "Open a pull request on a GitHub repository.", {
    "repo_full_name": str,
    "title": str,
    "head": str,
    "base": str,
    "body": str,
})
async def create_pr(args: dict[str, Any]) -> dict[str, Any]:
    """Open a pull request on a GitHub repository.

    Creates a PR from head branch to base branch with the given title and body.
    """
    repo_full_name = args["repo_full_name"]
    title = args["title"]
    head = args["head"]
    base = args.get("base", "main")
    body = args.get("body", "")

    try:
        g = await sync_to_async(_get_github_client_sync)()
        repo = await sync_to_async(g.get_repo)(repo_full_name)
        pr = await sync_to_async(lambda: repo.create_pull(
            title=title,
            head=head,
            base=base,
            body=body,
        ))()
        result = {
            "number": pr.number,
            "html_url": pr.html_url,
            "state": pr.state,
            "mergeable": pr.mergeable,
        }
        return {"content": [{"type": "text", "text": json.dumps(result)}]}
    except Exception as exc:
        logger.warning("create_pr failed: %s", exc)
        return {
            "content": [{"type": "text", "text": f"Error creating PR: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Tool 3: get_pr_status
# ---------------------------------------------------------------------------


@tool("get_pr_status", "Get the current status of a pull request.", {
    "repo_full_name": str,
    "pr_number": int,
})
async def get_pr_status(args: dict[str, Any]) -> dict[str, Any]:
    """Get the current status of a pull request.

    Returns PR state, mergeability, title, and URL.
    """
    repo_full_name = args["repo_full_name"]
    pr_number = args["pr_number"]

    try:
        g = await sync_to_async(_get_github_client_sync)()
        repo = await sync_to_async(g.get_repo)(repo_full_name)
        pr = await sync_to_async(repo.get_pull)(pr_number)
        result = {
            "number": pr.number,
            "state": pr.state,
            "mergeable": pr.mergeable,
            "title": pr.title,
            "html_url": pr.html_url,
        }
        return {"content": [{"type": "text", "text": json.dumps(result)}]}
    except Exception as exc:
        logger.warning("get_pr_status failed: %s", exc)
        return {
            "content": [{"type": "text", "text": f"Error getting PR status: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Tool 4: get_ci_status
# ---------------------------------------------------------------------------


@tool("get_ci_status", "Get CI/check run status for a Git ref.", {
    "repo_full_name": str,
    "ref": str,
})
async def get_ci_status(args: dict[str, Any]) -> dict[str, Any]:
    """Get CI/check run status for a Git ref.

    Fetches all check runs and the combined commit status for the given ref.
    """
    repo_full_name = args["repo_full_name"]
    ref = args.get("ref", "HEAD")

    try:
        g = await sync_to_async(_get_github_client_sync)()
        repo = await sync_to_async(g.get_repo)(repo_full_name)
        commit = await sync_to_async(repo.get_commit)(ref)
        check_runs = await sync_to_async(commit.get_check_runs)()
        combined = await sync_to_async(commit.get_combined_status)()
        result = {
            "ref": ref,
            "sha": commit.sha,
            "checks": [
                {
                    "name": cr.name,
                    "status": cr.status,
                    "conclusion": cr.conclusion,
                }
                for cr in check_runs
            ],
            "combined_status": combined.state,
        }
        return {"content": [{"type": "text", "text": json.dumps(result)}]}
    except Exception as exc:
        logger.warning("get_ci_status failed: %s", exc)
        return {
            "content": [{"type": "text", "text": f"Error getting CI status: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Tool 5: list_branches
# ---------------------------------------------------------------------------


@tool("list_branches", "List all branches in a GitHub repository.", {
    "repo_full_name": str,
})
async def list_branches(args: dict[str, Any]) -> dict[str, Any]:
    """List all branches in a GitHub repository.

    Returns branch names, commit SHAs, and protection status.
    """
    repo_full_name = args["repo_full_name"]

    try:
        g = await sync_to_async(_get_github_client_sync)()
        repo = await sync_to_async(g.get_repo)(repo_full_name)
        branches = await sync_to_async(repo.get_branches)()
        result = [
            {
                "name": b.name,
                "sha": b.commit.sha,
                "protected": b.protected,
            }
            for b in branches
        ]
        return {"content": [{"type": "text", "text": json.dumps(result)}]}
    except Exception as exc:
        logger.warning("list_branches failed: %s", exc)
        return {
            "content": [{"type": "text", "text": f"Error listing branches: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Tool 6: merge_pr
# ---------------------------------------------------------------------------


@tool("merge_pr", "Merge a pull request on a GitHub repository.", {
    "repo_full_name": str,
    "pr_number": int,
    "merge_method": str,
})
async def merge_pr(args: dict[str, Any]) -> dict[str, Any]:
    """Merge a pull request on a GitHub repository.

    Supports merge methods: merge, squash, rebase.
    """
    repo_full_name = args["repo_full_name"]
    pr_number = args["pr_number"]
    merge_method = args.get("merge_method", "squash")

    try:
        g = await sync_to_async(_get_github_client_sync)()
        repo = await sync_to_async(g.get_repo)(repo_full_name)
        pr = await sync_to_async(repo.get_pull)(pr_number)
        merge_status = await sync_to_async(pr.merge)(merge_method=merge_method)
        result = {
            "merged": merge_status.merged,
            "message": merge_status.message,
            "sha": merge_status.sha,
        }
        return {"content": [{"type": "text", "text": json.dumps(result)}]}
    except Exception as exc:
        logger.warning("merge_pr failed: %s", exc)
        return {
            "content": [{"type": "text", "text": f"Error merging PR: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Module-level tool list for registration
# ---------------------------------------------------------------------------

GITHUB_TOOLS = [
    create_repo,
    create_pr,
    get_pr_status,
    get_ci_status,
    list_branches,
    merge_pr,
]

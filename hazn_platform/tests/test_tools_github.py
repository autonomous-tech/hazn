"""Tests for GitHub tools -- 6 tools ported from github_server.py.

All Django ORM calls, Vault reads, and PyGithub are mocked.
Tests verify:
1. Zero auth params in tool signatures (Agency singleton PAT fetched internally)
2. Correct delegation to PyGithub
3. Agent SDK return format {"content": [{"type": "text", "text": "..."}]}
4. Error handling returns {"content": [...], "isError": True}
"""

from __future__ import annotations

import json
import uuid
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FAKE_AGENCY_ID = uuid.uuid4()


def _mock_agency():
    """Return a mock Agency singleton with .id attribute."""
    agency = MagicMock()
    agency.id = FAKE_AGENCY_ID
    return agency


def _patch_sync_to_async():
    """Patch sync_to_async to just run the sync function directly."""
    def fake_sync_to_async(fn):
        async def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return fake_sync_to_async


def _mock_github_client():
    """Create a mock PyGithub client."""
    return MagicMock()


# ---------------------------------------------------------------------------
# create_repo tests
# ---------------------------------------------------------------------------


class TestCreateRepo:
    """create_repo creates repo with zero auth params."""

    @pytest.mark.asyncio
    async def test_creates_repo_with_sdk_format(self):
        """create_repo returns repo info in Agent SDK format."""
        mock_g = _mock_github_client()
        mock_repo = MagicMock()
        mock_repo.id = 12345
        mock_repo.full_name = "user/test-repo"
        mock_repo.clone_url = "https://github.com/user/test-repo.git"
        mock_repo.html_url = "https://github.com/user/test-repo"
        mock_g.get_user.return_value.create_repo.return_value = mock_repo

        with (
            patch("hazn_platform.orchestrator.tools.github.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.github._get_github_client_sync", return_value=mock_g),
        ):
            from hazn_platform.orchestrator.tools.github import create_repo

            result = await create_repo.handler({
                "name": "test-repo",
                "description": "A test repo",
                "private": True,
            })

        text = result["content"][0]["text"]
        parsed = json.loads(text)
        assert parsed["full_name"] == "user/test-repo"
        assert parsed["id"] == 12345
        assert result["content"][0]["type"] == "text"

    @pytest.mark.asyncio
    async def test_no_l2_agency_id_param(self):
        """create_repo accepts no l2_agency_id -- only operation params."""
        mock_g = _mock_github_client()
        mock_repo = MagicMock()
        mock_repo.id = 1
        mock_repo.full_name = "u/r"
        mock_repo.clone_url = ""
        mock_repo.html_url = ""
        mock_g.get_user.return_value.create_repo.return_value = mock_repo

        with (
            patch("hazn_platform.orchestrator.tools.github.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.github._get_github_client_sync", return_value=mock_g),
        ):
            from hazn_platform.orchestrator.tools.github import create_repo

            # Should work without l2_agency_id
            result = await create_repo.handler({"name": "r"})

        assert result.get("isError") is not True


# ---------------------------------------------------------------------------
# create_pr tests
# ---------------------------------------------------------------------------


class TestCreatePr:
    """create_pr opens PR with zero auth params."""

    @pytest.mark.asyncio
    async def test_creates_pr(self):
        """create_pr delegates to PyGithub and returns PR info."""
        mock_g = _mock_github_client()
        mock_pr = MagicMock()
        mock_pr.number = 42
        mock_pr.html_url = "https://github.com/user/repo/pull/42"
        mock_pr.state = "open"
        mock_pr.mergeable = True
        mock_g.get_repo.return_value.create_pull.return_value = mock_pr

        with (
            patch("hazn_platform.orchestrator.tools.github.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.github._get_github_client_sync", return_value=mock_g),
        ):
            from hazn_platform.orchestrator.tools.github import create_pr

            result = await create_pr.handler({
                "repo_full_name": "user/repo",
                "title": "Test PR",
                "head": "feature",
                "base": "main",
            })

        text = result["content"][0]["text"]
        parsed = json.loads(text)
        assert parsed["number"] == 42
        assert parsed["state"] == "open"


# ---------------------------------------------------------------------------
# get_pr_status tests
# ---------------------------------------------------------------------------


class TestGetPrStatus:
    """get_pr_status returns PR details."""

    @pytest.mark.asyncio
    async def test_returns_pr_details(self):
        """get_pr_status returns PR status info in SDK format."""
        mock_g = _mock_github_client()
        mock_pr = MagicMock()
        mock_pr.number = 10
        mock_pr.state = "open"
        mock_pr.mergeable = True
        mock_pr.title = "Fix bug"
        mock_pr.html_url = "https://github.com/u/r/pull/10"
        mock_g.get_repo.return_value.get_pull.return_value = mock_pr

        with (
            patch("hazn_platform.orchestrator.tools.github.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.github._get_github_client_sync", return_value=mock_g),
        ):
            from hazn_platform.orchestrator.tools.github import get_pr_status

            result = await get_pr_status.handler({
                "repo_full_name": "u/r",
                "pr_number": 10,
            })

        text = result["content"][0]["text"]
        parsed = json.loads(text)
        assert parsed["number"] == 10
        assert parsed["title"] == "Fix bug"


# ---------------------------------------------------------------------------
# get_ci_status tests
# ---------------------------------------------------------------------------


class TestGetCiStatus:
    """get_ci_status returns check runs."""

    @pytest.mark.asyncio
    async def test_returns_check_runs(self):
        """get_ci_status returns CI check info in SDK format."""
        mock_g = _mock_github_client()
        mock_check = MagicMock()
        mock_check.name = "lint"
        mock_check.status = "completed"
        mock_check.conclusion = "success"
        mock_commit = MagicMock()
        mock_commit.sha = "abc123"
        mock_commit.get_check_runs.return_value = [mock_check]
        mock_combined = MagicMock()
        mock_combined.state = "success"
        mock_commit.get_combined_status.return_value = mock_combined
        mock_g.get_repo.return_value.get_commit.return_value = mock_commit

        with (
            patch("hazn_platform.orchestrator.tools.github.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.github._get_github_client_sync", return_value=mock_g),
        ):
            from hazn_platform.orchestrator.tools.github import get_ci_status

            result = await get_ci_status.handler({
                "repo_full_name": "u/r",
                "ref": "main",
            })

        text = result["content"][0]["text"]
        parsed = json.loads(text)
        assert parsed["sha"] == "abc123"
        assert parsed["combined_status"] == "success"
        assert len(parsed["checks"]) == 1
        assert parsed["checks"][0]["name"] == "lint"


# ---------------------------------------------------------------------------
# list_branches tests
# ---------------------------------------------------------------------------


class TestListBranches:
    """list_branches returns branch list."""

    @pytest.mark.asyncio
    async def test_returns_branch_list(self):
        """list_branches returns branches in SDK format."""
        mock_g = _mock_github_client()
        mock_branch = MagicMock()
        mock_branch.name = "main"
        mock_branch.commit.sha = "def456"
        mock_branch.protected = True
        mock_g.get_repo.return_value.get_branches.return_value = [mock_branch]

        with (
            patch("hazn_platform.orchestrator.tools.github.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.github._get_github_client_sync", return_value=mock_g),
        ):
            from hazn_platform.orchestrator.tools.github import list_branches

            result = await list_branches.handler({"repo_full_name": "u/r"})

        text = result["content"][0]["text"]
        parsed = json.loads(text)
        assert isinstance(parsed, list)
        assert parsed[0]["name"] == "main"
        assert parsed[0]["protected"] is True


# ---------------------------------------------------------------------------
# merge_pr tests
# ---------------------------------------------------------------------------


class TestMergePr:
    """merge_pr merges PR with squash default."""

    @pytest.mark.asyncio
    async def test_merges_pr_with_squash(self):
        """merge_pr merges with squash method by default."""
        mock_g = _mock_github_client()
        mock_merge = MagicMock()
        mock_merge.merged = True
        mock_merge.message = "Pull Request successfully merged"
        mock_merge.sha = "merge123"
        mock_g.get_repo.return_value.get_pull.return_value.merge.return_value = mock_merge

        with (
            patch("hazn_platform.orchestrator.tools.github.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.github._get_github_client_sync", return_value=mock_g),
        ):
            from hazn_platform.orchestrator.tools.github import merge_pr

            result = await merge_pr.handler({
                "repo_full_name": "u/r",
                "pr_number": 5,
            })

        text = result["content"][0]["text"]
        parsed = json.loads(text)
        assert parsed["merged"] is True
        assert parsed["sha"] == "merge123"
        # Verify squash is default merge method
        mock_g.get_repo.return_value.get_pull.return_value.merge.assert_called_once_with(
            merge_method="squash"
        )


# ---------------------------------------------------------------------------
# Error handling tests
# ---------------------------------------------------------------------------


class TestGitHubErrors:
    """Tool errors return {"content": [...], "isError": True}."""

    @pytest.mark.asyncio
    async def test_github_exception_returns_error(self):
        """GithubException is caught and returned as error content."""
        from github import GithubException

        mock_g = _mock_github_client()
        mock_g.get_user.return_value.create_repo.side_effect = GithubException(
            404, {"message": "Not Found"}, None
        )

        with (
            patch("hazn_platform.orchestrator.tools.github.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.github._get_github_client_sync", return_value=mock_g),
        ):
            from hazn_platform.orchestrator.tools.github import create_repo

            result = await create_repo.handler({"name": "nonexistent"})

        assert result.get("isError") is True
        assert result["content"][0]["type"] == "text"

    @pytest.mark.asyncio
    async def test_generic_exception_returns_error(self):
        """Generic exceptions are caught and returned as error content."""
        mock_g = _mock_github_client()
        mock_g.get_user.return_value.create_repo.side_effect = RuntimeError("connection failed")

        with (
            patch("hazn_platform.orchestrator.tools.github.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.github._get_github_client_sync", return_value=mock_g),
        ):
            from hazn_platform.orchestrator.tools.github import create_repo

            result = await create_repo.handler({"name": "fail"})

        assert result.get("isError") is True

"""Tests for Vercel tools -- 4 tools ported from vercel_server.py.

All Django ORM calls, Vault reads, and httpx are mocked.
Tests verify:
1. Zero auth params (Agency singleton Vercel token fetched internally)
2. Correct delegation to Vercel REST API via httpx
3. Agent SDK return format {"content": [{"type": "text", "text": "..."}]}
4. HTTP error handling returns error content gracefully
"""

from __future__ import annotations

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

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


def _make_mock_response(json_data: dict, status_code: int = 200):
    """Create a MagicMock httpx response with sync .json() method."""
    response = MagicMock()
    response.json.return_value = json_data
    response.status_code = status_code
    response.raise_for_status = MagicMock()
    return response


def _make_mock_client(method: str, response):
    """Create an async mock httpx client with proper context manager support."""
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    setattr(mock_client, method, AsyncMock(return_value=response))
    return mock_client


# ---------------------------------------------------------------------------
# deploy_project tests
# ---------------------------------------------------------------------------


class TestDeployProject:
    """deploy_project deploys with zero auth params."""

    @pytest.mark.asyncio
    async def test_deploys_project(self):
        """deploy_project sends deployment request and returns info in SDK format."""
        mock_response = _make_mock_response({
            "id": "dpl_123",
            "url": "project-abc.vercel.app",
            "readyState": "BUILDING",
            "inspectorUrl": "https://vercel.com/inspect/dpl_123",
        })
        mock_client = _make_mock_client("post", mock_response)

        with (
            patch("hazn_platform.orchestrator.tools.vercel.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.vercel._get_vercel_token_sync", return_value="fake-token"),
            patch("hazn_platform.orchestrator.tools.vercel.httpx.AsyncClient", return_value=mock_client),
        ):
            from hazn_platform.orchestrator.tools.vercel import deploy_project

            result = await deploy_project.handler({
                "project_name": "my-project",
                "git_repo_id": "repo-123",
                "git_ref": "main",
                "target": "staging",
            })

        text = result["content"][0]["text"]
        parsed = json.loads(text)
        assert parsed["deployment_id"] == "dpl_123"
        assert parsed["url"] == "project-abc.vercel.app"
        assert parsed["ready_state"] == "BUILDING"

    @pytest.mark.asyncio
    async def test_no_l2_agency_id_param(self):
        """deploy_project accepts no l2_agency_id -- only operation params."""
        mock_response = _make_mock_response({
            "id": "d1",
            "url": "x.vercel.app",
            "readyState": "READY",
        })
        mock_client = _make_mock_client("post", mock_response)

        with (
            patch("hazn_platform.orchestrator.tools.vercel.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.vercel._get_vercel_token_sync", return_value="tok"),
            patch("hazn_platform.orchestrator.tools.vercel.httpx.AsyncClient", return_value=mock_client),
        ):
            from hazn_platform.orchestrator.tools.vercel import deploy_project

            result = await deploy_project.handler({"project_name": "p", "git_repo_id": "r"})

        assert result.get("isError") is not True


# ---------------------------------------------------------------------------
# get_deployment_status tests
# ---------------------------------------------------------------------------


class TestGetDeploymentStatus:
    """get_deployment_status returns deployment details."""

    @pytest.mark.asyncio
    async def test_returns_deployment_status(self):
        """get_deployment_status returns status info in SDK format."""
        mock_response = _make_mock_response({
            "id": "dpl_456",
            "url": "project.vercel.app",
            "readyState": "READY",
            "alias": ["project.com"],
        })
        mock_client = _make_mock_client("get", mock_response)

        with (
            patch("hazn_platform.orchestrator.tools.vercel.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.vercel._get_vercel_token_sync", return_value="tok"),
            patch("hazn_platform.orchestrator.tools.vercel.httpx.AsyncClient", return_value=mock_client),
        ):
            from hazn_platform.orchestrator.tools.vercel import get_deployment_status

            result = await get_deployment_status.handler({"deployment_id": "dpl_456"})

        text = result["content"][0]["text"]
        parsed = json.loads(text)
        assert parsed["deployment_id"] == "dpl_456"
        assert parsed["ready_state"] == "READY"
        assert parsed["alias"] == ["project.com"]


# ---------------------------------------------------------------------------
# get_preview_url tests
# ---------------------------------------------------------------------------


class TestGetPreviewUrl:
    """get_preview_url returns preview URL."""

    @pytest.mark.asyncio
    async def test_returns_preview_url(self):
        """get_preview_url returns formatted preview URL in SDK format."""
        mock_response = _make_mock_response({
            "url": "project-abc123.vercel.app",
            "readyState": "READY",
        })
        mock_client = _make_mock_client("get", mock_response)

        with (
            patch("hazn_platform.orchestrator.tools.vercel.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.vercel._get_vercel_token_sync", return_value="tok"),
            patch("hazn_platform.orchestrator.tools.vercel.httpx.AsyncClient", return_value=mock_client),
        ):
            from hazn_platform.orchestrator.tools.vercel import get_preview_url

            result = await get_preview_url.handler({"deployment_id": "dpl_789"})

        text = result["content"][0]["text"]
        parsed = json.loads(text)
        assert parsed["preview_url"] == "https://project-abc123.vercel.app"
        assert parsed["ready"] is True
        assert parsed["ready_state"] == "READY"


# ---------------------------------------------------------------------------
# list_deployments tests
# ---------------------------------------------------------------------------


class TestListDeployments:
    """list_deployments returns deployment list with optional limit."""

    @pytest.mark.asyncio
    async def test_returns_deployment_list(self):
        """list_deployments returns list of deployments in SDK format."""
        mock_response = _make_mock_response({
            "deployments": [
                {
                    "uid": "d1",
                    "name": "project-a",
                    "url": "a.vercel.app",
                    "state": "READY",
                    "created": 1700000000000,
                },
                {
                    "uid": "d2",
                    "name": "project-a",
                    "url": "b.vercel.app",
                    "state": "BUILDING",
                    "created": 1700000001000,
                },
            ]
        })
        mock_client = _make_mock_client("get", mock_response)

        with (
            patch("hazn_platform.orchestrator.tools.vercel.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.vercel._get_vercel_token_sync", return_value="tok"),
            patch("hazn_platform.orchestrator.tools.vercel.httpx.AsyncClient", return_value=mock_client),
        ):
            from hazn_platform.orchestrator.tools.vercel import list_deployments

            result = await list_deployments.handler({"limit": 5})

        text = result["content"][0]["text"]
        parsed = json.loads(text)
        assert isinstance(parsed, list)
        assert len(parsed) == 2
        assert parsed[0]["id"] == "d1"
        assert parsed[1]["state"] == "BUILDING"

    @pytest.mark.asyncio
    async def test_optional_project_id_filter(self):
        """list_deployments passes project_id to Vercel API when provided."""
        mock_response = _make_mock_response({"deployments": []})
        mock_client = _make_mock_client("get", mock_response)

        with (
            patch("hazn_platform.orchestrator.tools.vercel.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.vercel._get_vercel_token_sync", return_value="tok"),
            patch("hazn_platform.orchestrator.tools.vercel.httpx.AsyncClient", return_value=mock_client),
        ):
            from hazn_platform.orchestrator.tools.vercel import list_deployments

            result = await list_deployments.handler({"project_id": "prj_abc", "limit": 3})

        assert result.get("isError") is not True
        # Verify the API call included project_id
        mock_client.get.assert_called_once()
        call_kwargs = mock_client.get.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params", {})
        assert params.get("projectId") == "prj_abc"


# ---------------------------------------------------------------------------
# Error handling tests
# ---------------------------------------------------------------------------


class TestVercelErrors:
    """HTTP errors from Vercel API return error content gracefully."""

    @pytest.mark.asyncio
    async def test_http_error_returns_error_content(self):
        """HTTP status errors are caught and returned as error content."""
        import httpx

        mock_request = MagicMock()
        mock_request.url = "https://api.vercel.com/v13/deployments"
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Forbidden", request=mock_request, response=mock_response
        )
        mock_client = _make_mock_client("post", mock_response)

        with (
            patch("hazn_platform.orchestrator.tools.vercel.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.vercel._get_vercel_token_sync", return_value="tok"),
            patch("hazn_platform.orchestrator.tools.vercel.httpx.AsyncClient", return_value=mock_client),
        ):
            from hazn_platform.orchestrator.tools.vercel import deploy_project

            result = await deploy_project.handler({"project_name": "p", "git_repo_id": "r"})

        assert result.get("isError") is True
        assert result["content"][0]["type"] == "text"

    @pytest.mark.asyncio
    async def test_connection_error_returns_error_content(self):
        """Connection errors are caught and returned as error content."""
        import httpx

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))

        with (
            patch("hazn_platform.orchestrator.tools.vercel.sync_to_async", side_effect=_patch_sync_to_async()),
            patch("hazn_platform.orchestrator.tools.vercel._get_vercel_token_sync", return_value="tok"),
            patch("hazn_platform.orchestrator.tools.vercel.httpx.AsyncClient", return_value=mock_client),
        ):
            from hazn_platform.orchestrator.tools.vercel import get_deployment_status

            result = await get_deployment_status.handler({"deployment_id": "dpl_999"})

        assert result.get("isError") is True

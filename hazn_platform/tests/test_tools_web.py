"""Tests for web tools -- fetch_page.

All httpx calls are mocked to avoid real network requests.
"""

from __future__ import annotations

from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# fetch_page tests
# ---------------------------------------------------------------------------

_SAMPLE_HTML = """
<html>
<head><title>Test Page</title></head>
<body>
<h1>Hello World</h1>
<p>This is a test paragraph with <strong>bold text</strong>.</p>
<nav>Navigation links here</nav>
<footer>Footer content</footer>
</body>
</html>
"""


class TestFetchPage:
    """fetch_page returns extracted text content from an HTML page."""

    @pytest.mark.asyncio
    async def test_returns_extracted_text(self):
        """fetch_page returns text content extracted from HTML (mock httpx)."""
        from hazn_platform.orchestrator.tools.web import fetch_page

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = _SAMPLE_HTML
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await fetch_page.handler({"url": "https://example.com"})

        assert result.get("isError") is not True
        text = result["content"][0]["text"]
        assert "Hello World" in text
        assert "test paragraph" in text

    @pytest.mark.asyncio
    async def test_returns_error_on_connection_failure(self):
        """fetch_page returns error message for connection failures."""
        from hazn_platform.orchestrator.tools.web import fetch_page

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await fetch_page.handler({"url": "https://unreachable.example.com"})

        assert result.get("isError") is True
        text = result["content"][0]["text"]
        assert "error" in text.lower() or "Connection refused" in text

    @pytest.mark.asyncio
    async def test_truncates_long_content(self):
        """fetch_page truncates very long content to max_length."""
        from hazn_platform.orchestrator.tools.web import fetch_page

        # Generate HTML with very long text content
        long_text = "A" * 100_000
        long_html = f"<html><body><p>{long_text}</p></body></html>"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = long_html
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await fetch_page.handler({"url": "https://example.com", "max_length": 500})

        assert result.get("isError") is not True
        text = result["content"][0]["text"]
        assert len(text) <= 500

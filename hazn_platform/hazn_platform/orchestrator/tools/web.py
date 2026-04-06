"""Web fetch tool -- fetch_page.

Standalone async Python function that fetches a URL and extracts text
content from the HTML response. Uses httpx for async HTTP and
beautifulsoup4 for HTML parsing (with regex fallback if bs4 unavailable).

Registered with the ToolRegistry via the module-level ``TOOLS`` list.

No Django imports required.
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Default max length for extracted text to avoid context window bloat
_DEFAULT_MAX_LENGTH = 50_000

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
            """Stub @tool decorator."""

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
# HTML text extraction
# ---------------------------------------------------------------------------


def _extract_text_bs4(html: str) -> str:
    """Extract text from HTML using BeautifulSoup."""
    from bs4 import BeautifulSoup  # noqa: PLC0415

    soup = BeautifulSoup(html, "html.parser")
    # Remove script and style elements
    for element in soup(["script", "style"]):
        element.decompose()
    return soup.get_text(separator="\n", strip=True)


def _extract_text_regex(html: str) -> str:
    """Extract text from HTML using regex (fallback when bs4 unavailable)."""
    # Remove script/style blocks
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "\n", text)
    # Decode common HTML entities
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " ")
    # Collapse whitespace
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text.strip()


def _extract_text(html: str) -> str:
    """Extract text from HTML, preferring bs4 with regex fallback."""
    try:
        return _extract_text_bs4(html)
    except ImportError:
        return _extract_text_regex(html)


# ---------------------------------------------------------------------------
# Tool implementation
# ---------------------------------------------------------------------------


@tool("fetch_page", "Fetch a URL and return extracted text content.", {
    "url": str,
    "max_length": int,
})
async def fetch_page(args: dict[str, Any]) -> dict[str, Any]:
    """Fetch ``args["url"]`` and return extracted text content.

    Parameters (via args dict)
    --------------------------
    url : str
        The URL to fetch.
    max_length : int, optional
        Maximum length of returned text (default 50000). Truncates if exceeded.

    Returns error content with ``isError: True`` on timeout or connection failure.
    """
    import httpx  # noqa: PLC0415

    url = args["url"]
    max_length = args.get("max_length", _DEFAULT_MAX_LENGTH)

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

        text = _extract_text(response.text)

        # Truncate to max_length
        if len(text) > max_length:
            text = text[:max_length]

        return {"content": [{"type": "text", "text": text}]}

    except Exception as exc:
        logger.warning("fetch_page failed for %s: %s", url, exc)
        return {
            "content": [{"type": "text", "text": f"Error fetching {url}: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Module-level tool list for registration
# ---------------------------------------------------------------------------

TOOLS = [fetch_page]

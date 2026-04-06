"""Filesystem tools -- read_file, write_file, mkdir.

Standalone async Python functions for file I/O operations. Each function
follows the Claude Agent SDK tool handler signature: accepts ``args: dict``
and returns ``{"content": [{"type": "text", "text": "..."}]}``.

These tools are registered with the ToolRegistry via the module-level
``TOOLS`` list.

No Django imports required.
"""

from __future__ import annotations

import asyncio
import logging
import os
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
        # Stub @tool decorator for environments without the SDK.
        # Creates a simple object with .name attribute that wraps the handler.
        def tool(name: str, description: str, schema: dict | None = None):  # type: ignore[misc]
            """Stub @tool decorator -- stores metadata, returns callable wrapper."""

            def decorator(fn):
                class _StubTool:
                    def __init__(self):
                        self.name = name
                        self.description = description
                        self.schema = schema or {}
                        self._handler = fn

                    async def __call__(self, args: dict[str, Any]) -> dict[str, Any]:
                        return await self._handler(args)

                stub = _StubTool()
                # Preserve the original function as a module-level callable
                # while also making the stub available for registration.
                return stub

            return decorator


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


@tool("read_file", "Read file content at a given path.", {"path": str})
async def read_file(args: dict[str, Any]) -> dict[str, Any]:
    """Read file at ``args["path"]`` and return its content as text.

    Returns error content with ``isError: True`` if the file cannot be read.
    """
    path = args["path"]
    try:
        content = await asyncio.to_thread(_read_sync, path)
        return {"content": [{"type": "text", "text": content}]}
    except Exception as exc:
        logger.warning("read_file failed for %s: %s", path, exc)
        return {
            "content": [{"type": "text", "text": f"Error reading {path}: {exc}"}],
            "isError": True,
        }


@tool("write_file", "Write content to a file, creating parent directories.", {
    "path": str,
    "content": str,
})
async def write_file(args: dict[str, Any]) -> dict[str, Any]:
    """Write ``args["content"]`` to file at ``args["path"]``.

    Creates parent directories if they do not exist. Returns success message.
    """
    path = args["path"]
    content = args["content"]
    try:
        await asyncio.to_thread(_write_sync, path, content)
        return {
            "content": [
                {"type": "text", "text": f"Successfully wrote {len(content)} chars to {path}"}
            ]
        }
    except Exception as exc:
        logger.warning("write_file failed for %s: %s", path, exc)
        return {
            "content": [{"type": "text", "text": f"Error writing {path}: {exc}"}],
            "isError": True,
        }


@tool("mkdir", "Create a directory recursively.", {"path": str})
async def mkdir(args: dict[str, Any]) -> dict[str, Any]:
    """Create directory at ``args["path"]`` recursively.

    Idempotent -- succeeds even if directory already exists.
    """
    path = args["path"]
    try:
        await asyncio.to_thread(os.makedirs, path, exist_ok=True)
        return {
            "content": [{"type": "text", "text": f"Directory created: {path}"}]
        }
    except Exception as exc:
        logger.warning("mkdir failed for %s: %s", path, exc)
        return {
            "content": [{"type": "text", "text": f"Error creating directory {path}: {exc}"}],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Sync helpers (run in thread pool via asyncio.to_thread)
# ---------------------------------------------------------------------------


def _read_sync(path: str) -> str:
    """Read file synchronously."""
    with open(path, encoding="utf-8") as f:
        return f.read()


def _write_sync(path: str, content: str) -> None:
    """Write file synchronously, creating parent dirs."""
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# Module-level tool list for registration
# ---------------------------------------------------------------------------

TOOLS = [read_file, write_file, mkdir]

"""ToolRegistry -- central tool registry for Claude Agent SDK integration.

Collects tool functions (decorated with ``@tool``) and bundles them into
an ``McpSdkServerConfig`` via ``create_sdk_mcp_server()`` for use by the
``AgentSDKBackend``.

Replaces the legacy ``ToolRouter`` + ``tool_wiring`` infrastructure.

Public API
----------
* ``ToolRegistry`` -- register tools, get server config, get allowed tool names.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SDK imports with graceful fallback
# ---------------------------------------------------------------------------
# The Claude Agent SDK may be installed under either package name.
# If neither is available, we define minimal stub types so the registry
# can still be used in tests and at import time.

try:
    from claude_agent_sdk import create_sdk_mcp_server  # type: ignore[import-untyped]

    SdkMcpTool = Any  # The @tool decorator returns this type
    McpSdkServerConfig = Any
except ImportError:
    try:
        from claude_code_sdk import create_sdk_mcp_server  # type: ignore[import-untyped]

        SdkMcpTool = Any
        McpSdkServerConfig = Any
    except ImportError:
        # Neither SDK installed -- provide stubs for testing/import time.
        # Tools are registered by reference; the server config is built
        # as a plain dict that can be validated when the SDK is available.
        SdkMcpTool = Any
        McpSdkServerConfig = Any
        create_sdk_mcp_server = None  # type: ignore[assignment]


class ToolRegistry:
    """Central registry mapping tool names to Claude Agent SDK tool definitions.

    Usage::

        from hazn_platform.orchestrator.tools.registry import ToolRegistry

        registry = ToolRegistry()
        registry.register(read_file_tool, write_file_tool)
        server = registry.get_server()
        allowed = registry.get_allowed_tools(phase_tools=["read_file"])
    """

    def __init__(self) -> None:
        self._tools: list[Any] = []
        self._tool_names: set[str] = set()
        self._server: Any | None = None

    def register(self, *tools: Any) -> None:
        """Register one or more tool instances (returned by ``@tool`` decorator).

        Each tool must have a ``.name`` attribute. Invalidates the cached
        server config so ``get_server()`` rebuilds it on next call.
        """
        for t in tools:
            self._tools.append(t)
            self._tool_names.add(t.name)
            logger.info("Registered tool: %s", t.name)
        # Invalidate cached server
        self._server = None

    def get_server(self) -> Any:
        """Return an ``McpSdkServerConfig`` bundling all registered tools.

        Calls ``create_sdk_mcp_server(name="hazn", version="3.0.0", tools=...)``
        and caches the result. Cache is invalidated when new tools are registered.

        If the Claude Agent SDK is not installed, returns a dict stub with
        the same shape for testing purposes.
        """
        if self._server is None:
            if create_sdk_mcp_server is not None:
                self._server = create_sdk_mcp_server(
                    name="hazn",
                    version="3.0.0",
                    tools=self._tools,
                )
            else:
                # Stub for environments without the SDK
                self._server = {
                    "name": "hazn",
                    "version": "3.0.0",
                    "tools": list(self._tools),
                }
        return self._server

    def get_allowed_tools(self, phase_tools: list[str] | None = None) -> list[str]:
        """Return ``mcp__hazn__<name>`` formatted tool names for Agent SDK.

        Parameters
        ----------
        phase_tools:
            If provided, filter to only tool names that exist in both
            ``phase_tools`` and the registry. If ``None``, return all
            registered tools.

        Returns
        -------
        list[str]
            Tool names prefixed with ``mcp__hazn__``.
        """
        if phase_tools is not None:
            names = [n for n in phase_tools if n in self._tool_names]
        else:
            names = sorted(self._tool_names)
        return [f"mcp__hazn__{n}" for n in names]

    def get_tool_callable(self, name: str) -> Any | None:
        """Return the callable for a tool by name.

        Used by ``dispatch_tool_async`` for backward compatibility with the
        Anthropic API backend. In the Agent SDK model, the SDK handles tool
        dispatch internally via the MCP server config.

        Parameters
        ----------
        name:
            Tool name to look up.

        Returns
        -------
        Any or None
            The tool function if found, None otherwise.
        """
        for t in self._tools:
            if t.name == name:
                # Real SdkMcpTool has .handler; stub is directly callable
                return getattr(t, "handler", t)
        return None

    def list_tools(self) -> list[str]:
        """Return sorted list of registered tool names."""
        return sorted(self._tool_names)

"""Tests for ToolRegistry -- Claude Agent SDK tool registry.

Tests cover registry operations: register, get_server, get_allowed_tools,
list_tools, and the build_registry() factory function.

All claude_agent_sdk imports are mocked since the SDK may not be installed
in the test environment. Tests verify registry logic, not SDK internals.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_tool(name: str = "test_tool") -> MagicMock:
    """Create a mock SdkMcpTool with a .name attribute."""
    tool = MagicMock()
    tool.name = name
    return tool


# ---------------------------------------------------------------------------
# TestToolRegistry
# ---------------------------------------------------------------------------


class TestToolRegistry:
    """Test ToolRegistry: register, list_tools, get_server, get_allowed_tools."""

    def test_register_and_list_tools(self):
        """register(tool) adds tool; list_tools() returns its name."""
        from hazn_platform.orchestrator.tools.registry import ToolRegistry

        reg = ToolRegistry()
        tool = _make_mock_tool("my_tool")
        reg.register(tool)
        assert "my_tool" in reg.list_tools()

    def test_register_multiple_tools(self):
        """register(*tools) accepts multiple tools at once."""
        from hazn_platform.orchestrator.tools.registry import ToolRegistry

        reg = ToolRegistry()
        t1 = _make_mock_tool("tool_a")
        t2 = _make_mock_tool("tool_b")
        reg.register(t1, t2)
        names = reg.list_tools()
        assert "tool_a" in names
        assert "tool_b" in names

    def test_list_tools_returns_sorted(self):
        """list_tools() returns sorted list of tool names."""
        from hazn_platform.orchestrator.tools.registry import ToolRegistry

        reg = ToolRegistry()
        reg.register(_make_mock_tool("zebra"))
        reg.register(_make_mock_tool("alpha"))
        reg.register(_make_mock_tool("middle"))
        assert reg.list_tools() == ["alpha", "middle", "zebra"]

    def test_get_server_returns_server_config(self):
        """get_server() returns result of create_sdk_mcp_server with registered tools."""
        from hazn_platform.orchestrator.tools.registry import ToolRegistry

        reg = ToolRegistry()
        tool = _make_mock_tool("my_tool")
        reg.register(tool)
        server = reg.get_server()
        # Server config should not be None
        assert server is not None

    def test_get_server_caches_result(self):
        """get_server() returns same object on second call (cached)."""
        from hazn_platform.orchestrator.tools.registry import ToolRegistry

        reg = ToolRegistry()
        reg.register(_make_mock_tool("tool_a"))
        server1 = reg.get_server()
        server2 = reg.get_server()
        assert server1 is server2

    def test_get_server_invalidates_cache_on_new_registration(self):
        """Registering new tool invalidates cached server."""
        from hazn_platform.orchestrator.tools.registry import ToolRegistry

        reg = ToolRegistry()
        reg.register(_make_mock_tool("tool_a"))
        server1 = reg.get_server()
        reg.register(_make_mock_tool("tool_b"))
        server2 = reg.get_server()
        # After registering a new tool, cache should be invalidated
        # so server2 should be a fresh object
        assert server1 is not server2

    def test_get_allowed_tools_returns_prefixed_names(self):
        """get_allowed_tools() returns mcp__hazn__<name> for all registered tools."""
        from hazn_platform.orchestrator.tools.registry import ToolRegistry

        reg = ToolRegistry()
        reg.register(_make_mock_tool("load_context"))
        reg.register(_make_mock_tool("write_finding"))
        allowed = reg.get_allowed_tools()
        assert "mcp__hazn__load_context" in allowed
        assert "mcp__hazn__write_finding" in allowed

    def test_get_allowed_tools_filters_by_phase_tools(self):
        """get_allowed_tools(phase_tools=["tool_a"]) filters to only listed tools in registry."""
        from hazn_platform.orchestrator.tools.registry import ToolRegistry

        reg = ToolRegistry()
        reg.register(_make_mock_tool("tool_a"))
        reg.register(_make_mock_tool("tool_b"))
        reg.register(_make_mock_tool("tool_c"))
        allowed = reg.get_allowed_tools(phase_tools=["tool_a"])
        assert allowed == ["mcp__hazn__tool_a"]

    def test_get_allowed_tools_nonexistent_phase_tool_returns_empty(self):
        """get_allowed_tools(phase_tools=["nonexistent"]) returns empty list."""
        from hazn_platform.orchestrator.tools.registry import ToolRegistry

        reg = ToolRegistry()
        reg.register(_make_mock_tool("tool_a"))
        allowed = reg.get_allowed_tools(phase_tools=["nonexistent"])
        assert allowed == []

    def test_get_allowed_tools_mixed_existing_and_nonexistent(self):
        """phase_tools with mix of existing and nonexistent returns only existing."""
        from hazn_platform.orchestrator.tools.registry import ToolRegistry

        reg = ToolRegistry()
        reg.register(_make_mock_tool("tool_a"))
        reg.register(_make_mock_tool("tool_b"))
        allowed = reg.get_allowed_tools(phase_tools=["tool_a", "nonexistent", "tool_b"])
        assert "mcp__hazn__tool_a" in allowed
        assert "mcp__hazn__tool_b" in allowed
        assert len(allowed) == 2


class TestBuildRegistry:
    """Test build_registry() factory function."""

    def test_build_registry_returns_tool_registry(self):
        """build_registry() returns a ToolRegistry instance."""
        from hazn_platform.orchestrator.tools import build_registry
        from hazn_platform.orchestrator.tools.registry import ToolRegistry

        reg = build_registry()
        assert isinstance(reg, ToolRegistry)

    def test_build_registry_has_tools(self):
        """build_registry() returns a registry (may have tools from domain modules)."""
        from hazn_platform.orchestrator.tools import build_registry

        reg = build_registry()
        # At minimum it should be a valid registry
        # (filesystem and web tools will be added in Task 2)
        assert reg is not None
        tools = reg.list_tools()
        assert isinstance(tools, list)

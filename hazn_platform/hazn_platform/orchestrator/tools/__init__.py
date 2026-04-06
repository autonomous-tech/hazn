"""orchestrator.tools -- Claude Agent SDK tool registry and tool modules.

This package replaces the legacy ToolRouter + tool_wiring infrastructure
with a ToolRegistry that bundles Python async functions (decorated with
``@tool``) into an ``McpSdkServerConfig`` via ``create_sdk_mcp_server()``.

Public API
----------
* ``ToolRegistry`` -- Central tool registry class.
* ``build_registry()`` -- Factory that creates a fully-populated ToolRegistry.
"""

from __future__ import annotations

from hazn_platform.orchestrator.tools.registry import ToolRegistry

__all__ = ["ToolRegistry", "build_registry"]


def build_registry() -> ToolRegistry:
    """Create a ToolRegistry populated with all domain tool modules.

    Currently registers:
    - filesystem tools (read_file, write_file, mkdir)
    - web tools (fetch_page)
    - memory tools (load_context, write_finding, search_memory, etc.)
    - github tools (create_repo, create_pr, get_pr_status, etc.)
    - vercel tools (deploy_project, get_deployment_status, etc.)
    - analytics tools (pull_ga4_data, query_gsc, check_pagespeed)
    """
    registry = ToolRegistry()

    # Import and register tools from domain modules.
    # Each module exposes a list of SdkMcpTool instances via module-level
    # variables or a get_tools() helper.
    try:
        from hazn_platform.orchestrator.tools.filesystem import TOOLS as fs_tools

        registry.register(*fs_tools)
    except ImportError:
        pass

    try:
        from hazn_platform.orchestrator.tools.web import TOOLS as web_tools

        registry.register(*web_tools)
    except ImportError:
        pass

    try:
        from hazn_platform.orchestrator.tools.memory import MEMORY_TOOLS

        registry.register(*MEMORY_TOOLS)
    except ImportError:
        pass

    try:
        from hazn_platform.orchestrator.tools.github import GITHUB_TOOLS

        registry.register(*GITHUB_TOOLS)
    except ImportError:
        pass

    try:
        from hazn_platform.orchestrator.tools.vercel import VERCEL_TOOLS

        registry.register(*VERCEL_TOOLS)
    except ImportError:
        pass

    try:
        from hazn_platform.orchestrator.tools.analytics import ANALYTICS_TOOLS

        registry.register(*ANALYTICS_TOOLS)
    except ImportError:
        pass

    return registry

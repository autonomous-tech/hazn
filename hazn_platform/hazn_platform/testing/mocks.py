"""Mock builders for LLM responses and MCP tool dispatch.

Provides reusable mocks that match the Anthropic API wire format.
No external dependencies -- works with plain dicts.

Usage::

    from hazn_platform.testing import MockLLMResponse, MockToolDispatcher

    # Build a mock assistant message with a tool_use block
    msg = (
        MockLLMResponse()
        .with_text("I'll look that up.")
        .with_tool_use("toolu_abc123", "load_context", {"agent_id": "test"})
        .build()
    )

    # Register canned tool results for testing
    dispatcher = MockToolDispatcher()
    dispatcher.register("load_context", {"status": "ok", "context": "loaded"})
    result = dispatcher.dispatch(tool_use_block)
"""

from __future__ import annotations

import json
from typing import Any


class MockLLMResponse:
    """Builds mock Anthropic API assistant messages.

    Supports chaining to build multi-block content arrays matching
    the exact wire format the Anthropic API returns.
    """

    def __init__(self) -> None:
        self._content_blocks: list[dict[str, Any]] = []

    def with_text(self, text: str) -> MockLLMResponse:
        """Add a text content block."""
        self._content_blocks.append({"type": "text", "text": text})
        return self

    def with_tool_use(
        self,
        tool_use_id: str,
        name: str,
        input_dict: dict[str, Any],
    ) -> MockLLMResponse:
        """Add a tool_use content block."""
        self._content_blocks.append({
            "type": "tool_use",
            "id": tool_use_id,
            "name": name,
            "input": input_dict,
        })
        return self

    def build(self) -> dict[str, Any]:
        """Return the complete assistant message dict.

        Format::

            {"role": "assistant", "content": [{"type": "text", ...}, ...]}
        """
        return {
            "role": "assistant",
            "content": list(self._content_blocks),
        }


class MockToolDispatcher:
    """Wraps a dict of tool_name -> canned_result for testing.

    Dispatches tool_use blocks and returns Anthropic-native
    tool_result format dicts.
    """

    def __init__(self) -> None:
        self._tools: dict[str, Any] = {}

    def register(self, name: str, result: Any) -> None:
        """Register a canned result for a tool name."""
        self._tools[name] = result

    def dispatch(self, tool_use_block: dict[str, Any]) -> dict[str, Any]:
        """Dispatch a tool_use block and return a tool_result block.

        Input format::

            {"type": "tool_use", "id": "toolu_...", "name": "...", "input": {...}}

        Output format::

            {"type": "tool_result", "tool_use_id": "toolu_...", "content": "..."}
        """
        tool_use_id = tool_use_block["id"]
        tool_name = tool_use_block["name"]

        if tool_name not in self._tools:
            return {
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": f"Unknown tool: {tool_name}",
                "is_error": True,
            }

        result = self._tools[tool_name]
        content = json.dumps(result) if isinstance(result, (dict, list)) else str(result)
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": content,
        }

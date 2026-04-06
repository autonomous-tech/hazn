"""Tests for the testing infrastructure (mock module and fixtures).

Validates that MockLLMResponse, MockToolDispatcher, and fixture loaders
work correctly for Phase 9+ test reuse.
"""

from __future__ import annotations


class TestLoadFixtureJson:
    """Fixture JSON loader tests."""

    def test_tool_use_responses_returns_list_of_dicts(self):
        from hazn_platform.testing.fixtures import load_fixture_json

        data = load_fixture_json("tool_use_responses.json")
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_tool_use_responses_have_required_keys(self):
        from hazn_platform.testing.fixtures import load_fixture_json

        data = load_fixture_json("tool_use_responses.json")
        for item in data:
            assert item["type"] == "tool_use"
            assert "id" in item
            assert "name" in item
            assert "input" in item

    def test_agent_sdk_tool_calls_returns_list_of_dicts(self):
        from hazn_platform.testing.fixtures import load_fixture_json

        data = load_fixture_json("agent_sdk_tool_calls.json")
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_agent_sdk_tool_calls_have_required_keys(self):
        from hazn_platform.testing.fixtures import load_fixture_json

        data = load_fixture_json("agent_sdk_tool_calls.json")
        for item in data:
            assert "tool_name" in item
            assert "tool_input" in item


class TestLoadFixtureText:
    """Fixture text loader tests."""

    def test_seo_audit_report_contains_findings(self):
        from hazn_platform.testing.fixtures import load_fixture_text

        text = load_fixture_text("agent_outputs/seo_audit_report.md")
        assert isinstance(text, str)
        assert len(text) > 0
        assert "## Findings" in text

    def test_seo_audit_report_contains_recommendations(self):
        from hazn_platform.testing.fixtures import load_fixture_text

        text = load_fixture_text("agent_outputs/seo_audit_report.md")
        assert "## Recommendations" in text

    def test_analytics_findings_contains_findings(self):
        from hazn_platform.testing.fixtures import load_fixture_text

        text = load_fixture_text("agent_outputs/analytics_findings.md")
        assert "## Findings" in text

    def test_code_generation_is_nonempty(self):
        from hazn_platform.testing.fixtures import load_fixture_text

        text = load_fixture_text("agent_outputs/code_generation.md")
        assert len(text) > 0


class TestMockLLMResponse:
    """MockLLMResponse builder tests."""

    def test_with_tool_use_builds_assistant_message(self):
        from hazn_platform.testing.mocks import MockLLMResponse

        msg = (
            MockLLMResponse()
            .with_tool_use("toolu_abc123", "load_context", {"agent_id": "test"})
            .build()
        )
        assert msg["role"] == "assistant"
        assert isinstance(msg["content"], list)
        assert msg["content"][0]["type"] == "tool_use"
        assert msg["content"][0]["name"] == "load_context"

    def test_with_text_builds_text_block(self):
        from hazn_platform.testing.mocks import MockLLMResponse

        msg = MockLLMResponse().with_text("Hello world").build()
        assert msg["role"] == "assistant"
        assert msg["content"][0]["type"] == "text"
        assert msg["content"][0]["text"] == "Hello world"

    def test_multiple_content_blocks(self):
        from hazn_platform.testing.mocks import MockLLMResponse

        msg = (
            MockLLMResponse()
            .with_text("Let me check that.")
            .with_tool_use("toolu_xyz", "search", {"query": "test"})
            .build()
        )
        assert len(msg["content"]) == 2
        assert msg["content"][0]["type"] == "text"
        assert msg["content"][1]["type"] == "tool_use"


class TestMockToolDispatcher:
    """MockToolDispatcher tests."""

    def test_register_and_dispatch(self):
        from hazn_platform.testing.mocks import MockToolDispatcher

        dispatcher = MockToolDispatcher()
        dispatcher.register("load_context", {"status": "ok"})
        result = dispatcher.dispatch(
            {"type": "tool_use", "id": "toolu_abc", "name": "load_context", "input": {}}
        )
        assert result["type"] == "tool_result"
        assert result["tool_use_id"] == "toolu_abc"

    def test_dispatch_unknown_tool(self):
        from hazn_platform.testing.mocks import MockToolDispatcher

        dispatcher = MockToolDispatcher()
        result = dispatcher.dispatch(
            {"type": "tool_use", "id": "toolu_abc", "name": "nonexistent", "input": {}}
        )
        assert result["type"] == "tool_result"
        assert result.get("is_error") is True


class TestReexports:
    """Verify __init__.py re-exports."""

    def test_imports_from_testing_package(self):
        from hazn_platform.testing import (
            MockLLMResponse,
            MockToolDispatcher,
            load_fixture_json,
            load_fixture_text,
        )

        assert MockLLMResponse is not None
        assert MockToolDispatcher is not None
        assert load_fixture_json is not None
        assert load_fixture_text is not None

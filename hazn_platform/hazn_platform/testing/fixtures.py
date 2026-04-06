"""Fixture loaders for test data files.

Loads JSON and text fixtures from hazn_platform/tests/fixtures/.

Usage::

    from hazn_platform.testing.fixtures import load_fixture_json, load_fixture_text

    tool_calls = load_fixture_json("tool_use_responses.json")
    report = load_fixture_text("agent_outputs/seo_audit_report.md")
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Points to hazn_platform/tests/fixtures/
FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures"


def load_fixture_json(relative_path: str) -> Any:
    """Load and parse a JSON fixture file.

    Args:
        relative_path: Path relative to tests/fixtures/, e.g. "tool_use_responses.json"

    Returns:
        Parsed JSON data (typically a list or dict).

    Raises:
        FileNotFoundError: If the fixture file does not exist.
    """
    filepath = FIXTURES_DIR / relative_path
    if not filepath.exists():
        msg = f"Fixture not found: {filepath}"
        raise FileNotFoundError(msg)
    return json.loads(filepath.read_text())


def load_fixture_text(relative_path: str) -> str:
    """Load a fixture file as text.

    Args:
        relative_path: Path relative to tests/fixtures/, e.g. "agent_outputs/seo_audit_report.md"

    Returns:
        File contents as a string.

    Raises:
        FileNotFoundError: If the fixture file does not exist.
    """
    filepath = FIXTURES_DIR / relative_path
    if not filepath.exists():
        msg = f"Fixture not found: {filepath}"
        raise FileNotFoundError(msg)
    return filepath.read_text()

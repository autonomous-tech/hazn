"""Tests for filesystem tools -- read_file, write_file, mkdir.

Uses tmp_path fixture for isolated filesystem operations.
All tools are tested as standalone async functions.
"""

from __future__ import annotations

import os

import pytest


@pytest.fixture
def _make_file(tmp_path):
    """Helper to create a file in tmp_path."""

    def _inner(name: str, content: str = "hello world") -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)

    return _inner


# ---------------------------------------------------------------------------
# read_file tests
# ---------------------------------------------------------------------------


class TestReadFile:
    """read_file returns file content as text."""

    @pytest.mark.asyncio
    async def test_reads_existing_file(self, tmp_path, _make_file):
        """read_file returns content of an existing file."""
        from hazn_platform.orchestrator.tools.filesystem import read_file

        path = _make_file("sample.txt", "test content here")
        result = await read_file.handler({"path": path})
        assert result["content"][0]["type"] == "text"
        assert "test content here" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_error_for_nonexistent_file(self, tmp_path):
        """read_file returns error for nonexistent file."""
        from hazn_platform.orchestrator.tools.filesystem import read_file

        result = await read_file.handler({"path": str(tmp_path / "does_not_exist.txt")})
        assert result.get("isError") is True

    @pytest.mark.asyncio
    async def test_reads_utf8_content(self, tmp_path, _make_file):
        """read_file handles UTF-8 content correctly."""
        from hazn_platform.orchestrator.tools.filesystem import read_file

        path = _make_file("utf8.txt", "Hallo Welt, Gruesse!")
        result = await read_file.handler({"path": path})
        assert "Hallo Welt" in result["content"][0]["text"]


# ---------------------------------------------------------------------------
# write_file tests
# ---------------------------------------------------------------------------


class TestWriteFile:
    """write_file creates file with given content."""

    @pytest.mark.asyncio
    async def test_writes_file_content(self, tmp_path):
        """write_file creates file with given content and returns success."""
        from hazn_platform.orchestrator.tools.filesystem import write_file

        path = str(tmp_path / "output.txt")
        result = await write_file.handler({"path": path, "content": "written data"})
        assert result.get("isError") is not True
        assert os.path.exists(path)
        with open(path) as f:
            assert f.read() == "written data"

    @pytest.mark.asyncio
    async def test_creates_parent_directories(self, tmp_path):
        """write_file creates parent directories if they don't exist."""
        from hazn_platform.orchestrator.tools.filesystem import write_file

        path = str(tmp_path / "nested" / "deep" / "file.txt")
        result = await write_file.handler({"path": path, "content": "nested content"})
        assert result.get("isError") is not True
        assert os.path.exists(path)
        with open(path) as f:
            assert f.read() == "nested content"

    @pytest.mark.asyncio
    async def test_returns_success_message(self, tmp_path):
        """write_file returns a success message in content."""
        from hazn_platform.orchestrator.tools.filesystem import write_file

        path = str(tmp_path / "msg.txt")
        result = await write_file.handler({"path": path, "content": "data"})
        assert result["content"][0]["type"] == "text"
        # Success message should mention the path or success
        text = result["content"][0]["text"]
        assert "success" in text.lower() or path in text


# ---------------------------------------------------------------------------
# mkdir tests
# ---------------------------------------------------------------------------


class TestMkdir:
    """mkdir creates directory recursively."""

    @pytest.mark.asyncio
    async def test_creates_directory(self, tmp_path):
        """mkdir creates directory and returns success."""
        from hazn_platform.orchestrator.tools.filesystem import mkdir

        path = str(tmp_path / "new_dir")
        result = await mkdir.handler({"path": path})
        assert result.get("isError") is not True
        assert os.path.isdir(path)

    @pytest.mark.asyncio
    async def test_creates_nested_directories(self, tmp_path):
        """mkdir creates nested directories recursively."""
        from hazn_platform.orchestrator.tools.filesystem import mkdir

        path = str(tmp_path / "a" / "b" / "c")
        result = await mkdir.handler({"path": path})
        assert result.get("isError") is not True
        assert os.path.isdir(path)

    @pytest.mark.asyncio
    async def test_idempotent_on_existing_directory(self, tmp_path):
        """mkdir on existing directory returns success (idempotent)."""
        from hazn_platform.orchestrator.tools.filesystem import mkdir

        path = str(tmp_path / "existing_dir")
        os.makedirs(path)
        result = await mkdir.handler({"path": path})
        assert result.get("isError") is not True
        assert os.path.isdir(path)

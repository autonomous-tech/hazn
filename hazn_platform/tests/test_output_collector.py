"""Tests for OutputCollector -- convention-based agent output parser.

Tests cover all four artifact types (Report, Findings, Code, Metadata),
edge cases (empty input, malformed sections), and realistic agent output
from fixture files.
"""

from __future__ import annotations

import pytest

from hazn_platform.testing.fixtures import load_fixture_text


# ── Helpers ───────────────────────────────────────────────────────────


def _import_collector():
    from hazn_platform.orchestrator.output_collector import OutputCollector
    return OutputCollector


def _import_artifact_type():
    from hazn_platform.orchestrator.output_collector import ArtifactType
    return ArtifactType


def _import_collected_artifact():
    from hazn_platform.orchestrator.output_collector import CollectedArtifact
    return CollectedArtifact


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture()
def seo_fixture():
    return load_fixture_text("agent_outputs/seo_audit_report.md")


@pytest.fixture()
def analytics_fixture():
    return load_fixture_text("agent_outputs/analytics_findings.md")


@pytest.fixture()
def code_fixture():
    return load_fixture_text("agent_outputs/code_generation.md")


@pytest.fixture()
def collector():
    OutputCollector = _import_collector()
    return OutputCollector()


# ── TestReportArtifact ────────────────────────────────────────────────


class TestReportArtifact:
    """Report artifact is always produced and contains full markdown body."""

    def test_always_produces_report(self, collector):
        """collect("any text") always has at least one artifact with type REPORT."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect("any text")
        types = [a.artifact_type for a in artifacts]
        assert ArtifactType.REPORT in types

    def test_report_contains_full_body(self, collector):
        """Report artifact content == original input."""
        ArtifactType = _import_artifact_type()
        text = "# My Report\n\nSome paragraph content here."
        artifacts = collector.collect(text)
        report = [a for a in artifacts if a.artifact_type == ArtifactType.REPORT][0]
        assert report.content == text

    def test_empty_input_produces_report(self, collector):
        """collect("") still produces Report artifact (empty content)."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect("")
        report = [a for a in artifacts if a.artifact_type == ArtifactType.REPORT][0]
        assert report.content == ""

    def test_report_from_fixture(self, collector, seo_fixture):
        """collect(seo_fixture) produces Report with full fixture content."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect(seo_fixture)
        report = [a for a in artifacts if a.artifact_type == ArtifactType.REPORT][0]
        assert report.content == seo_fixture
        assert "SEO Audit Report" in report.content


# ── TestFindingsExtraction ────────────────────────────────────────────


class TestFindingsExtraction:
    """Findings are extracted from ## Findings sections into structured data."""

    def test_structured_findings_extracted(self, collector, seo_fixture):
        """collect(seo_fixture) produces Findings artifact with structured_data["findings"] as list."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect(seo_fixture)
        findings_artifacts = [a for a in artifacts if a.artifact_type == ArtifactType.FINDINGS]
        assert len(findings_artifacts) == 1
        findings = findings_artifacts[0].structured_data["findings"]
        assert isinstance(findings, list)
        assert len(findings) > 0

    def test_finding_has_required_fields(self, collector, seo_fixture):
        """Each finding dict has severity, description, evidence, recommendation keys."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect(seo_fixture)
        findings_artifact = [a for a in artifacts if a.artifact_type == ArtifactType.FINDINGS][0]
        for finding in findings_artifact.structured_data["findings"]:
            assert "severity" in finding, f"Missing 'severity' in finding: {finding}"
            assert "description" in finding, f"Missing 'description' in finding: {finding}"
            assert "evidence" in finding, f"Missing 'evidence' in finding: {finding}"
            assert "recommendation" in finding, f"Missing 'recommendation' in finding: {finding}"

    def test_multiple_findings(self, collector, seo_fixture):
        """SEO fixture has 3+ findings."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect(seo_fixture)
        findings_artifact = [a for a in artifacts if a.artifact_type == ArtifactType.FINDINGS][0]
        assert len(findings_artifact.structured_data["findings"]) >= 3

    def test_no_findings_section(self, collector):
        """collect("# Just a report\\n\\nSome text") does NOT produce Findings artifact."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect("# Just a report\n\nSome text")
        findings_artifacts = [a for a in artifacts if a.artifact_type == ArtifactType.FINDINGS]
        assert len(findings_artifacts) == 0

    def test_analytics_findings(self, collector, analytics_fixture):
        """collect(analytics_fixture) extracts findings too."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect(analytics_fixture)
        findings_artifacts = [a for a in artifacts if a.artifact_type == ArtifactType.FINDINGS]
        assert len(findings_artifacts) == 1
        findings = findings_artifacts[0].structured_data["findings"]
        assert len(findings) >= 2

    def test_finding_severity_values(self, collector, seo_fixture):
        """Extracted severities are realistic strings (e.g., High, Medium, Low, Critical)."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect(seo_fixture)
        findings_artifact = [a for a in artifacts if a.artifact_type == ArtifactType.FINDINGS][0]
        valid_severities = {"High", "Medium", "Low", "Critical", "Info"}
        for finding in findings_artifact.structured_data["findings"]:
            assert finding["severity"] in valid_severities, (
                f"Unexpected severity: {finding['severity']}"
            )


# ── TestCodeArtifacts ─────────────────────────────────────────────────


class TestCodeArtifacts:
    """Code artifacts are extracted from ```artifact tagged code blocks."""

    def test_code_artifact_extracted(self, collector, code_fixture):
        """collect(code_fixture) produces at least one Code artifact."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect(code_fixture)
        code_artifacts = [a for a in artifacts if a.artifact_type == ArtifactType.CODE]
        assert len(code_artifacts) >= 1

    def test_code_has_language_and_path(self, collector, code_fixture):
        """Code artifact metadata has language and filepath keys."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect(code_fixture)
        code_artifacts = [a for a in artifacts if a.artifact_type == ArtifactType.CODE]
        for code_art in code_artifacts:
            assert "language" in code_art.metadata, f"Missing 'language' in metadata: {code_art.metadata}"
            assert "filepath" in code_art.metadata, f"Missing 'filepath' in metadata: {code_art.metadata}"

    def test_code_content_is_body(self, collector, code_fixture):
        """Code artifact content is the code text (not the fence markers)."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect(code_fixture)
        code_artifacts = [a for a in artifacts if a.artifact_type == ArtifactType.CODE]
        for code_art in code_artifacts:
            # Should not contain the fence markers
            assert "```artifact" not in code_art.content
            assert "```" not in code_art.content
            # Should have actual code content
            assert len(code_art.content.strip()) > 0

    def test_regular_code_block_ignored(self, collector, code_fixture):
        """Regular ```javascript blocks without 'artifact' tag are NOT extracted as Code artifacts."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect(code_fixture)
        code_artifacts = [a for a in artifacts if a.artifact_type == ArtifactType.CODE]
        # The code_generation fixture has 2 artifact blocks and 1 regular code block.
        # Only artifact blocks should be extracted.
        assert len(code_artifacts) == 2

    def test_multiple_code_artifacts(self, collector, code_fixture):
        """code_fixture has 2 artifact code blocks -> 2 Code artifacts."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect(code_fixture)
        code_artifacts = [a for a in artifacts if a.artifact_type == ArtifactType.CODE]
        assert len(code_artifacts) == 2


# ── TestMetadataExtraction ────────────────────────────────────────────


class TestMetadataExtraction:
    """Metadata artifact is always produced with word count, section count, and sections."""

    def test_always_produces_metadata(self, collector):
        """collect("any") produces Metadata artifact."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect("any")
        metadata_artifacts = [a for a in artifacts if a.artifact_type == ArtifactType.METADATA]
        assert len(metadata_artifacts) == 1

    def test_word_count(self, collector, seo_fixture):
        """Metadata structured_data["word_count"] is an int > 0 for non-empty input."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect(seo_fixture)
        metadata = [a for a in artifacts if a.artifact_type == ArtifactType.METADATA][0]
        assert isinstance(metadata.structured_data["word_count"], int)
        assert metadata.structured_data["word_count"] > 0

    def test_section_count(self, collector, seo_fixture):
        """Metadata structured_data["section_count"] matches number of ## headings."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect(seo_fixture)
        metadata = [a for a in artifacts if a.artifact_type == ArtifactType.METADATA][0]
        # SEO fixture has: ## Score Summary, ## Findings, ## Recommendations, ## Metadata
        # Plus subsections: ### Finding 1, etc. -- but section_count only counts ## headings
        expected_sections = seo_fixture.count("\n## ")
        if seo_fixture.startswith("## "):
            expected_sections += 1
        assert metadata.structured_data["section_count"] == expected_sections

    def test_sections_list(self, collector, seo_fixture):
        """Metadata structured_data["sections"] is list of heading text strings."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect(seo_fixture)
        metadata = [a for a in artifacts if a.artifact_type == ArtifactType.METADATA][0]
        sections = metadata.structured_data["sections"]
        assert isinstance(sections, list)
        assert "Score Summary" in sections
        assert "Findings" in sections
        assert "Recommendations" in sections

    def test_empty_input_metadata(self, collector):
        """collect("") produces metadata with word_count=0."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect("")
        metadata = [a for a in artifacts if a.artifact_type == ArtifactType.METADATA][0]
        assert metadata.structured_data["word_count"] == 0


# ── TestEdgeCases ─────────────────────────────────────────────────────


class TestEdgeCases:
    """Edge cases: malformed input, None input, type safety."""

    def test_tolerant_of_malformed_findings(self, collector):
        """Findings section with inconsistent formatting still extracts what it can."""
        ArtifactType = _import_artifact_type()
        text = """# Report

## Findings

- **Severity**: High
- **Description**: Something is wrong
- Missing evidence field
- **Recommendation**: Fix it

Some random text that is not a finding.
"""
        artifacts = collector.collect(text)
        # Should not crash -- either extracts partial findings or produces no Findings artifact
        types = [a.artifact_type for a in artifacts]
        assert ArtifactType.REPORT in types
        assert ArtifactType.METADATA in types

    def test_no_crash_on_none(self, collector):
        """If somehow called with weird input, convert to string, don't crash."""
        artifacts = collector.collect(None)  # type: ignore[arg-type]
        assert isinstance(artifacts, list)
        assert len(artifacts) >= 1  # At least Report + Metadata

    def test_artifact_types_are_strings(self, collector, seo_fixture):
        """All returned artifacts have artifact_type that is a valid ArtifactType enum value."""
        ArtifactType = _import_artifact_type()
        artifacts = collector.collect(seo_fixture)
        valid_types = set(ArtifactType)
        for artifact in artifacts:
            assert artifact.artifact_type in valid_types


# ── TestPhase8Integration ─────────────────────────────────────────────

from pathlib import Path

from hazn_platform.orchestrator.tools.registry import ToolRegistry

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_HOST_AGENTS_DIR = _PROJECT_ROOT / "hazn" / "agents"
_HOST_SKILLS_DIR = _PROJECT_ROOT / "hazn" / "skills"

HAS_REAL_CONTENT = (
    _HOST_AGENTS_DIR.is_dir()
    and any(_HOST_AGENTS_DIR.glob("*.md"))
    and _HOST_SKILLS_DIR.is_dir()
    and any(_HOST_SKILLS_DIR.glob("*/SKILL.md"))
)


@pytest.mark.skipif(not HAS_REAL_CONTENT, reason="Real agent/skill content not available")
class TestPhase8Integration:
    """Verify all three foundation components work together with mock data.

    Uses ToolRegistry (the new tool system) instead of the deleted ToolRouter.
    """

    def test_prompt_to_output_pipeline(self, seo_fixture):
        """Smoke test: PromptAssembler + OutputCollector work together."""
        from types import SimpleNamespace

        from hazn_platform.orchestrator.prompt_assembler import assemble_prompt
        from hazn_platform.orchestrator.output_collector import OutputCollector, ArtifactType

        # Step 1: PromptAssembler produces a non-empty system prompt
        prompt = assemble_prompt(
            "strategist", [],
            agents_dir=_HOST_AGENTS_DIR, skills_dir=_HOST_SKILLS_DIR,
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 0

        # Step 2: ToolRegistry registers a mock tool and verifies listing
        registry = ToolRegistry()
        mock_tool = SimpleNamespace(name="mock_tool")
        registry.register(mock_tool)
        assert "mock_tool" in registry.list_tools()
        allowed = registry.get_allowed_tools(phase_tools=["mock_tool"])
        assert allowed == ["mcp__hazn__mock_tool"]

        # Step 3: OutputCollector parses the SEO fixture into artifacts
        collector = OutputCollector()
        artifacts = collector.collect(seo_fixture)
        assert len(artifacts) >= 3  # Report + Findings + Metadata (at minimum)

        types = {a.artifact_type for a in artifacts}
        assert ArtifactType.REPORT in types
        assert ArtifactType.FINDINGS in types
        assert ArtifactType.METADATA in types

    def test_no_django_required(self, seo_fixture):
        """All three modules are importable and functional without Django ORM operations.

        The pytest config sets DJANGO_SETTINGS_MODULE, but this test verifies that
        no Django model instances are created during the operations -- all outputs
        are pure Pydantic/Python types.
        """
        from hazn_platform.orchestrator.prompt_assembler import assemble_prompt
        from hazn_platform.orchestrator.output_collector import (
            OutputCollector,
            CollectedArtifact,
        )

        # PromptAssembler returns a plain string
        prompt = assemble_prompt(
            "strategist", [],
            agents_dir=_HOST_AGENTS_DIR, skills_dir=_HOST_SKILLS_DIR,
        )
        assert isinstance(prompt, str)

        # OutputCollector returns Pydantic models, not Django models
        collector = OutputCollector()
        artifacts = collector.collect(seo_fixture)
        for artifact in artifacts:
            assert isinstance(artifact, CollectedArtifact)
            # CollectedArtifact is a Pydantic BaseModel, not a Django Model
            assert not hasattr(artifact, "_meta")  # Django models have _meta
            assert not hasattr(artifact, "pk")  # Django models have pk

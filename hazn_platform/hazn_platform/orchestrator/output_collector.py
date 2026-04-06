"""OutputCollector -- convention-based agent output parser (RUNT-08).

Parses agent markdown output into typed artifacts ready for the
deliverable pipeline. Recognizes four artifact types:

- **Report**: full markdown body (always produced)
- **Findings**: structured list extracted from ``## Findings`` section
- **Code**: code blocks tagged with ``artifact`` fence marker
- **Metadata**: summary stats (word count, section count, headings)

This module is intentionally self-contained: it does NOT import Django
models. OutputCollector produces ``list[CollectedArtifact]`` (pure
Pydantic). The caller (executor.py in Phase 9) handles persistence
to ``WorkflowPhaseOutput``.

Usage::

    from hazn_platform.orchestrator.output_collector import OutputCollector

    collector = OutputCollector()
    artifacts = collector.collect(agent_markdown_output)
"""

from __future__ import annotations

import enum
import logging
import re

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ── Enums and Models ──────────────────────────────────────────────────


class ArtifactType(str, enum.Enum):
    """Recognized artifact types from agent output."""

    REPORT = "report"
    FINDINGS = "findings"
    CODE = "code"
    METADATA = "metadata"


class CollectedArtifact(BaseModel):
    """A single artifact extracted from agent output.

    Attributes:
        artifact_type: One of the ArtifactType enum values.
        content: The artifact body (full markdown for Report, code for Code, etc.).
        structured_data: Structured data extracted from the artifact (findings list, metadata stats).
        metadata: Additional key-value metadata (language/filepath for code artifacts).
    """

    artifact_type: ArtifactType
    content: str = ""
    structured_data: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)


# ── OutputCollector ───────────────────────────────────────────────────


class OutputCollector:
    """Convention-based markdown parser that extracts structured artifacts from agent output.

    Agents follow markdown conventions defined in their skill instructions:

    - ``## Findings`` section with structured bullet items
    - ````` ```artifact {language} {filepath}`` ```` fence markers for code blocks
    - ``## `` headings for section structure

    The collector is tolerant of format deviations -- it never raises on
    unexpected input, always produces at least Report + Metadata artifacts,
    and logs warnings when expected patterns are found but not parseable.
    """

    # Regex for structured finding items.
    # Matches bullet items with **Severity/Priority**: value, **Description/Issue**: value,
    # **Evidence**: value, **Recommendation**: value.
    # Tolerant of both * and - bullet markers, and both label variants.
    _FINDING_PATTERN = re.compile(
        r"[-*]\s+\*\*(?:Severity|Priority)\*\*\s*:\s*(.+?)$"
        r".*?"
        r"[-*]\s+\*\*(?:Description|Issue)\*\*\s*:\s*(.+?)$"
        r".*?"
        r"[-*]\s+\*\*Evidence\*\*\s*:\s*(.+?)$"
        r".*?"
        r"[-*]\s+\*\*Recommendation\*\*\s*:\s*(.+?)$",
        re.MULTILINE | re.DOTALL,
    )

    # Regex for individual finding blocks -- finds each complete finding group.
    # We split the findings section by ### headings and parse each block.
    _FINDING_BLOCK_PATTERN = re.compile(
        r"[-*]\s+\*\*(?:Severity|Priority)\*\*\s*:\s*(.+)\n"
        r"[-*]\s+\*\*(?:Description|Issue)\*\*\s*:\s*((?:.+\n?)+?)"
        r"[-*]\s+\*\*Evidence\*\*\s*:\s*((?:.+\n?)+?)"
        r"[-*]\s+\*\*Recommendation\*\*\s*:\s*((?:.+\n?)+?)$",
        re.MULTILINE,
    )

    # Regex for ```artifact {language} {filepath}\n{code}\n```
    _CODE_ARTIFACT_PATTERN = re.compile(
        r"```artifact\s+(\S+)\s+(\S+)\n(.*?)```",
        re.DOTALL,
    )

    # Regex for ## headings (not ### or deeper)
    _SECTION_PATTERN = re.compile(r"^## (.+)$", re.MULTILINE)

    def collect(self, agent_output: str) -> list[CollectedArtifact]:
        """Parse agent markdown output into typed artifacts.

        Always produces at least Report + Metadata. Optionally produces
        Findings and/or Code artifacts if the corresponding patterns are
        found in the input.

        Parameters
        ----------
        agent_output:
            Raw markdown output from an agent. Tolerant of None (converted
            to empty string).

        Returns
        -------
        list[CollectedArtifact]
            Ordered list: Report first, then Findings (if any), Code (if
            any), Metadata last.
        """
        # Tolerate None or non-string input
        if agent_output is None:
            agent_output = ""
        elif not isinstance(agent_output, str):
            agent_output = str(agent_output)

        artifacts: list[CollectedArtifact] = []

        # 1. Always produce Report artifact
        metadata_dict = self._extract_metadata(agent_output)
        artifacts.append(
            CollectedArtifact(
                artifact_type=ArtifactType.REPORT,
                content=agent_output,
                metadata=metadata_dict,
            )
        )

        # 2. Try to extract findings
        findings = self._extract_findings(agent_output)
        if findings:
            artifacts.append(
                CollectedArtifact(
                    artifact_type=ArtifactType.FINDINGS,
                    structured_data={"findings": findings},
                )
            )

        # 3. Extract code artifacts
        code_artifacts = self._extract_code_artifacts(agent_output)
        artifacts.extend(code_artifacts)

        # 4. Always produce Metadata artifact
        artifacts.append(
            CollectedArtifact(
                artifact_type=ArtifactType.METADATA,
                structured_data=metadata_dict,
            )
        )

        # Log summary
        types_found = [a.artifact_type.value for a in artifacts]
        logger.info(
            "OutputCollector: %d artifacts collected, types=%s",
            len(artifacts),
            types_found,
        )

        return artifacts

    def _extract_findings(self, text: str) -> list[dict]:
        """Extract structured findings from the ## Findings section.

        Looks for a ``## Findings`` heading and parses structured bullet
        items within that section. Returns empty list if no findings are
        parseable (never raises).
        """
        # Find the ## Findings section
        findings_section = self._get_section_content(text, "Findings")
        if findings_section is None:
            return []

        findings: list[dict] = []

        # Split by ### headings (each finding is typically under ### Finding N)
        finding_blocks = re.split(r"###\s+", findings_section)

        for block in finding_blocks:
            if not block.strip():
                continue

            finding = self._parse_single_finding(block)
            if finding is not None:
                findings.append(finding)

        if not findings:
            # Fallback: try matching the entire section as one block
            finding = self._parse_single_finding(findings_section)
            if finding is not None:
                findings.append(finding)

        if not findings and findings_section.strip():
            logger.warning(
                "OutputCollector: ## Findings section found but no findings parseable "
                "(format deviation)"
            )

        return findings

    def _parse_single_finding(self, block: str) -> dict | None:
        """Parse a single finding block into a structured dict.

        Returns None if the block doesn't contain parseable finding data.
        """
        severity = self._extract_field(block, r"\*\*(?:Severity|Priority)\*\*\s*:\s*(.+)")
        description = self._extract_field(block, r"\*\*(?:Description|Issue)\*\*\s*:\s*(.+)")
        evidence = self._extract_field(block, r"\*\*Evidence\*\*\s*:\s*(.+)")
        recommendation = self._extract_field(block, r"\*\*Recommendation\*\*\s*:\s*(.+)")

        # Must have at least severity and description to count as a finding
        if severity and description:
            return {
                "severity": severity.strip(),
                "description": description.strip(),
                "evidence": (evidence or "").strip(),
                "recommendation": (recommendation or "").strip(),
            }

        return None

    @staticmethod
    def _extract_field(text: str, pattern: str) -> str | None:
        """Extract the first match of a field pattern from text."""
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        return None

    def _extract_code_artifacts(self, text: str) -> list[CollectedArtifact]:
        """Extract code artifacts from ```artifact tagged code blocks.

        Only blocks with the ``artifact`` tag are extracted. Regular code
        blocks (e.g., ```javascript) are ignored.
        """
        artifacts: list[CollectedArtifact] = []

        for match in self._CODE_ARTIFACT_PATTERN.finditer(text):
            language = match.group(1).strip()
            filepath = match.group(2).strip()
            code_body = match.group(3).strip()

            artifacts.append(
                CollectedArtifact(
                    artifact_type=ArtifactType.CODE,
                    content=code_body,
                    metadata={"language": language, "filepath": filepath},
                )
            )

        return artifacts

    def _extract_metadata(self, text: str) -> dict:
        """Extract metadata stats from the markdown text.

        Returns dict with word_count, section_count, sections, char_count.
        """
        # Word count: split on whitespace
        words = text.split() if text else []
        word_count = len(words)

        # Section headings: ## level only (not ### or deeper)
        section_matches = self._SECTION_PATTERN.findall(text)
        sections = [s.strip() for s in section_matches]
        section_count = len(sections)

        return {
            "word_count": word_count,
            "section_count": section_count,
            "sections": sections,
            "char_count": len(text),
        }

    @staticmethod
    def _get_section_content(text: str, heading: str) -> str | None:
        """Extract content between a ## heading and the next ## heading (or end).

        Parameters
        ----------
        text:
            Full markdown text.
        heading:
            Heading text to find (e.g., "Findings").

        Returns
        -------
        str or None
            Section content (excluding the heading line itself), or None
            if the heading is not found.
        """
        pattern = re.compile(
            rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
            re.MULTILINE | re.DOTALL,
        )
        match = pattern.search(text)
        if match:
            return match.group(1)
        return None

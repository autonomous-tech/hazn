"""Tests for PromptAssembler (RUNT-01).

Tests use real agent persona files and real SKILL.md content from the
hazn/ directory, following the locked decision for "real content with
mock interfaces". Client context is tested with synthetic data.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ── Path constants ────────────────────────────────────────────────────

# Resolve relative to this test file, matching test_workflow_parser.py pattern.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_HOST_AGENTS_DIR = _PROJECT_ROOT / "hazn" / "agents"
_HOST_SKILLS_DIR = _PROJECT_ROOT / "hazn" / "skills"

# Guard for environments where the real content dirs may not exist.
HAS_REAL_CONTENT = (
    _HOST_AGENTS_DIR.is_dir()
    and any(_HOST_AGENTS_DIR.glob("*.md"))
    and _HOST_SKILLS_DIR.is_dir()
    and any(_HOST_SKILLS_DIR.glob("*/SKILL.md"))
)


# ── Helpers ───────────────────────────────────────────────────────────

def _import_assemble_prompt():
    from hazn_platform.orchestrator.prompt_assembler import assemble_prompt
    return assemble_prompt


def _import_read_skill_content():
    from hazn_platform.orchestrator.prompt_assembler import _read_skill_content
    return _read_skill_content


# ── TestAssemblePromptBasic ───────────────────────────────────────────


@pytest.mark.skipif(not HAS_REAL_CONTENT, reason="Real agent/skill content not available")
class TestAssemblePromptBasic:
    """Tests with real agent personas."""

    def test_persona_only(self):
        """assemble_prompt with no skills returns persona content."""
        assemble_prompt = _import_assemble_prompt()
        result = assemble_prompt(
            "strategist", [], agents_dir=_HOST_AGENTS_DIR, skills_dir=_HOST_SKILLS_DIR,
        )
        assert "Strategist" in result
        assert "positioning" in result.lower()

    def test_unknown_agent_raises(self):
        """assemble_prompt with nonexistent agent raises ValueError."""
        assemble_prompt = _import_assemble_prompt()
        with pytest.raises(ValueError, match="not found"):
            assemble_prompt(
                "nonexistent-agent-xyz", [],
                agents_dir=_HOST_AGENTS_DIR, skills_dir=_HOST_SKILLS_DIR,
            )

    def test_returns_string(self):
        """Result is a str, not None."""
        assemble_prompt = _import_assemble_prompt()
        result = assemble_prompt(
            "strategist", [], agents_dir=_HOST_AGENTS_DIR, skills_dir=_HOST_SKILLS_DIR,
        )
        assert isinstance(result, str)
        assert len(result) > 0


# ── TestSkillInjection ────────────────────────────────────────────────


@pytest.mark.skipif(not HAS_REAL_CONTENT, reason="Real agent/skill content not available")
class TestSkillInjection:
    """Tests for skill content injection."""

    def test_single_skill_included(self):
        """assemble_prompt with seo-audit skill contains SKILL.md content."""
        assemble_prompt = _import_assemble_prompt()
        result = assemble_prompt(
            "seo-specialist", ["seo-audit"],
            agents_dir=_HOST_AGENTS_DIR, skills_dir=_HOST_SKILLS_DIR,
        )
        # SKILL.md starts with "# Website SEO Audit"
        assert "Website SEO Audit" in result

    def test_skill_content_not_truncated(self):
        """Full SKILL.md is present -- check for content that appears later in the file."""
        assemble_prompt = _import_assemble_prompt()
        result = assemble_prompt(
            "seo-specialist", ["seo-audit"],
            agents_dir=_HOST_AGENTS_DIR, skills_dir=_HOST_SKILLS_DIR,
        )
        # "Scoring Rubric" appears in the latter half of seo-audit/SKILL.md
        assert "Scoring Rubric" in result

    def test_multiple_skills(self):
        """assemble_prompt with 2 skills contains content from both."""
        assemble_prompt = _import_assemble_prompt()
        result = assemble_prompt(
            "seo-specialist", ["seo-audit", "analytics-audit"],
            agents_dir=_HOST_AGENTS_DIR, skills_dir=_HOST_SKILLS_DIR,
        )
        assert "Website SEO Audit" in result
        assert "GA4" in result or "Site Inspection" in result

    def test_unknown_skill_raises(self):
        """Unknown skill name raises ValueError."""
        _read_skill_content = _import_read_skill_content()
        with pytest.raises(ValueError, match="not found"):
            _read_skill_content("nonexistent-skill-xyz", skills_dir=_HOST_SKILLS_DIR)

    def test_skill_section_header(self):
        """Output contains '# Skill: seo-audit' header."""
        assemble_prompt = _import_assemble_prompt()
        result = assemble_prompt(
            "seo-specialist", ["seo-audit"],
            agents_dir=_HOST_AGENTS_DIR, skills_dir=_HOST_SKILLS_DIR,
        )
        assert "# Skill: seo-audit" in result


# ── TestReferenceHandling ─────────────────────────────────────────────


class TestReferenceHandling:
    """Tests for reference doc injection using temp skill directories."""

    @pytest.fixture()
    def skill_with_refs(self, tmp_path):
        """Create a temp skill dir with SKILL.md + small and large reference files."""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: A test skill.\n---\n\n# Test Skill\n\nTest content."
        )
        refs_dir = skill_dir / "references"
        refs_dir.mkdir()
        # Small reference (under 15KB)
        (refs_dir / "small-ref.md").write_text("# Small Reference\n\nThis is a small reference doc.")
        # Large reference (over 15KB)
        (refs_dir / "large-ref.md").write_text("# Large Reference\n\n" + "x" * 16_000)
        return tmp_path

    def test_small_reference_inlined(self, skill_with_refs):
        """Reference under 15KB appears in output with 'Reference:' header."""
        _read_skill_content = _import_read_skill_content()
        result = _read_skill_content("test-skill", skills_dir=skill_with_refs)
        assert "## Reference: small-ref" in result
        assert "This is a small reference doc." in result

    def test_large_reference_noted(self, skill_with_refs):
        """Reference over 15KB gets a size note, not full content."""
        _read_skill_content = _import_read_skill_content()
        result = _read_skill_content("test-skill", skills_dir=skill_with_refs)
        assert "large-ref" in result
        assert "omitted" in result.lower() or "available" in result.lower()
        # Full content of the large file should NOT be present
        assert "x" * 16_000 not in result

    def test_no_references_dir(self, tmp_path):
        """Skill without references/ dir works fine."""
        skill_dir = tmp_path / "simple-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: simple-skill\ndescription: Simple.\n---\n\n# Simple Skill\n\nContent."
        )
        _read_skill_content = _import_read_skill_content()
        result = _read_skill_content("simple-skill", skills_dir=tmp_path)
        assert "# Simple Skill" in result


# ── TestClientContextInjection ────────────────────────────────────────


@pytest.mark.skipif(not HAS_REAL_CONTENT, reason="Real agent/skill content not available")
class TestClientContextInjection:
    """Tests for client context formatting and injection."""

    _SAMPLE_CONTEXT = {
        "agency": {
            "name": "Hazn Digital",
            "focus": "B2B marketing websites",
        },
        "client": {
            "name": "Acme Corp",
            "domain": "acme-corp.com",
            "industry": "SaaS",
        },
        "brand_voice": "Professional, direct, technical",
        "active_campaigns": [
            {"name": "Q1 SEO Push", "status": "active"},
        ],
        "top_keywords": [
            {"keyword": "B2B SaaS SEO", "position": 12},
        ],
    }

    def test_context_section_present(self):
        """assemble_prompt with client_context includes '# Client Context'."""
        assemble_prompt = _import_assemble_prompt()
        result = assemble_prompt(
            "strategist", [], client_context=self._SAMPLE_CONTEXT,
            agents_dir=_HOST_AGENTS_DIR, skills_dir=_HOST_SKILLS_DIR,
        )
        assert "# Client Context" in result

    def test_context_contains_agency_data(self):
        """Agency info appears in output."""
        assemble_prompt = _import_assemble_prompt()
        result = assemble_prompt(
            "strategist", [], client_context=self._SAMPLE_CONTEXT,
            agents_dir=_HOST_AGENTS_DIR, skills_dir=_HOST_SKILLS_DIR,
        )
        assert "Hazn Digital" in result

    def test_no_context_section_when_none(self):
        """assemble_prompt with client_context=None has no '# Client Context'."""
        assemble_prompt = _import_assemble_prompt()
        result = assemble_prompt(
            "strategist", [],
            agents_dir=_HOST_AGENTS_DIR, skills_dir=_HOST_SKILLS_DIR,
        )
        assert "# Client Context" not in result


# ── TestPromptOrdering ────────────────────────────────────────────────


@pytest.mark.skipif(not HAS_REAL_CONTENT, reason="Real agent/skill content not available")
class TestPromptOrdering:
    """Tests for section ordering within assembled prompt."""

    def test_persona_before_skills(self):
        """Persona text appears at lower index than skill text."""
        assemble_prompt = _import_assemble_prompt()
        result = assemble_prompt(
            "seo-specialist", ["seo-audit"],
            agents_dir=_HOST_AGENTS_DIR, skills_dir=_HOST_SKILLS_DIR,
        )
        persona_idx = result.index("SEO Specialist Agent")
        skill_idx = result.index("# Skill: seo-audit")
        assert persona_idx < skill_idx

    def test_skills_before_context(self):
        """Skill text appears before client context text."""
        assemble_prompt = _import_assemble_prompt()
        context = {"agency": {"name": "Test Agency"}, "client": {"name": "Test Client"}}
        result = assemble_prompt(
            "seo-specialist", ["seo-audit"], client_context=context,
            agents_dir=_HOST_AGENTS_DIR, skills_dir=_HOST_SKILLS_DIR,
        )
        skill_idx = result.index("# Skill: seo-audit")
        context_idx = result.index("# Client Context")
        assert skill_idx < context_idx

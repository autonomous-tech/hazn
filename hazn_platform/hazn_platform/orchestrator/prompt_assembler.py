"""Prompt assembler for agent phase execution (RUNT-01).

Constructs complete system prompts from three sources:
1. Agent persona markdown (identity, role, process)
2. Skill SKILL.md content (domain knowledge, audit checklists)
3. L2/L3 client context (agency + end-client data)

Called once per phase execution, before any LLM call. The assembled
prompt becomes the system prompt for the entire agent conversation.

This module is intentionally self-contained: it does NOT import from
Letta/Django modules. The persona file-reading logic is self-contained
to keep prompt_assembler importable without Django configured.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default directories, resolved relative to project root.
# Structure: hazn_platform/hazn_platform/orchestrator/prompt_assembler.py
#   -> up 3 levels -> project root / hazn / {agents,skills}
_DEFAULT_AGENTS_DIR = Path(__file__).resolve().parent.parent.parent / "hazn" / "agents"
_DEFAULT_SKILLS_DIR = Path(__file__).resolve().parent.parent.parent / "hazn" / "skills"


def _read_agent_persona(
    agent_type: str,
    agents_dir: Path | None = None,
) -> str:
    """Read agent persona markdown from hazn/agents/{agent_type}.md.

    Self-contained persona reader to avoid importing from Letta/Django
    modules. This keeps prompt_assembler testable without Django configured.
    """
    base_dir = agents_dir or _DEFAULT_AGENTS_DIR
    persona_path = base_dir / f"{agent_type}.md"
    if not persona_path.exists():
        msg = f"Agent persona not found: {agent_type} (looked at {persona_path})"
        raise ValueError(msg)
    return persona_path.read_text()


def _read_skill_content(
    skill_name: str,
    skills_dir: Path | None = None,
    include_references: bool = True,
    reference_size_limit: int = 15_000,
) -> str:
    """Read SKILL.md content and optionally inline small reference files.

    Parameters
    ----------
    skill_name:
        Skill directory name (e.g. "seo-audit").
    skills_dir:
        Base directory containing skill subdirectories.
        Defaults to ``hazn/skills/`` relative to project root.
    include_references:
        Whether to look for and inline reference docs from
        ``{skill}/references/*.md``.
    reference_size_limit:
        Maximum character count for inlining a reference file.
        Files over this limit get a size note instead of content.
        Default: 15,000 chars (~15KB).

    Returns
    -------
    str
        The SKILL.md content with optional inlined references.

    Raises
    ------
    ValueError
        If the skill directory or SKILL.md does not exist.
    """
    base = skills_dir or _DEFAULT_SKILLS_DIR
    skill_path = base / skill_name / "SKILL.md"
    if not skill_path.exists():
        msg = f"Skill not found: {skill_name} (looked at {skill_path})"
        raise ValueError(msg)

    content = skill_path.read_text()

    # Log skill frontmatter allowed-tools (informational only --
    # workflow YAML tools: field is the authoritative source for tool scoping).
    _log_skill_frontmatter(skill_name, content)

    # Optionally inline small reference docs
    if include_references:
        refs_dir = base / skill_name / "references"
        if refs_dir.is_dir():
            for ref_file in sorted(refs_dir.iterdir()):
                if ref_file.suffix == ".md":
                    ref_size = ref_file.stat().st_size
                    if ref_size <= reference_size_limit:
                        ref_content = ref_file.read_text()
                        content += f"\n\n---\n## Reference: {ref_file.stem}\n\n{ref_content}"
                    else:
                        content += (
                            f"\n\n> Reference '{ref_file.stem}' available "
                            f"({ref_size:,} bytes) -- omitted for context budget."
                        )

    return content


def _log_skill_frontmatter(skill_name: str, content: str) -> None:
    """Log skill frontmatter allowed-tools at INFO level.

    This is informational only. Workflow YAML ``tools:`` field is the
    authoritative source for tool scoping, per user decision.
    """
    if not content.startswith("---"):
        return

    end_marker = content.find("---", 3)
    if end_marker == -1:
        return

    frontmatter = content[3:end_marker].strip()
    for line in frontmatter.splitlines():
        if line.startswith("allowed-tools:"):
            tools = line.split(":", 1)[1].strip()
            logger.info(
                "Skill %s declares allowed-tools: %s (informational -- "
                "workflow YAML is authoritative)",
                skill_name,
                tools,
            )
            break


def _format_client_context(context: dict[str, Any]) -> str:
    """Format client context dict as readable markdown.

    Iterates top-level keys, renders nested dicts as indented items
    and lists as bullet points.
    """
    lines: list[str] = []
    for key, value in context.items():
        # Top-level section header
        header = key.replace("_", " ").title()
        lines.append(f"## {header}")
        lines.append("")

        if isinstance(value, dict):
            for k, v in value.items():
                lines.append(f"- **{k}**: {v}")
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    parts = ", ".join(f"{k}: {v}" for k, v in item.items())
                    lines.append(f"- {parts}")
                else:
                    lines.append(f"- {item}")
        else:
            lines.append(str(value))

        lines.append("")

    return "\n".join(lines)


def assemble_prompt(
    agent_type: str,
    skills: list[str],
    client_context: dict[str, Any] | None = None,
    agents_dir: Path | None = None,
    skills_dir: Path | None = None,
) -> str:
    """Assemble a complete system prompt for an agent phase execution.

    Sections (in order):
    1. Agent persona (identity, role, process)
    2. Skill instructions (full SKILL.md content per skill)
    3. Client context (L2 agency + L3 end-client data)

    Parameters
    ----------
    agent_type:
        Agent type identifier (e.g. "strategist", "seo-specialist").
    skills:
        List of skill names to inject (e.g. ["seo-audit"]).
    client_context:
        Optional L2/L3 client context dict. When None, the client
        context section is omitted entirely.
    agents_dir:
        Override for agent persona directory.
    skills_dir:
        Override for skills directory.

    Returns
    -------
    str
        The assembled system prompt.

    Raises
    ------
    ValueError
        If agent persona or any skill is not found.
    """
    sections: list[str] = []

    # Section 1: Agent persona
    persona = _read_agent_persona(agent_type, agents_dir=agents_dir)
    sections.append(persona)

    # Section 2: Skills (full content injection)
    for skill_name in skills:
        skill_content = _read_skill_content(skill_name, skills_dir=skills_dir)
        sections.append(f"---\n# Skill: {skill_name}\n\n{skill_content}")

    # Section 3: Client context (only when provided)
    if client_context is not None:
        context_block = _format_client_context(client_context)
        sections.append(f"---\n# Client Context\n\n{context_block}")

    result = "\n\n".join(sections)

    # Log assembled prompt stats
    logger.info(
        "Assembled prompt: agent=%s, skills=%d, context=%s, chars=%d",
        agent_type,
        len(skills),
        "yes" if client_context is not None else "no",
        len(result),
    )

    return result

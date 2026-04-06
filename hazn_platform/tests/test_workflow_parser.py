"""Tests for workflow YAML Pydantic schema and parser.

Tests cover schema validation, YAML loading, dependency graph extraction,
execution order computation, and tolerance of schema variations across
all 7 existing workflow YAML files.

Note: Real YAML files live in hazn/workflows/ outside the Django project root.
Tests that load YAML use fixture files to remain container-agnostic. An
integration test loads all 7 real files when the directory is accessible.
"""

from graphlib import CycleError
from pathlib import Path
from textwrap import dedent

import pytest
from pydantic import ValidationError

from hazn_platform.orchestrator.workflow_models import WorkflowCheckpoint
from hazn_platform.orchestrator.workflow_models import WorkflowPhaseSchema
from hazn_platform.orchestrator.workflow_models import WorkflowSchema
from hazn_platform.orchestrator.workflow_parser import get_dependency_graph
from hazn_platform.orchestrator.workflow_parser import get_execution_order
from hazn_platform.orchestrator.workflow_parser import load_workflow

# hazn/workflows/ lives outside hazn_platform/ -- try both host and container paths
_HOST_WORKFLOWS = Path(__file__).resolve().parent.parent.parent / "hazn" / "workflows"
_CONTAINER_WORKFLOWS = Path("/app").parent / "hazn" / "workflows"
WORKFLOWS_DIR = _HOST_WORKFLOWS if _HOST_WORKFLOWS.is_dir() else _CONTAINER_WORKFLOWS

# Whether real YAML files are accessible (host dev environment)
HAS_REAL_YAMLS = WORKFLOWS_DIR.is_dir() and len(list(WORKFLOWS_DIR.glob("*.yaml"))) >= 7

# ── YAML Fixture Helpers ──────────────────────────────────────────────

WEBSITE_YAML = dedent("""\
    name: website
    description: Complete B2B/commercial marketing website from strategy to deployment
    trigger: /hazn-website
    phases:
      - id: type-check
        name: Organisation Type
        agent: strategist
        required: true
      - id: strategy
        name: Strategy & Positioning
        agent: strategist
        command: /hazn-strategy
        outputs:
          - .hazn/outputs/strategy.md
        required: true
      - id: ux
        name: UX Architecture
        agent: ux-architect
        command: /hazn-ux
        depends_on: [strategy]
        outputs:
          - .hazn/outputs/ux-blueprint.md
        required: true
      - id: copy
        name: Conversion Copy
        agent: copywriter
        command: /hazn-copy
        depends_on: [strategy, ux]
        outputs:
          - .hazn/outputs/copy/
        required: false
      - id: wireframe
        name: Wireframe Validation
        agent: wireframer
        command: /hazn-wireframe
        depends_on: [ux]
        outputs:
          - .hazn/outputs/wireframes/
        required: false
      - id: dev
        name: Development
        agent: developer
        command: /hazn-dev
        depends_on: [ux]
        optional_inputs: [copy, wireframe]
        outputs:
          - src/
          - app/
        required: true
      - id: seo
        name: SEO Optimization
        agent: seo-specialist
        command: /hazn-seo
        depends_on: [dev]
        outputs:
          - .hazn/outputs/seo-checklist.md
        required: true
      - id: content
        name: Blog Content
        agent: content-writer
        command: /hazn-content
        depends_on: [strategy, seo]
        outputs:
          - content/blog/
        required: false
    checkpoints:
      - after: strategy
        message: "Strategy complete."
      - after: wireframe
        message: "Wireframes ready."
      - after: dev
        message: "Core build complete."
    estimated_duration:
      quick: "2-3 days"
      standard: "1-2 weeks"
      thorough: "3-4 weeks"
""")

AUDIT_YAML = dedent("""\
    name: audit
    description: Comprehensive website audit
    trigger: /hazn-audit
    phases:
      - id: scope
        name: Define Scope
        actions:
          - Confirm URL to audit
          - Select audit types
      - id: analysis
        name: Run Analysis
        agent: auditor
        parallel_tracks:
          - conversion_audit
          - copy_audit
          - visual_audit
          - seo_audit
      - id: synthesis
        name: Synthesize Findings
        actions:
          - Aggregate scores
          - Prioritize by impact/effort
      - id: report
        name: Generate Report
        outputs:
          - .hazn/outputs/audit-report.html
    deliverables:
      - Branded HTML audit report
      - Prioritized fix list
    estimated_duration: "2-4 hours"
""")

BLOG_YAML = dedent("""\
    name: blog
    description: SEO-optimized blog content creation pipeline
    trigger: /hazn-content
    phases:
      - id: research
        name: Keyword Research
        actions:
          - Identify seed topics
      - id: planning
        name: Content Planning
        actions:
          - Create content calendar
      - id: writing
        name: Content Creation
        agent: content-writer
        per_article:
          - Research topic depth
          - Write draft
          - Optimize for keyword
      - id: optimization
        name: SEO Polish
        agent: seo-specialist
        actions:
          - Verify keyword placement
    article_template: |
      ---
      title: "{title}"
      ---
    estimated_duration:
      per_article: "1-2 hours"
      initial_setup: "2-3 hours"
""")


@pytest.fixture
def website_yaml(tmp_path):
    """Create a website.yaml fixture file."""
    p = tmp_path / "website.yaml"
    p.write_text(WEBSITE_YAML)
    return p


@pytest.fixture
def audit_yaml(tmp_path):
    """Create an audit.yaml fixture file."""
    p = tmp_path / "audit.yaml"
    p.write_text(AUDIT_YAML)
    return p


@pytest.fixture
def blog_yaml(tmp_path):
    """Create a blog.yaml fixture file."""
    p = tmp_path / "blog.yaml"
    p.write_text(BLOG_YAML)
    return p


# ── WorkflowPhaseSchema Validation ────────────────────────────────────


class TestWorkflowPhaseSchema:
    def test_validates_phase_with_all_fields(self):
        """WorkflowPhaseSchema validates a phase with id, name, agent, depends_on, outputs, required, tools."""
        phase = WorkflowPhaseSchema(
            id="strategy",
            name="Strategy & Positioning",
            agent="strategist",
            depends_on=["type-check"],
            outputs=[".hazn/outputs/strategy.md"],
            required=True,
            tools=["search_memory", "load_context"],
        )
        assert phase.id == "strategy"
        assert phase.name == "Strategy & Positioning"
        assert phase.agent == "strategist"
        assert phase.depends_on == ["type-check"]
        assert phase.outputs == [".hazn/outputs/strategy.md"]
        assert phase.required is True
        assert phase.tools == ["search_memory", "load_context"]

    def test_depends_on_defaults_to_empty_list(self):
        """WorkflowPhaseSchema.depends_on defaults to empty list."""
        phase = WorkflowPhaseSchema(id="setup", name="Setup")
        assert phase.depends_on == []

    def test_required_defaults_to_true(self):
        """WorkflowPhaseSchema.required defaults to True."""
        phase = WorkflowPhaseSchema(id="setup", name="Setup")
        assert phase.required is True


# ── WorkflowSchema Validation ────────────────────────────────────────


class TestWorkflowSchema:
    def test_validates_complete_workflow(self):
        """WorkflowSchema validates a complete workflow with name, description, trigger, phases, checkpoints."""
        workflow = WorkflowSchema(
            name="test",
            description="A test workflow",
            trigger="/hazn-test",
            phases=[
                WorkflowPhaseSchema(id="phase1", name="Phase 1"),
                WorkflowPhaseSchema(id="phase2", name="Phase 2", depends_on=["phase1"]),
            ],
            checkpoints=[
                WorkflowCheckpoint(after="phase1", message="Phase 1 done"),
            ],
        )
        assert workflow.name == "test"
        assert workflow.description == "A test workflow"
        assert workflow.trigger == "/hazn-test"
        assert len(workflow.phases) == 2
        assert len(workflow.checkpoints) == 1

    def test_checkpoints_default_to_empty_list(self):
        """WorkflowSchema.checkpoints defaults to empty list."""
        workflow = WorkflowSchema(
            name="minimal",
            description="Minimal workflow",
            trigger="/test",
            phases=[WorkflowPhaseSchema(id="only", name="Only Phase")],
        )
        assert workflow.checkpoints == []


# ── load_workflow ────────────────────────────────────────────────────


class TestLoadWorkflow:
    def test_load_website_yaml(self, website_yaml):
        """load_workflow returns a valid WorkflowSchema with 8 phases."""
        workflow = load_workflow(website_yaml)
        assert isinstance(workflow, WorkflowSchema)
        assert workflow.name == "website"
        assert len(workflow.phases) == 8

    def test_load_nonexistent_path_raises_file_not_found(self, tmp_path):
        """load_workflow on a non-existent path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_workflow(tmp_path / "nonexistent.yaml")

    def test_load_invalid_yaml_raises_validation_error(self, tmp_path):
        """load_workflow with invalid YAML (missing required field 'name') raises ValidationError."""
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text(
            "description: Missing name field\ntrigger: /test\nphases:\n  - id: p1\n    name: P1\n"
        )
        with pytest.raises(ValidationError):
            load_workflow(invalid_yaml)

    @pytest.mark.skipif(not HAS_REAL_YAMLS, reason="Real YAML files not accessible")
    def test_all_seven_yamls_parse(self):
        """All 7 existing workflow YAML files parse without error."""
        yaml_files = sorted(WORKFLOWS_DIR.glob("*.yaml"))
        assert len(yaml_files) == 7, f"Expected 7 YAML files, found {len(yaml_files)}"
        for yaml_file in yaml_files:
            workflow = load_workflow(yaml_file)
            assert isinstance(workflow, WorkflowSchema), f"Failed to parse {yaml_file.name}"
            assert len(workflow.phases) > 0, f"{yaml_file.name} has no phases"

    def test_audit_yaml_with_parallel_tracks(self, audit_yaml):
        """audit.yaml with parallel_tracks parses correctly."""
        workflow = load_workflow(audit_yaml)
        assert workflow.name == "audit"
        analysis_phase = next(p for p in workflow.phases if p.id == "analysis")
        assert "conversion_audit" in analysis_phase.parallel_tracks
        assert len(analysis_phase.parallel_tracks) == 4

    def test_blog_yaml_with_per_article(self, blog_yaml):
        """blog.yaml with per_article field parses without error (per_article stored via extra='allow')."""
        workflow = load_workflow(blog_yaml)
        assert workflow.name == "blog"
        writing_phase = next(p for p in workflow.phases if p.id == "writing")
        # per_article is captured via Pydantic extra="allow"
        assert hasattr(writing_phase, "per_article") or "per_article" in writing_phase.model_extra


# ── get_dependency_graph ─────────────────────────────────────────────


class TestGetDependencyGraph:
    def test_returns_dict_of_phase_id_to_dependencies(self, website_yaml):
        """get_dependency_graph returns a dict mapping phase_id -> set of dependency phase_ids."""
        workflow = load_workflow(website_yaml)
        graph = get_dependency_graph(workflow)
        assert isinstance(graph, dict)
        for phase_id, deps in graph.items():
            assert isinstance(phase_id, str)
            assert isinstance(deps, set)

    def test_website_yaml_dependency_graph(self, website_yaml):
        """website.yaml: strategy has no deps; ux depends on strategy; copy depends on strategy+ux; dev depends on ux."""
        workflow = load_workflow(website_yaml)
        graph = get_dependency_graph(workflow)
        assert graph["strategy"] == set()
        assert graph["ux"] == {"strategy"}
        assert graph["copy"] == {"strategy", "ux"}
        assert graph["dev"] == {"ux"}

    def test_detects_circular_dependencies(self):
        """Circular dependencies detected by get_execution_order raising CycleError."""
        workflow = WorkflowSchema(
            name="cyclic",
            description="Has a cycle",
            trigger="/test",
            phases=[
                WorkflowPhaseSchema(id="a", name="A", depends_on=["c"]),
                WorkflowPhaseSchema(id="b", name="B", depends_on=["a"]),
                WorkflowPhaseSchema(id="c", name="C", depends_on=["b"]),
            ],
        )
        with pytest.raises(CycleError):
            get_execution_order(workflow)


# ── get_execution_order ──────────────────────────────────────────────


class TestGetExecutionOrder:
    def test_returns_list_of_sets(self, website_yaml):
        """get_execution_order returns a list of sets (waves)."""
        workflow = load_workflow(website_yaml)
        order = get_execution_order(workflow)
        assert isinstance(order, list)
        for wave in order:
            assert isinstance(wave, set)

    def test_independent_phases_in_same_wave(self):
        """Phases with no inter-dependency should appear in the same wave."""
        workflow = WorkflowSchema(
            name="parallel",
            description="Parallel phases",
            trigger="/test",
            phases=[
                WorkflowPhaseSchema(id="root", name="Root"),
                WorkflowPhaseSchema(id="a", name="A", depends_on=["root"]),
                WorkflowPhaseSchema(id="b", name="B", depends_on=["root"]),
            ],
        )
        order = get_execution_order(workflow)
        # root should be in wave 0; a and b should be in the same wave
        assert {"root"} in order
        assert {"a", "b"} in order

    def test_website_yaml_type_check_and_strategy_in_early_waves(self, website_yaml):
        """website.yaml: type-check has no deps, so it should be in the first wave."""
        workflow = load_workflow(website_yaml)
        order = get_execution_order(workflow)
        # First wave should contain type-check (no dependencies)
        assert "type-check" in order[0]

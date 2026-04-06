"""Workflow YAML loading, validation, and dependency graph extraction.

Loads workflow YAML files into validated Pydantic models and provides
dependency graph construction and topological execution order computation
using Python stdlib graphlib.
"""

from __future__ import annotations

from graphlib import TopologicalSorter
from pathlib import Path

import yaml

from .workflow_models import WorkflowSchema


def load_workflow(path: str | Path) -> WorkflowSchema:
    """Load and validate a workflow YAML file.

    Args:
        path: Path to the YAML file.

    Returns:
        A validated WorkflowSchema instance.

    Raises:
        FileNotFoundError: If the path does not exist.
        pydantic.ValidationError: If the YAML does not match the schema.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Workflow file not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    return WorkflowSchema.model_validate(data)


def get_dependency_graph(workflow: WorkflowSchema) -> dict[str, set[str]]:
    """Build a dependency graph from workflow phases.

    Args:
        workflow: A validated WorkflowSchema.

    Returns:
        Dict mapping each phase_id to its set of dependency phase_ids.
    """
    graph: dict[str, set[str]] = {}
    for phase in workflow.phases:
        graph[phase.id] = set(phase.depends_on)
    return graph


def get_execution_order(workflow: WorkflowSchema) -> list[set[str]]:
    """Compute execution waves from workflow dependency graph.

    Uses graphlib.TopologicalSorter to produce a list of sets where
    each set contains phases that can run in parallel (all their
    dependencies have been satisfied in previous waves).

    Args:
        workflow: A validated WorkflowSchema.

    Returns:
        List of sets, each set containing phase_ids for one execution wave.

    Raises:
        graphlib.CycleError: If circular dependencies are detected.
    """
    graph = get_dependency_graph(workflow)
    ts = TopologicalSorter(graph)
    ts.prepare()

    waves: list[set[str]] = []
    while ts.is_active():
        ready = ts.get_ready()
        wave = set(ready)
        waves.append(wave)
        for node in ready:
            ts.done(node)

    return waves

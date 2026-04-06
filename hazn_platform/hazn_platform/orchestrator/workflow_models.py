"""Pydantic schemas for workflow YAML validation.

These models validate the structure of workflow YAML files found in
hazn/workflows/. The schema is tolerant of variations across files
(e.g., per_article in blog.yaml, parallel_tracks in audit.yaml)
via Pydantic's extra="allow" config.
"""

from __future__ import annotations

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class WorkflowPhaseSchema(BaseModel):
    """Schema for a single workflow phase."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    agent: str | None = None
    depends_on: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    required: bool = True
    tools: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    max_turns: int = 30
    actions: list[str] = Field(default_factory=list)
    command: str | None = None
    note: str | None = None
    optional_inputs: list[str] = Field(default_factory=list)
    parallel_tracks: list[str] = Field(default_factory=list)


class WorkflowCheckpoint(BaseModel):
    """Schema for a workflow checkpoint."""

    after: str
    message: str


class WorkflowSchema(BaseModel):
    """Schema for a complete workflow YAML definition."""

    model_config = ConfigDict(extra="allow")

    name: str
    description: str
    trigger: str
    phases: list[WorkflowPhaseSchema]
    checkpoints: list[WorkflowCheckpoint] = Field(default_factory=list)
    estimated_duration: dict | str | None = None
    deliverables: list[str] = Field(default_factory=list)

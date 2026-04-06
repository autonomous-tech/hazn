"""Pydantic schemas for validating structured agent output before rendering.

These models define the contract between the delivery-phase agent's JSON
output and the Jinja2 template. Validation catches malformed data before
it reaches the renderer, providing clear error messages.
"""

from __future__ import annotations

from pydantic import BaseModel


class Finding(BaseModel):
    """A single audit finding with severity, evidence, and recommendation."""

    severity: str
    description: str
    evidence: str
    recommendation: str


class Recommendation(BaseModel):
    """A prioritized recommendation with expected impact."""

    priority: str
    action: str
    impact: str


class AuditReportPayload(BaseModel):
    """Complete payload for rendering an analytics audit report.

    The delivery-phase agent produces this JSON structure, which is
    validated here before being passed to the Jinja2 renderer.
    """

    executive_summary: str
    findings: list[Finding]
    recommendations: list[Recommendation]
    scores: dict[str, int | float]
    client_name: str = ""
    report_date: str = ""

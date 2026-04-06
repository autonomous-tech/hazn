"""Jinja2 standalone rendering pipeline for branded HTML reports.

Uses Jinja2 directly (not Django's template engine) to render structured
JSON agent output into self-contained branded HTML. The Environment is
configured with autoescape for XSS prevention.
"""

from __future__ import annotations

from pathlib import Path

import jinja2

from .schemas import AuditReportPayload

TEMPLATE_DIR = Path(__file__).parent / "templates"

_jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=jinja2.select_autoescape(["html"]),
)


def render_report(template_name: str, payload: AuditReportPayload) -> str:
    """Render a branded HTML report from a validated payload.

    Parameters
    ----------
    template_name:
        Template filename (e.g., "analytics-audit.html").
    payload:
        Validated AuditReportPayload from the delivery agent.

    Returns
    -------
    str
        Complete HTML string ready for storage in Deliverable.html_content.
    """
    template = _jinja_env.get_template(template_name)
    return template.render(**payload.model_dump())

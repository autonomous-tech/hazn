"""Tests for the deliverable rendering pipeline.

Verifies:
- render_report() produces branded HTML from structured JSON context
- AuditReportPayload Pydantic schema validates correct/invalid payloads
- Finding and Recommendation models validate required fields
- HTML output includes Autonomous branding and is properly escaped
- Empty findings list produces valid HTML (not an error)
"""

import pytest


@pytest.fixture()
def sample_payload_dict():
    """Sample structured JSON payload for AuditReportPayload."""
    return {
        "executive_summary": "The website shows strong technical SEO fundamentals but needs improvement in content optimization and mobile performance.",
        "findings": [
            {
                "severity": "High",
                "description": "Missing meta descriptions on 15 key landing pages",
                "evidence": "Crawl analysis showed 15 of 42 pages lack meta descriptions",
                "recommendation": "Add unique, keyword-rich meta descriptions to all landing pages",
            },
            {
                "severity": "Medium",
                "description": "Slow Largest Contentful Paint on mobile",
                "evidence": "LCP averages 4.2s on mobile vs 2.5s target",
                "recommendation": "Optimize hero images and defer non-critical JavaScript",
            },
        ],
        "recommendations": [
            {
                "priority": "High",
                "action": "Implement meta description strategy for all landing pages",
                "impact": "Expected 15-20% improvement in organic CTR",
            },
            {
                "priority": "Medium",
                "action": "Optimize Core Web Vitals for mobile users",
                "impact": "Better mobile rankings and reduced bounce rate",
            },
        ],
        "scores": {
            "overall": 72,
            "technical": 85,
            "content": 60,
            "ux": 71,
        },
        "client_name": "Acme Corp",
        "report_date": "2026-03-06",
    }


class TestAuditReportPayload:
    """Test Pydantic schema validation for agent output."""

    def test_valid_payload_accepted(self, sample_payload_dict):
        from hazn_platform.deliverable_pipeline.schemas import AuditReportPayload

        payload = AuditReportPayload(**sample_payload_dict)
        assert payload.executive_summary == sample_payload_dict["executive_summary"]
        assert len(payload.findings) == 2
        assert len(payload.recommendations) == 2
        assert payload.scores["overall"] == 72
        assert payload.client_name == "Acme Corp"
        assert payload.report_date == "2026-03-06"

    def test_missing_required_field_rejected(self):
        from pydantic import ValidationError

        from hazn_platform.deliverable_pipeline.schemas import AuditReportPayload

        with pytest.raises(ValidationError):
            AuditReportPayload(
                # Missing executive_summary
                findings=[],
                recommendations=[],
                scores={},
            )

    def test_defaults_for_optional_fields(self):
        from hazn_platform.deliverable_pipeline.schemas import AuditReportPayload

        payload = AuditReportPayload(
            executive_summary="Summary",
            findings=[],
            recommendations=[],
            scores={"overall": 50},
        )
        assert payload.client_name == ""
        assert payload.report_date == ""


class TestFindingModel:
    """Test Pydantic Finding model validation."""

    def test_valid_finding(self):
        from hazn_platform.deliverable_pipeline.schemas import Finding

        finding = Finding(
            severity="High",
            description="Test finding",
            evidence="Test evidence",
            recommendation="Test recommendation",
        )
        assert finding.severity == "High"
        assert finding.description == "Test finding"

    def test_missing_required_field_rejected(self):
        from pydantic import ValidationError

        from hazn_platform.deliverable_pipeline.schemas import Finding

        with pytest.raises(ValidationError):
            Finding(
                severity="High",
                description="Missing evidence and recommendation",
                # Missing evidence and recommendation
            )


class TestRecommendationModel:
    """Test Pydantic Recommendation model validation."""

    def test_valid_recommendation(self):
        from hazn_platform.deliverable_pipeline.schemas import Recommendation

        rec = Recommendation(
            priority="High",
            action="Do the thing",
            impact="Big improvement",
        )
        assert rec.priority == "High"
        assert rec.action == "Do the thing"

    def test_missing_required_field_rejected(self):
        from pydantic import ValidationError

        from hazn_platform.deliverable_pipeline.schemas import Recommendation

        with pytest.raises(ValidationError):
            Recommendation(
                priority="High",
                # Missing action and impact
            )


class TestRenderReport:
    """Test Jinja2 rendering pipeline."""

    def test_render_produces_html_with_content(self, sample_payload_dict):
        from hazn_platform.deliverable_pipeline.schemas import AuditReportPayload
        from hazn_platform.deliverable_pipeline.renderer import render_report

        payload = AuditReportPayload(**sample_payload_dict)
        html = render_report("analytics-audit.html", payload)

        # Contains executive summary text
        assert "strong technical SEO fundamentals" in html
        # Contains finding descriptions
        assert "Missing meta descriptions" in html
        assert "Slow Largest Contentful Paint" in html
        # Contains recommendation actions
        assert "Implement meta description strategy" in html
        # Contains score values
        assert "72" in html
        assert "85" in html
        # Is valid HTML
        assert "<!DOCTYPE html>" in html or "<!doctype html>" in html.lower()
        assert "</html>" in html

    def test_render_with_empty_findings(self, sample_payload_dict):
        from hazn_platform.deliverable_pipeline.schemas import AuditReportPayload
        from hazn_platform.deliverable_pipeline.renderer import render_report

        sample_payload_dict["findings"] = []
        sample_payload_dict["recommendations"] = []
        payload = AuditReportPayload(**sample_payload_dict)
        html = render_report("analytics-audit.html", payload)

        # Should produce valid HTML without errors
        assert "<!DOCTYPE html>" in html or "<!doctype html>" in html.lower()
        assert "</html>" in html
        # Executive summary still present
        assert "strong technical SEO fundamentals" in html
        # No finding blocks (since findings is empty)
        assert "severity-high" not in html.lower() or "High" not in html

    def test_render_includes_autonomous_branding(self, sample_payload_dict):
        from hazn_platform.deliverable_pipeline.schemas import AuditReportPayload
        from hazn_platform.deliverable_pipeline.renderer import render_report

        payload = AuditReportPayload(**sample_payload_dict)
        html = render_report("analytics-audit.html", payload)

        # Contains Autonomous branding
        assert "Autonomous" in html
        # Contains footer with generation info (Autonomous is in a span)
        assert "Generated by" in html
        # Contains report date in footer
        assert "2026-03-06" in html

    def test_render_escapes_xss(self, sample_payload_dict):
        from hazn_platform.deliverable_pipeline.schemas import AuditReportPayload
        from hazn_platform.deliverable_pipeline.renderer import render_report

        # Inject XSS attempt in executive summary
        sample_payload_dict["executive_summary"] = '<script>alert("xss")</script>Test'
        payload = AuditReportPayload(**sample_payload_dict)
        html = render_report("analytics-audit.html", payload)

        # Script tag should be escaped, not rendered as raw HTML
        assert "<script>" not in html
        assert "&lt;script&gt;" in html or "&#" in html

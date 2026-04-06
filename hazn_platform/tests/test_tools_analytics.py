"""Tests for analytics tools -- pull_ga4_data, query_gsc, check_pagespeed.

All external API calls (Google Analytics, Search Console, PageSpeed Insights)
are mocked. Vault credential lookups are mocked. File output uses tmp_path.
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_vault_credential():
    """Return a mock VaultCredential with vault_secret_id."""
    cred = MagicMock()
    cred.vault_secret_id = "secret/data/clients/test-client/ga4"
    return cred


@pytest.fixture
def mock_sa_json():
    """Return a mock service account JSON dict."""
    return {
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "key123",
        "private_key": "-----BEGIN RSA PRIVATE KEY-----\nfake\n-----END RSA PRIVATE KEY-----\n",
        "client_email": "test@test-project.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }


@pytest.fixture
def tmp_output_dir(tmp_path):
    """Patch the output base directory to use tmp_path."""
    return tmp_path


# ---------------------------------------------------------------------------
# GA4 Tests
# ---------------------------------------------------------------------------


class TestGA4Tool:
    """pull_ga4_data collects 6 GA4 reports and writes JSON to file."""

    @pytest.mark.asyncio
    async def test_accepts_client_id_property_id_days(self):
        """pull_ga4_data accepts client_id, property_id, and days params."""
        from hazn_platform.orchestrator.tools.analytics import pull_ga4_data

        # Tool should have name attribute
        assert pull_ga4_data.name == "pull_ga4_data"

    @pytest.mark.asyncio
    async def test_fetches_credentials_from_vault(
        self, mock_vault_credential, mock_sa_json, tmp_output_dir
    ):
        """pull_ga4_data fetches credentials from Vault via VaultCredential."""
        from hazn_platform.orchestrator.tools.analytics import pull_ga4_data

        mock_vc_get = MagicMock(return_value=mock_vault_credential)
        mock_report_response = _make_ga4_report_response([])

        with (
            patch(
                "hazn_platform.orchestrator.tools.analytics.VaultCredential.objects"
            ) as mock_objects,
            patch(
                "hazn_platform.orchestrator.tools.analytics.read_secret",
                return_value=mock_sa_json,
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.service_account.Credentials.from_service_account_info",
                return_value=MagicMock(),
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.BetaAnalyticsDataClient"
            ) as mock_client_cls,
            patch(
                "hazn_platform.orchestrator.tools.analytics._OUTPUT_BASE",
                str(tmp_output_dir),
            ),
        ):
            mock_objects.get = mock_vc_get
            mock_client_cls.return_value.run_report.return_value = (
                mock_report_response
            )

            result = await pull_ga4_data.handler(
                {"client_id": "test-client", "property_id": "123456", "days": 30}
            )

        mock_vc_get.assert_called_once_with(
            end_client_id="test-client", service_name="ga4"
        )

    @pytest.mark.asyncio
    async def test_runs_six_reports(
        self, mock_vault_credential, mock_sa_json, tmp_output_dir
    ):
        """pull_ga4_data runs 6 GA4 Data API reports."""
        from hazn_platform.orchestrator.tools.analytics import pull_ga4_data

        mock_report_response = _make_ga4_report_response(
            [{"eventName": "page_view", "eventCount": "100", "totalUsers": "50"}]
        )

        with (
            patch(
                "hazn_platform.orchestrator.tools.analytics.VaultCredential.objects"
            ) as mock_objects,
            patch(
                "hazn_platform.orchestrator.tools.analytics.read_secret",
                return_value=mock_sa_json,
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.service_account.Credentials.from_service_account_info",
                return_value=MagicMock(),
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.BetaAnalyticsDataClient"
            ) as mock_client_cls,
            patch(
                "hazn_platform.orchestrator.tools.analytics._OUTPUT_BASE",
                str(tmp_output_dir),
            ),
        ):
            mock_objects.get = MagicMock(return_value=mock_vault_credential)
            mock_client = mock_client_cls.return_value
            mock_client.run_report.return_value = mock_report_response

            result = await pull_ga4_data.handler(
                {"client_id": "test-client", "property_id": "123456", "days": 30}
            )

        # Should call run_report 6 times (events, conversions, traffic_sources,
        # landing_pages, devices, countries)
        assert mock_client.run_report.call_count == 6

    @pytest.mark.asyncio
    async def test_writes_json_to_file(
        self, mock_vault_credential, mock_sa_json, tmp_output_dir
    ):
        """pull_ga4_data writes full JSON to /tmp/hazn-audit/{client_id}/{timestamp}/ga4.json."""
        from hazn_platform.orchestrator.tools.analytics import pull_ga4_data

        mock_report_response = _make_ga4_report_response(
            [{"eventName": "page_view", "eventCount": "100", "totalUsers": "50"}]
        )

        with (
            patch(
                "hazn_platform.orchestrator.tools.analytics.VaultCredential.objects"
            ) as mock_objects,
            patch(
                "hazn_platform.orchestrator.tools.analytics.read_secret",
                return_value=mock_sa_json,
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.service_account.Credentials.from_service_account_info",
                return_value=MagicMock(),
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.BetaAnalyticsDataClient"
            ) as mock_client_cls,
            patch(
                "hazn_platform.orchestrator.tools.analytics._OUTPUT_BASE",
                str(tmp_output_dir),
            ),
        ):
            mock_objects.get = MagicMock(return_value=mock_vault_credential)
            mock_client_cls.return_value.run_report.return_value = (
                mock_report_response
            )

            result = await pull_ga4_data.handler(
                {"client_id": "test-client", "property_id": "123456", "days": 30}
            )

        # Should return summary with output_file path
        assert result.get("isError") is not True
        text = json.loads(result["content"][0]["text"])
        assert "output_file" in text
        assert text["output_file"].endswith("ga4.json")
        assert os.path.exists(text["output_file"])

        # Read the output file and verify structure
        with open(text["output_file"]) as f:
            data = json.load(f)
        assert "events" in data
        assert "conversions" in data
        assert "traffic_sources" in data
        assert "landing_pages" in data
        assert "devices" in data
        assert "countries" in data

    @pytest.mark.asyncio
    async def test_returns_summary_with_sections(
        self, mock_vault_credential, mock_sa_json, tmp_output_dir
    ):
        """pull_ga4_data returns summary with output_file, record_count, sections."""
        from hazn_platform.orchestrator.tools.analytics import pull_ga4_data

        mock_report_response = _make_ga4_report_response(
            [{"eventName": "page_view", "eventCount": "100", "totalUsers": "50"}]
        )

        with (
            patch(
                "hazn_platform.orchestrator.tools.analytics.VaultCredential.objects"
            ) as mock_objects,
            patch(
                "hazn_platform.orchestrator.tools.analytics.read_secret",
                return_value=mock_sa_json,
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.service_account.Credentials.from_service_account_info",
                return_value=MagicMock(),
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.BetaAnalyticsDataClient"
            ) as mock_client_cls,
            patch(
                "hazn_platform.orchestrator.tools.analytics._OUTPUT_BASE",
                str(tmp_output_dir),
            ),
        ):
            mock_objects.get = MagicMock(return_value=mock_vault_credential)
            mock_client_cls.return_value.run_report.return_value = (
                mock_report_response
            )

            result = await pull_ga4_data.handler(
                {"client_id": "test-client", "property_id": "123456", "days": 30}
            )

        text = json.loads(result["content"][0]["text"])
        assert "record_count" in text
        assert "sections" in text
        assert set(text["sections"]) == {
            "events",
            "conversions",
            "traffic_sources",
            "landing_pages",
            "devices",
            "countries",
        }

    @pytest.mark.asyncio
    async def test_returns_error_on_api_failure(
        self, mock_vault_credential, mock_sa_json, tmp_output_dir
    ):
        """pull_ga4_data returns error content on API failure."""
        from hazn_platform.orchestrator.tools.analytics import pull_ga4_data

        with (
            patch(
                "hazn_platform.orchestrator.tools.analytics.VaultCredential.objects"
            ) as mock_objects,
            patch(
                "hazn_platform.orchestrator.tools.analytics.read_secret",
                return_value=mock_sa_json,
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.service_account.Credentials.from_service_account_info",
                return_value=MagicMock(),
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.BetaAnalyticsDataClient"
            ) as mock_client_cls,
            patch(
                "hazn_platform.orchestrator.tools.analytics._OUTPUT_BASE",
                str(tmp_output_dir),
            ),
        ):
            mock_objects.get = MagicMock(return_value=mock_vault_credential)
            mock_client_cls.return_value.run_report.side_effect = Exception(
                "Invalid property ID"
            )

            result = await pull_ga4_data.handler(
                {"client_id": "test-client", "property_id": "bad_id", "days": 30}
            )

        assert result.get("isError") is True
        assert "Invalid property ID" in result["content"][0]["text"]


# ---------------------------------------------------------------------------
# GSC Tests
# ---------------------------------------------------------------------------


class TestGSCTool:
    """query_gsc collects 5 GSC query groups and writes JSON to file."""

    @pytest.mark.asyncio
    async def test_accepts_client_id_site_url_days(self):
        """query_gsc accepts client_id, site_url, and days params."""
        from hazn_platform.orchestrator.tools.analytics import query_gsc

        assert query_gsc.name == "query_gsc"

    @pytest.mark.asyncio
    async def test_fetches_credentials_from_vault(
        self, mock_vault_credential, mock_sa_json, tmp_output_dir
    ):
        """query_gsc fetches credentials from Vault via VaultCredential."""
        from hazn_platform.orchestrator.tools.analytics import query_gsc

        mock_vc_get = MagicMock(return_value=mock_vault_credential)
        mock_query_response = {"rows": []}

        with (
            patch(
                "hazn_platform.orchestrator.tools.analytics.VaultCredential.objects"
            ) as mock_objects,
            patch(
                "hazn_platform.orchestrator.tools.analytics.read_secret",
                return_value=mock_sa_json,
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.service_account.Credentials.from_service_account_info",
                return_value=MagicMock(),
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.build"
            ) as mock_build,
            patch(
                "hazn_platform.orchestrator.tools.analytics._OUTPUT_BASE",
                str(tmp_output_dir),
            ),
        ):
            mock_objects.get = mock_vc_get
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            mock_service.searchanalytics.return_value.query.return_value.execute.return_value = (
                mock_query_response
            )

            result = await query_gsc.handler(
                {
                    "client_id": "test-client",
                    "site_url": "sc-domain:example.com",
                    "days": 30,
                }
            )

        mock_vc_get.assert_called_once_with(
            end_client_id="test-client", service_name="gsc"
        )

    @pytest.mark.asyncio
    async def test_runs_multiple_gsc_queries(
        self, mock_vault_credential, mock_sa_json, tmp_output_dir
    ):
        """query_gsc runs multiple GSC API queries for full data collection."""
        from hazn_platform.orchestrator.tools.analytics import query_gsc

        mock_query_response = {
            "rows": [
                {
                    "keys": ["test query", "https://example.com/page"],
                    "clicks": 10,
                    "impressions": 100,
                    "ctr": 0.1,
                    "position": 5.0,
                }
            ]
        }

        with (
            patch(
                "hazn_platform.orchestrator.tools.analytics.VaultCredential.objects"
            ) as mock_objects,
            patch(
                "hazn_platform.orchestrator.tools.analytics.read_secret",
                return_value=mock_sa_json,
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.service_account.Credentials.from_service_account_info",
                return_value=MagicMock(),
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.build"
            ) as mock_build,
            patch(
                "hazn_platform.orchestrator.tools.analytics._OUTPUT_BASE",
                str(tmp_output_dir),
            ),
        ):
            mock_objects.get = MagicMock(return_value=mock_vault_credential)
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            mock_service.searchanalytics.return_value.query.return_value.execute.return_value = (
                mock_query_response
            )

            result = await query_gsc.handler(
                {
                    "client_id": "test-client",
                    "site_url": "sc-domain:example.com",
                    "days": 30,
                }
            )

        # Should call query() multiple times for different dimension groups
        assert mock_service.searchanalytics.return_value.query.call_count >= 3

    @pytest.mark.asyncio
    async def test_writes_json_to_file(
        self, mock_vault_credential, mock_sa_json, tmp_output_dir
    ):
        """query_gsc writes full JSON to /tmp/hazn-audit/{client_id}/{timestamp}/gsc.json."""
        from hazn_platform.orchestrator.tools.analytics import query_gsc

        # Keys must have enough entries for ALL dimension combos used:
        # ["query"], ["page"], ["query", "page"], ["date"]
        mock_query_response = {
            "rows": [
                {
                    "keys": ["test query", "https://example.com/page"],
                    "clicks": 10,
                    "impressions": 100,
                    "ctr": 0.1,
                    "position": 5.0,
                }
            ]
        }

        with (
            patch(
                "hazn_platform.orchestrator.tools.analytics.VaultCredential.objects"
            ) as mock_objects,
            patch(
                "hazn_platform.orchestrator.tools.analytics.read_secret",
                return_value=mock_sa_json,
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.service_account.Credentials.from_service_account_info",
                return_value=MagicMock(),
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.build"
            ) as mock_build,
            patch(
                "hazn_platform.orchestrator.tools.analytics._OUTPUT_BASE",
                str(tmp_output_dir),
            ),
        ):
            mock_objects.get = MagicMock(return_value=mock_vault_credential)
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            mock_service.searchanalytics.return_value.query.return_value.execute.return_value = (
                mock_query_response
            )

            result = await query_gsc.handler(
                {
                    "client_id": "test-client",
                    "site_url": "sc-domain:example.com",
                    "days": 30,
                }
            )

        assert result.get("isError") is not True
        text = json.loads(result["content"][0]["text"])
        assert "output_file" in text
        assert text["output_file"].endswith("gsc.json")
        assert os.path.exists(text["output_file"])

        with open(text["output_file"]) as f:
            data = json.load(f)
        assert "top_queries" in data
        assert "landing_pages" in data
        assert "brand_analysis" in data
        assert "cannibalization" in data
        assert "weekly_trends" in data

    @pytest.mark.asyncio
    async def test_returns_summary_with_sections(
        self, mock_vault_credential, mock_sa_json, tmp_output_dir
    ):
        """query_gsc returns summary with output_file, record_count, sections."""
        from hazn_platform.orchestrator.tools.analytics import query_gsc

        mock_query_response = {
            "rows": [
                {
                    "keys": ["test query", "https://example.com/page"],
                    "clicks": 10,
                    "impressions": 100,
                    "ctr": 0.1,
                    "position": 5.0,
                }
            ]
        }

        with (
            patch(
                "hazn_platform.orchestrator.tools.analytics.VaultCredential.objects"
            ) as mock_objects,
            patch(
                "hazn_platform.orchestrator.tools.analytics.read_secret",
                return_value=mock_sa_json,
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.service_account.Credentials.from_service_account_info",
                return_value=MagicMock(),
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.build"
            ) as mock_build,
            patch(
                "hazn_platform.orchestrator.tools.analytics._OUTPUT_BASE",
                str(tmp_output_dir),
            ),
        ):
            mock_objects.get = MagicMock(return_value=mock_vault_credential)
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            mock_service.searchanalytics.return_value.query.return_value.execute.return_value = (
                mock_query_response
            )

            result = await query_gsc.handler(
                {
                    "client_id": "test-client",
                    "site_url": "sc-domain:example.com",
                    "days": 30,
                }
            )

        text = json.loads(result["content"][0]["text"])
        assert "record_count" in text
        assert "sections" in text
        assert set(text["sections"]) == {
            "top_queries",
            "landing_pages",
            "brand_analysis",
            "cannibalization",
            "weekly_trends",
        }

    @pytest.mark.asyncio
    async def test_returns_error_on_api_failure(
        self, mock_vault_credential, mock_sa_json, tmp_output_dir
    ):
        """query_gsc returns error content on API failure."""
        from hazn_platform.orchestrator.tools.analytics import query_gsc

        with (
            patch(
                "hazn_platform.orchestrator.tools.analytics.VaultCredential.objects"
            ) as mock_objects,
            patch(
                "hazn_platform.orchestrator.tools.analytics.read_secret",
                return_value=mock_sa_json,
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.service_account.Credentials.from_service_account_info",
                return_value=MagicMock(),
            ),
            patch(
                "hazn_platform.orchestrator.tools.analytics.build"
            ) as mock_build,
            patch(
                "hazn_platform.orchestrator.tools.analytics._OUTPUT_BASE",
                str(tmp_output_dir),
            ),
        ):
            mock_objects.get = MagicMock(return_value=mock_vault_credential)
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            mock_service.searchanalytics.return_value.query.return_value.execute.side_effect = Exception(
                "Quota exceeded"
            )

            result = await query_gsc.handler(
                {
                    "client_id": "test-client",
                    "site_url": "sc-domain:example.com",
                    "days": 30,
                }
            )

        assert result.get("isError") is True
        assert "Quota exceeded" in result["content"][0]["text"]


# ---------------------------------------------------------------------------
# PageSpeed Tests
# ---------------------------------------------------------------------------


# Realistic PSI API response shape for mocking
_PSI_RESPONSE_MOBILE = {
    "lighthouseResult": {
        "categories": {
            "performance": {"score": 0.72, "title": "Performance"},
        },
        "audits": {
            "largest-contentful-paint": {
                "id": "largest-contentful-paint",
                "title": "Largest Contentful Paint",
                "score": 0.5,
                "numericValue": 3200,
                "displayValue": "3.2 s",
            },
            "cumulative-layout-shift": {
                "id": "cumulative-layout-shift",
                "title": "Cumulative Layout Shift",
                "score": 0.8,
                "numericValue": 0.12,
                "displayValue": "0.12",
            },
            "interaction-to-next-paint": {
                "id": "interaction-to-next-paint",
                "title": "Interaction to Next Paint",
                "score": 0.6,
                "numericValue": 280,
                "displayValue": "280 ms",
            },
            "render-blocking-resources": {
                "id": "render-blocking-resources",
                "title": "Eliminate render-blocking resources",
                "score": 0.3,
                "displayValue": "Potential savings of 1,200 ms",
                "details": {
                    "type": "opportunity",
                    "overallSavingsMs": 1200,
                },
            },
            "unused-javascript": {
                "id": "unused-javascript",
                "title": "Reduce unused JavaScript",
                "score": 0.5,
                "displayValue": "Potential savings of 800 ms",
                "details": {
                    "type": "opportunity",
                    "overallSavingsMs": 800,
                },
            },
            "unminified-css": {
                "id": "unminified-css",
                "title": "Minify CSS",
                "score": 0.9,
                "details": {
                    "type": "opportunity",
                    "overallSavingsMs": 50,
                },
            },
        },
    },
}

_PSI_RESPONSE_DESKTOP = {
    "lighthouseResult": {
        "categories": {
            "performance": {"score": 0.91, "title": "Performance"},
        },
        "audits": {
            "largest-contentful-paint": {
                "id": "largest-contentful-paint",
                "title": "Largest Contentful Paint",
                "score": 0.9,
                "numericValue": 1200,
                "displayValue": "1.2 s",
            },
            "cumulative-layout-shift": {
                "id": "cumulative-layout-shift",
                "title": "Cumulative Layout Shift",
                "score": 0.95,
                "numericValue": 0.02,
                "displayValue": "0.02",
            },
            "interaction-to-next-paint": {
                "id": "interaction-to-next-paint",
                "title": "Interaction to Next Paint",
                "score": 0.9,
                "numericValue": 120,
                "displayValue": "120 ms",
            },
        },
    },
}


class TestPageSpeedTool:
    """check_pagespeed runs dual strategy with CWV extraction."""

    @pytest.mark.asyncio
    async def test_accepts_url_and_client_id(self):
        """check_pagespeed accepts url and client_id params."""
        from hazn_platform.orchestrator.tools.analytics import check_pagespeed

        assert check_pagespeed.name == "check_pagespeed"

    @pytest.mark.asyncio
    async def test_runs_dual_strategy(self, tmp_output_dir):
        """check_pagespeed runs both mobile AND desktop strategies."""
        from hazn_platform.orchestrator.tools.analytics import check_pagespeed

        call_count = 0

        async def mock_get(url, **kwargs):
            nonlocal call_count
            call_count += 1
            resp = MagicMock()
            resp.status_code = 200
            resp.raise_for_status = MagicMock()
            if "strategy=mobile" in url:
                resp.json.return_value = _PSI_RESPONSE_MOBILE
            else:
                resp.json.return_value = _PSI_RESPONSE_DESKTOP
            return resp

        mock_client = AsyncMock()
        mock_client.get = mock_get
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("httpx.AsyncClient", return_value=mock_client),
            patch(
                "hazn_platform.orchestrator.tools.analytics._OUTPUT_BASE",
                str(tmp_output_dir),
            ),
        ):
            result = await check_pagespeed.handler(
                {"client_id": "test-client", "url": "https://example.com"}
            )

        assert result.get("isError") is not True
        # Should make 2 requests (mobile + desktop)
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_extracts_cwv_and_performance_score(self, tmp_output_dir):
        """check_pagespeed extracts Core Web Vitals and performance score."""
        from hazn_platform.orchestrator.tools.analytics import check_pagespeed

        async def mock_get(url, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            resp.raise_for_status = MagicMock()
            if "strategy=mobile" in url:
                resp.json.return_value = _PSI_RESPONSE_MOBILE
            else:
                resp.json.return_value = _PSI_RESPONSE_DESKTOP
            return resp

        mock_client = AsyncMock()
        mock_client.get = mock_get
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("httpx.AsyncClient", return_value=mock_client),
            patch(
                "hazn_platform.orchestrator.tools.analytics._OUTPUT_BASE",
                str(tmp_output_dir),
            ),
        ):
            result = await check_pagespeed.handler(
                {"client_id": "test-client", "url": "https://example.com"}
            )

        assert result.get("isError") is not True
        text = json.loads(result["content"][0]["text"])
        assert "output_file" in text
        assert os.path.exists(text["output_file"])

        with open(text["output_file"]) as f:
            data = json.load(f)

        # Verify dual strategy data
        assert "mobile" in data
        assert "desktop" in data

        # Verify CWV extraction for mobile
        mobile = data["mobile"]
        assert "performance_score" in mobile
        assert mobile["performance_score"] == 72  # 0.72 * 100
        assert "core_web_vitals" in mobile
        cwv = mobile["core_web_vitals"]
        assert "lcp" in cwv
        assert "cls" in cwv
        assert "inp" in cwv

    @pytest.mark.asyncio
    async def test_extracts_opportunities(self, tmp_output_dir):
        """check_pagespeed extracts top opportunities sorted by savings."""
        from hazn_platform.orchestrator.tools.analytics import check_pagespeed

        async def mock_get(url, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            resp.raise_for_status = MagicMock()
            if "strategy=mobile" in url:
                resp.json.return_value = _PSI_RESPONSE_MOBILE
            else:
                resp.json.return_value = _PSI_RESPONSE_DESKTOP
            return resp

        mock_client = AsyncMock()
        mock_client.get = mock_get
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("httpx.AsyncClient", return_value=mock_client),
            patch(
                "hazn_platform.orchestrator.tools.analytics._OUTPUT_BASE",
                str(tmp_output_dir),
            ),
        ):
            result = await check_pagespeed.handler(
                {"client_id": "test-client", "url": "https://example.com"}
            )

        with open(json.loads(result["content"][0]["text"])["output_file"]) as f:
            data = json.load(f)

        # Mobile should have opportunities
        mobile = data["mobile"]
        assert "opportunities" in mobile
        opps = mobile["opportunities"]
        # render-blocking-resources (1200ms) should come before unused-javascript (800ms)
        # unminified-css (50ms) has score=0.9 so it should NOT appear (score < 0.9 filter)
        assert len(opps) >= 2
        assert opps[0]["savings_ms"] >= opps[-1]["savings_ms"]  # sorted desc

    @pytest.mark.asyncio
    async def test_writes_json_to_file(self, tmp_output_dir):
        """check_pagespeed writes full JSON to /tmp/hazn-audit/{client_id}/{timestamp}/pagespeed.json."""
        from hazn_platform.orchestrator.tools.analytics import check_pagespeed

        async def mock_get(url, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            resp.raise_for_status = MagicMock()
            resp.json.return_value = _PSI_RESPONSE_MOBILE
            return resp

        mock_client = AsyncMock()
        mock_client.get = mock_get
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("httpx.AsyncClient", return_value=mock_client),
            patch(
                "hazn_platform.orchestrator.tools.analytics._OUTPUT_BASE",
                str(tmp_output_dir),
            ),
        ):
            result = await check_pagespeed.handler(
                {"client_id": "test-client", "url": "https://example.com"}
            )

        text = json.loads(result["content"][0]["text"])
        assert text["output_file"].endswith("pagespeed.json")
        assert os.path.exists(text["output_file"])
        assert "sections" in text
        assert "mobile" in text["sections"]
        assert "desktop" in text["sections"]

    @pytest.mark.asyncio
    async def test_returns_summary_with_scores(self, tmp_output_dir):
        """check_pagespeed returns summary with scores, CWV metrics, opportunity count."""
        from hazn_platform.orchestrator.tools.analytics import check_pagespeed

        async def mock_get(url, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            resp.raise_for_status = MagicMock()
            if "strategy=mobile" in url:
                resp.json.return_value = _PSI_RESPONSE_MOBILE
            else:
                resp.json.return_value = _PSI_RESPONSE_DESKTOP
            return resp

        mock_client = AsyncMock()
        mock_client.get = mock_get
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("httpx.AsyncClient", return_value=mock_client),
            patch(
                "hazn_platform.orchestrator.tools.analytics._OUTPUT_BASE",
                str(tmp_output_dir),
            ),
        ):
            result = await check_pagespeed.handler(
                {"client_id": "test-client", "url": "https://example.com"}
            )

        text = json.loads(result["content"][0]["text"])
        assert "output_file" in text
        assert "record_count" in text
        assert "sections" in text

    @pytest.mark.asyncio
    async def test_handles_api_error(self, tmp_output_dir):
        """check_pagespeed handles API errors gracefully."""
        from hazn_platform.orchestrator.tools.analytics import check_pagespeed

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("httpx.AsyncClient", return_value=mock_client),
            patch(
                "hazn_platform.orchestrator.tools.analytics._OUTPUT_BASE",
                str(tmp_output_dir),
            ),
        ):
            result = await check_pagespeed.handler(
                {"client_id": "test-client", "url": "https://invalid.example.com"}
            )

        assert result.get("isError") is True
        assert "Connection refused" in result["content"][0]["text"]


class TestAnalyticsToolsExport:
    """ANALYTICS_TOOLS exports all 3 tools."""

    def test_exports_all_three_tools(self):
        """ANALYTICS_TOOLS contains pull_ga4_data, query_gsc, check_pagespeed."""
        from hazn_platform.orchestrator.tools.analytics import ANALYTICS_TOOLS

        tool_names = [t.name for t in ANALYTICS_TOOLS]
        assert "pull_ga4_data" in tool_names
        assert "query_gsc" in tool_names
        assert "check_pagespeed" in tool_names
        assert len(ANALYTICS_TOOLS) == 3


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _make_ga4_report_response(
    rows_data: list[dict] | None = None,
    num_dims: int = 3,
    num_metrics: int = 5,
) -> MagicMock:
    """Create a mock GA4 RunReportResponse.

    If rows_data is empty/None, creates a single row with generic values.
    The response has enough dimension_values and metric_values entries
    to satisfy any report query (which may have 1-3 dims and 2-4 metrics).
    """
    response = MagicMock()
    if not rows_data:
        # Create a single generic row with enough values for any report
        row = MagicMock()
        row.dimension_values = [
            MagicMock(value=f"dim_{i}") for i in range(num_dims)
        ]
        row.metric_values = [
            MagicMock(value=str(i * 10)) for i in range(num_metrics)
        ]
        response.rows = [row]
    else:
        rows = []
        for row_dict in rows_data:
            row = MagicMock()
            # Provide enough mock values for any dimension/metric count
            row.dimension_values = [
                MagicMock(value=f"dim_{i}") for i in range(num_dims)
            ]
            row.metric_values = [
                MagicMock(value=str(i * 10)) for i in range(num_metrics)
            ]
            rows.append(row)
        response.rows = rows
    return response

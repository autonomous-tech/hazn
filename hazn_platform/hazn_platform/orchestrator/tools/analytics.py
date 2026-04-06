"""Analytics tools -- pull_ga4_data, query_gsc, check_pagespeed.

Full-depth analytics data collection tools that port and expand the legacy
MCP analytics server. Each tool fetches per-client credentials from Vault,
runs comprehensive API queries, writes the full JSON to disk, and returns
a lean summary + file path to the agent.

Output directory: /tmp/hazn-audit/{client_id}/{timestamp}/

Registered with the ToolRegistry via the module-level ``ANALYTICS_TOOLS`` list.

Requires Django ORM (VaultCredential model) and Google API client libraries.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configurable output base directory (patchable in tests)
# ---------------------------------------------------------------------------

_OUTPUT_BASE = "/tmp/hazn-audit"

# ---------------------------------------------------------------------------
# SDK tool decorator with graceful fallback
# ---------------------------------------------------------------------------

try:
    from claude_agent_sdk import tool  # type: ignore[import-untyped]
except ImportError:
    try:
        from claude_code_sdk import tool  # type: ignore[import-untyped]
    except ImportError:

        def tool(name: str, description: str, schema: dict | None = None):  # type: ignore[misc]
            """Stub @tool decorator."""

            def decorator(fn):
                class _StubTool:
                    def __init__(self):
                        self.name = name
                        self.description = description
                        self.schema = schema or {}
                        self._handler = fn

                    async def __call__(self, args: dict[str, Any]) -> dict[str, Any]:
                        return await self._handler(args)

                return _StubTool()

            return decorator


# ---------------------------------------------------------------------------
# Lazy imports for Google API clients and Django ORM
# ---------------------------------------------------------------------------
# Guarded with try/except at module level so the module can be imported
# in environments without these dependencies or Django configured.


def _import_ga4_deps():
    """Import GA4 Data API dependencies."""
    from google.analytics.data_v1beta import BetaAnalyticsDataClient  # noqa: PLC0415
    from google.analytics.data_v1beta.types import (  # noqa: PLC0415
        DateRange,
        Dimension,
        Metric,
        OrderBy,
        RunReportRequest,
    )

    return BetaAnalyticsDataClient, RunReportRequest, DateRange, Dimension, Metric, OrderBy


def _import_gsc_deps():
    """Import GSC API dependencies."""
    from googleapiclient.discovery import build  # noqa: PLC0415

    return build


# Make these available at module level for patching in tests
try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient  # noqa: E402, PLC0415
    from google.oauth2 import service_account  # noqa: E402, PLC0415
    from googleapiclient.discovery import build  # noqa: E402, PLC0415

    from hazn_platform.core.models import VaultCredential  # noqa: E402, PLC0415
    from hazn_platform.core.vault import read_secret  # noqa: E402, PLC0415
except (ImportError, Exception):
    # Guarded for import-time safety when Django is not configured.
    # These will be available in Django runtime context where tools execute.
    BetaAnalyticsDataClient = None  # type: ignore[assignment,misc]
    service_account = None  # type: ignore[assignment]
    build = None  # type: ignore[assignment]
    VaultCredential = None  # type: ignore[assignment]
    read_secret = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _get_analytics_credentials(client_id: str, service_name: str):
    """Fetch service account credentials from Vault for a client.

    Looks up VaultCredential by end_client_id + service_name, reads the
    service account JSON from Vault, and returns google-auth Credentials.
    """
    credential = VaultCredential.objects.get(
        end_client_id=client_id, service_name=service_name
    )
    sa_json = read_secret(credential.vault_secret_id)
    scopes = {
        "ga4": ["https://www.googleapis.com/auth/analytics.readonly"],
        "gsc": ["https://www.googleapis.com/auth/webmasters.readonly"],
    }
    return service_account.Credentials.from_service_account_info(
        sa_json, scopes=scopes.get(service_name, [])
    )


def _write_and_summarize(client_id: str, tool_name: str, data: dict) -> dict:
    """Write full JSON data to disk and return a lean summary.

    Writes to: {_OUTPUT_BASE}/{client_id}/{timestamp}/{tool_name}.json

    Returns summary dict with output_file, record_count, sections.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(_OUTPUT_BASE, client_id, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{tool_name}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)

    # Count total records across all sections
    record_count = 0
    for key, value in data.items():
        if isinstance(value, list):
            record_count += len(value)
        elif isinstance(value, dict):
            record_count += 1

    summary = {
        "output_file": output_path,
        "record_count": record_count,
        "sections": list(data.keys()),
    }
    return {"content": [{"type": "text", "text": json.dumps(summary)}]}


# ---------------------------------------------------------------------------
# GA4 report helper
# ---------------------------------------------------------------------------


def _run_ga4_report(
    client,
    property_id: str,
    dimensions: list[str],
    metrics: list[str],
    date_range,
    limit: int = 20,
    order_by_metric: str | None = None,
) -> list[dict]:
    """Run a single GA4 report and return rows as dicts."""
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Metric,
        OrderBy,
        RunReportRequest,
    )

    dim_objs = [Dimension(name=d) for d in dimensions]
    met_objs = [Metric(name=m) for m in metrics]

    order = []
    if order_by_metric:
        order = [
            OrderBy(
                metric=OrderBy.MetricOrderBy(metric_name=order_by_metric), desc=True
            )
        ]

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=dim_objs,
        metrics=met_objs,
        date_ranges=[date_range],
        order_bys=order,
        limit=limit,
    )
    response = client.run_report(request)

    rows = []
    for row in response.rows:
        entry = {}
        for i, dim in enumerate(dimensions):
            entry[dim] = row.dimension_values[i].value
        for i, met in enumerate(metrics):
            entry[met] = row.metric_values[i].value
        rows.append(entry)
    return rows


# ---------------------------------------------------------------------------
# GSC query helper
# ---------------------------------------------------------------------------


def _query_search_analytics(
    service,
    site_url: str,
    start_date: str,
    end_date: str,
    dimensions: list[str],
    row_limit: int = 1000,
) -> list[dict]:
    """Run a Search Analytics query and return parsed rows."""
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": dimensions,
        "rowLimit": row_limit,
    }
    response = (
        service.searchanalytics().query(siteUrl=site_url, body=body).execute()
    )

    rows = []
    for row in response.get("rows", []):
        entry = {
            "clicks": row["clicks"],
            "impressions": row["impressions"],
            "ctr": round(row["ctr"], 4),
            "position": round(row["position"], 1),
        }
        for i, dim in enumerate(dimensions):
            entry[dim] = row["keys"][i]
        rows.append(entry)
    return rows


def _detect_cannibalization(
    query_page_rows: list[dict], min_impressions: int = 10
) -> list[dict]:
    """Find queries that rank on multiple pages (keyword cannibalization)."""
    query_pages: dict[str, list[dict]] = defaultdict(list)
    for row in query_page_rows:
        if row.get("impressions", 0) >= min_impressions:
            query_pages[row.get("query", "")].append(
                {
                    "page": row.get("page", ""),
                    "clicks": row["clicks"],
                    "impressions": row["impressions"],
                    "ctr": row["ctr"],
                    "position": row["position"],
                }
            )

    cannibalization = []
    for query, pages in query_pages.items():
        if len(pages) >= 2:
            pages_sorted = sorted(
                pages, key=lambda x: x["impressions"], reverse=True
            )
            severity = "high" if len(pages) >= 3 else "medium"
            cannibalization.append(
                {
                    "query": query,
                    "page_count": len(pages),
                    "severity": severity,
                    "pages": pages_sorted,
                }
            )

    return sorted(cannibalization, key=lambda x: x["page_count"], reverse=True)


def _aggregate_weekly(daily_rows: list[dict]) -> list[dict]:
    """Roll daily GSC data into ISO weeks."""
    weeks: dict[str, dict] = defaultdict(
        lambda: {"clicks": 0, "impressions": 0, "ctr_sum": 0, "pos_sum": 0, "days": 0}
    )
    for row in daily_rows:
        date_str = row.get("date", "")
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            # Skip rows without valid date values
            continue
        iso_year, iso_week, _ = dt.isocalendar()
        week_key = f"{iso_year}-W{iso_week:02d}"
        w = weeks[week_key]
        w["clicks"] += row.get("clicks", 0)
        w["impressions"] += row.get("impressions", 0)
        w["ctr_sum"] += row.get("ctr", 0)
        w["pos_sum"] += row.get("position", 0)
        w["days"] += 1

    weekly = []
    for week_key in sorted(weeks.keys()):
        w = weeks[week_key]
        weekly.append(
            {
                "week": week_key,
                "clicks": w["clicks"],
                "impressions": w["impressions"],
                "ctr": round(w["ctr_sum"] / w["days"], 4) if w["days"] else 0,
                "avg_position": round(w["pos_sum"] / w["days"], 1) if w["days"] else 0,
                "days": w["days"],
            }
        )
    return weekly


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


@tool(
    "pull_ga4_data",
    "Collect full-depth GA4 analytics data (events, conversions, traffic sources, "
    "landing pages, devices, countries) and write to JSON file.",
    {"client_id": str, "property_id": str, "days": int},
)
async def pull_ga4_data(args: dict[str, Any]) -> dict[str, Any]:
    """Collect comprehensive GA4 data for a client property.

    Runs 6 reports via the GA4 Data API:
    1. events -- top events by count
    2. conversions -- conversion/key events
    3. traffic_sources -- sessions by source/medium
    4. landing_pages -- top landing pages by sessions
    5. devices -- sessions by device category
    6. countries -- sessions by country

    Writes full JSON to /tmp/hazn-audit/{client_id}/{timestamp}/ga4.json
    and returns a summary with file path, record count, and section names.
    """
    client_id = args["client_id"]
    property_id = args["property_id"]
    days = args.get("days", 30)

    try:
        # Get credentials from Vault
        creds = await asyncio.to_thread(
            _get_analytics_credentials, client_id, "ga4"
        )

        # Create GA4 Data API client
        ga4_client = BetaAnalyticsDataClient(credentials=creds)

        from google.analytics.data_v1beta.types import DateRange

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = DateRange(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        )

        data = {}

        # 1. Events -- top 20 events by count
        data["events"] = await asyncio.to_thread(
            _run_ga4_report,
            ga4_client,
            property_id,
            ["eventName"],
            ["eventCount", "totalUsers"],
            date_range,
            limit=20,
            order_by_metric="eventCount",
        )

        # 2. Conversions -- key events
        data["conversions"] = await asyncio.to_thread(
            _run_ga4_report,
            ga4_client,
            property_id,
            ["eventName", "isKeyEvent"],
            ["eventCount", "totalUsers"],
            date_range,
            limit=50,
        )

        # 3. Traffic sources -- sessions by source/medium
        data["traffic_sources"] = await asyncio.to_thread(
            _run_ga4_report,
            ga4_client,
            property_id,
            ["sessionSource", "sessionMedium"],
            ["sessions", "totalUsers", "engagedSessions", "engagementRate"],
            date_range,
            limit=50,
            order_by_metric="sessions",
        )

        # 4. Landing pages -- top landing pages by sessions
        data["landing_pages"] = await asyncio.to_thread(
            _run_ga4_report,
            ga4_client,
            property_id,
            ["landingPage"],
            ["sessions", "totalUsers", "engagementRate"],
            date_range,
            limit=30,
            order_by_metric="sessions",
        )

        # 5. Devices -- sessions by device category
        data["devices"] = await asyncio.to_thread(
            _run_ga4_report,
            ga4_client,
            property_id,
            ["deviceCategory"],
            ["sessions", "totalUsers", "engagementRate"],
            date_range,
        )

        # 6. Countries -- sessions by country
        data["countries"] = await asyncio.to_thread(
            _run_ga4_report,
            ga4_client,
            property_id,
            ["country"],
            ["sessions", "totalUsers", "engagementRate"],
            date_range,
            limit=20,
            order_by_metric="sessions",
        )

        # Write to file and return summary
        return await asyncio.to_thread(
            _write_and_summarize, client_id, "ga4", data
        )

    except Exception as exc:
        logger.warning("pull_ga4_data failed for client %s: %s", client_id, exc)
        return {
            "content": [
                {"type": "text", "text": f"Error collecting GA4 data: {exc}"}
            ],
            "isError": True,
        }


@tool(
    "query_gsc",
    "Collect full-depth Google Search Console data (queries, pages, brand analysis, "
    "cannibalization, weekly trends) and write to JSON file.",
    {"client_id": str, "site_url": str, "days": int},
)
async def query_gsc(args: dict[str, Any]) -> dict[str, Any]:
    """Collect comprehensive GSC data for a client site.

    Runs 5 query groups via the Search Console API:
    1. top_queries -- top 100 queries by clicks
    2. landing_pages -- top 50 pages by clicks
    3. brand_analysis -- brand vs non-brand query split
    4. cannibalization -- queries ranking on multiple pages
    5. weekly_trends -- weekly aggregated clicks/impressions

    Writes full JSON to /tmp/hazn-audit/{client_id}/{timestamp}/gsc.json
    and returns a summary with file path, record count, and section names.
    """
    client_id = args["client_id"]
    site_url = args["site_url"]
    days = args.get("days", 30)

    try:
        # Get credentials from Vault
        creds = await asyncio.to_thread(
            _get_analytics_credentials, client_id, "gsc"
        )

        # Build Search Console service
        gsc_service = build("searchconsole", "v1", credentials=creds)

        # Date range (GSC data has ~3 day lag)
        end_dt = datetime.now() - timedelta(days=3)
        start_dt = end_dt - timedelta(days=days - 1)
        start_date = start_dt.strftime("%Y-%m-%d")
        end_date = end_dt.strftime("%Y-%m-%d")

        data = {}

        # 1. Top queries -- top 100 queries by clicks
        data["top_queries"] = await asyncio.to_thread(
            _query_search_analytics,
            gsc_service,
            site_url,
            start_date,
            end_date,
            ["query"],
            row_limit=100,
        )

        # 2. Landing pages -- top 50 pages by clicks
        data["landing_pages"] = await asyncio.to_thread(
            _query_search_analytics,
            gsc_service,
            site_url,
            start_date,
            end_date,
            ["page"],
            row_limit=50,
        )

        # 3. Brand analysis -- classify queries as brand vs non-brand
        # Extract brand name from site_url domain
        brand_name = _extract_brand_from_url(site_url)
        top_queries = data["top_queries"]
        if brand_name:
            brand_pattern = re.compile(re.escape(brand_name.lower()))
            brand_queries = [
                q for q in top_queries if brand_pattern.search(q.get("query", "").lower())
            ]
            non_brand_queries = [
                q for q in top_queries if not brand_pattern.search(q.get("query", "").lower())
            ]
            brand_clicks = sum(q.get("clicks", 0) for q in brand_queries)
            non_brand_clicks = sum(q.get("clicks", 0) for q in non_brand_queries)
            total_clicks = brand_clicks + non_brand_clicks
            data["brand_analysis"] = {
                "brand_name": brand_name,
                "brand_queries": brand_queries[:50],
                "non_brand_queries": sorted(
                    non_brand_queries, key=lambda x: x.get("clicks", 0), reverse=True
                )[:50],
                "brand_clicks": brand_clicks,
                "non_brand_clicks": non_brand_clicks,
                "brand_click_share": (
                    round(brand_clicks / total_clicks, 4) if total_clicks else 0
                ),
            }
        else:
            data["brand_analysis"] = {
                "brand_name": None,
                "note": "Could not extract brand name from site_url",
            }

        # 4. Cannibalization -- queries ranking on multiple pages
        query_page_data = await asyncio.to_thread(
            _query_search_analytics,
            gsc_service,
            site_url,
            start_date,
            end_date,
            ["query", "page"],
            row_limit=1000,
        )
        data["cannibalization"] = _detect_cannibalization(query_page_data)

        # 5. Weekly trends -- daily data aggregated to weeks
        daily_data = await asyncio.to_thread(
            _query_search_analytics,
            gsc_service,
            site_url,
            start_date,
            end_date,
            ["date"],
            row_limit=days,
        )
        data["weekly_trends"] = _aggregate_weekly(daily_data)

        # Write to file and return summary
        return await asyncio.to_thread(
            _write_and_summarize, client_id, "gsc", data
        )

    except Exception as exc:
        logger.warning("query_gsc failed for client %s: %s", client_id, exc)
        return {
            "content": [
                {"type": "text", "text": f"Error collecting GSC data: {exc}"}
            ],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# URL brand extraction helper
# ---------------------------------------------------------------------------


def _extract_brand_from_url(site_url: str) -> str | None:
    """Extract a likely brand name from a GSC site_url.

    Handles both formats:
    - sc-domain:example.com -> 'example'
    - https://www.example.com/ -> 'example'
    """
    url = site_url
    if url.startswith("sc-domain:"):
        domain = url.replace("sc-domain:", "")
    else:
        # Remove protocol and www
        domain = re.sub(r"^https?://", "", url)
        domain = re.sub(r"^www\.", "", domain)
        domain = domain.rstrip("/").split("/")[0]

    # Extract the main part before TLD
    parts = domain.split(".")
    if len(parts) >= 2:
        return parts[0]
    return parts[0] if parts else None


# ---------------------------------------------------------------------------
# PageSpeed Insights helpers
# ---------------------------------------------------------------------------

_PSI_API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


def _extract_pagespeed_data(raw: dict) -> dict:
    """Extract performance score, CWV, and opportunities from a PSI response."""
    lh = raw.get("lighthouseResult", {})
    audits = lh.get("audits", {})
    categories = lh.get("categories", {})

    # Performance score (0-100)
    perf_score = categories.get("performance", {}).get("score")
    performance_score = int(perf_score * 100) if perf_score is not None else None

    # Core Web Vitals from audits
    cwv = {}
    cwv_map = {
        "largest-contentful-paint": "lcp",
        "cumulative-layout-shift": "cls",
        "interaction-to-next-paint": "inp",
        "first-input-delay": "fid",
    }
    for audit_key, short_key in cwv_map.items():
        audit = audits.get(audit_key, {})
        if audit:
            cwv[short_key] = {
                "score": audit.get("score"),
                "numeric_value": audit.get("numericValue"),
                "display_value": audit.get("displayValue"),
            }

    # Top 5 opportunities sorted by savings (only where score < 0.9)
    opportunities = []
    for audit_id, audit_data in audits.items():
        details = audit_data.get("details", {})
        if (
            details.get("type") == "opportunity"
            and audit_data.get("score", 1) < 0.9
        ):
            savings = details.get("overallSavingsMs", 0)
            if savings > 0:
                opportunities.append(
                    {
                        "id": audit_id,
                        "title": audit_data.get("title"),
                        "savings_ms": savings,
                        "display_value": audit_data.get("displayValue"),
                    }
                )
    opportunities.sort(key=lambda x: x.get("savings_ms", 0), reverse=True)

    return {
        "performance_score": performance_score,
        "core_web_vitals": cwv,
        "opportunities": opportunities[:5],
    }


# ---------------------------------------------------------------------------
# PageSpeed tool
# ---------------------------------------------------------------------------


@tool(
    "check_pagespeed",
    "Run PageSpeed Insights for both mobile and desktop, extracting Core Web Vitals, "
    "performance scores, and top optimization opportunities.",
    {"client_id": str, "url": str},
)
async def check_pagespeed(args: dict[str, Any]) -> dict[str, Any]:
    """Run PageSpeed Insights for both mobile and desktop strategies.

    For each strategy, extracts:
    - Performance score (0-100)
    - Core Web Vitals (LCP, CLS, INP/FID)
    - Top 5 optimization opportunities sorted by time savings

    Writes full JSON to /tmp/hazn-audit/{client_id}/{timestamp}/pagespeed.json
    and returns a summary with file path and section names.
    """
    import httpx  # noqa: PLC0415

    client_id = args["client_id"]
    url = args["url"]
    api_key = os.environ.get("PSI_API_KEY")

    try:
        data = {}

        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            for strategy in ["mobile", "desktop"]:
                params = f"url={url}&strategy={strategy}&category=performance"
                if api_key:
                    params += f"&key={api_key}"
                request_url = f"{_PSI_API_URL}?{params}"

                response = await client.get(request_url)
                response.raise_for_status()
                raw = response.json()
                data[strategy] = _extract_pagespeed_data(raw)

        # Write to file and return summary
        return await asyncio.to_thread(
            _write_and_summarize, client_id, "pagespeed", data
        )

    except Exception as exc:
        logger.warning("check_pagespeed failed for %s: %s", url, exc)
        return {
            "content": [
                {"type": "text", "text": f"Error checking PageSpeed for {url}: {exc}"}
            ],
            "isError": True,
        }


# ---------------------------------------------------------------------------
# Module-level tool list for registration
# ---------------------------------------------------------------------------

ANALYTICS_TOOLS = [pull_ga4_data, query_gsc, check_pagespeed]

#!/usr/bin/env python3
"""
GA4 Audit Data Collector — Primary Dataset
Queries GA4 Data API for property config, events, conversions, traffic,
campaigns, e-commerce, device, and geographic data.

Usage:
    python ga4_collector.py <property_id> <output_file> [--days 30]

Prerequisites:
    pip install google-analytics-data google-auth-oauthlib
    OAuth credentials at ~/.config/ga4-audit/credentials.json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from google.analytics.admin import AnalyticsAdminServiceClient
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Filter, FilterExpression,
    Metric, OrderBy, RunReportRequest
)
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/analytics.edit",
    "https://www.googleapis.com/auth/webmasters.readonly",
]

CONFIG_DIR = Path.home() / ".config" / "ga4-audit"
CREDS_FILE = CONFIG_DIR / "credentials.json"
TOKEN_FILE = CONFIG_DIR / "token.json"


def get_credentials():
    """Get or refresh OAuth2 credentials."""
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    # Force re-auth if token doesn't include all required scopes
    if creds and creds.scopes and not set(SCOPES).issubset(set(creds.scopes)):
        creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            if not CREDS_FILE.exists():
                print(f"ERROR: OAuth credentials not found at {CREDS_FILE}")
                print("Download from Google Cloud Console > APIs & Services > Credentials")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json())
    return creds


def run_report(client, property_id, dimensions, metrics, date_range, limit=20, order_by_metric=None):
    """Run a GA4 report and return rows as dicts."""
    dim_objs = [Dimension(name=d) for d in dimensions]
    met_objs = [Metric(name=m) for m in metrics]
    order = []
    if order_by_metric:
        order = [OrderBy(metric=OrderBy.MetricOrderBy(metric_name=order_by_metric), desc=True)]

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


def collect_all(property_id, days=30):
    """Collect all GA4 audit data."""
    creds = get_credentials()
    data_client = BetaAnalyticsDataClient(credentials=creds)
    admin_client = AnalyticsAdminServiceClient(credentials=creds)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = DateRange(
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
    )

    result = {}

    # 1. Property metadata
    print("Collecting property metadata...")
    properties = []
    for summary in admin_client.list_account_summaries():
        for prop in summary.property_summaries:
            prop_detail = admin_client.get_property(name=prop.property)
            properties.append({
                "account": summary.display_name,
                "account_id": summary.name,
                "property": prop.display_name,
                "property_id": prop.property.split("/")[-1],
                "industry": str(prop_detail.industry_category),
                "time_zone": prop_detail.time_zone,
                "currency": prop_detail.currency_code,
                "create_time": str(prop_detail.create_time),
            })
    result["properties"] = properties

    # 2. Events inventory
    print("Collecting events...")
    result["events"] = run_report(
        data_client, property_id,
        ["eventName"],
        ["eventCount", "totalUsers"],
        date_range, limit=50, order_by_metric="eventCount"
    )

    # 3. Conversions (key events)
    print("Collecting conversions...")
    result["conversions"] = run_report(
        data_client, property_id,
        ["eventName", "isKeyEvent"],
        ["eventCount", "totalUsers", "sessionsPerUser"],
        date_range, limit=50
    )

    # 4. Traffic sources
    print("Collecting traffic sources...")
    result["traffic"] = run_report(
        data_client, property_id,
        ["sessionSource", "sessionMedium"],
        ["sessions", "totalUsers", "engagedSessions", "engagementRate", "conversions"],
        date_range, limit=50, order_by_metric="sessions"
    )

    # 5. Campaign performance
    print("Collecting campaigns...")
    result["campaigns"] = run_report(
        data_client, property_id,
        ["sessionCampaignName", "sessionSource", "sessionMedium"],
        ["sessions", "totalUsers", "conversions", "engagementRate"],
        date_range, limit=50, order_by_metric="sessions"
    )

    # 6. E-commerce data
    print("Collecting e-commerce data...")
    result["ecommerce"] = run_report(
        data_client, property_id,
        ["transactionId"],
        ["ecommercePurchases", "purchaseRevenue", "totalUsers"],
        date_range, limit=50, order_by_metric="purchaseRevenue"
    )

    # 7. Landing pages
    print("Collecting landing pages...")
    result["landing_pages"] = run_report(
        data_client, property_id,
        ["landingPage"],
        ["sessions", "totalUsers", "engagementRate", "conversions"],
        date_range, limit=30, order_by_metric="sessions"
    )

    # 8. Device categories
    print("Collecting devices...")
    result["devices"] = run_report(
        data_client, property_id,
        ["deviceCategory"],
        ["sessions", "totalUsers", "engagementRate", "conversions"],
        date_range
    )

    # 9. Countries
    print("Collecting countries...")
    result["countries"] = run_report(
        data_client, property_id,
        ["country"],
        ["sessions", "totalUsers", "engagementRate"],
        date_range, limit=20, order_by_metric="sessions"
    )

    return result


def main():
    parser = argparse.ArgumentParser(description="GA4 Audit Data Collector")
    parser.add_argument("property_id", help="GA4 Property ID (numeric)")
    parser.add_argument("output_file", help="Output JSON file path")
    parser.add_argument("--days", type=int, default=30, help="Days of data to collect (default: 30)")
    args = parser.parse_args()

    data = collect_all(args.property_id, args.days)

    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2))
    print(f"Data saved to {output_path}")


if __name__ == "__main__":
    main()

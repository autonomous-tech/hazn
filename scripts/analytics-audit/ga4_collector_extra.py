#!/usr/bin/env python3
"""
GA4 Audit Data Collector — Extended Dataset
Queries GA4 Data API for engagement metrics, weekly trends, referral sources,
UTM mediums, browser distribution, event parameters, and Google Ads keyword data.

Usage:
    python ga4_collector_extra.py <property_id> <output_file> [--days 90]

Prerequisites: Same as ga4_collector.py
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, OrderBy, RunReportRequest
)

# Import shared credentials from primary collector
sys.path.insert(0, str(Path(__file__).parent))
from ga4_collector import get_credentials, run_report


def collect_extra(property_id, days=90):
    """Collect extended GA4 audit data."""
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    date_range_90d = DateRange(
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
    )
    date_range_30d = DateRange(
        start_date=(end_date - timedelta(days=30)).strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
    )

    result = {}

    # 1. Overall engagement (30d)
    print("Collecting engagement metrics...")
    request = RunReportRequest(
        property=f"properties/{property_id}",
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="newUsers"),
            Metric(name="activeUsers"),
            Metric(name="engagedSessions"),
            Metric(name="engagementRate"),
            Metric(name="bounceRate"),
            Metric(name="averageSessionDuration"),
            Metric(name="screenPageViewsPerSession"),
            Metric(name="conversions"),
            Metric(name="eventCount"),
            Metric(name="sessionsPerUser"),
            Metric(name="userEngagementDuration"),
        ],
        date_ranges=[date_range_30d],
    )
    response = client.run_report(request)
    if response.rows:
        row = response.rows[0]
        metrics_names = [
            "sessions", "totalUsers", "newUsers", "activeUsers",
            "engagedSessions", "engagementRate", "bounceRate",
            "averageSessionDuration", "screenPageViewsPerSession",
            "conversions", "eventCount", "sessionsPerUser",
            "userEngagementDuration",
        ]
        result["engagement"] = {
            name: row.metric_values[i].value
            for i, name in enumerate(metrics_names)
        }

    # 2. Weekly trends (90d)
    print("Collecting weekly trends...")
    result["weekly_trends"] = run_report(
        client, property_id,
        ["week"],
        ["sessions", "totalUsers", "conversions", "engagementRate"],
        date_range_90d, limit=52, order_by_metric="sessions"
    )

    # 3. Referral sources (30d)
    print("Collecting referrals...")
    result["referrals"] = run_report(
        client, property_id,
        ["sessionSource"],
        ["sessions", "totalUsers", "engagementRate"],
        date_range_30d, limit=30, order_by_metric="sessions"
    )

    # 4. UTM mediums (30d)
    print("Collecting UTM mediums...")
    result["utm_mediums"] = run_report(
        client, property_id,
        ["sessionMedium"],
        ["sessions"],
        date_range_30d, limit=30, order_by_metric="sessions"
    )

    # 5. New vs returning (30d)
    print("Collecting new vs returning...")
    result["new_vs_returning"] = run_report(
        client, property_id,
        ["newVsReturning"],
        ["sessions", "totalUsers", "engagementRate", "conversions"],
        date_range_30d
    )

    # 6. Browser distribution (30d)
    print("Collecting browsers...")
    result["browsers"] = run_report(
        client, property_id,
        ["browser"],
        ["sessions", "totalUsers"],
        date_range_30d, limit=10, order_by_metric="sessions"
    )

    # 7. Event parameters — contentType by event (30d)
    print("Collecting event parameters...")
    result["event_params"] = run_report(
        client, property_id,
        ["eventName", "contentType"],
        ["eventCount"],
        date_range_30d, limit=50, order_by_metric="eventCount"
    )

    # 8. Google Ads keywords (30d)
    print("Collecting Ads keywords...")
    result["ads_keywords"] = run_report(
        client, property_id,
        ["sessionGoogleAdsKeyword"],
        ["sessions", "conversions"],
        date_range_30d, limit=20, order_by_metric="sessions"
    )

    # 9. Google Ads search queries (30d)
    print("Collecting Ads queries...")
    result["ads_queries"] = run_report(
        client, property_id,
        ["sessionGoogleAdsQuery"],
        ["sessions", "conversions"],
        date_range_30d, limit=20, order_by_metric="sessions"
    )

    # 10. Engagement summary (90d)
    print("Collecting 90d engagement...")
    request = RunReportRequest(
        property=f"properties/{property_id}",
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="conversions"),
            Metric(name="engagementRate"),
            Metric(name="bounceRate"),
        ],
        date_ranges=[date_range_90d],
    )
    response = client.run_report(request)
    if response.rows:
        row = response.rows[0]
        result["engagement_90d"] = {
            "sessions": row.metric_values[0].value,
            "totalUsers": row.metric_values[1].value,
            "conversions": row.metric_values[2].value,
            "engagementRate": row.metric_values[3].value,
            "bounceRate": row.metric_values[4].value,
        }

    return result


def main():
    parser = argparse.ArgumentParser(description="GA4 Audit Extended Data Collector")
    parser.add_argument("property_id", help="GA4 Property ID (numeric)")
    parser.add_argument("output_file", help="Output JSON file path")
    parser.add_argument("--days", type=int, default=90, help="Days for trend data (default: 90)")
    args = parser.parse_args()

    data = collect_extra(args.property_id, args.days)

    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2))
    print(f"Extended data saved to {output_path}")


if __name__ == "__main__":
    main()

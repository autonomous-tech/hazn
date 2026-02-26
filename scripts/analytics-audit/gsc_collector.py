#!/usr/bin/env python3
"""
Google Search Console Audit Data Collector
Queries GSC API for organic search query data, landing pages, devices,
countries, and trend data. Post-processes for brand analysis and cannibalization detection.

Usage:
    python gsc_collector.py <site_url> <output_file> [--days 90] [--brand-terms "term1,term2"]
    python gsc_collector.py --discover   # list available GSC properties

Prerequisites:
    pip install google-api-python-client google-auth-oauthlib
    OAuth credentials at ~/.config/ga4-audit/credentials.json
    Google Search Console API enabled in Cloud Console
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta

from googleapiclient.discovery import build

# Import credentials from ga4_collector (same OAuth flow)
from ga4_collector import get_credentials


def get_service():
    """Build the Search Console API service."""
    creds = get_credentials()
    return build("searchconsole", "v1", credentials=creds)


def discover_properties(service):
    """List all available GSC properties."""
    site_list = service.sites().list().execute()
    sites = site_list.get("siteEntry", [])
    if not sites:
        print("No Search Console properties found for this account.")
        return
    print(f"\nFound {len(sites)} Search Console properties:\n")
    for site in sites:
        print(f"  {site['siteUrl']:50s}  permission: {site['permissionLevel']}")
    print()
    print("Use the siteUrl value as the <site_url> argument.")
    print("Domain properties use format: sc-domain:example.com")
    print("URL prefix properties use format: https://www.example.com/")


def query_search_analytics(service, site_url, start_date, end_date,
                           dimensions, row_limit=1000, dimension_filter=None):
    """Run a Search Analytics query and return rows."""
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": dimensions,
        "rowLimit": row_limit,
    }
    if dimension_filter:
        body["dimensionFilterGroups"] = [{"filters": dimension_filter}]

    response = service.searchanalytics().query(
        siteUrl=site_url, body=body
    ).execute()

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


def make_brand_pattern(brand_terms):
    """Build a regex pattern from brand terms list."""
    escaped = [re.escape(t.strip().lower()) for t in brand_terms if t.strip()]
    return re.compile("|".join(escaped)) if escaped else None


def classify_brand(rows, brand_pattern):
    """Split rows into brand and non-brand based on query matching."""
    brand = []
    non_brand = []
    for row in rows:
        query = row.get("query", "").lower()
        if brand_pattern and brand_pattern.search(query):
            brand.append(row)
        else:
            non_brand.append(row)
    return brand, non_brand


def detect_cannibalization(query_page_rows, min_impressions=10):
    """Find queries that map to multiple pages with meaningful impressions."""
    query_pages = defaultdict(list)
    for row in query_page_rows:
        if row["impressions"] >= min_impressions:
            query_pages[row["query"]].append({
                "page": row["page"],
                "clicks": row["clicks"],
                "impressions": row["impressions"],
                "ctr": row["ctr"],
                "position": row["position"],
            })

    cannibalization = []
    for query, pages in query_pages.items():
        if len(pages) >= 2:
            pages_sorted = sorted(pages, key=lambda x: x["impressions"], reverse=True)
            severity = "high" if len(pages) >= 3 else "medium"
            cannibalization.append({
                "query": query,
                "page_count": len(pages),
                "severity": severity,
                "pages": pages_sorted,
            })

    return sorted(cannibalization, key=lambda x: x["page_count"], reverse=True)


def aggregate_weekly(daily_rows):
    """Roll daily data into ISO weeks."""
    weeks = defaultdict(lambda: {"clicks": 0, "impressions": 0, "ctr_sum": 0, "pos_sum": 0, "days": 0})
    for row in daily_rows:
        dt = datetime.strptime(row["date"], "%Y-%m-%d")
        iso_year, iso_week, _ = dt.isocalendar()
        week_key = f"{iso_year}-W{iso_week:02d}"
        w = weeks[week_key]
        w["clicks"] += row["clicks"]
        w["impressions"] += row["impressions"]
        w["ctr_sum"] += row["ctr"]
        w["pos_sum"] += row["position"]
        w["days"] += 1

    weekly = []
    for week_key in sorted(weeks.keys()):
        w = weeks[week_key]
        weekly.append({
            "week": week_key,
            "clicks": w["clicks"],
            "impressions": w["impressions"],
            "ctr": round(w["ctr_sum"] / w["days"], 4) if w["days"] else 0,
            "avg_position": round(w["pos_sum"] / w["days"], 1) if w["days"] else 0,
            "days": w["days"],
        })
    return weekly


def compute_period_comparison(service, site_url, end_date_str, days=30):
    """Compare current period vs previous period for the same duration."""
    end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
    start_dt = end_dt - timedelta(days=days - 1)
    prev_end_dt = start_dt - timedelta(days=1)
    prev_start_dt = prev_end_dt - timedelta(days=days - 1)

    current_rows = query_search_analytics(
        service, site_url,
        start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d"),
        ["query"], row_limit=500,
    )
    previous_rows = query_search_analytics(
        service, site_url,
        prev_start_dt.strftime("%Y-%m-%d"), prev_end_dt.strftime("%Y-%m-%d"),
        ["query"], row_limit=500,
    )

    # Build lookup dicts
    current_map = {r["query"]: r for r in current_rows}
    previous_map = {r["query"]: r for r in previous_rows}

    # Aggregate totals
    current_totals = {
        "clicks": sum(r["clicks"] for r in current_rows),
        "impressions": sum(r["impressions"] for r in current_rows),
        "period": f"{start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}",
    }
    previous_totals = {
        "clicks": sum(r["clicks"] for r in previous_rows),
        "impressions": sum(r["impressions"] for r in previous_rows),
        "period": f"{prev_start_dt.strftime('%Y-%m-%d')} to {prev_end_dt.strftime('%Y-%m-%d')}",
    }

    # Find movers
    rising = []
    declining = []
    all_queries = set(current_map.keys()) | set(previous_map.keys())
    for q in all_queries:
        cur = current_map.get(q, {"clicks": 0, "impressions": 0})
        prev = previous_map.get(q, {"clicks": 0, "impressions": 0})
        click_delta = cur["clicks"] - prev["clicks"]
        imp_delta = cur["impressions"] - prev["impressions"]
        if click_delta > 5:
            rising.append({"query": q, "click_delta": click_delta, "impression_delta": imp_delta,
                           "current_clicks": cur["clicks"], "previous_clicks": prev["clicks"]})
        elif click_delta < -5:
            declining.append({"query": q, "click_delta": click_delta, "impression_delta": imp_delta,
                              "current_clicks": cur["clicks"], "previous_clicks": prev["clicks"]})

    rising.sort(key=lambda x: x["click_delta"], reverse=True)
    declining.sort(key=lambda x: x["click_delta"])

    return {
        "current": current_totals,
        "previous": previous_totals,
        "movers": {
            "rising": rising[:20],
            "declining": declining[:20],
        }
    }


def collect_all(service, site_url, days=90, brand_terms=None):
    """Collect all GSC audit data."""
    end_dt = datetime.now() - timedelta(days=3)  # GSC data has 2-3 day lag
    start_dt = end_dt - timedelta(days=days - 1)
    start_date = start_dt.strftime("%Y-%m-%d")
    end_date = end_dt.strftime("%Y-%m-%d")

    result = {
        "site_url": site_url,
        "collection_date": datetime.now().strftime("%Y-%m-%d"),
        "date_range": {"start": start_date, "end": end_date},
    }

    # 1. Top queries
    print("Collecting top queries...")
    top_queries = query_search_analytics(
        service, site_url, start_date, end_date,
        ["query"], row_limit=1000,
    )
    result["top_queries"] = top_queries

    # Summary stats
    total_clicks = sum(r["clicks"] for r in top_queries)
    total_impressions = sum(r["impressions"] for r in top_queries)
    result["summary"] = {
        "total_clicks": total_clicks,
        "total_impressions": total_impressions,
        "average_ctr": round(total_clicks / total_impressions, 4) if total_impressions else 0,
        "average_position": round(
            sum(r["position"] * r["impressions"] for r in top_queries) / total_impressions, 1
        ) if total_impressions else 0,
        "total_queries": len(top_queries),
    }

    # 2. Brand analysis
    print("Analyzing brand vs non-brand...")
    brand_pattern = make_brand_pattern(brand_terms.split(",")) if brand_terms else None
    if brand_pattern:
        brand_queries, non_brand_queries = classify_brand(top_queries, brand_pattern)
        brand_clicks = sum(r["clicks"] for r in brand_queries)
        non_brand_clicks = sum(r["clicks"] for r in non_brand_queries)
        brand_impressions = sum(r["impressions"] for r in brand_queries)
        non_brand_impressions = sum(r["impressions"] for r in non_brand_queries)
        result["brand_analysis"] = {
            "brand_terms_used": brand_terms,
            "brand_clicks": brand_clicks,
            "non_brand_clicks": non_brand_clicks,
            "brand_impressions": brand_impressions,
            "non_brand_impressions": non_brand_impressions,
            "brand_click_share": round(brand_clicks / total_clicks, 4) if total_clicks else 0,
            "brand_queries": brand_queries[:50],
            "top_non_brand_queries": sorted(non_brand_queries, key=lambda x: x["clicks"], reverse=True)[:50],
        }
    else:
        result["brand_analysis"] = {
            "brand_terms_used": None,
            "note": "No brand terms provided. Use --brand-terms to enable brand/non-brand split.",
        }

    # 3. Top landing pages
    print("Collecting top landing pages...")
    result["landing_pages"] = query_search_analytics(
        service, site_url, start_date, end_date,
        ["page"], row_limit=500,
    )

    # 4. Query x Page (for cannibalization)
    print("Collecting query x page data...")
    query_page_data = query_search_analytics(
        service, site_url, start_date, end_date,
        ["query", "page"], row_limit=2000,
    )
    result["cannibalization"] = detect_cannibalization(query_page_data)

    # 5. Device breakdown
    print("Collecting device breakdown...")
    result["devices"] = query_search_analytics(
        service, site_url, start_date, end_date,
        ["device"], row_limit=3,
    )

    # 6. Country breakdown
    print("Collecting country breakdown...")
    result["countries"] = query_search_analytics(
        service, site_url, start_date, end_date,
        ["country"], row_limit=30,
    )

    # 7. Daily data → weekly aggregation
    print("Collecting daily trends...")
    daily_data = query_search_analytics(
        service, site_url, start_date, end_date,
        ["date"], row_limit=days,
    )
    result["daily_data"] = daily_data
    result["weekly_trends"] = aggregate_weekly(daily_data)

    # 8. Search appearance
    print("Collecting search appearance data...")
    result["search_appearance"] = query_search_analytics(
        service, site_url, start_date, end_date,
        ["searchAppearance"], row_limit=20,
    )

    # 9. Page x Device
    print("Collecting page x device data...")
    result["page_device"] = query_search_analytics(
        service, site_url, start_date, end_date,
        ["page", "device"], row_limit=500,
    )

    # 10. 30-day period comparison
    print("Computing 30-day period comparison...")
    result["period_comparison"] = compute_period_comparison(
        service, site_url, end_date, days=30,
    )

    return result


def main():
    parser = argparse.ArgumentParser(description="Google Search Console Audit Data Collector")
    parser.add_argument("site_url", nargs="?", help="GSC property URL (e.g., sc-domain:example.com)")
    parser.add_argument("output_file", nargs="?", help="Output JSON file path")
    parser.add_argument("--days", type=int, default=90, help="Days of data to collect (default: 90)")
    parser.add_argument("--brand-terms", type=str, default=None,
                        help="Comma-separated brand terms for brand/non-brand split")
    parser.add_argument("--discover", action="store_true", help="List available GSC properties")
    args = parser.parse_args()

    if args.discover:
        service = get_service()
        discover_properties(service)
        return

    if not args.site_url or not args.output_file:
        parser.error("site_url and output_file are required (unless using --discover)")

    service = get_service()
    print(f"Collecting GSC data for {args.site_url} ({args.days} days)...")
    data = collect_all(service, args.site_url, days=args.days, brand_terms=args.brand_terms)

    from pathlib import Path
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2))
    print(f"\nData saved to {output_path}")
    print(f"  Queries: {data['summary']['total_queries']}")
    print(f"  Clicks:  {data['summary']['total_clicks']}")
    print(f"  Impressions: {data['summary']['total_impressions']}")
    print(f"  Avg CTR: {data['summary']['average_ctr']:.2%}")
    print(f"  Avg Position: {data['summary']['average_position']}")
    if data.get("cannibalization"):
        print(f"  Cannibalization issues: {len(data['cannibalization'])}")


if __name__ == "__main__":
    main()

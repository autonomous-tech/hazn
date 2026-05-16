#!/usr/bin/env python3
"""
PageSpeed Insights Collector — Free Public API
Calls Google PageSpeed Insights API for both mobile and desktop strategies.
Extracts Lighthouse scores, Core Web Vitals (field + lab), failed audits,
third-party script summary, and performance opportunities.

Usage:
    python pagespeed_collector.py <URL> <output_file>

No API key required (uses free tier). Optional: set PSI_API_KEY env var
for higher rate limits.
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

PSI_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


def fetch_psi(url, strategy="mobile", api_key=None):
    """Fetch PageSpeed Insights data for a URL and strategy."""
    params = {
        "url": url,
        "strategy": strategy,
        "category": ["performance", "accessibility", "best-practices", "seo"],
    }
    if api_key:
        params["key"] = api_key

    # Build URL with repeated category params
    base_params = urllib.parse.urlencode(
        {k: v for k, v in params.items() if k != "category"}
    )
    cat_params = "&".join(f"category={c}" for c in params["category"])
    request_url = f"{PSI_API}?{base_params}&{cat_params}"

    print(f"  Fetching {strategy} data for {url}...")
    req = urllib.request.Request(request_url)
    req.add_header("User-Agent", "AnalyticsAuditAgent/1.0")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"  ERROR: PSI API returned {e.code} for {strategy}: {body[:200]}")
        return None
    except urllib.error.URLError as e:
        print(f"  ERROR: Could not reach PSI API: {e.reason}")
        return None


def extract_cwv(data):
    """Extract Core Web Vitals from field data (CrUX)."""
    metrics = data.get("loadingExperience", {}).get("metrics", {})
    if not metrics:
        return None

    result = {}
    cwv_map = {
        "LARGEST_CONTENTFUL_PAINT_MS": "lcp",
        "FIRST_INPUT_DELAY_MS": "fid",
        "INTERACTION_TO_NEXT_PAINT": "inp",
        "CUMULATIVE_LAYOUT_SHIFT_SCORE": "cls",
        "FIRST_CONTENTFUL_PAINT_MS": "fcp",
        "EXPERIMENTAL_TIME_TO_FIRST_BYTE": "ttfb",
    }

    for api_key, short_key in cwv_map.items():
        metric = metrics.get(api_key)
        if metric:
            result[short_key] = {
                "percentile": metric.get("percentile"),
                "category": metric.get("category"),
                "distributions": metric.get("distributions"),
            }

    overall = data.get("loadingExperience", {}).get("overall_category")
    if overall:
        result["overall_category"] = overall

    return result if result else None


def extract_lighthouse(data):
    """Extract Lighthouse audit results."""
    lh = data.get("lighthouseResult", {})
    if not lh:
        return None

    # Category scores
    categories = {}
    for cat_id, cat_data in lh.get("categories", {}).items():
        categories[cat_id] = {
            "score": cat_data.get("score"),
            "title": cat_data.get("title"),
        }

    # Lab metrics
    audits = lh.get("audits", {})
    lab_metrics = {}
    metric_keys = [
        "first-contentful-paint", "largest-contentful-paint",
        "total-blocking-time", "cumulative-layout-shift",
        "speed-index", "interactive", "server-response-time",
    ]
    for key in metric_keys:
        audit = audits.get(key, {})
        if audit:
            lab_metrics[key] = {
                "display_value": audit.get("displayValue"),
                "score": audit.get("score"),
                "numeric_value": audit.get("numericValue"),
            }

    # Failed audits (score < 0.9)
    failed_audits = []
    for audit_id, audit_data in audits.items():
        score = audit_data.get("score")
        if score is not None and score < 0.9 and audit_data.get("title"):
            failed_audits.append({
                "id": audit_id,
                "title": audit_data["title"],
                "score": score,
                "display_value": audit_data.get("displayValue"),
                "description": audit_data.get("description", "")[:200],
            })
    failed_audits.sort(key=lambda x: x.get("score") or 0)

    # Performance opportunities
    opportunities = []
    for audit_id, audit_data in audits.items():
        details = audit_data.get("details", {})
        if details.get("type") == "opportunity" and audit_data.get("score", 1) < 0.9:
            savings = details.get("overallSavingsMs", 0)
            if savings > 0:
                opportunities.append({
                    "id": audit_id,
                    "title": audit_data.get("title"),
                    "savings_ms": savings,
                    "savings_bytes": details.get("overallSavingsBytes", 0),
                    "display_value": audit_data.get("displayValue"),
                })
    opportunities.sort(key=lambda x: x.get("savings_ms", 0), reverse=True)

    # Third-party summary
    third_party = audits.get("third-party-summary", {})
    tp_data = None
    if third_party.get("details", {}).get("items"):
        items = third_party["details"]["items"]
        tp_data = {
            "total_count": len(items),
            "total_blocking_time": third_party.get("details", {}).get(
                "summary", {}
            ).get("wastedMs", 0),
            "total_transfer_size": third_party.get("details", {}).get(
                "summary", {}
            ).get("wastedBytes", 0),
            "items": [
                {
                    "entity": item.get("entity", "Unknown"),
                    "transfer_size": item.get("transferSize", 0),
                    "blocking_time": item.get("blockingTime", 0),
                    "main_thread_time": item.get("mainThreadTime", 0),
                }
                for item in items[:20]
            ],
        }

    # Diagnostics
    diagnostics = []
    diag_keys = [
        "dom-size", "bootup-time", "mainthread-work-breakdown",
        "font-display", "uses-passive-event-listeners",
        "no-document-write", "uses-http2",
    ]
    for key in diag_keys:
        audit = audits.get(key, {})
        if audit and audit.get("score") is not None and audit["score"] < 0.9:
            diagnostics.append({
                "id": key,
                "title": audit.get("title"),
                "display_value": audit.get("displayValue"),
                "score": audit.get("score"),
            })

    # Page weight
    resource_summary = audits.get("resource-summary", {})
    page_weight = None
    if resource_summary.get("details", {}).get("items"):
        page_weight = {
            "items": [
                {
                    "resource_type": item.get("resourceType"),
                    "request_count": item.get("requestCount"),
                    "transfer_size": item.get("transferSize"),
                }
                for item in resource_summary["details"]["items"]
            ]
        }

    return {
        "categories": categories,
        "lab_metrics": lab_metrics,
        "failed_audits": failed_audits[:15],
        "opportunities": opportunities[:10],
        "third_party": tp_data,
        "diagnostics": diagnostics,
        "page_weight": page_weight,
        "lighthouse_version": lh.get("lighthouseVersion"),
        "fetch_time": lh.get("fetchTime"),
        "final_url": lh.get("finalDisplayedUrl") or lh.get("finalUrl"),
    }


def collect(url, api_key=None):
    """Collect PageSpeed data for both mobile and desktop."""
    result = {
        "url": url,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "mobile": {},
        "desktop": {},
    }

    for strategy in ["mobile", "desktop"]:
        raw = fetch_psi(url, strategy, api_key)
        if not raw:
            result[strategy] = {"error": f"Failed to fetch {strategy} data"}
            continue

        cwv = extract_cwv(raw)
        lighthouse = extract_lighthouse(raw)

        result[strategy] = {
            "core_web_vitals": cwv,
            "lighthouse": lighthouse,
        }

    return result


def main():
    parser = argparse.ArgumentParser(description="PageSpeed Insights Collector")
    parser.add_argument("url", help="URL to analyze")
    parser.add_argument("output_file", help="Output JSON file path")
    args = parser.parse_args()

    import os
    api_key = os.environ.get("PSI_API_KEY")

    url = args.url
    if not url.startswith("http"):
        url = f"https://{url}"

    print(f"PageSpeed Insights Collector")
    print(f"URL: {url}")
    print()

    data = collect(url, api_key)

    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2))

    # Summary
    for strategy in ["mobile", "desktop"]:
        s = data[strategy]
        if "error" in s:
            print(f"  {strategy}: {s['error']}")
        elif s.get("lighthouse", {}).get("categories"):
            cats = s["lighthouse"]["categories"]
            scores = {k: int((v.get("score") or 0) * 100) for k, v in cats.items()}
            print(f"  {strategy}: Perf={scores.get('performance', '?')} "
                  f"A11y={scores.get('accessibility', '?')} "
                  f"BP={scores.get('best-practices', '?')} "
                  f"SEO={scores.get('seo', '?')}")

    print(f"\nData saved to {output_path}")


if __name__ == "__main__":
    main()

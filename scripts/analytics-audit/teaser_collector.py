#!/usr/bin/env python3
"""
Teaser Data Collector — Public Data Omnibus
Collects all publicly available data about a website without requiring
any API keys or authentication:
  - robots.txt parsing (crawl rules, AI crawler blocks)
  - sitemap.xml analysis (URL count, lastmod freshness)
  - Security headers (HSTS, CSP, X-Frame-Options, etc.)
  - SSL certificate info (issuer, expiry, grade)
  - Technology stack detection (CMS, framework, hosting/CDN)
  - Redirect chain recording
  - DNS info

Usage:
    python teaser_collector.py <URL> <output_file>
"""

import argparse
import json
import re
import socket
import ssl
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree


def normalize_url(url):
    """Ensure URL has https:// scheme."""
    if not url.startswith("http"):
        url = f"https://{url}"
    return url.rstrip("/")


def fetch_url(url, timeout=15, follow_redirects=True):
    """Fetch a URL and return (response_body, headers, status_code, redirect_chain)."""
    redirect_chain = []
    current_url = url
    max_redirects = 10

    for _ in range(max_redirects):
        req = urllib.request.Request(current_url)
        req.add_header("User-Agent", "Mozilla/5.0 (compatible; AnalyticsAuditBot/1.0)")

        try:
            opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
            resp = opener.open(req, timeout=timeout)
            body = resp.read().decode("utf-8", errors="replace")
            return body, dict(resp.headers), resp.status, redirect_chain
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 307, 308) and follow_redirects:
                location = e.headers.get("Location", "")
                if location:
                    redirect_chain.append({
                        "from": current_url,
                        "to": location,
                        "status": e.code,
                    })
                    current_url = urllib.parse.urljoin(current_url, location)
                    continue
            body = e.read().decode("utf-8", errors="replace") if e.fp else ""
            return body, dict(e.headers) if e.headers else {}, e.code, redirect_chain
        except urllib.error.URLError as e:
            return None, {}, 0, redirect_chain
        except Exception as e:
            return None, {}, 0, redirect_chain

    return None, {}, 0, redirect_chain


def fetch_simple(url, timeout=15):
    """Simple fetch returning just the body text, or None on failure."""
    body, _, status, _ = fetch_url(url, timeout)
    if status == 200 and body:
        return body
    return None


# --- Robots.txt ---

def analyze_robots(base_url):
    """Fetch and analyze robots.txt."""
    robots_url = f"{base_url}/robots.txt"
    body = fetch_simple(robots_url)
    if not body:
        return {"found": False, "url": robots_url}

    lines = body.strip().split("\n")
    result = {
        "found": True,
        "url": robots_url,
        "user_agents": [],
        "sitemaps": [],
        "disallow_rules": [],
        "allow_rules": [],
        "ai_crawler_blocks": [],
        "line_count": len(lines),
    }

    ai_crawlers = [
        "GPTBot", "ChatGPT-User", "Google-Extended", "CCBot",
        "anthropic-ai", "ClaudeBot", "Claude-Web", "Bytespider",
        "Amazonbot", "PerplexityBot", "YouBot", "Applebot-Extended",
        "cohere-ai", "FacebookBot", "Meta-ExternalAgent",
    ]
    ai_crawler_lower = {c.lower(): c for c in ai_crawlers}

    current_agent = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line.lower().startswith("user-agent:"):
            agent = line.split(":", 1)[1].strip()
            current_agent = agent
            if agent not in result["user_agents"]:
                result["user_agents"].append(agent)
        elif line.lower().startswith("disallow:"):
            path = line.split(":", 1)[1].strip()
            if path:
                result["disallow_rules"].append({
                    "agent": current_agent or "*",
                    "path": path,
                })
                if current_agent and current_agent.lower() in ai_crawler_lower:
                    result["ai_crawler_blocks"].append({
                        "crawler": ai_crawler_lower[current_agent.lower()],
                        "rule": f"Disallow: {path}",
                    })
        elif line.lower().startswith("allow:"):
            path = line.split(":", 1)[1].strip()
            if path:
                result["allow_rules"].append({
                    "agent": current_agent or "*",
                    "path": path,
                })
        elif line.lower().startswith("sitemap:"):
            sitemap_url = line.split(":", 1)[1].strip()
            # Re-join in case ":" was in the URL
            if not sitemap_url.startswith("http"):
                sitemap_url = line.split(" ", 1)[1].strip() if " " in line else ""
            if sitemap_url:
                result["sitemaps"].append(sitemap_url)

    # Check if AI crawlers are blocked via wildcard
    wildcard_disallows = [
        r["path"] for r in result["disallow_rules"] if r["agent"] == "*"
    ]
    if "/" in wildcard_disallows:
        result["ai_crawler_blocks"].append({
            "crawler": "ALL (via User-agent: *)",
            "rule": "Disallow: /",
        })

    return result


# --- Sitemap ---

def analyze_sitemap(base_url, robots_sitemaps=None):
    """Fetch and analyze sitemap.xml."""
    sitemap_urls = robots_sitemaps or []
    if not sitemap_urls:
        sitemap_urls = [f"{base_url}/sitemap.xml"]

    result = {
        "found": False,
        "sitemap_urls": sitemap_urls,
        "total_urls": 0,
        "url_samples": [],
        "lastmod_newest": None,
        "lastmod_oldest": None,
        "has_lastmod": False,
        "sub_sitemaps": [],
    }

    all_urls = []
    lastmods = []

    for sm_url in sitemap_urls[:5]:  # Limit to 5 sitemaps
        body = fetch_simple(sm_url)
        if not body:
            continue

        result["found"] = True

        try:
            root = ElementTree.fromstring(body)
        except ElementTree.ParseError:
            # Try to extract URLs with regex as fallback
            locs = re.findall(r"<loc>(.*?)</loc>", body)
            all_urls.extend(locs[:500])
            continue

        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        # Check if this is a sitemap index
        sub_sitemaps = root.findall(".//sm:sitemap", ns) or root.findall(
            ".//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap"
        )
        if sub_sitemaps:
            for sub in sub_sitemaps:
                loc = sub.find("sm:loc", ns)
                if loc is None:
                    loc = sub.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
                if loc is not None and loc.text:
                    result["sub_sitemaps"].append(loc.text)
            # Recurse into first 3 sub-sitemaps
            for sub_url in result["sub_sitemaps"][:3]:
                sub_body = fetch_simple(sub_url)
                if not sub_body:
                    continue
                try:
                    sub_root = ElementTree.fromstring(sub_body)
                    for url_el in sub_root.findall(".//sm:url", ns) or sub_root.findall(
                        ".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"
                    ):
                        loc = url_el.find("sm:loc", ns)
                        if loc is None:
                            loc = url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
                        if loc is not None and loc.text:
                            all_urls.append(loc.text)
                        lastmod = url_el.find("sm:lastmod", ns)
                        if lastmod is None:
                            lastmod = url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
                        if lastmod is not None and lastmod.text:
                            lastmods.append(lastmod.text)
                except ElementTree.ParseError:
                    pass
            continue

        # Regular sitemap
        for url_el in root.findall(".//sm:url", ns) or root.findall(
            ".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"
        ):
            loc = url_el.find("sm:loc", ns)
            if loc is None:
                loc = url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            if loc is not None and loc.text:
                all_urls.append(loc.text)
            lastmod = url_el.find("sm:lastmod", ns)
            if lastmod is None:
                lastmod = url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
            if lastmod is not None and lastmod.text:
                lastmods.append(lastmod.text)

    result["total_urls"] = len(all_urls)
    result["url_samples"] = all_urls[:10]
    result["has_lastmod"] = len(lastmods) > 0

    if lastmods:
        sorted_mods = sorted(lastmods)
        result["lastmod_newest"] = sorted_mods[-1]
        result["lastmod_oldest"] = sorted_mods[0]

    return result


# --- Security Headers ---

def analyze_security_headers(base_url):
    """Analyze HTTP security headers."""
    _, headers, status, redirect_chain = fetch_url(base_url)
    if not headers:
        return {"error": "Could not fetch headers", "redirect_chain": redirect_chain}

    # Normalize header keys to lowercase
    h = {k.lower(): v for k, v in headers.items()}

    checks = {
        "strict-transport-security": {
            "present": "strict-transport-security" in h,
            "value": h.get("strict-transport-security"),
            "has_max_age": False,
            "has_includesubdomains": False,
            "has_preload": False,
        },
        "content-security-policy": {
            "present": "content-security-policy" in h,
            "value": (h.get("content-security-policy") or "")[:500],
        },
        "x-frame-options": {
            "present": "x-frame-options" in h,
            "value": h.get("x-frame-options"),
        },
        "x-content-type-options": {
            "present": "x-content-type-options" in h,
            "value": h.get("x-content-type-options"),
        },
        "referrer-policy": {
            "present": "referrer-policy" in h,
            "value": h.get("referrer-policy"),
        },
        "permissions-policy": {
            "present": "permissions-policy" in h or "feature-policy" in h,
            "value": (h.get("permissions-policy") or h.get("feature-policy") or "")[:500],
        },
        "x-xss-protection": {
            "present": "x-xss-protection" in h,
            "value": h.get("x-xss-protection"),
        },
        "cross-origin-opener-policy": {
            "present": "cross-origin-opener-policy" in h,
            "value": h.get("cross-origin-opener-policy"),
        },
        "cross-origin-embedder-policy": {
            "present": "cross-origin-embedder-policy" in h,
            "value": h.get("cross-origin-embedder-policy"),
        },
    }

    # HSTS details
    hsts = h.get("strict-transport-security", "")
    if hsts:
        checks["strict-transport-security"]["has_max_age"] = "max-age" in hsts.lower()
        checks["strict-transport-security"]["has_includesubdomains"] = (
            "includesubdomains" in hsts.lower()
        )
        checks["strict-transport-security"]["has_preload"] = "preload" in hsts.lower()

    # Grade calculation
    score = 0
    max_score = 9
    for key, check in checks.items():
        if check["present"]:
            score += 1

    if score >= 7:
        grade = "A"
    elif score >= 5:
        grade = "B"
    elif score >= 3:
        grade = "C"
    elif score >= 1:
        grade = "D"
    else:
        grade = "F"

    return {
        "status_code": status,
        "headers": checks,
        "score": score,
        "max_score": max_score,
        "grade": grade,
        "server": h.get("server"),
        "x_powered_by": h.get("x-powered-by"),
        "redirect_chain": redirect_chain,
        "all_headers": {k: v for k, v in h.items() if not k.startswith("set-cookie")},
    }


# --- SSL Certificate ---

def analyze_ssl(hostname):
    """Analyze SSL certificate."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                protocol = ssock.version()

        subject = dict(x[0] for x in cert.get("subject", []))
        issuer = dict(x[0] for x in cert.get("issuer", []))
        not_after = cert.get("notAfter", "")
        not_before = cert.get("notBefore", "")

        # Parse expiry
        days_until_expiry = None
        if not_after:
            try:
                expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                days_until_expiry = (expiry - datetime.now(timezone.utc).replace(tzinfo=None)).days
            except ValueError:
                pass

        # SANs
        sans = []
        for san_type, san_value in cert.get("subjectAltName", []):
            if san_type == "DNS":
                sans.append(san_value)

        return {
            "valid": True,
            "subject": subject.get("commonName"),
            "issuer_org": issuer.get("organizationName"),
            "issuer_cn": issuer.get("commonName"),
            "not_before": not_before,
            "not_after": not_after,
            "days_until_expiry": days_until_expiry,
            "sans": sans[:10],
            "protocol": protocol,
            "cipher": cipher[0] if cipher else None,
            "cipher_bits": cipher[2] if cipher and len(cipher) > 2 else None,
        }
    except ssl.SSLError as e:
        return {"valid": False, "error": f"SSL error: {str(e)}"}
    except socket.error as e:
        return {"valid": False, "error": f"Connection error: {str(e)}"}
    except Exception as e:
        return {"valid": False, "error": str(e)}


# --- Technology Detection ---

def detect_technology(base_url, headers, body):
    """Detect CMS, framework, hosting, and CDN from headers and HTML."""
    if not body:
        body = ""
    if not headers:
        headers = {}

    h = {k.lower(): v for k, v in headers.items()}
    tech = {
        "cms": None,
        "framework": None,
        "hosting": None,
        "cdn": None,
        "server": h.get("server"),
        "signals": [],
    }

    # CMS detection
    cms_patterns = [
        (r'<meta name="generator" content="WordPress', "WordPress"),
        (r"wp-content/", "WordPress"),
        (r"wp-includes/", "WordPress"),
        (r"Shopify\.theme", "Shopify"),
        (r"cdn\.shopify\.com", "Shopify"),
        (r"myshopify\.com", "Shopify"),
        (r'<meta name="generator" content="Drupal', "Drupal"),
        (r"/sites/default/files", "Drupal"),
        (r'<meta name="generator" content="Joomla', "Joomla"),
        (r"Squarespace", "Squarespace"),
        (r"static1\.squarespace\.com", "Squarespace"),
        (r"Wix\.com", "Wix"),
        (r"wixsite\.com", "Wix"),
        (r"static\.wixstatic\.com", "Wix"),
        (r"Webflow", "Webflow"),
        (r"assets\.website-files\.com", "Webflow"),
        (r"GhostContentAPI", "Ghost"),
        (r'<meta name="generator" content="Hugo', "Hugo"),
        (r"payload", "Payload CMS"),
        (r"next/static", "Next.js"),
        (r"__next", "Next.js"),
        (r"_next/static", "Next.js"),
        (r"gatsby", "Gatsby"),
        (r"Framer", "Framer"),
    ]

    for pattern, name in cms_patterns:
        if re.search(pattern, body, re.IGNORECASE):
            if not tech["cms"]:
                tech["cms"] = name
            tech["signals"].append(f"CMS: {name} (HTML pattern)")

    # Framework detection
    fw_patterns = [
        (r"__next", "Next.js"),
        (r"_next/", "Next.js"),
        (r'id="__nuxt"', "Nuxt.js"),
        (r"_nuxt/", "Nuxt.js"),
        (r"ng-version", "Angular"),
        (r"react", "React"),
        (r"__vue", "Vue.js"),
        (r"svelte", "SvelteKit"),
        (r"astro", "Astro"),
    ]

    for pattern, name in fw_patterns:
        if re.search(pattern, body, re.IGNORECASE):
            if not tech["framework"]:
                tech["framework"] = name
            tech["signals"].append(f"Framework: {name}")

    # CDN detection
    cdn_signals = {
        "cloudflare": "Cloudflare",
        "akamai": "Akamai",
        "fastly": "Fastly",
        "cloudfront": "CloudFront (AWS)",
        "vercel": "Vercel",
        "netlify": "Netlify",
        "x-vercel": "Vercel",
        "x-nf-": "Netlify",
    }

    for key, cdn_name in cdn_signals.items():
        for header_key, header_val in h.items():
            if key in header_key.lower() or key in str(header_val).lower():
                tech["cdn"] = cdn_name
                tech["signals"].append(f"CDN: {cdn_name} (header: {header_key})")
                break

    # Also check body for CDN patterns
    if not tech["cdn"]:
        cdn_body_patterns = [
            (r"cdn\.cloudflare\.com", "Cloudflare"),
            (r"cloudflareinsights", "Cloudflare"),
            (r"vercel\.app", "Vercel"),
        ]
        for pattern, name in cdn_body_patterns:
            if re.search(pattern, body, re.IGNORECASE):
                tech["cdn"] = name
                tech["signals"].append(f"CDN: {name} (body pattern)")
                break

    # Hosting detection from headers/server
    server = h.get("server", "").lower()
    if "nginx" in server:
        tech["hosting"] = tech["hosting"] or "Nginx"
    elif "apache" in server:
        tech["hosting"] = tech["hosting"] or "Apache"
    elif "cloudflare" in server:
        tech["hosting"] = "Cloudflare"
    elif "vercel" in server:
        tech["hosting"] = "Vercel"
    elif "netlify" in server:
        tech["hosting"] = "Netlify"

    if h.get("x-powered-by"):
        tech["signals"].append(f"X-Powered-By: {h['x-powered-by']}")

    return tech


# --- DNS ---

def check_dns(hostname):
    """Basic DNS resolution check."""
    try:
        ips = socket.getaddrinfo(hostname, None)
        ipv4 = list(set(addr[4][0] for addr in ips if addr[0] == socket.AF_INET))
        ipv6 = list(set(addr[4][0] for addr in ips if addr[0] == socket.AF_INET6))
        return {"resolved": True, "ipv4": ipv4[:5], "ipv6": ipv6[:5]}
    except socket.gaierror:
        return {"resolved": False}


# --- Main ---

def collect(url):
    """Collect all public data for a URL."""
    base_url = normalize_url(url)
    parsed = urllib.parse.urlparse(base_url)
    hostname = parsed.hostname

    print(f"Teaser Collector")
    print(f"URL: {base_url}")
    print(f"Host: {hostname}")
    print()

    result = {
        "url": base_url,
        "hostname": hostname,
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }

    # Fetch main page for tech detection
    print("  Fetching main page...")
    body, headers, status, redirect_chain = fetch_url(base_url)
    result["main_page"] = {
        "status": status,
        "redirect_chain": redirect_chain,
    }

    print("  Analyzing robots.txt...")
    result["robots"] = analyze_robots(base_url)

    print("  Analyzing sitemap...")
    robots_sitemaps = result["robots"].get("sitemaps", []) if result["robots"].get("found") else None
    result["sitemap"] = analyze_sitemap(base_url, robots_sitemaps)

    print("  Checking security headers...")
    result["security"] = analyze_security_headers(base_url)

    print("  Checking SSL certificate...")
    result["ssl"] = analyze_ssl(hostname)

    print("  Detecting technology stack...")
    result["technology"] = detect_technology(base_url, headers, body)

    print("  Resolving DNS...")
    result["dns"] = check_dns(hostname)

    return result


def main():
    parser = argparse.ArgumentParser(description="Teaser Data Collector")
    parser.add_argument("url", help="URL to analyze")
    parser.add_argument("output_file", help="Output JSON file path")
    args = parser.parse_args()

    data = collect(args.url)

    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2))

    # Summary
    print()
    print(f"  Robots: {'Found' if data['robots']['found'] else 'Not found'}")
    if data["robots"].get("ai_crawler_blocks"):
        print(f"    AI crawler blocks: {len(data['robots']['ai_crawler_blocks'])}")
    print(f"  Sitemap: {data['sitemap']['total_urls']} URLs")
    print(f"  Security grade: {data['security'].get('grade', 'N/A')}")
    print(f"  SSL: {'Valid' if data['ssl'].get('valid') else 'INVALID'}"
          f" (expires in {data['ssl'].get('days_until_expiry', '?')} days)")
    print(f"  Technology: CMS={data['technology'].get('cms', 'Unknown')}"
          f" CDN={data['technology'].get('cdn', 'Unknown')}")
    print(f"\nData saved to {output_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
giveaway_analysis.py — Analyse Instagram giveaway comments via Meta Graph API.

Fetches all comments from one or more IG posts, counts @mentions per commenter,
and outputs a ranked leaderboard. Does NOT require instagrapi or IG credentials —
only the Meta Page Access Token.

Usage:
    # Single post
    python3 giveaway_analysis.py --post https://www.instagram.com/p/XXXX/

    # Multiple posts (aggregated — useful for giveaways with hype posts)
    python3 giveaway_analysis.py \\
        --post https://www.instagram.com/p/XXXX/ \\
        --post https://www.instagram.com/p/YYYY/ \\
        --post https://www.instagram.com/p/ZZZZ/

    # With custom output file
    python3 giveaway_analysis.py --post https://www.instagram.com/p/XXXX/ --output results.json

Required env vars (from .env.meta):
    META_PAGE_TOKEN    - Long-lived Page Access Token
    META_API_VERSION   - e.g. v21.0  (default: v21.0)

How to load credentials:
    source .env.meta && python3 scripts/giveaway/giveaway_analysis.py --post <URL>
"""

import json
import os
import re
import sys
import argparse
import urllib.request
import urllib.error
from collections import defaultdict

# ─── Credentials ─────────────────────────────────────────────────────────────
def load_env(dotenv_path: str = ".env.meta") -> dict:
    env = {}
    try:
        with open(dotenv_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return env

_env = load_env()
TOKEN   = os.getenv("META_PAGE_TOKEN", _env.get("META_PAGE_TOKEN", ""))
API_VER = os.getenv("META_API_VERSION", _env.get("META_API_VERSION", "v21.0"))

if not TOKEN:
    print("❌ META_PAGE_TOKEN not set. Source .env.meta or set the env var.", file=sys.stderr)
    sys.exit(1)

# ─── Helpers ─────────────────────────────────────────────────────────────────
def extract_media_id_from_url(post_url: str) -> str:
    """
    Extract the IG media shortcode from a post URL, then resolve to numeric ID.
    URL format: https://www.instagram.com/p/{shortcode}/
    Uses the oEmbed endpoint (no auth required) to resolve shortcode → media ID.
    """
    # Try to extract shortcode
    match = re.search(r"/p/([A-Za-z0-9_-]+)", post_url)
    if not match:
        print(f"❌ Could not parse Instagram post URL: {post_url}", file=sys.stderr)
        sys.exit(1)
    shortcode = match.group(1)

    # Use IG oEmbed to get media ID (requires token since 2020)
    oembed_url = (
        f"https://graph.facebook.com/{API_VER}/instagram_oembed"
        f"?url=https://www.instagram.com/p/{shortcode}/"
        f"&access_token={TOKEN}"
    )
    try:
        with urllib.request.urlopen(oembed_url) as r:
            data = json.loads(r.read())
        # oEmbed gives us the media ID via media_id field
        if "media_id" in data:
            return data["media_id"]
    except Exception:
        pass

    # Fallback: try using the shortcode directly (works for some API versions)
    # The IG Graph API accepts the shortcode as an alias for the media ID in some contexts
    # If oEmbed fails, we'll try and let the comments endpoint handle it
    print(f"⚠️  Could not resolve media ID via oEmbed for {post_url}.", file=sys.stderr)
    print("    Tip: You can also pass the numeric media ID directly with --media-id.", file=sys.stderr)
    return shortcode


def fetch_all_comments(media_id: str, label: str = "") -> list:
    """Fetch all comments for a media ID, paginating through all pages."""
    all_comments = []
    url = (
        f"https://graph.facebook.com/{API_VER}/{media_id}/comments"
        f"?fields=username,text,timestamp&limit=100&access_token={TOKEN}"
    )
    page = 0
    while url:
        page += 1
        try:
            with urllib.request.urlopen(url) as r:
                data = json.loads(r.read())
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            print(f"  ❌ HTTP {e.code} fetching comments: {err_body}", file=sys.stderr)
            break
        except Exception as e:
            print(f"  ❌ Error fetching page {page}: {e}", file=sys.stderr)
            break

        comments = data.get("data", [])
        all_comments.extend(comments)
        url = data.get("paging", {}).get("next")
        if url:
            print(f"  ... page {page}: {len(all_comments)} comments so far", end="\r")

    tag_label = f" [{label}]" if label else ""
    print(f"  ✅{tag_label} {len(all_comments)} comments fetched from media {media_id}")
    return all_comments


def extract_mentions(text: str) -> list:
    """Extract @usernames from comment text."""
    return [m.lower() for m in re.findall(r"@([\w.]+)", text)]


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Analyse Instagram giveaway comments and count @tags per user."
    )
    parser.add_argument(
        "--post", action="append", dest="post_urls", metavar="URL",
        help="Instagram post URL (repeat for multiple posts)"
    )
    parser.add_argument(
        "--media-id", action="append", dest="media_ids", metavar="ID",
        help="Numeric IG media ID (alternative to --post URL)"
    )
    parser.add_argument(
        "--top", type=int, default=20,
        help="Number of top taggers to display (default: 20)"
    )
    parser.add_argument(
        "--output", metavar="FILE",
        help="Save leaderboard JSON to this file"
    )
    args = parser.parse_args()

    posts = []  # list of (media_id, label)

    if args.post_urls:
        for url in args.post_urls:
            media_id = extract_media_id_from_url(url)
            posts.append((media_id, url))

    if args.media_ids:
        for mid in args.media_ids:
            posts.append((mid, f"media:{mid}"))

    if not posts:
        parser.print_help()
        sys.exit(1)

    print(f"\n🎯 Giveaway Analysis — {len(posts)} post(s)")
    print("=" * 60)

    combined_tags  = defaultdict(set)   # username → set of unique tags
    combined_count = defaultdict(int)   # username → total comments
    total_comments = 0

    for media_id, label in posts:
        print(f"\n📥 Fetching: {label}")
        comments = fetch_all_comments(media_id, label=label)
        total_comments += len(comments)

        post_tags = defaultdict(int)
        for c in comments:
            username = c.get("username", "").lower()
            text = c.get("text", "")
            mentions = extract_mentions(text)
            if username:
                combined_tags[username].update(mentions)
                combined_count[username] += 1
                post_tags[username] += len(mentions)

        # Post-level top 3
        top3 = sorted(post_tags.items(), key=lambda x: -x[1])[:3]
        top3_str = ", ".join([f"@{u}({n})" for u, n in top3]) if top3 else "none"
        print(f"  Post top taggers: {top3_str}")

    print()
    print(f"📊 SUMMARY")
    print(f"   Total comments analysed: {total_comments:,}")
    print(f"   Unique commenters:       {len(combined_tags):,}")
    print()

    # Build ranked leaderboard
    leaderboard = sorted(
        [
            {
                "rank": 0,
                "username": username,
                "unique_tags": len(tags),
                "total_comments": combined_count[username],
                "tagged_users": sorted(tags),
            }
            for username, tags in combined_tags.items()
        ],
        key=lambda x: (-x["unique_tags"], -x["total_comments"])
    )
    for i, entry in enumerate(leaderboard, 1):
        entry["rank"] = i

    top_n = min(args.top, len(leaderboard))
    print(f"🏆 TOP {top_n} TAGGERS:")
    print(f"{'Rank':<5} {'Username':<32} {'Tags':>6}  {'Comments':>8}")
    print("─" * 60)
    for entry in leaderboard[:top_n]:
        print(f"  {entry['rank']:<4} @{entry['username']:<31} {entry['unique_tags']:>6}  {entry['total_comments']:>8}")

    # Save output if requested
    if args.output:
        output = {
            "total_comments": total_comments,
            "unique_commenters": len(leaderboard),
            "posts_analysed": [{"media_id": mid, "label": lbl} for mid, lbl in posts],
            "leaderboard": leaderboard,
        }
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Leaderboard saved to: {args.output}")

    print()
    print("Done. To verify followers and select winners, run:")
    print("  python3 scripts/giveaway/giveaway_winner.py --post <URL> --winners 2")


if __name__ == "__main__":
    main()

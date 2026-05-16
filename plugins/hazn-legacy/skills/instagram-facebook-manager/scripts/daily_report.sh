#!/usr/bin/env bash
# ============================================================
# daily_report.sh — Fetch raw Meta engagement data to /tmp/
# ============================================================
#
# Usage:
#   source .env.meta && bash scripts/daily_report.sh
#   # Then run: python3 scripts/report.py
#
# Required env vars (from .env.meta):
#   META_PAGE_TOKEN    - Long-lived Page Access Token
#   META_PAGE_ID       - Facebook Page ID (numeric)
#   META_IG_ID         - Instagram Business Account ID (numeric)
#   META_API_VERSION   - e.g. v21.0
#
# Output files written to /tmp/:
#   /tmp/ig_data.json   - Instagram recent media
#   /tmp/fb_data.json   - Facebook published posts
#   /tmp/acct.json      - Instagram account stats
#   /tmp/fb_acct.json   - Facebook page stats
#
# ============================================================

set -euo pipefail

# ─── Validate required env vars ───────────────────────────────────────────────
: "${META_PAGE_TOKEN:?ERROR: META_PAGE_TOKEN is not set. Source .env.meta first.}"
: "${META_PAGE_ID:?ERROR: META_PAGE_ID is not set.}"
: "${META_IG_ID:?ERROR: META_IG_ID is not set.}"
: "${META_API_VERSION:=v21.0}"

BASE="https://graph.facebook.com/${META_API_VERSION}"

echo "📥 Fetching Instagram media..."
curl -sf "${BASE}/${META_IG_ID}/media?fields=caption,timestamp,permalink,like_count,comments_count,media_type&limit=25&access_token=${META_PAGE_TOKEN}" \
  -o /tmp/ig_data.json
echo "   ✅ Saved to /tmp/ig_data.json"

echo "📥 Fetching Facebook posts..."
curl -sf "${BASE}/${META_PAGE_ID}/published_posts?fields=message,created_time,permalink_url,likes.summary(true),comments.summary(true),shares&limit=25&access_token=${META_PAGE_TOKEN}" \
  -o /tmp/fb_data.json
echo "   ✅ Saved to /tmp/fb_data.json"

echo "📥 Fetching Instagram account stats..."
curl -sf "${BASE}/${META_IG_ID}?fields=followers_count,media_count&access_token=${META_PAGE_TOKEN}" \
  -o /tmp/acct.json
echo "   ✅ Saved to /tmp/acct.json"

echo "📥 Fetching Facebook page stats..."
curl -sf "${BASE}/${META_PAGE_ID}?fields=fan_count,name&access_token=${META_PAGE_TOKEN}" \
  -o /tmp/fb_acct.json
echo "   ✅ Saved to /tmp/fb_acct.json"

echo ""
echo "✅ All data fetched. Run: python3 scripts/report.py"

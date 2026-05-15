#!/usr/bin/env python3
"""
report.py — Format Meta API engagement data into a daily social media report.

Usage:
    bash scripts/daily_report.sh   # Fetch raw data first
    python3 scripts/report.py      # Then format it

    # Or with a custom timezone offset (default: UTC+5 / PKT):
    TIMEZONE_OFFSET=3 python3 scripts/report.py    # For UTC+3 (e.g. Turkey)
    TIMEZONE_OFFSET=0 python3 scripts/report.py    # For UTC

Input files (written by daily_report.sh):
    /tmp/ig_data.json
    /tmp/fb_data.json
    /tmp/acct.json
    /tmp/fb_acct.json

Output: formatted report printed to stdout (pipe or capture as needed)
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

# ─── Timezone config ──────────────────────────────────────────────────────────
tz_offset = int(os.getenv("TIMEZONE_OFFSET", "5"))  # Default: PKT (UTC+5)
TZ = timezone(timedelta(hours=tz_offset))
tz_label = f"UTC+{tz_offset}" if tz_offset >= 0 else f"UTC{tz_offset}"

today = datetime.now(TZ).strftime('%Y-%m-%d')
now_fmt = datetime.now(TZ).strftime('%I:%M %p') + f" ({tz_label})"

# ─── Load data ────────────────────────────────────────────────────────────────
def load_json(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Missing file: {path}", file=sys.stderr)
        print(f"   Run 'bash scripts/daily_report.sh' first.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)

ig = load_json('/tmp/ig_data.json')
fb = load_json('/tmp/fb_data.json')
acct = load_json('/tmp/acct.json')
fb_acct = load_json('/tmp/fb_acct.json')

# ─── Filter today's posts ─────────────────────────────────────────────────────
ig_today = []
for p in ig.get('data', []):
    ts = datetime.fromisoformat(p['timestamp'].replace('+0000', '+00:00')).astimezone(TZ)
    if ts.strftime('%Y-%m-%d') == today:
        ig_today.append({**p, 'time_fmt': ts.strftime('%I:%M %p')})

fb_today = []
for p in fb.get('data', []):
    ts = datetime.fromisoformat(p['created_time'].replace('+0000', '+00:00')).astimezone(TZ)
    if ts.strftime('%Y-%m-%d') == today:
        fb_today.append({**p, 'time_fmt': ts.strftime('%I:%M %p')})

# ─── Compute stats ────────────────────────────────────────────────────────────
ig_likes    = sum(p.get('like_count', 0) for p in ig_today)
ig_comments = sum(p.get('comments_count', 0) for p in ig_today)
ig_total    = ig_likes + ig_comments

ig_followers = acct.get('followers_count', 0)
ig_er = (ig_total / ig_followers * 100) if ig_followers else 0.0

fb_fans = fb_acct.get('fan_count', 0)
page_name = fb_acct.get('name', '{BRAND}')

fb_likes    = sum(p.get('likes', {}).get('summary', {}).get('total_count', 0) for p in fb_today)
fb_comments = sum(p.get('comments', {}).get('summary', {}).get('total_count', 0) for p in fb_today)
fb_shares   = sum((p.get('shares', {}).get('count', 0) if isinstance(p.get('shares'), dict) else 0) for p in fb_today)
fb_total    = fb_likes + fb_comments + fb_shares
fb_er = (fb_total / fb_fans * 100) if fb_fans else 0.0

# ─── Print report ─────────────────────────────────────────────────────────────
W = 50

print(f"📊 DAILY ENGAGEMENT REPORT — {page_name}")
print(f"📅 {today} | Generated at {now_fmt}")
print("=" * W)
print()

print(f"👥 AUDIENCE OVERVIEW")
print(f"   📘 Facebook Fans:    {fb_fans:,}")
print(f"   📸 Instagram Followers: {ig_followers:,}")
print(f"   📷 Total IG Posts:   {acct.get('media_count', 0):,}")
print()

# ─── Instagram section ────────────────────────────────────────────────────────
print(f"📸 INSTAGRAM — {len(ig_today)} post(s) today")
print("─" * W)
if ig_today:
    for i, p in enumerate(ig_today, 1):
        cap = (p.get('caption', '') or 'No caption')
        cap_short = cap[:50] + ("…" if len(cap) > 50 else "")
        likes    = p.get('like_count', 0)
        comments = p.get('comments_count', 0)
        print(f"  {i}. [{p['time_fmt']}] {p.get('media_type', 'POST')}")
        print(f"     ❤️  {likes}   💬 {comments}")
        print(f"     {cap_short}")
        print(f"     🔗 {p.get('permalink', '—')}")
        print()
    print(f"  📈 IG Totals:  ❤️ {ig_likes} likes | 💬 {ig_comments} comments")
    print(f"  📊 Engagement Rate: {ig_er:.2f}%")
else:
    print("  No Instagram posts published today.")
print()

# ─── Facebook section ─────────────────────────────────────────────────────────
print(f"📘 FACEBOOK — {len(fb_today)} post(s) today")
print("─" * W)
if fb_today:
    for i, p in enumerate(fb_today, 1):
        msg = (p.get('message', '') or 'No message')
        msg_short = msg[:50] + ("…" if len(msg) > 50 else "")
        p_likes    = p.get('likes', {}).get('summary', {}).get('total_count', 0)
        p_comments = p.get('comments', {}).get('summary', {}).get('total_count', 0)
        p_shares   = p.get('shares', {}).get('count', 0) if isinstance(p.get('shares'), dict) else 0
        print(f"  {i}. [{p['time_fmt']}] {msg_short}")
        print(f"     ❤️  {p_likes}   💬 {p_comments}   🔁 {p_shares}")
        print(f"     🔗 {p.get('permalink_url', '—')}")
        print()
    print(f"  📈 FB Totals:  ❤️ {fb_likes} likes | 💬 {fb_comments} comments | 🔁 {fb_shares} shares")
    print(f"  📊 Engagement Rate: {fb_er:.2f}%")
else:
    print("  No Facebook posts published today.")
print()

# ─── Top post ────────────────────────────────────────────────────────────────
all_today = ig_today + fb_today
if all_today:
    top = max(all_today, key=lambda x: (
        x.get('like_count', 0) + x.get('comments_count', 0)
        + x.get('likes', {}).get('summary', {}).get('total_count', 0)
        + x.get('comments', {}).get('summary', {}).get('total_count', 0)
    ))
    top_cap = (top.get('caption', None) or top.get('message', None) or '')
    top_eng = (
        top.get('like_count', 0) + top.get('comments_count', 0)
        + top.get('likes', {}).get('summary', {}).get('total_count', 0)
        + top.get('comments', {}).get('summary', {}).get('total_count', 0)
    )
    platform = "IG" if 'like_count' in top else "FB"
    print(f"🏆 TOP POST TODAY ({platform})")
    print(f"   {(top_cap[:60] + '…') if len(top_cap) > 60 else top_cap or '[no caption]'}")
    print(f"   Total interactions: {top_eng}")
    print(f"   🔗 {top.get('permalink', top.get('permalink_url', '—'))}")
    print()

print("=" * W)
print("Report end.")

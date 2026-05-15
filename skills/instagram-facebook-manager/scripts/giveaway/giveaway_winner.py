#!/usr/bin/env python3
"""
giveaway_winner.py — Full Instagram giveaway tool.

Pulls comments from a giveaway post, counts unique @tags per commenter,
verifies follower status against the brand account, and selects winners.

Usage:
    python3 giveaway_winner.py --post <IG_POST_URL> [options]

Options:
    --post URL          Instagram post URL (required)
    --account USERNAME  IG account whose followers to verify (required)
    --winners N         Number of winners to pick (default: 2)
    --min-tags N        Minimum unique tags required to be eligible (default: 1)
    --flat              Flat random draw instead of weighted by tag count
    --dry-run           Analyse comments only, skip follower check
    --top N             Show top N in leaderboard (default: 20)

Example:
    python3 giveaway_winner.py \\
        --post https://www.instagram.com/p/XXXX/ \\
        --account yourbrandhandle \\
        --winners 2

Credentials (in scripts/giveaway/.env or as env vars):
    IG_SESSION_ID   Session cookie from browser (preferred — see references/follower-verification.md)
    IG_USERNAME     Your IG username (optional fallback)
    IG_PASSWORD     Your IG password (optional fallback)

⚠️  Uses instagrapi (Instagram private API). See references/follower-verification.md for
    ToS notice and safe usage guidelines.

Requirements:
    pip install instagrapi python-dotenv
"""

import os
import re
import csv
import json
import time
import random
import argparse
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ─── Load .env ────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / ".env")
    load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env.meta", override=False)
except ImportError:
    pass

# ─── Check instagrapi ─────────────────────────────────────────────────────────
try:
    from instagrapi import Client
    from instagrapi.exceptions import UserNotFound, LoginRequired, ChallengeRequired
except ImportError:
    print("❌ instagrapi not installed.")
    print("   Run: pip install instagrapi")
    print("   See: references/follower-verification.md for full setup.")
    sys.exit(1)

# ─── Config ───────────────────────────────────────────────────────────────────
IG_USERNAME   = os.getenv("IG_USERNAME", "")
IG_PASSWORD   = os.getenv("IG_SESSION_ID", "")  # Note: variable name; stores session ID
IG_SESSION_ID = os.getenv("IG_SESSION_ID", "")
IG_PASSWORD   = os.getenv("IG_PASSWORD", "")

SESSION_FILE  = Path(__file__).parent / "ig_session.json"
OUTPUT_DIR    = Path(__file__).parent / "results"

# ─── IG Client ────────────────────────────────────────────────────────────────
def get_client() -> Client:
    """
    Login to Instagram. Priority:
    1. Saved session file (fastest, most trusted)
    2. IG_SESSION_ID from browser cookie (bypasses IP blocks)
    3. Username + password (fallback — may be challenged from server IPs)
    """
    cl = Client()
    cl.delay_range = [1, 3]  # Human-like delays

    # 1. Saved session
    if SESSION_FILE.exists():
        print("📂 Loading saved session...")
        try:
            cl.load_settings(str(SESSION_FILE))
            cl.get_timeline_feed()
            cl.dump_settings(str(SESSION_FILE))
            print("✅ Session restored.")
            return cl
        except Exception:
            print("⚠️  Saved session invalid, trying other methods...")
            SESSION_FILE.unlink(missing_ok=True)

    # 2. Browser session ID
    if IG_SESSION_ID:
        print("🍪 Logging in via browser session ID (safest method)...")
        try:
            cl.login_by_sessionid(IG_SESSION_ID)
            cl.dump_settings(str(SESSION_FILE))
            print("✅ Logged in via session ID.")
            return cl
        except Exception as e:
            print(f"⚠️  Session ID login failed: {e}")

    # 3. Password fallback
    if IG_PASSWORD and IG_USERNAME:
        print(f"🔐 Logging in with username + password as @{IG_USERNAME}...")
        try:
            cl.login(IG_USERNAME, IG_PASSWORD)
            cl.dump_settings(str(SESSION_FILE))
            print(f"💾 Session saved to {SESSION_FILE}")
            return cl
        except ChallengeRequired:
            print("❌ Instagram requires a challenge (2FA / CAPTCHA).")
            print("   Approve it in the Instagram app, then retry.")
            sys.exit(1)

    raise RuntimeError(
        "❌ No login method available.\n"
        "Set IG_SESSION_ID in scripts/giveaway/.env (extract from browser cookies)\n"
        "or set IG_USERNAME + IG_PASSWORD.\n"
        "See references/follower-verification.md for instructions."
    )


# ─── Follower verification ────────────────────────────────────────────────────
def check_is_follower(cl: Client, account_user_id: int, target_username: str) -> bool | None:
    """
    Check if target_username follows the brand account.
    Returns: True = follower, False = not follower, None = check failed
    """
    try:
        time.sleep(random.uniform(1.0, 2.5))
        results = cl.search_followers(account_user_id, query=target_username)
        for user in results:
            if user.username.lower() == target_username.lower():
                return True
        return False
    except UserNotFound:
        return False
    except Exception as e:
        print(f"  ⚠️  Could not check @{target_username}: {e}")
        return None


# ─── Comment parsing ─────────────────────────────────────────────────────────
def extract_unique_tags(text: str, exclude_accounts: list[str] = []) -> set:
    """Extract unique @mentions from comment text, excluding specified accounts."""
    exclude_lower = {a.lower() for a in exclude_accounts}
    tags = re.findall(r"@([\w.]+)", text)
    return {t.lower() for t in tags if t.lower() not in exclude_lower}


def fetch_all_comments(cl: Client, post_url: str) -> list:
    """Fetch all comments from an Instagram post URL via instagrapi."""
    print(f"\n📥 Fetching comments from: {post_url}")
    media_pk = cl.media_pk_from_url(post_url)
    comments = cl.media_comments(media_pk, amount=0)  # 0 = all
    print(f"✅ {len(comments)} comments fetched.")
    return comments


# ─── Winner selection ─────────────────────────────────────────────────────────
def pick_winners(eligible: list, num_winners: int, weighted: bool) -> list:
    """Select winners from eligible entrants, optionally weighted by tag count."""
    if len(eligible) <= num_winners:
        return eligible

    if not weighted:
        return random.sample(eligible, num_winners)

    # Weighted by tag count (cap at 50 to prevent monopoly)
    weights = [min(e["tag_count"], 50) for e in eligible]
    selected = random.choices(eligible, weights=weights, k=num_winners * 3)

    seen = set()
    winners = []
    for w in selected:
        if w["username"] not in seen:
            seen.add(w["username"])
            winners.append(w)
        if len(winners) >= num_winners:
            break

    # Fill from remaining if deduplication left gaps
    remaining = [e for e in eligible if e["username"] not in seen]
    while len(winners) < num_winners and remaining:
        winners.append(remaining.pop(0))

    return winners[:num_winners]


# ─── Main ─────────────────────────────────────────────────────────────────────
def run_giveaway(
    post_url: str,
    brand_account: str,
    num_winners: int = 2,
    min_tags: int = 1,
    weighted: bool = True,
    dry_run: bool = False,
    top_n: int = 20,
):
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Login
    cl = get_client()

    # Look up brand account
    print(f"\n🔍 Looking up @{brand_account}...")
    account_info = cl.user_info_by_username(brand_account)
    account_user_id = account_info.pk
    print(f"   User ID: {account_user_id} | Followers: {account_info.follower_count:,}")

    # Fetch comments
    comments = fetch_all_comments(cl, post_url)

    # Parse comments
    print("\n📊 Parsing comments...")
    entry_data = defaultdict(lambda: {"tags": set(), "comment_count": 0})
    for c in comments:
        username = c.user.username.lower()
        tags = extract_unique_tags(c.text, exclude_accounts=[brand_account])
        entry_data[username]["tags"].update(tags)
        entry_data[username]["comment_count"] += 1

    print(f"   Unique commenters: {len(entry_data)}")

    # Sort by tag count
    sorted_entrants = sorted(
        entry_data.items(),
        key=lambda x: (-len(x[1]["tags"]), -x[1]["comment_count"])
    )

    # Leaderboard
    print(f"\n🏅 TOP {min(top_n, len(sorted_entrants))} TAGGERS:")
    print(f"{'Rank':<5} {'Username':<32} {'Tags':>6}  {'Comments':>8}")
    print("─" * 60)
    for i, (username, data) in enumerate(sorted_entrants[:top_n], 1):
        print(f"  {i:<4} @{username:<31} {len(data['tags']):>6}  {data['comment_count']:>8}")

    if dry_run:
        print("\n⏩ Dry run — skipping follower verification and winner selection.")
        return

    # Follower verification (top 30 candidates)
    print(f"\n🔍 Verifying follower status (top {min(30, len(sorted_entrants))} taggers)...")
    eligible   = []
    ineligible = []
    unknown    = []

    for username, data in sorted_entrants[:30]:
        tag_count = len(data["tags"])
        if tag_count < min_tags:
            ineligible.append({"username": username, "reason": "insufficient_tags", "tag_count": tag_count})
            continue

        print(f"  Checking @{username} ({tag_count} tags)...", end=" ", flush=True)
        is_follower = check_is_follower(cl, account_user_id, username)

        entry = {
            "username": username,
            "tag_count": tag_count,
            "tags": sorted(data["tags"]),
            "comment_count": data["comment_count"],
            "is_follower": is_follower,
        }

        if is_follower is True:
            eligible.append(entry)
            print("✅ FOLLOWER")
        elif is_follower is False:
            ineligible.append({**entry, "reason": "not_follower"})
            print("❌ NOT FOLLOWING")
        else:
            unknown.append(entry)
            print("❓ UNKNOWN (present to brand owner for manual check)")

    # Pick winners
    print(f"\n🎯 Picking {num_winners} winner(s) from {len(eligible)} eligible entrants...")
    if len(eligible) < num_winners:
        print(f"⚠️  Only {len(eligible)} eligible entrants. Adjusting winner count.")
        num_winners = len(eligible)

    winners = pick_winners(eligible, num_winners, weighted)

    # Print winners
    print()
    print("═" * 60)
    print("🎉 WINNERS!")
    print("═" * 60)
    for i, w in enumerate(winners, 1):
        tags_preview = ", ".join(["@" + t for t in w["tags"][:5]])
        more = f" …+{len(w['tags'])-5}" if len(w["tags"]) > 5 else ""
        print(f"  {i}. @{w['username']}")
        print(f"     Tags: {w['tag_count']} | Comments: {w['comment_count']}")
        print(f"     Tagged: {tags_preview}{more}")
    print("═" * 60)

    if unknown:
        print(f"\n⚠️  {len(unknown)} accounts with UNKNOWN follower status (check manually):")
        for u in unknown:
            print(f"   @{u['username']} ({u['tag_count']} tags)")

    # Export CSV
    csv_path = OUTPUT_DIR / f"giveaway_{timestamp}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["rank", "username", "tag_count", "comment_count", "is_follower", "tags"]
        )
        writer.writeheader()
        for i, (username, data) in enumerate(sorted_entrants, 1):
            follower_status = (
                "YES"     if username in {e["username"] for e in eligible} else
                "NO"      if username in {e["username"] for e in ineligible} else
                "UNKNOWN"
            )
            writer.writerow({
                "rank":          i,
                "username":      username,
                "tag_count":     len(data["tags"]),
                "comment_count": data["comment_count"],
                "is_follower":   follower_status,
                "tags":          ", ".join(sorted(data["tags"])),
            })
    print(f"\n📁 Full results: {csv_path}")

    # Export winners JSON
    json_path = OUTPUT_DIR / f"winners_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "post_url":          post_url,
            "brand_account":     brand_account,
            "timestamp":         timestamp,
            "total_comments":    len(comments),
            "total_commenters":  len(entry_data),
            "eligible_count":    len(eligible),
            "unknown_count":     len(unknown),
            "winners":           winners,
        }, f, indent=2, ensure_ascii=False)
    print(f"🏆 Winners JSON:  {json_path}")

    return winners


# ─── CLI ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Instagram giveaway winner picker with follower verification."
    )
    parser.add_argument("--post",     required=True,  help="Instagram post URL")
    parser.add_argument("--account",  required=True,  help="Brand IG username to verify followers against")
    parser.add_argument("--winners",  type=int, default=2, help="Number of winners (default: 2)")
    parser.add_argument("--min-tags", type=int, default=1, help="Minimum unique tags required (default: 1)")
    parser.add_argument("--flat",     action="store_true", help="Flat random draw instead of weighted")
    parser.add_argument("--dry-run",  action="store_true", help="Analyse comments only, skip follower check")
    parser.add_argument("--top",      type=int, default=20, help="Show top N in leaderboard (default: 20)")
    args = parser.parse_args()

    run_giveaway(
        post_url=args.post,
        brand_account=args.account,
        num_winners=args.winners,
        min_tags=args.min_tags,
        weighted=not args.flat,
        dry_run=args.dry_run,
        top_n=args.top,
    )

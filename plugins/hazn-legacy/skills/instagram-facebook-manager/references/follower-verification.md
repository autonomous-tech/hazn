# Follower Verification with instagrapi

How to verify Instagram follower status for giveaway entrants.

---

## Why the Official API Won't Work

Meta intentionally blocks follower enumeration via the Graph API for privacy reasons.  
There is no endpoint that returns "is user X a follower of account Y" in the public API.

This means: **for giveaway follower verification, we must use `instagrapi`** — a Python library that reverse-engineered Instagram's private (app) API.

---

## ⚠️ Terms of Service Notice

> **Use at your own risk.** `instagrapi` uses Instagram's private API, which violates Meta's Terms of Service (Section 3.2: "You won't reverse engineer or access our Platform in unauthorized ways").
>
> In practice: Meta rarely bans accounts for read-only follower lookups. The risk is proportional to usage volume. For a one-off giveaway (checking 20–30 accounts), the risk is very low. For high-volume automation, the risk is significant.
>
> The brand owner should be aware of and accept this risk. Use this capability for giveaway verification only — do not build continuous monitoring or automation on top of it.

---

## Setup

### Install requirements

```bash
pip install instagrapi python-dotenv
```

Or if you have a `requirements.txt`:
```
instagrapi>=2.0.0
python-dotenv>=1.0.0
```

### Create `.env` in the giveaway script directory

```bash
# scripts/giveaway/.env
IG_USERNAME={your_ig_username}
IG_SESSION_ID={session_id_from_browser_cookies}
# Optional fallback:
IG_PASSWORD={your_ig_password}
```

---

## Getting the Instagram Session ID (Recommended Method)

The session ID approach is the safest — it uses your existing logged-in browser session, bypassing IP-block risks associated with username/password login from server IPs.

### Step-by-step: Extract session ID from browser

**Chrome / Edge:**
1. Go to [instagram.com](https://www.instagram.com) and log in to the brand account
2. Open DevTools: `F12` or right-click → Inspect
3. Go to **Application** tab → **Cookies** → `https://www.instagram.com`
4. Find the cookie named **`sessionid`**
5. Copy its **Value** (it's a long string like `12345678%3AaB3cD4eF5g...`)
6. Paste it as `IG_SESSION_ID` in your `.env`

**Firefox:**
1. Go to instagram.com (logged in)
2. DevTools: `F12` → **Storage** tab → **Cookies**
3. Find `sessionid` → copy the Value

**Safari:**
1. Enable Developer menu: Safari → Preferences → Advanced → Show Develop menu
2. Develop → Show Web Inspector
3. Storage → Cookies → instagram.com → `sessionid`

### How long is a session ID valid?

Instagram session cookies typically last 90–180 days. They expire when:
- The user logs out
- Instagram detects suspicious activity
- The session is explicitly revoked from the app (Settings → Security → Login Activity)

---

## The Login Flow (Code)

The `giveaway_winner.py` script handles this automatically, but here's the pattern for reference:

```python
from instagrapi import Client
from pathlib import Path

SESSION_FILE = Path("ig_session.json")
SESSION_ID   = "your_session_id_here"

cl = Client()
cl.delay_range = [1, 3]  # Human-like delays — important for avoiding blocks

# Priority 1: Load saved session file (fastest, most trusted by IG)
if SESSION_FILE.exists():
    cl.load_settings(str(SESSION_FILE))
    cl.get_timeline_feed()  # Validates session is still active
    cl.dump_settings(str(SESSION_FILE))  # Refresh/save updated session

# Priority 2: Login via browser session ID
elif SESSION_ID:
    cl.login_by_sessionid(SESSION_ID)
    cl.dump_settings(str(SESSION_FILE))  # Save for next time

# Priority 3: Username + password (fallback — higher block risk on server IPs)
else:
    cl.login("username", "password")
    cl.dump_settings(str(SESSION_FILE))
```

### Why `login_by_sessionid` is preferred

- ✅ Reuses an existing trusted browser session (less suspicious to IG)
- ✅ No 2FA prompts (already authenticated in browser)
- ✅ Avoids IP reputation issues — IG sees the login as originating from the same session, not a new bot login
- ✅ Works even if IG's challenge flow is blocking username/password logins from server IPs

---

## Follower Check Implementation

```python
import time, random
from instagrapi import Client
from instagrapi.exceptions import UserNotFound

def check_is_follower(cl: Client, account_user_id: int, target_username: str) -> bool | None:
    """
    Check if target_username is in account's follower list.
    Returns: True = follower, False = not follower, None = check failed
    """
    try:
        time.sleep(random.uniform(1.0, 2.5))  # Rate limiting
        results = cl.search_followers(account_user_id, query=target_username)
        for user in results:
            if user.username.lower() == target_username.lower():
                return True
        return False
    except UserNotFound:
        return False
    except Exception as e:
        print(f"  ⚠️  Could not check @{target_username}: {e}")
        return None  # None = unknown (don't count as eligible or ineligible)
```

**Important:** The `search_followers` method does a targeted search — it doesn't download the full follower list. This is much faster and less risky than paginating all followers.

---

## Handling Unknown Results

`None` means the check failed (API error, rate limit, private account, etc.).  
Handle unknowns carefully:

- Present the `UNKNOWN` list to the brand owner for manual verification
- Don't count unknowns as eligible or ineligible by default
- For giveaways with few eligible entrants, the brand owner may choose to manually verify the unknowns

---

## Rate Limiting and Safe Usage

`instagrapi` exposes methods that call Instagram's private API. To avoid detection:

| Practice | Implementation |
|----------|---------------|
| Human-like delays | `cl.delay_range = [1, 3]` (1–3 second random pause between calls) |
| Batch size limits | Check max 30–50 users per run |
| Error backoff | If `ChallengeRequired` or rate limit error → stop immediately |
| Session reuse | Always save and reload session file (builds trust with IG) |
| Don't spam | One follower check run per giveaway, not continuous polling |

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `ChallengeRequired` | IG wants 2FA or CAPTCHA | Approve the challenge in the IG app on the browser you extracted the cookie from, then retry |
| `LoginRequired` | Session expired | Re-extract `sessionid` from browser cookies |
| `UserNotFound` | Username doesn't exist or account is private/deleted | Treat as not eligible |
| `429 Too Many Requests` | Rate limited | Wait 15–30 minutes before retrying |
| `PleaseWaitFewMinutes` | IG temporary block | Wait 30 minutes; reduce request frequency |

---

## What NOT to Build on Top of This

To minimize ToS risk and avoid account bans:

- ❌ Continuous follower monitoring (poll every N minutes)
- ❌ Mass DM campaigns via instagrapi
- ❌ Scraping all followers/following lists
- ❌ Automated follow/unfollow
- ❌ Running from the same IP that does other automated IG activity

✅ Safe: One-off follower verification for a giveaway, checking 20–50 accounts max per run

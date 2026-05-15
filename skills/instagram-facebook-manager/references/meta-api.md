# Meta Graph API Reference

**API Version:** v21.0  
**Base URL:** `https://graph.facebook.com/v21.0/`

---

## Credentials Setup

### What you need

| Credential | Where to get it |
|-----------|-----------------|
| `META_PAGE_TOKEN` | Facebook Page Access Token (long-lived) |
| `META_PAGE_ID` | Facebook Page ID (numeric) |
| `META_IG_ID` | Instagram Business Account ID (numeric, linked to your FB Page) |

### How to get a Page Access Token

**Step 1: Create a Facebook App**
1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create a new App → Business type
3. Add "Facebook Login" and "Instagram Graph API" products

**Step 2: Get a short-lived User Access Token**
1. Visit the [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your App from the dropdown
3. Click "Generate Access Token"
4. Add permissions: `pages_manage_posts`, `pages_read_engagement`, `instagram_basic`, `instagram_content_publish`, `instagram_manage_comments`
5. Copy the token shown (short-lived, expires in 1 hour)

**Step 3: Exchange for a long-lived User Access Token (~60 days)**
```bash
curl -s "https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={APP_ID}&client_secret={APP_SECRET}&fb_exchange_token={SHORT_LIVED_TOKEN}"
```

**Step 4: Get the Page Access Token (never expires while app is active)**
```bash
curl -s "https://graph.facebook.com/v21.0/me/accounts?access_token={LONG_LIVED_USER_TOKEN}"
```
Find your page in the response and copy its `access_token`. This Page Access Token is long-lived (does not expire as long as the app is active and the user hasn't revoked access).

### How to find your Page ID and IG Business Account ID

```bash
# Page ID — look for "id" in accounts response above, or:
curl -s "https://graph.facebook.com/v21.0/me/accounts?access_token={PAGE_TOKEN}" | python3 -m json.tool

# IG Business Account ID
curl -s "https://graph.facebook.com/v21.0/{PAGE_ID}?fields=instagram_business_account&access_token={PAGE_TOKEN}"
```

### Verify credentials

```bash
source .env.meta
curl -s "https://graph.facebook.com/${META_API_VERSION}/${META_PAGE_ID}?fields=name,fan_count&access_token=${META_PAGE_TOKEN}"
```

---

## Key API Endpoints

### Facebook Page

| Action | Endpoint | Method |
|--------|----------|--------|
| Get page info | `/{PAGE_ID}?fields=name,fan_count,followers_count` | GET |
| Get published posts | `/{PAGE_ID}/published_posts?fields=message,created_time,permalink_url,likes.summary(true),comments.summary(true),shares&limit=25` | GET |
| Publish text post | `/{PAGE_ID}/feed` body: `message=...` | POST |
| Publish photo post | `/{PAGE_ID}/photos` body: `url=...&message=...` | POST |
| Edit a post | `/{POST_ID}` body: `message=<new text>` | POST |
| Delete a post | `/{POST_ID}` | DELETE |
| Get post comments | `/{POST_ID}/comments?fields=username,message,created_time&limit=100` | GET |

### Instagram Business Account

| Action | Endpoint | Method |
|--------|----------|--------|
| Get account info | `/{IG_ID}?fields=username,followers_count,media_count` | GET |
| Get recent media | `/{IG_ID}/media?fields=caption,timestamp,permalink,like_count,comments_count,media_type&limit=25` | GET |
| Create media container | `/{IG_ID}/media` body: `image_url=...&caption=...` | POST |
| Check container status | `/{CONTAINER_ID}?fields=status_code` | GET |
| Publish container | `/{IG_ID}/media_publish` body: `creation_id=...` | POST |
| Get post permalink | `/{MEDIA_ID}?fields=permalink` | GET |
| Edit IG caption | `/{MEDIA_ID}` body: `caption=<new caption>` | POST |
| Get IG comments | `/{MEDIA_ID}/comments?fields=username,text,timestamp&limit=100` | GET |

### Comment Pagination

The API returns comments in pages. Always paginate fully for giveaway analysis:

```python
url = f"https://graph.facebook.com/v21.0/{media_id}/comments?fields=username,text,timestamp&limit=100&access_token={token}"
all_comments = []
while url:
    data = fetch_json(url)
    all_comments.extend(data.get("data", []))
    url = data.get("paging", {}).get("next")  # None when done
```

---

## Publishing to Instagram — Step by Step

Instagram publishing is a 3-step process:

```bash
# 1. Create container (returns container_id)
curl -s -X POST "https://graph.facebook.com/v21.0/${META_IG_ID}/media" \
  -d "image_url=<PUBLIC_URL>&caption=<CAPTION>&access_token=${META_PAGE_TOKEN}"

# 2. Poll until status_code = FINISHED (usually 5–30 seconds)
curl -s "https://graph.facebook.com/v21.0/<CONTAINER_ID>?fields=status_code&access_token=${META_PAGE_TOKEN}"
# Expected: {"status_code": "FINISHED", "id": "..."}

# 3. Publish
curl -s -X POST "https://graph.facebook.com/v21.0/${META_IG_ID}/media_publish" \
  -d "creation_id=<CONTAINER_ID>&access_token=${META_PAGE_TOKEN}"
```

**Container status codes:**
| Code | Meaning |
|------|---------|
| `FINISHED` | Ready to publish |
| `IN_PROGRESS` | Wait and retry |
| `ERROR` | Something went wrong (check image URL) |
| `EXPIRED` | Container expired (older than 24h) — recreate it |

---

## Rate Limits

| Limit Type | Value | Notes |
|-----------|-------|-------|
| IG API posts per 24h | 25 | Hard limit; errors with code 9 |
| API calls per hour | 200 | Per token |
| Comment reads | Included in 200/hr | Pagination doesn't count separately |
| FB posts per day | No hard limit | >5/day hurts organic reach algorithmically |

---

## Common Errors and Fixes

| Error Code | Message | Fix |
|-----------|---------|-----|
| 190 | Invalid OAuth access token | Token expired or revoked — regenerate |
| 200 | Permission denied | Missing required permission — check app permissions |
| 100 | Invalid parameter | Check the field names and IDs |
| 9 | API rate limit reached | Wait 24h (IG post limit) or 1h (API call limit) |
| 4 | Application request limit | Rate limited — back off and retry |
| 32 | Page request limit | Too many calls to this page endpoint |
| 803 | Some of the aliases you requested do not exist | Wrong Page ID or IG ID |
| IG container ERROR | Image URL not accessible | Make sure URL is publicly reachable without auth |
| IG container ERROR | Unsupported image format | Use JPEG or PNG; max 8MB |

---

## Token Refresh Procedure

**When to do this:** Within 7 days of the 60-day expiry (set a calendar reminder).

```bash
# Step 1: Get a fresh short-lived token via Graph API Explorer (manual step)
# Step 2: Exchange for long-lived
curl -s "https://graph.facebook.com/oauth/access_token?\
grant_type=fb_exchange_token\
&client_id={APP_ID}\
&client_secret={APP_SECRET}\
&fb_exchange_token={SHORT_LIVED_TOKEN}"

# Step 3: Get Page token
curl -s "https://graph.facebook.com/v21.0/me/accounts?access_token={LONG_LIVED_TOKEN}"

# Step 4: Update .env.meta with new META_PAGE_TOKEN
```

> **Pro tip:** Page Access Tokens derived from a long-lived User Access Token are themselves long-lived (they don't expire as long as the user's session is active). Check the token's expiry at:
> `https://developers.facebook.com/tools/debug/accesstoken/`

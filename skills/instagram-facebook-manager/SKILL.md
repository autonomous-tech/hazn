---
name: instagram-facebook-manager
description: >
  Manage Instagram and Facebook social media for any brand using the Meta Graph API.
  Use this skill when: (1) drafting or publishing posts to Instagram or Facebook,
  (2) running scheduled content cron jobs for a brand, (3) analysing post engagement
  or generating daily social media reports, (4) managing giveaway campaigns
  (announcement, hype posts, comment analysis, winner selection, winner announcement),
  (5) writing captions and hashtag sets for specific images or campaigns,
  (6) researching influencers or social media strategy.
  Requires: Facebook Page ID, Instagram Business Account ID, and a Meta Page Access
  Token stored in .env.meta in the workspace root.
allowed-tools: exec, web_fetch, web_search, Read, Write
---

# Instagram + Facebook Manager

Complete social media management via Meta Graph API v21.0.  
Based on 10 days of live production usage managing a real brand — 40+ posts published,
580 giveaway comments analysed, 430 new IG followers gained in one campaign.

---

## Setup

### Credentials file: `.env.meta`

Create `.env.meta` in the workspace root (or the brand workspace root):

```
META_PAGE_TOKEN=<long-lived-page-access-token>
META_PAGE_ID=<facebook-page-id>
META_IG_ID=<instagram-business-account-id>
META_API_VERSION=v21.0
```

> **Token lifecycle:** Page Access Tokens last ~60 days. Set a calendar reminder
> before expiry. See `references/meta-api.md` for how to obtain and exchange tokens.

### Verify credentials are working

```bash
source .env.meta
curl -s "https://graph.facebook.com/${META_API_VERSION}/${META_PAGE_ID}?fields=name,fan_count&access_token=${META_PAGE_TOKEN}"
```

A JSON response with the page name confirms success.

---

## Core Workflows

---

### Workflow 1: Draft → Approve → Publish (Standard Post)

This is the heartbeat of all content. **Never publish without explicit approval.**

**Step 1: Draft the caption**
- Use brand voice (warm, story-driven, platform-appropriate)
- FB: can be longer (150–300 words); IG: concise hook + hashtag block
- Include relevant hashtags (see `references/content-guidelines.md`)
- Add an image suggestion as a separate note — **never in the caption text itself**
- Present to the brand owner/team for approval

**Step 2: Get approval**
- Wait for an explicit approval signal: "APPROVE", "GO", "post it", "looks good publish"
- If the team sends revision notes, redraft and re-present
- Do not auto-publish on ambiguous signals

**Step 3: Publish to Facebook (text post)**

```bash
source .env.meta
curl -s -X POST "https://graph.facebook.com/${META_API_VERSION}/${META_PAGE_ID}/feed" \
  -d "message=<CAPTION>&access_token=${META_PAGE_TOKEN}"
```

For a **photo post** (requires a public image URL):

```bash
curl -s -X POST "https://graph.facebook.com/${META_API_VERSION}/${META_PAGE_ID}/photos" \
  -d "url=<PUBLIC_IMAGE_URL>&message=<CAPTION>&access_token=${META_PAGE_TOKEN}"
```

**Step 4: Publish to Instagram (photo post)**

Instagram requires a publicly accessible image URL. Preferred sources:
1. Google Drive share link (most reliable from WhatsApp/messaging teams)
2. Public CDN or S3 bucket URL
3. Any direct public HTTPS image link

```bash
# Step 4a: Create media container
CONTAINER=$(curl -s -X POST \
  "https://graph.facebook.com/${META_API_VERSION}/${META_IG_ID}/media" \
  -d "image_url=<PUBLIC_IMAGE_URL>&caption=<CAPTION>&access_token=${META_PAGE_TOKEN}")
CONTAINER_ID=$(echo $CONTAINER | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Step 4b: Wait for container to be ready (poll until status_code = FINISHED)
sleep 10
STATUS=$(curl -s "https://graph.facebook.com/${META_API_VERSION}/${CONTAINER_ID}?fields=status_code&access_token=${META_PAGE_TOKEN}")
echo $STATUS

# Step 4c: Publish the container
MEDIA=$(curl -s -X POST \
  "https://graph.facebook.com/${META_API_VERSION}/${META_IG_ID}/media_publish" \
  -d "creation_id=${CONTAINER_ID}&access_token=${META_PAGE_TOKEN}")
MEDIA_ID=$(echo $MEDIA | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Step 4d: Fetch permalink
curl -s "https://graph.facebook.com/${META_API_VERSION}/${MEDIA_ID}?fields=permalink&access_token=${META_PAGE_TOKEN}"
```

**Step 5: Confirm and report back**
- Share both post URLs (FB + IG) with the team
- Log the post in the session memory if tracking a content calendar

---

### Workflow 2: Daily Engagement Report

Run this once per day (typically end-of-day) to report on the brand's social performance.

**Option A: Run the helper scripts**

```bash
# Fetch raw data into /tmp
source .env.meta
bash scripts/daily_report.sh > /tmp/raw_report.json

# Format the report (assumes /tmp/ig_data.json, /tmp/fb_data.json, /tmp/acct.json exist)
python3 scripts/report.py
```

**Option B: Call the API directly inline**

```bash
source .env.meta

# IG posts (last 25)
curl -s "https://graph.facebook.com/${META_API_VERSION}/${META_IG_ID}/media?fields=caption,timestamp,permalink,like_count,comments_count,media_type&limit=25&access_token=${META_PAGE_TOKEN}"

# FB posts (last 25)
curl -s "https://graph.facebook.com/${META_API_VERSION}/${META_PAGE_ID}/published_posts?fields=message,created_time,permalink_url,likes.summary(true),comments.summary(true),shares&limit=25&access_token=${META_PAGE_TOKEN}"

# Account insights
curl -s "https://graph.facebook.com/${META_API_VERSION}/${META_IG_ID}?fields=followers_count,media_count&access_token=${META_PAGE_TOKEN}"
curl -s "https://graph.facebook.com/${META_API_VERSION}/${META_PAGE_ID}?fields=fan_count&access_token=${META_PAGE_TOKEN}"
```

**Report must include:**
- Audience snapshot: FB fans + IG followers
- Posts published today per platform, with per-post: likes, comments, shares
- Total interactions + average engagement rate per platform
  - `ER = (likes + comments) / followers × 100`
- Top post of the day (highest combined interactions)
- Timezone note: always filter/report in the brand's local timezone

---

### Workflow 3: Giveaway Campaign — End-to-End

See `references/giveaway-workflow.md` for the full playbook.

**High-level phases:**

1. **Announce** — Draft giveaway post with entry rules (follow + like + tag N friends). Get approval, publish to FB + IG with a prize image.

2. **Hype** — During the campaign window, each content slot references the giveaway with countdown copy ("3 days left", "last chance", etc.)

3. **Analyse** — When the campaign closes, run comment analysis:
   ```bash
   source .env.meta
   python3 scripts/giveaway/giveaway_analysis.py --post <IG_POST_URL>
   ```
   This calls the Meta Graph API to pull all comments, counts `@mentions` per user, and outputs a ranked leaderboard. No IG login required.

4. **Verify followers** — Check top commenters are actually following the brand account:
   ```bash
   # Requires instagrapi setup — see references/follower-verification.md
   python3 scripts/giveaway/giveaway_winner.py \
     --post <IG_POST_URL> --winners 2
   ```
   This produces a CSV of all entrants + winners JSON.

5. **Announce winners** — Get explicit confirmation from the brand owner before publishing. Draft the winner announcement post, get approval, publish to FB + IG. Include prize collection details (address, hours).

**Critical rule:** Do NOT announce winners without the brand owner's explicit approval. Winners who are tagged prematurely create irreversible public commitments.

---

### Workflow 4: Caption Writing & Hashtag Research (On-Demand)

When the team requests captions for specific images or occasions:

1. Ask for (or receive): image description or URL, occasion, campaign context, tone
2. If image is accessible (Google Drive link or direct URL), analyse with vision tool
3. Draft caption with:
   - Hook line (first 1–2 sentences are what shows before "more")
   - Brand narrative body (cultural context, product story, seasonal tie-in)
   - Clear CTA (visit, tag friends, shop, etc.)
   - Location mention if relevant
   - Core hashtag block (researched or brand standard)
4. Present for approval — see content guidelines in `references/content-guidelines.md`

**Generic hashtag research approach:**
- Use web_search for trending hashtags in the brand's niche + location
- Check competitor posts for hashtag ideas
- Mix: brand hashtags (5–8) + niche hashtags (5–8) + location hashtags (3–5)
- Max 30 hashtags on IG; aim for 15–25 high-relevance tags

---

### Workflow 5: Influencer & Strategy Research (On-Demand)

When the team requests influencer lists, rate cards, or strategy inputs:

1. Clarify: platform (IG/TikTok/YouTube), niche, location, budget range
2. Web search for influencers by niche + city (e.g., "Karachi fashion influencers Instagram 2025")
3. Structure output as:
   - Tier breakdown (nano/micro/mid/macro/mega with follower ranges)
   - 10–20 specific handles with follower counts and niche notes
   - DM pitch template
   - Rate card by tier (market rates)
   - Collab format ideas (story takeover, review post, giveaway collab, etc.)
4. Save durable findings to session memory for future reference

---

### Workflow 6: Content Calendar Planning (On-Demand)

When the team needs a content plan for a period (week, month, campaign):

1. Gather: brand voice, current campaign/season, product focus, key dates, post frequency
2. Draft a structured content calendar:
   - Date + time slot
   - Theme / angle
   - Caption hook (first line)
   - Image/creative brief
   - Platform targets (FB + IG, FB-only, IG-only)
3. Present as a table for easy team review
4. Store in a shared document or send to the team's WhatsApp group

---

## Approval Workflow

**Phrases that count as APPROVAL:**
- "APPROVE" / "Approved"
- "GO" / "Go ahead"
- "Post it" / "Publish it"
- "Looks good" + post instruction
- "Yes" in response to "shall I publish?"

**Phrases that mean REVISE (do not publish):**
- "Change X" / "Update X" / "Edit X"
- "Not sure about X" / "Can you try Y instead"
- General feedback without a clear approval signal
- Silence (no response = do not publish)

**⚠️ NEVER include in published captions:**
- Draft metadata ("APPROVE / REVISE")
- Image suggestions ("Suggested image: …")
- Internal notes or instructions
- Placeholder text like `{HASHTAG_BLOCK}` or `[INSERT IMAGE]`

---

## Rate Limits

| Platform | Limit |
|----------|-------|
| IG API-published posts | 25 per 24 hours |
| FB organic posting | No hard limit, but >4–5/day hurts reach |
| Comment reads | 200 calls per hour (pagination safe) |
| API calls total | 200 calls per hour per token |

---

## Known Limitations

| Limitation | Workaround |
|-----------|------------|
| IG post deletion via API | Must delete manually in the Instagram app |
| IG follower list access | Meta intentionally blocks it — use `instagrapi` (see `references/follower-verification.md`) |
| WhatsApp image relay to IG | Unreliable — always prefer Google Drive or direct public URL |
| Token expiry (~60 days) | Set a calendar reminder; refresh via long-lived token exchange |
| IG caption editing via API | Supported (`POST /{media-id}` with `caption` field) |
| IG Reels/Video publishing | Meta API supports it — not yet implemented in these scripts |

---

## References

| File | Contents |
|------|----------|
| `references/meta-api.md` | API endpoint reference, token setup, rate limits, common errors |
| `references/giveaway-workflow.md` | Full end-to-end giveaway campaign playbook |
| `references/content-guidelines.md` | Caption writing, hashtag strategy, approval workflow |
| `references/follower-verification.md` | instagrapi setup, session cookie login, ToS note |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/daily_report.sh` | Fetch raw engagement data from Meta API |
| `scripts/report.py` | Format raw data into a human-readable daily report |
| `scripts/giveaway/giveaway_analysis.py` | Analyse giveaway comments via Meta API (no IG login needed) |
| `scripts/giveaway/giveaway_winner.py` | Full giveaway tool: comment parse + follower verify + winner pick |

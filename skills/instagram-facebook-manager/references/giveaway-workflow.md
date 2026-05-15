# Giveaway Campaign Playbook

Full end-to-end playbook for running a social media giveaway via Meta Graph API.  
Based on a live Ramadan Chocolate Hamper Giveaway campaign that generated 580+ comments.

---

## Overview: 5 Phases

```
Phase 1: Announce  →  Phase 2: Hype  →  Phase 3: Analyse  →  Phase 4: Verify  →  Phase 5: Winners
```

---

## Phase 1: Announce the Giveaway

### What to draft

The announcement post must include:
1. **Prize description** — what they're winning, visually appealing
2. **Entry rules** — the standard giveaway mechanic:
   - ✅ Follow `@{BRAND_IG_HANDLE}`
   - ✅ Like this post
   - ✅ Tag 2 (or more) friends in the comments
   - (Optional) Share to story for bonus entry
3. **Closing date** — specific day (not time, to give flexibility)
4. **Prize collection details** — city, general area (not full address yet — share after winner confirmation)
5. **Campaign hashtag** — create a unique one (e.g., `#{BrandName}Giveaway`)

### Approval process
- Draft announcement post
- Present to brand owner + social media manager for review
- Get explicit APPROVE signal
- Do NOT publish until approved

### Publishing sequence
1. Publish to Facebook first (as a photo post with prize image)
2. Then publish to Instagram (photo post — same image, same caption)
3. Share both post URLs with the team
4. Pin the post on Facebook if possible (do via Facebook app — API doesn't support pinning)

### Timing
- Announce during peak engagement hours: 7–10 PM local time
- Give campaign enough time: minimum 5 days, ideal 7–10 days
- End before a key date (Eid, weekend market day, sale event)

---

## Phase 2: Hype Posts (Daily During Campaign)

### Every content slot during the campaign window should reference the giveaway

**Countdown copy progression:**

| Days Left | Copy Frame |
|-----------|-----------|
| 7+ days | "HUGE GIVEAWAY happening right now! Comment to enter 👇" |
| 5–6 days | "Only 5 days left to enter our giveaway! Don't miss out" |
| 3–4 days | "3 days left! Have you tagged your friends yet?" |
| 2 days | "⚡ 2 days left! Last chance to tag your friends and win" |
| Final day | "⏰ TODAY IS THE LAST DAY — enter before midnight!" |
| Day after close | "Giveaway is now CLOSED! Winners announced [date]" |

### Content variety for hype posts
- Close-up of the prize (different angle each day)
- "Look who entered!" (screenshot of high-engagement comment — get permission or use as "XYZ and friends are excited")
- Behind-the-scenes of prize preparation
- Countdown timer graphic (if brand has one)
- Reminder of rules (keep it short — link to original post)

### Don't forget
- Link to / mention the original giveaway post
- Always include the campaign hashtag
- IG Stories: share the giveaway post to story daily (manual step — API supports it but usually done in-app)

---

## Phase 3: Comment Analysis

**Tool:** `scripts/giveaway/giveaway_analysis.py`  
**Requires:** Only Meta Graph API credentials (no IG login needed)

### Running the analysis

```bash
source .env.meta

# Single post analysis
python3 scripts/giveaway/giveaway_analysis.py --post https://www.instagram.com/p/{POST_CODE}/

# Multi-post aggregation (if giveaway had multiple hype posts where people could also enter)
python3 scripts/giveaway/giveaway_analysis.py \
  --post https://www.instagram.com/p/{CODE1}/ \
  --post https://www.instagram.com/p/{CODE2}/ \
  --post https://www.instagram.com/p/{CODE3}/
```

### What the script does
1. Calls `GET /{MEDIA_ID}/comments` with full pagination
2. Parses `@mentions` from each comment text
3. Counts unique tags per commenter (across all provided posts)
4. Outputs a ranked leaderboard

### Reading the output

```
TOP TAGGERS — GIVEAWAY (COMBINED):
  1. @username123: 12 tags
  2. @otherperson: 8 tags
  3. @user456: 6 tags
  ...
Total comments across all posts: 580
```

**What the numbers mean:**
- "12 tags" = this person tagged 12 unique friends across their comments
- Users with more tags get more weighted draw entries (if using weighted mode)
- Comments with 0 @mentions are still valid entries (they liked + commented, but tagged 0)

### Interpreting for the brand
- Top 10–15 taggers report (to share with brand owner)
- Note any suspicious patterns (same username repeated, obvious bots)
- Flag accounts with fewer than 2 tags for potential ineligibility (if rules required tagging 2 friends)

---

## Phase 4: Follower Verification

**Tool:** `scripts/giveaway/giveaway_winner.py`  
**Requires:** `instagrapi` + IG session credentials (see `references/follower-verification.md`)

**Why this step:** Meta Graph API intentionally blocks follower list access for privacy reasons. `instagrapi` uses Instagram's private app API to check follow status. See the ToS notice in `references/follower-verification.md`.

### Running verification + winner selection

```bash
cd scripts/giveaway

# Full run: verify followers and pick 2 winners
python3 giveaway_winner.py \
  --post https://www.instagram.com/p/{POST_CODE}/ \
  --winners 2

# Dry run: analyse comments only, skip follower check
python3 giveaway_winner.py \
  --post https://www.instagram.com/p/{POST_CODE}/ \
  --winners 2 \
  --dry-run

# Flat random draw instead of weighted by tag count
python3 giveaway_winner.py \
  --post https://www.instagram.com/p/{POST_CODE}/ \
  --winners 2 \
  --flat
```

### Output files

The script creates a `results/` directory with:
- `giveaway_{timestamp}.csv` — all commenters with tag counts, follower status
- `winners_{timestamp}.json` — winner details + summary stats

### Presenting results to brand owner

Share with the brand owner:
1. Top 15 leaderboard (from Phase 3 analysis)
2. How many are verified followers
3. Proposed winners (the script's selection)
4. Ask for confirmation: "Do you approve these winners, or would you like to make adjustments?"

**CRITICAL:** Do not announce winners publicly until the brand owner has confirmed the list.

---

## Phase 5: Winner Announcement

### After brand owner confirms winners

**Draft announcement post:**
```
🎉 CONGRATULATIONS to our {Giveaway Name} winners!

🏆 @{winner1}
🏆 @{winner2}

Thank you to everyone who participated — we were overwhelmed by the love! 
{winner_count}+ of you tagged your friends, and it made our hearts full. 💕

Prize collection details:
📍 {BRAND_STORE_LOCATION}
📅 {DATE} | ⏰ After {TIME}

DM us on Instagram to arrange collection if you can't make it in person.

{HASHTAGS}
```

### Publishing sequence
1. Get brand owner APPROVE on the draft
2. Publish to Facebook (photo post with prize/winner graphic if available)
3. Publish to Instagram (same image and caption)
4. Share both URLs with the team
5. DM winners on Instagram with prize collection details (do this manually in-app — IG DM API requires advanced permissions)

### Post-giveaway engagement
- Reply to top commenters thanking them for participating
- Share the winner announcement to Story (manual)
- Follow up: after prizes are collected, post a "happy winner" photo if the winners consent

---

## Giveaway Learnings from Production

1. **Aggregate across ALL giveaway posts** — entrants often comment on multiple posts. Use multi-post mode for a comprehensive tag count.

2. **Winner confirmation is non-negotiable** — in one case, a winner announcement was deleted and reposted because it was published before the brand owner did her own manual verification. Always wait for explicit confirmation.

3. **Cron prompts go stale** — if the giveaway end date was hardcoded in cron prompts ("giveaway closes March 1"), update the prompts when the campaign ends to prevent the agent from sending incorrect countdown posts.

4. **Personal reminder messages work** — on winner announcement day, sending a personal WhatsApp message to the brand owner and social media manager ("Today is the day! Ready to announce?") improved execution speed and accuracy.

5. **Phone reminders to team for complex logistics** — prize collection coordination, address sharing, DM-ing winners. These steps require human action that the agent can prompt but not execute.

6. **Bot/suspicious accounts** — flag accounts that have 0 posts, very new creation date, or that tagged the same person 10+ times (giveaway farming). Present to brand owner for manual review.

# Content Guidelines

Caption writing principles, hashtag strategy, platform differences, and the approval workflow.

---

## Caption Writing Principles

### The 5-element caption structure

1. **Hook** (1–2 sentences) — what shows before "more". Must stop the scroll.
   - Question: "Did you know that wearing silver can…"
   - Statement: "This is the gift she actually wants."
   - Urgency: "Only 3 days left to enter our giveaway! 🎁"

2. **Narrative body** — the story, context, or value
   - For products: the making, the meaning, the occasion
   - For giveaways: the prize details, the excitement, the rules
   - For culture-tied brands: seasonal/religious/cultural context (e.g., Ramadan, Eid)

3. **CTA** (Call to Action) — one clear ask
   - Shop: "Visit us at {LOCATION}"
   - Engage: "Tag a friend who needs this 👇"
   - Enter: "Comment below to enter!"
   - Save: "Save this post for gift ideas"

4. **Location mention** (if relevant) — physical store address or city

5. **Hashtag block** — at the end, after 2–3 line breaks (keeps caption clean on IG)

### Voice principles
- Warm, personal, story-driven (not corporate)
- Speak like a friend sharing something exciting, not a brand selling something
- Use "you" and "your" — direct address builds connection
- Mix languages strategically for multinational/bilingual brands (e.g., Urdu phrases for a Pakistani audience)
- Exclamation marks: use sparingly (1–2 max per caption; more reads as desperate)
- Emojis: use purposefully, not decoratively; 3–7 per caption is enough

### Seasonal and occasion-based content
- Match the tone to the season: Ramadan = warmth + giving; Eid = celebration + family; winter = warmth + gifting
- Acknowledge cultural moments authentically — don't just paste in a holiday hashtag
- For religious occasions: keep content respectful and community-focused

---

## Platform Differences: Facebook vs Instagram

| Dimension | Facebook | Instagram |
|-----------|----------|-----------|
| Optimal caption length | 150–300 words | 50–150 words |
| Hashtag count | 1–3 (FB doesn't benefit from hashtag SEO the same way) | 15–25 (strategic mix) |
| Link in post | ✅ Links are clickable | ❌ Links in captions are not clickable — reference "link in bio" |
| Image format | Landscape or square preferred | Square (1:1) or portrait (4:5) preferred |
| Audience behavior | More reading, sharing, commenting | More scrolling, liking, story-tapping |
| Post frequency | 1–2/day max for organic reach | 1–2/day; stories separate |
| Video autoplay | Yes | Yes (Reels prioritized) |
| Story link | Not applicable | Available for all accounts now |

### When to post different captions per platform
- If the caption references a "link in bio" — IG only, or add FB-specific CTA instead
- If the caption is very long — consider shortening for IG
- If the post only makes sense with the image — IG-native; on FB, add more text context
- Most of the time: same caption works fine for both

---

## Hashtag Strategy

### The 3-bucket system

| Bucket | Count | Size | Purpose |
|--------|-------|------|---------|
| Brand hashtags | 3–5 | Any | Always-on brand presence (e.g., `#BrandName`, `#BrandNamePK`) |
| Niche hashtags | 8–12 | 50K–500K posts | Reach your core audience |
| Location hashtags | 3–5 | 10K–500K posts | Capture local discovery |

**Total:** 15–25 hashtags on IG (sweet spot); 1–3 on FB

### Hashtag research process
1. Search the brand's own niche + location on IG Explore (look at top posts)
2. Check what hashtags competitors / similar brands use
3. Use web_search: "{NICHE} Instagram hashtags 2025" for trending sets
4. Avoid: super-broad tags (>5M posts — too competitive), banned tags, irrelevant tags
5. Rotate the niche hashtag set every 2–4 weeks to avoid being shadow-filtered

### Placement
- Instagram: put hashtags after 3–5 blank lines at the end of the caption, or in first comment
- Facebook: embed 1–3 naturally in caption text

---

## Approval Workflow

### The golden rule
**Never publish anything without explicit approval.** This is a feature, not a limitation — it keeps the brand owner in control while the agent handles 90% of the work.

### Presenting a draft
Always present drafts in this format:

```
📝 DRAFT — {Platform} | {Time Slot / Occasion}

{CAPTION TEXT}

---
📸 Suggested image: {brief description or Google Drive link}
Hashtags: {hashtag block}

Reply APPROVE to publish, or send your revisions.
```

### Approval signals (publish immediately)
| Signal | Example |
|--------|---------|
| "APPROVE" | "APPROVE" |
| "GO" | "Go", "GO AHEAD" |
| "Post it" | "Post it", "Publish this" |
| "Yes" in reply to publish question | Agent: "Shall I publish?" → Team: "Yes" |
| Thumbs up emoji + context | "👍 publish" |

### Revision signals (do NOT publish)
| Signal | Example |
|--------|---------|
| Revision request | "Change the hashtags", "Can you make it shorter?" |
| Expressing doubt | "Hmm not sure about this one" |
| New direction | "Actually let's do a different angle" |
| Silence | No response = do not publish |

### Revision workflow
1. Receive feedback
2. Redraft (keep changes minimal unless major direction change)
3. Present new draft with "REVISED:" prefix
4. Wait for approval

---

## What NEVER to Include in Published Captions

This section captures hard lessons from production.

### ❌ Draft metadata

**Never include:**
- "APPROVE / REVISE" text
- "Suggested image: …" or "Photo idea: …"
- "Note to team: …"
- "[INSERT HASHTAG BLOCK]" or other placeholders
- Draft version numbers ("v2", "Draft 3")

**Why:** In one live incident, a draft that contained "APPROVE / REVISE" instructions in the caption text was accidentally published to Facebook. The post had to be deleted and reposted. This causes confusion with followers and creates unnecessary cleanup work.

**How to prevent:**
- Always write the exact publishable caption text first
- Add all notes, suggestions, and instructions BELOW a separator (---) in your message
- Do a "final read" of the caption text alone before publishing

### ❌ Internal brand IDs or API metadata
- Post IDs, media container IDs
- Token fragments
- Internal code names or project labels

### ❌ Competitor mentions
- Unless it's a positive industry reference or collab, avoid tagging competitors
- Never make comparisons that could be seen as negative/comparative advertising

### ❌ Pricing without approval
- Never publish specific prices unless the brand owner explicitly provides them
- Prices change; incorrect pricing in posts causes customer service issues

### ❌ Promises the brand can't keep
- "Ships in 24 hours" (if shipping is not that fast)
- "Available at all locations" (if locations are limited)
- "While stocks last" (if stock is actually unlimited)

---

## Cron / Scheduled Content Guidelines

### Campaign focus must be current

If the brand is running a giveaway, all content slots must reference it. When the campaign changes, update the cron prompts.

**The problem:** If "giveaway ends March 1" is hardcoded in a cron prompt and the campaign ends, the cron will keep generating giveaway content. Campaign focus must be kept in a config file that the cron reads, not in the cron payload itself.

**The solution:**
```
# Create: memory/content-config.md
# Current campaign: Eid Collection Launch
# Active from: 2026-03-20 to 2026-04-05
# Focus: New Eid jewelry arrivals, gifting, Eid greetings
# NOT: giveaway (ended March 1)
```
Cron prompt references this file to stay current.

### Time-of-day tone matching

| Slot | Tone | Examples |
|------|------|---------|
| Morning (8–11am) | Inspiring, fresh start | "Start your day with…" |
| Afternoon (12–3pm) | Informative, feature-focused | "Did you know our…" |
| Evening (5–8pm) | Warm, community, seasonal | "As the sun sets…", Ramadan Iftar references |
| Night (9pm+) | Engaging, interactive | "Tell us in comments…", polls |

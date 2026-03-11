---
name: reddit-growth
description: >
  Grow a product or service through authentic Reddit community engagement. Use when doing Reddit outreach,
  warming up a Reddit account, finding high-intent posts, or building brand presence on Reddit. NOT for
  bulk posting or API automation.
allowed-tools: web_fetch, web_search, browser, Read, Write
---

# Reddit Growth

Authentic, community-first Reddit engagement for product and service growth. All activity is done via browser — no Reddit API, no PRAW, no automation libraries.

---

## Configuration Block

Fill this in before any session:

```
PRODUCT_NAME:        [e.g., "Trackify"]
PRODUCT_DESCRIPTION: [What it does, who it's for, key benefit — 2 sentences max]
PRODUCT_URL:         [https://...]
TARGET_SUBREDDITS:   [r/sub1, r/sub2, r/sub3]
INTENT_KEYWORDS:     [list of keywords indicating buyer intent, e.g., "looking for", "recommend", "best tool"]
ACCOUNT_AGE_DAYS:    [How many days old is the Reddit account?]
KARMA_COUNT:         [Current karma]
WARM_UP_COMPLETE:    [Yes / No — see warm-up protocol below]
```

---

## Core Rules (Non-Negotiable)

1. **Browser only** — No Reddit API, no PRAW, no headless automation libraries
2. **Post directly** — Not draft-only mode; comments go live
3. **Check subreddit rules before every single post** — Rules change; don't assume
4. **Never repeat identical replies** — Every comment is original, written for that specific post
5. **No copy-paste templates** — Use frameworks (below) as structure, not scripts
6. **Respect the 80/20 ratio** — 80% pure useful answer, 20% soft product mention at most

---

## Mode Selection

Run one of three modes each session:

| Mode | When to Use |
|------|-------------|
| **[A] Subreddit Research** | New product, don't know where to post yet |
| **[B] Account Warm-Up** | Account < 7 days old or karma < 100 |
| **[C] Engagement Session** | Warm account, ready to engage target posts |

---

## Mode A: Subreddit Research

Given a product description, find the 10 best subreddits to target.

### Process

1. Generate 10-15 search queries from PRODUCT_DESCRIPTION:
   - "[pain point] reddit"
   - "best tool for [use case] reddit"
   - "[industry] community reddit"
   - "[competitor name] reddit"

2. For each promising community found, check via `web_search`:
   - Subscriber count
   - Posts per day (activity level)
   - Subreddit rules (especially re: promotion, self-promotion, links)
   - Recent posts — are questions like yours being asked?

3. Score each subreddit:

```
SUBREDDIT EVALUATION
====================
r/[name]
Subscribers: [number]
Activity: [posts/day]
Self-promo rules: [Allowed / Restricted / Banned]
Intent density: [High / Medium / Low — how often do users ask recommendation questions?]
Fit score: [1-5]
Notes: [anything unusual about culture or rules]
```

4. Output top 10 ranked by fit score, with rules summary for each.

```
TOP 10 SUBREDDITS FOR [PRODUCT_NAME]
=====================================
Rank | Subreddit | Subscribers | Self-Promo | Fit | Notes
1    | r/...     | ...         | Allowed    | 5/5 | High intent, active Q&A
2    | r/...     | ...         | Restricted | 4/5 | Must be established member first
...
```

---

## Mode B: Account Warm-Up Protocol

**Required before any product mention.** Skipping this gets accounts banned.

### Rules
- Duration: **minimum 7 days** before any product mention
- Max **3 comments per day**
- **Zero links** in any comment
- **Zero product mentions** — not even oblique ones
- Contribute only where you have genuine knowledge

### What to Comment On
- Answer technical or practical questions in your knowledge areas
- Share opinions on topics you actually care about
- Upvote good content (builds account health)
- Stay in communities adjacent to, but not identical to, your target subreddits

### Session Log Entry (Mode B)
After each warm-up session, append to `reddit-session-log.md`:

```markdown
## [YYYY-MM-DD] — Warm-Up Day [N]
Mode: Warm-Up
Subreddits visited: r/..., r/...
Comments posted: [N] (max 3)
Topics commented on: [brief description]
Product mentioned: No
Links shared: No
Running karma: [number]
```

---

## Mode C: Engagement Session

### Step 1: Find Target Posts

Search each subreddit in TARGET_SUBREDDITS for recent posts containing INTENT_KEYWORDS.

```bash
# Browser: navigate to
https://www.reddit.com/r/[subreddit]/search/?q=[intent_keyword]&sort=new&t=week
```

Collect 10-20 candidate posts before evaluating any.

---

### Step 2: Intent Signal Scoring

Before replying to any post, score it on three signals (1-5 each):

| Signal | Score (1-5) | What to Look For |
|--------|-------------|-----------------|
| **Buying Intent** | | Are they about to make a decision? Asking for recommendations, comparing options, ready to choose? |
| **Pain Intensity** | | How frustrated or stuck are they? Words like "struggling", "can't find", "desperate", "nothing works" = high pain |
| **Fit** | | Does your product actually solve their stated problem? Be honest. |

**Threshold: Only engage if total score ≥ 9/15.**

Posts scoring < 9 get skipped. No exceptions.

```
INTENT SCORE: r/[subreddit] — "[post title snippet]"
=======================================================
Buying Intent:  [1-5] — [brief rationale]
Pain Intensity: [1-5] — [brief rationale]
Fit:            [1-5] — [brief rationale]
TOTAL:          [X/15]
Decision:       ENGAGE / SKIP
```

---

### Step 3: Red Flag Check

Before writing any reply, verify the post doesn't have these red flags:

- [ ] Bait or troll post (deliberately provocative, no genuine question)
- [ ] Polarized political/social debate (avoid entirely)
- [ ] Subreddit explicitly bans product promotion (check rules sidebar)
- [ ] OP's question has already been answered well 5+ times
- [ ] Post is > 7 days old (comment will be buried)

Any red flag = skip the post.

---

### Step 4: Check Subreddit Rules

Before the first post in any subreddit each session:

```bash
# Navigate to:
https://www.reddit.com/r/[subreddit]/about/rules/
```

Note any rules about:
- Self-promotion (is it allowed? ratio requirements?)
- Links (external links allowed?)
- Account age requirements
- Karma minimums

---

### Step 5: Write the Reply

Use the appropriate framework based on post type:

#### Framework 1: Product Recommendation Request
*"What tool do you recommend for X?"*

```
[Direct answer: name 2-3 options honestly, explain trade-offs]
[Show you understand their specific situation]
[Mention your product last, as one option among several]
[One sentence on why it might fit their use case]
[No link unless links are explicitly allowed in subreddit rules]
```

#### Framework 2: "How Do I Do X?" Question
*"How do I achieve [outcome]?"*

```
[Answer the actual question first — fully and usefully]
[Walk through the approach step by step]
[Only after fully answering: "If you want to automate part of this, [Product] handles [specific step] — saved me a lot of time on this"]
[Keep product mention to one sentence]
```

#### Framework 3: Beginner / New User Question
*"I'm new to X, where do I start?"*

```
[Validate the starting point — being new is fine]
[Give a clear learning path or resource list]
[Position your product (if relevant) as a tool they might reach for once they have basics down]
[Don't oversell — beginners who get over-sold churn and then post negative reviews]
```

#### Framework 4: Skill-Building / Learning Request
*"How do I get better at X?"*

```
[Share genuine advice from experience]
[Recommend free resources first (establishes good faith)]
[If product fits: "For the [specific advanced step], I've been using [Product] — it handles [specific thing] well"]
[Offer to answer follow-up questions — encourages engagement]
```

---

### Step 6: Frequency Caps

| Cap | Limit |
|-----|-------|
| Max promotional comments per day | 5 |
| Max promotional comments per subreddit per day | 2 |
| Minimum gap between comments | 20-30 minutes |
| Max days without non-promotional comments | 2 |

Promotional = any comment mentioning the product, even softly.

---

### Step 7: Session Report

After each engagement session, output:

```
SESSION REPORT — [YYYY-MM-DD]
==============================
Mode: Engagement
Posts evaluated: [N]
Posts engaged: [N]
Posts skipped (score < 9): [N]
Posts skipped (red flags): [N]

Subreddits covered:
- r/[name]: [N comments]
- r/[name]: [N comments]

Comments posted: [N total]
Links: [Comment permalink 1]
       [Comment permalink 2]
       ...

Karma estimate: [current karma]
```

Append to `reddit-session-log.md`:

```markdown
## [YYYY-MM-DD] — Engagement Session
Mode: Engagement
Subreddits: r/..., r/...
Posts evaluated: [N]
Posts engaged: [N]
Total comments posted: [N]
Promotional comments: [N]
Links:
- [permalink 1]
- [permalink 2]
Running karma: [number]
Warm-up day count: [N] (if still in warm-up period)
Notes: [anything notable — post that got good responses, community dynamics, etc.]
```

---

## Tone Guidelines

- **Sound like a person, not a brand** — First-person, opinions, imperfections
- **Admit trade-offs** — "It's not perfect for X, but it's solid for Y"
- **Don't open with your product** — Answer first, mention second (or not at all)
- **No marketing language** — "game-changing", "revolutionary", "seamlessly" are instant trust destroyers on Reddit
- **Match the subreddit's register** — Technical subs want precision; casual subs want conversational

---

## What Good Looks Like

✅ Reply that spends 4 sentences helping, 1 sentence mentioning product
✅ Reply that mentions no product because the fit wasn't strong enough
✅ Reply that recommends a competitor when it's genuinely better for the OP's situation
✅ Reply that gets upvoted and generates follow-up questions

❌ Reply that opens with "I built [Product] and..."
❌ Reply that is purely promotional with thin "help" wrapper
❌ Same reply posted in multiple threads
❌ Reply with tracked links or UTM parameters visible in URL

---

## Session Log File Format

Maintain `reddit-session-log.md` in the project folder:

```markdown
# Reddit Session Log — [PRODUCT_NAME]

Account created: [date]
Warm-up complete: [date / not yet]

---

## [YYYY-MM-DD] — [Mode]
[session entry]

## [YYYY-MM-DD] — [Mode]
[session entry]
```

---

## Related Skills

- **cold-email**: For outbound to non-Reddit channels
- **b2b-website-copywriter**: If Reddit growth surfaces messaging needs
- **ai-seo**: For broader GEO/AEO strategy alongside community presence

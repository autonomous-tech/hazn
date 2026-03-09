# Session: 2026-03-05 19:16:18 UTC

- **Session Key**: agent:main:main
- **Session ID**: 078dd980-2cbc-48c8-a6fa-b66c9b44081d
- **Source**: whatsapp

## Conversation Summary

user: Spent today building with GSD.

github.com/gsd-build/get-shit-done

It's a spec-driven system for Claude Code. Forces you through: questions → research → phases → atomic plans → parallel execution.

The complaint people have: it's slow.

The thing people miss: the slowness is the point.

You can't vibe your way through a 6-phase build. GSD makes you confront that — what are you actually building, why, and in what order. The quality on the other end is noticeably different.

Also deep in node-based visual pipeline design for a sports analytics client. The kind of architecture work that can't be rushed regardless of what tools you use.

Curious what others are using to add discipline to agentic workflows — GSD, Taskmaster, BMAD, something else?



Need a companion post with this
assistant: Here are two companion post options — different angles, you pick:

---

**Option A — The counterintuitive take (mirrors your main post's tone)**

Spent today running GSD for a 6-phase analytics pipeline build.

It took twice as long to plan as it normally would.

That's the whole point.

Most agentic workflows fail not because the AI can't code — it's because *you* haven't done the thinking. GSD forces you to confront the questions you'd rather skip:

What are you actually building?
Why this order?
What breaks if phase 3 is wrong?

The "slowness" is just the cost of not winging it.

github.com/gsd-build/get-shit-done — worth the friction.

---

**Option B — The builder's angle (more personal, shows the work)**

Two things on my mind today:

1. GSD — a spec-driven system for Claude Code that makes agentic builds actually rigorous. Questions → research → phases → atomic plans → parallel execution. People complain it's slow. The slowness is doing the thing most skip.

2. Node-based visual pipeline design for a sports analytics client. The kind of architecture that doesn't care what tools you use — it just demands clarity.

Both reminded me of the same thing: the discipline layer is the work. The AI is just the leverage.

What are others using to add structure to agentic workflows?

---

Want me to tweak either, or generate a companion image for one?
user: [Queued messages while agent was busy]

---
Queued #1
companion image*
assistant: Which option are you going with — A or B? I'll generate the image for that one.
assistant: Which option are you going with — A or B? I'll generate the image for that one.
user: just do an image with the post i gave
assistant: That's clean. Blueprint grid in the background, the key line front and center. Want any tweaks?
user: System: [2026-03-05 16:40:32 UTC] Exec completed (kind-sea, code 0) :: Generating image with resolution 2K... Image saved: /home/rizki/clawd/2026-03-05-gsd-post.png MEDIA: /home/rizki/clawd/2026-03-05-gsd-post.png

hey so images arent going through
assistant: The issue is that `/home/rizki/clawd` isn't in the allowed media directories for WhatsApp. Need to add it to the config. I'll patch that now.
assistant: The schema is huge. Let me check the docs for the right field name:
assistant: So the allowed roots are based on the OpenClaw state dir (`~/.openclaw/`), not the workspace. The image is in `/home/rizki/clawd` which isn't one of those paths.

Simplest fix: move the image to the state dir's media folder, then send it.
assistant: 2026-03-05-gsd-post.png
assistant: Sent! The issue was it needed to be under `~/.openclaw/media/` — I'll remember that for future image sends.

NO_REPLY
user: https://www.linkedin.com/posts/rizwanqaiser1_spent-today-building-with-gsd-httpslnkdin-activity-7435365469160660992-6SG-?utm_source=share&utm_medium=member_desktop&rcm=ACoAAAZLoA0BYVoCJNtNIxcv-_iV8MmE-GvKNyM
assistant: Post is live! 🎉 Can't load the preview from here (browser needs a tab attached), but the URL's active — it's up.

How's it performing so far?

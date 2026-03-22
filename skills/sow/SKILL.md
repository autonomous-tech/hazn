---
name: sow
description: Generate a branded Statement of Work (SoW) PDF for Autonomous Technology Inc. Use when a user provides a client name, project scope, and pricing and wants a finished SoW document. Trigger on any mention of "SoW", "statement of work", "SOW", "proposal document", "engagement document", or "client agreement". Runs a short interview, fetches the client logo, generates the HTML, and exports a PDF via Puppeteer.
---

# SoW Generator

Generates a polished, print-ready SoW PDF using the Autonomous Editorial Warmth v2 design system.

## Core Philosophy — You-View

Every SoW is written from the **client's perspective**, not Autonomous's.

| ❌ Us-view | ✅ You-view |
|---|---|
| "We will set up GTM" | "Your GTM setup includes..." |
| "We deliver a report" | "You'll receive a report..." |
| "Our team will..." | "Your project includes..." |
| "Scope of Work" | "Your Scope of Work" |
| "Investment: $4,000" | "Your Investment: $4,000" |
| "Prepared by Autonomous" | "Prepared for [CLIENT]" — listed first |

The client's logo always appears before ours. The document is made *for them*.

---

## Interview — Ask Everything in One Message

If any of the below isn't already provided, ask in a single message. Never ask in multiple rounds.

```
1. Client name?

2. Client logo — choose one:
   a) Their website URL (I'll fetch it automatically)
   b) Upload / paste a logo file
   c) Skip — use a placeholder for now

3. What's the scope? (bullet points fine — I'll expand them)

4. Total price? (USD, flat fee)

5. Payment structure? Choose one:
   a) Flat fee — 50% deposit / 50% on delivery (default)
   b) Monthly retainer — $X/mo, ongoing
   c) Hybrid — setup fee + monthly retainer
   d) Fixed term — $X/mo × N months

6. Rough timeline? (e.g. "2–3 weeks", "1 month")

7. Which pages/sections do you need?
   Always included:
   ✅ Cover
   ✅ Your Scope
   ✅ Your Deliverables + Timeline
   ✅ Your Investment + Payment Schedule
   ✅ Terms + Signatures

   Optional — include?
   □ Milestone list (good for phased or longer engagements)
   □ Stats bar (good if there are measurable outcomes to show)
   □ Quote / testimonial block
   □ Assumptions & exclusions (recommended for complex scope)
   □ CTA block on terms page (default: yes)
```

Defaults if not answered:
- Logo: fetch from URL if provided, else placeholder
- Payment split: 50/50
- Timeline: left blank until confirmed
- Optional sections: all off unless requested
- CTA block: on

---

## Workflow

### Step 1 — Interview (above)

### Step 2 — Fetch Logo

If client provided a URL:
```bash
cd ~/autonomous-proposals && node scripts/fetch-logo.js <url> <client-slug>
```
Returns path to saved file. On failure → use text placeholder, do not block.

If client uploaded a file → save to `~/hazn/logos/{slug}.ext` and use it.
If skipped → use the `.logo-placeholder` div (see `references/components.md#cover`).

See `references/logo-fetch.md` for SVG cleaning and base64 encoding.

### Step 3 — Generate HTML

Output file:
```
~/autonomous-proposals/proposals/{client-slug}-sow.html
```

Page structure — always in this order, include only selected sections:

| Page | Section | Always? |
|---|---|---|
| 1 | Cover | ✅ |
| 2 | Your Scope | ✅ |
| 3 | Your Deliverables + Timeline | ✅ |
| 4 | Milestone list | Optional |
| 4/5 | Your Investment + Payment Schedule | ✅ |
| Last-1 | Terms + Signatures | ✅ |

### Step 4 — Export PDF
```bash
cd ~/autonomous-proposals && node scripts/to-pdf.js proposals/{slug}-sow.html proposals/{slug}-sow.pdf
```

### Step 5 — Deliver
Send PDF. State page count. Mention HTML path for edits.

---

## Page Design Rules

- **Signatures always get their own page** — never share with investment table
- **Investment table + payment bar** always go together on one page
- **Terms grid** lives on the signatures page (above the sig block)
- If content overflows a fixed page, split to next page — never squeeze
- Footer page numbers: "X of Y" — update after adding optional sections

---

## Copy Rules — Quick Reference

See `references/copy-guide.md` for full patterns.

- Scope item titles: what the client *gets*, not what we *do*
- Scope descriptions: start with "Your [thing] will..." or "[Thing] gives you..."
- Section labels: "Your Scope", "Your Deliverables", "Your Investment"
- Table header: "What you're getting" not "Item"
- Total row: "Your Total" not "Total"
- Signatures: **client listed on the LEFT**, Autonomous on the right
- Meta row order: Prepared for → Prepared by → Date → Valid for

---

## Component Reference

See `references/components.md` for copy-paste HTML for every component.

| Component | Reference |
|---|---|
| Cover (with logo) | `#cover` |
| Scope list | `#scope` |
| Deliverable cards | `#cards` |
| Timeline strip | `#timeline` |
| Milestone list | `#milestones` |
| Investment table | `#investment` |
| Payment bar | `#payment` |
| Terms grid | `#terms` |
| Stats bar | `#stats` |
| Quote block | `#quote` |
| Two-col text | `#twocol` |
| CTA block | `#cta` |
| Signature block | `#signatures` |
| Status badges | `#badges` |

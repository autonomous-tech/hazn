# Audience Routing — Shared Spec

All audit skills must ask the audience question **before any data collection or report generation**. This spec defines the question, the two modes, and the rules for each.

---

## The Question

> **Who is this report for?**
>
> 1. 👔 **Business Executive** — CEO, CMO, founder, board, investor. They care about revenue, risk, and ROI. Not code.
> 2. 🔧 **Technical Team** — Dev, marketing ops, analytics engineer, SEO manager. They need implementation detail, specs, and code.
> 3. 📋 **Both** — Produce an executive summary first, then a full technical appendix.
>
> *Default: always ask. Never assume.*

---

## Executive Mode Rules

### Language — Banned Jargon

Never use these terms in executive-mode output. Replace with plain English equivalents.

| Banned term | Say instead |
|---|---|
| LCP, TBT, CLS, CWV | "page load time", "how fast the page feels", "how much the page jumps while loading" |
| 301 redirect | "automatic forwarding rule" |
| Canonical tag | "the signal that tells search engines which version of a page to index" |
| Schema markup / structured data | "structured labels that help Google display richer results" |
| robots.txt | "the instructions file that tells search engines what to read" |
| noindex | "hidden from search engines" |
| hreflang | "language/region targeting tags" |
| GTM | "tag manager" |
| GA4 | "analytics platform" |
| TLS / SSL expiry | "security certificate expires in X days" |
| HSTS, CSP, X-Frame-Options | "security headers" |
| CDN | "content delivery network" |
| HTTP/2 | "modern web protocol" |
| TTFB | "server response time" |
| INP / FID | "how quickly the page responds when tapped" |

### Section Structure (Executive Mode)

Every finding section must have **all five of these elements**:

1. **One-line headline** — states the business cost. Not a technical description. Example: *"Every slow second costs you customers — and your PK store is one of the slowest in its category."*
2. **Impact/Effort badge:**
   - 🔴 **Critical** — Fix within 1 week (revenue risk, security risk, or trust-breaking)
   - 🟠 **High** — Fix within 1 month (material conversion or visibility impact)
   - 🟡 **Medium** — Fix within 1 quarter (meaningful improvement, lower urgency)
3. **What's happening** — plain English, 2–3 sentences max. No jargon.
4. **Why it matters** — the business consequence: lost revenue, damaged trust, competitive disadvantage, compliance risk.
5. **ROI of fixing** — what measurably improves when this is resolved.
6. **Effort level** — Low / Medium / High. **No time estimates ever.** ("This takes 30 minutes" is never appropriate — time is subjective and presumptuous.)

### Section Ordering (Executive Mode)

Always order by **impact × speed of fix** — most impactful and quickest wins appear first.
Lead with the single most urgent finding (the one that would make an exec say "we need to fix this now").

### Scorecard Labels (Executive Mode)

Replace technical metric names with business-friendly equivalents:

| Technical label | Executive label |
|---|---|
| Performance Score | Site Speed |
| SEO Score | Search Visibility |
| MarTech Score | Tracking Health |
| Security Score | Data Security |
| CWV Pass Rate | Page Experience |
| Copy Quality | Message Clarity |

---

## Technical Mode Rules

### Full Detail Required

- All technical metrics with exact values (e.g., LCP: 17.7s, TBT: 2,270ms)
- Code snippets, config examples, before/after diffs
- Standard technical terminology — no need to translate
- Specific file names, tag IDs, property IDs to change
- Implementation steps in priority order (P0 / P1 / P2)

### Section Structure (Technical Mode)

Each finding: **Finding → Evidence (with data) → Root Cause → Fix (with code/config) → Priority**

---

## Both Mode

Generate in two parts:
1. **Executive Summary** (1 page) — plain English, impact/effort badges, ROI framing
2. **Technical Appendix** — full detail, implementation specs, code

Label each section clearly. The executive summary comes first.

---

## Routing Decision

| Audience | Output style | Jargon | Code examples | Time estimates |
|---|---|---|---|---|
| Executive | ROI-first, plain English, impact/effort badges | ❌ banned | ❌ hide | ❌ never |
| Technical | Detail-first, metric values, implementation steps | ✅ standard | ✅ required | ✅ optional |
| Both | Executive summary + technical appendix | mixed | in appendix only | in appendix only |

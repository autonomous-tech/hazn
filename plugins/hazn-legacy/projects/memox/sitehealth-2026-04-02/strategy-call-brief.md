# SiteHealth Strategy Call Brief — memox.io
**Date:** April 2, 2026
**Prepared by:** Autonomous Technology Inc.
**Call Duration:** 90 minutes

---

## Audit Scores at a Glance

| Audit | Score | Key Theme |
|-------|-------|-----------|
| SiteScore (SEO/AEO/GEO) | 81/100 | Strong on-site, invisible off-site |
| Revenue Leak (Attribution) | 47/100 | PostHog active — attribution gaps remain |
| ConversionIQ (CRO) | 68/100 | Great copy, thin proof layer |
| UX/UI Audit | 65/100 | Clean design, accessibility gaps |

---

## 1. Top 3 Cross-Audit Insights

### Insight 1: "Seeing intent, not outcomes"
Memox has PostHog actively tracking 14 events including demo button clicks, chat engagement, and pricing interactions — but the funnel stops short of measuring actual conversions:
- **Calendly completion is not tracked** (Revenue Leak) → demo booking intent visible, actual bookings invisible
- **Blog content is blocked in robots.txt** (SiteScore) → content can't be indexed
- **No off-site entity presence** (SiteScore) → AI platforms can't corroborate the brand
- **No UTM/campaign attribution** (Revenue Leak) → the Mar 24 traffic spike (16 DAU, 5× average) is unattributable

The foundation exists but the last mile is missing: Memox can see who clicks the demo button but not who actually books, or where they came from.

### Insight 2: "The proof gap"
Across all four audits, the same pattern emerges — insufficient third-party validation:
- **1 customer testimonial** (ConversionIQ) — competitors show 3-5+
- **No G2 or Crunchbase profile** (SiteScore) — AI engines can't cite Memox
- **No trust badges or certifications** (ConversionIQ / UX/UI) — B2B buyers need security assurance
- **No independent press coverage** (SiteScore) — zero brand awareness signals

For a product selling at $349-$799/mo to cautious equipment dealers, the proof layer must match the messaging quality.

### Insight 3: "Binary conversion path"
The only way to convert on memox.io is to book a live demo call:
- **No secondary CTA** (ConversionIQ) — no video demo, no downloadable case study
- **No email capture** (UX/UI) — visitors who aren't ready to call have no way to stay engaged
- **No analytics to measure the funnel** (Revenue Leak) — even if visitors engage, it's invisible
- **Phone number is untracked** (UX/UI + Revenue Leak) — call leads are invisible

This creates a high-commitment, low-capture funnel that loses potential leads at every stage.

---

## 2. The One Root Cause

**The demo booking funnel is incomplete.** PostHog IS installed and actively collecting data (14 events, 4 actions, 2 dashboards). The team tracks clicks, chat engagement, and pricing interactions. But the critical last step — knowing when a visitor actually *books* a demo — is missing. Without `calendly_booking_complete`:
- Cannot measure true conversion rate (only intent rate)
- Cannot calculate CAC or ROAS on any marketing spend
- Cannot attribute completed demos to traffic sources
- Cannot build a closed-loop funnel from visit → demo → deal
- The Mar 24 traffic spike (16 DAU) may have produced bookings — or none — and nobody knows

This single missing event is the linchpin: add it, and every other PostHog insight (DAU, retention, referrers, chat engagement) becomes attributable to revenue. **One event unlocks the entire measurement stack.**

---

## 3. Recommended Starting Point

**Week 1 Priority: Close the demo funnel and add attribution.**

| # | Action | Effort | Unlocks |
|---|--------|--------|---------|
| 1 | Add `calendly_booking_complete` event (Calendly postMessage listener) | Low | True conversion tracking — the #1 gap |
| 2 | Build UTM naming convention + apply to all outbound links | Low | Campaign attribution for every channel |
| 3 | Create "Marketing Funnel" dashboard in PostHog | Low | Funnel visibility: visit → CTA → Calendly → booking |
| 4 | Remove /blog/ from robots.txt (if migrated to /insights/) | 5 min | Content indexability |
| 5 | 301-redirect legacy pages (/what-is-a-unified-customer-experience/) | Low | Clean keyword targeting |
| 6 | Enable PostHog cookieless mode (`persistence: 'memory'`) | Low | GDPR/CCPA compliance without consent banner |

These 6 actions take the revenue leak score from 47/100 to an estimated 73/100 — all PostHog-native, no new platforms needed.

---

## 4. Expected ROI

**If the top 3 cross-audit issues are fixed:**

**Analytics (Revenue Leak fixes):**
- PostHog already shows ~4.1 DAU average (126 unique visitors/30 days) with a Mar 24 spike to 16 DAU
- Adding Calendly completion tracking closes the funnel — enables true CVR measurement
- UTM attribution makes every campaign dollar accountable for the first time

**Content/SEO (SiteScore fixes):**
- Unblocking blog content from robots.txt makes 15+ articles indexable
- Redirecting legacy pages stops keyword dilution
- Based on industry benchmarks for B2B SaaS with 15 indexed pages targeting long-tail keywords: estimated 200-500 monthly organic visits within 6 months (from current ~7/month)

**Conversion (ConversionIQ + UX fixes):**
- Adding a secondary conversion path (video/PDF) typically captures 15-25% of visitors who would otherwise bounce without converting
- Adding 2-3 more case studies with diverse verticals improves social proof — industry benchmark: +10-20% CVR lift for B2B landing pages
- Estimated combined impact: if Memox reaches 500 monthly visitors with a 3% CVR (up from estimated 1.5%), that's 15 demos/month vs 7.5 — doubling the pipeline

---

## 5. Questions to Ask Client on the Call

1. **"What drove the March 24 traffic spike?"** — PostHog shows DAU jumped to 16 (5× average) on March 24 and stayed elevated through March 30. Without UTMs, we can't attribute this. Was it a campaign, press mention, Product Hunt, or partner referral? This answers whether there's a repeatable channel.

2. **"How many demo bookings per month via Calendly?"** — PostHog tracks clicks and Calendly opens but not completions. The team should know from Calendly's dashboard. This establishes the baseline CVR we'll measure against once the completion event is added.

3. **"What happened to the previous site version?"** — Legacy pages (/what-is-a-unified-customer-experience/, /ai-for-customer-success-with-memox/) suggest a pivot from a broader "customer experience" product to the current equipment dealer focus. Understanding the history helps clean up SEO.

4. **"Are there other customers beyond ContainerOne willing to provide testimonials?"** — The single biggest CRO improvement is adding 2-3 more case studies. Do the customers exist?

5. **"Are paid campaigns planned?"** — No ad platform pixels are installed. If campaigns are launching soon, Meta/Google/LinkedIn pixels need to go in alongside PostHog. If not imminent, PostHog alone covers the measurement needs.

---

## Unified Roadmap Summary

### This Week (Quick Wins)
1. Add `calendly_booking_complete` PostHog event (Calendly postMessage listener)
2. Build UTM naming convention + apply to all outbound links
3. Create "Marketing Funnel" dashboard in PostHog
4. Remove /blog/ from robots.txt
5. 301-redirect legacy pages
6. Add skip navigation link (WCAG)
7. Add source citations to homepage statistics

### This Sprint (High Impact)
8. Enable PostHog cookieless mode for compliance
9. Enable PostHog Session Replay
10. Create G2 + Crunchbase profiles
11. Add trust bar below hero
12. Add secondary conversion path (video demo)
13. Add 2-3 more customer case studies
14. Add prefers-reduced-motion CSS query
15. Set up PostHog person identification (link anonymous → known on demo booking)

### Next Quarter (Strategic)
16. Build interactive ROI calculator
17. Create comparison pages (Memox vs X)
18. Launch Product Hunt
19. Build Reddit + YouTube presence
20. Target non-brand keywords in content strategy
21. Set up PostHog Feature Flags for A/B testing (CTA copy, pricing display)
22. Add ad platform pixels when campaigns launch (Meta, Google Ads, LinkedIn)
23. Pricing page redesign with cost comparison table
24. Full WCAG 2.1 AA compliance audit

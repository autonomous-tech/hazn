# SiteHealth Strategy Call Brief — memox.io
**Date:** April 2, 2026
**Prepared by:** Autonomous Technology Inc.
**Call Duration:** 90 minutes

---

## Audit Scores at a Glance

| Audit | Score | Key Theme |
|-------|-------|-----------|
| SiteScore (SEO/AEO/GEO) | 81/100 | Strong on-site, invisible off-site |
| Revenue Leak (Attribution) | 18/100 | Flying blind — zero analytics |
| ConversionIQ (CRO) | 68/100 | Great copy, thin proof layer |
| UX/UI Audit | 65/100 | Clean design, accessibility gaps |

---

## 1. Top 3 Cross-Audit Insights

### Insight 1: "Invisible to everything that matters"
Memox has invested in strong homepage copy, excellent schema markup, and a well-structured product positioning — but this investment is invisible because:
- **GA4 is not installed** (Revenue Leak) → no data on what's working
- **Blog content is blocked in robots.txt** (SiteScore) → content can't be indexed
- **No off-site entity presence** (SiteScore) → AI platforms can't corroborate the brand
- **No conversion tracking** (Revenue Leak) → marketing ROI is unmeasurable

These four issues compound: great content exists but can't be found, and even if visitors arrive, their journey is untracked.

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

**Analytics infrastructure is missing entirely.** Without GA4 or any analytics in place, Memox cannot:
- Measure which content drives traffic
- Know which pages lead to demo bookings
- Calculate CAC or ROAS on any marketing spend
- Run A/B tests to validate CRO improvements
- Measure the impact of SEO fixes

Every other recommendation in these audits (content strategy, CRO improvements, entity building) is unvalidatable until analytics exist. **This is the single dependency that gates all other progress.**

---

## 3. Recommended Starting Point

**Week 1 Priority: Install analytics and fix robots.txt.**

| # | Action | Effort | Unlocks |
|---|--------|--------|---------|
| 1 | Fix GA4 timezone → America/Chicago, currency → USD | 5 min | Correct data foundation |
| 2 | Install GTM on memox.io (add to CSP + head) | Low | All future tracking |
| 3 | Deploy GA4 via GTM | Low | Traffic, engagement, source data |
| 4 | Set up Calendly conversion event | Medium | Demo booking attribution |
| 5 | Remove /blog/ from robots.txt (if migrated to /insights/) | 5 min | Content indexability |
| 6 | 301-redirect legacy pages (/what-is-a-unified-customer-experience/) | Low | Clean keyword targeting |

These 6 actions take the revenue leak score from 18/100 to an estimated 60/100 and unblock every other recommendation.

---

## 4. Expected ROI

**If the top 3 cross-audit issues are fixed:**

**Analytics (Revenue Leak fixes):**
- Establishes baseline metrics — cannot project ROI without a baseline, but every future marketing dollar becomes accountable

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

1. **"Is PostHog actually deployed, or just whitelisted in CSP?"** — If PostHog is active (loaded via JS bundle), there may be analytics data we haven't accessed. This changes the Revenue Leak picture significantly.

2. **"What happened to the previous site version?"** — Legacy pages (/what-is-a-unified-customer-experience/, /ai-for-customer-success-with-memox/) suggest a pivot from a broader "customer experience" product to the current equipment dealer focus. Understanding the history helps clean up SEO.

3. **"How many demo bookings do you get per month currently?"** — Even without analytics, the team should have a rough sense. This establishes the baseline for all CVR projections.

4. **"Are there other customers beyond ContainerOne willing to provide testimonials?"** — The single biggest CRO improvement is adding 2-3 more case studies. Do the customers exist?

5. **"What's the current marketing spend / channel mix?"** — Understanding whether paid campaigns are running (or planned) determines urgency of ad pixel installation and attribution setup.

---

## Unified Roadmap Summary

### This Week (Quick Wins)
1. Fix GA4 timezone + currency
2. Install GTM container
3. Deploy GA4 tag
4. Remove /blog/ from robots.txt
5. 301-redirect legacy pages
6. Add skip navigation link (WCAG)
7. Add source citations to homepage statistics

### This Sprint (High Impact)
8. Set up Calendly conversion tracking
9. Set up chat engagement events
10. Create G2 + Crunchbase profiles
11. Add trust bar below hero
12. Add secondary conversion path (video demo)
13. Add 2-3 more customer case studies
14. Add prefers-reduced-motion CSS query
15. Build UTM naming convention

### Next Quarter (Strategic)
16. Build interactive ROI calculator
17. Create comparison pages (Memox vs X)
18. Launch Product Hunt
19. Build Reddit + YouTube presence
20. Target non-brand keywords in content strategy
21. Implement full consent management
22. Add ad platform pixels as campaigns launch
23. Pricing page redesign with cost comparison table
24. Full WCAG 2.1 AA compliance audit

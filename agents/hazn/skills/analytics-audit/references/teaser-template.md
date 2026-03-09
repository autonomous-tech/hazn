# Teaser Report — Section-by-Section Content Template

This is the narrative template for the teaser prospect report. Each section describes the content structure, data sources, tone, and CTA approach.

---

## Section 1: Hero

**Component:** Full-bleed section with site screenshot, overall grade, and personalized headline.

**Content:**
- Desktop screenshot of the homepage (Base64-embedded)
- Overall site grade (large `.grade-badge--lg`)
- Dynamic headline: "{Company Name}'s Digital Health Report"
- Subhead: "A complimentary analysis of your website's performance, technology, SEO, copy, UX, and conversion readiness."
- Audit date and URL

**Data sources:** `playwright_data.json` (screenshot), all data (grade calculation)

**Tone:** Professional, confident. This isn't a free tool — this is a professional assessment.

---

## Section 2: Site Health Scorecard

**Component:** Grid of 5 `.grade-badge` cards showing dimension grades.

**Content:**
Five grade badges in a responsive grid:

| Badge | Label | Score Source |
|-------|-------|-------------|
| Performance | "Performance" | Lighthouse performance × 100 |
| SEO | "SEO & Visibility" | Lighthouse SEO + meta completeness + structured data |
| MarTech | "MarTech Maturity" | MarTech maturity formula |
| Copy & UX | "Copy & UX" | Average of Copy + UX + CRO grades |
| Security | "Security" | Security headers grade mapping |

Below the grid: One-sentence summary of the biggest opportunity.

**Data sources:** `pagespeed.json`, `site_inspection.json`, `teaser_data.json`, inline analysis

---

## Section 3: Core Web Vitals

**Component:** `.cwv-display` three-column gauge.

**Content:**
Three Core Web Vitals with values, thresholds, and pass/fail status:

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP | ≤ 2.5s | ≤ 4.0s | > 4.0s |
| INP (or FID) | ≤ 200ms | ≤ 500ms | > 500ms |
| CLS | ≤ 0.1 | ≤ 0.25 | > 0.25 |

Show both field data (real user, if available from CrUX) and lab data.

Below gauges:
- "What this means for SEO:" — explain Google uses CWV as a ranking signal
- Specific recommendation based on worst metric

**Data sources:** `pagespeed.json` → `mobile.core_web_vitals` and `mobile.lighthouse.lab_metrics`

---

## Section 4: MarTech Stack Inventory

**Component:** `.tool-card` grid with health dots.

**Content:**
Grid of detected tools, organized by category:

| Category | What to show |
|----------|-------------|
| Tag Management | GTM containers, TMS |
| Analytics | GA4, other analytics |
| Ad Pixels | Facebook, Google Ads, Bing, TikTok, etc. |
| CRM & Email | HubSpot, Klaviyo, Mailchimp, etc. |
| Session Recording | Hotjar, Clarity, FullStory |
| Consent & Privacy | CMP, consent mode |
| Other | Chat, call tracking, A/B testing |

Each tool shows:
- Name + ID (if detected)
- Green dot = detected and likely healthy
- Amber dot = detected but has issues (e.g., dual loading)
- Red dot = critical issue or missing essential tool
- Gray dot = not detected (mark as gap if it should be there)

Below the grid: Summary of redundancies and missing essentials.

**Data sources:** `site_inspection.json`

---

## Section 5: Tracking & Privacy

**Component:** `.callout` cards for compliance status.

**Content:**
- Consent mode configuration (default values for all 5 signals)
- CMP/cookie banner detection
- Cookie inventory summary
- GDPR/CCPA compliance flags
- "What's at risk:" callout if consent mode is misconfigured or CMP is missing

**Data sources:** `site_inspection.json` → `consent`, `cookies`

**Urgency lever:** Legal compliance risk. "Without proper consent management, your ad platforms may be receiving signals they shouldn't — or missing signals they need."

---

## Section 6: SEO & Structured Data

**Component:** Mixed — data table + findings list.

**Content:**
- Meta tags: title, description, canonical, OG tags — present/missing/issues
- Structured data: JSON-LD types found, count, coverage
- Sitemap: URL count, freshness (lastmod), sub-sitemaps
- Robots.txt: AI crawler blocks, crawl rules
- AI readiness: Which AI crawlers are blocked/allowed

**Data sources:** `site_inspection.json` (meta, structured data), `teaser_data.json` (robots, sitemap)

**Urgency lever:** "AI search is growing 300%+ — are you visible to AI answer engines?"

---

## Section 7: Performance & Script Bloat

**Component:** Data table + stat strip.

**Content:**
- Total page weight breakdown (by resource type)
- Third-party script inventory (top 10 by blocking time)
- Total third-party count and combined blocking time
- Performance opportunities (top 5, with estimated savings in ms)
- Specific script recommendations

**Data sources:** `pagespeed.json` → `mobile.lighthouse.third_party`, `opportunities`, `page_weight`

---

## Section 8: Security & Infrastructure

**Component:** Score card + findings list.

**Content:**
- Security headers grade (A–F) with checklist
- Individual header status (present/missing for each of the 9 headers)
- SSL certificate status, issuer, days until expiry
- Technology stack: CMS, framework, CDN, server
- DNS resolution status

**Data sources:** `teaser_data.json` → `security`, `ssl`, `technology`

---

## Gate 1: Organic Search Intelligence

**Component:** `.teaser-gate` with blurred background.

**Content structure:**
1. Lock icon (🔒)
2. Title: "Unlock Your Organic Search Intelligence"
3. Hook: "Your sitemap contains {N} URLs. But which ones actually drive traffic? Which keywords are you ranking for — and which are you losing?"
4. Preview items (visible, from data we have):
   - "Your sitemap has {N} URLs — but are they the right ones?"
   - "We detected {N} AI crawler blocks in your robots.txt" (or "No AI crawler blocks detected")
   - One SEO finding from Section 6
5. What the full analysis delivers (bullet list):
   - Top 1,000+ ranking queries with traffic data
   - Keyword cannibalization detection
   - High-impression / low-CTR quick wins
   - Brand vs non-brand traffic split
   - Content refresh opportunities
6. CTA button: "Book a 15-min walkthrough →" → Calendly URL

---

## Section 9: Copy Audit

**Component:** Section title + `.audit-card` findings.

**Content structure:**
1. Section grade (`.grade-badge`)
2. Brief methodology note: "Analyzed using your site's page structure, headings, CTAs, and content across {N} pages."
3. Findings as `.audit-card` items (6–10 cards), covering:
   - **Hero headline analysis:** Is it specific? Does it use a proven framework? Length?
   - **Value proposition:** Clear within 5 seconds? States what/for whom/why different?
   - **CTA inventory:** List all CTAs found — score each on action-orientation, placement, prominence
   - **Social proof:** Testimonials present? Attributed? Specific and quantified?
   - **Pain point articulation:** Does copy address problems before presenting solutions?
   - **Readability:** Paragraph length, jargon level, scanability
   - **Messaging consistency:** Do page headings tell a coherent story?
   - **Trust language:** Guarantees, risk reversal, credibility claims

Each card has an icon (critical/warning/good/info) and specific, actionable text referencing actual content from the site.

**Data sources:** `playwright_data.json` → `pages[].snapshot_desktop`, `pages[].snapshot_mobile`

**Critical instruction:** EVERY finding must reference specific content from the actual site. Never write generic advice like "improve your headline." Instead: "Your hero headline '{actual headline}' is {N} words — consider shortening to 6-8 words with a specific outcome."

---

## Section 10: UX Audit

**Component:** Section title + `.audit-card` findings.

**Content structure:**
1. Section grade (`.grade-badge`)
2. Brief methodology note
3. Findings as `.audit-card` items (6–10 cards), covering:
   - **Visual hierarchy:** Does the eye flow logically? Is the primary action obvious?
   - **Navigation analysis:** Depth, clarity, number of top-level items, mobile menu
   - **Above-the-fold:** What loads first? Value prop + CTA visible?
   - **Mobile experience:** Tap target sizes, text readability, layout quality
   - **Information architecture:** Can users find what they need? Logical grouping?
   - **Accessibility basics:** Heading hierarchy (H1 → H2 → H3), alt text coverage, ARIA usage
   - **Design consistency:** Typography, spacing, color usage patterns
   - **Loading experience:** LCP element location, CLS issues

**Data sources:** `playwright_data.json` (snapshots + screenshots), `pagespeed.json` (LCP, CLS)

---

## Section 11: CRO Audit

**Component:** Section title + `.audit-card` findings.

**Content structure:**
1. Section grade (`.grade-badge`)
2. Brief methodology note
3. Findings as `.audit-card` items (6–10 cards), covering:
   - **Conversion path:** Steps from landing to primary conversion
   - **CTA placement:** Above-fold present? Frequency per scroll depth? Sticky?
   - **Form analysis:** Field count, required fields, labels, UX
   - **Trust signals:** Client logos, testimonials, review badges, certifications
   - **Social proof placement:** Is it near decision points?
   - **Urgency/scarcity:** Limited time offers, countdown timers
   - **Risk reversal:** Guarantees, free trials, "no CC required"
   - **Exit intent:** Popups, chat widgets, secondary CTAs
   - **Pricing transparency:** Is pricing visible and clear?

**Data sources:** `playwright_data.json` (snapshots + screenshots)

---

## Gate 2: Analytics Deep-Dive

**Component:** `.teaser-gate`

**Content structure:**
1. Lock icon (🔒)
2. Title: "See What Your Analytics Is Really Telling You"
3. Hook: "We found {N} tracking tags on your site. But tags installed ≠ tags working."
4. Preview items:
   - "Common findings: inflated conversions feeding ad bidding, 40-70% of revenue invisible to ad platforms"
   - Blurred score mockup: "GA4 Implementation Score: ??/100"
   - Blurred score mockup: "Attribution Architecture Score: ??/100"
5. What the full analysis delivers (bullet list):
   - GA4 event tracking completeness audit
   - Conversion accuracy (inflated signals detection)
   - Attribution architecture review
   - Ad platform signal loss quantification
   - 90-day implementation roadmap with ROI projections
6. CTA: "Book your audit walkthrough →" → Calendly URL

---

## Gate 3: Paid SEO Engagement

**Component:** `.teaser-gate`

**Content structure:**
1. Lock icon (🔒)
2. Title: "Validated Content Strategy & Execution"
3. Hook: "Your site ranks for content, but are you ranking for the RIGHT keywords?"
4. Preview items:
   - Reference 2-3 SEO findings from Section 6
   - Social proof: "For one client, we identified 4,800–8,500 clicks/month in unrealized organic traffic and 134 keyword cannibalization issues."
5. What the paid engagement delivers:
   - Validated keyword research (Ahrefs/SEMrush, not estimates)
   - Competitive gap analysis
   - GEO/AEO audit (AI answer engine optimization)
   - Content calendar + actual content writing
   - Schema markup implementation
   - Ongoing monthly execution
6. CTA: "Book your strategy call →" → Calendly URL

---

## Final CTA Section

**Component:** Full-width dark section with centered CTA.

**Content:**
- Headline: "Ready to Turn These Insights Into Revenue?"
- Subhead: "Book a 15-minute walkthrough of your report. We'll show you the quick wins and map out a plan."
- Primary CTA button: "Book Your Free Walkthrough →" → Calendly URL
- Secondary text: "Or email us at [email]"
- Company branding: "Report generated by Autonomous Technologies"

---

## Writing Style Guide

1. **Be specific, not generic.** Every finding must reference actual data from the site. "Your Lighthouse performance score is 34/100" not "your site could be faster."
2. **Lead with impact.** Start findings with what it costs the business, not what the technical issue is.
3. **Use numbers.** Quantify everything possible — scores, counts, percentages, dollar estimates.
4. **Create urgency without fear-mongering.** Present facts clearly. Let the data speak.
5. **One CTA per gate, one message per gate.** Don't dilute the upsell with too many options.
6. **Professional, not salesy.** This is a technical assessment from experts, not a marketing flyer.
7. **Personalize.** Use the company name, reference their specific tools, mention their CMS by name.

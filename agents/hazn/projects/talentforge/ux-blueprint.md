# TalentForge — UX Blueprint
**Version:** 1.0  
**Phase:** UX Architecture  
**Audience:** Copywriter, Wireframer, Developer  

---

## 1. SITE ARCHITECTURE

```
talentforge.io/
├── / (Homepage)                         [P0] — Primary conversion entry point
├── /how-it-works                        [P0] — Process clarity, objection removal
├── /engineers                           [P0] — Gated talent directory (primary CTA destination)
│   └── /engineers/[profile-slug]        [P0] — Individual engineer profile (post-gate)
├── /pricing                             [P0] — Tier 1 vs Tier 2 hiring model comparison
├── /get-started                         [P0] — Contact / intake form (secondary CTA destination)
├── /for-companies                       [P1] — Buyer-specific landing page
├── /for-agencies                        [P1] — Agency partner landing page
├── /about                               [P1] — Credibility + team
├── /blog                                [P2] — SEO / thought leadership (optional Phase 2)
└── /legal                               [P2] — Privacy, Terms
    ├── /legal/privacy
    └── /legal/terms
```

**Navigation (Primary):**
- Logo → /
- How It Works
- Browse Engineers (accent button)
- Pricing
- Talk to Our Team (CTA button, always visible)

**Navigation (Secondary/Footer):**
- For Companies | For Agencies | About | Blog | Privacy | Terms

**Gate Logic:**
- `/engineers` directory: visible teaser cards (name redacted, role/skills/rate visible) → "Unlock Full Profile" triggers email gate (name + company email + role)
- Post-gate: Full profile view + "Request Introduction" CTA

---

## 2. PAGE BLUEPRINTS

---

### 2.1 HOMEPAGE

**Goal:** Convert first-time visitors (CTOs, Heads of Engineering) into either profile browsers or conversation requests within one scroll.

**Viewport assumption:** Desktop-primary, but mobile must convert independently.

---

#### SECTION 1 — HERO
**Purpose:** Communicate the core value proposition in under 5 seconds. Establish urgency and specificity. Drive dual CTA.

**Layout:** Full-viewport-height, centered or left-aligned content, right side: engineer profile card teaser or ambient tech visualization.

**Content blocks:**
- **Eyebrow label:** `Data Engineers & AI Engineers — Pre-Screened, Pakistan-Based`
- **H1 (primary):** `Hire Elite Data & AI Engineers in Days.`
- **H2 (subheading):** `TalentForge is the only platform exclusively dedicated to pre-screened Data Engineers and AI Engineers for US & UK tech companies. No generalist agencies. No wasted months.`
- **Dual CTA:**
  - Primary: `Browse Engineer Profiles →` (filled, accent color)
  - Secondary: `Talk to Our Team` (outlined or ghost)
- **Social proof anchors (below CTAs):** 3 inline stats — e.g., `47+ Engineers Placed` · `< 7 Days to First Interview` · `Series A–C Clients`
- **Trust micro-copy:** `No commitment to browse. Profiles available immediately after signup.`

**Design notes:**
- Dark navy background, white type, electric blue or teal accent
- Right panel: animated or static engineer profile card showing role, skills, availability badge ("Available Now" in green)
- Subtle grid/dot pattern texture in background for tech feel

---

#### SECTION 2 — PROBLEM AGITATION
**Purpose:** Mirror the CTO's frustration. Make them feel understood before pitching anything. Validates the pain before offering relief.

**Layout:** 2–3 column pain point cards OR single-column bold statements with left border accent.

**Content blocks:**
- **Section label:** `Sound Familiar?`
- **H2:** `Generic staffing agencies don't speak data. And you're paying the price.`
- **Pain points (3–4 items):**
  1. "You post on LinkedIn. You get 200 CVs. 3 are relevant."
  2. "The recruiter calls them 'data professionals.' They've touched one Airflow pipeline."
  3. "3 months later, you're back to square one — and behind on your roadmap."
  4. "You need someone who knows dbt, Spark, and vector databases. Not someone who 'knows Python.'"
- **Transition line:** `There's a better way — built specifically for this problem.`

**Design notes:**
- Dark cards with subtle red/orange left border accents on each pain point
- Slightly lower contrast background than hero to create visual separation

---

#### SECTION 3 — SOLUTION (4 PILLARS)
**Purpose:** Reframe TalentForge as the direct answer to each pain. Build credibility through specificity.

**Layout:** 4-column icon cards (desktop), 2-col (tablet), 1-col stack (mobile)

**Content blocks:**
- **Section label:** `The TalentForge Difference`
- **H2:** `Built for Data & AI. Nothing else.`
- **Pillar cards:**
  1. **Specialist-Only** — "Every engineer in our pool is a Data or AI specialist. No generalists, no full-stack fillers."
  2. **Pre-Screened** — "Technical assessments, live coding reviews, and reference checks — done before you ever see a profile."
  3. **Fast** — "Go from brief to first interview in under 7 days. Our average is 4."
  4. **Pakistan-Based, Global-Ready** — "Elite engineers in Lahore, Karachi, Islamabad. Fluent in English, aligned to US/UK timezone overlap."

**Design notes:**
- Icon per pillar (minimal, line-art style)
- Cards on slightly elevated surface (subtle border or shadow)
- Accent color on icon + card number

---

#### SECTION 4 — HOW IT WORKS (CONDENSED)
**Purpose:** Remove process anxiety. Show the path from "I'm interested" to "engineer is onboarded" is short and clear.

**Layout:** 3-step horizontal flow with connecting line (desktop), vertical timeline (mobile)

**Content blocks:**
- **Section label:** `The Process`
- **H2:** `From brief to hire in 3 steps.`
- **Steps:**
  1. **Share Your Brief** — "Tell us the role, stack, and timeline. Takes 10 minutes."
  2. **Meet Your Shortlist** — "We surface 3–5 pre-matched profiles within 48 hours."
  3. **Hire with Confidence** — "Interview, select, and onboard. We handle contracts and compliance."
- **CTA below steps:** `See How It Works In Detail →` (links to /how-it-works)

**Design notes:**
- Step number in large accent color behind step label
- Connecting dotted line between steps (desktop)
- Estimated time stamps under each step for cognitive ease

---

#### SECTION 5 — SOCIAL PROOF
**Purpose:** Eliminate skepticism. Show real outcomes from real companies. This is where trust tips from "interested" to "I'll take action."

**Layout:** Metrics bar + testimonial cards (2–3 cards, carousel on mobile)

**Content blocks:**
- **Metrics bar (3–4 stats):**
  - `47+ Engineers Placed`
  - `4.2 Days Avg. Time to Interview`
  - `92% Retention Rate at 6 Months`
  - `Series A–C Companies`
- **Testimonials (2–3):**
  - Quote + name + role + company logo (or company type if logos unavailable)
  - Example: *"We'd tried 3 agencies. TalentForge sent us 4 profiles in 48 hours. We hired two of them."* — Head of Data, SaaS startup, UK
- **Logo bar (if available):** Client company logos or "As trusted by teams at..." with logo strip

**Design notes:**
- Metrics in large, bold type on contrasting background band
- Testimonial cards: avatar placeholder + quote marks in accent color
- Logo bar: greyscale logos, subtle opacity

---

#### SECTION 6 — HIRING MODELS (TIER 1 vs TIER 2)
**Purpose:** Pre-qualify visitors and remove pricing ambiguity. Let CTOs self-select their engagement model before reaching the pricing page.

**Layout:** 2-column comparison cards, toggle or side-by-side

**Content blocks:**
- **Section label:** `Hiring Models`
- **H2:** `Two ways to hire. Both built for speed.`
- **Tier 1 Card — Direct Hire / Contract:**
  - Headline: "Direct Placement"
  - For: Companies hiring full-time or long-contract engineers
  - Key features: 3 bullet points
  - CTA: `Learn More →` (→ /pricing#tier-1)
- **Tier 2 Card — Agency White-Label:**
  - Headline: "Agency Partnership"
  - For: Staffing agencies needing specialist overflow capacity
  - Key features: 3 bullet points
  - CTA: `Learn More →` (→ /pricing#tier-2 or /for-agencies)
- **Note:** "Not sure which fits? Talk to us." → /get-started

**Design notes:**
- Tier 1 card: highlighted (primary, slightly larger or bordered in accent)
- Tier 2 card: secondary treatment
- Small "Most Popular" badge on Tier 1

---

#### SECTION 7 — AGENCY CALLOUT
**Purpose:** Capture a secondary audience (staffing/recruiting agencies) without confusing the primary CTO audience. Brief, distinct, with clear routing.

**Layout:** Full-width band, asymmetric — icon/illustration left, text right

**Content blocks:**
- **Label:** `For Agencies`
- **H3:** `Running a staffing agency? We're your secret weapon.`
- **Body:** "Add specialist Data & AI capacity to your bench overnight. White-label partnerships available."
- **CTA:** `Explore Agency Partnership →` (→ /for-agencies)

**Design notes:**
- Visually distinct background (different shade of dark) to signal audience shift
- Smaller text weight — supporting role, not hero

---

#### SECTION 8 — FINAL CTA BLOCK
**Purpose:** Catch every visitor who scrolled to the bottom. Provide a clean, no-friction exit toward action.

**Layout:** Full-width centered, high contrast (light or accent background)

**Content blocks:**
- **H2:** `Ready to stop settling for generalists?`
- **Subtext:** "Browse pre-screened Data & AI engineers right now — or talk to our team to get matched in 48 hours."
- **Dual CTA:**
  - Primary: `Browse Engineer Profiles →`
  - Secondary: `Talk to Our Team`
- **Reassurance line:** `No commitment. No recruiter pitch. Just profiles.`

---

### 2.2 HOW IT WORKS PAGE

**Goal:** Remove process anxiety completely. Answer every "but how does this actually work?" question before the CTO has to ask.

**URL:** `/how-it-works`

---

#### SECTION 1 — PAGE HERO
- **H1:** `From Brief to Hire in Under 7 Days.`
- **Subheading:** `Here's exactly how TalentForge works — from your first message to your new engineer's first commit.`
- **No CTA here** — let curiosity carry the scroll

---

#### SECTION 2 — THE 3-STEP PROCESS (EXPANDED)
**Purpose:** Detailed breakdown of each step with timelines and what the client actually does vs. what TalentForge does.

**Layout:** Vertical timeline, alternating left/right panels (desktop), stacked (mobile)

**Step 1: Share Your Brief**
- What you do: Fill out a 10-minute intake form — role, required stack, timeline, engagement type
- What we do: Intake reviewed by a specialist (not a bot). Brief validated within 2 hours.
- Timeline: Day 0
- Micro-detail: "We'll ask about your stack, not just 'years of experience.'"

**Step 2: Receive Your Shortlist**
- What you do: Review 3–5 matched profiles (full CVs, technical assessment scores, availability)
- What we do: Match from active pool, surface only candidates who pass our 4-stage screen
- Timeline: 24–48 hours
- Micro-detail: "Every profile comes with our screening notes — why we matched them to you."

**Step 3: Interview & Select**
- What you do: Run your technical interviews (we can facilitate if needed)
- What we do: Coordinate scheduling, provide background context, support offer process
- Timeline: 3–5 days
- Micro-detail: "Most clients run 1–2 interviews. No 6-round processes needed — we've done the work."

**Step 4: Onboard with Support**
- What you do: Onboard your new engineer
- What we do: Handle contracts, compliance, payroll (for contract roles), 30-day check-in
- Timeline: Day 7–14

---

#### SECTION 3 — OUR SCREENING PROCESS
**Purpose:** Build confidence in quality. CTOs are skeptical — detail is the antidote.

**Layout:** 4-step horizontal process (our internal screening, not theirs)

**Steps:**
1. Application Review — skills, experience, portfolio check
2. Technical Assessment — role-specific test (Spark/dbt/ML pipelines etc.)
3. Live Technical Interview — 90-minute deep-dive with our senior engineers
4. Reference & Background Check — 2 professional references, identity verified

**Callout:** "Less than 12% of applicants make it into our pool."

---

#### SECTION 4 — WHAT YOU GET IN A PROFILE
**Purpose:** Preview the profile artifact. Reduce anxiety about the gated directory.

**Layout:** Annotated profile card mockup

**Profile card includes:**
- Role + seniority level
- Core skills (dbt, Airflow, Spark, Python, etc.)
- Technical assessment score
- Availability (date + timezone)
- Engagement type (contract / full-time / both)
- Rate range
- Language proficiency
- Our screening notes (1 paragraph)

**CTA:** `See Live Profiles → Browse Engineers`

---

#### SECTION 5 — FAQ
**Purpose:** Handle remaining objections inline. Prevent bounce to Google.

**Format:** Accordion

**Questions:**
1. "What if I don't like any of the shortlisted profiles?"
2. "How does the pricing work — what do I pay and when?"
3. "Do the engineers work in our timezone?"
4. "What happens if it doesn't work out after hire?"
5. "Can we trial an engineer before committing?"
6. "How is this different from Upwork or Toptal?"

---

#### SECTION 6 — CTA BLOCK
- **H2:** `Ready to see who's available?`
- **CTA:** `Browse Engineer Profiles →`

---

### 2.3 PRICING PAGE

**Goal:** Communicate value, pre-qualify by tier, and route to action without a sales call requirement.

**URL:** `/pricing`

---

#### SECTION 1 — PAGE HERO
- **H1:** `Transparent Pricing. Two Paths to Hire.`
- **Subheading:** `Whether you're hiring direct or running an agency, here's exactly what you get — and what it costs.`

---

#### SECTION 2 — TIER COMPARISON (ANCHOR: #tier-1 and #tier-2)
**Layout:** 2-column card comparison (sticky on scroll for comparison on desktop)

**Tier 1 — Direct Hire (for companies)**
- **Label:** Most Popular
- **Who it's for:** Series A–C companies hiring Data/AI engineers directly
- **Engagement types:** Contract (3–12 month) or Full-Time Placement
- **What's included:**
  - Unlimited profile access (post-gate)
  - Shortlist of 3–5 matched profiles within 48 hours
  - Full screening notes per candidate
  - Interview facilitation
  - Contract management (for contractors)
  - 90-day replacement guarantee
- **Pricing model:** Success fee on placement (percentage of first-year salary / contract value) OR monthly retainer for ongoing access
- **CTA:** `Get Started →` (→ /get-started?tier=1)

**Tier 2 — Agency White-Label**
- **Who it's for:** Staffing/recruiting agencies needing specialist Data & AI capacity
- **What's included:**
  - White-label profile access
  - Bulk shortlisting (10+ roles simultaneously)
  - Dedicated account manager
  - Custom SLA agreements
  - Confidential partnership (no TalentForge branding on profiles)
- **Pricing model:** Volume-based pricing, monthly retainer + placement fee
- **CTA:** `Talk to Our Team →` (→ /get-started?tier=2)

---

#### SECTION 3 — PRICING FAQ
- "Do I pay upfront?" 
- "What's the replacement guarantee?"
- "Can I hire multiple engineers simultaneously?"
- "Is there a free trial or browsing period?"

---

#### SECTION 4 — TRUST BAR
- 90-day guarantee badge
- Client count stat
- Security/compliance note ("All engineers verified and background checked")

---

#### SECTION 5 — CTA
- **H2:** `Still have questions about pricing?`
- **CTA:** `Talk to Our Team →`

---

### 2.4 CONTACT / GET STARTED PAGE

**Goal:** Convert warm, qualified visitors into actionable leads. Minimize form friction while capturing enough to route intelligently.

**URL:** `/get-started`

---

#### SECTION 1 — PAGE HERO
- **H1:** `Let's Find Your Next Engineer.`
- **Subheading:** `Tell us what you're looking for. We'll have a shortlist ready within 48 hours.`

---

#### SECTION 2 — DUAL ROUTING (above the form)
**Layout:** 2 cards with clear routing — let users self-identify before the form loads

- Card A: **I'm a company looking to hire** → shows Company intake form
- Card B: **I'm an agency looking to partner** → shows Agency intake form

*This prevents one generic form that fits no one.*

---

#### SECTION 3 — COMPANY INTAKE FORM
**Fields (progressive — show in groups):**

Group 1 (Basic):
- Your name
- Company email (no Gmail/Yahoo)
- Company name
- Role you want help with (dropdown: Data Engineer, AI/ML Engineer, Data Architect, Analytics Engineer, Other)

Group 2 (Role Detail):
- Required skills / tech stack (freetext + tag chips)
- Seniority level (Mid / Senior / Lead / Principal)
- Engagement type (Contract / Full-time / Either)
- Timeline (ASAP / 1 month / 3 months)

Group 3 (Context):
- Approx. budget range (optional — but helps us match better)
- How did you hear about us?

**Submit CTA:** `Request My Shortlist →`

**Post-submit:**
- Confirmation message: "We'll review your brief and be back within 2 hours. Check your inbox."
- Optional: Book a call slot (Calendly embed) for those who want faster contact

---

#### SECTION 4 — TRUST SIDEBAR (desktop: right column, mobile: below form)
- "What happens next" 3-step mini-process
- Testimonial quote
- Response time badge: "Average response: < 2 hours"
- Privacy note: "Your details are never shared without your permission."

---

## 3. USER FLOWS

---

### 3.1 CTO JOURNEY — Problem-Aware, Evaluating Options

```
Entry: Google Ad / LinkedIn Post / Referral
  ↓
Homepage → Hero (reads H1, H2)
  ↓
Scrolls to Problem section → "Yes, this is me"
  ↓
Reads Solution pillars → builds credibility
  ↓
[Decision Point A] — Confident CTO:
  → Clicks "Browse Engineer Profiles" → /engineers (gate)
  → Fills gate form (name + company email + role)
  → Browses profiles
  → Clicks "Request Introduction" on profile → /get-started (pre-filled)
  → Submits intake → awaits shortlist

[Decision Point B] — Skeptical CTO:
  → Clicks "How It Works" (nav or section link)
  → /how-it-works → reads process + screening detail
  → Reads FAQ → objections cleared
  → Clicks "Browse Engineer Profiles" → gate → profiles
  → OR clicks "Talk to Our Team" → /get-started

[Decision Point C] — Pricing-First CTO:
  → Clicks "Pricing" in nav
  → /pricing → reads Tier 1
  → Clicks "Get Started" → /get-started?tier=1
  → Submits intake
```

**Key insight:** Every path leads to the same two endpoints: engineer gate OR intake form. The site never dead-ends.

---

### 3.2 AGENCY JOURNEY — Staffing Agency Evaluating White-Label Partnership

```
Entry: Direct outreach / referral / Google search "white label data engineers"
  ↓
Homepage → Hero (skims, notices "For Agencies" in nav)
  ↓
Scrolls to Agency Callout section → "This is for me"
  ↓
Clicks "Explore Agency Partnership" → /for-agencies
  ↓
Reads value prop, capacity model, white-label details
  ↓
Clicks "Talk to Our Team" → /get-started
  ↓
Selects "I'm an agency" card → Agency intake form
  ↓
Submits → dedicated account manager follow-up

Alternative:
  ↓
Homepage → Pricing → Tier 2 card → "Talk to Our Team" → /get-started
```

---

## 4. CONVERSION PATH DESIGN

### Primary Conversion Path (Homepage → Profile Gate → Intake)
```
/ → /engineers (gate fills: name, company email, role) → /engineers/[profile] → /get-started
```
- Gate is frictionless (3 fields max)
- Profile unlocks immediately (no email confirmation required to view)
- "Request Introduction" pre-fills company name and role into intake form

### Secondary Conversion Path (Homepage → Get Started directly)
```
/ → /get-started (for CTOs who don't need to browse first)
```
- "Talk to Our Team" CTA present in nav at all times
- Particularly useful for CTOs who come from referral and already trust the brand

### Tertiary Conversion Path (How It Works → Browse → Intake)
```
/how-it-works → /engineers → /get-started
```
- Used by skeptical buyers who need process confidence before committing

### Micro-Conversion Events (tracked for analytics/retargeting):
1. Gate form fill on /engineers
2. Individual profile view
3. "Request Introduction" click
4. /get-started page view
5. Intake form started (partial)
6. Intake form completed (primary conversion)
7. Calendly booking post-form

---

## 5. RESPONSIVE / MOBILE CONSIDERATIONS

### Navigation (Mobile)
- Hamburger menu below 768px
- "Browse Engineers" and "Talk to Our Team" CTAs remain visible in collapsed nav (sticky bar)
- Sticky bottom bar on mobile with dual CTA (Browse / Talk) — always accessible

### Hero (Mobile)
- Engineer profile card moves below text (stack layout)
- H1 font size: 32–36px (from 52–60px desktop)
- Stats anchors collapse to 2 per row

### Problem Section (Mobile)
- Pain point cards stack to 1-column
- Bold statements remain full-width

### How It Works (Mobile)
- Horizontal 3-step flow becomes vertical timeline
- Each step expands with a tap (accordion behavior on mobile)

### Pricing (Mobile)
- Tier cards stack vertically (Tier 1 first, most popular)
- Comparison table collapses to single-tier view with toggle

### Contact Form (Mobile)
- Single-column progressive form
- Trust sidebar moves below form
- Calendly embed adapts to mobile viewport

### Performance Targets (Mobile)
- First Contentful Paint: < 1.5s
- Largest Contentful Paint: < 2.5s (hero image/card)
- No layout shift from font loading (use font-display: swap)
- All CTAs minimum 44×44px tap target

---

## 6. TRUST SIGNAL PLACEMENT

### Tier 1 — Primary Trust (Above the Fold / Hero)
- Inline stats (47+ engineers placed, <7 days, retention rate) — anchored below hero CTAs
- Social proof micro-copy: "No commitment to browse"
- Professional dark-mode visual aesthetic signals legitimacy immediately

### Tier 2 — Process Trust (Sections 2–4)
- Problem agitation section: demonstrates deep domain understanding (trust via empathy)
- 4 solution pillars: specificity = credibility
- Screening detail (12% acceptance rate) on How It Works page

### Tier 3 — Outcome Trust (Social Proof Section)
- Metrics bar with hard numbers
- Testimonials with role + company type (real attribution where possible)
- Client logos (greyscale, non-distracting)

### Tier 4 — Risk Removal (Pricing + Contact)
- 90-day replacement guarantee (badge + plain language)
- "No commitment to browse" on profile gate
- Privacy note on all forms: "We never share your details without permission"
- Response time badge on contact page: "< 2 hours average"
- Post-submit confirmation with explicit next steps

### Tier 5 — Persistent Trust (Global)
- Nav always shows "Talk to Our Team" — signals human availability
- Footer: Company registration details, physical address (if applicable), LinkedIn
- SSL + security badges (footer)
- Engineer verification badge on profile cards ("Screened & Verified")

### Trust Signal by Page:
| Page | Primary Trust Signal | Secondary |
|------|---------------------|-----------|
| Homepage | Stats + testimonials | Problem empathy |
| How It Works | Screening process detail | "12% acceptance" stat |
| /engineers | "Screened & Verified" badge per profile | Stats bar |
| Pricing | 90-day guarantee | Client count |
| /get-started | Response time + privacy note | "What happens next" |

---

## 7. NAVIGATION & INFORMATION HIERARCHY NOTES

### Intentional Omissions
- **No pricing in nav** — drives users to pricing page via context (after value is established), not direct navigation. Prevents price-first decisions before value is understood.
- **No "About" in primary nav** — secondary page, footer only. CTOs don't hire based on About pages; they hire based on proof.
- **No blog in primary nav** — Phase 2 addition; clutters primary decision flow.

### CTA Hierarchy Enforcement
- Primary CTA (`Browse Engineer Profiles`) always appears in accent color (electric blue / teal)
- Secondary CTA (`Talk to Our Team`) always appears as outlined or ghost variant
- Never two filled buttons side by side — visual hierarchy must be preserved
- Footer CTA: always present, always `Browse Engineers` primary + `Talk to Our Team` secondary

---

*End of UX Blueprint v1.0*

**Next step:** Copywriter consumes this document + strategy.md to write copy for each section.  
**Then:** Wireframer produces visual layouts per section brief.  
**Output location:** `/home/rizki/clawd/agents/hazn/projects/talentforge/`

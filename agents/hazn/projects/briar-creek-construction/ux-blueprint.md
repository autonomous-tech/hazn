# UX Blueprint — Briar Creek Construction
**Version:** 1.0  
**Status:** Ready for Development  
**Audience:** Developer / Frontend Team

---

## 1. SITE ARCHITECTURE

```
briar-creek-construction.com/
│
├── / (Home)
├── /services (Services Overview)
│   ├── /services/new-home-construction
│   ├── /services/remodeling
│   └── /services/additions
├── /our-work (Gallery)
├── /about (About Us)
├── /testimonials
├── /contact (Contact / Free Estimate)
└── /service-areas
```

**URL Notes:**
- Keep URLs short and keyword-rich
- All service pages live under `/services/` for SEO hierarchy
- `/our-work` is more conversational than `/gallery` — matches how homeowners speak

---

## 2. SHARED COMPONENTS

These appear on every page. Build once, reuse everywhere.

---

### 2A. STICKY HEADER

**Behavior:** Sticks to top on scroll. Slightly smaller/more opaque than hero-overlay version.

**Desktop Layout (left → right):**
```
[Logo: Briar Creek Construction]     [Nav: Services ▾ | Our Work | About | Testimonials | Service Areas]     [CTA Button: Get a Free Estimate →]     [Phone: 📞 (555) 000-0000]
```

**Mobile Layout:**
```
[Logo]     [📞 TAP-TO-CALL — LARGE, AMBER]     [☰ Hamburger]
```

**Key UX Decisions:**
- Phone number must be a `tel:` link — tappable on mobile, always visible
- On mobile, the call button is the PRIMARY header action, not buried in hamburger
- "Get a Free Estimate" CTA in header goes to `/contact`
- Services nav item has dropdown: New Home Construction / Remodeling / Additions
- Header bg: Deep Forest Green (#2D4A2D) with Off-White text
- CTA button: Ohio Amber (#D4870A)

---

### 2B. FOOTER

**Structure (3-column desktop, stacked mobile):**

**Column 1 — Brand**
- Logo (white variant)
- Tagline: "Built Right. Built for Ohio."
- License number + insurance badge
- Ohio contractor logo/seal if available

**Column 2 — Navigation**
- Services: New Home Construction, Remodeling, Additions
- Company: About Us, Our Work, Testimonials, Service Areas
- Contact: Get a Free Estimate, (555) 000-0000

**Column 3 — Contact + Social**
- Large tap-to-call phone number (amber, bold)
- Email address
- Physical address / service region: "Proudly serving [County List], Ohio"
- Social icons: Facebook, Instagram, Houzz (construction audiences use these)
- Google Reviews badge/widget

**Bottom Bar:**
- © 2025 Briar Creek Construction. All rights reserved.
- Privacy Policy | Terms
- "Licensed General Contractor — Ohio License #XXXXXXXX"

---

### 2C. FLOATING PHONE CTA (Mobile Only)

**What it is:** A fixed bottom bar on mobile viewports.

**Design:**
```
[📞  CALL NOW — (555) 000-0000]  |  [Get Free Estimate →]
```

- Full-width bar, split into two equal tap targets
- Left: Amber background, phone icon, "CALL NOW" in bold Oswald
- Right: Dark green background, "Get Free Estimate" → links to /contact
- Height: 56–64px (comfortable thumb tap zone per iOS HIG)
- Always visible on scroll — never hidden
- z-index above all content

**Why this exists:** Homeowners researching on mobile are often in "decision mode." Removing friction from calling is the #1 mobile conversion lever. Every tap away from calling is a leak.

---

### 2D. SECTION CTA BANNER (Reusable Mid-Page Component)

Used throughout all pages to re-engage visitors before they scroll away.

```
[BG: Full-width Forest Green or Dark photo]
  "Ready to Start Your Project?"
  "Get a free, no-pressure estimate from Ohio's trusted contractor."
  [Call Now: (555) 000-0000]   [Request a Callback →]
```

---

## 3. HOMEPAGE BLUEPRINT

**Goal:** Establish trust, showcase work, drive call/form conversion within 30 seconds of landing.  
**Primary Visitor Intent:** "Is this contractor legit? Can they do my project? Do they serve my area?"

---

### SECTION 1 — HERO

**Position:** Above the fold, full-viewport height  
**Purpose:** Immediate impact. Answer "What do you do, where, and why should I trust you?" in 3 seconds.

**Content:**
- **Background:** Full-bleed, high-quality photo of a completed Ohio home or major remodel. Real project, not stock. Slight dark overlay (40%) for text legibility.
- **Eyebrow (small caps, amber):** "Ohio's Trusted Residential Contractor"
- **H1 (Oswald, white, large):** "Built Right. Built for Ohio."
- **Subheadline (Inter, white, 18–20px):** "Full-service residential construction — new builds, remodels, and additions — by a contractor your neighbors already trust."
- **CTA Row:**
  - Primary button (Amber): 📞 Call (555) 000-0000
  - Secondary button (outlined white): Request a Free Estimate →
- **Scroll indicator:** Subtle animated down arrow below CTAs

**Mobile Notes:**
- H1 scales down to ~36px — still dominant
- CTA buttons stack vertically, full-width
- Call button is top/first — thumb reaches it without scrolling
- Photo crops to portrait, ensure focal point (house/door) stays centered

**Why it earns its place:** First impressions are irreversible. Every element here is doing conversion work — the photo builds aspiration, the headline builds identity, the subhead overcomes "are they right for me?", and dual CTAs serve two buyer modes (ready-to-call vs. form-preferers).

---

### SECTION 2 — TRUST BAR

**Position:** Immediately below hero (or overlapping hero bottom edge as a floating strip)  
**Purpose:** Deflect "but can I trust them?" before that question forms.

**Design:** 4-column horizontal strip, icon + text, dark green or off-white background.

| Icon | Label |
|------|-------|
| 🛡️ Shield | Licensed & Insured in Ohio |
| ⭐ Star | 4.9★ — 120+ Google Reviews |
| 📅 Calendar | 15+ Years in Business |
| 🏠 House | 300+ Ohio Homes Built & Remodeled |

**Mobile:** 2×2 grid layout. Each badge large enough to read without zoom.

**Why it earns its place:** Trust bar is the #1 anxiety-reducer for residential contractor sites. Homeowners fear scams, shoddy work, and no-shows. This bar directly addresses those fears with social proof before they scroll an inch.

---

### SECTION 3 — SERVICES OVERVIEW

**Position:** Third section  
**Purpose:** "I see what you do — now which service fits my need?"

**Headline:** "What Can We Build For You?"

**Layout:** 3-column card grid (stack to 1-col on mobile)

**Card Structure:**
```
[Large photo — relevant project]
[Service Name — Oswald H3]
[2–3 sentence description]
[Learn More →] (links to service page)
```

**Cards:**
1. **New Home Construction** — Photo: new build exterior. "Build your dream home from the ground up with a contractor who knows Ohio soil, codes, and climate."
2. **Remodeling** — Photo: kitchen/bath remodel. "Transform your existing space — kitchen, bath, basement, whole-home — with expert craftsmanship and zero guesswork."
3. **Additions** — Photo: room addition or sunroom. "Need more space? We design and build seamless additions that look like they were always part of your home."

**Below cards:** "Not sure what you need? [Call us — we'll help you figure it out →]" (links to contact)

**Why it earns its place:** Visitors self-segment here. Someone researching a kitchen remodel needs to quickly find their path. This section acts as a routing hub — reducing pogo-stick back-button behavior by giving clear lanes.

---

### SECTION 4 — FEATURED PROJECTS (MINI-GALLERY)

**Position:** Fourth section  
**Purpose:** Prove the work. Show before/afters. Build desire.

**Headline:** "Recent Ohio Projects"
**Subhead:** "Real work. Real Ohio homes. Real results."

**Layout:** Masonry or 3-col photo grid, 6 photos (desktop). 2-col on mobile.

**Each photo:**
- Label overlay on hover (desktop) / always visible (mobile): project type + location (e.g., "Kitchen Remodel — Columbus, OH")
- Click → opens lightbox OR links to full gallery

**CTA below grid:** [See All Projects →] links to /our-work

**Why it earns its place:** Photos are the #1 conversion driver for residential contractors. More than testimonials, more than copy. Visitors want to see "can they do THIS kind of project, in THIS kind of home, that looks like MY home." 6 photos here tease the gallery and drive deeper engagement.

---

### SECTION 5 — WHY CHOOSE US

**Position:** Fifth section  
**Purpose:** Differentiation. Why Briar Creek over the 50 other contractors they'll Google.

**Headline:** "Why Ohio Homeowners Choose Briar Creek"

**Layout:** 2-column — left side feature list, right side large photo (contractor + homeowner shaking hands or walkthrough)

**Feature List (icon + headline + 1 sentence each):**
1. 🏅 **Licensed & Insured** — Full Ohio licensing and liability coverage on every project.
2. 📋 **Transparent Pricing** — Detailed quotes, no hidden fees, no surprise change orders.
3. 📆 **On Time, On Budget** — We set realistic timelines and we hold to them.
4. 🌿 **Local Roots** — We live here, work here, and stand behind every project with our name.
5. 📸 **Real Project Photos** — No stock imagery. Every photo on this site is a Briar Creek project.
6. 🤝 **Clear Communication** — You'll always know what's happening with your project.

**Why it earns its place:** After seeing the work, visitors move to "but what's it like to work with them?" This section handles objections pre-emptively and reinforces the trust story with specifics, not platitudes.

---

### SECTION 6 — TESTIMONIALS STRIP

**Position:** Sixth section  
**Purpose:** Social proof from peers (other Ohio homeowners, not celebrities).

**Headline:** "What Ohio Homeowners Are Saying"

**Layout:** 3-col card grid on desktop. Carousel/slider on mobile.

**Each card:**
- Star rating (⭐⭐⭐⭐⭐)
- Quote (2–4 sentences, real, unedited)
- Name, City, Project type (e.g., "Sarah M. — Dublin, OH — Kitchen Remodel")
- Optional: small headshot or avatar initial

**Below cards:**
- "4.9 Stars — 120+ Reviews on Google" + Google Reviews logo
- [Read All Testimonials →] links to /testimonials

**Why it earns its place:** Testimonials placed after "why choose us" reinforce the claims with human voices. The peer-to-peer signal ("Sarah from Dublin got her kitchen done") is more persuasive than any copy.

---

### SECTION 7 — CTA BANNER

**Position:** Seventh section  
**Purpose:** Re-engagement / conversion for visitors who've read this far but haven't clicked.

Use the shared **Section CTA Banner** component (see 2D).

Variation for homepage:
- BG: Full-bleed photo of a finished home at dusk (dramatic, aspirational)
- Headline: "Your Project Starts with One Call."
- Subhead: "Free estimates. No pressure. Just honest answers from an Ohio contractor you can trust."
- CTA: [📞 Call (555) 000-0000] + [Request a Callback Form →]

**Why it earns its place:** Some visitors scroll the entire page before committing. This banner captures the "convinced but not quite pulled the trigger" segment. Placement before footer ensures it's the last thing they see before leaving.

---

### SECTION 8 — SERVICE AREAS TEASER

**Position:** Eighth section (before footer)  
**Purpose:** SEO + local relevance. "Do they serve my town?"

**Headline:** "Proudly Serving Ohio Homeowners"

**Layout:** Clean list or map visual + county/city tags

**Content:**
- Simple Ohio outline map (decorative) OR
- Tag cloud of served cities: Columbus, Dublin, Westerville, Gahanna, New Albany, Grove City, Hilliard, Powell, Worthington, Pickerington, etc.
- "Don't see your city? [Call us — we likely serve your area →]"

**Link:** [View All Service Areas →] → /service-areas

**Why it earns its place:** "Do they come to me?" is a top-3 question for residential service businesses. Answering it on the homepage reduces exit rate from visitors who assumed "probably not my area."

---

## 4. SERVICES OVERVIEW PAGE BLUEPRINT

**URL:** `/services`  
**Goal:** Route visitors to the right service page. Brief them on the scope of work.

---

### Section Order:

**1. Page Hero (shorter than homepage — 50vh)**
- BG: Collage or split-image (new build / remodel / addition)
- H1: "Residential Construction Services"
- Subhead: "From new home builds to full remodels — Briar Creek handles it all under one roof."
- Trust bar (same as homepage)

**2. Services Cards — Expanded (3 cards, more detail than homepage)**
Each card includes:
- Large photo
- H2 service name
- 4–6 bullet points describing what's included
- Typical project timeline / budget range (helps self-qualify)
- [Explore [Service Name] →] CTA

**3. How We Work (Process Section)**
Headline: "Our Simple 4-Step Process"
Steps: 1. Free Estimate → 2. Design & Planning → 3. Build → 4. Final Walkthrough
Layout: Horizontal stepper (desktop), vertical (mobile)
Each step: icon + headline + 2-sentence description

**4. Mini-Testimonials (2–3, service-relevant)**

**5. CTA Banner**

---

## 5. GALLERY PAGE BLUEPRINT

**URL:** `/our-work`  
**Goal:** Demonstrate range, quality, and Ohio-relevance. Convert browsers into callers.

---

### Section Order:

**1. Page Hero (minimal — 40vh)**
- H1: "Our Work"
- Subhead: "300+ Ohio projects. Real homes. Real results."
- Filter bar below headline (see below)

**2. Filter Bar**
Sticky filter row below header on scroll.

**Filters (pills/tabs):**
- All Projects
- New Home Construction
- Kitchen Remodel
- Bathroom Remodel
- Additions
- Basement Finishing
- Full Home Remodel

**Sort:** Most Recent | Most Popular (optional)

**3. Photo Grid**
- Masonry layout, 3-col desktop / 2-col tablet / 1-col mobile
- Each card:
  - Photo (before OR after — or before/after toggle)
  - Overlay on hover: Project name, location, type
  - Click → Lightbox with full-size image, project details, before/after toggle if available
- Lazy-load images below fold
- "Load More" button (or infinite scroll) — show 12 initially

**4. Before/After Feature Section**
- 3–5 featured transformations with side-by-side or slider compare
- Headline: "See the Difference"
- These should be the most dramatic transformations in the portfolio

**5. Project Stats Bar**
```
[300+ Projects] [15+ Years] [Columbus & Surrounding Counties] [4.9★ Google Rating]
```

**6. CTA Banner**
- "Inspired by what you see? Let's talk about your project."
- [Call Now] + [Get Free Estimate]

---

### Gallery UX Notes:
- Before/after slider component is HIGH priority — it's the most shared/viral element on contractor sites
- All photos must have alt text with project type + location for SEO
- Lightbox must be keyboard-navigable and mobile-swipeable
- Consider lazy video (short time-lapse of build) if available — massive engagement driver

---

## 6. CONTACT PAGE BLUEPRINT

**URL:** `/contact`  
**Goal:** Convert visitor intent into a concrete lead — call or form submission.

---

### Section Order:

**1. Page Hero (minimal — 30vh)**
- H1: "Get a Free Estimate"
- Subhead: "No obligation. No pressure. Just an honest conversation about your project."
- No photo needed — keep focus on form below

**2. Two-Column Layout: Form Left, Info Right**

**LEFT — Lead Form:**

```
Headline: "Tell Us About Your Project"

Fields:
- First Name *
- Last Name *
- Email *
- Phone * (tel input, large on mobile)
- Service Needed (dropdown): New Home Construction | Remodeling | Addition | Not Sure Yet
- Project Description (textarea): "Tell us a little about what you're planning..."
- How did you hear about us? (dropdown, optional)
- Preferred Contact Method: Phone | Email
- Best time to reach you: Morning | Afternoon | Evening

[Submit Button — Full Width, Amber]: "Request My Free Estimate →"

Microcopy below button: "We typically respond within 1 business day. No spam, ever."
```

**RIGHT — Contact Info:**
```
[Large tap-to-call phone: (555) 000-0000]
"Prefer to talk? Call us Monday–Friday, 7am–6pm."

[Email address]

[Physical address or service region]

[Google Maps embed — service area or office if applicable]

---
Trust badges:
- BBB Accredited (if applicable)
- Google 4.9★ Reviews
- Licensed & Insured badge
- "100% Free Estimate — No Obligation"
```

**3. FAQ Strip (below form)**
Headline: "Common Questions"

- How long does a free estimate take?
- Do I need to know exactly what I want?
- How soon can you start?
- What areas do you serve?
- Do you provide financing?

Each: accordion expand. Keep it brief. Link to /service-areas for the area question.

**4. Mini Testimonials (2)**
Service-specific social proof. "They made the estimate process completely stress-free..." style quotes.

---

### Contact Page UX Notes:
- Form must not auto-redirect on submit — show inline success message: "Thanks! We'll reach out within 1 business day."
- Phone field should auto-format (XXX) XXX-XXXX
- On mobile, form fields should be tall enough for fat-finger input (min 48px height)
- Reduce form fields if conversion is low — "Name, Phone, Project Type" is minimum viable
- Consider adding: "Or text us at (555) 000-0000" for younger segment

---

## 7. INDIVIDUAL SERVICE PAGE BLUEPRINT

**Applies to:** `/services/new-home-construction`, `/services/remodeling`, `/services/additions`  
**Goal:** Rank for service + location keywords. Convert informed visitors with specific intent.

---

### Section Order:

**1. Hero (60vh)**
- Service-specific hero photo (most impressive relevant project)
- H1: "[Service Name] in Ohio"
- Subhead: Service-specific value prop
- Dual CTAs (call + form)

**2. What's Included**
- Detailed scope bullets — what Briar Creek handles
- 2-column layout: scope list left, photo right

**3. Process for This Service**
- 4–6 steps specific to this service type
- Timeline expectations (e.g., "Most kitchen remodels: 3–6 weeks")

**4. Featured Projects from This Category**
- 4–6 photos filtered to this service
- [See All [Service] Projects →] → Gallery filtered to category

**5. Investment Range / FAQ**
- General budget ranges (not quotes) — helps self-qualify and reduces low-intent leads
- 3–5 FAQs specific to this service

**6. Testimonials (service-specific)**
- 2–3 quotes from customers who had this type of work done

**7. CTA Banner**

---

## 8. MOBILE CONSIDERATIONS

### Priority Order for Mobile Conversions:
1. **Floating bottom bar** — always visible, two large tap targets (call + form)
2. **Header phone button** — amber, prominent, always in header
3. **Hero CTA buttons** — stacked vertically, full-width, call on top
4. **Section CTAs** — full-width buttons, min 48px height

### Typography on Mobile:
- H1: 32–40px (Oswald)
- H2: 26–32px (Oswald)
- Body: 16px min (Inter) — never go below 16px on mobile
- CTA buttons: 18–20px, bold

### Image Handling:
- Use `srcset` for responsive images — load smaller files on mobile
- Hero image: ensure focal point (building exterior, key visual) crops correctly on portrait
- Lazy load all below-fold images

### Navigation on Mobile:
- Hamburger opens full-screen overlay menu (not sidebar)
- Top of menu: large tap-to-call button (amber, full-width)
- Menu items: large tap targets, 56px min height per item
- Close button top-right, large

### Form on Mobile:
- Single-column layout
- Input fields: 48px+ height
- Keyboard types: `type="tel"` for phone, `type="email"` for email
- Submit button: full-width, amber, minimum 56px height

### Performance:
- Target < 3s load on 4G (critical for mobile contractor searchers)
- Prioritize hero image load (LCP)
- Defer non-critical scripts

---

## 9. COMPONENT INVENTORY

All components the developer needs to build. Grouped by type.

---

### Layout Components
| Component | Description |
|-----------|-------------|
| `StickyHeader` | Logo, nav, phone CTA. Shrinks on scroll. |
| `MobileHeader` | Logo, tap-to-call, hamburger. Separate component. |
| `MobileNav` | Full-screen overlay. Call CTA at top. |
| `Footer` | 3-col desktop, stacked mobile. |
| `FloatingCTA` | Mobile-only fixed bottom bar. Two tap targets. |
| `PageHero` | Configurable height, bg photo, headline, subhead, CTAs. |
| `SectionCTABanner` | Full-width reusable CTA strip. Dark bg. |

---

### Homepage-Specific Components
| Component | Description |
|-----------|-------------|
| `TrustBar` | 4-item icon + label strip. 2×2 on mobile. |
| `ServicesGrid` | 3-col service card grid. Photo + title + desc + link. |
| `FeaturedGallery` | 6-photo masonry/grid preview. Hover labels. |
| `WhyChooseUs` | 2-col: feature list + photo. |
| `TestimonialsStrip` | 3-col cards desktop. Carousel on mobile. |
| `ServiceAreasTeaser` | Map visual or city tag cloud. |

---

### Gallery Components
| Component | Description |
|-----------|-------------|
| `GalleryFilter` | Pills/tabs for category filter. Sticky on scroll. |
| `GalleryGrid` | Masonry grid. Lazy load. Click-to-lightbox. |
| `Lightbox` | Full-screen image viewer. Keyboard nav. Swipe on mobile. |
| `BeforeAfterSlider` | Drag-handle before/after image compare. |
| `ProjectCard` | Individual project tile. Hover overlay. |

---

### Form Components
| Component | Description |
|-----------|-------------|
| `LeadForm` | Full contact form. Inline validation. Success state. |
| `PhoneInput` | Auto-formatting tel input. |
| `ServiceSelect` | Dropdown with icons. |
| `FormSuccess` | Inline confirmation message. No redirect. |

---

### Content Components
| Component | Description |
|-----------|-------------|
| `ServiceCard` | Used in overview page. Photo + bullets + CTA. |
| `ProcessStepper` | Horizontal (desktop) / vertical (mobile) 4-step process. |
| `TestimonialCard` | Stars + quote + name/city/project. |
| `AccordionFAQ` | Expandable FAQ rows. |
| `StatsBadge` | Number + label. Used in stats bars. |
| `ProjectCategoryTag` | Pill label for project type filter. |

---

### Utility Components
| Component | Description |
|-----------|-------------|
| `GoogleReviewsBadge` | Star rating + count + Google logo. |
| `LicenseBadge` | Shield icon + license number text. |
| `TrustBadge` | Generic icon + label. Used in TrustBar + footer. |
| `CTAButton` | Primary (amber) and secondary (outlined) variants. |
| `SectionHeading` | Eyebrow + H2 + optional subhead. Consistent style. |
| `BreadcrumbNav` | For inner pages. SEO + wayfinding. |

---

## 10. DESIGN TOKENS (FOR DEVELOPER)

```css
/* Colors */
--color-green: #2D4A2D;       /* Deep Forest Green — primary brand, headers, footer */
--color-amber: #D4870A;       /* Ohio Amber — all CTAs, highlights, accents */
--color-slate: #4A5568;       /* Warm Slate — body text, secondary UI */
--color-offwhite: #F7F5F0;    /* Off-White — page background, card backgrounds */
--color-white: #FFFFFF;
--color-black: #1A1A1A;

/* Typography */
--font-heading: 'Oswald', sans-serif;   /* All headings, buttons, labels */
--font-body: 'Inter', sans-serif;       /* All body copy, form fields */

/* Spacing Scale (8px base) */
--space-xs: 8px;
--space-sm: 16px;
--space-md: 24px;
--space-lg: 40px;
--space-xl: 64px;
--space-2xl: 96px;

/* Border Radius */
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;

/* Shadows */
--shadow-card: 0 2px 12px rgba(0,0,0,0.10);
--shadow-header: 0 2px 8px rgba(0,0,0,0.15);

/* Breakpoints */
--bp-mobile: 480px;
--bp-tablet: 768px;
--bp-desktop: 1024px;
--bp-wide: 1280px;
```

---

## 11. PAGE-BY-PAGE SUMMARY TABLE

| Page | Primary Goal | Key Sections | Primary CTA |
|------|-------------|--------------|-------------|
| Home | Trust + Route + Convert | Hero, Trust Bar, Services, Gallery, Why Us, Testimonials, CTA | Call or Form |
| Services Overview | Route to service pages | Hero, 3 service cards, Process, CTA | Service page links |
| New Home Construction | SEO + Convert new-build intent | Hero, Scope, Process, Projects, FAQ, CTA | Call or Form |
| Remodeling | SEO + Convert remodel intent | Hero, Scope, Process, Projects, FAQ, CTA | Call or Form |
| Additions | SEO + Convert additions intent | Hero, Scope, Process, Projects, FAQ, CTA | Call or Form |
| Our Work / Gallery | Show proof, inspire, convert | Filter, Grid, Before/After, CTA | Call or Form |
| About Us | Build trust, human connection | Team, Story, Values, Licenses, CTA | Call or Form |
| Testimonials | Deep social proof | Review grid, Google badge, CTA | Call or Form |
| Contact | Lead capture | Form, Phone, Map, FAQ | Form submit or Call |
| Service Areas | SEO + Local relevance | Map, City list, service links, CTA | Call or Form |

---

*Blueprint complete. All sections are developer-ready. Build shared components first (Header, Footer, FloatingCTA), then Homepage, then Gallery, then remaining inner pages.*

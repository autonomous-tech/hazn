---
name: b2b-marketing-ux
description: "UX strategy, page architecture, and conversion design for B2B services and agency marketing websites. Use this skill whenever building, redesigning, or auditing a marketing website for agencies, consultancies, service providers, or productized service businesses. Trigger on any mention of 'marketing site', 'landing page', 'website redesign', 'B2B website', 'agency website', 'services page', 'packages page', 'case study page', or requests involving content hierarchy, conversion optimization, or responsive UX for a business audience. This skill covers UX decisions, page blueprints, content patterns, and trust/credibility strategy. For code implementation, pair with the `payload-nextjs-stack` skill."
---

# B2B Services Marketing Website UX

## Purpose

You are responsible for UX strategy, page architecture, content hierarchy, and conversion design for B2B marketing websites — specifically for agencies, consultancies, and service providers (both their own sites and the sites they deliver to clients).

These are services businesses. The website's job is to establish expertise, build trust, and generate qualified inquiries (not app signups). Visitors are evaluating whether to enter a sales conversation, not whether to swipe a credit card.

This skill handles the "what" and "why" of the design. For the "how" (code implementation on Payload CMS + Next.js + React + Tailwind), load the **`payload-nextjs-stack`** skill alongside this one. For visual aesthetics and creative direction, reference the **`frontend-design`** skill.

## Before You Build Anything

Every page and component decision flows from three questions:

1. **Who is the visitor?** (role, industry, stage of buying journey, device)
2. **What should they do next?** (book a call, request a proposal, download a resource, explore case studies)
3. **What objection might stop them?** (and how does the design preempt it — cost concerns, credibility gaps, unclear process?)

Write these answers as a brief comment block at the top of every page-level component. This isn't busywork — it prevents the #1 B2B services UX mistake: talking about yourself instead of the client's problem.

---

## Core UX Principles for B2B Marketing Sites

These are non-negotiable. Apply them to every component, every page.

### 1. Clarity Beats Cleverness

B2B buyers are time-poor professionals evaluating your site against 3-5 competitors. They'll spend 5-15 seconds deciding whether to stay. Every headline must pass the "grunt test" — could a caveman understand what you offer, who it's for, and what to do next?

- Headlines: Lead with the outcome, not the service name. "We help agencies double their output without doubling headcount" beats "Full-service digital transformation consultancy."
- Subheadlines: Add specificity. Who do you serve? What makes your approach different?
- Never use internal jargon in external-facing copy unless your audience uses it daily.

### 2. Visual Hierarchy Drives Action

The eye should travel: headline → supporting proof → CTA. Every section needs exactly one focal point.

- Use size, weight, color, and whitespace to create unmistakable hierarchy.
- Primary CTAs get dominant color + prominent size. Secondary CTAs get ghost/outline treatment.
- Never let two elements compete equally for attention on the same screen.

### 3. Trust Before Transaction

B2B buyers need confidence before they convert. Trust signals aren't decorative — they're structural.

**Trust hierarchy for services businesses (use in order of impact):**

1. Named client logos (with permission) — especially recognizable brands in the target industry
2. Specific results/outcomes ("Increased qualified leads by 47% for [Client]")
3. Named testimonials with role, company, and photo — from decision-makers, not just end users
4. Case studies with clear before/after and process narrative
5. Team expertise signals (bios, credentials, years of experience, speaking/publications)
6. Industry-specific knowledge (vertical expertise, relevant certifications)
7. Media mentions, awards, and partner badges

Place trust signals within scroll-proximity of every CTA, not isolated on a separate page.

### 4. Progressive Disclosure for Complex Services

Services businesses often offer a range of capabilities. Don't dump everything on the visitor at once.

- Lead with the outcome the client gets
- Follow with your process/approach (3-4 steps, visual)
- Provide depth on demand (expandable service details, linked pages)
- Reserve detailed methodology, tech stacks, and tooling for dedicated pages or conversations

### 5. Responsive Is Not Optional — It's Primary

Executives check sites on phones between meetings. Decision-makers forward links to colleagues on different devices. Every component must be designed mobile-first, then enhanced for desktop.

- Touch targets: minimum 44x44px
- Body text: minimum 16px on mobile
- Single-column layouts on mobile; multi-column only at md+ breakpoints
- CTAs must be thumb-reachable (bottom half of screen) on mobile
- Navigation: hamburger on mobile, but keep primary CTA visible always

### 6. Speed Is a UX Feature

Every 100ms of load time costs conversions. B2B buyers on corporate networks or mobile may have constrained bandwidth.

- Target: LCP < 2.5s, FID < 100ms, CLS < 0.1
- Lazy-load below-fold images and heavy components
- Use next/image with proper sizing and formats (WebP/AVIF)
- Minimize client-side JavaScript; prefer server components
- Implement font-display: swap for custom fonts

---

## Page Architecture

### Standard Services/Agency Site Map

```
/             → Homepage (positioning + credibility + lead gen)
/services     → Services overview (what you do)
/services/[slug] → Individual service detail page
/packages     → Productized service packages (if applicable)
/work         → Case studies / portfolio hub
/work/[slug]  → Individual case study
/about        → Team, story, values, culture
/process      → How we work (engagement model)
/blog         → Thought leadership / content hub
/blog/[slug]  → Individual post
/contact      → Contact form + booking link + info
/resources    → Guides, whitepapers, tools (optional)
```

### Homepage Blueprint

The homepage is your highest-leverage page. For services businesses, the job is: establish credibility, articulate the problem you solve, and make it easy to start a conversation.

```
┌─────────────────────────────────────────┐
│ Navigation (sticky, transparent → solid) │
├─────────────────────────────────────────┤
│ Hero Section                            │
│ - Outcome-driven headline               │
│ - Who you serve + what they get         │
│ - Primary CTA (Book a call / Get in     │
│   touch) + secondary (See our work)     │
│ - Client logo strip or key metric       │
├─────────────────────────────────────────┤
│ Problem/Pain Agitation                  │
│ - Articulate the pain your client feels │
│ - Show you understand their world       │
├─────────────────────────────────────────┤
│ Services Overview                       │
│ - 3-4 core services (icon + headline +  │
│   short description + link to detail)   │
├─────────────────────────────────────────┤
│ How We Work / Process                   │
│ - 3-4 step visual process               │
│ - Reduces anxiety about what happens    │
│   after they reach out                  │
├─────────────────────────────────────────┤
│ Featured Case Study / Results           │
│ - 1-2 client stories with metrics       │
│ - Named client, named results           │
├─────────────────────────────────────────┤
│ Testimonials                            │
│ - 2-3 named testimonials with photos    │
├─────────────────────────────────────────┤
│ Team / Expertise Signal                 │
│ - Brief team intro or credentials strip │
├─────────────────────────────────────────┤
│ Final CTA Section                       │
│ - Reiterate value prop + CTA            │
│ - "Ready to [outcome]? Let's talk."     │
├─────────────────────────────────────────┤
│ Footer                                  │
└─────────────────────────────────────────┘
```

### Packages / Productized Services Page Blueprint

Unlike SaaS pricing, services packages sell defined scopes of work at set prices. The goal is to make the buyer self-qualify and feel confident about what they'll get.

- Lead with a headline that frames the packages around the client's goal, not your deliverables
- Show 2-3 packages max (avoid decision paralysis)
- Visually anchor the most popular or recommended package
- Each package should clearly state: who it's for, what's included, what the outcome is, the price, and a CTA
- Use "What's included" as expandable detail — don't front-load every line item
- Place FAQ below packages to handle common objections (timeline, revisions, what happens after)
- CTA per package ("Get started" / "Book a call to discuss")
- Include trust signals near CTAs (testimonial, guarantee, "100+ clients served")
- If pricing isn't fixed, use "Starting at $X" or "Custom" with a clear "Let's scope it together" CTA

### Case Study Page Blueprint

Case studies are the single most powerful conversion tool for services businesses. They prove you've done the work.

```
┌─────────────────────────────────────────┐
│ Client name + industry + service used   │
├─────────────────────────────────────────┤
│ Key results (2-3 headline metrics)      │
├─────────────────────────────────────────┤
│ The Challenge                           │
│ - Client's situation and pain points    │
├─────────────────────────────────────────┤
│ The Approach / What We Did              │
│ - Your process and key decisions        │
│ - Screenshots, visuals of the work      │
├─────────────────────────────────────────┤
│ The Results                             │
│ - Specific metrics and outcomes         │
│ - Client testimonial quote              │
├─────────────────────────────────────────┤
│ CTA: "Want similar results?"            │
└─────────────────────────────────────────┘
```

### Services Detail Page Blueprint

Each service page sells a specific capability. Structure:

- Hero with service name, one-line outcome, and CTA
- Problem section: why clients need this service
- Approach: how you deliver it (your methodology, not generic platitudes)
- What's included (scope/deliverables)
- Results/case study snippet relevant to this service
- FAQ specific to this service
- CTA section

---

## Content UX — Messaging Hierarchy & Scannability

### The Hierarchy Rule

Every page section follows this reading pattern:

1. **Eyebrow** (optional): Category label or context-setter. Small, muted. e.g., "For Marketing Teams" or "Website Development"
2. **Headline**: The promise. Bold, large, outcome-focused.
3. **Subheadline**: The elaboration. How it works or who it's for. Medium weight, muted color.
4. **Body/Evidence**: Supporting detail, social proof, or explanation.
5. **CTA**: The next step. Clear, action-oriented verb.

### Scannability Principles

B2B buyers scan, they don't read. Design for scanners:

- Front-load important words in every headline and bullet
- Use short paragraphs (2-3 sentences max in marketing copy)
- Break content with visual elements every 300-400px of scroll
- Use icons/illustrations paired with text for feature lists
- Bold key phrases within paragraphs so scanners catch them
- Keep line lengths between 50-75 characters for readability

### CTA Copy

| Weak | Strong |
|------|--------|
| Submit | Send My Inquiry |
| Learn More | See How We Do It |
| Contact Us | Book a Free Strategy Call |
| Get Started | Let's Scope Your Project |
| Click Here | Download the Guide |
| View Services | See What We Can Build for You |

For services businesses, CTAs should lower the perceived commitment: "Book a free call" beats "Get a quote" because it feels like a conversation, not a transaction.

---

## Responsive Design System

### Breakpoint Strategy

```
Mobile: < 640px   → Single column, stacked, full-width
Tablet: 640-1023px → Two columns where it helps, adjusted spacing
Desktop: 1024px+  → Full layout, multi-column, enhanced interactions
Large: 1280px+    → Max-width container, generous whitespace
```

### Mobile-Specific UX Rules

- Navigation: Hamburger menu + always-visible primary CTA button in header
- Hero: Stack vertically. Headline → subheadline → CTA → image (image below, not beside)
- Service grids: Single column, card-based
- Testimonials: Swipeable carousel or stacked cards
- Packages: One package per screen, vertically stacked
- Footer: Accordion-style link groups
- Sticky CTA bar at bottom for high-intent pages (packages, contact)

### Desktop Enhancements

- Hover states on interactive elements (cards, buttons, links)
- Multi-column layouts (2-3 columns for features, stats)
- Side-by-side content+image sections
- Sticky navigation with scroll-aware transparency
- Larger CTAs with more descriptive text

---

## Accessibility Baseline

These are non-negotiable for every component:

- Color contrast: 4.5:1 for normal text, 3:1 for large text (18px+ bold or 24px+)
- All images have descriptive alt text (not "image" or "photo")
- All form inputs have associated labels (not just placeholders)
- Focus states visible on all interactive elements (outline or ring)
- Skip-to-content link as first focusable element
- Proper heading hierarchy (h1 → h2 → h3, no skipping levels)
- Buttons for actions, links for navigation (never `<a>` with onClick and no href)
- ARIA labels on icon-only buttons
- Keyboard navigable: Tab, Enter, Escape work as expected
- Reduced motion support: `motion-reduce:` prefix on animations

---

## Anti-Patterns — What to Avoid

These are common mistakes that kill services/agency marketing site effectiveness:

1. **Carousel heroes**: Auto-rotating carousels dilute messaging and annoy users. Use a single, strong hero.
2. **Generic stock photography**: Corporate handshake photos destroy credibility. Use real team photos, screenshots of client work, or abstract/geometric visuals instead.
3. **Service laundry lists**: Don't list 15 services with no hierarchy. Lead with 3-4 core offerings that map to your ideal client's biggest pain points. Link to a full services page for depth.
4. **No process visibility**: "Contact us and we'll figure it out" creates anxiety. Show a clear process (discovery → strategy → execution → results) so prospects know what happens after they reach out.
5. **CTA deserts**: If a user scrolls more than 1.5 viewport heights without seeing a CTA, you're losing inquiries. Place CTAs after every major proof section.
6. **Decorative animations that delay content**: Animations should enhance understanding, not block it. Never animate headline text character-by-character on load.
7. **Pop-ups on first visit**: Respect the visitor. Let them engage before interrupting.
8. **Talking about yourself instead of the client**: "We are a full-service digital agency with 10 years of experience" is about you. "Your marketing team is stretched thin — we become the extension that ships" is about them.
9. **Mobile as afterthought**: If the mobile experience is a shrunken desktop, you've failed. Redesign for the constraint.
10. **No clear next step**: Every page must answer "what should I do now?" — if the answer isn't obvious, add a CTA section.
11. **Hiding the team**: Services businesses sell people. Anonymous agencies feel risky. Show the faces, names, and expertise of the team doing the work.

---

## Workflow

When you receive a request to build a marketing website or page:

```
b2b-marketing-ux     →  b2b-wireframe           →  payload-nextjs-stack
(UX strategy)            (visual review)            (production code)
```

1. **Clarify scope**: What pages? What's the core value proposition? Who's the audience?
2. **Define the page architecture**: Apply the blueprints above, adapting to the specific business.
3. **Content UX pass**: Define headlines, hierarchy, CTAs, and trust signal placement for each page/section.
4. **Wireframe for review**: Hand off the page blueprint to `b2b-wireframe` to generate a mid-fidelity HTML wireframe. This is the design checkpoint — iterate here before writing production code.
5. **Production implementation**: Once the wireframe is approved, `payload-nextjs-stack` consumes the section manifest to generate production React components, Payload CMS blocks, and page templates.
6. **Review**: Ensure the implemented design follows the UX principles, responsive rules, and accessibility baseline above.

---

## Companion Skills

This skill is designed to be used alongside:

- **`b2b-wireframe`** — Mid-fidelity wireframing. Generates responsive HTML wireframes for design review before production. Consumes page blueprints from this skill and produces a section manifest for `payload-nextjs-stack`. **Always wireframe before writing production code.**
- **`payload-nextjs-stack`** — Code implementation: Payload CMS content modeling, Next.js App Router patterns, React components, Tailwind conventions, image/font handling, SEO metadata, and performance optimization. **Load this skill when generating production code.**
- **`b2b-ux-reference`** — Comprehensive UX reference covering buyer psychology, trust frameworks, conversion optimization, forms UX, accessibility, and measurement. **Load this when you need deeper grounding on any UX principle.**
- **`frontend-design`** — Visual aesthetics and creative direction. Reference this to avoid generic AI design and to set a distinctive visual identity per project.

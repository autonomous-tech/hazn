# Hazn Landing Page: UX Blueprint
*Version 2.0 | Waitlist Launch*

---

## Design Philosophy

**Core Aesthetic:** Dark, minimal, precise. Linear meets Vercel meets Raycast.

**Principles:**
1. **Density without clutter.** Every element earns its pixel.
2. **Motion with purpose.** Animations guide, not distract.
3. **Confidence, not hype.** Premium feels quiet. Let the product speak.
4. **Builder-first.** Technical audience respects craft, detects bullshit.

**Anti-patterns to avoid:**
- Gradient vomit (subtle only)
- Floating 3D objects for no reason
- "As seen in" logos we don't have
- Exclamation marks anywhere
- Stock photos of humans

---

## Global Design System

### Color Palette

```
Background:       #0A0A0B (near-black)
Surface:          #141416 (cards, elevated elements)
Surface Hover:    #1C1C1F (interactive states)
Border:           #27272A (subtle dividers)
Border Hover:     #3F3F46 (interactive borders)

Text Primary:     #FAFAFA (headlines, important)
Text Secondary:   #A1A1AA (body, descriptions)
Text Muted:       #71717A (captions, metadata)

Accent:           #3B82F6 (primary blue, CTAs)
Accent Hover:     #60A5FA (hover state)
Accent Subtle:    #3B82F6/10 (backgrounds, glows)

Success:          #22C55E (confirmations)
```

### Typography

```
Font Family:      Inter (primary), JetBrains Mono (code/numbers)

Hero Headline:    4rem/1.1 (64px), -0.03em tracking, 600 weight
Section Headline: 2.5rem/1.2 (40px), -0.02em tracking, 600 weight
Subheadline:      1.25rem/1.5 (20px), normal tracking, 400 weight
Body:             1rem/1.6 (16px), normal tracking, 400 weight
Caption:          0.875rem/1.5 (14px), normal tracking, 400 weight
Mono/Stats:       JetBrains Mono, 0.875rem, 500 weight
```

### Spacing Scale

```
Base unit: 4px
xs: 4px    | sm: 8px   | md: 16px
lg: 24px   | xl: 32px  | 2xl: 48px
3xl: 64px  | 4xl: 96px | 5xl: 128px
```

### Border Radius

```
Buttons/Inputs:   8px
Cards:            12px
Large cards:      16px
```

---

## Background Animation Concept

### "Grid Pulse"

**Concept:** A subtle dot grid that responds to scroll position, creating gentle waves of luminosity.

**Implementation:**
```
Base: Fixed dot grid pattern (24px spacing)
Dots: 1px circles, #27272A default
Animation: Radial gradient "pulse" follows scroll position
Pulse: Dots within radius brighten to #3F3F46, fade over 400ms
Effect: Creates subtle "alive" feeling without distraction
```

**Technical approach:**
- CSS: `background-image: radial-gradient(circle, #27272A 1px, transparent 1px)`
- JS: requestAnimationFrame tracks scroll, updates CSS custom property
- Gradient overlay follows scroll, brightens nearby dots
- Performance: GPU-accelerated, no repaints

**Alternative (simpler):** Static gradient mesh
- Soft blue/purple gradients at corners
- Blur: 200px, opacity: 0.15
- No animation, just atmosphere

**Recommendation:** Start with static gradient mesh. Add Grid Pulse if performance allows.

---

## Section Architecture

### Section 1: Hero

**Purpose:** Instant clarity on what Hazn is. Capture attention, drive waitlist signup.

**Content Hierarchy:**

```
1. Eyebrow (optional):        "From the builders at Autonomous"
2. Headline (H1):             "Your coding assistant. Now a marketing team."
3. Subheadline:               "10 AI agents that ship marketing. From strategy to production. Works where you work."
4. Primary CTA:               [Join the waitlist] button
5. Trust line:                "No spam. Updates every 2 weeks."
6. Visual anchor:             Terminal/code mockup OR agent visualization
```

**Animation Specs:**

| Element | Animation | Trigger | Duration | Easing |
|---------|-----------|---------|----------|--------|
| Headline | Fade up + blur clear | Page load | 600ms | ease-out |
| Subheadline | Fade up | 100ms delay | 500ms | ease-out |
| CTA button | Fade up + scale from 0.95 | 200ms delay | 400ms | ease-out |
| Trust line | Fade in | 300ms delay | 400ms | ease-out |
| Visual | Fade in + subtle parallax | 400ms delay | 800ms | ease-out |
| Background | Gradient fade in | Page load | 1200ms | linear |

**CTA Button Design:**
```
Primary: Blue (#3B82F6) background, white text
Size: 48px height, 24px horizontal padding
Border-radius: 8px
Hover: Lighten to #60A5FA, slight lift (translateY -1px)
Active: Scale 0.98
Glow: 0 0 20px rgba(59, 130, 246, 0.3) on hover
```

**Visual Options (pick one):**

Option A: **Terminal mockup**
- Dark terminal window showing `/marketing` command
- Animated typing effect: "Running 10 agents..."
- Shows agent names appearing one by one
- Conveys "works in your workflow"

Option B: **Agent constellation**
- 10 nodes (agents) connected by subtle lines
- Nodes gently pulse
- On hover, show agent name
- Conveys "coordinated team"

**Recommendation:** Terminal mockup. Speaks directly to technical audience.

**Mobile Considerations:**
- Headline: 2.5rem (40px)
- Stack vertically: headline, subhead, CTA
- Visual below fold on mobile (optional to show)
- Full-width CTA button
- Remove parallax effects

---

### Section 2: Problem

**Purpose:** Name the pain. Make them feel seen before you offer the solution.

**Content Hierarchy:**

```
1. Section label:            "THE PROBLEM"
2. Headline (H2):            "You can build anything. Marketing is the hard part."
3. Pain points (3 max):
   - "Agencies charge $20K/month for mediocre work"
   - "AI tools produce generic content that needs heavy editing"
   - "Hiring takes months, costs six figures"
4. Transition line:          "There's a better way."
```

**Layout:**
- Centered text block, max-width 680px
- Pain points as simple list (no cards needed)
- Minimal, text-focused

**Animation Specs:**

| Element | Animation | Trigger | Duration |
|---------|-----------|---------|----------|
| Section label | Fade in | Scroll into view (20%) | 300ms |
| Headline | Fade up | Scroll into view (30%) | 500ms |
| Pain points | Stagger fade up | 100ms apart | 400ms each |
| Transition | Fade in | After pain points | 300ms |

**Mobile Considerations:**
- Same layout, naturally responsive
- Reduce vertical padding (3xl to 2xl)

---

### Section 3: Solution

**Purpose:** Introduce Hazn as the answer. Show the "team" structure.

**Content Hierarchy:**

```
1. Section label:            "THE SOLUTION"
2. Headline (H2):            "Meet your marketing team."
3. Subheadline:              "10 specialized agents. 22 skills. 6 workflows. All working together."
4. Agent grid:               Visual display of the 10 agents
5. Capability line:          "From strategy to production. No handoffs, no delays."
```

**Agent Grid Design:**

Display 10 agents in a 5x2 grid (desktop) or 2x5 (mobile):

```
Each agent card:
- Icon (simple, geometric, monochrome)
- Name (e.g., "Strategist")
- One-liner (e.g., "Defines positioning and audience")
- Subtle border on hover
- Size: 200px x 160px (desktop)
```

**The 10 Agents:**
1. Strategist: Defines positioning and audience
2. UX Architect: Plans user experience and flow
3. Copywriter: Writes converting headlines and body
4. Wireframer: Creates page structure and layout
5. Developer: Builds production-ready pages
6. SEO Specialist: Optimizes for search visibility
7. Content Writer: Produces long-form articles
8. Auditor: Reviews and improves existing work
9. Designer: Handles visual direction
10. Analyst: Measures and iterates

**Animation Specs:**

| Element | Animation | Trigger | Duration |
|---------|-----------|---------|----------|
| Section label | Fade in | Scroll 20% | 300ms |
| Headline | Fade up | Scroll 30% | 500ms |
| Agent cards | Stagger fade up | 50ms apart, scroll 40% | 400ms each |
| Hover state | Border brighten + lift | Hover | 200ms |

**Alternative layout:** Horizontal scroll carousel on mobile (cards snap).

**Mobile Considerations:**
- 2-column grid, cards stack nicely
- Or: horizontal scroll with snap points
- Reduce card size to fill width with 16px gap

---

### Section 4: How It Works

**Purpose:** Demystify the product. Show simplicity.

**Content Hierarchy:**

```
1. Section label:            "HOW IT WORKS"
2. Headline (H2):            "Three commands. Infinite output."
3. Steps (3):
   Step 1: "Describe your product"
           "Tell the agents what you're building and who it's for."
   
   Step 2: "Pick a workflow"
           "Landing page, blog post, full site. Type the command."
   
   Step 3: "Ship it"
           "Review the output. Deploy. Marketing, done."
```

**Layout Options:**

Option A: **Vertical steps**
- Left: step number (large, muted)
- Right: title + description
- Connector line between steps
- Works well on all screens

Option B: **Horizontal steps with visual**
- Three columns, each with icon, title, description
- Center: mockup showing the flow
- More impressive on desktop

**Recommendation:** Vertical steps. Cleaner, faster to scan.

**Visual Enhancement:**
- Include subtle terminal snippet for step 2:
```
> /landing
Running workflow: landing-page
→ Strategist analyzing...
→ Copywriter drafting...
→ Developer building...
```

**Animation Specs:**

| Element | Animation | Trigger | Duration |
|---------|-----------|---------|----------|
| Step numbers | Scale in from 0.8 + fade | Scroll | 400ms |
| Step content | Fade right | 100ms after number | 400ms |
| Connector line | Draw (height animation) | Between step triggers | 300ms |
| Terminal snippet | Typing effect | Scroll into view | 2000ms |

**Mobile Considerations:**
- Stack vertically (already responsive)
- Full-width terminal snippet
- Connector line becomes subtle dots

---

### Section 5: Who It's For

**Purpose:** Qualification. Help them self-identify.

**Content Hierarchy:**

```
1. Section label:            "WHO IT'S FOR"
2. Headline (H2):            "Built for people who build."
3. Audience cards (3-4):

   Card 1: Technical Founders
   "You can ship a product in a weekend. Marketing takes you months.
   Hazn gives you a team without the hire."

   Card 2: Marketing Leaders
   "Your team of 3 can't keep up. Agencies cost too much.
   Hazn multiplies your output without multiplying headcount."

   Card 3: Agencies
   "Junior talent is expensive and inconsistent.
   Hazn lets senior strategists deliver at scale."

   Card 4 (optional): Growth Teams
   "Experiment velocity limited by production capacity.
   Ship 10 tests this week instead of 2 this month."
```

**Card Design:**
```
Background: #141416 (surface)
Border: 1px solid #27272A
Border-radius: 12px
Padding: 24px
Title: 18px, 600 weight, white
Body: 15px, 400 weight, #A1A1AA
Hover: Border brightens to #3F3F46, subtle lift
```

**Layout:**
- 2x2 grid on desktop (if 4 cards)
- Single column on mobile
- Max-width per card: 400px

**Animation Specs:**

| Element | Animation | Trigger | Duration |
|---------|-----------|---------|----------|
| Cards | Stagger fade up | 75ms apart | 500ms each |
| Card hover | Border + shadow | Hover | 200ms |

**Mobile Considerations:**
- Stack single column
- Full-width cards with 16px margin
- Consider collapsible accordion if too long

---

### Section 6: Founder Story

**Purpose:** Build trust through origin. Show you're operators, not consultants.

**Content Hierarchy:**

```
1. Section label:            "WHO'S BUILDING THIS"
2. Headline (H2):            "Built by operators who felt your pain."
3. Story block:
   "Abdullah and Rizwan have shipped 100s of websites and apps 
   over 35 years combined. Marketing was always the bottleneck.
   
   Agencies were slow. Freelancers were inconsistent. Hiring was expensive.
   
   So they built the marketing team they always wished existed.
   10 agents. One framework. For people like us."

4. Credential pills:         "35 years experience" | "100s of products" | "Built at Autonomous"
```

**Layout:**
- Centered text block, max-width 600px
- No photos needed (optional: small founder avatars)
- Credential pills in a row below story

**Pill Design:**
```
Background: transparent
Border: 1px solid #27272A
Border-radius: 999px (fully rounded)
Padding: 8px 16px
Text: 14px, #A1A1AA
```

**Animation Specs:**

| Element | Animation | Trigger | Duration |
|---------|-----------|---------|----------|
| Story text | Fade up paragraph by paragraph | Scroll | 500ms, 150ms stagger |
| Credential pills | Fade in together | After story | 400ms |

**Mobile Considerations:**
- Pills wrap to multiple rows naturally
- Same centered layout works

---

### Section 7: Early Access

**Purpose:** Drive conversion. Communicate exclusivity and benefits.

**Content Hierarchy:**

```
1. Section label:            "EARLY ACCESS"
2. Headline (H2):            "Join the waitlist. Shape the product."
3. Subheadline:              "First 100 users get founding member benefits."

4. Benefits list:
   ✓ Lock in founding member pricing
   ✓ Direct access to founders on Slack
   ✓ Shape the roadmap with your feedback
   ✓ Extended 60-day trial

5. Waitlist form:            [Tally.so embed]
6. Trust line:               "No spam. Updates every 2 weeks. Unsubscribe anytime."

7. Scarcity signal:          "73 people on the waitlist" (show after 50 signups)
```

**Form Design:**
- Tally.so embed, styled to match dark theme
- Single email field + submit button
- Consider custom styling if Tally allows

**Benefits List Design:**
```
Checkmark: #22C55E (success green)
Text: #FAFAFA
Spacing: 12px between items
```

**Animation Specs:**

| Element | Animation | Trigger | Duration |
|---------|-----------|---------|----------|
| Headline | Fade up | Scroll | 500ms |
| Benefits | Stagger fade in | 100ms apart | 400ms each |
| Form | Fade up + subtle glow | After benefits | 600ms |
| Waitlist count | Count up animation | On view | 1500ms |

**CTA Button (in form):**
```
Text: "Join the waitlist"
Full-width on mobile
Same blue style as hero CTA
```

**Mobile Considerations:**
- Full-width form
- Benefits list stacks naturally
- Ensure Tally embed is responsive

---

### Section 8: Footer

**Purpose:** Minimal links, legal, social.

**Content Hierarchy:**

```
1. Logo:                     "Hazn" wordmark
2. Tagline:                  "Marketing agents for builders."
3. Links:                    Twitter/X | Contact | Privacy
4. Copyright:                "© 2025 Autonomous"
```

**Layout:**
- Single row on desktop: logo left, links center, copyright right
- Stacked on mobile: logo, links, copyright

**Design:**
```
Background: Same as page (#0A0A0B)
Border-top: 1px solid #27272A
Padding: 48px vertical
Text: #71717A (muted)
Links: #A1A1AA, hover: #FAFAFA
```

**No animations.** Footer should feel grounded.

---

## CTA Placement Strategy

### Primary CTAs (Join Waitlist)

| Location | Type | Context |
|----------|------|---------|
| Hero | Button | First impression, highest visibility |
| Early Access | Form embed | Dedicated conversion section |
| Sticky header | Small button | Always visible after scroll |

### Sticky Header CTA

**Behavior:**
- Hidden at page load
- Appears after scrolling past hero (100vh)
- Contains: "Hazn" wordmark + "Join waitlist" small button
- Height: 56px
- Background: #0A0A0B with blur(8px) backdrop

**Animation:**
- Slide down from top, 300ms, ease-out

### Secondary CTAs

| Location | Action |
|----------|--------|
| Post-signup confirmation | "Share with a founder" |
| Footer | "Follow on X" |

---

## Mobile Breakpoint Strategy

### Breakpoints

```
Mobile:     < 640px   (full-width, stacked)
Tablet:     640-1024px (2-column grids)
Desktop:    > 1024px  (full layout)
Large:      > 1280px  (max-width container, centered)
```

### Container

```
Max-width: 1200px
Padding:   24px (mobile), 48px (tablet+), 64px (large)
```

### Mobile-Specific Adjustments

| Section | Desktop | Mobile |
|---------|---------|--------|
| Hero | Side-by-side text + visual | Stacked, visual optional |
| Agent grid | 5x2 grid | 2-column or horizontal scroll |
| How It Works | Horizontal steps | Vertical stack |
| Who It's For | 2x2 grid | Single column |
| Footer | Horizontal row | Stacked |

### Touch Considerations

- All tap targets: minimum 44px
- Adequate spacing between interactive elements
- No hover-dependent information (use tap)
- Swipe gestures for any carousels

---

## Performance Considerations

### Loading Strategy

1. **Critical CSS inlined** (hero section styles)
2. **Fonts:** Inter preloaded, system fallback during load
3. **Images:** WebP format, lazy-loaded below fold
4. **Animations:** Respect `prefers-reduced-motion`
5. **Tally.so:** Load after LCP (defer)

### Animation Performance

- Use `transform` and `opacity` only (GPU-accelerated)
- Avoid animating `width`, `height`, `margin`
- `will-change` on animated elements
- IntersectionObserver for scroll triggers (not scroll events)

### Target Metrics

```
LCP:  < 2.5s
FID:  < 100ms
CLS:  < 0.1
```

---

## Component Library Summary

| Component | Usage |
|-----------|-------|
| `Button` | Primary CTA, secondary actions |
| `Card` | Agent cards, audience cards |
| `SectionHeader` | Label + headline + subhead |
| `FeatureList` | Benefits, pain points |
| `Terminal` | Code mockup in hero, how it works |
| `Pill` | Credential tags, metadata |
| `Form` | Tally.so embed wrapper |
| `StickyHeader` | Scroll-triggered nav |
| `Footer` | Site footer |

---

## Scroll Journey Summary

```
0vh     Hero: Headline, CTA, terminal mockup
100vh   Problem: Pain points, transition
180vh   Solution: Agent grid
280vh   How It Works: 3 steps, terminal
360vh   Who It's For: Audience cards
440vh   Founder Story: Origin narrative
520vh   Early Access: Benefits, waitlist form
580vh   Footer
```

**Total scroll:** ~6 viewport heights (adjust based on content)

---

## Next Steps

1. **Copywriter:** Write all section copy based on this hierarchy
2. **Wireframer:** Create low-fi layouts from this spec
3. **Developer:** Build with these animation specs

---

*Blueprint complete. This document defines UX structure, animations, and component specifications for the Hazn v2 waitlist landing page.*

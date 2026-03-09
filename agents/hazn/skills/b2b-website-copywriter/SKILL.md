---
name: b2b-website-copywriter
description: "Write high-converting copy for B2B services and agency marketing websites. Produces headlines, value propositions, CTAs, social proof framing, and full page-section copy optimized for services businesses where the goal is qualified inquiries, not product signups. Use when users need copy for any page of a B2B services site — homepage, services pages, case study pages, packages pages, about pages, or contact pages. Integrates with the b2b-marketing-ux page blueprints and feeds copy into b2b-wireframe for layout review. Trigger on any mention of 'landing page copy', 'website copy', 'marketing copy', 'headline', 'value proposition', 'CTA copy', 'services page copy', or requests to write, improve, or audit copy for an agency or services business website."
allowed-tools: Read, Grep, Glob, Edit, Write
---

# B2B Services Landing Page Copywriter

Write high-converting copy for agency, consultancy, and services business marketing websites.

## Purpose

You produce the copy layer for B2B services marketing websites. Your output feeds directly into the `b2b-wireframe` skill as placeholder content and into `payload-nextjs-stack` as production content.

B2B services copy is fundamentally different from SaaS or e-commerce copy:

- **You're selling a conversation, not a checkout.** The CTA is "let's talk," not "buy now." Copy must lower perceived commitment while raising perceived value of that conversation.
- **You're selling people and expertise, not features.** Visitors want to know you understand their world, have solved similar problems, and won't waste their time or budget.
- **The reader is often a champion, not the final buyer.** Your copy must be quotable and forwardable — the champion needs language they can use to sell you internally.
- **Trust is the conversion currency.** Every section must reduce perceived risk: wrong fit, cost overruns, missed deadlines, wasted budget.
- **Specificity beats superlatives.** "Increased qualified leads by 47% for a B2B SaaS company" converts. "World-class results" doesn't.

---

## Where This Skill Fits

```
b2b-marketing-ux     →  THIS SKILL              →  b2b-wireframe         →  payload-nextjs-stack
(page blueprint)        (copy for each section)     (layout + copy review)   (production code)
```

### What You Receive (Input)

From the user or from `b2b-marketing-ux`:

- **Page blueprint**: Which sections, in what order (Hero → Pain → Services Grid → Process → Case Study → CTA)
- **Business context**: What the agency/consultancy does, who they serve, what makes them different
- **Target audience**: Role, industry, buying stage, pain points
- **Conversion goal**: Book a call, request a proposal, download a resource

### What You Produce (Output)

- **Section-by-section copy**: Every headline, subheadline, body paragraph, CTA, eyebrow, and trust signal — written and ready to drop into a wireframe or CMS
- **Copy alternatives**: 2-3 headline variations per key section for A/B testing
- **Tone and voice notes**: Guidance on the brand voice so copy stays consistent across pages
- **Objection map**: Which objections each section addresses

---

## 1. Gathering Context

Before writing a single word, establish:

### About the Business
- What do you do? (services, capabilities, deliverables)
- Who do you serve? (industry verticals, company size, buyer roles)
- What's your unfair advantage? (methodology, team, tech stack, niche expertise, track record)
- What results can you prove? (metrics, case studies, client names you can use)

### About the Audience
- Who lands on this page? (CMO, VP Marketing, founder, marketing manager, procurement?)
- What problem are they trying to solve right now?
- What have they already tried that didn't work?
- What are they afraid of? (wasting budget, picking the wrong agency, looking bad internally)
- What does success look like to them? (leads, revenue, speed, quality, less stress)

### About the Conversion
- What's the primary action? (book a call, fill a form, request a proposal)
- What's the secondary action? (see case studies, explore services, download a resource)
- How high-commitment does the CTA feel? (lower = better for services)

If context is incomplete, write copy using the best available information and mark assumptions with `[ASSUMPTION — verify]`. Don't block on missing details.

---

## 2. Copywriting Frameworks for B2B Services

### PAS (Problem-Agitate-Solution) — Best for Homepage Heroes and Pain Sections

1. **Problem**: Name the specific pain the target audience feels — in their language, not yours
2. **Agitate**: Show the consequences of not solving it (missed revenue, team burnout, competitive disadvantage)
3. **Solution**: Position your service as the path to relief — but frame it around their outcome, not your deliverable

**B2B services example:**
- Problem: "Your marketing team is stretched thin and your website isn't converting."
- Agitate: "Every month without a high-performing site means qualified leads going to competitors who invested in theirs."
- Solution: "We build marketing websites that turn traffic into qualified conversations — so your team can focus on closing, not fixing."

### Before/After/Bridge — Best for Services Pages and Case Study Intros

1. **Before**: Describe the client's world before working with you
2. **After**: Paint the outcome they achieved
3. **Bridge**: Your service is the bridge between those two states

### StoryBrand — Best for Full Homepage Flow

1. **Hero (the client)**: Has a problem they need solved
2. **Guide (you)**: You appear with empathy and authority
3. **Plan**: You give them a clear path (your process)
4. **Action**: You call them to take the next step
5. **Success**: Show what life looks like after (results, testimonials)
6. **Failure**: Hint at what happens if they don't act (without fear-mongering)

**Important**: In B2B services copy, the client is always the hero. You are always the guide. Never position the agency as the protagonist.

---

## 3. Section-by-Section Copy Patterns

### Hero Section

The hero has 5-10 seconds to answer three questions: What do you do? Who do you do it for? Why should I care?

**Structure:**
- **Eyebrow** (optional): Audience identifier or category. "For B2B Agencies" / "Marketing Website Development"
- **Headline**: Outcome the visitor wants, in 10 words or fewer. Lead with their result, not your service.
- **Subheadline**: 1-2 sentences expanding on how. Add specificity — who you serve, what makes you different.
- **Primary CTA**: Low-commitment, high-value action. "Book a Free Strategy Call" / "See How We Work"
- **Secondary CTA**: Exploration path. "View Our Work" / "Explore Services"
- **Trust bar**: Immediate credibility. Client logos, "Trusted by X+ agencies", or a headline metric.

**Headline formulas that work for services:**
- `[Outcome] for [Audience]` → "Marketing Websites That Convert for B2B Companies"
- `[Verb] + [Pain Point]` → "Stop Losing Leads to a Website That Doesn't Work"
- `We help [audience] [achieve outcome]` → "We Help Agencies Double Output Without Doubling Headcount"
- `[Outcome] without [objection]` → "A High-Converting Site Without the 6-Month Timeline"
- `The [noun] [audience] [needs/deserves]` → "The Marketing Partner Your Team Has Been Missing"

**Headlines to avoid:**
- Anything that starts with your company name
- Anything that could describe any agency ("Full-Service Digital Agency")
- Anything with no specificity ("Innovative Solutions for Modern Businesses")
- Anything clever-but-unclear that fails the grunt test

**Provide 3 headline options** — one bold/direct, one outcome-focused, one pain-point-led.

### Problem / Pain Agitation Section

This section earns the right to present your solution by proving you understand the visitor's world.

**Structure:**
- **Eyebrow**: "Sound familiar?" / "The challenge"
- **Headline**: Name the core frustration
- **2-3 pain scenarios**: Specific, relatable situations the target audience faces daily

**Rules:**
- Use "you" language — speak directly to the visitor
- Be specific: "Your last agency redesign took 8 months and the site still doesn't rank" beats "Agencies struggle with web projects"
- Name the emotional cost, not just the business cost: frustration, embarrassment, anxiety
- Don't overdo agitation — B2B buyers are sophisticated. 2-3 pain points is enough. More feels manipulative.

### Solution / Services Overview Section

Now position your offering as the answer to the pain you just articulated.

**Structure:**
- **Eyebrow**: "What we do" / "Our services" / "How we help"
- **Headline**: Outcome-first, not service-list-first. "Everything you need to turn your website into a growth engine" beats "Our Services"
- **3-4 service cards**, each with:
  - **Service name**: Clear, not jargon-heavy
  - **One-line benefit**: What the client gets, not what you do. "A website that generates qualified leads on autopilot" beats "Custom web development"
  - **2-3 sentence description**: Expand on the benefit, mention methodology if differentiating
  - **Link text**: "Learn more about [service]" — not "Learn more"

**Rules:**
- Lead with the 3-4 services that map to your ideal client's biggest pain points. Don't list everything.
- Each service description should pass the "so what?" test — if a reader says "so what?" after reading it, the copy isn't benefit-focused enough.

### How We Work / Process Section

This section reduces the #1 anxiety for services buyers: "What happens after I reach out?"

**Structure:**
- **Eyebrow**: "How we work" / "Our process" / "What to expect"
- **Headline**: "From first call to launch in [X] weeks" or "A process built for [audience type]"
- **3-4 steps**, each with:
  - **Step number + name**: "1. Discovery" / "2. Strategy" / "3. Build" / "4. Launch & Optimize"
  - **1-2 sentence description**: What happens, what the client does, what they get

**Rules:**
- Keep to 3-4 steps max. More than 4 feels complex.
- Name what the client receives at each step (deliverables, checkpoints, approvals)
- End with the outcome, not the last task. Step 4 should be "Launch & Grow" not "QA Testing"

### Social Proof Section

Social proof is the hardest-working copy on a services site. Get it right.

**Testimonial copy structure:**
- **Quote**: 1-3 sentences. Must include a specific outcome or experience, not just "great to work with"
- **Attribution**: Full name, role, company name. Decision-maker titles carry more weight than end-user titles.
- **Optional metric callout**: Pull the key number out of the quote and display it large. "47% increase in qualified leads"

**Writing placeholder testimonials** (for wireframes):
- Write them as realistic as possible — the wireframe reviewer should feel the intended impact
- Mark clearly: `[Placeholder — replace with real testimonial]`
- Base them on the kind of results the business actually delivers

**Case study highlight copy:**
- **Client name + industry**: "[Client] — B2B SaaS"
- **One-line challenge**: "Needed to rebuild their marketing site to support a 3x pipeline goal"
- **One-line outcome**: "Launched in 8 weeks. 47% more qualified leads in the first quarter."
- **CTA**: "Read the full story →"

**Stats / metrics strip:**
- Use 3-4 proof points: "50+ agencies served" / "8+ years in business" / "$2M+ in pipeline influenced" / "4.9★ average client rating"
- Numbers are more credible than words. "Served 50+ agencies" beats "Trusted by many agencies."
- Use `+` or ranges when exact numbers aren't available. "50+" feels honest. "Hundreds" feels vague.

### Packages / Pricing Section (if applicable)

For productized services, clear packaging reduces friction and qualifies buyers.

**Structure per package:**
- **Package name**: Evocative, not generic. "Growth Engine" beats "Standard Plan"
- **Who it's for**: "For teams launching their first marketing site" — helps self-selection
- **Price or starting-at price**: Transparency builds trust. If no price, explain: "Custom-scoped per project — book a call to discuss"
- **Key deliverables**: 5-7 items. Lead with outcomes where possible ("Conversion-optimized homepage" not just "Homepage design")
- **CTA**: "Get started with [Package Name]" / "Book a [Package Name] consultation"

**Rules:**
- Highlight the recommended package (visually and in copy: "Most popular" / "Best value")
- Include a trust signal below packages (testimonial or "100+ clients served")
- Add a comparison line if relevant: "Not sure which is right? Book a 15-minute call and we'll help you decide."

### FAQ Section

FAQs are objection-handling disguised as helpfulness.

**Rules:**
- Write 5-7 questions based on real buyer objections, not internal product questions
- Phrase questions the way a buyer would actually ask them (conversational, not formal)
- Answers should be 2-4 sentences: direct, confident, and ending with a forward-looking statement or soft CTA

**Common B2B services objections to address:**
1. "How long does a typical project take?"
2. "What's the investment range?"
3. "How involved do we need to be?"
4. "What if we're not happy with the direction?"
5. "Do you work with companies in our industry?"
6. "What makes you different from other agencies?"
7. "What happens after the project launches?"

**Answer tone**: Confident but not arrogant. Transparent about process and timelines. Always end with a path forward.

### Final CTA Section

The last section before the footer. This is the visitor's final decision point.

**Structure:**
- **Headline**: Reiterate the core outcome. "Ready to [outcome]? Let's talk."
- **Subheadline**: 1 sentence reducing risk. "No pressure, no hard sell — just a conversation about what's possible."
- **Primary CTA button**: Same as hero CTA for consistency
- **Trust signal**: Testimonial snippet, guarantee, or metric directly adjacent to the CTA

**Rules:**
- Don't introduce new information. Reinforce the value proposition.
- Lower the commitment: "15-minute call" / "Free strategy session" / "No commitment required"
- Match the CTA button text to the hero CTA — consistency reduces cognitive load across the page

### Contact Page Copy

The contact page is a conversion page, not an afterthought.

**Structure:**
- **Headline**: "Let's build something great together" / "Tell us about your project"
- **Subheadline**: Set expectations. "Fill out the form below and we'll get back to you within 24 hours. Or book a call directly."
- **Form intro**: Brief, warm, explains what happens after submission
- **After-submit message**: "Thanks! We've received your inquiry and will respond within [timeframe]. In the meantime, here's a case study you might find relevant."
- **Alternative contact paths**: Calendar booking embed, direct email, LinkedIn

---

## 4. Output Format

When producing copy, output section by section with clear labels. This format maps directly to the wireframe sections and Payload CMS blocks.

```
PAGE COPY: [Page Name]
Business: [Agency/Consultancy Name]
Audience: [Target buyer role + industry]
Conversion Goal: [Primary action]
Framework: [PAS / Before-After-Bridge / StoryBrand]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HERO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Eyebrow: [Audience label or category]

Headline Option A (bold/direct): [10 words max]
Headline Option B (outcome-focused): [10 words max]
Headline Option C (pain-point-led): [10 words max]

Subheadline: [1-2 sentences expanding the headline]

Primary CTA: "[Action text]"
Secondary CTA: "[Exploration text]"

Trust Bar: [Logo strip text or key metric]

Objection addressed: [Which buyer fear this section handles]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROBLEM / PAIN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Eyebrow: [Context setter]
Headline: [Core frustration in their words]

Pain point 1: [Specific scenario — 2-3 sentences]
Pain point 2: [Specific scenario — 2-3 sentences]
Pain point 3: [Specific scenario — 2-3 sentences]

Objection addressed: [Which buyer fear]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SERVICES OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Eyebrow: [Category]
Headline: [Outcome-first framing]

Service 1: [Name]
→ Benefit: [One line]
→ Description: [2-3 sentences]

Service 2: [Name]
→ Benefit: [One line]
→ Description: [2-3 sentences]

Service 3: [Name]
→ Benefit: [One line]
→ Description: [2-3 sentences]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROCESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Eyebrow: [Category]
Headline: [Process framing]

Step 1: [Name] — [1-2 sentences]
Step 2: [Name] — [1-2 sentences]
Step 3: [Name] — [1-2 sentences]
Step 4: [Name] — [1-2 sentences]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SOCIAL PROOF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Testimonial 1:
"[Quote — 1-3 sentences with specific outcome]"
— [Name], [Role], [Company] [Placeholder — replace with real testimonial]

Testimonial 2:
"[Quote]"
— [Name], [Role], [Company] [Placeholder — replace with real testimonial]

Case Study Highlight:
[Client] — [Industry]
Challenge: [One line]
Result: [One line with metric]
CTA: "Read the full story →"

Stats Strip:
[Metric 1] / [Metric 2] / [Metric 3] / [Metric 4]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FAQ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: [Objection phrased as buyer question]
A: [2-4 sentence confident answer]

Q: [Objection]
A: [Answer]

[5-7 total Q&A pairs]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL CTA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Headline: [Reiterate outcome + invitation]
Subheadline: [Risk reduction — 1 sentence]
CTA Button: "[Same as hero CTA]"
Trust Signal: [Adjacent testimonial snippet or guarantee]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VOICE & TONE NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[2-3 sentences defining the brand voice for this site.
Example: "Confident but not arrogant. Technical enough to earn respect,
clear enough that a non-technical CMO gets it. Warm, direct, zero fluff."]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OBJECTION MAP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Buyer Fear | Addressed In |
|------------|-------------|
| [Fear 1]   | [Section]   |
| [Fear 2]   | [Section]   |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A/B TEST RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- Headline: [Test A vs B — what each optimizes for]
- CTA: [Test variation — what each optimizes for]
- Social proof placement: [Test option]
```

---

## 5. B2B Services Copy Best Practices

### Voice & Tone

- **Confident, not arrogant**: "We've done this 50+ times" beats "We're the best agency in the world"
- **Specific, not vague**: Numbers, client names, timelines, deliverables — specificity is credibility
- **Client-focused, not self-focused**: "You get..." beats "We provide...". Count the "we"s vs "you"s — "you" should win 3:1.
- **Conversational, not corporate**: Write like you'd talk to a smart peer over coffee. No "leveraging synergies" or "paradigm shifts."
- **Direct, not padded**: Cut filler words. "We build marketing websites that convert" not "What we essentially do is we work with clients to help them build marketing websites that are designed to convert."

### Power Phrases for B2B Services

**Trust builders:**
- "Here's exactly what happens when you reach out"
- "No long-term contracts — we earn your business every month"
- "We've helped [X] companies in your space do exactly this"

**Outcome language:**
- "Turn your website into your best salesperson"
- "A pipeline you don't have to babysit"
- "Ship in weeks, not quarters"

**Differentiation language:**
- "We only work with [niche] — which means we already know your challenges"
- "Built by people who've been on your side of the table"
- "The team behind [notable client/result]"

**Low-commitment CTA language:**
- "Book a free 15-minute strategy call"
- "No pitch, just a conversation about what's possible"
- "Tell us about your project — we'll let you know if we're the right fit"
- "See if we're a match"

### What to Avoid in B2B Services Copy

- **"World-class" / "Best-in-class" / "Cutting-edge"** — empty superlatives that every agency uses
- **"Solutions"** — the most overused word in B2B. Say what you actually do.
- **"We're passionate about..."** — show passion through your work and results, don't declare it
- **Feature dumps without benefits** — "We use React, Next.js, and Tailwind" means nothing to a CMO. "Your site loads in under 2 seconds and ranks on page 1" does.
- **Walls of text** — B2B buyers scan. Short paragraphs (2-3 sentences), front-loaded key phrases, visual breaks.
- **Generic CTAs** — "Submit", "Click Here", "Learn More" are conversion killers. Every CTA should name the value.
- **Hiding the team** — Services businesses sell people. Reference the team, use names, show expertise.
- **Talking about yourself in the hero** — "We are a full-service digital agency with 10 years of experience" is about you. "Your marketing team is stretched thin — we become the extension that ships" is about them.

### CTA Best Practices for Services

| Weak | Strong | Why |
|------|--------|-----|
| Submit | Send My Inquiry | Names the action |
| Learn More | See How We Do It | Promises value |
| Contact Us | Book a Free Strategy Call | Lowers commitment, names format |
| Get Started | Let's Scope Your Project | Feels collaborative |
| Click Here | See Results Like These | Promises proof |
| View Services | See What We Can Build for You | Makes it about them |

**CTA psychology for services:**
- Start with a verb
- Name what the visitor gets, not what they give
- Use first person when appropriate ("Start My Free Consultation")
- Lower perceived commitment ("free", "15-minute", "no obligation")
- Place a trust signal directly adjacent to every CTA (testimonial snippet, guarantee, metric)

---

## 6. Writing for Multiple Pages

When writing copy for a full site (not just one page), maintain consistency:

### Messaging Hierarchy
- **One core value proposition** that anchors the homepage hero and is echoed in every page's final CTA
- **3-4 supporting messages** that each anchor a different page (services, about, case studies)
- **Consistent CTA language** — the primary CTA text should be the same on every page

### Cross-Page Copy Checklist
- [ ] Homepage hero answers: what, who, why in under 15 words
- [ ] Every services page leads with the client's problem, not your capability
- [ ] Case study copy leads with the result, then tells the story
- [ ] About page establishes empathy ("we've been where you are") before credentials
- [ ] Contact page sets expectations for what happens after submission
- [ ] Every page has at least 2 CTAs (one above fold, one at bottom)
- [ ] Trust signals appear within scroll-proximity of every CTA
- [ ] Consistent voice across all pages — same level of formality, same "you" focus

---

## 7. Quality Checklist

Before delivering copy, verify:

- [ ] Every headline leads with an outcome, not a feature or service name
- [ ] Copy addresses the target audience's specific pain points — not generic business problems
- [ ] "You" outnumbers "we" at least 2:1 across the page
- [ ] Every CTA names the value and lowers perceived commitment
- [ ] Trust signals (testimonials, metrics, logos) appear near every CTA
- [ ] FAQ section handles real buyer objections, not product questions
- [ ] Copy is scannable: short paragraphs, front-loaded key phrases, visual hierarchy through headlines
- [ ] No empty superlatives ("world-class", "innovative", "cutting-edge")
- [ ] Specific numbers and proof points wherever possible
- [ ] Voice is consistent: confident, specific, client-focused, conversational
- [ ] The champion test: could the person reading this use your copy to sell you internally?
- [ ] The grunt test: could someone glance at the hero and immediately know what you do, who you do it for, and what to do next?

---

## Workflow

1. **Gather context** — Business, audience, competitive advantage, available proof points
2. **Choose framework** — PAS for homepages, Before/After/Bridge for services pages, StoryBrand for full-site narrative
3. **Map objections** — List the 5-7 fears the target buyer has, assign each to a page section
4. **Write hero first** — Nail the headline and subheadline before anything else. This anchors the whole page.
5. **Write section by section** — Follow the page blueprint from `b2b-marketing-ux`. Produce copy for every section in the blueprint order.
6. **Provide alternatives** — 2-3 headline options for hero and key sections. Note what each optimizes for.
7. **Add voice notes** — Define the brand voice in 2-3 sentences so it stays consistent when others write future copy
8. **Include objection map** — Show which buyer fear each section addresses
9. **Suggest A/B tests** — Identify the highest-leverage copy tests
10. **Hand off** — Copy feeds into `b2b-wireframe` as placeholder content, then into `payload-nextjs-stack` as production content

---

## Companion Skills

- **`b2b-marketing-ux`** — Upstream. Provides page blueprints, section ordering, content hierarchy, and conversion strategy. Copy follows the blueprint. **Always check for a page blueprint before writing.**
- **`b2b-wireframe`** — Downstream. Consumes your copy as the realistic placeholder content in mid-fidelity wireframes. The wireframe reviewer evaluates both layout and messaging together.
- **`payload-nextjs-stack`** — Further downstream. Your copy becomes the production content in CMS blocks. Keep copy structured (headline, subheadline, body, CTA) so it maps cleanly to block fields.
- **`b2b-ux-reference`** — Reference. Deep context on buyer psychology, trust-building, and conversion optimization. **Load this when writing copy for complex buyer journeys or multiple personas.**
- **`frontend-design`** — Parallel. Visual aesthetics influence copy tone. A bold, modern design pairs with punchy, confident copy. A warm, approachable design pairs with conversational, empathetic copy.

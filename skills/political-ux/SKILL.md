---
name: political-ux
description: "UX strategy, page architecture, and legitimacy design for political organizations, associations, parties, and advocacy groups. Use this skill when building websites for political parties, trade associations (Verbände), international political alliances (like IDU), campaign sites, lobbying organizations, or policy advocacy groups. Covers audience segmentation (members, politicians, journalists, public), issue framing, coalition signals, and trust architecture. For code implementation, pair with `payload-nextjs-stack` or `wordpress-stack`. For visual layout review, use `wireframe`."
---

# Political Organization Website UX

## Purpose

You are responsible for UX strategy, page architecture, content hierarchy, and legitimacy design for political organization websites — parties, associations (Verbände), international alliances, campaigns, advocacy groups, and lobbying organizations.

These are not commercial websites selling services. They are **legitimacy engines**. The website's job is to:

1. **Establish authority** — Show the organization represents a real constituency
2. **Frame issues** — Control the narrative on policy positions
3. **Build coalitions** — Signal alignment with allies and broader movements
4. **Mobilize action** — Drive membership, donations, contact with officials, or public support
5. **Serve multiple audiences** — Members, potential members, politicians/regulators, journalists, and the general public each need different things

This skill handles the "what" and "why" of political website design. For the "how" (code implementation), load `payload-nextjs-stack` or `wordpress-stack` alongside this one. For visual layout review before coding, use `wireframe`.

---

## Before You Build Anything

Every page and component decision flows from these questions:

1. **Who are the audiences?** (members, potential members, politicians, journalists, public — prioritize)
2. **What is the core narrative?** (How does this org want to be perceived? What worldview does it embody?)
3. **What are we positioning against?** (Every political org defines itself partly in opposition — to what?)
4. **What actions matter?** (Join, donate, contact officials, share, subscribe to updates?)
5. **What legitimacy signals exist?** (Member count, economic impact, history, allied organizations, prominent supporters)

Write these answers as a brief comment block at the top of every page-level component. This prevents the #1 political website mistake: talking about the organization instead of the cause.

---

## Core UX Principles for Political Organization Sites

### 1. Legitimacy Before Persuasion

Visitors are skeptical of political organizations. Before they'll accept your framing on issues, they need to believe you're legitimate — that you represent real people with real stakes.

**Legitimacy hierarchy (use in order of impact):**

1. **Representation scale** — "We represent X members" / "X companies employing Y workers"
2. **Economic/social contribution** — Jobs, tax revenue, community investment, tradition
3. **Named members/supporters** — Recognizable companies, individuals, or allied organizations
4. **History and continuity** — "Since 1920" signals permanence and credibility
5. **Leadership visibility** — Named board members, spokespersons with credentials
6. **Geographic presence** — Regional roots, local chapters, national/international reach
7. **Media recognition** — Press coverage, citations, official consultations

Place legitimacy signals on the homepage hero or immediately below. Don't bury them.

### 2. Issue Framing Is the Product

The website exists to frame issues favorably. Every policy position page must:

- **Name the stakes** — What's at risk if the wrong policy prevails?
- **State the position clearly** — No bureaucratic hedging
- **Provide evidence** — Data, studies, member testimonials, economic impact
- **Counter the opposition frame** — What's the unfair characterization? Preempt it.
- **Offer a path forward** — What should policymakers/public do?

### 3. Multiple Audiences, Clear Paths

Unlike B2B sites with one buyer persona, political sites serve distinct audiences:

| Audience | Primary Need | Key Pages |
|----------|--------------|-----------|
| **Members** | Updates, resources, community | Member portal, news, events |
| **Potential members** | Why join, what's in it for me | Membership page, benefits, member directory |
| **Politicians/Regulators** | Position briefs, data, contact | Policy positions, research, press contact |
| **Journalists** | Quotes, data, spokesperson access | Press page, media kit, news releases |
| **General public** | Understanding the org's role | About, issue explainers, impact stories |

Design the navigation and homepage to give each audience a clear entry point.

### 4. Coalition Signals Build Power

Political organizations gain strength through perceived coalitions. Show:

- **Allied organizations** — Logo grids of partners, joint statements
- **Member diversity** — Not monolithic; show range of member types
- **Broader movement alignment** — Connection to widely-held values (family, community, freedom, tradition, etc.)
- **Endorsements** — Politicians, thought leaders, or respected figures who support the org

### 5. Counter-Positioning Without Mud

Political orgs often face hostile framing (e.g., tobacco = big tobacco, not family Mittelstand). The website must counter without appearing defensive or attacking.

Techniques:
- **Lead with your frame** — "Family businesses since 1920" not "We're not big tobacco"
- **Humanize with specifics** — Named members, real locations, real faces
- **Use Mittelstand/underdog positioning** — Small vs. big, local vs. foreign, traditional vs. radical
- **Let data speak** — Employment numbers, tax contributions, regional impact

### 6. Mobile and Accessibility Are Non-Negotiable

Politicians' staffers check sites on phones. Journalists on deadline need fast access. All principles from B2B apply here:

- Touch targets: minimum 44x44px
- Body text: minimum 16px on mobile
- Single-column layouts on mobile
- CTAs must be thumb-reachable
- Navigation: hamburger on mobile, primary CTA always visible
- Target: LCP < 2.5s, FID < 100ms, CLS < 0.1

---

## Page Architecture for Political Organizations

### Standard Site Map

```
/                    → Homepage: positioning + legitimacy + key issues
/themen              → Policy positions hub (or /positionen, /issues)
/themen/[slug]       → Individual position page
/verband             → About: history, mission, structure (or /about, /ueber-uns)
/vorstand            → Leadership: board, team, spokespersons
/mitglieder          → Member directory / showcase
/mitglied-werden     → Membership CTA page (or /join)
/aktuelles           → News hub
/aktuelles/[slug]    → Individual news/press release
/presse              → Press page: releases, media kit, contact
/veranstaltungen     → Events (if applicable)
/kontakt             → Contact page
```

### Homepage Blueprint

The homepage must establish legitimacy, frame the core narrative, and route audiences to their needs.

```
┌─────────────────────────────────────────┐
│ Navigation                              │
│ - Logo + org name                       │
│ - Key nav items: Themen, Verband,       │
│   Mitglieder, Aktuelles, Presse         │
│ - Primary CTA (Mitglied werden/Kontakt) │
├─────────────────────────────────────────┤
│ Hero Section                            │
│ - Positioning statement (identity, not  │
│   ask). E.g., "Mittelstand und Genuss   │
│   seit 1920"                            │
│ - Supporting line: who you represent    │
│ - Legitimacy metric ("X Mitglieder,     │
│   Y Arbeitsplätze")                     │
│ - CTA: Learn more about us / Our        │
│   positions                             │
├─────────────────────────────────────────┤
│ Key Issues / Positions Teaser           │
│ - 3-4 top policy positions with         │
│   headline + brief framing + link       │
├─────────────────────────────────────────┤
│ About / Identity Section                │
│ - Brief org description                 │
│ - Mittelstand/tradition/values signals  │
│ - Link to full about page               │
├─────────────────────────────────────────┤
│ Member Showcase                         │
│ - Logo grid or featured member stories  │
│ - "X Mitgliedsunternehmen"              │
├─────────────────────────────────────────┤
│ News / Aktuelles                        │
│ - 2-3 recent news items                 │
│ - Link to full news archive             │
├─────────────────────────────────────────┤
│ Coalition / Partner Signals (optional)  │
│ - Allied organizations, endorsements    │
├─────────────────────────────────────────┤
│ CTA Section                             │
│ - Membership or contact CTA             │
├─────────────────────────────────────────┤
│ Footer                                  │
│ - Contact info, legal, social links     │
└─────────────────────────────────────────┘
```

### Policy Position Page Blueprint

Each position page is a persuasion document for policymakers and journalists.

```
┌─────────────────────────────────────────┐
│ Eyebrow: Policy Area                    │
│ Headline: Position in clear language    │
│ Subheadline: Stakes / why it matters    │
├─────────────────────────────────────────┤
│ The Issue                               │
│ - Context: what's happening             │
│ - Threat/opportunity: what's at stake   │
├─────────────────────────────────────────┤
│ Our Position                            │
│ - Clear statement of what we advocate   │
│ - Key arguments (3-5 points)            │
├─────────────────────────────────────────┤
│ Evidence / Impact                       │
│ - Data, statistics, studies             │
│ - Member testimonials or case examples  │
│ - Economic/social impact metrics        │
├─────────────────────────────────────────┤
│ What Should Happen                      │
│ - Policy recommendations                │
│ - Call to action for policymakers       │
├─────────────────────────────────────────┤
│ Downloads / Resources                   │
│ - Position paper PDF                    │
│ - Related studies or fact sheets        │
├─────────────────────────────────────────┤
│ Press Contact                           │
│ - Spokesperson for this issue           │
│ - Contact info for journalists          │
├─────────────────────────────────────────┤
│ Related Positions                       │
│ - Links to related policy areas         │
└─────────────────────────────────────────┘
```

### Member Directory Page Blueprint

Shows representation breadth and lets visitors find specific members.

```
┌─────────────────────────────────────────┐
│ Headline: Our Members                   │
│ Subheadline: "X companies representing  │
│   Y employees across Germany"           │
├─────────────────────────────────────────┤
│ Filter/Search (optional)                │
│ - By region, by size, alphabetical      │
├─────────────────────────────────────────┤
│ Member Grid                             │
│ - Logo + company name + location        │
│ - Link to member detail or external site│
├─────────────────────────────────────────┤
│ Membership CTA                          │
│ - "Become a member" for eligible orgs   │
└─────────────────────────────────────────┘
```

### Press Page Blueprint

Journalists need fast access to information and contacts.

```
┌─────────────────────────────────────────┐
│ Headline: Press & Media                 │
├─────────────────────────────────────────┤
│ Press Contact                           │
│ - Spokesperson name, title, photo       │
│ - Email, phone (direct line)            │
│ - Response time commitment              │
├─────────────────────────────────────────┤
│ Latest Press Releases                   │
│ - Recent releases with dates + download │
├─────────────────────────────────────────┤
│ Media Kit                               │
│ - Logo downloads (various formats)      │
│ - Fact sheet / org overview PDF         │
│ - Key statistics                        │
│ - Approved photos / imagery             │
├─────────────────────────────────────────┤
│ Key Positions Summary                   │
│ - Quick reference to main policy stances│
├─────────────────────────────────────────┤
│ Recent Media Coverage (optional)        │
│ - Links to press mentions               │
└─────────────────────────────────────────┘
```

---

## Design Philosophy

### Visual Language for Political/Association Sites

1. **Gravitas over flash** — These sites need to feel established, serious, credible. No startup energy. Institutional but not stuffy.

2. **Tradition signals** — "Seit 1920", heritage imagery, serif accents in typography. History = legitimacy.

3. **Conservative design values** — Clean, ordered, structured. Typography that conveys stability. Colors that code to tradition/authority (blues, deep reds, golds, earth tones).

4. **Real photography** — Never generic stock. Real members, real facilities, real events, real regional landscapes. Authenticity is everything.

5. **Political neutrality in design** — Avoid colors that code to specific parties unless that's the intent. Use industry-appropriate or org-specific colors.

6. **Accessible information architecture** — Politicians' staffers and journalists need to find positions fast. Clear nav, good search, downloadable PDFs.

### Typography Recommendations

- **Headings**: Serif for tradition (Merriweather, Lora, Source Serif) or strong sans for modernity (Outfit, DM Sans, Space Grotesk)
- **Body**: Clean readable sans (Inter, Work Sans, Source Sans)
- **German sites**: Ensure proper support for umlauts and ß; test readability in German sentence structures

### Photography Direction

- Workshops, facilities, craftsmanship
- Regional landscapes (German countryside, industrial heritage)
- Real people at work (not posed stock)
- Events, member gatherings
- Leadership in professional but accessible settings

---

## Discovery Questions for Clients

### Identity & Positioning
- What is the core narrative you want to project?
- Who are you positioning against or distinct from?
- What's the "unfair framing" you're fighting? How do opponents characterize your industry/movement?

### Audiences
- Priority ranking: members, potential members, politicians/regulators, journalists, general public?
- Which political bodies/individuals matter most? Federal, state, EU?
- Do you have active press relationships?

### Content & Issues
- What are your 3-5 core policy positions?
- For each: what's the current threat or opportunity? What's your ask?
- Do you have existing position papers, studies, data?
- What member success stories can we tell?

### Membership
- Is membership acquisition a goal for the site?
- What does membership include? Who's eligible?
- Any membership tiers?

### Operations
- Who updates the site? How often?
- Event functionality needed?
- Newsletter/subscription?
- Multi-language? (German + English for EU audience?)

---

## Workflow

When building a political organization website:

```
political-ux         →  political-copywriter  →  wireframe  →  implementation
(this skill)             (messaging)             (visual)       (code)
```

1. **Discovery**: Use the questions above to understand positioning, audiences, and content
2. **Page architecture**: Apply blueprints, adapting to org specifics
3. **Content strategy**: Work with `political-copywriter` to develop messaging for each page/section
4. **Wireframe**: Use `wireframe` skill to produce visual layouts for review
5. **Implementation**: Use `payload-nextjs-stack` or `wordpress-stack` for production code

---

## Companion Skills

- **`political-copywriter`** — Messaging frameworks for political organizations. Position statements, coalition language, legitimacy copy.
- **`wireframe`** — Mid-fidelity wireframes for visual review before coding.
- **`payload-nextjs-stack`** — Production code for Payload CMS + Next.js sites.
- **`wordpress-stack`** — Production code for WordPress sites (when applicable).
- **`frontend-design`** — Visual aesthetics and creative direction.

---

## Anti-Patterns — What to Avoid

1. **Leading with asks instead of identity** — "Join us!" before establishing why you matter
2. **Bureaucratic language** — Write for humans, not committees
3. **Hiding the stakes** — Political sites must name what's at risk
4. **Generic stock photography** — Kills credibility instantly
5. **Defensive framing** — "We're not X" instead of "We are Y"
6. **Ignoring journalists** — No press page = no coverage
7. **Monolithic member representation** — Show diversity of membership
8. **No clear issue framing** — Policy pages that don't take a position
9. **Dated design** — "Established" doesn't mean visually stuck in 2005
10. **Missing mobile optimization** — Staffers and journalists are on phones

# IDU Website Redesign — UX Blueprint
**International Democracy Union | idu.org**
**Prepared by:** Hazn UX Architect
**Date:** March 2026
**Version:** 1.0
**Follows:** strategy.md v1.0

---

## Table of Contents

1. [Site Architecture](#1-site-architecture)
2. [Navigation Design](#2-navigation-design)
3. [Page Blueprints](#3-page-blueprints)
   - 3.1 Homepage
   - 3.2 About
   - 3.3 About → Honorary Advisory Board
   - 3.4 About → IYDU
   - 3.5 Members
   - 3.6 News
   - 3.7 Events / Events Directory
   - 3.8 Leadership
   - 3.9 Media Centre
   - 3.10 Privacy Policy
4. [User Flows](#4-user-flows)
5. [Component Library](#5-component-library)
6. [Responsive Notes](#6-responsive-notes)
7. [Accessibility Notes](#7-accessibility-notes)

---

## 1. Site Architecture

### 1.1 Full Navigation Tree

```
idu.org/
│
├── / (Homepage)
│
├── /about/
│   ├── /about/ (Overview — mission, history, governance, values, sub-orgs)
│   ├── /about/honorary-board/ (Honorary Advisory Board)
│   └── /about/iydu/ (International Young Democrat Union)
│
├── /members/
│   └── /members/ (Interactive filterable directory)
│
├── /news/
│   └── /news/ (Filterable news archive — Statements, Resolutions, Event Reports, Awards, Press Releases)
│
├── /events/
│   └── /events/ (Upcoming + past events directory)
│
├── /leadership/
│   └── /leadership/ (Secretary General, Executive Committee, Honorary Officers)
│
├── /media-centre/
│   ├── /media-centre/ (Hub: press releases, press kit, photo library, press contact)
│   └── /media-centre/photo-library/ (Searchable photo archive)
│
└── /privacy-policy/
```

### 1.2 WordPress Content Types

| Content Type | Implementation | Notes |
|---|---|---|
| Pages | WordPress Pages | About, Homepage, Leadership, Media Centre, Privacy Policy |
| News items | WordPress Posts + Custom Taxonomy `news_type` | Values: Statement, Resolution, Event Report, Award, Press Release |
| Member Parties | Custom Post Type `idu_member` | Fields: logo, party name, country, region, status, URL, short description |
| Events | Custom Post Type `idu_event` | Fields: date, location, type, description, image, report link |
| Leadership profiles | Custom Post Type `idu_person` | Fields: role, photo, bio, party, country |
| Media assets | WordPress Media Library + custom metadata | Photo captions: name, date, event |

---

## 2. Navigation Design

### 2.1 Primary Navigation (Desktop)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  [IDU Logo]        About   Members   News   Events   Leadership   Media  │
│                                                          [Member Login ↗] │
└─────────────────────────────────────────────────────────────────────────┘
```

**Behaviour:**
- Fixed/sticky on scroll — remains visible as users navigate long pages
- "About" triggers a dropdown (see 2.2)
- "Media" links to /media-centre/
- "Member Login" is a utility button — right-aligned, distinguished visually (outline style, not filled)
- Active page state: underline indicator in IDU gold/accent colour
- No mega-menus — this is an institutional site, not an e-commerce portal

### 2.2 About Dropdown

```
About ▾
├── About IDU
├── Honorary Advisory Board
└── IYDU
```

Keep dropdown minimal. Sub-organisations other than IYDU are surfaced on the About page itself, not individually in nav — they are components of IDU, not separate top-level entities.

### 2.3 Mobile Navigation

- Hamburger icon (top-right, clearly labelled "Menu")
- Full-screen drawer overlay, dark background
- Navigation items stacked vertically, large tap targets (min 48px)
- "Member Login" appears at bottom of drawer
- Accordion for About sub-pages

### 2.4 Utility Navigation (Header Top Bar — optional)

If a top bar is used above the main nav (common for institutional sites):
```
[Language selector — if multi-language ever added]    [Member Login]    [Press Kit ↓]
```

For launch: keep it simple — Member Login only in utility position.

### 2.5 Footer Navigation

Four-column footer:

```
┌──────────────┬──────────────┬──────────────────────┬────────────────────┐
│  IDU          │  Navigate     │  Sub-Organisations    │  Contact           │
│  [Logo]       │               │                       │                    │
│               │  About        │  IYDU                 │  info@idu.org      │
│  The global   │  Members      │  IWDU                 │                    │
│  alliance of  │  News         │  CDU                  │  [LinkedIn icon]   │
│  centre-right │  Events       │  DUA                  │  [X/Twitter icon]  │
│  democratic   │  Leadership   │  UPLA                 │                    │
│  parties.     │  Media Centre │  APDU                 │  Press Contact     │
│               │               │                       │  [press@idu.org]   │
└──────────────┴──────────────┴──────────────────────┴────────────────────┘
  © 2026 International Democracy Union  |  Privacy Policy  |  Member Login
```

**Footer design notes:**
- IDU blue background (dark), white text — institutional authority
- Logo in white/reversed version
- Sub-organisation names link to their respective sections on the About page (or external sites if they have their own)
- Bottom bar: slim, copyright + utility links

---

## 3. Page Blueprints

---

### 3.1 Homepage

**URL:** `/`
**Purpose:** Establish authority instantly. Route each audience to their destination. Prove the IDU is active and consequential.
**Tone:** Gravitas. History. Global scale.

---

#### Section 1: Hero

**Purpose:** First impression. Establish institutional weight within 3 seconds.

**Content elements:**
- Full-bleed high-resolution summit photography (formal diplomatic setting — leaders, flags, podiums; NOT abstract or generic)
- Subtle dark overlay (60–70% opacity) to ensure text legibility
- Primary headline: `"The Global Alliance of Centre-Right Democratic Parties"`
- Sub-line: `"Founded in 1983 by Margaret Thatcher, Ronald Reagan, and Helmut Kohl"`
- NO call-to-action button — this is a statement, not a prompt
- IDU logo top-left within the hero space (via sticky nav)

**Layout:** Full-viewport-height (100vh), single static image. No carousel. No auto-play. No parallax (performance cost not justified).

**Interaction notes:**
- On scroll: hero fades/transitions naturally to stats bar below
- Image: sourced from IDU's archive of summit photography; must be >= 2560px wide for full-bleed retina quality
- Image alt text: descriptive of scene (e.g., "IDU Summit, [city], [year] — world leaders gathered")

---

#### Section 2: Stats Bar

**Purpose:** Immediate quantitative proof of scale and permanence.

**Content elements:**
- Four stats in a horizontal strip:
  - `80+` Member Parties
  - `6` Continents
  - `Founded` 1983
  - `40+` Years of Democracy
- Each stat: large numeral, label below

**Layout:** Full-width horizontal band. IDU blue background. White numerals (large, bold), white label text (smaller, regular). Equal-width columns.

**Interaction notes:**
- Stats are static — no animated counting (animation adds no institutional value)
- On mobile: 2×2 grid

---

#### Section 3: Latest News

**Purpose:** Prove the IDU is active. Route media/researchers to current content.

**Content elements:**
- Section label: `"Latest from the IDU"`
- 3 most recent news items, each showing:
  - News type tag (Statement / Resolution / Press Release / etc.)
  - Headline (linked)
  - Date (prominent — day month year format, e.g., "12 February 2026")
  - 1-sentence excerpt
- "View all news →" text link at section end

**Layout:** Three-column card grid (desktop). Each card: top tag (coloured pill), date, headline, excerpt. Minimal visual decoration — these are records, not features.

**Interaction notes:**
- Hover: subtle card elevation / border emphasis
- No featured image required on news cards (optional thumbnail if image available)
- Cards link to individual news articles

---

#### Section 4: Upcoming Events

**Purpose:** Show IDU's ongoing convening power. Route member parties and governments to events.

**Content elements:**
- Section label: `"Upcoming Events"`
- 2–3 next events, each showing:
  - Event date (prominent, large)
  - Event name
  - Location (City, Country)
  - 1-sentence description
- "Full Events Calendar →" text link

**Layout:** Horizontal list/row (not cards — events are time-bound, list format signals precision). Each event: left-aligned date block (day large, month small, year), right: event details.

**Interaction notes:**
- Events link to individual event pages
- If no upcoming events: hide this section entirely (do not show empty section)

---

#### Section 5: Member Parties Preview

**Purpose:** Signal global breadth through visual logo display. Route researchers/media to full directory.

**Content elements:**
- Section label: `"Our Member Parties"`
- Sub-label: `"80+ member parties across 6 continents"`
- Logo strip: scrolling or static display of ~20–30 recognisable party logos
- "View Full Directory →" button (primary style)

**Layout:** Horizontal logo strip with contained scroll (or CSS marquee if logos are numerous). Logos in greyscale with hover → colour to keep visual clean. Logos link to their party's member page entry.

**Interaction notes:**
- Logo strip: CSS scroll animation (subtle, slow, not distracting) or static grid of logos
- Prefer static grid for accessibility — animated strips can cause issues for motion-sensitive users; use `prefers-reduced-motion` to disable animation
- "View Full Directory" CTA is the only explicit button on the homepage below the hero

---

#### Section 6: About the IDU

**Purpose:** Brief institutional description for first-time visitors. Route to About page.

**Content elements:**
- Section label: `"About the IDU"`
- 2–3 sentences: what the IDU is, its founding, its purpose
- "Learn More →" text link to /about/

**Layout:** Centered text block, constrained width (~700px max), generous white space. No imagery needed — the words carry the section.

---

#### Section 7: Bush-Thatcher Award

**Purpose:** Leverage two of the most recognisable names in democratic history as a prestige signal.

**Content elements:**
- Section label: `"Bush-Thatcher Award for Freedom"`
- 1–2 sentence description of the award's significance
- Most recent or most notable winner: photo, name, brief context
- Past winners list (abbreviated: 3–5 names) or "View past recipients →"

**Layout:** Split layout — left: text/description; right: featured winner photo or award imagery. Dark blue or warm neutral background to distinguish from surrounding sections. Gold accent colour for the award name and any decorative elements.

**Interaction notes:**
- "View past recipients →" links to the relevant news/award section or a dedicated anchor on the About page
- If an award ceremony photo exists, use it — formal setting amplifies prestige

---

#### Section 8: Sub-Organisations

**Purpose:** Demonstrate global infrastructure depth. The six regional/thematic bodies prove IDU is not a nominal alliance.

**Content elements:**
- Section label: `"The IDU Family"`
- 6 cards, one per sub-organisation:
  - Logo (if available) or abbreviation badge
  - Full name
  - Region/focus (one line)
  - Brief description (1–2 sentences)
- Each card links to that sub-org's section on the About page (or external site)

**Layout:** 3×2 grid on desktop, 2×3 on tablet, 1×6 (stacked) on mobile. Cards: clean white with IDU blue border-left accent. Uniform height.

**Interaction notes:**
- Hover: subtle lift, border accent intensifies
- If a sub-org has its own site (e.g., iydu.org), external link opens in new tab with `rel="noopener noreferrer"`

---

#### Section 9: Media Centre Quick Access

**Purpose:** Zero-friction access for journalists. Media is audience priority #1.

**Content elements:**
- Section label: `"For the Press"`
- Three quick-access blocks:
  1. **Press Kit** — "Download Press Kit (PDF)" with download icon — one click
  2. **Latest Release** — Title + date of most recent press release, linked
  3. **Press Contact** — Name + email address of press officer
- "Visit Media Centre →" text link to full /media-centre/

**Layout:** Three-column horizontal block. Neutral grey background to distinguish from content sections. Each block: icon above, label, action link/element.

**Interaction notes:**
- Press Kit download: direct file download, no intermediate page
- Email address is `mailto:` linked
- This section must render correctly on mobile — journalists use phones on-location

---

#### Homepage Section Order Summary

| # | Section | Height | Background |
|---|---------|--------|------------|
| 1 | Hero | 100vh | Full-bleed photo |
| 2 | Stats Bar | ~100px | IDU blue |
| 3 | Latest News | ~500px | White |
| 4 | Upcoming Events | ~300px | Light grey |
| 5 | Member Parties Preview | ~300px | White |
| 6 | About IDU | ~200px | Light grey |
| 7 | Bush-Thatcher Award | ~400px | Deep blue / warm neutral |
| 8 | Sub-Organisations | ~500px | White |
| 9 | Media Centre Quick Access | ~250px | Light grey |
| — | Footer | ~300px | Dark blue |

---

### 3.2 About

**URL:** `/about/`
**Purpose:** Establish institutional legitimacy, historical depth, and governance transparency.

---

#### Section 1: Page Header

**Content:** Page title "About the IDU". Brief mission statement (2 sentences).
**Layout:** Full-width banner, IDU blue background, white text. Not full-viewport — approximately 300px height. Optional: subtle background image of founding moment (if archival photography exists).

---

#### Section 2: Mission & Vision

**Content:**
- `"Mission"` heading + 2–3 sentence institutional mission statement
- `"Vision"` heading + 1–2 sentence aspirational statement
- Core values listed: Democracy, Freedom, Rule of Law, Human Rights, Free Markets (IDU's established pillars)

**Layout:** Two-column text layout (Mission left, Vision right) above a values icon-strip. Clean, no imagery required.

---

#### Section 3: Founding History

**Content:**
- Section heading: `"Our History"`
- Founding narrative: London, 1983, Thatcher/Reagan/Kohl — told in 3–4 paragraphs
- Timeline: Key milestones from 1983 to present
  - 1983: Founded in London
  - Post-1989: Expansion after Cold War
  - Key events, membership milestones, award inaugurations
  - Present day

**Layout:** Alternating or vertical timeline component. Each milestone: year (large, accent colour), event description (paragraph). Timeline line runs vertically through milestones. On mobile: vertical stack.

**Interaction notes:** Timeline is static — no JS-heavy animation needed. CSS-only vertical line with milestone dots.

---

#### Section 4: Governance

**Content:**
- How IDU is structured: General Assembly, Executive Committee, Secretary General
- Roles and responsibilities described in plain, institutional language
- Link to Leadership page for current office-holders

**Layout:** Text block with subsections. A simple diagram/org chart (static SVG or image) would clarify structure without cluttering. Not required for launch.

---

#### Section 5: Sub-Organisations

**Content:**
- Section heading: `"The IDU Family of Organisations"`
- Same 6-card grid as homepage (Section 8), but with expanded descriptions (3–4 sentences each)
- Each card has a "Learn more" link (external site or anchor section)

**Layout:** 3×2 grid on desktop. Expanded card format vs. homepage — more text visible.

---

#### Section 6: Values

**Content:**
- IDU's core democratic values: stated clearly, without political campaigning
- Each value: heading + 2–3 sentence description

**Layout:** Full-width alternating text/accent-background rows, or a clean bulleted list with bold value names. Dignified, not flashy.

---

#### Section 7: Sub-Page Links (Navigation within About)

**Content:** Inline navigation block to sub-pages
- → Honorary Advisory Board
- → IYDU

**Layout:** Two link cards with brief description of each sub-page. Positioned at the bottom of the main About content before footer.

---

### 3.3 About → Honorary Advisory Board

**URL:** `/about/honorary-board/`
**Purpose:** Display prestigious advisory figures. Each name is a trust signal.

---

#### Section 1: Page Header

**Content:** "Honorary Advisory Board" — brief explanation of the board's role.
**Layout:** Standard page header banner (IDU blue).

---

#### Section 2: Board Members Grid

**Content per member:**
- Professional photograph (formal/official)
- Full name
- Title / former role (e.g., "Former Prime Minister of [Country]")
- Country flag icon (optional, adds international visual)
- Brief biography (2–3 sentences on hover or expanded)

**Layout:** Grid — 3 or 4 columns on desktop, 2 on tablet, 1 on mobile. Each member is a card with photo top, name and title below.

**Interaction notes:**
- Click or hover: expand to show brief bio (accordion or modal)
- Photos must be professional and recent — old or low-quality photos undermine the prestige signal
- Consistent aspect ratio (portrait, 3:4) with object-fit: cover

---

### 3.4 About → IYDU

**URL:** `/about/iydu/`
**Purpose:** Give IYDU its own identity within the IDU umbrella. Audience: young political professionals, media covering youth politics.

---

#### Section 1: Page Header

**Content:** IYDU logo + "International Young Democrat Union" — sub-headline: "The Youth Wing of the IDU"
**Layout:** Header with IYDU branding. IDU blue, possibly with IYDU's own accent if they have one.

---

#### Section 2: About IYDU

**Content:** What IYDU is, its mission, membership, relationship to IDU.
**Layout:** Text block, 2-column on desktop.

---

#### Section 3: IYDU Leadership

**Content:** IYDU President + key officers. Photo, name, role.
**Layout:** Profile cards (2–3 people). Horizontal row.

---

#### Section 4: IYDU Events/News (if applicable)

**Content:** IYDU-related news items filtered from main news feed, OR a link to iydu.org.
**Layout:** 2–3 recent news items in card format. "More from IYDU →" links to full news feed filtered by IYDU tag OR to external IYDU site.

---

### 3.5 Members

**URL:** `/members/`
**Purpose:** The definitive reference for IDU membership. Most-visited page by researchers, media, and member parties verifying their own representation.

**Design principle:** Every member party receives equal dignity. The page must be comprehensive, accurate, and fast to navigate.

---

#### Section 1: Page Header

**Content:** "Member Parties" — sub-headline: "80+ member parties across 6 continents representing millions of democratic voters worldwide"
**Layout:** Standard header banner. IDU blue. Stats optionally visible (number of members, continents covered).

---

#### Section 2: Filter Bar

**Purpose:** Enable fast navigation of 80+ parties without cognitive overload.

**Content elements:**
- Search field: "Search by party name or country..."
- Filter dropdowns:
  - **Region/Continent:** All | Africa | Americas | Asia-Pacific | Europe | Middle East & North Africa
  - **Status:** All Members | Full Members | Associate Members | Observer Members
- Results count: "Showing 82 parties" (updates dynamically)
- Clear filters link

**Layout:** Sticky filter bar that stays visible as user scrolls through results. White background, subtle bottom border to separate from directory below.

**Interaction notes:**
- Filtering: JavaScript (Isotope.js or FacetWP if using WordPress facets) — instant client-side filtering preferred for UX
- Search is client-side full-text search across party name and country fields
- Filter state persists if user returns via back button (use URL query params: `/members/?region=europe&status=full`)
- "Clear all filters" resets to full directory

---

#### Section 3: Members Directory Grid

**Content per party card:**
- Party logo (high-res, consistent white or transparent background)
- Party name (full official name)
- Country (with small flag icon)
- Region label (small tag)
- Member status badge (Full / Associate / Observer)
- Link to party's official website (external)

**Layout:** Responsive grid — 4 columns desktop, 3 tablet, 2 mobile. Cards: white background, subtle border, party logo centred at top, text below. Consistent card height.

**Interaction notes:**
- Hover: subtle card lift, cursor pointer, "Visit party website" label appears
- Click: opens party's external website in new tab
- Logos: display at consistent size (e.g., max 120×80px container) with object-fit: contain (preserve aspect ratio)
- Fallback: If no logo available, display country flag + party name in styled text card
- Logos in full colour (greyscale-on-hover is too subtle for a directory; full colour identifies parties clearly)

---

#### Section 4: Regional Groupings (Alternate View — Optional)

An alternate layout mode: "View by Region" toggle showing parties grouped under their regional sub-organisation (IYDU, CDU, DUA, etc.).

**Interaction notes:**
- Toggle between "Grid view" and "By Region" view
- By Region: collapsible sections per region with party cards inside
- Default view: Grid (shows full breadth at once)

---

### 3.6 News

**URL:** `/news/`
**Purpose:** Official record of IDU statements, resolutions, and activities. Serves media on deadline and researchers building archives.

**Design principle:** This is a record, not a blog. Dates are prominent. Categories are clear. Archive is navigable.

---

#### Section 1: Page Header

**Content:** "News & Statements"
**Layout:** Standard header. IDU blue.

---

#### Section 2: Filter Bar

**Content:**
- Filter by type (pills/tabs): `All | Statements | Resolutions | Event Reports | Awards | Press Releases`
- Year filter dropdown: current year back to earliest available
- Search field: "Search news..."
- Results count

**Layout:** Horizontal filter bar. Type pills are the primary filter (prominent, toggle-style). Year is secondary (dropdown). Search is tertiary.

**Interaction notes:**
- Default view: All types, most recent first
- Active filter pill: filled IDU blue background, white text
- URL state: `/news/?type=statement&year=2025`
- Pagination or infinite scroll: **Pagination preferred** for institutional sites (allows direct linking to specific pages of archive; better for research use)

---

#### Section 3: News Feed

**Content per item:**
- Type badge (coloured pill — each type has a distinct colour within IDU palette)
- Date (prominent, e.g., "14 January 2026")
- Headline (H2, linked)
- 2-sentence excerpt
- Optional: thumbnail image if available

**Layout:** Vertical list (not card grid) — news items read as a chronological record. Each item has a subtle bottom border separator. Left-aligned. Dates are left-aligned in a dedicated column on desktop (table-like presentation creates journalistic credibility).

**Interaction notes:**
- Hover: headline underlines, subtle row highlight
- Click: full article page
- Share buttons on individual article pages: LinkedIn, X/Twitter, "Copy link"

---

#### Section 4: Individual News Article

**Content:**
- Type badge + date
- Headline (H1)
- Author/source: "International Democracy Union" or specific author if relevant
- Body content (full text)
- Related articles (2–3 items of same type or topic)
- Share bar (LinkedIn, X, Copy link)
- "← Back to News" navigation

**Layout:** Single-column article layout, max-width ~720px for readability. Clean sans-serif body text. No sidebar needed — keep focus on content.

---

### 3.7 Events / Events Directory

**URL:** `/events/`
**Purpose:** Communicate IDU's active convening power. Past events prove consistent activity; upcoming events show continued vitality.

---

#### Section 1: Page Header

**Content:** "Events"
**Layout:** Standard header. IDU blue.

---

#### Section 2: Upcoming Events

**Content per event:**
- Date block (day large, month/year smaller) — visually prominent
- Event name (H3, linked)
- Location (city, country + flag)
- Event type (Summit / Forum / Working Group / Award Ceremony)
- Brief description (2–3 sentences)
- Optional: "Registration" or "More info" link if applicable

**Layout:** Vertical list with left-aligned date blocks. Each event separated by a horizontal rule. Clean, minimal — no full-bleed image per event (too visually heavy for a directory).

---

#### Section 3: Past Events

**Content:**
- Same format as upcoming events
- Grouped by year (year as section subheading)
- Link to Event Report (news item) where available

**Layout:** Collapsible year groups — current year open by default, past years collapsed. Each event in compact list format.

**Interaction notes:**
- Year accordions: expand/collapse on click
- "View Event Report →" link connects events to news items — important cross-linking for researchers

---

#### Individual Event Page

**Content:**
- Event header: name, date, location, type
- Full description
- Gallery (if photos from event are available) — links to photo library in Media Centre
- Event Report / Outcome document (link to news item if published)
- Previous/Next event navigation

---

### 3.8 Leadership

**URL:** `/leadership/`
**Purpose:** Authoritative identification of current IDU leadership. Supports diplomatic and media audiences.

---

#### Section 1: Page Header

**Content:** "Leadership"
**Layout:** Standard header. IDU blue.

---

#### Section 2: Secretary General

**Content:**
- Professional headshot (formal, recent)
- Full name
- Title: "Secretary General, International Democracy Union"
- Country/party affiliation
- Biography (3–4 paragraphs — substantial, authoritative)
- Contact: Secretary General's office email

**Layout:** Split layout — photo left (~40%), text right (~60%). Dignified whitespace. Photo: black and white or colour (both work; B&W can add gravitas).

---

#### Section 3: Executive Committee

**Content per member:**
- Professional headshot
- Full name
- Role/position within IDU
- Party name + country
- Brief bio (3–5 sentences)

**Layout:** Grid — 3 or 4 columns on desktop, 2 on tablet. Cards with photo, name, role. Expandable bio on click.

**Interaction notes:**
- Click on card → expands to show full bio in an inline accordion or modal
- Consistent photo treatment (same aspect ratio, similar style — if photos come from various sources, consider B&W filter for visual consistency)

---

#### Section 4: Honorary Officers (if applicable)

**Content:** Honorary President, Honorary Chair, etc. (names, former roles, brief note on honorary designation)
**Layout:** Simple text list or minimal card row. Does not need the full visual treatment of Executive Committee.

---

#### Section 5: Contact

**Content:**
- IDU Secretariat contact details: address, email
- "For media enquiries, please contact [press@idu.org]" — cross-links to Media Centre

**Layout:** Simple text block, left-aligned. Institutional address format (formal).

---

### 3.9 Media Centre

**URL:** `/media-centre/`
**Purpose:** Eliminate friction for journalists. All press resources in one professional hub. This page's quality is a direct signal of IDU's institutional seriousness.

**Design principle:** A journalist on deadline should find what they need in under 30 seconds.

---

#### Section 1: Page Header

**Content:** "Media Centre"
**Sub-heading:** "Press resources, statements, photography, and contact for media professionals"
**Layout:** Standard header. IDU blue.

---

#### Section 2: Press Contact (Prominent, Above the Fold)

**Purpose:** Journalists on deadline need contact first. This comes before everything else.

**Content:**
- Heading: "Press Enquiries"
- Press officer name and title
- Email address (mailto: linked, large font)
- Phone number (if provided)
- Note: "For urgent media enquiries: [phone]" — if 24hr contact is available

**Layout:** Full-width band, distinct background (light blue or warm grey). Left-aligned content. Email is the most visually prominent element. No form — email address directly.

---

#### Section 3: Press Kit Download

**Content:**
- Heading: "Press Kit"
- Brief description: "Everything you need for accurate IDU reporting"
- Contents list:
  - IDU logo files (PNG, SVG, all variants)
  - Boilerplate organisational description
  - Leadership headshots (high-resolution)
  - IDU factsheet (founding, membership, mission)
- Large download button: "Download Press Kit (.zip)" with file size
- Version note: "Updated [Month Year]" — proves currency

**Layout:** Prominent card or highlight block. Download button is the largest and most visually prominent action on the page. Accent colour (gold or IDU blue filled button).

**Interaction notes:**
- Direct download — `.zip` file, no registration, no email gate
- Button opens download immediately; no intermediate page
- File size displayed (so journalists know what they're downloading)

---

#### Section 4: Latest Press Releases

**Content:**
- 5 most recent press releases with date, headline, and PDF download link
- "View all press releases →" links to /news/?type=press-release

**Layout:** Simple list — date | headline | [PDF ↓] icon link. No excerpts needed for this summary view — journalists want to scan fast.

---

#### Section 5: Photo Library

**URL:** `/media-centre/photo-library/`
**Content:**
- Searchable/filterable archive of official IDU photography
- Filters: Event, Year, Person, Topic
- Each photo:
  - Thumbnail in grid
  - Caption: event name, date, names of people pictured (required for journalistic use)
  - High-res download link
  - Usage rights note (e.g., "For editorial use. Credit: IDU / [Photographer]")

**Layout:** Masonry or uniform grid of photo thumbnails. Filter bar at top. Click on thumbnail → lightbox with full caption and download link.

**Interaction notes:**
- Lightbox: keyboard navigable (left/right arrow keys), close on Escape
- Download: full-resolution file
- Caption format: "From left: [Name], [Name]. [Event Name], [City], [Date]."

---

#### Section 6: Video (if applicable)

**Content:** Embedded videos from summits, award ceremonies, speeches. YouTube or Vimeo embeds.
**Layout:** 2–3 column video grid with title and date below each. Only include if meaningful video content exists — an empty or near-empty section is worse than no section.

---

#### Section 7: IDU Facts & Figures (Journalist Quick Reference)

**Content:**
- Founded: 1983
- Founders: Margaret Thatcher (UK Conservative Party), Ronald Reagan (US Republican Party), Helmut Kohl (German CDU)
- Headquarters: [City]
- Members: 80+ parties, 6 continents
- Secretary General: [Current name]
- Notable awards: Bush-Thatcher Award for Freedom (since [year])

**Layout:** Two-column fact list. Clean, minimal. Easy to copy-paste for journalists writing about IDU for the first time.

---

### 3.10 Privacy Policy

**URL:** `/privacy-policy/`
**Purpose:** Legal compliance. GDPR-compliant given European operations and membership.

**Content:** Standard privacy policy covering:
- Data controller (IDU Secretariat details)
- Types of data collected (contact forms, analytics cookies, member login)
- Legal basis for processing
- Data retention
- User rights (access, deletion, portability)
- Cookie policy
- Contact for data enquiries

**Layout:** Long-form legal text. Clean, readable typography. Table of contents with anchor links at top. No design flourishes — clarity only.

---

## 4. User Flows

### 4.1 Flow 1: Media Journalist (Priority #1)

**Goal:** Access press kit, find a quote, verify IDU facts, and contact press officer — all in under 2 minutes.

```
Entry: Google search "IDU press kit" or "International Democracy Union statement [topic]"
  ↓
Homepage
  ↓
Sees "For the Press" section → clicks "Download Press Kit"
  [OR]
Clicks "Media Centre" in primary nav
  ↓
Media Centre → sees Press Contact block immediately
  ↓
Downloads Press Kit (one click)
  ↓
Scans Latest Press Releases → clicks relevant release
  ↓
Reads press release → uses share button or copies URL
  ↓
If needing photo: Photo Library → filters by topic → lightbox → download high-res
  ↓
Sends email to press contact if needing comment
```

**Friction points to eliminate:**
- Press contact must be visible without scrolling on Media Centre page
- Press Kit download must never require a login or form submission
- Photo captions must identify all people (journalists cannot publish unattributed photos)

---

### 4.2 Flow 2: Member Party Leadership (Priority #2)

**Goal:** Verify party representation, check upcoming events, find sister party contacts.

```
Entry: Direct URL (idu.org) or from IDU email newsletter
  ↓
Homepage — sees upcoming events, latest news
  ↓
Members page → searches for own party → verifies logo and description are correct
  ↓
Filters by own region → finds sister parties in region
  ↓
Clicks sister party → visits party's external website
  [OR]
Events page → checks upcoming events → notes dates for diary
  ↓
News page → reads latest Statement or Resolution
  ↓
Member Login → accesses member portal (if authenticated area exists)
```

**Friction points to eliminate:**
- Member party cards must load fast — if a party chairman is sharing their screen in a board meeting, a slow Members page is embarrassing
- Logo for their own party must be correct and high quality — wrong or missing logo is a relationship issue
- Member login must be clearly accessible but not prominently promoted to non-members

---

### 4.3 Flow 3: Government / Diplomatic Contact (Priority #3)

**Goal:** Understand IDU's position on a current issue, identify the right person to contact, assess institutional legitimacy.

```
Entry: IDU.org (likely direct — diplomats receive communications with idu.org)
  ↓
Homepage — assesses visual authority (hero, founding year, scale)
  ↓
Homepage news section → finds IDU's recent Statement on relevant topic
  ↓
News page → filters by "Statements" → reads full statements
  ↓
Leadership page → identifies Secretary General → finds contact
  ↓
About page → reads governance structure → understands IDU's decision-making authority
  ↓
Members page → checks which parties from their own country/region are members
```

**Friction points to eliminate:**
- Homepage must project authority within 3 seconds — the diplomatic audience makes rapid credibility assessments
- Leadership page contact details must be current and not gated
- Statements must be easy to find and well-attributed (date, context)

---

### 4.4 Flow 4: Researcher / Think Tank (Priority #4)

**Goal:** Verify membership, access historical resolutions, cite IDU accurately.

```
Entry: Google "International Democracy Union members" or "IDU resolutions"
  ↓
Members page — browses full directory, potentially downloads or screenshots for research
  ↓
Uses filters to verify regional breakdown
  ↓
News page → filters by "Resolutions" → finds relevant resolutions
  ↓
About page → reads founding history → notes founding year, founders, purpose
  ↓
Individual news/resolution pages → copies URL for citation
  [OR]
Homepage → Stats Bar → About → Timeline for chronological research
```

**Friction points to eliminate:**
- Resolutions must be individually addressable pages (unique URLs) for academic citation
- Founding date and founders must be easily findable and clearly stated (currently primary trust signal gaps)
- Member directory must show accurate status (full/associate/observer) — researchers distinguish these

---

### 4.5 Flow 5: Political Association / Observer (Priority #5)

**Goal:** Understand IDU scope, assess alignment, find contact for potential collaboration.

```
Entry: Referral from member party, or search "centre-right international organisation"
  ↓
Homepage — assesses IDU's scope and legitimacy
  ↓
About page → reads mission, governance, sub-organisations
  ↓
Members page → checks which parties from their region are members
  ↓
Leadership page → identifies appropriate contact
  ↓
Media Centre / About → finds email or contact route
```

---

## 5. Component Library

Reusable components defined here. These should be built as Gutenberg blocks (WordPress) or template parts.

---

### C01: Page Header Banner

**Usage:** All interior pages
**Structure:**
- Background: IDU blue (solid or with subtle texture)
- H1: page title, white, centered or left-aligned
- Optional: sub-headline (smaller, white, below H1)
- Height: ~280–320px
- Breadcrumb: small white text above H1 (e.g., "Home › About › Honorary Board")

---

### C02: News Card

**Usage:** Homepage news section, News page, related articles
**Structure:**
- Top: type badge (coloured pill — colour by category)
- Date: "12 February 2026" — prominent, grey
- Headline: H3, linked, IDU-blue on hover
- Excerpt: 1–2 sentences, smaller body text
- Border: subtle bottom line or card shadow
**Variants:** Full card (with image) / Compact card (text only)

---

### C03: Event List Item

**Usage:** Homepage events, Events page
**Structure:**
- Left column: date block (day large, month/year small, IDU-blue background)
- Right: event name, location, brief description, optional link
- Separator: horizontal rule between items

---

### C04: Member Party Card

**Usage:** Members page directory
**Structure:**
- Logo: centered, max 120×80px, object-fit: contain, white background
- Party name: H4
- Country + flag icon
- Region tag: small pill
- Status badge: Full / Associate / Observer (colour-coded)
- External link: on hover, "Visit party website →" appears
**Card states:** Default, hover (elevation), filtered-out (dimmed/hidden)

---

### C05: Person Profile Card

**Usage:** Leadership page, Honorary Board, IYDU Leadership
**Structure:**
- Photo: 3:4 portrait, object-fit: cover
- Name: H3
- Title/role: smaller text, italicised or muted
- Party + country: small text
- Expandable bio: accordion within card or modal on click
**Variants:** Large (Secretary General — full-width split), Standard (grid), Compact (honorary list)

---

### C06: Stats Bar

**Usage:** Homepage stats section; can be reused on About page
**Structure:**
- 4 horizontal cells, equal width
- Large numeral (bold, white), label below (smaller, white)
- Background: IDU blue
- Mobile: 2×2 grid

---

### C07: Sub-Org Card

**Usage:** Homepage sub-org grid, About page sub-org grid
**Structure:**
- Logo/badge (if sub-org logo exists) or acronym in styled badge
- Sub-org full name: H4
- Region/focus line: small text, muted
- Description: 2–4 sentences
- Link: "Learn more →" or external link icon
- Left border accent: IDU blue or sub-org colour

---

### C08: Award Feature Block

**Usage:** Homepage Bush-Thatcher Award section
**Structure:**
- Section background: deep blue or warm neutral (distinguished from surrounding sections)
- Award name: large type, gold accent colour
- Description: 2–3 sentences
- Winner feature: photo + name + year + brief context
- Past recipients: small linked list or abbreviated names
- CTA: "View past recipients →" (text link)

---

### C09: Press Kit Download Block

**Usage:** Media Centre, Homepage media quick access
**Structure:**
- Heading: "Press Kit"
- Contents list (bulleted)
- Download button: large, accent colour, download icon
- File size + version date below button

---

### C10: Filter Bar

**Usage:** Members page, News page, Photo Library
**Structure:**
- Search field (leftmost)
- Filter dropdowns or pill toggles (centre)
- Results count (right)
- Clear filters link (appears when filters are active)
- Sticky positioning on scroll
**Variants:** Pill-style (News page type filter) / Dropdown-style (Members page region filter)

---

### C11: Logo Strip

**Usage:** Homepage member parties preview
**Structure:**
- Horizontal scrollable strip of party logos
- Logos: full colour, consistent height, white/transparent background
- Optional: slow CSS scroll animation (disable via prefers-reduced-motion)
- Below strip: CTA button "View Full Directory"

---

### C12: Section Header

**Usage:** All non-hero sections across all pages
**Structure:**
- Section label: small caps or overline text, IDU blue, above main heading
- Main heading: H2
- Optional: sub-heading (H3-level, muted)
- Optional: section-level CTA (right-aligned text link on desktop)
- Consistent top/bottom padding: 64–80px section padding

---

### C13: Footer

**Usage:** All pages (universal)
**Structure:** As defined in Navigation Design 2.5. Dark IDU blue background.

---

### C14: Breadcrumb

**Usage:** All interior pages above Page Header Banner
**Structure:** "Home › Section › Sub-page" — small type, white on blue (within header), or grey on white (above header if separate)

---

### C15: Lightbox

**Usage:** Photo Library, person profile photos
**Structure:**
- Full-screen overlay (dark background)
- Image centered, responsive
- Caption below image
- Download link (high-res)
- Close button (X, top-right)
- Keyboard: Escape to close, arrows to navigate between images
**Accessibility:** Focus trap within lightbox; returns focus to trigger element on close

---

### C16: Accordion

**Usage:** Past events by year, FAQs (if any), expandable bios
**Structure:**
- Header row: clickable, title + expand/collapse icon (+ / −)
- Content: expands below header with transition
- ARIA: `aria-expanded` on trigger, `aria-hidden` on content panel
- Only one open at a time (per group) OR allow multiple — specify per usage

---

## 6. Responsive Notes

### 6.1 Breakpoints

| Label | Width | Target devices |
|---|---|---|
| Mobile | < 640px | Smartphones |
| Tablet | 640–1024px | Tablets, landscape phones |
| Desktop | 1025–1440px | Laptops, monitors |
| Wide | > 1440px | Large monitors |

### 6.2 Homepage — Mobile Priorities

- **Hero:** Full-viewport height maintained on mobile. Headline at 2rem (not 4rem desktop). Sub-headline may truncate or be removed if space tight. Hero image: focus area centered (avoid edges where key subjects appear).
- **Stats Bar:** 2×2 grid (not horizontal strip). Numerals remain large and bold.
- **News cards:** Single column. Full card width. Date and type badge must remain visible.
- **Events:** Single column list. Date block moves above event name (not left-column).
- **Member logos strip:** Touch-scrollable horizontal strip. Disable CSS auto-scroll on mobile (touch scroll is sufficient). 
- **Sub-org grid:** 1-column stack. Cards at full width.
- **Media quick access:** Stack vertically. Press Kit download button full-width (large tap target).

### 6.3 Members Page — Mobile

- Filter bar: collapses to "Filter" button → opens a full-screen filter drawer (modal) on mobile. Prevents filter bar from occupying too much screen real estate.
- Directory: 2-column grid minimum (1-column feels too spacious and requires excessive scrolling through 80+ entries).
- Party cards: logo remains visible; name below; country and region below that. Status badge maintained.

### 6.4 Navigation — Mobile

- Hamburger: positioned top-right, 44×44px minimum tap area
- Logo: top-left, links to homepage
- Full-screen overlay nav: dark background, white text, items spaced for touch
- No hover states on mobile — ensure all interactions are tap-based

### 6.5 Media Centre — Mobile

- Press Contact block: appears first (above Press Kit on mobile — journalists on mobile phones need contact info fastest)
- Download button: full-width, large tap target
- Photo Library: 2-column grid minimum; lightbox works on touch (swipe to navigate)

### 6.6 Leadership Page — Mobile

- Secretary General: photo above text (stacked), not side-by-side
- Executive Committee grid: 2 columns on mobile

### 6.7 Typography Scale (Mobile vs Desktop)

| Element | Desktop | Mobile |
|---|---|---|
| Hero headline (H1) | 3.5–4rem | 2–2.5rem |
| Page title (H1) | 2.5–3rem | 1.75–2rem |
| Section heading (H2) | 2–2.5rem | 1.5–1.75rem |
| Card heading (H3) | 1.25–1.5rem | 1.125–1.25rem |
| Body text | 1rem (16px) | 1rem (16px) — do not reduce |
| Small/label | 0.875rem | 0.875rem |

---

## 7. Accessibility Notes

### 7.1 Compliance Target

**WCAG 2.1 Level AA** — minimum requirement.

Rationale: IDU's audiences include government bodies, diplomatic contacts, and media professionals in EU member states and other jurisdictions with public sector accessibility mandates. A site that fails accessibility checks reflects poorly on an institution that champions democratic values.

---

### 7.2 Colour Contrast

- All body text on white backgrounds: minimum 4.5:1 contrast ratio
- White text on IDU blue: verify the specific blue value achieves minimum 4.5:1 (dark blues typically pass; mid-range blues may not)
- Type badges (coloured pills): ensure text colour on badge background meets 4.5:1
- Gold/warm accent text: if used on white, verify — gold often fails contrast; consider using gold only as decorative (border, icon), not as text colour
- Focus indicator: visible, high-contrast outline on all focusable elements (do not remove browser default focus styles without replacing with visible alternative)

---

### 7.3 Keyboard Navigation

- All interactive elements reachable and operable by keyboard: links, buttons, filters, dropdowns, accordions, lightbox
- Tab order: logical, follows visual flow (top-to-bottom, left-to-right)
- Skip link: "Skip to main content" link as first focusable element on page (visible on focus, can be visually hidden until focused)
- Sticky nav: ensure sticky navigation does not trap keyboard focus

---

### 7.4 Screen Reader Compatibility

- Semantic HTML: `<nav>`, `<main>`, `<article>`, `<section>`, `<header>`, `<footer>`, `<aside>` used appropriately
- Headings: logical hierarchy — one H1 per page; H2 for major sections; H3 for subsections/cards
- Images: meaningful alt text for all images; decorative images use `alt=""`
- Icons: SVG icons have `aria-label` or `aria-hidden="true"` with adjacent visible text
- Form labels: all filter inputs and search fields have visible labels or `aria-label`
- News type badges: include in accessible name (e.g., screen reader reads "Statement — [headline]" not just "[headline]")

---

### 7.5 Lightbox Accessibility

- Focus trap: keyboard focus confined within open lightbox
- Close on Escape key
- Return focus to triggering element when lightbox closes
- ARIA: `role="dialog"`, `aria-modal="true"`, `aria-label="Photo: [caption]"`

---

### 7.6 Filter Bars

- Filter controls: visible labels, not just placeholder text
- Results: announce result count change to screen readers using `aria-live="polite"` region
- "Clear filters" button: accessible label "Clear all filters"

---

### 7.7 Motion & Animation

- CSS scroll animations (logo strip, any transitions): respect `prefers-reduced-motion` media query — disable or reduce motion for users who have opted out
- No auto-playing video or animation that cannot be paused

---

### 7.8 Language and Internationalisation

- `lang="en"` attribute on `<html>` element
- If IDU publishes content in multiple languages in future: `lang` attributes on individual content blocks; `hreflang` meta tags for alternate language pages
- Avoid language-specific assumptions in design (e.g., English party names may be longer/shorter when translated)

---

### 7.9 Forms (Contact, Member Login if applicable)

- All form fields: visible label (not placeholder-only)
- Error messages: associated with field via `aria-describedby`; colour alone not sufficient to indicate error (use icon + colour + text)
- Required fields: marked visually and with `aria-required="true"`
- Success/error states: announced to screen readers

---

## Appendix A: Page Template Map

| Page | Template | Sidebar? | Filter? | Custom CPT? |
|---|---|---|---|---|
| Homepage | Custom homepage template | No | No | No |
| About | Standard page | No | No | No |
| Honorary Board | Standard page | No | No | No |
| IYDU | Standard page | No | No | No |
| Members | Archive template (CPT) | No | Yes | `idu_member` |
| News | Archive template (Posts) | No | Yes | Custom taxonomy |
| News article | Single post | No | No | No |
| Events | Archive template (CPT) | No | No | `idu_event` |
| Event single | Single CPT | No | No | No |
| Leadership | Standard page | No | No | `idu_person` |
| Media Centre | Standard page | No | No | No |
| Photo Library | Custom gallery template | No | Yes | Media library |
| Privacy Policy | Standard page | No | No | No |

---

## Appendix B: Content Dependency Map

Items that must be ready before a page can launch:

| Page | Content Dependencies |
|---|---|
| Homepage | Hero photo (hi-res), 3+ news items with dates, 2+ events, member logos (min 20), Bush-Thatcher Award content, press kit file |
| Members | All member logos, accurate party names, country assignments, status classification for 80+ parties |
| Leadership | Professional headshots (recent) for all Executive Committee members, current Secretary General bio |
| Media Centre | Press kit (complete zip), press officer contact details, min 5 press releases, photo library (min 20 photos with captions) |
| Honorary Board | Professional photos and bios for all board members |
| About | Founding history text, governance description, sub-org descriptions |

---

*Document prepared for handoff to Copywriter and Developer.*
*Next steps: copywriter produces page-by-page copy; developer builds WordPress implementation.*

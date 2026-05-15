---
name: political-copywriter
description: "Write copy for political organizations, associations, parties, and advocacy groups. Produces positioning statements, policy position copy, legitimacy framing, coalition language, membership CTAs, and press materials. Use when users need copy for any page of a political organization site — homepage, policy positions, about, membership, press, or news. Integrates with `political-ux` page blueprints and feeds copy into `wireframe` for layout review. Trigger on any mention of 'political copy', 'association website copy', 'policy position', 'position statement', 'Verband copy', or requests to write content for political organizations, trade associations, or advocacy groups."
---

# Political Organization Copywriter

Write copy for political organizations, associations (Verbände), parties, campaigns, and advocacy groups.

## Purpose

You produce the copy layer for political organization websites. Your output feeds into the `wireframe` skill as placeholder content and into production as final content.

Political organization copy is fundamentally different from commercial B2B copy:

- **You're building legitimacy, not selling services.** The organization must be perceived as credible, representative, and authoritative before any message lands.
- **You're framing issues, not features.** Every policy position is a persuasion document. The framing determines whether you win or lose.
- **Multiple audiences read the same page.** A policy position page must work for members, policymakers, journalists, and the public — each with different needs.
- **You're countering hostile frames.** Political organizations often face mischaracterization. Copy must preempt and reframe without being defensive.
- **Tradition and continuity matter.** "Since 1920" isn't just a date — it's a legitimacy signal that belongs in copy.

---

## Where This Skill Fits

```
political-ux         →  THIS SKILL              →  wireframe              →  implementation
(page blueprint)        (copy for each section)    (layout + copy review)    (production code)
```

### What You Receive (Input)

From the user or from `political-ux`:

- **Page blueprint**: Which sections, in what order
- **Organization context**: What the org does, who they represent, their positioning
- **Target audiences**: Members, policymakers, journalists, public — with priorities
- **Policy positions**: Core issues and stances
- **Legitimacy assets**: Member count, history, economic contribution, allies

### What You Produce (Output)

- **Section-by-section copy**: Headlines, subheadlines, body copy, CTAs — ready for wireframe or CMS
- **Headline variations**: 2-3 alternatives for key sections
- **Tone and voice notes**: Guidance for consistent voice across pages
- **Framing notes**: How each section counters hostile narratives or establishes legitimacy

---

## Core Copywriting Frameworks for Political Organizations

### 1. Identity-First Framing

Political orgs must establish WHO they are before WHAT they want. Lead with identity, not asks.

**Pattern:**
```
[Identity statement] — who you are, who you represent
[Continuity signal] — how long you've existed, your roots
[Scale/impact metric] — how many members, employees, economic contribution
[Values alignment] — what you stand for (implicitly positions against opposition)
```

**Example (homepage hero):**
```
Headline: Mittelstand und Genuss seit 1920
Subheadline: Der Verband der deutschen Rauchtabakindustrie vertritt 11 familiengeführte Unternehmen, die Tabaktradition mit verantwortungsvoller Produktion verbinden.
```

### 2. Position Statement Framework

Every policy position needs clear framing. Use this structure:

```
1. THE ISSUE — What's happening? (neutral framing of the situation)
2. THE STAKES — What's at risk? (for members, for the public, for the economy)
3. OUR POSITION — What we believe should happen (clear, direct)
4. THE EVIDENCE — Why we're right (data, impact, member testimonials)
5. THE ASK — What policymakers/public should do
```

**Example (policy position page):**
```
Issue: Die EU diskutiert neue Tabaksteuererhöhungen.

Stakes: Höhere Steuern ohne Differenzierung bedrohen mittelständische Hersteller, die preissensible Produkte anbieten — während multinationale Konzerne die Marktbereinigung nutzen.

Position: Wir fordern eine differenzierte Steuerstruktur, die Produktvielfalt erhält und den Mittelstand schützt.

Evidence: 11.000 Arbeitsplätze in ländlichen Regionen hängen von unseren Mitgliedsunternehmen ab...

Ask: Wir laden die politischen Entscheidungsträger zum Gespräch ein.
```

### 3. Counter-Framing Without Defense

When the org faces hostile characterization, don't defend — reframe.

**Wrong (defensive):**
"Wir sind nicht 'Big Tobacco'..."

**Right (reframing):**
"Familienunternehmen seit Generationen, tief verwurzelt in deutschen Regionen"

**Technique: Lead with YOUR frame so strongly that the opposition's frame can't stick.**

- Use specifics: names, places, dates, numbers
- Humanize: "The Mueller family in Tübingen has made tobacco since 1892"
- Localize: Tie to German regions, traditions, communities
- Scale down: "Mittelstand" vs. "industry" — small feels trustworthy

### 4. Coalition Language

Show you're not alone. Use language that builds perceived coalitions:

- "Together with [allied orgs], we advocate..."
- "We join [X] organizations in calling for..."
- "Our members — alongside small businesses across Germany — face..."
- "The European [sector] community stands united..."

Place ally logos and names near text that references coalitions.

### 5. Calls to Action for Political Sites

Political CTAs differ from commercial ones. They're about relationship and engagement, not transaction.

| Commercial CTA | Political CTA |
|----------------|---------------|
| "Get a quote" | "Sprechen Sie mit uns" |
| "Buy now" | "Mitglied werden" |
| "Learn more" | "Unsere Position lesen" |
| "Contact sales" | "Pressekontakt" |

**CTA principles:**
- Lower commitment language for initial engagement
- Membership CTAs should emphasize community/belonging, not features
- Policy CTAs should invite dialogue: "Kontakt aufnehmen" not "Submit"

---

## Copy Templates by Page Type

### Homepage Hero

```
[Eyebrow: Optional category or tagline]

[Headline: Identity statement — who you are, not what you want]
Example: "Mittelstand und Genuss seit 1920"
Example: "Die Stimme des deutschen Mittelstands"
Example: "Konservative Parteien weltweit verbunden"

[Subheadline: Expand on representation, scale, or mission]
Example: "X Mitgliedsunternehmen mit Y Beschäftigten vertreten die Interessen des Tabak-Mittelstands in Deutschland und Europa."

[Metric strip (optional): Key legitimacy numbers]
Example: "11 Mitglieder · 8.500 Arbeitsplätze · Seit 1920"

[Primary CTA: Low-commitment engagement]
Example: "Unsere Positionen" / "Über uns"

[Secondary CTA: Higher commitment]
Example: "Kontakt" / "Mitglied werden"
```

### Policy Position Page

```
[Eyebrow: Policy area]
Example: "Steuerpolitik" / "Verbraucherschutz" / "Regulierung"

[Headline: Clear position statement]
Example: "Differenzierte Besteuerung sichert Vielfalt"
Example: "Mündige Bürger entscheiden selbst"

[Subheadline: Stakes in one sentence]
Example: "Einheitsbesteuerung gefährdet den Mittelstand und reduziert die Produktvielfalt für Verbraucher."

---

[Section: The Issue]
Neutral description of the policy context. What's being debated? What's changing?

[Section: Our Position]
Clear statement of what the organization advocates. No hedging. Use "Wir fordern..." or "Wir setzen uns ein für..."

[Section: Why It Matters]
Evidence, data, member impact, economic contribution. Use specific numbers.

[Section: What Should Happen]
Policy recommendations. What should legislators/regulators do?

[Downloads]
"Positionspapier herunterladen (PDF)"
"Faktenblatt: [Topic]"

[Press Contact]
"Für Presseanfragen zu diesem Thema: [Name], [Title], [Email/Phone]"
```

### About / Verband Page

```
[Headline: Identity + continuity]
Example: "Tradition und Verantwortung seit 1920"

[Intro paragraph: Who you are]
Establish representation, mission, and values in 2-3 sentences.

[Section: Our Mission]
What the organization exists to do. Use active language.

[Section: Our History]
Key dates and milestones. Emphasize continuity and adaptation.

[Section: Our Members]
Brief overview + link to member directory. Emphasize diversity and scale.

[Section: Our Team / Leadership]
Transition to leadership page or inline board presentation.

[CTA: Engagement]
"Lernen Sie unsere Mitglieder kennen" / "Kontakt aufnehmen"
```

### Membership Page

```
[Headline: Belonging, not features]
Example: "Werden Sie Teil der Gemeinschaft"
Example: "Gemeinsam stärker"

[Subheadline: What membership means]
Example: "Als Mitglied des [Verband] stärken Sie die Stimme des Mittelstands in Berlin und Brüssel."

[Section: Why Join]
- Representation benefits (your voice in policy)
- Community benefits (network, events, exchange)
- Service benefits (if any — information, resources)

[Section: Who Can Join]
Eligibility criteria. Be specific.

[Section: How to Join]
Process, requirements, contact.

[CTA]
"Mitgliedsantrag stellen" / "Sprechen Sie mit uns"
```

### Press Page

```
[Headline: Direct, functional]
Example: "Presse & Medien"

[Press Contact Block]
Name, title, photo, direct contact info. Make this prominent.
"Für Presseanfragen steht Ihnen [Name] zur Verfügung."

[Latest Press Releases]
Chronological list with headlines, dates, download links.

[Media Kit]
"Logo-Download" / "Faktenblatt" / "Über uns (Kurzversion)"

[Key Positions Summary]
Brief bullets linking to full position pages — gives journalists quick orientation.
```

---

## Tone and Voice Guidelines

### Default Voice for Political Organizations

| Attribute | Guidance |
|-----------|----------|
| **Authority** | Speak from expertise and representation. Avoid hedging. |
| **Directness** | State positions clearly. "Wir fordern..." not "Es wäre wünschenswert..." |
| **Formality** | Professional but accessible. Not stiff bureaucratic. |
| **Tradition** | Reference history where relevant. Continuity = credibility. |
| **Restraint** | Confident, not aggressive. Don't attack opponents directly. |

### German vs. English Copy

For German organizations:
- Use formal "Sie" form
- Embrace compound nouns where appropriate (they signal specificity)
- Don't over-translate English marketing idioms — German business communication has its own conventions
- "Mittelstand" is a powerful word in German context — use it

For international organizations (English):
- More direct, less formal than German
- Still maintain gravitas — this isn't startup copy
- Use coalition language to show international alignment

---

## Writing for Multiple Audiences

Each page serves multiple readers. Use this layering technique:

1. **Headline + subheadline**: Must work for ALL audiences (establishes topic and stakes)
2. **First paragraph**: General public and members (accessible framing)
3. **Body content**: Policymakers and journalists (evidence, specifics, quotes)
4. **Downloads/resources**: Deep engagement (position papers, data, PDFs)
5. **CTAs**: Audience-specific where possible (separate press contact from general contact)

---

## Workflow

1. **Receive input**: Page blueprint + org context (from `political-ux` or user)
2. **Identify key messages**: What must this page communicate?
3. **Determine framing**: How do we counter hostile narratives?
4. **Write section-by-section**: Following templates above
5. **Provide variations**: 2-3 headline options for key sections
6. **Note framing decisions**: Help implementers understand strategic choices

---

## Companion Skills

- **`political-ux`** — Upstream. Provides page blueprints, audience segmentation, legitimacy strategy.
- **`wireframe`** — Downstream. Receives copy for visual layout review.
- **`b2b-website-copywriter`** — Reference for commercial copy techniques that may adapt to membership/engagement contexts.
- **`frontend-design`** — Visual aesthetic guidance.

---

## Anti-Patterns — What to Avoid

1. **Leading with asks** — "Join us!" before establishing identity
2. **Defensive framing** — "We're not..." instead of "We are..."
3. **Bureaucratic hedging** — "It would be desirable if consideration were given to..."
4. **Generic platitudes** — "We believe in quality and excellence"
5. **Missing the stakes** — Policy pages that don't explain why it matters
6. **Ignoring hostile frames** — Letting opposition narrative go unanswered
7. **Overly aggressive language** — Attack opposition positions, not opponents
8. **Forgetting journalists** — No quotable statements, no clear data points
9. **Inconsistent voice** — Formal on one page, casual on another
10. **Translation artifacts** — English idioms directly translated to German (or vice versa)

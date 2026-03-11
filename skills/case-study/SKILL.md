---
name: case-study
description: Generate polished case studies and portfolio items for Autonomous Tech. Produces two outputs simultaneously — a standalone HTML page (for sales/email) and a structured JSON file (for Wagtail CMS import). Use when asked to "create a case study", "write up a project", "document a client win", "add to portfolio", or "create a portfolio item". Walks the creator through a step-by-step interview before generating any output. Trigger on any mention of "case study", "portfolio", "client story", "project write-up", or "showcase".
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Case Study & Portfolio Generator

Generate dual-output case studies for Autonomous Tech: a standalone HTML page for sales use and structured JSON for Wagtail CMS import.

## Purpose

You produce case studies that do two jobs simultaneously:
- **Sales tool**: A self-contained, beautifully designed HTML page sent to warm prospects during the sales process
- **Website content**: Structured JSON that maps directly to Wagtail StreamField blocks for frictionless CMS import

Case studies are Autonomous Tech's most powerful sales asset. They prove capability, reduce perceived risk, and give prospects language to sell the engagement internally. Every case study must balance specificity (to be credible) with narrative (to be memorable).

## Framework: PSR + JTBD Hybrid

All case studies follow this structure:

1. **Client Context** — Who they are, what they do, what stage they were at
2. **The Job To Be Done** — What they were trying to achieve (in their language, not ours)
3. **Why Existing Approaches Were Not Working** — The gap that created the opportunity
4. **What We Built** — The solution, with specifics on scope and approach
5. **How We Built It** — Tech stack, methodology, timeline (closes technical buyers)
6. **The Outcome** — Results, metrics where available, qualitative wins if not
7. **What's Next** — Signals ongoing relationship, not a one-off project

---

## Step 1: Interview the Creator (ALWAYS DO THIS FIRST)

**Never skip the interview phase.** Before writing a single word, walk the creator through these questions one group at a time. Wait for answers before proceeding to the next group. Present questions conversationally. Acknowledge answers before moving on.

---

### Group 1: Project Basics

```
Let's build your case study. A few quick questions first — the more detail you give, the stronger the output.

1. What's the client name? (or a pseudonym if confidential)
2. What industry are they in?
3. What's the one-line description of this project? (e.g. "Custom inventory management system for a heavy equipment dealer")
4. Roughly when did this project happen and how long did it take?
```

### Group 2: The Problem

```
Now tell me about the problem side:

5. What was the client trying to achieve? What was the job they hired us for?
6. What was broken, slow, or missing before we got involved?
7. Had they tried to solve it before? What failed or fell short?
```

### Group 3: The Solution

```
Now the solution:

8. What did we actually build or deliver? (be specific — features, integrations, modules)
9. What's the tech stack? (frameworks, languages, platforms, APIs)
10. Was there anything technically interesting or novel about how we solved it?
11. How did we work with the client? (sprints, dedicated team, embedded, remote?)
```

### Group 4: The Outcome

```
The results section is the most important part:

12. What changed for the client after the project?
13. Do you have any metrics? (time saved, revenue impact, conversion lift, users onboarded — anything quantifiable)
14. What did the client say about the experience? (even informal Slack quotes work)
15. Is there ongoing work or a follow-on engagement?
```

### Group 5: Permissions and Presentation

```
Last few:

16. Can we use the client's real name and logo, or should this be anonymized?
17. Can you share the client's logo file? (SVG or PNG preferred — it appears in the hero lockup alongside the Autonomous logo)
18. Do you have any screenshots, mockups, or images to include? (If yes, describe them and I'll generate contextual illustrations using Imagen 3)
19. What's the primary audience for this case study? (e.g. "other fintech startups", "NGOs", "equipment dealers", "enterprise IT buyers")
20. Any specific competitor or alternative we implicitly position against?
```

---

### Writing Rules (Apply to All Copy)

- **No em-dashes, ever.** Restructure sentences. Use colons, commas, or a new sentence instead.
- **No placeholder fluff.** Every sentence earns its place.
- **Client as hero.** Autonomous is the guide, not the protagonist.
- **Specificity over vagueness.** "34% of closed deals" beats "improved attribution significantly".
- **No superlatives.** Show results, do not claim greatness.

### Handling Incomplete Answers

If the creator cannot answer certain questions (especially metrics), do not block:
- Missing metrics: write outcome copy in qualitative terms and mark with `[ADD METRIC IF AVAILABLE]`
- Missing client name: use a plausible industry descriptor ("A mid-market fintech startup in Toronto")
- Missing testimonial: write a realistic placeholder marked `[REPLACE WITH REAL QUOTE]`

---

## Step 2: Generate Images with Imagen 3

After the interview, generate 3 contextual images using the Vertex AI Imagen 3 API (`imagen-3.0-generate-002`). These should visually represent the project — not stock photo aesthetics. Think interface mockups, abstract system diagrams, industry-contextual illustrations.

### Image Style by Project Type

| Project Type | Visual Direction |
|---|---|
| Custom software / web apps | Clean UI mockup aesthetic, warm parchment and midnight tones |
| Marketing websites | Bold editorial typography, above-fold hero aesthetic |
| AI agents / automation | Abstract neural flow diagram, data pipeline visualization |
| Martech / integrations | Connected node diagrams, pipeline visualization |
| Fintech | Minimal financial UI, charts, trust aesthetic |
| Enterprise IT | Architecture diagrams, server/cloud visual metaphors |
| Mobile apps | Device mockup, app UI screenshot style |
| Sports analytics | Data visualization, dashboard, real-time stats aesthetic |

### Imagen API Call

```python
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

vertexai.init(project=PROJECT_ID, location="us-central1")
model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")

images = model.generate_images(
    prompt=prompt,
    number_of_images=1,
    aspect_ratio="16:9",
    safety_filter_level="block_some",
    person_generation="dont_allow",
)
images[0].save(location=output_path, include_generation_parameters=False)
```

### Image Prompts by Section

**Hero** (`images/hero.png`) — full-width banner behind the hero lockup
Prompt formula: `"[Project type] digital interface, [industry aesthetic], warm parchment and deep midnight tones, editorial warmth style, professional, no people, no text, photorealistic render, 16:9"`

**Solution** (`images/solution.png`) — mid-page illustration after challenge copy
Prompt formula: `"[Technology/solution visual metaphor], [specific system or process], warm editorial aesthetic, no people, no text, 16:9"`

**Outcome** (`images/outcome.png`) — used behind or alongside the outcome stats
Prompt formula: `"Abstract data visualization showing growth or transformation, [industry context], minimal, warm editorial aesthetic, no people, no text, 16:9"`

If a client logo is provided, place it at `images/client-logo.svg` (or `.png`) and reference it in the hero lockup instead of the letter placeholder.

---

## Step 3: Generate Dual Output

### Output A: Standalone HTML (`index.html`)

Single self-contained file. All CSS in a `<style>` block. No external dependencies except Google Fonts.

#### Design System: Editorial Warmth v2

**Fonts** — load via Google Fonts:
```html
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

**CSS Custom Properties** — use these exact tokens, no deviations:
```css
:root {
  /* Editorial Warmth v2 — exact tokens */
  --parchment:        #F5EFE0;   /* page background */
  --parchment-light:  #FAF7F0;   /* cards, sidebar */
  --parchment-dark:   #EDE5D3;   /* borders */
  --midnight:         #0D0D1F;   /* dark sections, hero bg */
  --vermillion:       #E8513D;   /* primary accent, CTAs, labels */
  --vermillion-dark:  #C43C2A;   /* hover state */
  --indigo:           #1E3A8A;   /* secondary accent */
  --sage:             #7CA982;   /* positive/pass states */
  --gold:             #D4A853;   /* highlights, data callouts */
  --ink:              #1A1A2E;   /* headings */
  --prose:            #4A4A60;   /* body text */
  --caption:          #7A7A90;   /* muted/secondary text */
  --ocean:            #0EA5E9;   /* info, links */
  --white:            #FFFFFF;
  --border:           #EDE5D3;   /* parchment-dark as border */
  --border-dark:      rgba(255,255,255,0.08);  /* borders on midnight bg */
  --gold-glow:        rgba(212,168,83,0.12);
  --vermillion-glow:  rgba(232,81,61,0.10);
}
```

**Typography rules** — follow exactly:
```css
/* Hero display — Fraunces opsz 144, weight 400, -0.04em, lh 0.95 */
.hero-title {
  font-family: 'Fraunces', serif;
  font-variation-settings: 'opsz' 144;
  font-weight: 400;
  letter-spacing: -0.04em;
  line-height: 0.95;
}

/* Section H2 — Fraunces opsz 72, weight 400, -0.03em */
.section-title {
  font-family: 'Fraunces', serif;
  font-variation-settings: 'opsz' 72;
  font-weight: 400;
  letter-spacing: -0.03em;
}

/* Body — DM Sans 400, 18px, 1.7 line-height, var(--prose) */
body {
  font-family: 'DM Sans', system-ui, sans-serif;
  font-size: 18px;
  line-height: 1.7;
  color: var(--prose);
}

/* Eyebrow labels — JetBrains Mono 400, 12px, uppercase, tracking-wider, vermillion */
.section-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--vermillion);
}

/* Card titles, sidebar labels — JetBrains Mono */
.sidebar-card-title, .detail-key {
  font-family: 'JetBrains Mono', monospace;
  color: var(--caption);
}
```

**Squiggle underline** — apply to key words in hero title and one section title per brand guide:
```css
.squiggle {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='6'%3E%3Cpath d='M0 3 Q5 0 10 3 Q15 6 20 3' stroke='%23E8513D' stroke-width='1.5' fill='none'/%3E%3C/svg%3E");
  background-repeat: repeat-x;
  background-position: bottom;
  background-size: 20px 6px;
  padding-bottom: 6px;
}

.squiggle-gold {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='6'%3E%3Cpath d='M0 3 Q5 0 10 3 Q15 6 20 3' stroke='%23D4A853' stroke-width='1.5' fill='none'/%3E%3C/svg%3E");
  background-repeat: repeat-x;
  background-position: bottom;
  background-size: 20px 6px;
  padding-bottom: 6px;
}
```

#### HTML Page Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Client] x Autonomous — [Short project title]</title>
  <meta name="description" content="[SEO meta — under 160 chars]">
  [Google Fonts link]
  <style>[All CSS using tokens above]</style>
</head>
<body>

  <!-- NAV -->
  <nav>
    <a href="https://autonomoustech.ca" class="nav-logo">Autonomous</a>
    <div class="nav-right">
      <span class="nav-tag">Case Study</span>
      <a href="https://autonomoustech.ca/contact" class="btn-primary">Work with us</a>
    </div>
  </nav>

  <!-- HERO (midnight background) -->
  <section class="hero">
    <!-- Breadcrumb -->
    <div class="hero-breadcrumb">
      <a href="https://autonomoustech.ca/work">Work</a>
      <span>/</span>
      <span>[Client Name]</span>
    </div>

    <!-- Client x Autonomous lockup -->
    <div class="hero-lockup">
      <!-- If logo provided: <img src="images/client-logo.svg" class="client-logo" alt="[Client] logo"> -->
      <!-- If no logo: letter placeholder box -->
      <div class="client-logo-box">[First letter of client name]</div>
      <span class="hero-x">x</span>
      <div class="autonomous-logo-box">Auto</div>
      <div>
        <span class="hero-client-name">[Client Name]</span>
        <span class="hero-client-meta">[Industry] · [Region]</span>
      </div>
    </div>

    <!-- Headline — short, punchy, 3 lines max, outcome-first -->
    <h1 class="hero-title">
      [Line 1].<br>
      [Key word with <span class="squiggle-gold">squiggle accent</span>].<br>
      [Line 3].
    </h1>

    <!-- Tags -->
    <div class="hero-tags">
      <span class="hero-tag">[Service type]</span>
      <span class="hero-tag">[Key technology]</span>
      <span class="hero-tag">[Timeline]</span>
    </div>
  </section>

  <!-- METRICS STRIP (vermillion background) -->
  <section class="metrics">
    <div class="metrics-grid">
      <!-- 3 to 4 metrics. Use qualitative if no hard numbers. -->
      <div class="metric">
        <span class="metric-value">[Number or timeframe]</span>
        <span class="metric-label">[What it means]</span>
      </div>
    </div>
  </section>

  <!-- BODY: sidebar + article grid -->
  <div class="body-wrap">

    <article class="article">

      <!-- CHALLENGE SECTION -->
      <div class="section-block">
        <span class="section-label">The Challenge</span>
        <h2 class="section-title">[What the client needed to do — outcome framing]</h2>
        <p>[Challenge narrative — 2 to 3 paragraphs. Lead with JTBD. Use before-state language. End with why existing approaches were not enough.]</p>

        <!-- 4 pain point callout cards (2x2 grid) -->
        <!-- Each card: SVG icon + h4 + one sentence -->
        <div class="callout-grid">
          <div class="callout-card">
            [SVG icon — parchment-light background, vermillion strokes]
            <h4>[Pain point name]</h4>
            <p>[One sentence description]</p>
          </div>
          <!-- repeat x4 -->
        </div>
      </div>

      <!-- BEFORE / AFTER SVG DIAGRAM -->
      <!-- Use inline SVG — no image file needed. Show the before state (disconnected, broken, red) -->
      <!-- vs the after state (connected, flowing, sage/gold) side by side. -->
      <!-- Label sections BEFORE and AFTER in JetBrains Mono. -->
      <!-- Use parchment-light background, midnight boxes, vermillion for broken connections, sage for healthy ones. -->
      <div class="section-block">
        <span class="section-label">Before vs After</span>
        <h2 class="section-title">[What changed structurally]</h2>
        <figure class="ba-illustration">
          <svg viewBox="0 0 680 320" ...>[Before/after architecture diagram]</svg>
          <figcaption>// [one line caption describing the transformation]</figcaption>
        </figure>
      </div>

      <hr class="divider">

      <!-- SOLUTION SECTION -->
      <div class="section-block">
        <span class="section-label">The Solution</span>
        <h2 class="section-title">[What we built — specifics]</h2>
        <p>[Solution narrative — 2 paragraphs. What was built, why those choices, how we worked.]</p>

        <!-- Numbered deliverables list -->
        <ul class="deliverables">
          <li class="deliverable">
            <span class="deliverable-num">01</span>
            <div>
              <strong>[Deliverable name]</strong>
              <p>[One to two sentences on what it does and why it matters]</p>
            </div>
          </li>
          <!-- 4 to 6 deliverables -->
        </ul>
      </div>

      <hr class="divider">

      <!-- OUTCOME SECTION -->
      <div class="section-block">
        <span class="section-label">The Outcome</span>
        <h2 class="section-title">[What changed — use <span class="squiggle">squiggle on key phrase</span>]</h2>
        <p>[Outcome narrative — 1 to 2 paragraphs. Lead with the most impressive result. Close with the ongoing relationship if applicable.]</p>

        <!-- 2x2 outcome stats grid (midnight background, gold values) -->
        <div class="outcome-visual">
          <div class="outcome-stat">
            <span class="outcome-stat-value">[Number]</span>
            <span class="outcome-stat-label">[What it measures]</span>
            <span class="outcome-stat-sub">[Context]</span>
          </div>
          <!-- repeat x4 -->
        </div>

        <!-- 3 insight cards (parchment-light, colored dot, bold insight) -->
        <div class="insight-cards">
          <div class="insight-card">
            <span class="insight-dot gold"></span>
            <p><strong>[Key finding].</strong> [One to two sentences expanding on it.]</p>
          </div>
          <!-- dot colors: gold, red (vermillion), sage -->
        </div>
      </div>

      <!-- TESTIMONIAL -->
      <!-- Only include if a real quote exists. Never fabricate without [REPLACE] flag. -->
      <blockquote class="testimonial">
        <p class="testimonial-quote">[Client quote — specific, outcome-focused, 1 to 3 sentences. No em-dashes.]</p>
        <div class="testimonial-footer">
          <div class="author-avatar">[Initial]</div>
          <div>
            <span class="author-name">[Name]</span>
            <span class="author-title">[Role], [Company]</span>
          </div>
        </div>
      </blockquote>

    </article>

    <!-- SIDEBAR (sticky on desktop) -->
    <aside class="sidebar">

      <!-- Project details card -->
      <div class="sidebar-card">
        <div class="sidebar-card-title">Project Details</div>
        <div class="detail-list">
          <div class="detail-row">
            <span class="detail-key">Client</span>
            <span class="detail-val">[Client Name]</span>
          </div>
          <div class="detail-row">
            <span class="detail-key">Industry</span>
            <span class="detail-val">[Industry]</span>
          </div>
          <div class="detail-row">
            <span class="detail-key">Timeline</span>
            <span class="detail-val">[Duration]</span>
          </div>
          <div class="detail-row">
            <span class="detail-key">Team</span>
            <span class="detail-val">[e.g. 2 eng + PM]</span>
          </div>
          <div class="detail-row">
            <span class="detail-key">Type</span>
            <span class="detail-val">[Fixed scope / Retainer]</span>
          </div>
          <div class="detail-row">
            <span class="detail-key">Status</span>
            <span class="detail-val [green or default]">[Active / Ongoing retainer / Complete]</span>
          </div>
        </div>
      </div>

      <!-- Tech stack card -->
      <div class="sidebar-card">
        <div class="sidebar-card-title">Tech Stack</div>
        <div class="tech-grid">
          <span class="tech-pill">[Technology]</span>
          <!-- one per technology, JetBrains Mono, parchment background -->
        </div>
      </div>

      <!-- Services card -->
      <div class="sidebar-card">
        <div class="sidebar-card-title">Services Delivered</div>
        <div class="tech-grid">
          <span class="tech-pill">[Service category]</span>
        </div>
      </div>

      <!-- CTA card (midnight background) -->
      <div class="sidebar-card sidebar-cta">
        <p>[Audience-specific hook — one sentence related to this project type]</p>
        <a href="https://autonomoustech.ca/contact" class="btn-cta">Let's talk</a>
        <a href="https://autonomoustech.ca/work" class="btn-ghost">See more work</a>
      </div>

    </aside>
  </div>

  <!-- FOOTER CTA (parchment-dark background) -->
  <section class="footer-cta">
    <h2>Building something similar?</h2>
    <p>[Audience-specific invitation — 2 sentences max. No em-dashes.]</p>
    <a href="https://autonomoustech.ca/contact" class="btn-primary">Start the conversation</a>
  </section>

  <!-- FOOTER -->
  <footer>
    <p>2026 <a href="https://autonomoustech.ca">Autonomous Technologies</a></p>
    <p><a href="https://autonomoustech.ca/work">View all case studies</a></p>
  </footer>

  <!-- Scroll reveal -->
  <script>
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => { if (entry.isIntersecting) entry.target.classList.add('visible'); });
    }, { threshold: 0.12 });
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  </script>

</body>
</html>
```

#### CSS Component Reference

Key patterns to implement (write full CSS in the `<style>` block):

```css
/* Nav */
nav { background: var(--parchment); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 200; }
.nav-logo { font-family: 'Fraunces', serif; color: var(--ink); }
.btn-primary { background: var(--vermillion); color: var(--white); border-radius: 4px; font-weight: 600; }
.btn-primary:hover { background: var(--vermillion-dark); }

/* Hero */
.hero { background: var(--midnight); padding: 5rem 2.5rem 4rem; overflow: hidden; }
.hero-breadcrumb a { color: rgba(255,255,255,0.4); font-size: 0.8rem; }
.client-logo-box { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); border-radius: 12px; color: var(--gold); font-family: 'Fraunces', serif; }
.autonomous-logo-box { background: var(--vermillion); border-radius: 12px; color: var(--white); font-family: 'Fraunces', serif; }
.hero-client-name { font-family: 'Fraunces', serif; color: rgba(255,255,255,0.9); }
.hero-client-meta { color: rgba(255,255,255,0.4); font-size: 0.82rem; }
.hero-tag { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); color: rgba(255,255,255,0.6); border-radius: 100px; font-size: 0.78rem; }

/* Metrics strip */
.metrics { background: var(--vermillion); }
.metric-value { font-family: 'Fraunces', serif; font-size: 2.8rem; font-weight: 400; color: var(--white); line-height: 1; }
.metric-label { color: rgba(255,255,255,0.65); text-transform: uppercase; letter-spacing: 0.07em; font-size: 0.78rem; }
.metric { border-right: 1px solid rgba(255,255,255,0.15); }

/* Body layout */
.body-wrap { max-width: 1060px; margin: 0 auto; padding: 5rem 2.5rem; display: grid; grid-template-columns: 1fr 300px; gap: 5rem; align-items: start; }

/* Sidebar */
.sidebar { position: sticky; top: 80px; }
.sidebar-card { background: var(--parchment-light); border: 1px solid var(--border); border-radius: 10px; padding: 1.5rem; margin-bottom: 1.25rem; }
.sidebar-card-title { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.12em; color: var(--caption); }
.detail-key { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: var(--caption); }
.detail-val { font-size: 0.85rem; color: var(--ink); font-weight: 600; }
.detail-val.green { color: var(--sage); }
.tech-pill { background: var(--parchment); border: 1px solid var(--border); color: var(--prose); font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; padding: 0.22rem 0.65rem; border-radius: 4px; }
.sidebar-cta { background: var(--midnight); border-color: transparent; text-align: center; }
.sidebar-cta p { color: rgba(255,255,255,0.65); }
.btn-cta { background: var(--vermillion); color: var(--white); border-radius: 5px; font-weight: 700; }
.btn-cta:hover { background: var(--vermillion-dark); }
.btn-ghost { color: rgba(255,255,255,0.4); }

/* Article */
.section-label { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.14em; color: var(--vermillion); display: inline-flex; align-items: center; gap: 0.6rem; }
.section-label::before { content: ''; width: 18px; height: 1.5px; background: var(--vermillion); display: block; }
.article p { color: var(--prose); line-height: 1.85; margin-bottom: 1.25rem; }

/* Callout grid (2x2) */
.callout-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1px; background: var(--border); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
.callout-card { background: var(--white); padding: 1.75rem; }
.callout-card h4 { font-family: 'Fraunces', serif; color: var(--ink); font-weight: 600; margin-bottom: 0.5rem; }
.callout-card p { font-size: 0.85rem; color: var(--caption); line-height: 1.6; margin: 0; }

/* Before/after illustration */
.ba-illustration { background: var(--white); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
.ba-illustration figcaption { background: var(--parchment-dark); font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: var(--caption); border-top: 1px solid var(--border); padding: 0.85rem 1.5rem; }

/* Deliverables */
.deliverables { list-style: none; border: 1px solid var(--border); border-radius: 10px; overflow: hidden; background: var(--white); }
.deliverable { display: flex; gap: 1.25rem; padding: 1.4rem 1.75rem; border-bottom: 1px solid var(--border); }
.deliverable:hover { background: var(--parchment); }
.deliverable-num { font-family: 'JetBrains Mono', monospace; color: var(--vermillion); font-size: 0.72rem; }
.deliverable strong { color: var(--ink); font-size: 0.95rem; font-weight: 600; display: block; margin-bottom: 0.3rem; }
.deliverable p { color: var(--caption); font-size: 0.85rem; margin: 0; line-height: 1.6; }

/* Outcome visual (2x2 midnight grid) */
.outcome-visual { background: var(--midnight); border-radius: 10px; padding: 2.5rem; display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.outcome-stat { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 1.5rem; text-align: center; }
.outcome-stat-value { font-family: 'Fraunces', serif; font-size: 2.5rem; font-weight: 400; color: var(--gold); display: block; line-height: 1; }
.outcome-stat-label { color: rgba(255,255,255,0.5); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.07em; display: block; }
.outcome-stat-sub { color: rgba(255,255,255,0.3); font-size: 0.75rem; display: block; }

/* Insight cards */
.insight-cards { border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
.insight-card { background: var(--parchment-light); padding: 1.4rem 1.75rem; display: flex; gap: 1rem; border-bottom: 1px solid var(--border); }
.insight-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; margin-top: 0.55rem; }
.insight-dot.red { background: var(--vermillion); }
.insight-dot.gold { background: var(--gold); }
.insight-dot.sage { background: var(--sage); }
.insight-card p { color: var(--prose); font-size: 0.9rem; line-height: 1.6; margin: 0; }
.insight-card strong { color: var(--ink); }

/* Testimonial */
.testimonial { background: var(--parchment-dark); border-left: 4px solid var(--vermillion); border-radius: 0 10px 10px 0; padding: 2.25rem 2.5rem; margin: 3rem 0; }
.testimonial-quote { font-family: 'Fraunces', serif; font-variation-settings: 'opsz' 72; font-size: 1.15rem; font-weight: 400; font-style: italic; color: var(--ink); line-height: 1.7; }
.author-avatar { background: var(--vermillion); color: var(--white); border-radius: 50%; font-family: 'Fraunces', serif; font-weight: 600; }
.author-name { color: var(--ink); font-weight: 600; font-size: 0.9rem; display: block; }
.author-title { color: var(--caption); font-size: 0.8rem; display: block; }

/* Footer CTA */
.footer-cta { background: var(--parchment-dark); border-top: 1px solid var(--border); padding: 6rem 2.5rem; text-align: center; }
.footer-cta h2 { font-family: 'Fraunces', serif; font-variation-settings: 'opsz' 72; font-weight: 400; letter-spacing: -0.03em; color: var(--ink); }
.footer-cta p { color: var(--prose); }

/* Divider */
.divider { border: none; border-top: 1px solid var(--border); margin: 4rem 0; }

/* Scroll reveal */
.reveal { opacity: 0; transform: translateY(22px); transition: opacity 0.55s ease, transform 0.55s ease; }
.reveal.visible { opacity: 1; transform: none; }

/* Responsive */
@media (max-width: 900px) {
  .body-wrap { grid-template-columns: 1fr; }
  .sidebar { position: static; }
  .callout-grid { grid-template-columns: 1fr; }
  .outcome-visual { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 600px) {
  .metrics-grid { grid-template-columns: repeat(2, 1fr); }
  .outcome-visual { grid-template-columns: 1fr; }
}
```

#### SVG Diagram Conventions

When drawing before/after architecture diagrams:
- Background: `#FAFAF7` (near-parchment)
- Tool boxes: `white` fill, `var(--border)` stroke for after-state; `#FFF0EE` fill, vermillion stroke for before-state
- Section labels: JetBrains Mono, 9px, `var(--vermillion)` for BEFORE, `var(--sage)` for AFTER
- Broken connections: `var(--vermillion)` dashed lines, x markers
- Healthy connections: `var(--sage)` solid lines with arrow markers
- Central hub/middleware box: `var(--midnight)` fill, `var(--gold)` stroke and text
- Result/output box: sage-tinted fill, sage stroke
- All text: DM Sans or JetBrains Mono, no other fonts

---

### Output B: Wagtail JSON (`case-study.json`)

```json
{
  "model": "case_studies.CaseStudy",
  "fields": {
    "title": "[Outcome-first headline]",
    "slug": "[client-name-project-slug]",
    "client_name": "[Client Name]",
    "client_industry": "[Industry]",
    "is_confidential": false,
    "published_date": "[YYYY-MM-DD]",
    "tags": ["[industry]", "[service-type]", "[tech-stack-highlight]"],
    "hero_image_alt": "[Hero image description]",
    "metrics": [
      { "value": "[Key metric]", "label": "[What it represents]" }
    ],
    "project_details": {
      "timeline": "[Duration]",
      "team_size": "[e.g. 2 engineers + PM]",
      "engagement_type": "[Fixed scope / Retainer / Time and Materials]"
    },
    "tech_stack": ["[Technology 1]", "[Technology 2]"],
    "body": [
      {
        "type": "challenge_section",
        "value": {
          "label": "The Challenge",
          "heading": "[What the client needed to achieve]",
          "content": "[Full challenge narrative — 2 to 3 paragraphs. No em-dashes.]"
        }
      },
      {
        "type": "solution_section",
        "value": {
          "label": "The Solution",
          "heading": "[What we built]",
          "content": "[Solution narrative. No em-dashes.]",
          "deliverables": [
            { "name": "[Deliverable]", "description": "[One sentence]" }
          ]
        }
      },
      {
        "type": "outcome_section",
        "value": {
          "label": "The Outcome",
          "heading": "[What changed after launch]",
          "content": "[Outcome narrative. No em-dashes.]"
        }
      }
    ],
    "testimonial": {
      "quote": "[Client quote or null]",
      "author_name": "[Name or null]",
      "author_role": "[Role or null]",
      "author_company": "[Company or null]"
    },
    "seo": {
      "meta_title": "[Client] Case Study — Autonomous Tech",
      "meta_description": "[Under 160 chars. Lead with client problem and our solution.]",
      "og_title": "[Client] x Autonomous — [Short outcome statement]",
      "focus_keyword": "[primary search term]",
      "schema_type": "Article"
    },
    "cta": {
      "heading": "Building something similar?",
      "body": "[Audience-specific invitation — 2 sentences, no em-dashes]",
      "button_text": "Start the conversation",
      "button_url": "https://autonomoustech.ca/contact"
    }
  }
}
```

---

## Step 4: File Output Structure

```
[client-slug]-case-study/
├── index.html          — Standalone HTML (send to prospects)
├── case-study.json     — Wagtail CMS import
└── images/
    ├── hero.png        — Imagen 3 generated
    ├── solution.png    — Imagen 3 generated
    ├── outcome.png     — Imagen 3 generated
    └── client-logo.svg — If provided by creator
```

---

## Step 5: Quality Checklist

Before delivering, verify every item:

**Copy**
- [ ] No em-dashes anywhere in copy or JSON
- [ ] Headline leads with client outcome, not our service
- [ ] Challenge section uses JTBD language
- [ ] Tech stack uses real technology names
- [ ] All metrics are real or marked `[ADD METRIC IF AVAILABLE]`
- [ ] Testimonial is real or marked `[REPLACE WITH REAL QUOTE]`
- [ ] Footer CTA copy is audience-specific
- [ ] SEO meta description is under 160 characters

**HTML**
- [ ] All CSS tokens match Editorial Warmth v2 exactly
- [ ] Fraunces hero uses `opsz 144`, weight `400`, `-0.04em`, lh `0.95`
- [ ] Section H2 uses `opsz 72`, weight `400`, `-0.03em`
- [ ] Eyebrow labels use JetBrains Mono (not DM Sans, not DM Mono)
- [ ] Squiggle underline applied to one key word in hero and one section title
- [ ] All CSS inline in `<style>` block
- [ ] Google Fonts import includes Fraunces, DM Sans, JetBrains Mono
- [ ] Responsive at 375px and 1440px
- [ ] Image paths reference `images/` subdirectory
- [ ] Nav links point to `autonomoustech.ca`
- [ ] Scroll reveal applied with `.reveal` class and IntersectionObserver

**JSON**
- [ ] Slug is URL-safe (lowercase, hyphens only)
- [ ] `is_confidential` set correctly
- [ ] Tags are lowercase
- [ ] No em-dashes in any content field

---

## Step 6: Delivery

After generating both outputs:

1. Confirm all files are written to the output directory
2. Tell the creator: send `index.html` to prospects, import `case-study.json` via `manage.py loaddata` or the Wagtail StreamField API
3. Flag any `[ADD METRIC IF AVAILABLE]` or `[REPLACE WITH REAL QUOTE]` markers and ask if they can fill them in now

---

## Companion Skills

- **b2b-website-copywriter** — Use its PSR and Before/After/Bridge frameworks for challenge and outcome sections
- **analytics-audit-client-report** — Reference for HTML report structure patterns and component conventions
- **seo-blog-writer** — Meta title and description should follow its keyword patterns when the case study will be indexed
- **landing-page-copywriter** — Reference for footer CTA copy — low commitment language, adjacent trust signals
- **frontend-design** — Reference for visual direction when adapting layout for unusual project types

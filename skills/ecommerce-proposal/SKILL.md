---
name: ecommerce-proposal
description: Generate tailored Shopify/WooCommerce proposals with branded HTML presentations or PowerPoint attachments. Use when responding to ecommerce job postings, creating pitch decks for Upwork proposals, or generating client-ready proposal documents. Takes job URL or description as input, classifies job type, and outputs personalized proposal text + branded presentation.
allowed-tools: Read, Write, exec, web_fetch, browser
---

# Ecommerce Proposal Generator

Generate high-converting, branded proposals for Shopify/WooCommerce job opportunities.

---

## Overview

This skill creates:
1. **Quick Proposal Text** — For Upwork message/cover letter
2. **Branded Presentation** — HTML (recommended) or PPTX pitch deck

**Output Options:**
| Format | Quality | Use Case |
|--------|---------|----------|
| **HTML** | ⭐⭐⭐⭐⭐ Premium | Client presentations, hosted proposals, shareable links |
| **PPTX** | ⭐⭐ Basic | When client specifically needs PowerPoint |

The system is modular:
- Fixed brand sections (always included)
- Dynamic service modules (matched to job type)
- AI-generated personalization (tailored to specific job)

---

## Input Options

### Option 1: Job URL
```
Generate proposal for: https://www.upwork.com/jobs/~01234567890
```

### Option 2: Job Description
```
Generate proposal for this job:
Title: [job title]
Description: [full description]
Budget: [budget info]
Skills: [required skills]
```

### Option 3: Database Job ID
```
Generate proposal for job ID: 26940
```

---

## Job Classification

Classify the job into one of these categories based on title, description, and skills:

| Category | Signals |
|----------|---------|
| `store-build` | "new store", "build from scratch", "create store", "setup" |
| `theme-customization` | "theme", "customize", "design tweaks", "template" |
| `speed-optimization` | "speed", "performance", "pagespeed", "core web vitals", "slow" |
| `cro-conversion` | "conversion", "CRO", "landing page", "optimize", "not converting" |
| `integration` | "API", "integrate", "connect", "payment gateway", "sync" |
| `migration` | "migrate", "move from", "transfer", "switch platform" |
| `email-automation` | "Klaviyo", "email flow", "abandoned cart", "automation" |
| `bug-fix` | "fix", "broken", "issue", "error", "urgent" |
| `ongoing-maintenance` | "ongoing", "long-term", "maintain", "support", "retainer" |
| `product-listing` | "product upload", "listing", "catalog", "data entry" |

A job can have 1-2 categories. Use primary category for module selection.

---

## Proposal Structure

### Quick Proposal Text (for Upwork message)

**Read `reference/upwork-best-practices.md` for full research.**

The Upwork cover letter is the MOST important part. It determines if they ever see the PDF.

#### The 5-Part Formula

```markdown
Hi [Client Name],

[1. HOOK — First 1-2 sentences MUST grab attention]
→ Reference something SPECIFIC from their job post
→ Lead with their pain point or a relevant result
→ This is what they see in the proposal list

[2. PROOF — 1-2 sentences with measurable results]
→ Similar project, specific outcome
→ Include numbers: "increased by 30%", "from 35 to 82"

[3. VALUE — 3-4 bullet points]
→ What you bring to THIS job
→ Outcomes, not features
→ Keep scannable

[4. CTA — End with a question]
→ Gets them to respond
→ Shows engagement
→ Or offer quick call with specific times

Best,
[Name]
Autonomous
```

#### Length: 150-200 words MAX

Clients are busy. Shorter = better.

#### Instant Rejection (Never Do These)

❌ "Dear Sir/Madam" or "To Whom It May Concern"
❌ "I am writing to express my interest..."
❌ "I am confident I can help you..."
❌ "I have X years of experience in..."
❌ Generic intros that could fit any job
❌ Talking about yourself before their problem
❌ Passive endings ("I look forward to hearing from you")

#### Winning Hooks (Examples)

```
✅ "Your 35 PageSpeed score is costing you sales every day."

✅ "Selling $10K gym equipment requires trust mechanics most templates don't have."

✅ "A 0.8% conversion rate with good traffic means money is leaking somewhere specific."

✅ "Magento to Shopify without losing SEO rankings — I've done this 12 times."
```

#### Winning CTAs (Examples)

```
✅ "What's your biggest priority — the score or the actual load time? Happy to do a quick audit."

✅ "One question: is this Dawn theme or custom? That changes the approach."

✅ "Would a 10-minute call work? I have tomorrow open 2-5pm EST."
```

#### Attachments

- Reference the PDF in your cover letter
- Don't just attach without context
- Say: "I've attached a brief overview of our approach and relevant work."

---

## Presentation Output (Two Options)

### Option A: HTML Presentation (RECOMMENDED)

Premium visual quality with full CSS control. Use for:
- Client-facing proposals
- Hosted shareable links
- Maximum visual impact

**Features:**
- Animated gradient backgrounds
- Glassmorphic cards with hover effects
- Gradient text (cyan → purple → pink)
- Scroll-snap navigation between slides
- Keyboard navigation (← → ↑ ↓)
- Print-ready (Cmd+P for PDF)
- **MUST be mobile-responsive**

**Structure (6 slides):**

| Slide | Content |
|-------|---------|
| **1. Cover** | Logo + brand name, gradient title, subtitle, client info, tagline |
| **2. The Challenge** | 4 pain point cards with icons, hover effects |
| **3. Our Approach** | 4-step process with timeline badges |
| **4. Deliverables** | 3-column grid of what we'll deliver |
| **5. Why Us** | 6 trust builders in 2x3 grid |
| **6. CTA** | Contact info, pricing, timeline |

**Template Location:** `/home/rizki/clawd/output/proposal-gym-premium.html`

**CSS Requirements (from brand guide):**
```css
:root {
  --bg: #08080f;
  --bg-card: rgba(255, 255, 255, 0.03);
  --border: rgba(255, 255, 255, 0.06);
  --cyan: #00d4ff;
  --purple: #a855f7;
  --pink: #ec4899;
  --white: #ffffff;
  --gray: #64748b;
  --light: #94a3b8;
}
```

**Typography:**
- Headings: `Outfit` (700-800 weight)
- Body: `Space Grotesk` (400-500 weight)

**⚠️ MOBILE OPTIMIZATION REQUIRED:**
```css
/* Add to all HTML proposals */
@media (max-width: 768px) {
  .slide { padding: 30px 24px; }
  h1 { font-size: 2rem; }
  h2 { font-size: 1.5rem; }
  .challenge-grid,
  .deliverables-grid,
  .why-grid { grid-template-columns: 1fr; }
  .nav-dots { display: none; }
  .process-step { flex-direction: column; gap: 16px; }
  .step-days { position: static; margin-top: 12px; }
}
```

### Option B: PPTX (Basic)

Use python-pptx or pptxgenjs. Limited visual capabilities.

**When to use:**
- Client specifically requests PowerPoint
- Needs editable format
- Offline presentation required

**Script:** `/home/rizki/clawd/scripts/autonomous_pptx.py`

```bash
uv run /home/rizki/clawd/scripts/autonomous_pptx.py
```

**Limitations:**
- No real gradients on text
- Limited typography control
- No animations
- Basic card styling only

---

## Deployment Workflow

### Hosting on pages.autonomoustech.ca

Proposals can be hosted for shareable links.

**Repository:** `github.com/autonomous-tech/landing-pages`
**Local path:** `/home/rizki/landing-pages`

**Deployment Steps:**

```bash
# 1. Copy HTML to proposals folder
cp /path/to/proposal.html /home/rizki/landing-pages/proposals/[client]-[project]-[date].html

# 2. Commit and push
cd /home/rizki/landing-pages
git add proposals/
git commit -m "Add [client] proposal"
git pull --rebase && git push

# 3. URL available at:
# https://pages.autonomoustech.ca/proposals/[client]-[project]-[date].html
```

**Naming Convention:**
```
[client-name]-[project-type]-YYYY-MM-DD.html

Examples:
- premium-fitness-shopify-2026-02-07.html
- zenith-seo-audit-2026-02-03.html
- um-enterprises-email-2026-02-02.html
```

**Repository Structure:**
```
landing-pages/
├── proposals/           ← Client proposals go here
│   ├── autonomous-logo-small.png
│   └── [proposal files].html
├── docs/                ← Documentation/demos
├── services/            ← Service pages
├── wrangler.jsonc       ← Cloudflare Pages config
└── .github/workflows/   ← Auto-generates index
```

**Auto-deployment:** Push to main triggers Cloudflare Pages build (~30-60 seconds).

---

## Service Modules

Load the appropriate module from `modules/` based on job classification:

| File | Category |
|------|----------|
| `modules/store-build.md` | store-build |
| `modules/speed-optimization.md` | speed-optimization |
| `modules/cro-conversion.md` | cro-conversion |
| `modules/integration.md` | integration |
| `modules/migration.md` | migration |
| `modules/email-automation.md` | email-automation |
| `modules/ongoing-maintenance.md` | ongoing-maintenance |
| `modules/theme-customization.md` | theme-customization |

Each module contains:
- Service description
- Typical deliverables
- Our process for this service
- Pricing guidance
- Relevant case study placeholder

---

## Brand Compliance

All presentations must follow the Autonomous brand guide:
- Read `../brand-guide/SKILL.md` for full guidelines
- Dark theme (#0a0a12 or #08080f background)
- Cyan (#00d5ff) for headings and accents
- White text for primary content
- Mid gray (#94a3b8) for secondary text
- Glassmorphic card style with backdrop blur
- Gradient text for key headings
- → arrows for list items
- Tagline: "Canadian Expertise. Pakistani Efficiency. World-class Quality."

---

## Execution Flow

```
1. RECEIVE INPUT
   └─ Job URL, description, or ID

2. FETCH JOB DATA
   └─ If URL: fetch and parse
   └─ If ID: query database
   └─ If description: use directly

3. CLASSIFY JOB
   └─ Determine primary category
   └─ Identify secondary category (if applicable)

4. EXTRACT PAIN POINTS
   └─ Parse description for specific problems
   └─ Note budget, timeline, skills requested
   └─ Identify client industry/niche

5. LOAD MODULES
   └─ Read relevant service module(s)
   └─ Read brand guide

6. GENERATE CONTENT
   └─ Write job-specific "Challenge" section
   └─ Write tailored "Approach" section
   └─ Select relevant case study
   └─ Compose quick proposal text

7. BUILD PRESENTATION
   └─ Create HTML file (recommended)
   └─ Ensure mobile responsiveness
   └─ Output to /home/rizki/clawd/output/

8. DEPLOY (OPTIONAL)
   └─ Copy to landing-pages repo
   └─ Git commit and push
   └─ Share URL with client

9. OUTPUT
   └─ Quick proposal text (for copy/paste)
   └─ Presentation file path or URL
```

---

## Output Format

```markdown
## Quick Proposal (Copy to Upwork)

[proposal text here]

---

## Presentation Generated

**Local:** /home/rizki/clawd/output/[proposal-name].html
**Hosted:** https://pages.autonomoustech.ca/proposals/[proposal-name].html

---

## Job Analysis

- **Category:** [primary] / [secondary]
- **Pain Points:** [extracted list]
- **Budget:** [from job]
- **Recommended Services:** [matched services]
```

---

## Example Usage

**Input:**
```
Generate proposal for this job:

Title: Shopify Speed Optimization Expert Needed
Description: Our store loads slowly on mobile. PageSpeed score is 35. 
Need someone to improve Core Web Vitals and real loading speed.
Budget: $200 fixed
Skills: Shopify, Performance Tuning
```

**Output:**

### Quick Proposal (150 words, Upwork-optimized)

```
Your 35 PageSpeed score is costing you sales every time someone tries to load your store on mobile.

Last month I took a fashion store from 28 → 78 on mobile PageSpeed — bounce rate dropped 22%, conversions up 15%. No fake optimizations that break features.

For your store, I'd focus on:
→ Image compression + lazy loading
→ Render-blocking resource cleanup
→ App script consolidation
→ Liquid template efficiency

Timeline: 3-5 days for full optimization.

I've attached a brief overview of our process and a relevant case study.

One question: are you seeing the slow speed mostly on product pages, or across the whole site? That'll help me prioritize.

Best,
[Name]
Autonomous
```

### Presentation
**Hosted:** https://pages.autonomoustech.ca/proposals/client-speed-optimization-2026-02-07.html

### Why This Works
- **Hook:** Opens with their specific problem (35 score)
- **Proof:** Specific result with numbers (28→78, 22% bounce drop)
- **Value:** Bullet points of what we'll do
- **CTA:** Ends with relevant question (gets response)

---

## Files in This Skill

```
ecommerce-proposal/
├── SKILL.md                    # This file
├── generate-ppt.js             # PPTX generator (Node.js, basic)
├── package.json                # Node dependencies (pptxgenjs)
├── modules/
│   ├── store-build.md          # New store development
│   ├── speed-optimization.md   # Performance optimization
│   ├── cro-conversion.md       # Conversion rate optimization
│   ├── integration.md          # API & integrations
│   ├── migration.md            # Platform migration
│   ├── email-automation.md     # Klaviyo & email flows
│   ├── ongoing-maintenance.md  # Retainer/support
│   └── theme-customization.md  # Theme & design work
├── templates/
│   └── proposal.html           # HTML template reference
└── reference/
    ├── job-analysis.md         # Market research (7,695 jobs)
    ├── case-studies.md         # Portfolio examples
    └── upwork-best-practices.md # Proposal writing research
```

**External scripts:**
- `/home/rizki/clawd/scripts/autonomous_pptx.py` — Python PPTX generator (basic)

**Deployment repo:**
- `/home/rizki/landing-pages` — GitHub Pages hosting

---

## Database Connection (Optional)

If pulling jobs from the leads database:

```javascript
const { Client } = require('pg');
const client = new Client({
  connectionString: 'postgres://analytics_user:Rahnuma824630*@46.62.227.215:54321/postgres'
});

// Fetch job by ID
const job = await client.query(`
  SELECT * FROM leads_job WHERE id = $1
`, [jobId]);
```

---

## Tips for High-Converting Proposals

Based on analysis of 7,695 ecommerce jobs:

1. **40% of clients want experience proof** — Always mention relevant past work
2. **34% want price upfront** — Include ballpark or "starting at" pricing
3. **30% care about communication** — Write clearly, no fluff
4. **Lead with their problem** — First sentence should mirror their pain
5. **Be specific** — Reference details from THEIR job, not generic claims
6. **Clear CTA** — Tell them exactly what to do next

---

## Pricing Guidance

Based on market data:

| Service | Market Range | Our Positioning |
|---------|--------------|-----------------|
| Speed Optimization | $50-250 | $150-400 (premium) |
| Store Build | $200-2500 | $500-2000 |
| CRO/Landing Page | $100-600 | $200-800 |
| Integration | $100-1000 | $200-1000 |
| Migration | $200-1500 | $400-1200 |
| Email Setup | $200-1000 | $300-800 |
| Ongoing Retainer | $15-50/hr | $30-60/hr |

Position above median but justify with quality + outcomes.

---

## Changelog

### 2026-02-07
- Added HTML presentation output (recommended over PPTX)
- Documented deployment workflow to pages.autonomoustech.ca
- Added mobile responsiveness requirements
- Created Python PPTX generator script
- Established naming conventions for hosted proposals

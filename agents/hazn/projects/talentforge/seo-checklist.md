# TalentForge — SEO Optimization Checklist

**File:** `/home/rizki/autonomous-proposals/talentforge/homepage.html`  
**Date:** 2026-03-05  
**Agent:** Hazn SEO Specialist

---

## ✅ Implemented

### 1. Head SEO Tags
- [x] `<title>` updated: "Hire Pre-Screened Data & AI Engineers | TalentForge"
- [x] `<meta name="description">` — 155 chars, includes primary keywords + 72-hour promise
- [x] `<meta name="keywords">` — 6 target keywords
- [x] `<link rel="canonical" href="https://talentforge.io/">`
- [x] `<meta name="robots" content="index, follow">`

### 2. Open Graph Tags
- [x] `og:type`, `og:url`, `og:title`, `og:description`, `og:image`, `og:site_name`, `og:locale`

### 3. Twitter Card Tags
- [x] `twitter:card` (summary_large_image), `twitter:title`, `twitter:description`, `twitter:image`

### 4. JSON-LD Structured Data (`@graph` array)
- [x] **Organization** — name, url, logo, description, foundingLocation (Karachi), areaServed (US/UK), knowsAbout, serviceType
- [x] **WebPage** — url, name, description, isPartOf, about
- [x] **Service (Tier 1)** — Talent + Payroll, $2,800/mo, USD
- [x] **Service (Tier 2)** — Full Stack Hire, $3,800/mo, USD
- [x] **FAQPage** — 5 Q&A pairs matching visible FAQ section

### 5. Visible FAQ Section
- [x] Added before CTA section with `id="faq"` and `aria-label="Frequently Asked Questions"`
- [x] 5 `<details>`/`<summary>` accordion items — accessible, keyboard-navigable
- [x] Styled with `glass-card rounded-xl p-6` per design system
- [x] Electric blue chevron indicator with CSS `group-open:rotate-180` animation
- [x] Questions match schema FAQ markup exactly

### 6. Image Alt Text
- [x] No `<img>` tags present in the file (engineer card is CSS/SVG — no alt fix needed)
- [x] Scrollbar background reference to `hero-bg.png` is CSS, not an `<img>` tag

### 7. Section aria-labels
- [x] Hero → `aria-label="Hero — Hire Data and AI Engineers"`
- [x] Problem → `aria-label="The staffing problem with generalist platforms"`
- [x] Solution → `aria-label="TalentForge solution and differentiators"`
- [x] How It Works → `aria-label="How TalentForge works — 3 step process"`
- [x] Pricing → `aria-label="Hiring models — Tier 1 and Tier 2 pricing"`
- [x] FAQ → `aria-label="Frequently Asked Questions"`
- [x] CTA → `aria-label="Get started with TalentForge"`

---

## Target Keywords
| Keyword | Status |
|---------|--------|
| hire data engineers remotely | ✅ In meta, title, body |
| AI engineers for hire | ✅ In meta, title, body |
| pre-screened data engineers | ✅ In meta, H1, body |
| remote data engineering talent | ✅ In meta, body |
| hire data engineer Pakistan | ✅ In meta, schema |
| AI engineering talent platform | ✅ In meta, schema |

---

## Schema Coverage
- Organization entity established for knowledge graph
- FAQPage eligible for FAQ rich results in Google SERPs
- Service schema with pricing eligible for structured snippets
- WebPage schema for AI crawler entity clarity

---

## Notes
- Domain placeholder `https://talentforge.io` — swap when confirmed live domain
- `og-image.png` and `logo.png` need to be created and uploaded to the root
- FAQ section uses native `<details>`/`<summary>` — no JS dependency

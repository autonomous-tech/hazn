# Platform-Specific AI Readiness

This reference defines how to score a site's readiness for each major AI engine individually.
Generic "AI search readiness" scoring misses platform-specific differences — each engine has different
source preferences, citation patterns, and optimization levers.

---

## Evidence Labels

| Label | Meaning |
|-------|---------|
| `Observed` | Directly confirmed — found in page source, search results, or platform check |
| `Assessment` | Judgment or inference from observed signals |
| `Not verified` | Platform not checked or signal not findable — state clearly |

---

## Platform Profiles

### 1. ChatGPT (OpenAI)

**Why it matters:** Drives ~87.4% of all AI referral traffic across industries (Conductor 2025). Optimize here first.

**What ChatGPT favors:**
- Bing-indexed content (ChatGPT search is Bing-backed)
- Wikipedia and Reddit as authority validators
- Clear entity definition in first paragraph
- Content with statistics and cited sources
- Sites not blocking `GPTBot` or `ChatGPT-User`

**Checks:**

```
robots.txt: GPTBot allowed?
robots.txt: ChatGPT-User allowed?
First paragraph: defines brand/product clearly?
Content: statistics with sources?
Off-site: Wikipedia present? Reddit mentions?
```

| Signal | Status | Label |
|--------|--------|-------|
| GPTBot allowed | ✅ / 🔴 | Observed |
| ChatGPT-User allowed | ✅ / 🔴 | Observed |
| Bing indexing (test: `site:bing.com/search?q=site:[domain]`) | ✅ / 🔴 | Observed |
| Wikipedia entity present | ✅ / 🔴 | Observed |
| Reddit presence | ✅ / 🔴 | Observed |

**Manual test:** Ask ChatGPT: *"What is [brand]?"* and *"Best [category] for [use case]"* — is the brand cited?

---

### 2. Perplexity

**Why it matters:** Always shows sources with links. Strong at finding specific, well-structured answers.
Reddit accounts for ~1.8% of ChatGPT citations but is disproportionately influential in Perplexity.

**What Perplexity favors:**
- Direct, answer-first structured content
- Pages that are easy to quote (40–60 word passages)
- FAQ sections with natural language questions
- Review/comparison content (G2, Reddit)
- Sites not blocking `PerplexityBot` or `Perplexity-User`

**Checks:**

```
robots.txt: PerplexityBot allowed?
robots.txt: Perplexity-User allowed?
Content structure: answer-first passages?
FAQ section present?
G2/Reddit presence?
```

| Signal | Status | Label |
|--------|--------|-------|
| PerplexityBot allowed | ✅ / 🔴 | Observed |
| Perplexity-User allowed | ✅ / 🔴 | Observed |
| Answer-first structure | ✅ / 🟡 / 🔴 | Assessment |
| G2/Capterra profile | ✅ / 🔴 | Observed |

**Manual test:** Search for *"[brand] review"* and *"[category] comparison"* on Perplexity.

---

### 3. Google AI Overviews (Gemini)

**Why it matters:** Appears in 16–49% of Google searches depending on vertical (Semrush/Conductor 2025).
Strong correlation with traditional Google rankings — good SEO is the foundation.

**What Google AI Overviews favors:**
- Top-ranking Google pages (traditional SEO is a prerequisite)
- FAQPage and HowTo schema
- Structured content matching informational query intent
- Google Knowledge Graph entity recognition
- Sites not blocking `Google-Extended`

**Checks:**

```
robots.txt: Google-Extended allowed?
robots.txt: Googlebot allowed?
Schema: FAQPage present?
Schema: Organization with sameAs?
Google ranking: does site appear in top 5 for core queries?
Knowledge Panel: does brand have one?
```

| Signal | Status | Label |
|--------|--------|-------|
| Google-Extended allowed | ✅ / 🔴 | Observed |
| FAQPage schema | ✅ / 🟡 / 🔴 | Observed |
| Organization sameAs schema | ✅ / 🟡 / 🔴 | Observed |
| Knowledge Panel exists | ✅ / 🔴 | Observed |
| Wikidata entity | ✅ / 🔴 | Observed |

**Manual test:** Search core queries on Google. Does an AI Overview appear? Is the brand cited in it?

---

### 4. Gemini (Google Assistant / Workspace)

**Why it matters:** Deeply integrated with Google Workspace and Google ecosystem. Favors Google-native signals.

**What Gemini favors:**
- Google Knowledge Graph presence
- Google Business Profile (for local/B2B)
- YouTube content
- Schema with sameAs pointing to Google-recognized properties
- Strong Google organic ranking

**Checks:**

```
Google Business Profile: exists + complete?
YouTube: brand channel or mentions?
Wikidata: entity with Google-compatible properties?
Schema: sameAs linking to GBP, Wikipedia, LinkedIn?
```

| Signal | Status | Label |
|--------|--------|-------|
| Google Business Profile | ✅ / 🟡 / 🔴 | Observed |
| YouTube presence | ✅ / 🟡 / 🔴 | Observed |
| sameAs in Organization schema | ✅ / 🔴 | Observed |
| Wikidata entity | ✅ / 🔴 | Observed |

---

### 5. Bing Copilot (Microsoft)

**Why it matters:** Bing powers ChatGPT search. Bing Copilot is integrated into Windows and Edge — large enterprise user base.

**What Bing Copilot favors:**
- Bing-indexed pages (verify with `site:bing.com/search?q=site:[domain]`)
- IndexNow support (tells Bing immediately when content updates)
- LinkedIn presence (Microsoft-owned)
- GitHub presence (Microsoft-owned)
- Content freshness signals

**Checks:**

```
robots.txt: Bingbot allowed?
Bing index: confirm with bing.com site: query
IndexNow: implemented? (check sitemap submission)
LinkedIn: company + leadership pages?
GitHub: org presence?
```

| Signal | Status | Label |
|--------|--------|-------|
| Bingbot allowed | ✅ / 🔴 | Observed |
| Bing indexed | ✅ / 🔴 | Observed |
| LinkedIn presence | ✅ / 🟡 / 🔴 | Observed |
| GitHub presence (tech brands) | ✅ / 🟡 / 🔴 | Observed |
| "Last updated" dates on content | ✅ / 🔴 | Observed |

**Manual test:** Search core queries on Bing. Does Copilot cite the brand in its response?

---

## Platform-Specific AI Readiness Summary Table

Use this in the HTML report after the standard AI Search Readiness section:

```markdown
## Platform-Specific AI Readiness

| Platform | Crawler Access | Content Fit | Off-Site Signals | Readiness |
|----------|:--------------:|:-----------:|:----------------:|:---------:|
| ChatGPT (Bing) | ✅/🔴 | ✅/🟡/🔴 | ✅/🟡/🔴 | Strong/Mod/Weak |
| Perplexity | ✅/🔴 | ✅/🟡/🔴 | ✅/🟡/🔴 | Strong/Mod/Weak |
| Google AI Overviews | ✅/🔴 | ✅/🟡/🔴 | ✅/🟡/🔴 | Strong/Mod/Weak |
| Gemini | ✅/🔴 | ✅/🟡/🔴 | ✅/🟡/🔴 | Strong/Mod/Weak |
| Bing Copilot | ✅/🔴 | ✅/🟡/🔴 | ✅/🟡/🔴 | Strong/Mod/Weak |

**Strongest platform:** [name + why]
**Biggest gap:** [name + one-line fix]
```

---

## HTML Report Section

This feeds into the **AI Search Readiness** section of the HTML report (Step 9 in `seo-audit/SKILL.md`).
Extend the existing AI Search Readiness section with:

1. Standard AI crawler access table (existing)
2. **Platform-Specific Readiness grid** (this reference)
3. Micro-upsell callout

---

## Scoring Contribution

Platform-specific AI readiness feeds into **Category 6: Platform Optimization (10 pts)** of the GEO Composite Score:

| Sub-criterion | Max Pts |
|---------------|---------|
| Google Business Profile complete (B2B/local) | 3 |
| Wikidata entity with properties | 3 |
| Crunchbase / equivalent directory | 2 |
| Active on platforms AI cites for the vertical | 2 |

---

## Micro-Upsell Prompt (HTML report)

> 🔍 **Which platform is your biggest AI citation gap?** With a full platform-by-platform readiness review, we'd show you exactly which engine is underserving you and map out the three fastest fixes. Part of the **SEO + GEO Audit** engagement. [Book a 20-min call →](https://calendly.com/rizwan-20/30min)

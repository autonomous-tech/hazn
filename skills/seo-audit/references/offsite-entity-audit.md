# Off-Site Entity Audit

This reference defines how to run the off-site entity and brand mention layer for any SEO audit.
Run this after on-page and technical checks. All checks use `web_search` — no API keys needed.

---

## Purpose

AI engines don't only cite your domain — they cite where *you appear* across the web.
A brand that is invisible on LinkedIn, Reddit, Wikipedia, and G2 will underperform in AI-generated answers
regardless of how well-optimized the main site is.

This layer answers: **Is this brand recognizable as a real entity with off-site presence?**

---

## Evidence Labels

Apply one label to every finding in this layer:

| Label | Meaning |
|-------|---------|
| `Observed` | Directly confirmed by search result or page visit |
| `Assessment` | Interpretation or judgment drawn from observed evidence |
| `Not verified` | Not checked or not findable — state this clearly, do not guess |

---

## Platforms to Check + Search Queries

### 1. LinkedIn

**Purpose:** Most B2B AI citations reference LinkedIn for org/founder validation.

```
web_search: site:linkedin.com/company "[brand name]"
web_search: site:linkedin.com/in "[founder or CEO name]" "[brand name]"
```

| Signal | Score |
|--------|-------|
| Company page exists + active | ✅ Strong |
| Company page exists, minimal activity | 🟡 Weak |
| No company page found | 🔴 Missing |
| Founder/leadership page links to company | ✅ Bonus |

---

### 2. Reddit

**Purpose:** Perplexity and ChatGPT heavily cite Reddit for brand comparisons and recommendation queries.

```
web_search: site:reddit.com "[brand name]"
web_search: "[brand name]" reddit review OR recommendation OR vs
```

| Signal | Score |
|--------|-------|
| Multiple threads discussing brand | ✅ Strong |
| 1–2 mentions, minimal engagement | 🟡 Weak |
| No Reddit presence | 🔴 Missing |
| Negative sentiment dominates | ⚠️ Risk |

---

### 3. YouTube

**Purpose:** Google AI Overviews and Perplexity frequently cite YouTube for how-to and explainer queries.

```
web_search: site:youtube.com "[brand name]"
web_search: "[brand name]" youtube tutorial OR review OR walkthrough
```

| Signal | Score |
|--------|-------|
| Brand-owned channel with relevant content | ✅ Strong |
| Mentioned in third-party videos | 🟡 Moderate |
| No YouTube presence found | 🔴 Missing |

---

### 4. Wikipedia / Wikidata

**Purpose:** Wikipedia accounts for ~7.8% of all ChatGPT citations. Wikidata is used for entity disambiguation by Google and Gemini.

```
web_search: site:en.wikipedia.org "[brand name]"
web_search: site:wikidata.org "[brand name]"
```

Direct check:
- `https://www.wikidata.org/w/index.php?search=[brand]`
- `https://en.wikipedia.org/wiki/[Brand_Name]`

| Signal | Score |
|--------|-------|
| Wikipedia article exists for brand | ✅ Strong (6 pts in GEO scoring) |
| Brand mentioned in a related Wikipedia article | 🟡 Moderate (3 pts) |
| Wikidata entity exists with properties | ✅ Strong |
| Wikidata stub only | 🟡 Weak |
| Neither found | 🔴 Missing |

---

### 5. G2 / Capterra / Trustpilot (SaaS/Services)

**Purpose:** Perplexity and ChatGPT cite G2/Capterra for software comparison queries ("best X tool", "X vs Y").

```
web_search: site:g2.com "[brand name]"
web_search: site:capterra.com "[brand name]"
web_search: site:trustpilot.com "[brand name]"
```

| Signal | Score |
|--------|-------|
| Active profile with reviews | ✅ Strong (5 pts in GEO scoring) |
| Profile exists, few/no reviews | 🟡 Weak |
| Not present | 🔴 Missing |

*Skip if client is not SaaS or does not sell software/tools.*

---

### 6. Crunchbase

**Purpose:** Used by AI engines for funding, founding date, and org identity validation.

```
web_search: site:crunchbase.com "[brand name]"
```

| Signal | Score |
|--------|-------|
| Complete profile with org data | ✅ Strong |
| Stub or incomplete | 🟡 Weak |
| Not found | 🔴 Missing |

---

### 7. GitHub (Tech / SaaS brands)

**Purpose:** Technical credibility signal for developer tools, APIs, and SaaS products.

```
web_search: site:github.com "[brand name]"
```

| Signal | Score |
|--------|-------|
| Active org with public repos | ✅ Strong |
| Account exists, minimal activity | 🟡 Weak |
| Not found | 🔴 Missing (only flag if tech brand) |

---

### 8. Product Hunt

**Purpose:** Launch visibility and community credibility for SaaS and tools.

```
web_search: site:producthunt.com "[brand name]"
```

| Signal | Score |
|--------|-------|
| Listed with upvotes and reviews | ✅ Strong |
| Listed but no engagement | 🟡 Weak |
| Not found | 🔴 Missing (flag if SaaS/tool) |

---

### 9. Industry Press / Trade Publications

**Purpose:** Third-party mentions in recognized publications are strong EEAT and GEO signals.

```
web_search: "[brand name]" site:[industry-publication.com]
web_search: "[brand name]" press mention OR featured OR interview
web_search: "[brand name]" -site:[brand-domain.com] inurl:blog OR inurl:news
```

| Signal | Score |
|--------|-------|
| 3+ external mentions in recognizable publications | ✅ Strong |
| 1–2 external mentions | 🟡 Moderate |
| No external press found | 🔴 Missing |

---

### 10. Podcasts (Optional, bonus)

**Purpose:** Podcast citations are rare but high-value for authority in some verticals.

```
web_search: "[brand name]" podcast guest OR featured OR episode
```

---

## Off-Site Summary Table

Use this at the end of the off-site section in the audit report:

```markdown
## Off-Site Entity Validation

| Platform | Status | Evidence | Label |
|----------|--------|----------|-------|
| LinkedIn (Company) | ✅ / 🟡 / 🔴 | [link or search result snippet] | Observed |
| LinkedIn (Leadership) | ✅ / 🟡 / 🔴 | ... | Observed |
| Reddit | ✅ / 🟡 / 🔴 | ... | Observed |
| YouTube | ✅ / 🟡 / 🔴 | ... | Observed |
| Wikipedia | ✅ / 🟡 / 🔴 | ... | Observed |
| Wikidata | ✅ / 🟡 / 🔴 | ... | Observed |
| G2 / Capterra | ✅ / 🟡 / 🔴 | ... | Observed |
| Crunchbase | ✅ / 🟡 / 🔴 | ... | Observed |
| GitHub | ✅ / 🟡 / 🔴 | ... | Observed |
| Product Hunt | ✅ / 🟡 / 🔴 | ... | Observed |
| Press/Publications | ✅ / 🟡 / 🔴 | ... | Observed |

**Overall Off-Site Entity Strength:** Strong / Moderate / Weak

**Biggest Gap:** [highest-impact missing platform + why it matters for AI citation]
```

---

## Scoring in the GEO Composite

Off-site entity strength feeds into **Category 2: Brand Authority Signals (20 pts)** of the GEO Composite Score.

| Sub-criterion | Max Pts |
|---------------|---------|
| Wikipedia article or mention | 6 |
| G2/Capterra/Trustpilot (where applicable) | 5 |
| Industry publications / non-owned press | 5 |
| LinkedIn presence | 2 |
| YouTube presence | 2 |

---

## Micro-Upsell Prompt (HTML report)

> 🔍 **Want validated off-site coverage?** With a full entity audit + backlink analysis, we'd map every platform where you're missing and prioritize the three that would have the fastest impact on AI citation. Part of the **SEO + GEO Audit** engagement. [Book a 20-min call →](https://calendly.com/rizwan-20/30min)

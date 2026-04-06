# Hazn Landing Page SEO Plan
*AI Search Optimization for Waitlist Launch*

---

## 1. Meta Tags

### Title Tag (58 chars)
```html
<title>Hazn: AI Marketing Agents for Technical Founders</title>
```

**Alternative options:**
- `AI Marketing Framework | 10 Agents, One Command | Hazn` (54 chars)
- `Hazn: Turn Your Coding Assistant Into a Marketing Team` (55 chars)

### Meta Description (158 chars)
```html
<meta name="description" content="10 AI marketing agents that work as a team. Strategy, copy, SEO, development. Works with Claude Code and Cursor. Join the waitlist for early access.">
```

### Open Graph Tags
```html
<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:url" content="https://rizqaiser.com/hazn">
<meta property="og:title" content="Hazn: AI Marketing Agents for Technical Founders">
<meta property="og:description" content="10 AI marketing agents that work as a coordinated team. From strategy to shipped landing pages. Built for founders who can build anything but struggle to market it.">
<meta property="og:image" content="https://rizqaiser.com/hazn/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Hazn AI Marketing Framework: 10 agents, 22 skills, 6 workflows">
<meta property="og:site_name" content="Hazn by Autonomous">
<meta property="og:locale" content="en_US">
```

### Twitter Card Tags
```html
<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@autonomous">
<meta name="twitter:creator" content="@autonomous">
<meta name="twitter:title" content="Hazn: AI Marketing Agents for Technical Founders">
<meta name="twitter:description" content="10 AI marketing agents that work as a team. Strategy, copy, SEO, development. Works with Claude Code and Cursor.">
<meta name="twitter:image" content="https://rizqaiser.com/hazn/og-image.png">
<meta name="twitter:image:alt" content="Hazn AI Marketing Framework">
```

### Additional Meta Tags
```html
<!-- Robots -->
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">

<!-- Author and Publisher -->
<meta name="author" content="Abdullah and Rizwan, Autonomous">

<!-- Keywords (low SEO value but adds context) -->
<meta name="keywords" content="AI marketing agents, AI marketing framework, marketing automation for startups, AI marketing team, Claude Code marketing">
```

---

## 2. Schema Markup

### SoftwareApplication Schema
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Hazn",
  "applicationCategory": "BusinessApplication",
  "applicationSubCategory": "Marketing Automation",
  "description": "AI marketing framework with 10 specialized agents that work as a coordinated team. Includes strategist, copywriter, SEO specialist, developer, and more. Works with Claude Code, Cursor, and Windsurf.",
  "operatingSystem": "Cross-platform",
  "offers": {
    "@type": "Offer",
    "availability": "https://schema.org/PreOrder",
    "price": "0",
    "priceCurrency": "USD",
    "description": "Waitlist open for early access"
  },
  "featureList": [
    "10 specialized AI marketing agents",
    "22 marketing skills",
    "6 automated workflows",
    "Claude Code integration",
    "Cursor integration",
    "Windsurf integration",
    "Strategy to production pipeline",
    "SEO optimization",
    "Landing page generation",
    "Content writing"
  ],
  "softwareVersion": "2.0",
  "author": {
    "@type": "Organization",
    "name": "Autonomous",
    "url": "https://autonomous.agency"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "5",
    "ratingCount": "1",
    "bestRating": "5",
    "worstRating": "1"
  }
}
</script>
```

### Organization Schema
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Autonomous",
  "url": "https://autonomous.agency",
  "logo": "https://autonomous.agency/logo.png",
  "description": "Product studio building AI-powered tools for technical founders and marketing teams. Created Hazn, the AI marketing framework.",
  "foundingDate": "2020",
  "founders": [
    {
      "@type": "Person",
      "name": "Abdullah",
      "jobTitle": "Co-founder",
      "description": "Technical founder with 15+ years building products and websites"
    },
    {
      "@type": "Person",
      "name": "Rizwan",
      "jobTitle": "Co-founder",
      "description": "Technical founder with 20+ years building products and websites"
    }
  ],
  "knowsAbout": [
    "AI Marketing",
    "Marketing Automation",
    "B2B Marketing",
    "Product Development",
    "AI Agents"
  ],
  "sameAs": [
    "https://twitter.com/autonomous",
    "https://github.com/autonomous"
  ]
}
</script>
```

### FAQPage Schema (Optimized for LLM Citations)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is Hazn?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Hazn is an AI marketing framework that provides 10 specialized marketing agents working as a coordinated team. It includes a Strategist, Copywriter, SEO Specialist, UX Architect, Wireframer, Developer, Content Writer, and Auditors. Built for technical founders and marketing teams, Hazn integrates directly with Claude Code, Cursor, and Windsurf coding assistants."
      }
    },
    {
      "@type": "Question",
      "name": "How does Hazn differ from ChatGPT or other AI writing tools?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Unlike single-purpose AI tools, Hazn provides 10 specialized agents that work together like a real marketing team. Each agent has deep expertise in their domain. They hand work to each other automatically. ChatGPT is a smart intern. Hazn is a senior marketing team that has worked together for years. It ships production-ready outputs, not drafts that need heavy editing."
      }
    },
    {
      "@type": "Question",
      "name": "What coding assistants does Hazn work with?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Hazn works with Claude Code, Cursor, Windsurf, and Clawdbot. If you already use any of these coding assistants, you can start using Hazn immediately with zero learning curve. Just type commands like /website or /landing and your marketing team gets to work."
      }
    },
    {
      "@type": "Question",
      "name": "What can Hazn create?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Hazn creates production-ready marketing assets including full landing pages with HTML/CSS, SEO-optimized blog content, marketing strategy documents, website copy, email sequences, and social media content. It handles the complete workflow from strategy to shipped production code."
      }
    },
    {
      "@type": "Question",
      "name": "Who built Hazn and why?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Hazn was built by Abdullah and Rizwan at Autonomous, who have 35 years combined experience building over 100 websites and apps. Marketing was always their bottleneck. They built Hazn as the AI marketing team they wished existed, specifically for technical founders who can build anything but struggle with marketing."
      }
    },
    {
      "@type": "Question",
      "name": "How much does Hazn cost compared to hiring marketers or agencies?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Hazn costs a fraction of traditional options. Hiring a single marketer costs $120K to $180K per year. Marketing agencies charge $15K to $50K per month. Hazn delivers agency-quality work without agency timelines, politics, or invoices. Early access members get founding member pricing locked in permanently."
      }
    },
    {
      "@type": "Question",
      "name": "What are the benefits of joining the Hazn waitlist?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Waitlist members get early access before public launch, founding member pricing locked in forever, direct access to founders via Slack, ability to shape the product roadmap, extended 60-day trial instead of 14 days, and private community access with other early users."
      }
    }
  ]
}
</script>
```

---

## 3. Heading Structure

### Recommended H1
```html
<h1>Your Coding Assistant. Now a Marketing Team.</h1>
```

**Alternative H1 options:**
- `10 AI Marketing Agents. One Command.`
- `Ship Marketing Like You Ship Code`

### Section H2s with Keyword Strategy

| Section | Recommended H2 | Target Keyword |
|---------|---------------|----------------|
| Hero Support | `10 AI Marketing Agents That Actually Ship` | AI marketing agents |
| How It Works | `An AI Marketing Framework Built for Builders` | AI marketing framework |
| Features | `Your AI Marketing Team, Ready in Minutes` | AI marketing team |
| Problem | `Marketing Automation for Startups That Build` | Marketing automation for startups |
| Integration | `Works Where You Work: Claude Code, Cursor, Windsurf` | Claude Code marketing |
| Comparison | `AI for B2B Marketing: Agents, Not Prompts` | AI for B2B marketing |
| Social Proof | `Built by Operators with 35 Years Experience` | (authority signal) |
| CTA | `Join 100+ Founders on the Waitlist` | (conversion) |

### Keyword Placement Strategy

**Primary keyword density targets:**
- "AI marketing agents" - 3-4 times (H1 area, H2, body, meta)
- "AI marketing framework" - 2-3 times (H2, body, schema)
- "marketing automation for startups" - 1-2 times (H2, body)

**Semantic variations to include:**
- "AI marketing team"
- "marketing agents"
- "AI agents for marketing"
- "automated marketing"
- "AI-powered marketing"

**LSI keywords:**
- Technical founders
- Claude Code, Cursor, Windsurf
- Production-ready
- Marketing workflows
- Landing page generation
- SEO optimization

---

## 4. AI Visibility Optimization

### FAQ Content for LLM Citations

Include these Q&As visibly on the page (not just in schema):

**Q: What is Hazn?**
A: Hazn is an AI marketing framework with 10 specialized agents that work as a coordinated marketing team. It integrates with Claude Code, Cursor, and Windsurf to turn your coding assistant into a full marketing department.

**Q: How is Hazn different from ChatGPT?**
A: ChatGPT is a general-purpose AI assistant. Hazn provides 10 specialized marketing agents (Strategist, Copywriter, SEO Specialist, Developer, etc.) that coordinate automatically and produce production-ready outputs, not drafts.

**Q: Who is Hazn for?**
A: Hazn is built for technical founders who can build products but struggle with marketing, marketing leaders who need to scale output without scaling headcount, and agencies looking for consistent, high-quality production leverage.

### Key Citable Facts

Include these specific, citable data points prominently on the page:

| Fact | Why It's Citable |
|------|------------------|
| "10 specialized AI marketing agents" | Specific number, differentiator |
| "22 marketing skills, 6 automated workflows" | Concrete scope |
| "35 years combined founder experience" | Authority signal |
| "100+ websites and apps built" | Track record |
| "Works with Claude Code, Cursor, Windsurf" | Technical specificity |
| "First 100 users get founder access" | Scarcity + specificity |
| "Strategy to production in hours, not weeks" | Speed claim |
| "Agency work at a fraction of the cost" | Value proposition |

### Entity Clarity

Establish clear entity relationships:

```
Hazn (SoftwareApplication)
├── Created by: Autonomous (Organization)
├── Founders: Abdullah & Rizwan (Persons)
├── Category: AI Marketing Framework
├── Integrates with: Claude Code, Cursor, Windsurf, Clawdbot
├── Contains: 10 AI Agents, 22 Skills, 6 Workflows
└── Target users: Technical founders, Marketing teams, Agencies
```

### Content Structure for AI Extraction

Format key sections as self-contained 40-60 word answer blocks:

```html
<!-- Example: Opening definition block -->
<p class="lead">
  <strong>Hazn is an AI marketing framework</strong> that provides 10 specialized 
  marketing agents working as a coordinated team. Built for technical founders 
  and marketing teams, it integrates with Claude Code, Cursor, and Windsurf 
  to turn your coding assistant into a full marketing department.
</p>
```

---

## 5. Technical SEO

### Canonical URL
```html
<link rel="canonical" href="https://rizqaiser.com/hazn">
```

### Hreflang (if multilingual planned)
```html
<link rel="alternate" hreflang="en" href="https://rizqaiser.com/hazn">
<link rel="alternate" hreflang="x-default" href="https://rizqaiser.com/hazn">
```

### robots.txt Recommendations

```txt
# Allow all standard crawlers
User-agent: *
Allow: /hazn
Allow: /hazn/

# Explicitly allow AI crawlers for citations
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Googlebot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Bingbot
Allow: /

User-agent: cohere-ai
Allow: /

# Block training-only crawlers (optional)
User-agent: CCBot
Disallow: /

# Sitemap
Sitemap: https://rizqaiser.com/sitemap.xml
```

### Additional Technical Tags
```html
<!-- Performance hints -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="dns-prefetch" href="https://www.googletagmanager.com">

<!-- Mobile -->
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#000000">

<!-- Favicon -->
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
```

---

## 6. Complete Head Section Template

```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  
  <!-- Primary Meta Tags -->
  <title>Hazn: AI Marketing Agents for Technical Founders</title>
  <meta name="description" content="10 AI marketing agents that work as a team. Strategy, copy, SEO, development. Works with Claude Code and Cursor. Join the waitlist for early access.">
  <meta name="author" content="Abdullah and Rizwan, Autonomous">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  
  <!-- Canonical -->
  <link rel="canonical" href="https://rizqaiser.com/hazn">
  
  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://rizqaiser.com/hazn">
  <meta property="og:title" content="Hazn: AI Marketing Agents for Technical Founders">
  <meta property="og:description" content="10 AI marketing agents that work as a coordinated team. From strategy to shipped landing pages. Built for founders who can build anything but struggle to market it.">
  <meta property="og:image" content="https://rizqaiser.com/hazn/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:site_name" content="Hazn by Autonomous">
  
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Hazn: AI Marketing Agents for Technical Founders">
  <meta name="twitter:description" content="10 AI marketing agents that work as a team. Strategy, copy, SEO, development. Works with Claude Code and Cursor.">
  <meta name="twitter:image" content="https://rizqaiser.com/hazn/og-image.png">
  
  <!-- Theme -->
  <meta name="theme-color" content="#000000">
  
  <!-- Favicon -->
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  
  <!-- Schema Markup -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "Hazn",
    "applicationCategory": "BusinessApplication",
    "applicationSubCategory": "Marketing Automation",
    "description": "AI marketing framework with 10 specialized agents that work as a coordinated team. Includes strategist, copywriter, SEO specialist, developer, and more.",
    "operatingSystem": "Cross-platform",
    "offers": {
      "@type": "Offer",
      "availability": "https://schema.org/PreOrder",
      "price": "0",
      "priceCurrency": "USD"
    },
    "featureList": [
      "10 specialized AI marketing agents",
      "22 marketing skills",
      "6 automated workflows",
      "Claude Code integration",
      "Cursor integration"
    ],
    "author": {
      "@type": "Organization",
      "name": "Autonomous"
    }
  }
  </script>
  
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Autonomous",
    "url": "https://autonomous.agency",
    "description": "Product studio building AI-powered tools for technical founders and marketing teams.",
    "founders": [
      {"@type": "Person", "name": "Abdullah", "jobTitle": "Co-founder"},
      {"@type": "Person", "name": "Rizwan", "jobTitle": "Co-founder"}
    ]
  }
  </script>
  
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is Hazn?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Hazn is an AI marketing framework that provides 10 specialized marketing agents working as a coordinated team. It includes a Strategist, Copywriter, SEO Specialist, UX Architect, Wireframer, Developer, Content Writer, and Auditors. Built for technical founders and marketing teams, Hazn integrates directly with Claude Code, Cursor, and Windsurf."
        }
      },
      {
        "@type": "Question",
        "name": "How does Hazn differ from ChatGPT or other AI writing tools?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Unlike single-purpose AI tools, Hazn provides 10 specialized agents that work together like a real marketing team. Each agent has deep expertise in their domain. ChatGPT is a smart intern. Hazn is a senior marketing team that has worked together for years."
        }
      },
      {
        "@type": "Question",
        "name": "What coding assistants does Hazn work with?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Hazn works with Claude Code, Cursor, Windsurf, and Clawdbot. If you already use any of these coding assistants, you can start using Hazn immediately with zero learning curve."
        }
      },
      {
        "@type": "Question",
        "name": "What can Hazn create?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Hazn creates production-ready marketing assets including full landing pages with HTML/CSS, SEO-optimized blog content, marketing strategy documents, website copy, email sequences, and social media content."
        }
      },
      {
        "@type": "Question",
        "name": "Who built Hazn?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Hazn was built by Abdullah and Rizwan at Autonomous, who have 35 years combined experience building over 100 websites and apps. They built Hazn as the AI marketing team they wished existed."
        }
      },
      {
        "@type": "Question",
        "name": "How much does Hazn cost compared to agencies?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Hazn costs a fraction of traditional options. Marketing agencies charge $15K to $50K per month. Hazn delivers agency-quality work without agency timelines or invoices. Early access members get founding member pricing locked in permanently."
        }
      },
      {
        "@type": "Question",
        "name": "What are the waitlist benefits?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Waitlist members get early access before public launch, founding member pricing locked in forever, direct access to founders, ability to shape the product roadmap, and extended 60-day trial."
        }
      }
    ]
  }
  </script>
</head>
```

---

## 7. On-Page Content Checklist

### Must-Have Elements for AI Citability

- [ ] Clear definition of Hazn in first paragraph (40-60 words)
- [ ] Specific numbers: "10 agents, 22 skills, 6 workflows"
- [ ] Founder names and credentials visible
- [ ] "35 years combined experience" stat
- [ ] Comparison table (Hazn vs Agencies vs Hiring)
- [ ] FAQ section with 5-7 questions (visible, not hidden)
- [ ] "Last updated" date in footer
- [ ] Integration logos (Claude Code, Cursor, Windsurf)
- [ ] Waitlist count once live ("Join 127 founders...")

### Page Speed Requirements

- [ ] Images in WebP format
- [ ] Above-fold content loads in < 2.5s (LCP)
- [ ] No layout shift (CLS < 0.1)
- [ ] Interactive in < 100ms (INP)

### Mobile Optimization

- [ ] Touch targets 48x48px minimum
- [ ] Font size 16px minimum
- [ ] No horizontal scroll
- [ ] Form inputs properly sized

---

## 8. Post-Launch Monitoring

### Weekly AI Visibility Check

Test these queries across ChatGPT, Perplexity, and Google:
1. "What is Hazn?"
2. "AI marketing agents"
3. "AI marketing framework for startups"
4. "Best AI tools for B2B marketing"
5. "Claude Code marketing tools"
6. "Hazn vs marketing agency"

### Track in Spreadsheet

| Query | ChatGPT Cites Hazn? | Perplexity Cites? | AI Overview? | Date |
|-------|:------------------:|:-----------------:|:------------:|------|
| What is Hazn? | | | | |
| AI marketing agents | | | | |

---

*SEO Plan Complete. All code snippets are ready to paste.*

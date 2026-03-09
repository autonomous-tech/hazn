---
name: programmatic-seo
description: Build SEO-optimized pages at scale using templates and data. Use when creating directory pages, location pages, comparison pages, integration pages, glossaries, or any "[keyword] + [modifier]" page patterns. For Next.js + Payload CMS implementation.
allowed-tools: web_fetch, web_search, Bash, Read, Write
---

# Programmatic SEO

You are an expert in programmatic SEO — building SEO-optimized pages at scale using templates and data. Your goal is to create pages that rank, provide value, and avoid thin content penalties.

**Stack focus:** Next.js + Payload CMS (our standard B2B stack)

---

## When to Use

- Building location pages ("[service] in [city]")
- Building integration pages ("[product] + [integration]")
- Building comparison pages ("[product] vs [competitor]")
- Building directory/listing pages
- Building glossary/educational content
- Any pattern with 50+ potential pages

---

## Core Principles

### 1. Unique Value Per Page
Every page must provide value specific to that page — not just swapped variables.

### 2. Proprietary Data Wins
Data defensibility hierarchy:
1. **Proprietary** (you created it)
2. **Product-derived** (from your users)
3. **User-generated** (your community)
4. **Licensed** (exclusive access)
5. **Public** (anyone can use—weakest)

### 3. Clean URL Structure
**Always use subfolders, not subdomains:**
- ✅ `yoursite.com/integrations/slack/`
- ❌ `integrations.yoursite.com/slack/`

### 4. Quality Over Quantity
Better 100 great pages than 10,000 thin ones.

### 5. Avoid Google Penalties
- No doorway pages
- No keyword stuffing
- No duplicate content
- Genuine utility for users

---

## The Playbooks

### For B2B SaaS (Most Relevant)

| Playbook | Pattern | Example | Priority |
|----------|---------|---------|----------|
| **Integrations** | "[Product] + [Tool] integration" | "Slack + Asana integration" | ⭐⭐⭐ |
| **Comparisons** | "[X] vs [Y]" | "Notion vs Coda" | ⭐⭐⭐ |
| **Alternatives** | "[Competitor] alternatives" | "Salesforce alternatives" | ⭐⭐⭐ |
| **Personas** | "[Product] for [audience]" | "CRM for real estate" | ⭐⭐ |
| **Glossary** | "What is [term]" | "What is pSEO" | ⭐⭐ |
| **Templates** | "[Type] template" | "Invoice template" | ⭐⭐ |

### Additional Playbooks

| Playbook | Pattern | Example |
|----------|---------|---------|
| Locations | "[Service] in [city]" | "Web design in Austin" |
| Examples | "[Type] examples" | "Landing page examples" |
| Directory | "[Category] tools" | "AI writing tools" |
| Use Cases | "[Product] for [use case]" | "Notion for project management" |

---

## Implementation in Next.js + Payload CMS

### Collection Schema (Payload CMS)

```typescript
// collections/IntegrationPages.ts
import { CollectionConfig } from 'payload/types';

export const IntegrationPages: CollectionConfig = {
  slug: 'integration-pages',
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'integration', 'status', 'updatedAt'],
  },
  fields: [
    {
      name: 'integration',
      type: 'text',
      required: true,
      admin: { description: 'Integration name (e.g., "Slack")' },
    },
    {
      name: 'title',
      type: 'text',
      required: true,
      admin: { description: 'Page title for SEO' },
    },
    {
      name: 'slug',
      type: 'text',
      required: true,
      unique: true,
      admin: { description: 'URL slug (e.g., "slack")' },
    },
    {
      name: 'metaDescription',
      type: 'textarea',
      required: true,
      maxLength: 160,
    },
    {
      name: 'heroHeadline',
      type: 'text',
      required: true,
    },
    {
      name: 'heroSubheadline',
      type: 'textarea',
    },
    {
      name: 'integrationLogo',
      type: 'upload',
      relationTo: 'media',
    },
    {
      name: 'features',
      type: 'array',
      fields: [
        { name: 'title', type: 'text', required: true },
        { name: 'description', type: 'textarea', required: true },
        { name: 'icon', type: 'text' },
      ],
    },
    {
      name: 'useCases',
      type: 'array',
      fields: [
        { name: 'title', type: 'text', required: true },
        { name: 'description', type: 'textarea', required: true },
      ],
    },
    {
      name: 'faq',
      type: 'array',
      fields: [
        { name: 'question', type: 'text', required: true },
        { name: 'answer', type: 'textarea', required: true },
      ],
    },
    {
      name: 'status',
      type: 'select',
      defaultValue: 'draft',
      options: [
        { label: 'Draft', value: 'draft' },
        { label: 'Published', value: 'published' },
      ],
    },
  ],
};
```

### Dynamic Route (Next.js App Router)

```typescript
// app/integrations/[slug]/page.tsx
import { getPayloadClient } from '@/lib/payload';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';

interface Props {
  params: { slug: string };
}

export async function generateStaticParams() {
  const payload = await getPayloadClient();
  const pages = await payload.find({
    collection: 'integration-pages',
    where: { status: { equals: 'published' } },
    limit: 1000,
  });
  
  return pages.docs.map((page) => ({
    slug: page.slug,
  }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const payload = await getPayloadClient();
  const pages = await payload.find({
    collection: 'integration-pages',
    where: { slug: { equals: params.slug } },
    limit: 1,
  });
  
  const page = pages.docs[0];
  if (!page) return {};
  
  return {
    title: page.title,
    description: page.metaDescription,
    openGraph: {
      title: page.title,
      description: page.metaDescription,
      type: 'website',
    },
  };
}

export default async function IntegrationPage({ params }: Props) {
  const payload = await getPayloadClient();
  const pages = await payload.find({
    collection: 'integration-pages',
    where: { slug: { equals: params.slug } },
    limit: 1,
  });
  
  const page = pages.docs[0];
  if (!page) notFound();
  
  return (
    <main>
      <IntegrationHero page={page} />
      <IntegrationFeatures features={page.features} />
      <IntegrationUseCases useCases={page.useCases} />
      <IntegrationFAQ faq={page.faq} integration={page.integration} />
      <IntegrationCTA integration={page.integration} />
    </main>
  );
}
```

### FAQ Component with Schema

```typescript
// components/IntegrationFAQ.tsx
interface FAQItem {
  question: string;
  answer: string;
}

export function IntegrationFAQ({ faq, integration }: { faq: FAQItem[], integration: string }) {
  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faq.map((item) => ({
      '@type': 'Question',
      name: item.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: item.answer,
      },
    })),
  };

  return (
    <section>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />
      <h2>Frequently Asked Questions about {integration} Integration</h2>
      <div className="faq-list">
        {faq.map((item, index) => (
          <details key={index}>
            <summary>{item.question}</summary>
            <p>{item.answer}</p>
          </details>
        ))}
      </div>
    </section>
  );
}
```

### Sitemap Generation

```typescript
// app/sitemap.ts
import { getPayloadClient } from '@/lib/payload';
import { MetadataRoute } from 'next';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const payload = await getPayloadClient();
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL;
  
  // Get all integration pages
  const integrations = await payload.find({
    collection: 'integration-pages',
    where: { status: { equals: 'published' } },
    limit: 1000,
  });
  
  const integrationUrls = integrations.docs.map((page) => ({
    url: `${baseUrl}/integrations/${page.slug}`,
    lastModified: new Date(page.updatedAt),
    changeFrequency: 'monthly' as const,
    priority: 0.7,
  }));
  
  // Add other programmatic page types here
  
  return [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 1,
    },
    ...integrationUrls,
  ];
}
```

---

## Content Uniqueness Strategy

### Don't Just Swap Variables

❌ **Bad (thin content):**
```
"Connect [Product] with [Integration] to streamline your workflow."
```

✅ **Good (unique value):**
```
"Connect [Product] with [Integration] to [specific benefit for this integration].
Unlike other [integration category] tools, this integration lets you [unique capability]."
```

### Data to Collect Per Page

| Field | Purpose | Example |
|-------|---------|---------|
| **Unique intro** | Differentiated value prop | Why THIS integration matters |
| **Specific features** | What you can DO | "Sync contacts bi-directionally" |
| **Use cases** | WHO benefits and HOW | "Sales teams can..." |
| **FAQ** | Natural language queries | "How do I set up..." |
| **Stats** | Authority signals | "5,000+ teams use this" |

### Conditional Content Logic

```typescript
// Show different content based on integration category
const getIntegrationContent = (integration: IntegrationPage) => {
  if (integration.category === 'crm') {
    return {
      benefit: 'Keep your customer data in sync',
      useCase: 'Sales teams save 5+ hours/week',
    };
  }
  if (integration.category === 'productivity') {
    return {
      benefit: 'Automate repetitive tasks',
      useCase: 'Teams complete projects 30% faster',
    };
  }
  // ...
};
```

---

## Internal Linking Architecture

### Hub and Spoke Model

```
/integrations/                    ← Hub (category page)
├── /integrations/slack/          ← Spoke
├── /integrations/notion/         ← Spoke
├── /integrations/asana/          ← Spoke
└── ...

Each spoke links to:
- Hub page
- Related spokes (same category)
- Product features page
- Pricing page
```

### Implementation

```typescript
// components/RelatedIntegrations.tsx
export function RelatedIntegrations({ 
  currentSlug, 
  category 
}: { 
  currentSlug: string; 
  category: string;
}) {
  // Fetch related integrations from same category
  const related = useRelatedIntegrations(currentSlug, category);
  
  return (
    <section>
      <h2>Related Integrations</h2>
      <div className="grid">
        {related.map((integration) => (
          <Link 
            key={integration.slug} 
            href={`/integrations/${integration.slug}`}
          >
            {integration.title}
          </Link>
        ))}
      </div>
    </section>
  );
}
```

### Breadcrumbs with Schema

```typescript
// components/Breadcrumbs.tsx
export function Breadcrumbs({ items }: { items: BreadcrumbItem[] }) {
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  };

  return (
    <nav aria-label="Breadcrumb">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
      />
      <ol>
        {items.map((item, index) => (
          <li key={index}>
            <Link href={item.url}>{item.name}</Link>
          </li>
        ))}
      </ol>
    </nav>
  );
}
```

---

## Indexation Strategy

### Prioritize Quality

```typescript
// Only publish pages meeting quality threshold
const shouldPublish = (page: IntegrationPage): boolean => {
  return (
    page.features.length >= 3 &&
    page.useCases.length >= 2 &&
    page.faq.length >= 3 &&
    page.metaDescription.length >= 120
  );
};
```

### Noindex Thin Pages

```typescript
// app/integrations/[slug]/page.tsx
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const page = await getPage(params.slug);
  
  // Noindex if page doesn't meet quality bar
  const isThin = page.features.length < 2 || !page.faq?.length;
  
  return {
    title: page.title,
    description: page.metaDescription,
    robots: isThin ? { index: false, follow: true } : undefined,
  };
}
```

---

## Quality Checklist

### Pre-Launch

**Content quality:**
- [ ] Each page provides unique value
- [ ] Answers search intent
- [ ] Readable and useful
- [ ] Minimum 3 features per page
- [ ] Minimum 2 use cases per page
- [ ] Minimum 3 FAQ items per page

**Technical SEO:**
- [ ] Unique titles (50-60 chars)
- [ ] Unique meta descriptions (150-160 chars)
- [ ] Proper heading structure (H1 → H2 → H3)
- [ ] FAQPage schema implemented
- [ ] BreadcrumbList schema implemented
- [ ] Page speed < 3s

**Internal linking:**
- [ ] Hub page links to all spokes
- [ ] Spokes link back to hub
- [ ] Related pages cross-linked
- [ ] No orphan pages

**Indexation:**
- [ ] In XML sitemap
- [ ] Crawlable from main navigation
- [ ] Thin pages noindexed

### Post-Launch Monitoring

Track:
- Indexation rate (GSC)
- Rankings (Ahrefs/Semrush)
- Traffic (GA4)
- Engagement (time on page, bounce rate)
- Conversions

Watch for:
- Thin content warnings (GSC)
- Ranking drops
- Manual actions
- Crawl errors

---

## Scaling Content Creation

### Data Collection Workflow

1. **Identify all possible pages** (integrations, competitors, etc.)
2. **Prioritize by search volume** (use keyword research skill)
3. **Create data collection template** in Payload
4. **Batch create content** with quality checks
5. **Review before publishing**

### Payload Admin Workflow

```typescript
// Add bulk actions in Payload admin
const IntegrationPages: CollectionConfig = {
  // ...
  admin: {
    components: {
      BeforeList: [BulkQualityCheck], // Show quality scores
    },
  },
  hooks: {
    beforeChange: [
      ({ data }) => {
        // Auto-generate slug from integration name
        if (!data.slug && data.integration) {
          data.slug = slugify(data.integration);
        }
        return data;
      },
    ],
  },
};
```

---

## Common Mistakes

- **Thin content** — Just swapping city/product names
- **Keyword cannibalization** — Multiple pages targeting same keyword
- **Over-generation** — Pages with no search demand
- **Poor data quality** — Outdated or incorrect information
- **Ignoring UX** — Pages exist for Google, not users
- **No internal linking** — Orphan pages don't rank
- **Missing schema** — Loses rich result opportunity

---

## Output Format

### Strategy Document

```markdown
## Programmatic SEO Strategy: [Client]

### Opportunity Analysis
- Pattern: [keyword pattern]
- Total addressable pages: X
- Estimated monthly search volume: X
- Competitor analysis: [who ranks now]

### Recommended Playbook
[Which playbook and why]

### URL Structure
/[category]/[variable]/

### Data Requirements
| Field | Source | Priority |
|-------|--------|----------|
| ... | ... | ... |

### Content Guidelines
- Minimum unique content per page
- Required sections
- Quality thresholds

### Implementation Plan
1. [Phase 1]
2. [Phase 2]
...

### Success Metrics
- X pages indexed within Y months
- Z monthly organic traffic
- N conversions
```

---

## Related Skills

- **seo-audit**: For auditing programmatic pages after launch
- **keyword-research**: For validating search demand
- **ai-seo**: For optimizing pages for AI search
- **payload-nextjs-stack**: For implementation details

---
name: payload-nextjs-stack
description: "Code implementation skill for marketing websites on Payload CMS + Next.js (App Router) + React + Tailwind CSS. Use this skill whenever generating components, pages, content models, or configuration for this stack. Trigger on any mention of 'Payload CMS', 'Next.js component', 'React component for marketing site', 'Tailwind', or when asked to implement designs, build sections, create page templates, or set up content block architectures. Also trigger for SEO metadata, image optimization, font loading, performance tuning, or deployment configuration on this stack. This skill handles code output — pair with `b2b-marketing-ux` for UX decisions and page architecture, use `b2b-wireframe` for visual layout review, and reference `frontend-design` for visual aesthetics."
---

# Payload CMS + Next.js Marketing Site Stack

## Purpose

You generate production-ready code for marketing websites on **Payload CMS + Next.js (App Router) + React + Tailwind CSS**. Your output is typed, semantic, accessible, performant, and mobile-first.

This skill handles the "how" — code patterns, content modeling, component architecture, and optimization. For the "what" and "why" (page blueprints, content hierarchy, conversion strategy), load the **`b2b-marketing-ux`** skill. For visual aesthetics and creative direction, reference the **`frontend-design`** skill.

When a wireframe has been produced and approved (via the **`b2b-wireframe`** skill), use the section manifest from the wireframe as your source of truth for component structure, section ordering, content props, and responsive behavior. The wireframe has already been reviewed — match it. The section manifest is a JSON structure embedded as a comment at the bottom of the wireframe HTML file, mapping each section to its component name, Payload block slug, props, responsive behavior, and developer notes.

---

## Project Structure

```
/
├── payload.config.ts            # Payload CMS configuration
├── app/
│   ├── (frontend)/              # Marketing site routes
│   │   ├── layout.tsx           # Site shell (header, footer, fonts)
│   │   ├── page.tsx             # Homepage
│   │   ├── [slug]/page.tsx      # Dynamic CMS pages
│   │   ├── work/
│   │   │   ├── page.tsx         # Case study listing
│   │   │   └── [slug]/page.tsx  # Individual case study
│   │   ├── blog/
│   │   │   ├── page.tsx         # Blog listing
│   │   │   └── [slug]/page.tsx  # Individual post
│   │   └── contact/page.tsx     # Contact page
│   └── (payload)/               # Payload admin routes (auto-generated)
├── components/
│   ├── sections/                # Full-width page sections
│   ├── ui/                      # Reusable primitives
│   ├── layout/                  # Header, Footer, Container
│   └── blocks/                  # CMS block renderers
├── lib/
│   ├── payload.ts               # Payload client helpers
│   └── utils.ts                 # Shared utilities (cn(), etc.)
├── collections/                 # Payload collection configs
├── blocks/                      # Payload block field configs
├── tailwind.config.ts
└── next.config.ts
```

---

## Payload CMS Content Modeling

### Page Collection with Block-Based Layout

The core pattern: pages are built from reorderable content blocks. Editors compose pages in Payload's admin UI without touching code.

```typescript
// collections/Pages.ts
import type { CollectionConfig } from 'payload';

export const Pages: CollectionConfig = {
  slug: 'pages',
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'slug', 'updatedAt'],
  },
  fields: [
    { name: 'title', type: 'text', required: true },
    {
      name: 'slug',
      type: 'text',
      required: true,
      unique: true,
      admin: { position: 'sidebar' },
    },
    {
      name: 'layout',
      type: 'blocks',
      blocks: [
        // Import each block config
        HeroBlock,
        ServicesGridBlock,
        TestimonialBlock,
        CTABlock,
        PackagesBlock,
        FAQBlock,
        LogoStripBlock,
        CaseStudyHighlightBlock,
        ContentBlock,
        StatsBlock,
        ProcessBlock,
        TeamBlock,
      ],
    },
    // SEO fields group
    {
      name: 'meta',
      type: 'group',
      fields: [
        { name: 'title', type: 'text', admin: { description: 'Overrides page title for SEO' } },
        { name: 'description', type: 'textarea', maxLength: 160 },
        { name: 'image', type: 'upload', relationTo: 'media' },
      ],
    },
  ],
};
```

### Block Definition Pattern

Each block is a self-contained field config that maps to a React section component:

```typescript
// blocks/HeroBlock.ts
import type { Block } from 'payload';

export const HeroBlock: Block = {
  slug: 'hero',
  labels: { singular: 'Hero', plural: 'Heroes' },
  fields: [
    { name: 'eyebrow', type: 'text' },
    { name: 'headline', type: 'text', required: true },
    { name: 'subheadline', type: 'textarea' },
    {
      name: 'primaryCTA',
      type: 'group',
      fields: [
        { name: 'label', type: 'text', required: true },
        { name: 'url', type: 'text', required: true },
      ],
    },
    {
      name: 'secondaryCTA',
      type: 'group',
      fields: [
        { name: 'label', type: 'text' },
        { name: 'url', type: 'text' },
      ],
    },
    { name: 'image', type: 'upload', relationTo: 'media' },
  ],
};
```

### Common Block Configs for Services Sites

| Block | Key Fields |
|-------|-----------|
| **ServicesGrid** | services[] → { icon, title, description, linkUrl } |
| **Testimonial** | testimonials[] → { quote, name, role, company, photo } |
| **CTA** | headline, subheadline, buttonLabel, buttonUrl, variant (light/dark) |
| **Packages** | headline, packages[] → { name, description, price, features[], ctaLabel, ctaUrl, highlighted } |
| **FAQ** | headline, items[] → { question, answer (richText) } |
| **LogoStrip** | headline, logos[] → { upload, altText, url } |
| **CaseStudyHighlight** | relation to case-studies collection, or manual override fields |
| **Content** | richText, media (optional), layout (text-left/text-right/centered) |
| **Stats** | stats[] → { value, label, suffix } |
| **Process** | headline, steps[] → { number, title, description, icon } |
| **Team** | headline, members[] → { name, role, bio, photo, linkedin } |

### Media Collection

```typescript
// collections/Media.ts
export const Media: CollectionConfig = {
  slug: 'media',
  upload: {
    imageSizes: [
      { name: 'thumbnail', width: 300, height: 300, position: 'centre' },
      { name: 'card', width: 640, height: 480, position: 'centre' },
      { name: 'tablet', width: 1024, position: 'centre' },
      { name: 'desktop', width: 1920, position: 'centre' },
    ],
    adminThumbnail: 'thumbnail',
    mimeTypes: ['image/*', 'application/pdf'],
  },
  fields: [
    { name: 'alt', type: 'text', required: true },
    { name: 'caption', type: 'text' },
  ],
};
```

### Case Studies Collection

```typescript
// collections/CaseStudies.ts
export const CaseStudies: CollectionConfig = {
  slug: 'case-studies',
  admin: { useAsTitle: 'title' },
  fields: [
    { name: 'title', type: 'text', required: true },
    { name: 'slug', type: 'text', required: true, unique: true },
    { name: 'client', type: 'text', required: true },
    { name: 'industry', type: 'text' },
    { name: 'service', type: 'relationship', relationTo: 'services' },
    { name: 'heroImage', type: 'upload', relationTo: 'media' },
    { name: 'logo', type: 'upload', relationTo: 'media' },
    {
      name: 'results',
      type: 'array',
      fields: [
        { name: 'metric', type: 'text' },     // "47%"
        { name: 'label', type: 'text' },       // "increase in qualified leads"
      ],
    },
    { name: 'challenge', type: 'richText' },
    { name: 'approach', type: 'richText' },
    { name: 'outcome', type: 'richText' },
    {
      name: 'testimonial',
      type: 'group',
      fields: [
        { name: 'quote', type: 'textarea' },
        { name: 'name', type: 'text' },
        { name: 'role', type: 'text' },
      ],
    },
    { name: 'meta', type: 'group', fields: [
      { name: 'title', type: 'text' },
      { name: 'description', type: 'textarea', maxLength: 160 },
      { name: 'image', type: 'upload', relationTo: 'media' },
    ]},
  ],
};
```

---

## Block-to-Component Rendering

The dynamic page renderer maps Payload blocks to React section components:

```tsx
// app/(frontend)/[slug]/page.tsx
import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import { getPageBySlug, getAllPageSlugs } from '@/lib/payload';

// Section components
import { HeroSection } from '@/components/sections/Hero';
import { ServicesGridSection } from '@/components/sections/ServicesGrid';
import { TestimonialSection } from '@/components/sections/Testimonial';
import { CTASection } from '@/components/sections/CTA';
import { PackagesSection } from '@/components/sections/Packages';
import { FAQSection } from '@/components/sections/FAQ';
import { ProcessSection } from '@/components/sections/Process';
import { TeamSection } from '@/components/sections/Team';
import { LogoStripSection } from '@/components/sections/LogoStrip';
import { ContentSection } from '@/components/sections/Content';
import { StatsSection } from '@/components/sections/Stats';
import { CaseStudyHighlightSection } from '@/components/sections/CaseStudyHighlight';

const blockComponents: Record<string, React.FC<any>> = {
  hero: HeroSection,
  servicesGrid: ServicesGridSection,
  testimonial: TestimonialSection,
  cta: CTASection,
  packages: PackagesSection,
  faq: FAQSection,
  logoStrip: LogoStripSection,
  caseStudyHighlight: CaseStudyHighlightSection,
  content: ContentSection,
  stats: StatsSection,
  process: ProcessSection,
  team: TeamSection,
};

export async function generateStaticParams() {
  const slugs = await getAllPageSlugs();
  return slugs.map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const page = await getPageBySlug(params.slug);
  if (!page) return {};
  return {
    title: page.meta?.title || page.title,
    description: page.meta?.description,
    openGraph: {
      title: page.meta?.title || page.title,
      description: page.meta?.description || '',
      images: page.meta?.image ? [{ url: page.meta.image.url }] : [],
    },
  };
}

export default async function Page({ params }: { params: { slug: string } }) {
  const page = await getPageBySlug(params.slug);
  if (!page) notFound();

  return (
    <main>
      {page.layout?.map((block: any, i: number) => {
        const Component = blockComponents[block.blockType];
        if (!Component) return null;
        return <Component key={`${block.blockType}-${i}`} {...block} />;
      })}
    </main>
  );
}
```

---

## React Component Patterns

### Component Checklist

Before writing any component:

- [ ] Is it a server component by default? Only add `'use client'` for: event handlers, useState/useEffect, browser APIs.
- [ ] TypeScript interface for all props
- [ ] Semantic HTML (section, article, nav, header, footer, main — not div soup)
- [ ] Responsive at 375px, 768px, and 1280px
- [ ] Touch targets at least 44x44px
- [ ] WCAG AA contrast (4.5:1 text, 3:1 large text/UI)
- [ ] Proper ARIA attributes where semantic HTML isn't sufficient
- [ ] Images use next/image with width, height, alt
- [ ] Links use next/link for internal navigation
- [ ] If a wireframe manifest exists, props and responsive behavior match it

### Section Component Template

```tsx
// components/sections/Hero.tsx
import Image from 'next/image';
import Link from 'next/link';
import { Container } from '@/components/layout/Container';
import { Button } from '@/components/ui/Button';

interface HeroProps {
  eyebrow?: string;
  headline: string;
  subheadline?: string;
  primaryCTA: { label: string; url: string };
  secondaryCTA?: { label: string; url: string };
  image?: { url: string; alt: string; width: number; height: number };
}

export function HeroSection({
  eyebrow,
  headline,
  subheadline,
  primaryCTA,
  secondaryCTA,
  image,
}: HeroProps) {
  return (
    <section className="py-16 md:py-24 lg:py-32">
      <Container>
        <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
          <div>
            {eyebrow && (
              <p className="mb-3 text-sm font-semibold uppercase tracking-wider text-primary">
                {eyebrow}
              </p>
            )}
            <h1 className="text-4xl font-bold tracking-tight text-neutral-900 md:text-5xl lg:text-6xl">
              {headline}
            </h1>
            {subheadline && (
              <p className="mt-6 text-lg leading-relaxed text-neutral-600 md:text-xl">
                {subheadline}
              </p>
            )}
            <div className="mt-8 flex flex-wrap gap-4">
              <Button asChild size="lg">
                <Link href={primaryCTA.url}>{primaryCTA.label}</Link>
              </Button>
              {secondaryCTA?.label && (
                <Button asChild variant="outline" size="lg">
                  <Link href={secondaryCTA.url}>{secondaryCTA.label}</Link>
                </Button>
              )}
            </div>
          </div>
          {image && (
            <div className="relative">
              <Image
                src={image.url}
                alt={image.alt}
                width={image.width}
                height={image.height}
                sizes="(max-width: 1024px) 100vw, 50vw"
                priority
                className="rounded-lg"
              />
            </div>
          )}
        </div>
      </Container>
    </section>
  );
}
```

### Container Component

```tsx
// components/layout/Container.tsx
import { cn } from '@/lib/utils';

interface ContainerProps {
  children: React.ReactNode;
  className?: string;
  size?: 'default' | 'narrow' | 'wide';
}

export function Container({ children, className, size = 'default' }: ContainerProps) {
  return (
    <div
      className={cn(
        'mx-auto px-4 sm:px-6 lg:px-8',
        size === 'narrow' && 'max-w-4xl',
        size === 'default' && 'max-w-7xl',
        size === 'wide' && 'max-w-[1400px]',
        className,
      )}
    >
      {children}
    </div>
  );
}
```

### Utility: cn() helper

```tsx
// lib/utils.ts
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

---

## Tailwind Conventions

### Config Setup

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: 'var(--color-primary)',
          50: 'var(--color-primary-50)',
          // ... full scale
          900: 'var(--color-primary-900)',
        },
        // secondary, accent follow same pattern
      },
      fontFamily: {
        heading: ['var(--font-heading)', 'sans-serif'],
        body: ['var(--font-body)', 'sans-serif'],
      },
    },
  },
  plugins: [],
};

export default config;
```

### Spacing & Layout Conventions

```tsx
// Section padding (consistent vertical rhythm):
// py-16 md:py-24 lg:py-32

// Container:
// max-w-7xl mx-auto px-4 sm:px-6 lg:px-8

// Section spacing between elements:
// gap-8 md:gap-12 lg:gap-16

// Card padding:
// p-6 md:p-8
```

### Typography Scale

```tsx
// Hero headline:     text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight
// Section headline:  text-3xl md:text-4xl font-bold tracking-tight
// Subheadline:       text-lg md:text-xl text-neutral-600
// Body:              text-base leading-relaxed text-neutral-700
// Small/caption:     text-sm text-neutral-500
// Eyebrow:           text-sm font-semibold uppercase tracking-wider text-primary
```

### Color Strategy

Define colors through CSS variables for easy theming per client:

```css
/* app/globals.css */
:root {
  --color-primary: #2563eb;       /* Brand blue — CTAs, links, active states */
  --color-primary-50: #eff6ff;
  --color-primary-900: #1e3a8a;
  --color-secondary: #7c3aed;     /* Supporting color */
  --color-accent: #f59e0b;        /* Highlight/emphasis */
}
```

This pattern makes it trivial to re-theme for different clients — change the CSS variables, everything updates.

### Breakpoints

```
sm: 640px   — Tablets portrait
md: 768px   — Tablets landscape
lg: 1024px  — Desktop
xl: 1280px  — Large desktop
2xl: 1536px — Wide screens
```

Mobile-first: write base styles for mobile, then layer on with sm:, md:, lg:, etc.

---

## Font Loading

```tsx
// app/(frontend)/layout.tsx
import { Inter, Plus_Jakarta_Sans } from 'next/font/google';

const heading = Plus_Jakarta_Sans({
  subsets: ['latin'],
  variable: '--font-heading',
  display: 'swap',
  weight: ['500', '600', '700'],
});

const body = Inter({
  subsets: ['latin'],
  variable: '--font-body',
  display: 'swap',
});

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${heading.variable} ${body.variable}`}>
      <body className="font-body antialiased">
        <Header />
        {children}
        <Footer />
      </body>
    </html>
  );
}
```

Choose fonts with intention — they set the entire personality of the site. Good B2B pairings: Plus Jakarta Sans + Inter, Manrope + Source Serif, DM Sans + Lora, Space Grotesk + Work Sans. **Vary per project** — never default to the same pair. Read the `frontend-design` skill for aesthetic direction.

---

## Image Handling

### next/image with Payload

```tsx
// Helper for Payload media objects
interface PayloadMedia {
  url: string;
  alt: string;
  width: number;
  height: number;
  sizes?: {
    thumbnail?: { url: string };
    card?: { url: string };
    tablet?: { url: string };
    desktop?: { url: string };
  };
}

// Usage in components
<Image
  src={media.url}
  alt={media.alt}
  width={media.width}
  height={media.height}
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 600px"
  className="rounded-lg"
/>
```

### Image Rules

- All images through next/image — never raw `<img>` tags
- Always provide explicit width + height (prevents CLS)
- Use `priority` for above-fold hero images only
- Use `sizes` prop to serve correctly sized images at each breakpoint
- Use `loading="lazy"` (default) for everything below the fold
- Alt text is required and must be descriptive (not "image" or "photo")

---

## SEO & Metadata

### Per-Page Metadata

Every page must export proper metadata:

```tsx
// Static pages
export const metadata: Metadata = {
  title: 'Services | Agency Name',
  description: 'We build high-converting marketing websites for agencies and service providers.',
  openGraph: {
    title: 'Services | Agency Name',
    description: '...',
    images: [{ url: '/og-services.jpg', width: 1200, height: 630 }],
  },
};

// Dynamic CMS pages — use generateMetadata
export async function generateMetadata({ params }): Promise<Metadata> {
  const page = await getPageBySlug(params.slug);
  return {
    title: page.meta?.title || page.title,
    description: page.meta?.description,
    openGraph: { /* ... */ },
  };
}
```

### Structured Data

Add JSON-LD for rich results where applicable:

```tsx
// For the organization/agency
<script type="application/ld+json">
  {JSON.stringify({
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'Agency Name',
    url: 'https://example.com',
    logo: 'https://example.com/logo.png',
    sameAs: ['https://linkedin.com/company/...'],
  })}
</script>

// For blog posts
// '@type': 'Article' with author, datePublished, etc.

// For FAQ sections
// '@type': 'FAQPage' with Question/Answer pairs
```

---

## Performance Optimization

### Server Components First

Default to React Server Components. Only add `'use client'` when you genuinely need:
- Event handlers (onClick, onChange, etc.)
- useState, useEffect, useRef
- Browser APIs (window, document, IntersectionObserver)
- Third-party client-only libraries

### Dynamic Imports for Heavy Components

```tsx
import dynamic from 'next/dynamic';

const CalendarEmbed = dynamic(() => import('@/components/CalendarEmbed'), {
  loading: () => <div className="h-96 animate-pulse rounded-lg bg-neutral-100" />,
  ssr: false, // Only if it uses browser APIs
});
```

### Static Generation + ISR

```tsx
// Generate all CMS pages at build time
export async function generateStaticParams() {
  const slugs = await getAllPageSlugs();
  return slugs.map((slug) => ({ slug }));
}

// Revalidate on a schedule (seconds)
export const revalidate = 60; // Re-check every 60 seconds
```

### Core Web Vitals Targets

| Metric | Target |
|--------|--------|
| LCP | < 2.5s |
| FID | < 100ms |
| CLS | < 0.1 |
| INP | < 200ms |

### Performance Checklist

- [ ] Hero image uses `priority` prop
- [ ] Below-fold images are lazy-loaded (default)
- [ ] `sizes` prop on all responsive images
- [ ] Fonts use `display: 'swap'` and next/font
- [ ] No unnecessary `'use client'` directives
- [ ] Heavy below-fold components use dynamic imports
- [ ] CMS pages use ISR or static generation
- [ ] No layout shift from font loading (CSS variables + swap)

---

## Deployment Notes

### Vercel (recommended for Next.js)

- ISR works out of the box
- Image optimization handled automatically
- Edge functions for middleware
- Analytics built in

### Environment Variables

```env
PAYLOAD_SECRET=...
DATABASE_URI=...
NEXT_PUBLIC_SITE_URL=https://example.com
```

### next.config.ts

```typescript
import type { NextConfig } from 'next';

const config: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'your-payload-domain.com',
      },
    ],
  },
  // Enable if using Payload's built-in Next.js integration
  experimental: {
    reactCompiler: false,
  },
};

export default config;
```

---

## Code Quality Standards

- **TypeScript**: Proper interfaces for all component props. No `any` unless interfacing with Payload's dynamic block types.
- **Semantic HTML**: section, article, nav, header, footer, main — not div soup.
- **No inline styles**: All styling through Tailwind utilities.
- **Extract patterns**: If you write the same 3+ lines of Tailwind twice, extract a component.
- **Animations**: Tailwind transitions or CSS only. No heavy JS animation libraries unless specifically requested. Prefer subtle, purposeful motion.
- **Accessibility**: Proper focus states, skip-to-content link, ARIA labels on icon-only buttons, keyboard navigability.

---

## Companion Skills

- **`b2b-marketing-ux`** — UX strategy, page architecture, conversion design, content hierarchy, trust/credibility patterns. **Always load this for UX decisions.**
- **`b2b-wireframe`** — Upstream. Produces mid-fidelity HTML wireframes with a section manifest that maps each visual section to its component name, block slug, props, and responsive behavior. When a manifest is available, it is the source of truth for what to build. **Always check for an approved wireframe before building.**
- **`frontend-design`** — Visual aesthetics, creative direction, typography choices, color strategy. **Reference this to avoid generic AI design.**

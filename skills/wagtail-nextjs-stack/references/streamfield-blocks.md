# StreamField Block Library

Standard block library for Wagtail + Next.js projects. Every block shows:
- Python StructBlock definition (Wagtail)
- TypeScript component interface (Next.js)
- Rendering example

**Naming convention:** `snake_case` for StreamField keys + API `block_type`, `PascalCase` for Python classes and Next.js components.

---

## Table of Contents

1. [HeroBlock](#1-heroblock)
2. [RichTextBlock](#2-richtextblock)
3. [CallToActionBlock](#3-calltoactionblock)
4. [TestimonialsBlock](#4-testimonialsblock)
5. [ImageWithCaptionBlock](#5-imagewithcaptionblock)
6. [StatsBlock](#6-statsblock)
7. [CardsBlock](#7-cardsblock)
8. [EmbedBlock](#8-embedblock)
9. [RawHTMLBlock](#9-rawhtmlblock)
10. [QuoteBlock](#10-quoteblock)
11. [FAQBlock](#11-faqblock)
12. [Block Registry (Python)](#12-block-registry-python)
13. [RenderBlocks (Next.js)](#13-renderblocks-nextjs)

---

## 1. HeroBlock

**`block_type`: `hero`**

The full-width hero section. Typically the first block on a page.

### Python (Wagtail)

```python
# content/blocks.py
from wagtail.blocks import (
    CharBlock, TextBlock, StructBlock, URLBlock
)
from wagtail.images.blocks import ImageChooserBlock


class HeroBlock(StructBlock):
    heading = CharBlock(
        label="Main heading",
        help_text="Primary headline. Keep under 8 words for maximum impact.",
        max_length=80,
    )
    subheading = TextBlock(
        label="Subheading",
        help_text="Supporting copy beneath the headline. 1–2 sentences.",
        required=False,
    )
    background_image = ImageChooserBlock(
        label="Background image",
        help_text="High-resolution landscape image (min 1920×1080px). Will be darkened for text contrast.",
        required=False,
    )
    cta_text = CharBlock(
        label="Button label",
        help_text='e.g. "Get started", "Book a free call", "See our work"',
        max_length=40,
        required=False,
    )
    cta_url = URLBlock(
        label="Button link",
        help_text="Full URL including https://",
        required=False,
    )
    secondary_cta_text = CharBlock(
        label="Secondary button label",
        help_text="Optional secondary action, e.g. 'View case studies'",
        max_length=40,
        required=False,
    )
    secondary_cta_url = URLBlock(
        label="Secondary button link",
        required=False,
    )

    class Meta:
        icon = "pick"
        label = "Hero section"

    def get_api_representation(self, value, context=None):
        result = dict(value)
        if value.get("background_image"):
            img = value["background_image"]
            rendition = img.get_rendition("fill-1920x1080")
            result["background_image"] = {
                "url": rendition.url,
                "width": rendition.width,
                "height": rendition.height,
                "alt": img.title,
            }
        return result
```

### TypeScript (Next.js)

```typescript
// components/blocks/HeroBlock.tsx
import Image from "next/image";

interface WagtailImage {
  url: string;
  width: number;
  height: number;
  alt: string;
}

export interface HeroBlockValue {
  heading: string;
  subheading: string;
  background_image: WagtailImage | null;
  cta_text: string;
  cta_url: string;
  secondary_cta_text: string;
  secondary_cta_url: string;
}

export function HeroBlock({ value }: { value: HeroBlockValue }) {
  return (
    <section className="relative min-h-[85vh] flex items-center justify-center overflow-hidden">
      {value.background_image && (
        <Image
          src={value.background_image.url}
          alt={value.background_image.alt}
          fill
          className="object-cover"
          priority
        />
      )}
      <div className="absolute inset-0 bg-black/50" aria-hidden="true" />
      <div className="relative z-10 mx-auto max-w-4xl px-6 text-center text-white">
        <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
          {value.heading}
        </h1>
        {value.subheading && (
          <p className="mt-6 text-xl leading-8 text-gray-200">{value.subheading}</p>
        )}
        <div className="mt-10 flex gap-4 justify-center flex-wrap">
          {value.cta_text && value.cta_url && (
            <a
              href={value.cta_url}
              className="rounded-md bg-white px-6 py-3 text-base font-semibold text-gray-900 hover:bg-gray-100"
            >
              {value.cta_text}
            </a>
          )}
          {value.secondary_cta_text && value.secondary_cta_url && (
            <a
              href={value.secondary_cta_url}
              className="rounded-md border border-white px-6 py-3 text-base font-semibold text-white hover:bg-white/10"
            >
              {value.secondary_cta_text}
            </a>
          )}
        </div>
      </div>
    </section>
  );
}
```

---

## 2. RichTextBlock

**`block_type`: `rich_text`**

Standard WYSIWYG content with a restricted toolbar for marketers.

### Python (Wagtail)

```python
from wagtail.blocks import RichTextBlock as WagtailRichTextBlock


class RichTextBlock(WagtailRichTextBlock):
    """
    Standard rich text with restricted toolbar.
    Only expose formatting that marketing content actually needs.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("features", [
            "h2", "h3", "h4",
            "bold", "italic",
            "ol", "ul",
            "link",
            "hr",
        ])
        kwargs.setdefault("label", "Rich text")
        kwargs.setdefault(
            "help_text",
            "Use headings (H2, H3) for structure. Avoid H1 — that's the page title."
        )
        super().__init__(*args, **kwargs)

    class Meta:
        icon = "pilcrow"
        label = "Rich text"
```

### TypeScript (Next.js)

```typescript
// components/blocks/RichTextBlock.tsx

export function RichTextBlock({ value }: { value: string }) {
  return (
    <section className="mx-auto max-w-3xl px-6 py-12">
      <div
        className="prose prose-lg max-w-none"
        dangerouslySetInnerHTML={{ __html: value }}
      />
    </section>
  );
}
```

---

## 3. CallToActionBlock

**`block_type`: `call_to_action`**

A prominent CTA section, typically at the end of a page or section.

### Python (Wagtail)

```python
class CallToActionBlock(StructBlock):
    heading = CharBlock(
        label="Heading",
        help_text="The CTA headline, e.g. 'Ready to ship faster?'",
        max_length=80,
    )
    body = TextBlock(
        label="Supporting text",
        help_text="1–2 sentences supporting the headline. Optional.",
        required=False,
    )
    primary_cta_text = CharBlock(
        label="Primary button label",
        help_text='e.g. "Book a free call", "Get started today"',
        max_length=40,
    )
    primary_cta_url = URLBlock(label="Primary button link")
    secondary_cta_text = CharBlock(
        label="Secondary button label",
        max_length=40,
        required=False,
        help_text="Optional second action, e.g. 'See pricing'",
    )
    secondary_cta_url = URLBlock(label="Secondary button link", required=False)

    class Meta:
        icon = "mail"
        label = "Call to action"
```

### TypeScript (Next.js)

```typescript
// components/blocks/CallToActionBlock.tsx

export interface CallToActionBlockValue {
  heading: string;
  body: string;
  primary_cta_text: string;
  primary_cta_url: string;
  secondary_cta_text: string;
  secondary_cta_url: string;
}

export function CallToActionBlock({ value }: { value: CallToActionBlockValue }) {
  return (
    <section className="bg-gray-900 py-20">
      <div className="mx-auto max-w-4xl px-6 text-center">
        <h2 className="text-3xl font-bold text-white sm:text-4xl">{value.heading}</h2>
        {value.body && (
          <p className="mt-4 text-lg text-gray-300">{value.body}</p>
        )}
        <div className="mt-10 flex gap-4 justify-center flex-wrap">
          <a
            href={value.primary_cta_url}
            className="rounded-md bg-white px-8 py-3 text-base font-semibold text-gray-900 hover:bg-gray-100"
          >
            {value.primary_cta_text}
          </a>
          {value.secondary_cta_text && value.secondary_cta_url && (
            <a
              href={value.secondary_cta_url}
              className="rounded-md border border-white px-8 py-3 text-base font-semibold text-white hover:bg-white/10"
            >
              {value.secondary_cta_text}
            </a>
          )}
        </div>
      </div>
    </section>
  );
}
```

---

## 4. TestimonialsBlock

**`block_type`: `testimonials`**

A section showcasing client testimonials.

### Python (Wagtail)

```python
from wagtail.blocks import ListBlock


class TestimonialItemBlock(StructBlock):
    quote = TextBlock(
        label="Quote",
        help_text="Use the client's exact words. Don't paraphrase.",
    )
    author_name = CharBlock(
        label="Author name",
        help_text="Full name",
        max_length=100,
    )
    author_role = CharBlock(
        label="Author role",
        help_text="Job title and company, e.g. 'Head of Engineering, Shopify'",
        max_length=120,
        required=False,
    )
    author_photo = ImageChooserBlock(
        label="Author photo",
        help_text="Square headshot (min 200×200px)",
        required=False,
    )

    class Meta:
        icon = "user"
        label = "Testimonial"

    def get_api_representation(self, value, context=None):
        result = dict(value)
        if value.get("author_photo"):
            img = value["author_photo"]
            rendition = img.get_rendition("fill-200x200")
            result["author_photo"] = {
                "url": rendition.url,
                "width": 200,
                "height": 200,
                "alt": img.title,
            }
        return result


class TestimonialsBlock(StructBlock):
    heading = CharBlock(
        label="Section heading",
        help_text='e.g. "What our clients say"',
        max_length=80,
        required=False,
    )
    testimonials = ListBlock(
        TestimonialItemBlock(),
        label="Testimonials",
        help_text="Add 2–4 testimonials. Odd numbers look better in grid layouts.",
    )

    class Meta:
        icon = "openquote"
        label = "Testimonials"
```

### TypeScript (Next.js)

```typescript
// components/blocks/TestimonialsBlock.tsx
import Image from "next/image";

interface TestimonialItem {
  quote: string;
  author_name: string;
  author_role: string;
  author_photo: { url: string; width: number; height: number; alt: string } | null;
}

export interface TestimonialsBlockValue {
  heading: string;
  testimonials: TestimonialItem[];
}

export function TestimonialsBlock({ value }: { value: TestimonialsBlockValue }) {
  return (
    <section className="py-20 bg-gray-50">
      <div className="mx-auto max-w-7xl px-6">
        {value.heading && (
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            {value.heading}
          </h2>
        )}
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {value.testimonials.map((item, index) => (
            <blockquote key={index} className="bg-white rounded-xl p-8 shadow-sm">
              <p className="text-gray-700 leading-relaxed">"{item.quote}"</p>
              <footer className="mt-6 flex items-center gap-4">
                {item.author_photo && (
                  <Image
                    src={item.author_photo.url}
                    alt={item.author_photo.alt}
                    width={48}
                    height={48}
                    className="rounded-full object-cover"
                  />
                )}
                <div>
                  <div className="font-semibold text-gray-900">{item.author_name}</div>
                  {item.author_role && (
                    <div className="text-sm text-gray-500">{item.author_role}</div>
                  )}
                </div>
              </footer>
            </blockquote>
          ))}
        </div>
      </div>
    </section>
  );
}
```

---

## 5. ImageWithCaptionBlock

**`block_type`: `image_with_caption`**

A full-width or contained image with an optional caption.

### Python (Wagtail)

```python
from wagtail.blocks import ChoiceBlock


class ImageWithCaptionBlock(StructBlock):
    image = ImageChooserBlock(
        label="Image",
        help_text="Upload a high-resolution image. Will be resized automatically for web.",
    )
    alt_text = CharBlock(
        label="Alt text",
        help_text="Describe the image for screen readers and SEO. Don't start with 'Image of...'",
        max_length=120,
    )
    caption = CharBlock(
        label="Caption",
        help_text="Short caption shown beneath the image. Optional.",
        max_length=200,
        required=False,
    )
    width = ChoiceBlock(
        choices=[
            ("full", "Full width"),
            ("contained", "Contained (max 800px)"),
        ],
        default="full",
        label="Image width",
        help_text="Full width spans the page; Contained is better for diagrams or screenshots.",
    )

    class Meta:
        icon = "image"
        label = "Image with caption"

    def get_api_representation(self, value, context=None):
        result = dict(value)
        img = value.get("image")
        if img:
            if value.get("width") == "full":
                rendition = img.get_rendition("width-1920")
            else:
                rendition = img.get_rendition("width-800")
            result["image"] = {
                "url": rendition.url,
                "width": rendition.width,
                "height": rendition.height,
                "alt": value.get("alt_text") or img.title,
            }
        return result
```

### TypeScript (Next.js)

```typescript
// components/blocks/ImageWithCaptionBlock.tsx
import Image from "next/image";

export interface ImageWithCaptionBlockValue {
  image: { url: string; width: number; height: number; alt: string };
  alt_text: string;
  caption: string;
  width: "full" | "contained";
}

export function ImageWithCaptionBlock({ value }: { value: ImageWithCaptionBlockValue }) {
  const isContained = value.width === "contained";

  return (
    <figure className={isContained ? "mx-auto max-w-3xl px-6 py-8" : "py-8"}>
      <div className={`relative ${isContained ? "rounded-lg overflow-hidden" : ""}`}>
        <Image
          src={value.image.url}
          alt={value.image.alt || value.alt_text}
          width={value.image.width}
          height={value.image.height}
          className={`w-full h-auto ${isContained ? "" : ""}`}
        />
      </div>
      {value.caption && (
        <figcaption className="mt-3 text-sm text-gray-500 text-center">
          {value.caption}
        </figcaption>
      )}
    </figure>
  );
}
```

---

## 6. StatsBlock

**`block_type`: `stats`**

A metrics / stats strip. Great for social proof.

### Python (Wagtail)

```python
class StatItemBlock(StructBlock):
    value = CharBlock(
        label="Stat value",
        help_text='The number or metric, e.g. "200+", "$2M", "99.9%"',
        max_length=20,
    )
    label = CharBlock(
        label="Stat label",
        help_text='What the number means, e.g. "Projects shipped", "Revenue generated"',
        max_length=60,
    )
    description = CharBlock(
        label="Description",
        help_text="Optional one-line context below the label",
        max_length=100,
        required=False,
    )

    class Meta:
        label = "Stat"


class StatsBlock(StructBlock):
    heading = CharBlock(
        label="Section heading",
        help_text='Optional heading above stats, e.g. "Our impact"',
        required=False,
        max_length=80,
    )
    stats = ListBlock(
        StatItemBlock(),
        label="Stats",
        help_text="Add 3–4 stats. More than 5 becomes hard to read.",
    )

    class Meta:
        icon = "bold"
        label = "Stats / metrics"
```

### TypeScript (Next.js)

```typescript
// components/blocks/StatsBlock.tsx

interface StatItem {
  value: string;
  label: string;
  description: string;
}

export interface StatsBlockValue {
  heading: string;
  stats: StatItem[];
}

export function StatsBlock({ value }: { value: StatsBlockValue }) {
  return (
    <section className="py-16 bg-white">
      <div className="mx-auto max-w-7xl px-6">
        {value.heading && (
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-12">
            {value.heading}
          </h2>
        )}
        <dl className="grid grid-cols-2 gap-8 lg:grid-cols-4">
          {value.stats.map((stat, index) => (
            <div key={index} className="text-center">
              <dt className="text-4xl font-bold text-gray-900">{stat.value}</dt>
              <dd className="mt-2 text-base font-medium text-gray-600">{stat.label}</dd>
              {stat.description && (
                <p className="mt-1 text-sm text-gray-400">{stat.description}</p>
              )}
            </div>
          ))}
        </dl>
      </div>
    </section>
  );
}
```

---

## 7. CardsBlock

**`block_type`: `cards`**

A grid of cards — services, features, case study previews, team members.

### Python (Wagtail)

```python
class CardItemBlock(StructBlock):
    title = CharBlock(label="Card title", max_length=80)
    body = TextBlock(
        label="Card body",
        help_text="2–4 sentences. Don't write an essay in a card.",
    )
    image = ImageChooserBlock(label="Card image", required=False)
    link_text = CharBlock(
        label="Link label",
        help_text='e.g. "Learn more", "Read case study"',
        max_length=40,
        required=False,
    )
    link_url = URLBlock(label="Link URL", required=False)

    class Meta:
        label = "Card"

    def get_api_representation(self, value, context=None):
        result = dict(value)
        if value.get("image"):
            img = value["image"]
            rendition = img.get_rendition("fill-600x400")
            result["image"] = {
                "url": rendition.url,
                "width": 600,
                "height": 400,
                "alt": img.title,
            }
        return result


class CardsBlock(StructBlock):
    heading = CharBlock(label="Section heading", required=False, max_length=80)
    subheading = TextBlock(label="Section subheading", required=False)
    columns = ChoiceBlock(
        choices=[("2", "2 columns"), ("3", "3 columns"), ("4", "4 columns")],
        default="3",
        label="Grid columns",
        help_text="How many cards per row on desktop",
    )
    cards = ListBlock(CardItemBlock(), label="Cards")

    class Meta:
        icon = "grip"
        label = "Cards grid"
```

### TypeScript (Next.js)

```typescript
// components/blocks/CardsBlock.tsx
import Image from "next/image";

interface CardItem {
  title: string;
  body: string;
  image: { url: string; width: number; height: number; alt: string } | null;
  link_text: string;
  link_url: string;
}

export interface CardsBlockValue {
  heading: string;
  subheading: string;
  columns: "2" | "3" | "4";
  cards: CardItem[];
}

const colsMap: Record<string, string> = {
  "2": "sm:grid-cols-2",
  "3": "sm:grid-cols-2 lg:grid-cols-3",
  "4": "sm:grid-cols-2 lg:grid-cols-4",
};

export function CardsBlock({ value }: { value: CardsBlockValue }) {
  return (
    <section className="py-16">
      <div className="mx-auto max-w-7xl px-6">
        {value.heading && (
          <h2 className="text-3xl font-bold text-gray-900 mb-4">{value.heading}</h2>
        )}
        {value.subheading && (
          <p className="text-lg text-gray-600 mb-10">{value.subheading}</p>
        )}
        <div className={`grid gap-8 ${colsMap[value.columns] ?? colsMap["3"]}`}>
          {value.cards.map((card, index) => (
            <div key={index} className="bg-white rounded-xl overflow-hidden shadow-sm border border-gray-100">
              {card.image && (
                <Image
                  src={card.image.url}
                  alt={card.image.alt}
                  width={600}
                  height={400}
                  className="w-full h-48 object-cover"
                />
              )}
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900">{card.title}</h3>
                <p className="mt-2 text-gray-600">{card.body}</p>
                {card.link_text && card.link_url && (
                  <a
                    href={card.link_url}
                    className="mt-4 inline-block text-sm font-medium text-blue-600 hover:text-blue-700"
                  >
                    {card.link_text} →
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
```

---

## 8. EmbedBlock

**`block_type`: `embed`**

YouTube, Vimeo, or other oEmbed content.

### Python (Wagtail)

```python
from wagtail.embeds.blocks import EmbedBlock as WagtailEmbedBlock


class EmbedBlock(StructBlock):
    url = WagtailEmbedBlock(
        label="Video URL",
        help_text="Paste a YouTube or Vimeo URL. Private videos won't work.",
        required=True,
    )
    caption = CharBlock(
        label="Caption",
        help_text="Optional caption shown beneath the video",
        max_length=200,
        required=False,
    )

    class Meta:
        icon = "media"
        label = "Video embed"
```

### TypeScript (Next.js)

```typescript
// components/blocks/EmbedBlock.tsx

export interface EmbedBlockValue {
  url: { url: string; html: string }; // Wagtail returns oEmbed HTML
  caption: string;
}

export function EmbedBlock({ value }: { value: EmbedBlockValue }) {
  return (
    <figure className="mx-auto max-w-4xl px-6 py-8">
      <div
        className="relative aspect-video rounded-lg overflow-hidden"
        dangerouslySetInnerHTML={{ __html: value.url?.html ?? "" }}
      />
      {value.caption && (
        <figcaption className="mt-3 text-sm text-gray-500 text-center">
          {value.caption}
        </figcaption>
      )}
    </figure>
  );
}
```

---

## 9. RawHTMLBlock

**`block_type`: `raw_html`**

Developer only. Restrict this block to admin/developer roles. Never expose to content editors.

### Python (Wagtail)

```python
from wagtail.blocks import RawHTMLBlock as WagtailRawHTMLBlock


class RawHTMLBlock(WagtailRawHTMLBlock):
    """
    Arbitrary HTML injection. Developer use only.
    Remove from editor StreamBlock definitions — only include in
    developer-only page types.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label", "Raw HTML")
        kwargs.setdefault(
            "help_text",
            "⚠️ Developer only. Paste raw HTML. This bypasses all safety checks. "
            "Do not expose to content editors.",
        )
        super().__init__(*args, **kwargs)

    class Meta:
        icon = "code"
        label = "Raw HTML (dev only)"
```

### TypeScript (Next.js)

```typescript
// components/blocks/RawHTMLBlock.tsx

export function RawHTMLBlock({ value }: { value: string }) {
  // dangerouslySetInnerHTML is intentional — this is a developer block
  return (
    <div
      className="raw-html-block"
      dangerouslySetInnerHTML={{ __html: value }}
    />
  );
}
```

---

## 10. QuoteBlock

**`block_type`: `quote`**

A pull quote — usually for long-form content or blog posts.

### Python (Wagtail)

```python
class QuoteBlock(StructBlock):
    quote = TextBlock(
        label="Quote text",
        help_text="The pull quote. Don't repeat text that appears nearby in body copy.",
    )
    attribution = CharBlock(
        label="Attribution",
        help_text="Who said this? Name, role, or source. Optional.",
        max_length=120,
        required=False,
    )

    class Meta:
        icon = "openquote"
        label = "Pull quote"
```

### TypeScript (Next.js)

```typescript
// components/blocks/QuoteBlock.tsx

export interface QuoteBlockValue {
  quote: string;
  attribution: string;
}

export function QuoteBlock({ value }: { value: QuoteBlockValue }) {
  return (
    <figure className="mx-auto max-w-3xl px-6 py-8">
      <blockquote className="border-l-4 border-gray-900 pl-8">
        <p className="text-2xl font-medium text-gray-900 leading-relaxed">
          "{value.quote}"
        </p>
        {value.attribution && (
          <figcaption className="mt-4 text-base text-gray-500">
            — {value.attribution}
          </figcaption>
        )}
      </blockquote>
    </figure>
  );
}
```

---

## 11. FAQBlock

**`block_type`: `faq`**

Frequently asked questions — accordion or list format.

### Python (Wagtail)

```python
class FAQItemBlock(StructBlock):
    question = CharBlock(
        label="Question",
        help_text="Write questions as a customer would ask them. Use first person: 'How do I...'",
        max_length=200,
    )
    answer = RichTextBlock(
        label="Answer",
        help_text="Keep answers concise. Link to longer pages if needed.",
        features=["bold", "italic", "link", "ul", "ol"],
    )

    class Meta:
        label = "FAQ item"


class FAQBlock(StructBlock):
    heading = CharBlock(
        label="Section heading",
        help_text='e.g. "Frequently asked questions"',
        max_length=80,
        required=False,
    )
    items = ListBlock(
        FAQItemBlock(),
        label="Questions",
        help_text="Add your FAQ items. 5–10 is typical.",
    )
    schema_markup = BooleanBlock(
        label="Add FAQ schema markup",
        help_text="Adds FAQ structured data for Google rich snippets. Recommended.",
        default=True,
        required=False,
    )

    class Meta:
        icon = "help"
        label = "FAQ"
```

### TypeScript (Next.js)

```typescript
// components/blocks/FAQBlock.tsx
"use client";

import { useState } from "react";

interface FAQItem {
  question: string;
  answer: string; // HTML from RichTextBlock
}

export interface FAQBlockValue {
  heading: string;
  items: FAQItem[];
  schema_markup: boolean;
}

export function FAQBlock({ value }: { value: FAQBlockValue }) {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const schemaData = value.schema_markup
    ? {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        mainEntity: value.items.map((item) => ({
          "@type": "Question",
          name: item.question,
          acceptedAnswer: {
            "@type": "Answer",
            text: item.answer.replace(/<[^>]+>/g, ""),
          },
        })),
      }
    : null;

  return (
    <section className="py-16">
      {schemaData && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaData) }}
        />
      )}
      <div className="mx-auto max-w-3xl px-6">
        {value.heading && (
          <h2 className="text-3xl font-bold text-gray-900 mb-10">{value.heading}</h2>
        )}
        <dl className="divide-y divide-gray-200">
          {value.items.map((item, index) => (
            <div key={index} className="py-6">
              <dt>
                <button
                  className="flex w-full justify-between text-left text-lg font-semibold text-gray-900"
                  onClick={() => setOpenIndex(openIndex === index ? null : index)}
                  aria-expanded={openIndex === index}
                >
                  {item.question}
                  <span className="ml-4 flex-shrink-0 text-gray-400">
                    {openIndex === index ? "−" : "+"}
                  </span>
                </button>
              </dt>
              {openIndex === index && (
                <dd
                  className="mt-4 prose prose-base text-gray-600"
                  dangerouslySetInnerHTML={{ __html: item.answer }}
                />
              )}
            </div>
          ))}
        </dl>
      </div>
    </section>
  );
}
```

---

## 12. Block Registry (Python)

Centralise all blocks in `content/blocks.py` and import from there:

```python
# content/blocks.py
"""
Standard Wagtail block library for Autonomous Technologies projects.
Import from this module in all page models.
"""

from .blocks_hero import HeroBlock
from .blocks_text import RichTextBlock, QuoteBlock
from .blocks_cta import CallToActionBlock
from .blocks_testimonials import TestimonialsBlock, TestimonialItemBlock
from .blocks_media import ImageWithCaptionBlock, EmbedBlock
from .blocks_data import StatsBlock, StatItemBlock, CardsBlock, CardItemBlock
from .blocks_faq import FAQBlock, FAQItemBlock
from .blocks_dev import RawHTMLBlock

__all__ = [
    "HeroBlock",
    "RichTextBlock",
    "QuoteBlock",
    "CallToActionBlock",
    "TestimonialsBlock",
    "TestimonialItemBlock",
    "ImageWithCaptionBlock",
    "EmbedBlock",
    "StatsBlock",
    "StatItemBlock",
    "CardsBlock",
    "CardItemBlock",
    "FAQBlock",
    "FAQItemBlock",
    "RawHTMLBlock",
]

# Standard StreamBlock for MarketingPage
MARKETING_STREAM_BLOCKS = [
    ("hero", HeroBlock()),
    ("rich_text", RichTextBlock()),
    ("call_to_action", CallToActionBlock()),
    ("cards", CardsBlock()),
    ("testimonials", TestimonialsBlock()),
    ("stats", StatsBlock()),
    ("faq", FAQBlock()),
    ("image_with_caption", ImageWithCaptionBlock()),
    ("quote", QuoteBlock()),
    ("embed", EmbedBlock()),
    # RawHTMLBlock intentionally excluded — add to dev-only page types
]
```

---

## 13. RenderBlocks (Next.js)

```typescript
// components/RenderBlocks.tsx
import { HeroBlock } from "./blocks/HeroBlock";
import { RichTextBlock } from "./blocks/RichTextBlock";
import { CallToActionBlock } from "./blocks/CallToActionBlock";
import { TestimonialsBlock } from "./blocks/TestimonialsBlock";
import { ImageWithCaptionBlock } from "./blocks/ImageWithCaptionBlock";
import { StatsBlock } from "./blocks/StatsBlock";
import { CardsBlock } from "./blocks/CardsBlock";
import { EmbedBlock } from "./blocks/EmbedBlock";
import { RawHTMLBlock } from "./blocks/RawHTMLBlock";
import { QuoteBlock } from "./blocks/QuoteBlock";
import { FAQBlock } from "./blocks/FAQBlock";

// Maps Wagtail block_type (snake_case) to React component (PascalCase)
const blockMap: Record<string, React.ComponentType<{ value: any }>> = {
  hero: HeroBlock,
  rich_text: RichTextBlock,
  call_to_action: CallToActionBlock,
  testimonials: TestimonialsBlock,
  image_with_caption: ImageWithCaptionBlock,
  stats: StatsBlock,
  cards: CardsBlock,
  embed: EmbedBlock,
  raw_html: RawHTMLBlock,
  quote: QuoteBlock,
  faq: FAQBlock,
};

interface Block {
  type: string;
  value: unknown;
  id: string;
}

interface Props {
  blocks: Block[];
}

export function RenderBlocks({ blocks }: Props) {
  return (
    <>
      {blocks.map((block) => {
        const Component = blockMap[block.type];

        if (!Component) {
          if (process.env.NODE_ENV === "development") {
            console.warn(`[RenderBlocks] Unknown block type: "${block.type}"`);
            return (
              <div key={block.id} className="p-4 bg-yellow-50 border border-yellow-200 text-yellow-800 text-sm">
                Unknown block: <code>{block.type}</code>
              </div>
            );
          }
          return null;
        }

        return <Component key={block.id} value={block.value} />;
      })}
    </>
  );
}
```

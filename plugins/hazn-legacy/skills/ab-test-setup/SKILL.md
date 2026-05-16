---
name: ab-test-setup
description: Design and implement A/B tests and experiments for B2B websites and landing pages. Use when the user wants to test headlines, CTAs, layouts, or any conversion-focused changes. Outputs experiment specifications, implementation guides, and analysis frameworks.
allowed-tools: Read, Write, Bash
---

# A/B Test Setup

Design statistically rigorous A/B tests for B2B websites and landing pages. Focus on experiments that produce actionable results even with lower B2B traffic volumes.

## Process Overview

1. **Understand Context** — What are we testing and why?
2. **Form Hypothesis** — Structure the test prediction
3. **Calculate Feasibility** — Can we reach statistical significance?
4. **Design Variants** — Specify exact changes
5. **Implementation Plan** — Technical setup for Next.js/PostHog
6. **Analysis Framework** — How we'll interpret results

---

## 1. Gather Test Context

**CHECKPOINT:** Before designing any test, ask:

- **What page/element are you testing?** (URL, component)
- **Why do you want to test this?** (data, hunch, audit finding)
- **Current conversion rate?** (or best estimate)
- **Monthly traffic to this page?**
- **Primary conversion goal?** (demo request, signup, purchase)
- **Tools available?** (PostHog, VWO, custom)
- **Timeline constraints?**

---

## 2. Hypothesis Framework

### Structure Every Test As:

```
Because [observation/data],
we believe [specific change]
will cause [expected outcome]
for [target audience].
We'll know this is true when [primary metric] improves by [target %].
```

### Example — Weak vs. Strong

**Weak:** "Let's test a new headline."

**Strong:** "Because the current headline is generic ('Welcome to Our Platform'), we believe a benefit-focused headline ('Cut Your Sales Cycle by 40%') will increase demo requests by 20%+ for VP-level visitors. We'll measure demo request rate from page view to form submission."

---

## 3. Test Feasibility Calculator

### Sample Size Quick Reference

| Baseline CVR | 10% Lift | 20% Lift | 50% Lift |
|--------------|----------|----------|----------|
| 1% | 150k/variant | 39k/variant | 6k/variant |
| 3% | 47k/variant | 12k/variant | 2k/variant |
| 5% | 27k/variant | 7k/variant | 1.2k/variant |
| 10% | 12k/variant | 3k/variant | 550/variant |

### B2B Reality Check

Most B2B landing pages get 1-10k visitors/month. This means:

| Monthly Traffic | Feasible Tests |
|-----------------|----------------|
| <1k visitors | Sequential testing only, or qualitative feedback |
| 1-5k visitors | Bold changes (50%+ lift), 4-8 week tests |
| 5-15k visitors | Moderate changes (20%+ lift), 2-4 week tests |
| 15k+ visitors | Standard A/B testing feasible |

**Recommendation for low-traffic B2B:**
1. Test bolder changes (redesigns, not button colors)
2. Use micro-conversions (clicks, scroll, time) as secondary metrics
3. Run sequential tests (before/after with same-period comparison)
4. Combine with qualitative data (sales feedback, user interviews)

---

## 4. Test Types

| Type | Description | When to Use |
|------|-------------|-------------|
| **A/B** | Two versions, single change | Default for most tests |
| **A/B/n** | Multiple variants | When you have 3+ distinct ideas |
| **Sequential** | Before/after periods | Low traffic (<1k/month) |
| **Multi-page** | Same change across funnel | Consistent experience testing |

### For B2B, Prefer:
- **A/B** with bold changes over subtle tweaks
- **Sequential** when traffic doesn't support simultaneous
- **Multi-page** for messaging consistency tests

---

## 5. Metrics Selection

### Primary Metric
- Single metric that determines winner
- Directly tied to business value
- Example: Demo request rate, signup rate

### Secondary Metrics
- Support interpretation of primary
- Example: CTA click rate, time on page, scroll depth

### Guardrail Metrics
- Things that shouldn't get worse
- Example: Bounce rate, support tickets, sales qualified rate

### B2B Metrics Hierarchy

```
Macro Conversion (Primary)
├── Demo Requested
├── Trial Started
└── Contact Form Submitted

Micro Conversions (Secondary)
├── CTA Clicked
├── Pricing Page Viewed
├── Case Study Downloaded
├── Video Watched (50%+)
└── Scroll Depth (75%+)

Guardrails
├── Bounce Rate
├── Pages Per Session
└── Lead Quality Score (from sales)
```

---

## 6. Design Variants

### What to Test (B2B Priority Order)

1. **Headlines** — Specificity, benefit focus, audience callout
2. **Value Proposition** — Different angles, proof points
3. **CTA Copy** — Action words, benefit vs. action
4. **Social Proof** — Logos, testimonials, case study placement
5. **Form Length** — Fields required, progressive disclosure
6. **Page Structure** — Section order, content length

### Variant Specification Template

```markdown
## Variant A (Control)
- Element: Homepage hero headline
- Current: "The All-in-One Platform for Your Business"
- Screenshot: [link or description]

## Variant B (Treatment)
- Element: Homepage hero headline  
- Change: "Cut Your Sales Cycle by 40% — Like [Customer] Did"
- Rationale: Adds specificity, social proof, and quantified benefit
```

---

## 7. Implementation (Next.js + PostHog)

### PostHog Feature Flags Setup

```typescript
// lib/posthog.ts
import posthog from 'posthog-js'

export const initPostHog = () => {
  if (typeof window !== 'undefined') {
    posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
      api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
      loaded: (posthog) => {
        if (process.env.NODE_ENV === 'development') posthog.debug()
      }
    })
  }
}
```

### Using Feature Flags for A/B Tests

```tsx
// components/HeroHeadline.tsx
'use client'
import { useFeatureFlagVariantKey } from 'posthog-js/react'

export function HeroHeadline() {
  const variant = useFeatureFlagVariantKey('homepage-headline-test')
  
  const headlines = {
    control: "The All-in-One Platform for Your Business",
    treatment: "Cut Your Sales Cycle by 40% — Like Acme Did"
  }
  
  return (
    <h1 className="text-4xl font-bold">
      {headlines[variant as keyof typeof headlines] || headlines.control}
    </h1>
  )
}
```

### Server-Side Rendering (Recommended)

```tsx
// app/page.tsx
import { cookies } from 'next/headers'
import { PostHog } from 'posthog-node'

export default async function HomePage() {
  const posthog = new PostHog(process.env.POSTHOG_API_KEY!)
  
  let distinctId: string
  let variant: string | boolean | undefined
  
  try {
    // Get or create distinct ID from cookies
    const cookieStore = await cookies()
    distinctId = cookieStore.get('ph_distinct_id')?.value || crypto.randomUUID()
    
    variant = await posthog.getFeatureFlag('homepage-headline-test', distinctId)
  } catch (error) {
    // Fallback if cookies fail (e.g., during static generation)
    console.error('Failed to get feature flag:', error)
    distinctId = crypto.randomUUID()
    variant = 'control'
  } finally {
    // Always shutdown PostHog client to flush events
    await posthog.shutdown()
  }
  
  return <HeroSection variant={variant} />
}
```

### Track Conversion Events

```typescript
// Track when user sees the variant
posthog.capture('experiment_viewed', {
  experiment: 'homepage-headline-test',
  variant: variant
})

// Track conversion
posthog.capture('demo_requested', {
  experiment: 'homepage-headline-test',
  variant: variant,
  source: 'homepage_hero'
})
```

---

## 8. Pre-Launch Checklist

**CHECKPOINT:** Before launching, verify:

- [ ] Hypothesis documented with specific predictions
- [ ] Sample size calculated, test duration estimated
- [ ] Primary metric defined and trackable
- [ ] Variants implemented correctly (QA both versions)
- [ ] Tracking events firing correctly
- [ ] Feature flag configured with correct % split
- [ ] Guardrail metrics being captured
- [ ] Team aligned on "do not touch" during test

---

## 9. Running the Test

### Do:
- Monitor for technical issues daily
- Document any external factors (campaigns, PR, seasonality)
- Keep stakeholders informed of timeline

### Don't:
- Peek at results and stop early (the #1 mistake)
- Make changes to variants mid-test
- Add new traffic sources during test
- Declare winners before reaching sample size

### The Peeking Problem

Checking results early and stopping when you see "significance" leads to false positives 30%+ of the time. Pre-commit to your sample size and timeline.

---

## 10. Analysis Framework

### When Test Completes

1. **Check sample size reached** — Did we hit our target?
2. **Statistical significance** — Is p < 0.05?
3. **Effect size** — Is the lift meaningful for business?
4. **Confidence interval** — What's the range of likely impact?
5. **Secondary metrics** — Do they tell a consistent story?
6. **Guardrails** — Did anything get worse?
7. **Segments** — Different results for mobile/desktop, new/returning?

### Interpreting Results

| Result | Action |
|--------|--------|
| Significant winner | Implement, document learnings |
| Significant loser | Keep control, analyze why |
| No significant difference | Need bolder test or more traffic |
| Mixed signals | Segment analysis, qualitative research |

---

## 11. Documentation Template

```markdown
# A/B Test: [Name]

## Overview
- **Page:** [URL]
- **Test Period:** [Start] to [End]
- **Traffic:** [X] visitors per variant

## Hypothesis
Because [observation],
we believe [change]
will cause [outcome]
for [audience].

## Variants
### Control (A)
[Description + screenshot]

### Treatment (B)
[Description + screenshot]

## Results
| Metric | Control | Treatment | Lift | Significance |
|--------|---------|-----------|------|--------------|
| Primary: [X] | X% | Y% | +Z% | p = 0.XX |
| Secondary: [X] | X | Y | +Z% | p = 0.XX |

## Decision
[Implement Treatment / Keep Control / Inconclusive]

## Learnings
- What worked:
- What didn't:
- Next test idea:
```

---

## Output Deliverables

When designing a test, provide:

1. **Test Specification Document** — Hypothesis, variants, metrics, timeline
2. **Implementation Guide** — Code snippets for Next.js/PostHog
3. **Tracking Checklist** — Events to configure
4. **Analysis Template** — Pre-filled with metrics to track

---

## Checkpoints (Human-in-Loop)

**CHECKPOINT 1:** After gathering context
- Present feasibility assessment
- Ask: "Given your traffic, this test will take [X weeks]. Proceed or adjust?"

**CHECKPOINT 2:** After designing variants
- Present variant specifications
- Ask: "Do these variants capture what you want to test?"

**CHECKPOINT 3:** Before implementation
- Present technical approach
- Ask: "Ready to implement? Any technical constraints?"

---

## Related Skills

- `conversion-audit` — Identifies what to test
- `analytics-tracking` — Sets up measurement infrastructure
- `b2b-marketing-ux` — B2B conversion principles

---

## References

- [Evan Miller's Sample Size Calculator](https://www.evanmiller.org/ab-testing/sample-size.html)
- [PostHog Experimentation Docs](https://posthog.com/docs/experiments)
- [Statistical Significance Explained](https://posthog.com/blog/ab-testing-guide-for-engineers)

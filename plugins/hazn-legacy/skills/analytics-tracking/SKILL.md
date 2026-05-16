---
name: analytics-tracking
description: Set up and audit analytics tracking for Next.js websites. Covers GA4, PostHog, and conversion tracking implementation. Use when implementing tracking plans, debugging analytics issues, or auditing measurement infrastructure.
allowed-tools: Read, Write, Bash
---

# Analytics Tracking

Implement comprehensive analytics tracking for Next.js + Payload CMS websites. Focus on GA4 and PostHog for a complete measurement stack.

## Our Stack

| Tool | Purpose | Priority |
|------|---------|----------|
| **PostHog** | Product analytics, session replay, feature flags, A/B tests | Primary |
| **GA4** | Web analytics, Google Ads integration, SEO insights | Primary |
| **Google Tag Manager** | Tag management, marketing pixels | Secondary |

---

## Process Overview

1. **Audit Current State** — What's tracking, what's missing?
2. **Define Tracking Plan** — Events, properties, conversions
3. **Implement Tracking** — Next.js code setup
4. **Validate & QA** — Ensure everything fires correctly
5. **Document** — Tracking plan for ongoing reference

---

## 1. Audit Current State

**CHECKPOINT:** Before implementing, ask:

- **What's currently tracked?** (Check for existing GA, pixels)
- **What decisions need data?** (What questions are you trying to answer?)
- **Key conversion goals?** (Demo, signup, purchase, contact)
- **Privacy requirements?** (GDPR, cookie consent needed?)
- **Who needs access?** (Marketing, product, sales)

### Quick Audit Commands

```bash
# Check for existing tracking in codebase
grep -r "gtag\|analytics\|posthog\|segment" --include="*.tsx" --include="*.ts" .

# Check for GTM
grep -r "GTM-\|googletagmanager" --include="*.tsx" --include="*.html" .
```

---

## 2. Tracking Plan

### Event Naming Convention

Use `object_action` format, lowercase with underscores:

```
page_viewed
cta_clicked
form_started
form_submitted
demo_requested
pricing_viewed
```

### Essential Events for B2B Sites

| Event | Properties | Trigger |
|-------|------------|---------|
| `page_viewed` | page_title, page_path, referrer | Every page load |
| `cta_clicked` | button_text, button_location, destination | CTA click |
| `form_viewed` | form_name, form_location | Form enters viewport |
| `form_started` | form_name, first_field | First field interaction |
| `form_submitted` | form_name, form_location | Successful submission |
| `demo_requested` | source, plan_interest | Demo form submit |
| `pricing_viewed` | referrer_page | Pricing page view |
| `case_study_viewed` | case_study_name, industry | Case study page view |
| `video_played` | video_name, video_duration | Video play start |
| `video_completed` | video_name, percent_watched | Video 90%+ watched |
| `scroll_depth` | depth_percent, page_path | 25%, 50%, 75%, 100% |

### Property Standards

| Property | Type | Example |
|----------|------|---------|
| `page_path` | string | "/pricing" |
| `page_title` | string | "Pricing - Acme" |
| `button_text` | string | "Get Started" |
| `button_location` | string | "hero", "nav", "footer" |
| `form_name` | string | "demo_request", "newsletter" |
| `utm_source` | string | "google", "linkedin" |
| `utm_medium` | string | "cpc", "organic", "email" |
| `utm_campaign` | string | "spring_2024" |

---

## 3. Implementation (Next.js App Router)

### PostHog Setup

#### Install

```bash
npm install posthog-js posthog-node
```

#### Provider Setup

```tsx
// app/providers.tsx
'use client'
import posthog from 'posthog-js'
import { PostHogProvider } from 'posthog-js/react'
import { usePathname, useSearchParams } from 'next/navigation'
import { useEffect } from 'react'

if (typeof window !== 'undefined') {
  posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
    api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://app.posthog.com',
    capture_pageview: false, // We'll capture manually for more control
    capture_pageleave: true,
  })
}

export function PHProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  
  useEffect(() => {
    if (pathname) {
      let url = window.origin + pathname
      if (searchParams?.toString()) {
        url = url + '?' + searchParams.toString()
      }
      posthog.capture('$pageview', { $current_url: url })
    }
  }, [pathname, searchParams])
  
  return <PostHogProvider client={posthog}>{children}</PostHogProvider>
}
```

#### Root Layout

```tsx
// app/layout.tsx
import { PHProvider } from './providers'
import { Suspense } from 'react'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Suspense fallback={null}>
          <PHProvider>{children}</PHProvider>
        </Suspense>
      </body>
    </html>
  )
}
```

### GA4 Setup (Consent-Aware)

> **⚠️ GDPR Compliance:** GA4 must NOT load before user consent. The implementation below uses a consent-first approach.

#### Consent-Aware GA4 Component

```tsx
// components/GoogleAnalytics.tsx
'use client'
import Script from 'next/script'
import { useEffect, useState } from 'react'

const GA_ID = process.env.NEXT_PUBLIC_GA_ID

export function GoogleAnalytics() {
  const [hasConsent, setHasConsent] = useState(false)
  
  useEffect(() => {
    // Check for existing consent
    const consent = localStorage.getItem('cookie_consent')
    if (consent === 'accepted') {
      setHasConsent(true)
    }
    
    // Listen for consent changes
    const handleConsentChange = (e: CustomEvent) => {
      if (e.detail.analytics) {
        setHasConsent(true)
      }
    }
    
    window.addEventListener('cookie_consent_update', handleConsentChange as EventListener)
    return () => window.removeEventListener('cookie_consent_update', handleConsentChange as EventListener)
  }, [])
  
  // Only load GA4 after consent
  if (!hasConsent || !GA_ID) return null
  
  return (
    <>
      <Script
        src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`}
        strategy="afterInteractive"
      />
      <Script id="gtag-init" strategy="afterInteractive">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${GA_ID}', {
            page_path: window.location.pathname,
          });
        `}
      </Script>
    </>
  )
}
```

#### Root Layout (Consent-Safe)

```tsx
// app/layout.tsx
import { GoogleAnalytics } from '@/components/GoogleAnalytics'
import { CookieConsent } from '@/components/CookieConsent'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}
        <GoogleAnalytics />
        <CookieConsent />
      </body>
    </html>
  )
}
```

### Unified Analytics Hook

```tsx
// lib/analytics.ts
import posthog from 'posthog-js'

type EventProperties = Record<string, string | number | boolean | undefined>

export const analytics = {
  track: (event: string, properties?: EventProperties) => {
    // PostHog
    posthog.capture(event, properties)
    
    // GA4
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', event, properties)
    }
  },
  
  identify: (userId: string, traits?: EventProperties) => {
    posthog.identify(userId, traits)
    
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('config', process.env.NEXT_PUBLIC_GA_ID!, {
        user_id: userId,
        ...traits
      })
    }
  },
  
  page: (pageName?: string, properties?: EventProperties) => {
    posthog.capture('$pageview', { page_name: pageName, ...properties })
    
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'page_view', {
        page_title: pageName,
        ...properties
      })
    }
  }
}

// TypeScript declarations
declare global {
  interface Window {
    gtag: (...args: any[]) => void
    dataLayer: any[]
  }
}
```

### Component Examples

#### Tracked CTA Button

```tsx
// components/TrackedButton.tsx
'use client'
import { analytics } from '@/lib/analytics'

interface TrackedButtonProps {
  children: React.ReactNode
  location: string
  destination?: string
  onClick?: () => void
  className?: string
}

export function TrackedButton({ 
  children, 
  location, 
  destination,
  onClick,
  className 
}: TrackedButtonProps) {
  const handleClick = () => {
    analytics.track('cta_clicked', {
      button_text: typeof children === 'string' ? children : 'CTA',
      button_location: location,
      destination: destination
    })
    onClick?.()
  }
  
  return (
    <button onClick={handleClick} className={className}>
      {children}
    </button>
  )
}
```

#### Form Tracking Hook

```tsx
// hooks/useFormTracking.ts
'use client'
import { useEffect, useRef } from 'react'
import { analytics } from '@/lib/analytics'

export function useFormTracking(formName: string, formLocation: string) {
  const hasStarted = useRef(false)
  
  const trackFormView = () => {
    analytics.track('form_viewed', { form_name: formName, form_location: formLocation })
  }
  
  const trackFormStart = () => {
    if (!hasStarted.current) {
      hasStarted.current = true
      analytics.track('form_started', { form_name: formName, form_location: formLocation })
    }
  }
  
  const trackFormSubmit = (success: boolean, errorMessage?: string) => {
    if (success) {
      analytics.track('form_submitted', { form_name: formName, form_location: formLocation })
    } else {
      analytics.track('form_error', { 
        form_name: formName, 
        form_location: formLocation,
        error_message: errorMessage 
      })
    }
  }
  
  return { trackFormView, trackFormStart, trackFormSubmit }
}
```

#### Scroll Depth Tracking

```tsx
// components/ScrollTracker.tsx
'use client'
import { useEffect, useRef } from 'react'
import { analytics } from '@/lib/analytics'

export function ScrollTracker() {
  const tracked = useRef<Set<number>>(new Set())
  
  useEffect(() => {
    const thresholds = [25, 50, 75, 100]
    
    const handleScroll = () => {
      const scrollPercent = Math.round(
        (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
      )
      
      thresholds.forEach(threshold => {
        if (scrollPercent >= threshold && !tracked.current.has(threshold)) {
          tracked.current.add(threshold)
          analytics.track('scroll_depth', {
            depth_percent: threshold,
            page_path: window.location.pathname
          })
        }
      })
    }
    
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])
  
  return null
}
```

---

## 4. Conversion Setup

### GA4 Conversions

In GA4 Admin > Events, mark as conversions:
- `form_submitted` (when form_name = "demo_request")
- `demo_requested`
- `signup_completed`

### PostHog Actions

Create Actions in PostHog for key conversions:
1. Go to Data Management > Actions
2. Create action matching your event (e.g., `demo_requested`)
3. Use in Funnels, Trends, and Experiments

### Conversion Funnel Definition

```
Landing Page View
    ↓ (track: page_viewed)
CTA Click  
    ↓ (track: cta_clicked)
Form View
    ↓ (track: form_viewed)
Form Start
    ↓ (track: form_started)
Form Submit
    ↓ (track: form_submitted, demo_requested)
Thank You Page
    ↓ (track: page_viewed where path = /thank-you)
```

---

## 5. UTM Parameter Handling

### Capture UTMs on Landing

```tsx
// hooks/useUTMCapture.ts
'use client'
import { useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import posthog from 'posthog-js'

export function useUTMCapture() {
  const searchParams = useSearchParams()
  
  useEffect(() => {
    const utmParams = {
      utm_source: searchParams?.get('utm_source'),
      utm_medium: searchParams?.get('utm_medium'),
      utm_campaign: searchParams?.get('utm_campaign'),
      utm_content: searchParams?.get('utm_content'),
      utm_term: searchParams?.get('utm_term'),
    }
    
    // Filter out null values
    const filteredUTMs = Object.fromEntries(
      Object.entries(utmParams).filter(([_, v]) => v != null)
    )
    
    if (Object.keys(filteredUTMs).length > 0) {
      // Store in PostHog as person properties
      posthog.people.set(filteredUTMs)
      
      // Also store in session storage for form submissions
      sessionStorage.setItem('utm_params', JSON.stringify(filteredUTMs))
    }
  }, [searchParams])
}
```

### Include UTMs in Form Submissions

```tsx
// When submitting forms, include stored UTMs
const getStoredUTMs = () => {
  if (typeof window === 'undefined') return {}
  const stored = sessionStorage.getItem('utm_params')
  return stored ? JSON.parse(stored) : {}
}

// In your form submit handler
const handleSubmit = async (formData: FormData) => {
  const utms = getStoredUTMs()
  
  analytics.track('demo_requested', {
    ...utms,
    source_page: window.location.pathname
  })
}
```

---

## 6. Validation & QA

### Testing Checklist

- [ ] Page views firing on navigation
- [ ] CTA clicks tracked with correct properties
- [ ] Form events firing in sequence (view → start → submit)
- [ ] UTM parameters captured and persisted
- [ ] Conversions registering in GA4
- [ ] PostHog receiving events (check Live Events)
- [ ] No duplicate events
- [ ] Works on mobile
- [ ] Works with ad blockers (graceful degradation)

### Debug Tools

```typescript
// Enable PostHog debug mode
posthog.debug()

// Check dataLayer for GTM/GA4
console.log(window.dataLayer)

// Verify tracking in browser console
// PostHog: Check Network tab for /e/ requests to PostHog
// GA4: Use Google Analytics Debugger extension
```

### PostHog Live Events

1. Go to PostHog → Activity → Live Events
2. Filter by your test user/session
3. Verify events and properties appear correctly

---

## 7. Consent Management

> **⚠️ CRITICAL:** Analytics scripts must NOT load before user consent in GDPR/CCPA jurisdictions. This section covers compliant implementation.

### Requirements

1. **Default-off for EU visitors** — No tracking scripts load until explicit consent
2. **Granular consent** — Users should be able to accept/reject different categories
3. **Persistent storage** — Remember consent choice across sessions
4. **Easy withdrawal** — Users can change their mind anytime

### Cookie Consent Implementation

```tsx
// components/CookieConsent.tsx
'use client'
import { useState, useEffect } from 'react'
import posthog from 'posthog-js'

type ConsentState = {
  necessary: boolean    // Always true
  analytics: boolean    // GA4, PostHog
  marketing: boolean    // Ads, retargeting
}

const DEFAULT_CONSENT: ConsentState = {
  necessary: true,
  analytics: false,  // Default OFF for GDPR compliance
  marketing: false,
}

export function CookieConsent() {
  const [showBanner, setShowBanner] = useState(false)
  const [consent, setConsent] = useState<ConsentState>(DEFAULT_CONSENT)
  
  useEffect(() => {
    const stored = localStorage.getItem('cookie_consent')
    if (!stored) {
      setShowBanner(true)
      // Disable all tracking until consent
      posthog.opt_out_capturing()
    } else {
      const parsed = JSON.parse(stored) as ConsentState
      setConsent(parsed)
      applyConsent(parsed)
    }
  }, [])
  
  const applyConsent = (newConsent: ConsentState) => {
    // PostHog
    if (newConsent.analytics) {
      posthog.opt_in_capturing()
    } else {
      posthog.opt_out_capturing()
    }
    
    // Dispatch event for GA4 and other scripts
    window.dispatchEvent(new CustomEvent('cookie_consent_update', { 
      detail: newConsent 
    }))
    
    // Update Google Consent Mode if using GTM
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('consent', 'update', {
        analytics_storage: newConsent.analytics ? 'granted' : 'denied',
        ad_storage: newConsent.marketing ? 'granted' : 'denied',
      })
    }
  }
  
  const handleAcceptAll = () => {
    const newConsent = { necessary: true, analytics: true, marketing: true }
    localStorage.setItem('cookie_consent', JSON.stringify(newConsent))
    setConsent(newConsent)
    applyConsent(newConsent)
    setShowBanner(false)
  }
  
  const handleAcceptNecessary = () => {
    const newConsent = { necessary: true, analytics: false, marketing: false }
    localStorage.setItem('cookie_consent', JSON.stringify(newConsent))
    setConsent(newConsent)
    applyConsent(newConsent)
    setShowBanner(false)
  }
  
  const handleCustomize = () => {
    // Open preferences modal - implement based on your UI needs
    console.log('Open consent preferences modal')
  }
  
  if (!showBanner) return null
  
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t p-4 shadow-lg z-50">
      <div className="max-w-4xl mx-auto flex flex-col sm:flex-row items-center gap-4">
        <p className="text-sm flex-1">
          We use cookies to analyze site usage and improve your experience. 
          <button onClick={handleCustomize} className="underline ml-1">
            Customize
          </button>
        </p>
        <div className="flex gap-2">
          <button 
            onClick={handleAcceptNecessary}
            className="px-4 py-2 border rounded hover:bg-gray-50"
          >
            Necessary Only
          </button>
          <button 
            onClick={handleAcceptAll}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Accept All
          </button>
        </div>
      </div>
    </div>
  )
}
```

### Integrating with Third-Party Consent Tools

For enterprise deployments, integrate with established consent management platforms:

#### Cookiebot Integration

```tsx
// components/CookiebotConsent.tsx
'use client'
import Script from 'next/script'
import { useEffect } from 'react'
import posthog from 'posthog-js'

export function CookiebotConsent() {
  useEffect(() => {
    // Listen for Cookiebot consent
    window.addEventListener('CookiebotOnAccept', () => {
      if (window.Cookiebot?.consent?.statistics) {
        posthog.opt_in_capturing()
        window.dispatchEvent(new CustomEvent('cookie_consent_update', {
          detail: { analytics: true }
        }))
      }
    })
  }, [])
  
  return (
    <Script
      id="Cookiebot"
      src="https://consent.cookiebot.com/uc.js"
      data-cbid="YOUR-COOKIEBOT-ID"
      data-blockingmode="auto"
      strategy="beforeInteractive"
    />
  )
}

declare global {
  interface Window {
    Cookiebot?: {
      consent?: {
        necessary?: boolean
        statistics?: boolean
        marketing?: boolean
      }
    }
  }
}
```

#### OneTrust Integration

```tsx
// Listen for OneTrust consent
window.OneTrust?.OnConsentChanged(() => {
  const groups = window.OnetrustActiveGroups || ''
  
  // C0002 = Performance/Analytics in OneTrust
  if (groups.includes('C0002')) {
    posthog.opt_in_capturing()
    window.dispatchEvent(new CustomEvent('cookie_consent_update', {
      detail: { analytics: true }
    }))
  }
})
```

### Consent-Aware Analytics Helper

```tsx
// lib/analytics.ts
import posthog from 'posthog-js'

export const hasAnalyticsConsent = (): boolean => {
  if (typeof window === 'undefined') return false
  
  const stored = localStorage.getItem('cookie_consent')
  if (!stored) return false
  
  try {
    const consent = JSON.parse(stored)
    return consent.analytics === true
  } catch {
    return false
  }
}

export const analytics = {
  track: (event: string, properties?: Record<string, any>) => {
    if (!hasAnalyticsConsent()) return
    
    // PostHog
    posthog.capture(event, properties)
    
    // GA4
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', event, properties)
    }
  },
  
  // ... other methods
}
```

### Geo-Based Default Consent

For automatic GDPR detection:

```tsx
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const EU_COUNTRIES = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 
  'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 
  'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', 'GB']

export function middleware(request: NextRequest) {
  const response = NextResponse.next()
  const country = request.geo?.country || ''
  
  // Set header for client-side GDPR detection
  response.headers.set('x-user-country', country)
  response.headers.set('x-requires-consent', EU_COUNTRIES.includes(country) ? 'true' : 'false')
  
  return response
}
```

### Testing Consent Flow

```typescript
// Manually test consent states
localStorage.removeItem('cookie_consent')  // Reset to show banner
localStorage.setItem('cookie_consent', JSON.stringify({ 
  necessary: true, 
  analytics: true, 
  marketing: false 
}))

// Verify PostHog state
console.log('PostHog opted in:', !posthog.has_opted_out_capturing())

// Verify GA4 state
console.log('dataLayer:', window.dataLayer)
```
```

---

## 8. Documentation Template

### Tracking Plan Document

```markdown
# [Site Name] Tracking Plan

## Overview
- **Tools:** PostHog, GA4
- **Last Updated:** [Date]
- **Owner:** [Name]

## Events

| Event | Description | Properties | Trigger |
|-------|-------------|------------|---------|
| page_viewed | Page load | page_path, page_title, referrer | Auto |
| cta_clicked | Button click | button_text, location | Click |
| form_submitted | Form success | form_name, form_location | Submit |
| demo_requested | Demo form | source, utm_* | Demo submit |

## Conversions

| Conversion | Event | GA4 | PostHog |
|------------|-------|-----|---------|
| Demo Request | demo_requested | ✓ | Action |
| Newsletter Signup | form_submitted (newsletter) | ✓ | Action |

## UTM Convention

| Parameter | Format | Example |
|-----------|--------|---------|
| utm_source | platform_name | google, linkedin |
| utm_medium | channel_type | cpc, organic, email |
| utm_campaign | campaign_name | spring_2024_launch |
```

---

## Checkpoints (Human-in-Loop)

**CHECKPOINT 1:** After audit
- Present current tracking state
- Ask: "What key questions should tracking answer?"

**CHECKPOINT 2:** After tracking plan
- Present proposed events and properties
- Ask: "Does this cover your measurement needs?"

**CHECKPOINT 3:** After implementation
- Present QA results
- Ask: "Ready to deploy to production?"

---

## Related Skills

- `ab-test-setup` — Uses tracking for experiment measurement
- `conversion-audit` — Identifies what to measure
- `payload-nextjs-stack` — Our implementation stack

---

## Environment Variables

```bash
# .env.local
NEXT_PUBLIC_POSTHOG_KEY=phc_xxxxxxxxxxxx
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
POSTHOG_API_KEY=phx_xxxxxxxxxxxx  # Server-side only
```

---
name: shopify-cro-audit
description: Visually audit Shopify stores and generate CRO recommendations. Takes screenshots, evaluates UX/conversion elements across homepage, product pages, cart, and checkout. Generates branded HTML audit report with before/after mockups. Use for client audits, sales call prep, or delivering value-add reports.
---

# Shopify CRO Visual Audit

Comprehensive visual + data-driven audit for Shopify stores. Captures screenshots, pulls analytics from CDP/PostHog if available, queries Shopify Admin API, and generates actionable CRO recommendations with projected revenue impact.

## When to Use

- Auditing prospect/client Shopify stores
- Pre-sales value-add deliverables
- Preparing CRO improvement roadmaps
- Competitive analysis
- Ongoing client optimization reviews

---

## Process

### 1. Discovery Questions (MANDATORY — DO NOT SKIP)

**⚠️ STOP. Ask these questions BEFORE doing any audit work.**

Present this to the user:

---

> **Before I start the audit, I need a few details:**
>
> **1. Store Info**
> - Store URL?
> - Industry/vertical? (fashion, beauty, electronics, home, food, health, luxury, B2B)
> - Price point? (budget <$50 / mid-market $50-200 / premium $200-500 / luxury $500+)
>
> **2. Market Context**
> - Primary markets? (Pakistan, UAE, US, UK, etc.)
> - Any specific local payment methods needed? (COD, Mada, etc.)
>
> **3. Data Access** (helps me go deeper)
> - [ ] **Shopify Admin API** — store domain + access token? (for orders, products, abandoned carts)
> - [ ] **PostgreSQL/CDP** — connection string? (for funnel analysis, cohorts, attribution)
> - [ ] **PostHog** — project ID + API key? (for session recordings, heatmaps, rage clicks)
> - [ ] **GA4** — property ID + access? (for traffic sources, user flow, conversions)
> - [ ] **None** — I'll do a visual-only audit
>
> **4. Known Issues** (optional)
> - Current CVR if known?
> - Any specific pain points you've identified?

---

Wait for answers before proceeding.

### Data Access Note for Reports

When data access is NOT provided, include this section in the audit report:

```html
<section id="data-insights">
    <div class="section-header">
        <div class="section-number">XX</div>
        <h2>📊 Unlock Deeper Insights</h2>
        <p>This audit is based on visual analysis. With data access, we can provide significantly more actionable insights.</p>
    </div>
    
    <div class="card" style="border-left: 3px solid var(--accent-cyan);">
        <h4 style="margin-bottom: 16px;">With Shopify Admin API access, we can analyze:</h4>
        <ul style="color: var(--text-secondary); margin-left: 20px;">
            <li>Actual conversion rates and revenue trends</li>
            <li>Abandoned checkout patterns and recovery rates</li>
            <li>Top-selling products vs. most-viewed products gap</li>
            <li>Customer lifetime value and repeat purchase rates</li>
            <li>Discount code usage and effectiveness</li>
        </ul>
    </div>
    
    <div class="card" style="border-left: 3px solid var(--accent-purple);">
        <h4 style="margin-bottom: 16px;">With CDP/PostgreSQL access, we can analyze:</h4>
        <ul style="color: var(--text-secondary); margin-left: 20px;">
            <li>Full funnel drop-off analysis (product view → add to cart → checkout → purchase)</li>
            <li>Attribution modeling and channel ROI</li>
            <li>Customer segmentation and cohort behavior</li>
            <li>Time-to-purchase and session patterns</li>
            <li>Geographic and device-level conversion differences</li>
        </ul>
    </div>
    
    <div class="card" style="border-left: 3px solid var(--accent-pink);">
        <h4 style="margin-bottom: 16px;">With PostHog/GA4 access, we can analyze:</h4>
        <ul style="color: var(--text-secondary); margin-left: 20px;">
            <li>Session recordings of drop-off points</li>
            <li>Heatmaps showing where users click (and don't)</li>
            <li>Rage clicks and UX friction points</li>
            <li>A/B test results and experiment data</li>
            <li>User flow and navigation patterns</li>
        </ul>
    </div>
    
    <p style="margin-top: 24px; color: var(--text-muted); font-size: 14px;">
        Contact us to set up data integrations and unlock a comprehensive data-driven audit.
    </p>
</section>
```

---

### 2. Pull Analytics Data (If Available)

Pull ALL relevant data from available sources. Don't limit — get everything useful.

#### CDP Data (RudderStack)
Reference: `references/cdp-schema.md`

**Funnel & Conversion:**
```sql
-- Full checkout funnel with drop-off rates
WITH funnel AS (
  SELECT 'product_viewed' as step, 1 as ord, COUNT(DISTINCT anonymous_id) as cnt FROM rudder_cdp.product_viewed WHERE context_source_id = '{SOURCE_ID}'
  UNION ALL SELECT 'product_added', 2, COUNT(DISTINCT anonymous_id) FROM rudder_cdp.product_added WHERE context_source_id = '{SOURCE_ID}'
  UNION ALL SELECT 'cart_viewed', 3, COUNT(DISTINCT anonymous_id) FROM rudder_cdp.cart_viewed WHERE context_source_id = '{SOURCE_ID}'
  UNION ALL SELECT 'checkout_started', 4, COUNT(DISTINCT anonymous_id) FROM rudder_cdp.checkout_started WHERE context_source_id = '{SOURCE_ID}'
  UNION ALL SELECT 'contact_info', 5, COUNT(DISTINCT anonymous_id) FROM rudder_cdp.checkout_contact_info_submitted WHERE context_source_id = '{SOURCE_ID}'
  UNION ALL SELECT 'shipping_info', 6, COUNT(DISTINCT anonymous_id) FROM rudder_cdp.checkout_shipping_info_submitted WHERE context_source_id = '{SOURCE_ID}'
  UNION ALL SELECT 'payment_entered', 7, COUNT(DISTINCT anonymous_id) FROM rudder_cdp.payment_info_entered WHERE context_source_id = '{SOURCE_ID}'
  UNION ALL SELECT 'order_completed', 8, COUNT(DISTINCT anonymous_id) FROM rudder_cdp.order_completed WHERE context_source_id = '{SOURCE_ID}'
)
SELECT step, cnt, ROUND(100.0 * cnt / FIRST_VALUE(cnt) OVER (ORDER BY ord), 1) as pct_of_top,
       ROUND(100.0 * cnt / LAG(cnt) OVER (ORDER BY ord), 1) as step_cvr
FROM funnel ORDER BY ord;
```

**Attribution & Traffic:**
```sql
-- Revenue by traffic source
SELECT context_campaign_source, context_campaign_medium, context_campaign_name,
       COUNT(DISTINCT order_id) as orders, SUM(revenue) as revenue, AVG(revenue) as aov
FROM rudder_cdp.order_completed WHERE context_source_id = '{SOURCE_ID}'
GROUP BY 1, 2, 3 ORDER BY revenue DESC;

-- Landing page performance
SELECT REGEXP_EXTRACT(context_page_url, '^https?://[^/]+(/[^?]*)', 1) as landing_page,
       COUNT(DISTINCT anonymous_id) as visitors,
       COUNT(DISTINCT CASE WHEN event = 'order_completed' THEN anonymous_id END) as conversions
FROM rudder_cdp.pages WHERE context_source_id = '{SOURCE_ID}'
GROUP BY 1 ORDER BY visitors DESC LIMIT 20;

-- UTM campaign breakdown
SELECT context_campaign_name, context_campaign_content,
       COUNT(*) as sessions, SUM(CASE WHEN event = 'order_completed' THEN 1 ELSE 0 END) as orders
FROM rudder_cdp.tracks WHERE context_source_id = '{SOURCE_ID}' AND context_campaign_name IS NOT NULL
GROUP BY 1, 2 ORDER BY sessions DESC;
```

**Device & Browser:**
```sql
-- Device type performance
SELECT context_device_type, context_browser_name,
       COUNT(DISTINCT anonymous_id) as visitors,
       COUNT(DISTINCT CASE WHEN event = 'order_completed' THEN anonymous_id END) as conversions,
       ROUND(100.0 * conversions / NULLIF(visitors, 0), 2) as cvr
FROM rudder_cdp.tracks WHERE context_source_id = '{SOURCE_ID}'
GROUP BY 1, 2 ORDER BY visitors DESC;

-- Screen size distribution
SELECT context_screen_width, context_screen_height, COUNT(*) as sessions
FROM rudder_cdp.pages WHERE context_source_id = '{SOURCE_ID}'
GROUP BY 1, 2 ORDER BY sessions DESC LIMIT 10;

-- OS breakdown
SELECT context_os_name, context_os_version, COUNT(DISTINCT anonymous_id) as users
FROM rudder_cdp.tracks WHERE context_source_id = '{SOURCE_ID}'
GROUP BY 1, 2 ORDER BY users DESC;
```

**Product Performance:**
```sql
-- Top viewed products
SELECT product_id, name, COUNT(*) as views,
       COUNT(DISTINCT anonymous_id) as unique_viewers
FROM rudder_cdp.product_viewed WHERE context_source_id = '{SOURCE_ID}'
GROUP BY 1, 2 ORDER BY views DESC LIMIT 20;

-- Product add-to-cart rate
SELECT pv.product_id, pv.name, 
       COUNT(DISTINCT pv.anonymous_id) as viewers,
       COUNT(DISTINCT pa.anonymous_id) as adders,
       ROUND(100.0 * COUNT(DISTINCT pa.anonymous_id) / NULLIF(COUNT(DISTINCT pv.anonymous_id), 0), 2) as atc_rate
FROM rudder_cdp.product_viewed pv
LEFT JOIN rudder_cdp.product_added pa ON pv.product_id = pa.product_id AND pv.anonymous_id = pa.anonymous_id
WHERE pv.context_source_id = '{SOURCE_ID}'
GROUP BY 1, 2 ORDER BY viewers DESC LIMIT 20;

-- Products frequently abandoned
SELECT pa.product_id, pa.name, COUNT(*) as times_added,
       COUNT(DISTINCT oc.order_id) as times_purchased,
       ROUND(100.0 * (COUNT(*) - COUNT(DISTINCT oc.order_id)) / NULLIF(COUNT(*), 0), 1) as abandon_rate
FROM rudder_cdp.product_added pa
LEFT JOIN rudder_cdp.order_completed oc ON pa.checkout_id = oc.checkout_id
WHERE pa.context_source_id = '{SOURCE_ID}'
GROUP BY 1, 2 ORDER BY abandon_rate DESC LIMIT 20;

-- Category performance
SELECT category, COUNT(DISTINCT product_id) as products,
       SUM(quantity) as units_sold, SUM(price * quantity) as revenue
FROM rudder_cdp.order_completed, UNNEST(products) as p
WHERE context_source_id = '{SOURCE_ID}'
GROUP BY 1 ORDER BY revenue DESC;
```

**Search & Discovery:**
```sql
-- Top search queries
SELECT query, COUNT(*) as searches, COUNT(DISTINCT anonymous_id) as searchers
FROM rudder_cdp.search_submitted WHERE context_source_id = '{SOURCE_ID}'
GROUP BY 1 ORDER BY searches DESC LIMIT 30;

-- Search-to-purchase conversion
SELECT ss.query, COUNT(DISTINCT ss.anonymous_id) as searchers,
       COUNT(DISTINCT oc.anonymous_id) as purchasers
FROM rudder_cdp.search_submitted ss
LEFT JOIN rudder_cdp.order_completed oc ON ss.anonymous_id = oc.anonymous_id
WHERE ss.context_source_id = '{SOURCE_ID}'
GROUP BY 1 ORDER BY searchers DESC LIMIT 20;
```

**Customer Behavior:**
```sql
-- Time to purchase (sessions before converting)
SELECT anonymous_id, MIN(timestamp) as first_visit, 
       MIN(CASE WHEN event = 'order_completed' THEN timestamp END) as first_purchase,
       DATE_DIFF(first_purchase, first_visit, DAY) as days_to_convert
FROM rudder_cdp.tracks WHERE context_source_id = '{SOURCE_ID}'
GROUP BY 1 HAVING first_purchase IS NOT NULL;

-- Repeat purchase rate
SELECT user_id, COUNT(DISTINCT order_id) as orders, SUM(revenue) as ltv
FROM rudder_cdp.order_completed WHERE context_source_id = '{SOURCE_ID}'
GROUP BY 1 ORDER BY orders DESC;

-- Geographic distribution
SELECT context_locale, context_timezone,
       COUNT(DISTINCT anonymous_id) as visitors,
       COUNT(DISTINCT CASE WHEN event = 'order_completed' THEN anonymous_id END) as buyers
FROM rudder_cdp.tracks WHERE context_source_id = '{SOURCE_ID}'
GROUP BY 1, 2 ORDER BY visitors DESC;
```

#### PostHog Data

**Session Analysis:**
```bash
# Session recordings with rage clicks (UX friction points)
curl -X POST 'https://app.posthog.com/api/projects/{PROJECT_ID}/session_recordings' \
  -H "Authorization: Bearer {POSTHOG_API_KEY}" \
  -d '{"filter": {"events": [{"id": "$rageclick"}]}}'

# Dead clicks (clicked but nothing happened)
curl -X POST 'https://app.posthog.com/api/projects/{PROJECT_ID}/session_recordings' \
  -H "Authorization: Bearer {POSTHOG_API_KEY}" \
  -d '{"filter": {"events": [{"id": "$dead_click"}]}}'

# Sessions with errors
curl -X POST 'https://app.posthog.com/api/projects/{PROJECT_ID}/session_recordings' \
  -H "Authorization: Bearer {POSTHOG_API_KEY}" \
  -d '{"filter": {"events": [{"id": "$exception"}]}}'

# Long sessions (potential confusion)
curl -X POST 'https://app.posthog.com/api/projects/{PROJECT_ID}/session_recordings' \
  -H "Authorization: Bearer {POSTHOG_API_KEY}" \
  -d '{"filter": {"duration": {"gt": 600}}}'  # >10 min sessions
```

**Funnel Analysis:**
```bash
# Full checkout funnel
curl -X POST 'https://app.posthog.com/api/projects/{PROJECT_ID}/insights/funnel' \
  -H "Authorization: Bearer {POSTHOG_API_KEY}" \
  -d '{"events": [
    {"id": "$pageview", "properties": {"$current_url": {"$regex": "/products/"}}},
    {"id": "add_to_cart"},
    {"id": "begin_checkout"},
    {"id": "add_payment_info"},
    {"id": "purchase"}
  ]}'

# Funnel by device
curl -X POST 'https://app.posthog.com/api/projects/{PROJECT_ID}/insights/funnel' \
  -H "Authorization: Bearer {POSTHOG_API_KEY}" \
  -d '{"events": [...], "breakdown": "$device_type"}'

# Funnel by traffic source
curl -X POST 'https://app.posthog.com/api/projects/{PROJECT_ID}/insights/funnel' \
  -H "Authorization: Bearer {POSTHOG_API_KEY}" \
  -d '{"events": [...], "breakdown": "utm_source"}'
```

**Heatmaps & Scroll:**
```bash
# Toolbar heatmap (click heatmap for specific URL)
# Access via PostHog toolbar: https://app.posthog.com/toolbar?url={STORE_URL}

# Scroll depth insights
curl -X POST 'https://app.posthog.com/api/projects/{PROJECT_ID}/insights' \
  -H "Authorization: Bearer {POSTHOG_API_KEY}" \
  -d '{"insight": "TRENDS", "events": [{"id": "$pageview"}], 
       "properties": [{"key": "$viewport_height", "type": "event"}]}'
```

**Path Analysis:**
```bash
# User paths from homepage
curl -X POST 'https://app.posthog.com/api/projects/{PROJECT_ID}/insights/path' \
  -H "Authorization: Bearer {POSTHOG_API_KEY}" \
  -d '{"start_point": "/", "path_type": "url"}'

# Paths leading to purchase
curl -X POST 'https://app.posthog.com/api/projects/{PROJECT_ID}/insights/path' \
  -H "Authorization: Bearer {POSTHOG_API_KEY}" \
  -d '{"end_point": "purchase", "path_type": "event"}'

# Drop-off paths (where do people leave?)
curl -X POST 'https://app.posthog.com/api/projects/{PROJECT_ID}/insights/path' \
  -H "Authorization: Bearer {POSTHOG_API_KEY}" \
  -d '{"drop_off": true}'
```

**Performance & Errors:**
```bash
# Page load times
curl -X POST 'https://app.posthog.com/api/projects/{PROJECT_ID}/insights' \
  -H "Authorization: Bearer {POSTHOG_API_KEY}" \
  -d '{"insight": "TRENDS", "events": [{"id": "$web_vitals"}],
       "properties": [{"key": "LCP"}, {"key": "FID"}, {"key": "CLS"}]}'

# JavaScript errors
curl -X POST 'https://app.posthog.com/api/projects/{PROJECT_ID}/insights' \
  -H "Authorization: Bearer {POSTHOG_API_KEY}" \
  -d '{"insight": "TRENDS", "events": [{"id": "$exception"}], "breakdown": "$exception_message"}'

# Network errors
curl -X POST 'https://app.posthog.com/api/projects/{PROJECT_ID}/insights' \
  -H "Authorization: Bearer {POSTHOG_API_KEY}" \
  -d '{"insight": "TRENDS", "events": [{"id": "$network_request"}], 
       "properties": [{"key": "status", "value": "4xx|5xx", "operator": "regex"}]}'
```

**Feature Flags & Experiments:**
```bash
# A/B test results
curl -X GET 'https://app.posthog.com/api/projects/{PROJECT_ID}/experiments' \
  -H "Authorization: Bearer {POSTHOG_API_KEY}"

# Feature flag exposure
curl -X POST 'https://app.posthog.com/api/projects/{PROJECT_ID}/insights' \
  -H "Authorization: Bearer {POSTHOG_API_KEY}" \
  -d '{"insight": "TRENDS", "events": [{"id": "$feature_flag_called"}], "breakdown": "$feature_flag"}'
```

**Cohort Analysis:**
```bash
# Retention by signup cohort
curl -X POST 'https://app.posthog.com/api/projects/{PROJECT_ID}/insights/retention' \
  -H "Authorization: Bearer {POSTHOG_API_KEY}" \
  -d '{"target_entity": {"id": "purchase"}, "returning_entity": {"id": "purchase"}}'

# Lifecycle analysis
curl -X POST 'https://app.posthog.com/api/projects/{PROJECT_ID}/insights/lifecycle' \
  -H "Authorization: Bearer {POSTHOG_API_KEY}" \
  -d '{"events": [{"id": "purchase"}]}'
```

#### Shopify Admin API

**Store Overview:**
```bash
# Shop info
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/shop.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"

# Store analytics reports
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/reports.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"
```

**Orders & Revenue:**
```bash
# Recent orders
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/orders.json?status=any&limit=250" \
  -H "X-Shopify-Access-Token: {TOKEN}"

# Order count for CVR calculation
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/orders/count.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"

# Orders by financial status
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/orders.json?financial_status=paid" \
  -H "X-Shopify-Access-Token: {TOKEN}"

# Refunds (return rate indicator)
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/orders.json?financial_status=refunded" \
  -H "X-Shopify-Access-Token: {TOKEN}"
```

**Abandoned Checkouts:**
```bash
# All abandoned checkouts
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/checkouts.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"

# Abandoned checkout count
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/checkouts/count.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"

# Specific abandoned checkout details
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/checkouts/{CHECKOUT_TOKEN}.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"
```

**Products:**
```bash
# All products
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/products.json?limit=250" \
  -H "X-Shopify-Access-Token: {TOKEN}"

# Product count
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/products/count.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"

# Products with inventory
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/inventory_levels.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"

# Product variants (for size/color analysis)
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/variants.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"
```

**Customers:**
```bash
# Customer list
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/customers.json?limit=250" \
  -H "X-Shopify-Access-Token: {TOKEN}"

# Customer count
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/customers/count.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"

# Customer orders count
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/customers/{CUSTOMER_ID}/orders.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"

# Customers by location
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/customers/search.json?query=country:Pakistan" \
  -H "X-Shopify-Access-Token: {TOKEN}"
```

**Collections & Navigation:**
```bash
# Collections
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/custom_collections.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"

curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/smart_collections.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"

# Navigation menus
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/menus.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"
```

**Theme & Assets:**
```bash
# Current theme
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/themes.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"

# Theme assets (check for customizations)
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/themes/{THEME_ID}/assets.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"
```

**Discounts & Marketing:**
```bash
# Price rules
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/price_rules.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"

# Discount codes
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/price_rules/{PRICE_RULE_ID}/discount_codes.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"

# Marketing events
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/marketing_events.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"
```

**Shipping & Locations:**
```bash
# Shipping zones
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/shipping_zones.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"

# Locations
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/locations.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"

# Fulfillment services
curl -X GET "https://{STORE}.myshopify.com/admin/api/2024-01/fulfillment_services.json" \
  -H "X-Shopify-Access-Token: {TOKEN}"
```

---

### 3. Capture & Annotate Screenshots

**CRITICAL: 70% of e-commerce traffic is mobile.** You MUST capture both desktop AND mobile screenshots for every page.

#### Required Screenshots (MANDATORY)

| Page | Desktop (1440px) | Mobile (390px) |
|------|------------------|----------------|
| Homepage | ✓ | ✓ |
| Product Page | ✓ | ✓ |
| Cart | ✓ | ✓ |
| Checkout | ✓ | ✓ |

**Total: 8 screenshots minimum (4 pages × 2 viewports)**

#### Capture Process

```
# Start browser
browser action=start profile=hazn

# === HOMEPAGE ===
# Desktop
browser action=open targetUrl="https://{store}"
browser action=act request='{"kind":"resize","width":1440,"height":900}'
browser action=screenshot fullPage=true  # → homepage-desktop.jpg

# Mobile
browser action=act request='{"kind":"resize","width":390,"height":844}'
browser action=screenshot fullPage=true  # → homepage-mobile.jpg

# === PRODUCT PAGE ===
# Navigate to a product
browser action=navigate targetUrl="https://{store}/collections/all"
browser action=snapshot  # Get element refs
browser action=navigate targetUrl="https://{store}/products/{product-slug}"

# Desktop
browser action=act request='{"kind":"resize","width":1440,"height":900}'
browser action=screenshot fullPage=true  # → product-desktop.jpg

# Mobile
browser action=act request='{"kind":"resize","width":390,"height":844}'
browser action=screenshot fullPage=true  # → product-mobile.jpg

# === CART & CHECKOUT ===
# Add item to cart first
browser action=snapshot
browser action=act request='{"kind":"click","ref":"[add-to-cart-button]"}'

# Cart - Desktop
browser action=navigate targetUrl="https://{store}/cart"
browser action=act request='{"kind":"resize","width":1440,"height":900}'
browser action=screenshot fullPage=true  # → cart-desktop.jpg

# Cart - Mobile
browser action=act request='{"kind":"resize","width":390,"height":844}'
browser action=screenshot fullPage=true  # → cart-mobile.jpg

# Checkout - Desktop
browser action=navigate targetUrl="https://{store}/checkout"
browser action=act request='{"kind":"resize","width":1440,"height":900}'
browser action=screenshot fullPage=true  # → checkout-desktop.png

# Checkout - Mobile
browser action=act request='{"kind":"resize","width":390,"height":844}'
browser action=screenshot fullPage=true  # → checkout-mobile.png
```

#### Save Screenshots to Report Assets

```bash
# Create assets folder for this audit
mkdir -p ~/hazn/landing-pages/audits/{store-name}-assets/

# Copy screenshots
cp ~/.hazn/media/browser/*.jpg ~/hazn/landing-pages/audits/{store-name}-assets/
cp ~/.hazn/media/browser/*.png ~/hazn/landing-pages/audits/{store-name}-assets/
```

#### Display in Report: Desktop + Mobile Side-by-Side

**Layout: Grid with desktop (2fr) and mobile (1fr) columns, constrained height**

```html
<!-- Desktop + Mobile side by side -->
<div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 40px;">
    <!-- Desktop -->
    <div class="screenshot-annotated" style="position: relative; border-radius: 12px; overflow: hidden; border: 1px solid var(--border-subtle);">
        <div style="padding: 8px 12px; background: var(--bg-card); font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em;">💻 Desktop</div>
        <img src="{store}-assets/homepage-desktop.jpg" alt="Homepage Desktop" style="width: 100%; display: block; max-height: 400px; object-fit: cover; object-position: top;">
        <!-- CSS overlay callouts -->
        <div class="callout" style="position: absolute; top: 15%; left: 50%; transform: translateX(-50%); width: 24px; height: 24px; background: var(--accent-red); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px; color: white;">1</div>
        <div class="callout" style="position: absolute; top: 25%; right: 8%; width: 24px; height: 24px; background: var(--accent-red); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px; color: white;">2</div>
    </div>
    <!-- Mobile -->
    <div class="screenshot-annotated" style="position: relative; border-radius: 12px; overflow: hidden; border: 1px solid var(--border-subtle);">
        <div style="padding: 8px 12px; background: var(--bg-card); font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em;">📱 Mobile (70% traffic)</div>
        <img src="{store}-assets/homepage-mobile.jpg" alt="Homepage Mobile" style="width: 100%; display: block; max-height: 400px; object-fit: cover; object-position: top;">
        <!-- Mobile-specific callouts -->
        <div class="callout" style="position: absolute; top: 12%; left: 50%; transform: translateX(-50%); width: 24px; height: 24px; background: var(--accent-red); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px; color: white;">1</div>
    </div>
</div>
<!-- Issue Legend -->
<div style="padding: 12px 16px; background: var(--bg-card); border-radius: 8px; margin-bottom: 40px; font-size: 13px; color: var(--text-muted);">
    <strong>Key Issues:</strong> 
    <span style="color: var(--accent-red);">❶</span> No trust badges above fold · 
    <span style="color: var(--accent-red);">❷</span> No WhatsApp button · 
    No free shipping banner
</div>
```

#### Screenshot Styling Rules

1. **Size**: Constrain with `max-height: 400px` and `object-fit: cover; object-position: top`
2. **Grid**: Desktop gets 2fr, mobile gets 1fr (side-by-side)
3. **Labels**: Show device type + traffic percentage for mobile
4. **Callouts**: Use CSS positioned circles (not image editing)
5. **Legend**: Always include issue legend below screenshot pair

#### CSS Overlay Annotations (Preferred Method)

Use CSS positioned elements instead of image editing. This is:
- Easier to update
- Responsive
- No image processing required

**Callout Styles:**
```css
.callout {
    position: absolute;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 12px;
    color: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
/* Critical - Red */
.callout.critical { background: #ff3c3c; }
/* High - Yellow */
.callout.high { background: #ffaa00; color: #0a0a12; }
/* Quick win - Green */
.callout.quick { background: #00d564; }
```

**Position callouts using percentage-based positioning:**
- `top: 15%; left: 50%` — relative to screenshot container
- This works across different screen sizes

#### Annotation Color Coding

| Color | Hex | Usage |
|-------|-----|-------|
| 🔴 Red | #ff3c3c | Critical issues |
| 🟡 Yellow | #ffaa00 | High priority |
| 🟢 Green | #00d564 | Quick wins / what's working |

#### Mobile-Specific Observations

When reviewing mobile screenshots, specifically check:
- [ ] Is add-to-cart button sticky? (Should stay visible on scroll)
- [ ] Are touch targets at least 44px?
- [ ] Is text readable without zooming?
- [ ] Are forms easy to complete on mobile?
- [ ] Do images load on mobile? (Some lazy-loading breaks on mobile)
- [ ] Is WhatsApp button present? (Critical for Pakistan/MENA)

---

### 4. Evaluate Each Page

**Use the `ui-audit` skill** for design evaluation. Load `../ui-audit/SKILL.md` and apply:
- Visual hierarchy assessment
- Accessibility checks
- Cognitive load analysis
- Pattern recommendations

Score each page on these **Shopify + market-specific criteria** (1-10):

#### Homepage Audit

| Element | What to Check | Market Variations |
|---------|--------------|-------------------|
| Hero/Above-fold | Clear value prop? Strong CTA? | Pakistan/MENA: WhatsApp CTA often outperforms |
| Navigation | Logical categories? Search prominent? | RTL support for Arabic markets |
| Trust signals | Reviews, press, security badges? | Pakistan: COD badge critical |
| Featured products | Best sellers showcased? | Show local bestsellers per market |
| Load speed | FCP < 2s? LCP < 2.5s? | Critical for emerging markets with slower connections |
| Mobile experience | Thumb-friendly? No horizontal scroll? | 70%+ traffic is mobile in most markets |

#### Product Page Audit

| Element | What to Check | Market Variations |
|---------|--------------|-------------------|
| Product images | High quality? Multiple angles? Zoom? | Video crucial for fashion/beauty |
| Price display | Clear? Compare-at? | Pakistan: Show EMI options |
| Buy button | Above fold? High contrast? Sticky? | Mobile sticky ATC = +15-25% CVR |
| Product description | Benefits > features? Scannable? | Localized copy for each market |
| Social proof | Reviews? Star rating? | Pakistan: Instagram proof > formal reviews |
| Urgency/scarcity | Stock levels? Limited offers? | "Only X left" = +37% urgency purchases |
| Cross-sells | Related products shown? | "Complete the look" for fashion |
| Shipping info | Delivery estimates? Free threshold? | Pakistan: Free over PKR 5000 is standard |
| Size guides | Detailed? Fit calculator? | Reduces returns by 64% |
| Payment badges | COD? BNPL? Local methods? | Market-specific payment visibility |

#### Cart Page Audit

| Element | What to Check | Market Variations |
|---------|--------------|-------------------|
| Cart summary | Clear items? Easy edit? | Show images always |
| Checkout CTA | Prominent? Multiple positions? | Express checkout = +30% completion |
| Trust badges | Payment icons? Security? | COD badge for Pakistan/MENA |
| Upsells | Cart recommendations? | Free shipping progress bar = +26% AOV |
| Promo code | Visible but not distracting? | Don't over-emphasize (causes abandonment searching for codes) |
| Express checkout | Shop Pay / Apple Pay / PayPal? | Local wallets for each market |

#### Checkout Audit

| Element | What to Check | Market Variations |
|---------|--------------|-------------------|
| Guest checkout | Available? Not hidden? | 26% abandon if forced to register |
| Form fields | Minimal? Autofill works? | Pakistan: phone field prominent |
| Progress indicator | Clear steps? | Reduces anxiety |
| Payment options | Multiple methods? | COD often 40-60% of orders in Pakistan |
| Order summary | Visible throughout? | Reduces cart abandonment |
| Trust signals | SSL? Guarantee? | Final reassurance before purchase |

---

### 5. Market-Specific Best Practices

#### Pakistan / South Asia
- **COD is king** — 40-60% of orders; badge it prominently
- **WhatsApp support** — Floating button is expected, not optional
- **Free shipping threshold** — PKR 3000-5000 is standard
- **EMI/installments** — Partner with local BNPL providers
- **Cash price vs card price** — Some show different prices
- **Local reviews** — Show Pakistani customer testimonials
- **Mobile-first** — 80%+ traffic; optimize aggressively
- **Slow connections** — Image compression critical

#### UAE / Saudi / MENA
- **COD still significant** — 30-50% of orders
- **Mada (Saudi)** — Local debit card, must support
- **Tabby / Tamara** — Popular BNPL in region
- **Arabic RTL** — Full RTL support if targeting Arabic speakers
- **Luxury perception** — Premium packaging messaging works
- **Fast delivery** — Same-day/next-day expected in cities

#### US / UK / EU
- **Express checkout** — Shop Pay, Apple Pay, Google Pay expected
- **Free shipping** — Often expected over $50-75
- **Reviews** — Verified purchase badges important
- **Returns policy** — Prominent, generous returns = +trust
- **BNPL** — Klarna, Afterpay, Affirm popular
- **Sustainability** — Eco-friendly messaging resonates

---

### 6. CRO Best Practices & Benchmarks

**Reference:** `references/benchmarks.md` — Full benchmark data with sources

Load benchmarks for the client's industry and compare their current CVR.

#### Quick Reference (see benchmarks.md for full data)

**Speed Impact:**
- 1 second faster = +7% CVR
- Sub-2 second load = +15% CVR
- Mobile delay = -20% CVR per second

**Top Tactics by Impact:**
| Tactic | Impact | Effort |
|--------|--------|--------|
| Shop Pay vs guest | +50% CVR | Low |
| Mobile sticky ATC | +15-25% CVR | Low |
| Reviews | +58% purchase likelihood | Medium |
| BNPL | +30% checkout completion | Low |
| Product videos | +46% CVR | Medium |
| Size guides | -64% returns | Medium |

**Cart Abandonment:** 70-85% (mobile highest)

#### Key Psychological Principles
- **Loss aversion** — "Only 3 left" > "In stock"
- **Social proof** — "500+ customers" > no mention
- **Anchoring** — Show compare-at price first
- **Reciprocity** — Free shipping threshold drives AOV
- **Urgency** — Countdown timers work (but don't abuse)

When writing the report, pull specific benchmarks from `references/benchmarks.md` for:
- Industry CVR comparison
- Market-specific benchmarks
- Tactic impact projections
- Revenue impact calculations

---

### 7. Identify Top Issues

Prioritize by impact × effort:

**🔴 Critical (Fix immediately)**
- Broken checkout flow
- Missing/buried buy buttons
- Major mobile usability issues
- No trust signals at checkout
- Slow load times (>4s)
- Payment method mismatch for market

**🟡 High Impact (This week)**
- Weak value proposition
- Poor product photography
- Missing reviews/social proof
- Confusing navigation
- No urgency elements
- Missing market-specific payment options

**🟢 Quick Wins (Easy improvements)**
- Add trust badges
- Improve CTA button contrast
- Add free shipping threshold bar
- Enable express checkout
- Add product recommendations
- Add WhatsApp button (for applicable markets)

---

### 8. Generate Recommendations

For each issue, provide:
- **Current state**: Screenshot/description
- **Recommended change**: Specific improvement
- **Why it matters**: Psychological/conversion principle
- **Expected impact**: CVR lift estimate with revenue projection
- **Implementation**: Shopify steps, app recommendations, or code
- **Effort**: Low/Medium/High
- **Priority**: Critical/High/Medium/Low

---

### 9. Build HTML Report

**USE THE TEMPLATE:** Load `assets/template-audit.html` as the base. This template includes all Autonomous branding:
- Fixed header with logo + "AUTONOMOUS"
- Radial gradient cover with circular score ring
- Section numbers (01, 02, etc.)
- Glassmorphic cards with hover effects
- Gradient text headings
- Positioning statement: "Canadian Expertise. Pakistani Efficiency. World-class Quality."
- Branded footer

**Replace placeholders in template:**
- `{{STORE_NAME}}` → Store name
- `{{STORE_URL}}` → Store domain
- `{{SCORE}}` → Overall CRO score (0-100)
- `{{DATE}}` → Audit date (e.g., "February 6, 2026")

**CSS Classes Reference:**

Issue severity:
- `.issue-number.critical` — Red (#ff3c3c)
- `.issue-number.high` — Yellow (#fbbf24)
- `.issue-number.ok` — Green (#00d564)

Effort badges:
- `.effort-badge.low` — Green
- `.effort-badge.medium` — Cyan
- `.effort-badge.high` — Yellow

Score bars:
- `.score-bar-fill.excellent` — Green (80%+)
- `.score-bar-fill.good` — Cyan (60-79%)
- `.score-bar-fill.needs-work` — Yellow (40-59%)
- `.score-bar-fill.poor` — Red (<40%)

**Report Sections:**

1. **Cover / Hero**
   - Autonomous logo (MANDATORY)
   - "AUTONOMOUS" text + positioning tagline
   - Store name + audit date
   - Overall CRO score (0-100)

2. **Executive Summary**
   - Current CVR vs industry benchmark (from `references/benchmarks.md`)
   - Top 3 priority issues with thumbnails
   - Projected CVR improvement
   - Revenue impact estimate

3. **Data Insights** (if CDP/PostHog available)
   - Funnel visualization
   - Drop-off points
   - Device breakdown
   - Traffic source performance

4. **Homepage Audit**
   - **Annotated screenshot** with numbered callouts (boxes + arrows)
   - Issues list matching callout numbers
   - Score breakdown table
   - Recommendations with "Before → After" descriptions

5. **Product Page Audit**
   - **Annotated screenshot** (desktop + mobile)
   - Issues list with callout numbers
   - Score breakdown
   - Specific recommendations with mockup descriptions

6. **Cart & Checkout Audit**
   - **Annotated screenshots** of cart and checkout
   - Funnel drop-off data if available
   - Issues list with callouts
   - Recommendations

7. **Market-Specific Recommendations**
   - Localization opportunities
   - Payment method gaps (with visual examples)
   - Shipping/trust signal gaps

8. **Quick Wins Checklist**
   - Visual checklist with thumbnails
   - Effort estimates
   - Expected impact (from benchmarks)

9. **Implementation Roadmap**
   - Week 1-2: Critical fixes (annotated screenshots)
   - Week 3-4: High impact
   - Month 2: Optimization
   - Ongoing: A/B testing

10. **Appendix**
    - Full annotated screenshots gallery
    - CVR benchmarks by industry (from `references/benchmarks.md`)
    - Shopify app recommendations
    - Technical implementation guides

#### Screenshot Requirements for Report

Every audit section MUST include:

```html
<section class="audit-section">
  <h2>Homepage Audit</h2>
  
  <!-- Annotated Screenshot -->
  <div class="screenshot-container">
    <img src="homepage-annotated.png" alt="Homepage with issues marked">
    <div class="screenshot-caption">Homepage - Desktop View (issues highlighted)</div>
  </div>
  
  <!-- Issue Legend -->
  <div class="issues-legend">
    <div class="issue critical">
      <span class="callout">1</span>
      <div class="issue-content">
        <strong>No trust badges above fold</strong>
        <p>Trust signals should be visible without scrolling. Add payment + security badges near CTA.</p>
        <span class="impact">Impact: +42% checkout completion</span>
      </div>
    </div>
    <div class="issue high">
      <span class="callout">2</span>
      <div class="issue-content">
        <strong>Weak hero CTA contrast</strong>
        <p>"Shop Now" button blends with background. Use high-contrast color.</p>
        <span class="impact">Impact: +24% CTA clicks</span>
      </div>
    </div>
    <!-- ... more issues -->
  </div>
  
  <!-- Before/After Comparison (optional mockup) -->
  <div class="before-after">
    <div class="before">
      <h4>Current</h4>
      <img src="homepage-current.png">
    </div>
    <div class="after">
      <h4>Recommended</h4>
      <img src="homepage-mockup.png">
      <!-- OR text description if no mockup -->
      <div class="mockup-description">
        <ul>
          <li>→ Add trust badge row below hero</li>
          <li>→ Change CTA to cyan (#00d5ff) background</li>
          <li>→ Add "Free shipping over PKR 5000" banner</li>
        </ul>
      </div>
    </div>
  </div>
</section>
```

#### Annotation Styling (CSS)

```css
.callout {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-weight: 700;
  font-size: 14px;
  color: white;
}
.issue.critical .callout { background: #ff3c3c; }
.issue.high .callout { background: #ffaa00; }
.issue.medium .callout { background: #ffd500; color: #0a0a12; }
.issue.quick-win .callout { background: #00d564; }

.screenshot-container {
  position: relative;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  overflow: hidden;
  margin: 24px 0;
}
.screenshot-container img {
  width: 100%;
  display: block;
}
```

---

### 10. Publish Report

```bash
# Save to autonomous-proposals repo
mkdir -p ~/hazn/autonomous-proposals/audits
# Write report to ~/hazn/autonomous-proposals/audits/{store-name}-cro-audit-{date}.html

# Deploy
cd ~/hazn/autonomous-proposals
git add audits/
git commit -m "Add {store-name} CRO audit report"
git pull --rebase origin main && git push origin main

# Report URL:
# https://pages.autonomoustech.ca/audits/{store-name}-cro-audit-{date}.html
```

---

## Shopify App Recommendations by Issue

| Issue | Recommended Apps | Notes |
|-------|-----------------|-------|
| No reviews | Judge.me, Loox, Stamped.io | Judge.me has best free tier |
| Slow speed | Hyperspeed, TinyIMG | Image optimization critical |
| No urgency | Hurrify, Ultimate Scarcity | Don't overdo fake urgency |
| Cart abandonment | Klaviyo, Privy, Omnisend | Email + SMS recovery |
| No upsells | ReConvert, Bold Upsell, Candy Rack | Post-purchase upsells too |
| Poor search | Searchanise, Algolia | AI-powered recommendations |
| No trust badges | Trust Badges Bear, Vitals | Payment + security badges |
| No BNPL | Klarna, Afterpay, Tabby (MENA) | Market-specific |
| No WhatsApp | WhatsApp Chat Button, Zoko | Essential for Pakistan/MENA |
| Size issues | Kiwi Size Chart, True Fit | Reduce returns |
| No video | Videowise, Vimeo Create | Product videos |

---

## Additional Ideas

### Advanced Audit Capabilities

1. **Competitor Benchmarking**
   - Screenshot 2-3 competitors
   - Compare UX patterns
   - Identify differentiation opportunities

2. **Heatmap Analysis**
   - If Hotjar/Clarity access available
   - Click maps, scroll maps, attention maps
   - Identify rage clicks and dead zones

3. **Page Speed Deep Dive**
   - Lighthouse audit integration
   - Core Web Vitals breakdown
   - Specific optimization recommendations

4. **SEO Quick Scan**
   - Meta tags presence
   - Schema markup
   - Mobile-friendliness
   - (Cross-reference with `seo-audit` skill)

5. **Accessibility Audit**
   - WCAG compliance check
   - Screen reader compatibility
   - Color contrast issues
   - (Use `ui-audit` skill patterns)

6. **Email/SMS Flow Audit**
   - Abandoned cart sequence review
   - Welcome series evaluation
   - Post-purchase flow assessment

7. **Pricing Psychology Audit**
   - Anchoring effectiveness
   - Bundle strategies
   - Discount presentation

8. **Trust Architecture Audit**
   - Review authenticity
   - Social proof distribution
   - Security perception

### Automation Opportunities

1. **Scheduled Re-audits**
   - Monthly progress tracking
   - Before/after comparison
   - CVR trend monitoring

2. **Alert System**
   - Notify on CVR drops
   - Page speed degradation alerts
   - Checkout error monitoring

3. **A/B Test Tracking**
   - Document test hypotheses
   - Track results
   - Build optimization playbook

---

## Related Skills

- `ui-audit` — Deep UX/UI pattern analysis (LOAD FOR EVERY AUDIT)
- `brand-guide` — Autonomous brand styling for reports (LOAD FOR REPORT GENERATION)
- `conversion-audit` — General landing page audits
- `seo-audit` — SEO technical analysis
- `landing-page-copywriter` — Copy improvement recommendations

---

## References

- `references/cdp-schema.md` — RudderStack CDP table schema
- `references/checklist-homepage.md` — Detailed homepage criteria
- `references/checklist-product.md` — Product page checklist
- `references/checklist-cart.md` — Cart & checkout checklist
- `references/benchmarks.md` — Industry CVR benchmarks
- `references/market-practices.md` — Market-specific best practices
- `references/app-recommendations.md` — Shopify app directory

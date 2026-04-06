# Analytics Audit: example.com

## Executive Summary

The analytics implementation for example.com has significant gaps in tracking coverage, data quality, and marketing attribution. Google Analytics 4 is installed but misconfigured, resulting in inflated session counts and missing conversion data. Google Tag Manager is present but contains 4 unused tags and 2 firing triggers that generate console errors.

## Findings

### Finding 1: GA4 Cross-Domain Tracking Misconfigured

- **Severity**: High
- **Description**: The GA4 property tracks the main site (example.com) and the checkout subdomain (checkout.example.com) as separate sessions. Users completing a purchase are counted as two separate sessions with two different client IDs, inflating session counts by an estimated 18-22% and breaking the conversion funnel.
- **Evidence**: GA4 debug mode shows different `client_id` values when navigating from example.com to checkout.example.com. The GA4 admin panel shows cross-domain tracking is not configured. Comparing server-side order count (1,240/month) to GA4 purchase events (980/month) reveals a 21% discrepancy.
- **Recommendation**: Configure GA4 cross-domain tracking to include both example.com and checkout.example.com. Add both domains to the "Configure your domains" section in GA4 Admin > Data Streams > Web stream details. Verify with debug mode that client_id persists across domain boundary.

### Finding 2: Missing E-commerce Event Tracking

- **Severity**: High
- **Description**: Only the `purchase` event is implemented. The full e-commerce funnel events (`view_item`, `add_to_cart`, `begin_checkout`, `add_shipping_info`, `add_payment_info`) are not firing. This prevents funnel analysis, audience building for remarketing, and accurate ROAS calculation.
- **Evidence**: GA4 DebugView shows no `view_item` or `add_to_cart` events during a complete browse-to-purchase user journey. The GTM container has no tags configured for these events. GA4 Monetization reports show purchase data but empty funnel visualization.
- **Recommendation**: Implement the full GA4 e-commerce event taxonomy via GTM. Push a dataLayer event for each funnel step from the application code. Use GTM triggers to fire corresponding GA4 event tags. Test each event in GA4 DebugView before publishing.

### Finding 3: Tag Manager Container Contains Dead Tags

- **Severity**: Low
- **Description**: The GTM container has 4 tags that are paused or reference removed triggers, and 2 active tags firing on triggers that generate JavaScript console errors. The dead tags add unnecessary payload to the container snippet, and the error-generating tags may affect site performance and data quality.
- **Evidence**: GTM audit shows tags "Old Facebook Pixel" (paused since 2024-08), "Legacy Hotjar" (trigger deleted), "Test Conversion Tag" (no trigger), and "Draft Remarketing" (paused). Active tags "Custom HTML - Chat Widget" and "Custom HTML - Exit Intent" throw `TypeError: Cannot read property 'style' of null` on 3 page templates where the target DOM element doesn't exist.
- **Recommendation**: Remove the 4 dead tags from the GTM container. Fix the 2 error-generating tags by adding null checks before DOM manipulation. Implement a GTM container audit as a quarterly maintenance task.

## Recommendations

1. **Immediate**: Configure GA4 cross-domain tracking for example.com and checkout.example.com
2. **Week 1-2**: Implement full e-commerce event tracking via GTM dataLayer
3. **Week 2**: Clean up GTM container -- remove dead tags, fix error-generating tags
4. **Month 2**: Set up GA4 custom dimensions for user segments and campaign attribution
5. **Ongoing**: Quarterly GTM container audit and GA4 data quality review

## Metadata

| Field | Value |
|-------|-------|
| Audit Date | 2026-02-20 |
| Domain | example.com |
| GA4 Property | G-XXXXXXXXXX |
| GTM Container | GTM-XXXXXXX |
| Tools Used | GA4 DebugView, GTM Preview Mode, Chrome DevTools |

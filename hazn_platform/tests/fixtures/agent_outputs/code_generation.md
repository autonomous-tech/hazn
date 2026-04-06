# GTM Implementation: Custom Event Tracking

## Overview

This implementation adds Google Tag Manager dataLayer pushes for the full GA4 e-commerce funnel. The code covers `view_item`, `add_to_cart`, and `begin_checkout` events with proper item-level data.

The dataLayer events follow the GA4 recommended e-commerce schema, ensuring compatibility with standard GA4 reports and BigQuery export.

## Implementation Files

### Product Page Event Tracking

This module handles the `view_item` event when a user views a product detail page, and the `add_to_cart` event when they click the add-to-cart button.

```artifact javascript src/tracking/gtm-setup.js
/**
 * GTM DataLayer Push Utilities
 *
 * Provides helper functions for pushing GA4 e-commerce events
 * to the Google Tag Manager dataLayer.
 */

// Ensure dataLayer exists
window.dataLayer = window.dataLayer || [];

/**
 * Push a view_item event when a product page loads.
 * @param {Object} product - Product data from the page context.
 */
function trackViewItem(product) {
  window.dataLayer.push({ ecommerce: null }); // Clear previous ecommerce data
  window.dataLayer.push({
    event: 'view_item',
    ecommerce: {
      currency: product.currency || 'EUR',
      value: product.price,
      items: [{
        item_id: product.sku,
        item_name: product.name,
        item_category: product.category,
        price: product.price,
        quantity: 1,
      }],
    },
  });
}

/**
 * Push an add_to_cart event when the user adds a product.
 * @param {Object} product - Product data.
 * @param {number} quantity - Number of items added.
 */
function trackAddToCart(product, quantity) {
  window.dataLayer.push({ ecommerce: null });
  window.dataLayer.push({
    event: 'add_to_cart',
    ecommerce: {
      currency: product.currency || 'EUR',
      value: product.price * quantity,
      items: [{
        item_id: product.sku,
        item_name: product.name,
        item_category: product.category,
        price: product.price,
        quantity: quantity,
      }],
    },
  });
}

export { trackViewItem, trackAddToCart };
```

### Checkout Flow Event Tracking

This module handles the `begin_checkout` event when a user enters the checkout flow.

```artifact javascript src/tracking/checkout-events.js
/**
 * Checkout Flow Event Tracking
 *
 * Pushes begin_checkout and shipping/payment step events
 * to the GTM dataLayer for GA4 e-commerce reporting.
 */

import { getCartItems } from '../cart/cart-store';

/**
 * Push a begin_checkout event with all cart items.
 * Call this when the user navigates to the checkout page.
 */
function trackBeginCheckout() {
  const items = getCartItems();
  const totalValue = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({ ecommerce: null });
  window.dataLayer.push({
    event: 'begin_checkout',
    ecommerce: {
      currency: 'EUR',
      value: totalValue,
      items: items.map(item => ({
        item_id: item.sku,
        item_name: item.name,
        item_category: item.category,
        price: item.price,
        quantity: item.quantity,
      })),
    },
  });
}

export { trackBeginCheckout };
```

### Example Usage in Application Code

Here is how these tracking functions would be integrated into a typical product page component. Note this is a regular code block showing usage context -- not a generated artifact.

```javascript
// In your product page component
import { trackViewItem, trackAddToCart } from './tracking/gtm-setup';

// On page load
document.addEventListener('DOMContentLoaded', () => {
  const product = getProductFromPage();
  trackViewItem(product);
});

// On add-to-cart button click
document.getElementById('add-to-cart').addEventListener('click', () => {
  const product = getProductFromPage();
  const quantity = parseInt(document.getElementById('quantity').value, 10);
  trackAddToCart(product, quantity);
});
```

## Testing Notes

- Verify events appear in GTM Preview Mode before publishing
- Check GA4 DebugView for correct event parameters and item data
- Ensure `ecommerce: null` clear push precedes each event to prevent data leakage
- Test with multiple items in cart for begin_checkout event

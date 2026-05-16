# RudderStack CDP Schema (rudder_cdp)

Filter for boopbody.com: `WHERE context_source_id = '31E2sqOsYvKrjKhrxZei2ySRZVk'`

## Tables

### Funnel Events
| Table | Key Columns |
|-------|-------------|
| `product_viewed` | product_id, name, price, category, context_campaign_* |
| `product_added` | product_id, name, price, quantity, variant |
| `cart_viewed` | cart_id, products (JSON), total |
| `checkout_started` | checkout_id, products, revenue, tax, shipping, discount |
| `checkout_contact_info_submitted` | checkout_id, user_id |
| `checkout_address_info_submitted` | checkout_id, context_campaign_* |
| `checkout_shipping_info_submitted` | checkout_id, context_campaign_* |
| `payment_info_entered` | checkout_id |
| `order_completed` | order_id, checkout_id, revenue, total, products |

### Order Events
| Table | Key Columns |
|-------|-------------|
| `order_created` | order_id, value, products, context_traits_* |
| `order_paid` | order_id, products, context_traits_email |
| `order_fulfilled` | order_id, products |
| `order_updated` | order_id, products, tax |
| `order_cancelled` | order_id, value, products |

### Supporting Events
| Table | Key Columns |
|-------|-------------|
| `pages` | url, path, title, context_campaign_* |
| `tracks` | event, context_campaign_* |
| `identifies` | user_id, context_traits_* |
| `search_submitted` | query |
| `product_list_viewed` | list_id, products |
| `product_removed` | product_id, quantity |

## Key Attribution Fields
- `context_campaign_source` — utm_source
- `context_campaign_medium` — utm_medium
- `context_campaign_name` — utm_campaign
- `context_campaign_content` — utm_content
- `context_campaign_term` — utm_term
- `context_campaign_id` — campaign ID

## Customer Identity
- `anonymous_id` — cookie-based visitor ID
- `user_id` — identified customer ID (post-checkout)
- `context_traits_email` — customer email
- `context_traits_first_name`, `context_traits_last_name`
- `context_traits_phone`
- `context_traits_address_*` — shipping address fields

## Common Queries

### Daily Revenue (boopbody)
```sql
SELECT DATE(timestamp) as day, SUM(revenue) as revenue, COUNT(*) as orders
FROM rudder_cdp.order_completed
WHERE context_source_id = '31E2sqOsYvKrjKhrxZei2ySRZVk'
GROUP BY DATE(timestamp)
ORDER BY day DESC;
```

### Attribution by Source
```sql
SELECT context_campaign_source, context_campaign_medium, 
       COUNT(*) as orders, SUM(revenue) as revenue
FROM rudder_cdp.order_completed
WHERE context_source_id = '31E2sqOsYvKrjKhrxZei2ySRZVk'
  AND context_campaign_source IS NOT NULL
GROUP BY context_campaign_source, context_campaign_medium
ORDER BY revenue DESC;
```

### Checkout Funnel
```sql
WITH funnel AS (
  SELECT 'checkout_started' as step, COUNT(DISTINCT checkout_id) as cnt
  FROM rudder_cdp.checkout_started WHERE context_source_id = '31E2sqOsYvKrjKhrxZei2ySRZVk'
  UNION ALL
  SELECT 'contact_info', COUNT(DISTINCT checkout_id)
  FROM rudder_cdp.checkout_contact_info_submitted WHERE context_source_id = '31E2sqOsYvKrjKhrxZei2ySRZVk'
  UNION ALL
  SELECT 'payment_entered', COUNT(DISTINCT checkout_id)
  FROM rudder_cdp.payment_info_entered WHERE context_source_id = '31E2sqOsYvKrjKhrxZei2ySRZVk'
  UNION ALL
  SELECT 'order_completed', COUNT(DISTINCT checkout_id)
  FROM rudder_cdp.order_completed WHERE context_source_id = '31E2sqOsYvKrjKhrxZei2ySRZVk'
)
SELECT * FROM funnel;
```

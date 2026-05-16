---
name: wordpress-generatepress
description: "WordPress site generation using GeneratePress Premium + GenerateBlocks + Meta Box + custom child theme. Use when building or modifying WordPress sites: theme setup, custom post types, page layouts, member directories, blog/SEO integration, or WP-CLI automation. Handles provisioning on HestiaCP, child theme architecture, CPT registration, filterable archives, and WP-CLI-based deployment. Pairs with seo-blog-writer and keyword-research for content workflows."
---

# WordPress + GeneratePress Stack

## Philosophy

- Minimize paid tooling — only GeneratePress Premium is required
- Maintainable code over clever abstractions — future devs should understand it
- WP-CLI for everything automatable — no clicking in admin if avoidable
- Child theme owns all custom logic — never modify parent theme files

---

## Stack

### Required (paid)
| Tool | Cost | Purpose |
|------|------|---------|
| GeneratePress Premium | $59/yr | Header/footer builder, Elements hooks, full layout control |

### Free
| Tool | Purpose |
|------|---------|
| GenerateBlocks (free) | Page layout blocks — hero, grid, cards, sections |
| Meta Box (free) | Custom fields + CPTs (replaces ACF Pro — free tier includes repeater) |
| Meta Box AIO | Free bundle: CPT UI, Taxonomy, Relationships |
| Filter Everything | AJAX filterable archives (replaces FacetWP) |
| LiteSpeed Cache | Caching + performance (use if server supports; else W3 Total Cache) |
| WebP Express | Auto WebP conversion for images |
| Yoast SEO (free) | Meta, schema, sitemaps |
| WP Mail SMTP | Reliable transactional email |

### Only add if genuinely needed
- GenerateBlocks Pro ($39/yr) — only if free GB limits are hit on complex animations/interactions
- The Events Calendar — only if recurring events + iCal export required; otherwise use custom CPT

---

## HestiaCP Provisioning

### Create new WP site via WP-CLI + HestiaCP

```bash
# SSH into server
ssh admin@server-ip

# Add domain in HestiaCP
v-add-domain admin idu.wp.autonomoustech.ca

# Install WordPress
v-install-app admin wordpress idu.wp.autonomoustech.ca / admin admin@autonomoustech.ca "IDU Website" en_US

# Get WP path
WP_PATH="/home/admin/web/idu.wp.autonomoustech.ca/public_html"

# Set up WP-CLI alias
alias wp="wp --path=$WP_PATH --allow-root"
```

### Install plugins via WP-CLI

```bash
# Install + activate all required plugins
wp plugin install meta-box --activate
wp plugin install meta-box-aio --activate  # CPT UI, Taxonomy, Relationships
wp plugin install filter-everything --activate
wp plugin install litespeed-cache --activate
wp plugin install webp-express --activate
wp plugin install wordpress-seo --activate
wp plugin install wp-mail-smtp --activate

# Install GeneratePress + Premium (license key needed for Premium)
wp plugin install generatepress --activate
# GP Premium — upload manually or via URL if license allows
wp theme install generatepress --activate
```

---

## Child Theme Structure

```
{client}-child/
├── style.css              ← child theme header (Template: GeneratePress)
├── functions.php          ← require all inc/ files, enqueue scripts
├── inc/
│   ├── cpt-registration.php   ← register CPTs via Meta Box
│   ├── taxonomies.php          ← register custom taxonomies
│   └── hooks.php               ← GP hooks (full-width templates, etc.)
├── templates/
│   ├── archive-member.php      ← filterable member directory
│   ├── single-member.php       ← party profile page
│   ├── archive-event.php       ← events list + calendar
│   └── page-media-centre.php   ← press kit, releases, photo library
├── css/
│   └── custom.css         ← brand CSS variables + GP overrides
└── js/
    └── filters.js         ← Filter Everything hooks if needed
```

### style.css header

```css
/*
Theme Name: {Client} Child
Template: generatepress
Version: 1.0.0
*/
@import url('../generatepress/style.css');
```

### functions.php

```php
<?php
// Enqueue child theme CSS
add_action('wp_enqueue_scripts', function() {
    wp_enqueue_style('parent-style', get_template_directory_uri() . '/style.css');
    wp_enqueue_style('child-style', get_stylesheet_uri(), ['parent-style']);
    wp_enqueue_style('custom-style', get_stylesheet_directory_uri() . '/css/custom.css', ['child-style']);
});

require_once get_stylesheet_directory() . '/inc/cpt-registration.php';
require_once get_stylesheet_directory() . '/inc/taxonomies.php';
require_once get_stylesheet_directory() . '/inc/hooks.php';
```

---

## Brand Colors (GP Customizer + CSS Variables)

Set primary/link/button colors in GP Customizer → Colors.

Then override in `css/custom.css` for precision:

```css
:root {
  --idu-blue: #003087;
  --idu-mid: #0057B7;
  --idu-bright: #0071CE;
  --idu-gold: #C9A84C;
  --idu-text: #1A1A2E;
  --idu-bg: #F4F6F8;
}

/* Override GP variables */
:root {
  --gp-primary: var(--idu-blue);
  --gp-link: var(--idu-mid);
}
```

---

## Custom Post Types with Meta Box

```php
// inc/cpt-registration.php
add_filter('rwmb_meta_boxes', function($meta_boxes) {

    // MEMBERS CPT
    $meta_boxes[] = [
        'title'      => 'Member Details',
        'post_types' => ['member'],
        'fields'     => [
            ['name' => 'Party Logo',         'id' => 'party_logo',        'type' => 'image_advanced'],
            ['name' => 'Country',            'id' => 'country',           'type' => 'text'],
            ['name' => 'Party Website',      'id' => 'party_website',     'type' => 'url'],
            ['name' => 'Chairman',           'id' => 'chairman',          'type' => 'text'],
            ['name' => 'Government Status',  'id' => 'govt_status',       'type' => 'select',
             'options' => ['in-government' => 'In Government', 'opposition' => 'In Opposition']],
            ['name' => 'Membership Type',    'id' => 'membership_type',   'type' => 'select',
             'options' => ['full' => 'Full Member', 'associate' => 'Associate', 'observer' => 'Observer']],
        ],
    ];

    // LEADERSHIP CPT
    $meta_boxes[] = [
        'title'      => 'Leadership Details',
        'post_types' => ['idu_leadership'],
        'fields'     => [
            ['name' => 'Photo',    'id' => 'photo',    'type' => 'image_advanced'],
            ['name' => 'Title',    'id' => 'title',    'type' => 'text'],
            ['name' => 'Party',    'id' => 'party',    'type' => 'text'],
            ['name' => 'Country',  'id' => 'country',  'type' => 'text'],
            ['name' => 'Bio',      'id' => 'bio',      'type' => 'textarea'],
        ],
    ];

    // EVENTS CPT
    $meta_boxes[] = [
        'title'      => 'Event Details',
        'post_types' => ['idu_event'],
        'fields'     => [
            ['name' => 'Event Date',     'id' => 'event_date',     'type' => 'date'],
            ['name' => 'Location',       'id' => 'event_location', 'type' => 'text'],
            ['name' => 'Event Type',     'id' => 'event_type',     'type' => 'select',
             'options' => ['summit' => 'Summit', 'forum' => 'Forum', 'meeting' => 'Meeting', 'award' => 'Award Ceremony']],
        ],
    ];

    return $meta_boxes;
});

// Register CPTs
add_action('init', function() {
    register_post_type('member', [
        'label'  => 'Members',
        'public' => true,
        'menu_icon' => 'dashicons-groups',
        'supports' => ['title', 'editor', 'thumbnail'],
        'rewrite' => ['slug' => 'members'],
    ]);
    register_post_type('idu_leadership', [
        'label'  => 'Leadership',
        'public' => true,
        'menu_icon' => 'dashicons-admin-users',
        'supports' => ['title', 'thumbnail'],
        'rewrite' => ['slug' => 'leadership'],
    ]);
    register_post_type('idu_event', [
        'label'  => 'Events',
        'public' => true,
        'menu_icon' => 'dashicons-calendar',
        'supports' => ['title', 'editor', 'thumbnail'],
        'rewrite' => ['slug' => 'events'],
    ]);
});
```

---

## Filterable Archive (Member Directory)

Filter Everything plugin handles AJAX filtering by taxonomy. Wire it up:

```php
// inc/taxonomies.php
add_action('init', function() {
    register_taxonomy('member_region', 'member', [
        'label'        => 'Region',
        'hierarchical' => false,
        'rewrite'      => ['slug' => 'region'],
    ]);
    // Filter Everything auto-detects registered taxonomies
});
```

In archive-member.php:
```php
// Loop outputs member cards; Filter Everything wraps with AJAX
echo do_shortcode('[filter_everything post_type="member"]');
```

---

## GenerateBlocks Layout Patterns

Use GP Elements (GP Premium) for global header/footer. Use GenerateBlocks for page sections.

### Full-bleed hero with overlay
- GB Section block → Background image → Overlay color (rgba)
- GP Element: inject `.full-width` body class on hero pages via GP Elements

### Stats bar
- GB Grid (4 columns) → GB Text for number + label
- Responsive: collapses to 2x2 on mobile

### Card grid (members, news, team)
- GB Query Loop → GB Grid → custom PHP card template
- Filter Everything wraps the Query Loop output

---

## Blog + SEO Workflow Integration

### Publishing blog posts via WP-CLI

After `seo-blog-writer` produces a markdown file:

```bash
# Create post from markdown
wp post create \
  --post_title="$TITLE" \
  --post_content="$CONTENT" \
  --post_status=publish \
  --post_type=post \
  --post_category="$CATEGORY_ID"

# Set Yoast meta via WP-CLI + Yoast extension
wp post meta update $POST_ID _yoast_wpseo_title "$SEO_TITLE"
wp post meta update $POST_ID _yoast_wpseo_metadesc "$META_DESC"
wp post meta update $POST_ID _yoast_wpseo_focuskw "$FOCUS_KW"
```

### Schema markup
Yoast SEO handles Organization + Article schema automatically. For custom schemas (Event, Person), add via GP Elements or custom `wp_head` hook in `inc/hooks.php`.

---

## Performance Checklist

- [ ] LiteSpeed Cache configured (or W3 Total Cache)
- [ ] WebP Express active + serving WebP
- [ ] GP lazy load enabled (Settings → GeneratePress → Performance)
- [ ] Hero image explicitly NOT lazy loaded (set loading="eager" via hook)
- [ ] Unused GP modules disabled (WooCommerce, Blog if not used)
- [ ] CSS/JS minified via caching plugin
- [ ] Target: <2.5s LCP on staging before launch

---

## WP-CLI Quick Reference

```bash
# Plugin management
wp plugin list
wp plugin install {slug} --activate
wp plugin update --all

# Theme
wp theme activate generatepress
wp theme activate {client}-child

# Content
wp post list --post_type=member --fields=ID,title
wp post create --from-post=$SOURCE_ID  # duplicate a post

# Search-replace (after domain change)
wp search-replace 'http://old.domain' 'https://new.domain' --all-tables

# Database
wp db export backup.sql
wp db import backup.sql

# Cache flush
wp cache flush
wp litespeed-purge all  # LiteSpeed Cache
```

---

## Companion Skills/Agents

- **`keyword-research`** → upstream for blog content planning
- **`seo-blog-writer`** → produces markdown posts for WP-CLI import
- **`seo-optimizer`** → post-publish on-page SEO pass
- **`frontend-design`** → visual direction for GP Customizer + CSS

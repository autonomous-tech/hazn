# Page Inventory — Audit Order

> Ordered by traffic priority. Each entry lists route, template, and rendering mode.

---

## Tier 1: High-Traffic Pages

| # | Route | Template | Rendering | Key Components |
|---|-------|----------|-----------|----------------|
| 1 | `/` | `page.tsx` (Homepage) | `HeroSection` + `RenderBlocks` | HeroSection, UrgencyBand, ThreeDoors, CaseStudy, Capabilities, Products, Testimonials, HowWeWork, GlobalDelivery, CTABand, FinalCTA |
| 2 | `/marketing/` | `MarketingTemplate` | Custom (hardcoded) | DarkHero, ProblemCards, MarketingTabs, ServiceCards, DualCaseStudy, DarkProcess, FAQ, FinalCTA, CrossDoorNav |
| 3 | `/ecommerce/` | `EcommerceTemplate` | Custom (hardcoded) | DarkHero, ServiceCards, CTABand, DeliverablesGrid, PricingTiers, CaseStudyCard, TechStack, HowWeWork, FAQ, FinalCTA, CrossDoorNav |
| 4 | `/engineering/` | `EngineeringTemplate` | Custom (hardcoded) | ServiceHeroLight, ProblemCards, RichServiceCards, DarkProcess, CaseStudyCard, FinalCTA, CrossDoorNav |
| 5 | `/agency/` | `AgencyTemplate` | Custom (hardcoded) | DarkHero, ProblemCards, FlowDiagram, ChecklistWithVisual, CaseStudyCard, PricingTiers, FAQ, FinalCTA, CrossDoorNav |
| 6 | `/pricing/` | `PricingPageTemplate` | Custom (hardcoded) | Custom hero, PricingTiers, FAQ, FinalCTA |
| 7 | `/contact/` | `ServicePageTemplate` | RenderBlocks | ServiceHero, Breadcrumbs, body blocks |
| 8 | `/about/` | `ServicePageTemplate` | RenderBlocks | ServiceHero, TeamGrid, Timeline, body blocks |
| 9 | `/blog/` | `BlogIndexTemplate` | Custom | Hero, FeaturedPost, BlogIndexClient (filter + grid) |
| 10 | `/blog/[slug]/` | `BlogPostTemplate` | Custom (RenderBlogBody) | PostHero, ArticleBody, BlogSidebar, AuthorCard, RelatedPosts |

## Tier 2: Service Sub-Pages

| # | Route | Template | Rendering |
|---|-------|----------|-----------|
| 11 | `/marketing/attribution/` | `AttributionTemplate` | Custom (hardcoded) |
| 12 | `/marketing/cdp/` | `CDPTemplate` | Custom (hardcoded) |
| 13 | `/ecommerce/shopify/` | `ShopifyTemplate` | Custom (hardcoded) |
| 14 | `/ecommerce/klaviyo/` | `KlaviyoTemplate` | Custom (hardcoded) |
| 15 | `/ecommerce/operations/` | `EcommerceOpsTemplate` | Custom (hardcoded) |
| 16 | `/ecommerce/analytics/` | `EcomAnalyticsTemplate` | Custom (hardcoded) |
| 17 | `/enterprise/` | `EnterpriseTemplate` | Custom (hardcoded) |
| 18 | `/enterprise/managed-it/` | `ManagedITTemplate` | Custom (hardcoded) |
| 19 | `/fintech/` | `FintechTemplate` | Custom (hardcoded) |
| 20 | `/sports-analytics/` | `SportsAnalyticsTemplate` | Custom (hardcoded) |

## Tier 3: Intelligence & Products

| # | Route | Template | Rendering |
|---|-------|----------|-----------|
| 21 | `/intelligence/` | `IntelligenceSuiteTemplate` | Custom (hardcoded) |
| 22 | `/intelligence/sitescore/` | `IntelligenceProductTemplate` | Custom (hardcoded) |
| 23 | `/intelligence/attributioncheck/` | `IntelligenceProductTemplate` | Custom (hardcoded) |
| 24 | `/intelligence/searchintel/` | `IntelligenceProductTemplate` | Custom (hardcoded) |
| 25 | `/intelligence/conversioniq/` | `IntelligenceProductTemplate` | Custom (hardcoded) |
| 26 | `/intelligence/analyticsaudit/` | `IntelligenceProductTemplate` | Custom (hardcoded) |
| 27 | `/products/` | `ServicePageTemplate` | RenderBlocks |
| 28 | `/products/memox/` | `ServicePageTemplate` | RenderBlocks (ProductSplit) |
| 29 | `/products/agent-os/` | `ServicePageTemplate` | RenderBlocks (ProductSplit) |
| 30 | `/products/moltcloud/` | `ServicePageTemplate` | RenderBlocks (ProductSplit) |

## Tier 4: Work & Other

| # | Route | Template | Rendering |
|---|-------|----------|-----------|
| 31 | `/work/` | `WorkIndexTemplate` | Custom |
| 32 | `/work/senestudio/` | `CaseStudyTemplate` | Custom (hardcoded, 6 sections) |
| 33 | `/hazn/` | `ServicePageTemplate` | RenderBlocks |

## Global (Every Page)

| # | Component | File |
|---|-----------|------|
| G1 | Navigation | `NavClient.tsx` — 930px breakpoint, announcement bar |
| G2 | Footer | `Footer.tsx` — text-white/40, responsive CTA |
| G3 | CSS | `globals.css` — layers, typography, animations |
| G4 | Layout | `layout.tsx` — font loading, metadata defaults |

## RenderBlocks Routing Reference

The `RenderBlocks` component maps block types to components with smart routing:

| Block Type | Routes To | Routing Logic |
|------------|-----------|---------------|
| `cards_section` | ThreeDoors / ProblemCards / ServiceCards / DeliverablesGrid | By `card_style` field |
| `process_steps` | HowWeWork / DarkProcess | By `bg_style` (dark → DarkProcess) |
| `case_study_highlight` | CaseStudy / CaseStudyCard | By `layout` field |
| `urgency_band` | UrgencyBandSection | Direct |
| `stats_section` | StatsSection | Direct |
| `capabilities` | CapabilitiesSection | Direct |
| `products_section` | ProductsSection | Direct |
| `testimonials_section` | TestimonialsSection | Direct |
| `global_delivery` | GlobalDeliverySection | Direct |
| `cta_band` | CTABandSection | Direct |
| `final_cta` | FinalCTASection | Direct |
| `rich_text_section` | RichTextSection | Direct |
| `faq` | FAQSection | Direct |
| `comparison_table` | ComparisonTableSection | Direct |
| `pricing_tiers` | PricingTiersSection | Direct |
| `tech_stack` | TechStackGridSection | Direct |
| `tab_section` | TabSection | Direct |
| `related_services` | RelatedServicesSection | Direct |
| `dual_case_study` | DualCaseStudySection | Direct |
| `tabbed_cards` | TabbedCardsSection | Direct |
| `rich_service_cards` | RichServiceCardsSection | Direct |
| `categorized_card_grid` | CategorizedCardGridSection | Direct |
| `flow_diagram` | FlowDiagramSection | Direct |
| `checklist_with_visual` | ChecklistWithVisualSection | Direct |
| `product_split` | ProductSplitSection | Direct |
| `team_grid` | TeamGridSection | Direct |
| `timeline` | TimelineSection | Direct |

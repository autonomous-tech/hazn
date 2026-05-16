# Ahrefs Integration Guide — SiteScore Deep Dive

## When to use this
Only during TIER = Deep Dive for SiteScore audits. Requires Ahrefs access (shared Hazn account or client-provided API key).

## Access Methods

### Method 1: Ahrefs API (preferred)
If API key is available:
- Base URL: https://api.ahrefs.com/v3/
- Auth: Bearer token in header
- Rate limits: check plan tier

Key endpoints to use:
- Site Audit: POST /site-audit/new-crawl — trigger crawl for target domain
- Backlinks: GET /site-explorer/backlinks — get backlink profile
- Organic Keywords: GET /site-explorer/organic-keywords — keyword rankings
- Competitors: GET /site-explorer/competing-domains — find competitors
- Keyword Gap: GET /keywords-explorer/serp-overview — gap analysis

### Method 2: Manual Export (fallback)
If no API key, ask client to export from Ahrefs dashboard:
- Site Audit report → export as CSV
- Top pages report → export as CSV
- Backlinks report → export as CSV
- Organic keywords → export as CSV

Parse CSV exports and extract the relevant data.

### Method 3: Ahrefs Free Tools (minimal fallback)
If neither API nor CSV available:
- Use https://ahrefs.com/backlink-checker (free, limited)
- Use https://ahrefs.com/website-authority-checker
- Clearly label all findings as "Not verified — limited data source"

## What to Pull and How to Report It

### Technical Issues (Site Audit)
Pull top issues by: Errors (fix immediately) → Warnings (fix soon) → Notices (optional)
Report top 20 issues maximum. Group by category:
- Crawlability: blocked pages, noindex, redirect chains
- On-page: missing meta, duplicate titles, thin content
- Performance: slow pages, large images, render-blocking resources
- Links: broken internal links, broken external links, orphan pages

Label each: Observed (confirmed from Ahrefs data)

### Backlink Profile
Report:
- Domain Rating (DR): X/100
- Total referring domains: X (trend: +X% / -X% over 3 months if available)
- Total backlinks: X
- Top 10 referring domains by DR (table: domain, DR, links from that domain)
- Anchor text distribution: branded XX% / exact-match XX% / generic XX% / other XX%
- Toxic/spammy links: X flagged (list top 5 if any)

### Keyword Rankings
Report:
- Total ranking keywords: X
- By position bucket: #1-3 (X kws) / #4-10 (X kws) / #11-20 (X kws) / #21-50 (X kws)
- Top 20 pages by estimated organic traffic (table: URL, top keyword, position, est. traffic)
- Quick win pages: pages ranking #4-10 with search volume >500/mo (flag as priority)

### Keyword Gap (requires competitor domains)
For each competitor:
- Run keyword gap: keywords they rank for in top 10 that target domain does not rank for at all
- Filter by: search volume >200/mo, keyword difficulty <50 (accessible opportunities)
- Report top 20 gap keywords per competitor
- Group by topic/intent to identify content clusters

### Content Opportunities
Synthesise from GSC (impressions/CTR) + Ahrefs (rankings):
1. High impression, low CTR pages → title/meta optimisation opportunity
2. Pages ranking #4-10 → content improvement for quick ranking gains
3. Keyword gap clusters → new content needed

## Output Format in Report

Add a dedicated section "Deep Dive: Search Intelligence" to the HTML report with:
1. Backlink Profile summary card
2. Keyword Rankings distribution chart (described in HTML, not image)
3. Top 20 ranking pages table
4. Quick wins table (pages at #4-10)
5. Keyword gap table (top 20 per competitor)
6. Content opportunity list

All data must be labeled: Observed (from Ahrefs) / Assessment (interpretation) / Not verified

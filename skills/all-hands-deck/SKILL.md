---
name: all-hands-deck
description: Create branded All Hands presentation decks for FAST. Use when asked to create, build, or prepare an all-hands meeting deck, company update presentation, team meeting slides, or Monday all-hands. Outputs a styled HTML presentation with AI-generated imagery.
---

# All Hands Deck Generator

Create polished All Hands presentation decks with FAST branding, AI-generated images, and a consistent structure.

## Quick Start

1. **Gather context** via conversation:
   - What's the main theme? (quarterly update, product launch, team changes)
   - Company status (financials, wins, challenges)
   - Key announcements or priorities
   - Shoutouts/recognition
   - Tone: energizing, honest, rallying

2. **Generate images** using Google Imagen API (see [references/imagen.md](references/imagen.md))

3. **Build deck** using the HTML template in `assets/template.html`

4. **Deploy** to pages.autonomoustech.ca for preview/sharing

## Standard Slide Structure

1. **Title** — Month + Year, tagline
2. **Where We Stand** — Financial health, team status
3. **Team Update** — Restructuring, culture
4. **Why Now** — Market opportunity, AI moment
5. **The Bet** — Strategic focus (AI is the Lever)
6. **AI Portfolio** — Products being built
7. **Core Business** — Existing clients, revenue base
8. **Target** — Quarterly goals (e.g., 1-2 new clients)
9. **Level Up** — Culture expectations (watch out / aim for)
10. **AI Advantage** — Why learning AI matters
11. **Quality + Fun** — The bar for great work
12. **Two Modes** — Client work vs experiments
13. **Priorities** — Next 90 days (5 priorities)
14. **Scoreboard** — What winning looks like
15. **Shoutouts** — Team recognition (2-4 people)
16. **Final Word** — Rally cry
17. **Let's Go** — Energy closer
18. **Questions** — Open floor

## Brand Guide

See [references/brand.md](references/brand.md) for colors, fonts, and styling.

## Image Generation

Use Google Imagen 4 API. See [references/imagen.md](references/imagen.md) for prompts and API usage.

Suggested images:
- **Hero**: Abstract tech/network visualization
- **Growth**: Rocket, upward momentum
- **AI**: Neural brain, circuits
- **Target**: Bullseye, achievement
- **Team**: Celebration, silhouettes
- **Finale**: Sunrise, new beginning

## Serving the Deck

Deploy to pages.autonomoustech.ca for sharing:

```bash
cp -r deck-folder /home/rizki/clawd/landing-pages/decks/
cd /home/rizki/clawd/landing-pages
git add decks/ && git commit -m "Add deck" && git push
# Live at: https://pages.autonomoustech.ca/decks/<folder>/
```

## Output

- `all-hands-deck.html` — Full presentation
- `deck-images/` — Generated images + logos

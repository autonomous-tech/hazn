# Logo Fetching

## Script
```bash
cd ~/autonomous-proposals && node scripts/fetch-logo.js <url>
```
Outputs the path to the saved logo file, or "FAILED" if not found.

## What the script does
1. Opens the URL in headless Chrome
2. Finds the first `<img>` with `src` matching `/logo/i` or `alt` matching `/logo|brand/i`
3. Grabs the `src` URL
4. If SVG → downloads and saves to `~/hazn/logos/{slug}.svg`
5. If PNG/JPG → downloads and saves to `~/hazn/logos/{slug}.png`

## Embedding in HTML

**SVG (preferred)** — inline directly, strip animation keyframes:
```python
import re
svg = open('~/hazn/logos/client.svg').read()
svg = re.sub(r'<style>.*?</style>', '', svg, flags=re.DOTALL)
svg = svg.replace(' class="floating-tile"', '')
# Set explicit dimensions: width="110" height="27"
```

**PNG/JPG** — base64 encode for self-contained HTML:
```python
import base64
data = open('~/hazn/logos/client.png', 'rb').read()
b64 = base64.b64encode(data).decode()
img_tag = f'<img src="data:image/png;base64,{b64}" height="28" style="display:block;">'
```

## Failure fallback
If logo fetch fails, use the text placeholder — never block generation:
```html
<div class="logo-placeholder">
  <span class="logo-placeholder-icon">⬡</span>
  <span class="logo-placeholder-text">CLIENT NAME</span>
</div>
```

## Known edge cases
- React SPAs (like JuristAI) — logo is in a `<img>` tag once JS renders; Puppeteer handles this with `waitUntil: networkidle0`
- SVGs with dark fills on transparent bg — works fine on white card background
- SVGs with animation — strip `<style>` block and `.floating-tile` class before inlining
- Logos on dark nav bars — may need `filter: invert(1)` or fetch from a light-bg page

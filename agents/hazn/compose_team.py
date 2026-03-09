from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

W, H = 2560, 1440
BG       = "#0A0A0B"
WHITE    = "#FAFAFA"
MUTED    = "#71717A"
BLUE     = "#3B82F6"
BLUE_LT  = "#60A5FA"

ASSET    = "/home/rizki/clawd/agents/hazn/brand-assets"
SANS_B   = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS     = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
MONO_B   = "/tmp/jbmono/fonts/ttf/JetBrainsMono-Bold.ttf"

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

def paste_avatar(canvas, path, cx, cy, size, circle=True):
    av = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
    if circle:
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, size, size], fill=255)
        av.putalpha(mask)
    canvas.paste(av, (cx - size//2, cy - size//2), av)

# ── Subtle radial glow behind main avatar ──────────────────────────
glow = Image.new("RGB", (W, H), BG)
gd   = ImageDraw.Draw(glow)
for r in range(600, 0, -8):
    alpha = int(40 * (1 - r/600))
    gd.ellipse([(640 - r, H//2 - r), (640 + r, H//2 + r)],
               fill=(30, 60, 120))
img = Image.blend(img, glow, 0.5)
draw = ImageDraw.Draw(img)

# ── Main avatar — large, left-center ──────────────────────────────
paste_avatar(img, f"{ASSET}/avatar.png", 560, H//2, 620)

# Blue ring around main avatar
draw = ImageDraw.Draw(img)
r = 315
draw.ellipse([(560 - r, H//2 - r), (560 + r, H//2 + r)],
             outline=BLUE, width=4)

# ── Agent grid — right side ────────────────────────────────────────
agents = [
    ("strategist",          "Strategist"),
    ("ux-architect",        "UX Architect"),
    ("copywriter",          "Copywriter"),
    ("developer",           "Developer"),
    ("seo-specialist",      "SEO Specialist"),
    ("content-writer",      "Content Writer"),
    ("auditor",             "Auditor"),
    ("wireframer",          "Wireframer"),
    ("email-specialist",    "Email Specialist"),
    ("conversion-specialist","Conversion"),
]

AVATAR_SIZE = 200
COLS        = 5
ROWS        = 2
COL_GAP     = 260
ROW_GAP     = 340
START_X     = 1150
START_Y     = H//2 - (ROWS * ROW_GAP)//2 + 20

f_name = ImageFont.truetype(SANS, 30)

for i, (slug, label) in enumerate(agents):
    col = i % COLS
    row = i // COLS
    cx  = START_X + col * COL_GAP
    cy  = START_Y + row * ROW_GAP

    path = f"{ASSET}/avatars/{slug}.png"
    if os.path.exists(path):
        paste_avatar(img, path, cx, cy, AVATAR_SIZE)
        draw = ImageDraw.Draw(img)

    # name label
    tw = draw.textlength(label, font=f_name)
    draw.text((cx - tw//2, cy + AVATAR_SIZE//2 + 14), label,
              fill=MUTED, font=f_name)

# ── Connector lines from main avatar to grid ──────────────────────
draw = ImageDraw.Draw(img)
for i, (slug, label) in enumerate(agents):
    col = i % COLS
    row = i // COLS
    cx  = START_X + col * COL_GAP
    cy  = START_Y + row * ROW_GAP
    draw.line([(875, H//2), (cx - 100, cy)], fill=(59, 130, 246, 40), width=1)

# ── Branding ──────────────────────────────────────────────────────
f_brand  = ImageFont.truetype(SANS_B, 70)
f_tag    = ImageFont.truetype(SANS, 38)
f_url    = ImageFont.truetype(MONO_B, 44)

# hazn.ai top left
draw.text((72, 60), "hazn.ai", fill=WHITE, font=f_brand)
bar_w = int(draw.textlength("hazn.ai", font=f_brand))
draw.rectangle([(72, 138), (72 + bar_w, 142)], fill=BLUE)

# Headline over main avatar
f_headline = ImageFont.truetype(SANS_B, 58)
headline = "your marketing team\njust got here."
lines_h = headline.split("\n")
for li, hl in enumerate(lines_h):
    hw = draw.textlength(hl, font=f_headline)
    draw.text((560 - hw//2, 170 + li * 72), hl, fill=WHITE, font=f_headline)

# Bottom scrim
scrim = Image.new("RGB", (W, 130), "#000000")
img.paste(scrim, (0, H - 130))
draw = ImageDraw.Draw(img)
draw.rectangle([(0, H - 130), (W, H - 127)], fill=BLUE)

draw.text((72, H - 90),
          "AI Marketing Agents for Technical Founders",
          fill=MUTED, font=f_tag)

url_t = "hazn.ai/waitlist →"
url_w = int(draw.textlength(url_t, font=f_url))
draw.text((W - url_w - 72, H - 94), url_t, fill=BLUE_LT, font=f_url)

out = "/home/rizki/.openclaw/agents/2026-03-04-hazn-linkedin-v10.png"
img.save(out, "PNG")
print("saved:", out)

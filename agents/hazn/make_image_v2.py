from PIL import Image, ImageDraw, ImageFont

W, H = 2560, 1440

# hazn.ai brand colors
BG       = "#0A0A0B"
WHITE    = "#FAFAFA"
MUTED    = "#71717A"
BORDER   = "#27272A"
GREEN    = "#22C55E"
BLUE     = "#3B82F6"
BLUE_LT  = "#60A5FA"

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

MONO     = "/tmp/jbmono/fonts/ttf/JetBrainsMono-Regular.ttf"
MONO_B   = "/tmp/jbmono/fonts/ttf/JetBrainsMono-Bold.ttf"
SANS     = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B   = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

f_label  = ImageFont.truetype(MONO, 36)
f_cmd    = ImageFont.truetype(MONO_B, 52)
f_line   = ImageFont.truetype(MONO, 52)
f_url    = ImageFont.truetype(MONO_B, 56)
f_brand  = ImageFont.truetype(SANS, 42)
f_tag    = ImageFont.truetype(MONO, 34)

# subtle top border line
draw.rectangle([(0, 0), (W, 3)], fill=BLUE)

# hazn.ai — top left
draw.text((80, 60), "hazn.ai", fill=MUTED, font=f_brand)

# terminal block — centered
lines = [
    ("prompt", "$ hazn run --week 1"),
    ("blank", ""),
    ("check", "✓", "4 websites built"),
    ("check", "✓", "12 variants"),
    ("check", "✓", "2 complete client sites"),
    ("check", "✓", "2 martech audits → 2 upsells"),
    ("blank", ""),
    ("output", "it launched itself."),
    ("blank", ""),
    ("url", "→ hazn.ai"),
]

line_h = 78
total_h = len(lines) * line_h
start_y = (H - total_h) // 2 - 20
x = (W - 900) // 2 - 80

y = start_y
for item in lines:
    if item[0] == "blank":
        y += line_h // 2
        continue
    elif item[0] == "prompt":
        # green prompt
        draw.text((x, y), item[1], fill=GREEN, font=f_cmd)
    elif item[0] == "check":
        check, text = item[1], item[2]
        draw.text((x, y), check, fill=GREEN, font=f_line)
        draw.text((x + 60, y), "  " + text, fill=WHITE, font=f_line)
    elif item[0] == "output":
        draw.text((x + 4, y), item[1], fill=MUTED, font=f_line)
    elif item[0] == "url":
        draw.text((x + 4, y), item[1], fill=BLUE_LT, font=f_url)
    y += line_h

# blinking cursor after URL
cursor_x = x + 4 + draw.textlength("→ hazn.ai", font=f_url) + 8
draw.rectangle([(cursor_x, y - line_h + 8), (cursor_x + 32, y - 14)], fill=BLUE_LT)

# bottom right — subtle tag
tag = "AI Marketing Agents for Technical Founders"
tw = draw.textlength(tag, font=f_tag)
draw.text((W - tw - 80, H - 70), tag, fill=MUTED, font=f_tag)

# bottom border line
draw.rectangle([(0, H - 3), (W, H)], fill=BORDER)

out = "/home/rizki/.openclaw/agents/2026-03-04-hazn-linkedin-v5.png"
img.save(out, "PNG")
print("MEDIA:", out)
print("saved to", out)

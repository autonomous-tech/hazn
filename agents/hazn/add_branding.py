from PIL import Image, ImageDraw, ImageFont

img = Image.open("/home/rizki/clawd/agents/hazn/2026-03-04-hazn-linkedin-v7.png").convert("RGBA")
W, H = img.size

overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)

SANS    = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B  = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
MONO_B  = "/tmp/jbmono/fonts/ttf/JetBrainsMono-Bold.ttf"

# hazn.ai — top left, clean white, semi-transparent
f_brand = ImageFont.truetype(SANS_B, 64)
draw.text((72, 64), "hazn.ai", fill=(250, 250, 250, 210), font=f_brand)

# Blue accent bar under brand name
bar_w = int(draw.textlength("hazn.ai", font=f_brand))
draw.rectangle([(72, 64 + 70), (72 + bar_w, 64 + 74)], fill=(59, 130, 246, 200))

# Bottom — tagline left, url right
f_tag = ImageFont.truetype(SANS, 38)
f_url = ImageFont.truetype(MONO_B, 42)

# dark scrim at bottom for legibility
scrim = Image.new("RGBA", (W, 120), (0, 0, 0, 160))
overlay.paste(scrim, (0, H - 120))

draw.text((72, H - 80), "AI Marketing Agents for Technical Founders", fill=(161, 161, 170, 200), font=f_tag)

url_text = "hazn.ai/waitlist →"
url_w = int(draw.textlength(url_text, font=f_url))
draw.text((W - url_w - 72, H - 82), url_text, fill=(96, 165, 250, 230), font=f_url)

out_img = Image.alpha_composite(img, overlay).convert("RGB")
out = "/home/rizki/.openclaw/agents/2026-03-04-hazn-linkedin-v8.png"
out_img.save(out, "PNG")
print("MEDIA:", out)

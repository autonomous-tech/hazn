from PIL import Image, ImageDraw, ImageFont

W, H = 2560, 1440
img = Image.new("RGB", (W, H), "#000000")
draw = ImageDraw.Draw(img)

bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# hazn.ai — top left, small
f_small = ImageFont.truetype(regular, 48)
draw.text((80, 72), "hazn.ai", fill="#ffffff", font=f_small)

# Giant "4" — centered, fills the frame
f_huge = ImageFont.truetype(bold, 1100)
bbox = draw.textbbox((0, 0), "4", font=f_huge)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
x = (W - tw) // 2 - bbox[0]
y = (H - th) // 2 - bbox[1] - 60
draw.text((x, y), "4", fill="#ffffff", font=f_huge)

# "websites. this week." — bottom right, small
f_sub = ImageFont.truetype(regular, 44)
text = "websites. this week."
bbox2 = draw.textbbox((0, 0), text, font=f_sub)
tw2 = bbox2[2] - bbox2[0]
draw.text((W - tw2 - 80, H - 90), text, fill="#888888", font=f_sub)

out = "/home/rizki/.openclaw/agents/2026-03-04-hazn-linkedin-v4.png"
img.save(out, "PNG")
print("MEDIA:", out)

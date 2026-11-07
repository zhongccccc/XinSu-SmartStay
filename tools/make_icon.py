# -*- coding: utf-8 -*-
"""生成「芯宿·智控」应用图标（256x256 PNG，圆角渐变 + 芯字）。"""
import os

from PIL import Image, ImageDraw, ImageFont

S = 256
OUT = r"E:\zhikong\app\assets\zhikong.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# 渐变底色：青绿 -> 天蓝
grad = Image.new("RGB", (S, S))
px = grad.load()
c1, c2 = (34, 211, 166), (63, 169, 245)
for y in range(S):
    for x in range(S):
        t = (x + y) / (2.0 * S - 2)
        px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# 圆角遮罩
mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=58, fill=255)
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
img.paste(grad, (0, 0), mask)

d = ImageDraw.Draw(img)
# 内描边
d.rounded_rectangle([6, 6, S - 7, S - 7], radius=52, outline=(255, 255, 255, 90), width=2)

# 中文字
font = None
for f in (r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\msyh.ttc",
          r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\simsun.ttc"):
    if os.path.exists(f):
        try:
            font = ImageFont.truetype(f, 132)
            break
        except Exception:
            pass

if font:
    text = "芯"
    bbox = d.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((S - w) / 2 - bbox[0], (S - h) / 2 - bbox[1] - 6), text,
           font=font, fill=(255, 255, 255, 245))
else:
    d.ellipse([88, 88, 168, 168], fill=(255, 255, 255, 230))

img.save(OUT, "PNG")
print("saved", OUT, os.path.getsize(OUT), "bytes")

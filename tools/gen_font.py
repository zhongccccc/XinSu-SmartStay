# -*- coding: utf-8 -*-
"""按 lcd_font.h 的格式生成中文字模（16px / 24px）。

格式：
  16px: Index[3] + Msk[32]  —— 16 行，每行 2 字节，小端，bit i = 第 i 个像素
  24px: Index[3] + Msk[72]  —— 24 行，每行 3 字节，小端
"""
from PIL import Image, ImageDraw, ImageFont

CHARS = "光照燃气人体风扇灯有无关状态环境空调"

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simsun.ttc",
]


def load_font(size):
    for p in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    raise SystemExit("找不到中文字体")


def glyph(ch, size):
    """渲染成 size x size 的黑白点阵，返回 rows 列表（每行是 0/1 列表）"""
    img = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(img)
    f = load_font(size)
    bbox = d.textbbox((0, 0), ch, font=f)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (size - w) // 2 - bbox[0]
    y = (size - h) // 2 - bbox[1]
    d.text((x, y), ch, fill=255, font=f)
    px = img.load()
    rows = []
    for yy in range(size):
        row = [1 if px[xx, yy] > 110 else 0 for xx in range(size)]
        rows.append(row)
    return rows


def to_bytes(rows, size):
    """按行打包成小端字节序列"""
    data = []
    for row in rows:
        val = 0
        for i, bit in enumerate(row):
            if bit:
                val |= (1 << i)
        nbytes = (size + 7) // 8
        for b in range(nbytes):
            data.append((val >> (8 * b)) & 0xFF)
    return data


def emit(chars, size, table_name):
    out = []
    for ch in chars:
        rows = glyph(ch, size)
        data = to_bytes(rows, size)
        hexes = ",".join("0x%02X" % b for b in data)
        out.append('    "%s", %s,/*"%s"*/' % (ch, hexes, ch))
    return "\n".join(out)


need16 = "".join(c for c in CHARS)
print("生成 16px:", need16)
body16 = emit(need16, 16, "tfont16")
print("生成 24px")
body24 = emit(need16, 24, "tfont24")

open(r"E:\zhikong\tools\font16_add.txt", "w", encoding="utf-8").write(body16 + "\n")
open(r"E:\zhikong\tools\font24_add.txt", "w", encoding="utf-8").write(body24 + "\n")
print("已写出 font16_add.txt / font24_add.txt")
print()
print("16px 第一行预览:")
print(body16.splitlines()[0][:160], "...")

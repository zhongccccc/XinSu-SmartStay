# -*- coding: utf-8 -*-
"""放大第 4 页触摸按键区。"""
import os

from PIL import Image

SRC = r"E:\zhikong\refs\lockboard\img\page4.png"
im = Image.open(SRC)
w, h = im.size
print("原图:", w, h)

# 左上：TTP229 及其引脚
crops = {
    "ttp229": (int(w * 0.02), int(h * 0.05), int(w * 0.45), int(h * 0.45)),
    "aw9523": (int(w * 0.55), int(h * 0.05), int(w * 0.98), int(h * 0.50)),
    "table":  (int(w * 0.05), int(h * 0.38), int(w * 0.55), int(h * 0.68)),
}
for name, box in crops.items():
    c = im.crop(box)
    c = c.resize((c.width * 3, c.height * 3), Image.LANCZOS)
    out = r"E:\zhikong\refs\lockboard\img\p4_%s.png" % name
    c.save(out)
    print(out, c.size, os.path.getsize(out) // 1024, "KB")

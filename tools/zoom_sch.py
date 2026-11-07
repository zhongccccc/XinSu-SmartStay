# -*- coding: utf-8 -*-
"""裁剪并放大原理图第 3 页的核心板引脚区，便于确认 GPIO 对应关系。"""
import os

from PIL import Image

SRC = r"E:\zhikong\refs\lockboard\img\page3.png"
OUT = r"E:\zhikong\refs\lockboard\img\page3_zoom.png"

im = Image.open(SRC)
w, h = im.size
print("原图尺寸:", w, h)

# 核心板符号大致在左上到中部
box = (int(w * 0.22), int(h * 0.05), int(w * 0.72), int(h * 0.42))
crop = im.crop(box)
crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)
crop.save(OUT)
print("已保存:", OUT, crop.size, os.path.getsize(OUT) // 1024, "KB")

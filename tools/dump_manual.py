# -*- coding: utf-8 -*-
"""提取实验手册里的构建/烧录相关段落。"""
import docx

PATH = (r"C:\Users\zhong\xwechat_files\wxid_10goeiat75bj22_8ed3\msg\file"
        r"\2026-10\实验手册01-OpenHarmony南向开发环境搭建.docx")
OUT = r"E:\zhikong\refs\lock\manual01.txt"

d = docx.Document(PATH)
lines = []
for p in d.paragraphs:
    t = p.text.strip()
    if t:
        lines.append(t)
for tb in d.tables:
    for row in tb.rows:
        cells = [c.text.strip() for c in row.cells if c.text.strip()]
        if cells:
            lines.append(" | ".join(cells))

text = "\n".join(lines)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(text)
print("段落数:", len(lines), "字符数:", len(text), "->", OUT)

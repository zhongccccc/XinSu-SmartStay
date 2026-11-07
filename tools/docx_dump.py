# -*- coding: utf-8 -*-
"""导出 docx 全文（含表格），便于阅读实验手册。"""
import sys

from docx import Document

src, out = sys.argv[1], sys.argv[2]
d = Document(src)
lines = []
for p in d.paragraphs:
    t = p.text.strip()
    if t:
        style = p.style.name if p.style is not None else ""
        prefix = "#" * (1 if style.startswith("Heading 1") else 2 if style.startswith("Heading 2")
                        else 3 if style.startswith("Heading 3") else 0)
        lines.append((prefix + " " + t) if prefix else t)
for i, tbl in enumerate(d.tables, 1):
    lines.append("\n[TABLE %d]" % i)
    for row in tbl.rows:
        lines.append(" | ".join(c.text.strip().replace("\n", " ") for c in row.cells))
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("wrote", out, len(lines), "blocks")

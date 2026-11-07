# -*- coding: utf-8 -*-
"""把引脚表导出成 UTF-8 文本，便于阅读。"""
import io
import sys

import openpyxl

BASE = r"C:\Users\zhong\Desktop\通晓开发板（鸿蒙南向轻量系统开发板）\02-电路原理图"
OUT = r"E:\zhikong\refs\lock\pins.txt"

buf = io.StringIO()
for fn in ["通晓开发板引脚使用.xlsx", "RK2206引脚复用表.xlsx"]:
    path = BASE + "\\" + fn
    buf.write("=" * 78 + "\n文件: %s\n" % fn)
    wb = openpyxl.load_workbook(path, data_only=True)
    for ws in wb.worksheets:
        buf.write("-" * 70 + "\n工作表: %s  (%dx%d)\n" % (ws.title, ws.max_row, ws.max_column))
        for r in ws.iter_rows(values_only=True):
            cells = [str(c).strip() for c in r if c is not None and str(c).strip()]
            if cells:
                buf.write("  " + " | ".join(cells) + "\n")

with open(OUT, "w", encoding="utf-8") as f:
    f.write(buf.getvalue())
print("written", OUT, len(buf.getvalue()), "chars")

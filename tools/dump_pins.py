# -*- coding: utf-8 -*-
"""导出通晓开发板引脚表，找电机/门磁/键盘/NFC/指纹的引脚。"""
import sys

import openpyxl

BASE = r"C:\Users\zhong\Desktop\通晓开发板（鸿蒙南向轻量系统开发板）\02-电路原理图"
FILES = ["通晓开发板引脚使用.xlsx", "RK2206引脚复用表.xlsx"]

for fn in FILES:
    path = BASE + "\\" + fn
    print("=" * 70)
    print("文件:", fn)
    try:
        wb = openpyxl.load_workbook(path, data_only=True)
    except Exception as e:
        print("  打不开:", e)
        continue
    for ws in wb.worksheets:
        print("-" * 60)
        print("工作表:", ws.title, " 尺寸:", ws.max_row, "x", ws.max_column)
        for r in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 60), values_only=True):
            cells = [str(c).strip() for c in r if c is not None and str(c).strip()]
            if cells:
                print("   " + " | ".join(cells))

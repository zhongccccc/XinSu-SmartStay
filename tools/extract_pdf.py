#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取 PDF 文本（用于阅读身份证 SAM 接口手册）。"""
import sys

from pypdf import PdfReader

src = sys.argv[1]
out = sys.argv[2]
r = PdfReader(src)
print("pages:", len(r.pages))
with open(out, "w", encoding="utf-8") as f:
    for i, p in enumerate(r.pages, 1):
        try:
            t = p.extract_text() or ""
        except Exception as e:
            t = "<page %d extract failed: %s>" % (i, e)
        f.write("\n\n===== PAGE %d =====\n" % i)
        f.write(t)
print("wrote", out)

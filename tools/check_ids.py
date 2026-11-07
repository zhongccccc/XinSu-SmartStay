# -*- coding: utf-8 -*-
"""比对各文件引用的 element id 是否都存在。"""
import re

J = r"E:\zhikong\app\web\app.js"
H = r"E:\zhikong\app\web\index.html"
js = open(J, encoding="utf-8").read()
html = open(H, encoding="utf-8").read()

ids = set(re.findall(r"\$\('#([A-Za-z0-9_-]+)'\)", js))
ids |= set(re.findall(r"getElementById\('([A-Za-z0-9_-]+)'\)", js))
ids |= set(re.findall(r"getElementById\(\"([A-Za-z0-9_-]+)\"\)", js))

have = set(re.findall(r'id="([A-Za-z0-9_-]+)"', html))
missing = sorted(i for i in ids if i not in have)
print("JS 引用 id 数:", len(ids))
print("HTML 现有 id 数:", len(have))
print("缺失 id:", missing)

# -*- coding: utf-8 -*-
"""把参考资料里的 GBK/GB18030 文本转成 UTF-8，方便阅读。"""
import os
import sys

ROOT = r"E:\zhikong\refs\idcard"
OUT = r"E:\zhikong\refs\txt"
EXTS = (".h", ".c", ".cpp", ".cs", ".py", ".txt", ".cfg", ".html", ".xml", ".java", ".pas", ".vb")

os.makedirs(OUT, exist_ok=True)
count = 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    # 跳过编译中间产物
    dirnames[:] = [d for d in dirnames if d.lower() not in ("debug", "release", ".vs", "packages", "obj", "bin")]
    for fn in filenames:
        if not fn.lower().endswith(EXTS):
            continue
        src = os.path.join(dirpath, fn)
        if os.path.getsize(src) > 2_000_000:
            continue
        try:
            raw = open(src, "rb").read()
        except Exception:
            continue
        text = None
        for enc in ("utf-8-sig", "utf-8", "gb18030", "gbk", "latin-1"):
            try:
                text = raw.decode(enc)
                break
            except Exception:
                continue
        if text is None:
            continue
        rel = os.path.relpath(src, ROOT).replace("\\", "_").replace("/", "_")
        dst = os.path.join(OUT, rel + ".txt")
        try:
            with open(dst, "w", encoding="utf-8") as f:
                f.write(text)
            count += 1
        except Exception as e:
            print("skip", src, e)

print("converted", count, "files ->", OUT)
for f in sorted(os.listdir(OUT))[:40]:
    print("  ", f)

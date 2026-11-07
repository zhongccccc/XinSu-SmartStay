# -*- coding: utf-8 -*-
"""把关键参考文件转成 UTF-8 + ASCII 文件名，便于阅读。"""
import os
import shutil

ROOT = r"E:\zhikong\refs\idcard"
OUT = r"E:\zhikong\refs\key"
os.makedirs(OUT, exist_ok=True)

targets = []


def find(base, name_fragment):
    hits = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d.lower() not in ("debug", "release", ".vs", "packages", "obj")]
        for fn in filenames:
            if name_fragment.lower() in fn.lower():
                hits.append(os.path.join(dirpath, fn))
    return hits


idroot = os.path.join(ROOT, "二代身份证阅读器")
rfroot = os.path.join(ROOT, "读卡器")

mapping = [
    ("bland.h", "bland_h", idroot),
    ("sdtapi.h", "sdtapi_h", idroot),
    ("main.c", "main_c", idroot),
    ("sdtapi_dll.py", "sdtapi_dll_py", idroot),
    ("webapi_http.py", "webapi_http_py", idroot),
    ("idreader.cfg", "idreader_cfg", idroot),
    ("http_service.cfg", "http_service_cfg", idroot),
    ("目录说明.txt", "sdk_readme", idroot),
    ("WebAPI说明.html", "webapi_html", idroot),
    ("bland.cs", "bland_cs", idroot),
]

for frag, alias, base in mapping:
    for p in find(base, frag):
        if "packages" in p.lower():
            continue
        try:
            raw = open(p, "rb").read()
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
        # 同名多份时加序号
        dst = os.path.join(OUT, alias + ".txt")
        i = 1
        while os.path.exists(dst):
            i += 1
            dst = os.path.join(OUT, "%s_%d.txt" % (alias, i))
        with open(dst, "w", encoding="utf-8") as f:
            f.write(text)
        print("%-22s <- %s (%d bytes)" % (os.path.basename(dst), p.replace(ROOT, ""), len(text)))
        break

# RFID 包里的说明文档
for p in find(rfroot, ".pdf") + find(rfroot, "说明") + find(rfroot, ".doc"):
    print("RFID doc:", p.replace(ROOT, ""))

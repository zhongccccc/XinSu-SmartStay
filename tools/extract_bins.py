# -*- coding: utf-8 -*-
"""从新版 SDK 压缩包里抽取 aarch64 二进制，供分析。"""
import os
import zipfile

SRC = r"E:\zhikong\refs\idcard\二代身份证阅读器\SDK_20261003.zip"
OUT = r"E:\zhikong\refs\bin"

WANT = [
    "SDK/Bin/Linux/aarch64/id_reader",
    "SDK/Library/Linux/aarch64/libsdtapi.so",
    "SDK/Library/Linux/aarch64/libbland.so",
    "SDK/Library/Linux/aarch64/libidreader.so",
    "SDK/Bin/Linux/idreader.service",
    "SDK/Bin/Linux/install.sh",
]

os.makedirs(OUT, exist_ok=True)
z = zipfile.ZipFile(SRC)
names = set(z.namelist())
for w in WANT:
    if w not in names:
        print("MISSING", w)
        continue
    data = z.read(w)
    dst = os.path.join(OUT, os.path.basename(w))
    with open(dst, "wb") as f:
        f.write(data)
    os.chmod(dst, 0o755)
    print("%-20s %8.1f KB" % (os.path.basename(w), len(data) / 1024))

# 顺便看看还有没有别的 riscv 痕迹
riscv = [n for n in names if "riscv" in n.lower()]
print("riscv entries:", riscv or "none")

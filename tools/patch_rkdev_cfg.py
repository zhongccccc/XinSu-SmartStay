# -*- coding: utf-8 -*-
"""改写 RKDevTool 的 config.cfg：把相对路径换成 E:\\zhikong\\firmware 下的绝对路径。

config.cfg 里的字符串是 UTF-16LE，字段长度固定；新路径更短，用 0x00 补满即可。
"""
import os
import shutil
import sys

TARGETS = [
    r"E:\zhikong\firmware\tools\config.cfg",
    r"E:\zhikong\build_windows\device\rockchip\tools\windows\config.cfg",
]
PAIRS = [
    (r"..\..\..\out\rk2206\isoftstone-rk2206\images\rk2206_db_loader.bin",
     r"E:\zhikong\firmware\rk2206_db_loader.bin"),
    (r"..\..\..\out\rk2206\isoftstone-rk2206\images\Firmware.img",
     r"E:\zhikong\firmware\Firmware.img"),
]

for path in TARGETS:
    if not os.path.exists(path):
        print("跳过（不存在）:", path)
        continue
    shutil.copy2(path, path + ".bak")
    data = bytearray(open(path, "rb").read())
    changed = []
    for old, new in PAIRS:
        ob = old.encode("utf-16-le")
        nb = new.encode("utf-16-le")
        idx = data.find(ob)
        if idx < 0:
            print("  [%s] 没找到: %s" % (os.path.basename(os.path.dirname(path)), old))
            continue
        if len(nb) > len(ob):
            print("  !! 新路径更长，跳过:", new)
            continue
        data[idx:idx + len(ob)] = nb + b"\x00" * (len(ob) - len(nb))
        changed.append((old, new))
    open(path, "wb").write(data)
    print("已处理:", path)
    for old, new in changed:
        print("   %s\n   -> %s" % (old, new))

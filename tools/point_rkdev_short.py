# -*- coding: utf-8 -*-
"""把 RKDevTool 默认固件路径指向 E:\\zhikong\\fs（短路径以适配固定长度字段）。"""
import os

SHORT = r"E:\zhikong\fs"
os.makedirs(SHORT, exist_ok=True)

TARGETS = [
    r"E:\zhikong\firmware\tools\config.cfg",
    r"E:\zhikong\build_windows\device\rockchip\tools\windows\config.cfg",
]
PAIRS = [
    (r"E:\zhikong\firmware\rk2206_db_loader.bin",
     SHORT + r"\rk2206_db_loader.bin"),
    (r"E:\zhikong\firmware\Firmware.img",
     SHORT + r"\Firmware.img"),
]

for path in TARGETS:
    if not os.path.exists(path):
        print("skip:", path)
        continue
    data = bytearray(open(path, "rb").read())
    ok = 0
    for old, new in PAIRS:
        ob, nb = old.encode("utf-16-le"), new.encode("utf-16-le")
        i = data.find(ob)
        if i < 0:
            print("  not found:", old)
            continue
        if len(nb) > len(ob):
            print("  still too long:", new)
            continue
        data[i:i + len(ob)] = nb + b"\x00" * (len(ob) - len(nb))
        ok += 1
    open(path, "wb").write(data)
    print("updated %s (%d paths)" % (path, ok))

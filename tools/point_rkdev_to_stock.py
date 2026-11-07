# -*- coding: utf-8 -*-
"""把 RKDevTool 的默认固件路径指向原厂镜像。"""
import os
import shutil

TARGETS = [
    r"E:\zhikong\firmware\tools\config.cfg",
    r"E:\zhikong\build_windows\device\rockchip\tools\windows\config.cfg",
]
PAIRS = [
    (r"E:\zhikong\firmware\rk2206_db_loader.bin",
     r"E:\zhikong\firmware_stock\rk2206_db_loader.bin"),
    (r"E:\zhikong\firmware\Firmware.img",
     r"E:\zhikong\firmware_stock\Firmware.img"),
]

for path in TARGETS:
    if not os.path.exists(path):
        print("skip:", path)
        continue
    data = bytearray(open(path, "rb").read())
    for old, new in PAIRS:
        ob, nb = old.encode("utf-16-le"), new.encode("utf-16-le")
        i = data.find(ob)
        if i < 0:
            print("  not found in %s: %s" % (os.path.basename(os.path.dirname(path)), old))
            continue
        if len(nb) > len(ob):
            print("  too long, skip:", new)
            continue
        data[i:i + len(ob)] = nb + b"\x00" * (len(ob) - len(nb))
    open(path, "wb").write(data)
    print("updated:", path)
print("done")

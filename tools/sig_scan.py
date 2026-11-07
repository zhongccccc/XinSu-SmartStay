#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在厂商 aarch64 库里搜索协议特征字节，判断读卡器用的是哪套帧格式。"""
import re

LIBS = [
    "/opt/zhikong/idreader/lib/libsdtapi.so",
    "/opt/zhikong/idreader/lib/libbland.so",
    "/opt/zhikong/idreader/lib/libidreader.so",
    "/opt/zhikong/idreader/bin/id_reader",
]

# 候选帧头
SIGS = {
    "华视 AA AA AA 96 69": bytes.fromhex("aaaaaa9669"),
    "96 69 05": bytes.fromhex("966905"),
    "SDT 96 69": bytes.fromhex("9669"),
    "APDU 00 A4": bytes.fromhex("00a40000"),
    "00 84 00 00": bytes.fromhex("00840000"),
    "hid2com": b"hid2com",
    "no card": b"no card",
    "usb report type": b"usb report type",
}

for path in LIBS:
    try:
        data = open(path, "rb").read()
    except OSError as e:
        print(path, "open fail", e)
        continue
    print("=== %s (%.0f KB) ===" % (path.rsplit("/", 1)[-1], len(data) / 1024))
    for name, sig in SIGS.items():
        idxs = [m.start() for m in re.finditer(re.escape(sig), data)]
        if idxs:
            print("   %-22s x%d  首个偏移 0x%X" % (name, len(idxs), idxs[0]))
            # 打印首个命中附近的字节
            o = max(0, idxs[0] - 16)
            print("      上下文: %s" % data[o:o + 48].hex(" "))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 hardware_LIBS 里移除厂商示例 iot_smart_home_example，只保留我们的应用。"""
P = "/home/openharmony/txsmartropenharmony/device/rockchip/rk2206/sdk_liteos/Makefile"

s = open(P, encoding="utf-8", errors="replace").read()
before = None
for line in s.splitlines():
    if line.startswith("hardware_LIBS"):
        before = line
        break

s2 = s.replace("hardware_LIBS = -lhal_iothardware -lhardware  -liot_smart_home_example ",
               "hardware_LIBS = -lhal_iothardware -lhardware ")
s2 = s2.replace("hardware_LIBS = -lhal_iothardware -lhardware -liot_smart_home_example ",
                "hardware_LIBS = -lhal_iothardware -lhardware ")

if s2 == s:
    print("未匹配到，当前行：", before)
else:
    open(P, "w", encoding="utf-8").write(s2)
    print("已移除 iot_smart_home_example")

for line in open(P, encoding="utf-8", errors="replace"):
    if line.startswith("hardware_LIBS") or line.startswith("app_LIBS"):
        print("  " + line.rstrip())

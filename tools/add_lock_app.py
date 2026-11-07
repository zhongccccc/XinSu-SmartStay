#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把门锁应用重新装进源码树（带 -lzk_lock 链接）。"""
import os

ROOT = "/home/openharmony/txsmartropenharmony"
APP = ROOT + "/applications/sample/wifi-iot/app"
zdir = APP + "/zhikong_lock"
os.makedirs(zdir, exist_ok=True)

# app/BUILD.gn
p = APP + "/BUILD.gn"
s = open(p, encoding="utf-8").read()
if "zhikong_lock" not in s:
    s = s.replace("features = [", 'features = [\n        "zhikong_lock:zk_lock",', 1)
    open(p, "w", encoding="utf-8").write(s)
    print("app/BUILD.gn: 已加入")
else:
    print("app/BUILD.gn: 已存在")

# Makefile
m = ROOT + "/device/rockchip/rk2206/sdk_liteos/Makefile"
s = open(m, encoding="utf-8", errors="replace").read()
if "-lzk_lock" not in s:
    s = s.replace("app_LIBS = -lshellcmd ", "app_LIBS = -lshellcmd -lzk_lock ", 1)
    open(m, "w", encoding="utf-8").write(s)
    print("Makefile: 已加入 -lzk_lock")
else:
    print("Makefile: 已存在")

print("\n=== 检查 ===")
print(open(p, encoding="utf-8").read().split("lite_component")[-1])
for line in open(m, encoding="utf-8", errors="replace"):
    if line.startswith("app_LIBS"):
        print(line.rstrip())

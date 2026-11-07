#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 -lzk_lock 加进 SDK Makefile 的 app_LIBS（whole-archive 段）。"""
P = "/home/openharmony/txsmartropenharmony/device/rockchip/rk2206/sdk_liteos/Makefile"

s = open(P, encoding="utf-8", errors="replace").read()
if "-lzk_lock" in s:
    print("已经包含 -lzk_lock")
else:
    old = "app_LIBS = -lshellcmd "
    new = "app_LIBS = -lshellcmd -lzk_lock "
    if old not in s:
        print("!! 没找到 app_LIBS 行")
    else:
        open(P, "w", encoding="utf-8").write(s.replace(old, new, 1))
        print("已修改")

for line in open(P, encoding="utf-8", errors="replace"):
    if line.startswith("app_LIBS") or line.startswith("LIBS="):
        print("  " + line.rstrip())

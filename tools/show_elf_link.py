#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打印 liteos.elf 的链接语句，看它链了哪些库。"""
import re

P = "/home/openharmony/txsmartropenharmony/out/rk2206/isoftstone-rk2206/build.ninja"
s = open(P, encoding="utf-8", errors="replace").read()

i = s.find("build liteos.elf")
if i < 0:
    print("没找到 liteos.elf")
    raise SystemExit

seg = s[i:i + 12000]
print("=== 链接语句前 1500 字 ===")
print(seg[:1500])
print()
print("=== 其中出现的 lib*.a ===")
libs = re.findall(r"libs/(lib[\w\-]+\.a)", seg)
for name in libs:
    print("  ", name)
print("总计", len(libs), "个")
print()
print("=== 是否包含 startup / app ===")
for key in ("libstartup", "app.stamp", "whole-archive", "start-group", "zk_lock"):
    print("  %-16s %s" % (key, "有" if key in seg else "无"))

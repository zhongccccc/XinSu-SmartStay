#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打印 build.ninja 中引用 libzk_lock.a 的上下文。"""
import re

P = "/home/openharmony/txsmartropenharmony/out/rk2206/isoftstone-rk2206/build.ninja"
s = open(P, encoding="utf-8", errors="replace").read()

for m in re.finditer(r"libzk_lock\.a", s):
    a = max(0, m.start() - 260)
    b = min(len(s), m.end() + 160)
    print("=" * 70)
    print(s[a:b].replace("\n", "\\n"))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修 hb 的 UnicodeDecodeError：把构建输出的解码改成容错模式。"""
P = "/usr/local/lib/python3.8/dist-packages/hb/common/utils.py"

src = open(P, encoding="utf-8").read()
if "errors='replace'" in src and "encoding='utf-8'," in src:
    print("已经修过")
else:
    old = """                                   encoding='utf-8',
                                   **kwargs)"""
    new = """                                   encoding='utf-8',
                                   errors='replace',
                                   **kwargs)"""
    if old not in src:
        print("!! 没找到目标片段")
    else:
        open(P, "w", encoding="utf-8").write(src.replace(old, new, 1))
        print("已修复：Popen 增加 errors='replace'")

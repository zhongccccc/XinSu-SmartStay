#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 zhikong_lock 加进 applications/sample/wifi-iot/app/BUILD.gn 的 features。"""
P = "/home/openharmony/txsmartropenharmony/applications/sample/wifi-iot/app/BUILD.gn"

s = open(P, encoding="utf-8").read()
if "zhikong_lock" in s:
    print("已经包含 zhikong_lock，无需修改")
else:
    s2 = s.replace("features = [", 'features = [\n        "zhikong_lock:zk_lock",', 1)
    if s2 == s:
        print("!! 没找到 features = [ ，请检查文件")
    else:
        open(P, "w", encoding="utf-8").write(s2)
        print("已写入")

print("---- 现在的内容 ----")
print(open(P, encoding="utf-8").read())

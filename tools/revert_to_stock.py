#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""回退为原厂固件：移除门锁应用、恢复 app/BUILD.gn 和 Makefile。"""
import os
import shutil

ROOT = "/home/openharmony/txsmartropenharmony"
APP = ROOT + "/applications/sample/wifi-iot/app"

# 1. 删掉我们的应用目录
zdir = APP + "/zhikong_lock"
if os.path.isdir(zdir):
    shutil.rmtree(zdir)
    print("已删除:", zdir)
else:
    print("目录不存在（已清）:", zdir)

# 2. 恢复 app/BUILD.gn
p = APP + "/BUILD.gn"
s = open(p, encoding="utf-8").read()
s2 = s.replace('        "zhikong_lock:zk_lock",\n', "")
if s2 != s:
    open(p, "w", encoding="utf-8").write(s2)
    print("已恢复 app/BUILD.gn")
else:
    print("app/BUILD.gn 无需修改")

# 3. 恢复 Makefile
p = ROOT + "/device/rockchip/rk2206/sdk_liteos/Makefile"
s = open(p, encoding="utf-8", errors="replace").read()
s2 = s.replace("app_LIBS = -lshellcmd -lzk_lock ", "app_LIBS = -lshellcmd ")
if s2 != s:
    open(p, "w", encoding="utf-8").write(s2)
    print("已恢复 Makefile")
else:
    print("Makefile 无需修改")

print()
print("=== 当前 app/BUILD.gn ===")
print(open(APP + "/BUILD.gn", encoding="utf-8").read())
for line in open(p, encoding="utf-8", errors="replace"):
    if line.startswith("app_LIBS"):
        print("=== Makefile ===")
        print(line.rstrip())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""遍历所有 ttyUSB，用门锁协议 ping 一遍。"""
import glob
import sys

sys.path.insert(0, "/opt/zhikong/app")
from backend.devices.lock_board import BoardLock  # noqa: E402

ports = sorted(glob.glob("/dev/ttyUSB*"))
print("端口:", ports)
for dev in ports:
    print("=" * 46)
    print(dev)
    lk = BoardLock(dev, log=lambda *a: None)
    ok, detail = lk.ping(3.0)
    print("  ping ->", ok, detail)
    if ok:
        print("  keypad/bat:", lk.status().get("firmware"))
    lk.close()

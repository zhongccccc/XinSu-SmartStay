#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门锁板实测：ping、开门（1.5 秒自动停）、紧急停止。"""
import sys
import time

sys.path.insert(0, "/opt/zhikong/app")
from backend.devices.lock_board import BoardLock  # noqa: E402

evts = []
lk = BoardLock("/dev/ttyUSB1", on_event=lambda t, v: evts.append((t, v)))

print("1) ping ...")
ok, detail = lk.ping(3.0)
print("   ->", ok, detail)

if ok:
    print("2) open（应转 1.5 秒后自动刹）...")
    print("   ->", lk.open_door("8801"))
    time.sleep(3)
    print("3) close（反向 1.5 秒）...")
    print("   ->", lk.close_door("8801") if hasattr(lk, "close_door") else "no-method")
    time.sleep(2.5)

print("事件:", evts)
print("状态:", lk.status())
lk.close()

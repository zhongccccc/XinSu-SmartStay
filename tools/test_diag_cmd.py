#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 ttyUSB2 上测试门锁命令通路。"""
import sys
import time

sys.path.insert(0, "/opt/zhikong/app")
from backend.devices.lock_board import BoardLock  # noqa: E402

lk = BoardLock("/dev/ttyUSB2", on_event=lambda t, v: print("  EVENT", t, v), log=print)
print("ping :", lk.ping(3.0))
print("open :", lk.open_door("8801"))
time.sleep(1)
print("stop :", lk.revoke("8801"))
print("status:", lk.status())
lk.close()

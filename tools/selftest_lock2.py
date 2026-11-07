#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""驱动自测（shell 版协议）：ping/issue/open/revoke + 事件。"""
import sys
import time

sys.path.insert(0, "/opt/zhikong/app")
from backend.devices.lock_board import BoardLock  # noqa: E402

lk = BoardLock("/opt/zhikong/run/ttyLOCK",
               on_event=lambda t, v: print("  EVENT %s: %s" % (t, v)))
print("ping   :", lk.ping())
print("issue  :", lk.issue("8801", "张三", "123456", "CARD01", 1440))
print("open   :", lk.open_door("8801"))
print("revoke :", lk.revoke("8801"))
print("等待硬件事件…")
time.sleep(9)
print("status :", lk.status())
lk.close()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试：打印驱动收到的每一行，定位 revoke 丢 ACK 的原因。"""
import sys
import time

sys.path.insert(0, "/opt/zhikong/app")
from backend.devices.lock_board import BoardLock  # noqa: E402

lk = BoardLock("/opt/zhikong/run/ttyLOCK", log=lambda *a: None)

_orig = lk._handle


def traced(line):
    if line:
        print("RAW:", repr(line))
    _orig(line)


lk._handle = traced
print("ping:", lk.ping())
time.sleep(0.5)
print("revoke:", lk.revoke("8801"))
time.sleep(0.5)
print("ping2:", lk.ping())
lk.close()

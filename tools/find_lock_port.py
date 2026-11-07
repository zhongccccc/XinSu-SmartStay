#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 ttyUSB* 里找出响应门锁协议的口。"""
import glob
import sys

sys.path.insert(0, "/opt/zhikong/app")
from backend.devices.lock_board import BoardLock  # noqa: E402

for dev in sorted(glob.glob("/dev/ttyUSB*")):
    lk = BoardLock(dev, log=lambda *a: None)
    ok, detail = lk.ping(2.5)
    print("%-16s ping=%-5s %s" % (dev, ok, detail))
    lk.close()

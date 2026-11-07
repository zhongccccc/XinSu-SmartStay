#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""两个串口都试：先静听 2 秒，再发 ping。"""
import sys

sys.path.insert(0, "/opt/zhikong/app")
from backend.devices.lock_board import BoardLock  # noqa: E402
from tools_watch import listen  # noqa: E402  (不存在时 fallback)

for dev in ("/dev/ttyUSB0", "/dev/ttyUSB1"):
    print("=" * 50)
    print(dev)
    try:
        listen(dev, 2)
    except Exception:
        pass
    lk = BoardLock(dev, log=lambda *a: None)
    ok, detail = lk.ping(3.0)
    print("  ping ->", ok, detail)
    lk.close()

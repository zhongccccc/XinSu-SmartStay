#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""两个串口分别静听 + ping。"""
import os
import select
import sys
import termios

sys.path.insert(0, "/opt/zhikong/app")
from backend.devices.lock_board import BoardLock  # noqa: E402


def listen(dev, secs):
    fd = os.open(dev, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    a = termios.tcgetattr(fd)
    a[0] = a[1] = 0
    a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
    a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
    a[3] = 0
    a[4] = a[5] = termios.B115200
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, a)
    buf = b""
    import time
    end = time.time() + secs
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.2)
        if r:
            try:
                buf += os.read(fd, 1024)
            except BlockingIOError:
                pass
    os.close(fd)
    if buf:
        txt = buf.decode("utf-8", "ignore")
        print("  静听 %d 字节:" % len(buf))
        for line in txt.splitlines()[:6]:
            if line.strip():
                print("   |", line.strip()[:90])
    else:
        print("  静听无数据")


for dev in ("/dev/ttyUSB0", "/dev/ttyUSB1"):
    print("=" * 52)
    print(dev)
    try:
        listen(dev, 2)
    except Exception as e:
        print("  静听失败:", e)
    lk = BoardLock(dev, log=lambda *a: None)
    ok, detail = lk.ping(3.0)
    print("  ping ->", ok, detail)
    lk.close()

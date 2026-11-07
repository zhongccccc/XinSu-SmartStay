#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""连续试 1200/1250/1300 三档开锁时长。"""
import os
import select
import termios
import time

fd = os.open("/dev/ttyUSB2", os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
a = termios.tcgetattr(fd)
a[0] = a[1] = 0
a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
a[3] = 0
a[4] = a[5] = termios.B115200
a[6][termios.VMIN] = 0
a[6][termios.VTIME] = 0
termios.tcsetattr(fd, termios.TCSANOW, a)
time.sleep(0.3)
try:
    while os.read(fd, 8192):
        pass
except BlockingIOError:
    pass


def cmd(text, wait=1.0):
    os.write(fd, ("%s\r" % text).encode())
    buf = b""
    end = time.time() + wait
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.1)
        if r:
            try:
                buf += os.read(fd, 8192)
            except BlockingIOError:
                pass
    return buf.decode("utf-8", "ignore")


for idx, ms in enumerate((1200, 1250, 1300), 1):
    cmd("zk pt %d 1500" % ms, 0.5)
    print(">>> 第 %d 档：开锁 %dms" % (idx, ms), flush=True)
    cmd("zk open 8808", 0.3)
    time.sleep(9)      # 开 + 6秒自动上锁

os.close(fd)
print("=== 三档试完 ===")

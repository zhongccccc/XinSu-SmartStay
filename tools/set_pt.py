#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在线调整开锁时长。用法: python3 set_pt.py <open_ms> <lock_ms>"""
import os
import select
import sys
import termios
import time

open_ms = sys.argv[1] if len(sys.argv) > 1 else "1350"
lock_ms = sys.argv[2] if len(sys.argv) > 2 else "1500"

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

os.write(fd, ("zk pt %s %s\r" % (open_ms, lock_ms)).encode())
buf = b""
end = time.time() + 1.5
while time.time() < end:
    r, _, _ = select.select([fd], [], [], 0.15)
    if r:
        try:
            buf += os.read(fd, 8192)
        except BlockingIOError:
            pass
os.close(fd)
for line in buf.decode("utf-8", "ignore").splitlines():
    if "PT|OK" in line:
        print(line.strip()[:70])

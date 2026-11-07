#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接监听 ttyUSB2 并 ping 家居板。"""
import os
import select
import termios
import time

fd = os.open('/dev/ttyUSB2', os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
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
end = time.time() + 5
while time.time() < end:
    r, _, _ = select.select([fd], [], [], 0.2)
    if r:
        try:
            buf += os.read(fd, 4096)
        except BlockingIOError:
            pass
os.write(fd, b"zh ping\r")
end = time.time() + 7
while time.time() < end:
    r, _, _ = select.select([fd], [], [], 0.2)
    if r:
        try:
            buf += os.read(fd, 4096)
        except BlockingIOError:
            pass
os.close(fd)
print("收到 %d 字节" % len(buf))
print(buf.decode("utf-8", "ignore")[:500])

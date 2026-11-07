#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""被动监听串口，打印文本和 hex。"""
import os
import select
import sys
import termios
import time

dev = sys.argv[1]
baud = int(sys.argv[2]) if len(sys.argv) > 2 else 115200
secs = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
SPEED = {9600: termios.B9600, 19200: termios.B19200, 38400: termios.B38400,
         57600: termios.B57600, 115200: termios.B115200}.get(baud, termios.B115200)
try:
    fd = os.open(dev, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
except OSError as e:
    print("  open fail:", e)
    raise SystemExit(1)
a = termios.tcgetattr(fd)
a[0] = a[1] = 0
a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
a[3] = 0
a[4] = a[5] = SPEED
a[6][termios.VMIN] = 0
a[6][termios.VTIME] = 0
termios.tcsetattr(fd, termios.TCSANOW, a)
buf = b""
end = time.time() + secs
while time.time() < end:
    r, _, _ = select.select([fd], [], [], 0.2)
    if r:
        try:
            buf += os.read(fd, 512)
        except BlockingIOError:
            pass
os.close(fd)
if not buf:
    print("  (无数据)")
else:
    print("  收到 %d 字节" % len(buf))
    txt = "".join(chr(c) if 32 <= c < 127 or c in (10, 13) else "." for c in buf[:400])
    print("  文本: %r" % txt)
    print("  HEX :", buf[:64].hex(" "))

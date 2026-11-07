#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""监听串口，捕捉板子启动日志。"""
import os
import select
import sys
import termios
import time

dev = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB0"
secs = float(sys.argv[2]) if len(sys.argv) > 2 else 60.0

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

print("监听 %s 共 %d 秒，请给板子复位…" % (dev, secs), flush=True)
buf = b""
total = 0
end = time.time() + secs
while time.time() < end:
    r, _, _ = select.select([fd], [], [], 0.3)
    if not r:
        continue
    try:
        d = os.read(fd, 2048)
    except BlockingIOError:
        continue
    if not d:
        continue
    total += len(d)
    buf += d
    while b"\n" in buf:
        line, buf = buf.split(b"\n", 1)
        t = line.decode("utf-8", "ignore").replace("\r", "").strip()
        if t:
            print("  | " + t[:110], flush=True)

os.close(fd)
print("结束，共 %d 字节" % total, flush=True)

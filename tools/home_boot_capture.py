#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""监听 ttyUSB1 的开机输出，捕捉 zh 应用的日志。"""
import os
import select
import termios
import time

OUT = "/tmp/home_boot.txt"
fd = os.open("/dev/ttyUSB1", os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
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
end = time.time() + 55
while time.time() < end:
    r, _, _ = select.select([fd], [], [], 0.2)
    if r:
        try:
            buf += os.read(fd, 8192)
        except BlockingIOError:
            pass
os.close(fd)

txt = buf.decode("utf-8", "ignore")
open(OUT, "w").write(txt)
lines = [l.strip() for l in txt.splitlines() if l.strip()]
print("收到 %d 字节 / %d 行" % (len(buf), len(lines)))
for l in lines[-40:]:
    print("  |", l[:100])

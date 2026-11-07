#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对指定端口跑键盘学习。"""
import os
import select
import termios
import time

DEV = "/dev/ttyUSB2"

fd = os.open(DEV, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
a = termios.tcgetattr(fd)
a[0] = a[1] = 0
a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
a[3] = 0
a[4] = a[5] = termios.B115200
a[6][termios.VMIN] = 0
a[6][termios.VTIME] = 0
termios.tcsetattr(fd, termios.TCSANOW, a)
time.sleep(0.2)
try:
    while os.read(fd, 4096):
        pass
except BlockingIOError:
    pass

print(">>> zk learn 已发送，请按 1..9 * 0 # 顺序按键")
os.write(fd, b"zk learn\r")

buf = b""
seen = set()
end = time.time() + 165
while time.time() < end:
    r, _, _ = select.select([fd], [], [], 0.15)
    if r:
        try:
            buf += os.read(fd, 8192)
        except BlockingIOError:
            pass
    text = buf.decode("utf-8", "ignore")
    for line in text.split("\n"):
        s = line.strip().replace("\r", "")
        if "LEARN" in s and s not in seen:
            seen.add(s)
            print("  ", s[:100], flush=True)
    if "LEARN|DONE" in text:
        break

os.close(fd)
print("=== 结束 ===")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把每个串口 10 秒内收到的原始内容打出来，看看板子在说什么。"""
import glob
import os
import select
import termios
import time

fds = {}
for p in sorted(glob.glob("/dev/ttyUSB*")):
    try:
        fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        a = termios.tcgetattr(fd)
        a[0] = a[1] = 0
        a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
        a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
        a[3] = 0
        a[4] = a[5] = termios.B115200
        a[6][termios.VMIN] = 0
        a[6][termios.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSANOW, a)
        fds[p] = fd
    except Exception as e:
        print("%s open 失败: %s" % (p, e))

bufs = {p: b"" for p in fds}
end = time.time() + 10
while time.time() < end:
    rl, _, _ = select.select(list(fds.values()), [], [], 0.2)
    for fd in rl:
        name = [k for k, v in fds.items() if v == fd][0]
        try:
            bufs[name] += os.read(fd, 2048)
        except BlockingIOError:
            pass

for fd in fds.values():
    os.close(fd)

for p, b in bufs.items():
    txt = b.decode("utf-8", "ignore")
    print("=== %s : %d 字节 ===" % (p, len(b)))
    if b:
        print("   十六进制:", b[:48].hex(" "))
        printable = "".join(c if 32 <= ord(c) < 127 else "." for c in txt[:200])
        print("   可读部分:", printable)
    print()

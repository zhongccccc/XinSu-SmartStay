#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 ttyUSB1 上同时试 zk / zh 两种协议，判断当前固件。"""
import os
import select
import termios
import time

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
time.sleep(0.3)
try:
    while os.read(fd, 8192):
        pass
except BlockingIOError:
    pass


def cmd(text, wait=2.0):
    os.write(fd, ("%s\r" % text).encode())
    buf = b""
    end = time.time() + wait
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.12)
        if r:
            try:
                buf += os.read(fd, 8192)
            except BlockingIOError:
                pass
    return buf.decode("utf-8", "ignore")


for c in ("zk ping", "zh ping", "ls"):
    print(">>> %s" % c)
    for line in cmd(c).splitlines():
        s = line.strip()
        if s and "ping" not in s.lower():
            print("  |", s[:90])
    print()

os.close(fd)

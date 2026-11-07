#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""确认门锁板凭证已清空。"""
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


def cmd(text, wait=1.5):
    os.write(fd, ("%s\r" % text).encode())
    buf = b""
    end = time.time() + wait
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.15)
        if r:
            try:
                buf += os.read(fd, 8192)
            except BlockingIOError:
                pass
    return buf.decode("utf-8", "ignore")


for line in cmd("zk revoke").splitlines():
    if "REVOKE" in line:
        print("清空:", line.strip()[:60])

for line in cmd("zk ping").splitlines():
    if "PING" in line:
        print("状态:", line.strip()[:90])

os.close(fd)

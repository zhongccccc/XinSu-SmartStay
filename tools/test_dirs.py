#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分别驱动 IA / IB 两个方向，观察门锁动作。"""
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


def cmd(text, wait=0.6):
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


# 确保处于锁着状态
cmd("zk lock", 1.5)
time.sleep(1)

print(">>> A：执行 open（IA 方向，400ms）", flush=True)
cmd("zk pt 400 400", 0.4)
cmd("zk open 8808", 0.4)
time.sleep(4)

print(">>> B：执行 lock（IB 方向，400ms）", flush=True)
cmd("zk lock", 0.4)
time.sleep(2)

os.close(fd)
print("=== 结束：请告诉我 A 和 B 各自发生了什么 ===")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""连续采样 PIR 40 秒，看有没有变化。"""
import glob
import os
import select
import termios
import time


def open_port(dev):
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
    return fd


dev = "/dev/ttyUSB2"
fd = open_port(dev)
time.sleep(0.3)
try:
    while os.read(fd, 8192):
        pass
except BlockingIOError:
    pass

ones = 0
total = 0
changes = []
last = None
end = time.time() + 40
while time.time() < end:
    os.write(fd, b"zh pir\r")
    buf = b""
    t1 = time.time() + 0.5
    while time.time() < t1:
        r, _, _ = select.select([fd], [], [], 0.08)
        if r:
            try:
                buf += os.read(fd, 8192)
            except BlockingIOError:
                pass
    txt = buf.decode("utf-8", "ignore")
    v = None
    for line in txt.splitlines():
        if "ZH|ACK|PIR|" in line:
            try:
                v = int(line.strip().split("|")[-1])
            except Exception:
                pass
    if v is not None:
        total += 1
        if v:
            ones += 1
        if v != last:
            changes.append((round(time.time() % 1000, 1), v))
            last = v
    time.sleep(0.3)

os.close(fd)
print("采样 %d 次，读到 1 的次数: %d" % (total, ones))
print("状态变化:", changes[:10] if changes else "无（一直是同一个值）")

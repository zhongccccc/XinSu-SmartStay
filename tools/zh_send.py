#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 K1 上找到家居板端口，发一条 zh 命令。用法: python3 zh_send.py "zh inv 1" """
import glob
import os
import select
import sys
import termios
import time

CMD = sys.argv[1] if len(sys.argv) > 1 else "zh ping"


def open_port(p):
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
    return fd


def rd(fd, sec):
    b = b""
    end = time.time() + sec
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.1)
        if r:
            try:
                b += os.read(fd, 512)
            except BlockingIOError:
                pass
    return b


target = None
for p in sorted(glob.glob("/dev/ttyUSB*")):
    try:
        fd = open_port(p)
    except Exception:
        continue
    rd(fd, 0.3)
    os.write(fd, b"zh ping\r")
    t = rd(fd, 1.5)
    if b"ZH|ACK|PING" in t:
        target = p
        os.close(fd)
        break
    os.close(fd)

if not target:
    print("!! 没找到家居板")
    raise SystemExit(1)

fd = open_port(target)
rd(fd, 0.3)
os.write(fd, (CMD + "\r").encode())
out = rd(fd, 2.5).decode("utf-8", "ignore")
os.close(fd)
print("端口:", target)
for line in out.splitlines():
    s = line.strip()
    if "ZH|" in s:
        print("  ->", s[:100])

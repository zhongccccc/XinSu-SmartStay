#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""下发开门码 123456，然后监听键盘输入。"""
import os
import select
import sys
import termios
import time

DEV = "/dev/ttyUSB2"


def open_port():
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
    return fd


fd = open_port()
time.sleep(0.2)
try:
    while os.read(fd, 4096):
        pass
except BlockingIOError:
    pass

print(">>> 下发凭证 123456 到 8805 房")
os.write(fd, b"zk issue 8805 123456 CARD01 1440\r")
time.sleep(1.5)
try:
    out = os.read(fd, 4096).decode("utf-8", "ignore")
    for line in out.splitlines():
        if "ZK|" in line:
            print("   ", line.strip()[:100])
except BlockingIOError:
    pass

print()
print(">>> 现在请按 1 2 3 4 5 6 # （监听到第一组 CODE 为止，最多 25 秒）")
buf = b""
end = time.time() + 25
got_code = False
while time.time() < end and not got_code:
    r, _, _ = select.select([fd], [], [], 0.2)
    if not r:
        continue
    try:
        d = os.read(fd, 4096)
    except BlockingIOError:
        continue
    buf += d
    while b"\n" in buf:
        line, buf = buf.split(b"\n", 1)
        s = line.decode("utf-8", "ignore").strip()
        if "ZK|EVT|KEY" in s or "ZK|EVT|CODE" in s or "ZK|EVT|DOOR" in s:
            print("   ", s[:90])
        if "ZK|EVT|CODE" in s:
            got_code = True

os.close(fd)
print(">>> 结束")

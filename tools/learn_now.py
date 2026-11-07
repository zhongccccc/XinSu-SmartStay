#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""先确认板子，再启动键盘学习。"""
import glob
import os
import select
import sys
import termios
import time

sys.path.insert(0, "/opt/zhikong/app")
from backend.devices.lock_board import BoardLock  # noqa: E402


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


ports = sorted(glob.glob("/dev/ttyUSB*"))
print("串口:", ports)

dev = None
for p in ports:
    lk = BoardLock(p, log=lambda *a: None)
    ok, detail = lk.ping(2.0)
    lk.close()
    print("  %-16s ping=%s %s" % (p, ok, detail))
    if ok and not dev:
        dev = p

if not dev:
    print("!! 没有板子响应，可能没上电/串口没插")
    raise SystemExit(1)

print("使用端口:", dev)
fd = open_port(dev)
time.sleep(0.3)
try:
    while os.read(fd, 8192):
        pass
except BlockingIOError:
    pass

print(">>> 发送 zk learn")
os.write(fd, b"zk learn\r")

buf = b""
seen = set()
end = time.time() + 130
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
            print("  ", s[:90], flush=True)
    if "LEARN|DONE" in text:
        break

os.close(fd)
print("=== 结束 ===")

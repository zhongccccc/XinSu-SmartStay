#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""执行键盘学习，实时打印进度。"""
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


dev = None
for p in sorted(glob.glob("/dev/ttyUSB*")):
    lk = BoardLock(p, log=lambda *a: None)
    ok, _ = lk.ping(1.5)
    lk.close()
    if ok:
        dev = p
        break
if not dev:
    print("!! 没有端口响应")
    raise SystemExit(1)
print("端口:", dev)

fd = open_port(dev)
time.sleep(0.3)
try:
    while os.read(fd, 4096):
        pass
except BlockingIOError:
    pass

os.write(fd, b"zk learn\r")
buf = b""
end = time.time() + 150
last_printed = 0
while time.time() < end:
    r, _, _ = select.select([fd], [], [], 0.15)
    if r:
        try:
            buf += os.read(fd, 8192)
        except BlockingIOError:
            pass
    text = buf.decode("utf-8", "ignore")
    lines = text.splitlines()
    for line in lines[last_printed:]:
        s = line.strip()
        if "LEARN" in s:
            print("  ", s[:90], flush=True)
    last_printed = len(lines)
    if "LEARN|DONE" in text:
        time.sleep(0.5)
        break

os.close(fd)
print("结束")

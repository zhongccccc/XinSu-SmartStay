#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""指纹录入第 1 步：连续重试 en1，直到抓取成功。"""
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


def drain(fd):
    try:
        while os.read(fd, 4096):
            pass
    except BlockingIOError:
        pass


def read_for(fd, secs):
    buf = b""
    end = time.time() + secs
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.08)
        if r:
            try:
                buf += os.read(fd, 4096)
            except BlockingIOError:
                pass
    return buf.decode("utf-8", "ignore")


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
print("端口:", dev, "  现在请把手指按上并保持…")

fd = open_port(dev)
time.sleep(0.2)
drain(fd)

ok = False
for attempt in range(15):
    os.write(fd, b"zk en1\r")
    buf = read_for(fd, 1.2)
    for line in buf.splitlines():
        if "ZK|ACK|EN1|OK" in line:
            ok = True
            break
    if ok:
        print("   第 %d 次尝试成功" % (attempt + 1))
        break
    print("   第 %d 次未抓到，继续…" % (attempt + 1))

print("结果:", "EN1 OK（第一枚已采集）" if ok else "EN1 失败（没抓到指纹）")
os.close(fd)

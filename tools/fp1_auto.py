#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""找端口并执行指纹录入第一步（按住手指时运行）。"""
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


def read_for(fd, secs):
    buf = b""
    end = time.time() + secs
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.1)
        if r:
            try:
                buf += os.read(fd, 4096)
            except BlockingIOError:
                pass
    return buf.decode("utf-8", "ignore")


# 找端口
dev = None
for p in sorted(glob.glob("/dev/ttyUSB*")):
    lk = BoardLock(p, log=lambda *a: None)
    ok, _ = lk.ping(2.0)
    lk.close()
    if ok:
        dev = p
        break
if not dev:
    print("!! 没有端口响应门锁协议")
    raise SystemExit(1)
print("端口:", dev)

fd = open_port(dev)
time.sleep(0.3)
try:
    while os.read(fd, 4096):
        pass
except BlockingIOError:
    pass

print(">>> 第 1 次按压：采集中（最长 15 秒）…")
os.write(fd, b"zk en1\r")
buf = ""
end = time.time() + 15
while time.time() < end:
    buf += read_for(fd, 0.5)
    if "ZK|ACK|EN1" in buf:
        break
for line in buf.splitlines():
    if "ZK|ACK|EN1" in line:
        print("   ", line.strip()[:80])
os.close(fd)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""指纹录入第 2 步：重试 en2 直到合并入库成功。"""
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
print("端口:", dev, "  请按第二次（同一个手指）…")

fd = open_port(dev)
time.sleep(0.2)
drain(fd)

ok = False
for attempt in range(15):
    os.write(fd, b"zk en2 0\r")
    buf = read_for(fd, 1.5)
    for line in buf.splitlines():
        s = line.strip()
        if "ZK|ACK|EN2" in s:
            print("   ", s[:90])
            if "|OK" in s:
                ok = True
    if ok:
        break
    print("   第 %d 次未成功，重试…" % (attempt + 1))

print("结果:", "入库成功（0 号位）" if ok else "入库失败")
os.close(fd)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""识别 ttyUSB0 是门锁板还是 RFID 读卡器。"""
import os
import select
import sys
import termios
import time

sys.path.insert(0, "/opt/zhikong/app")
from backend.devices.lock_board import BoardLock  # noqa: E402


def listen(dev, secs=3.0):
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
    buf = b""
    end = time.time() + secs
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.2)
        if r:
            try:
                buf += os.read(fd, 1024)
            except BlockingIOError:
                pass
    os.close(fd)
    return buf


print("=== 静听 ttyUSB0 3 秒 ===")
data = listen("/dev/ttyUSB0")
if data:
    txt = data.decode("utf-8", "ignore")
    for line in txt.splitlines()[:10]:
        if line.strip():
            print("  |", line.strip()[:100])
else:
    print("  (无数据)")

print()
print("=== 发 zk ping ===")
lk = BoardLock("/dev/ttyUSB0", log=lambda *a: None)
ok, detail = lk.ping(3.0)
print("  ->", ok, detail)
print("  status:", lk.status())
lk.close()

print()
print("=== 试着当 RFID 读（V23B 帧）===")
try:
    fd = os.open("/dev/ttyUSB0", os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    a = termios.tcgetattr(fd)
    a[0] = a[1] = 0
    a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
    a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
    a[3] = 0
    a[4] = a[5] = termios.B9600
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, a)
    os.write(fd, bytes([0x01, 0x08, 0xA1, 0x20, 0x00, 0x01, 0x00, 0x76]))
    time.sleep(0.5)
    r, _, _ = select.select([fd], [], [], 1.0)
    got = os.read(fd, 64) if r else b""
    os.close(fd)
    print("  回包:", got.hex(" ") if got else "(无)")
except Exception as e:
    print("  失败:", e)

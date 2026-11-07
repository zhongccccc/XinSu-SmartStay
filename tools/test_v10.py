#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v10 测试：ping、空闲键盘掩码、指纹识别。"""
import os
import select
import sys
import termios
import time

DEV = "/dev/ttyUSB2"


def raw_cmd(cmd, secs=4.0):
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
    time.sleep(0.2)
    try:
        while os.read(fd, 4096):
            pass
    except BlockingIOError:
        pass
    os.write(fd, (cmd + "\r").encode())
    buf = b""
    end = time.time() + secs
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.2)
        if r:
            try:
                buf += os.read(fd, 4096)
            except BlockingIOError:
                pass
    os.close(fd)
    return buf.decode("utf-8", "ignore")


def show(out, tag):
    for line in out.splitlines():
        s = line.strip()
        if "ZK|" in s:
            print("   ", s[:120])


print("=== ① ping ===")
show(raw_cmd("zk ping", 2.5), "ping")

print()
print("=== ② 键盘空闲掩码（应为 0x0000）===")
for i in range(3):
    out = raw_cmd("zk keys", 1.5)
    for line in out.splitlines():
        if "ZK|ACK|KEYS" in line:
            print("   ", line.strip()[:100])
    time.sleep(0.3)

print()
print("=== ③ 指纹识别 ===")
show(raw_cmd("zk fp", 6.0), "fp")

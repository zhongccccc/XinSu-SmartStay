#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门锁板 v6 实测：ping、外设探测、电机开合。"""
import os
import select
import sys
import termios
import time

sys.path.insert(0, "/opt/zhikong/app")
from backend.devices.lock_board import BoardLock  # noqa: E402

DEV = "/dev/ttyUSB2"


def raw_cmd(cmd, secs=4.0):
    """直接发一条 shell 命令，收集全部回显。"""
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
                buf += os.read(fd, 2048)
            except BlockingIOError:
                pass
    os.close(fd)
    return buf.decode("utf-8", "ignore")


print("=" * 60)
print("① ping")
print("=" * 60)
out = raw_cmd("zk ping", 2.5)
for line in out.splitlines():
    if "ZK|" in line or "[zk]" in line:
        print("  ", line.strip()[:120])

print()
print("=" * 60)
print("② 外设探测 zk probe")
print("=" * 60)
out = raw_cmd("zk probe", 6.0)
for line in out.splitlines():
    if "PROBE" in line:
        print("  ", line.strip()[:120])

print()
print("=" * 60)
print("③ 电机：open（应转 1.5 秒后停）")
print("=" * 60)
out = raw_cmd("zk open", 3.0)
for line in out.splitlines():
    if "ZK|" in line:
        print("  ", line.strip()[:100])
time.sleep(2)

print()
print("④ 电机：close（反向 1.5 秒）")
out = raw_cmd("zk close", 3.0)
for line in out.splitlines():
    if "ZK|" in line:
        print("  ", line.strip()[:100])

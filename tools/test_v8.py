#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v8 实测：ping、硬件扫描、下发凭证 + 本地校验开门。"""
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
                buf += os.read(fd, 2048)
            except BlockingIOError:
                pass
    os.close(fd)
    return buf.decode("utf-8", "ignore")


def show(out, keys=("ZK|",)):
    for line in out.splitlines():
        s = line.strip()
        if any(k in s for k in keys):
            print("   ", s[:120])


print("=" * 62)
print("① ping（应回 v8）")
print("=" * 62)
show(raw_cmd("zk ping", 2.5))

print()
print("=" * 62)
print("② 硬件扫描")
print("=" * 62)
show(raw_cmd("zk scan", 8.0), keys=("ZK|SCAN",))

print()
print("=" * 62)
print("③ 下发凭证")
print("=" * 62)
show(raw_cmd("zk issue 8805 123456 CARD01 1440", 3.0))

print()
print("=" * 62)
print("④ 本地校验开门码 123456（应开门）")
print("=" * 62)
show(raw_cmd("zk code 123456", 3.5))

print()
print("=" * 62)
print("⑤ 错误码 999999（应拒绝）")
print("=" * 62)
show(raw_cmd("zk code 999999", 3.0))

print()
print("=" * 62)
print("⑥ 退房作废")
print("=" * 62)
show(raw_cmd("zk revoke 8805", 3.0))

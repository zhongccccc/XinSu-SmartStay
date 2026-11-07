#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 K1 上找门锁板端口并执行 zk 命令（多次重试，容忍板子忙）。"""
import glob
import os
import select
import sys
import termios
import time

CMDS = sys.argv[1:] if len(sys.argv) > 1 else ["zk ping"]


def open_port(p):
    fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
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


def rd(fd, sec):
    b = b""
    end = time.time() + sec
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.1)
        if r:
            try:
                b += os.read(fd, 512)
            except BlockingIOError:
                pass
    return b


def find_board():
    for attempt in range(3):
        for p in sorted(glob.glob("/dev/ttyUSB*")):
            try:
                fd = open_port(p)
            except Exception:
                continue
            try:
                rd(fd, 0.4)
                for _ in range(2):
                    os.write(fd, b"zk ping\r")
                    t = rd(fd, 2.5)
                    if b"ZK|ACK|PING" in t:
                        return p, t
            finally:
                os.close(fd)
        time.sleep(1.0)
    return None, b""


target, first = find_board()
if not target:
    print("!! 没找到门锁板（已重试 3 轮）")
    raise SystemExit(1)

print("端口:", target)
for line in first.decode("utf-8", "ignore").splitlines():
    if "ZK|ACK|PING" in line:
        print("  ", line.strip()[:110])
        break

fd = open_port(target)
rd(fd, 0.4)
for c in CMDS:
    os.write(fd, (c + "\r").encode())
    out = rd(fd, 3.0).decode("utf-8", "ignore")
    hits = [l.strip() for l in out.splitlines() if "ZK|" in l]
    print(">> %s" % c)
    for h in hits[:4]:
        print("     ", h[:110])
    if not hits:
        print("      (无应答)")
os.close(fd)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 K1 上找门锁板端口，发一条 zk 命令。用法: python3 zk_send.py "zk ping" """
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


target = None
for p in sorted(glob.glob("/dev/ttyUSB*")):
    try:
        fd = open_port(p)
    except Exception:
        continue
    rd(fd, 0.3)
    os.write(fd, b"zk ping\r")
    t = rd(fd, 1.6)
    os.close(fd)
    if b"ZK|ACK|PING" in t:
        target = p
        print("端口:", p)
        for line in t.decode("utf-8", "ignore").splitlines():
            if "ZK|ACK|PING" in line:
                print("  ", line.strip()[:110])
        break

if not target:
    print("!! 没找到门锁板")
    raise SystemExit(1)

fd = open_port(target)
for c in CMDS:
    rd(fd, 0.3)
    os.write(fd, (c + "\r").encode())
    out = rd(fd, 2.2).decode("utf-8", "ignore")
    hits = [l.strip() for l in out.splitlines() if "ZK|" in l]
    print(">> %s" % c)
    for h in hits[:4]:
        print("     ", h[:110])
os.close(fd)

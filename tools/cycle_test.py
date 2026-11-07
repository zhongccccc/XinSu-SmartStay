#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""设 400/600 并跑一次完整循环：开锁 → 6 秒自动上锁。"""
import glob
import os
import select
import termios
import time


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
        while os.read(fd, 8192):
            pass
    except BlockingIOError:
        pass


def read_for(fd, secs):
    buf = b""
    end = time.time() + secs
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.1)
        if r:
            try:
                buf += os.read(fd, 8192)
            except BlockingIOError:
                pass
    return buf


dev = None
for p in sorted(glob.glob("/dev/ttyUSB*")):
    try:
        fd = open_port(p)
    except Exception:
        continue
    time.sleep(0.2)
    drain(fd)
    os.write(fd, b"zk ping\r")
    if b"ZK|ACK|PING" in read_for(fd, 1.6):
        dev = p
    os.close(fd)
    if dev:
        break

if not dev:
    print("!! 没找到门锁板")
    raise SystemExit(1)

fd = open_port(dev)
time.sleep(0.2)
drain(fd)


def cmd(text, wait=1.0):
    os.write(fd, ("%s\r" % text).encode())
    out = read_for(fd, wait).decode("utf-8", "ignore")
    for line in out.splitlines():
        if "PT|OK" in line or "OPEN" in line or "LOCK" in line:
            print("   ", line.strip()[:60])
    return out


print(">>> 设置 开锁400 / 关锁600")
cmd("zk pt 400 600", 0.6)

print(">>> 现在执行一次完整开门 → 6 秒后自动上锁")
cmd("zk open 8808", 0.8)
time.sleep(9)
cmd("zk ping", 1.0)

os.close(fd)
print("=== 请确认：刚才门是不是开了，6 秒后又关上了？ ===")

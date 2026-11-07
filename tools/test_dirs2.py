#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动找端口，分别驱动 IA / IB 两个方向。"""
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
print("端口:", dev)

fd = open_port(dev)
time.sleep(0.2)
drain(fd)


def cmd(text, wait=0.6):
    os.write(fd, ("%s\r" % text).encode())
    return read_for(fd, wait).decode("utf-8", "ignore")


cmd("zk lock", 1.5)
time.sleep(1)

print(">>> A：open（IA 方向 400ms）", flush=True)
cmd("zk pt 400 400", 0.4)
cmd("zk open 8808", 0.4)
time.sleep(4)

print(">>> B：lock（IB 方向 400ms）", flush=True)
cmd("zk lock", 0.4)
time.sleep(2)

os.close(fd)
print("=== 结束 ===")

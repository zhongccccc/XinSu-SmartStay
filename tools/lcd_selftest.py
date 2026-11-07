#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""找到智能家居板并执行 zh lcd 自检。"""
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
        r, _, _ = select.select([fd], [], [], 0.12)
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
    os.write(fd, b"zh ping\r")
    out = read_for(fd, 1.8).decode("utf-8", "ignore")
    os.close(fd)
    if "ZH|ACK|PING" in out:
        dev = p
        print("家居板:", p)
        for line in out.splitlines():
            if "PING" in line:
                print("  ", line.strip()[:90])
        break

if not dev:
    print("!! 没找到智能家居板（zh 协议）")
    raise SystemExit(1)

fd = open_port(dev)
time.sleep(0.2)
drain(fd)

print(">>> 执行 zh lcd 自检（会把屏幕刷红）")
os.write(fd, b"zh lcd\r")
out = read_for(fd, 6.0).decode("utf-8", "ignore")
for line in out.splitlines():
    s = line.strip()
    if "LCD" in s:
        print("  ", s[:100])

print(">>> 顺带测一次传感器")
os.write(fd, b"zh env\r")
out = read_for(fd, 3.0).decode("utf-8", "ignore")
for line in out.splitlines():
    s = line.strip()
    if "ENV" in s:
        print("  ", s[:100])

os.close(fd)
print("=== 完 ===")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""逐条下发 zh 命令，每步都确认板子还活着。"""
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
        for line in out.splitlines():
            if "PING" in line:
                print("板子:", p, "|", line.strip()[:80])
        break

if not dev:
    print("!! 找不到 zh 板子")
    raise SystemExit(1)

fd = open_port(dev)
time.sleep(0.2)
drain(fd)

STEPS = [
    "zh ping",
    "zh i2c",
    "zh ping",
    "zh adc",
    "zh ping",
    "zh pwm",
    "zh ping",
    "zh pir",
    "zh ping",
    "zh beep 150",
    "zh ping",
    "zh env",
    "zh ping",
    "zh lcd",
    "zh ping",
]

for s in STEPS:
    os.write(fd, ("%s\r" % s).encode())
    out = read_for(fd, 2.5).decode("utf-8", "ignore")
    lines = [l.strip() for l in out.splitlines()
             if l.strip() and ("ZH|" in l or "alive" in l)]
    alive = any("ZH|ACK|PING" in l for l in lines)
    print("%-14s -> %s" % (s, "  ".join(lines[:3])[:110] if lines else "(无响应)"))
    if s.startswith("zh ping") and not alive and s != "zh ping":
        print("   !! 上一步之后板子已失联")
        break
    time.sleep(0.3)

os.close(fd)
print("=== 结束 ===")

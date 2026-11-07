#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""手动开灯/关灯 + 读 PIR，判断问题在哪。"""
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


def cmd(fd, text, wait=2.0):
    os.write(fd, ("%s\r" % text).encode())
    buf = b""
    end = time.time() + wait
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.12)
        if r:
            try:
                buf += os.read(fd, 8192)
            except BlockingIOError:
                pass
    return buf.decode("utf-8", "ignore")


dev = None
for p in sorted(glob.glob("/dev/ttyUSB*")):
    try:
        fd = open_port(p)
    except Exception:
        continue
    time.sleep(0.2)
    drain(fd)
    os.write(fd, b"zh ping\r")
    if b"ZH|ACK|PING" in (lambda: b"")().__class__() or True:
        pass
    buf = b""
    end = time.time() + 1.8
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.12)
        if r:
            try:
                buf += os.read(fd, 8192)
            except BlockingIOError:
                pass
    os.close(fd)
    if b"ZH|ACK|PING" in buf:
        dev = p
        break

if not dev:
    print("!! 找不到 zh 板子")
    raise SystemExit(1)
print("板子:", dev)

fd = open_port(dev)
time.sleep(0.2)
drain(fd)

print(">>> 手动开灯：zh light on")
for l in cmd(fd, "zh light on").splitlines():
    if "LIGHT" in l:
        print("   ", l.strip()[:60])
time.sleep(3)

print(">>> 读人体状态：zh pir")
for l in cmd(fd, "zh pir").splitlines():
    if "PIR" in l:
        print("   ", l.strip()[:60])

print(">>> 保持 8 秒，请在这期间在感应器前挥手")
time.sleep(8)

print(">>> 再读人体状态")
for l in cmd(fd, "zh pir").splitlines():
    if "PIR" in l:
        print("   ", l.strip()[:60])

os.close(fd)
print("=== 完 ===")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""观察一次 open → 自动上锁 的完整事件 + 手动关锁对比。"""
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

print(">>> 发送 zk open（400ms 开锁）")
os.write(fd, b"zk open 8808\r")
out = read_for(fd, 1.2).decode("utf-8", "ignore")
for line in out.splitlines():
    if "OPEN" in line or "DOOR" in line:
        print("   ", line.strip()[:70])

print(">>> 等 8 秒，看是否自动上锁")
out = read_for(fd, 8.0).decode("utf-8", "ignore")
for line in out.splitlines():
    if "DOOR" in line or "alive" in line:
        print("   ", line.strip()[:70])

print(">>> 手动 zk lock（600ms 关锁）")
os.write(fd, b"zk lock\r")
out = read_for(fd, 1.5).decode("utf-8", "ignore")
for line in out.splitlines():
    if "LOCK" in line or "DOOR" in line:
        print("   ", line.strip()[:70])

print(">>> 直接给 GPIO 56 通电 600ms（对照组）")
os.write(fd, b"zk gpio 56 600\r")
out = read_for(fd, 1.5).decode("utf-8", "ignore")
for line in out.splitlines():
    if "GPIO" in line:
        print("   ", line.strip()[:70])

os.close(fd)
print("=== 完 ===")

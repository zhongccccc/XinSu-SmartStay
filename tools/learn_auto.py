#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动找端口并跑键盘学习（每键按住 2 秒）。"""
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
    os.write(fd, b"zk ping\r")
    buf = read_for(fd, 2.0)
    os.close(fd)
    if b"ZK|ACK|PING" in buf:
        dev = p
        print("端口:", p)
        break

if not dev:
    print("!! 没有端口响应门控协议")
    raise SystemExit(1)

fd = open_port(dev)
time.sleep(0.2)
drain(fd)

print(">>> 开始学习：按提示顺序按键，每个按住 2 秒")
os.write(fd, b"zk learn\r")

buf = b""
seen = set()
end = time.time() + 170
while time.time() < end:
    r, _, _ = select.select([fd], [], [], 0.12)
    if r:
        try:
            buf += os.read(fd, 8192)
        except BlockingIOError:
            pass
    text = buf.decode("utf-8", "ignore")
    for line in text.split("\n"):
        s = line.strip().replace("\r", "")
        if "LEARN" in s and s not in seen:
            seen.add(s)
            print("  ", s[:100], flush=True)
    if "LEARN|DONE" in text:
        break

os.close(fd)
print("=== 结束 ===")

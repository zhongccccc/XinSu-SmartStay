#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""逐个试引脚，找出真正驱动关锁的那个。"""
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
ver = ""
for p in sorted(glob.glob("/dev/ttyUSB*")):
    try:
        fd = open_port(p)
    except Exception:
        continue
    time.sleep(0.2)
    drain(fd)
    os.write(fd, b"zk ping\r")
    out = read_for(fd, 1.6).decode("utf-8", "ignore")
    os.close(fd)
    if "ZK|ACK|PING" in out:
        dev = p
        ver = [l for l in out.splitlines() if "PING" in l][0].strip()
        break

if not dev:
    print("!! 没找到门锁板")
    raise SystemExit(1)
print("端口:", dev)
print("版本:", ver[:90])
print()

fd = open_port(dev)
time.sleep(0.2)
drain(fd)


def cmd(text, wait=1.2):
    os.write(fd, ("%s\r" % text).encode())
    return read_for(fd, wait).decode("utf-8", "ignore")


# 确认 gpio 命令存在
out = cmd("zk gpio 25 60", 1.0)
if "GPIO" not in out:
    print("!! 固件里还没有 gpio 命令，请刷最新固件")
    os.close(fd)
    raise SystemExit(1)
print("gpio 命令可用")

for idx, pin in enumerate((24, 56, 55, 57), 1):
    print(">>> 第 %d 次：引脚 %d 通电 600ms" % (idx, pin), flush=True)
    cmd("zk gpio %d 600" % pin, 1.4)
    time.sleep(2)

os.close(fd)
print("=== 四次都试完 ===")

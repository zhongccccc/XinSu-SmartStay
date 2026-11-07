#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""依次试三档开锁时长：600 / 800 / 1000 ms。"""
import os
import select
import termios
import time

DEV = "/dev/ttyUSB2"


def open_port():
    fd = os.open(DEV, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
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
    return buf.decode("utf-8", "ignore")


fd = open_port()
time.sleep(0.3)
drain(fd)

for ms in (600, 800, 1000):
    os.write(fd, ("zk pt %d 400\r" % ms).encode())
    time.sleep(0.4)
    print(">>> 第 %d 档：开锁 %dms" % ((600, 800, 1000).index(ms) + 1, ms), flush=True)
    os.write(fd, b"zk open 8808\r")
    time.sleep(1.2)
    out = read_for(fd, 0.8)
    for line in out.splitlines():
        if "PT|OK" in line or "OPEN" in line:
            print("    ", line.strip()[:70])
    time.sleep(7)          # 等自动上锁完成

os.close(fd)
print("=== 三档试完 ===")

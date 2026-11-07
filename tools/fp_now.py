#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""立刻采指纹：连发 3 次 fpid。"""
import os
import select
import sys
import termios
import time

DEV = "/dev/ttyUSB2"


def raw_cmd(cmd, secs=4.0):
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
    time.sleep(0.15)
    try:
        while os.read(fd, 4096):
            pass
    except BlockingIOError:
        pass
    os.write(fd, (cmd + "\r").encode())
    buf = b""
    end = time.time() + secs
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.15)
        if r:
            try:
                buf += os.read(fd, 4096)
            except BlockingIOError:
                pass
    os.close(fd)
    return buf.decode("utf-8", "ignore")


for i in range(3):
    print("===== 第 %d 次 fpid =====" % (i + 1))
    out = raw_cmd("zk fpid", 5.0)
    for line in out.splitlines():
        s = line.strip()
        if "ZK|FP" in s or "ZK|EVT|FP" in s:
            print("  ", s[:120])
    time.sleep(0.6)

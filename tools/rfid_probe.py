#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""监听外接 USB 读卡器（ttyUSB0），打印原始字节，判断波特率/协议。"""
import os
import select
import sys
import termios
import time

DEV = "/dev/ttyUSB0"
BAUDS = [(9600, termios.B9600), (115200, termios.B115200), (19200, termios.B19200)]


def open_at(fd, speed):
    a = termios.tcgetattr(fd)
    a[0] = a[1] = 0
    a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
    a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
    a[3] = 0
    a[4] = a[5] = speed
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, a)


fd = os.open(DEV, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)

for baud, speed in BAUDS:
    open_at(fd, speed)
    time.sleep(0.3)
    try:
        while os.read(fd, 4096):
            pass
    except BlockingIOError:
        pass

    print(">>> 请把卡在读卡器上放一下（%d 波特率，等 6 秒）" % baud, flush=True)
    buf = b""
    end = time.time() + 6
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.15)
        if r:
            try:
                buf += os.read(fd, 4096)
            except BlockingIOError:
                pass
    if buf:
        print("    收到 %d 字节: %s" % (len(buf), buf[:40].hex(" ")), flush=True)
        print("    文本: %r" % buf[:60], flush=True)
    else:
        print("    无数据", flush=True)

os.close(fd)
print("=== 结束 ===")

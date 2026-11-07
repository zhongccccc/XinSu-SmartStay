#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 ttyUSB2 上尝试多种波特率，找出可读的那个。"""
import os
import select
import termios
import time

DEV = "/dev/ttyUSB2"
CAND = [
    (9600, termios.B9600), (19200, termios.B19200), (38400, termios.B38400),
    (57600, termios.B57600), (115200, termios.B115200), (230400, termios.B230400),
    (460800, termios.B460800), (921600, termios.B921600), (1500000, termios.B1500000),
]

fd = os.open(DEV, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)


def set_speed(speed):
    a = termios.tcgetattr(fd)
    a[0] = a[1] = 0
    a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
    a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
    a[3] = 0
    a[4] = a[5] = speed
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, a)


for baud, speed in CAND:
    try:
        set_speed(speed)
    except Exception as e:
        print("%7d : 不支持 (%s)" % (baud, e))
        continue
    time.sleep(0.2)
    buf = b""
    end = time.time() + 3.5
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.2)
        if r:
            try:
                buf += os.read(fd, 4096)
            except BlockingIOError:
                pass
    if not buf:
        print("%7d : 无数据" % baud)
        continue
    # 可读字符比例
    printable = sum(1 for b in buf if 32 <= b < 127 or b in (10, 13))
    ratio = printable / len(buf)
    sample = buf[:60].decode("utf-8", "ignore").replace("\n", " ").replace("\r", " ")
    flag = "  <== 可读" if ratio > 0.85 else ""
    print("%7d : %3d 字节 可读率 %.0f%% | %s%s" % (baud, len(buf), ratio * 100, sample[:50], flag))

os.close(fd)

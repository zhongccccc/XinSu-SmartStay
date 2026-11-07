#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对每个串口 @9600 发读卡命令，找出真正回包的端口。"""
import glob
import os
import select
import termios
import time

CMD = bytes([0x01, 0x08, 0xA1, 0x20, 0x20, 0x00, 0x01, 0x00, 0x76])

for p in sorted(glob.glob("/dev/ttyUSB*")):
    try:
        fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    except Exception as e:
        print("  %-14s 打开失败: %s" % (p, e))
        continue
    a = termios.tcgetattr(fd)
    a[0] = a[1] = 0
    a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
    a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
    a[3] = 0
    a[4] = a[5] = termios.B9600
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, a)

    hits = 0
    noise = 0
    for _ in range(20):
        try:
            while os.read(fd, 512):
                pass
        except BlockingIOError:
            pass
        try:
            os.write(fd, CMD)
        except OSError:
            break
        buf = b""
        t = time.time() + 0.25
        while time.time() < t:
            r, _, _ = select.select([fd], [], [], 0.05)
            if r:
                try:
                    buf += os.read(fd, 256)
                except BlockingIOError:
                    pass
        if len(buf) >= 5:
            hits += 1
            if hits == 1:
                print("  %-14s 有回包: %s" % (p, buf.hex(" ")))
        elif buf:
            noise += 1
    os.close(fd)
    if hits == 0:
        print("  %-14s 无回包（杂音 %d 次）" % (p, noise))

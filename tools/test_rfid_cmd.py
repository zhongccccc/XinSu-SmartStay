#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接在 ttyUSB0 上测试两种读卡命令，看哪种能读到卡。"""
import os
import select
import termios
import time

PORT = "/dev/ttyUSB0"
BAUD = 9600
SPEED = termios.B9600

VARIANTS = [
    ("变体A 01 08 A1 20 20 00 01 00 76", bytes([0x01, 0x08, 0xA1, 0x20, 0x20, 0x00, 0x01, 0x00, 0x76])),
    ("变体B 01 08 A1 20 00 01 00 76",    bytes([0x01, 0x08, 0xA1, 0x20, 0x00, 0x01, 0x00, 0x76])),
]

fd = os.open(PORT, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
a = termios.tcgetattr(fd)
a[0] = a[1] = 0
a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
a[3] = 0
a[4] = a[5] = SPEED
a[6][termios.VMIN] = 0
a[6][termios.VTIME] = 0
termios.tcsetattr(fd, termios.TCSANOW, a)


def drain():
    try:
        while os.read(fd, 4096):
            pass
    except BlockingIOError:
        pass


print("请在 30 秒内把房卡放到读卡器上（保持不动）…")
for name, cmd in VARIANTS:
    print("---- %s ----" % name)
    hits = 0
    end = time.time() + 15
    while time.time() < end:
        drain()
        os.write(fd, cmd)
        buf = b""
        t = time.time() + 0.45
        while time.time() < t:
            r, _, _ = select.select([fd], [], [], 0.05)
            if r:
                try:
                    buf += os.read(fd, 256)
                except BlockingIOError:
                    pass
        if len(buf) >= 5:
            hits += 1
            if hits <= 3:
                print("   收到 %d 字节: %s" % (len(buf), buf.hex(" ")))
        time.sleep(0.05)
    print("   本次收到响应次数: %d" % hits)

os.close(fd)

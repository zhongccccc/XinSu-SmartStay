#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""与 OpenHarmony 门锁板交互：发命令、收回显。"""
import os
import select
import sys
import termios
import time

DEV = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB1"
SPEED = termios.B115200


def open_port():
    fd = os.open(DEV, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    a = termios.tcgetattr(fd)
    a[0] = a[1] = 0
    a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
    a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
    a[3] = 0
    a[4] = a[5] = SPEED
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, a)
    return fd


def read_for(fd, secs):
    buf = b""
    end = time.time() + secs
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.15)
        if r:
            try:
                buf += os.read(fd, 1024)
            except BlockingIOError:
                pass
    return buf


def clean(b):
    out = []
    for c in b:
        if c == 13:
            continue
        if c == 10:
            out.append("\n")
        elif 32 <= c < 127:
            out.append(chr(c))
        else:
            out.append(".")
    return "".join(out)


fd = open_port()
read_for(fd, 0.5)          # 清掉上电噪声

for cmd in ["\n", "help\n", "ls\n", "ps\n"]:
    label = cmd.strip() or "<回车>"
    print(">>> %s" % label)
    os.write(fd, cmd.encode())
    time.sleep(0.35)
    data = read_for(fd, 1.6)
    text = clean(data).strip()
    print(text[:1200] if text else "   (无回显)")
    print("-" * 50)

os.close(fd)

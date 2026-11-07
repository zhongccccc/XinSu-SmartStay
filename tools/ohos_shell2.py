#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""与 OHOS 门锁板交互 v2：用 CR 结尾，先发 Ctrl-C 清状态。"""
import os
import select
import sys
import time
import termios

DEV = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB1"


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
read_for(fd, 0.4)
os.write(fd, b"\x03")          # Ctrl-C，打断可能卡住的输入
time.sleep(0.3)
read_for(fd, 0.4)

for cmd in [b"\r", b"help\r", b"ls /\r", b"ps\r", b"date\r"]:
    print(">>> %s" % cmd.decode(errors="replace").replace("\r", "<CR>"))
    os.write(fd, cmd)
    time.sleep(0.4)
    data = read_for(fd, 2.0)
    text = clean(data).strip()
    print(text[:1500] if text else "   (无回显)")
    print("-" * 55)

os.close(fd)

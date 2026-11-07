#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探测 OHOS 门锁板：任务列表、硬件信息、目录。"""
import os
import select
import sys
import time
import termios

DEV = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB1"
CMDS = sys.argv[2:] or ["task", "hwinfo", "ls", "pwd", "free", "uname"]


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
                buf += os.read(fd, 2048)
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
os.write(fd, b"\x03")
time.sleep(0.3)
read_for(fd, 0.4)

for cmd in CMDS:
    print(">>> %s" % cmd)
    os.write(fd, (cmd + "\r").encode())
    time.sleep(0.5)
    data = read_for(fd, 2.5)
    text = clean(data).strip()
    # 去掉回显的第一行
    lines = text.split("\n")
    if lines and lines[0].strip() == cmd:
        lines = lines[1:]
    print("\n".join(lines)[:2000] if lines else "   (无回显)")
    print("-" * 55)

os.close(fd)

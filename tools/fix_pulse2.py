#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把开锁/关锁时长都设为 2000ms，并检查板子是否存活。"""
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


def cmd(fd, text, wait=2.5):
    os.write(fd, ("%s\r" % text).encode())
    buf = b""
    end = time.time() + wait
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

print("=== ping（看板子是否还活着）===")
for line in cmd(fd, "zk ping", 2.5).splitlines():
    if "PING" in line:
        print("  ", line.strip()[:100])

print("=== 设置开锁/关锁都为 2000ms ===")
for line in cmd(fd, "zk pt 2000 2000", 2.0).splitlines():
    if "PT|OK" in line:
        print("  ", line.strip()[:80])

print("=== 立即执行一次开→关，验证关锁 ===")
cmd(fd, "zk open 8808", 1.0)
print("   已开锁，等 8 秒自动上锁…")
time.sleep(9)
for line in cmd(fd, "zk ping", 2.0).splitlines():
    if "PING" in line:
        print("  ", line.strip()[:100])

os.close(fd)
print("=== 完 ===")

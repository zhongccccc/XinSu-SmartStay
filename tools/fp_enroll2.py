#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""指纹录入第二步：采第二枚 → 合并模板 → 存到 0 号位。"""
import os
import select
import termios
import time


def open_port():
    fd = os.open("/dev/ttyUSB1", os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
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
        r, _, _ = select.select([fd], [], [], 0.1)
        if r:
            try:
                buf += os.read(fd, 4096)
            except BlockingIOError:
                pass
    return buf.decode("utf-8", "ignore")


fd = open_port()
time.sleep(0.3)
try:
    while os.read(fd, 4096):
        pass
except BlockingIOError:
    pass

print(">>> 等待第二次按压（最长 15 秒）…")
os.write(fd, b"zk en2 0\r")
buf = ""
end = time.time() + 15
while time.time() < end:
    buf += read_for(fd, 0.5)
    if "ZK|ACK|EN2" in buf:
        break

for line in buf.splitlines():
    s = line.strip()
    if "ZK|ACK|EN2" in s:
        print("   ", s[:80])
os.close(fd)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""独占 ttyUSB0，两种读卡命令轮询 60 秒，把响应写入 /tmp/rfid_test.log。"""
import os
import select
import termios
import time

PORT = "/dev/ttyUSB0"
LOG = "/tmp/rfid_test.log"

A = bytes([0x01, 0x08, 0xA1, 0x20, 0x20, 0x00, 0x01, 0x00, 0x76])
B = bytes([0x01, 0x08, 0xA1, 0x20, 0x00, 0x01, 0x00, 0x76])

out = open(LOG, "w")

try:
    fd = os.open(PORT, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
except Exception as e:
    out.write("open 失败: %s\n" % e)
    out.close()
    raise SystemExit

a = termios.tcgetattr(fd)
a[0] = a[1] = 0
a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
a[3] = 0
a[4] = a[5] = termios.B9600
a[6][termios.VMIN] = 0
a[6][termios.VTIME] = 0
termios.tcsetattr(fd, termios.TCSANOW, a)

out.write("开始轮询 60 秒\n")
out.flush()


def drain():
    try:
        while os.read(fd, 4096):
            pass
    except BlockingIOError:
        pass


seq = 0
end = time.time() + 60
while time.time() < end:
    seq += 1
    cmd = A if (seq % 2 == 1) else B
    tag = "A" if (seq % 2 == 1) else "B"
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
        out.write("t=%5.1f 变体%s 收到 %d 字节: %s\n" % (time.time() % 100, tag, len(buf), buf.hex(" ")))
        out.flush()
    time.sleep(0.05)

os.close(fd)
out.write("结束\n")
out.close()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""独占 ttyUSB0 轮询 20 秒，看读卡器到底有没有回包。"""
import os
import select
import termios
import time

LOG = "/tmp/rfid_poll.log"
CMD = bytes([0x01, 0x08, 0xA1, 0x20, 0x20, 0x00, 0x01, 0x00, 0x76])

out = open(LOG, "w")
try:
    fd = os.open("/dev/ttyUSB0", os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
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

hits = 0
tries = 0
end = time.time() + 20
while time.time() < end:
    tries += 1
    try:
        while os.read(fd, 512):
            pass
    except BlockingIOError:
        pass
    os.write(fd, CMD)
    buf = b""
    t = time.time() + 0.3
    while time.time() < t:
        r, _, _ = select.select([fd], [], [], 0.05)
        if r:
            try:
                buf += os.read(fd, 256)
            except BlockingIOError:
                pass
    if len(buf) >= 5:
        hits += 1
        out.write("收到 %d 字节: %s\n" % (len(buf), buf.hex(" ")))
        out.flush()
os.close(fd)
out.write("轮询 %d 次，有响应 %d 次\n" % (tries, hits))
out.close()

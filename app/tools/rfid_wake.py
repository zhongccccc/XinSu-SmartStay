#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RFID：尝试 DTR/RTS 组合 + 多波特率，看能否唤醒读卡器。"""
import fcntl
import os
import select
import termios
import time

DEV = "/dev/ttyUSB0"
TIOCMBIS = 0x5416   # set modem bits
TIOCMBIC = 0x5417   # clear modem bits
DTR, RTS = 0x02, 0x04
CMD = bytes([0x01, 0x08, 0xA1, 0x20, 0x00, 0x01, 0x00, 0x76])


def try_one(baud_const, dtr, rts, label):
    try:
        fd = os.open(DEV, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    except OSError as e:
        print("open fail:", e)
        return False
    a = termios.tcgetattr(fd)
    a[0] = 0
    a[1] = 0
    a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
    a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
    a[3] = 0
    a[4] = a[5] = baud_const
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, a)
    try:
        fcntl.ioctl(fd, TIOCMBIS if dtr else TIOCMBIC, DTR)
        fcntl.ioctl(fd, TIOCMBIS if rts else TIOCMBIC, RTS)
    except Exception as e:
        print("  ioctl:", e)
    time.sleep(0.4)
    for _ in range(2):
        os.write(fd, CMD)
        buf = b""
        end = time.time() + 0.8
        while time.time() < end:
            r, _, _ = select.select([fd], [], [], 0.1)
            if r:
                buf += os.read(fd, 64)
        if buf:
            print("  %-22s -> %s" % (label, buf.hex(" ")))
            os.close(fd)
            return True
    print("  %-22s -> (无应答)" % label)
    os.close(fd)
    return False


found = False
for bname, bconst in [("9600", termios.B9600), ("115200", termios.B115200),
                      ("38400", termios.B38400)]:
    for dtr in (0, 1):
        for rts in (0, 1):
            if try_one(bconst, dtr, rts, "baud=%s DTR=%d RTS=%d" % (bname, dtr, rts)):
                found = True
                break
        if found:
            break
    if found:
        break
print("RESULT:", "有应答" if found else "所有组合均无应答")

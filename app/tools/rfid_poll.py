#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""持续轮询 RFID 读卡器，记录任何应答（用于现场确认）。"""
import os
import select
import sys
import termios
import time

DEV = "/dev/ttyUSB0"
DURATION = int(sys.argv[1]) if len(sys.argv) > 1 else 180
LOG = "/opt/zhikong/data/rfid_poll.log"
CMD = bytes([0x01, 0x08, 0xA1, 0x20, 0x00, 0x01, 0x00, 0x76])


def log(s):
    line = "%s %s" % (time.strftime("%H:%M:%S"), s)
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def checksum_ok(b):
    c = 0
    for x in b[:-1]:
        c ^= x
    return b[-1] == (~c) & 0xFF


def scan(buf):
    out = []
    i = 0
    while i + 4 <= len(buf):
        n = buf[i + 1]
        if 4 <= n <= 32 and i + n <= len(buf):
            cand = buf[i:i + n]
            if checksum_ok(cand):
                out.append(cand)
                i += n
                continue
        i += 1
    return out


fd = os.open(DEV, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
a = termios.tcgetattr(fd)
a[0] = a[1] = 0
a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
a[3] = 0
a[4] = a[5] = termios.B9600
a[6][termios.VMIN] = 0
a[6][termios.VTIME] = 0
termios.tcsetattr(fd, termios.TCSANOW, a)

log("=== rfid poll start %ds ===" % DURATION)
end = time.time() + DURATION
n = 0
while time.time() < end:
    n += 1
    try:
        os.write(fd, CMD)
    except OSError as e:
        log("write err %s" % e)
    buf = b""
    t = time.time() + 0.45
    while time.time() < t:
        r, _, _ = select.select([fd], [], [], 0.05)
        if r:
            try:
                buf += os.read(fd, 512)
            except BlockingIOError:
                pass
    if buf:
        frames = scan(buf)
        if frames:
            f = frames[-1]
            if len(f) >= 12 and f[4] == 0:
                log("CARD uid=%s type=%s raw=%s" % (f[7:11].hex().upper(),
                                                   f[5:7].hex().upper(), f.hex(" ")))
            else:
                log("frame=%s (status=0x%02X)" % (f.hex(" "), f[4] if len(f) > 4 else -1))
        else:
            log("raw %d bytes: %s" % (len(buf), buf[:32].hex(" ")))
    time.sleep(0.15)
log("=== poll end, %d rounds ===" % n)
os.close(fd)

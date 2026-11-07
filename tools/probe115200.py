#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 115200 下对每个端口发 zk/zh ping，确认谁是门锁板/家居板。"""
import glob
import os
import select
import termios
import time


def probe(p):
    try:
        fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    except Exception as e:
        return "open 失败: %s" % e
    a = termios.tcgetattr(fd)
    a[0] = a[1] = 0
    a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
    a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
    a[3] = 0
    a[4] = a[5] = termios.B115200
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, a)

    def rd(sec):
        b = b""
        end = time.time() + sec
        while time.time() < end:
            r, _, _ = select.select([fd], [], [], 0.1)
            if r:
                try:
                    b += os.read(fd, 512)
                except BlockingIOError:
                    pass
        return b

    rd(0.5)
    os.write(fd, b"zk ping\r")
    zk = rd(1.8)
    os.write(fd, b"zh ping\r")
    zh = rd(1.8)
    os.close(fd)
    tags = []
    if b"ZK|ACK|PING" in zk:
        tags.append("门锁板")
    if b"ZH|ACK|PING" in zh:
        tags.append("家居板")
    ver = ""
    for line in (zk + zh).decode("utf-8", "ignore").splitlines():
        if "|PING|OK|" in line:
            ver = line.split("|PING|OK|")[1].split("|")[0]
    return ("%s %s" % (",".join(tags), ver)) if tags else "无应答（%d 字节杂音）" % len(zk + zh)


for p in sorted(glob.glob("/dev/ttyUSB*")):
    print("  %-14s %s" % (p, probe(p)))

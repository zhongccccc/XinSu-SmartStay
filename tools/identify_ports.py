#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描每个串口：试 RFID 读卡命令 + zk/zh ping，判断谁是谁。"""
import glob
import os
import select
import termios
import time

RFID = bytes([0x01, 0x08, 0xA1, 0x20, 0x20, 0x00, 0x01, 0x00, 0x76])
SPEEDS = [(9600, termios.B9600), (115200, termios.B115200)]


def try_port(p):
    for baud, sp in SPEEDS:
        try:
            fd = os.open(p, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        except Exception as e:
            print("  %-14s open 失败: %s" % (p, e))
            return
        a = termios.tcgetattr(fd)
        a[0] = a[1] = 0
        a[2] = (a[2] & ~termios.CSIZE) | termios.CS8
        a[2] &= ~(termios.PARENB | termios.CSTOPB | termios.CRTSCTS)
        a[3] = 0
        a[4] = a[5] = sp
        a[6][termios.VMIN] = 0
        a[6][termios.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSANOW, a)
        try:
            while os.read(fd, 4096):
                pass
        except BlockingIOError:
            pass

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

        res = []
        for i in range(6):
            os.write(fd, RFID)
            got = rd(0.35)
            if len(got) >= 4:
                res.append("RFID:" + got.hex(" "))
                break
        os.write(fd, b"zk ping\r")
        zk = rd(1.2)
        if b"ZK|ACK|PING" in zk:
            res.append("门锁板")
        os.write(fd, b"zh ping\r")
        zh = rd(1.2)
        if b"ZH|ACK|PING" in zh:
            res.append("家居板")
        os.close(fd)
        print("  %-14s @%-6d %s" % (p, baud, " | ".join(res) if res else "无响应"))
        if res:
            return


print("=== 端口识别 ===")
for p in sorted(glob.glob("/dev/ttyUSB*")):
    try_port(p)
